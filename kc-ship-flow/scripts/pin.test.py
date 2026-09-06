#!/usr/bin/env python3
"""Standalone runnable check for pin.py's write/check contract. Run directly, no pytest."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
FAILURES: list[str] = []


def check(condition: bool, message: str) -> None:
    if not condition:
        FAILURES.append(message)


def run_pin(sandbox: Path, args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(sandbox / "scripts" / "pin.py"), *args],
        cwd=sandbox,
        capture_output=True,
        text=True,
    )


def make_sandbox() -> Path:
    sandbox = Path(tempfile.mkdtemp()) / "kc-ship-flow"
    (sandbox / "scripts").mkdir(parents=True)
    (sandbox / "schemas").mkdir(parents=True)
    (sandbox / "references").mkdir(parents=True)
    (sandbox / ".claude-plugin").mkdir(parents=True)
    shutil.copy(PACKAGE_ROOT / "scripts" / "pin.py", sandbox / "scripts" / "pin.py")
    shutil.copy(PACKAGE_ROOT / "schemas" / "resources.json", sandbox / "schemas" / "resources.json")
    shutil.copy(PACKAGE_ROOT / "references" / "kernel.md", sandbox / "references" / "kernel.md")
    shutil.copy(
        PACKAGE_ROOT / ".claude-plugin" / "plugin.json",
        sandbox / ".claude-plugin" / "plugin.json",
    )
    return sandbox


def test_write_produces_valid_record(sandbox: Path, pin_path: Path) -> None:
    result = run_pin(sandbox, ["write", "--batch", "b1", "--station", "accepted", "--pin", str(pin_path)])
    check(result.returncode == 0, f"write exited {result.returncode}: {result.stderr}")
    record = json.loads(result.stdout)
    check(record.get("schema") == "kc-ship-flow-batch-pin/v1", "write printed the wrong schema")
    digest = record.get("contract_digest", "")
    check(
        len(digest) == 64 and all(c in "0123456789abcdef" for c in digest),
        "contract_digest is not 64 lowercase hex characters",
    )
    check(record.get("previous_station") == "dispatched", "accepted's previous_station should be dispatched")
    check(pin_path.is_file(), "write --pin did not persist the record to disk")


def test_check_passes_on_unmodified_sandbox(sandbox: Path, pin_path: Path) -> None:
    result = run_pin(sandbox, ["check", "--pin", str(pin_path), "--station", "accepted"])
    check(result.returncode == 0, f"check refused an unmodified sandbox: {result.stderr}")


def test_mutated_resource_byte_is_refused(sandbox: Path, pin_path: Path) -> None:
    kernel = sandbox / "references" / "kernel.md"
    original = kernel.read_bytes()
    kernel.write_bytes(original + b"x")
    try:
        result = run_pin(sandbox, ["check", "--pin", str(pin_path), "--station", "accepted"])
        check(result.returncode != 0, "check accepted a mutated declared resource byte (AC-2 mutation 1)")
        check(
            "references/kernel.md" in result.stderr,
            f"check did not name the mutated resource: {result.stderr!r}",
        )
    finally:
        kernel.write_bytes(original)


def test_wrong_previous_station_is_refused(sandbox: Path, pin_path: Path) -> None:
    record = json.loads(pin_path.read_text(encoding="utf-8"))
    record["previous_station"] = "uat"
    pin_path.write_text(json.dumps(record), encoding="utf-8")
    result = run_pin(sandbox, ["check", "--pin", str(pin_path), "--station", "accepted"])
    check(result.returncode != 0, "check accepted a wrong previous_station (AC-2 mutation 2)")
    check(
        "dispatched" in result.stderr,
        f"check did not name the expected previous station: {result.stderr!r}",
    )


def main() -> int:
    sandbox = make_sandbox()
    pin_path = sandbox / "batch.pin.json"
    test_write_produces_valid_record(sandbox, pin_path)
    test_check_passes_on_unmodified_sandbox(sandbox, pin_path)
    test_mutated_resource_byte_is_refused(sandbox, pin_path)
    test_wrong_previous_station_is_refused(sandbox, pin_path)
    if FAILURES:
        for failure in FAILURES:
            print(f"FAIL: {failure}", file=sys.stderr)
        print(f"{len(FAILURES)} failing", file=sys.stderr)
        return 1
    print("pin.test.py: all checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
