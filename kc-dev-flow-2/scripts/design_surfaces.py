#!/usr/bin/env python3
"""Check a dev2 task file for the design-surface artifacts its Surfaces: line owes; exit 1 on any violation."""
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


def check_task(path):
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

    if "ui" in surfaces:
        check_ui(path.name, body, path.resolve().parent, errors)
    if "db" in surfaces:
        check_db(path.name, body, errors)
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    check = sub.add_parser("check", help="check a task file for the design-surface artifacts its Surfaces: owes")
    check.add_argument("task")
    args = parser.parse_args(argv)
    path = Path(args.task)
    errors = check_task(path)
    for error in errors:
        print(error)
    if not errors:
        print(f"{path.name}: design surfaces presentable")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
