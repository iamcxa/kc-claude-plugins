#!/usr/bin/env python3
"""POC pre-tool guard: a `gh pr merge` passes only when some task's newest
merge/ask-N.json carries that PR and its saved head equals --match-head-commit.

usage: merge_guard.py claude|codex   (hook JSON on stdin)
       merge_guard.py record <state dir> --pr owner/repo#N --head <40 hex> --question-file <file> --answer <his words>
record saves <state dir>/_merges/<owner>-<repo>-<N>/merge/ask-K.json for a PR no task owns (Release, workflow sync,
learning) after the Captain approved it in chat; it refuses a question that does not name #N and the head's first 7 hex.
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
        for merge_dir in list(Path(root).glob("*/merge")) + list(Path(root).glob("_archive/*/merge")) + list(Path(root).glob("_merges/*/merge")):
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


def record(argv):
    import argparse, datetime
    ap = argparse.ArgumentParser(prog="merge_guard.py record")
    ap.add_argument("state"); ap.add_argument("--pr", required=True); ap.add_argument("--head", required=True)
    ap.add_argument("--question-file", required=True); ap.add_argument("--answer", required=True)
    a = ap.parse_args(argv)
    m = re.fullmatch(r"([\w.-]+)/([\w.-]+)#(\d+)", a.pr)
    question = Path(a.question_file).read_text()
    problems = []
    if not m:
        problems.append("--pr must look like owner/repo#N")
    if not re.fullmatch(r"[0-9a-f]{40}", a.head.lower()):
        problems.append("--head must be the full 40-hex head")
    if m and not re.search(rf"(?:#|/pull/){m.group(3)}(?!\d)", question):
        problems.append(f"the question does not name #{m.group(3)}")
    if a.head[:7].lower() not in question.lower():
        problems.append(f"the question does not name head {a.head[:7]}")
    if not a.answer.strip():
        problems.append("--answer is empty")
    if problems:
        print("\n".join(problems)); return 1
    folder = Path(a.state) / "_merges" / f"{m.group(1)}-{m.group(2)}-{m.group(3)}" / "merge"
    folder.mkdir(parents=True, exist_ok=True)
    taken = [int(x.group(1)) for q in folder.glob("ask-*.json") if (x := re.fullmatch(r"ask-(\d+)\.json", q.name))]
    path = folder / f"ask-{max(taken, default=0) + 1}.json"
    path.write_text(json.dumps({"pr": a.pr, "head": a.head.lower(), "verdict": "captain-approved-in-chat",
                                "answer": a.answer.strip()[:200], "question": question.strip()[:600],
                                "time": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")},
                               indent=2, sort_keys=True) + "\n")
    print(f"record: {path}"); return 0


def main():
    if sys.argv[1] == "record":
        return record(sys.argv[2:])
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
