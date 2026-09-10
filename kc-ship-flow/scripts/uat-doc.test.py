#!/usr/bin/env python3
"""Behavior contract for kc-ship-flow/scripts/uat-doc.py (cloud-wrapper redesign, v2 -- reads
`docs/dev` entities + the batch record directly, not a plan-flow batch dir).

Pins the entity's own AC-1:
`python3 kc-ship-flow/scripts/uat-doc.py ship-cloud-wrapper --state-dir <fixture>` exits 0
writing the document with every task of the fixture sprint, and exits 1 printing the slug when a
task lacks a prepared `validation` gate.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "uat-doc.py"
FIXTURES = HERE / "fixtures" / "uat-doc-v2"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"uat-doc test: {message}")


def run(state_dir: Path, sprint: str = "ship-cloud-wrapper"):
    return subprocess.run(
        [sys.executable, str(SCRIPT), sprint, "--state-dir", str(state_dir)],
        capture_output=True, text=True,
    )


# --- AC-1, happy path: every task has a prepared validation gate -----------
ready = run(FIXTURES / "ready")
require(ready.returncode == 0, f"ready fixture did not exit 0: {ready.returncode} stderr={ready.stderr!r}")
require("# UAT: ship-cloud-wrapper" in ready.stdout, "document missing its title heading")
require("## DEV-201" in ready.stdout and "## DEV-202" in ready.stdout, "document missing a task heading")
require(
    "https://github.com/acme/repo/pull/42" in ready.stdout,
    f"document did not render DEV-202's owner/repo#N PR as a link: {ready.stdout!r}",
)
require(
    "Does this task's Local Profile row cover the delivery branch base?" in ready.stdout
    and "Yes, see the Local Profile's delivery-branch-base policy row." in ready.stdout,
    "document dropped the batch record's recorded question/answer pair",
)
require("[trunk]" in ready.stdout, "document did not read the Integrated head Local Profile row")

# --- AC-1, negative path: a task's validation gate is resolved, not prepared -----
missing_gate = run(FIXTURES / "missing-gate")
require(
    missing_gate.returncode == 1,
    f"missing-gate fixture did not exit 1: {missing_gate.returncode} stdout={missing_gate.stdout!r}",
)
require(
    missing_gate.stdout.strip() == "DEV-203",
    f"missing-gate fixture did not print exactly the unprepared slug: {missing_gate.stdout!r}",
)

# --- usage: no task found for the sprint under an empty state-dir exits 2 --
import tempfile  # noqa: E402

with tempfile.TemporaryDirectory() as empty_dir:
    empty = run(Path(empty_dir), sprint="nothing-here")
    require(
        empty.returncode == 2,
        f"empty state-dir with no matching entity did not exit 2: {empty.returncode}",
    )

# --- module-level unit checks on the frontmatter parser (fast, no subprocess) ---
import importlib.util  # noqa: E402

spec = importlib.util.spec_from_file_location("uat_doc", SCRIPT)
uat_doc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(uat_doc)

resolved_text = (FIXTURES / "missing-gate" / "DEV-203.md").read_text(encoding="utf-8")
fm = uat_doc.read_frontmatter_text(resolved_text)
require(
    uat_doc.validation_gate_status(fm) == "resolved",
    "DEV-203's validation gate did not parse as 'resolved' -- the frontmatter fixture text or the "
    "attempt-block parser drifted",
)

prepared_text = (FIXTURES / "ready" / "DEV-201.md").read_text(encoding="utf-8")
fm2 = uat_doc.read_frontmatter_text(prepared_text)
require(
    uat_doc.validation_gate_status(fm2) == "prepared",
    "DEV-201's validation gate did not parse as 'prepared'",
)

require(
    uat_doc.render_pr("pr-merge:99", None) == "PR #99 (merged via pr-merge)",
    "render_pr did not fall back to a plain label for pr-merge:N with no repo hint",
)
require(
    uat_doc.render_pr(None, None) == "not recorded",
    "render_pr did not report an absent PR as 'not recorded'",
)

print("uat-doc test: all checks passed")
