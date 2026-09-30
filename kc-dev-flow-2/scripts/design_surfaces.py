#!/usr/bin/env python3
"""Check a dev2 task file: the FO-alignment record, the artifacts its Surfaces: line owes, its acceptance criteria and any Captain amendments; exit 1 on any violation."""
import argparse
import re
import sys
from pathlib import Path

KNOWN = {"ui", "db", "none"}
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
AC_DECLARATION = re.compile(r"\*\*(AC-[A-Za-z0-9]+)[^*\n]*\*\*")
AMENDMENTS_HEADING = re.compile(rf"^{GO_SPACE}## Captain amendments{GO_SPACE}$", re.I)
CAPTAIN_WORDS = re.compile(r"^Captain:[ \t]*\S", re.M)
SUPERSEDES = re.compile(r"^Supersedes:(.*)$", re.M)
AC_ID = re.compile(r"AC-[A-Za-z0-9]+")
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
    target = Path(value)
    if not target.is_absolute():
        target = task_dir / value
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
            end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
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


def check_amendments(name, lines, declared, errors):
    body = section(unfenced(lines), AMENDMENTS_HEADING)
    if body is None:
        return
    for entry in re.split(r"(?m)^(?=### )", "\n".join(body))[1:]:
        title = entry.split("\n", 1)[0].strip()
        if not CAPTAIN_WORDS.search(entry):
            errors.append(f"{name}: '{title}' has no 'Captain:' line with his words")
        line = SUPERSEDES.search(entry)
        for superseded in sorted(set(AC_ID.findall(line.group(1) if line else "")) & declared):
            errors.append(f"{name}: '{title}' supersedes {superseded} but it is still declared in '## Acceptance criteria'")


def check_task(path, seed=False):
    errors = []
    text = path.read_text()
    if not FO_HEADING.search(text):
        errors.append(f"{path.name}: missing '## FO alignment' section")
    fo, body = split_fo(text)
    match = SURFACES.search(fo)
    surfaces = set()
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
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    check = sub.add_parser("check", help="check a task file: FO alignment, surface artifacts, acceptance criteria, Captain amendments")
    check.add_argument("--seed", action="store_true", help="check only the FO-alignment record, before ideation is dispatched")
    check.add_argument("task")
    args = parser.parse_args(argv)
    path = Path(args.task)
    errors = check_task(path, seed=args.seed)
    for error in errors:
        print(error)
    if not errors:
        print(f"{path.name}: {'FO alignment recorded' if args.seed else 'design surfaces presentable'}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
