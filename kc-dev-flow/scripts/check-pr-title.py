#!/usr/bin/env python3
"""Refuse a pull request title release-please's conventional-commits grammar
cannot parse.

Exit 0: the title parses; its commit type is written to stdout.
Exit 1: the title does not parse under the grammar below -- refuse.
Exit 2: the checker could not decide (unreadable fixture or bad usage) --
    every caller treats this the same as exit 1.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# <type> ["(" <scope> ")"] ["!"] ":" <text>* -- release-please's own
# @conventional-commits/parser walks this grammar (see
# node_modules/release-please/build/src/commit.js after `npm ci` in
# scripts/fixtures/release-please-runtime/, function
# toConventionalChangelogFormat). A present-but-empty scope, e.g.
# "feat(): x", must refuse: it is the row a naive `(\w+)(\(.*\))?!?:` regex
# would wrongly pass.
_TITLE = re.compile(
    r"^\s*(?P<type>[^\s()!:]+)(?:\((?P<scope>[^)]*)\))?(?P<breaking>!)?:(?P<rest>.*)$"
)

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "pr-title" / "release-please-verdicts.tsv"


def classify(title: str) -> str | None:
    """Return the parsed commit type, or None when the title does not parse."""
    match = _TITLE.match(title)
    if match is None:
        return None
    scope = match.group("scope")
    if scope is not None and scope == "":
        return None
    return match.group("type")


def load_fixture(path: Path) -> list[tuple[str, bool]]:
    text = path.read_text(encoding="utf-8")
    rows: list[tuple[str, bool]] = []
    for line in text.split("\n"):
        line = line.rstrip("\r")
        if not line or line.startswith("#"):
            continue
        fields = line.split("\t")
        if len(fields) != 3:
            raise ValueError(f"malformed fixture row: {line!r}")
        subject, verdict, _reason = fields
        if verdict not in ("parses", "drops"):
            raise ValueError(f"unknown verdict {verdict!r} in fixture row: {line!r}")
        rows.append((subject, verdict == "parses"))
    if not rows:
        raise ValueError("fixture has no data rows")
    return rows


def self_test(path: Path) -> str | None:
    """Return an error message, or None when classify() agrees with every
    fixture row. Runs before the real title so a passing decision on an
    unrelated title can never hide a broken grammar."""
    try:
        rows = load_fixture(path)
    except (OSError, ValueError) as error:
        return f"fixture unreadable or malformed at {path}: {error}"
    for subject, expect_parses in rows:
        actual_parses = classify(subject) is not None
        if actual_parses != expect_parses:
            expected = "parses" if expect_parses else "drops"
            actual = "parses" if actual_parses else "drops"
            return f"self-test disagreement on {subject!r}: fixture says {expected}, checker says {actual}"
    return None


def main(argv: list[str]) -> int:
    error = self_test(FIXTURE)
    if error is not None:
        print(f"check-pr-title: {error}", file=sys.stderr)
        return 2
    if len(argv) != 2:
        print("usage: check-pr-title.py <title>", file=sys.stderr)
        return 2
    title = argv[1]
    commit_type = classify(title)
    if commit_type is None:
        print(
            f"check-pr-title: {title!r} is not a Conventional Commits subject "
            "release-please can parse",
            file=sys.stderr,
        )
        return 1
    print(commit_type)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
