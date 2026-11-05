#!/usr/bin/env python3
"""POC pre-tool guard: a `gh pr merge` passes only when some task's newest
merge/ask-N.json carries that PR and its saved head equals --match-head-commit.

usage: merge_guard.py claude|codex   (hook JSON on stdin)
State roots: MERGE_GUARD_STATE, colon-separated directories searched for
*/merge/ask-N.json and _archive/*/merge/ask-N.json.
"""
import json, os, re, shlex, subprocess, sys
from pathlib import Path

LOG = Path("/tmp/merge-guard-poc/hook.log")
MERGE = re.compile(r"(?<![\w/-])(?:[\w./-]*/)?gh\s+pr\s+merge\b")


def log(obj):
    with LOG.open("a") as f:
        f.write(json.dumps(obj) + "\n")


def newest_records():
    for root in filter(None, os.environ.get("MERGE_GUARD_STATE", "").split(":")):
        for merge_dir in list(Path(root).glob("*/merge")) + list(Path(root).glob("_archive/*/merge")):
            asks = [(int(m.group(1)), p) for p in merge_dir.glob("ask-*.json")
                    if (m := re.fullmatch(r"ask-(\d+)\.json", p.name))]
            if asks:
                try:
                    yield merge_dir.parent.name, json.loads(max(asks)[1].read_text())
                except (OSError, ValueError):
                    continue


def parse(segment, cwd):
    try:
        words = shlex.split(segment)
    except ValueError:
        return None, "the merge command cannot be parsed"
    i = next((k for k in range(len(words) - 2) if words[k].endswith("gh") and words[k + 1:k + 3] == ["pr", "merge"]), None)
    if i is None:
        return None, "the merge command cannot be parsed"
    args, number, repo, head = words[i + 3:], None, None, None
    k = 0
    while k < len(args):
        a = args[k]
        if a in ("--repo", "-R", "--match-head-commit") and k + 1 < len(args):
            value = args[k + 1]
            repo, head = (value, head) if a != "--match-head-commit" else (repo, value)
            k += 2
            continue
        if a.startswith("--repo="):
            repo = a.split("=", 1)[1]
        elif a.startswith("--match-head-commit="):
            head = a.split("=", 1)[1]
        elif not a.startswith("-") and number is None:
            number = a
        k += 1
    if number and (m := re.fullmatch(r"https://github\.com/([^/]+/[^/]+)/pull/(\d+)", number)):
        repo, number = m.group(1), m.group(2)
    if repo is None:
        try:
            url = subprocess.run(["git", "-C", cwd, "remote", "get-url", "origin"], capture_output=True, text=True).stdout.strip()
            m = re.search(r"github\.com[:/]([^/]+/[^/.]+)", url)
            repo = m.group(1) if m else None
        except OSError:
            repo = None
    if not (number and number.isdigit() and repo and head):
        return None, "the merge names no PR number, repository or --match-head-commit head"
    return (f"{repo}#{number}", head.lower()), None


def verdict(command, cwd):
    hits = list(MERGE.finditer(command))
    if not hits:
        return "pass", None
    if len(hits) > 1:
        return "stop", "more than one gh pr merge in one command"
    tail = command[hits[0].start():]
    segment = re.split(r"\s*(?:&&|\|\||;|\||\n)\s*", tail, maxsplit=1)[0].strip().strip("'\"")
    target, problem = parse(segment, cwd)
    if problem:
        return "stop", problem
    pr, head = target
    for task, rec in newest_records():
        if rec.get("pr") == pr and len(head) >= 7 and str(rec.get("head", "")).lower().startswith(head):
            return "pass", f"carried by {task} merge record"
    return "stop", f"no task's newest merge/ask-N.json carries {pr} at {head}"


def main():
    host = sys.argv[1]
    payload = json.load(sys.stdin)
    command = (payload.get("tool_input") or {}).get("command") or ""
    if isinstance(command, list):
        command = " ".join(command)
    result, why = verdict(command, payload.get("cwd") or os.getcwd())
    log({"host": host, "event": payload.get("hook_event_name"), "tool": payload.get("tool_name"),
         "mode": payload.get("permission_mode"), "command": command, "result": result, "why": why})
    if result == "pass":
        return 0
    reason = f"merge guard: {why}. Ask the Captain before this merge."
    decision = "ask" if host == "claude" and os.environ.get("MERGE_GUARD_ROUTE", "ask") == "ask" else "deny"
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": decision,
                                             "permissionDecisionReason": reason}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
