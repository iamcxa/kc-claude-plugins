#!/usr/bin/env python3
"""Public CLI contract for the read-only engage comparator."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
COMPARATOR = HERE / "engage-reconcile.py"
DEFAULT_WINDOW = "2026-W35"
DEFAULT_OUTCOME = "provider-neutral execution"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"engage reconcile test: {message}")


def item(source: str) -> dict[str, object]:
    return {
        "source": source,
        "planning-window": DEFAULT_WINDOW,
        "planning-outcome": DEFAULT_OUTCOME,
        "accepted-goal": "Dispatch only the admitted Ready set",
        "non-goals": ["provider write-back", "polling"],
    }


def invoke(
    snapshot: Path,
    current: Path,
    expected_source: str,
    expected_window: str = DEFAULT_WINDOW,
    expected_outcome: str = DEFAULT_OUTCOME,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(COMPARATOR),
            "--snapshot",
            str(snapshot),
            "--current",
            str(current),
            "--expected-source",
            expected_source,
            "--expected-window",
            expected_window,
            "--expected-outcome",
            expected_outcome,
        ],
        text=True,
        capture_output=True,
    )


def run_text(
    snapshot: str,
    current: str,
    expected_source: str,
    expected_window: str = DEFAULT_WINDOW,
    expected_outcome: str = DEFAULT_OUTCOME,
) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory(prefix="kc-dev-flow-reconcile-") as temporary:
        root = Path(temporary)
        snapshot_path = root / "snapshot.json"
        current_path = root / "current.json"
        snapshot_path.write_text(snapshot, encoding="utf-8")
        current_path.write_text(current, encoding="utf-8")
        return invoke(
            snapshot_path,
            current_path,
            expected_source,
            expected_window,
            expected_outcome,
        )


def run(
    snapshot: list[dict[str, object]],
    current: list[dict[str, object]],
    expected_source: str | None = None,
    expected_window: str = DEFAULT_WINDOW,
    expected_outcome: str = DEFAULT_OUTCOME,
) -> subprocess.CompletedProcess[str]:
    if expected_source is None:
        expected_source = str(snapshot[0]["source"]) if snapshot else "issue:missing"
    return run_text(
        json.dumps(snapshot),
        json.dumps(current),
        expected_source,
        expected_window,
        expected_outcome,
    )


def run_alias(document: str, expected_source: str) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory(prefix="kc-dev-flow-reconcile-") as temporary:
        path = Path(temporary) / "both.json"
        path.write_text(document, encoding="utf-8")
        return invoke(path, path, expected_source)


def expect_json(
    label: str,
    completed: subprocess.CompletedProcess[str],
    returncode: int,
    expected: dict[str, object],
) -> None:
    require(
        completed.returncode == returncode,
        f"{label} returned {completed.returncode}: {completed.stderr}",
    )
    require(
        json.loads(completed.stdout) == expected,
        f"{label} returned unexpected JSON: {completed.stdout!r}",
    )


def expect_error(
    label: str, completed: subprocess.CompletedProcess[str], fragment: str
) -> None:
    require(
        completed.returncode == 2 and completed.stdout == "",
        f"{label} was not rejected: {completed.stdout!r} {completed.stderr!r}",
    )
    require(fragment in completed.stderr, f"{label} diagnostic: {completed.stderr!r}")


expect_json(
    "equal sets",
    run([item("issue:1")], [item("issue:1")]),
    0,
    {
        "added": [],
        "changed": [],
        "moved": [],
        "removed": [],
        "status": "clean",
    },
)
expect_error(
    "empty snapshot",
    run([], []),
    "snapshot must contain the engaged source",
)
expect_error(
    "partial snapshot",
    run([item("issue:1")], [item("issue:1")], expected_source="issue:missing"),
    "snapshot does not contain expected source: issue:missing",
)
expect_error(
    "aliased inputs",
    run_alias(json.dumps([item("issue:1")]), "issue:1"),
    "snapshot and current must be different files",
)
expect_error(
    "placeholder source",
    run([item("<issue>")], [item("<issue>")]),
    "snapshot item 0 has invalid source",
)
for sentinel_field in ("source", "planning-window", "planning-outcome", "accepted-goal"):
    sentinel_item = item("issue:sentinel")
    sentinel_item[sentinel_field] = "TBD"
    expect_error(
        f"sentinel {sentinel_field}",
        run([sentinel_item], [sentinel_item]),
        f"snapshot item 0 has invalid {sentinel_field}",
    )
sentinel_non_goal = item("issue:sentinel-non-goal")
sentinel_non_goal["non-goals"] = ["TBD"]
expect_error(
    "sentinel non-goal",
    run([sentinel_non_goal], [sentinel_non_goal]),
    "snapshot item 0 has invalid non-goals",
)

punctuated_item = item("issue:punctuation")
punctuated_item["planning-outcome"] = "[MVP] provider-neutral execution"
punctuated_item["accepted-goal"] = ">99% successful dispatch"
punctuated_item["non-goals"] = ["*No* provider writes"]
require(
    run(
        [punctuated_item],
        [punctuated_item],
        expected_outcome="[MVP] provider-neutral execution",
    ).returncode
    == 0,
    "valid leading punctuation was rejected",
)

wrong_scope = item("issue:wrong-scope")
wrong_scope["planning-window"] = "2026-W36"
expect_error(
    "engaged source scope mismatch",
    run([wrong_scope], [wrong_scope]),
    "snapshot engaged source does not match expected planning scope",
)
mixed_scope = item("issue:mixed-scope")
mixed_scope["planning-outcome"] = "different outcome"
expect_error(
    "mixed snapshot scope",
    run(
        [item("issue:scope-anchor"), mixed_scope],
        [item("issue:scope-anchor"), mixed_scope],
    ),
    "snapshot source is outside expected planning scope: issue:mixed-scope",
)
expect_error(
    "malformed JSON",
    run_text("[", json.dumps([item("issue:1")]), "issue:1"),
    "cannot read snapshot",
)
with tempfile.TemporaryDirectory(prefix="kc-dev-flow-reconcile-") as temporary:
    root = Path(temporary)
    current_path = root / "current.json"
    current_path.write_text(json.dumps([item("issue:1")]), encoding="utf-8")
    expect_error(
        "missing snapshot path",
        invoke(root / "missing.json", current_path, "issue:1"),
        "cannot read snapshot",
    )

with tempfile.TemporaryDirectory(prefix="kc-dev-flow-reconcile-") as temporary:
    root = Path(temporary)
    snapshot_path = root / "snapshot.json"
    current_path = root / "current.json"
    snapshot_bytes = json.dumps([item("issue:read-only")]).encode()
    current_bytes = bytes(snapshot_bytes)
    snapshot_path.write_bytes(snapshot_bytes)
    current_path.write_bytes(current_bytes)
    completed = invoke(snapshot_path, current_path, "issue:read-only")
    require(completed.returncode == 0, "read-only probe did not compare cleanly")
    require(snapshot_path.read_bytes() == snapshot_bytes, "snapshot input was modified")
    require(current_path.read_bytes() == current_bytes, "current input was modified")

expect_json(
    "membership delta",
    run([item("issue:1")], [item("issue:2")]),
    1,
    {
        "added": ["issue:2"],
        "changed": [],
        "moved": [],
        "removed": ["issue:1"],
        "status": "delta",
    },
)
expect_json(
    "empty current set",
    run([item("issue:10")], []),
    1,
    {
        "added": [],
        "changed": [],
        "moved": [],
        "removed": ["issue:10"],
        "status": "delta",
    },
)

snapshot_item = item("issue:3")
current_item = item("issue:3")
current_item["planning-window"] = "2026-W36"
current_item["accepted-goal"] = "Dispatch the newly accepted Ready set"
expect_json(
    "moved and changed item",
    run([snapshot_item], [current_item]),
    1,
    {
        "added": [],
        "changed": ["issue:3"],
        "moved": ["issue:3"],
        "removed": [],
        "status": "delta",
    },
)

outcome_snapshot = item("issue:31")
outcome_current = item("issue:31")
outcome_current["planning-outcome"] = "revised provider-neutral execution"
expect_json(
    "planning outcome move",
    run([outcome_snapshot], [outcome_current]),
    1,
    {
        "added": [],
        "changed": [],
        "moved": ["issue:31"],
        "removed": [],
        "status": "delta",
    },
)

non_goals_snapshot = item("issue:32")
non_goals_current = item("issue:32")
non_goals_current["non-goals"] = ["polling"]
expect_json(
    "non-goal change",
    run([non_goals_snapshot], [non_goals_current]),
    1,
    {
        "added": [],
        "changed": ["issue:32"],
        "moved": [],
        "removed": [],
        "status": "delta",
    },
)

invalid_item = item("issue:4")
del invalid_item["accepted-goal"]
expect_error(
    "missing field",
    run([item("issue:4")], [invalid_item]),
    "current item 0 is missing required field: accepted-goal",
)

expect_error(
    "duplicate source",
    run([item("issue:5"), item("issue:5")], [item("issue:5")]),
    "snapshot contains duplicate source: issue:5",
)

reordered_snapshot = item("issue:6")
reordered_current = item("issue:6")
reordered_current["non-goals"] = ["polling", "provider write-back"]
require(
    run([reordered_snapshot], [reordered_current]).returncode == 0,
    "non-goal ordering created a false delta",
)

wrong_type = item("issue:7")
wrong_type["non-goals"] = "polling"
expect_error(
    "wrong field type",
    run([item("issue:7")], [wrong_type]),
    "current item 0 has invalid non-goals",
)

duplicate_key_snapshot = json.dumps([item("issue:8")]).replace(
    '"source": "issue:8"',
    '"source": "issue:8", "source": "issue:9"',
)
expect_error(
    "duplicate JSON key",
    run_text(duplicate_key_snapshot, json.dumps([item("issue:9")]), "issue:9"),
    "duplicate field: source",
)

print("engage reconcile test: PASS")
