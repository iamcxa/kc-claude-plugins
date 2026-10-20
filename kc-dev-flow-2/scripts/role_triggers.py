#!/usr/bin/env python3
"""List the chief-engineer and engineering-reviewer calls a committed task state owes.

Usage: role_triggers.py <state checkout> <task slug> [--rev REV]
Reads the task at REV (default HEAD) from committed bytes, never the disk; live or archived, flat or folder.
Chief-engineer is owed at four repair passes: the `## Stage Report: implementation` headings minus one.
Engineering-reviewer is owed for each `### Amendment N` under `## Captain amendments` whose `Supersedes:` or
`Design:` value does not start with `none`; one line per task, on fable when the frontmatter says `profile: prod`
or the `Surfaces:` line under `## FO alignment` lists `db`, else on opus. Fenced blocks are skipped everywhere.
A call is `Reviewer: <agent> <model> <date> — <question>` whatever the question says. A chief-engineer call or
waiver clears the repair event. For engineering-reviewer a call dated no earlier than an amendment, on a model
ranked haiku < sonnet < opus < fable by its leading word and no lower than the one required, or a waiver
`Reviewer: <agent> not run <date>: <reason>` dated no earlier than it, clears that amendment.
Records count only under `## FO alignment` and its subheadings; a call written under another heading leaves the
event owed and adds a `next:` line naming that heading.
Exit 0 nothing owed; stdout counts the events read. Exit 1 `next:` lines per owed role. Exit 2 cannot tell
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
ALIGNMENT_SECTION = titled("##", "FO alignment")
IMPLEMENTATION_REPORT = re.compile(rf"^{SPACE}## Stage Report: implementation\b", re.I)
AMENDMENT = re.compile(rf"^{SPACE}### Amendment (\d+)\b", re.I)
DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
FIELD = re.compile(r"^(Supersedes|Design):[ \t]*(.*?)[ \t]*$")
FRONT_PROFILE = re.compile(r"""^profile:[ \t]*["']?([^\s"']+)["']?[ \t]*$""", re.M)
SURFACES_DB = re.compile(r"^Surfaces:.*\bdb\b", re.M)
MARK = r"(?:-[ \t]+)?Reviewer:[ \t]*(?:kc-dev-flow-2:)?"
REPAIRS = 4
RANK = {"haiku": 0, "sonnet": 1, "opus": 2, "fable": 3}

QUESTION = {
    "chief-engineer": "what is the smallest next step, given the findings so far?",
    "engineering-reviewer": "do these amendments withdraw what the Captain approved, and what changes in the build?",
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
    """Return (implementation reports, [(amendment number, entry date or None)]) for amendments that replace something."""
    reports, amendments = 0, []
    section = ""
    entry = None
    for line in lines:
        heading = HEADING.match(line)
        if heading and len(heading.group(1)) <= 3:
            amendment = AMENDMENT.match(line)
            if not amendment:
                section = line
            if IMPLEMENTATION_REPORT.match(line):
                reports += 1
            found = DATE.search(line)
            entry = [int(amendment.group(1)), found.group(0) if found else None, False] \
                if amendment and AMENDMENTS_SECTION.match(section) else None
            continue
        field = FIELD.match(line)
        if entry and not entry[2] and field and field.group(2) and not field.group(2).lower().startswith("none"):
            entry[2] = True
            amendments.append((entry[0], entry[1]))
    return reports, amendments


def alignment(lines):
    keep = False
    for line in lines:
        heading = HEADING.match(line)
        if heading and len(heading.group(1)) <= 2:
            keep = bool(ALIGNMENT_SECTION.match(line))
        if keep:
            yield line


def records(lines, agent):
    """Return (calls, waivers): (model, date) and (date or None) for each `Reviewer:` line naming agent."""
    name = re.escape(agent)
    call = re.compile(rf"^{MARK}{name}[ \t]+(\S+)[ \t]+({DATE.pattern})[ \t]+[—–-][ \t]+\S")
    waiver = re.compile(rf"^{MARK}{name}[ \t]+not run(?:[ \t]+({DATE.pattern}))?:[ \t]*(.*)$")
    calls, waivers = [], []
    for line in lines:
        line = line.strip()
        made, waived = call.match(line), waiver.match(line)
        if made:
            calls.append((made.group(1), made.group(2)))
        elif waived and re.sub(r"[\s()\[\]:;,.\-—–]+", "", waived.group(2)):
            waivers.append(waived.group(1))
    return calls, waivers


def rank(model):
    word = re.match(r"[a-z]+", model.lower())
    return RANK.get(word.group(0), -1) if word else -1


def misplaced(lines, agent):
    """Return the heading above the first call or waiver for agent that sits outside FO alignment, or None."""
    kept = set(map(id, alignment(lines)))
    heading = None
    for line in lines:
        if HEADING.match(line):
            heading = line.strip()
        if id(line) not in kept and heading and any(records([line], agent)):
            return heading[:60]
    return None


def owed_line(slug, agent, happened, where="", model="<model>", waived=""):
    return (f"next: {slug} {happened}; dispatch kc-dev-flow-2:{agent} {where}with the question \"{QUESTION[agent]}\" "
            f"and record `Reviewer: kc-dev-flow-2:{agent} {model} <date> — <question>` under ## FO alignment; "
            f"or, to decline, record `Reviewer: kc-dev-flow-2:{agent} not run{waived}: <reason>` instead.")


def hint(slug, agent, heading):
    return (f"next: {slug} has a Reviewer: line for {agent} under \"{heading}\", where it does not count; "
            "move it under ## FO alignment.")


def check(state, slug, rev):
    text = read_task(state, slug, rev)
    lines = list(outside_fences(text))
    reports, amendments = events(lines)
    kept = list(alignment(lines))
    front = re.match(r"---\n(.*?)\n---\n", text, re.S)
    profile = FRONT_PROFILE.search(front.group(1)) if front else None
    strong = (profile and profile.group(1) == "prod", any(SURFACES_DB.match(line.strip()) for line in kept))
    owed, seen = [], 0
    repairs = max(reports - 1, 0)
    if repairs >= REPAIRS:
        seen += 1
        calls, waivers = records(kept, "chief-engineer")
        if not (calls or waivers):
            owed.append(owed_line(slug, "chief-engineer", f"has {repairs} repair passes"))
            owed += [hint(slug, "chief-engineer", h) for h in [misplaced(lines, "chief-engineer")] if h]
    if amendments:
        seen += len(amendments)
        need = "fable" if any(strong) else "opus"
        calls, waivers = records(kept, "engineering-reviewer")
        open_numbers = []
        for number, date in sorted(amendments):
            by_call = any(rank(model) >= RANK[need] and (date is None or made >= date) for model, made in calls)
            by_waiver = any(waived and (date is None or waived >= date) for waived in waivers)
            if not (by_call or by_waiver):
                open_numbers.append(str(number))
        if open_numbers:
            basis = ", ".join(name for name, on in zip(("profile prod", "Surfaces db"), strong) if on)
            where = f"on {need}{f' ({basis})' if basis else ''} "
            plural = "s" * (len(open_numbers) > 1)
            happened = f"has replacing amendment{plural} {', '.join(open_numbers)}"
            owed.append(owed_line(slug, "engineering-reviewer", happened, where, need, " <date>"))
            owed += [hint(slug, "engineering-reviewer", h) for h in [misplaced(lines, "engineering-reviewer")] if h]
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
