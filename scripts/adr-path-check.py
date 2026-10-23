#!/usr/bin/env python3
"""Check the ADR paths that tracked AGENTS.md and CLAUDE.md files name.

Exit 0: every reference passes. Exit 1: findings, one per line as
`file:line: reference: reason`. Exit 2: not a git repository or git failed.

A `docs/adr` path must exist among the tracked files. A reference that names a
branch or other ref (`git show REF:docs/adr/...`) is refused: point at the file
on the trunk. No ref is fetched or resolved.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ADR_FILE = re.compile(r"docs/adr/\d{4}-[^/]+\.md")
REF_FORM = re.compile(r"(?<![\w./-])([^\s:`'\"()]+):(docs/adr[^\s`'\"()]*)")
PATH_FORM = re.compile(r"(?<![\w./:-])docs/adr((?:/[^\s`'\"()<>\[\],;|]*)?)")
PLACEHOLDER = re.compile(r"NNNN|[*?]")


def tracked_files(root: Path) -> list[str]:
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z"],
            check=True, capture_output=True, text=True,
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError, OSError) as exc:
        detail = getattr(exc, "stderr", "") or str(exc)
        sys.stderr.write(f"adr-path-check: cannot list tracked files in {root}: {detail.strip()}\n")
        raise SystemExit(2)
    return [name for name in out.split("\0") if name]


def check_line(line: str, tracked: set[str], has_adr_dir: bool) -> list[tuple[str, str]]:
    findings: list[tuple[str, str]] = []
    for match in REF_FORM.finditer(line):
        findings.append((
            match.group(0),
            f"names ref `{match.group(1)}`; point at the file on the trunk "
            f"(`{match.group(2)}`), not at a branch or ref",
        ))
    plain = REF_FORM.sub(" ", line)
    for match in PATH_FORM.finditer(plain):
        rest = match.group(1).rstrip(".:")
        nxt = plain[match.end():match.end() + 1]
        if PLACEHOLDER.search(rest) or nxt == "<":
            continue
        if rest in ("", "/"):
            if not has_adr_dir:
                findings.append(("docs/adr", "directory missing or holds no NNNN-*.md"))
        elif f"docs/adr{rest}" not in tracked:
            findings.append((f"docs/adr{rest}", "no such file in the tree"))
    return findings


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=".", help="repository root (default: current directory)")
    root = Path(parser.parse_args(argv).root)
    files = tracked_files(root)
    tracked = set(files)
    has_adr_dir = any(ADR_FILE.fullmatch(name) for name in files)
    failed = False
    for name in files:
        if Path(name).name not in ("AGENTS.md", "CLAUDE.md"):
            continue
        text = (root / name).read_text(encoding="utf-8", errors="replace")
        for number, line in enumerate(text.splitlines(), 1):
            for reference, reason in check_line(line, tracked, has_adr_dir):
                print(f"{name}:{number}: {reference}: {reason}")
                failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
