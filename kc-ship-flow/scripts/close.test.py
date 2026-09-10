#!/usr/bin/env python3
"""Behavior contract for kc-ship-flow/scripts/close.py.

Pins the entity's own AC-2 and AC-3:

AC-2: `python3 kc-ship-flow/scripts/close.py ship-cloud-wrapper --dry-run --state-dir <fixture>`
prints one `conductor message create --session <id>` argv per merged task and none for an
unmerged one, and exits 3 printing `not all tasks merged` when asked to write the receipt with an
unmerged task present.

AC-3: `python3 kc-ship-flow/scripts/close.py --validate <receipt.json>` exits 0 on the fixture
receipt and exits 1 on a copy missing any task's `debrief` field.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "close.py"
FIXTURES = HERE / "fixtures" / "close-v2"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"close test: {message}")


def run(argv):
    return subprocess.run([sys.executable, str(SCRIPT), *argv], capture_output=True, text=True)


# --- AC-2, dry-run: one message per merged task, none for the unmerged one ---
dry_run_dir = FIXTURES / "dry-run"
dry_run = run(["ship-cloud-wrapper", "--dry-run", "--state-dir", str(dry_run_dir)])
require(dry_run.returncode == 0, f"--dry-run did not exit 0: {dry_run.returncode} stderr={dry_run.stderr!r}")
lines = [l for l in dry_run.stdout.splitlines() if l.strip()]
require(len(lines) == 1, f"--dry-run printed {len(lines)} message argv lines, expected exactly 1: {lines!r}")
require(
    lines[0].startswith("conductor message create --session sess-301"),
    f"--dry-run's message argv did not target the merged task's session: {lines[0]!r}",
)
require("sess-302" not in dry_run.stdout, "--dry-run messaged the unmerged task DEV-302")

# --- AC-2, non-dry-run with an unmerged task present: exit 3 ----------------
live = run(["ship-cloud-wrapper", "--state-dir", str(dry_run_dir)])
require(
    live.returncode == 3 and "not all tasks merged" in live.stdout + live.stderr,
    f"non-dry-run with an unmerged task did not exit 3 printing 'not all tasks merged': "
    f"exit={live.returncode} stdout={live.stdout!r} stderr={live.stderr!r}",
)

# --- closing all-merged, all-debriefed fixture writes the receipt ----------
with tempfile.TemporaryDirectory() as scratch_name:
    scratch = Path(scratch_name)
    for name in ("DEV-301.md",):
        (scratch / name).write_text((FIXTURES / "closeable" / name).read_text(encoding="utf-8"), encoding="utf-8")
    fence_dir = scratch / "_ship_fence"
    fence_dir.mkdir()
    (fence_dir / "ship-cloud-wrapper.json").write_text(
        (FIXTURES / "closeable" / "_ship_fence" / "ship-cloud-wrapper.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    closeable = run(["ship-cloud-wrapper", "--state-dir", str(scratch)])
    require(
        closeable.returncode == 0,
        f"closeable fixture did not exit 0: {closeable.returncode} stdout={closeable.stdout!r} stderr={closeable.stderr!r}",
    )
    receipt_path = fence_dir / "close-receipt-ship-cloud-wrapper.json"
    require(receipt_path.is_file(), f"closeable run did not write a receipt at {receipt_path}")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    require(receipt["schema"] == "kc-ship-close-receipt/v2", "written receipt has the wrong schema id")
    require(
        receipt["tasks"]["DEV-301"]["debrief"] == "_debriefs/2026-09-10-01-claude-fable-5-1.md",
        "written receipt did not carry the pushed debrief's path",
    )

# --- AC-3: --validate on the fixture receipt vs. a copy missing `debrief` --
valid = run(["--validate", str(FIXTURES / "receipts" / "valid.json")])
require(valid.returncode == 0, f"--validate did not accept the valid fixture receipt: {valid.returncode} stderr={valid.stderr!r}")

missing = run(["--validate", str(FIXTURES / "receipts" / "missing-debrief.json")])
require(
    missing.returncode == 1 and "DEV-301" in missing.stderr,
    f"--validate did not refuse a receipt missing a task's debrief field, naming it: "
    f"exit={missing.returncode} stderr={missing.stderr!r}",
)

# --- close.py's own readers against a fence file dispatch.sh/watch.sh actually produce ---
# Same reconciliation as uat-doc.test.py: `debrief_status`/`build_receipt` must read the
# top-level `<slug> -> {workspace, session, message_sha256}` shape dispatch.sh actually commits
# (pinned in the sibling dispatch/watch task's own fixture,
# fixtures/watch/state/_ship_fence/ship-cloud-wrapper.json -- verified against dispatch.sh's real
# writes in dispatch.test.sh cases (b)/(e)), with close.py's own `merged_sha`/`debrief` additions
# layered on top of one slug's object, not nested under a "tasks" key.
import importlib.util as _importlib_util  # noqa: E402

close_spec = _importlib_util.spec_from_file_location("close_module", SCRIPT)
close_module = _importlib_util.module_from_spec(close_spec)
close_spec.loader.exec_module(close_module)

dispatch_fence = json.loads(
    (HERE / "fixtures" / "watch" / "state" / "_ship_fence" / "ship-cloud-wrapper.json").read_text(encoding="utf-8")
)
dispatch_fence["task-gate-prepared"]["merged_sha"] = "deadbeef"
dispatch_fence["task-gate-prepared"]["debrief"] = {"status": "pushed", "path": "_debriefs/x.md"}
require(
    close_module.debrief_status(dispatch_fence, "task-gate-prepared") == {"status": "pushed", "path": "_debriefs/x.md"},
    "debrief_status misread a debrief nested in dispatch.sh's real top-level slug shape",
)
receipt = close_module.build_receipt(
    "ship-cloud-wrapper",
    {"task-gate-prepared": {"pr": "pr-merge:9"}},
    dispatch_fence,
)
require(
    receipt["tasks"]["task-gate-prepared"]["workspace_id"] == "ws-1"
    and receipt["tasks"]["task-gate-prepared"]["session_id"] == "sess-gate-prepared",
    f"build_receipt did not read workspace/session from dispatch.sh's real field names: {receipt!r}",
)

print("close test: all checks passed")
