#!/usr/bin/env python3
"""Fail-closed package contract for the portable kc-dev-flow product."""

from __future__ import annotations

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
    require(phrase in continue_skill, f"continue skill is missing boundary: {phrase}")
require(
    "If none or multiple candidates remain" not in continue_skill,
    "continue skill still blocks product work when no debrief home exists",
)
require(
    "stop with `UNKNOWN` instead of risking an overwrite" not in continue_skill,
    "continue skill still lets self-improvement storage block product routing",
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
for heading in stage_headings:
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
    end = min(boundaries, default=len(workflow))
    require(
        "Policy mods:" in workflow[start:end],
        f"self-adoption stage is missing Policy mods: {heading}",
    )
    selected = "_mods/engineering-judgment.md" in workflow[start:end]
    require(
        selected == (heading in {"### `ideation`", "### `validation`"}),
        f"engineering judgment stage selection is wrong: {heading}",
    )

kernel = required_files[4].read_text(encoding="utf-8")
for phrase in [
    "Project context authority",
    "Work-item authority",
    "Iteration authority",
    "Delivery authority",
    "Observation is not authority",
    "backlog → ideation → implementation → validation → done",
    "smallest sufficient route",
    "before routing product work",
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

# Collect independent gaps in one RED run.
change_shape_failures: list[str] = []


def check_order(text: str, label: str, markers: list[str]) -> None:
    positions = [text.find(marker) for marker in markers]
    missing = [marker for marker, position in zip(markers, positions) if position < 0]
    if missing:
        change_shape_failures.append(f"{label} is missing: {', '.join(missing)}")
    elif positions != sorted(positions):
        change_shape_failures.append(f"{label} is out of sequence")


normalized_kernel = " ".join(kernel.split())
implementation_start = workflow.find("### `implementation`")
validation_start = workflow.find("### `validation`")
implementation_stage = workflow[implementation_start:validation_start]
normalized_implementation_stage = " ".join(implementation_stage.split())
largest_responsibility_question = (
    "If the largest added responsibility is removed, which named AC fails?"
)
check_order(
    kernel,
    "ordered route",
    [
        "1. **Accepted outcome.**",
        "2. **Recover the existing seam.**",
        "3. **Prove subtraction or bypass.**",
        "4. **Authorize only necessary addition.**",
        "5. **Run RED/GREEN.**",
        "6. **Observe post-diff change shape.**",
        "7. **Validate fresh.**",
    ],
)
check_order(
    normalized_implementation_stage,
    "implementation stage",
    [
        "record a failing RED test",
        "map every changed file to an AC",
        largest_responsibility_question,
    ],
)
for text, label, phrases in [
    (
        normalized_kernel,
        "kernel",
        [
            largest_responsibility_question,
            "gross additions and gross deletions as separate facts",
            "Counts may focus inspection; they do not choose the responsibility or supply the answer.",
            "not a forecast, budget, score, or gate",
            "Numbers cannot gate or rank a change, offset additions with deletions",
        ],
    ),
    (
        normalized_implementation_stage,
        "implementation stage",
        [
            "**Success:**",
            "**No incremental value:**",
            "**Immediate stop/removal:**",
            "**Redundancy retirement:**",
            "classify the cohort Immediate stop/removal before considering other outcomes",
            "any newly attributable subtraction is Success, including a one-subtraction/two-defense cohort",
            "When neither is present, two defense-only rows are No incremental value.",
            "None of these outcomes is a per-change delivery gate.",
        ],
    ),
]:
    change_shape_failures.extend(
        f"{label} is missing: {phrase}" for phrase in phrases if phrase not in text
    )

require(
    not change_shape_failures,
    "change-shape contract failures:\n- " + "\n- ".join(change_shape_failures),
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
