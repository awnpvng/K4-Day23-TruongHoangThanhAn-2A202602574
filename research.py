"""research.py - STUDENT IMPLEMENTS.  The main script.   Guide: GUIDE.md, part 3.

Usage:  python research.py "survey about world model"
Result: reports/<slug>.md   reports/<slug>.sources.json   reports/<slug>.meta.json
"""
import json  # noqa: F401
import os  # noqa: F401
import re  # noqa: F401
import sys
import time  # noqa: F401
from collections import Counter  # noqa: F401
from pathlib import Path

from langchain_core.rate_limiters import InMemoryRateLimiter

from agents import FINALIZER_PATH, REPORT_PATH, SOURCES_PATH, VALIDATOR_PATH, WORKDIR, build_lead_agent  # noqa: F401
from check_citations import check as check_citations_check
from model import make_model  # noqa: F401
from sandbox import download, open_sandbox, upload  # noqa: F401

ROOT = Path(__file__).parent
REPORTS = ROOT / "reports"
VALIDATOR_SOURCE = ROOT / "check_citations.py"
FINALIZER_SOURCE = ROOT / "finalize_citations.py"   # provided: uploaded next to your validator

# Client-side cap on model calls per minute, shared by the lead and every subagent (they call the same model
# instance). Keeps free-tier providers (e.g. Gemini free tier: 10-15 RPM) from being hit by bursts of parallel
# subagent calls. Override with LAB_MAX_RPM in .env; default stays safely under a 10 RPM provider limit.
MAX_RPM = float(os.getenv("LAB_MAX_RPM", "8"))


def slugify(topic):
    """Turn a topic into a safe file name: lower case, runs of non-word characters become one "-", max 60 chars,
    never empty (fall back to "topic"). The topic is user input: "../../x" must not escape reports/."""
    slug = re.sub(r"[^a-z0-9]+", "-", topic.strip().lower()).strip("-")
    slug = slug[:60].strip("-")
    return slug or "topic"


def build_prompt(topic):
    """The user message sent to the lead agent."""
    return (
        f'Research topic: "{topic}"\n\n'
        "Produce a cited survey report on this topic following your system prompt end to end: plan, delegate to "
        "researcher subagents in parallel, merge sources, write the report body, run the finalizer and your "
        "validator until it prints OK, then have citation-checker spot-check a few claims."
    )


def summarize(messages, elapsed, model_name):
    """Return {"model", "elapsed_s", "subagent_calls", "tool_calls": {name: count}, "tokens": {"input", "output"}}.

    PSEUDO-CODE: walk the lead's messages; for every message with tool_calls count call["name"] (subagent_calls = the
    count of "task"); add the input/output token counts from each message's usage_metadata when present.
    (Lead messages only: subagent tokens are not included, so this undercounts the real cost.)
    elapsed_s rounded to 0.1.
    """
    tool_calls = Counter()
    subagent_calls = 0
    input_tokens = 0
    output_tokens = 0
    for message in messages:
        for call in getattr(message, "tool_calls", None) or []:
            name = call.get("name") if isinstance(call, dict) else getattr(call, "name", None)
            if not name:
                continue
            tool_calls[name] += 1
            if name == "task":
                subagent_calls += 1
        usage = getattr(message, "usage_metadata", None) or {}
        input_tokens += usage.get("input_tokens", 0) or 0
        output_tokens += usage.get("output_tokens", 0) or 0
    return {
        "model": model_name,
        "elapsed_s": round(elapsed, 1),
        "subagent_calls": subagent_calls,
        "tool_calls": dict(tool_calls),
        "tokens": {"input": input_tokens, "output": output_tokens},
    }


def save_outputs(backend, topic, messages, elapsed, model_name, reports_dir=REPORTS):
    """Download the report from the sandbox and write the three files into reports_dir. Return the report path.

    PSEUDO-CODE:
      files = download(backend, [REPORT_PATH, SOURCES_PATH])
      if the report is missing/empty or sources.json is missing/invalid JSON: raise RuntimeError and WRITE NOTHING
          (a failed run must never leave an empty or half-written report behind)
      write <slug>.sources.json, <slug>.meta.json (topic + summarize(...) + n_sources + source_families: the sorted
      distinct "source" values of sources.json) and <slug>.md
    """
    files = download(backend, [REPORT_PATH, SOURCES_PATH])
    report_bytes = files.get(REPORT_PATH)
    sources_bytes = files.get(SOURCES_PATH)
    if not report_bytes or not report_bytes.strip():
        raise RuntimeError(f"no report produced at {REPORT_PATH}")
    if not sources_bytes:
        raise RuntimeError(f"no sources.json produced at {SOURCES_PATH}")
    try:
        sources = json.loads(sources_bytes)
    except ValueError as exc:
        raise RuntimeError(f"sources.json is not valid JSON: {exc}") from exc
    if not isinstance(sources, list) or not sources:
        raise RuntimeError("sources.json is empty or not a list")
    report_text = report_bytes.decode("utf-8")
    problems = check_citations_check(report_text, sources)
    if problems:
        raise RuntimeError("downloaded report fails citation validation: " + "; ".join(problems))
    tldr_match = re.search(r"## TL;DR\n(.*?)\n## ", report_text, re.S)
    if tldr_match:
        uncited = [b for b in tldr_match.group(1).splitlines() if b.strip().startswith("-") and "[" not in b]
        if uncited:
            raise RuntimeError(f"{len(uncited)} TL;DR bullet(s) have no [n] citation (REPORT_TEMPLATE violation)")

    reports_dir.mkdir(parents=True, exist_ok=True)
    slug = slugify(topic)
    report_path = reports_dir / f"{slug}.md"
    sources_path = reports_dir / f"{slug}.sources.json"
    meta_path = reports_dir / f"{slug}.meta.json"

    meta = summarize(messages, elapsed, model_name)
    meta["topic"] = topic
    meta["n_sources"] = len(sources)
    meta["source_families"] = sorted({s.get("source") for s in sources if s.get("source")})

    report_path.write_bytes(report_bytes)
    sources_path.write_text(json.dumps(sources, ensure_ascii=False, indent=2), encoding="utf-8")
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return report_path


def main(topic):
    """Return the process exit code (0 ok, 1 failed run, 2 no topic).

    PSEUDO-CODE:
      empty topic -> print usage to stderr, return 2
      model = make_model(); start = time.monotonic()
      with open_sandbox() as backend:                # the sandbox is always cleaned up, even on errors
          backend.execute("mkdir -p <WORKDIR>/research/notes <WORKDIR>/report")
          upload(backend, {VALIDATOR_PATH: VALIDATOR_SOURCE.read_bytes(), FINALIZER_PATH: FINALIZER_SOURCE.read_bytes()})
          agent = build_lead_agent(backend, model)
          result = agent.invoke({"messages": [{"role": "user", "content": build_prompt(topic)}]},
                                config={"recursion_limit": 1000})
          save_outputs(...); on RuntimeError print "FAILED: ..." to stderr and return 1
      print where the report was saved; return 0
    """
    topic = topic.strip()
    if not topic:
        print('Usage: python research.py "<topic>"', file=sys.stderr)
        return 2

    model = make_model()
    model.rate_limiter = InMemoryRateLimiter(
        requests_per_second=MAX_RPM / 60, check_every_n_seconds=0.1, max_bucket_size=1,
    )
    start = time.monotonic()
    with open_sandbox() as backend:
        backend.execute(f"mkdir -p {WORKDIR}/research/notes {WORKDIR}/report")
        upload(backend, {
            VALIDATOR_PATH: VALIDATOR_SOURCE.read_bytes(),
            FINALIZER_PATH: FINALIZER_SOURCE.read_bytes(),
        })
        agent = build_lead_agent(backend, model)
        result = agent.invoke(
            {"messages": [{"role": "user", "content": build_prompt(topic)}]},
            config={"recursion_limit": 1000},
        )
        elapsed = time.monotonic() - start
        model_name = getattr(model, "model_name", None) or getattr(model, "model", None) or str(model)
        try:
            report_path = save_outputs(backend, topic, result["messages"], elapsed, model_name)
        except RuntimeError as exc:
            print(f"FAILED: {exc}", file=sys.stderr)
            return 1

    print(f"Report saved to {report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(" ".join(sys.argv[1:])))
