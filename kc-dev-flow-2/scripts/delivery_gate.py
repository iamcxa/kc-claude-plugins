#!/usr/bin/env python3
"""Check what FO is about to ask the Captain to merge.

Usage: delivery_gate.py check <task file> --pr <owner/repo>#<N> --text-file <file> [--head <sha>]

The dispatched heads are the whole `Candidate: <40-hex head>` lines above the first `## ` heading of the
highest-numbered `<task folder>/dispatch/validation-<N>.md` record; the check reads no validation verdict.
A task whose frontmatter says `profile: prod` must also pass `validation_security.py` (saved security review at a dispatched head, every finding disposed).
The PR head is compared, as a prefix, with each line; it passes when it matches one (--head, else `gh pr view --json headRefOid`).
--text-file holds the gate question and summary: each `Second reviewer: <X> because` needs `<X> not run: <reason>`
or, in one sentence naming <X>, a `review:<id>` or `comment:<id>` token.
Exit 0 when both hold; 1 when the head differs, a second reviewer has no stated outcome or a prod task's security review fails (all printed);
2 when that record has no such line, the head cannot be read, or an input is unusable.
Each exit ends with one `next:` line, or one per problem for exit 1, naming what FO does with the ask.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

CANDIDATE = re.compile(r"^Candidate:[ \t]+([0-9a-f]{40})[ \t]*$", re.M)
RECORD = re.compile(r"^validation-(\d+)\.md$")
SECOND_REVIEWER = re.compile(r"Second reviewer:\s*([\w.-]+)\s+because", re.I)
OUTCOME_TOKEN = re.compile(r"\b(?:review|comment):\d+")
PR = re.compile(r"^([\w.-]+/[\w.-]+)#(\d+)$")


def dispatched_candidates(task):
    records = [(int(m.group(1)), path) for path in (task.with_suffix("") / "dispatch").glob("validation-*.md")
               if (m := RECORD.match(path.name))]
    if not records:
        return [], None
    path = max(records)[1]
    try:
        header = re.split(r"^## ", path.read_text(), maxsplit=1, flags=re.M)[0]
    except (OSError, UnicodeDecodeError):
        return [], path
    return CANDIDATE.findall(header), path


def run_gh(repo, number):
    done = subprocess.run(["gh", "pr", "view", number, "--repo", repo, "--json", "headRefOid"],
                          capture_output=True, text=True, timeout=60)
    if done.returncode:
        raise RuntimeError(f"gh pr view exited {done.returncode}: {done.stderr.strip()}")
    return json.loads(done.stdout)["headRefOid"]


def unstated_second_reviewers(text):
    missing = []
    for reviewer in dict.fromkeys(m.lower() for m in SECOND_REVIEWER.findall(text)):
        rest = SECOND_REVIEWER.sub("", text)
        named = re.compile(rf"(?<![\w-]){re.escape(reviewer)}(?![\w-])", re.I)
        not_run = re.search(rf"(?<![\w-]){re.escape(reviewer)}\s+not run:\s*\S", rest, re.I)
        sentences = re.split(r"(?<=[.!?])\s+|\n", rest)
        cited = any(named.search(s) and OUTCOME_TOKEN.search(s) for s in sentences)
        if not (not_run or cited):
            missing.append(reviewer)
    return missing


def check(args):
    task, text_file = Path(args.task), Path(args.text_file)
    pr = PR.match(args.pr)
    try:
        task_text, gate_text = task.read_text(), text_file.read_text()
    except OSError as error:
        print(f"cannot read input: {error}")
        return 2
    if not pr:
        print(f"--pr must look like owner/repo#N, got {args.pr}")
        return 2
    problems, holds, nexts = [], [], []

    candidates, record = dispatched_candidates(task)
    if not candidates:
        holds.append(f"no latest validation dispatch record under {task.with_suffix('')}/dispatch has a 'Candidate: <40-hex head>' line")
        nexts.append("next: hold the ask; dispatch validation of this head with a Candidate line, or tell the Captain.")
    if args.head:
        head = args.head.lower()
        if not re.fullmatch(r"[0-9a-f]{7,40}", head):
            holds.append(f"--head must be 7-40 hexadecimal characters, got {args.head}")
            head = None
    else:
        try:
            head = run_gh(*pr.groups()).lower()
        except (OSError, RuntimeError, ValueError, KeyError, subprocess.SubprocessError) as error:
            holds.append(f"cannot read the head of {args.pr}: {error}")
            head = None
    if candidates and head:
        if not any(c.startswith(head) for c in candidates):
            problems.append(f"PR head {head} differs from dispatched candidate {' '.join(candidates)} (latest validation record {record.name})")
            nexts.append("next: hold the ask; revalidate this head or tell the Captain the difference.")

    security_errors, security_note = [], None
    if candidates:
        try:
            from validation_security import check_task as security_check
            security_errors, security_note = security_check(task, candidates)
        except (OSError, UnicodeDecodeError) as error:
            security_errors = [f"cannot read the validation security review: {error}"]
    for error in security_errors:
        problems.append(error)
        nexts.append("next: hold the ask; run the validation security review at this head, or tell the Captain.")

    for reviewer in unstated_second_reviewers(gate_text):
        nexts.append("next: hold the ask until each second reviewer has an outcome.")
        problems.append(f"second reviewer {reviewer} has no stated outcome: "
                        f"add '{reviewer} not run: <reason>' or a review:<id> or comment:<id> in a sentence naming {reviewer}")

    for line in problems + holds:
        print(line)
    if problems:
        print(*dict.fromkeys(nexts), sep="\n")
        return 1
    if holds:
        print(*(dict.fromkeys(nexts) or ["next: hold the ask and show the Captain these lines."]), sep="\n")
        return 2
    print(f"PR head {head} equals dispatched candidate {head}; no second reviewer outcome is missing")
    if security_note:
        print(security_note)
    print("next: ask for merge with this text.")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(prog="delivery_gate.py", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    sub = commands.add_parser("check")
    sub.add_argument("task")
    sub.add_argument("--pr", required=True)
    sub.add_argument("--text-file", required=True)
    sub.add_argument("--head")
    return check(parser.parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())
