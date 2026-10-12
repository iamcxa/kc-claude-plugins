#!/usr/bin/env python3
"""Report whether GitHub Copilot has answered a review request on a pull request's head.

Usage: copilot_review.py <owner/repo> <pr>
This reader does not judge what Copilot found; FO reads the review it names.
Exit 0 answered: Copilot reviewed the head commit after its latest request. The line names
  the review (evidence=review:<id>, one round per id), its heading line, and how many line
  comments belong to it.
Exit 2 configuration error: bad arguments or a gh call that failed.
Exit 3 requested: Copilot was asked after its latest review of any commit and has not answered.
Exit 4 not reviewed: no Copilot review of the head commit, or the head moved while reading.
"""
import html
import json
import subprocess
import sys

BOT = "copilot-pull-request-reviewer[bot]"
LINE_AUTHORS = {"Copilot", BOT}


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


def heading(body):
    for row in html.unescape(body).splitlines():
        row = row.strip()
        if row.startswith("### ") or row.startswith("## Pull request overview"):
            return row.lstrip("# ").strip().replace("evidence=", "evidence:")
    return "no heading"


def state(repo, pr, call=gh, pages=pages):
    head = call("pr", "view", pr, "--repo", repo, "--json", "headRefOid")["headRefOid"]
    reviews = [r for r in pages(f"repos/{repo}/pulls/{pr}/reviews") if r["user"]["login"] == BOT]
    lines = [c for c in pages(f"repos/{repo}/pulls/{pr}/comments") if c["user"]["login"] in LINE_AUTHORS]
    asked = [e["created_at"] for e in pages(f"repos/{repo}/issues/{pr}/timeline")
             if e.get("event") == "review_requested"
             and (e.get("requested_reviewer") or {}).get("login") in {"Copilot", BOT}]
    on_head = sorted((r for r in reviews if r.get("commit_id") == head), key=lambda r: r["submitted_at"])
    if call("pr", "view", pr, "--repo", repo, "--json", "headRefOid")["headRefOid"] != head:
        return 4, f"not reviewed: the head moved from {head[:9]} while its review was being read"
    if asked and max(asked) > max((r["submitted_at"] for r in reviews), default=""):
        return 3, f"requested: Copilot was asked at {max(asked)} and has not reviewed {head[:9]} since"
    if not on_head:
        return 4, f"not reviewed: no Copilot review covers {head[:9]}"
    latest = on_head[-1]
    own = sum(c.get("pull_request_review_id") == latest["id"] for c in lines)
    return 0, (f"answered on {head[:9]}: \"{heading(latest.get('body') or '')}\", {own} line comment(s); "
               f"evidence=review:{latest['id']} at {latest['submitted_at']}")


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
