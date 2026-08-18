#!/usr/bin/env python3
"""Deterministic contract for the kc-dev-flow loader capture adapter."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import stat
import subprocess
import tempfile
from contextlib import contextmanager
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
ADAPTER_PATH = ROOT / "scripts/kc-dev-flow-loader-eval.py"
TRACKED_FIXTURE_PATH = ROOT / "scripts/fixtures/kc-dev-flow-loader-eval/q08.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"loader eval test: {message}")


def run(command: list[str], *, cwd: Path) -> str:
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    require(
        result.returncode == 0,
        f"command failed: {' '.join(command)}\n{result.stdout}{result.stderr}",
    )
    return result.stdout.strip()


def write_fixture(path: Path, **updates: object) -> None:
    fixture: dict[str, object] = {
        "schema": "kc-dev-flow-loader-eval-fixture/v1",
        "id": "Q08",
        "title": "Linked policy",
        "response_contract": (
            "Begin with a single uppercase route word summarizing the disposition. "
            "Then give ordered next actions, evidence or receipts needed, authority "
            "retained by each actor, intended state effects, and the stopping condition. "
            "Do not mutate anything."
        ),
        "scenario": (
            "The committed item selected Pilot and is in implementation. Its loader "
            "output contains only kernel, Pilot base, and Pilot build; the workflow "
            "also links PR delivery, validation, and recovery procedures. A worker has "
            "just recorded the first failing behavior check. No candidate revision, "
            "delivery request, validation trigger, or recovery incident exists. "
            "Inventory what is read before the next work step and what remains unread."
        ),
        "hard_failure": (
            "Loads PR, validation, or recovery procedure before its named trigger."
        ),
        "required_behavior": (
            "Read only the selected loader output; leave delivery, validation, and "
            "recovery procedures unloaded."
        ),
    }
    fixture.update(updates)
    path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")


def commit_workflow(repo: Path, body: bytes, message: str) -> str:
    workflow_dir = repo / "docs/dev"
    workflow_dir.mkdir(parents=True, exist_ok=True)
    (workflow_dir / "README.md").write_bytes(body)
    run(["git", "add", "docs/dev/README.md"], cwd=repo)
    run(["git", "commit", "-m", message], cwd=repo)
    return run(["git", "rev-parse", "HEAD"], cwd=repo)


def make_fake_spacedock(path: Path) -> None:
    path.write_text(
        """#!/usr/bin/env python3
import os
import pathlib
import sys

if sys.argv[1:] == ["--version"]:
    if os.environ.get("FAKE_SPACEDOCK_MODE") == "bad-version":
        print("unexpected version")
    else:
        print("spacedock 9.8.7 (contract 4)")
        if os.environ.get("FAKE_SPACEDOCK_MODE") == "multiline-version":
            print("Sandbox: available, not enabled")
            print("codex: spacedock 9.8.7")
    raise SystemExit(0)

if len(sys.argv) != 7 or sys.argv[1:3] != ["dispatch", "show-stage-def"]:
    print("unexpected arguments", file=sys.stderr)
    raise SystemExit(2)

workflow_dir = pathlib.Path(sys.argv[4])
stage = sys.argv[6]
if sys.argv[3] != "--workflow-dir" or sys.argv[5] != "--stage" or stage != "implementation":
    print("unexpected capture arguments", file=sys.stderr)
    raise SystemExit(2)

body = (workflow_dir / "README.md").read_bytes()
if os.environ.get("FAKE_SPACEDOCK_MODE") == "capture-failure" and b"candidate" in body:
    print("synthetic capture failure", file=sys.stderr)
    raise SystemExit(3)
sys.stdout.buffer.write(body)
""",
        encoding="utf-8",
    )
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


@contextmanager
def expected_failure(fragment: str):
    try:
        yield
    except Exception as exc:
        require(fragment in str(exc), f"expected {fragment!r}, got {exc!r}")
    else:
        raise SystemExit(f"loader eval test: expected failure containing {fragment!r}")


require(ADAPTER_PATH.is_file(), "capture adapter is missing")
spec = importlib.util.spec_from_file_location("kc_dev_flow_loader_eval", ADAPTER_PATH)
require(spec is not None and spec.loader is not None, "cannot load capture adapter")
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)
require(TRACKED_FIXTURE_PATH.is_file(), "tracked Q08 fixture is missing")
tracked_fixture = adapter.load_fixture(TRACKED_FIXTURE_PATH)[0]
require(
    tracked_fixture["id"] == "Q08"
    and tracked_fixture["hard_failure"]
    == "loads PR, validation, or recovery procedure before its named trigger."
    and tracked_fixture["required_behavior"]
    == (
        "Read only the selected loader output; leave delivery, validation, and "
        "recovery procedures unloaded."
    ),
    f"tracked Q08 grading contract drifted: {tracked_fixture!r}",
)


with tempfile.TemporaryDirectory(prefix="kc-dev-flow-loader-eval-test-") as temp:
    temp_root = Path(temp)
    repo = temp_root / "repo"
    repo.mkdir()
    run(["git", "init", "-q"], cwd=repo)
    run(["git", "config", "user.email", "loader-eval@example.invalid"], cwd=repo)
    run(["git", "config", "user.name", "Loader Eval Test"], cwd=repo)

    base_bytes = "base stage — café\n".encode()
    candidate_bytes = b"candidate stage\nwith trailing newline\n"
    base_sha = commit_workflow(repo, base_bytes, "fixture: base")
    candidate_sha = commit_workflow(repo, candidate_bytes, "fixture: candidate")
    blob_ref = run(["git", "rev-parse", "HEAD:docs/dev/README.md"], cwd=repo)

    fixture_path = temp_root / "q08.json"
    write_fixture(fixture_path)
    fixture_digest = hashlib.sha256(fixture_path.read_bytes()).hexdigest()
    fake_spacedock = temp_root / "spacedock"
    make_fake_spacedock(fake_spacedock)

    output = temp_root / "capture"
    with mock.patch.dict(os.environ, {"SPACEDOCK_BIN": str(fake_spacedock)}, clear=False):
        manifest = adapter.capture_pair(
            repo=repo,
            known_bad_ref="HEAD~1",
            candidate_ref="HEAD",
            fixture_path=fixture_path,
            output_dir=output,
        )

    require(output.is_dir(), "successful capture did not publish the output directory")
    on_disk = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    require(manifest == on_disk, "returned and published manifests differ")
    require(
        set(manifest) == {"schema", "stage", "tool", "fixture", "arms"}
        and manifest["schema"] == "kc-dev-flow-loader-eval/v1"
        and manifest["stage"] == "implementation",
        f"root manifest is not closed: {manifest!r}",
    )
    require(
        set(manifest["tool"]) == {"executable", "version"}
        and manifest["tool"]["executable"] == str(fake_spacedock.resolve())
        and manifest["tool"]["version"] == "spacedock 9.8.7 (contract 4)",
        f"tool provenance is incomplete: {manifest['tool']!r}",
    )
    require(
        set(manifest["fixture"]) == {"path", "sha256"}
        and manifest["fixture"]["path"] == str(fixture_path.resolve())
        and manifest["fixture"]["sha256"] == fixture_digest,
        f"fixture provenance is incomplete: {manifest['fixture']!r}",
    )

    arms = manifest["arms"]
    require(isinstance(arms, list) and len(arms) == 2, f"wrong arm count: {arms!r}")
    require(
        {arm["role"] for arm in arms} == {"known_bad", "candidate"}
        and len({arm["opaque_id"] for arm in arms}) == 2,
        f"arms are not separately mapped: {arms!r}",
    )
    expected = {
        "known_bad": ("HEAD~1", base_sha, base_bytes),
        "candidate": ("HEAD", candidate_sha, candidate_bytes),
    }
    hidden_text = json.loads(fixture_path.read_text(encoding="utf-8"))
    for arm in arms:
        require(
            set(arm)
            == {
                "role",
                "input_ref",
                "resolved_sha",
                "opaque_id",
                "stage_file",
                "stage_sha256",
                "stage_bytes",
                "prompt_file",
                "prompt_sha256",
                "prompt_bytes",
            },
            f"arm manifest is not closed: {arm!r}",
        )
        input_ref, resolved_sha, stage_bytes = expected[arm["role"]]
        stage_path = output / arm["stage_file"]
        prompt_path = output / arm["prompt_file"]
        prompt_bytes = prompt_path.read_bytes()
        prompt = prompt_bytes.decode("utf-8")
        require(
            arm["input_ref"] == input_ref
            and arm["resolved_sha"] == resolved_sha
            and stage_path.read_bytes() == stage_bytes
            and arm["stage_bytes"] == len(stage_bytes)
            and arm["stage_sha256"] == hashlib.sha256(stage_bytes).hexdigest(),
            f"stage bytes or exact ref drifted: {arm!r}",
        )
        require(
            hidden_text["response_contract"] in prompt
            and hidden_text["scenario"] in prompt
            and stage_bytes.decode("utf-8") in prompt
            and hidden_text["hard_failure"] not in prompt
            and hidden_text["required_behavior"] not in prompt
            and input_ref not in prompt
            and resolved_sha not in prompt
            and "known_bad" not in prompt
            and arm["prompt_bytes"] == len(prompt_bytes)
            and arm["prompt_sha256"] == hashlib.sha256(prompt_bytes).hexdigest(),
            f"runner prompt leaks hidden grading or identity data: {prompt!r}",
        )

    with mock.patch.dict(os.environ, {"SPACEDOCK_BIN": str(fake_spacedock)}, clear=False):
        with expected_failure("already exists"):
            adapter.capture_pair(repo, "HEAD~1", "HEAD", fixture_path, output)

        for label, ref in [("invalid", "missing-ref"), ("non-commit", blob_ref)]:
            rejected = temp_root / f"rejected-{label}"
            with expected_failure("commit"):
                adapter.capture_pair(repo, ref, "HEAD", fixture_path, rejected)
            require(not rejected.exists(), f"{label} ref left a published output")

        inside_checkout = repo / "capture"
        with expected_failure("outside the repository"):
            adapter.capture_pair(repo, "HEAD~1", "HEAD", fixture_path, inside_checkout)
        require(not inside_checkout.exists(), "inside-checkout target was created")

        malformed_fixture = temp_root / "malformed-q08.json"
        write_fixture(malformed_fixture, extra="not allowed")
        malformed_output = temp_root / "malformed-output"
        with expected_failure("fixture fields"):
            adapter.capture_pair(
                repo, "HEAD~1", "HEAD", malformed_fixture, malformed_output
            )
        require(not malformed_output.exists(), "invalid fixture left an output")

    bad_version_output = temp_root / "bad-version"
    with mock.patch.dict(
        os.environ,
        {"SPACEDOCK_BIN": str(fake_spacedock), "FAKE_SPACEDOCK_MODE": "bad-version"},
        clear=False,
    ):
        with expected_failure("version"):
            adapter.capture_pair(
                repo, "HEAD~1", "HEAD", fixture_path, bad_version_output
            )
    require(not bad_version_output.exists(), "bad version left an output")

    multiline_version_output = temp_root / "multiline-version"
    with mock.patch.dict(
        os.environ,
        {
            "SPACEDOCK_BIN": str(fake_spacedock),
            "FAKE_SPACEDOCK_MODE": "multiline-version",
        },
        clear=False,
    ):
        multiline_manifest = adapter.capture_pair(
            repo,
            "HEAD~1",
            "HEAD",
            fixture_path,
            multiline_version_output,
        )
    require(
        multiline_manifest["tool"]["version"] == "spacedock 9.8.7 (contract 4)",
        f"multiline version did not preserve canonical identity: {multiline_manifest!r}",
    )

    missing_executable_output = temp_root / "missing-executable"
    with mock.patch.dict(
        os.environ,
        {"SPACEDOCK_BIN": str(temp_root / "missing-spacedock")},
        clear=False,
    ):
        with expected_failure("executable"):
            adapter.capture_pair(
                repo, "HEAD~1", "HEAD", fixture_path, missing_executable_output
            )
    require(
        not missing_executable_output.exists(), "missing executable left an output"
    )

    failed_capture_output = temp_root / "failed-capture"
    with mock.patch.dict(
        os.environ,
        {
            "SPACEDOCK_BIN": str(fake_spacedock),
            "FAKE_SPACEDOCK_MODE": "capture-failure",
        },
        clear=False,
    ):
        with expected_failure("capture"):
            adapter.capture_pair(
                repo, "HEAD~1", "HEAD", fixture_path, failed_capture_output
            )
    require(not failed_capture_output.exists(), "failed capture published a receipt")

print("kc-dev-flow loader eval test: PASS")
