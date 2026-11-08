#!/usr/bin/env python3
"""Stop an uncarried gh pr merge; record a separately approved PR/head.

Usage: merge_guard.py claude|codex (hook JSON on stdin)
       merge_guard.py record STATE --pr OWNER/REPO#N --head SHA --question-file FILE --answer WORDS
"""
import argparse
import datetime
import json
import os
import posixpath
import re
import shlex
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

# see docs/adr/0063-a-merge-no-record-carries-is-stopped-by-a-user-registered-hook.md
MERGE = re.compile(r"\bgh\b[\s\S]*(?:\bpr\b[\s\S]*\bmerge\b|/pulls/[^/\s]+/merge|\bgraphql\b)")
SHELL_END = {";", "&&", "||", "|", "&", "(", ")", ">", ">>", "<", "<<"}
BUILTINS = set("auth browse codespace discussion gist issue org project release repo skill cache run workflow alias attestation completion config extension gpg-key label licenses ruleset search secret ssh-key status variable help".split())
PR_COMMANDS = set("checks checkout close comment create diff edit list lock ready reopen review status unlock update-branch view --help".split())
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


def repo_args(args):
    cleaned, repo, k = [], None, 0
    while k < len(args):
        arg = args[k]
        value = None
        if arg in ("--repo", "-R"):
            k += 1
            value = args[k] if k < len(args) else ""
        elif arg.startswith("--repo="):
            value = arg.split("=", 1)[1]
        elif arg.startswith("-R"):
            value = arg[2:].removeprefix("=")
        else:
            cleaned.append(arg)
        if value is not None:
            if not REPO.fullmatch(value) or (repo and repo.lower() != value.lower()):
                raise ValueError("the repository flags are missing, unsupported or disagree")
            repo = value
        k += 1
    return cleaned, repo


def check_wrapper(prefix):
    while prefix:
        wrapper, prefix = Path(prefix[0]).name, prefix[1:]
        if wrapper not in ("env", "command"):
            raise ValueError("the gh wrapper cannot be parsed")
        if wrapper == "command" and prefix and prefix[0] == "-p":
            prefix = prefix[1:]
        if prefix and prefix[0] == "--":
            prefix = prefix[1:]


def check_api(args):
    endpoint, k = None, 0
    valued = set("-X --method -f --raw-field -F --field -H --header --hostname --input --cache -q --jq -p --preview -t --template".split())
    switches = set("-i --include --paginate --silent --slurp --verbose --allow-escape-sequences".split())
    while k < len(args):
        arg = args[k]
        if arg in valued:
            k += 1
            if k == len(args):
                raise ValueError("the gh api flag has no value")
        elif arg in switches:
            pass
        elif arg.startswith("--") and "=" in arg and arg.split("=", 1)[0] in valued:
            pass
        elif len(arg) > 2 and arg[:2] in valued:
            pass
        elif arg.startswith("-") or endpoint is not None:
            raise ValueError("the gh api command cannot be parsed")
        else:
            endpoint = arg
        k += 1
    if not endpoint or any(char in endpoint for char in "$`\\()"):
        raise ValueError("the gh api endpoint cannot be parsed")
    for _ in range(8):
        decoded = unquote(endpoint)
        if decoded == endpoint:
            break
        endpoint = decoded
    if "%" in endpoint:
        raise ValueError("the gh api endpoint cannot be decoded")
    path = posixpath.normpath(urlsplit(endpoint).path)
    if re.search(r"(?:^|/)pulls/[^/]+/merge-async(?:/|$)", path):
        raise ValueError("FO never enables auto-merge; asynchronous merges and merge queues are not carried by a saved head")
    if path == "graphql" or path.endswith("/graphql") or re.search(r"(?:^|/)pulls/[^/]+/merge(?:/|$)", path):
        raise ValueError("FO never enables auto-merge; API merges or opaque GraphQL need synchronous gh pr merge with --match-head-commit")


def parse(command, cwd):
    lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|()<>")
    lexer.whitespace_split = True
    lexer.commenters = ""
    words = list(lexer)
    merges = []
    for i, word in enumerate(words):
        if Path(word).name != "gh":
            continue
        end = next((j for j in range(i + 1, len(words)) if words[j] in SHELL_END), len(words))
        args, repo = repo_args(words[i + 1:end])
        if args[:2] == ["pr", "merge"]:
            start = max((j + 1 for j in range(i) if words[j] in SHELL_END), default=0)
            check_wrapper(words[start:i])
            merges.append((args[2:], repo, start > 0))
        elif args[:1] == ["api"]:
            check_api(args[1:])
        elif (not args or (args[0] == "pr" and (len(args) < 2 or args[1] not in PR_COMMANDS))
              or (args[0] not in BUILTINS | {"pr", "--version", "--help"})
              or args[:2] == ["extension", "exec"]):
            raise ValueError("the gh command or alias cannot be parsed")
    if not merges:
        if MERGE.search(command):
            raise ValueError("the merge command cannot be parsed")
        return None
    if len(merges) != 1:
        raise ValueError("more than one gh pr merge in one command")
    args, repo, context_changed = merges[0]
    number = head = None
    valued = {"--subject", "--body", "--body-file", "--author-email", "-t", "-b", "-F", "-A"}
    switches = {"--admin", "--disable-auto", "--delete-branch", "--merge", "--rebase", "--squash", "--help"}
    k = 0
    while k < len(args):
        arg = args[k]
        if arg.split("=", 1)[0] == "--auto":
            raise ValueError("FO never enables auto-merge; a saved head does not authorize a deferred merge")
        elif arg == "--match-head-commit":
            k += 1
            head = args[k] if k < len(args) else ""
        elif arg.startswith("--match-head-commit="):
            head = arg.split("=", 1)[1]
        elif arg in valued:
            k += 1
            if k == len(args):
                raise ValueError("the merge flag has no value")
        elif "=" in arg and arg.split("=", 1)[0] in valued | switches:
            pass
        elif arg in switches or re.fullmatch(r"-[dmrs]+", arg):
            pass
        elif arg.startswith("-"):
            raise ValueError("the merge flag cannot be parsed")
        else:
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
        if context_changed or os.environ.get("GH_REPO"):
            raise ValueError("the shell context or GH_REPO needs an explicit repository")
        remote = git(cwd, "remote", "get-url", "origin")
        m = re.fullmatch(r"(?:https://github\.com/|git@github\.com:|ssh://git@github\.com/)([^/]+/[^/]+?)(?:\.git)?/?", remote)
        repo = m.group(1) if m else None
    if os.environ.get("GH_HOST", "github.com").lower() not in ("", "github.com"):
        raise ValueError("GH_HOST must be github.com for this merge guard")
    if not (number and re.fullmatch(r"[1-9]\d*", number) and repo and REPO.fullmatch(repo)
            and head and re.fullmatch(r"[0-9a-fA-F]{7,40}", head)):
        raise ValueError("the merge needs a PR number, repository and 7-to-40-hex --match-head-commit")
    return f"{repo}#{number}".lower(), head.lower()


def verdict(command, cwd, roots=None):
    try:
        target = parse(command, cwd)
        if target is None:
            return "pass", None
        pr, head = target
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
    if args.head[:7].lower() not in question.lower():
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
