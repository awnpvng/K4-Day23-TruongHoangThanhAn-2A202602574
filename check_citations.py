"""check_citations.py - STUDENT IMPLEMENTS `check`.   Runs INSIDE the sandbox (standard library only).

research.py uploads this file to the sandbox and the lead agent runs it with the `execute` tool:
    python3 /tmp/work/research/check_citations.py [report.md] [sources.json]
It must exit 0 and print "OK: ..." when the report is consistent, else print each problem and exit 1.
"""
import json
import re
import sys

REPORT = "/tmp/work/report/report.md"
SOURCES = "/tmp/work/research/sources.json"

REFERENCES_HEADING = "## References"
CITATION_RE = re.compile(r"\[(\d+)\]")
MD_LINK_RE = re.compile(r"\[\d+\]\([^)]*\)")
REF_LINE_RE = re.compile(r"^\[(\d+)\]")
URL_RE = re.compile(r"https?://\S+")


def _strip_code_and_links(text):
    """Remove fenced/inline code spans and markdown links `[n](url)` so their digits are not read as citations."""
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    text = re.sub(r"`[^`]*`", "", text)
    text = MD_LINK_RE.sub("", text)
    return text


def check(report_text, sources):
    """Return a list of problem strings (empty list = OK).

    PSEUDO-CODE:
      problems = []
      if sources is empty: return ["no sources in sources.json"]
      for each source entry:
          n must be an int                       -> problem if not
          url must start with http:// or https://-> problem if not
          the same url must not appear twice     -> problem if duplicated
      split report_text at the heading "## References":
          body = text before it; if the heading is missing -> problem
      cited = set of numbers found as [n] in the BODY only (not in the reference list; use a regex)
      every number in `cited` must exist in sources -> problem "[n] cited but missing from sources.json"
      every source number must be in `cited`        -> problem "source [n] never cited"
      the lines of the References section that start with "[n]" (regex) are the reference lines:
          every source needs exactly ONE reference line (none missing, no number twice, no number that is not a source)
          each reference line holds exactly ONE http(s) URL and it must equal that source's url
          (a line bundling several sources under one number is a problem)
      return problems
    """
    problems = []
    if not sources:
        return ["no sources in sources.json"]

    seen_urls = {}
    valid_ns = set()
    for src in sources:
        n = src.get("n")
        if not isinstance(n, int):
            problems.append(f"source n={n!r} is not an integer")
            continue
        valid_ns.add(n)
        url = src.get("url", "")
        if not isinstance(url, str) or not url.startswith(("http://", "https://")):
            problems.append(f"source [{n}] has invalid url: {url!r}")
        if url in seen_urls:
            problems.append(f"duplicate url between source [{seen_urls[url]}] and [{n}]: {url}")
        else:
            seen_urls[url] = n
        family = src.get("source")
        if family not in ("arxiv", "hf-daily", "hf-search", "web"):
            problems.append(f"source [{n}] has invalid source family: {family!r}")

    if REFERENCES_HEADING not in report_text:
        problems.append(f"missing '{REFERENCES_HEADING}' heading")
        return problems

    body, _, references = report_text.partition(REFERENCES_HEADING)
    cleaned_body = _strip_code_and_links(body)

    for line in cleaned_body.splitlines():
        if re.match(r"^#{1,6}\s*References\s*$", line.strip(), re.IGNORECASE):
            problems.append(f"body contains a stray references heading before '{REFERENCES_HEADING}': {line!r}")

    cited = set()
    for group in re.findall(r"\[([\d,\-\s]+)\]", cleaned_body):
        for part in group.split(","):
            part = part.strip()
            if "-" in part:
                lo, _, hi = part.partition("-")
                lo, hi = lo.strip(), hi.strip()
                if lo.isdigit() and hi.isdigit():
                    cited.update(range(int(lo), int(hi) + 1))
            elif part.isdigit():
                cited.add(int(part))

    for n in sorted(cited):
        if n not in valid_ns:
            problems.append(f"[{n}] cited but missing from sources.json")
    for n in sorted(valid_ns):
        if n not in cited:
            problems.append(f"source [{n}] never cited")

    ref_counts = {}
    for line in references.splitlines():
        line = line.strip()
        m = REF_LINE_RE.match(line)
        if not m:
            continue
        n = int(m.group(1))
        ref_counts[n] = ref_counts.get(n, 0) + 1
        urls = URL_RE.findall(line)
        if len(urls) != 1:
            problems.append(f"reference line [{n}] must contain exactly one URL, found {len(urls)}")
        elif n in valid_ns:
            expected = next(s.get("url") for s in sources if s.get("n") == n)
            if urls[0] != expected:
                problems.append(f"reference line [{n}] url {urls[0]!r} does not match sources.json url {expected!r}")

    for n in valid_ns:
        count = ref_counts.get(n, 0)
        if count == 0:
            problems.append(f"source [{n}] has no reference line")
        elif count > 1:
            problems.append(f"source [{n}] has {count} reference lines, expected exactly one")
    for n in ref_counts:
        if n not in valid_ns:
            problems.append(f"reference line [{n}] does not correspond to any source")

    return problems


def main(argv):
    report_path = argv[1] if len(argv) > 1 else REPORT
    sources_path = argv[2] if len(argv) > 2 else SOURCES
    try:
        with open(report_path, encoding="utf-8") as f:
            report = f.read()
        with open(sources_path, encoding="utf-8") as f:
            sources = json.load(f)
    except (OSError, ValueError) as exc:
        print(f"cannot read inputs: {exc}")
        return 1
    problems = check(report, sources)
    if problems:
        print("\n".join(problems))
        return 1
    print(f"OK: {len(sources)} sources, all citations resolve")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
