#!/usr/bin/env python3
"""Capture two exact kc-dev-flow implementation stages through Spacedock."""

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


def capture_stage(
    executable: Path,
    workflow_dir: Path,
    revision: str,
) -> bytes:
    stage = command_output(
        [
            str(executable),
            "dispatch",
            "show-stage-def",
            "--workflow-dir",
            str(workflow_dir),
            "--stage",
            "implementation",
        ],
        label=f"capture {revision}",
    )
    if not stage:
        raise CaptureError(f"capture returned no implementation stage: {revision}")
    return stage


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Capture known-bad and candidate implementation stages through the "
            "installed Spacedock loader."
        )
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
    parser.add_argument("--repo", type=Path, default=ROOT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
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
