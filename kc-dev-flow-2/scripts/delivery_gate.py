#!/usr/bin/env python3
"""Check what FO is about to ask the Captain to merge.

Usage: delivery_gate.py check <task file> --pr <owner/repo>#<N> --text-file <file> [--head <sha>]

The validated candidate is the first 7-40 character hexadecimal SHA containing a digit within 160 characters
after the first verdict form of the latest `## Stage Report: validation` section that has one, when that form
says PASSED. The form the validation skill states is `Verdict PASSED at <sha>`; `Verdict: PASSED`,
`Verdict recommended: PASSED` (also `recommendation:`) and `Verdict: recommend PASSED` are read too, and `*` is ignored.
A form counts at the start of a line (after list, heading or DONE/SKIPPED/FAILED markers) or after `.`, `!` or `?`;
one after a word, such as `Independent Verdict: PASSED`, and one naming both outcomes are skipped.
A REJECTED first counting form, or no counting form, names no candidate.
It is compared, as a prefix of equal length, with the PR head (--head, else `gh pr view --json headRefOid`).
--text-file holds the gate question and summary: each `Second reviewer: <X> because` needs `<X> not run: <reason>`
or, in one sentence naming <X>, a `review:<id>` or `comment:<id>` token.
Exit 0 when both hold; 1 when the head differs or a second reviewer has no stated outcome (both printed);
2 when no passing report names a candidate, the head cannot be read, or an input is unusable.
Each exit ends with one `next:` line, or one per problem for exit 1, naming what FO does with the ask.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

SHA = r"(?<![0-9A-Za-z])(?=[0-9a-f]*\d)([0-9a-f]{7,40})(?![0-9A-Za-z])"
VERDICT = re.compile(r"\bVerdict(?:[ \t]+recommend(?:ed|ation)?)?:?[ \t]+(?:recommend[ \t]+)?(PASSED|REJECTED)\b([ \t]*(?:or|/)[ \t]*(?:PASSED|REJECTED)\b)?")
LINE_START = re.compile(r"[ \t]*(?:(?:[-+]|\d+[.)]|#+)[ \t]+)?(?:(?:DONE|SKIPPED|FAILED):[ \t]*)?")
SENTENCE_END = re.compile(r"[.!?][ \t]+$")
CANDIDATE = re.compile(r"[\s\S]{0,160}?" + SHA)
REPORT = re.compile(r"^## Stage Report: validation\b", re.M)
SECOND_REVIEWER = re.compile(r"Second reviewer:\s*([\w.-]+)\s+because", re.I)
OUTCOME_TOKEN = re.compile(r"\b(?:review|comment):\d+")
PR = re.compile(r"^([\w.-]+/[\w.-]+)#(\d+)$")


def validated_candidate(task_text):
    sections = re.split(r"^(?=## )", task_text, flags=re.M)
    for section in reversed([s for s in sections if REPORT.match(s)]):
        found = first_passing_candidate(section.replace("*", ""))
        if found:
            return found
    return None


def first_passing_candidate(section):
    for verdict in VERDICT.finditer(section):
        before = section[section.rfind("\n", 0, verdict.start()) + 1:verdict.start()]
        if verdict.group(2) or not (LINE_START.fullmatch(before) or SENTENCE_END.search(before)):
            continue
        if verdict.group(1) != "PASSED":
            return None
        found = CANDIDATE.match(section, verdict.end(1))
        return found.group(1) if found else None
    return None


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

    candidate = validated_candidate(task_text)
    if not candidate:
        holds.append(f"no passing validation report in {task} names a candidate SHA")
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
    if candidate and head:
        length = min(len(candidate), len(head))
        if candidate[:length] != head[:length]:
            problems.append(f"PR head {head} differs from validated candidate {candidate} "
                            f"(latest passing validation report in {task})")
            nexts.append("next: hold the ask; revalidate this head or tell the Captain the difference.")

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
        print("next: hold the ask and show the Captain these lines.")
        return 2
    print(f"PR head {head} equals validated candidate {candidate}; no second reviewer outcome is missing")
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
