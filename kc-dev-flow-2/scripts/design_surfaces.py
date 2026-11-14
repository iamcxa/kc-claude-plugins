#!/usr/bin/env python3
"""Check a dev2 task file: the FO-alignment record, the artifacts its Surfaces: line owes, its acceptance criteria and any Captain amendments; exit 1 on any violation.

An unapproved Pilot design in ideation needs a command, observed exit and output path per criterion, or a named reason under 'Not provable now'.

While the task's frontmatter says `status: ideation` it also holds a `## Scope` line (the first such heading outside a code fence) added or removed after the backlog gate closed.
The baseline is the task file at the commit that added the newest `### Amendment N — <date>` dated on or after the backlog approval
(the working copy when that heading is uncommitted), else at the sha the backlog briefing binds (`git-root://state/<sha>/<path>`);
lines opening with Non-goals, Budget, Stop condition or Follow-up: are exempt. The check reads git history and the working copy,
not what the Captain said; an amendment covers every earlier unrecorded Scope edit. It prints `scope check not run: <why>` and
leaves the exit code alone in any other stage, with no closed backlog approval, outside a git checkout, or when the backlog briefing binds another file and no amendment supplies the baseline.
A `Captain:` or `Asked:` amendment line holding a JSON backslash-quote is an error unless it sits after a `Superseded text:` line. A superseded
criterion that is still declared is an error only once a `dispatch/*.md` checklist names the amendment; before that it waits for its worker. An
`Override: recommended ...; Captain chose ...; area: ...` line in the body that no gate resolution reason carries is printed as a note, exit code unchanged.
"""
import argparse
import difflib
import hashlib
import json
import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import decision_ledger

KNOWN = {"ui", "db", "none"}
CAPTAIN_QUOTE = re.compile(r"「[^」]*\S[^」]*」")
FO_HEADING = re.compile(r"^## FO alignment[ \t]*$", re.M)
SURFACES = re.compile(r"^Surfaces:\s*(.*)$", re.M)
VISIBLE = re.compile(r"^Visible change:\s*(.*)$", re.M)
UI_PROPOSAL = re.compile(r"^UI proposal:\s*(\S.*)$", re.M)
PREVIEW = re.compile(r"^Preview:\s*(\S.*)$", re.M)
MIGRATION = re.compile(r"^Migration source:\s*(\S.*)$", re.M)
URL = re.compile(r"^https?://\S+$")
MERMAID = re.compile(r"```mermaid\n(.*?)```", re.S)
FENCE = re.compile(r"^[ \t]*```")
GO_SPACE = "[\t\n\v\f\r \x85\xa0\u1680\u2000-\u200a\u2028\u2029\u202f\u205f\u3000]*"
AC_HEADING = re.compile(rf"^{GO_SPACE}## Acceptance criteria{GO_SPACE}$", re.I)
SECTION_END = re.compile(rf"^{GO_SPACE}## ")
AC_DECLARATION = re.compile(r"\*\*(AC-[A-Za-z0-9]+)[^*\n]*\*\*")
AMENDMENTS_HEADING = re.compile(rf"^{GO_SPACE}## Captain amendments{GO_SPACE}$", re.I)
SUPERSEDES = re.compile(r"^Supersedes:(.*)$", re.M)
AC_ID = re.compile(r"AC-[A-Za-z0-9]+")
DECLARATION_LINE = re.compile(r"^[ \t]*(?:>[ \t]*)*(?:(?:[-*+]|\d+[.)])[ \t]+)?\*\*(AC-[A-Za-z0-9]+)[^*\n]*\*\*")
NO_REPLACEMENT = re.compile(r"no replacement", re.I)
FRONTMATTER = re.compile(r"\A---\n(.*?\n)---\n", re.S)
FM_PROFILE = re.compile(r"""^profile:[ \t]*["']?([^\s"']+)["']?[ \t]*$""", re.M)
FM_STATUS = re.compile(r"""^status:[ \t]*["']?([^\s"']+)["']?[ \t]*$""", re.M)
REVIEW_LINE = re.compile(r"^Security review:[ \t]*(\S.*)$", re.M)
FOCUS_LINE = re.compile(r"^Security focus file:[ \t]*(\S.*)$", re.M)
FINDING_LINE = re.compile(r"^Security finding (\d+):[ \t]*(\S.*)$", re.M)
SEVERITY_SCALE = ("CRITICAL", "HIGH", "MEDIUM", "LOW")
DESIGN_SCALE = ("MAJOR", "MINOR")
DESIGN_REVIEW_LINE = re.compile(r"^Design review:[ \t]*(\S.*)$", re.M)
DESIGN_FINDING_LINE = re.compile(r"^Design finding (\d+):[ \t]*(\S.*)$", re.M)
DECLINE_CHECK_LINE = re.compile(r"^Decline check:[ \t]*(\S.*)$", re.M)
BUILT_REVIEW_LINE = re.compile(r"^Built screen review:[ \t]*(\S.*)$", re.M)
BUILT_FINDING_LINE = re.compile(r"^Built screen finding (\d+):[ \t]*(\S.*)$", re.M)
BUILT_DECLINE_LINE = re.compile(r"^Built screen decline check:[ \t]*(\S.*)$", re.M)
DECLINED = re.compile(r"declined:\s*\S")
NEEDS_DECISION = re.compile(r"Needs decision:\s*\S")
HOST_REASON = re.compile(r"declined:\s*host component\b")
HOST_FORM = re.compile(r"declined:\s*host component\s+\S.*?\s+at\s+\S+:\s*\S")
RULING_ITEM = re.compile(r"^[ \t]*-[ \t]+finding:[ \t]*(\S.*)$", re.M)
RULING_FIELD = re.compile(r"^[ \t]+([a-z]+):[ \t]*(.*)$", re.M)
RULINGS = ("upheld", "overruled", "decision")
KINDS = ("host-look", "other-task", "recorded-ruling")
ADR_TITLE = re.compile(r"\bADR:[ \t]*\S[^\n]*$")
REPORT_FINDINGS_KEY = re.compile(r"^([ \t]+)findings:(.*)$", re.M)
REPORT_ROOT_LINE = re.compile(r"^tob_security_review:", re.M)
FINDINGS_LINE = re.compile(r"^[ \t]*(?:-[ \t]+)?findings:", re.M)
SEVERITY_LINE = re.compile(r"^[ \t]*(?:-[ \t]+)?severity:", re.M)
ITEM_FIRST_KEY = re.compile(r"[A-Za-z_][\w-]*:")
SCOPE_EXEMPT = re.compile(r"\s*(?:[-*]\s*)?(?:Non-goals?\b|Budget\b|Stop condition\b|Follow-up:)", re.I)
ALIGN_NEEDED = re.compile(r"^Alignment:[ \t]*needed\b", re.I | re.M)
RESULT_LINE = re.compile(r"^Result:[ \t]*\S", re.M)
JSON_QUOTE = re.compile(r'\\"')
AMENDMENT_DATED = re.compile(r"^### Amendment (\d+) — (\d{4}-\d{2}-\d{2})", re.M)
BOUND_URI = re.compile(r"git-root://state/([0-9a-f]{40})/(.+)")
SCOPE_HOLD = ("Scope changed after {what} ({sha}): \"{line}\". FO: restore the line; add an '### Amendment N' with 'Supersedes: none' only if "
              "the Captain asked for it, with his words verbatim and where he said them. "
              "A worker that sees this line reports it to FO and edits neither Scope nor amendments.")
TABLE = re.compile(r"^[ \t]*\|.*\|[ \t]*\n[ \t]*\|[ \t:|-]*-[ \t:|-]*\|?[ \t]*$", re.M)


def split_fo(text):
    fo, body, current = [], [], False
    for line in text.split("\n"):
        if line.startswith("## "):
            current = line[3:].strip() == "FO alignment"
            body.append(line)
            continue
        (fo if current else body).append(line)
    return "\n".join(fo), "\n".join(body)


def has_erdiagram(body):
    for block in MERMAID.findall(body):
        first = next((l.strip() for l in block.split("\n") if l.strip()), "")
        if first == "erDiagram":
            return True
    return False


def preview_target(task_dir, value):
    target = Path(value)
    return target if target.is_absolute() else task_dir / value


def check_ui(name, body, task_dir, errors):
    proposal = UI_PROPOSAL.search(body)
    if not proposal:
        errors.append(f"{name}: surface 'ui' needs a 'UI proposal:' line with text")
    preview = PREVIEW.search(body)
    if not preview:
        errors.append(f"{name}: surface 'ui' needs a 'Preview:' line")
        return
    value = preview.group(1).strip()
    if URL.match(value):
        return
    target = preview_target(task_dir, value)
    if not target.exists():
        errors.append(f"{name}: surface 'ui' Preview '{value}' does not exist")


def check_db(name, body, errors):
    if not MIGRATION.search(body):
        errors.append(f"{name}: surface 'db' needs a 'Migration source:' line with a value")
    if not (has_erdiagram(body) or TABLE.search(body)):
        errors.append(f"{name}: surface 'db' needs a schema shown as a Mermaid erDiagram or a markdown table")


def section(lines, heading):
    for start, line in enumerate(lines):
        if heading.match(line):
            end = next((i for i in range(start + 1, len(lines)) if SECTION_END.match(lines[i])), len(lines))
            return lines[start + 1:end]
    return None


def unfenced(lines):
    kept, inside = [], False
    for line in lines:
        if FENCE.match(line):
            inside = not inside
        elif not inside:
            kept.append(line)
    return kept


def alignment_owes_result(text):
    fo, _ = split_fo("\n".join(unfenced(text.split("\n"))))
    return bool(ALIGN_NEEDED.search(fo)) and not RESULT_LINE.search(fo)


def escaped_amendment_lines(lines):
    found = []
    for entry in parse_amendments(lines)[0]:
        title = entry.header.strip()
        for line in entry.prefix.split("\n"):
            if line.startswith(("Captain:", "Asked:")) and JSON_QUOTE.search(line):
                found.append((title, line.split(":", 1)[0]))
    return found


def owed_overrides(text):
    fm, body = decision_ledger.split_task(text)
    if fm is None:
        return []
    chosen = {" ".join(m.group("chose").split())[:18] for e in decision_ledger.gate_entries(fm) if e["kind"] == "resolution"
              for m in [decision_ledger.OVERRIDE.search(e.get("reason") or "")] if m}
    found = []
    for line in unfenced(body.split("\n")):
        m = decision_ledger.OVERRIDE.search(line)
        if m and not m.group("rec").startswith(("<", ".", "…")) and " ".join(m.group("chose").split())[:18] not in chosen:
            found.append(" ".join(line[m.start():].split()))
    return found


def check_criteria(name, lines, errors):
    body = section(lines, AC_HEADING)
    if body is None:
        errors.append(f"{name}: missing '## Acceptance criteria' section")
        return set()
    declared = {found for line in body for found in AC_DECLARATION.findall(line)}
    if not declared:
        errors.append(f"{name}: '## Acceptance criteria' declares no criterion (a '**AC-<id>**' bold line)")
    return declared


PROOF_EXIT = re.compile(r"\bexit(?:ed| code)?\s*[:=]?\s*-?\d+", re.I)
PROOF_PATH = re.compile(r"[\w.<>~-]*/[\w./<>-]*\w|\b[\w-]+(?:\.[\w-]+)*\.(?:log|json|jsonl|txt|md|out|err|stdout|stderr|diff|xml|csv|html|png)\b")
PROOF_COMMAND = re.compile(r"\bcommand\b|`[^`\n]+`", re.I)
FALSIFIER_PART = re.compile(r"Falsifiers?\b:?.*?(?=Current evidence:|Evidence(?: command)?:|$)", re.S | re.I)
UNPROVABLE_HEADING = re.compile(r"^[ \t]*#{2,4}[ \t]*Not provable now\b", re.I)


def unprovable_entries(lines):
    named, inside, level = {}, False, 0
    for line in unfenced(lines):
        head = re.match(r"^[ \t]*(#{1,6})[ \t]", line)
        if UNPROVABLE_HEADING.match(line):
            inside, level = True, len(head.group(1))
            continue
        if inside and head and len(head.group(1)) <= level:
            inside = False
        if inside:
            for found in AC_ID.findall(line):
                if len(words_of(AC_ID.sub("", line))) >= 3:
                    named[found] = line.strip()
    return named


def proof_gaps(lines):
    body = section(lines, AC_HEADING) or []
    unprovable = unprovable_entries(lines)
    gaps = []
    for key, block in criterion_blocks(unfenced(body)).items():
        claim = FALSIFIER_PART.sub(" ", block)
        missing = [field for field, rx in (("command", PROOF_COMMAND), ("exit", PROOF_EXIT), ("output path", PROOF_PATH))
                   if not rx.search(DECLARATION_LINE.sub("", claim, count=1) if field == "command" else claim)]
        if missing and key not in unprovable:
            gaps.append((key, missing))
    return gaps


def pilot_ideation(front):
    return all(re.search(rf"""^{key}:[ \t]*(?:{value}|'{value}'|"{value}")(?:[ \t]+#[^\n]*)?[ \t]*$""",
                         front, re.M)
               for key, value in (("profile", "pilot"), ("status", "ideation")))


def design_approved(text):
    fm, _ = decision_ledger.split_task(text)
    return any(e["kind"] == "resolution" and e["stage"] == "ideation" and e.get("decision") == "approve"
               for e in decision_ledger.gate_entries(fm or []))


def declarations(lines):
    return [(found.group(1), line) for line in lines for found in [DECLARATION_LINE.match(line)] if found]


AMENDMENT_START = re.compile(r"^\s*### Amendment\b", re.I)
AMENDMENT_HEADER = re.compile(r"^\s*### Amendment ([0-9]+) — [0-9]{4}-[0-9]{2}-[0-9]{2}[^\r\n]*\r?$", re.I)
AMENDMENT_FENCE = re.compile(r"^[ \t]*(`{3,}|~{3,})(.*)$")
AMENDMENT_LEVEL = re.compile(r"^\s*(#{1,3})[ \t]+")
SUPERSEDES_VALUE = re.compile(
    r"(?:none|AC-[A-Za-z0-9]+(?:(?:[ \t]*,[ \t]*|[ \t]+)AC-[A-Za-z0-9]+)*"
    r"(?:[ \t]*(?:,[ \t]*)?and[ \t]+AC-[A-Za-z0-9]+)?)"
    r"\.?(?:[ \t]+\(no replacement:[ \t]*\S[^\r\n]*\))?")


def protected_text(lines):
    lines = list(lines)
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines)


class AmendmentRecord:
    def __init__(self, lines, start, end, owner, visible):
        self.start, self.end, self.owner = start, end, owner
        self.ambiguous_from = None
        self.raw = protected_text(lines[start:end])
        self.header = lines[start]
        match = re.match(r"^\s*### Amendment ([0-9]+)\b", self.header, re.I)
        self.number = int(match[1]) if match else None
        self.visible = [(i, line) for i, line in visible if start < i < end]
        marker = next((i for i, line in self.visible if line.rstrip("\r") == "Superseded text:"), None)
        self.metadata = protected_text(lines[start:marker if marker is not None else end])
        self.payload = None if marker is None else protected_text(lines[marker:end])
        self.prefix = "\n".join(line for i, line in self.visible if marker is None or i < marker)
        self.moved = [line for i, line in self.visible if marker is not None and i > marker]


def parse_amendments(lines):
    """Return raw records and structural defects; fenced examples are not metadata."""
    records, issues, visible, starts = [], [], [], []
    owner, active, fence, sections = None, None, None, 0
    for i, line in enumerate(lines):
        marker = AMENDMENT_FENCE.match(line)
        if fence:
            if marker and marker[1][0] == fence[0][0] and len(marker[1]) >= len(fence[0]):
                if not marker[2].strip():
                    fence = None
                elif fence[2] is not None:
                    issues.append((fence[1] + 1, "unmatched amendment-region fence before another opening delimiter"))
            continue
        if marker:
            fence = (marker[1], i, active, owner)
            continue
        visible.append((i, line))
        heading = AMENDMENT_LEVEL.match(line)
        if heading:
            if active is not None:
                starts[active][1] = i
                active = None
            if len(heading[1]) <= 2:
                owner = line.strip()
                if AMENDMENTS_HEADING.match(line):
                    sections += 1
                    if sections > 1:
                        issues.append((i + 1, "duplicate '## Captain amendments' section"))
            if AMENDMENT_START.match(line):
                starts.append([i, len(lines), owner])
                active = len(starts) - 1
                if not AMENDMENTS_HEADING.match(owner or ""):
                    issues.append((i + 1, "amendment outside '## Captain amendments'"))
                if not AMENDMENT_HEADER.fullmatch(line):
                    issues.append((i + 1, "malformed amendment heading; expected '### Amendment N — YYYY-MM-DD'"))
    if fence and (fence[2] is not None or AMENDMENTS_HEADING.match(fence[3] or "")):
        issues.append((fence[1] + 1, "unmatched amendment-region fence"))
    seen = set()
    for start, end, owner in starts:
        entry = AmendmentRecord(lines, start, end, owner, visible)
        if fence and fence[2] is not None and start == starts[fence[2]][0]:
            entry.ambiguous_from = fence[1] - start
        records.append(entry)
        if entry.number in seen:
            issues.append((start + 1, f"duplicate amendment number {entry.number}"))
        seen.add(entry.number)
    return records, issues


def supersedes_ids(value):
    if not SUPERSEDES_VALUE.fullmatch(value.strip()):
        return None
    prefix = re.split(r"\(no replacement:", value, flags=re.I)[0]
    ids = AC_ID.findall(prefix)
    return set(ids) if len(ids) == len(set(ids)) else None


def amendment_form(lines):
    records, issues = parse_amendments(lines)
    for entry in records:
        captains = re.findall(r"^Captain:([^\n]*)$", entry.prefix, re.M)
        values = SUPERSEDES.findall(entry.prefix)
        if len(captains) != 1 or not captains[0].strip():
            issues.append((entry.start + 1, f"'{entry.header.strip()}' has no 'Captain:' line with his words (expected exactly one)"))
        if len(values) != 1 or supersedes_ids(values[0]) is None:
            issues.append((entry.start + 1, f"'{entry.header.strip()}' needs one 'Supersedes:' value: none or explicit unique AC ids, optionally '(no replacement: reason)'"))
    return records, issues


def amendment_entries(lines):
    records, _ = parse_amendments(lines)
    return [entry.raw for entry in records if AMENDMENTS_HEADING.match(entry.owner or "")]


REQUIREMENT_WORD = re.compile(r"[A-Za-z0-9][A-Za-z0-9'’_-]*")
FILLER_WORDS = frozenset("a an the and or of to in on at by for with that this these those it its is are be been "
                         "was were still remain remains also as from into not no".split())


def criterion_blocks(lines):
    blocks, current = {}, None
    for line in lines:
        found = DECLARATION_LINE.match(line)
        if found:
            current = found.group(1)
            blocks[current] = [line]
        elif current and not re.match(r"^[ \t]*#{1,6}(?:[ \t]+|$)", line):
            blocks[current].append(line)
        else:
            current = None
    return {key: " ".join(value) for key, value in blocks.items()}


def requirement_sentences(block):
    text = re.split(r"Current evidence:", block)[0]
    text = DECLARATION_LINE.sub("", text, count=1)
    text = re.sub(r"Amended by Captain, amendment \d+\.?", "", text)
    return [s.strip() for s in re.split(r"(?<=[.;:])\s+", text) if len(words_of(s)) >= 3]


def words_of(text):
    return [w.lower() for w in REQUIREMENT_WORD.findall(text)]


def added_words(lines):
    """Find inserted words in kept sentences of live amendment replacements."""
    # see docs/adr/0057-rewritten-criteria-are-compared-with-the-captains-words.md
    live = criterion_blocks(section(unfenced(lines), AC_HEADING) or [])
    entries = [e for e in parse_amendments(lines)[0] if e.number is not None]
    found = []
    for entry in entries:
        if entry.payload is None:
            continue
        his = set(words_of(" ".join(l for e in entries if e.number >= entry.number
                                    for l in e.prefix.split("\n") if l.startswith(("Captain:", "Asked:")))))
        old = [s for block in criterion_blocks(entry.moved).values() for s in requirement_sentences(block)]
        marker = re.compile(rf"Amended by Captain, amendment {entry.number}(?!\d)")
        for ident, block in live.items():
            if not marker.search(block):
                continue
            added = []
            for sentence in requirement_sentences(block):
                if sentence in old or not old:
                    continue
                new = words_of(sentence)
                best = max(old, key=lambda o: difflib.SequenceMatcher(None, words_of(o), new, autojunk=False).ratio())
                match = difflib.SequenceMatcher(None, words_of(best), new, autojunk=False)
                if match.ratio() < 0.75:
                    continue
                added += [w for op, _, _, j1, j2 in match.get_opcodes() if op in ("insert", "replace") for w in new[j1:j2]
                          if w not in his and w not in FILLER_WORDS and not re.fullmatch(r"ac-[a-z0-9]+", w)]
            if added:
                found.append((entry.number, ident, added))
    return found


AMENDMENT_NAMED = re.compile(r"amendments?[ \t]+((?:\d+(?:[ \t]*(?:,[ \t]*(?:and|&)?|and|&|to|-)[ \t]*)?)+)", re.I)


def dispatched_amendments(folder, texts=None):
    texts = [p.read_text() for p in sorted(Path(folder, "dispatch").glob("*.md"))] if texts is None else texts
    named = set()
    for text in texts:
        found = re.search(r"^## Checklist[ \t]*\n((?:(?!^## )[\s\S])*)", text, re.M)
        for m in AMENDMENT_NAMED.finditer(found.group(1) if found else ""):
            named |= {int(n) for n in re.findall(r"\d+", m.group(1))}
    return named


def check_amendments(name, lines, declared, errors, dispatched=None):
    entries, issues = amendment_form(lines)
    errors.extend(f"{name}:{line}: Captain amendment form: {message}" for line, message in issues)
    moved = [declarations(entry.moved) for entry in entries]
    live = declarations(section(lines, AC_HEADING) or [])
    for index, entry in enumerate(entries):
        title = entry.header.strip()
        values = SUPERSEDES.findall(entry.prefix)
        value = values[0] if len(values) == 1 else ""
        named = supersedes_ids(value)
        if named is None:
            continue
        number = entry.number
        waits = dispatched is not None and number not in dispatched
        for superseded in sorted(set() if waits else named & declared):
            errors.append(f"{name}: '{title}' supersedes {superseded} but it is still declared in '## Acceptance criteria'")
        held = {found for found, _ in moved[index]}
        if held - named:
            errors.append(f"{name}: '{title}' holds {', '.join(sorted(held - named))} but its 'Supersedes:' line does not name them")
        others = [pair for i, pairs in enumerate(moved) if i != index for pair in pairs]
        if unmarked(entry, live, others):
            errors.append(f"{name}: '{title}' supersedes {', '.join(sorted(named))} but no criterion says 'Amended by Captain, amendment {number}' and its 'Supersedes:' line does not say 'no replacement'")


def unmarked(entry, live, others):
    values = SUPERSEDES.findall(entry.prefix)
    if len(values) == 1:
        value = values[0]
        named = supersedes_ids(value)
        waiver = NO_REPLACEMENT.search(value)
        marker = re.compile(rf"Amended by Captain, amendment {entry.number}(?!\d)")
        if named and not waiver and not any(marker.search(text) for _, text in live + others):
            return True
    return False


def move_defects(lines):
    entries, issues = parse_amendments(lines)
    entries = [entry for entry in entries
               if not any(entry.start < line <= entry.end for line, _ in issues)]
    moved = [declarations(entry.moved) for entry in entries]
    visible, fence = [], None
    for line in lines:
        marker = AMENDMENT_FENCE.match(line)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                fence = None
        elif marker:
            fence = marker[1]
        else:
            visible.append(line)
    live = declarations(section(visible, AC_HEADING) or [])
    declared = {ident for ident, _ in live}
    defects = []
    for index, entry in enumerate(entries):
        if entry.payload is None:
            continue
        held = {ident for ident, _ in moved[index]}
        reused = tuple(sorted(held & declared))
        if reused:
            defects.append(("reused", entry.number, reused))
        others = [pair for i, pairs in enumerate(moved) if i != index for pair in pairs]
        if unmarked(entry, live, others):
            defects.append(("unmarked", entry.number))
    return defects


def report_severities(text, scale=SEVERITY_SCALE):
    key = REPORT_FINDINGS_KEY.search(text)
    indent = len(key.group(1))
    rest = re.sub(r"(?:^|[ \t]+)#.*$", "", key.group(2)).strip()
    if rest == "[]":
        return [], []
    if rest:
        return None, ["has a 'findings' value that is not a list"]
    items = []
    item_indent = None
    for line in text[key.end():].split("\n"):
        body = line.lstrip(" ")
        if not body or body.startswith("#"):
            continue
        depth = len(line) - len(body)
        marker = body == "-" or body.startswith("- ")
        if depth < indent or (depth == indent and not marker):
            break
        if item_indent is None:
            if not marker:
                return None, ["has a 'findings' value that is not a list"]
            item_indent = depth
        if depth < item_indent or (depth == item_indent and not marker):
            return None, ["has a 'findings' list whose items do not share one indent"]
        if depth == item_indent:
            items.append([])
        items[-1].append((depth, body))
    if not items:
        return None, ["has a 'findings' key with no items (an empty list is written 'findings: []')"]
    severities, problems = [], []
    for number, item in enumerate(items, 1):
        first = re.match(r"- +", item[0][1])
        if not first or not ITEM_FIRST_KEY.match(item[0][1][first.end():]):
            problems.append(f"has findings item {number} that is not a 'key: value' entry")
            continue
        key_indent = item[0][0] + first.end()
        lines = [item[0][1][first.end():]] + [b for d, b in item[1:] if d == key_indent]
        found = next((b for b in lines if b.startswith("severity:")), None)
        if found is None:
            problems.append(f"has findings item {number} with no 'severity:' line")
            continue
        value = re.sub(r"[ \t]+#.*$", "", found[len("severity:"):]).strip().strip("\"'")
        if value not in scale:
            problems.append(f"has findings item {number} with severity '{value}', not one of {', '.join(scale)}")
            continue
        severities.append(value)
    return severities, problems


def findings_is_direct_child(text, root, key):
    line = text[key.start():].split("\n", 1)[0]
    indent = len(line) - len(line.lstrip(" \t"))
    between = [b for b in text[root.end():key.start()].split("\n")[1:-1] if b.strip() and not b.lstrip().startswith("#")]
    if key.start() < root.end() or not line.lstrip(" \t").startswith("findings:") or any(not b[0].isspace() for b in between):
        return False
    first = (between or [line])[0]
    return indent > 0 and indent == len(first) - len(first.lstrip(" \t"))


def root_value(text, root):
    rest = text[root.end():].split("\n", 1)[0]
    return re.sub(r"(?:^|[ \t]+)#.*$", "", rest).strip()


def report_shape(text, root="tob_security_review"):
    roots = list(re.compile(rf"^{root}:", re.M).finditer(text))
    keys = list(FINDINGS_LINE.finditer(text))
    problems = []
    if len(roots) != 1:
        problems.append(f"is not a {root} report: {len(roots)} '{root}:' lines at column 0, expected exactly 1")
    if len(keys) != 1:
        problems.append(f"has {len(keys)} 'findings:' lines, expected exactly 1")
    if len(roots) == 1 and root_value(text, roots[0]):
        problems.append(f"has a '{root}:' line with a value after its colon, so its children are not a mapping")
    if not problems and not findings_is_direct_child(text, roots[0], keys[0]):
        problems.append(f"has a 'findings:' line that is not a direct child of '{root}:'")
    return problems


def repeated(found, label, name, errors):
    for n, count in sorted(Counter(int(n) for n, _ in found).items()):
        if count > 1:
            errors.append(f"{name}: '{label} finding {n}:' appears more than once; write one disposition per finding")


def check_security(path, body, declared, errors):
    name = path.name
    review = REVIEW_LINE.search(body)
    if not review:
        errors.append(f"{name}: a prod task needs a 'Security review:' line naming the saved report")
        return None
    if len(REVIEW_LINE.findall(body)) > 1:
        errors.append(f"{name}: {len(REVIEW_LINE.findall(body))} 'Security review:' lines, expected exactly 1; a rerun replaces the old line with the last report")
        return None
    value = review.group(1).strip()
    if value.lower().startswith("not run"):
        errors.append(f"{name}: security review not run ({value}); a missing reviewer holds the stage")
        return None
    folder = path.parent if path.name == "index.md" else path.parent / path.stem
    report = folder / value
    if Path(value).is_absolute() or ".." in Path(value).parts or not report.is_file():
        errors.append(f"{name}: 'Security review:' names '{value}', not a report file inside the task folder")
        return None
    text = report.read_text()
    shape = report_shape(text)
    if shape:
        errors.extend(f"{name}: '{value}' {problem}" for problem in shape)
        return None
    if not FOCUS_LINE.search(body):
        errors.append(f"{name}: a prod task needs a 'Security focus file:' line (a path, or none)")
    severities, problems = report_severities(text)
    if problems:
        errors.extend(f"{name}: '{value}' {problem}" for problem in problems)
        return None
    plain = len(SEVERITY_LINE.findall(text))
    if plain != len(severities):
        errors.append(f"{name}: '{value}' has {plain} 'severity:' lines but {len(severities)} in its findings items; every severity line must be a key of one findings item")
        return None
    found = len(severities)
    lines = {int(n): v.strip() for n, v in FINDING_LINE.findall(body)}
    repeated(FINDING_LINE.findall(body), "Security", name, errors)
    tally = {"ac": 0, "declined": 0, "decision": 0}
    for number in range(1, found + 1):
        entry = lines.get(number, "")
        if re.fullmatch(r"AC-[A-Za-z0-9]+", entry.split()[0] if entry else "") and entry.split()[0] in declared:
            tally["ac"] += 1
        elif re.match(r"declined:\s*\S", entry) and severities[number - 1] in ("MEDIUM", "LOW"):
            tally["declined"] += 1
        elif re.match(r"Needs decision:\s*\S", entry):
            tally["decision"] += 1
        else:
            errors.append(f"{name}: report finding {number} has no 'Security finding {number}:' line naming a declared AC-<id>, 'declined: <reason>' (MEDIUM or LOW only) or 'Needs decision: <text>'")
    for number in sorted(set(lines) - set(range(1, found + 1))):
        errors.append(f"{name}: 'Security finding {number}:' has no finding in '{value}' ({found} listed)")
    return f"security review {value}: {found} findings, {tally['ac']} acceptance criteria, {tally['declined']} declined, {tally['decision']} decisions"


def task_folder(path):
    return path.parent if path.name == "index.md" else path.parent / path.stem


def saved_report(name, label, value, folder, errors):
    report = folder / value
    if Path(value).is_absolute() or ".." in Path(value).parts or not report.is_file():
        errors.append(f"{name}: '{label}' names '{value}', not a report file inside the task folder")
        return None
    return report.read_text()


def design_report(name, value, text, errors, on_preview):
    """The severities of a design_review report, or None after appending its defects to errors."""
    shape = report_shape(text, "design_review")
    if shape:
        errors.extend(f"{name}: '{value}' {problem}" for problem in shape)
        return None
    child = re.match(r"[ \t]*", FINDINGS_LINE.search(text).group(0)).group(0)
    block = re.search(r"^design_review:.*\n((?:[ \t].*\n|[ \t]*\n|#.*\n)*)", text + "\n", re.M).group(1)
    named = re.findall(rf"^{child}preview:[ \t]*(.*)$", block, re.M)
    if len(named) > 1:
        errors.append(f"{name}: '{value}' has {len(named)} 'preview:' lines directly under 'design_review:', expected exactly 1")
        return None
    if named == [""]:
        tail = re.split(rf"^{child}preview:[ \t]*$", block, maxsplit=1, flags=re.M)[1]
        named = []
        for line in tail.splitlines():
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            item = re.fullmatch(rf"{child}(?:[ \t]+)?-[ \t]+(.+)", line)
            if not item:
                break
            named.append(item[1])
    on_preview(named)
    severities, problems = report_severities(text, DESIGN_SCALE)
    if problems:
        errors.extend(f"{name}: '{value}' {problem}" for problem in problems)
        return None
    plain = len(SEVERITY_LINE.findall(text))
    if plain != len(severities):
        errors.append(f"{name}: '{value}' has {plain} 'severity:' lines but {len(severities)} in its findings items; every severity line must be a key of one findings item")
        return None
    return severities


RULING_REQUIRED = ("evidence", "change")


def rulings_lines(text):
    """The lines of the `rulings:` list directly under the `design_decline_check:` root, and nothing else."""
    lines = text.split("\n")
    root = next((i for i, line in enumerate(lines) if line.startswith("design_decline_check:")), None)
    if root is None:
        return []
    block = []
    for line in lines[root + 1:]:
        if line.strip() and not line[0].isspace() and not line.startswith("#"):
            break
        block.append(line)
    child = min((len(line) - len(line.lstrip()) for line in block if line.strip() and not line.lstrip().startswith("#")), default=1)
    key = next((i for i, line in enumerate(block) if re.fullmatch(rf"[ \t]{{{child}}}rulings:[ \t]*", line)), None)
    if key is None:
        return []
    depth = len(block[key]) - len(block[key].lstrip())
    kept = []
    for line in block[key + 1:]:
        body = line.lstrip()
        if not body or body.startswith("#"):
            continue
        indent = len(line) - len(body)
        if indent < depth or (indent == depth and not body.startswith("- ")):
            break
        kept.append(line)
    return kept


def read_rulings(text):
    lines = rulings_lines(text)
    marks = [i for i, line in enumerate(lines) if re.match(r"[ \t]*-[ \t]", line)]
    if not marks:
        return []
    first = min(len(lines[i]) - len(lines[i].lstrip()) for i in marks)
    marks = [i for i in marks if len(lines[i]) - len(lines[i].lstrip()) == first]
    items = []
    for index, mark in enumerate(marks):
        dash = re.match(r"([ \t]*)-([ \t]+)", lines[mark])
        field = len(dash.group(1)) + 1 + len(dash.group(2))
        stop = marks[index + 1] if index + 1 < len(marks) else len(lines)
        fields = {}
        for line in [" " * dash.end() + lines[mark][dash.end():]] + lines[mark + 1:stop]:
            found = re.match(rf"[ \t]{{{field}}}([a-z]+):[ \t]*(.*)$", line)
            if found:
                fields.setdefault(found.group(1), found.group(2).strip().strip("\"'"))
        raw = fields.get("finding", "")
        fields["finding"] = int(raw) if raw.isdigit() else raw
        items.append(fields)
    return items


def plural_groups(count):
    return f"{count} group" if count == 1 else f"{count} groups"


def check_rulings(name, value, text, found, lines, word, errors, titled):
    """Check a design_decline_check report against the dispositions; return (upheld numbers, overruled count, decision groups)."""
    ruled = {}
    for item in read_rulings(text):
        number = item["finding"]
        if not isinstance(number, int) or not 1 <= number <= found:
            errors.append(f"{name}: '{value}' rules finding {number}, which the review does not list ({found} listed)")
        elif number in ruled:
            errors.append(f"{name}: '{value}' rules finding {number} more than once")
        elif missing := [key for key in RULING_REQUIRED if not item.get(key)]:
            errors.append(f"{name}: '{value}' rules finding {number} without {', '.join(repr(key) for key in missing)}")
        elif item.get("ruling") not in RULINGS:
            errors.append(f"{name}: '{value}' rules finding {number} as '{item.get('ruling', '')}', not one of {', '.join(RULINGS)}")
        else:
            ruled[number] = item
    declined = [n for n in range(1, found + 1) if DECLINED.match(lines.get(n, ""))]
    for number in declined:
        entry = lines[number]
        if number not in ruled:
            errors.append(f"{name}: declined finding {number} has no ruling in '{value}'")
        elif ruled[number]["ruling"] != "upheld":
            errors.append(f"{name}: declined finding {number} is ruled {ruled[number]['ruling']} in '{value}'; write 'fixed:', an AC-<id> or 'Needs decision:' for it, not 'declined:'")
        if HOST_REASON.match(entry) and not HOST_FORM.match(entry):
            errors.append(f"{name}: '{word} finding {number}:' declines a host component without 'host component <Name> at <path>: <reason>'")
    groups = {}
    for number, item in sorted(ruled.items()):
        entry = lines.get(number, "")
        if item["ruling"] == "upheld" and number not in declined:
            errors.append(f"{name}: '{value}' upholds finding {number}, which is not a declined finding")
        if item["ruling"] != "decision":
            continue
        if number not in declined and not NEEDS_DECISION.match(entry):
            errors.append(f"{name}: finding {number} is ruled decision in '{value}' and needs a '{word} finding {number}: Needs decision:' line")
        kind, owner = item.get("kind", ""), item.get("owner", "")
        if kind not in KINDS or not owner:
            errors.append(f"{name}: decision ruling for finding {number} needs a kind of {', '.join(KINDS)} and an owner")
        elif titled and kind == "host-look" and not item.get("adr") and not ADR_TITLE.search(entry):
            errors.append(f"{name}: 'Design finding {number}:' is a host-look decision and must end 'ADR: <short title>'")
        key = (kind, owner.strip().casefold())
        group = groups.setdefault(key, dict(kind=kind, owner=owner, numbers=[], change=item.get("change", "")))
        group["numbers"].append(number)
    upheld = [n for n, item in sorted(ruled.items()) if item["ruling"] == "upheld" and n in declined]
    overruled = sum(1 for item in ruled.values() if item["ruling"] == "overruled")
    return upheld, overruled, list(groups.values())


def ruling_notes(word, lines, upheld, groups):
    notes = [f"upheld {word} {n}: {lines[n].split(':', 1)[1].strip()}" for n in upheld]
    for group in groups:
        found = ", ".join(str(n) for n in group["numbers"])
        notes.append(f"decision {group['kind']}, owner {group['owner']} (findings {found}): {group['change']}")
    return notes


def decline_report(name, label, lines_found, folder, errors):
    value = lines_found[0].strip()
    text = saved_report(name, label, value, folder, errors)
    if text is None:
        return None, value
    if len(re.findall(r"^design_decline_check:", text, re.M)) != 1:
        errors.append(f"{name}: '{value}' is not a design_decline_check report: expected exactly 1 'design_decline_check:' line at column 0")
        return None, value
    root = re.search(r"^design_decline_check:(.*)$", text, re.M)
    if re.sub(r"(?:^|[ \t]+)#.*$", "", root.group(1)).strip():
        errors.append(f"{name}: '{value}' has a 'design_decline_check:' line with a value after its colon, so its children are not a mapping")
        return None, value
    return text, value


def check_design_review(path, body, declared, previews, errors):
    name = path.name
    review = DESIGN_REVIEW_LINE.search(body)
    if not review:
        errors.append(f"{name}: a ui task needs a 'Design review:' line naming the saved report")
        return None
    if len(DESIGN_REVIEW_LINE.findall(body)) > 1:
        errors.append(f"{name}: {len(DESIGN_REVIEW_LINE.findall(body))} 'Design review:' lines, expected exactly 1; a rerun replaces the old line with the last report")
        return None
    value = review.group(1).strip()
    if value.lower().startswith("not run"):
        errors.append(f"{name}: design review not run ({value}); a missing reviewer holds the stage")
        return None
    folder = task_folder(path)
    text = saved_report(name, "Design review:", value, folder, errors)
    if text is None:
        return None

    def on_preview(named):
        if len(named) != 1:
            errors.append(f"{name}: '{value}' has {len(named)} 'preview:' lines directly under 'design_review:', expected exactly 1")
        elif named[0].strip().strip("\"'") not in previews:
            errors.append(f"{name}: '{value}' reviewed preview '{named[0].strip().strip(chr(34)+chr(39))}' but the task's 'Preview:' line names {', '.join(repr(p) for p in previews)}")

    severities = design_report(name, value, text, errors, on_preview)
    if severities is None:
        return None
    found = len(severities)
    lines = {int(n): v.strip() for n, v in DESIGN_FINDING_LINE.findall(body)}
    repeated(DESIGN_FINDING_LINE.findall(body), "Design", name, errors)
    tally = {"ac": 0, "fixed": 0, "declined": 0, "decision": 0}
    for number in range(1, found + 1):
        entry = lines.get(number, "")
        if re.fullmatch(r"AC-[A-Za-z0-9]+", entry.split()[0] if entry else "") and entry.split()[0] in declared:
            tally["ac"] += 1
        elif re.match(r"fixed:\s*\S", entry):
            tally["fixed"] += 1
        elif re.match(r"declined:\s*\S", entry) and severities[number - 1] == "MINOR":
            tally["declined"] += 1
        elif re.match(r"Needs decision:\s*\S", entry):
            tally["decision"] += 1
        else:
            errors.append(f"{name}: report finding {number} has no 'Design finding {number}:' line naming a declared AC-<id>, 'fixed: <what changed>', 'declined: <reason>' (MINOR only) or 'Needs decision: <text>'")
    for number in sorted(set(lines) - set(range(1, found + 1))):
        errors.append(f"{name}: 'Design finding {number}:' has no finding in '{value}' ({found} listed)")
    summary = f"design review {value}: {found} findings, {tally['fixed']} fixed, {tally['ac']} criteria, {tally['declined']} declined, {tally['decision']} decisions"
    rulings = []
    checks = DECLINE_CHECK_LINE.findall(body)
    if len(checks) > 1:
        errors.append(f"{name}: {len(checks)} 'Decline check:' lines, expected exactly 1; a rerun replaces the old line with the last report")
    elif checks:
        ruled, check_value = decline_report(name, "Decline check:", checks, folder, errors)
        if ruled is not None:
            upheld, overruled, groups = check_rulings(name, check_value, ruled, found, lines, "Design", errors, True)
            summary += f"; decline check {check_value}: {len(upheld)} upheld, {overruled} overruled, {sum(len(g['numbers']) for g in groups)} decisions in {plural_groups(len(groups))}"
            rulings = ruling_notes("decline", lines, upheld, groups)
    elif tally["declined"]:
        errors.append(f"{name}: a 'Design finding n: declined:' line needs a 'Decline check:' line naming the saved ruling report")
    return [summary, *(f"preview: {preview}" for preview in preview_lines(path, previews)), *rulings]


def preview_lines(path, previews):
    task_dir = path.resolve().parent
    return [value if URL.match(value) else str(preview_target(task_dir, value)) for value in previews]


def validation_report(body):
    """The text of the last `## Stage Report: validation` section, or empty."""
    sections = re.split(r"(?m)^(?=## )", body)
    reports = [part for part in sections if re.match(r"## Stage Report: validation\b", part)]
    return reports[-1] if reports else ""


def file_digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_built_screen(path, body, previews, errors):
    name = path.name
    body = validation_report(body)
    reviews = BUILT_REVIEW_LINE.findall(body)
    if len(reviews) > 1:
        errors.append(f"{name}: {len(reviews)} 'Built screen review:' lines, expected exactly 1; a rerun replaces the old line with the last report")
        return None
    if not reviews:
        errors.append(f"{name}: built screen review not run: a ui task with a design review needs a 'Built screen review:' line or a quoted waiver")
        return None
    value = reviews[0].strip()
    if value.startswith("waived"):
        if not CAPTAIN_QUOTE.search(value):
            errors.append(f"{name}: built screen review not run: a waiver needs the Captain's words in 「…」")
        return None
    folder = task_folder(path)
    text = saved_report(name, "Built screen review:", value, folder, errors)
    if text is None:
        return None
    named = []
    severities = design_report(name, value, text, errors, named.extend)
    if severities is None:
        return None
    pictures = []
    for shot in named or [""]:
        shot_name = shot.strip().strip("\"'")
        picture = folder / shot_name
        if (not shot_name or Path(shot_name).is_absolute() or ".." in Path(shot_name).parts
                or not picture.is_file() or not picture.resolve().is_relative_to(folder.resolve())):
            errors.append(f"{name}: built screen review not run: '{value}' preview '{shot_name}' names no screenshot file inside the task folder")
            return None
        pictures.append(picture)
    task_dir, seen = path.resolve().parent, set()
    for preview in previews:
        if URL.match(preview):
            continue
        target = preview_target(task_dir, preview)
        seen.update(file_digest(p) for p in (target.rglob("*") if target.is_dir() else [target]) if p.is_file())
    for picture in pictures:
        if file_digest(picture) in seen:
            errors.append(f"{name}: built screen review not run: '{value}' preview '{picture.relative_to(folder)}' names a screenshot that is an ideation picture, or has the bytes of one")
            return None
    found = len(severities)
    lines = {int(n): v.strip() for n, v in BUILT_FINDING_LINE.findall(body)}
    repeated(BUILT_FINDING_LINE.findall(body), "Built screen", name, errors)
    for number in range(1, found + 1):
        entry = lines.get(number, "")
        token = entry.split()[0] if entry else ""
        if severities[number - 1] == "MAJOR" and re.fullmatch(r"F\d+", token):
            if not re.search(rf"^[ \t]*[-*][ \t]+{token}[ \t]+\S[^\n:]*:", body, re.M):
                errors.append(f"{name}: 'Built screen finding {number}:' names {token}, but the current validation report has no '- {token} <Class>:' bullet")
        elif not (severities[number - 1] == "MINOR" and (DECLINED.match(entry) or NEEDS_DECISION.match(entry))):
            errors.append(f"{name}: built screen finding {number} has no 'Built screen finding {number}:' line naming F<N> (MAJOR), 'declined: <reason>' (MINOR only) or 'Needs decision: <text>' (MINOR only)")
    for number in sorted(set(lines) - set(range(1, found + 1))):
        errors.append(f"{name}: 'Built screen finding {number}:' has no finding in '{value}' ({found} listed)")
    declines = BUILT_DECLINE_LINE.findall(body)
    upheld, groups = [], []
    if len(declines) > 1:
        errors.append(f"{name}: {len(declines)} 'Built screen decline check:' lines, expected exactly 1; a rerun replaces the old line with the last report")
    elif declines:
        ruled, check_value = decline_report(name, "Built screen decline check:", declines, folder, errors)
        if ruled is not None:
            upheld, _, groups = check_rulings(name, check_value, ruled, found, lines, "Built screen", errors, False)
    elif any(DECLINED.match(entry) for entry in lines.values()):
        errors.append(f"{name}: a 'Built screen finding n: declined:' line needs a 'Built screen decline check:' line naming the saved ruling report")
    summary = f"built screen review {value}: {found} findings, {len(upheld)} upheld declines, {sum(len(g['numbers']) for g in groups)} decisions in {plural_groups(len(groups))}"
    return [summary, *(f"preview: {picture.resolve()}" for picture in pictures), *ruling_notes("built-screen decline", lines, upheld, groups)]


def scope_lines(text):
    text, inside, start, at = text or "", False, None, 0
    for line in text.split("\n"):
        if FENCE.match(line):
            inside = not inside
        elif not inside and line.startswith("## "):
            if start is not None:
                return text[start:at].splitlines()
            if re.match(r"## Scope\b", line) and at + len(line) < len(text):
                start = at + len(line) + 1
        at += len(line) + 1
    return text[start:].splitlines() if start is not None else []


def git_out(task, *args):
    return subprocess.run(["git", "-C", str(task.parent), *args], capture_output=True)


def file_at(task, commit, rel):
    for name in (rel, rel[len("_archive/"):] if rel.startswith("_archive/") else f"_archive/{rel}"):
        done = git_out(task, "show", f"{commit}:{name}")
        if done.returncode == 0:
            return done.stdout.decode("utf-8", "replace")
    return None


def unarchived(rel):
    return rel[len("_archive/"):] if rel.startswith("_archive/") else rel


def task_path(task):
    return git_out(task, "rev-parse", "--show-prefix").stdout.decode().rstrip("\n") + task.name


def records_amendment(text, number):
    return any((m := AMENDMENT_DATED.match(e)) and int(m.group(1)) == number for e in amendment_entries((text or "").split("\n")) or [])


def introducing_commit(task, number):
    done = git_out(task, "log", "--follow", "--format=%H", f"-G^### Amendment {number} — ", "--", task.name)
    rel = git_out(task, "ls-files", "--full-name", "--", task.name).stdout.decode().strip() or task.name
    unreadable = None
    for commit in reversed(done.stdout.decode().split()):
        baseline = file_at(task, commit, rel)
        if baseline is None:
            unreadable = (commit, None)
        elif records_amendment(baseline, number):
            return commit, baseline
    return unreadable


def scope_hold(task):
    """('hold', line) for a Scope change with no record, ('not run', why), or ('clean', baseline)."""
    text = task.read_text()
    front, body = decision_ledger.split_task(text)
    if front is None:
        return "not run", "no frontmatter"
    status = FM_STATUS.search("\n".join(front))
    if not status or status.group(1) != "ideation":
        return "not run", f"stage is {status.group(1) if status else 'unknown'}, not ideation"
    closed = [e for e in decision_ledger.gate_entries(front)
              if e["stage"] == "backlog" and e["kind"] == "resolution" and e.get("decision") == "approve"]
    if not closed:
        return "not run", "no closed backlog approval"
    gate = closed[-1]
    try:
        bound = BOUND_URI.fullmatch(json.loads((task.parent / gate["room"] / "index.json").read_text())["artifacts"][0]["uri"])
    except (OSError, ValueError, KeyError, IndexError, TypeError):
        return "not run", "backlog briefing unreadable"
    if not bound:
        return "not run", "backlog briefing artifact has no sha"
    if git_out(task, "rev-parse", "--git-dir").returncode:
        return "not run", "not in a git checkout"
    baseline = file_at(task, bound.group(1), bound.group(2))
    if baseline is None:
        return "not run", "backlog sha not readable by git"
    foreign = unarchived(bound.group(2)) != unarchived(task_path(task))
    what, sha = "the backlog gate", bound.group(1)
    day = (gate.get("at") or "")[:10]
    dated = [AMENDMENT_DATED.match(e) for e in amendment_entries(body.split("\n")) or []]
    newer = [int(m.group(1)) for m in dated if m and m.group(2) >= day]
    if newer:
        found = introducing_commit(task, max(newer))
        if found is None:
            baseline, what, sha = text, "the newest amendment", "working copy"
        else:
            sha, baseline = found
            if baseline is None:
                return "not run", f"amendment {max(newer)} commit not readable by git"
            what = "the newest amendment"
    elif foreign:
        return "not run", f"backlog briefing binds {bound.group(2)}, not this task file"
    before, now = scope_lines(baseline), scope_lines(text)
    changed = [l for l in now if l not in before] + [l for l in before if l not in now]
    changed = [l for l in changed if l.strip() and not SCOPE_EXEMPT.match(l)]
    if not changed:
        return "clean", sha
    return "hold", SCOPE_HOLD.format(what=what, sha=sha[:8], line=changed[0].strip()[:80])


# see docs/adr/0041-seed-admission-enforces-required-fields.md
def check_seed_fields(name, text):
    from role_triggers import budget_bound, budget_text

    front = FRONTMATTER.match(text)
    body = text[front.end():] if front else text
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    fields = (("Non-goals", r"Non-goals?"), ("Budget", r"Budget"),
              ("Stop condition", r"Stop conditions?"))
    found, current, fence = set(), "", None
    for line in body.splitlines():
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                fence = None
            continue
        if marker:
            fence = marker[1]
            continue
        heading = re.match(r"^##[ \t]+(.+?)[ \t]*$", line)
        if heading:
            current = heading[1].lower()
            continue
        if re.match(r"^#{1,6}[ \t]", line):
            current = ""
        if line.lstrip().startswith(">") or line.startswith(("    ", "\t", "#")):
            continue
        for label, pattern in fields:
            value = None
            if re.fullmatch(pattern, current, re.I):
                value = line
            elif current == "scope":
                match = re.match(r"^(?:[-*] )?" + pattern + r":[ \t]*(.*)$", line, re.I)
                if match:
                    value = match[1]
            if value is not None:
                value = re.sub(r"<[^>]*>", "", value).strip(" \t-'\"*")
                if value:
                    found.add(label)
    errors = [f"{name}: missing required body field: {label}" for label, _ in fields if label not in found]
    # see docs/adr/0077-a-task-budget-counts-cycles-and-past-it-the-question-returns-to-the-captain.md
    if "Budget" in found and not budget_bound(budget_text(body, amendments=False)):
        errors.append(f"{name}: Budget must start with 'N cycles per stage', 'N implementation and M validation cycles', "
                      "'N ideation, N implementation and M validation cycles', "
                      "'at most N dispatches total' or '最多 N 次派工'; an explicit agent-minutes clause may precede it, but minutes are not counted")
    return errors


# see docs/adr/0077-a-task-budget-counts-cycles-and-past-it-the-question-returns-to-the-captain.md
def worth_lines(text):
    from role_triggers import FENCE as marker_pattern

    fence, comment = None, False
    for line in text.splitlines():
        marker = marker_pattern.match(line) if not comment else None
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence):
                fence = None
            continue
        if marker:
            fence = marker[1]
            continue
        visible = ""
        while line:
            if comment:
                _, closed, line = line.partition("-->")
                comment = not bool(closed)
                if comment:
                    break
            else:
                part, opened, line = line.partition("<!--")
                visible += part
                comment = bool(opened)
        yield visible


def worth_stage(path):
    from dispatch_records import find_readme

    path = path.resolve()
    readme = find_readme(path)
    workflow = readme.parent if readme else path.parent
    done = subprocess.run([os.environ.get("SPACEDOCK_BIN") or "spacedock", "status", "--workflow-dir", str(workflow),
                           "--read", str(path), "--json"], capture_output=True, text=True, timeout=30)
    if done.returncode:
        raise ValueError((done.stderr or done.stdout).strip() or f"Spacedock read exited {done.returncode}")
    data = json.loads(done.stdout)
    if not isinstance(data, dict):
        raise ValueError("malformed Spacedock read")
    fields = data.get("frontmatter")
    if data.get("command") != "read" or data.get("path") != str(path) or not isinstance(fields, dict) \
            or ("status" in fields and not isinstance(fields["status"], str)):
        raise ValueError("malformed or mismatched Spacedock read")
    return fields.get("status")


# see docs/adr/0076-a-journey-workflows-new-seed-records-its-story-or-none.md
def check_story_record(path, text, seed):
    from workflow_extensions import readme_extensions

    try:
        for parent in path.resolve().parents:
            readme = parent / "README.md"
            if not readme.is_file():
                continue
            front, _ = decision_ledger.split_task(readme.read_text())
            if front is not None and any(re.match(r"^stages:", line) for line in front):
                if "journey-map" not in readme_extensions(readme):
                    return []
                break
        else:
            return []
    except (OSError, UnicodeError, ValueError) as error:
        return [f"{path.name}: cannot read workflow story rule: {error}"]
    plain, fence = [], None
    for line in re.sub(r"<!--.*?-->", "", text, flags=re.S).splitlines():
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                fence = None
        elif marker:
            fence = marker[1]
        else:
            plain.append(line)
    fo, _ = split_fo("\n".join(plain))
    record = re.search(r"^Story:[ \t]*(.*)$", fo, re.M)
    value = record[1].strip() if record else ""
    named = value.split()[0] if value else ""
    if not named or (named in ("none", "none:") and not re.match(r"^none:[ \t]*\S", value)):
        return [f"{path.name}: '## FO alignment' needs a 'Story:' line naming a story or 'none: <reason>'"] if seed else []
    if seed:
        return []
    front, _ = decision_ledger.split_task(text)
    stored = next((line.split(":", 1)[1] for line in front or [] if line.startswith("journey-story:")), "")
    try:
        story = decision_ledger.unquote(re.sub(r"[ \t]+#.*$", "", stored).strip())
    except ValueError as error:
        return [f"{path.name}: cannot read journey-story: {error}"]
    if (named == "none:" and story) or (named != "none:" and named != story):
        return [f"{path.name}: 'Story:' names {named} but journey-story is {story or '(empty)'}"]
    return []


# see docs/adr/0086-a-captain-question-outside-a-gate-stays-open-until-answered.md
ASK_SENTENCE = 'Before asking the Captain outside a gate, FO runs `python3 <package>/scripts/task_timeline.py <state> <task> ask "<question>" --holds <task|acceptance|nothing> --by "<session>"` and records each later showing, answer or withdrawal with the command it prints; `python3 <package>/scripts/task_timeline.py <state> --open` lists what waits on him.'


def question_adoption(path):
    from dispatch_records import find_readme

    readme = find_readme(path)
    if readme is None:
        return None, "no adopted workflow README"
    readme = readme.resolve()
    try:
        repo = Path(subprocess.run(["git", "-C", str(readme.parent), "rev-parse", "--show-toplevel"],
                                  capture_output=True, text=True, check=True).stdout.strip())
        shallow = subprocess.run(["git", "-C", str(repo), "rev-parse", "--is-shallow-repository"],
                                 capture_output=True, text=True, check=True).stdout.strip()
        if shallow == "true":
            return None, "shallow workflow history"
        if ASK_SENTENCE not in readme.read_text():
            return None, "approved ask sentence absent"
        relative = readme.relative_to(repo).as_posix()
        history = subprocess.run(["git", "-C", str(repo), "log", "--reverse", "--format=%H %aI",
                                  "-S", ASK_SENTENCE, "--", relative], capture_output=True, text=True, check=True)
        for line in history.stdout.splitlines():
            sha, date = line.split(" ", 1)
            text = subprocess.run(["git", "-C", str(repo), "show", f"{sha}:{relative}"],
                                  capture_output=True, text=True, check=True).stdout
            if ASK_SENTENCE in text:
                return date[:10], None
        return None, "ask sentence has no introducing commit"
    except (OSError, ValueError, subprocess.CalledProcessError):
        return None, "workflow git history unavailable"


def check_question_records(path, lines, notes):
    from task_timeline import ask_files, read_asks

    adopted, why = question_adoption(path)
    if adopted is None:
        if notes is not None and why != "no adopted workflow README":
            notes.append(f"{path.name}: question record check not run: {why}")
        return []
    entries = [e for e in parse_amendments(lines)[0]
               if (m := AMENDMENT_DATED.match(e.header)) and m[2] >= adopted]
    if not entries:
        return []
    own = task_folder(path)
    state = own.parent.parent if own.parent.name == "_archive" else own.parent
    try:
        records = []
        for file in ask_files(state):
            events = read_asks(file)
            shared = {e.get("key") for e in events if own.name in (e.get("tasks") or [])}
            records.extend(e for e in events if file.parent == own or e.get("key") in shared)
    except (OSError, ValueError) as exc:
        return [f"{path.name}: cannot read question records: {exc}"]
    questions = [e["asked"] for e in records if isinstance(e.get("asked"), str)]
    errors = []
    for entry in entries:
        asked = re.search(r"^Asked:[ \t]*(.+)$", entry.prefix, re.M)
        if not asked or re.fullmatch(r"(?:commit )?[0-9a-f]{7,40}", asked[1].strip()):
            continue
        value = asked[1].strip()
        start, depth, quoted = None, 0, None
        for i, char in enumerate(value):
            if char == "「":
                if depth == 0:
                    start = i + 1
                depth += 1
            elif char == "」" and depth:
                depth -= 1
                if depth == 0:
                    quoted = value[start:i]
                    break
        if (quoted if quoted is not None else value) not in questions:
            errors.append(f"{path.name}: '{entry.header}' quoted question has no ask record; "
                          "FO: record it, using --late when the asking time is unknown")
    return errors


def check_task(path, seed=False, notes=None):
    errors = []
    try:
        text = path.read_text()
    except (OSError, UnicodeError) as exc:
        return [f"{path.name}: cannot read task: {exc}"]
    if not FO_HEADING.search(text):
        errors.append(f"{path.name}: missing '## FO alignment' section")
    _, body = split_fo(text)
    fo, _ = split_fo("\n".join(unfenced(text.split("\n"))))
    match = SURFACES.search(fo)
    surfaces = set()
    if len(SURFACES.findall(fo)) > 1:
        errors.append(f"{path.name}: '## FO alignment' has {len(SURFACES.findall(fo))} 'Surfaces:' lines, expected exactly 1")
    if not match or not match.group(1).strip():
        errors.append(f"{path.name}: '## FO alignment' needs a non-empty 'Surfaces:' line")
    else:
        raw = [v.strip() for v in match.group(1).split(",") if v.strip()]
        surfaces = set(raw)
        unknown = sorted(surfaces - KNOWN)
        if unknown:
            errors.append(f"{path.name}: 'Surfaces:' has unknown value(s) {', '.join(unknown)}")
        if "none" in surfaces and len(surfaces) > 1:
            errors.append(f"{path.name}: 'Surfaces:' combines 'none' with other values")

    visible = VISIBLE.search(fo)
    if not visible:
        errors.append(f"{path.name}: '## FO alignment' needs a 'Visible change:' line")
    else:
        value = visible.group(1).strip()
        if value.lower() != "none" and "ui" not in surfaces:
            errors.append(f"{path.name}: 'Visible change:' is not 'none' but 'Surfaces:' has no 'ui'")
        if value.lower() == "none" and "ui" in surfaces:
            errors.append(f"{path.name}: 'Visible change: none' contradicts 'ui' in 'Surfaces:'")

    errors.extend(check_story_record(path, text, seed))
    if seed:
        return check_seed_fields(path.name, text) + errors
    if "ui" in surfaces:
        check_ui(path.name, body, path.resolve().parent, errors)
    if "db" in surfaces:
        check_db(path.name, body, errors)
    lines = text.split("\n")
    declared = check_criteria(path.name, lines, errors)
    check_amendments(path.name, lines, declared, errors, dispatched_amendments(task_folder(path)))
    errors.extend(check_question_records(path, lines, notes))
    for title, key in escaped_amendment_lines(lines):
        errors.append(f"{path.name}: '{title}' {key} line holds a backslash-quote copied from JSON; FO writes his words and the question as they were said")
    if notes is not None:
        notes.extend(f"{path.name}: this Override line is in no gate resolution reason: {line[:120]}" for line in owed_overrides(text))
    front = FRONTMATTER.match(text)
    profile, status = (FM_PROFILE.search(front.group(1)), FM_STATUS.search(front.group(1))) if front else (None, None)
    plain = "\n".join(unfenced(lines))
    worth = list(worth_lines(text))
    design = section(worth, re.compile(r"^## Design[ \t]*$", re.I))
    if not any(re.fullmatch(r"### Worth questions[ \t]*", line, re.I) for line in (design if design is not None else worth)):
        needed = design is not None
        if text.lstrip("\ufeff\n").startswith("---\n"):
            try:
                stage = worth_stage(path)
                needed = stage == "ideation" or (needed and stage in (None, "", "backlog"))
            except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
                needed = False
                errors.append(f"{path.name}: cannot read stage for Worth questions: {exc}")
        if needed:
            errors.append(f"{path.name}: design needs '### Worth questions': Captain words served, what breaks without each part, and the premise's cheap test")
    if front and pilot_ideation(front.group(1)) and not design_approved(text):
        for key, missing in proof_gaps(lines):
            errors.append(f"{path.name}: Pilot criterion {key} has no {', '.join(missing)} in its proof record "
                          "(command, observed exit <n>, output path; Falsifier text does not count) and is not named "
                          "with a reason under a 'Not provable now' heading")
    if profile and status and (profile.group(1), status.group(1)) == ("prod", "ideation"):
        summary = check_security(path, plain, declared, errors)
        if summary and notes is not None:
            notes.append(summary)
    if "ui" in surfaces and status and status.group(1) == "ideation":
        shown = [v.strip() for v in PREVIEW.findall("\n".join(unfenced(body.split("\n"))))]
        summary = check_design_review(path, plain, declared, shown, errors)
        if summary and notes is not None:
            notes.extend(summary)
    if "ui" in surfaces and status and status.group(1) == "validation" and DESIGN_REVIEW_LINE.search(plain):
        shown = [v.strip() for v in PREVIEW.findall("\n".join(unfenced(body.split("\n"))))]
        summary = check_built_screen(path, plain, shown, errors)
        if summary and notes is not None:
            notes.extend(summary)
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    check = sub.add_parser("check", help="check a task file: FO alignment, surface artifacts, acceptance criteria, Captain amendments")
    check.add_argument("--seed", action="store_true", help="check seed fields and FO alignment before admitting a new task")
    check.add_argument("task")
    args = parser.parse_args(argv)
    path = Path(args.task)
    if not path.is_file() and path.name and (path.is_dir() or not path.suffix):
        path = path.parent / (path.name + ".md")
    if not path.is_file():
        parser.error(f"task file not found: {path}; pass a task file or its suffixless name")
    notes = []
    errors = check_task(path, seed=args.seed, notes=notes)
    verdict, why = ("clean", "") if args.seed else scope_hold(path)
    if verdict == "hold":
        errors.append(why)
    for error in errors:
        print(error)
    if not errors:
        print(f"{path.name}: {'seed fields and FO alignment recorded' if args.seed else 'design surfaces presentable'}")
    for note in notes:
        print(note)
    if verdict == "not run":
        print(f"scope check not run: {why}")
    if not errors:
        front, _ = decision_ledger.split_task(path.read_text())
        status = FM_STATUS.search("\n".join(front or []))
        if status and status.group(1) in ("backlog", "ideation"):
            from delivery_gate import ASK_FORM
            print(ASK_FORM)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
