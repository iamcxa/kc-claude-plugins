#!/usr/bin/env python3
"""Behavior contract for kc-ship-flow/scripts/dev-debrief.py."""

from __future__ import annotations

import importlib.util
import json as json_mod
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "dev-debrief.py"
FIXTURES = HERE / "fixtures" / "debrief-writer"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"dev-debrief test: {message}")


def load_module():
    spec = importlib.util.spec_from_file_location("dev_debrief", MODULE_PATH)
    require(spec is not None and spec.loader is not None, "cannot load dev-debrief.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


dev_debrief = load_module()


def run(batch: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(MODULE_PATH), str(batch)], capture_output=True, text=True
    )


# --- finding #4: evidence-file selection prefers "accepted", then the -----
# --- highest round suffix, and refuses an unresolved ambiguity -----------
selection = run(FIXTURES / "batch-selection-probe")
require(selection.returncode == 0, f"selection-probe must exit 0, got {selection.returncode}: {selection.stderr}")
selection_doc = json_mod.loads(selection.stdout)
require(
    selection_doc["per_issue"]["DEV-301"]["evidence_refusals"] == ["retained -> exit 0; removed -> exit 2"],
    "selection-probe must draft from worker-evidence-DEV-301-r2-accepted.md, not the r1-refused file: "
    f"got {selection_doc['per_issue']['DEV-301']['evidence_refusals']}",
)

# --- finding #3: a missing evidence file exits 2 naming the issue, never --
# --- a silently empty draft ------------------------------------------------
missing_evidence = run(FIXTURES / "batch-missing-evidence-probe")
require(missing_evidence.returncode == 2, f"missing evidence file must exit 2, got {missing_evidence.returncode}")
require("DEV-302" in missing_evidence.stderr, f"missing-evidence refusal must name DEV-302: {missing_evidence.stderr!r}")

# --- finding #3: a missing `rounds` key exits 2 naming the issue, never ---
# --- a silent default of 0 -------------------------------------------------
missing_rounds = run(FIXTURES / "batch-missing-rounds-probe")
require(missing_rounds.returncode == 2, f"missing rounds must exit 2, got {missing_rounds.returncode}")
require("DEV-305" in missing_rounds.stderr, f"missing-rounds refusal must name DEV-305: {missing_rounds.stderr!r}")

# --- finding #3: code_refusals is sourced from the record, never a copy --
# --- of issues[*].residuals, and a record naming neither source emits ----
# --- an explicit marker instead of an empty list --------------------------
happy = FIXTURES.parent / "uat-doc" / "batch-1016352e0223"
happy_result = run(happy)
require(happy_result.returncode == 0, f"batch-1016352e0223 must exit 0, got {happy_result.returncode}: {happy_result.stderr}")
happy_doc = json_mod.loads(happy_result.stdout)
require(
    happy_doc["per_issue"]["DEV-91"]["code_refusals"] == [
        "2026-09-03T15:10:00Z — DEV-91 REFUSE: minimal-necessity fail, goal already met by DEV-90 (S26); "
        "accepted without a PR per `minimal_necessity_fail: accepted_no_pr`."
    ],
    f"DEV-91 code_refusals must be its own README REFUSE bullet: {happy_doc['per_issue']['DEV-91']['code_refusals']}",
)
require(
    happy_doc["per_issue"]["DEV-90"]["code_refusals"] != happy_doc["per_issue"]["DEV-91"]["code_refusals"],
    "DEV-90 must not inherit DEV-91's REFUSE bullet merely for being named inside it",
)
require(
    happy_doc["per_issue"]["DEV-90"]["code_refusals"] == ["source: not recorded"],
    f"DEV-90 has no README REFUSE bullet or review disposition of its own; "
    f"got {happy_doc['per_issue']['DEV-90']['code_refusals']}",
)
require(
    happy_doc["per_issue"]["DEV-92"]["code_refusals"][0].startswith("disposition-365.json:"),
    f"DEV-92 code_refusals must be sourced from review/disposition-365.json: {happy_doc['per_issue']['DEV-92']['code_refusals']}",
)

# --- finding #4: the selection function itself, isolated from any batch --
# --- fixture -- refuses when no round suffix can rank the survivors ------
require(
    dev_debrief.select_evidence_file(["worker-evidence-DEV-1-r1.md", "worker-evidence-DEV-1-r2.md"])
    == "worker-evidence-DEV-1-r2.md",
    "select_evidence_file must prefer the highest round suffix when nothing is marked accepted",
)
try:
    dev_debrief.select_evidence_file(["worker-evidence-DEV-1-a.md", "worker-evidence-DEV-1-b.md"])
    require(False, "select_evidence_file must refuse two candidates with no accepted marker and no round suffix")
except dev_debrief.AmbiguousEvidence:
    pass

# --- finding #9: malformed JSON exits 2 with a one-line reason, never a --
# --- raw traceback -----------------------------------------------------------
with tempfile.TemporaryDirectory() as tmp:
    receipt_dir = Path(tmp) / "receipt"
    receipt_dir.mkdir()
    (receipt_dir / "close-receipt.json").write_text("{not valid json", encoding="utf-8")
    malformed = run(Path(tmp))
    require(malformed.returncode == 2, f"malformed close receipt must exit 2, got {malformed.returncode}")
    require("Traceback" not in malformed.stderr, f"malformed JSON leaked a traceback: {malformed.stderr!r}")

# --- DEV-135 AC-1: a carried issue with no worker-evidence file exits 0 ---
# --- with an empty refusal list and a not-dispatched note -----------------
carried = run(FIXTURES / "batch-carried-probe")
require(carried.returncode == 0, f"batch-carried-probe must exit 0, got {carried.returncode}: {carried.stderr}")
carried_doc = json_mod.loads(carried.stdout)
carried_entry = next(v for k, v in carried_doc["per_issue"].items() if k.startswith("DEV-9"))
require(
    carried_entry == {"rounds": 0, "evidence_refusals": [], "code_refusals": [], "note": "not dispatched"},
    f"carried issue must be an empty-refusal, not-dispatched entry: {carried_entry}",
)

# --- DEV-135 AC-2: the same fixture with the carried issue's outcome ------
# --- changed to `merged` still exits 2 naming the missing evidence file ---
with tempfile.TemporaryDirectory() as tmp:
    mutated_batch = Path(tmp) / "batch-carried-probe"
    shutil.copytree(FIXTURES / "batch-carried-probe", mutated_batch)
    close_path = mutated_batch / "receipt" / "close-receipt.DRAFT.json"
    close_doc = json_mod.loads(close_path.read_text(encoding="utf-8"))
    (issue_id,) = close_doc["issues"]
    close_doc["issues"][issue_id]["outcome"] = "merged"
    close_path.write_text(json_mod.dumps(close_doc), encoding="utf-8")
    merged_outcome = run(mutated_batch)
    require(
        merged_outcome.returncode == 2 and issue_id in merged_outcome.stderr,
        f"a `merged` outcome with no evidence file must still exit 2 naming {issue_id}: "
        f"exit={merged_outcome.returncode} stderr={merged_outcome.stderr!r}",
    )

print("dev-debrief test: all checks passed")
