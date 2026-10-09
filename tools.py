"""tools.py - STUDENT IMPLEMENTS.  Source tools for the research agents.   Guide: GUIDE.md, part 1.

Rules for every tool:
  * runs on the HOST (not in the sandbox): API keys must never enter the sandbox;
  * returns a STRING (JSON text of compact records) and NEVER raises:
        "NO RESULTS"  when the source answers with nothing,
        "ERROR: ..."  when the source keeps failing after the retries (the agent then tries another source);
  * the docstring is the tool description the LLM reads: keep it precise (what it does, what it returns, when to use it).
Try your tools without any agent:   python tools.py
"""
import json
import os
import random
import re
import time
import xml.etree.ElementTree as ET

import httpx
from langchain_core.tools import tool

# ---- constants (given) ----
ARXIV_URL = "https://export.arxiv.org/api/query"  # https only: http answers 301
HF_DAILY_URL = "https://huggingface.co/api/daily_papers"
HF_SEARCH_URL = "https://huggingface.co/api/papers/search"
EXA_URL = "https://mcp.exa.ai/mcp"


class RetryableError(Exception):
    """Given. Raise it inside a call to ask with_retry to wait and try again (retry_after in seconds, optional)."""

    def __init__(self, message, retry_after=None):
        super().__init__(message)
        self.retry_after = retry_after


# ---- TODO 1: retry helper ----
def with_retry(fn, *, attempts=5, base=1.0, cap=30.0):
    """Call fn(); when it raises RetryableError, wait and call it again.

    PSEUDO-CODE:
      for attempt in 0 .. attempts-1:
          try: return fn()
          except RetryableError as e:
              if this was the last attempt: raise
              delay = e.retry_after if the server told us, else exponential backoff base * 2**attempt
              cap the delay at `cap` seconds; add random jitter to the exponential case
              sleep(delay)
    Use it to wrap EVERY network call below. Also treat these as retryable: HTTP 429/500/502/503/504,
    httpx.TransportError (timeouts, connection resets). Read the Retry-After header when present.
    """
    for attempt in range(attempts):
        try:
            return fn()
        except RetryableError as exc:
            if attempt == attempts - 1:
                raise
            if exc.retry_after is not None:
                delay = min(exc.retry_after, cap)
            else:
                delay = min(base * (2 ** attempt), cap) + random.uniform(0, base)
                delay = min(delay, cap)
            time.sleep(delay)


def _retryable_from_httpx(exc):
    """Convert an httpx error into RetryableError when it looks transient; otherwise return it unchanged."""
    if isinstance(exc, httpx.HTTPStatusError):
        status = exc.response.status_code
        if status == 429 or status >= 500:
            retry_after = exc.response.headers.get("Retry-After")
            return RetryableError(str(exc), retry_after=float(retry_after) if retry_after else None)
        return exc
    if isinstance(exc, httpx.TransportError):
        return RetryableError(str(exc))
    return exc


# ---- TODO 2: arXiv ----
@tool
def arxiv_search(query: str, max_results: int = 10) -> str:
    """Search arXiv papers by keywords, newest first. Returns a JSON list of {id, url, published, title, summary}."""
    # PSEUDO-CODE:
    #   keep only word characters of `query` -> terms; no terms -> "NO RESULTS" (do not call the network)
    #   respect arXiv etiquette: at least 3 seconds between two arXiv calls (remember the time of the last call)
    #   GET ARXIV_URL params: search_query="all:t1 AND all:t2 ...", sortBy=submittedDate, sortOrder=descending,
    #       max_results=clamp(max_results, 1, 30)           (wrap in with_retry)
    #   parse the Atom XML: each <entry> -> {id (last part of <id> after /abs/), url, published[:10], title, summary}
    #       collapse whitespace/newlines in title and summary; cut summary to ~600 chars
    #   no entries -> "NO RESULTS"; else json.dumps(records, ensure_ascii=False)
    #   any exception -> "ERROR: <type>: <message>"
    try:
        terms = re.findall(r"\w+", query)
        if not terms:
            return "NO RESULTS"
        since_last = time.monotonic() - _arxiv_state["last_call"]
        if since_last < 3.0:
            time.sleep(3.0 - since_last)

        search_query = " AND ".join(f"all:{t}" for t in terms)
        params = {
            "search_query": search_query,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
            "max_results": max(1, min(max_results, 30)),
            "start": 0,
        }

        def _call():
            try:
                resp = httpx.get(ARXIV_URL, params=params, timeout=30.0)
                resp.raise_for_status()
                return resp.text
            except (httpx.HTTPStatusError, httpx.TransportError) as exc:
                raise _retryable_from_httpx(exc) from exc

        xml_text = with_retry(_call, attempts=6, base=2.0, cap=60.0)
        _arxiv_state["last_call"] = time.monotonic()

        ns = {"atom": "http://www.w3.org/2005/Atom"}
        root = ET.fromstring(xml_text)
        records = []
        for entry in root.findall("atom:entry", ns):
            id_url = (entry.findtext("atom:id", default="", namespaces=ns) or "").strip()
            arxiv_id = id_url.rsplit("/abs/", 1)[-1]
            arxiv_id = re.sub(r"v\d+$", "", arxiv_id)
            published = (entry.findtext("atom:published", default="", namespaces=ns) or "")[:10]
            title = " ".join((entry.findtext("atom:title", default="", namespaces=ns) or "").split())
            summary = " ".join((entry.findtext("atom:summary", default="", namespaces=ns) or "").split())[:600]
            if not arxiv_id:
                continue
            records.append({
                "id": arxiv_id,
                "url": f"https://arxiv.org/abs/{arxiv_id}",
                "published": published,
                "title": title,
                "summary": summary,
            })
        if not records:
            return "NO RESULTS"
        return json.dumps(records, ensure_ascii=False)
    except Exception as exc:  # noqa: BLE001 - tool contract: never raise
        return f"ERROR: {type(exc).__name__}: {exc}"


_arxiv_state = {"last_call": 0.0}


# ---- TODO 3: Hugging Face ----
@tool
def hf_daily_papers(limit: int = 30, date: str = "", keyword: str = "") -> str:
    """Hugging Face Daily Papers = what is trending in AI research. Returns a JSON list of
    {id, url, published, title, summary, upvotes, github, stars} sorted by upvotes. `date` is YYYY-MM-DD (empty = latest).
    `keyword` filters title/summary; there is no topic search on this endpoint (use hf_search_papers for a topic)."""
    # PSEUDO-CODE:
    #   GET HF_DAILY_URL params: limit (clamp 1..100) and date (only when given)      (with_retry)
    #   response = list of items {"paper": {id, title, summary, upvotes, githubRepo, githubStars, publishedAt}, ...}
    #   map every item to the record shape above (skip items without paper.id); url = https://huggingface.co/papers/<id>
    #   keyword -> keep records whose title+summary contains it (case-insensitive); sort by upvotes descending
    try:
        params = {"limit": max(1, min(limit, 100))}
        if date:
            params["date"] = date

        def _call():
            try:
                resp = httpx.get(HF_DAILY_URL, params=params, timeout=30.0)
                resp.raise_for_status()
                return resp.json()
            except (httpx.HTTPStatusError, httpx.TransportError) as exc:
                raise _retryable_from_httpx(exc) from exc

        items = with_retry(_call)
        records = []
        for item in items:
            paper = item.get("paper") or {}
            pid = paper.get("id")
            if not pid:
                continue
            records.append({
                "id": pid,
                "url": f"https://huggingface.co/papers/{pid}",
                "published": paper.get("publishedAt", "")[:10],
                "title": paper.get("title", ""),
                "summary": (paper.get("summary") or "")[:600],
                "upvotes": paper.get("upvotes", 0),
                "github": paper.get("githubRepo", ""),
                "stars": paper.get("githubStars", 0),
            })
        if keyword:
            kw = keyword.lower()
            records = [r for r in records if kw in r["title"].lower() or kw in r["summary"].lower()]
        records.sort(key=lambda r: r.get("upvotes", 0), reverse=True)
        if not records:
            return "NO RESULTS"
        return json.dumps(records, ensure_ascii=False)
    except Exception as exc:  # noqa: BLE001
        return f"ERROR: {type(exc).__name__}: {exc}"


@tool
def hf_search_papers(query: str, limit: int = 10) -> str:
    """Search Hugging Face papers by topic. Returns a JSON list of
    {id, url, published, title, summary, upvotes, github, stars}."""
    # PSEUDO-CODE:
    #   GET HF_SEARCH_URL params: q=query, limit (clamp 1..50)                         (with_retry)
    #   same item shape as the daily endpoint; prefer paper["ai_summary"] over paper["summary"] when present
    try:
        params = {"q": query, "limit": max(1, min(limit, 50))}

        def _call():
            try:
                resp = httpx.get(HF_SEARCH_URL, params=params, timeout=30.0)
                resp.raise_for_status()
                return resp.json()
            except (httpx.HTTPStatusError, httpx.TransportError) as exc:
                raise _retryable_from_httpx(exc) from exc

        items = with_retry(_call)
        records = []
        for item in items:
            paper = item.get("paper") or {}
            pid = paper.get("id")
            if not pid:
                continue
            summary = paper.get("ai_summary") or paper.get("summary") or ""
            records.append({
                "id": pid,
                "url": f"https://huggingface.co/papers/{pid}",
                "published": paper.get("publishedAt", "")[:10],
                "title": paper.get("title", ""),
                "summary": summary[:600],
                "upvotes": paper.get("upvotes", 0),
                "github": paper.get("githubRepo", ""),
                "stars": paper.get("githubStars", 0),
            })
        if not records:
            return "NO RESULTS"
        return json.dumps(records, ensure_ascii=False)
    except Exception as exc:  # noqa: BLE001
        return f"ERROR: {type(exc).__name__}: {exc}"


# ---- TODO 4: web search / fetch through the Exa MCP endpoint ----
@tool
def web_search(query: str, objective: str = "", num_results: int = 5) -> str:
    """Search the web (Exa). Describe the ideal page in natural language. Returns clean text of the top results with URLs."""
    # PSEUDO-CODE:
    #   call the MCP tool "web_search_exa" with arguments {query, objective, numResults}
    #       (objective is REQUIRED by Exa: when empty, build one from the query)
    #   see GUIDE.md part 1.4 for how to call an MCP server over plain HTTP (JSON-RPC "tools/call") and read the answer
    #   read optional env EXA_API_KEY; when present it is sent to the Exa endpoint.
    #       (see GUIDE.md 1.4 for where it goes) => the key then appears in exception text: redact it before returning "ERROR: ..."
    #   WATCH OUT: read GUIDE.md 1.4 about how Exa signals "rate limited" on the free tier, and retry on it
    try:
        if not objective:
            objective = f"find pages relevant to: {query}"
        result = _exa_call("web_search_exa", {
            "query": query, "objective": objective, "numResults": max(1, min(num_results, 20)),
        })
        text = _exa_text(result)
        return text if text.strip() else "NO RESULTS"
    except Exception as exc:  # noqa: BLE001
        return f"ERROR: {_redact_exa_key(str(exc))}"


@tool
def web_fetch(url: str) -> str:
    """Read the full content of one web page (e.g. an arXiv abstract page) as markdown. Long pages are truncated."""
    # PSEUDO-CODE: MCP tool "web_fetch_exa" with arguments {"urls": [url]}; truncate the text to ~12000 chars
    try:
        result = _exa_call("web_fetch_exa", {"urls": [url]})
        text = _exa_text(result)
        if not text.strip():
            return "NO RESULTS"
        return text[:12000]
    except Exception as exc:  # noqa: BLE001
        return f"ERROR: {_redact_exa_key(str(exc))}"


_EXA_RATE_LIMIT_MARKERS = ("rate limit", "rate-limit", "ratelimit", "too many requests")


def _redact_exa_key(text):
    return re.sub(r"exaApiKey=[^&\s'\"]+", "exaApiKey=<redacted>", text)


def _exa_call(name, arguments):
    """Call one Exa MCP tool via plain JSON-RPC over HTTP, retrying on transient errors and Exa's soft rate limit."""
    url = EXA_URL
    api_key = os.getenv("EXA_API_KEY", "").strip()
    if api_key:
        url = f"{EXA_URL}?exaApiKey={api_key}"
    payload = {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": name, "arguments": arguments}}
    headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}

    def _call():
        try:
            resp = httpx.post(url, json=payload, headers=headers, timeout=60.0)
            resp.raise_for_status()
        except (httpx.HTTPStatusError, httpx.TransportError) as exc:
            raise _retryable_from_httpx(exc) from exc

        body = None
        for line in resp.text.splitlines():
            line = line.strip()
            if line.startswith("data:"):
                body = json.loads(line[len("data:"):].strip())
                break
        if body is None:
            body = resp.json()

        if "error" in body:
            raise RuntimeError(f"Exa MCP error: {body['error']}")
        result = body.get("result", {})
        meta = result.get("_meta") or {}
        meta_text = json.dumps(meta).lower()
        if any(marker in meta_text for marker in _EXA_RATE_LIMIT_MARKERS):
            raise RetryableError("Exa MCP rate limited (seen in result._meta)")
        return result

    return with_retry(_call, attempts=6, base=3.0, cap=60.0)


def _exa_text(result):
    parts = []
    for item in result.get("content", []):
        if item.get("type") == "text":
            parts.append(item.get("text", ""))
    return "\n".join(parts)


# ---- TODO 5: registry (the researcher subagent gets exactly these) ----
SOURCE_TOOLS = [arxiv_search, hf_daily_papers, hf_search_papers, web_search, web_fetch]


if __name__ == "__main__":
    for name, fn, args in [
        ("arxiv_search", arxiv_search, {"query": "world model", "max_results": 3}),
        ("hf_daily_papers", hf_daily_papers, {"limit": 20}),
        ("hf_search_papers", hf_search_papers, {"query": "world model", "limit": 3}),
        ("web_search", web_search, {"query": "survey paper on world models", "num_results": 2}),
        ("web_fetch", web_fetch, {"url": "https://arxiv.org/abs/1803.10122"}),
    ]:
        try:
            print(f"== {name}\n{fn.invoke(args)[:400]}\n")
        except NotImplementedError as exc:
            print(f"== {name}: not implemented yet ({exc})\n")
