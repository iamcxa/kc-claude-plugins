#!/usr/bin/env python3
"""Load the shared core and one selected profile-stage contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


ROUTES = {
    "poc-exploration": {
        "implementation": ("build", "validation"),
        "validation": ("prove", "done"),
    },
    "pilot-product-slice": {
        "ideation": ("shape", "implementation"),
        "implementation": ("build", "validation"),
        "validation": ("verify-deliver", "done"),
    },
    "production": {
        "ideation": ("shape", "implementation"),
        "implementation": ("build", "validation"),
        "validation": ("verify", "release"),
        "release": ("release", "done"),
    },
}


class ContractError(RuntimeError):
    """A selected route cannot be loaded safely."""


def _one_field(text: str, pattern: str, label: str) -> str:
    matches = re.findall(pattern, text, flags=re.MULTILINE)
    if len(matches) != 1:
        raise ContractError(f"work item must contain exactly one {label}")
    return matches[0].strip().strip("\"'")


def resolve_work_item(path: Path) -> dict[str, str]:
    path = path.expanduser().resolve()
    try:
        raw = path.read_bytes()
        text = raw.decode("utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise ContractError(f"cannot read work item {path}: {exc}") from exc

    if not text.startswith("---\n"):
        raise ContractError("work item is missing leading frontmatter")
    frontmatter_end = text.find("\n---\n", 4)
    if frontmatter_end < 0:
        raise ContractError("work item frontmatter is unterminated")
    frontmatter = text[4:frontmatter_end]
    workflow_stage = _one_field(
        frontmatter, r"^status:\s*([^\n#]+?)\s*$", "frontmatter status"
    )

    headings = list(re.finditer(r"^## Work profile receipt\s*$", text, re.MULTILINE))
    if len(headings) != 1:
        raise ContractError("work item must contain exactly one Work profile receipt")
    start = headings[0].end()
    next_heading = re.search(r"^##\s+", text[start:], re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(text)
    section = text[start:end]
    blocks = [
        block
        for block in re.findall(r"```(?:yaml|yml)\s*\n(.*?)```", section, re.DOTALL)
        if re.search(r"^work_profile:\s*$", block, re.MULTILINE)
    ]
    if len(blocks) != 1:
        raise ContractError("Work profile receipt must contain one YAML work_profile")
    block = blocks[0]
    schema = _one_field(block, r"^  schema:\s*([^\n#]+?)\s*$", "profile schema")
    if schema != "kc-dev-flow-work-profile/v2":
        raise ContractError(f"unsupported work profile schema: {schema}")
    profile = _one_field(block, r"^  selected:\s*([^\n#]+?)\s*$", "selected profile")
    if profile not in ROUTES:
        raise ContractError(f"unsupported profile: {profile}")

    route_text = _one_field(block, r"^  route:\s*([^\n#]+?)\s*$", "profile route")
    if not (route_text.startswith("[") and route_text.endswith("]")):
        raise ContractError("profile route must be an inline list")
    receipt_route = [
        stage.strip().strip("\"'")
        for stage in route_text[1:-1].split(",")
        if stage.strip()
    ]
    expected_route = [logical for logical, _next in ROUTES[profile].values()]
    if receipt_route != expected_route:
        raise ContractError(
            f"stale route for {profile}: expected {expected_route}, got {receipt_route}"
        )

    return {
        "path": path.as_posix(),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "schema": schema,
        "profile": profile,
        "workflow_stage": workflow_stage,
    }


CONDITIONAL_SCHEMA = "kc-dev-flow-conditional-references/v1"


def check_conditional_references(contract_path: Path, text: str) -> None:
    """Refuse a stage contract that names a reference the adopter has not vendored.

    The reference itself stays unread until its trigger fires; only its presence
    is checked, so an incomplete vendor fails at load instead of silently
    dropping the capability the stage declares.
    """
    for block in re.findall(r"```json\s*\n(.*?)```", text, re.DOTALL):
        try:
            declared = json.loads(block)
        except json.JSONDecodeError as exc:
            raise ContractError(
                f"{contract_path.name} has an unparseable JSON block: {exc}"
            ) from exc
        if declared.get("schema") != CONDITIONAL_SCHEMA:
            continue
        for entry in declared.get("references", []):
            target = (contract_path.parent / entry["path"]).resolve()
            if not target.is_file():
                raise ContractError(
                    f"{contract_path.name} declares conditional reference "
                    f"{entry['path']!r}, which is not vendored at {target}"
                )


def load_contracts(root: Path, work_item: Path) -> dict[str, object]:
    root = root.expanduser().resolve()
    receipt = resolve_work_item(work_item)
    profile = receipt["profile"]
    workflow_stage = receipt["workflow_stage"]
    route = ROUTES[profile]
    if workflow_stage not in route:
        allowed = ", ".join(route)
        raise ContractError(
            f"workflow stage {workflow_stage!r} is outside {profile}; expected: {allowed}"
        )

    logical_stage, next_stage = route[workflow_stage]
    paths = [
        root / "kernel.md",
        root / "profiles" / profile / "base.md",
        root / "profiles" / profile / f"{logical_stage}.md",
    ]
    loaded: list[dict[str, object]] = []
    for path in paths:
        try:
            relative = path.relative_to(root)
            raw = path.read_bytes()
            text = raw.decode("utf-8")
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            raise ContractError(f"cannot load selected contract {path}: {exc}") from exc
        check_conditional_references(path, text)
        loaded.append(
            {
                "path": relative.as_posix(),
                "sha256": hashlib.sha256(raw).hexdigest(),
                "bytes": len(raw),
                "content": text,
            }
        )

    return {
        "schema": "kc-dev-flow-profile-contract/v2",
        "work_item": receipt["path"],
        "work_item_sha256": receipt["sha256"],
        "receipt_schema": receipt["schema"],
        "profile": profile,
        "workflow_stage": workflow_stage,
        "logical_stage": logical_stage,
        "next_workflow_stage": next_stage,
        "loaded": loaded,
    }


def render_text(contract: dict[str, object]) -> str:
    header = {
        key: contract[key]
        for key in (
            "schema",
            "work_item",
            "work_item_sha256",
            "receipt_schema",
            "profile",
            "workflow_stage",
            "logical_stage",
            "next_workflow_stage",
        )
    }
    chunks = [json.dumps(header, sort_keys=True)]
    for item in contract["loaded"]:
        chunks.append(
            f"\n<contract path={json.dumps(item['path'])} "
            f"sha256={json.dumps(item['sha256'])}>\n"
            f"{item['content']}"
            "</contract>"
        )
    return "\n".join(chunks) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contracts-root", type=Path, required=True)
    parser.add_argument("--work-item", type=Path, required=True)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        contract = load_contracts(args.contracts_root, args.work_item)
    except ContractError as exc:
        print(f"profile contract: {exc}", file=sys.stderr)
        return 2
    if args.format == "json":
        json.dump(contract, sys.stdout, sort_keys=True)
        sys.stdout.write("\n")
    else:
        sys.stdout.write(render_text(contract))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
