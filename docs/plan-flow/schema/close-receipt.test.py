#!/usr/bin/env python3
"""Behavior contract for validate-receipt.py's close-receipt argument
(docs/plan-flow/schema/validate-receipt.py <receipt> <approval> <close>).

`jsonschema` is a hard requirement: every case below runs with it available
(the interpreter running this test), and one case runs the script under
`python3 -S` (which drops site-packages, so `jsonschema` is unimportable
while the stdlib this script needs stays available) to prove the import
failure exits 2 naming it, rather than silently falling back to a weaker
check.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "validate-receipt.py"
FIXTURES = HERE.parent.parent.parent / "kc-ship-flow" / "scripts" / "fixtures" / "close-receipt"

PLAN_RECEIPT = FIXTURES / "plan-receipt.json"
PLAN_APPROVAL = FIXTURES / "plan-approval.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"close-receipt test: {message}")


def run(close_fixture: str, *, no_jsonschema: bool = False) -> subprocess.CompletedProcess:
    cmd = [sys.executable]
    if no_jsonschema:
        cmd.append("-S")
    cmd += [str(MODULE_PATH), str(PLAN_RECEIPT), str(PLAN_APPROVAL), str(FIXTURES / close_fixture)]
    return subprocess.run(cmd, capture_output=True, text=True)


def require_refusal(close_fixture: str, needle: str) -> None:
    """Run a negative fixture (jsonschema available) and require exit 1 with
    an INVALID: line naming `needle`."""
    plain = run(close_fixture)
    require(plain.returncode == 1, f"{close_fixture}: expected exit 1, got {plain.returncode}: {plain.stdout}{plain.stderr}")
    require(needle in plain.stdout, f"{close_fixture}: refusal must name {needle!r}: {plain.stdout!r}")


# --- DEV-147 AC-1: jsonschema absent exits 2 naming it, never a silent -----
# --- structural-only fallback -----------------------------------------------
no_jsonschema_result = run("close-receipt.dispositioned.json", no_jsonschema=True)
require(
    no_jsonschema_result.returncode == 2,
    f"jsonschema-absent run must exit 2, got {no_jsonschema_result.returncode}: "
    f"{no_jsonschema_result.stdout}{no_jsonschema_result.stderr}",
)
require(
    "jsonschema required" in no_jsonschema_result.stdout,
    f"jsonschema-absent run must print 'jsonschema required': {no_jsonschema_result.stdout!r}",
)

# --- finding #8: the "refuses undispositioned" step is isolated -- the ----
# --- DRAFT fixture differs from the accepted one in exactly the three ----
# --- accepted_residual fields, so this is the only thing that can fail ----
require_refusal("close-receipt.DRAFT.json", "S24, S25, S26")

accepted = run("close-receipt.dispositioned.json")
require(accepted.returncode == 0, f"dispositioned fixture must exit 0: {accepted.returncode} {accepted.stdout}{accepted.stderr}")
require("CLOSE OK" in accepted.stdout, f"dispositioned fixture must print CLOSE OK: {accepted.stdout!r}")

# --- AC-3: a missing dev_debrief and a missing per-issue field each -------
# --- refuse naming the field, isolated from each other and from #8 -------
require_refusal("close-receipt.missing-dev-debrief.json", "dev_debrief")
require_refusal("close-receipt.missing-rounds.json", "DEV-91")

# --- finding #1: a whitespace-only disposition is the same as absent -----
require_refusal("close-receipt.blank-residual.json", "S24")

# --- finding #2: every schema-expressed check also runs in plain Python --
require_refusal("close-receipt.blank-candidate-correction.json", "candidate_correction")
require_refusal("close-receipt.malformed-fix-ticket.json", "fix_ticket")
require_refusal("close-receipt.malformed-defect-id.json", "malformed id")

# --- finding #7: per_issue and defects_disposition completeness ----------
require_refusal("close-receipt.per-issue-mismatch.json", "dev_debrief.per_issue")
require_refusal("close-receipt.disposition-mismatch.json", "ship_debrief.defects_disposition")

# --- DEV-147: a close receipt embedding the debrief writers' own wrapper -
# --- (`schema` + `close_receipt` keys) inside `dev_debrief` is a shape ----
# --- `additionalProperties: false` forbids -- reproduces batch ----------
# --- ab2fb2635f0c's actual defect (a hand-written dev-debrief.json's -----
# --- content pasted into the close receipt's own dev_debrief field) ------
require_refusal("close-receipt.dev-debrief-wrapper-embedded.json", "dev_debrief")

# --- falsifier: a real close-receipt shape (batch ab2fb2635f0c, ids -------
# --- replaced) with a `captain_stopped` issue and a mixed defect ---------
# --- disposition set validates unchanged ----------------------------------
ab2fb2635f0c_dir = FIXTURES / "ab2fb2635f0c-shape"
ab2fb2635f0c_result = subprocess.run(
    [
        sys.executable, str(MODULE_PATH),
        str(ab2fb2635f0c_dir / "plan-receipt.json"),
        str(ab2fb2635f0c_dir / "plan-approval.json"),
        str(ab2fb2635f0c_dir / "close-receipt.json"),
    ],
    capture_output=True, text=True,
)
require(
    ab2fb2635f0c_result.returncode == 0 and "CLOSE OK" in ab2fb2635f0c_result.stdout,
    f"ab2fb2635f0c-shape fixture must validate unchanged: "
    f"exit={ab2fb2635f0c_result.returncode} stdout={ab2fb2635f0c_result.stdout!r} stderr={ab2fb2635f0c_result.stderr!r}",
)

# --- validate-receipt.py refuses when the plugin's close-receipt schema is
# --- not installed (HERE.parents[2]/kc-ship-flow/schemas/ absent). jsonschema
# --- is required up front, so this case runs with it available; the
# --- schema-not-installed check is a plain-Python guard ahead of the
# --- jsonschema.validate() call, not a substitute for jsonschema itself.
with tempfile.TemporaryDirectory(prefix="close-receipt-absent-schema-") as absent_root_name:
    absent_root = Path(absent_root_name)
    absent_module_dir = absent_root / "docs" / "plan-flow" / "schema"
    absent_module_dir.mkdir(parents=True)
    absent_module = absent_module_dir / "validate-receipt.py"
    shutil.copy(MODULE_PATH, absent_module)
    # validate-receipt.py loads both plan schemas unconditionally now that
    # jsonschema is a hard requirement, so the copy needs both.
    shutil.copy(HERE / "kc-plan-receipt.v1.schema.json", absent_module_dir / "kc-plan-receipt.v1.schema.json")
    shutil.copy(HERE / "kc-plan-approval.v1.schema.json", absent_module_dir / "kc-plan-approval.v1.schema.json")
    absent_fixtures = absent_root / "fixtures"
    absent_fixtures.mkdir()
    absent_plan_receipt = shutil.copy(PLAN_RECEIPT, absent_fixtures / "plan-receipt.json")
    absent_plan_approval = shutil.copy(PLAN_APPROVAL, absent_fixtures / "plan-approval.json")
    absent_close_receipt = shutil.copy(
        FIXTURES / "close-receipt.dispositioned.json", absent_fixtures / "close-receipt.json"
    )
    absent = subprocess.run(
        [
            sys.executable, str(absent_module),
            absent_plan_receipt, absent_plan_approval, absent_close_receipt,
        ],
        capture_output=True, text=True,
    )
    require(
        absent.returncode == 1,
        f"absent close-receipt schema: expected exit 1, got {absent.returncode}: {absent.stdout}{absent.stderr}",
    )
    require(
        "close-receipt schema not installed" in absent.stdout,
        f"absent close-receipt schema refusal must name it: {absent.stdout!r}",
    )

print("close-receipt test: all checks passed")
