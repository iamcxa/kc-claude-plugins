#!/usr/bin/env python3
"""Check a docs/adr directory against the dev2 ADR format; exit 1 on any violation."""
import argparse
import re
import sys
from pathlib import Path

NAME = re.compile(r"^(\d{4})-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
SECTIONS = ["Status", "Context", "Decision", "Consequences"]
STATUS = re.compile(r"^(Proposed|Accepted|Deprecated|Superseded by (\d{4}))$")
LEGACY = re.compile(r"^Status: Legacy\b", re.M)
SKIP = {"README.md", "index.md", "template.md"}


def sections(text):
    found, current = {}, None
    for line in text.split("\n"):
        if line.startswith("## "):
            current = line[3:].strip()
            found.setdefault("_order", []).append(current)
            found[current] = []
        elif current:
            found[current].append(line)
    return found


def check_file(path, numbers):
    errors, text = [], path.read_text()
    number = int(NAME.match(path.name).group(1))
    head = "\n".join(text.split("\n")[:30])
    if LEGACY.search(head):
        return errors, True
    first = next((l for l in text.split("\n") if l.strip()), "")
    title = re.match(r"^# (\d+)\. \S", first)
    if not title or int(title.group(1)) != number:
        errors.append(f"{path.name}: first line must be '# {number}. <title>'")
    preamble = text.split("\n## ", 1)[0]
    if not re.search(r"^Date: \d{4}-\d{2}-\d{2}$", preamble, re.M):
        errors.append(f"{path.name}: needs a 'Date: YYYY-MM-DD' line before the first section")
    found = sections(text)
    if found.get("_order") != SECTIONS:
        errors.append(f"{path.name}: sections must be exactly {', '.join(SECTIONS)} in that order")
    for name in SECTIONS:
        if not "".join(found.get(name, [])).strip():
            errors.append(f"{path.name}: section '{name}' is empty")
    status = next((l.strip() for l in found.get("Status", []) if l.strip()), "")
    matched = STATUS.match(status)
    if not matched:
        errors.append(f"{path.name}: status '{status}' is not Proposed, Accepted, Deprecated or 'Superseded by NNNN'")
    elif matched.group(2) and int(matched.group(2)) not in numbers:
        errors.append(f"{path.name}: superseded by {matched.group(2)}, which does not exist")
    decision = "\n".join(found.get("Decision", []))
    for label in ("**Words:**", "**Options considered:**"):
        if label not in decision:
            errors.append(f"{path.name}: Decision needs a '{label}' line")
    return errors, False


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("adr_dir")
    parser.add_argument("--require", nargs="*", default=[], help="ADR numbers this change must add or update")
    args = parser.parse_args(argv)
    root = Path(args.adr_dir)
    errors, files = [], {}
    for path in sorted(root.glob("*.md")):
        if path.name in SKIP:
            continue
        match = NAME.match(path.name)
        if not match:
            errors.append(f"{path.name}: file name must be NNNN-short-title.md")
            continue
        number = int(match.group(1))
        if number in files:
            errors.append(f"{path.name}: number {number} is also used by {files[number].name}")
        files[number] = path
    legacy = set()
    for number, path in files.items():
        found, is_legacy = check_file(path, set(files))
        errors += found
        if is_legacy:
            legacy.add(number)
    for raw in args.require:
        number = int(raw)
        if number not in files:
            errors.append(f"required ADR {raw} does not exist")
        elif number in legacy:
            errors.append(f"required ADR {raw} is a legacy record; a new ruling needs its own file")
    for error in errors:
        print(error)
    if not errors:
        print(f"{len(files)} ADR file(s) checked, {len(legacy)} legacy")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
