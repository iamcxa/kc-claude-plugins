#!/usr/bin/env python3
"""Run the release-closeout kc-dev-flow EM smoke against an exact published tag."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE_SOURCE = "iamcxa/kc-claude-plugins"
REPOSITORY_URL = f"https://github.com/{MARKETPLACE_SOURCE}.git"
TAG_PATTERN = re.compile(r"kc-dev-flow-v\d+\.\d+\.\d+")
ROUTES = {"proceed", "narrow", "return", "block", "costly_no"}
CONFIDENCES = {"high", "medium", "low"}
MULTI_MODEL = {"recommended", "not_needed"}


class SmokeError(RuntimeError):
    """A bounded setup, invocation, or report-contract failure."""


def run(
    command: list[str],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    timeout: int = 240,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip().splitlines()
        tail = " | ".join(detail[-3:]) if detail else "no diagnostic"
        raise SmokeError(f"{command[0]} command failed: {tail}")
    return result


def without_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise SmokeError(f"report contains duplicate key: {key}")
        result[key] = value
    return result


def exact_object(value: object, name: str, fields: set[str]) -> dict[str, object]:
    if not isinstance(value, dict):
        raise SmokeError(f"report field must be an object: {name}")
    actual = set(value)
    if actual != fields:
        missing = sorted(fields - actual)
        extra = sorted(actual - fields)
        raise SmokeError(f"report object has wrong fields: {name}; missing={missing}; extra={extra}")
    return value


def text_field(value: dict[str, object], name: str, *, allow_empty: bool = False) -> str:
    field = value[name]
    if not isinstance(field, str) or (not allow_empty and not field.strip()):
        raise SmokeError(f"report field is missing or empty: {name}")
    return field


def validate_report(report: str, expected_revision: str) -> None:
    candidate = report.strip()
    if candidate.startswith("```"):
        lines = candidate.splitlines()
        if len(lines) < 3 or not lines[-1].strip().startswith("```"):
            raise SmokeError("report code fence is incomplete")
        candidate = "\n".join(lines[1:-1]).strip()
    try:
        document = json.loads(candidate, object_pairs_hook=without_duplicate_keys)
    except json.JSONDecodeError as exc:
        raise SmokeError(f"report is not one structural JSON/YAML document: {exc}") from exc

    root = exact_object(
        document,
        "root",
        {"science_officer_em_upward_report"},
    )
    envelope = exact_object(
        root["science_officer_em_upward_report"],
        "science_officer_em_upward_report",
        {
            "em_judgment",
            "evidence_synthesis",
            "risk_tradeoff_call",
            "recommendation",
            "route",
            "confidence",
            "multi_model",
            "fo_boundary",
            "engineering_judgment",
        },
    )
    for name in [
        "em_judgment",
        "evidence_synthesis",
        "risk_tradeoff_call",
        "recommendation",
        "route",
        "confidence",
        "multi_model",
    ]:
        text_field(envelope, name)
    text_field(envelope, "fo_boundary", allow_empty=True)

    judgment = exact_object(
        envelope["engineering_judgment"],
        "engineering_judgment",
        {
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
        },
    )
    for name in [
        "question",
        "revision",
        "evidence_synthesis",
        "risk_tradeoff",
        "recommendation",
        "route",
        "confidence",
        "disproof_condition",
        "authority_boundary",
    ]:
        text_field(judgment, name)
    text_field(judgment, "dissent", allow_empty=True)

    adjudications = judgment["adjudications"]
    if not isinstance(adjudications, list) or not adjudications:
        raise SmokeError("report adjudications must be a non-empty list")
    for index, item in enumerate(adjudications):
        adjudication = exact_object(
            item,
            f"adjudications[{index}]",
            {"finding", "disposition", "basis"},
        )
        for name in ["finding", "disposition", "basis"]:
            text_field(adjudication, name)
        if adjudication["disposition"] not in {"supported", "unsupported", "unresolved"}:
            raise SmokeError(f"report adjudication disposition is invalid at index {index}")

    if envelope["route"] not in ROUTES or judgment["route"] not in ROUTES:
        raise SmokeError("report route is invalid")
    if envelope["confidence"] not in CONFIDENCES or judgment["confidence"] not in CONFIDENCES:
        raise SmokeError("report confidence is invalid")
    if envelope["multi_model"] not in MULTI_MODEL:
        raise SmokeError("report multi_model is invalid")
    if judgment["revision"] != expected_revision:
        raise SmokeError(
            f"report revision differs from exact tag commit: {judgment['revision']} != {expected_revision}"
        )
    for outer, inner in [
        ("evidence_synthesis", "evidence_synthesis"),
        ("risk_tradeoff_call", "risk_tradeoff"),
        ("recommendation", "recommendation"),
        ("route", "route"),
        ("confidence", "confidence"),
    ]:
        if envelope[outer] != judgment[inner]:
            raise SmokeError(f"report compatibility values differ: {outer} != {inner}")


def installed_plugin(root: Path, host: str) -> Path:
    if host == "claude":
        candidates = list(root.glob(".claude/plugins/cache/*/kc-dev-flow/*"))
    else:
        candidates = list(root.glob("plugins/cache/*/kc-dev-flow/*"))
    matches = [path for path in candidates if (path / "skills/science-officer-em/SKILL.md").is_file()]
    if len(matches) != 1:
        raise SmokeError(f"{host} installed plugin path count is {len(matches)}, expected 1")
    return matches[0]


def installed_version(plugin: Path) -> str:
    versions = {
        json.loads(manifest.read_text(encoding="utf-8"))["version"]
        for manifest in [
            plugin / ".claude-plugin/plugin.json",
            plugin / ".codex-plugin/plugin.json",
        ]
        if manifest.is_file()
    }
    if len(versions) != 1:
        raise SmokeError(f"installed plugin manifests disagree: {sorted(versions)}")
    return versions.pop()


def tree_digest(root: Path) -> str:
    records: list[dict[str, object]] = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            raise SmokeError(f"plugin tree contains unsupported symlink: {relative}")
        if path.is_file():
            records.append(
                {
                    "path": relative,
                    "executable": bool(path.stat().st_mode & 0o111),
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                }
            )
    return hashlib.sha256(
        json.dumps(records, separators=(",", ":"), sort_keys=True).encode("utf-8")
    ).hexdigest()


def package_identity(checkout: Path) -> tuple[str, str, str]:
    marketplace_data = json.loads(
        (checkout / ".claude-plugin/marketplace.json").read_text(encoding="utf-8")
    )
    marketplace = marketplace_data["name"]
    version = installed_version(checkout / "kc-dev-flow")
    marketplace_versions = {
        entry["version"]
        for entry in marketplace_data["plugins"]
        if entry["name"] == "kc-dev-flow"
    }
    if marketplace_versions != {version}:
        raise SmokeError(
            f"marketplace version differs from manifests: {sorted(marketplace_versions)} != {version}"
        )
    return marketplace, version, tree_digest(checkout / "kc-dev-flow")


def install_verified_plugin(
    checkout: Path,
    host: str,
    state_root: Path,
    marketplace: str,
    expected_version: str,
    expected_digest: str,
    operator_env: dict[str, str],
    timeout: int,
    *,
    codex_auth: Path | None = None,
) -> Path:
    home = state_root / f"{host}-home"
    home.mkdir()
    if host == "claude":
        install_env = operator_env | {"HOME": str(home)}
        run(
            ["claude", "plugin", "marketplace", "add", str(checkout)],
            env=install_env,
            timeout=timeout,
        )
        run(
            ["claude", "plugin", "install", f"kc-dev-flow@{marketplace}"],
            env=install_env,
            timeout=timeout,
        )
    elif host == "codex":
        if codex_auth is not None:
            (home / "auth.json").symlink_to(codex_auth)
        install_env = operator_env | {"CODEX_HOME": str(home)}
        run(
            ["codex", "plugin", "marketplace", "add", str(checkout), "--json"],
            env=install_env,
            timeout=timeout,
        )
        run(
            ["codex", "plugin", "add", f"kc-dev-flow@{marketplace}", "--json"],
            env=install_env,
            timeout=timeout,
        )
    else:
        raise SmokeError(f"unsupported host: {host}")

    plugin = installed_plugin(home, host)
    observed_version = installed_version(plugin)
    if observed_version != expected_version:
        raise SmokeError(
            f"{host.title()} installed version differs from expected identity: "
            f"{observed_version} != {expected_version}"
        )
    if tree_digest(plugin) != expected_digest:
        raise SmokeError(f"{host.title()} installed tree differs from expected identity")
    return plugin


def claude_stream_result(
    output: str, expected_plugin: Path, expected_version: str
) -> str:
    events: list[dict[str, object]] = []
    for line in output.splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise SmokeError(f"Claude returned invalid stream JSON: {exc}") from exc
        if not isinstance(event, dict):
            raise SmokeError("Claude stream event is not an object")
        events.append(event)

    init_events = [
        event
        for event in events
        if event.get("type") == "system" and event.get("subtype") == "init"
    ]
    if len(init_events) != 1:
        raise SmokeError(f"Claude init event count is {len(init_events)}, expected 1")
    plugins = init_events[0].get("plugins")
    if not isinstance(plugins, list) or len(plugins) != 1 or not isinstance(plugins[0], dict):
        raise SmokeError("Claude did not isolate runtime plugin state to one explicit plugin")
    observed = plugins[0]
    if (
        observed.get("name") != "kc-dev-flow"
        or observed.get("version") != expected_version
        or Path(str(observed.get("path", ""))).resolve() != expected_plugin.resolve()
    ):
        raise SmokeError(f"Claude loaded an unexpected plugin: {observed}")

    results = [
        event.get("result")
        for event in events
        if event.get("type") == "result" and isinstance(event.get("result"), str)
    ]
    if len(results) != 1 or not results[0].strip():
        raise SmokeError(f"Claude final report count is {len(results)}, expected 1")
    return results[0]


def codex_result(output: str) -> str:
    messages: list[str] = []
    for raw_line in output.splitlines():
        try:
            event = json.loads(raw_line)
        except json.JSONDecodeError:
            continue
        item = event.get("item", {})
        if (
            event.get("type") == "item.completed"
            and item.get("type") == "agent_message"
            and isinstance(item.get("text"), str)
        ):
            messages.append(item["text"])
    if not messages:
        raise SmokeError("Codex returned no final agent report")
    return messages[-1]


def smoke_prompt(artifact: str, revision: str) -> str:
    return f"""Use $science-officer-em in explicit invocation-only mode.
Evaluate this bounded hypothetical: a reversible documentation-only rename has passing checks.
Return only one JSON object, which is valid YAML 1.2, containing the complete science_officer_em_upward_report for artifact {artifact}.
Include every compatibility and nested field, including multi_model.
Treat the root object, science_officer_em_upward_report, engineering_judgment, and every adjudication item as closed objects: emit exactly the documented keys and no additional keys, including verdict_note.
Set engineering_judgment.revision to exactly {revision}.
Do not claim a stage verdict or mutate files."""


def load_candidate_receipt(path: Path) -> dict[str, object]:
    try:
        document = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=without_duplicate_keys,
        )
    except json.JSONDecodeError as exc:
        raise SmokeError(f"candidate receipt is not structural JSON: {exc}") from exc
    receipt = exact_object(
        document,
        "candidate receipt",
        {
            "schema",
            "candidate_revision",
            "version",
            "tree_sha256",
            "reports",
        },
    )
    if receipt["schema"] != "kc-dev-flow-candidate-smoke/v1":
        raise SmokeError(f"candidate receipt schema is invalid: {receipt['schema']!r}")
    revision = receipt["candidate_revision"]
    if not isinstance(revision, str) or re.fullmatch(r"[0-9a-f]{40,64}", revision) is None:
        raise SmokeError(f"candidate receipt candidate_revision is invalid: {revision!r}")
    version = receipt["version"]
    if not isinstance(version, str) or re.fullmatch(r"\d+\.\d+\.\d+", version) is None:
        raise SmokeError(f"candidate receipt version is invalid: {version!r}")
    digest = receipt["tree_sha256"]
    if not isinstance(digest, str) or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
        raise SmokeError(f"candidate receipt tree_sha256 is invalid: {digest!r}")
    reports = exact_object(
        receipt["reports"], "candidate receipt reports", {"claude", "codex"}
    )
    if reports != {"claude": "PASS", "codex": "PASS"}:
        raise SmokeError(f"candidate receipt reports are invalid: {reports!r}")
    return receipt


def run_candidate_smoke(receipt_path: Path, timeout: int) -> dict[str, object]:
    for command in ["git", "claude", "codex"]:
        if shutil.which(command) is None:
            raise SmokeError(f"required command is unavailable: {command}")
    if receipt_path.exists():
        raise SmokeError(f"candidate receipt already exists: {receipt_path}")

    checkout = ROOT
    revision = run(["git", "rev-parse", "HEAD"], cwd=checkout).stdout.strip()
    if re.fullmatch(r"[0-9a-f]{40,64}", revision) is None:
        raise SmokeError(f"candidate revision is invalid: {revision!r}")
    if run(["git", "status", "--porcelain"], cwd=checkout).stdout.strip():
        raise SmokeError("candidate checkout must be clean")

    marketplace, version, source_digest = package_identity(checkout)

    operator_env = os.environ.copy()
    operator_home = Path(operator_env.get("HOME", ""))
    if not operator_home.is_dir():
        raise SmokeError("operator HOME is unavailable")

    with tempfile.TemporaryDirectory(prefix="kc-dev-flow-candidate-") as candidate_tmp:
        candidate_root = Path(candidate_tmp)
        runtime_root = candidate_root / "runtime"
        runtime_root.mkdir()
        runtime_note = "There is no repository workflow context. Invoke installed skills directly and do not search outside this directory.\n"
        (runtime_root / "CLAUDE.md").write_text(runtime_note, encoding="utf-8")
        (runtime_root / "AGENTS.md").write_text(runtime_note, encoding="utf-8")
        mcp_config = runtime_root / "empty-mcp.json"
        mcp_config.write_text('{"mcpServers": {}}\n', encoding="utf-8")

        claude_plugin = install_verified_plugin(
            checkout,
            "claude",
            candidate_root,
            marketplace,
            version,
            source_digest,
            operator_env,
            timeout,
        )
        claude_runtime_env = operator_env | {"DISABLE_PLUGIN_AUTOLOAD": "1"}
        run(
            ["claude", "auth", "status", "--json"],
            env=claude_runtime_env,
            timeout=timeout,
        )
        prompt = smoke_prompt(f"candidate@{revision}", revision)
        claude_output = run(
            [
                "claude",
                "--setting-sources",
                "local",
                "--plugin-dir",
                str(claude_plugin),
                "--strict-mcp-config",
                "--mcp-config",
                str(mcp_config),
                "--allowedTools",
                "Read,Grep,Glob",
                "--effort",
                "high",
                "--max-turns",
                "8",
                "--output-format",
                "stream-json",
                "--verbose",
                "-p",
                prompt,
            ],
            cwd=runtime_root,
            env=claude_runtime_env,
            timeout=timeout,
        )
        validate_report(
            claude_stream_result(claude_output.stdout, claude_plugin, version),
            revision,
        )

        source_codex_home = Path(
            operator_env.get("CODEX_HOME", operator_home / ".codex")
        )
        auth_file = source_codex_home / "auth.json"
        if not auth_file.is_file():
            raise SmokeError("Codex auth.json is unavailable; run codex login first")
        codex_plugin = install_verified_plugin(
            checkout,
            "codex",
            candidate_root,
            marketplace,
            version,
            source_digest,
            operator_env,
            timeout,
            codex_auth=auth_file,
        )
        codex_home = candidate_root / "codex-home"
        codex_env = operator_env | {"CODEX_HOME": str(codex_home)}
        codex_output = run(
            [
                "codex",
                "exec",
                "--skip-git-repo-check",
                "--ephemeral",
                "--json",
                "-C",
                str(runtime_root),
                "-s",
                "read-only",
                "-c",
                'model_reasoning_effort="high"',
                "-c",
                'approval_policy="never"',
                prompt,
            ],
            env=codex_env,
            timeout=timeout,
        )
        validate_report(codex_result(codex_output.stdout), revision)

    receipt: dict[str, object] = {
        "schema": "kc-dev-flow-candidate-smoke/v1",
        "candidate_revision": revision,
        "version": version,
        "tree_sha256": source_digest,
        "reports": {"claude": "PASS", "codex": "PASS"},
    }
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return receipt


def run_published_smoke(
    tag: str, candidate_receipt_path: Path, timeout: int
) -> dict[str, object]:
    if TAG_PATTERN.fullmatch(tag) is None:
        raise SmokeError("tag must match kc-dev-flow-vX.Y.Z")
    receipt = load_candidate_receipt(candidate_receipt_path)
    for command in ["git", "claude", "codex"]:
        if shutil.which(command) is None:
            raise SmokeError(f"required command is unavailable: {command}")

    operator_env = os.environ.copy()
    with tempfile.TemporaryDirectory(prefix="kc-dev-flow-published-") as published_tmp:
        published_root = Path(published_tmp)
        checkout = published_root / "repo"
        run(
            [
                "git",
                "clone",
                "--depth",
                "1",
                "--branch",
                tag,
                "--single-branch",
                REPOSITORY_URL,
                str(checkout),
            ],
            timeout=timeout,
        )
        revision = run(["git", "rev-parse", "HEAD"], cwd=checkout).stdout.strip()
        observed_tag = run(
            ["git", "describe", "--tags", "--exact-match", "HEAD"], cwd=checkout
        ).stdout.strip()
        if observed_tag != tag:
            raise SmokeError(f"checkout resolved {observed_tag!r}, expected {tag!r}")

        marketplace, version, source_digest = package_identity(checkout)
        expected_version = tag.removeprefix("kc-dev-flow-v")
        if version != expected_version:
            raise SmokeError(
                f"published tag version differs from manifests: {expected_version} != {version}"
            )
        if version != receipt["version"]:
            raise SmokeError(
                f"published version differs from candidate receipt: {version} != {receipt['version']}"
            )
        if source_digest != receipt["tree_sha256"]:
            raise SmokeError("published source tree differs from candidate receipt")

        for host in ["claude", "codex"]:
            install_verified_plugin(
                checkout,
                host,
                published_root,
                marketplace,
                receipt["version"],
                receipt["tree_sha256"],
                operator_env,
                timeout,
            )

        return {
            "schema": "kc-dev-flow-published-tag-smoke/v2",
            "tag": tag,
            "candidate_revision": receipt["candidate_revision"],
            "published_revision": revision,
            "version": version,
            "tree_sha256": source_digest,
            "installed": {"claude": "PASS", "codex": "PASS"},
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a kc-dev-flow candidate with both hosts, then bind its exact published tag."
    )
    parser.add_argument(
        "--validate-report",
        metavar="PATH",
        help="validate one report file, or - for stdin, without invoking a host",
    )
    parser.add_argument(
        "--expected-revision",
        help="exact 40-64 character Git revision required by --validate-report",
    )
    modes = parser.add_subparsers(dest="mode")
    candidate = modes.add_parser(
        "candidate", help="invoke both isolated hosts against the clean checkout"
    )
    candidate.add_argument(
        "--receipt", required=True, type=Path, help="new candidate receipt path"
    )
    candidate.add_argument(
        "--timeout", type=int, default=240, help="seconds per external command"
    )
    published = modes.add_parser(
        "published", help="bind a published tag to a validated candidate receipt"
    )
    published.add_argument("tag", help="published tag, for example kc-dev-flow-v2.2.0")
    published.add_argument(
        "--candidate-receipt",
        required=True,
        type=Path,
        help="candidate receipt written before publication",
    )
    published.add_argument(
        "--timeout", type=int, default=240, help="seconds per external command"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.validate_report:
            if not args.expected_revision or re.fullmatch(
                r"[0-9a-f]{40,64}", args.expected_revision
            ) is None:
                raise SmokeError(
                    "--validate-report requires --expected-revision with a 40-64 character lowercase Git revision"
                )
            report = sys.stdin.read() if args.validate_report == "-" else Path(args.validate_report).read_text(encoding="utf-8")
            validate_report(report, args.expected_revision)
            print("report: PASS")
            return 0
        if args.mode == "candidate":
            result = run_candidate_smoke(args.receipt, args.timeout)
        elif args.mode == "published":
            result = run_published_smoke(
                args.tag, args.candidate_receipt, args.timeout
            )
        else:
            raise SmokeError("candidate or published mode is required")
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, subprocess.TimeoutExpired, SmokeError) as exc:
        print(f"published-tag smoke: FAIL — {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
