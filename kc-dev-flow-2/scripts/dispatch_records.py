#!/usr/bin/env python3
"""Check a task's dispatch records: each needs a Dispatched line with a full SHA, a Model line,
non-empty Checklist and Scope notes sections, and a scope-notes line naming `main` as the completion recipient.

Usage: dispatch_records.py <task folder or task .md file>
       dispatch_records.py --names <record file>...
Exit 1 naming each record that lacks a part, or when the task has no dispatch records.
--names prints `<file>:<line>: bare package script name <NAME>` for each package script (a .py file
directly under <package>/scripts/ or <package>/extensions/<name>/) written with no directory part in the
Checklist or Scope notes section (the whole file when it has neither heading), and exits 1 when any is found.
"""
import re
import sys
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent.parent

PARTS = {
    "a 'Dispatched:' line with a full 40-character SHA": re.compile(r"^Dispatched:.*\b[0-9a-f]{40}\b", re.M),
    "a 'Model:' line": re.compile(r"^Model:[ \t]*\S", re.M),
    "a non-empty '## Checklist' section": re.compile(r"^## Checklist[ \t]*\n(?:[ \t]*\n)*(?!## )\S", re.M),
    "a non-empty '## Scope notes' section": re.compile(r"^## Scope notes[ \t]*\n(?:[ \t]*\n)*(?!## )\S", re.M),
    "a scope-notes line naming main as the completion recipient":
        re.compile(r"^## Scope notes\b(?:(?!^## )[\s\S])*?\bcompletion(?: message)? to [`']?main(?![\w-])", re.M | re.I),
}

SCRIPT_TOKEN = re.compile(r"(?<![\w./~-])([\w-]+\.py)(?!\w)")
SCANNED = re.compile(r"^## (?:Checklist|Scope notes)[ \t]*$")


def package_scripts(package):
    return {p.name for pattern in ("scripts/*.py", "extensions/*/*.py") for p in package.glob(pattern)}


def bare_names(text, names):
    lines = text.splitlines()
    if not any(SCANNED.match(line) for line in lines):
        scanned = range(len(lines))
    else:
        scanned, inside = [], False
        for number, line in enumerate(lines):
            if line.startswith("## "):
                inside = bool(SCANNED.match(line))
            elif inside:
                scanned.append(number)
    return [(number + 1, name) for number in scanned
            for name in dict.fromkeys(SCRIPT_TOKEN.findall(lines[number])) if name in names]


def check_names(files, package):
    names = package_scripts(package)
    found = False
    for file in files:
        for number, name in bare_names(Path(file).read_text(), names):
            print(f"{file}:{number}: bare package script name {name}")
            found = True
    return 1 if found else 0


def main(argv=None, package=PACKAGE):
    args = sys.argv[1:] if argv is None else argv
    if args[:1] == ["--names"] and len(args) > 1:
        return check_names(args[1:], package)
    if len(args) != 1 or args[0] == "--names":
        print(__doc__.strip())
        return 2
    task = Path(args[0])
    folder = task.with_suffix("") if task.suffix == ".md" else task
    records = sorted((folder / "dispatch").glob("*.md"))
    if not records:
        print(f"{folder}: no dispatch records under dispatch/")
        return 1
    errors = [f"{path.name}: needs {part}" for path in records
              for part, pattern in PARTS.items() if not pattern.search(path.read_text())]
    for error in errors:
        print(error)
    if not errors:
        print(f"{len(records)} dispatch record(s) complete")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
