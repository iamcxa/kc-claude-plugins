#!/usr/bin/env python3
"""List the chief-engineer and engineering-reviewer calls a committed task state owes.

Usage: role_triggers.py <state checkout> <task slug> [--rev REV]
Reads the task at REV (default HEAD) from committed bytes, never the disk; live or archived, flat or folder.
Event A: a `- Cycle N` line with N >= 3 under `### Feedback Cycles`; owes a `Reviewer:` line for chief-engineer.
Event B: a `### Amendment N` under `## Captain amendments` whose `Supersedes:` or `Design:` value does not start
with `none`; owes one for engineering-reviewer. Fenced blocks are skipped everywhere.
A call is `Reviewer: <agent> <model> <date> — <question>` whose question names `Cycle 3` or `Amendment N` (for B the
date is not before the entry's). A waiver is `Reviewer: <agent> not run: <reason>` that also names the token.
Records count only under `## FO alignment` and its subheadings.
Exit 0 nothing owed; stdout counts the events read. Exit 1 one `next:` line per owed event. Exit 2 cannot tell
(usage, not a git work tree, REV names no commit, no task for the slug); stdout names the cause.
"""
import re
import subprocess
import sys
from pathlib import Path

FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
SPACE = "[\t\n\v\f\r \x85\xa0\u1680\u2000-\u200a\u2028\u2029\u202f\u205f\u3000]*"
HEADING = re.compile(rf"^{SPACE}(#{{1,6}})\s")


def titled(hashes, text):
    return re.compile(rf"^{SPACE}{hashes} {text}{SPACE}$", re.I)


AMENDMENTS_SECTION = titled("##", "Captain amendments")
CYCLES_SECTION = titled("###", "Feedback Cycles")
ALIGNMENT_SECTION = titled("##", "FO alignment")
CYCLE = re.compile(r"^- Cycle (\d+)\b")
AMENDMENT = re.compile(rf"^{SPACE}### Amendment (\d+)\b", re.I)
DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
FIELD = re.compile(r"^(Supersedes|Design):[ \t]*(.*?)[ \t]*$")
MARK = r"(?:-[ \t]+)?Reviewer:[ \t]*(?:kc-dev-flow-2:)?"

QUESTION = {
    "chief-engineer": "what is the smallest next step, given the findings so far?",
    "engineering-reviewer": "does this amendment withdraw what the Captain approved, and what does that change in the build?",
}


class Unverifiable(Exception):
    pass


def git(state, *args):
    done = subprocess.run(["git", "-C", str(state), *args], capture_output=True)
    return done.returncode, done.stdout.decode("utf-8", "replace")


def parse(args):
    rev = "HEAD"
    if "--rev" in args:
        at = args.index("--rev")
        if at + 1 >= len(args):
            raise Unverifiable("usage: --rev needs a value")
        rev = args[at + 1]
        args = args[:at] + args[at + 2:]
    if len(args) != 2 or "/" in args[1] or args[1] in ("", ".", ".."):
        raise Unverifiable("usage: role_triggers.py <state checkout> <task slug> [--rev REV]")
    return Path(args[0]), args[1], rev


def read_task(state, slug, rev):
    if git(state, "rev-parse", "--is-inside-work-tree")[1].strip() != "true":
        raise Unverifiable(f"{state} is not a git work tree")
    if git(state, "rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}")[0]:
        raise Unverifiable(f"--rev {rev} names no commit in {state}")
    for base in ("", "_archive/"):
        for path in (f"{base}{slug}/index.md", f"{base}{slug}.md"):
            code, out = git(state, "show", f"{rev}:./{path}")
            if code == 0:
                return out
    raise Unverifiable(f"no task file for {slug} at {rev} in {state}")


def outside_fences(text):
    marker = None
    for line in text.split("\n"):
        fence = FENCE.match(line)
        if marker is None:
            if fence:
                marker = fence.group(1)
                continue
            yield line
        elif fence and fence.group(1)[0] == marker[0] and len(fence.group(1)) >= len(marker):
            marker = None


def events(lines):
    """Return (cycle numbers, [(amendment number, entry date or None)]) for amendments that replace something."""
    cycles, amendments = [], []
    section = ""
    entry = None
    for line in lines:
        heading = HEADING.match(line)
        if heading and len(heading.group(1)) <= 3:
            amendment = AMENDMENT.match(line)
            if not amendment:
                section = line
            found = DATE.search(line)
            entry = [int(amendment.group(1)), found.group(0) if found else None, False] \
                if amendment and AMENDMENTS_SECTION.match(section) else None
            continue
        cycle = CYCLE.match(line)
        if CYCLES_SECTION.match(section) and cycle:
            cycles.append(int(cycle.group(1)))
        field = FIELD.match(line)
        if entry and not entry[2] and field and field.group(2) and not field.group(2).lower().startswith("none"):
            entry[2] = True
            amendments.append((entry[0], entry[1]))
    return cycles, amendments


def cleared(lines, agent, token, latest=None):
    name = re.escape(agent)
    call = re.compile(rf"^{MARK}{name}[ \t]+\S+[ \t]+({DATE.pattern})[ \t]+[—–-][ \t]+(.+)$")
    waiver = re.compile(rf"^{MARK}{name}[ \t]+not run:[ \t]*(.*)$")
    for line in lines:
        line = line.strip()
        made, waived = call.match(line), waiver.match(line)
        if made and re.search(token, made.group(2)) and (latest is None or made.group(1) >= latest):
            return True
        if waived and re.search(token, waived.group(1)):
            if re.sub(r"[\s()\[\]:;,.\-—–]+", "", re.sub(token, "", waived.group(1))):
                return True
    return False


def alignment(lines):
    keep = False
    for line in lines:
        heading = HEADING.match(line)
        if heading and len(heading.group(1)) <= 2:
            keep = bool(ALIGNMENT_SECTION.match(line))
        if keep:
            yield line


def owed_line(slug, agent, happened, token):
    return (f"next: {slug} {happened}; dispatch kc-dev-flow-2:{agent} with the question \"{token}: {QUESTION[agent]}\" "
            f"and record `Reviewer: kc-dev-flow-2:{agent} <model> <date> — <question>` under ## FO alignment; "
            f"or, if you will not, record `Reviewer: kc-dev-flow-2:{agent} not run: <reason> {token}` instead.")


def check(state, slug, rev):
    lines = list(outside_fences(read_task(state, slug, rev)))
    cycles, amendments = events(lines)
    records = list(alignment(lines))
    owed, seen = [], 0
    if any(number >= 3 for number in cycles):
        seen += 1
        if not cleared(records, "chief-engineer", r"\bCycle 3\b"):
            owed.append(owed_line(slug, "chief-engineer", "has a third Feedback Cycle", "Cycle 3"))
    for number, date in amendments:
        seen += 1
        token = f"Amendment {number}"
        if not cleared(records, "engineering-reviewer", rf"\b{token}\b", date):
            owed.append(owed_line(slug, "engineering-reviewer", f"has a Captain amendment {number} that replaces approved text", token))
    if owed:
        return 1, "\n".join(owed)
    return 0, f"role triggers: {seen} event(s) read at {rev}, each with a call or a waiver."


def main(argv=None):
    args = sys.argv[1:] if argv is None else list(argv)
    try:
        state, slug, rev = parse(args)
        code, message = check(state, slug, rev)
    except Unverifiable as err:
        print(f"cannot tell whether a chief-engineer or engineering-reviewer call is owed: {err}. Hold and report the cause.")
        return 2
    print(message)
    return code


if __name__ == "__main__":
    sys.exit(main())
