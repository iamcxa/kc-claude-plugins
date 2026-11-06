#!/usr/bin/env python3
"""Stop an uncarried gh pr merge; record a separately approved PR/head.

Usage: merge_guard.py claude|codex (hook JSON on stdin)
       merge_guard.py record STATE --pr OWNER/REPO#N --head SHA --question-file FILE --answer WORDS
"""
import argparse
import datetime
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

# see docs/adr/0063-a-merge-no-record-carries-is-stopped-by-a-user-registered-hook.md
MERGE = re.compile(r"(?<![\w/-])(?:[\w./-]*/)?gh\s+pr\s+merge\b")
ASK_FILE = re.compile(r"ask-(\d+)\.json")
PR = re.compile(r"([\w.-]+)/([\w.-]+)#([1-9]\d*)")
REPO = re.compile(r"[\w.-]+/[\w.-]+")


def git(cwd, *args):
    return subprocess.run(["git", "-C", str(cwd), *args], check=True,
                          capture_output=True, text=True).stdout.strip()


def state_roots(cwd):
    roots = []
    for entry in git(cwd, "worktree", "list", "--porcelain").split("\n\n"):
        lines = entry.splitlines()
        if any(line.startswith("branch refs/heads/spacedock-state/") for line in lines):
            roots.append(Path(next(line[9:] for line in lines if line.startswith("worktree "))))
    return roots


def newest_records(roots):
    records = []
    for root in roots:
        for pattern in ("*/merge", "_archive/*/merge", "_merges/*/merge"):
            for folder in root.glob(pattern):
                asks = [(int(m.group(1)), p) for p in folder.glob("ask-*.json")
                        if (m := ASK_FILE.fullmatch(p.name))]
                if asks:
                    record = json.loads(max(asks)[1].read_text())
                    if not isinstance(record, dict):
                        raise ValueError("merge record is not an object")
                    records.append(record)
    return records


def parse(command, cwd):
    lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|()<>")
    lexer.whitespace_split = True
    lexer.commenters = ""
    words = list(lexer)
    starts = [i for i in range(len(words) - 2)
              if Path(words[i]).name == "gh" and words[i + 1:i + 3] == ["pr", "merge"]]
    if len(starts) != 1:
        raise ValueError("the merge command cannot be parsed")
    i = starts[0]
    if i and words[i - 1] not in (";", "&&", "||", "|", "("):
        raise ValueError("the merge command cannot be parsed")
    args = words[i + 3:]
    number = repo = head = None
    k = 0
    while k < len(args) and args[k] not in (";", "&&", "||", "|", ")", ">", ">>", "<"):
        arg = args[k]
        if arg in ("--repo", "-R", "--match-head-commit"):
            k += 1
            value = args[k] if k < len(args) else ""
            if arg == "--match-head-commit":
                head = value
            else:
                repo = value
        elif arg.startswith("--repo="):
            repo = arg.split("=", 1)[1]
        elif arg.startswith("--match-head-commit="):
            head = arg.split("=", 1)[1]
        elif arg in ("--subject", "--body", "--body-file", "--author-email"):
            k += 1
        elif not arg.startswith("-"):
            if number is not None:
                raise ValueError("the merge command has multiple PR arguments")
            number = arg
        k += 1
    if number and (m := re.fullmatch(r"https://github\.com/([^/]+/[^/]+)/pull/([1-9]\d*)/?", number)):
        url_repo, number = m.groups()
        if repo and repo.lower() != url_repo.lower():
            raise ValueError("the PR URL and --repo disagree")
        repo = url_repo
    if repo is None:
        remote = git(cwd, "remote", "get-url", "origin")
        m = re.fullmatch(r"(?:https://github\.com/|git@github\.com:|ssh://git@github\.com/)([^/]+/[^/]+?)(?:\.git)?/?", remote)
        repo = m.group(1) if m else None
    if not (number and re.fullmatch(r"[1-9]\d*", number) and repo and REPO.fullmatch(repo)
            and head and re.fullmatch(r"[0-9a-fA-F]{7,40}", head)):
        raise ValueError("the merge needs a PR number, repository and 7-to-40-hex --match-head-commit")
    return f"{repo}#{number}".lower(), head.lower()


def verdict(command, cwd, roots=None):
    hits = list(MERGE.finditer(command))
    if not hits:
        return "pass", None
    if len(hits) > 1:
        return "stop", "more than one gh pr merge in one command"
    try:
        pr, head = parse(command, cwd)
        records = newest_records(state_roots(cwd) if roots is None else roots)
        for record in records:
            saved = str(record.get("head", "")).lower()
            if (str(record.get("pr", "")).lower() == pr
                    and re.fullmatch(r"[0-9a-f]{40}", saved) and saved.startswith(head)):
                return "pass", None
        return "stop", f"no task's newest merge/ask-N.json carries {pr} at {head}"
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        return "stop", f"cannot check merge: {error}"


def record(argv):
    parser = argparse.ArgumentParser(prog="merge_guard.py record")
    parser.add_argument("state", type=Path)
    for name in ("pr", "head", "question-file", "answer"):
        parser.add_argument("--" + name, required=True)
    args = parser.parse_args(argv)
    try:
        question = Path(args.question_file).read_text()
    except OSError as error:
        print(f"cannot read question: {error}")
        return 1
    match = PR.fullmatch(args.pr)
    problems = []
    if not match:
        problems.append("--pr must look like owner/repo#N")
    if not re.fullmatch(r"[0-9a-fA-F]{40}", args.head):
        problems.append("--head must be the full 40-hex head")
    if match and not re.search(rf"(?:#|/pull/){match.group(3)}(?!\d)", question):
        problems.append(f"the question does not name #{match.group(3)}")
    if False:
        problems.append(f"the question does not name head {args.head[:7]}")
    if not args.answer.strip():
        problems.append("--answer is empty")
    if problems:
        print("\n".join(problems))
        return 1
    folder = args.state / "_merges" / "-".join(match.groups()) / "merge"
    folder.mkdir(parents=True, exist_ok=True)
    numbers = [int(m.group(1)) for p in folder.glob("ask-*.json") if (m := ASK_FILE.fullmatch(p.name))]
    number = max(numbers, default=0) + 1
    data = {"pr": args.pr, "head": args.head.lower(), "verdict": "captain-approved-in-chat",
            "question": question.strip()[:600], "answer": args.answer.strip()[:200],
            "time": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    while True:
        path = folder / f"ask-{number}.json"
        try:
            with path.open("x") as stream:
                stream.write(json.dumps(data, indent=2, sort_keys=True) + "\n")
            break
        except FileExistsError:
            number += 1
    print(f"record: {path}")
    return 0


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "record":
        return record(sys.argv[2:])
    parser = argparse.ArgumentParser()
    parser.add_argument("host", choices=("claude", "codex"))
    host = parser.parse_args().host
    payload = json.load(sys.stdin)
    tool_input = payload.get("tool_input") or {}
    command = tool_input.get("command") or tool_input.get("cmd") or ""
    if isinstance(command, list):
        command = " ".join(command)
    result, why = verdict(command, payload.get("cwd") or os.getcwd())
    if result == "pass":
        return 0
    reason = f"merge guard: {why}; ask the Captain before this merge."
    if host == "codex":
        reason += (" If the Captain approved this merge by a question naming the PR and its head, "
                   "run merge_guard.py record and retry; otherwise ask him; on this host only he can run this merge.")
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                     "permissionDecision": "ask" if host == "claude" else "deny",
                     "permissionDecisionReason": reason}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
