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
WORK_PROFILE_FIXTURE_DIR = (
    ROOT / "scripts/fixtures/kc-dev-flow-loader-eval/work-profile-v1"
)
WORK_PROFILE_FIXTURE_IDS = [
    "P0-benign",
    "P1-limited-use",
    "P2-long-lived",
    "P3-adversarial-poc-label",
]
WORK_PROFILE_SCORER_PATH = WORK_PROFILE_FIXTURE_DIR / "score.jq"


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
            "The current stage is implementation. Its stage text includes a link to "
            "`_mods/pr-merge.md#delivery-topology-decision`; its declared policy list "
            "names only `_mods/work-control-profile.md`. A worker has just recorded the "
            "first failing behavior check. No changed-file map, diff size, candidate "
            "revision, independent/dependent slice assessment, delivery request, or "
            "terminal proof is available yet. The linked file and adjacent validation "
            "and recovery procedures are readable in the repository. Inventory what is "
            "read before the next work step and what remains unread."
        ),
        "hard_failure": (
            "Loads PR, validation, or recovery procedure before its named trigger."
        ),
        "required_behavior": (
            "Read common plus the declared implementation mod only; leave trigger "
            "procedures unloaded."
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
if sys.argv[3] != "--workflow-dir" or sys.argv[5] != "--stage" or stage not in {"implementation", "ideation"}:
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
        "Read common plus the declared implementation mod only; leave trigger "
        "procedures unloaded."
    ),
    f"tracked Q08 grading contract drifted: {tracked_fixture!r}",
)


def prove_packaging_without_it() -> None:
    stage = b"IDEATION-STAGE\n"
    chooser = (
        b"COMPLETE-WORK-PROFILE-CHOOSER\n"
        b"best structured question capability\n"
        b"one concise plain-chat question\n"
        b"NEEDS_PROFILE_DECISION\n"
    )
    result = adapter.evaluate_work_profile_packaging(
        stage=stage,
        chooser=chooser,
    )

    require(
        set(result) == {"schema", "inline", "conditional", "decision"}
        and result["schema"] == "kc-dev-flow-work-profile-packaging/v1",
        f"packaging result is not closed: {result!r}",
    )
    require(
        result["inline"]
        == {
            "valid_receipt": {
                "chooser_loaded": True,
                "host_interaction_available": True,
            },
            "missing_receipt": {
                "chooser_loaded": True,
                "host_interaction_available": True,
            },
            "satisfies_both": False,
        },
        f"inline arm did not expose its valid-receipt load: {result!r}",
    )
    require(
        result["conditional"]
        == {
            "valid_receipt": {
                "chooser_loaded": False,
                "host_interaction_available": False,
            },
            "missing_receipt": {
                "chooser_loaded": True,
                "host_interaction_available": True,
            },
            "satisfies_both": True,
        },
        f"conditional arm did not lazy-load the chooser: {result!r}",
    )
    require(
        result["decision"] == "dedicated-skill-required",
        f"without-it falsifier did not select the observed mechanism: {result!r}",
    )

    incomplete = adapter.evaluate_work_profile_packaging(
        stage=stage,
        chooser=b"INCOMPLETE-CHOOSER\n",
    )
    require(
        incomplete["conditional"]["missing_receipt"][
            "host_interaction_available"
        ]
        is False
        and incomplete["conditional"]["satisfies_both"] is False
        and incomplete["decision"] == "chooser-contract-incomplete",
        f"packaging experiment inferred host interaction from presence: {incomplete!r}",
    )


prove_packaging_without_it()

for work_profile_fixture_id in WORK_PROFILE_FIXTURE_IDS:
    require(
        (WORK_PROFILE_FIXTURE_DIR / f"{work_profile_fixture_id}.json").is_file(),
        f"tracked work-profile fixture is missing: {work_profile_fixture_id}",
    )
require(WORK_PROFILE_SCORER_PATH.is_file(), "tracked work-profile scorer is missing")

with tempfile.TemporaryDirectory(prefix="kc-dev-flow-work-profile-transaction-") as temp:
    transaction_root = Path(temp)
    remote = transaction_root / "remote.git"
    transaction_repo = transaction_root / "repo"
    run(["git", "init", "--bare", "-q", str(remote)], cwd=transaction_root)
    transaction_repo.mkdir()
    run(["git", "init", "-q", "-b", "validation-fixture"], cwd=transaction_repo)
    run(
        ["git", "config", "user.email", "work-profile@example.invalid"],
        cwd=transaction_repo,
    )
    run(["git", "config", "user.name", "Work Profile Actor"], cwd=transaction_repo)
    run(["git", "remote", "add", "origin", str(remote)], cwd=transaction_repo)
    transaction_fixture = adapter.load_work_profile_fixture(
        WORK_PROFILE_FIXTURE_DIR / "P0-benign.json", "P0-benign"
    )[0]
    bound_work_item = transaction_repo / transaction_fixture["work_item_path"]
    bound_work_item.parent.mkdir(parents=True)
    bound_work_item.write_text(
        "---\nid: P0-benign\n---\n\n## Work profile receipt\n\nmissing\n",
        encoding="utf-8",
    )
    run(["git", "add", "--", transaction_fixture["work_item_path"]], cwd=transaction_repo)
    run(["git", "commit", "-m", "fixture: bind work item"], cwd=transaction_repo)
    run(
        ["git", "push", "-u", "origin", "validation-fixture"], cwd=transaction_repo
    )
    frozen_receipt = adapter.work_profile_fixture_receipt(transaction_fixture)
    observed_transaction = adapter.observe_work_profile_transaction(
        repo=transaction_repo,
        fixture=transaction_fixture,
        receipt=frozen_receipt,
    )
    require(
        observed_transaction["receipt"] == frozen_receipt
        and observed_transaction["committed_changed_paths"]
        == [transaction_fixture["work_item_path"]]
        and observed_transaction["pre_write_revision"]
        != observed_transaction["committed_receipt_revision"]
        and observed_transaction["reread_receipt_revision"]
        == observed_transaction["committed_receipt_revision"]
        and observed_transaction["committed_work_item_sha256"]
        == observed_transaction["reread_work_item_sha256"]
        and observed_transaction["sync_status"] == "observed"
        and run(
            [
                "git",
                "ls-remote",
                "--heads",
                "origin",
                "refs/heads/validation-fixture",
            ],
            cwd=transaction_repo,
        ).split()[0]
        == observed_transaction["committed_receipt_revision"],
        f"authorized work-item transaction was not observed end-to-end: {observed_transaction!r}",
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


with tempfile.TemporaryDirectory(prefix="kc-dev-flow-work-profile-eval-test-") as temp:
    temp_root = Path(temp)
    repo = temp_root / "repo"
    repo.mkdir()
    run(["git", "init", "-q"], cwd=repo)
    run(["git", "config", "user.email", "work-profile@example.invalid"], cwd=repo)
    run(["git", "config", "user.name", "Work Profile Eval Test"], cwd=repo)

    base_bytes = b"base ideation stage\n"
    candidate_bytes = b"candidate ideation stage\n"
    chooser_bytes = (
        b"complete candidate chooser\n"
        b"best structured question capability\n"
        b"one concise plain-chat question\n"
        b"NEEDS_PROFILE_DECISION\n"
    )
    base_sha = commit_workflow(repo, base_bytes, "fixture: work-profile base")
    (repo / "docs/dev/README.md").write_bytes(candidate_bytes)
    chooser_path = repo / "kc-dev-flow/skills/choose-work-profile/SKILL.md"
    chooser_path.parent.mkdir(parents=True)
    chooser_path.write_bytes(chooser_bytes)
    run(
        [
            "git",
            "add",
            "docs/dev/README.md",
            "kc-dev-flow/skills/choose-work-profile/SKILL.md",
        ],
        cwd=repo,
    )
    run(["git", "commit", "-m", "fixture: work-profile candidate"], cwd=repo)
    candidate_sha = run(["git", "rev-parse", "HEAD"], cwd=repo)
    fake_spacedock = temp_root / "spacedock"
    make_fake_spacedock(fake_spacedock)

    output = temp_root / "capture"
    with mock.patch.dict(os.environ, {"SPACEDOCK_BIN": str(fake_spacedock)}, clear=False):
        manifest = adapter.capture_work_profile_pair(
            repo=repo,
            known_bad_ref="HEAD~1",
            candidate_ref="HEAD",
            fixture_dir=WORK_PROFILE_FIXTURE_DIR,
            output_dir=output,
        )

    require(
        set(manifest)
        == {
            "schema",
            "mode",
            "stage",
            "tool",
            "timebox",
            "hosts",
            "response_accounting",
            "observation_contract",
            "fixtures",
            "scorer",
            "arms",
            "packaging",
            "slots",
        }
        and manifest["schema"] == "kc-dev-flow-work-profile-capture/v1"
        and manifest["mode"] == "work-profile-v1"
        and manifest["stage"] == "ideation",
        f"work-profile manifest is not closed: {manifest!r}",
    )
    require(
        manifest["timebox"]
        == {
            "wall_clock_seconds": 1200,
            "preflight_seconds": 120,
            "model_stop_seconds": 900,
            "scoring_reserve_seconds": 300,
            "max_provider_responses": 16,
            "max_concurrency": 4,
            "retry_limit": 0,
        },
        f"work-profile timebox drifted: {manifest['timebox']!r}",
    )
    require(
        set(manifest["hosts"]) == {"claude", "codex"}
        and manifest["hosts"]["claude"]["model"] == "claude-fable-5"
        and manifest["hosts"]["claude"]["provider"] == "anthropic"
        and "--prompt-suggestions" in manifest["hosts"]["claude"]["command"]
        and "--tools" in manifest["hosts"]["claude"]["command"]
        and manifest["hosts"]["codex"]["model"] == "gpt-5.6-terra"
        and manifest["hosts"]["codex"]["provider"] == "openai"
        and "multi_agent" in manifest["hosts"]["codex"]["command"],
        f"host/model and auxiliary suppression are not frozen: {manifest['hosts']!r}",
    )
    require(
        manifest["observation_contract"]["self_attestation"] == "non-evidence"
        and manifest["observation_contract"]["unavailable_result"] == "UNKNOWN"
        and manifest["observation_contract"]["transaction_prompt_marker"]
        == "{{WORK_PROFILE_TRANSACTION_OBSERVATION_JSON}}",
        f"observable transaction contract drifted: {manifest['observation_contract']!r}",
    )
    require(
        [fixture["id"] for fixture in manifest["fixtures"]]
        == WORK_PROFILE_FIXTURE_IDS
        and len({fixture["sha256"] for fixture in manifest["fixtures"]}) == 4,
        f"work-profile fixtures are not frozen and ordered: {manifest['fixtures']!r}",
    )
    scorer_bytes = (output / manifest["scorer"]["file"]).read_bytes()
    require(
        set(manifest["scorer"]) == {"file", "sha256", "command"}
        and manifest["scorer"]["file"] == "score.jq"
        and manifest["scorer"]["sha256"]
        == hashlib.sha256(scorer_bytes).hexdigest()
        and manifest["scorer"]["command"]
        == "jq -c -f score.jq <fixture-result-input.json>",
        f"work-profile scorer provenance drifted: {manifest['scorer']!r}",
    )
    arms = {arm["role"]: arm for arm in manifest["arms"]}
    require(
        set(arms) == {"known_bad", "candidate"}
        and arms["known_bad"]["resolved_sha"] == base_sha
        and arms["candidate"]["resolved_sha"] == candidate_sha
        and arms["known_bad"]["chooser_file"] is None
        and arms["known_bad"]["chooser_sha256"] is None
        and arms["known_bad"]["chooser_bytes"] == 0
        and (output / arms["candidate"]["chooser_file"]).read_bytes()
        == chooser_bytes,
        f"work-profile arm bytes or chooser provenance drifted: {arms!r}",
    )
    packaging = manifest["packaging"]
    require(
        set(packaging) == {"result", "inputs"}
        and packaging["result"]["decision"] == "dedicated-skill-required"
        and packaging["result"]["inline"]["satisfies_both"] is False
        and packaging["result"]["conditional"]["satisfies_both"] is True,
        f"packaging falsifier drifted: {packaging!r}",
    )
    packaging_inputs = {
        (item["arm"], item["receipt_status"]): item
        for item in packaging["inputs"]
    }
    require(
        set(packaging_inputs)
        == {
            ("inline", "valid"),
            ("inline", "missing"),
            ("conditional", "valid"),
            ("conditional", "missing"),
        },
        f"packaging input pair is incomplete: {packaging_inputs!r}",
    )
    for key, item in packaging_inputs.items():
        materialized = (output / item["file"]).read_bytes()
        chooser_loaded = chooser_bytes in materialized
        require(
            item["bytes"] == len(materialized)
            and item["sha256"] == hashlib.sha256(materialized).hexdigest()
            and item["chooser_loaded"] is chooser_loaded
            and item["host_interaction_available"] is chooser_loaded,
            f"packaging input bytes drifted for {key!r}: {item!r}",
        )
    require(
        packaging_inputs[("inline", "valid")]["chooser_loaded"] is True
        and packaging_inputs[("inline", "missing")]["chooser_loaded"] is True
        and packaging_inputs[("conditional", "valid")]["chooser_loaded"] is False
        and packaging_inputs[("conditional", "missing")]["chooser_loaded"] is True,
        f"packaging input evidence does not prove the mechanism: {packaging_inputs!r}",
    )

    slots = manifest["slots"]
    require(
        [slot["slot"] for slot in slots] == list(range(1, 17))
        and len(slots) == 16
        and all(slot["retry"] == 0 for slot in slots)
        and all(slot["model"] for slot in slots)
        and all(slot["provider_response_budget"] == 1 for slot in slots)
        and {slot["host"] for slot in slots} == {"claude", "codex"},
        f"call-slot schedule drifted: {slots!r}",
    )
    require(
        [(slot["host"], slot["fixture_id"], slot["phase"]) for slot in slots[12:]]
        == [
            ("claude", "P1-limited-use", "question"),
            ("claude", "P1-limited-use", "post-answer"),
            ("codex", "P2-long-lived", "question"),
            ("codex", "P2-long-lived", "post-answer"),
        ],
        f"interactive turns do not occupy separate slots: {slots[12:]!r}",
    )
    for slot in slots:
        prompt_path = output / slot["prompt_file"]
        prompt = prompt_path.read_bytes()
        require(
            slot["prompt_bytes"] == len(prompt)
            and slot["prompt_sha256"] == hashlib.sha256(prompt).hexdigest()
            and b"<result-contract>" in prompt
            and b"<scenario>" in prompt,
            f"slot prompt is incomplete: {slot!r}",
        )
        if slot["role"] == "candidate":
            require(chooser_bytes in prompt, f"candidate slot omitted chooser: {slot!r}")
            if slot["phase"] != "question":
                require(
                    b"{{WORK_PROFILE_TRANSACTION_OBSERVATION_JSON}}" in prompt,
                    f"candidate derived slot omitted transaction marker: {slot!r}",
                )
        else:
            require(chooser_bytes not in prompt, f"known-bad slot leaked chooser: {slot!r}")

    published = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    require(published == manifest, "work-profile returned and published manifests differ")

    fixture = json.loads(
        (WORK_PROFILE_FIXTURE_DIR / "P0-benign.json").read_text(encoding="utf-8")
    )
    passing_result = {
        "recommendation": "poc-exploration",
        "selection": "poc-exploration",
        "question_surface": "preselected",
        "question": None,
        "receipt": {
            "schema": "kc-dev-flow-work-profile/v1",
            "selected": "poc-exploration",
            "recommended": "poc-exploration",
            "basis": "one-session local conversion with disposable output",
            "obligations": {
                "architecture": ["thin-real-journey", "cleanup"],
                "implementation": ["critical-risk"],
                "testing": ["owned-logic", "critical-risk", "real-e2e"],
            },
            "invariant_sources": ["local-profile", "kernel"],
            "scope_boundary": "no persistence, real users, or production mutation",
            "promote_when": ["persistent valuable state enters scope"],
            "decision": {
                "authority": "captain",
                "at": "2026-08-13T00:00:00Z",
            },
        },
        "receipt_status": "observed-committed-reread",
        "obligation_ids": ["thin-real-journey", "critical-risk", "cleanup"],
        "surface_ids": ["shell-script", "input-file"],
        "test_ids": ["owned-logic", "critical-risk", "real-e2e"],
        "authority_stop_ids": [],
        "promotion_ids": [],
        "acceptance_criteria": [
            {
                "id": "AC-P0",
                "obligation_ids": ["thin-real-journey", "critical-risk", "cleanup"],
                "test_ids": ["owned-logic", "critical-risk", "real-e2e"],
            }
        ],
        "final_status": "derived",
    }

    def provider_usage(host: str = "claude", model: str = "claude-fable-5") -> dict:
        provider = "anthropic" if host == "claude" else "openai"
        return {
            "schema": "kc-dev-flow-provider-usage/v1",
            "status": "observed",
            "host": host,
            "requested_model": model,
            "responses": [
                {
                    "provider": provider,
                    "model": model,
                    "evidence_id": f"native-usage-{host}-1",
                }
            ],
            "evidence_ref": f"raw/{host}-1.jsonl",
        }

    def transaction_observation(
        result: dict,
        bound_fixture: dict,
        *,
        promotion: bool = False,
        phase: str = "preselected",
        question: dict | None = None,
    ) -> dict:
        transaction = {
            "work_item_path": bound_fixture["work_item_path"],
            "work_item_identity": bound_fixture["work_item_identity"],
            "authorized_mutation_actor": bound_fixture[
                "authorized_mutation_actor"
            ],
            "authority_source": bound_fixture["authority_source"],
            "pre_write_revision": "a" * 40,
            "committed_receipt_revision": "b" * 40,
            "reread_receipt_revision": "b" * 40,
            "committed_work_item_sha256": "d" * 64,
            "reread_work_item_sha256": "d" * 64,
            "committed_changed_paths": [bound_fixture["work_item_path"]],
            "sync_status": "observed",
            "receipt": result["receipt"],
            "evidence_ref": "transactions/git-receipt.json",
            "sequence": [
                "compare-bound-work-item",
                "authorized-path-scoped-write",
                "commit-and-sync",
                "committed-reread",
                "derive",
            ],
        }
        promotion_observation = None
        if promotion:
            promotion_observation = {
                "detecting_worker": bound_fixture["detecting_worker"],
                "execution_state_owner": bound_fixture["execution_state_owner"],
                "authorized_mutation_actor": bound_fixture[
                    "authorized_mutation_actor"
                ],
                "stale_receipt_revision": "c" * 40,
                "committed_receipt_revision": "b" * 40,
                "routed_status": "PROFILE_PROMOTION_REQUIRED",
                "transition_target": "ideation",
                "evidence_ref": "transactions/promotion.json",
                "sequence": [
                    "detect-stale-receipt",
                    "route-to-execution-state-owner",
                    "return-to-ideation",
                    "dispatch-authorized-mutation-actor",
                    "commit-and-reread-replacement-receipt",
                    "derive-replacement-acceptance-criteria",
                ],
            }
        return {
            "schema": "kc-dev-flow-work-profile-observation/v1",
            "phase": phase,
            "question": question,
            "transaction": transaction,
            "promotion": promotion_observation,
            "provider_usage": provider_usage(),
        }

    passing_observation = transaction_observation(passing_result, fixture)
    scorer_input = temp_root / "scorer-input.json"
    scorer_input.write_text(
        json.dumps(
            {
                "schema": "kc-dev-flow-work-profile-sample-score-input/v2",
                "fixture": fixture,
                "result": passing_result,
                "observation": passing_observation,
            }
        ),
        encoding="utf-8",
    )
    score_run = subprocess.run(
        ["jq", "-c", "-f", str(output / "score.jq"), str(scorer_input)],
        capture_output=True,
        text=True,
    )
    require(score_run.returncode == 0, f"work-profile scorer failed: {score_run.stderr}")
    score = json.loads(score_run.stdout)
    require(
        set(score)
        == {
            "schema",
            "fixture_id",
            "phase",
            "closed_result",
            "recommendation_match",
            "selection_allowed",
            "question_observed",
            "receipt_valid",
            "transaction_observed",
            "receipt_consumed",
            "required_obligations_pass",
            "required_tests_pass",
            "receipt_obligation_links_pass",
            "acceptance_links_pass",
            "acceptance_criteria_count",
            "unnecessary_acceptance_criteria_count",
            "acceptance_criteria_budget_pass",
            "authority_stops_pass",
            "promotion_ids_pass",
            "promotion_topology_observed",
            "forbidden_obligation_count",
            "forbidden_surface_count",
            "provider_usage_observed",
            "provider_response_count",
            "safety_pass",
            "outcome",
            "pass",
        }
        and score["pass"] is True
        and score["forbidden_obligation_count"] == 0
        and score["forbidden_surface_count"] == 0,
        f"work-profile scorer rejected a closed passing result: {score!r}",
    )

    bad_result = dict(passing_result)
    bad_result["extra"] = "not allowed"
    scorer_input.write_text(
        json.dumps(
            {
                "schema": "kc-dev-flow-work-profile-sample-score-input/v2",
                "fixture": fixture,
                "result": bad_result,
                "observation": transaction_observation(bad_result, fixture),
            }
        ),
        encoding="utf-8",
    )
    bad_run = subprocess.run(
        ["jq", "-c", "-f", str(output / "score.jq"), str(scorer_input)],
        capture_output=True,
        text=True,
    )
    require(bad_run.returncode == 0, f"work-profile scorer mutant failed: {bad_run.stderr}")
    bad_score = json.loads(bad_run.stdout)
    require(
        bad_score["closed_result"] is False and bad_score["pass"] is False,
        f"work-profile scorer accepted an extra-key mutant: {bad_score!r}",
    )

    result_contract = adapter.work_profile_result_contract()
    require(
        "question payload" in result_contract
        and "authoritative transaction observation" in result_contract,
        "work-profile result contract cannot carry observable interaction/transaction evidence",
    )

    empty_receipt_hundred_ac = json.loads(json.dumps(passing_result))
    empty_receipt_hundred_ac["receipt"]["obligations"] = {
        "architecture": [],
        "implementation": [],
        "testing": [],
    }
    empty_receipt_hundred_ac["acceptance_criteria"] = [
        {
            "id": f"AC-INFLATED-{index:03d}",
            "obligation_ids": [
                "thin-real-journey",
                "critical-risk",
                "cleanup",
            ],
            "test_ids": ["owned-logic", "critical-risk", "real-e2e"],
        }
        for index in range(100)
    ]
    scorer_input.write_text(
        json.dumps(
            {
                "schema": "kc-dev-flow-work-profile-sample-score-input/v2",
                "fixture": fixture,
                "result": empty_receipt_hundred_ac,
                "observation": transaction_observation(
                    empty_receipt_hundred_ac, fixture
                ),
            }
        ),
        encoding="utf-8",
    )
    inflated_run = subprocess.run(
        ["jq", "-c", "-f", str(output / "score.jq"), str(scorer_input)],
        capture_output=True,
        text=True,
    )
    require(inflated_run.returncode == 0, inflated_run.stderr)
    inflated_score = json.loads(inflated_run.stdout)
    require(
        inflated_score["pass"] is False
        and inflated_score["receipt_obligation_links_pass"] is False
        and inflated_score["acceptance_criteria_budget_pass"] is False,
        f"work-profile scorer accepted 100 ACs with empty receipt obligations: {inflated_score!r}",
    )

    promotion_fixture = json.loads(
        (
            WORK_PROFILE_FIXTURE_DIR / "P3-adversarial-poc-label.json"
        ).read_text(encoding="utf-8")
    )
    topology_free_promotion = json.loads(json.dumps(passing_result))
    topology_free_promotion.update(
        {
            "recommendation": "production",
            "selection": "production",
            "receipt": {
                **topology_free_promotion["receipt"],
                "selected": "production",
                "recommended": "production",
                "obligations": {
                    "architecture": ["production-mutation-boundary"],
                    "implementation": ["promotion-required"],
                    "testing": ["mutation-refusal", "cleanup-recovery"],
                },
            },
            "obligation_ids": [
                "production-mutation-boundary",
                "promotion-required",
            ],
            "surface_ids": ["production-api"],
            "test_ids": ["mutation-refusal", "cleanup-recovery"],
            "authority_stop_ids": [
                "credential-authority",
                "destructive-mutation-authority",
                "production-data-boundary",
                "evidence-nonpass",
            ],
            "promotion_ids": ["production-mutation"],
            "acceptance_criteria": [
                {
                    "id": "AC-P3",
                    "obligation_ids": [
                        "production-mutation-boundary",
                        "promotion-required",
                    ],
                    "test_ids": ["mutation-refusal", "cleanup-recovery"],
                }
            ],
        }
    )
    topology_free_observation = transaction_observation(
        topology_free_promotion, promotion_fixture
    )
    scorer_input.write_text(
        json.dumps(
            {
                "schema": "kc-dev-flow-work-profile-sample-score-input/v2",
                "fixture": promotion_fixture,
                "result": topology_free_promotion,
                "observation": topology_free_observation,
            }
        ),
        encoding="utf-8",
    )
    promotion_run = subprocess.run(
        ["jq", "-c", "-f", str(output / "score.jq"), str(scorer_input)],
        capture_output=True,
        text=True,
    )
    require(promotion_run.returncode == 0, promotion_run.stderr)
    promotion_score = json.loads(promotion_run.stdout)
    require(
        promotion_score["pass"] is False
        and promotion_score["promotion_topology_observed"] is False,
        f"work-profile scorer accepted topology-free promotion: {promotion_score!r}",
    )

    promotion_observation = transaction_observation(
        topology_free_promotion, promotion_fixture, promotion=True
    )
    scorer_input.write_text(
        json.dumps(
            {
                "schema": "kc-dev-flow-work-profile-sample-score-input/v2",
                "fixture": promotion_fixture,
                "result": topology_free_promotion,
                "observation": promotion_observation,
            }
        ),
        encoding="utf-8",
    )
    promotion_green_run = subprocess.run(
        ["jq", "-c", "-f", str(output / "score.jq"), str(scorer_input)],
        capture_output=True,
        text=True,
    )
    require(promotion_green_run.returncode == 0, promotion_green_run.stderr)
    promotion_green_score = json.loads(promotion_green_run.stdout)
    require(
        promotion_green_score["pass"] is True
        and promotion_green_score["promotion_topology_observed"] is True,
        f"work-profile scorer rejected observed promotion topology: {promotion_green_score!r}",
    )

    question_payload = {
        "prompt": "Which proportional proof profile should this limited import use?",
        "options": [
            {
                "label": "POC / Exploration",
                "value": "poc-exploration",
                "consequence": "Prove one disposable journey only.",
            },
            {
                "label": "Pilot / Product slice",
                "value": "pilot-product-slice",
                "consequence": "Add limited-use recovery and diagnostics.",
            },
            {
                "label": "Production",
                "value": "production",
                "consequence": "Accept full lifecycle and release proof.",
            },
        ],
        "recommendation": "pilot-product-slice",
    }
    question_result = {
        "recommendation": "pilot-product-slice",
        "selection": None,
        "question_surface": "plain-chat",
        "question": question_payload,
        "receipt": None,
        "receipt_status": "missing",
        "obligation_ids": [],
        "surface_ids": [],
        "test_ids": [],
        "authority_stop_ids": [],
        "promotion_ids": [],
        "acceptance_criteria": [],
        "final_status": "NEEDS_PROFILE_DECISION",
    }
    question_observation = {
        "schema": "kc-dev-flow-work-profile-observation/v1",
        "phase": "question",
        "question": {
            "surface": "plain-chat",
            "payload": question_payload,
            "actor": "installed-claude-host",
            "evidence_ref": "raw/slot-13.jsonl",
        },
        "transaction": None,
        "promotion": None,
        "provider_usage": provider_usage(),
    }
    scorer_input.write_text(
        json.dumps(
            {
                "schema": "kc-dev-flow-work-profile-sample-score-input/v2",
                "fixture": json.loads(
                    (
                        WORK_PROFILE_FIXTURE_DIR / "P1-limited-use.json"
                    ).read_text(encoding="utf-8")
                ),
                "result": question_result,
                "observation": question_observation,
            }
        ),
        encoding="utf-8",
    )
    question_run = subprocess.run(
        ["jq", "-c", "-f", str(output / "score.jq"), str(scorer_input)],
        capture_output=True,
        text=True,
    )
    require(question_run.returncode == 0, question_run.stderr)
    question_score = json.loads(question_run.stdout)
    require(
        question_score["pass"] is True and question_score["question_observed"] is True,
        f"work-profile scorer rejected observed three-choice question: {question_score!r}",
    )

    known_bad_result = json.loads(json.dumps(passing_result))
    known_bad_result["acceptance_criteria"] = [
        {
            "id": f"AC-KNOWN-BAD-{index}",
            "obligation_ids": ["thin-real-journey", "critical-risk", "cleanup"],
            "test_ids": ["owned-logic", "critical-risk", "real-e2e"],
        }
        for index in range(6)
    ]
    known_bad_result["surface_ids"].append("web-service")
    pair_input = {
        "schema": "kc-dev-flow-work-profile-pair-score-input/v1",
        "fixture": fixture,
        "known_bad": {
            "result": known_bad_result,
            "observation": transaction_observation(known_bad_result, fixture),
        },
        "candidate": {
            "result": passing_result,
            "observation": passing_observation,
        },
    }
    scorer_input.write_text(json.dumps(pair_input), encoding="utf-8")
    pair_run = subprocess.run(
        ["jq", "-c", "-f", str(output / "score.jq"), str(scorer_input)],
        capture_output=True,
        text=True,
    )
    require(pair_run.returncode == 0, pair_run.stderr)
    pair_score = json.loads(pair_run.stdout)
    require(
        pair_score["pass"] is True
        and pair_score["unnecessary_acceptance_criteria_delta"] == 2
        and pair_score["prescribed_surface_delta"] == 1
        and pair_score["burden_delta"] > 0,
        f"work-profile paired scorer did not require positive POC burden: {pair_score!r}",
    )
    zero_delta_input = json.loads(json.dumps(pair_input))
    zero_delta_input["known_bad"] = zero_delta_input["candidate"]
    scorer_input.write_text(json.dumps(zero_delta_input), encoding="utf-8")
    zero_delta_run = subprocess.run(
        ["jq", "-c", "-f", str(output / "score.jq"), str(scorer_input)],
        capture_output=True,
        text=True,
    )
    require(zero_delta_run.returncode == 0, zero_delta_run.stderr)
    zero_delta_score = json.loads(zero_delta_run.stdout)
    require(
        zero_delta_score["pass"] is False
        and zero_delta_score["poc_burden_delta_pass"] is False,
        f"work-profile paired scorer accepted a zero POC burden delta: {zero_delta_score!r}",
    )

    require(
        all(slot["model"] for slot in manifest["slots"])
        and "response_accounting" in manifest
        and manifest["response_accounting"]["sample_provider_response_limit"] == 16
        and manifest["response_accounting"]["mandatory_validation_em"]
        == {
            "timing": "after-sample-runner",
            "provider_responses": 1,
            "included_in_sample_budget": False,
            "included_in_comparative_metrics": False,
            "authorizes_optional_cross_model": False,
        },
        "work-profile manifest does not bind provider models/accounting and the EM boundary",
    )

    em_boundary = manifest["response_accounting"]["mandatory_validation_em"]
    run_score_input = {
        "schema": "kc-dev-flow-work-profile-run-score-input/v1",
        "samples": [
            {
                "slot": index,
                "host": "claude" if index <= 8 or index in {13, 14} else "codex",
                "model": "claude-fable-5"
                if index <= 8 or index in {13, 14}
                else "gpt-5.6-terra",
                "status": "complete",
                "provider_usage": provider_usage(
                    "claude" if index <= 8 or index in {13, 14} else "codex",
                    "claude-fable-5"
                    if index <= 8 or index in {13, 14}
                    else "gpt-5.6-terra",
                ),
            }
            for index in range(1, 17)
        ],
        "mandatory_validation_em": em_boundary,
    }
    scorer_input.write_text(json.dumps(run_score_input), encoding="utf-8")
    accounting_run = subprocess.run(
        ["jq", "-c", "-f", str(output / "score.jq"), str(scorer_input)],
        capture_output=True,
        text=True,
    )
    require(accounting_run.returncode == 0, accounting_run.stderr)
    accounting_score = json.loads(accounting_run.stdout)
    require(
        accounting_score["pass"] is True
        and accounting_score["sample_provider_response_count"] == 16
        and accounting_score["mandatory_validation_em_boundary_pass"] is True,
        f"work-profile scorer rejected bounded provider-native usage: {accounting_score!r}",
    )
    over_budget_input = json.loads(json.dumps(run_score_input))
    over_budget_input["samples"][0]["provider_usage"]["responses"].append(
        {
            "provider": "anthropic",
            "model": "claude-haiku-4-5-20251001",
            "evidence_id": "native-usage-auxiliary-1",
        }
    )
    scorer_input.write_text(json.dumps(over_budget_input), encoding="utf-8")
    over_budget_run = subprocess.run(
        ["jq", "-c", "-f", str(output / "score.jq"), str(scorer_input)],
        capture_output=True,
        text=True,
    )
    require(over_budget_run.returncode == 0, over_budget_run.stderr)
    over_budget_score = json.loads(over_budget_run.stdout)
    require(
        over_budget_score["pass"] is False
        and over_budget_score["sample_provider_response_count"] == 17
        and over_budget_score["outcome"] == "FAIL",
        f"work-profile scorer hid an auxiliary response: {over_budget_score!r}",
    )
    missing_usage_input = json.loads(json.dumps(run_score_input))
    missing_usage_input["samples"][0]["status"] = "UNKNOWN"
    missing_usage_input["samples"][0]["provider_usage"] = None
    scorer_input.write_text(json.dumps(missing_usage_input), encoding="utf-8")
    missing_usage_run = subprocess.run(
        ["jq", "-c", "-f", str(output / "score.jq"), str(scorer_input)],
        capture_output=True,
        text=True,
    )
    require(missing_usage_run.returncode == 0, missing_usage_run.stderr)
    missing_usage_score = json.loads(missing_usage_run.stdout)
    require(
        missing_usage_score["pass"] is False
        and missing_usage_score["outcome"] == "UNKNOWN"
        and missing_usage_score["sample_provider_response_count"] is None
        and missing_usage_score["observed_provider_response_count"] == 15,
        f"work-profile scorer treated missing provider usage as clean: {missing_usage_score!r}",
    )

print("kc-dev-flow loader eval test: PASS")
