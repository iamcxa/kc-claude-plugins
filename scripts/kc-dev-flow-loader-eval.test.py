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
        "receipt_status": "recorded-re-read",
        "obligation_ids": ["thin-real-journey", "critical-risk", "cleanup"],
        "surface_ids": ["shell-script", "input-file"],
        "test_ids": ["owned-logic", "critical-risk", "real-e2e"],
        "authority_stop_ids": [],
        "promotion_ids": [],
        "acceptance_criteria": [
            {
                "id": "AC-P0",
                "obligation_ids": ["thin-real-journey", "critical-risk", "cleanup"],
            }
        ],
        "final_status": "derived",
    }
    scorer_input = temp_root / "scorer-input.json"
    scorer_input.write_text(
        json.dumps({"fixture": fixture, "result": passing_result}), encoding="utf-8"
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
            "closed_result",
            "recommendation_match",
            "selection_allowed",
            "receipt_valid",
            "receipt_consumed",
            "required_obligations_pass",
            "required_tests_pass",
            "authority_stops_pass",
            "promotion_pass",
            "forbidden_obligation_count",
            "forbidden_surface_count",
            "safety_pass",
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
        json.dumps({"fixture": fixture, "result": bad_result}), encoding="utf-8"
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

print("kc-dev-flow loader eval test: PASS")
