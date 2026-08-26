#!/usr/bin/env python3
"""Focused behavioral contract for the mandatory published-tag smoke."""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SMOKE_PATH = ROOT / "scripts/kc-dev-flow-published-tag-smoke.py"
SPEC = importlib.util.spec_from_file_location("kc_dev_flow_published_tag_smoke", SMOKE_PATH)
if SPEC is None or SPEC.loader is None:
    raise SystemExit("cannot import published-tag smoke")
smoke = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(smoke)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"published-tag smoke test: {message}")


def capture(action):
    try:
        return action(), ""
    except Exception as exc:
        return None, str(exc)


def report_data(revision: str) -> dict[str, object]:
    return {
        "science_officer_em_upward_report": {
            "em_judgment": "proceed",
            "evidence_synthesis": "installed host output",
            "risk_tradeoff_call": "reversible and bounded",
            "recommendation": "proceed through normal delivery",
            "route": "proceed",
            "confidence": "high",
            "multi_model": "not_needed",
            "fo_boundary": "",
            "engineering_judgment": {
                "question": "Does the installed compatibility envelope close?",
                "revision": revision,
                "evidence_synthesis": "installed host output",
                "adjudications": [
                    {
                        "finding": "runtime contract is present",
                        "disposition": "supported",
                        "basis": "installed host output",
                    }
                ],
                "risk_tradeoff": "reversible and bounded",
                "recommendation": "proceed through normal delivery",
                "route": "proceed",
                "confidence": "high",
                "dissent": "",
                "disproof_condition": "a required field or host is missing",
                "authority_boundary": "captain and delivery owners retain authority",
            },
        }
    }


def report(revision: str) -> str:
    return json.dumps(report_data(revision))


def expect_error(action, fragment: str, label: str) -> None:
    _result, error = capture(action)
    require(fragment in error, f"{label} was accepted or failed differently: {error!r}")


REVISION = "a" * 40
smoke.validate_report(report(REVISION), REVISION)

invalid_reports: list[tuple[str, str, str]] = [
    ("malformed", "not json", "structural"),
    ("wrong revision", report(REVISION), "revision"),
]
missing = report_data(REVISION)
del missing["science_officer_em_upward_report"]["engineering_judgment"][
    "disproof_condition"
]
invalid_reports.append(("missing field", json.dumps(missing), "disproof_condition"))
extra = report_data(REVISION)
extra["science_officer_em_upward_report"]["engineering_judgment"]["adjudications"][
    0
]["verdict_note"] = "not part of the closed record"
invalid_reports.append(("extra field", json.dumps(extra), "verdict_note"))
duplicate = report(REVISION).replace(
    '"route": "proceed",', '"route": "proceed", "route": "return",', 1
)
invalid_reports.append(("duplicate key", duplicate, "duplicate"))
invalid_enum = report_data(REVISION)
invalid_enum["science_officer_em_upward_report"]["route"] = "maybe"
invalid_enum["science_officer_em_upward_report"]["engineering_judgment"][
    "route"
] = "maybe"
invalid_reports.append(("invalid enum", json.dumps(invalid_enum), "route"))

for label, document, fragment in invalid_reports:
    expected = "b" * 40 if label == "wrong revision" else REVISION
    expect_error(
        lambda document=document, expected=expected: smoke.validate_report(
            document, expected
        ),
        fragment,
        label,
    )

with mock.patch.object(
    sys, "argv", ["smoke", "candidate", "--receipt", "/tmp/candidate.json"]
):
    candidate_args = smoke.parse_args()
with mock.patch.object(
    sys,
    "argv",
    [
        "smoke",
        "published",
        "kc-dev-flow-v2.5.0",
        "--candidate-receipt",
        "/tmp/candidate.json",
    ],
):
    published_args = smoke.parse_args()
require(
    candidate_args.mode == "candidate"
    and candidate_args.receipt == Path("/tmp/candidate.json")
    and published_args.mode == "published"
    and published_args.candidate_receipt == Path("/tmp/candidate.json"),
    "candidate and published CLI modes drifted",
)

plugin = ROOT / "kc-dev-flow"
version = smoke.installed_version(plugin)
claude_events = [
    {
        "type": "system",
        "subtype": "init",
        "plugins": [{"name": "kc-dev-flow", "version": version, "path": str(plugin)}],
    },
    {
        "type": "result",
        "result": json.dumps(extra),
        "structured_output": report_data(REVISION),
    },
]
structured = smoke.claude_stream_result(
    "\n".join(json.dumps(event) for event in claude_events), plugin, version
)
require(
    json.loads(structured) == report_data(REVISION),
    "Claude extraction ignored structured_output",
)
del claude_events[-1]["structured_output"]
expect_error(
    lambda: smoke.claude_stream_result(
        "\n".join(json.dumps(event) for event in claude_events), plugin, version
    ),
    "structured_output",
    "Claude result-text fallback",
)

codex_output = json.dumps(
    {
        "type": "item.completed",
        "item": {"type": "agent_message", "text": report(REVISION)},
    }
)
require(smoke.codex_result(codex_output) == report(REVISION), "Codex extraction drifted")
expect_error(lambda: smoke.codex_result("{}"), "no final", "empty Codex output")


def git(repo: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments], cwd=repo, check=True, capture_output=True, text=True
    ).stdout.strip()


def initialize_snapshot_fixture(repo: Path) -> str:
    plugin = repo / "kc-dev-flow"
    assets = plugin / "skills/setup-github-project-projection/assets"
    assets.mkdir(parents=True)
    (repo / ".claude-plugin").mkdir()
    (repo / ".gitignore").write_text("__pycache__/\n", encoding="utf-8")
    marketplace = {"name": "fixture", "plugins": [{"name": "kc-dev-flow", "version": "2.5.0"}]}
    (repo / ".claude-plugin/marketplace.json").write_text(json.dumps(marketplace), encoding="utf-8")
    for host in ["claude", "codex"]:
        manifest = plugin / f".{host}-plugin/plugin.json"
        manifest.parent.mkdir(parents=True)
        manifest.write_text('{"version":"2.5.0"}\n', encoding="utf-8")
    (assets / "install-projection.py").write_text("print('v1')\n", encoding="utf-8")
    (assets / "project-spacedock-state.py").write_text("print('v1')\n", encoding="utf-8")
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "smoke@example.test")
    git(repo, "config", "user.name", "Smoke Test")
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "fixture")
    return git(repo, "rev-parse", "HEAD")


with tempfile.TemporaryDirectory(prefix="kc-dev-flow-snapshot-test-") as temporary:
    fixture_root = Path(temporary)
    fixture_repo = fixture_root / "repo"
    fixture_repo.mkdir()
    clean_revision = initialize_snapshot_fixture(fixture_repo)
    clean_snapshot = fixture_root / "clean"
    smoke.tracked_package_snapshot(fixture_repo, clean_revision, clean_snapshot, 30)
    clean_identity = smoke.package_identity(clean_snapshot)
    clean_ambient_digest = smoke.tree_digest(fixture_repo / "kc-dev-flow")

    pycache = fixture_repo / "kc-dev-flow/skills/setup-github-project-projection/assets/__pycache__"
    pycache.mkdir()
    ignored_paths = [pycache / f"{name}.cpython-314.pyc" for name in ["install-projection", "project-spacedock-state"]]
    for path in ignored_paths:
        path.write_bytes(b"v2.5.0 incident bytecode")
    untracked = fixture_repo / "kc-dev-flow/untracked.txt"
    untracked.write_text("ambient only\n", encoding="utf-8")

    contaminated_snapshot = fixture_root / "contaminated"
    smoke.tracked_package_snapshot(fixture_repo, clean_revision, contaminated_snapshot, 30)
    require(
        smoke.tree_digest(fixture_repo / "kc-dev-flow") != clean_ambient_digest
        and smoke.package_identity(contaminated_snapshot) == clean_identity
        and all(path.is_file() for path in ignored_paths)
        and untracked.is_file(),
        "ignored v2.5.0 files changed tracked identity or the snapshot mutated the worktree",
    )

    tracked = fixture_repo / "kc-dev-flow/skills/setup-github-project-projection/assets/install-projection.py"
    tracked.write_text("print('v2')\n", encoding="utf-8")
    git(fixture_repo, "add", tracked.relative_to(fixture_repo).as_posix())
    git(fixture_repo, "commit", "-qm", "tracked change")
    changed_snapshot = fixture_root / "changed"
    changed_revision = git(fixture_repo, "rev-parse", "HEAD")
    smoke.tracked_package_snapshot(fixture_repo, changed_revision, changed_snapshot, 30)
    require(
        smoke.package_identity(changed_snapshot)[2] != clean_identity[2],
        "a committed tracked package byte did not change snapshot identity",
    )

    malicious_source = fixture_root / "malicious"
    malicious_source.write_text("escape\n", encoding="utf-8")

    def write_unsafe_archive(command, **_kwargs):
        output = Path(next(value for value in command if value.startswith("--output="))[9:])
        with tarfile.open(output, "w") as archive:
            archive.add(malicious_source, arcname="../escaped")
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    with mock.patch.object(smoke, "run", write_unsafe_archive):
        expect_error(
            lambda: smoke.tracked_package_snapshot(fixture_repo, clean_revision, fixture_root / "unsafe", 30),
            "unsafe",
            "unsafe archive member",
        )


class FakeSmokeRuntime:
    candidate_revision = "c" * 40
    published_revision = "d" * 40

    def __init__(
        self,
        *,
        observed_tag: str,
        mutate_host: str = "",
        invalid_codex_report: bool = False,
    ) -> None:
        self.observed_tag = observed_tag
        self.mutate_host = mutate_host
        self.invalid_codex_report = invalid_codex_report
        self.sources: dict[str, Path] = {}
        self.plugins: dict[str, Path] = {}
        self.host_invocations: list[str] = []
        self.host_schemas: dict[str, object] = {}

    def _install(self, host: str, env: dict[str, str]) -> None:
        source = self.sources[host] / "kc-dev-flow"
        installed_version = smoke.installed_version(source)
        cache = (
            Path(env["HOME"]) / ".claude/plugins/cache"
            if host == "claude"
            else Path(env["CODEX_HOME"]) / "plugins/cache"
        )
        installed = cache / "test/kc-dev-flow" / installed_version
        installed.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, installed)
        if self.mutate_host == host:
            (installed / "unexpected-runtime-file.txt").write_text(
                "mutated\n", encoding="utf-8"
            )
        self.plugins[host] = installed

    def __call__(
        self,
        command: list[str],
        *,
        cwd: Path | None = None,
        env: dict[str, str] | None = None,
        timeout: int = 240,
    ) -> subprocess.CompletedProcess[str]:
        del timeout
        stdout = ""
        if command[:3] == ["git", "rev-parse", "HEAD"]:
            stdout = (
                self.candidate_revision if cwd == ROOT else self.published_revision
            ) + "\n"
        elif command[:3] == ["git", "status", "--porcelain"]:
            pass
        elif command[:3] == ["git", "archive", "--format=tar"]:
            archived = command.copy()
            archived[4] = "HEAD"
            subprocess.run(archived, cwd=cwd, check=True, capture_output=True, text=True)
        elif command[:2] == ["git", "clone"]:
            checkout = Path(command[-1])
            subprocess.run(["git", "clone", "-q", "--no-hardlinks", str(ROOT), str(checkout)], check=True)
        elif command[:3] == ["git", "describe", "--tags"]:
            stdout = self.observed_tag + "\n"
        elif command[:4] == ["claude", "plugin", "marketplace", "add"]:
            self.sources["claude"] = Path(command[4])
        elif command[:3] == ["claude", "plugin", "install"]:
            self._install("claude", env or {})
        elif command[:3] == ["claude", "auth", "status"]:
            stdout = '{"loggedIn":true}\n'
        elif command[0] == "claude" and "-p" in command:
            self.host_invocations.append("claude")
            schema = json.loads(command[command.index("--json-schema") + 1])
            self.host_schemas["claude"] = schema
            installed = self.plugins["claude"]
            init = {
                "type": "system",
                "subtype": "init",
                "plugins": [
                    {
                        "name": "kc-dev-flow",
                        "version": smoke.installed_version(installed),
                        "path": str(installed),
                    }
                ],
            }
            result = {
                "type": "result",
                "result": report(self.candidate_revision),
                "structured_output": report_data(self.candidate_revision),
            }
            stdout = json.dumps(init) + "\n" + json.dumps(result)
        elif command[:4] == ["codex", "plugin", "marketplace", "add"]:
            self.sources["codex"] = Path(command[4])
        elif command[:3] == ["codex", "plugin", "add"]:
            self._install("codex", env or {})
        elif command[:2] == ["codex", "exec"]:
            self.host_invocations.append("codex")
            schema_path = Path(command[command.index("--output-schema") + 1])
            self.host_schemas["codex"] = json.loads(
                schema_path.read_text(encoding="utf-8")
            )
            text = "{}" if self.invalid_codex_report else report(self.candidate_revision)
            stdout = json.dumps(
                {
                    "type": "item.completed",
                    "item": {"type": "agent_message", "text": text},
                }
            )
        return subprocess.CompletedProcess(command, 0, stdout=stdout, stderr="")


def run_fake(runtime: FakeSmokeRuntime, action, codex_home: Path | None = None):
    with mock.patch.object(smoke, "run", runtime), mock.patch.object(
        smoke.shutil, "which", return_value="/fake/bin"
    ):
        if codex_home is None:
            return capture(action)
        with mock.patch.dict(
            smoke.os.environ, {"CODEX_HOME": str(codex_home)}, clear=False
        ):
            return capture(action)


def write_receipt(path: Path, value: dict[str, object]) -> None:
    path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")


smoke_tag = f"kc-dev-flow-v{version}"
with tempfile.TemporaryDirectory(prefix="kc-dev-flow-smoke-test-") as temporary:
    temp_root = Path(temporary)
    receipt_path = temp_root / "candidate.json"
    codex_home = temp_root / "operator-codex"
    codex_home.mkdir()
    (codex_home / "auth.json").write_text("{}\n", encoding="utf-8")

    candidate_runtime = FakeSmokeRuntime(observed_tag=smoke_tag)
    candidate_result, candidate_error = run_fake(
        candidate_runtime,
        lambda: smoke.run_candidate_smoke(receipt_path, 30),
        codex_home,
    )
    candidate_receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    require(
        not candidate_error
        and candidate_result == candidate_receipt
        and candidate_runtime.host_invocations == ["claude", "codex"]
        and candidate_receipt["reports"] == {"claude": "PASS", "codex": "PASS"}
        and {path.name for path in candidate_runtime.sources.values()} == {"snapshot"},
        f"candidate mode did not close both hosts: {candidate_error!r}",
    )
    schema = candidate_runtime.host_schemas["claude"]
    envelope = schema["properties"]["science_officer_em_upward_report"]
    judgment = envelope["properties"]["engineering_judgment"]
    adjudication = judgment["properties"]["adjudications"]["items"]
    require(
        candidate_runtime.host_schemas["codex"] == schema
        and all(
            node.get("additionalProperties") is False
            for node in [schema, envelope, judgment, adjudication]
        )
        and "verdict_note" not in adjudication["properties"],
        "candidate hosts did not receive one closed schema",
    )

    failed_path = temp_root / "failed.json"
    failed_runtime = FakeSmokeRuntime(
        observed_tag=smoke_tag, invalid_codex_report=True
    )
    _result, failed_error = run_fake(
        failed_runtime,
        lambda: smoke.run_candidate_smoke(failed_path, 30),
        codex_home,
    )
    require(
        failed_error
        and failed_runtime.host_invocations == ["claude", "codex"]
        and not failed_path.exists(),
        "candidate mode wrote a receipt before both hosts passed",
    )

    receipt_variants: list[tuple[str, dict[str, object], str]] = [
        ("extra root", candidate_receipt | {"extra": True}, "extra"),
        ("wrong schema", candidate_receipt | {"schema": "wrong"}, "schema"),
        ("wrong revision", candidate_receipt | {"candidate_revision": "bad"}, "revision"),
        ("wrong version", candidate_receipt | {"version": "next"}, "version"),
        ("wrong digest", candidate_receipt | {"tree_sha256": "short"}, "tree_sha256"),
        (
            "wrong report",
            candidate_receipt
            | {"reports": {"claude": "PASS", "codex": "UNKNOWN"}},
            "reports",
        ),
    ]
    for index, (label, value, fragment) in enumerate(receipt_variants):
        path = temp_root / f"receipt-{index}.json"
        write_receipt(path, value)
        expect_error(
            lambda path=path: smoke.load_candidate_receipt(path), fragment, label
        )

    published_runtime = FakeSmokeRuntime(observed_tag=smoke_tag)
    published_result, published_error = run_fake(
        published_runtime,
        lambda: smoke.run_published_smoke(smoke_tag, receipt_path, 30),
    )
    require(
        not published_error
        and not published_runtime.host_invocations
        and published_result["installed"] == {"claude": "PASS", "codex": "PASS"}
        and {path.name for path in published_runtime.sources.values()} == {"snapshot"},
        f"published mode did not bind identity without models: {published_error!r}",
    )

    published_cases = [
        (
            "tag",
            candidate_receipt,
            FakeSmokeRuntime(observed_tag=f"{smoke_tag}-other"),
            "resolved",
        ),
        (
            "version",
            candidate_receipt | {"version": "9.9.9"},
            FakeSmokeRuntime(observed_tag=smoke_tag),
            "version",
        ),
        (
            "source",
            candidate_receipt | {"tree_sha256": "e" * 64},
            FakeSmokeRuntime(observed_tag=smoke_tag),
            "source tree",
        ),
        (
            "Claude tree",
            candidate_receipt,
            FakeSmokeRuntime(observed_tag=smoke_tag, mutate_host="claude"),
            "Claude installed tree",
        ),
        (
            "Codex tree",
            candidate_receipt,
            FakeSmokeRuntime(observed_tag=smoke_tag, mutate_host="codex"),
            "Codex installed tree",
        ),
    ]
    for index, (label, value, runtime, fragment) in enumerate(published_cases):
        path = temp_root / f"published-{index}.json"
        write_receipt(path, value)
        _result, error = run_fake(
            runtime,
            lambda path=path: smoke.run_published_smoke(smoke_tag, path, 30),
        )
        require(
            fragment in error and not runtime.host_invocations,
            f"published {label} falsifier was missed: {error!r}",
        )

print("published-tag smoke test: PASS")
