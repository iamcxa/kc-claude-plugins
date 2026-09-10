#!/usr/bin/env python3
"""Check that a kc-ship-flow batch workflow README's Local Profile table carries every
required row before the first-officer skill dispatches a batch, and that every station
script the README names resolves to a real file next to this script -- regardless of
where the plugin is installed or what directory this check is run from.

usage: local-profile-check.py <readme.md>
exit 0: every required row present and every named script resolves; each resolved script
path is printed to stdout alongside LOCAL_PROFILE_OK.
exit 1: at least one required row is missing, or at least one named script does not
resolve; stderr names each.
exit 2: usage error, unreadable file, or a Local Profile block that is missing, duplicated, or
out of order (a start/end marker must each occur exactly once, start before end).
"""
from __future__ import annotations

import re
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

# Matches the trailing filename of any "scripts/<name>" reference regardless of the
# prefix (repo-relative, an unexpanded `${CLAUDE_PLUGIN_ROOT}`, or bare `scripts/`).
SCRIPT_REF_PATTERN = re.compile(r"scripts/([A-Za-z0-9._-]+\.(?:sh|py))")


def resolve_scripts_root() -> Path:
    # This file's own parent is always the scripts root -- independent of cwd,
    # CLAUDE_PLUGIN_ROOT, or the checkout's directory name.
    return Path(__file__).resolve().parent


def extract_script_refs(text: str) -> list[str]:
    seen: dict[str, None] = {}
    for match in SCRIPT_REF_PATTERN.finditer(text):
        seen.setdefault(match.group(1), None)
    return list(seen)


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

    start_count = text.count(START_MARKER)
    end_count = text.count(END_MARKER)
    if start_count != 1 or end_count != 1:
        print(
            f"LOCAL_PROFILE_MARKER_COUNT: {readme_path} has {start_count} start marker(s) and "
            f"{end_count} end marker(s); exactly one of each is required",
            file=sys.stderr,
        )
        return 2

    start = text.find(START_MARKER)
    end = text.find(END_MARKER)
    if end < start:
        print(
            f"LOCAL_PROFILE_MARKER_ORDER: {readme_path} has the end marker before the start "
            "marker",
            file=sys.stderr,
        )
        return 2

    block = text[start + len(START_MARKER) : end]
    present = set(extract_row_labels(block))
    missing = [row for row in REQUIRED_ROWS if row not in present]
    if missing:
        print(f"LOCAL_PROFILE_MISSING_ROW: {', '.join(missing)}", file=sys.stderr)
        return 1

    scripts_root = resolve_scripts_root()
    script_refs = extract_script_refs(text)
    unresolved = [name for name in script_refs if not (scripts_root / name).is_file()]
    if unresolved:
        print(
            f"LOCAL_PROFILE_SCRIPT_MISSING: {', '.join(unresolved)} not found under "
            f"{scripts_root}",
            file=sys.stderr,
        )
        return 1

    print(f"LOCAL_PROFILE_OK: {len(REQUIRED_ROWS)} required rows present")
    for name in script_refs:
        print(f"LOCAL_PROFILE_SCRIPT_OK: {scripts_root / name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
