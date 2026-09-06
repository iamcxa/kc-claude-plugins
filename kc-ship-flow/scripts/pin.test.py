#!/usr/bin/env python3
"""Standalone runnable check for pin.py's write/check contract. Run directly, no pytest."""

from __future__ import annotations

import importlib.util
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


def make_digest_sandbox() -> Path:
    sandbox = Path(tempfile.mkdtemp()) / "kc-ship-flow"
    (sandbox / "scripts").mkdir(parents=True)
    (sandbox / "schemas").mkdir(parents=True)
    (sandbox / ".claude-plugin").mkdir(parents=True)
    shutil.copy(PACKAGE_ROOT / "scripts" / "pin.py", sandbox / "scripts" / "pin.py")
    (sandbox / "schemas" / "resources.json").write_text(
        json.dumps({"schema": "kc-ship-flow-resources/v1", "resources": ["a", "b"]}),
        encoding="utf-8",
    )
    (sandbox / ".claude-plugin" / "plugin.json").write_text(
        json.dumps({"version": "0.1.0"}), encoding="utf-8"
    )
    return sandbox


def load_pin_module(sandbox: Path):
    spec = importlib.util.spec_from_file_location("pin_under_test", sandbox / "scripts" / "pin.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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


def assert_refused_without_rewrite(
    sandbox: Path, pin_path: Path, args: list[str], reason: str, case: str,
) -> None:
    before = pin_path.read_bytes()
    result = run_pin(sandbox, args)
    check(result.returncode != 0, f"{case}: command accepted the invalid pin")
    check(reason in result.stderr, f"{case}: expected {reason}, got {result.stderr!r}")
    check(pin_path.read_bytes() == before, f"{case}: command rewrote the refused pin")


def test_same_station_replay_preserves_record(sandbox: Path, pin_path: Path) -> None:
    record = json.loads(pin_path.read_bytes())
    record["written_at"] = "2026-01-01T00:00:00Z"
    pin_path.write_text(json.dumps(record, indent=4) + "\n", encoding="utf-8")
    before = pin_path.read_bytes()
    result = run_pin(sandbox, ["write", "--batch", "b1", "--station", "accepted", "--pin", str(pin_path)])
    check(result.returncode == 0, f"unchanged replay was refused: {result.stderr}")
    if result.returncode == 0:
        check(json.loads(result.stdout) == record, "unchanged replay replaced the existing record")
    check(pin_path.read_bytes() == before, "unchanged replay rewrote the existing pin bytes")


def test_record_mutations_are_refused(sandbox: Path, pin_path: Path) -> None:
    original = pin_path.read_bytes()
    for field, value, reason in [
        ("plugin_version", "999.999.999", "PLUGIN_VERSION_MISMATCH"),
        ("plugin_version", None, "PLUGIN_VERSION_MISMATCH"),
        ("contract_digest", "0" * 64, "CONTRACT_DIGEST_MISMATCH"),
        ("previous_station", "uat", "PREVIOUS_STATION_MISMATCH"),
    ]:
        record = json.loads(original)
        if value is None:
            del record[field]
        else:
            record[field] = value
        for command in ["check", "write"]:
            pin_path.write_text(json.dumps(record) + "\n", encoding="utf-8")
            args = [command, "--station", "accepted", "--pin", str(pin_path)]
            if command == "write":
                args += ["--batch", "b1"]
            assert_refused_without_rewrite(
                sandbox, pin_path, args, reason, f"{command} with {field}={value!r}",
            )
    pin_path.write_bytes(original)


def test_mutated_resource_byte_is_refused(sandbox: Path, pin_path: Path) -> None:
    kernel = sandbox / "references" / "kernel.md"
    original = kernel.read_bytes()
    original_pin = pin_path.read_bytes()
    kernel.write_bytes(original + b"x")
    try:
        result = run_pin(sandbox, ["check", "--pin", str(pin_path), "--station", "accepted"])
        check(result.returncode != 0, "check accepted a mutated declared resource byte (AC-2 mutation 1)")
        check(
            "references/kernel.md" in result.stderr,
            f"check did not name the mutated resource: {result.stderr!r}",
        )
        assert_refused_without_rewrite(
            sandbox, pin_path,
            ["write", "--batch", "b1", "--station", "accepted", "--pin", str(pin_path)],
            "CONTRACT_DIGEST_MISMATCH: changed resource: references/kernel.md",
            "same-station replay after resource drift",
        )
        result = run_pin(sandbox, ["check", "--pin", str(pin_path), "--station", "accepted"])
        check(result.returncode != 0, "same-station replay made a drifted contract pass check")
    finally:
        kernel.write_bytes(original)
        pin_path.write_bytes(original_pin)


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


def test_digest_is_length_prefixed_not_delimiter_joined() -> None:
    # Content for "a" below is byte-identical to the delimiter-joined
    # concatenation of resource "b" in the second pair, so an unprefixed join
    # of these two pairs collides; a length-prefixed join must not.
    sandbox = make_digest_sandbox()
    module = load_pin_module(sandbox)

    (sandbox / "a").write_bytes(b"resource\x00b\x00PREFIX")
    (sandbox / "b").write_bytes(b"SUFFIX")
    digest_1, _ = module.compute_contract_digest(["a", "b"])

    (sandbox / "a").write_bytes(b"")
    (sandbox / "b").write_bytes(b"PREFIXresource\x00b\x00SUFFIX")
    digest_2, _ = module.compute_contract_digest(["a", "b"])

    check(
        digest_1 != digest_2,
        "contract digest collided across two different resource content pairs "
        "(delimiter-joined digest, not length-prefixed)",
    )


def test_write_refuses_a_station_regression() -> None:
    sandbox = make_sandbox()
    pin_path = sandbox / "regression.pin.json"

    result = run_pin(sandbox, ["write", "--batch", "b2", "--station", "merged", "--pin", str(pin_path)])
    check(result.returncode == 0, f"seeding a merged pin failed: {result.stderr}")

    result = run_pin(sandbox, ["write", "--batch", "b2", "--station", "accepted", "--pin", str(pin_path)])
    check(result.returncode != 0, "write let an existing merged pin rewind to accepted")
    check(
        "PIN_REGRESSION_REFUSED" in result.stderr and "merged" in result.stderr,
        f"write did not name the regression: {result.stderr!r}",
    )

    result = run_pin(sandbox, ["write", "--batch", "b2", "--station", "merged", "--pin", str(pin_path)])
    check(result.returncode == 0, f"re-writing the same station was refused: {result.stderr}")


def test_write_preserves_batch_and_station_guards() -> None:
    sandbox = make_sandbox()
    pin_path = sandbox / "guards.pin.json"
    test_write_produces_valid_record(sandbox, pin_path)
    original = pin_path.read_bytes()
    for updates, batch, reason in [
        ({}, "other-batch", "PIN_BATCH_MISMATCH"),
        ({"station": "unknown"}, "b1", "PIN_UNREADABLE"),
        ({"schema": "unknown"}, "b1", "PIN_UNREADABLE"),
        ({"station": "merged"}, "b1", "PIN_REGRESSION_REFUSED"),
    ]:
        record = json.loads(original)
        record.update(updates)
        pin_path.write_text(json.dumps(record), encoding="utf-8")
        assert_refused_without_rewrite(
            sandbox, pin_path,
            ["write", "--batch", batch, "--station", "accepted", "--pin", str(pin_path)],
            reason, f"write guard {reason}",
        )
    pin_path.write_bytes(original)
    assert_refused_without_rewrite(
        sandbox, pin_path, ["check", "--pin", str(pin_path), "--station", "reviewed"],
        "STATION_MISMATCH", "check with another station",
    )


def test_forward_write_remains_compatible() -> None:
    sandbox = make_sandbox()
    pin_path = sandbox / "forward.pin.json"
    test_write_produces_valid_record(sandbox, pin_path)
    result = run_pin(sandbox, ["write", "--batch", "b1", "--station", "reviewed", "--pin", str(pin_path)])
    check(result.returncode == 0, f"unchanged forward write was refused: {result.stderr}")
    result = run_pin(sandbox, ["check", "--pin", str(pin_path), "--station", "reviewed"])
    check(result.returncode == 0, f"unchanged forward pin failed check: {result.stderr}")
    record = json.loads(pin_path.read_bytes())
    check(record.get("previous_station") == "accepted", "forward write recorded the wrong predecessor")

    kernel = sandbox / "references" / "kernel.md"
    kernel.write_bytes(kernel.read_bytes() + b"x")
    manifest_path = sandbox / ".claude-plugin" / "plugin.json"
    manifest = json.loads(manifest_path.read_bytes())
    manifest["version"] = "0.2.0"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    result = run_pin(sandbox, ["write", "--batch", "b1", "--station", "uat", "--pin", str(pin_path)])
    check(result.returncode == 0, f"forward write refused an updated contract: {result.stderr}")
    updated = json.loads(pin_path.read_bytes())
    check(updated.get("contract_digest") != record.get("contract_digest"), "forward write kept the old digest")
    check(updated.get("plugin_version") == "0.2.0", "forward write kept the old plugin version")
    result = run_pin(sandbox, ["check", "--pin", str(pin_path), "--station", "uat"])
    check(result.returncode == 0, f"updated forward pin failed check: {result.stderr}")


def main() -> int:
    sandbox = make_sandbox()
    pin_path = sandbox / "batch.pin.json"
    test_write_produces_valid_record(sandbox, pin_path)
    test_check_passes_on_unmodified_sandbox(sandbox, pin_path)
    test_same_station_replay_preserves_record(sandbox, pin_path)
    test_record_mutations_are_refused(sandbox, pin_path)
    test_mutated_resource_byte_is_refused(sandbox, pin_path)
    test_wrong_previous_station_is_refused(sandbox, pin_path)
    test_digest_is_length_prefixed_not_delimiter_joined()
    test_write_refuses_a_station_regression()
    test_write_preserves_batch_and_station_guards()
    test_forward_write_remains_compatible()
    if FAILURES:
        for failure in FAILURES:
            print(f"FAIL: {failure}", file=sys.stderr)
        print(f"{len(FAILURES)} failing", file=sys.stderr)
        return 1
    print("pin.test.py: all checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
