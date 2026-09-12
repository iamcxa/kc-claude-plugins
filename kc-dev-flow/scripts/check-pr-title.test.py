#!/usr/bin/env python3
"""Process-level contract test for check-pr-title.py. Drives the checker as a
subprocess over every fixture row and asserts the exit code, not an imported
predicate -- a fixture-only unit test would not catch a checker that reads
the wrong file or crashes before reaching classify()."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CHECKER = ROOT / "check-pr-title.py"
FIXTURE = ROOT / "fixtures" / "pr-title" / "release-please-verdicts.tsv"


def run_checker(*args: str, checker: Path = CHECKER) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(checker), *args],
        text=True,
        capture_output=True,
    )


def load_rows() -> list[tuple[str, bool]]:
    rows: list[tuple[str, bool]] = []
    for line in FIXTURE.read_text(encoding="utf-8").split("\n"):
        line = line.rstrip("\r")
        if not line or line.startswith("#"):
            continue
        subject, verdict, _reason = line.split("\t")
        rows.append((subject, verdict == "parses"))
    return rows


rows = load_rows()
if not rows:
    raise SystemExit("check-pr-title:FAIL fixture has no data rows to drive")

failures: list[str] = []

for subject, expect_parses in rows:
    result = run_checker(subject)
    expected_exit = 0 if expect_parses else 1
    if result.returncode != expected_exit:
        failures.append(
            f"{subject!r}: expected exit {expected_exit}, got {result.returncode} "
            f"(stdout={result.stdout!r} stderr={result.stderr!r})"
        )
    elif expect_parses and not result.stdout.strip():
        failures.append(f"{subject!r}: exit 0 printed no type")

# Falsifier kind `refusal`: the checker must be watched exiting 1 on a
# non-conventional sentence before its silence on a good title counts as
# evidence.
refusal = run_checker("Release-please credentials and verified production promotion")
if refusal.returncode != 1:
    failures.append(f"refusal case: expected exit 1, got {refusal.returncode}")

# Falsifier kind `refusal`: exit 2 on an unreadable fixture, watched by
# copying only the checker (no fixtures/ sibling) into an isolated directory
# so its self-test's fixture read fails before any title is evaluated.
with tempfile.TemporaryDirectory() as tmp:
    isolated_checker = Path(tmp) / "check-pr-title.py"
    shutil.copy(CHECKER, isolated_checker)
    unreadable = run_checker("feat: x", checker=isolated_checker)
    if unreadable.returncode != 2:
        failures.append(f"unreadable fixture: expected exit 2, got {unreadable.returncode}")

missing_arg = run_checker()
if missing_arg.returncode != 2:
    failures.append(f"missing argument: expected exit 2, got {missing_arg.returncode}")

if failures:
    raise SystemExit("check-pr-title:FAIL\n" + "\n".join(failures))
print(f"check-pr-title:PASS ({len(rows)} fixture rows + 3 boundary cases)")
