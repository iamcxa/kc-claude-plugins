#!/usr/bin/env python3
"""Fail-closed package contract for the portable kc-dev-flow product."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
from unittest import mock
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "kc-dev-flow"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"kc-dev-flow contract: {message}")


def load_json(path: Path) -> object:
    require(path.is_file(), f"missing {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


required_files = [
    PLUGIN / ".claude-plugin/plugin.json",
    PLUGIN / ".codex-plugin/plugin.json",
    PLUGIN / "skills/adopt-dev-flow/SKILL.md",
    PLUGIN / "skills/continue-dev-flow/SKILL.md",
    PLUGIN / "references/kernel.md",
    PLUGIN / "references/project-context-maintenance.md",
    PLUGIN / "references/reverse-recovery-audit.md",
    PLUGIN / "references/work-control-profile.md",
    PLUGIN / "scripts/absolutes-check.py",
    PLUGIN / "references/absolutes.registry",
    PLUGIN / "skills/promote-dev-flow/SKILL.md",
    PLUGIN / "skills/promote-dev-flow/agents/openai.yaml",
    PLUGIN / "scripts/improvement-intake.py",
    PLUGIN / "scripts/improvement-intake.test.py",
    PLUGIN / "references/engineering-judgment.md",
    PLUGIN / "skills/science-officer-em/SKILL.md",
    PLUGIN / "skills/science-officer-em/agents/openai.yaml",
    ROOT / "scripts/kc-dev-flow-published-tag-smoke.py",
    ROOT / "scripts/kc-dev-flow-loader-eval.py",
    ROOT / "scripts/kc-dev-flow-loader-eval.test.py",
    ROOT / "scripts/fixtures/kc-dev-flow-loader-eval/q08.json",
    ROOT / "scripts/kc-dev-flow-continuation-eval.py",
    ROOT / "scripts/kc-dev-flow-continuation-eval.test.py",
    ROOT / "scripts/fixtures/kc-dev-flow-continuation-eval/pressures.json",
    PLUGIN / "references/retained-document-policy.md",
]
for required_file in required_files:
    require(required_file.is_file(), f"missing {required_file.relative_to(ROOT)}")

require(
    (PLUGIN / "scripts/absolutes-check.py").stat().st_mode & 0o111,
    "scripts/absolutes-check.py is not executable",
)
require(
    (PLUGIN / "scripts/improvement-intake.py").stat().st_mode & 0o111,
    "scripts/improvement-intake.py is not executable",
)
require(
    (ROOT / "scripts/kc-dev-flow-published-tag-smoke.py").stat().st_mode & 0o111,
    "scripts/kc-dev-flow-published-tag-smoke.py is not executable",
)
require(
    (ROOT / "scripts/kc-dev-flow-loader-eval.py").stat().st_mode & 0o111,
    "scripts/kc-dev-flow-loader-eval.py is not executable",
)
require(
    (ROOT / "scripts/kc-dev-flow-loader-eval.test.py").stat().st_mode & 0o111,
    "scripts/kc-dev-flow-loader-eval.test.py is not executable",
)
require(
    (ROOT / "scripts/kc-dev-flow-continuation-eval.py").stat().st_mode & 0o111,
    "scripts/kc-dev-flow-continuation-eval.py is not executable",
)
require(
    (ROOT / "scripts/kc-dev-flow-continuation-eval.test.py").stat().st_mode & 0o111,
    "scripts/kc-dev-flow-continuation-eval.test.py is not executable",
)

loader_eval_test = subprocess.run(
    [sys.executable, "scripts/kc-dev-flow-loader-eval.test.py"],
    cwd=ROOT,
    text=True,
    capture_output=True,
)
require(
    loader_eval_test.returncode == 0,
    "loader eval contract failed:\n"
    + loader_eval_test.stdout
    + loader_eval_test.stderr,
)

continuation_eval_test = subprocess.run(
    [sys.executable, "scripts/kc-dev-flow-continuation-eval.test.py"],
    cwd=ROOT,
    text=True,
    capture_output=True,
)
require(
    continuation_eval_test.returncode == 0,
    "continuation eval contract failed:\n"
    + continuation_eval_test.stdout
    + continuation_eval_test.stderr,
)

expected_smoke_revision = "a" * 40
valid_em_report_data = {
    "science_officer_em_upward_report": {
        "em_judgment": "proceed on the bounded documentation change",
        "evidence_synthesis": "exact-tag installed-runtime evidence",
        "risk_tradeoff_call": "low-cost reversible change versus stale guidance",
        "recommendation": "proceed through normal delivery",
        "route": "proceed",
        "confidence": "high",
        "multi_model": "not_needed",
        "fo_boundary": "",
        "engineering_judgment": {
            "question": "should the bounded change proceed",
            "revision": expected_smoke_revision,
            "evidence_synthesis": "exact-tag installed-runtime evidence",
            "adjudications": [
                {
                    "finding": "runtime contract is present",
                    "disposition": "supported",
                    "basis": "installed host output",
                }
            ],
            "risk_tradeoff": "low-cost reversible change versus stale guidance",
            "recommendation": "proceed through normal delivery",
            "route": "proceed",
            "confidence": "high",
            "dissent": "",
            "disproof_condition": "a required field or installed host is missing",
            "authority_boundary": "captain and delivery owners retain authority",
        },
    }
}
valid_em_report = json.dumps(valid_em_report_data)

smoke_spec = importlib.util.spec_from_file_location(
    "kc_dev_flow_published_tag_smoke",
    ROOT / "scripts/kc-dev-flow-published-tag-smoke.py",
)
require(smoke_spec is not None and smoke_spec.loader is not None, "cannot load published-tag smoke")
smoke = importlib.util.module_from_spec(smoke_spec)
smoke_spec.loader.exec_module(smoke)
smoke_tag = f"kc-dev-flow-v{smoke.installed_version(ROOT / 'kc-dev-flow')}"

with mock.patch.object(
    sys, "argv", ["smoke", "candidate", "--receipt", "/tmp/candidate.json"]
):
    candidate_args = smoke.parse_args()
with mock.patch.object(
    sys,
    "argv",
    [
        "smoke", "published", smoke_tag,
        "--candidate-receipt", "/tmp/candidate.json",
    ],
):
    published_args = smoke.parse_args()
require(
    candidate_args.mode == "candidate"
    and candidate_args.receipt == Path("/tmp/candidate.json")
    and published_args.mode == "published"
    and published_args.candidate_receipt == Path("/tmp/candidate.json"),
    "published-tag smoke CLI modes are incomplete",
)


def run_report_check(report: str, revision: str = expected_smoke_revision) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/kc-dev-flow-published-tag-smoke.py"),
            "--validate-report",
            "-",
            "--expected-revision",
            revision,
        ],
        input=report,
        capture_output=True,
        text=True,
    )


report_check = run_report_check(valid_em_report)
require(
    report_check.returncode == 0,
    report_check.stdout.strip() or report_check.stderr.strip() or "valid EM report was rejected",
)

invalid_reports: dict[str, tuple[str, str]] = {
    "malformed structure": ("not a JSON/YAML document", "structural"),
}
incomplete = json.loads(valid_em_report)
del incomplete["science_officer_em_upward_report"]["engineering_judgment"]["disproof_condition"]
invalid_reports["incomplete"] = (json.dumps(incomplete), "disproof_condition")

misplaced = json.loads(valid_em_report)
misplaced_value = misplaced["science_officer_em_upward_report"]["engineering_judgment"].pop(
    "disproof_condition"
)
misplaced["science_officer_em_upward_report"]["disproof_condition"] = misplaced_value
invalid_reports["misplaced"] = (json.dumps(misplaced), "disproof_condition")

duplicate = valid_em_report.replace(
    '"route": "proceed",', '"route": "proceed", "route": "return",', 1
)
invalid_reports["duplicate"] = (duplicate, "duplicate")

invalid_enum = json.loads(valid_em_report)
invalid_enum["science_officer_em_upward_report"]["route"] = "maybe"
invalid_enum["science_officer_em_upward_report"]["engineering_judgment"]["route"] = "maybe"
invalid_reports["invalid enum"] = (json.dumps(invalid_enum), "route")

mismatched = json.loads(valid_em_report)
mismatched["science_officer_em_upward_report"]["engineering_judgment"][
    "recommendation"
] = "return for more work"
invalid_reports["mismatched duplicates"] = (json.dumps(mismatched), "recommendation")

extra_adjudication = json.loads(valid_em_report)
extra_adjudication["science_officer_em_upward_report"]["engineering_judgment"][
    "adjudications"
][0]["verdict_note"] = "not part of the closed compatibility record"
invalid_reports["extra verdict_note"] = (json.dumps(extra_adjudication), "verdict_note")

invalid_reports["wrong revision"] = (valid_em_report, "revision")

for label, (report, expected_error) in invalid_reports.items():
    expected_revision = "b" * 40 if label == "wrong revision" else expected_smoke_revision
    invalid_report_check = run_report_check(report, expected_revision)
    require(
        invalid_report_check.returncode != 0
        and expected_error in (invalid_report_check.stdout + invalid_report_check.stderr),
        f"published-tag smoke accepts an invalid EM report: {label}",
    )


def report_for_revision(revision: str) -> str:
    report = json.loads(valid_em_report)
    report["science_officer_em_upward_report"]["engineering_judgment"]["revision"] = revision
    return json.dumps(report)


def capture(action):
    try:
        return action(), ""
    except Exception as exc:
        return None, str(exc)


claude_plugin = ROOT / "kc-dev-flow"
claude_version = smoke.installed_version(claude_plugin)
claude_probe_events = [
    {
        "type": "system",
        "subtype": "init",
        "plugins": [
            {
                "name": "kc-dev-flow",
                "version": claude_version,
                "path": str(claude_plugin),
            }
        ],
    },
    {
        "type": "result",
        "result": json.dumps(extra_adjudication),
        "structured_output": valid_em_report_data,
    },
]
claude_probe_output = "\n".join(json.dumps(event) for event in claude_probe_events)
claude_structured_report = smoke.claude_stream_result(
    claude_probe_output,
    claude_plugin,
    claude_version,
)
require(
    json.loads(claude_structured_report) == valid_em_report_data,
    "Claude extraction ignored the schema-validated structured_output envelope",
)
del claude_probe_events[-1]["structured_output"]
_, missing_structured_error = capture(
    lambda: smoke.claude_stream_result(
        "\n".join(json.dumps(event) for event in claude_probe_events),
        claude_plugin,
        claude_version,
    )
)
require(
    "structured_output" in missing_structured_error,
    "Claude extraction fell back to unvalidated result text",
)


class FakeSmokeRuntime:
    candidate_revision = "c" * 40
    published_revision = "d" * 40

    def __init__(
        self,
        *,
        observed_tag: str = smoke_tag,
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
        version = smoke.installed_version(source)
        cache = (
            Path(env["HOME"]) / ".claude/plugins/cache"
            if host == "claude"
            else Path(env["CODEX_HOME"]) / "plugins/cache"
        )
        plugin = cache / "test/kc-dev-flow" / version
        plugin.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, plugin)
        if self.mutate_host == host:
            (plugin / "unexpected-runtime-file.txt").write_text(
                "mutated\n", encoding="utf-8"
            )
        self.plugins[host] = plugin

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
        elif command[:2] == ["git", "clone"]:
            checkout = Path(command[-1])
            shutil.copytree(ROOT / ".claude-plugin", checkout / ".claude-plugin")
            shutil.copytree(ROOT / "kc-dev-flow", checkout / "kc-dev-flow")
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
            schema_index = command.index("--json-schema") + 1
            self.host_schemas["claude"] = json.loads(command[schema_index])
            plugin = self.plugins["claude"]
            init = {
                "type": "system",
                "subtype": "init",
                "plugins": [{
                    "name": "kc-dev-flow",
                    "version": smoke.installed_version(plugin),
                    "path": str(plugin),
                }],
            }
            result = {
                "type": "result",
                "result": report_for_revision(self.candidate_revision),
                "structured_output": json.loads(report_for_revision(self.candidate_revision)),
            }
            stdout = json.dumps(init) + "\n" + json.dumps(result)
        elif command[:4] == ["codex", "plugin", "marketplace", "add"]:
            self.sources["codex"] = Path(command[4])
        elif command[:3] == ["codex", "plugin", "add"]:
            self._install("codex", env or {})
        elif command[:2] == ["codex", "exec"]:
            self.host_invocations.append("codex")
            schema_index = command.index("--output-schema") + 1
            self.host_schemas["codex"] = json.loads(
                Path(command[schema_index]).read_text(encoding="utf-8")
            )
            stdout = json.dumps({
                "type": "item.completed",
                "item": {
                    "type": "agent_message",
                    "text": (
                        "{}"
                        if self.invalid_codex_report
                        else report_for_revision(self.candidate_revision)
                    ),
                },
            })
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


def write_receipt(path: Path, receipt: dict[str, object]) -> None:
    path.write_text(json.dumps(receipt, sort_keys=True) + "\n", encoding="utf-8")


with tempfile.TemporaryDirectory(prefix="kc-dev-flow-contract-") as contract_tmp:
    contract_root = Path(contract_tmp)
    receipt_path = contract_root / "candidate.json"
    operator_codex_home = contract_root / "operator-codex"
    operator_codex_home.mkdir()
    (operator_codex_home / "auth.json").write_text("{}\n", encoding="utf-8")

    candidate_runtime = FakeSmokeRuntime()
    candidate_result, candidate_error = run_fake(
        candidate_runtime,
        lambda: smoke.run_candidate_smoke(receipt_path, 30),
        operator_codex_home,
    )
    candidate_receipt = (
        json.loads(receipt_path.read_text(encoding="utf-8"))
        if receipt_path.is_file()
        else {}
    )
    require(
        not candidate_error
        and candidate_runtime.host_invocations == ["claude", "codex"]
        and candidate_result == candidate_receipt
        and set(candidate_receipt)
        == {"schema", "candidate_revision", "version", "tree_sha256", "reports"}
        and candidate_receipt["reports"] == {"claude": "PASS", "codex": "PASS"},
        "candidate mode did not invoke both hosts and write the minimum receipt: "
        f"{candidate_error!r}; {candidate_runtime.host_invocations}; {candidate_receipt!r}",
    )
    schema = candidate_runtime.host_schemas.get("claude")
    require(
        isinstance(schema, dict),
        f"Claude candidate command omitted the report schema: {candidate_runtime.host_schemas!r}",
    )
    envelope_schema = schema["properties"]["science_officer_em_upward_report"]
    judgment_schema = envelope_schema["properties"]["engineering_judgment"]
    adjudication_schema = judgment_schema["properties"]["adjudications"]["items"]
    schema_objects = [schema, envelope_schema, judgment_schema, adjudication_schema]
    require(
        candidate_runtime.host_schemas.get("codex") == schema
        and all(
            isinstance(node, dict)
            and node.get("additionalProperties") is False
            for node in schema_objects
        )
        and "verdict_note" not in adjudication_schema["properties"],
        "candidate hosts did not receive one closed report schema: "
        f"{candidate_runtime.host_schemas!r}",
    )

    failed_receipt = contract_root / "failed.json"
    failed_runtime = FakeSmokeRuntime(invalid_codex_report=True)
    _, failed_error = run_fake(
        failed_runtime,
        lambda: smoke.run_candidate_smoke(failed_receipt, 30),
        operator_codex_home,
    )
    require(
        bool(failed_error)
        and failed_runtime.host_invocations == ["claude", "codex"]
        and not failed_receipt.exists(),
        "candidate mode wrote a receipt before both reports passed",
    )

    receipt_variants = [
        ("extra root", candidate_receipt | {"extra": True}, "extra"),
        (
            "extra reports",
            candidate_receipt
            | {"reports": candidate_receipt["reports"] | {"extra": True}},
            "extra",
        ),
        (
            "wrong schema",
            candidate_receipt | {"schema": "kc-dev-flow-candidate-smoke/v2"},
            "schema",
        ),
        (
            "wrong revision",
            candidate_receipt | {"candidate_revision": "bad"},
            "candidate_revision",
        ),
        ("wrong version", candidate_receipt | {"version": "next"}, "version"),
        ("wrong digest", candidate_receipt | {"tree_sha256": "short"}, "tree_sha256"),
        (
            "wrong report",
            candidate_receipt | {"reports": {"claude": "PASS", "codex": "UNKNOWN"}},
            "reports",
        ),
    ]
    receipt_results: dict[str, str] = {}
    loaded_receipt, valid_receipt_error = capture(
        lambda: smoke.load_candidate_receipt(receipt_path)
    )
    for index, (label, receipt, expected_error) in enumerate(receipt_variants):
        path = contract_root / f"receipt-{index}.json"
        write_receipt(path, receipt)
        _, error = capture(lambda path=path: smoke.load_candidate_receipt(path))
        receipt_results[label] = (
            "rejected" if expected_error in error else error or "accepted"
        )
    duplicate_path = contract_root / "duplicate.json"
    duplicate_path.write_text(
        json.dumps(candidate_receipt).replace(
            '"schema": "kc-dev-flow-candidate-smoke/v1",',
            '"schema": "kc-dev-flow-candidate-smoke/v1", "schema": "duplicate",',
            1,
        ),
        encoding="utf-8",
    )
    _, duplicate_error = capture(
        lambda: smoke.load_candidate_receipt(duplicate_path)
    )
    require(
        not valid_receipt_error
        and loaded_receipt == candidate_receipt
        and set(receipt_results.values()) == {"rejected"}
        and "duplicate" in duplicate_error,
        f"candidate receipt contract is not closed: {receipt_results}; {duplicate_error!r}",
    )

    published_runtime = FakeSmokeRuntime()
    published_result, published_error = run_fake(
        published_runtime,
        lambda: smoke.run_published_smoke(smoke_tag, receipt_path, 30),
    )
    published_cases = [
        (
            "tag",
            smoke_tag,
            candidate_receipt,
            FakeSmokeRuntime(observed_tag=f"{smoke_tag}-other"),
            "resolved",
        ),
        (
            "version",
            smoke_tag,
            candidate_receipt | {"version": "9.9.9"},
            FakeSmokeRuntime(),
            "version",
        ),
        (
            "source",
            smoke_tag,
            candidate_receipt | {"tree_sha256": "e" * 64},
            FakeSmokeRuntime(),
            "source tree",
        ),
        (
            "Claude tree",
            smoke_tag,
            candidate_receipt,
            FakeSmokeRuntime(mutate_host="claude"),
            "Claude installed tree",
        ),
        (
            "Codex tree",
            smoke_tag,
            candidate_receipt,
            FakeSmokeRuntime(mutate_host="codex"),
            "Codex installed tree",
        ),
    ]
    published_results: dict[str, str] = {}
    for index, (label, tag, receipt, runtime, expected_error) in enumerate(
        published_cases
    ):
        path = contract_root / f"published-{index}.json"
        write_receipt(path, receipt)
        _, error = run_fake(
            runtime, lambda tag=tag, path=path: smoke.run_published_smoke(tag, path, 30)
        )
        published_results[label] = (
            "rejected" if expected_error in error and not runtime.host_invocations else error or "accepted"
        )
    require(
        not published_error
        and not published_runtime.host_invocations
        and set(published_result)
        == {
            "schema",
            "tag",
            "candidate_revision",
            "published_revision",
            "version",
            "tree_sha256",
            "installed",
        }
        and published_result["installed"] == {"claude": "PASS", "codex": "PASS"}
        and set(published_results.values()) == {"rejected"},
        f"published mode invoked a model or missed an identity falsifier: {published_error!r}; {published_results}",
    )


for legacy in [
    PLUGIN / "assets/kernel-binding.template.yaml",
    PLUGIN / "scripts/verify-binding.py",
    ROOT / "scripts/verify-binding.test.sh",
    ROOT / "docs/dev/kernel-binding.yaml",
    ROOT / "docs/dev/_mods/STATUS.md",
]:
    require(not legacy.exists(), f"legacy distribution artifact remains: {legacy.relative_to(ROOT)}")

claude_manifest = load_json(required_files[0])
codex_manifest = load_json(required_files[1])
marketplace = load_json(ROOT / ".claude-plugin/marketplace.json")
release_manifest = load_json(ROOT / ".release-please-manifest.json")
release_config = load_json(ROOT / "release-please-config.json")

require(claude_manifest["name"] == "kc-dev-flow", "wrong Claude plugin name")
require(codex_manifest["name"] == "kc-dev-flow", "wrong Codex plugin name")
require(codex_manifest.get("skills") == "./skills/", "Codex skills path is missing")

entries = [p for p in marketplace["plugins"] if p["name"] == "kc-dev-flow"]
require(len(entries) == 1, "marketplace must contain exactly one entry")
versions = {
    claude_manifest["version"],
    codex_manifest["version"],
    entries[0]["version"],
    release_manifest["kc-dev-flow"],
}
require(len(versions) == 1, f"version parity failed: {sorted(versions)}")
version = next(iter(versions))
require(re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version) is not None, "version is not semver")

package = release_config["packages"].get("kc-dev-flow")
require(package is not None, "release-please package is missing")
extra_paths = {item["path"] for item in package["extra-files"]}
require(
    extra_paths
    == {
        ".claude-plugin/plugin.json",
        ".codex-plugin/plugin.json",
        "/.claude-plugin/marketplace.json",
    },
    f"release propagation paths are incomplete: {sorted(extra_paths)}",
)

adopt_skill = required_files[2].read_text(encoding="utf-8")
for phrase in [
    "adopt, audit, or upgrade",
    "Do not replace an existing tracker",
    "Do not create, schedule, advance, or merge",
    "one narrow improvement proposal",
    "Claude Code and Codex",
    "Local Profile",
    "byte-for-byte",
    "_mods/",
]:
    require(phrase in adopt_skill, f"adopt skill is missing boundary: {phrase}")

continue_skill = required_files[3].read_text(encoding="utf-8")
continue_skill_flat = " ".join(continue_skill.split())
harvest_reference_path = PLUGIN / "references/improvement-harvesting.md"
require(
    harvest_reference_path.is_file(),
    "missing kc-dev-flow/references/improvement-harvesting.md",
)
harvest_reference = harvest_reference_path.read_text(encoding="utf-8")
continue_contract = continue_skill + "\n" + harvest_reference
continue_skill_words = len(continue_skill.split())
require(
    continue_skill_words <= 650,
    f"ordinary continuation policy exceeds 650 words: {continue_skill_words}",
)
require(
    "## Advance the work" in continue_skill
    and "## Harvest improvements only when explicitly requested" in continue_skill
    and continue_skill.index("## Advance the work")
    < continue_skill.index("## Harvest improvements only when explicitly requested"),
    "continuation does not route product work before optional harvesting",
)
require(
    "Do not inspect `_debriefs/` or `_improvements/`" in continue_skill,
    "ordinary continuation does not prohibit improvement-state I/O",
)
require(
    "Do not enumerate the execution-state tree" in continue_skill,
    "ordinary routing does not guard broad execution-state enumeration",
)
require(
    "never enumerate a workflow parent" in continue_skill
    and "read its exact bound entity path" in continue_skill
    and "`rg --files`, `find`, `ls`" in continue_skill,
    "ordinary routing does not operationalize direct active-entity resolution",
)
require(
    "Read iteration authority first" in continue_skill_flat
    and "report scheduling immediately" in continue_skill_flat
    and "do not inspect work-item or execution state" in continue_skill_flat,
    "an explicitly empty iteration does not short-circuit state discovery",
)
require(
    "already-loaded instruction chain" in continue_skill_flat
    and "batch the workflow README and complete vendored kernel" in continue_skill_flat
    and "batch iteration, identity, ownership, and delivery reads" in continue_skill_flat
    and "stop-before-action invocation does not read it" in continue_skill_flat,
    "ordinary P1 resolution does not bound redundant discovery and read calls",
)
require(
    "Before opening the harvest reference or enumerating improvement evidence"
    in continue_skill,
    "explicit harvesting does not require concrete product-route resolution first",
)
require(
    "../../references/improvement-harvesting.md" in continue_skill,
    "explicit harvesting does not load the packaged reference",
)
require(
    "Never print or interpolate the private key" in harvest_reference,
    "explicit harvesting does not protect private identity from host traces",
)
for phrase in [
    "next committed work item",
    "continue without a captain pause",
    "Do not invent or schedule work",
    "fresh validation",
    "Claude Code and Codex",
    "repository-local",
    "reusable kernel",
    "_mods/kernel.md",
    "Policy mods",
    "_improvements/state.yaml",
    "If no debrief home is bound",
    "no unseen debrief",
    "Inside the same transaction",
    "report `UNKNOWN`, skip the improvement write, and continue to product routing",
    "compatibility transport label",
    "kc-dev-flow-improvement-handoff/v1",
    "rule-gap",
    "enforcement-gap",
    "merge its existing observations by ID",
    "write neither",
    "Before the handoff leaves the repository",
    "source_namespace",
    "durable pseudonymous state",
    "16 bytes decoded from the stored lowercase hex key",
    "kc-dev-flow-vX.Y.Z",
    "adopter-coined label",
    "First-write-wins",
    "_improvements/.private/source-identity.json",
    "require ignore proof",
    "roll over to the next sequence",
    "exactly one fresh-context EM verdict for every ideation and validation gate",
    "Implementation opens no reviewer loop",
    "Multi-model review is optional",
    "silence is not approval",
]:
    require(phrase in continue_contract, f"continue contract is missing boundary: {phrase}")
require(
    "If none or multiple candidates remain" not in continue_contract,
    "continue contract still blocks product work when no debrief home exists",
)
require(
    "stop with `UNKNOWN` instead of risking an overwrite" not in continue_contract,
    "continue contract still lets self-improvement storage block product routing",
)

promote_skill = required_files[10].read_text(encoding="utf-8")
for phrase in [
    "source-side intake",
    "captain-review-only",
    "rule-gap",
    "enforcement-gap",
    "local-instance",
    "duplicate/no-change",
    "Do not create, schedule, edit, post, or merge",
    "improvement-intake.py",
    "captain-approved file attachment or copied path",
    "not source-verified",
]:
    require(phrase in promote_skill, f"promote skill is missing boundary: {phrase}")

package_readme = (PLUGIN / "README.md").read_text(encoding="utf-8")
require("promote-dev-flow" in package_readme, "package README is missing source intake skill")
require(
    "Only an explicit request" in package_readme
    and "improvement-harvesting.md" in package_readme
    and "Ordinary continuation" in package_readme,
    "package README does not document product-first explicit harvesting",
)
require(
    "engineering-judgment" in package_readme,
    "package README is missing engineering judgment mod",
)
require(
    "- `retained-document-policy` —" in package_readme,
    "package README is missing the independently selectable retained-document policy mod",
)
require(
    "- `project-context-maintenance` —" in package_readme,
    "package README is missing the independently selectable project-context mod",
)
require(
    "independently adoptable parts" not in package_readme,
    "package README still claims path-internal policy selection",
)
root_readme = (ROOT / "README.md").read_text(encoding="utf-8")
require("promote-dev-flow" in root_readme, "root README is missing source intake skill")
default_prompts = codex_manifest["interface"]["defaultPrompt"]
require(
    any("promote-dev-flow" in prompt for prompt in default_prompts),
    "Codex manifest is missing source intake discovery",
)
require(
    any("science-officer-em" in prompt for prompt in default_prompts),
    "Codex manifest is missing Science Officer discovery",
)

intake_tests = subprocess.run(
    [sys.executable, str(PLUGIN / "scripts/improvement-intake.test.py")],
    capture_output=True,
    text=True,
)
require(
    intake_tests.returncode == 0,
    intake_tests.stdout.strip() or intake_tests.stderr.strip() or "improvement intake tests failed",
)

project_context_mod = required_files[5].read_text(encoding="utf-8")
retained_document_mod = required_files[-1].read_text(encoding="utf-8")
require(
    "# Part 1" not in project_context_mod,
    "project-context-maintenance still embeds the separately selectable retained-document policy",
)
require(
    "name: retained-document-policy" in retained_document_mod,
    "retained-document policy has the wrong mod identity",
)
retained_stage_rows = {
    line.split("|", 2)[1].strip(" `"): line
    for line in retained_document_mod.splitlines()
    if line.startswith("| `")
}
require(
    "For an addition or deletion, execute Rule 4."
    in retained_stage_rows.get("implementation", ""),
    "retained-document policy does not assign Rule 4 to implementation",
)
require(
    "For an addition or deletion, repeat Rule 4 independently"
    in retained_stage_rows.get("validation", ""),
    "retained-document policy does not assign independent Rule 4 verification",
)
require(
    "`work-context-protocol`" not in project_context_mod,
    "project-context-maintenance references an unshipped work-context-protocol",
)
require(
    "`kernel.md` Authority model" in project_context_mod,
    "project-context-maintenance does not name the shipped project-context binding policy",
)

runtime_docs = {
    "adopt skill": adopt_skill,
    "continue skill": continue_skill,
    "package README": (PLUGIN / "README.md").read_text(encoding="utf-8"),
    "workflow README": (ROOT / "docs/dev/README.md").read_text(encoding="utf-8"),
}
for label, content in runtime_docs.items():
    for legacy_reference in [
        "verify-binding.py",
        "kernel-binding.yaml",
        "kernel-binding.template.yaml",
    ]:
        require(
            legacy_reference not in content,
            f"{label} still instructs the legacy distribution path: {legacy_reference}",
        )

workflow = (ROOT / "docs/dev/README.md").read_text(encoding="utf-8")
state_recovery_runbook = ROOT / "docs/dev/runbooks/state-recovery.md"
validation_evidence_runbook = ROOT / "docs/dev/runbooks/validation-evidence.md"
for runtime_reference in [
    state_recovery_runbook,
    validation_evidence_runbook,
]:
    require(
        runtime_reference.is_file(),
        f"self-adoption is missing trigger-loaded reference: {runtime_reference.relative_to(ROOT)}",
    )
state_recovery = state_recovery_runbook.read_text(encoding="utf-8")
require(
    "spacedock 0.26.0 (contract 3)" in state_recovery,
    "state recovery does not name the supported Spacedock runtime contract",
)

pr_merge_mod_path = ROOT / "docs/dev/_mods/pr-merge.md"
require(pr_merge_mod_path.is_file(), "self-adoption is missing the pr-merge mod")
pr_merge_mod = pr_merge_mod_path.read_text(encoding="utf-8")
extension_start = "<!-- kc-dev-flow runtime extension:start -->\n"
extension_end = "<!-- kc-dev-flow runtime extension:end -->\n"
require(
    pr_merge_mod.count(extension_start) == 1
    and pr_merge_mod.count(extension_end) == 1
    and pr_merge_mod.endswith(extension_end),
    "pr-merge does not contain one trailing runtime extension",
)
released_body, local_extension = pr_merge_mod.split(extension_start, 1)
local_extension = extension_start + local_extension
released_body_without_draft = released_body.replace(
    "gh pr create --draft --base", "gh pr create --base", 1
)
require(
    released_body.count("gh pr create --draft --base") == 1,
    "pr-merge does not make the released single-PR command Draft by default",
)
require(
    hashlib.sha256(released_body_without_draft.encode("utf-8")).hexdigest()
    == "a70a0ba4f9fb48a1c33e9f9e2c4ff3cb76b0a816d050a42bdbd6eced9fd15f64",
    "pr-merge released 0.12.2 body drifted outside the Draft adjustment",
)
decision_heading = "### Delivery topology decision\n"
require(
    local_extension.count(decision_heading) == 1,
    "pr-merge must contain one authoritative delivery-topology decision table",
)
decision_section = local_extension.split(decision_heading, 1)[1].split("\n### ", 1)[0]
require(
    "Numeric trigger: `gross additions + deletions > 1,500 OR changed files > 20`."
    in decision_section,
    "delivery-topology numeric trigger is not the strict >1,500 OR >20 predicate",
)
topology_table_section = decision_section.split("\n#### ", 1)[0]
decision_table_lines = [
    line for line in topology_table_section.splitlines() if line.startswith("|")
]
require(
    len(decision_table_lines) == 6,
    "delivery-topology decision table must contain one header and exactly four rows",
)


def markdown_row(line: str) -> tuple[str, ...]:
    return tuple(cell.strip() for cell in line.strip().strip("|").split("|"))


require(
    markdown_row(decision_table_lines[0])
    == (
        "Dependent green layers?",
        "Independent green slices?",
        "Numeric trigger?",
        "Required topology",
    ),
    "delivery-topology decision table header drifted",
)
require(
    markdown_row(decision_table_lines[1]) == ("---", "---", "---", "---"),
    "delivery-topology decision table separator drifted",
)
expected_topology_rows = [
    ("yes", "any", "any", "Native stack at any size"),
    ("no", "yes", "any", "Parallel Draft PRs from trunk"),
    (
        "no",
        "no",
        "yes",
        "One Draft PR with `## Native stack exception`",
    ),
    ("no", "no", "no", "One Draft PR"),
]
require(
    [markdown_row(line) for line in decision_table_lines[2:]]
    == expected_topology_rows,
    "delivery-topology row polarity or required outcome drifted",
)


def policy_table(section: str, heading: str) -> list[tuple[str, ...]]:
    marker = f"#### {heading}\n"
    if section.count(marker) != 1:
        return []
    body = section.split(marker, 1)[1]
    body = re.split(r"\n#### ", body, maxsplit=1)[0]
    return [markdown_row(line) for line in body.splitlines() if line.startswith("|")]


expected_layer_rows = [
    ("Layer", "`UNIT_BASE_BRANCH`", "`UNIT_BASE_SHA`"),
    ("---", "---", "---"),
    ("bottom", "trunk `$BASE`", "approved trunk `$BASE_SHA`"),
    (
        "each higher",
        "branch immediately below",
        "approved `UNIT_CANDIDATE_SHA` immediately below",
    ),
]
expected_stack_completion_rows = [
    ("Evidence", "Required result", "Otherwise"),
    ("---", "---", "---"),
    ("Stack lookup", "exactly one stack for stored top PR", "stop"),
    ("Base", "`base.ref` equals trunk", "stop"),
    ("Top position", "stored top PR is final ordered entry", "stop"),
    (
        "Atomic landing",
        "every ordered `pull_requests[].merged_at` is non-empty",
        "stop",
    ),
    (
        "Candidate",
        "each `head.sha` and explicit PR `headRefOid` equal body Candidate",
        "stop",
    ),
    (
        "Required checks",
        "each explicit-repository required check succeeds",
        "stop",
    ),
    (
        "Completion time",
        "stored top PR `mergedAt` is non-empty",
        "only then sentinel and guard",
    ),
]
stack_link = 'gh stack link --base "$BASE" "$BOTTOM_PR_URL" "$NEXT_PR_URL" ... "$TOP_PR_URL"'
stack_api = 'gh api --method GET "repos/$STACK_REPO/stacks?pull_request=$TOP_PR_NUMBER"'
layer_view = 'gh pr view "$LAYER_PR_NUMBER" --repo "$STACK_REPO" --json body,headRefOid,mergedAt'
layer_checks = 'gh pr checks "$LAYER_PR_NUMBER" --repo "$STACK_REPO" --required'


def stack_contract_errors(section: str) -> list[str]:
    errors: list[str] = []
    if policy_table(section, "Native stack delivery-unit composition") != expected_layer_rows:
        errors.append("stack layer/base binding drifted")
    if policy_table(section, "Native stack completion decision") != expected_stack_completion_rows:
        errors.append("native-stack completion decision drifted")
    for label, phrase in {
        "one unit per layer": "Bind one approved canonical Draft delivery unit per layer in bottom-to-top order",
        "canonical invocation": "Invoke the canonical bottom delivery unit unchanged for every layer",
        "URL-only link": stack_link,
        "explicit stack lookup": stack_api,
        "explicit layer view": layer_view,
        "explicit layer checks": layer_checks,
        "public-preview fields": "`number`, `base.ref`, and ordered `pull_requests[]` entries containing `number`, `merged_at`, `head.ref`, and `head.sha`",
        "atomic merge": "Use GitHub native atomic stack merge through `gh stack merge` or the native UI; never merge an individual PR.",
        "captain-authorized ready gate": "Only after each layer's required checks and review are green and the captain explicitly authorizes readiness, run `gh pr ready \"$LAYER_PR_URL\"` for every layer in bottom-to-top order.",
        "Draft merge refusal": "Do not call `gh stack merge` while any layer remains Draft.",
        "non-stack refusal": "A top PR merged outside exactly one matching native stack stops without sentinel or guard",
    }.items():
        if phrase not in section:
            errors.append(f"missing {label}")
    if "gh pr create" in section:
        errors.append("policy duplicates the canonical create recipe")
    if "gh pr merge" in section:
        errors.append("policy permits individual PR merge")
    return errors


require(
    not stack_contract_errors(decision_section),
    "native-stack contract failed: " + "; ".join(stack_contract_errors(decision_section)),
)
stack_mutants = {
    "trunk-sha-for-higher-layer": decision_section.replace(
        "approved `UNIT_CANDIDATE_SHA` immediately below",
        "approved trunk `$BASE_SHA`",
        1,
    ),
    "branch-link": decision_section.replace(
        stack_link,
        'gh stack link --base "$BASE" {bottom-branch} {top-branch}',
        1,
    ),
    "individual-merge": decision_section.replace("gh stack merge", "gh pr merge", 1),
}
for mutant_name, mutant in stack_mutants.items():
    require(
        stack_contract_errors(mutant),
        f"native-stack mutant survived: {mutant_name}",
    )

for phrase in [
    "merge-base diff at review request",
    "Mechanical, generated, vendor, and lock-file changes stay in both counts",
    "Counts choose topology only; they do not relax quality boundaries",
    "approve every title, full body, and bottom-to-top branch order",
    "Do not pass `--open`",
    "track the top PR",
    "pull_request CI for every layer",
]:
    require(phrase in local_extension, f"pr-merge native-stack mechanics are missing: {phrase}")
require(
    "waiting for the lower PR to merge blocks useful work" not in workflow,
    "workflow README adds a second stack-readiness condition",
)
require(
    "[`_mods/pr-merge.md`](./_mods/pr-merge.md#delivery-topology-decision)"
    in workflow
    and "dependent green layers, independent green slices, and numeric trigger"
    in workflow,
    "workflow README does not point to the authoritative topology predicates",
)
for phrase in [
    "overrides the released audit-link inputs",
    "spacedock status --workflow-dir {dir} --resolve {entity ref} --json",
    'git -C "$STATE_ROOT" rev-parse HEAD',
    'git -C "$STATE_ROOT" ls-files --full-name -- "$ENTITY_PATH"',
    'git -C "$STATE_ROOT" cat-file -e "$STATE_SHA:$STATE_RELATIVE_PATH"',
    'git -C "$STATE_ROOT" remote get-url origin',
    'gh repo view "$STATE_ORIGIN"',
    "/{state-owner}/{state-repo}/blob/{state-sha}/{state-relative-path}",
    "Stop if entity state is unresolved, untracked, or absent from the state commit",
    "Do not fall back to the code-worktree SHA, code-relative path, or `main`",
]:
    require(phrase in local_extension, f"pr-merge split-root audit link is missing: {phrase}")
for forbidden in ["gh " + "pr link"]:
    require(forbidden not in pr_merge_mod, f"runtime-only pr-merge contains policy: {forbidden}")
portable_delivery = subprocess.run(
    [sys.executable, "scripts/pr-merge-portable-delivery.test.py"],
    cwd=ROOT,
    text=True,
    capture_output=True,
)
require(
    portable_delivery.returncode == 0,
    "portable pr-merge delivery contract failed:\n"
    + portable_delivery.stdout
    + portable_delivery.stderr,
)
require(
    "cannot be authenticated; preserve the evidence and stop"
    in " ".join(state_recovery.split()),
    "state recovery does not fail closed after delivery artifact removal",
)

forbidden_tracked_references = {
    "removed delivery artifact field": "pr_" + "artifact_v1",
    "removed extraction marker": "pr-merge-audit-link-recipe:" + "start",
    "removed extraction marker end": "pr-merge-audit-link-recipe:" + "end",
    "obsolete contract test": "terminal-" + "transaction-contract-test.sh",
}
tracked_files = subprocess.run(
    ["git", "ls-files", "-z"],
    cwd=ROOT,
    check=True,
    capture_output=True,
).stdout.split(b"\0")
for raw_path in tracked_files:
    if not raw_path:
        continue
    tracked_path = ROOT / raw_path.decode("utf-8")
    if not tracked_path.is_file():
        continue
    try:
        tracked_text = tracked_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    for label, reference in forbidden_tracked_references.items():
        require(
            reference not in tracked_text,
            f"{label} remains in {tracked_path.relative_to(ROOT)}",
        )
published_smoke = (ROOT / "scripts/kc-dev-flow-published-tag-smoke.py").read_text(
    encoding="utf-8"
)
for phrase in [
    "DISABLE_PLUGIN_AUTOLOAD",
    "stream-json",
    "Claude did not isolate runtime plugin state to one explicit plugin",
    "tree_digest",
    "report revision differs from exact tag commit",
    "closed objects",
    "exactly the documented keys and no additional keys",
    "verdict_note",
]:
    require(phrase in published_smoke, f"published-tag smoke is missing boundary: {phrase}")
release_instructions = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
normalized_release_instructions = " ".join(release_instructions.split())
candidate_command = (
    'python3 scripts/kc-dev-flow-published-tag-smoke.py candidate --receipt "$RECEIPT"'
)
published_command = (
    "python3 scripts/kc-dev-flow-published-tag-smoke.py published "
    'kc-dev-flow-vX.Y.Z --candidate-receipt "$RECEIPT"'
)
require(
    candidate_command in normalized_release_instructions
    and published_command in normalized_release_instructions
    and normalized_release_instructions.index(candidate_command)
    < normalized_release_instructions.index(published_command)
    < normalized_release_instructions.index("Post-merge — LOCAL install sync"),
    "root release instructions do not order candidate proof before published identity and local sync",
)
require(
    len(workflow.splitlines()) <= 700,
    f"workflow README exceeds its 700-line runtime budget: {len(workflow.splitlines())}",
)
for phrase in [
    "Read [`runbooks/state-recovery.md`](./runbooks/state-recovery.md) only after",
    "Read [`runbooks/validation-evidence.md`](./runbooks/validation-evidence.md) when entering validation",
    "exactly one fresh-context EM verdict",
    "Implementation opens no reviewer loop",
    "Multi-model review is optional",
]:
    require(phrase in workflow, f"self-adoption is missing runtime-budget contract: {phrase}")
for forbidden in [
    "Cross-model gate before merge approval",
    "The independent cross-model gate",
]:
    require(forbidden not in workflow, f"self-adoption still requires universal multi-model review: {forbidden}")
require(
    "ship-flow:science-officer-em" not in workflow,
    "self-adoption still routes engineering judgment to the replaced Ship-Flow skill",
)
require(
    workflow.count("kc-dev-flow:science-officer-em") >= 2,
    "self-adoption does not route both EM gate and escalation to the replacement skill",
)
for phrase in [
    "## Local Profile",
    "| Project context |",
    "| Work items |",
    "| Iteration |",
    "| Execution state |",
    "| Delivery |",
    "| Gate verdicts |",
    "| Scope and irreversibility |",
    "| Observation | none |",
    "No binding YAML",
    "Origin re-observation:",
    "Reported scenario:",
    "Originating runtime kind:",
    "Re-observation artifact/revision:",
    "Equivalent-runtime rationale:",
    "Falsifier kind:",
    "is not an `N/A` condition",
    "costly_no recommendations",
    "engineering_judgment advisory record",
]:
    require(phrase in workflow, f"self-adoption is missing Local Profile boundary: {phrase}")

judgment_mod = (PLUGIN / "references/engineering-judgment.md").read_text(
    encoding="utf-8"
)
normalized_judgment = " ".join(judgment_mod.lower().split())
for phrase in [
    "governing contract and primary-source behavior",
    "reviewer confidence and labels carry no authority",
    "independent synthesis",
    "costly_no",
    "irreversible, schema, or scope-cut",
    "PASS | FAIL | UNKNOWN | UNAVAILABLE",
    "advisory",
    "unsupported is not a blocking basis",
    "schedule pressure, sunk cost, and an instruction to conclude",
    "before acceptance criteria expand",
    "independently releasable value surfaces",
    "governing contract's route discipline",
    "technical seams spanning one primary journey do not multiply",
    "actor count is evidence",
    "more than one value surface defaults to `narrow`",
    "exact scope exception is captain-approved and recorded by work-item authority",
    "re-estimating the same scope does not resolve an appetite mismatch",
]:
    require(
        " ".join(phrase.lower().split()) in normalized_judgment,
        f"engineering judgment is missing: {phrase}",
    )
require(
    re.search(r"^## Iteration-size precheck$", judgment_mod, re.MULTILINE)
    is not None,
    "engineering judgment is missing the top-level iteration-size precheck",
)
for forbidden in [
    "science officer",
    "first officer",
    "ship-flow",
    "github",
    "gh api",
    "model: opus",
    "science_officer_em",
    "upward_report",
    "subagent_type",
    "team_name",
    "reasoning: xhigh",
    "re-trigger",
]:
    require(
        forbidden not in normalized_judgment,
        f"engineering judgment imported orchestration-specific surface: {forbidden}",
    )
science_skill = (PLUGIN / "skills/science-officer-em/SKILL.md").read_text(
    encoding="utf-8"
)
normalized_science_skill = " ".join(science_skill.lower().split())
for phrase in [
    "canonical replacement",
    "ship-flow:science-officer-em",
    "science-officer",
    "科學官",
    "selected repository-local",
    "_mods/engineering-judgment.md",
    "invocation-only",
    "../../references/engineering-judgment.md",
    "parent decides whether judgment runs inline or in isolated context",
    "never spawns itself",
    "science_officer_em_upward_report",
    "engineering_judgment",
    "adjudications",
    "dissent",
    "disproof_condition",
    "authority_boundary",
    "deadline, sunk cost, mechanical green, and an orchestrator instruction",
    "status-only report is invalid",
    "activates without an explicit request and no stage selects the mod",
    "loaded mod is authoritative",
    "grants no task creation, sprint admission, scheduling, policy edit, provider posting, gate re-trigger, stage advancement, merge, archive, or closeout authority",
    "keep duplicated envelope and nested values identical",
    "capability tier above the artifact-producing worker",
    "highest available tier in fresh context with high reasoning",
    "contested, irreversible, low-confidence, or unresolved",
    "multi_model: recommended | not_needed",
    "closed objects",
    "exactly the documented keys and no additional keys",
    "verdict_note",
]:
    require(
        " ".join(phrase.lower().split()) in normalized_science_skill,
        f"Science Officer skill is missing: {phrase}",
    )
for forbidden in [
    "user-invocable:",
    "argument-hint:",
    "gh api",
    "model: opus",
    "reasoning: xhigh",
    "subagent_type",
    "team_name",
]:
    require(
        forbidden not in normalized_science_skill,
        f"Science Officer skill imported adapter-specific surface: {forbidden}",
    )

compatibility_block = re.search(
    r"```yaml\s+(science_officer_em_upward_report:.*?\n)```",
    science_skill,
    re.DOTALL,
)
require(
    compatibility_block is not None,
    "Science Officer compatibility report is not one bounded YAML block",
)
compatibility_yaml = compatibility_block.group(1)
for field in [
    "em_judgment",
    "evidence_synthesis",
    "risk_tradeoff_call",
    "recommendation",
    "route",
    "confidence",
    "fo_boundary",
    "engineering_judgment",
]:
    require(
        re.search(rf"^  {field}:\s*", compatibility_yaml, re.MULTILINE) is not None,
        f"Science Officer legacy envelope is missing nested field: {field}",
    )
for field in [
    "question",
    "revision",
    "evidence_synthesis",
    "adjudications",
    "risk_tradeoff",
    "recommendation",
    "route",
    "confidence",
    "dissent",
    "disproof_condition",
    "authority_boundary",
]:
    require(
        re.search(rf"^    {field}:\s*", compatibility_yaml, re.MULTILINE)
        is not None,
        f"Science Officer portable record is missing nested field: {field}",
    )

science_agent = (
    PLUGIN / "skills/science-officer-em/agents/openai.yaml"
).read_text(encoding="utf-8")
require(
    "$science-officer-em" in science_agent,
    "Science Officer UI metadata does not explicitly invoke the skill",
)
require(
    "science-officer-em" in package_readme,
    "package README is missing the Science Officer replacement skill",
)
require(
    "science-officer-em" in root_readme,
    "root README is missing the Science Officer replacement skill",
)

stage_headings = [
    "### `backlog`",
    "### `ideation`",
    "### `implementation`",
    "### `validation`",
    "### `done`",
]


def stage_body(heading: str) -> str:
    start = workflow.find(heading)
    require(start >= 0, f"self-adoption is missing stage: {heading}")
    boundaries = [
        position
        for position in [
            workflow.find("### `", start + len(heading)),
            workflow.find("\n## ", start + len(heading)),
        ]
        if position >= 0
    ]
    return workflow[start : min(boundaries, default=len(workflow))]


def selected_policy_mods(heading: str) -> set[str]:
    lines = stage_body(heading).splitlines()
    declarations = [
        (index, match.group(1))
        for index, line in enumerate(lines)
        if (match := re.fullmatch(r"Policy mods:[ \t]*(.*)", line)) is not None
    ]
    require(
        len(declarations) == 1,
        f"self-adoption stage must have one Policy mods declaration: {heading}",
    )
    index, first_line = declarations[0]
    declaration_lines = [first_line.strip()]
    for line in lines[index + 1 :]:
        if not line.strip():
            break
        declaration_lines.append(line.strip())
    text = " ".join(filter(None, declaration_lines))
    if text.rstrip(".") == "none":
        return set()
    selected = set(
        re.findall(r"\]\((?:\./)?(_mods/[^)#]+\.md)(?:#[^)]+)?\)", text)
    )
    require(selected, f"self-adoption stage has unreadable Policy mods: {heading}")
    return selected


real_workflow = workflow
workflow = """### `ideation`

Policy mods:

The stage body mentions [`_mods/journey-slicing.md`](./_mods/journey-slicing.md)
without selecting it.
"""
try:
    try:
        selected_policy_mods("### `ideation`")
        rejects_body_only_policy_link = False
    except SystemExit:
        rejects_body_only_policy_link = True
finally:
    workflow = real_workflow
require(
    rejects_body_only_policy_link,
    "Policy mods parser crossed a blank line into the stage body",
)


implementation_heading = "### `implementation`"
implementation_section = stage_body(implementation_heading)
implementation_mods = selected_policy_mods(implementation_heading)
normalized_implementation_section = " ".join(implementation_section.split())
require(
    implementation_mods == {"_mods/work-control-profile.md"},
    "implementation entry policy mods drifted",
)
for label, phrase in {
    "inactive locator rule": (
        "Links to mods not listed in `Policy mods` are inactive locators, "
        "not active policy, until their stage-native trigger is satisfied."
    ),
    "candidate revision trigger": "candidate revision",
    "changed-file map trigger": "changed-file map",
    "merge-base diff trigger": "merge-base diff size",
    "slice assessment trigger": "independent/dependent slice assessment",
    "pre-trigger unread boundary": (
        "Before those four facts exist, leave `_mods/pr-merge.md` unread."
    ),
}.items():
    require(
        phrase in normalized_implementation_section,
        f"implementation activation contract is missing {label}",
    )


for heading in stage_headings:
    selected = "_mods/engineering-judgment.md" in selected_policy_mods(heading)
    require(
        selected == (heading in {"### `ideation`", "### `validation`"}),
        f"engineering judgment stage selection is wrong: {heading}",
    )

journey_activation_failures: list[str] = []
normalized_adopt_skill = " ".join(adopt_skill.split())
for phrase in [
    "newly available optional policy mod",
    "separate adopt or decline decision",
    "A prior blanket instruction may supply the decision",
    "upgrade record still names each mod and its disposition",
    "Never vendor or select a newly available policy mod silently",
]:
    if phrase not in normalized_adopt_skill:
        journey_activation_failures.append(
            f"upgrade does not require explicit optional-mod choice: {phrase}"
        )

journey_reference = PLUGIN / "references/journey-slicing.md"
if not journey_reference.is_file():
    journey_activation_failures.append("package has no journey-slicing reference")
journey_vendored = ROOT / "docs/dev/_mods/journey-slicing.md"
if not journey_vendored.is_file():
    journey_activation_failures.append("self-adoption has no vendored journey-slicing mod")
elif (
    journey_reference.is_file()
    and journey_vendored.read_bytes() != journey_reference.read_bytes()
):
    journey_activation_failures.append("self-adoption journey-slicing mod is not canonical")

for heading in stage_headings:
    selected = "_mods/journey-slicing.md" in selected_policy_mods(heading)
    if selected != (heading == "### `ideation`"):
        journey_activation_failures.append(
            f"journey-slicing stage selection is wrong: {heading}"
        )

if "read only the named local `_mods/` files" not in continue_skill:
    journey_activation_failures.append(
        "continuation does not load policy from the active stage selection"
    )

kernel = required_files[4].read_text(encoding="utf-8")
normalized_kernel = " ".join(kernel.split())
if (
    "When the current stage selects `_mods/journey-slicing.md`, carve along "
    "the journey" not in normalized_kernel
):
    journey_activation_failures.append(
        "kernel applies journey slicing without the stage selection condition"
    )
if "Carve along the journey; apply journey slicing" in normalized_kernel:
    journey_activation_failures.append(
        "kernel still carries the unconditional journey-slicing command"
    )

require(
    not journey_activation_failures,
    "journey-slicing activation gaps: " + "; ".join(journey_activation_failures),
)

for phrase in [
    "Project context authority",
    "Work-item authority",
    "Iteration authority",
    "Delivery authority",
    "Observation is not authority",
    "backlog → ideation → implementation → validation → done",
    "smallest sufficient route",
    "resolves the committed product route before optional self-improvement",
    "Do not inspect `_debriefs/` or `_improvements/` on an ordinary continuation",
    "repository-local",
    "reusable kernel",
    "_improvements/state.yaml",
    "newer than the recorded cursor",
    "compare-and-swap",
    "Preserve the observation boundary at closure",
    "Unavailable re-observation is missing evidence",
]:
    require(phrase in kernel, f"kernel is missing invariant: {phrase}")
require(
    "coordinates bounded self-improvement before routing product work" not in kernel,
    "kernel still activates self-improvement before product routing",
)

product_doc = (ROOT / "PRODUCT.md").read_text(encoding="utf-8")
require(
    "routes committed product work before optional improvement harvesting" in product_doc
    and "explicitly requested" in product_doc,
    "PRODUCT.md does not state the product-first continuation value",
)
architecture_doc = (ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8")
for boundary in [
    "default product router",
    "conditional adopter-harvest reference",
    "downstream source intake",
]:
    require(boundary in architecture_doc, f"ARCHITECTURE.md is missing boundary: {boundary}")
require(
    re.search(
        r"Lower-level diagnosis and guards do not\s+replace re-observation",
        kernel,
    )
    is not None,
    "kernel is missing the lower-level evidence boundary",
)

lifecycle_start = kernel.find("## Lifecycle")
sprint_continuity_start = kernel.find("## Sprint continuity and autonomy")
require(
    0 <= lifecycle_start < sprint_continuity_start,
    "kernel lifecycle boundaries are missing or out of order",
)
lifecycle_contract = " ".join(
    kernel[lifecycle_start:sprint_continuity_start].split()
)
for phrase in [
    "inherited backlog criteria are hypotheses, not accepted outcome constraints",
    "value, governing constraint, or mechanism",
    "constraints explicitly imposed by the captain or governing authority",
    "rewrites a mechanism-shaped criterion to the value or failure it serves, or removes it",
    "may remain only when its absence fails a named value-level criterion",
    "the simpler route has proved insufficient",
    "the selected route still exposes the hazard",
    "structurally eliminates or bypasses the failure mode",
    "defense criterion is superseded",
    "Before the accepted outcome is recorded",
    "work-item authority records each inherited criterion's class and retain, rewrite, remove, or supersede disposition",
    "a governing constraint names its imposing authority",
    "a later reviewer can read the normalization",
]:
    require(
        phrase in lifecycle_contract,
        f"kernel ideation entry is missing seed normalization: {phrase}",
    )

route_discipline = kernel.find("## Route discipline")
require(route_discipline >= 0, "kernel is missing Route discipline")
require(
    kernel.find("## Sprint continuity and autonomy")
    < route_discipline
    < kernel.find("## Outcome discipline"),
    "Route discipline is not between Sprint continuity and Outcome discipline",
)
for phrase in [
    "approved outcome contract is its destination",
    "last accepted route",
    "observable lifecycle invariant",
    "plan-local pre/post mapping",
    "Work Control Profile",
    "reviewer's recorded `PASS`",
    "resolves only the ambiguity it names",
    "authority that owns the changed field or decision",
]:
    require(phrase in kernel, f"Route discipline is missing invariant: {phrase}")

# The three recorded pilot packets reported no uniquely attributable
# subtraction. Preserve the already-required decision checks and prevent the
# observe-only packet from returning to the normal implementation path.
change_shape_retirement_failures: list[str] = []


def check_order(text: str, label: str, markers: list[str]) -> None:
    positions = [text.find(marker) for marker in markers]
    missing = [marker for marker, position in zip(markers, positions) if position < 0]
    if missing:
        change_shape_retirement_failures.append(
            f"{label} is missing: {', '.join(missing)}"
        )
    elif positions != sorted(positions):
        change_shape_retirement_failures.append(f"{label} is out of sequence")


implementation_start = workflow.find("### `implementation`")
validation_start = workflow.find("### `validation`")
implementation_stage = workflow[implementation_start:validation_start]
normalized_implementation_stage = " ".join(implementation_stage.split())
check_order(
    kernel,
    "ordered route",
    [
        "1. **Accepted outcome.**",
        "2. **Recover the existing seam.**",
        "3. **Prove subtraction or bypass.**",
        "4. **Authorize only necessary addition.**",
        "5. **Run RED/GREEN.**",
        "6. **Validate fresh.**",
    ],
)
check_order(
    normalized_implementation_stage,
    "implementation stage",
    [
        "record a failing RED test",
        "map every changed file to an AC",
    ],
)
for phrase in [
    "Trace candidate surfaces backward from the accepted outcome",
    "try the cheapest reversible without-it instrument",
    "numbers do not authorize it",
    "Bind fresh validation to the final exact revision",
    "a changed head invalidates prior evidence",
]:
    if phrase not in normalized_kernel:
        change_shape_retirement_failures.append(
            f"kernel lost retained subtraction guard: {phrase}"
        )

for text, label in [
    (kernel, "kernel"),
    (workflow, "self-adoption workflow"),
]:
    for forbidden in [
        "Observe post-diff change shape",
        "If the largest added responsibility is removed",
        "git diff --numstat",
        "gross additions and gross deletions",
        "number-management incident",
        "defense-only rows",
        "Redundancy retirement",
    ]:
        if forbidden in text:
            change_shape_retirement_failures.append(
                f"{label} still requires retired bookkeeping: {forbidden}"
            )

require(
    not change_shape_retirement_failures,
    "change-shape retirement failures:\n- "
    + "\n- ".join(change_shape_retirement_failures),
)

# The kernel requires an absolute to name its enforcement point or be rewritten
# as a bounded claim, and that rule had none of its own. Four hand-audits of one
# file each found a different subset, so the registry replaces re-reading: every
# block carrying an absolute is judged once, and an unjudged or edited one fails
# here rather than in a fifth read-through.
absolutes = subprocess.run(
    [sys.executable, str(PLUGIN / "scripts/absolutes-check.py"), str(PLUGIN / "references/absolutes.registry")]
    + [str(p) for p in sorted((PLUGIN / "references").glob("*.md"))],
    capture_output=True,
    text=True,
)
require(absolutes.returncode == 0, absolutes.stdout.strip() or "absolutes-check failed")

for reference_name in [
    "engineering-judgment.md",
    "kernel.md",
    "reverse-recovery-audit.md",
    "work-control-profile.md",
]:
    canonical = (PLUGIN / "references" / reference_name).read_bytes()
    self_adoption = (ROOT / "docs/dev/_mods" / reference_name).read_bytes()
    require(canonical == self_adoption, f"self-adoption drifted: {reference_name}")

print("kc-dev-flow contract: PASS")
