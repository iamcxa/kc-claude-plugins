#!/usr/bin/env python3
"""Report the Codex review state of a pull request's head commit.

Usage: codex_review.py <owner/repo> <pr>
The latest Codex result on the head decides, and its evidence id is printed so a round
is counted once per id.
Exit 0 clean: that result is Codex's "Didn't find any major issues" on the head, as a
  comment naming the head or a badge-free review of it, or its summary marking the code
  review of the head completed with no finding, and no finding on the head before it.
Exit 1 findings: that result carries a severity badge on the head, in a review, a line
  comment, or a comment that names the head or names no commit (fail closed).
Exit 2 configuration error: bad arguments or a gh call that failed.
Exit 3 running: Codex's eyes reaction is on the pull request.
Exit 4 not reviewed: no Codex evidence covers the head commit yet, or the head moved while reading.
Exit 5 not recognized: no evidence covers the head, or the newest evidence is clean and a newer Codex comment
  names the head in a shape this reader does not read (unrecognized=comment:<id>, its first 120 characters
  quoted); no evidence= token, so no round.
"""
import json
import re
import subprocess
import sys

BOT = "chatgpt-codex-connector[bot]"
SUMMARY = "<!-- codex-pull-request-review-summary -->"
MARKER = re.compile(r"^<!-- codex-review-state:v1 (\{[^\n]*\}) -->$", re.M)
P1 = re.compile(r"!\[P[01] Badge\]")
BADGE = re.compile(r"!\[P\d Badge\]")
CLEAN = "Didn't find any major issues"
RECEIPT = "<!-- codex-review-receipt:v1 -->\n"
REVIEWED = re.compile(r"^\*\*Reviewed commit:\*\* `([0-9a-f]{7,40})`$", re.M)


def says_review(body):
    if body.startswith(RECEIPT):
        body = body[len(RECEIPT):].lstrip("\n")
    return body.startswith("Codex Review:")


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


def state(repo, pr, call=gh, pages=pages):
    head = call("pr", "view", pr, "--repo", repo, "--json", "headRefOid")["headRefOid"]
    reactions = [r for r in pages(f"repos/{repo}/issues/{pr}/reactions") if r["user"]["login"] == BOT]
    inline = [c for c in pages(f"repos/{repo}/pulls/{pr}/comments")
              if c["user"]["login"] == BOT and c.get("original_commit_id") == head]
    reviews = [r for r in pages(f"repos/{repo}/pulls/{pr}/reviews")
               if r["user"]["login"] == BOT and r.get("commit_id") == head]
    comments = pages(f"repos/{repo}/issues/{pr}/comments")
    issue = [c for c in comments if c["user"]["login"] == BOT]
    triggers = [c for c in comments if "@codex review" in (c.get("body") or "")]
    if triggers:
        reactions += [r for r in pages(f"repos/{repo}/issues/comments/{triggers[-1]['id']}/reactions")
                      if r["user"]["login"] == BOT]
    evidence = []

    def badges(*bodies):
        return sum(len(BADGE.findall(b or "")) for b in bodies), sum(len(P1.findall(b or "")) for b in bodies)

    def names_head(body):
        return any(head.startswith(m.group(1)) for m in REVIEWED.finditer(body or ""))

    for r in reviews:
        own = [c["body"] for c in inline if c.get("pull_request_review_id") == r["id"]]
        found, p1 = badges(r.get("body"), *own)
        if not own and not found and CLEAN in (r.get("body") or ""):
            evidence.append((r["submitted_at"], f"review:{r['id']}", 0, "Codex review says no issues"))
        else:
            evidence.append((r["submitted_at"], f"review:{r['id']}", 1,
                             f"{len(own)} line finding(s), {max(found, len(own))} badge(s), {p1} at P0/P1"))
    for c in [c for c in inline if c.get("pull_request_review_id") not in {r["id"] for r in reviews}]:
        evidence.append((c["created_at"], f"comment:{c['id']}", 1, f"1 line finding, {badges(c['body'])[1]} at P0/P1"))
    for c in issue:
        found, p1 = badges(c["body"])
        if found and (names_head(c["body"]) or not REVIEWED.search(c["body"])):
            evidence.append((c["created_at"], f"comment:{c['id']}", 1, f"{found} finding(s) in a comment, {p1} at P0/P1"))
        elif says_review(c["body"]) and CLEAN in c["body"] and names_head(c["body"]):
            evidence.append((c["created_at"], f"comment:{c['id']}", 0, "Codex Review comment says no issues on the head"))
    for c in issue:
        if c["body"].startswith(SUMMARY):
            for m in MARKER.finditer(c["body"].split("\n## ", 1)[0]):
                review = json.loads(m.group(1)).get("code_review") or {}
                found_before = any(e[2] == 1 and e[0] <= c["updated_at"] for e in evidence)
                if (review.get("status") == "completed" and review.get("has_any_findings") is False
                        and review.get("commit_sha") == head and not found_before):
                    evidence.append((c["updated_at"], f"summary:{c['id']}@{head[:9]}", 0, "summary marks the code review of the head completed"))
    if call("pr", "view", pr, "--repo", repo, "--json", "headRefOid")["headRefOid"] != head:
        return 4, f"not reviewed: the head moved from {head[:9]} while its review was being read"
    if any(r["content"] == "eyes" for r in reactions):
        return 3, f"running: a Codex review is in progress; head {head[:9]}"
    known = {e[1] for e in evidence}
    odd = [c for c in issue if not c["body"].startswith(SUMMARY) and names_head(c["body"]) and f"comment:{c['id']}" not in known]
    if odd and (not evidence or max(evidence)[2] == 0 and max(c["created_at"] for c in odd) > max(evidence)[0]):
        last = max(odd, key=lambda c: c["created_at"])
        quote = " ".join(last["body"].split())[:120].replace("evidence=", "evidence:")
        return 5, f'not recognized on {head[:9]}: "{quote}"; unrecognized=comment:{last["id"]} at {last["created_at"]}'
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
