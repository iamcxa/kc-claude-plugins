#!/usr/bin/env python3
"""Behavior contract for scripts/ship-flow/uat-doc.py."""

from __future__ import annotations

import importlib.util
import json as json_mod
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "uat-doc.py"
FIXTURES = HERE.parent / "fixtures" / "ship-flow" / "uat-doc"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"uat-doc test: {message}")


def load_module():
    spec = importlib.util.spec_from_file_location("uat_doc", MODULE_PATH)
    require(spec is not None and spec.loader is not None, "cannot load uat-doc.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


uat_doc = load_module()


def heading_lines(text: str) -> list[str]:
    def normalize(line: str) -> str:
        line = line.rstrip()
        return line.split(" — ", 1)[0] if " — " in line else line

    return [normalize(l) for l in text.splitlines() if l.startswith("#")]


def pr_numbers(text: str) -> set[str]:
    return set(re.findall(r"/pull/(\d+)", text))


# --- finding #11: uat.md.reference gets a reader ---------------------------
reference_batch = FIXTURES / "batch-1016352e0223"
reference_text = (reference_batch / "evidence" / "uat.md.reference").read_text(encoding="utf-8")
generated_text = uat_doc.build_doc(str(reference_batch))
require(
    set(heading_lines(reference_text)) <= set(heading_lines(generated_text)),
    f"generated doc dropped a reference heading: {set(heading_lines(reference_text)) - set(heading_lines(generated_text))}",
)
require(
    pr_numbers(reference_text) == pr_numbers(generated_text),
    f"PR set differs from reference: reference={pr_numbers(reference_text)} generated={pr_numbers(generated_text)}",
)

# --- findings #1, #6: BRANCH injection + newline-title injection ----------
injection_text = uat_doc.build_doc(str(FIXTURES / "batch-injection-probe"))
require("](" not in injection_text, "a markdown link survived sanitization")
require(
    sum(1 for line in injection_text.splitlines() if line == "## For the Captain") == 1,
    "an embedded newline in a title forged a second '## For the Captain' heading",
)
require(
    "<unsafe value refused>" in injection_text,
    "a BRANCH value outside the git-ref-safe allowlist was rendered instead of refused",
)

# --- finding #2: an issue with no Evidence file and no close entry --------
unaccounted_text = uat_doc.build_doc(str(FIXTURES / "batch-unaccounted-probe"))
require("## Unaccounted" in unaccounted_text, "missing Unaccounted section")
require("- DEV-2: no Evidence file and no close-receipt entry." in unaccounted_text, "DEV-2 not listed as unaccounted")
require(
    "none stuck." not in unaccounted_text,
    "'Not handed off' printed 'none stuck.' while Unaccounted is non-empty",
)

# --- finding #4: missing Evidence file never renders literal None ---------
missing_evidence_text = uat_doc.build_doc(str(FIXTURES / "batch-missing-evidence-probe"))
require(
    "base: not recorded · branch: not recorded" in missing_evidence_text,
    "a missing Evidence file did not render 'base: not recorded · branch: not recorded'",
)
require("None" not in missing_evidence_text, "a missing field rendered literal 'None'")
require(uat_doc.base_label(None, {}) == "(not recorded)", "base_label(None, ...) must be '(not recorded)', not '(main)'")
require(uat_doc.base_label("deadbeef", {}) == "(main)", "base_label of a real, unmapped base_sha must stay '(main)'")

# --- finding #5: branch selection is no longer dead code ------------------
branch_logic_text = uat_doc.build_doc(str(FIXTURES / "batch-branch-logic-probe"))
require(
    "branch `feature/dev-1-actual-pushed`" in branch_logic_text,
    "a close-receipt candidate present must select the worker's own BRANCH",
)
require(
    "branch `feature/dev-2-planned`" in branch_logic_text,
    "no close-receipt candidate must fall back to the plan receipt's planned branch, not the worker's",
)

# --- finding #3: worker-sourced lines are labeled honestly -----------------
require(
    "Without-it (worker self-report):" in generated_text,
    "without-it line is not labeled as a worker self-report",
)
require(
    "contract test (worker self-report)" in generated_text,
    "contract test status is not labeled as a worker self-report",
)
require("FO ran verbatim" not in generated_text, "a line still claims the FO ran something verbatim")
self_check_text = uat_doc.build_doc(str(FIXTURES / "batch-e56e9f09873c"))
require(
    "FO accept station: 2026-09-06T02:20:47Z accept-evidence: ACCEPT" in self_check_text,
    "FO accept station line is not sourced from the block's SELF_CHECK field",
)

# --- finding #7: decisions parser recognizes '- ' and '* ' and joins wraps -
decisions = uat_doc.load_defaults_decisions(str(FIXTURES / "decisions-mixed-bullets"))
require(decisions is not None and len(decisions) == 3, f"expected 3 decisions, got {decisions}")
require(decisions[0] == "2026-09-06T00:00Z — dash-bullet decision, single line.", f"dash bullet not parsed: {decisions}")
require(decisions[1] == "2026-09-06T00:01Z — star-bullet decision, single line.", f"star bullet not parsed: {decisions}")
require(
    decisions[2]
    == "2026-09-06T00:02Z — dash-bullet decision that wraps onto a second physical line that must join the first.",
    f"wrapped continuation line not joined: {decisions}",
)

# --- finding #8: malformed receipt data exits 2, not a traceback ----------
with tempfile.TemporaryDirectory() as tmp:
    tmp_path = Path(tmp)
    (tmp_path / "receipt").mkdir()
    (tmp_path / "receipt" / "plan-receipt.json").write_text("{not valid json", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(MODULE_PATH), str(tmp_path)],
        capture_output=True,
        text=True,
    )
    require(result.returncode == 2, f"malformed JSON must exit 2, got {result.returncode}")
    require("Traceback" not in result.stderr, "malformed JSON leaked a traceback instead of a one-line reason")

with tempfile.TemporaryDirectory() as tmp:
    tmp_path = Path(tmp)
    (tmp_path / "receipt").mkdir()
    (tmp_path / "receipt" / "plan-receipt.json").write_text(
        json_mod.dumps({"project": {"name": "no dispatch_order here"}}), encoding="utf-8"
    )
    result = subprocess.run(
        [sys.executable, str(MODULE_PATH), str(tmp_path)],
        capture_output=True,
        text=True,
    )
    require(result.returncode == 2, f"a receipt missing a required key must exit 2, got {result.returncode}")
    require("Traceback" not in result.stderr, "a missing key leaked a traceback instead of a one-line reason")

# --- finding #10: the evidence glob is anchored ----------------------------
glob_batch = str(FIXTURES / "batch-glob-anchor-probe")
require(not uat_doc.has_worker_evidence(glob_batch, "DEV-9"), "DEV-9 must not match DEV-90's evidence file")
require(uat_doc.has_worker_evidence(glob_batch, "DEV-90"), "DEV-90's own evidence file must be found")

print("uat-doc test: all checks passed")
