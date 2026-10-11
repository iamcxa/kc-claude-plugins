#!/usr/bin/env python3
"""Report the Codex review state of a pull request's head commit.

Usage: codex_review.py <owner/repo> <pr>
The latest Codex result on the head decides, and its evidence id is printed so a round
is counted once per id.
Exit 0 clean: that result is a "Codex Review:" comment naming the head as its reviewed
  commit, or Codex's summary marking the head completed.
Exit 1 findings: that result is a Codex review, or line finding, made on the head.
Exit 2 configuration error: bad arguments or a gh call that failed.
Exit 3 running: Codex's eyes reaction is on the pull request.
Exit 4 not reviewed: no Codex evidence covers the head commit yet, or the head moved while reading.
"""
import json
import re
import subprocess
import sys

BOT = "chatgpt-codex-connector[bot]"
SUMMARY = "<!-- codex-pull-request-review-summary -->"
MARKER = re.compile(r"^<!-- codex-[a-z-]+-review:v1 (\{[^\n]*\}) -->$", re.M)
P1 = re.compile(r"!\[P[01] Badge\]")
REVIEWED = re.compile(r"^\*\*Reviewed commit:\*\* `([0-9a-f]{7,40})`$", re.M)


def gh(*args):
    done = subprocess.run(["gh", *args], capture_output=True, text=True)
    if done.returncode:
        raise RuntimeError(done.stderr.strip() or f"gh {' '.join(args)} failed")
    return json.loads(done.stdout or "null")


def pages(path):
    return [item for page in gh("api", "--paginate", "--slurp", path) for item in page]


def state(repo, pr, call=gh, pages=pages):
    head = call("pr", "view", pr, "--repo", repo, "--json", "headRefOid")["headRefOid"]
    reactions = [r for r in pages(f"repos/{repo}/issues/{pr}/reactions") if r["user"]["login"] == BOT]
    inline = [c for c in pages(f"repos/{repo}/pulls/{pr}/comments")
              if c["user"]["login"] == BOT and c.get("original_commit_id") == head]
    reviews = [r for r in pages(f"repos/{repo}/pulls/{pr}/reviews")
               if r["user"]["login"] == BOT and r.get("commit_id") == head]
    issue = [c for c in pages(f"repos/{repo}/issues/{pr}/comments") if c["user"]["login"] == BOT]
    evidence = []
    for r in reviews:
        own = [c for c in inline if c.get("pull_request_review_id") == r["id"]]
        p1 = sum(bool(P1.search(c["body"])) for c in own)
        evidence.append((r["submitted_at"], f"review:{r['id']}", 1, f"{len(own)} line finding(s), {p1} at P0/P1"))
    loose = [c for c in inline if c.get("pull_request_review_id") not in {r["id"] for r in reviews}]
    for c in loose:
        evidence.append((c["created_at"], f"comment:{c['id']}", 1, "1 line finding"))
    for c in issue:
        if c["body"].startswith("Codex Review:") and any(head.startswith(m.group(1)) for m in REVIEWED.finditer(c["body"])):
            evidence.append((c["created_at"], f"comment:{c['id']}", 0, "Codex Review comment names the head"))
        if c["body"].startswith(SUMMARY):
            for m in MARKER.finditer(c["body"].split("\n## ", 1)[0]):
                meta = json.loads(m.group(1))
                if (meta.get("repository") == repo and str(meta.get("pullRequestNumber")) == str(pr)
                        and meta.get("headSha") == head and meta.get("status") == "completed"):
                    evidence.append((c["updated_at"], f"summary:{c['id']}@{c['updated_at']}", 0, "summary marks the head completed"))
    if call("pr", "view", pr, "--repo", repo, "--json", "headRefOid")["headRefOid"] != head:
        return 4, f"not reviewed: the head moved from {head[:9]} while its review was being read"
    if any(r["content"] == "eyes" for r in reactions):
        return 3, f"running: a Codex review is in progress; head {head[:9]}"
    if not evidence:
        return 4, f"not reviewed: no Codex evidence covers {head[:9]}"
    when, ident, code, detail = max(evidence)
    word = "findings" if code else "clean"
    return code, f"{word} on {head[:9]}: {detail}; evidence={ident} at {when}"


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
