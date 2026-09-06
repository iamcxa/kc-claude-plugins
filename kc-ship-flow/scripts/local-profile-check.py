#!/usr/bin/env python3
"""Check that a kc-ship-flow batch workflow README's Local Profile table carries every
required row before the first-officer skill dispatches a batch.

usage: local-profile-check.py <readme.md>
exit 0: every required row present.
exit 1: at least one required row is missing; stderr names each missing row.
exit 2: usage error, unreadable file, or no Local Profile block found.
"""
from __future__ import annotations

import sys
from pathlib import Path

START_MARKER = "<!-- kc-ship-flow-static-local-profile:start -->"
END_MARKER = "<!-- kc-ship-flow-static-local-profile:end -->"

REQUIRED_ROWS = [
    "Holder",
    "Runtime",
    "Planning provider",
    "UAT delivery",
    "Approval defaults",
    "E2E flows",
    "Pin",
    "Installed contract interface",
]


def extract_row_labels(block: str) -> list[str]:
    labels = []
    for line in block.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if not cells:
            continue
        label = cells[0]
        if not label or set(label) <= {"-", ":"}:
            continue
        labels.append(label)
    # First data row's header ("Role") is not a required row; drop it if present verbatim.
    if labels and labels[0] == "Role":
        labels = labels[1:]
    return labels


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    readme_path = Path(argv[1])
    try:
        text = readme_path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"LOCAL_PROFILE_UNREADABLE: {readme_path}: {exc}", file=sys.stderr)
        return 2

    start = text.find(START_MARKER)
    end = text.find(END_MARKER)
    if start == -1 or end == -1 or end < start:
        print(
            f"LOCAL_PROFILE_MARKER_MISSING: {readme_path} has no matched "
            f"{START_MARKER} .. {END_MARKER} block",
            file=sys.stderr,
        )
        return 2

    block = text[start + len(START_MARKER) : end]
    present = set(extract_row_labels(block))
    missing = [row for row in REQUIRED_ROWS if row not in present]
    if missing:
        print(f"LOCAL_PROFILE_MISSING_ROW: {', '.join(missing)}", file=sys.stderr)
        return 1

    print(f"LOCAL_PROFILE_OK: {len(REQUIRED_ROWS)} required rows present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
