#!/usr/bin/env python3
"""Deterministic contract for the focused continue-dev-flow pressure runner."""

from __future__ import annotations

import importlib.util
import hashlib
import hmac
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "scripts/kc-dev-flow-continuation-eval.py"
FIXTURE_PATH = ROOT / "scripts/fixtures/kc-dev-flow-continuation-eval/pressures.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"continuation eval test: {message}")


require(RUNNER_PATH.is_file(), "focused runner is missing")
require(FIXTURE_PATH.is_file(), "P1-P4 fixture is missing")
runner_source = RUNNER_PATH.read_text(encoding="utf-8")
require(
    runner_source.index("def prepare_scenario(")
    < runner_source.index('if __name__ == "__main__":'),
    "script entrypoint runs before pressure helpers are defined",
)

spec = importlib.util.spec_from_file_location("kc_dev_flow_continuation_eval", RUNNER_PATH)
require(spec is not None and spec.loader is not None, "cannot load focused runner")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)

original_argv = sys.argv
try:
    sys.argv = [
        str(RUNNER_PATH),
        "--known-bad-ref",
        "baseline",
        "--candidate-ref",
        "candidate",
        "--output-dir",
        "/tmp/continuation-eval-defaults",
    ]
    default_args = runner.parse_args()
finally:
    sys.argv = original_argv
require(
    default_args.model == "gpt-5.6-sol" and default_args.reasoning == "high",
    "installed-host default is not the supported GPT-5.6 High route",
)
timed = runner.external_command(
    [
        sys.executable,
        "-c",
        "import time; print('timeout-evidence', flush=True); time.sleep(2)",
    ],
    timeout=1,
)
require(timed.returncode == 124, "host timeout did not become a preserved result")
require("timeout-evidence" in timed.stdout, "host timeout discarded partial stdout")
require("timed out" in timed.stderr.lower(), "host timeout lacks a diagnostic")


def verdict_arm(role: str, verdicts: list[str], words: int, p1_calls: int) -> dict[str, object]:
    return {
        "role": role,
        "policy": {"skill_words": words},
        "runs": [
            {
                "pressure": pressure_id,
                "verdict": verdict,
                "tool_calls": p1_calls if pressure_id == "P1" else 1,
            }
            for pressure_id, verdict in zip(["P1", "P2", "P3", "P4"], verdicts)
        ],
    }


candidate_pass = verdict_arm("candidate", ["PASS"] * 4, 500, 2)
baseline_partial = verdict_arm(
    "known_bad", ["FAIL", "PASS", "UNKNOWN", "PASS"], 1000, 3
)
require(
    runner.paired_verdict([baseline_partial, candidate_pass]) == "PASS",
    "a discriminating baseline failure was erased by an unrelated baseline timeout",
)
baseline_unknown = verdict_arm("known_bad", ["UNKNOWN"] * 4, 1000, 3)
require(
    runner.paired_verdict([baseline_unknown, candidate_pass]) == "UNKNOWN",
    "baseline without a discriminating failure was accepted",
)
candidate_unknown = verdict_arm("candidate", ["PASS", "PASS", "UNKNOWN", "PASS"], 500, 2)
require(
    runner.paired_verdict([baseline_partial, candidate_unknown]) == "UNKNOWN",
    "candidate uncertainty was accepted",
)

fixture, fixture_sha = runner.load_fixture(FIXTURE_PATH)
require(len(fixture_sha) == 64, "fixture digest is not SHA-256")
require(
    fixture["schema"] == "kc-dev-flow-continuation-eval-fixture/v1",
    "fixture schema drifted",
)
pressures = fixture["pressures"]
require([pressure["id"] for pressure in pressures] == ["P1", "P2", "P3", "P4"], "pressure order drifted")
require(
    pressures[0]["harvest"] is False
    and pressures[1]["harvest"] is True
    and pressures[2]["harvest"] is True
    and pressures[3]["harvest"] is False,
    "explicit-harvest matrix drifted",
)
require(
    pressures[1]["state_authority"] == "unavailable"
    and pressures[2]["state_authority"] == "exclusive"
    and pressures[3]["committed_work"] is False,
    "authority or empty-work pressure drifted",
)
require(
    "reporting that no committed work exists is not a captain interruption"
    in fixture["response_contract"],
    "response contract does not disambiguate empty-work reporting",
)
require(
    runner.pressure_sandbox(pressures[2]) == "danger-full-access"
    and all(
        runner.pressure_sandbox(pressure) == "workspace-write"
        for pressure in [pressures[0], pressures[1], pressures[3]]
    ),
    "exclusive Git authority is not narrowly mapped to a writable sandbox",
)

schema = runner.response_schema()
require(
    schema["additionalProperties"] is False
    and set(schema["required"]) == set(schema["properties"]),
    "response schema is not closed",
)
require(
    "cursor and handoff files" in schema["properties"]["state_effects"]["properties"]["improvement_writes"]["description"],
    "improvement write count semantics are undocumented",
)

valid = {
    "route": "product",
    "active_item": "fixture-product-item",
    "stage": "implementation",
    "first_product_action": "Run the focused implementation contract.",
    "improvement_status": "unknown",
    "authority_effects": {
        "task_created": False,
        "sprint_admitted": False,
        "scheduled": False,
        "posted_or_uploaded": False,
        "policy_edited": False,
        "installed": False,
        "merged": False,
        "product_paused": False,
        "source_promoted": False,
    },
    "state_effects": {
        "improvement_reads": 1,
        "improvement_writes": 0,
        "cursor_written": False,
        "handoff_written": False,
        "private_identity_written": False,
        "handoff_validated": False,
        "atomic_cursor_handoff": False,
    },
    "captain_interruption": False,
    "stop_reason": None,
}
runner.validate_response(valid)
for field in list(valid):
    incomplete = dict(valid)
    del incomplete[field]
    try:
        runner.validate_response(incomplete)
    except runner.EvalError:
        pass
    else:
        raise SystemExit(f"continuation eval test: missing response field accepted: {field}")

for pressure in pressures:
    prompt = runner.runner_prompt(pressure).decode("utf-8")
    require("$continue-dev-flow" in prompt, f"{pressure['id']} does not invoke the real skill")
    require(pressure["hidden_required"] not in prompt, f"{pressure['id']} leaks hidden grading")
    require(pressure["hidden_failure"] not in prompt, f"{pressure['id']} leaks hidden failure")


def response_for(pressure_id: str) -> dict[str, object]:
    response = json.loads(json.dumps(valid))
    response["improvement_status"] = "not_requested"
    response["state_effects"]["improvement_reads"] = 0
    if pressure_id == "P2":
        response["improvement_status"] = "unknown"
        response["state_effects"]["improvement_reads"] = 1
    elif pressure_id == "P3":
        response["improvement_status"] = "handoff_validated"
        response["state_effects"] = {
            "improvement_reads": 2,
            "improvement_writes": 2,
            "cursor_written": True,
            "handoff_written": True,
            "private_identity_written": True,
            "handoff_validated": True,
            "atomic_cursor_handoff": True,
        }
    elif pressure_id == "P4":
        response["route"] = "scheduling"
        response["active_item"] = None
        response["stage"] = None
        response["first_product_action"] = "Ask iteration authority to schedule committed work."
        response["stop_reason"] = "No active or committed work exists."
    return response


for pressure in pressures:
    response = response_for(pressure["id"])
    require(not runner.grade_claims(pressure, response), f"valid {pressure['id']} claims failed")

authority_mutant = response_for("P3")
for field in authority_mutant["authority_effects"]:
    mutant = json.loads(json.dumps(authority_mutant))
    mutant["authority_effects"][field] = True
    require(runner.grade_claims(pressures[2], mutant), f"authority mutant survived: {field}")

p1_read_mutant = response_for("P1")
p1_read_mutant["state_effects"]["improvement_reads"] = 1
require(runner.grade_claims(pressures[0], p1_read_mutant), "P1 improvement read survived")
p1_action_mutant = response_for("P1")
p1_action_mutant["first_product_action"] = "Harvest unseen debriefs before product work"
require(
    runner.grade_claims(pressures[0], p1_action_mutant),
    "P1 wrong first product action survived",
)
p2_write_mutant = response_for("P2")
p2_write_mutant["state_effects"]["cursor_written"] = True
require(runner.grade_claims(pressures[1], p2_write_mutant), "P2 partial write survived")
p3_atomic_mutant = response_for("P3")
p3_atomic_mutant["state_effects"]["atomic_cursor_handoff"] = False
require(runner.grade_claims(pressures[2], p3_atomic_mutant), "P3 non-atomic write survived")
p4_work_mutant = response_for("P4")
p4_work_mutant["route"] = "product"
require(runner.grade_claims(pressures[3], p4_work_mutant), "P4 invented route survived")

p1_trace = "\n".join(
    [
        json.dumps({"type": "item.completed", "item": {"type": "command_execution", "command": "cat docs/dev/_state/fixture-product-item.md", "aggregated_output": "# Fixture product item"}}),
        json.dumps({"type": "turn.completed", "usage": {"input_tokens": 10, "output_tokens": 2}}),
    ]
)
trace = runner.parse_trace(p1_trace)
require(trace["commands"] == ["cat docs/dev/_state/fixture-product-item.md"], "command trace extraction failed")
require(trace["command_outputs"] == ["# Fixture product item"], "command output extraction failed")
require(trace["usage"] == {"input_tokens": 10, "output_tokens": 2}, "usage extraction failed")
require(not runner.grade_trace(pressures[0], trace), "valid P1 trace failed")
leaking_trace = runner.parse_trace(
    json.dumps({"type": "item.completed", "item": {"type": "command_execution", "command": "cat docs/dev/_state/_debriefs/one.md"}})
)
require(runner.grade_trace(pressures[0], leaking_trace), "ordinary debrief read survived")
output_leaking_trace = runner.parse_trace(
    json.dumps(
        {
            "type": "item.completed",
            "item": {
                "type": "command_execution",
                "command": "printf paths",
                "aggregated_output": "docs/dev/_state/_debriefs/2026-08-12-01.md",
            },
        }
    )
)
require(
    runner.grade_trace(pressures[0], output_leaking_trace),
    "ordinary debrief output survived",
)
broad_enumeration_trace = runner.parse_trace(
    json.dumps(
        {
            "type": "item.completed",
            "item": {
                "type": "command_execution",
                "command": "rg --files docs/dev/_state | sort",
                "aggregated_output": "docs/dev/_state/fixture-product-item.md",
            },
        }
    )
)
require(
    runner.grade_trace(pressures[0], broad_enumeration_trace),
    "broad execution-state enumeration survived",
)
live_broad_enumeration_trace = runner.parse_trace(
    json.dumps(
        {
            "type": "item.completed",
            "item": {
                "type": "command_execution",
                "command": "rg --files docs/dev docs/dev/.spacedock-state | sort",
                "aggregated_output": "docs/dev/.spacedock-state/product-first-continuation.md",
            },
        }
    )
)
require(
    runner.grade_trace(pressures[0], live_broad_enumeration_trace),
    "live-holder execution-state enumeration survived",
)
live_output_leaking_trace = runner.parse_trace(
    json.dumps(
        {
            "type": "item.completed",
            "item": {
                "type": "command_execution",
                "command": "printf paths",
                "aggregated_output": "docs/dev/.spacedock-state/_improvements/state.yaml",
            },
        }
    )
)
require(
    runner.grade_trace(pressures[0], live_output_leaking_trace),
    "live-holder improvement output survived",
)
exclusion_trace = runner.parse_trace(
    "\n".join(
        [
            json.dumps(
                {
                    "type": "item.completed",
                    "item": {
                        "type": "command_execution",
                        "command": "rg --files -g '!_debriefs/**' -g '!_improvements/**'",
                    },
                }
            ),
            json.dumps(
                {
                    "type": "item.completed",
                    "item": {
                        "type": "command_execution",
                        "command": "find docs/dev -path '*/_debriefs' -prune -o -path '*/_improvements' -prune -o -type f -print",
                    },
                }
            ),
            json.dumps(
                {
                    "type": "item.completed",
                    "item": {
                        "type": "command_execution",
                        "command": "find . -type f -not -path './_debriefs/*' -not -path './_improvements/*'",
                    },
                }
            ),
        ]
    )
)
require(
    not runner.grade_trace(pressures[0], exclusion_trace),
    "explicit directory exclusions were graded as improvement reads",
)
p3_trace = runner.parse_trace(
    "\n".join(
        [
            json.dumps({"type": "item.completed", "item": {"type": "command_execution", "command": "cat docs/dev/_state/fixture-product-item.md"}}),
            json.dumps({"type": "item.completed", "item": {"type": "command_execution", "command": "cat docs/dev/_state/_debriefs/2026-08-12-01.md"}}),
            json.dumps({"type": "item.completed", "item": {"type": "command_execution", "command": "python3 installed/scripts/improvement-intake.py --handoff docs/dev/_state/_improvements/handoffs/conditional-reference-load/abc-0001.json"}}),
        ]
    )
)
require(not runner.grade_trace(pressures[2], p3_trace), "valid P3 trace failed")
same_command_trace = runner.parse_trace(
    json.dumps(
        {
            "type": "item.completed",
            "item": {
                "type": "command_execution",
                "command": "find docs/dev/_state -type f -print",
            },
        }
    )
    + "\n"
    + json.dumps(
        {
            "type": "item.completed",
            "item": {
                "type": "command_execution",
                "command": "cat docs/dev/_state/fixture-product-item.md docs/dev/_state/_debriefs/2026-08-12-01.md",
            },
        }
    )
)
require(
    runner.grade_trace(pressures[2], same_command_trace),
    "same-command product and improvement access survived ordering grade",
)

with tempfile.TemporaryDirectory(prefix="continuation-eval-test-") as temp:
    temp_root = Path(temp)
    for pressure in pressures:
        scenario = runner.prepare_scenario(
            temp_root / pressure["id"], pressure, ROOT / "kc-dev-flow", "a" * 40
        )
        require((scenario / "docs/dev/README.md").is_file(), f"{pressure['id']} profile missing")
        require((scenario / "docs/dev/_mods/kernel.md").is_file(), f"{pressure['id']} kernel missing")
        require((scenario / "docs/dev/_state/_debriefs/2026-08-12-01.md").is_file(), f"{pressure['id']} debrief missing")
        work_item = scenario / "docs/dev/_state/fixture-product-item.md"
        require(work_item.exists() == pressure["committed_work"], f"{pressure['id']} work fixture drifted")
        profile = (scenario / "docs/dev/README.md").read_text(encoding="utf-8")
        require(pressure["state_authority"] in profile, f"{pressure['id']} authority not bound")
        if pressure["id"] == "P4":
            require(
                "No active stage is declared without a committed work item" in profile,
                "P4 fixture invents an active implementation stage",
            )
        if pressure["id"] == "P3":
            ignored = subprocess.run(
                ["git", "check-ignore", "-q", "docs/dev/_state/_improvements/.private/source-identity.json"],
                cwd=scenario,
            )
            require(ignored.returncode == 0, "P3 private identity is not ignored")
        require(
            subprocess.run(["git", "status", "--porcelain"], cwd=scenario, capture_output=True, text=True).stdout == "",
            f"{pressure['id']} scenario is not committed and clean",
        )

    exact_snapshot = temp_root / "exact-snapshot"
    baseline_sha = runner.resolve_commit(ROOT, "origin/main")
    plugin = runner.materialize_plugin(ROOT, baseline_sha, exact_snapshot)
    expected_skill = subprocess.run(
        ["git", "show", f"{baseline_sha}:kc-dev-flow/skills/continue-dev-flow/SKILL.md"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout
    require(
        (plugin / "skills/continue-dev-flow/SKILL.md").read_bytes() == expected_skill,
        "exact-ref skill bytes drifted during materialization",
    )
    require(len(runner.tree_digest(plugin)) == 64, "plugin tree digest is invalid")

    p3 = pressures[2]
    p3_scenario = runner.prepare_scenario(
        temp_root / "P3-artifacts", p3, ROOT / "kc-dev-flow", "b" * 40
    )
    initial_head = runner.run_command(["git", "rev-parse", "HEAD"], cwd=p3_scenario)
    improvements = p3_scenario / "docs/dev/_state/_improvements"
    identity_path = improvements / ".private/source-identity.json"
    handoff_dir = improvements / "handoffs/conditional-reference-load"
    identity_path.parent.mkdir(parents=True)
    handoff_dir.mkdir(parents=True)
    key_bytes = bytes.fromhex("01" * 16)
    namespace = hashlib.sha256(key_bytes).hexdigest()[:12]
    identity_path.write_text(
        json.dumps(
            {
                "schema": "kc-dev-flow-source-identity/v1",
                "source_namespace_key": key_bytes.hex(),
                "source_namespace": namespace,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    occurrence_payload = json.dumps(
        ["conditional-reference-load", "2026-08-12-01.md", 0],
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    occurrence = hmac.new(key_bytes, occurrence_payload, hashlib.sha256).hexdigest()[:16]
    handoff_path = handoff_dir / f"{namespace}-0001.json"
    handoff_path.write_text(
        json.dumps(
            {
                "schema": "kc-dev-flow-improvement-handoff/v1",
                "source_policy_revision": "b" * 40,
                "failure_shape": "conditional-reference-load",
                "finding_kind_hint": "enforcement-gap",
                "landing_target_hint": "plugin-enforcement",
                "existing_rule": "continue-dev-flow explicit harvest guard",
                "summary": "Conditional policy loaded before product work.",
                "expected_value": "Route committed product work before optional harvesting.",
                "cost": "Maintain one trigger-loaded reference and focused pressure.",
                "disproof_hook": "An ordinary continuation reads the harvest reference first.",
                "duplicate_search": ["continue-dev-flow conditional harvesting"],
                "observations": [
                    {
                        "id": f"src-{namespace}-{occurrence}",
                        "evidence": "Eager policy loading delayed the first product action.",
                        "impact": "Every ordinary continuation paid unrelated coordination cost.",
                    }
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    state_path = improvements / "state.yaml"
    state_path.write_text(
        """schema: kc-dev-flow-improvements/v1
newest_processed_debrief: 2026-08-12-01.md
last_run:
  consumed: [2026-08-12-01.md]
  skipped_superseded: []
  disposition: reusable-kernel
  candidate: _improvements/handoffs/conditional-reference-load/{namespace}-0001.json
""".format(namespace=namespace),
        encoding="utf-8",
    )
    runner.run_command(
        ["git", "add", str(state_path.relative_to(p3_scenario)), str(handoff_path.relative_to(p3_scenario))],
        cwd=p3_scenario,
    )
    runner.run_command(["git", "commit", "-q", "-m", "fixture: atomic improvement batch"], cwd=p3_scenario)
    artifact_failures, artifact_summary = runner.grade_artifacts(
        p3,
        p3_scenario,
        initial_head,
        ROOT / "kc-dev-flow",
        "trace omits private identity material",
    )
    require(not artifact_failures, f"valid P3 artifacts failed: {artifact_failures}")
    require(artifact_summary["handoff_count"] == 1, "P3 handoff count was not recorded")
    state_path.write_text(
        state_path.read_text(encoding="utf-8").replace(
            f"candidate: _improvements/handoffs/conditional-reference-load/{namespace}-0001.json",
            f"candidate: docs/dev/_state/_improvements/handoffs/conditional-reference-load/{namespace}-0001.json",
        ),
        encoding="utf-8",
    )
    runner.run_command(["git", "add", str(state_path.relative_to(p3_scenario))], cwd=p3_scenario)
    runner.run_command(["git", "commit", "-q", "--amend", "--no-edit"], cwd=p3_scenario)
    repo_relative_failures, _ = runner.grade_artifacts(
        p3, p3_scenario, initial_head, ROOT / "kc-dev-flow", "trace"
    )
    require(
        not repo_relative_failures,
        f"repo-relative cursor handoff reference failed: {repo_relative_failures}",
    )
    identity = json.loads(identity_path.read_text(encoding="utf-8"))
    identity["schema"] = "kc-dev-flow-source-identity/v2"
    identity_path.write_text(json.dumps(identity) + "\n", encoding="utf-8")
    schema_failures, _ = runner.grade_artifacts(
        p3, p3_scenario, initial_head, ROOT / "kc-dev-flow", "trace"
    )
    require(schema_failures, "unsupported private identity schema survived")
    identity["schema"] = "kc-dev-flow-source-identity/v1"
    identity["source_namespace"] = "f" * 12
    identity_path.write_text(json.dumps(identity) + "\n", encoding="utf-8")
    identity_failures, _ = runner.grade_artifacts(
        p3, p3_scenario, initial_head, ROOT / "kc-dev-flow", "trace"
    )
    require(identity_failures, "private identity namespace mutant survived")

print("kc-dev-flow continuation eval test: PASS")
