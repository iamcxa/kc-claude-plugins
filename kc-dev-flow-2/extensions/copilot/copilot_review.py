#!/usr/bin/env python3
"""Report the GitHub Copilot review state of a pull request's head commit.

Usage: copilot_review.py <owner/repo> <pr>
The latest Copilot review of the head decides, and its evidence id is printed so a round
is counted once per id.
Exit 0 clean: that review says "0 open findings", or (older format) "generated no
  comments", and has no line comment.
Exit 1 findings: that review has open findings or line comments, or a shape this reader
  does not know together with a line comment (fail closed).
Exit 2 configuration error: bad arguments or a gh call that failed.
Exit 3 requested: Copilot was asked to review after its last review and has not answered.
Exit 4 not reviewed: no Copilot review of the head commit, an unknown review shape with
  no line comment, or the head moved while reading.
"""
import html
import json
import re
import subprocess
import sys

BOT = "copilot-pull-request-reviewer[bot]"
LINE_AUTHORS = {"Copilot", BOT}
OVERVIEW = "<!-- ccr-overview-v2 -->"
OPEN = re.compile(r"(?:\*\*|<strong>)(\d+) open findings?(?:\*\*|</strong>)")
LEGACY = re.compile(r"generated (no|\d+) comments?")
SEVERITY = re.compile(r'alt="(Critical|High|Medium|Low) severity"')
TOP = {"Critical", "High"}


def gh(*args):
    try:
        done = subprocess.run(["gh", *args], capture_output=True, text=True)
    except OSError as error:
        raise RuntimeError(f"gh not runnable: {error}") from error
    if done.returncode:
        raise RuntimeError(done.stderr.strip() or f"gh {' '.join(args)} failed")
    return json.loads(done.stdout or "null")


def pages(path):
    return [item for page in gh("api", "--paginate", "--slurp", path) for item in page]


def verdict(body, lines):
    if OVERVIEW in body and (m := OPEN.search(body)):
        found = int(m.group(1))
        if found == 0 and not lines:
            return 0, "0 open findings"
        levels = SEVERITY.findall(body)
        top = sum(level in TOP for level in levels)
        return 1, f"{max(found, len(lines))} open finding(s), {top} at High or above"
    if m := LEGACY.search(body):
        if m.group(1) == "no" and not lines:
            return 0, "generated no comments"
        return 1, f"{len(lines) or m.group(1)} comment(s), no severity given"
    if lines:
        return 1, f"{len(lines)} line comment(s) in a review shape this reader does not know"
    return None, "a review shape this reader does not know"


def state(repo, pr, call=gh, pages=pages):
    head = call("pr", "view", pr, "--repo", repo, "--json", "headRefOid")["headRefOid"]
    reviews = [r for r in pages(f"repos/{repo}/pulls/{pr}/reviews") if r["user"]["login"] == BOT]
    lines = [c for c in pages(f"repos/{repo}/pulls/{pr}/comments") if c["user"]["login"] in LINE_AUTHORS]
    asked = [e["created_at"] for e in pages(f"repos/{repo}/issues/{pr}/timeline")
             if e.get("event") == "review_requested"
             and (e.get("requested_reviewer") or {}).get("login") in {"Copilot", BOT}]
    on_head = sorted((r for r in reviews if r.get("commit_id") == head), key=lambda r: r["submitted_at"])
    last_review = max((r["submitted_at"] for r in reviews), default="")
    if call("pr", "view", pr, "--repo", repo, "--json", "headRefOid")["headRefOid"] != head:
        return 4, f"not reviewed: the head moved from {head[:9]} while its review was being read"
    if asked and max(asked) > last_review:
        return 3, f"requested: Copilot was asked at {max(asked)} and has not reviewed since; head {head[:9]}"
    if not on_head:
        return 4, f"not reviewed: no Copilot review covers {head[:9]}"
    latest = on_head[-1]
    own = [c for c in lines if c.get("pull_request_review_id") == latest["id"]]
    code, detail = verdict(html.unescape(latest.get("body") or ""), own)
    if code is None:
        return 4, f"not reviewed: {detail} on {head[:9]} (review {latest['id']})"
    word = "findings" if code else "clean"
    return code, f"{word} on {head[:9]}: {detail}; evidence=review:{latest['id']} at {latest['submitted_at']}"


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 2 or "/" not in args[0]:
        print(__doc__.strip())
        return 2
    try:
        code, line = state(*args)
    except (RuntimeError, KeyError, TypeError, json.JSONDecodeError) as error:
        print(f"configuration error: {error}")
        return 2
    print(line)
    return code


if __name__ == "__main__":
    sys.exit(main())
