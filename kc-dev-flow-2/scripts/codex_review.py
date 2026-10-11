#!/usr/bin/env python3
"""Report the Codex review state of a pull request's head commit.

Usage: codex_review.py <owner/repo> <pr>
Exit 0 clean: no review running, none of Codex's findings were made on the head, and
  Codex's summary names the head as completed or its +1 reaction is newer than the head commit.
Exit 1 findings: Codex made line findings or a review on the head commit.
Exit 2 configuration error: bad arguments or a gh call that failed.
Exit 3 running: Codex's eyes reaction is on the pull request.
Exit 4 not reviewed: no Codex evidence covers the head commit yet.
"""
import json
import re
import subprocess
import sys

BOT = "chatgpt-codex-connector[bot]"
MARKER = re.compile(r"codex-[a-z-]*review:v1 (\{.*?\}) -->")
P1 = re.compile(r"!\[P[01] Badge\]")


def gh(*args):
    done = subprocess.run(["gh", *args], capture_output=True, text=True)
    if done.returncode:
        raise RuntimeError(done.stderr.strip() or f"gh {' '.join(args)} failed")
    return json.loads(done.stdout or "null")


def pages(path):
    return [item for page in gh("api", "--paginate", "--slurp", path) for item in page]


def state(repo, pr, call=gh, pages=pages):
    head = call("pr", "view", pr, "--repo", repo, "--json", "headRefOid")["headRefOid"]
    head_date = call("api", f"repos/{repo}/commits/{head}")["commit"]["committer"]["date"]
    reactions = [r for r in pages(f"repos/{repo}/issues/{pr}/reactions") if r["user"]["login"] == BOT]
    inline = [c for c in pages(f"repos/{repo}/pulls/{pr}/comments")
              if c["user"]["login"] == BOT and c.get("original_commit_id") == head]
    reviews = [r for r in pages(f"repos/{repo}/pulls/{pr}/reviews")
               if r["user"]["login"] == BOT and r.get("commit_id") == head]
    markers = [json.loads(m.group(1)) for c in pages(f"repos/{repo}/issues/{pr}/comments")
               if c["user"]["login"] == BOT for m in MARKER.finditer(c["body"])]
    p1 = sum(bool(P1.search(c["body"])) for c in inline)
    if any(r["content"] == "eyes" for r in reactions):
        return 3, f"running: Codex is reviewing {head[:9]}"
    if inline or reviews:
        return 1, f"findings on {head[:9]}: {len(inline)} line comment(s), {p1} at P0/P1, {len(reviews)} review(s)"
    if any(m.get("headSha") == head and m.get("status") == "completed" for m in markers):
        return 0, f"clean: Codex summary marks {head[:9]} completed with no findings on it"
    if any(r["content"] == "+1" and r["created_at"] > head_date for r in reactions):
        return 0, f"clean: Codex +1 is newer than {head[:9]} and no findings were made on it"
    return 4, f"not reviewed: no Codex evidence covers {head[:9]}"


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
