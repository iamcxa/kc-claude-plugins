#!/usr/bin/env python3
"""Validate portable dev-flow work-context fields without a YAML dependency."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


SCHEMA = "dev-flow-work-context-check/v1"
CAPABILITY = "bound_field_validation"
CONTROL_MODE = "required"
ADAPTER = "scripts/dev-flow-work-context-check.py"
AUTHORITY = "captain or designated state migration owner"
PRODUCT_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SPRINT_PATTERN = re.compile(r"^S[1-9][0-9]*$")
PRODUCT_HEADING = re.compile(r"^##\s+`([^`]+)`\s*$")
SPRINT_HEADING = re.compile(r"^###\s+Sprint\s+(S[1-9][0-9]*)\b")
CONTROLLED_FIELD = re.compile(r"^(product|sprint)\s*:(.*)$")
COLLECTION_PREFIXES = ("[", "{", "|", ">", "&", "*", "!")


class ProviderError(Exception):
    """A required external input could not be read or interpreted."""


def finding(code: str, message: str, task: str | None = None) -> dict[str, str]:
    result = {"code": code, "message": message}
    if task is not None:
        result["task"] = task
    return result


def emit(payload: dict[str, Any], exit_code: int) -> int:
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return exit_code


def base_receipt(operation: str, outcome: str) -> dict[str, str]:
    return {
        "adapter": ADAPTER,
        "authority": AUTHORITY,
        "capability": CAPABILITY,
        "mode": CONTROL_MODE,
        "operation": operation,
        "outcome": outcome,
        "schema": SCHEMA,
    }


def unknown_payload(
    operation: str, inputs: dict[str, Any], error: Exception
) -> dict[str, Any]:
    payload: dict[str, Any] = base_receipt(operation, "UNKNOWN")
    payload.update(
        {
            "findings": [
                finding(
                    "provider_input_unavailable",
                    str(error),
                )
            ],
            "input": inputs,
        }
    )
    return payload


def read_input(path: Path, label: str) -> tuple[str, dict[str, str]]:
    try:
        raw = path.read_bytes()
        text = raw.decode("utf-8")
    except (OSError, UnicodeError) as error:
        raise ProviderError(f"{label} unavailable: {path}: {error}") from error
    return text, {
        "ref": str(path),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }


def load_products(path: Path) -> tuple[set[str], dict[str, str]]:
    raw, input_descriptor = read_input(path, "marketplace registry")
    try:
        document = json.loads(raw)
    except json.JSONDecodeError as error:
        raise ProviderError(
            f"marketplace registry is invalid JSON: {path}: {error}"
        ) from error

    plugins = document.get("plugins") if isinstance(document, dict) else None
    if not isinstance(plugins, list):
        raise ProviderError(f"marketplace registry has no plugins array: {path}")

    products = {"repo-platform"}
    for index, plugin in enumerate(plugins):
        name = plugin.get("name") if isinstance(plugin, dict) else None
        if not isinstance(name, str) or not PRODUCT_PATTERN.fullmatch(name):
            raise ProviderError(
                f"marketplace plugin at index {index} has no valid scalar name: {path}"
            )
        products.add(name)
    return products, input_descriptor


def load_sprint_pairs(
    path: Path, products: set[str]
) -> tuple[set[tuple[str, str]], dict[str, str]]:
    pairs: set[tuple[str, str]] = set()
    current_product: str | None = None
    raw, input_descriptor = read_input(path, "roadmap registry")
    for line in raw.splitlines():
        product_match = PRODUCT_HEADING.match(line)
        if product_match:
            current_product = product_match.group(1)
            continue
        sprint_match = SPRINT_HEADING.match(line)
        if not sprint_match:
            continue
        if current_product is None:
            raise ProviderError(
                f"roadmap sprint heading has no product section: {path}: {line}"
            )
        if current_product not in products:
            raise ProviderError(
                f"roadmap product is absent from the marketplace registry: "
                f"{current_product}"
            )
        pairs.add((current_product, sprint_match.group(1)))
    return pairs, input_descriptor


def controlled_frontmatter(
    raw: str, task_ref: str
) -> tuple[dict[str, str], list[dict[str, str]]]:
    lines = raw.splitlines()
    if not lines or lines[0] != "---":
        return {}, [
            finding(
                "frontmatter_missing",
                "task must begin with a frontmatter block",
                task_ref,
            )
        ]

    try:
        closing_index = lines.index("---", 1)
    except ValueError:
        return {}, [
            finding(
                "frontmatter_unterminated",
                "task frontmatter has no closing delimiter",
                task_ref,
            )
        ]

    values: dict[str, str] = {}
    findings: list[dict[str, str]] = []
    for line in lines[1:closing_index]:
        match = CONTROLLED_FIELD.match(line)
        if not match:
            continue
        key, raw_value = match.groups()
        if key in values:
            duplicate = finding(
                "controlled_field_duplicate",
                f"controlled field appears more than once: {key}",
                task_ref,
            )
            duplicate["field"] = key
            findings.append(duplicate)
            continue
        values[key] = raw_value.strip()
    return values, findings


def validate_controlled_fields(
    path: Path,
    products: set[str],
    sprint_pairs: set[tuple[str, str]],
) -> tuple[list[dict[str, str]], dict[str, str]]:
    task_ref = str(path)
    raw, input_descriptor = read_input(path, "task input")
    values, findings = controlled_frontmatter(raw, task_ref)
    if any(item["code"].startswith("frontmatter_") for item in findings):
        return findings, input_descriptor

    product = values.get("product", "")
    sprint = values.get("sprint", "")

    product_valid = False
    if not product:
        findings.append(
            finding("product_missing", "product must be a non-empty scalar", task_ref)
        )
    elif product.startswith(COLLECTION_PREFIXES):
        findings.append(
            finding(
                "product_not_scalar",
                "product must not use a collection, block, alias, or tag shape",
                task_ref,
            )
        )
    elif not PRODUCT_PATTERN.fullmatch(product):
        findings.append(
            finding(
                "product_malformed",
                "product must be an unquoted lowercase slug",
                task_ref,
            )
        )
    elif product not in products:
        findings.append(
            finding(
                "product_unknown",
                f"product is absent from the registry: {product}",
                task_ref,
            )
        )
    else:
        product_valid = True

    sprint_valid = False
    if not sprint:
        sprint_valid = True
    elif sprint.startswith(COLLECTION_PREFIXES):
        findings.append(
            finding(
                "sprint_not_scalar",
                "sprint must not use a collection, block, alias, or tag shape",
                task_ref,
            )
        )
    elif not SPRINT_PATTERN.fullmatch(sprint):
        findings.append(
            finding(
                "sprint_malformed",
                "sprint must be blank or use S<number>",
                task_ref,
            )
        )
    else:
        sprint_valid = True

    if (
        product_valid
        and sprint
        and sprint_valid
        and (product, sprint) not in sprint_pairs
    ):
        findings.append(
            finding(
                "sprint_unregistered",
                f"product and sprint pair is absent from the roadmap: {product}/{sprint}",
                task_ref,
            )
        )
    return findings, input_descriptor


def provider_inputs(
    marketplace: Path,
    roadmap: Path,
) -> tuple[
    set[str],
    set[tuple[str, str]],
    dict[str, str],
    dict[str, str],
]:
    products, marketplace_input = load_products(marketplace)
    sprint_pairs, roadmap_input = load_sprint_pairs(roadmap, products)
    return products, sprint_pairs, marketplace_input, roadmap_input


def hash_json(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def evidence_for(inputs: dict[str, Any]) -> list[str]:
    evidence: list[str] = []
    for name in sorted(inputs):
        descriptor = inputs[name]
        if isinstance(descriptor, dict) and "sha256" in descriptor:
            evidence.append(f"{name}:sha256:{descriptor['sha256']}")
    return evidence


def command_validate(args: argparse.Namespace) -> int:
    task = Path(args.task)
    marketplace = Path(args.marketplace)
    roadmap = Path(args.roadmap)
    unresolved_inputs = {
        "marketplace": str(marketplace),
        "roadmap": str(roadmap),
        "task": str(task),
    }
    try:
        products, sprint_pairs, marketplace_input, roadmap_input = provider_inputs(
            marketplace, roadmap
        )
        findings, task_input = validate_controlled_fields(task, products, sprint_pairs)
    except ProviderError as error:
        return emit(unknown_payload("validate", unresolved_inputs, error), 2)

    outcome = "FAIL" if findings else "PASS"
    inputs = {
        "marketplace": marketplace_input,
        "roadmap": roadmap_input,
        "task": task_input,
    }
    payload: dict[str, Any] = base_receipt("validate", outcome)
    payload.update(
        {
            "evidence": evidence_for(inputs),
            "findings": findings,
            "input": inputs,
            "input_revision": hash_json(inputs),
        }
    )
    return emit(
        payload,
        1 if findings else 0,
    )


def live_task_paths(state_dir: Path) -> list[Path]:
    if not state_dir.is_dir():
        raise ProviderError(f"state directory unavailable: {state_dir}")

    paths: list[Path] = []
    for path in state_dir.rglob("*.md"):
        relative = path.relative_to(state_dir)
        if any(part.startswith("_") for part in relative.parts[:-1]):
            continue
        if len(relative.parts) == 1 or relative.name == "index.md":
            paths.append(path)
    return sorted(paths, key=lambda path: path.relative_to(state_dir).as_posix())


def git_output(workdir: Path, label: str, *arguments: str) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(workdir), *arguments],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        detail = (
            error.stderr.strip()
            if isinstance(error, subprocess.CalledProcessError) and error.stderr
            else str(error)
        )
        raise ProviderError(
            f"{label} Git identity unavailable: {workdir}: {detail}"
        ) from error
    return result.stdout.strip()


def provider_common_dir(marketplace: Path, roadmap: Path) -> Path:
    roots = []
    for label, path in (
        ("marketplace registry", marketplace),
        ("roadmap registry", roadmap),
    ):
        top_level = Path(git_output(path.parent, label, "rev-parse", "--show-toplevel"))
        try:
            roots.append(top_level.resolve(strict=True))
        except OSError as error:
            raise ProviderError(
                f"{label} Git root cannot be resolved: {top_level}: {error}"
            ) from error
    if roots[0] != roots[1]:
        raise ProviderError(
            "marketplace and roadmap registries do not share one Git repository"
        )

    common_dir = Path(
        git_output(
            roots[0],
            "provider repository",
            "rev-parse",
            "--path-format=absolute",
            "--git-common-dir",
        )
    )
    try:
        return common_dir.resolve(strict=True)
    except OSError as error:
        raise ProviderError(
            f"provider Git common directory cannot be resolved: {common_dir}: {error}"
        ) from error


def state_snapshot(state_dir: Path, provider_common: Path) -> dict[str, str]:
    if state_dir.is_symlink():
        raise ProviderError(f"state directory must not be a symlink: {state_dir}")

    top_level = Path(git_output(state_dir, "state", "rev-parse", "--show-toplevel"))
    try:
        expected = state_dir.resolve(strict=True)
        observed = top_level.resolve(strict=True)
    except OSError as error:
        raise ProviderError(
            f"state Git root cannot be resolved: {state_dir}: {error}"
        ) from error
    if observed != expected:
        raise ProviderError(
            f"state directory is not the Git worktree root: {state_dir}"
        )

    state_common = Path(
        git_output(
            state_dir,
            "state",
            "rev-parse",
            "--path-format=absolute",
            "--git-common-dir",
        )
    )
    try:
        state_common = state_common.resolve(strict=True)
    except OSError as error:
        raise ProviderError(
            f"state Git common directory cannot be resolved: {state_common}: {error}"
        ) from error
    if state_common != provider_common:
        raise ProviderError("state worktree does not belong to the provider repository")

    branch = git_output(
        state_dir, "state", "symbolic-ref", "--quiet", "--short", "HEAD"
    )
    if branch != "spacedock-state/dev":
        raise ProviderError(
            f"state worktree has unexpected branch: {branch or '<detached>'}"
        )

    revision = git_output(state_dir, "state", "rev-parse", "HEAD^{commit}")
    dirty = git_output(
        state_dir,
        "state",
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
    )
    if dirty:
        raise ProviderError(f"state worktree is dirty: {state_dir}")
    return {"branch": branch, "revision": revision}


def command_audit(args: argparse.Namespace) -> int:
    state_dir = Path(args.state_dir)
    marketplace = Path(args.marketplace)
    roadmap = Path(args.roadmap)
    unresolved_inputs = {
        "marketplace": str(marketplace),
        "roadmap": str(roadmap),
        "state_dir": str(state_dir),
    }
    try:
        products, sprint_pairs, marketplace_input, roadmap_input = provider_inputs(
            marketplace, roadmap
        )
        provider_common = provider_common_dir(marketplace, roadmap)
        state_identity = state_snapshot(state_dir, provider_common)
        paths = live_task_paths(state_dir)
        if not paths:
            raise ProviderError(
                f"state directory contains no live work items: {state_dir}"
            )
        findings: list[dict[str, str]] = []
        product_invalid_tasks: set[str] = set()
        iteration_invalid_tasks: set[str] = set()
        state_entries: list[dict[str, str]] = []
        for path in paths:
            relative = path.relative_to(state_dir).as_posix()
            path_findings, task_input = validate_controlled_fields(
                path, products, sprint_pairs
            )
            state_entries.append({"ref": relative, "sha256": task_input["sha256"]})
            for item in path_findings:
                item["task"] = relative
                findings.append(item)
                code = item["code"]
                duplicate_field = (
                    item.get("field") if code == "controlled_field_duplicate" else None
                )
                if (
                    code.startswith("frontmatter_")
                    or code.startswith("product_")
                    or duplicate_field == "product"
                ):
                    product_invalid_tasks.add(relative)
                if (
                    code.startswith("frontmatter_")
                    or code.startswith("product_")
                    or code.startswith("sprint_")
                    or duplicate_field in {"product", "sprint"}
                ):
                    iteration_invalid_tasks.add(relative)
        if state_snapshot(state_dir, provider_common) != state_identity:
            raise ProviderError(f"state revision changed during audit: {state_dir}")
    except ProviderError as error:
        return emit(unknown_payload("audit", unresolved_inputs, error), 2)

    product_authoritative = not product_invalid_tasks
    iteration_authoritative = (
        bool(args.iteration_migration_complete) and not iteration_invalid_tasks
    )
    outcome = "FAIL" if findings else "PASS"
    inputs = {
        "declaration": {
            "iteration_migration_complete": bool(args.iteration_migration_complete)
        },
        "marketplace": marketplace_input,
        "roadmap": roadmap_input,
        "state": {
            "branch": state_identity["branch"],
            "live_items": len(state_entries),
            "ref": str(state_dir),
            "revision": state_identity["revision"],
            "sha256": hash_json(state_entries),
        },
    }
    payload = base_receipt("audit", outcome)
    payload.update(
        {
            "counts": {
                "invalid_iteration_items": len(iteration_invalid_tasks),
                "invalid_product_items": len(product_invalid_tasks),
                "live_items": len(paths),
            },
            "evidence": evidence_for(inputs),
            "findings": findings,
            "input": inputs,
            "input_revision": hash_json(inputs),
            "iteration_filter_authoritative": iteration_authoritative,
            "iteration_migration_complete_declared": bool(
                args.iteration_migration_complete
            ),
            "product_filter_authoritative": product_authoritative,
        }
    )
    return emit(
        payload,
        1 if findings else 0,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate dev-flow product and sprint work-context fields."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser(
        "validate", help="validate one new or changed work item"
    )
    validate_parser.add_argument("--task", required=True)
    validate_parser.add_argument("--marketplace", required=True)
    validate_parser.add_argument("--roadmap", required=True)
    validate_parser.set_defaults(handler=command_validate)

    audit_parser = subparsers.add_parser(
        "audit", help="audit non-archived live work items"
    )
    audit_parser.add_argument("--state-dir", required=True)
    audit_parser.add_argument("--marketplace", required=True)
    audit_parser.add_argument("--roadmap", required=True)
    audit_parser.add_argument(
        "--iteration-migration-complete",
        action="store_true",
        help=(
            "record the migration owner's assertion that blank sprint fields are "
            "genuinely unscheduled; invalid live fields still keep iteration "
            "filtering non-authoritative"
        ),
    )
    audit_parser.set_defaults(handler=command_audit)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.handler(args)


if __name__ == "__main__":
    sys.exit(main())
