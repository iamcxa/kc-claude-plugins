#!/usr/bin/env python3
"""List the chief-engineer and engineering-reviewer calls a committed task state owes.

Usage: role_triggers.py <state checkout> <task slug> [--rev REV] [--review-rounds N [--drift-date YYYY-MM-DD]]
Reads the task at REV (default HEAD) from committed bytes, never the disk; live or archived, flat or folder.
Chief-engineer is owed at four repair passes: the `## Stage Report: implementation` headings minus one (or, given
--review-rounds, N >= 2 review ids that left inline findings on the open PR).
--drift-date is the UTC date of the newest review round (`review_facts`); given it, a call or waiver clears the
review-round event only when dated no earlier than it, so a call about something else dated before the newest
round leaves it owed. A call made earlier on the same date as that round still clears it. Without it, any call or
waiver clears, as before.
Two validations with a Material or Needs decision F bullet, or two amendments with non-none Supersedes, print
three step-back questions without a hold, independently even when the other event has already cleared at three.
An owed line carrying those questions suppresses a duplicate reminder. Either count at three owes chief-engineer;
the third amendment's date clears that event, while the validation event has no date test. Counts stay separate.
Dispatch records also count by stage and normalized Symptom: header: two remind, three owe chief-engineer.
The third record's Dispatched: date dates that event; a qualifying call or waiver clears later rounds too.
Engineering-reviewer is owed for each `### Amendment N` under `## Captain amendments` whose `Supersedes:` or
`Design:` value does not start with `none`; one line per task, on fable when the frontmatter says `profile: prod`
or the `Surfaces:` line under `## FO alignment` lists `db`, else on opus. Fenced blocks are skipped everywhere.
A call is `Reviewer: <agent> <model> <date> — <question>` whatever the question says. A chief-engineer call at opus rank or above, or a
waiver, clears the repair event with no date test: a stage-report heading has no date. For engineering-reviewer a call dated no earlier than an amendment, on a model
ranked haiku < sonnet < opus < fable = astra by its first recognized word and no lower than the one required, or a waiver
`Reviewer: <agent> not run <date>: <reason>` dated no earlier than it, clears that amendment.
Records count only under `## FO alignment` and its subheadings; a call written under another heading leaves the
event owed and adds a `next:` line naming that heading.
Exit 0 nothing owed; stdout counts the events read or prints the advisory `next:` line. Exit 1 `next:` lines per owed role. Exit 2 cannot tell
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
VALIDATION_REPORT = re.compile(rf"^{SPACE}## Stage Report: validation\b", re.I)
FINDING = re.compile(r"^[ \t]*[-*][ \t]+\*{0,2}F[0-9]+\*{0,2}[ \t]*[:(—–-]?[ \t]*(?:Material|Needs decision)\b")
AMENDMENT = re.compile(rf"^{SPACE}### Amendment (\d+)\b", re.I)
DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
FIELD = re.compile(r"^(Supersedes|Design):[ \t]*(.*?)[ \t]*$")
FRONT_PROFILE = re.compile(r"""^profile:[ \t]*["']?([^\s"']+)["']?[ \t]*$""", re.M)
SURFACES_DB = re.compile(r"^Surfaces:.*\bdb\b", re.M)
MARK = r"(?:-[ \t]+)?Reviewer:[ \t]*(?:kc-dev-flow-2:)?"
REPAIRS, REVIEW_ROUNDS = 4, 2
ROUND_DATE = re.compile(rf"^{DATE.pattern}(?=T)")
# see docs/adr/0049-special-roles-and-stage-defaults-follow-one-model-table.md
RANK = {"haiku": 0, "sonnet": 1, "opus": 2, "fable": 3, "astra": 3}

QUESTION = {
    "chief-engineer": "what is the smallest next step, given the findings so far?",
    "engineering-reviewer": "do these amendments withdraw what the Captain approved, and what changes in the build?",
}
STEP_BACK = ("is what I am solving still the outcome first asked for; can this gap be tested now, or am I waiting; "
             "what breaks if this criterion or process is deleted?")
DIAGNOSIS_RECORD = re.compile(r"^(implementation|validation)-([1-9][0-9]*)\.md$")


class Unverifiable(Exception):
    pass


def git(state, *args):
    done = subprocess.run(["git", "-C", str(state), *args], capture_output=True)
    return done.returncode, done.stdout.decode("utf-8", "replace")


def review_facts(comments):
    """Return (review rounds, UTC date of the newest round or None) from a pulls/<N>/comments list.

    A round is a distinct pull_request_review_id; its time is its earliest comment's created_at. The date is None
    below two rounds or when any round has no ISO timestamp.
    """
    stamps = {}
    for comment in comments:
        stamps.setdefault(comment["pull_request_review_id"], []).append(comment.get("created_at") or "")
    if len(stamps) < REVIEW_ROUNDS or not all(ROUND_DATE.match(at) for ats in stamps.values() for at in ats):
        return len(stamps), None
    return len(stamps), max(min(ats) for ats in stamps.values())[:10]


def parse(args):
    options = {"--rev": "HEAD", "--review-rounds": None, "--drift-date": None}
    for name in options:
        if name in args:
            at = args.index(name)
            if at + 1 >= len(args):
                raise Unverifiable(f"usage: {name} needs a value")
            options[name] = args[at + 1]
            args = args[:at] + args[at + 2:]
    rounds = options["--review-rounds"]
    if rounds is not None and not rounds.isdigit():
        raise Unverifiable("usage: --review-rounds needs a whole number")
    drift = options["--drift-date"]
    if drift is not None and not re.fullmatch(DATE.pattern, drift):
        raise Unverifiable("usage: --drift-date needs YYYY-MM-DD")
    if len(args) != 2 or "/" in args[1] or args[1] in ("", ".", ".."):
        raise Unverifiable("usage: role_triggers.py <state checkout> <task slug> [--rev REV] [--review-rounds N [--drift-date YYYY-MM-DD]]")
    return Path(args[0]), args[1], options["--rev"], None if rounds is None else int(rounds), drift


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


def dispatch_header(text):
    header = []
    for line in outside_fences(text):
        if line.startswith("## "):
            break
        header.append(line)
    return "\n".join(header)


def symptom_name(text):
    match = re.search(r"^Symptom:[ \t]*(.*)$", dispatch_header(text), re.M)
    return " ".join(match[1].split()).casefold() if match else None


def symptom_rounds(dispatches):
    groups = {}
    for name, text in dispatches:
        record = DIAGNOSIS_RECORD.fullmatch(name)
        symptom = symptom_name(text)
        if record and symptom and not symptom.startswith("none"):
            dispatched = re.search(r"^Dispatched:([^\n]*)", dispatch_header(text), re.M)
            date = DATE.search(dispatched[1]) if dispatched else None
            groups.setdefault((record[1], symptom), []).append((int(record[2]), date[0] if date else None))
    return {key: sorted(rounds) for key, rounds in groups.items()}


def read_records(state, slug, rev):
    for base in ("", "_archive/"):
        if any(git(state, "cat-file", "-e", f"{rev}:./{path}")[0] == 0
               for path in (f"{base}{slug}/index.md", f"{base}{slug}.md")):
            code, paths = git(state, "ls-tree", "-r", "--name-only", rev, "--", f"{base}{slug}/dispatch/")
            if code:
                raise Unverifiable(f"cannot read dispatch records for {slug} at {rev}")
            dispatches = []
            for path in paths.splitlines():
                if DIAGNOSIS_RECORD.fullmatch(Path(path).name):
                    code, text = git(state, "show", f"{rev}:./{path}")
                    if code:
                        raise Unverifiable(f"cannot read {path} at {rev}")
                    dispatches.append((Path(path).name, text))
            return dispatches
    return []


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


def step_back_events(lines):
    failures, replacements = 0, []
    section, validation, entry = "", False, None
    for line in lines:
        heading = HEADING.match(line)
        if heading:
            if len(heading.group(1)) <= 2:
                section = line
                validation = bool(VALIDATION_REPORT.match(line))
            if len(heading.group(1)) <= 3:
                amendment = AMENDMENT.match(line)
                found = DATE.search(line)
                entry = [found.group(0) if found else None, False] \
                    if amendment and AMENDMENTS_SECTION.match(section) else None
        if validation and FINDING.match(line):
            failures += 1
            validation = False
        field = FIELD.match(line)
        if entry and not entry[1] and field and field.group(1) == "Supersedes" and field.group(2) \
                and not field.group(2).lower().startswith("none"):
            replacements.append(entry[0])
            entry[1] = True
    return failures, replacements


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
    return next((RANK[word] for word in re.findall(r"[a-z]+", model.lower()) if word in RANK), -1)


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


def owed_line(slug, agent, happened, where="", model="<model>", waived="", question=None):
    return (f"next: {slug} {happened}; dispatch kc-dev-flow-2:{agent} {where}with the question \"{question or QUESTION[agent]}\" "
            f"and record `Reviewer: kc-dev-flow-2:{agent} {model} <date> — <question>` under ## FO alignment; "
            f"or, to decline, record `Reviewer: kc-dev-flow-2:{agent} not run{waived}: <reason>` instead.")


def hint(slug, agent, heading):
    return (f"next: {slug} has a Reviewer: line for {agent} under \"{heading}\", where it does not count; "
            "move it under ## FO alignment.")


def check(state, slug, rev, rounds=None, drift=None):
    text = read_task(state, slug, rev)
    lines = list(outside_fences(text))
    reports, amendments = events(lines)
    failures, replacements = step_back_events(lines)
    symptoms = symptom_rounds(read_records(state, slug, rev))
    kept = list(alignment(lines))
    front = re.match(r"---\n(.*?)\n---\n", text, re.S)
    profile = FRONT_PROFILE.search(front.group(1)) if front else None
    strong = (profile and profile.group(1) == "prod", any(SURFACES_DB.match(line.strip()) for line in kept))
    owed, seen = [], 0
    repairs = max(reports - 1, 0)
    if (repairs >= REPAIRS or (rounds or 0) >= REVIEW_ROUNDS or max(failures, len(replacements)) >= 3
            or any(len(group) >= 3 for group in symptoms.values())):
        seen += 1
        calls, waivers = records(kept, "chief-engineer")
        calls = [(model, made) for model, made in calls if rank(model) >= RANK["opus"]]
        dated = [made for _, made in calls] + [waived for waived in waivers if waived]
        repair_owed = repairs >= REPAIRS and not (calls or waivers)
        rounds_owed = (rounds or 0) >= REVIEW_ROUNDS and not (
            any(made >= drift for made in dated) if drift else calls or waivers)
        failures_owed = failures >= 3 and not (calls or waivers)
        third_date = replacements[2] if len(replacements) >= 3 else None
        replacements_owed = len(replacements) >= 3 and not (
            any(made >= third_date for made in dated) if third_date else calls or waivers)
        symptom_owed = [f'{len(group)} {stage} dispatches on symptom "{symptom}"'
                        for (stage, symptom), group in sorted(symptoms.items()) if len(group) >= 3 and not (
                            any(made >= group[2][1] for made in dated) if group[2][1] else calls or waivers)]
        if repair_owed or rounds_owed or failures_owed or replacements_owed or symptom_owed:
            found = [f"{repairs} repair passes"] * repair_owed + [f"{rounds} review rounds"] * rounds_owed
            if rounds_owed and drift:
                found[-1] += f", the newest on {drift}"
            found += [f"{failures} validations with a Material or Needs decision finding"] * failures_owed
            found += [f"{len(replacements)} replacing amendments"] * replacements_owed
            found += symptom_owed
            owed.append(owed_line(slug, "chief-engineer", "has " + " and ".join(found), "on opus or gpt-6-astra ",
                                  waived=" <date>" if drift or replacements_owed or symptom_owed else "",
                                  question=STEP_BACK if failures_owed or replacements_owed or symptom_owed else None))
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
            where = f"on {need} or gpt-6-astra{f' ({basis})' if basis else ''} "
            plural = "s" * (len(open_numbers) > 1)
            happened = f"has replacing amendment{plural} {', '.join(open_numbers)}"
            owed.append(owed_line(slug, "engineering-reviewer", happened, where, waived=" <date>"))
            owed += [hint(slug, "engineering-reviewer", h) for h in [misplaced(lines, "engineering-reviewer")] if h]
    reminder = [f"next: {slug} has {failures} validations with a Material or Needs decision finding and "
                f"{len(replacements)} replacing amendments: before the next step, answer: {STEP_BACK}"] \
        if 2 in (failures, len(replacements)) and not any(STEP_BACK in line for line in owed) else []
    if not any(STEP_BACK in line for line in owed):
        reminder += [f'next: {slug} has 2 {stage} dispatches on symptom "{symptom}": '
                     f"before the next step, answer: {STEP_BACK}"
                     for (stage, symptom), group in sorted(symptoms.items()) if len(group) == 2]
    if owed or reminder:
        return int(bool(owed)), "\n".join(owed + reminder)
    return 0, f"role triggers: {seen} event(s) read at {rev}, each with a call or a waiver."


def main(argv=None):
    args = sys.argv[1:] if argv is None else list(argv)
    try:
        state, slug, rev, rounds, drift = parse(args)
        code, message = check(state, slug, rev, rounds, drift)
    except Unverifiable as err:
        print(f"cannot tell whether a chief-engineer or engineering-reviewer call is owed: {err}. Hold and report the cause.")
        return 2
    print(message)
    return code


if __name__ == "__main__":
    sys.exit(main())
