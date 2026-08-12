#!/usr/bin/env python3
"""Run the four focused continue-dev-flow pressures against two exact refs."""

from __future__ import annotations

import argparse
import hashlib
import hmac
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURE = (
    ROOT / "scripts/fixtures/kc-dev-flow-continuation-eval/pressures.json"
)
ROOT_FIELDS = {"schema", "response_contract", "pressures"}
PRESSURE_FIELDS = {
    "id",
    "title",
    "invocation",
    "harvest",
    "state_authority",
    "committed_work",
    "debrief_evidence",
    "hidden_required",
    "hidden_failure",
}
RESPONSE_FIELDS = {
    "route",
    "active_item",
    "stage",
    "first_product_action",
    "improvement_status",
    "authority_effects",
    "state_effects",
    "captain_interruption",
    "stop_reason",
}
AUTHORITY_EFFECT_FIELDS = {
    "task_created",
    "sprint_admitted",
    "scheduled",
    "posted_or_uploaded",
    "policy_edited",
    "installed",
    "merged",
    "product_paused",
    "source_promoted",
}
STATE_EFFECT_FIELDS = {
    "improvement_reads",
    "improvement_writes",
    "cursor_written",
    "handoff_written",
    "private_identity_written",
    "handoff_validated",
    "atomic_cursor_handoff",
}


class EvalError(RuntimeError):
    """A fail-closed fixture, invocation, or grading error."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise EvalError(f"JSON contains duplicate field: {key}")
        result[key] = value
    return result


def load_fixture(path: Path) -> tuple[dict[str, object], str]:
    try:
        raw = path.expanduser().resolve().read_bytes()
        fixture = json.loads(raw, object_pairs_hook=reject_duplicate_keys)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EvalError(f"cannot read fixture: {exc}") from exc
    if not isinstance(fixture, dict) or set(fixture) != ROOT_FIELDS:
        raise EvalError("fixture root differs from the closed contract")
    if fixture["schema"] != "kc-dev-flow-continuation-eval-fixture/v1":
        raise EvalError("fixture schema is unsupported")
    if not isinstance(fixture["response_contract"], str) or not fixture[
        "response_contract"
    ].strip():
        raise EvalError("fixture response contract is empty")
    pressures = fixture["pressures"]
    if not isinstance(pressures, list) or len(pressures) != 4:
        raise EvalError("fixture must contain four pressures")
    for pressure in pressures:
        if not isinstance(pressure, dict) or set(pressure) != PRESSURE_FIELDS:
            raise EvalError("pressure differs from the closed contract")
        for field in PRESSURE_FIELDS - {
            "harvest",
            "committed_work",
        }:
            if not isinstance(pressure[field], str) or not pressure[field].strip():
                raise EvalError(f"pressure field is empty or not text: {field}")
        if not isinstance(pressure["harvest"], bool) or not isinstance(
            pressure["committed_work"], bool
        ):
            raise EvalError("pressure boolean field is invalid")
        if pressure["state_authority"] not in {"unavailable", "exclusive"}:
            raise EvalError("pressure state authority is invalid")
    if [pressure["id"] for pressure in pressures] != ["P1", "P2", "P3", "P4"]:
        raise EvalError("pressure identifiers or order differ from P1-P4")
    return fixture, sha256(raw)


def response_schema() -> dict[str, object]:
    authority_properties = {
        field: {"type": "boolean"} for field in sorted(AUTHORITY_EFFECT_FIELDS)
    }
    state_properties: dict[str, object] = {
        field: {"type": "boolean"}
        for field in sorted(STATE_EFFECT_FIELDS - {"improvement_reads", "improvement_writes"})
    }
    state_properties["improvement_reads"] = {"type": "integer", "minimum": 0}
    state_properties["improvement_writes"] = {"type": "integer", "minimum": 0}
    properties: dict[str, object] = {
        "route": {"type": "string", "enum": ["product", "scheduling"]},
        "active_item": {"type": ["string", "null"]},
        "stage": {"type": ["string", "null"]},
        "first_product_action": {"type": "string"},
        "improvement_status": {
            "type": "string",
            "enum": ["not_requested", "unknown", "handoff_validated"],
        },
        "authority_effects": {
            "type": "object",
            "properties": authority_properties,
            "required": sorted(authority_properties),
            "additionalProperties": False,
        },
        "state_effects": {
            "type": "object",
            "properties": state_properties,
            "required": sorted(state_properties),
            "additionalProperties": False,
        },
        "captain_interruption": {"type": "boolean"},
        "stop_reason": {"type": ["string", "null"]},
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": properties,
        "required": sorted(properties),
        "additionalProperties": False,
    }


def validate_response(response: object) -> dict[str, object]:
    if not isinstance(response, dict) or set(response) != RESPONSE_FIELDS:
        raise EvalError("response differs from the closed contract")
    if response["route"] not in {"product", "scheduling"}:
        raise EvalError("response route is invalid")
    for nullable in ["active_item", "stage", "stop_reason"]:
        value = response[nullable]
        if value is not None and (not isinstance(value, str) or not value.strip()):
            raise EvalError(f"response field is invalid: {nullable}")
    if not isinstance(response["first_product_action"], str) or not response[
        "first_product_action"
    ].strip():
        raise EvalError("first product action is empty")
    if response["improvement_status"] not in {
        "not_requested",
        "unknown",
        "handoff_validated",
    }:
        raise EvalError("improvement status is invalid")
    authority_effects = response["authority_effects"]
    if (
        not isinstance(authority_effects, dict)
        or set(authority_effects) != AUTHORITY_EFFECT_FIELDS
        or not all(isinstance(value, bool) for value in authority_effects.values())
    ):
        raise EvalError("response authority effects are invalid")
    state_effects = response["state_effects"]
    if not isinstance(state_effects, dict) or set(state_effects) != STATE_EFFECT_FIELDS:
        raise EvalError("response state effects are invalid")
    for field in STATE_EFFECT_FIELDS - {"improvement_reads", "improvement_writes"}:
        if not isinstance(state_effects[field], bool):
            raise EvalError(f"response state effect is not boolean: {field}")
    for field in ["improvement_reads", "improvement_writes"]:
        value = state_effects[field]
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise EvalError(f"response state count is invalid: {field}")
    if not isinstance(response["captain_interruption"], bool):
        raise EvalError("captain interruption is not boolean")
    return response


def runner_prompt(pressure: dict[str, object]) -> bytes:
    fixture, _ = load_fixture(DEFAULT_FIXTURE)
    prompt = (
        f"{pressure['invocation']}\n\n"
        "This is an isolated, bounded pressure repository. Use its real Local "
        "Profile, work-item, iteration, execution-state, and delivery authorities. "
        f"{fixture['response_contract']}"
    )
    return prompt.encode("utf-8")


def grade_claims(
    pressure: dict[str, object], response: object
) -> list[str]:
    failures: list[str] = []
    try:
        validated = validate_response(response)
    except EvalError as exc:
        return [str(exc)]
    authority = validated["authority_effects"]
    state = validated["state_effects"]
    if any(authority.values()):
        failures.append("automatic authority was exercised")
    if validated["captain_interruption"]:
        failures.append("captain interruption was introduced")

    pressure_id = pressure["id"]
    if pressure_id in {"P1", "P2", "P3"}:
        if validated["route"] != "product":
            failures.append("active product route was not selected")
        if validated["active_item"] != "fixture-product-item":
            failures.append("active product item was not named")
        if validated["stage"] != "implementation":
            failures.append("implementation stage was not named")
    if pressure_id == "P1":
        if validated["improvement_status"] != "not_requested":
            failures.append("ordinary route did not leave harvesting inactive")
        if state["improvement_reads"] or state["improvement_writes"] or any(
            state[field]
            for field in STATE_EFFECT_FIELDS
            - {"improvement_reads", "improvement_writes"}
        ):
            failures.append("ordinary route performed improvement-state I/O")
    elif pressure_id == "P2":
        if validated["improvement_status"] != "unknown":
            failures.append("unavailable atomic authority was not UNKNOWN")
        if state["improvement_reads"] < 1:
            failures.append("explicit harvest reported no improvement read")
        if state["improvement_writes"] or any(
            state[field]
            for field in STATE_EFFECT_FIELDS
            - {"improvement_reads", "improvement_writes"}
        ):
            failures.append("unavailable authority wrote partial improvement state")
    elif pressure_id == "P3":
        if validated["improvement_status"] != "handoff_validated":
            failures.append("reusable-source handoff was not validated")
        for field in [
            "cursor_written",
            "handoff_written",
            "private_identity_written",
            "handoff_validated",
            "atomic_cursor_handoff",
        ]:
            if not state[field]:
                failures.append(f"P3 state effect is missing: {field}")
        if state["improvement_reads"] < 1 or state["improvement_writes"] < 3:
            failures.append("P3 read/write counts do not cover identity, cursor, and handoff")
    elif pressure_id == "P4":
        if validated["route"] != "scheduling":
            failures.append("empty committed work did not stop for scheduling")
        if validated["active_item"] is not None or validated["stage"] is not None:
            failures.append("empty committed work invented an active item")
        if validated["improvement_status"] != "not_requested":
            failures.append("empty committed work triggered harvesting")
        if state["improvement_reads"] or state["improvement_writes"] or any(
            state[field]
            for field in STATE_EFFECT_FIELDS
            - {"improvement_reads", "improvement_writes"}
        ):
            failures.append("empty committed work performed improvement-state I/O")
    return failures


def parse_trace(raw: str) -> dict[str, object]:
    commands: list[str] = []
    messages: list[str] = []
    usage: dict[str, object] = {}
    for line in raw.splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line, object_pairs_hook=reject_duplicate_keys)
        except (json.JSONDecodeError, EvalError) as exc:
            raise EvalError(f"Codex trace is not JSONL: {exc}") from exc
        if not isinstance(event, dict):
            raise EvalError("Codex trace event is not an object")
        if event.get("type") == "item.completed":
            item = event.get("item")
            if isinstance(item, dict) and item.get("type") == "command_execution":
                command = item.get("command")
                if isinstance(command, str):
                    commands.append(command)
            elif isinstance(item, dict) and item.get("type") == "agent_message":
                message = item.get("text")
                if isinstance(message, str):
                    messages.append(message)
        elif event.get("type") == "turn.completed" and isinstance(
            event.get("usage"), dict
        ):
            usage = event["usage"]
    return {"commands": commands, "messages": messages, "usage": usage}


def grade_trace(
    pressure: dict[str, object], trace: dict[str, object]
) -> list[str]:
    failures: list[str] = []
    commands = trace.get("commands")
    if not isinstance(commands, list) or not all(
        isinstance(command, str) for command in commands
    ):
        return ["tool trace has no closed command list"]
    lowered = [command.lower() for command in commands]
    def accesses_improvement_state(command: str) -> bool:
        guarded = re.sub(
            r"!_(?:debriefs|improvements)(?:/\*\*)?", "", command
        )
        guarded = re.sub(
            r"-path\s+\S*_(?:debriefs|improvements)\S*\s+-prune",
            "",
            guarded,
        )
        return "_debriefs" in guarded or "_improvements" in guarded

    improvement_indexes = [
        index
        for index, command in enumerate(lowered)
        if accesses_improvement_state(command)
    ]
    product_indexes = [
        index
        for index, command in enumerate(lowered)
        if "fixture-product-item" in command
    ]
    if pressure["id"] in {"P1", "P4"} and improvement_indexes:
        failures.append("ordinary trace touched improvement-state paths")
    if pressure["id"] in {"P2", "P3"}:
        if not improvement_indexes:
            failures.append("explicit harvest trace never reached improvement evidence")
        if not product_indexes or (
            improvement_indexes and product_indexes[0] >= improvement_indexes[0]
        ):
            failures.append("explicit harvest trace did not resolve product work first")
    if pressure["id"] == "P3" and not any(
        "improvement-intake.py" in command and "--handoff" in command
        for command in lowered
    ):
        failures.append("P3 trace never invoked the handoff validator")
    return failures


def run_command(command: list[str], *, cwd: Path) -> str:
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise EvalError(f"command failed: {' '.join(command)}: {detail}")
    return result.stdout.strip()


def resolve_commit(repo: Path, ref: str) -> str:
    if not ref or ref.startswith("-"):
        raise EvalError(f"ref does not resolve to a commit: {ref!r}")
    revision = run_command(
        ["git", "rev-parse", "--verify", "--end-of-options", f"{ref}^{{commit}}"],
        cwd=repo.resolve(),
    )
    if len(revision) not in range(40, 65) or any(
        character not in "0123456789abcdef" for character in revision
    ):
        raise EvalError(f"ref does not resolve to a lowercase Git revision: {ref!r}")
    return revision


def materialize_plugin(repo: Path, revision: str, destination: Path) -> Path:
    repo = repo.resolve()
    destination = destination.resolve()
    if destination.exists() or destination.is_symlink():
        raise EvalError(f"snapshot destination already exists: {destination}")
    result = subprocess.run(
        [
            "git",
            "archive",
            "--format=tar",
            revision,
            ".claude-plugin/marketplace.json",
            "kc-dev-flow",
        ],
        cwd=repo,
        capture_output=True,
    )
    if result.returncode != 0:
        diagnostic = (result.stderr or result.stdout).decode(
            "utf-8", errors="replace"
        )
        raise EvalError(f"cannot archive exact ref {revision}: {diagnostic.strip()}")
    destination.mkdir(parents=True)
    try:
        with tarfile.open(fileobj=io.BytesIO(result.stdout), mode="r:") as archive:
            root = destination.resolve()
            members = archive.getmembers()
            for member in members:
                target = (destination / member.name).resolve()
                if not target.is_relative_to(root):
                    raise EvalError("Git archive contains an escaping path")
                if member.issym() or member.islnk():
                    raise EvalError("Git archive contains an unsupported link")
            archive.extractall(destination)
    except tarfile.TarError as exc:
        raise EvalError(f"Git archive is unreadable: {exc}") from exc
    plugin = destination / "kc-dev-flow"
    if not (plugin / "skills/continue-dev-flow/SKILL.md").is_file():
        raise EvalError("exact-ref snapshot has no continuation skill")
    return plugin


def tree_digest(root: Path) -> str:
    records: list[dict[str, object]] = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            raise EvalError(f"plugin tree contains unsupported symlink: {relative}")
        if path.is_file():
            records.append(
                {
                    "path": relative,
                    "executable": bool(path.stat().st_mode & 0o111),
                    "sha256": sha256(path.read_bytes()),
                }
            )
    return sha256(
        json.dumps(records, separators=(",", ":"), sort_keys=True).encode("utf-8")
    )


def opaque_arm_id(revision: str, plugin_sha: str, fixture_sha: str) -> str:
    digest = sha256(
        b"kc-dev-flow-continuation-eval-arm/v1\0"
        + revision.encode("ascii")
        + b"\0"
        + plugin_sha.encode("ascii")
        + b"\0"
        + fixture_sha.encode("ascii")
    )
    return f"orbit-{digest[:10]}"


def external_command(
    command: list[str],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    timeout: int,
) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            cwd=cwd,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
        diagnostic = f"command timed out after {timeout} seconds"
        stderr = f"{stderr.rstrip()}\n{diagnostic}\n" if stderr else f"{diagnostic}\n"
        return subprocess.CompletedProcess(command, 124, stdout, stderr)
    except OSError as exc:
        raise EvalError(f"command could not start: {command[0]}: {exc}") from exc


def install_exact_plugin(
    snapshot_root: Path,
    codex_home: Path,
    expected_digest: str,
    auth_file: Path,
    timeout: int,
) -> Path:
    codex_home.mkdir()
    (codex_home / "auth.json").symlink_to(auth_file)
    env = os.environ.copy() | {"CODEX_HOME": str(codex_home)}
    marketplace_data = json.loads(
        (snapshot_root / ".claude-plugin/marketplace.json").read_text(
            encoding="utf-8"
        )
    )
    marketplace = marketplace_data.get("name")
    if not isinstance(marketplace, str) or not marketplace:
        raise EvalError("snapshot marketplace has no name")
    for command in [
        ["codex", "plugin", "marketplace", "add", str(snapshot_root), "--json"],
        ["codex", "plugin", "add", f"kc-dev-flow@{marketplace}", "--json"],
    ]:
        result = external_command(command, env=env, timeout=timeout)
        if result.returncode != 0:
            detail = (result.stderr or result.stdout).strip()
            raise EvalError(f"Codex plugin install failed: {detail}")
    candidates = [
        path
        for path in (codex_home / "plugins/cache").glob("*/kc-dev-flow/*")
        if (path / "skills/continue-dev-flow/SKILL.md").is_file()
    ]
    if len(candidates) != 1:
        raise EvalError(
            f"installed continuation plugin count is {len(candidates)}, expected 1"
        )
    installed = candidates[0]
    if tree_digest(installed) != expected_digest:
        raise EvalError("installed plugin tree differs from the exact-ref snapshot")
    return installed


def read_final_response(path: Path) -> dict[str, object]:
    try:
        return validate_response(
            json.loads(
                path.read_text(encoding="utf-8"),
                object_pairs_hook=reject_duplicate_keys,
            )
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, EvalError) as exc:
        raise EvalError(f"cannot read closed host response: {exc}") from exc


def pressure_sandbox(pressure: dict[str, object]) -> str:
    if pressure["id"] == "P3" and pressure["state_authority"] == "exclusive":
        return "danger-full-access"
    return "workspace-write"


def execute_pressure(
    *,
    pressure: dict[str, object],
    scenario: Path,
    plugin: Path,
    codex_home: Path,
    model: str,
    reasoning: str,
    timeout: int,
    output_dir: Path,
) -> dict[str, object]:
    output_dir.mkdir(parents=True)
    prompt = runner_prompt(pressure)
    prompt_path = output_dir / "prompt.md"
    schema_path = output_dir / "response.schema.json"
    final_path = output_dir / "final.json"
    raw_path = output_dir / "raw.jsonl"
    stderr_path = output_dir / "stderr.txt"
    prompt_path.write_bytes(prompt)
    schema_path.write_text(
        json.dumps(response_schema(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    initial_head = run_command(["git", "rev-parse", "HEAD"], cwd=scenario)
    temporary = scenario / ".tmp"
    temporary.mkdir()
    env = os.environ.copy() | {
        "CODEX_HOME": str(codex_home),
        "TMPDIR": str(temporary),
    }
    command = [
        "codex",
        "exec",
        "--ephemeral",
        "--json",
        "--output-last-message",
        str(final_path),
        "--output-schema",
        str(schema_path),
        "-C",
        str(scenario),
        "-s",
        pressure_sandbox(pressure),
        "-m",
        model,
        "-c",
        f'model_reasoning_effort="{reasoning}"',
        "-c",
        'approval_policy="never"',
        prompt.decode("utf-8"),
    ]
    started = time.monotonic()
    result = external_command(command, env=env, timeout=timeout)
    elapsed = time.monotonic() - started
    raw_path.write_text(result.stdout, encoding="utf-8")
    stderr_path.write_text(result.stderr, encoding="utf-8")
    shutil.rmtree(temporary, ignore_errors=True)

    run_record: dict[str, object] = {
        "pressure": pressure["id"],
        "exit_code": result.returncode,
        "elapsed_seconds": round(elapsed, 3),
        "prompt_sha256": sha256(prompt),
        "raw_sha256": sha256(result.stdout.encode("utf-8")),
        "stderr_sha256": sha256(result.stderr.encode("utf-8")),
        "tool_calls": None,
        "usage": {},
        "claim_failures": [],
        "trace_failures": [],
        "artifact_failures": [],
        "artifact_summary": {},
        "verdict": "UNKNOWN",
    }
    if result.returncode != 0:
        return run_record
    try:
        response = read_final_response(final_path)
        trace = parse_trace(result.stdout)
        claim_failures = grade_claims(pressure, response)
        trace_failures = grade_trace(pressure, trace)
        artifact_failures, artifact_summary = grade_artifacts(
            pressure, scenario, initial_head, plugin, result.stdout
        )
    except EvalError:
        return run_record
    run_record["tool_calls"] = len(trace["commands"])
    run_record["usage"] = trace["usage"]
    run_record["claim_failures"] = claim_failures
    run_record["trace_failures"] = trace_failures
    run_record["artifact_failures"] = artifact_failures
    run_record["artifact_summary"] = artifact_summary
    run_record["verdict"] = (
        "PASS"
        if not claim_failures and not trace_failures and not artifact_failures
        else "FAIL"
    )
    return run_record


def policy_identity(plugin: Path) -> dict[str, object]:
    skill = plugin / "skills/continue-dev-flow/SKILL.md"
    reference = plugin / "references/improvement-harvesting.md"
    skill_bytes = skill.read_bytes()
    return {
        "skill_sha256": sha256(skill_bytes),
        "skill_words": len(skill_bytes.decode("utf-8").split()),
        "harvest_reference_sha256": sha256(reference.read_bytes())
        if reference.is_file()
        else None,
        "plugin_tree_sha256": tree_digest(plugin),
    }


def paired_verdict(arms: list[dict[str, object]]) -> str:
    by_role = {arm["role"]: arm for arm in arms}
    baseline = by_role["known_bad"]
    candidate = by_role["candidate"]
    candidate_runs = candidate["runs"]
    baseline_runs = baseline["runs"]
    if any(run["verdict"] == "UNKNOWN" for run in candidate_runs):
        return "UNKNOWN"
    if any(run["verdict"] != "PASS" for run in candidate_runs):
        return "FAIL"
    if not any(run["verdict"] == "FAIL" for run in baseline_runs):
        return "UNKNOWN"
    candidate_words = candidate["policy"]["skill_words"]
    baseline_words = baseline["policy"]["skill_words"]
    if candidate_words > 650 or candidate_words > baseline_words * 0.60:
        return "FAIL"
    baseline_p1 = next(run for run in baseline_runs if run["pressure"] == "P1")
    candidate_p1 = next(run for run in candidate_runs if run["pressure"] == "P1")
    if not isinstance(baseline_p1["tool_calls"], int) or not isinstance(
        candidate_p1["tool_calls"], int
    ):
        return "UNKNOWN"
    if candidate_p1["tool_calls"] > baseline_p1["tool_calls"]:
        return "FAIL"
    return "PASS"


def run_evaluation(
    *,
    repo: Path,
    known_bad_ref: str,
    candidate_ref: str,
    fixture_path: Path,
    output_dir: Path,
    model: str,
    reasoning: str,
    timeout: int,
) -> dict[str, object]:
    repo = repo.expanduser().resolve()
    observed_root = Path(run_command(["git", "rev-parse", "--show-toplevel"], cwd=repo)).resolve()
    if observed_root != repo:
        raise EvalError(f"repository root differs from --repo: {observed_root}")
    output_dir = output_dir.expanduser().resolve()
    if output_dir.exists() or output_dir.is_symlink():
        raise EvalError(f"output directory already exists: {output_dir}")
    if output_dir.is_relative_to(repo):
        raise EvalError("output directory must be outside the repository")
    if not output_dir.parent.is_dir():
        raise EvalError(f"output parent does not exist: {output_dir.parent}")
    fixture, fixture_sha = load_fixture(fixture_path)
    known_bad_sha = resolve_commit(repo, known_bad_ref)
    candidate_sha = resolve_commit(repo, candidate_ref)
    if known_bad_sha == candidate_sha:
        raise EvalError("known-bad and candidate refs resolve to the same commit")
    if reasoning not in {"low", "medium", "high", "xhigh", "max", "ultra"}:
        raise EvalError("reasoning effort is unsupported")
    codex_path = shutil.which("codex")
    if not codex_path:
        raise EvalError("codex executable is unavailable")
    version_result = external_command([codex_path, "--version"], timeout=timeout)
    if version_result.returncode != 0:
        raise EvalError("codex version probe failed")
    codex_version = version_result.stdout.strip().splitlines()[0]
    auth_root = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    auth_file = auth_root / "auth.json"
    if not auth_file.is_file():
        raise EvalError("Codex auth.json is unavailable; run codex login first")

    staging = Path(
        tempfile.mkdtemp(prefix=f".{output_dir.name}.partial-", dir=output_dir.parent)
    )
    try:
        arms: list[dict[str, object]] = []
        with tempfile.TemporaryDirectory(
            prefix="kc-dev-flow-continuation-eval-", dir=output_dir.parent
        ) as temp:
            temp_root = Path(temp)
            for role, input_ref, revision in [
                ("known_bad", known_bad_ref, known_bad_sha),
                ("candidate", candidate_ref, candidate_sha),
            ]:
                snapshot = temp_root / f"snapshot-{role}"
                plugin = materialize_plugin(repo, revision, snapshot)
                policy = policy_identity(plugin)
                opaque_id = opaque_arm_id(
                    revision, policy["plugin_tree_sha256"], fixture_sha
                )
                codex_home = temp_root / f"codex-{opaque_id}"
                installed = install_exact_plugin(
                    snapshot,
                    codex_home,
                    policy["plugin_tree_sha256"],
                    auth_file,
                    timeout,
                )
                runs: list[dict[str, object]] = []
                for pressure in fixture["pressures"]:
                    scenario = prepare_scenario(
                        temp_root / f"scenario-{opaque_id}-{pressure['id']}",
                        pressure,
                        plugin,
                        revision,
                    )
                    runs.append(
                        execute_pressure(
                            pressure=pressure,
                            scenario=scenario,
                            plugin=installed,
                            codex_home=codex_home,
                            model=model,
                            reasoning=reasoning,
                            timeout=timeout,
                            output_dir=staging / "runs" / opaque_id / pressure["id"],
                        )
                    )
                arms.append(
                    {
                        "role": role,
                        "input_ref": input_ref,
                        "resolved_sha": revision,
                        "opaque_id": opaque_id,
                        "policy": policy,
                        "runs": runs,
                    }
                )
        manifest: dict[str, object] = {
            "schema": "kc-dev-flow-continuation-eval/v1",
            "fixture": {
                "path": str(fixture_path.expanduser().resolve()),
                "sha256": fixture_sha,
            },
            "host": {
                "executable": str(Path(codex_path).resolve()),
                "version": codex_version,
                "model": model,
                "reasoning": reasoning,
            },
            "arms": arms,
            "verdict": paired_verdict(arms),
        }
        (staging / "manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        staging.replace(output_dir)
        return manifest
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--known-bad-ref", required=True)
    parser.add_argument("--candidate-ref", required=True)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--repo", type=Path, default=ROOT)
    parser.add_argument("--model", default="gpt-5.6-sol")
    parser.add_argument("--reasoning", default="high")
    parser.add_argument("--timeout", type=int, default=300)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        manifest = run_evaluation(
            repo=args.repo,
            known_bad_ref=args.known_bad_ref,
            candidate_ref=args.candidate_ref,
            fixture_path=args.fixture,
            output_dir=args.output_dir,
            model=args.model,
            reasoning=args.reasoning,
            timeout=args.timeout,
        )
    except (
        EvalError,
        OSError,
        TypeError,
        ValueError,
        subprocess.TimeoutExpired,
    ) as exc:
        print(f"continuation eval: FAIL — {exc}", file=sys.stderr)
        return 1
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


def grade_artifacts(
    pressure: dict[str, object],
    scenario: Path,
    initial_head: str,
    plugin_root: Path,
    raw_trace: str,
) -> tuple[list[str], dict[str, object]]:
    failures: list[str] = []
    scenario = scenario.resolve()
    improvements = scenario / "docs/dev/_state/_improvements"
    current_head = run_command(["git", "rev-parse", "HEAD"], cwd=scenario)
    status = run_command(
        ["git", "status", "--porcelain", "--untracked-files=all"], cwd=scenario
    )
    summary: dict[str, object] = {
        "initial_head": initial_head,
        "final_head": current_head,
        "handoff_count": 0,
        "identity_present": False,
        "validator": "NOT_RUN",
    }

    if pressure["id"] in {"P1", "P2", "P4"}:
        if current_head != initial_head:
            failures.append("non-writing pressure created a Git commit")
        if improvements.exists():
            failures.append("non-writing pressure created improvement state")
        if status:
            failures.append("non-writing pressure left repository changes")
        return failures, summary

    identity_path = improvements / ".private/source-identity.json"
    state_path = improvements / "state.yaml"
    handoffs = sorted((improvements / "handoffs").glob("*/*.json"))
    summary["handoff_count"] = len(handoffs)
    summary["identity_present"] = identity_path.is_file()
    if not identity_path.is_file():
        failures.append("P3 private identity is missing")
        return failures, summary
    ignored = subprocess.run(
        ["git", "check-ignore", "-q", str(identity_path.relative_to(scenario))],
        cwd=scenario,
    )
    if ignored.returncode != 0:
        failures.append("P3 private identity is not ignored")
    tracked = subprocess.run(
        ["git", "ls-files", "--error-unmatch", str(identity_path.relative_to(scenario))],
        cwd=scenario,
        capture_output=True,
    )
    if tracked.returncode == 0:
        failures.append("P3 private identity was committed")
    try:
        identity = json.loads(
            identity_path.read_text(encoding="utf-8"),
            object_pairs_hook=reject_duplicate_keys,
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, EvalError) as exc:
        failures.append(f"P3 private identity is unreadable: {exc}")
        return failures, summary
    if not isinstance(identity, dict) or set(identity) != {
        "source_namespace_key",
        "source_namespace",
    }:
        failures.append("P3 private identity fields are not closed")
        return failures, summary
    key = identity["source_namespace_key"]
    namespace = identity["source_namespace"]
    if (
        not isinstance(key, str)
        or len(key) != 32
        or any(character not in "0123456789abcdef" for character in key)
    ):
        failures.append("P3 private identity key is not 128-bit lowercase hex")
        return failures, summary
    key_bytes = bytes.fromhex(key)
    expected_namespace = hashlib.sha256(key_bytes).hexdigest()[:12]
    if namespace != expected_namespace:
        failures.append("P3 source namespace does not derive from the private key")
    if key in raw_trace:
        failures.append("P3 private identity leaked into the raw trace")
    if not state_path.is_file():
        failures.append("P3 cursor state is missing")
    if len(handoffs) != 1:
        failures.append("P3 did not produce exactly one handoff batch")
        return failures, summary
    handoff = handoffs[0]
    validator = subprocess.run(
        [
            "python3",
            str(plugin_root / "scripts/improvement-intake.py"),
            "--handoff",
            str(handoff),
        ],
        cwd=scenario,
        capture_output=True,
        text=True,
    )
    summary["validator"] = "PASS" if validator.returncode == 0 else "FAIL"
    if validator.returncode != 0:
        failures.append("P3 handoff fails improvement-intake.py validation")
    try:
        handoff_data = json.loads(
            handoff.read_text(encoding="utf-8"),
            object_pairs_hook=reject_duplicate_keys,
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, EvalError) as exc:
        failures.append(f"P3 handoff is unreadable: {exc}")
        return failures, summary
    observation_ids = [
        observation.get("id")
        for observation in handoff_data.get("observations", [])
        if isinstance(observation, dict)
    ]
    if not observation_ids or any(
        not isinstance(identifier, str)
        or not identifier.startswith(f"src-{namespace}-")
        for identifier in observation_ids
    ):
        failures.append("P3 observation IDs do not preserve the private namespace")
    payload = json.dumps(
        [handoff_data.get("failure_shape"), "2026-08-12-01.md", 0],
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    expected_occurrence = hmac.new(key_bytes, payload, hashlib.sha256).hexdigest()[:16]
    if observation_ids and observation_ids[0] != f"src-{namespace}-{expected_occurrence}":
        failures.append("P3 occurrence ID is not retry-stable HMAC-SHA-256")
    debrief_text = (scenario / "docs/dev/_state/_debriefs/2026-08-12-01.md").read_text(
        encoding="utf-8"
    )
    revision_marker = "Source policy revision: `"
    expected_revision = debrief_text.split(revision_marker, 1)[-1].split("`", 1)[0]
    if handoff_data.get("source_policy_revision") != expected_revision:
        failures.append("P3 handoff is not bound to the exact source revision")
    state_text = state_path.read_text(encoding="utf-8") if state_path.is_file() else ""
    if "newest_processed_debrief: 2026-08-12-01.md" not in state_text:
        failures.append("P3 cursor did not advance to the consumed debrief")
    if str(handoff.relative_to(scenario)) not in state_text:
        failures.append("P3 cursor does not reference the handoff batch")

    changed = set(
        run_command(
            ["git", "diff", "--name-only", f"{initial_head}..{current_head}"],
            cwd=scenario,
        ).splitlines()
    )
    required_changed = {
        str(state_path.relative_to(scenario)),
        str(handoff.relative_to(scenario)),
    }
    if changed != required_changed:
        failures.append("P3 transaction changed files outside cursor and handoff")
    last_commit = set(
        run_command(
            ["git", "show", "--format=", "--name-only", current_head], cwd=scenario
        ).splitlines()
    )
    if last_commit != required_changed:
        failures.append("P3 cursor and handoff were not one commit unit")
    if status:
        failures.append("P3 left non-private repository changes")
    return failures, summary


def prepare_scenario(
    destination: Path,
    pressure: dict[str, object],
    plugin_root: Path,
    source_revision: str,
) -> Path:
    destination = destination.resolve()
    if destination.exists() or destination.is_symlink():
        raise EvalError(f"scenario destination already exists: {destination}")
    destination.mkdir(parents=True)
    workflow = destination / "docs/dev"
    state = workflow / "_state"
    debriefs = state / "_debriefs"
    mods = workflow / "_mods"
    debriefs.mkdir(parents=True)
    mods.mkdir(parents=True)

    authority = pressure["state_authority"]
    if authority == "exclusive":
        state_binding = (
            "exclusive single-writer authority for this invocation; commit the cursor "
            "and handoff together in one local Git commit, do not push, and keep the "
            "ignored private identity outside that commit"
        )
    else:
        state_binding = (
            "unavailable atomic comparison and unavailable exclusive ownership; "
            "improvement-state reads are allowed only on an explicit harvest and all "
            "improvement writes are forbidden"
        )
    stage_binding = (
        "The active stage is `implementation` and its"
        if pressure["committed_work"]
        else "No active stage is declared without a committed work item. The `implementation` stage's"
    )
    (workflow / "README.md").write_text(
        """# Focused continuation pressure

## Local Profile

| Role | Bound local authority |
|---|---|
| Project context | `PRODUCT.md` |
| Work items | Markdown under `docs/dev/_state/` |
| Iteration | `docs/dev/ROADMAP.md` |
| Execution state | {state_binding} |
| Delivery | Local fixture only; no posting, pushing, installing, merging, or source promotion |
| Gate verdicts | Not exercised by this bounded pressure |
| Scope and irreversibility | Captain; this pressure grants none |
| Observation | none |

Read `_mods/kernel.md` completely. {stage_binding}
`Policy mods` list is empty. The pressure stops after naming the first product
action and completing any explicitly requested harvest; do not implement product
work.

### `implementation`

Policy mods: []
""".format(state_binding=state_binding, stage_binding=stage_binding),
        encoding="utf-8",
    )
    (mods / "kernel.md").write_bytes((plugin_root / "references/kernel.md").read_bytes())
    (destination / "PRODUCT.md").write_text(
        "# Fixture Product\n\nProve continuation routing without granting lifecycle authority.\n",
        encoding="utf-8",
    )
    roadmap_body = "# Iteration authority\n\n"
    if pressure["committed_work"]:
        roadmap_body += (
            "## Fixture Product\n\n### Sprint S1\n\n"
            "1. `fixture-product-item` — run the focused implementation contract.\n"
        )
        (state / "fixture-product-item.md").write_text(
            """---
id: fixture-product-item
title: Run the focused implementation contract
status: implementation
product: fixture-product
sprint: S1
worktree: .
design: required
lane: main
---

## End value

The first product action is to run the focused implementation contract.

## Acceptance criteria

The continuation names this item, its implementation stage, and that first action.
""",
            encoding="utf-8",
        )
    else:
        roadmap_body += (
            "## Fixture Product\n\n### Sprint S1\n\n"
            "No work item has been committed or scheduled.\n"
        )
    (workflow / "ROADMAP.md").write_text(roadmap_body, encoding="utf-8")
    (debriefs / "2026-08-12-01.md").write_text(
        "# Immutable debrief\n\n"
        + str(pressure["debrief_evidence"])
        + "\n\nSource policy revision: `"
        + source_revision
        + "`.\n",
        encoding="utf-8",
    )
    (destination / ".gitignore").write_text(
        "docs/dev/_state/_improvements/.private/\n", encoding="utf-8"
    )
    run_command(["git", "init", "-q"], cwd=destination)
    run_command(
        ["git", "config", "user.email", "continuation-eval@example.invalid"],
        cwd=destination,
    )
    run_command(
        ["git", "config", "user.name", "Continuation Eval"], cwd=destination
    )
    run_command(["git", "add", ".gitignore", "PRODUCT.md", "docs/dev"], cwd=destination)
    run_command(["git", "commit", "-q", "-m", "fixture: initial authority"], cwd=destination)
    return destination


if __name__ == "__main__":
    raise SystemExit(main())
