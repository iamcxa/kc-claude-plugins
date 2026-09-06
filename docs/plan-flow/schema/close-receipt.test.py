#!/usr/bin/env python3
"""Behavior contract for validate-receipt.py's close-receipt argument
(docs/plan-flow/schema/validate-receipt.py <receipt> <approval> <close>).

Every negative fixture here runs under both the plain interpreter and
`python3 -S` (which drops site-packages, so `jsonschema` is unimportable
while the stdlib this script needs stays available) and asserts the same
INVALID: line -- proving the structural Python checks, not jsonschema, are
what names the refusal.
"""
from __future__ import annotations

import subprocess
import sys
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
    """Run a negative fixture with and without jsonschema and require both
    runs to exit 1 with the same INVALID: line naming `needle`."""
    plain = run(close_fixture)
    require(plain.returncode == 1, f"{close_fixture}: expected exit 1, got {plain.returncode}: {plain.stdout}{plain.stderr}")
    require(needle in plain.stdout, f"{close_fixture}: refusal must name {needle!r}: {plain.stdout!r}")

    structural = run(close_fixture, no_jsonschema=True)
    require(
        "jsonschema not installed" in structural.stdout,
        f"{close_fixture}: -S run did not actually drop jsonschema: {structural.stdout!r}",
    )
    require(
        structural.returncode == 1 and needle in structural.stdout,
        f"{close_fixture}: -S run must refuse identically naming {needle!r}: {structural.stdout!r}",
    )
    plain_invalid = next(l for l in plain.stdout.splitlines() if l.startswith("INVALID:"))
    structural_invalid = next(l for l in structural.stdout.splitlines() if l.startswith("INVALID:"))
    require(
        plain_invalid == structural_invalid,
        f"{close_fixture}: INVALID line differs with/without jsonschema: {plain_invalid!r} vs {structural_invalid!r}",
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

print("close-receipt test: all checks passed")
