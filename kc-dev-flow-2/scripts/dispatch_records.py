#!/usr/bin/env python3
"""Check a task's dispatch records: each needs a Dispatched line with a full SHA, a Model line,
and non-empty Checklist and Scope notes sections.

Usage: dispatch_records.py <task folder or task .md file>
Exit 1 naming each record that lacks a part, or when the task has no dispatch records.
"""
import re
import sys
from pathlib import Path

PARTS = {
    "a 'Dispatched:' line with a full 40-character SHA": re.compile(r"^Dispatched:.*\b[0-9a-f]{40}\b", re.M),
    "a 'Model:' line": re.compile(r"^Model:[ \t]*\S", re.M),
    "a non-empty '## Checklist' section": re.compile(r"^## Checklist[ \t]*\n(?:[ \t]*\n)*(?!## )\S", re.M),
    "a non-empty '## Scope notes' section": re.compile(r"^## Scope notes[ \t]*\n(?:[ \t]*\n)*(?!## )\S", re.M),
}


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
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
