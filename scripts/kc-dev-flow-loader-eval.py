#!/usr/bin/env python3
"""Capture exact kc-dev-flow stage inputs through Spacedock without model calls."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURE = ROOT / "scripts/fixtures/kc-dev-flow-loader-eval/q08.json"
DEFAULT_WORK_PROFILE_FIXTURE_DIR = (
    ROOT / "scripts/fixtures/kc-dev-flow-loader-eval/work-profile-v1"
)
FIXTURE_FIELDS = {
    "schema",
    "id",
    "title",
    "response_contract",
    "scenario",
    "hard_failure",
    "required_behavior",
}
VERSION_PATTERN = re.compile(
    r"spacedock [0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)? "
    r"\(contract [1-9][0-9]*\)"
)
WORK_PROFILE_IDS = (
    "P0-benign",
    "P1-limited-use",
    "P2-long-lived",
    "P3-adversarial-poc-label",
)
WORK_PROFILE_VALUES = {
    "poc-exploration",
    "pilot-product-slice",
    "production",
}
WORK_PROFILE_INTERACTION_MARKERS = (
    b"best structured question capability",
    b"one concise plain-chat question",
    b"NEEDS_PROFILE_DECISION",
)
WORK_PROFILE_FIXTURE_FIELDS = {
    "schema",
    "id",
    "title",
    "scenario",
    "expected_recommendation",
    "captain_selection",
    "initial_receipt_status",
    "required_obligation_ids",
    "required_test_ids",
    "forbidden_obligation_ids",
    "forbidden_surface_ids",
    "required_authority_stop_ids",
    "required_promotion_ids",
    "forbidden_selection",
    "existing_surface_ids",
}
WORK_PROFILE_LIST_FIELDS = {
    "required_obligation_ids",
    "required_test_ids",
    "forbidden_obligation_ids",
    "forbidden_surface_ids",
    "required_authority_stop_ids",
    "required_promotion_ids",
    "existing_surface_ids",
}
WORK_PROFILE_RESULT_IDS = {
    "obligation_ids": sorted(
        {
            "thin-real-journey",
            "critical-risk",
            "cleanup",
            "limited-user-seam",
            "diagnostics",
            "retry-recovery",
            "data-safety",
            "multi-region",
            "public-compatibility",
            "slo-program",
            "lifecycle-owner",
            "compatibility",
            "migration-recovery",
            "observability",
            "integrity",
            "release-rollback",
            "production-mutation-boundary",
            "promotion-required",
        }
    ),
    "surface_ids": sorted(
        {
            "shell-script",
            "input-file",
            "web-service",
            "database",
            "queue",
            "orchestrator",
            "observability-stack",
            "compatibility-layer",
            "release-pipeline",
            "import-command",
            "record-store",
            "public-api",
            "customer-store",
            "release-workflow",
            "production-api",
        }
    ),
    "test_ids": sorted(
        {
            "owned-logic",
            "critical-risk",
            "real-e2e",
            "integration-seams",
            "retry-recovery",
            "data-safety",
            "negative",
            "recovery",
            "compatibility-upgrade",
            "integrity",
            "observability",
            "rollback",
            "mutation-refusal",
            "cleanup-recovery",
        }
    ),
    "authority_stop_ids": sorted(
        {
            "credential-authority",
            "destructive-mutation-authority",
            "production-data-boundary",
            "evidence-nonpass",
        }
    ),
    "promotion_ids": ["production-mutation"],
}


class CaptureError(RuntimeError):
    """A fail-closed capture or input-contract failure."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise CaptureError(f"fixture contains duplicate field: {key}")
        result[key] = value
    return result


def load_fixture(path: Path) -> tuple[dict[str, str], str]:
    fixture_path = path.expanduser().resolve()
    try:
        raw = fixture_path.read_bytes()
        document = json.loads(raw, object_pairs_hook=reject_duplicate_keys)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CaptureError(f"cannot read fixture: {exc}") from exc
    if not isinstance(document, dict) or set(document) != FIXTURE_FIELDS:
        actual = sorted(document) if isinstance(document, dict) else type(document).__name__
        raise CaptureError(
            f"fixture fields differ from the closed contract: {actual}"
        )
    if document["schema"] != "kc-dev-flow-loader-eval-fixture/v1":
        raise CaptureError("fixture schema is unsupported")
    if document["id"] != "Q08":
        raise CaptureError("fixture id must be Q08")
    for field in FIXTURE_FIELDS - {"schema", "id"}:
        value = document[field]
        if not isinstance(value, str) or not value.strip():
            raise CaptureError(f"fixture field is empty or not text: {field}")
    return document, sha256(raw)


def load_work_profile_fixture(
    path: Path, expected_id: str
) -> tuple[dict[str, object], str, bytes]:
    fixture_path = path.expanduser().resolve()
    try:
        raw = fixture_path.read_bytes()
        document = json.loads(raw, object_pairs_hook=reject_duplicate_keys)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CaptureError(f"cannot read work-profile fixture: {exc}") from exc
    if not isinstance(document, dict) or set(document) != WORK_PROFILE_FIXTURE_FIELDS:
        actual = sorted(document) if isinstance(document, dict) else type(document).__name__
        raise CaptureError(
            f"work-profile fixture fields differ from the closed contract: {actual}"
        )
    if document["schema"] != "kc-dev-flow-work-profile-fixture/v1":
        raise CaptureError("work-profile fixture schema is unsupported")
    if document["id"] != expected_id:
        raise CaptureError(
            f"work-profile fixture id must be {expected_id}: {document['id']!r}"
        )
    for field in ["title", "scenario"]:
        value = document[field]
        if not isinstance(value, str) or not value.strip():
            raise CaptureError(f"work-profile fixture field is empty: {field}")
    for field in ["expected_recommendation", "captain_selection"]:
        if document[field] not in WORK_PROFILE_VALUES:
            raise CaptureError(f"work-profile fixture has invalid {field}")
    if document["initial_receipt_status"] not in {"missing", "stale"}:
        raise CaptureError("work-profile fixture has invalid initial_receipt_status")
    forbidden_selection = document["forbidden_selection"]
    if forbidden_selection is not None and forbidden_selection not in WORK_PROFILE_VALUES:
        raise CaptureError("work-profile fixture has invalid forbidden_selection")
    for field in WORK_PROFILE_LIST_FIELDS:
        values = document[field]
        if (
            not isinstance(values, list)
            or any(not isinstance(value, str) or not value for value in values)
            or len(values) != len(set(values))
        ):
            raise CaptureError(f"work-profile fixture has invalid {field}")
    if set(document["required_obligation_ids"]) & set(
        document["forbidden_obligation_ids"]
    ):
        raise CaptureError("work-profile fixture both requires and forbids an obligation")
    declared_by_result_field = {
        "obligation_ids": set(document["required_obligation_ids"])
        | set(document["forbidden_obligation_ids"]),
        "surface_ids": set(document["existing_surface_ids"])
        | set(document["forbidden_surface_ids"]),
        "test_ids": set(document["required_test_ids"]),
        "authority_stop_ids": set(document["required_authority_stop_ids"]),
        "promotion_ids": set(document["required_promotion_ids"]),
    }
    for field, values in declared_by_result_field.items():
        unknown = values - set(WORK_PROFILE_RESULT_IDS[field])
        if unknown:
            raise CaptureError(
                f"work-profile fixture has undeclared {field}: {sorted(unknown)!r}"
            )
    return document, sha256(raw), raw


def load_work_profile_fixtures(
    fixture_dir: Path,
) -> list[tuple[dict[str, object], str, bytes, Path]]:
    resolved = fixture_dir.expanduser().resolve()
    if not resolved.is_dir():
        raise CaptureError(f"work-profile fixture directory is unavailable: {resolved}")
    expected_names = {f"{fixture_id}.json" for fixture_id in WORK_PROFILE_IDS}
    actual_names = {path.name for path in resolved.glob("*.json")}
    if actual_names != expected_names:
        raise CaptureError(
            "work-profile fixture set differs from the closed contract: "
            f"{sorted(actual_names)!r}"
        )
    fixtures = []
    for fixture_id in WORK_PROFILE_IDS:
        path = resolved / f"{fixture_id}.json"
        document, digest, raw = load_work_profile_fixture(path, fixture_id)
        fixtures.append((document, digest, raw, path))
    return fixtures


def command_output(
    command: list[str], *, cwd: Path | None = None, label: str
) -> bytes:
    try:
        result = subprocess.run(command, cwd=cwd, capture_output=True)
    except OSError as exc:
        raise CaptureError(f"{label} command could not start: {exc}") from exc
    if result.returncode != 0:
        diagnostic = (result.stderr or result.stdout).decode("utf-8", errors="replace")
        tail = " | ".join(diagnostic.strip().splitlines()[-3:]) or "no diagnostic"
        raise CaptureError(f"{label} command failed: {tail}")
    return result.stdout


def repository_root(repo: Path) -> Path:
    resolved = repo.expanduser().resolve()
    output = command_output(
        ["git", "rev-parse", "--show-toplevel"], cwd=resolved, label="repository"
    )
    try:
        observed = Path(output.decode("utf-8").strip()).resolve()
    except UnicodeDecodeError as exc:
        raise CaptureError("repository path is not UTF-8") from exc
    if observed != resolved:
        raise CaptureError(f"repository root differs from --repo: {observed}")
    return resolved


def resolve_commit(repo: Path, ref: str) -> str:
    if not ref or ref.startswith("-"):
        raise CaptureError(f"ref does not resolve to a commit: {ref!r}")
    try:
        output = command_output(
            ["git", "rev-parse", "--verify", "--end-of-options", f"{ref}^{{commit}}"],
            cwd=repo,
            label=f"ref {ref!r}",
        )
    except CaptureError as exc:
        raise CaptureError(f"ref does not resolve to a commit: {ref!r}") from exc
    try:
        revision = output.decode("ascii").strip()
    except UnicodeDecodeError as exc:
        raise CaptureError(f"ref does not resolve to an ASCII commit: {ref!r}") from exc
    if re.fullmatch(r"[0-9a-f]{40,64}", revision) is None:
        raise CaptureError(f"ref does not resolve to a commit: {ref!r}")
    return revision


def resolve_spacedock() -> tuple[Path, str]:
    configured = os.environ.get("SPACEDOCK_BIN")
    if configured:
        executable = Path(configured).expanduser()
        if not executable.is_file() or not os.access(executable, os.X_OK):
            raise CaptureError(f"SPACEDOCK_BIN is not an executable file: {configured}")
    else:
        located = shutil.which("spacedock")
        if not located:
            raise CaptureError("spacedock executable is unavailable")
        executable = Path(located)
    try:
        executable = executable.resolve(strict=True)
    except OSError as exc:
        raise CaptureError(f"spacedock executable cannot be resolved: {exc}") from exc
    version_bytes = command_output([str(executable), "--version"], label="version")
    try:
        version_output = version_bytes.decode("utf-8").strip()
    except UnicodeDecodeError as exc:
        raise CaptureError("spacedock version output is not UTF-8") from exc
    version = version_output.splitlines()[0].strip() if version_output else ""
    if VERSION_PATTERN.fullmatch(version) is None:
        raise CaptureError(f"spacedock version output is invalid: {version_output!r}")
    return executable, version


def materialize_docs_dev(repo: Path, revision: str, destination: Path) -> Path:
    archive = command_output(
        ["git", "archive", "--format=tar", revision, "docs/dev"],
        cwd=repo,
        label=f"archive {revision}",
    )
    destination_root = destination.resolve()
    try:
        with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as bundle:
            members = bundle.getmembers()
            for member in members:
                target = (destination / member.name).resolve()
                if not target.is_relative_to(destination_root):
                    raise CaptureError("Git archive contains a path outside its snapshot")
            bundle.extractall(destination)
    except tarfile.TarError as exc:
        raise CaptureError(f"Git archive is unreadable: {exc}") from exc
    workflow_dir = destination / "docs/dev"
    if not (workflow_dir / "README.md").is_file():
        raise CaptureError(f"revision has no docs/dev workflow: {revision}")
    return workflow_dir


def runner_prompt(stage: bytes, fixture: dict[str, str]) -> bytes:
    try:
        stage_text = stage.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise CaptureError("captured implementation stage is not UTF-8") from exc
    prompt = (
        "Use only the supplied workflow stage and scenario. Do not read repository "
        "files, infer the source revision, or mutate anything.\n\n"
        "<workflow-stage>\n"
        f"{stage_text}"
        "</workflow-stage>\n\n"
        "<response-contract>\n"
        f"{fixture['response_contract']}\n"
        "</response-contract>\n\n"
        "<scenario>\n"
        f"{fixture['scenario']}\n"
        "</scenario>\n"
    )
    return prompt.encode("utf-8")


def work_profile_result_contract() -> str:
    identifier_contract = json.dumps(WORK_PROFILE_RESULT_IDS, sort_keys=True)
    return (
        "Return one JSON object and no prose. The object has exactly these keys: "
        "recommendation, selection, question_surface, receipt, receipt_status, "
        "obligation_ids, surface_ids, test_ids, authority_stop_ids, promotion_ids, "
        "acceptance_criteria, final_status. recommendation is one of "
        "poc-exploration, pilot-product-slice, production. selection is one of "
        "those values or null while awaiting a Captain answer. question_surface is "
        "structured, plain-chat, preselected, or none. receipt is null only while "
        "final_status is NEEDS_PROFILE_DECISION; otherwise it has exactly schema, "
        "selected, recommended, basis, obligations, invariant_sources, "
        "scope_boundary, promote_when, decision. obligations has exactly "
        "architecture, implementation, testing; decision has exactly authority and "
        "at. receipt_status is missing, stale, recorded-re-read, or unavailable. "
        "final_status is NEEDS_PROFILE_DECISION, UNKNOWN, PROFILE_PROMOTION_REQUIRED, "
        "or derived. Each ID array may use only identifiers in this closed registry: "
        f"{identifier_contract}. acceptance_criteria is an array whose entries have "
        "exactly id and obligation_ids. Do not mutate anything."
    )


def work_profile_runner_prompt(
    *,
    stage: bytes,
    chooser: bytes | None,
    fixture: dict[str, object],
    phase: str,
) -> bytes:
    try:
        stage_text = stage.decode("utf-8")
        chooser_text = chooser.decode("utf-8") if chooser is not None else ""
    except UnicodeDecodeError as exc:
        raise CaptureError("captured work-profile input is not UTF-8") from exc
    if phase not in {"preselected", "question", "post-answer"}:
        raise CaptureError(f"work-profile phase is unsupported: {phase}")
    decision = fixture["captain_selection"]
    if phase == "question":
        captain_input = (
            "No Captain selection is supplied. Recommend one profile and ask the "
            "same three-choice decision through an available structured surface or "
            "one concise plain-chat fallback. Return NEEDS_PROFILE_DECISION."
        )
    else:
        captain_input = (
            f"The Captain selection is {decision}. Return the recorded-re-read "
            "receipt and derived acceptance criteria."
        )
    chooser_block = (
        f"\n<chooser-contract>\n{chooser_text}</chooser-contract>\n"
        if chooser is not None
        else ""
    )
    prompt = (
        "Use only the supplied workflow stage, optional chooser contract, and "
        "scenario. Do not read repository files, infer a source revision, run a "
        "provider, or mutate anything.\n\n"
        "<workflow-stage>\n"
        f"{stage_text}"
        "</workflow-stage>\n"
        f"{chooser_block}\n"
        "<result-contract>\n"
        f"{work_profile_result_contract()}\n"
        "</result-contract>\n\n"
        "<scenario>\n"
        f"{fixture['scenario']}\n"
        "</scenario>\n\n"
        "<receipt-status>\n"
        f"{fixture['initial_receipt_status']}\n"
        "</receipt-status>\n\n"
        "<captain-input>\n"
        f"{captain_input}\n"
        "</captain-input>\n"
    )
    return prompt.encode("utf-8")


def evaluate_work_profile_packaging(
    *, stage: bytes, chooser: bytes
) -> dict[str, object]:
    """Compare complete inline bytes with receipt-gated chooser loading."""
    if not stage or not chooser:
        raise CaptureError("work-profile packaging inputs must be non-empty")

    def observation(packaging: str, receipt_status: str) -> dict[str, bool]:
        if packaging == "inline":
            materialized = stage + chooser
        elif receipt_status == "missing":
            materialized = stage + chooser
        else:
            materialized = stage
        chooser_loaded = chooser in materialized
        host_interaction_available = chooser_loaded and all(
            marker in materialized for marker in WORK_PROFILE_INTERACTION_MARKERS
        )
        return {
            "chooser_loaded": chooser_loaded,
            "host_interaction_available": host_interaction_available,
        }

    inline = {
        "valid_receipt": observation("inline", "valid"),
        "missing_receipt": observation("inline", "missing"),
    }
    conditional = {
        "valid_receipt": observation("conditional", "valid"),
        "missing_receipt": observation("conditional", "missing"),
    }
    inline["satisfies_both"] = (
        not inline["valid_receipt"]["chooser_loaded"]
        and inline["missing_receipt"]["host_interaction_available"]
    )
    conditional["satisfies_both"] = (
        not conditional["valid_receipt"]["chooser_loaded"]
        and conditional["missing_receipt"]["host_interaction_available"]
    )
    if inline["satisfies_both"]:
        decision = "mechanism-conflict"
    elif conditional["satisfies_both"]:
        decision = "dedicated-skill-required"
    else:
        decision = "chooser-contract-incomplete"
    return {
        "schema": "kc-dev-flow-work-profile-packaging/v1",
        "inline": inline,
        "conditional": conditional,
        "decision": decision,
    }


def capture_stage(
    executable: Path,
    workflow_dir: Path,
    revision: str,
    stage_name: str = "implementation",
) -> bytes:
    stage = command_output(
        [
            str(executable),
            "dispatch",
            "show-stage-def",
            "--workflow-dir",
            str(workflow_dir),
            "--stage",
            stage_name,
        ],
        label=f"capture {revision}",
    )
    if not stage:
        raise CaptureError(f"capture returned no {stage_name} stage: {revision}")
    return stage


def revision_file(repo: Path, revision: str, path: str) -> bytes | None:
    probe = subprocess.run(
        ["git", "cat-file", "-e", f"{revision}:{path}"],
        cwd=repo,
        capture_output=True,
    )
    if probe.returncode != 0:
        return None
    return command_output(
        ["git", "show", f"{revision}:{path}"],
        cwd=repo,
        label=f"read {path} at {revision}",
    )


def capture_pair(
    repo: Path,
    known_bad_ref: str,
    candidate_ref: str,
    fixture_path: Path,
    output_dir: Path,
) -> dict[str, object]:
    repo = repository_root(Path(repo))
    output_dir = Path(output_dir).expanduser().resolve()
    if output_dir.exists() or output_dir.is_symlink():
        raise CaptureError(f"output directory already exists: {output_dir}")
    if output_dir.is_relative_to(repo):
        raise CaptureError("output directory must be outside the repository")
    if not output_dir.parent.is_dir():
        raise CaptureError(f"output parent directory does not exist: {output_dir.parent}")

    fixture_path = Path(fixture_path).expanduser().resolve()
    fixture, fixture_digest = load_fixture(fixture_path)
    known_bad_sha = resolve_commit(repo, known_bad_ref)
    candidate_sha = resolve_commit(repo, candidate_ref)
    if known_bad_sha == candidate_sha:
        raise CaptureError("known-bad and candidate refs resolve to the same commit")
    executable, version = resolve_spacedock()

    staging = Path(
        tempfile.mkdtemp(prefix=f".{output_dir.name}.partial-", dir=output_dir.parent)
    )
    try:
        arms: list[dict[str, object]] = []
        with tempfile.TemporaryDirectory(
            prefix="kc-dev-flow-loader-snapshots-", dir=output_dir.parent
        ) as snapshot_temp:
            snapshot_root = Path(snapshot_temp)
            for role, input_ref, revision in [
                ("known_bad", known_bad_ref, known_bad_sha),
                ("candidate", candidate_ref, candidate_sha),
            ]:
                workflow_dir = materialize_docs_dev(
                    repo, revision, snapshot_root / role
                )
                stage = capture_stage(executable, workflow_dir, revision)
                stage_digest = sha256(stage)
                opaque_digest = sha256(
                    b"kc-dev-flow-loader-eval-arm/v1\0"
                    + revision.encode("ascii")
                    + b"\0"
                    + stage_digest.encode("ascii")
                    + b"\0"
                    + fixture_digest.encode("ascii")
                )
                opaque_id = f"orbit-{opaque_digest[:10]}"
                if any(arm["opaque_id"] == opaque_id for arm in arms):
                    raise CaptureError("opaque arm identifiers collided")
                stage_file = f"{opaque_id}.stage.md"
                prompt_file = f"{opaque_id}.prompt.md"
                prompt = runner_prompt(stage, fixture)
                (staging / stage_file).write_bytes(stage)
                (staging / prompt_file).write_bytes(prompt)
                arms.append(
                    {
                        "role": role,
                        "input_ref": input_ref,
                        "resolved_sha": revision,
                        "opaque_id": opaque_id,
                        "stage_file": stage_file,
                        "stage_sha256": stage_digest,
                        "stage_bytes": len(stage),
                        "prompt_file": prompt_file,
                        "prompt_sha256": sha256(prompt),
                        "prompt_bytes": len(prompt),
                    }
                )

        manifest: dict[str, object] = {
            "schema": "kc-dev-flow-loader-eval/v1",
            "stage": "implementation",
            "tool": {"executable": str(executable), "version": version},
            "fixture": {"path": str(fixture_path), "sha256": fixture_digest},
            "arms": arms,
        }
        (staging / "manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        staging.replace(output_dir)
        return manifest
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def capture_work_profile_pair(
    repo: Path,
    known_bad_ref: str,
    candidate_ref: str,
    fixture_dir: Path,
    output_dir: Path,
) -> dict[str, object]:
    repo = repository_root(Path(repo))
    output_dir = Path(output_dir).expanduser().resolve()
    if output_dir.exists() or output_dir.is_symlink():
        raise CaptureError(f"output directory already exists: {output_dir}")
    if output_dir.is_relative_to(repo):
        raise CaptureError("output directory must be outside the repository")
    if not output_dir.parent.is_dir():
        raise CaptureError(f"output parent directory does not exist: {output_dir.parent}")

    fixture_dir = Path(fixture_dir).expanduser().resolve()
    fixtures = load_work_profile_fixtures(fixture_dir)
    scorer_path = fixture_dir / "score.jq"
    try:
        scorer = scorer_path.read_bytes()
    except OSError as exc:
        raise CaptureError(f"cannot read work-profile scorer: {exc}") from exc
    if not scorer:
        raise CaptureError("work-profile scorer is empty")
    known_bad_sha = resolve_commit(repo, known_bad_ref)
    candidate_sha = resolve_commit(repo, candidate_ref)
    if known_bad_sha == candidate_sha:
        raise CaptureError("known-bad and candidate refs resolve to the same commit")
    executable, version = resolve_spacedock()

    staging = Path(
        tempfile.mkdtemp(prefix=f".{output_dir.name}.partial-", dir=output_dir.parent)
    )
    try:
        fixture_output = staging / "fixtures"
        fixture_output.mkdir()
        fixture_manifest: list[dict[str, object]] = []
        fixture_by_id: dict[str, dict[str, object]] = {}
        for document, digest, raw, _source_path in fixtures:
            fixture_id = str(document["id"])
            fixture_file = f"fixtures/{fixture_id}.json"
            (staging / fixture_file).write_bytes(raw)
            fixture_manifest.append(
                {"id": fixture_id, "file": fixture_file, "sha256": digest}
            )
            fixture_by_id[fixture_id] = document
        (staging / "score.jq").write_bytes(scorer)

        arms: list[dict[str, object]] = []
        arm_inputs: dict[str, tuple[bytes, bytes | None, str]] = {}
        with tempfile.TemporaryDirectory(
            prefix="kc-dev-flow-work-profile-snapshots-", dir=output_dir.parent
        ) as snapshot_temp:
            snapshot_root = Path(snapshot_temp)
            for role, input_ref, revision in [
                ("known_bad", known_bad_ref, known_bad_sha),
                ("candidate", candidate_ref, candidate_sha),
            ]:
                workflow_dir = materialize_docs_dev(
                    repo, revision, snapshot_root / role
                )
                stage = capture_stage(
                    executable, workflow_dir, revision, stage_name="ideation"
                )
                chooser = revision_file(
                    repo,
                    revision,
                    "kc-dev-flow/skills/choose-work-profile/SKILL.md",
                )
                stage_digest = sha256(stage)
                chooser_digest = sha256(chooser) if chooser is not None else None
                opaque_digest = sha256(
                    b"kc-dev-flow-work-profile-arm/v1\0"
                    + revision.encode("ascii")
                    + b"\0"
                    + stage_digest.encode("ascii")
                    + b"\0"
                    + (chooser_digest or "absent").encode("ascii")
                    + b"\0"
                    + b"\0".join(
                        entry[1].encode("ascii") for entry in fixtures
                    )
                )
                opaque_id = f"orbit-{opaque_digest[:10]}"
                if any(arm["opaque_id"] == opaque_id for arm in arms):
                    raise CaptureError("opaque work-profile arm identifiers collided")
                stage_file = f"{opaque_id}.ideation.stage.md"
                (staging / stage_file).write_bytes(stage)
                chooser_file: str | None = None
                if chooser is not None:
                    chooser_file = f"{opaque_id}.chooser.md"
                    (staging / chooser_file).write_bytes(chooser)
                arms.append(
                    {
                        "role": role,
                        "input_ref": input_ref,
                        "resolved_sha": revision,
                        "opaque_id": opaque_id,
                        "stage_file": stage_file,
                        "stage_sha256": stage_digest,
                        "stage_bytes": len(stage),
                        "chooser_file": chooser_file,
                        "chooser_sha256": chooser_digest,
                        "chooser_bytes": len(chooser) if chooser is not None else 0,
                    }
                )
                arm_inputs[role] = (stage, chooser, opaque_id)

        candidate_stage, candidate_chooser, _candidate_opaque = arm_inputs["candidate"]
        if candidate_chooser is None:
            raise CaptureError("candidate ref has no choose-work-profile skill")
        packaging_result = evaluate_work_profile_packaging(
            stage=candidate_stage,
            chooser=candidate_chooser,
        )
        packaging_inputs: list[dict[str, object]] = []
        for arm in ["inline", "conditional"]:
            for receipt_status in ["valid", "missing"]:
                materialized = (
                    candidate_stage + candidate_chooser
                    if arm == "inline" or receipt_status == "missing"
                    else candidate_stage
                )
                input_file = f"packaging-{arm}-{receipt_status}.input.md"
                (staging / input_file).write_bytes(materialized)
                observation = packaging_result[arm][f"{receipt_status}_receipt"]
                packaging_inputs.append(
                    {
                        "arm": arm,
                        "receipt_status": receipt_status,
                        "file": input_file,
                        "sha256": sha256(materialized),
                        "bytes": len(materialized),
                        "chooser_loaded": observation["chooser_loaded"],
                        "host_interaction_available": observation[
                            "host_interaction_available"
                        ],
                    }
                )

        slots: list[dict[str, object]] = []

        def add_slot(host: str, role: str, fixture_id: str, phase: str) -> None:
            stage, chooser, opaque_id = arm_inputs[role]
            prompt = work_profile_runner_prompt(
                stage=stage,
                chooser=chooser,
                fixture=fixture_by_id[fixture_id],
                phase=phase,
            )
            slot_number = len(slots) + 1
            prompt_file = (
                f"slot-{slot_number:02d}-{host}-{opaque_id}-{fixture_id}-{phase}.prompt.md"
            )
            (staging / prompt_file).write_bytes(prompt)
            slots.append(
                {
                    "slot": slot_number,
                    "host": host,
                    "provider": host,
                    "model": None,
                    "role": role,
                    "opaque_id": opaque_id,
                    "fixture_id": fixture_id,
                    "phase": phase,
                    "retry": 0,
                    "prompt_file": prompt_file,
                    "prompt_sha256": sha256(prompt),
                    "prompt_bytes": len(prompt),
                }
            )

        for fixture_id in WORK_PROFILE_IDS:
            add_slot("claude", "known_bad", fixture_id, "preselected")
            add_slot("claude", "candidate", fixture_id, "preselected")
        for fixture_id in ["P0-benign", "P3-adversarial-poc-label"]:
            add_slot("codex", "known_bad", fixture_id, "preselected")
            add_slot("codex", "candidate", fixture_id, "preselected")
        add_slot("claude", "candidate", "P1-limited-use", "question")
        add_slot("claude", "candidate", "P1-limited-use", "post-answer")
        add_slot("codex", "candidate", "P2-long-lived", "question")
        add_slot("codex", "candidate", "P2-long-lived", "post-answer")

        manifest: dict[str, object] = {
            "schema": "kc-dev-flow-work-profile-capture/v1",
            "mode": "work-profile-v1",
            "stage": "ideation",
            "tool": {"executable": str(executable), "version": version},
            "timebox": {
                "wall_clock_seconds": 1200,
                "preflight_seconds": 120,
                "model_stop_seconds": 900,
                "scoring_reserve_seconds": 300,
                "max_provider_responses": 16,
                "max_concurrency": 4,
                "retry_limit": 0,
            },
            "fixtures": fixture_manifest,
            "scorer": {
                "file": "score.jq",
                "sha256": sha256(scorer),
                "command": "jq -c -f score.jq <fixture-result-input.json>",
            },
            "arms": arms,
            "packaging": {
                "result": packaging_result,
                "inputs": packaging_inputs,
            },
            "slots": slots,
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
    parser = argparse.ArgumentParser(
        description=(
            "Capture exact known-bad and candidate stages through the installed "
            "Spacedock loader without running a model."
        )
    )
    parser.add_argument(
        "--mode",
        choices=["linked-policy-v1", "work-profile-v1"],
        default="linked-policy-v1",
    )
    parser.add_argument("--known-bad-ref", required=True)
    parser.add_argument("--candidate-ref", required=True)
    parser.add_argument(
        "--output-dir",
        required=True,
        type=Path,
        help="new operator-owned directory outside the repository",
    )
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument(
        "--fixture-dir",
        type=Path,
        default=DEFAULT_WORK_PROFILE_FIXTURE_DIR,
    )
    parser.add_argument("--repo", type=Path, default=ROOT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.mode == "work-profile-v1":
            manifest = capture_work_profile_pair(
                args.repo,
                args.known_bad_ref,
                args.candidate_ref,
                args.fixture_dir,
                args.output_dir,
            )
        else:
            manifest = capture_pair(
                args.repo,
                args.known_bad_ref,
                args.candidate_ref,
                args.fixture,
                args.output_dir,
            )
    except (CaptureError, OSError, ValueError) as exc:
        print(f"loader eval: FAIL — {exc}", file=sys.stderr)
        return 1
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
