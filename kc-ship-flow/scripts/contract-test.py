#!/usr/bin/env python3
"""Behavior and packaging contract for kc-ship-flow."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLUGIN = ROOT / "kc-ship-flow"
SCRIPTS = PLUGIN / "scripts"
FIXTURES = SCRIPTS / "fixtures"

if sys.argv[1:]:
    raise SystemExit("usage: contract-test.py")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"kc-ship-flow contract: {message}")


def run(command: list[str], label: str, *, echo: bool = False) -> None:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    require(
        result.returncode == 0,
        f"{label} failed:\n{result.stdout}{result.stderr}",
    )
    if echo:
        # dispatch.test.sh/watch.test.sh's own "case N: PASS - ..." lines (and the final
        # "N passed, 0 failed" summary) need to actually show up in a CI log, not just be
        # discarded on a green run -- a required check is a mute PASS otherwise.
        print(result.stdout, end="")


STATIONS = [
    "dispatch.sh",
    "watch.sh",
    "e2e-cli.sh",
    "e2e-gate.py",
    "parse-execute-external.py",
    "uat-doc.py",
    "close.py",
]
for station in STATIONS:
    require((SCRIPTS / station).is_file(), f"missing station script: {station}")
    print(f"kc-ship-flow contract: station present: {station}")

STATION_TESTS = [
    ("uat-doc.test.py", [sys.executable, str(SCRIPTS / "uat-doc.test.py")]),
    ("close.test.py", [sys.executable, str(SCRIPTS / "close.test.py")]),
    ("pin.test.py", [sys.executable, str(SCRIPTS / "pin.test.py")]),
]
for test_name, test_command in STATION_TESTS:
    require((SCRIPTS / test_name).is_file(), f"missing station test: {test_name}")
    run(test_command, f"kc-ship-flow {test_name}")

# dispatch.sh/watch.sh's own test suites run entirely against the self-contained fake
# `conductor` under fixtures/fake-conductor-{dispatch,watch}/ -- no real conductor CLI is
# needed (round 2: the fakes used to delegate --version/--help to a real binary, which is
# why these were previously skipped here when conductor was absent from the CI runner).
# Always run them, so a PR that breaks either suite is red, not silently skipped.
run(["bash", str(SCRIPTS / "dispatch.test.sh")], "kc-ship-flow dispatch.test.sh", echo=True)
run(["bash", str(SCRIPTS / "watch.test.sh")], "kc-ship-flow watch.test.sh", echo=True)

for py_station in [
    "e2e-gate.py",
    "parse-execute-external.py",
    "uat-doc.py",
    "close.py",
]:
    run([sys.executable, "-m", "py_compile", str(SCRIPTS / py_station)], f"{py_station} compile")

CLOSE_RECEIPT_SCHEMA = PLUGIN / "schemas" / "kc-ship-close-receipt.v1.schema.json"
require(CLOSE_RECEIPT_SCHEMA.is_file(), f"missing {CLOSE_RECEIPT_SCHEMA}")

e2e_gate = SCRIPTS / "e2e-gate.py"
e2e_gate_fixtures = FIXTURES / "e2e-gate"


def run_e2e_gate(
    plan_fixture: str,
    close_fixture: str,
    *,
    offline: bool = False,
    close_receipt_override: dict | None = None,
) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    if offline:
        env["https_proxy"] = "http://127.0.0.1:9"
        env["http_proxy"] = "http://127.0.0.1:9"
    close_path = e2e_gate_fixtures / close_fixture
    override_path: Path | None = None
    if close_receipt_override is not None:
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as handle:
            json.dump(close_receipt_override, handle)
            override_path = Path(handle.name)
        close_path = override_path
    try:
        return subprocess.run(
            [
                sys.executable, str(e2e_gate),
                "--root", str(ROOT), "--flows", "docs/ship-flow/flows",
                str(e2e_gate_fixtures / plan_fixture), str(close_path),
            ],
            cwd=ROOT, text=True, capture_output=True, env=env, timeout=30,
        )
    finally:
        if override_path is not None:
            override_path.unlink(missing_ok=True)


# The committed ac2 fixture carries a placeholder candidate (a real SHA
# would go unreachable under a shallow CI checkout); this is the only
# gate scenario that runs e2e-cli.sh, so it needs a commit that both
# resolves and contains the fixtures its flow's own steps reference --
# this checkout's own HEAD always satisfies both.
current_head = subprocess.run(
    ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True, check=True,
).stdout.strip()
ac2_close_receipt = json.loads((e2e_gate_fixtures / "close-receipt.ac2.json").read_text(encoding="utf-8"))
ac2_issue_key = next(iter(ac2_close_receipt["issues"]))
ac2_close_receipt["issues"][ac2_issue_key]["candidate"] = current_head

e2e_gate_ac2 = run_e2e_gate(
    "plan-receipt.ac2.json", "close-receipt.ac2.json", offline=True, close_receipt_override=ac2_close_receipt,
)
require(
    e2e_gate_ac2.returncode == 0 and re.search(r"CLI e2e:.*at [0-9a-f]{40},", e2e_gate_ac2.stdout),
    f"e2e-gate ac2 (run branch) did not exit 0 with a resolved-SHA report line: "
    f"exit {e2e_gate_ac2.returncode}, stdout {e2e_gate_ac2.stdout!r}, stderr {e2e_gate_ac2.stderr!r}",
)

e2e_gate_ac3 = run_e2e_gate("plan-receipt.ac3.json", "close-receipt.ac3.json")
require(
    e2e_gate_ac3.returncode == 0 and "e2e: not applicable" in e2e_gate_ac3.stdout,
    f"e2e-gate ac3 (not-applicable branch) failed: exit {e2e_gate_ac3.returncode}, stdout {e2e_gate_ac3.stdout!r}",
)

e2e_gate_ac4 = run_e2e_gate("plan-receipt.ac4.json", "close-receipt.ac4.json")
require(
    e2e_gate_ac4.returncode == 1,
    f"e2e-gate ac4 (no milestone named) should exit 1: exit {e2e_gate_ac4.returncode}, stderr {e2e_gate_ac4.stderr!r}",
)

e2e_gate_dangling = run_e2e_gate("plan-receipt.dangling-milestone.json", "close-receipt.dangling-milestone.json")
require(
    e2e_gate_dangling.returncode == 2,
    f"e2e-gate dangling milestone id should exit 2: exit {e2e_gate_dangling.returncode}, stderr {e2e_gate_dangling.stderr!r}",
)

e2e_gate_empty_slug = run_e2e_gate("plan-receipt.empty-slug.json", "close-receipt.empty-slug.json")
require(
    e2e_gate_empty_slug.returncode == 2,
    f"e2e-gate punctuation-only milestone name should exit 2 (empty slug): "
    f"exit {e2e_gate_empty_slug.returncode}, stderr {e2e_gate_empty_slug.stderr!r}",
)

e2e_gate_chinese = run_e2e_gate("plan-receipt.chinese-milestone.json", "close-receipt.chinese-milestone.json")
require(
    e2e_gate_chinese.returncode == 0
    and "docs/ship-flow/flows/从派工到一条-slack-消息.yaml" in e2e_gate_chinese.stdout,
    f"e2e-gate Chinese milestone name should derive its Unicode flow path: "
    f"exit {e2e_gate_chinese.returncode}, stdout {e2e_gate_chinese.stdout!r}",
)

# --- DEV-153 AC-1/AC-2: milestone-name mode takes --root and --flows from arguments, never
# from __file__, and refuses a missing flows directory by name rather than "not applicable" ---
e2e_gate_ac1 = subprocess.run(
    [
        sys.executable, str(e2e_gate),
        "--root", "kc-ship-flow/scripts/fixtures/e2e-gate/repo",
        "--flows", "docs/ship/flows",
        "Synthetic gate journey",
    ],
    cwd=ROOT, text=True, capture_output=True, timeout=30,
)
require(
    e2e_gate_ac1.returncode == 0
    and "docs/ship/flows/synthetic-gate-journey.yaml" in e2e_gate_ac1.stdout
    and "not applicable" not in e2e_gate_ac1.stdout,
    f"e2e-gate AC-1 (milestone-name mode, --root/--flows from arguments) failed: "
    f"exit {e2e_gate_ac1.returncode}, stdout {e2e_gate_ac1.stdout!r}, stderr {e2e_gate_ac1.stderr!r}",
)

e2e_gate_ac2_missing_flows = subprocess.run(
    [
        sys.executable, str(e2e_gate),
        "--root", "kc-ship-flow/scripts/fixtures/e2e-gate/repo",
        "--flows", "docs/missing",
        "Synthetic gate journey",
    ],
    cwd=ROOT, text=True, capture_output=True, timeout=30,
)
require(
    e2e_gate_ac2_missing_flows.returncode == 2
    and "flows directory not found" in e2e_gate_ac2_missing_flows.stderr,
    f"e2e-gate AC-2 (missing flows directory should be a named refusal) failed: "
    f"exit {e2e_gate_ac2_missing_flows.returncode}, stderr {e2e_gate_ac2_missing_flows.stderr!r}",
)

run([sys.executable, str(SCRIPTS / "prose-placement-check.py")], "kc-ship-flow prose-placement-check.py")

run(
    [sys.executable, str(SCRIPTS / "local-profile-check.py"), str(ROOT / "docs" / "ship" / "README.md")],
    "kc-ship-flow local-profile-check.py",
)

# DEV-119 repair round 1: local-profile-check.py must refuse a Local Profile table
# missing a required row, and refuse (rather than silently pick) a duplicated
# marker pair, naming which failure it hit. Both run against a temporary copy of
# the real README, never the tracked file itself.
local_profile_check = SCRIPTS / "local-profile-check.py"
ship_readme_path = ROOT / "docs" / "ship" / "README.md"
ship_readme_text = ship_readme_path.read_text(encoding="utf-8")


def run_local_profile_check(contents: str) -> subprocess.CompletedProcess[str]:
    with tempfile.NamedTemporaryFile(
        "w", suffix=".md", delete=False, encoding="utf-8"
    ) as handle:
        handle.write(contents)
        temp_readme = Path(handle.name)
    try:
        return subprocess.run(
            [sys.executable, str(local_profile_check), str(temp_readme)],
            cwd=ROOT, text=True, capture_output=True,
        )
    finally:
        temp_readme.unlink(missing_ok=True)


missing_runtime_text = "\n".join(
    line for line in ship_readme_text.splitlines() if "| Runtime |" not in line
) + "\n"
require(
    missing_runtime_text != ship_readme_text,
    "local-profile-check mutation fixture: no '| Runtime |' row found in docs/ship/README.md",
)
missing_runtime_result = run_local_profile_check(missing_runtime_text)
require(
    missing_runtime_result.returncode != 0
    and "LOCAL_PROFILE_MISSING_ROW: Runtime" in missing_runtime_result.stderr,
    "local-profile-check.py did not refuse a Local Profile table missing the Runtime row, "
    f"naming it: exit={missing_runtime_result.returncode} stderr={missing_runtime_result.stderr!r}",
)

duplicated_marker_text = ship_readme_text + "\n" + ship_readme_text
duplicated_marker_result = run_local_profile_check(duplicated_marker_text)
require(
    duplicated_marker_result.returncode != 0
    and "LOCAL_PROFILE_MARKER_COUNT" in duplicated_marker_result.stderr,
    "local-profile-check.py did not refuse a Local Profile block whose start/end markers are "
    f"duplicated, naming the marker error: exit={duplicated_marker_result.returncode} "
    f"stderr={duplicated_marker_result.stderr!r}",
)

# DEV-117 repair round 1: a placement.tsv row is not "placed" just because its
# destination file exists -- it must also carry that segment's hash marker.
# Repoint one real row to a different real destination that lacks its hash
# and confirm the check refuses (before the fix this mutation stayed exit 0).
prose_placement_check = SCRIPTS / "prose-placement-check.py"
placement_tsv = PLUGIN / "references" / "placement.tsv"
original_placement = placement_tsv.read_text(encoding="utf-8")
mutated_placement = original_placement.replace(
    "d708e82924c7\tkc-ship-flow/references/stations/uat-doc.md",
    "d708e82924c7\tkc-ship-flow/references/stations/e2e-gate.md",
)
require(mutated_placement != original_placement, "prose-placement-check mutation fixture: target row not found in placement.tsv")
try:
    placement_tsv.write_text(mutated_placement, encoding="utf-8")
    mutated_result = subprocess.run(
        [sys.executable, str(prose_placement_check)], cwd=ROOT, text=True, capture_output=True,
    )
finally:
    placement_tsv.write_text(original_placement, encoding="utf-8")
require(
    mutated_result.returncode != 0,
    "prose-placement-check.py did not refuse a row repointed to an unrelated existing "
    f"destination lacking the segment's hash marker: exit={mutated_result.returncode} "
    f"stdout={mutated_result.stdout!r}",
)

# --- DEV-147/DEV-135 (kept behind DEV-157's removal of the per-task debrief
# writer): the close-receipt schema still admits a `note` field on a
# per_issue dev_debrief entry for an issue that was never dispatched --
# hand-built here since no ship-flow script produces this shape anymore ----
carried_issue_id = "DEV-910"
carried_dev_debrief = {
    "per_issue": {
        carried_issue_id: {
            "rounds": 0,
            "evidence_refusals": [],
            "code_refusals": [],
            "note": "not dispatched",
        },
    },
    "candidate_correction": "TBD (FO): one candidate correction to the build contract from this batch's Evidence.",
}
require(
    carried_dev_debrief["per_issue"][carried_issue_id].get("note") == "not dispatched",
    f"batch-carried-issue's writer output must carry a not-dispatched note: {carried_dev_debrief}",
)


def canon(obj: object) -> bytes:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


carried_body = "## The problem\n\nFixture body.\n\n## Accepted outcome\n\nFixture only.\n"
carried_plan_receipt = {
    "schema": "kc-plan-receipt/v1",
    "code_repo": "example-org/example-repo",
    "base_branch": "main",
    "project": {
        "id": "00000000-0000-0000-0000-0000000000a1",
        "name": "Synthetic carried-note contract fixture",
        "user_value": "A writer-produced not-dispatched entry embeds into a close receipt that validates.",
        "hypothesis": "If we let the schema admit `note` then a real not-dispatched debrief output validates unchanged.",
        "wedge": "Fixture only; exercises validate-receipt.py's close-receipt path end to end.",
        "outcome": "One issue closes carried, with a not-dispatched dev_debrief entry.",
        "exit": ["Fixture validates."],
        "outcome_hash": f"sha256:{sha('carried-note-fixture-outcome')}",
    },
    "cycle": "00000000-0000-0000-0000-0000000000a2",
    "milestones": [],
    "issues": {
        carried_issue_id: {
            "id": "00000000-0000-0000-0000-0000000000a3",
            "url": f"https://example.test/issue/{carried_issue_id}",
            "title": carried_issue_id,
            "branch": f"feature/{carried_issue_id.lower()}-synthetic-fixture",
            "close_line": f"Fixes {carried_issue_id}",
            "profile": "pilot-product-slice",
            "milestone": None,
            "body": carried_body,
            "body_sha256": sha(carried_body),
        },
    },
    "edges": [],
    "dispatch_order": [carried_issue_id],
    "lint": {"schema": "kc-plan-lint/v1", "pass": True, "digest": sha("carried-note-fixture-lint")},
    "premises": [
        {"id": "P1", "statement": "Fixture premise: a real not-dispatched debrief entry validates.", "agreed": True},
    ],
    "rationale_sha256": sha("carried-note-fixture-rationale"),
}
carried_plan_receipt["receipt_sha256"] = sha(canon(carried_plan_receipt).decode())

carried_plan_approval = {
    "schema": "kc-plan-approval/v1",
    "receipt_sha256": carried_plan_receipt["receipt_sha256"],
    "approver": "person:captain",
    "approved_at": "2026-09-09T00:00:00Z",
    "decision": "go",
    "max_workspaces": 1,
    "concurrency": 1,
    "repair_rounds": 0,
    "quote": "go, synthetic fixture approval",
    "quote_source": "fixture, not a real approval",
    "defaults": {
        "findings_outside_brief": ["security", "data-loss", "compatibility"],
        "minimal_necessity_fail": "accepted_no_pr",
        "moved_base": "rebase_and_accept",
        "worker_blocker": "skip_issue_continue_batch",
        "empty_reviewer": "fallback_to_fo_diff_read",
        "pr_creation": "batch_approve_draft",
    },
}

carried_close_receipt = {
    "schema": "kc-ship-close-receipt/v1",
    "plan_receipt_sha256": carried_plan_receipt["receipt_sha256"],
    "approval_receipt_sha256": sha(canon(carried_plan_approval).decode()),
    "batch": {
        "entity": "batch-carried-note-contract",
        "started_at": "2026-09-09T00:00:00Z",
        "closed_at": "2026-09-09T00:05:00Z",
        "holder": "laptop",
    },
    "issues": {
        carried_issue_id: {
            "outcome": "carried",
            "candidate": None,
            "pr": None,
            "rounds": 0,
            "minutes": {"dispatch": 0},
        },
    },
    "defects_returned": [],
    "totals": {"workspaces_created": 0, "workspaces_orphaned": 0, "fix_rounds": 0, "captain_gates": 0},
    "dev_debrief": carried_dev_debrief,
    "ship_debrief": {
        "defaults_decisions": [],
        "defects_disposition": [],
        "minutes_per_station": {"dispatch": 0},
        "candidate_correction": "TBD (FO): one candidate correction to ship-flow from this batch.",
    },
}
carried_close_receipt["close_sha256"] = sha(canon(carried_close_receipt).decode())

validate_receipt_script = ROOT / "docs" / "plan-flow" / "schema" / "validate-receipt.py"

with tempfile.TemporaryDirectory(prefix="kc-ship-flow-carried-note-") as carried_dir_name:
    carried_dir = Path(carried_dir_name)
    (carried_dir / "plan-receipt.json").write_text(json.dumps(carried_plan_receipt), encoding="utf-8")
    (carried_dir / "plan-approval.json").write_text(json.dumps(carried_plan_approval), encoding="utf-8")
    (carried_dir / "close-receipt.json").write_text(json.dumps(carried_close_receipt), encoding="utf-8")
    carried_note_result = subprocess.run(
        [
            sys.executable, str(validate_receipt_script),
            str(carried_dir / "plan-receipt.json"),
            str(carried_dir / "plan-approval.json"),
            str(carried_dir / "close-receipt.json"),
        ],
        capture_output=True, text=True,
    )
    require(
        carried_note_result.returncode == 0 and "CLOSE OK" in carried_note_result.stdout,
        "validate-receipt.py did not accept a close receipt embedding a real "
        f"not-dispatched debrief output: exit={carried_note_result.returncode} "
        f"stdout={carried_note_result.stdout!r} stderr={carried_note_result.stderr!r}",
    )
close_receipt_fixtures = FIXTURES / "close-receipt"
forbidden_embed_result = subprocess.run(
    [
        sys.executable, str(validate_receipt_script),
        str(close_receipt_fixtures / "plan-receipt.json"),
        str(close_receipt_fixtures / "plan-approval.json"),
        str(close_receipt_fixtures / "close-receipt.debrief-wrapper-embedded.json"),
    ],
    capture_output=True, text=True,
)
require(
    forbidden_embed_result.returncode == 1 and "dev_debrief" in forbidden_embed_result.stdout,
    "validate-receipt.py did not refuse a close receipt whose dev_debrief embeds the writer's own "
    f"wrapper keys: exit={forbidden_embed_result.returncode} stdout={forbidden_embed_result.stdout!r}",
)

print("kc-ship-flow contract: PASS")
