#!/usr/bin/env python3
"""Check a dev2 task file: the FO-alignment record, the artifacts its Surfaces: line owes, its acceptance criteria and any Captain amendments; exit 1 on any violation.

While the task's frontmatter says `status: ideation` it also holds a `## Scope` line added or removed after the backlog gate closed.
The baseline is the task file at the commit that added the newest `### Amendment N — <date>` dated on or after the backlog approval
(the working copy when that heading is uncommitted), else at the sha the backlog briefing binds (`git-root://state/<sha>/<path>`);
lines opening with Non-goals, Budget, Stop condition or Follow-up: are exempt. The check reads git history and the working copy,
not what the Captain said; an amendment covers every earlier unrecorded Scope edit. It prints `scope check not run: <why>` and
leaves the exit code alone in any other stage, with no closed backlog approval, or outside a git checkout.
"""
import argparse
import hashlib
import json
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
CAPTAIN_WORDS = re.compile(r"^Captain:[ \t]*\S", re.M)
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


def check_criteria(name, lines, errors):
    body = section(lines, AC_HEADING)
    if body is None:
        errors.append(f"{name}: missing '## Acceptance criteria' section")
        return set()
    declared = {found for line in body for found in AC_DECLARATION.findall(line)}
    if not declared:
        errors.append(f"{name}: '## Acceptance criteria' declares no criterion (a '**AC-<id>**' bold line)")
    return declared


def declarations(lines):
    return [(found.group(1), line) for line in lines for found in [DECLARATION_LINE.match(line)] if found]


def amendment_entries(lines):
    body = section(unfenced(lines), AMENDMENTS_HEADING)
    return None if body is None else re.split(r"(?m)^(?=### )", "\n".join(body))[1:]


def check_amendments(name, lines, declared, errors):
    entries = amendment_entries(lines)
    if entries is None:
        return
    moved = [declarations(e.split("\n")[1:]) for e in entries]
    live = declarations(section(lines, AC_HEADING) or [])
    for index, entry in enumerate(entries):
        title = entry.split("\n", 1)[0].strip()
        if not CAPTAIN_WORDS.search(entry):
            errors.append(f"{name}: '{title}' has no 'Captain:' line with his words")
        line = SUPERSEDES.search(entry)
        value = line.group(1) if line else ""
        waiver = NO_REPLACEMENT.search(value)
        named = set(AC_ID.findall(value[:waiver.start()] if waiver else value))
        for superseded in sorted(named & declared):
            errors.append(f"{name}: '{title}' supersedes {superseded} but it is still declared in '## Acceptance criteria'")
        held = {found for found, _ in moved[index]}
        if held - named:
            errors.append(f"{name}: '{title}' holds {', '.join(sorted(held - named))} but its 'Supersedes:' line does not name them")
        digits = re.search(r"\d+", title)
        number = digits.group() if digits else str(index + 1)
        marker = re.compile(rf"Amended by Captain, amendment {number}(?!\d)")
        others = [pair for i, pairs in enumerate(moved) if i != index for pair in pairs]
        if named and not waiver and not any(marker.search(text) for _, text in live + others):
            errors.append(f"{name}: '{title}' supersedes {', '.join(sorted(named))} but no criterion says 'Amended by Captain, amendment {number}' and its 'Supersedes:' line does not say 'no replacement'")


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
    on_preview(re.findall(rf"^{child}preview:[ \t]*(.*)$", block, re.M))
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
        elif missing := [key for key in RULING_REQUIRED if key not in item]:
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
    shot_name = named[0].strip().strip("\"'") if len(named) == 1 else ""
    picture = folder / shot_name
    if not shot_name or Path(shot_name).is_absolute() or ".." in Path(shot_name).parts or not picture.is_file():
        errors.append(f"{name}: built screen review not run: '{value}' names no screenshot file inside the task folder")
        return None
    task_dir, seen = path.resolve().parent, set()
    for preview in previews:
        if URL.match(preview):
            continue
        target = preview_target(task_dir, preview)
        seen.update(file_digest(p) for p in (target.rglob("*") if target.is_dir() else [target]) if p.is_file())
    if file_digest(picture) in seen:
        errors.append(f"{name}: built screen review not run: '{value}' names a screenshot that is an ideation picture, or has the bytes of one")
        return None
    found = len(severities)
    lines = {int(n): v.strip() for n, v in BUILT_FINDING_LINE.findall(body)}
    repeated(BUILT_FINDING_LINE.findall(body), "Built screen", name, errors)
    for number in range(1, found + 1):
        entry = lines.get(number, "")
        token = entry.split()[0] if entry else ""
        if severities[number - 1] == "MAJOR" and re.fullmatch(r"F\d+", token):
            if not re.search(rf"^[ \t]*[-*][ \t]+{token}[ \t]+\S[^\n:]*:", validation_report(body), re.M):
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
    return [summary, f"preview: {picture.resolve()}", *ruling_notes("built-screen decline", lines, upheld, groups)]


def scope_lines(text):
    found = re.search(r"^## Scope\b[^\n]*\n(.*?)(?=^## |\Z)", text or "", re.M | re.S)
    return (found.group(1) if found else "").splitlines()


def git_out(task, *args):
    return subprocess.run(["git", "-C", str(task.parent), *args], capture_output=True)


def file_at(task, commit, rel):
    for name in (rel, rel[len("_archive/"):] if rel.startswith("_archive/") else f"_archive/{rel}"):
        done = git_out(task, "show", f"{commit}:{name}")
        if done.returncode == 0:
            return done.stdout.decode("utf-8", "replace")
    return None


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
    before, now = scope_lines(baseline), scope_lines(text)
    changed = [l for l in now if l not in before] + [l for l in before if l not in now]
    changed = [l for l in changed if l.strip() and not SCOPE_EXEMPT.match(l)]
    if not changed:
        return "clean", sha
    return "hold", SCOPE_HOLD.format(what=what, sha=sha[:8], line=changed[0].strip()[:80])


def check_task(path, seed=False, notes=None):
    errors = []
    text = path.read_text()
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

    if seed:
        return errors
    if "ui" in surfaces:
        check_ui(path.name, body, path.resolve().parent, errors)
    if "db" in surfaces:
        check_db(path.name, body, errors)
    lines = text.split("\n")
    declared = check_criteria(path.name, lines, errors)
    check_amendments(path.name, lines, declared, errors)
    front = FRONTMATTER.match(text)
    profile, status = (FM_PROFILE.search(front.group(1)), FM_STATUS.search(front.group(1))) if front else (None, None)
    plain = "\n".join(unfenced(lines))
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
    check.add_argument("--seed", action="store_true", help="check only the FO-alignment record, before ideation is dispatched")
    check.add_argument("task")
    args = parser.parse_args(argv)
    path = Path(args.task)
    notes = []
    errors = check_task(path, seed=args.seed, notes=notes)
    verdict, why = ("clean", "") if args.seed else scope_hold(path)
    if verdict == "hold":
        errors.append(why)
    for error in errors:
        print(error)
    if not errors:
        print(f"{path.name}: {'FO alignment recorded' if args.seed else 'design surfaces presentable'}")
        for note in notes:
            print(note)
    if verdict == "not run":
        print(f"scope check not run: {why}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
