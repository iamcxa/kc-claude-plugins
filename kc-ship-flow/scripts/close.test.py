#!/usr/bin/env python3
"""Behavior contract for kc-ship-flow/scripts/close.py. Pins AC-1..AC-4:

AC-1: a fake `gh pr view N` stub gates `merged_sha` in the written receipt; refuses (non-zero,
slug + state named, no receipt) a task whose stub-reported state is not `MERGED`.
AC-2: `find_debrief_path` matches a `## Shipped`-section mention of the slug, never the ship FO's
own debrief (named only outside `## Shipped`). Also the original AC-2: dry-run prints one
`conductor message create` argv per merged task, exits 3 with an unmerged task present.
AC-3: `--validate <receipt.json>` exits 0/1 on `debrief` and on a null/non-40-hex `merged_sha`.
AC-4: every AC-1 case runs against a fake `gh` (never real, never a real repo SHA); removing it
from `PATH` flips an otherwise-closeable batch to a failure, proving the gh-call path is exercised.

close-roster-is-the-fence-and-captain-stopped-validates adds two more:
AC-1 (roster): the batch's task set is scoped to the fence's own roster -- a sprint-matching
entity absent from the fence and never merged (e.g. a deferred, never-dispatched sibling) is
dropped, named once on stderr as `not dispatched`, and closing the rest of the batch still
succeeds and writes a receipt that omits it.
AC-2 (captain_stopped validates): a `captain_stopped` task's receipt entry carries `merged_sha:
null` and `closed: "captain_stopped"`, and `--validate` accepts it; the pre-existing
bad-merged-sha fixture (a null/short `merged_sha` with no `closed` marker) still fails.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "close.py"
FIXTURES = HERE / "fixtures" / "close-v2"
FAKE_GH_DIR = FIXTURES / "fake-gh"
FAKE_GH_RESPONSES = FAKE_GH_DIR / "responses.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"close test: {message}")


def run(argv, gh_responses=None, path_override=None):
    """Run close.py with a fake `gh` on `PATH` by default so no case falls through to a real `gh`
    binary; `path_override` replaces `PATH` entirely (AC-4's stub-removed case)."""
    env = dict(os.environ)
    env["PATH"] = path_override if path_override is not None else f"{FAKE_GH_DIR}{os.pathsep}{env.get('PATH', '')}"
    env["FAKE_GH_RESPONSES"] = str(gh_responses or FAKE_GH_RESPONSES)
    return subprocess.run([sys.executable, str(SCRIPT), *argv], capture_output=True, text=True, env=env)


def write_closeable_scratch(scratch):
    """Copy the single-task `closeable` fixture (DEV-301, `pr-merge:501`) into `scratch`; returns
    the `_ship_fence` dir. Shared by the closeable-run and the AC-4 no-gh-on-PATH assertions."""
    (scratch / "DEV-301.md").write_text(
        (FIXTURES / "closeable" / "DEV-301.md").read_text(encoding="utf-8"), encoding="utf-8"
    )
    fence_dir = scratch / "_ship_fence"
    fence_dir.mkdir()
    (fence_dir / "ship-cloud-wrapper.json").write_text(
        (FIXTURES / "closeable" / "_ship_fence" / "ship-cloud-wrapper.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    return fence_dir


# close.py's own module, imported directly to call find_debrief_path/debrief_status/build_receipt.
import importlib.util as _importlib_util  # noqa: E402

close_spec = _importlib_util.spec_from_file_location("close_module", SCRIPT)
close_module = _importlib_util.module_from_spec(close_spec)
close_spec.loader.exec_module(close_module)


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

# --- AC-1 bullet 1: closing an all-merged fixture writes merged_sha from the fake gh stub's oid --
with tempfile.TemporaryDirectory() as scratch_name:
    scratch = Path(scratch_name)
    fence_dir = write_closeable_scratch(scratch)
    closeable = run(["ship-cloud-wrapper", "--state-dir", str(scratch)])
    require(closeable.returncode == 0, f"closeable fixture did not exit 0: {closeable.returncode} stderr={closeable.stderr!r}")
    receipt_path = fence_dir / "close-receipt-ship-cloud-wrapper.json"
    require(receipt_path.is_file(), f"closeable run did not write a receipt at {receipt_path}")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    require(receipt["schema"] == "kc-ship-close-receipt/v2", "written receipt has the wrong schema id")
    require(
        receipt["tasks"]["DEV-301"]["debrief"] == "_debriefs/2026-09-10-01-claude-fable-5-1.md",
        "written receipt did not carry the pushed debrief's path",
    )
    require(
        receipt["tasks"]["DEV-301"]["merged_sha"] == "abc1230000000000000000000000000000000000",
        f"written receipt's merged_sha did not come from the fake gh stub's oid: {receipt['tasks']['DEV-301']!r}",
    )

# --- AC-4: removing the fake gh stub from PATH flips the same closeable fixture to a failure --
with tempfile.TemporaryDirectory() as scratch_name:
    scratch = Path(scratch_name)
    fence_dir = write_closeable_scratch(scratch)
    no_gh = run(["ship-cloud-wrapper", "--state-dir", str(scratch)], path_override="/usr/bin:/bin")
    require(no_gh.returncode != 0, f"closing succeeded with no gh on PATH -- resolution isn't gating: exit={no_gh.returncode}")
    require(
        not (fence_dir / "close-receipt-ship-cloud-wrapper.json").is_file(),
        "a receipt was written even though gh could not be called to confirm the merge",
    )

# --- AC-1 bullet 2: a pr-merge task whose gh-confirmed state is not MERGED is refused, no receipt --
not_merged_dir = FIXTURES / "not-merged"
not_merged = run(["ship-cloud-wrapper", "--state-dir", str(not_merged_dir)])
require(not_merged.returncode != 0, f"a non-MERGED gh state did not fail the close: exit={not_merged.returncode}")
require(
    "DEV-305" in (not_merged.stdout + not_merged.stderr) and "OPEN" in (not_merged.stdout + not_merged.stderr),
    f"the not-merged refusal did not name the slug and state: stdout={not_merged.stdout!r} stderr={not_merged.stderr!r}",
)
require(
    not (not_merged_dir / "_ship_fence" / "close-receipt-ship-cloud-wrapper.json").is_file(),
    "a receipt was written for a batch containing a task whose PR is not actually MERGED",
)

# --- AC-2: find_debrief_path matches a worker's own `## Shipped` section, never the FO's file --
fo_exclude_dir = FIXTURES / "debrief-fo-exclude"
require(
    close_module.find_debrief_path(fo_exclude_dir, "slug-alpha") == "_debriefs/02-worker.md",
    "find_debrief_path picked the FO's debrief (or nothing) instead of the worker's Shipped file",
)
require(
    close_module.find_debrief_path(fo_exclude_dir, "slug-beta") is None,
    "find_debrief_path matched a slug named only outside any '## Shipped' section",
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

# --- AC-3: --validate refuses a null merged_sha and a short/non-40-hex merged_sha, naming both --
bad_sha = run(["--validate", str(FIXTURES / "receipts" / "bad-merged-sha.json")])
require(
    bad_sha.returncode == 1 and "DEV-301" in bad_sha.stderr and "DEV-306" in bad_sha.stderr,
    f"--validate did not refuse null (DEV-301) and short (DEV-306) merged_sha, naming both: "
    f"exit={bad_sha.returncode} stderr={bad_sha.stderr!r}",
)

# --- close.py's own readers against a fence file dispatch.sh/watch.sh actually produce ---
# Same reconciliation as uat-doc.test.py: `debrief_status`/`build_receipt` must read the
# top-level `<slug> -> {workspace, session, message_sha256}` shape dispatch.sh actually commits
# (pinned in the sibling dispatch/watch task's own fixture,
# fixtures/watch/state/_ship_fence/ship-cloud-wrapper.json -- verified against dispatch.sh's real
# writes in dispatch.test.sh cases (b)/(e)), with close.py's own `merged_sha`/`debrief` additions
# layered on top of one slug's object, not nested under a "tasks" key.
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

# --- AC-1/AC-2/AC-4 two-root flags: --dev-state/--ship-state and --state-dir shorthand ---
require(
    run(["ship-cloud-wrapper", "--dry-run", "--dev-state", str(dry_run_dir), "--ship-state", str(dry_run_dir)]).returncode == 0,
    "--dev-state/--ship-state pointed at the same dir did not behave like --state-dir",
)
usage_err = run(["ship-cloud-wrapper", "--dry-run", "--dev-state", str(dry_run_dir)])
require(
    usage_err.returncode == 2,
    f"missing --ship-state (and no --state-dir) did not exit 2: {usage_err.returncode}",
)

# --- AC-2: close.py itself scans `_debriefs/` and finds a task's pushed debrief the fence has
# not recorded yet -- no message for it even in --dry-run, and a non-dry-run writes
# `<slug>.debrief.status: pushed` with the matched path into the ship-state fence.
# AC-4: a merged task with *no* fence entry at all still shows up "merged" from its own `pr:`
# field, is not counted as a dispatch/merge failure, and appears in the receipt with
# `workspace_id: null`.
scan_fixtures = FIXTURES / "debrief-scan"
scan_dev = scan_fixtures / "dev-state"
scan_ship = scan_fixtures / "ship-state"

scan_dry_run = run(["ship-cloud-wrapper", "--dry-run", "--dev-state", str(scan_dev), "--ship-state", str(scan_ship)])
require(
    scan_dry_run.returncode == 0,
    f"debrief-scan fixture --dry-run did not exit 0: {scan_dry_run.returncode} stderr={scan_dry_run.stderr!r}",
)
require(
    not [l for l in scan_dry_run.stdout.splitlines() if l.strip()],
    f"debrief-scan fixture --dry-run printed a message for a task whose debrief is already "
    f"findable under _debriefs/: {scan_dry_run.stdout!r}",
)

with tempfile.TemporaryDirectory() as scratch_name:
    import shutil as _shutil  # noqa: E402

    scratch = Path(scratch_name)
    scratch_dev = scratch / "dev-state"
    scratch_ship = scratch / "ship-state"
    _shutil.copytree(scan_dev, scratch_dev)
    _shutil.copytree(scan_ship, scratch_ship)

    scan_live = run(["ship-cloud-wrapper", "--dev-state", str(scratch_dev), "--ship-state", str(scratch_ship)])
    require(
        scan_live.returncode == 0,
        f"debrief-scan fixture non-dry-run did not exit 0: {scan_live.returncode} "
        f"stdout={scan_live.stdout!r} stderr={scan_live.stderr!r}",
    )

    updated_fence = json.loads((scratch_ship / "_ship_fence" / "ship-cloud-wrapper.json").read_text(encoding="utf-8"))
    require(
        updated_fence["DEV-303"]["debrief"] == {"status": "pushed", "path": "_debriefs/2026-09-11-fixture-303.md"},
        f"close.py did not scan _debriefs/ and record DEV-303's pushed debrief into the fence: {updated_fence!r}",
    )
    require(
        updated_fence.get("DEV-304", {}).get("debrief") == {"status": "pushed", "path": "_debriefs/2026-09-11-fixture-304.md"},
        f"close.py did not record a debrief found only in a _debriefs/ file's body: {updated_fence!r}",
    )

    scan_receipt_path = scratch_ship / "_ship_fence" / "close-receipt-ship-cloud-wrapper.json"
    require(scan_receipt_path.is_file(), "debrief-scan fixture did not write a receipt")
    scan_receipt = json.loads(scan_receipt_path.read_text(encoding="utf-8"))
    require(
        scan_receipt["tasks"]["DEV-304"]["workspace_id"] is None,
        f"a task with no fence entry did not carry workspace_id: null in the receipt: {scan_receipt['tasks']['DEV-304']!r}",
    )
    require(
        set(scan_receipt["tasks"]) == {"DEV-303", "DEV-304"},
        f"receipt task set did not include the fence-less merged task: {sorted(scan_receipt['tasks'])!r}",
    )

# --- AC-1 (roster): a sprint-matching entity absent from the fence and never merged is dropped,
# named once on stderr as "not dispatched", and the batch still closes -- the r3 bug fix ---
not_dispatched_dir = FIXTURES / "not-dispatched"
with tempfile.TemporaryDirectory() as scratch_name:
    scratch = Path(scratch_name)
    for name in ("DEV-301.md", "DEV-307.md"):
        (scratch / name).write_text(
            (not_dispatched_dir / name).read_text(encoding="utf-8"), encoding="utf-8"
        )
    fence_dir = scratch / "_ship_fence"
    fence_dir.mkdir()
    (fence_dir / "ship-cloud-wrapper.json").write_text(
        (not_dispatched_dir / "_ship_fence" / "ship-cloud-wrapper.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    not_dispatched = run(["ship-cloud-wrapper", "--state-dir", str(scratch)])
    require(
        not_dispatched.returncode == 0,
        f"a batch with a deferred, never-dispatched sibling did not close: "
        f"exit={not_dispatched.returncode} stdout={not_dispatched.stdout!r} stderr={not_dispatched.stderr!r}",
    )
    require(
        "close: DEV-307 not dispatched, skipping" in not_dispatched.stderr,
        f"the never-dispatched sibling was not named 'not dispatched' on stderr: {not_dispatched.stderr!r}",
    )
    nd_receipt_path = fence_dir / "close-receipt-ship-cloud-wrapper.json"
    require(nd_receipt_path.is_file(), f"the batch did not write a receipt at {nd_receipt_path}")
    nd_receipt = json.loads(nd_receipt_path.read_text(encoding="utf-8"))
    require(
        set(nd_receipt["tasks"]) == {"DEV-301"},
        f"the written receipt did not omit the never-dispatched sibling: {sorted(nd_receipt['tasks'])!r}",
    )

# --- AC-2 (captain_stopped validates): --validate accepts a captain_stopped task's null
# merged_sha paired with the closed marker; the existing bad-merged-sha fixture still fails ---
captain_stopped_receipt = run(["--validate", str(FIXTURES / "receipts" / "captain-stopped.json")])
require(
    captain_stopped_receipt.returncode == 0,
    f"--validate refused a captain_stopped task's null merged_sha: "
    f"exit={captain_stopped_receipt.returncode} stderr={captain_stopped_receipt.stderr!r}",
)
bad_sha_still_fails = run(["--validate", str(FIXTURES / "receipts" / "bad-merged-sha.json")])
require(
    bad_sha_still_fails.returncode == 1
    and "DEV-301" in bad_sha_still_fails.stderr
    and "DEV-306" in bad_sha_still_fails.stderr,
    f"adding the captain_stopped exemption widened the bad-merged-sha refusal: "
    f"exit={bad_sha_still_fails.returncode} stderr={bad_sha_still_fails.stderr!r}",
)

print("close test: all checks passed")
