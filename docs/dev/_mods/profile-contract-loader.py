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
        "validation": ("verify", "done"),
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

    first_workflow_stage = next(iter(ROUTES[profile]))
    if workflow_stage == first_workflow_stage:
        sprint = _one_field(
            frontmatter, r"^sprint:\s*([^\n#]+?)\s*$", "frontmatter sprint"
        )
        if not sprint:
            raise ContractError("frontmatter sprint must name an iteration")
        sprint_readiness = _one_field(
            frontmatter,
            r"^sprint-readiness:\s*([^\n#]+?)\s*$",
            "frontmatter sprint-readiness",
        )
        if sprint_readiness != "ready":
            raise ContractError("frontmatter sprint-readiness must be 'ready'")

    return {
        "path": path.as_posix(),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "schema": schema,
        "profile": profile,
        "workflow_stage": workflow_stage,
    }


CONDITIONAL_SCHEMA = "kc-dev-flow-conditional-references/v1"


def check_conditional_references(
    root: Path, contract_path: Path, text: str
) -> list[str]:
    """Refuse a stage contract that names a reference the adopter has not vendored,
    and return this contract's own declared non-null receipt names.

    The reference itself stays unread until its trigger fires; only its presence
    is checked, so an incomplete vendor fails at load instead of silently
    dropping the capability the stage declares. Presence alone is not enough:
    the resolved target must stay inside the contracts root, so an absolute
    path, a `..` escape, or a symlink out of the tree cannot satisfy the check
    with a file the adopter never vendored.

    Bounded guarantee on the returned receipt names: this surfaces which
    receipt names this contract's own `kc-dev-flow-conditional-references/v1`
    block declares. It does not verify that a receipt was produced, does not
    evaluate `trigger`, and does not block a stage that completes without one.
    """
    declared_receipts: list[str] = []
    for block in re.findall(r"```json\s*\n(.*?)```", text, re.DOTALL):
        try:
            declared = json.loads(block)
        except json.JSONDecodeError as exc:
            raise ContractError(
                f"{contract_path.name} has an unparseable JSON block: {exc}"
            ) from exc
        if not isinstance(declared, dict):
            continue
        if declared.get("schema") != CONDITIONAL_SCHEMA:
            continue
        entries = declared.get("references")
        if not isinstance(entries, list):
            raise ContractError(
                f"{contract_path.name} declares conditional references that are "
                "not a list"
            )
        for entry in entries:
            if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
                raise ContractError(
                    f"{contract_path.name} has a conditional reference entry "
                    f"without a string path: {entry!r}"
                )
            declared_path = entry["path"]
            if Path(declared_path).is_absolute():
                raise ContractError(
                    f"{contract_path.name} declares absolute conditional "
                    f"reference {declared_path!r}"
                )
            target = (contract_path.parent / declared_path).resolve()
            if not target.is_relative_to(root):
                raise ContractError(
                    f"{contract_path.name} declares conditional reference "
                    f"{declared_path!r}, which resolves outside the contracts "
                    f"root at {target}"
                )
            if not target.is_file():
                raise ContractError(
                    f"{contract_path.name} declares conditional reference "
                    f"{declared_path!r}, which is not vendored at {target}"
                )
            receipt = entry.get("receipt")
            if isinstance(receipt, str):
                declared_receipts.append(receipt)
    return declared_receipts


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
    declared_receipts: list[str] = []
    stage_path = paths[-1]
    for path in paths:
        try:
            relative = path.relative_to(root)
            raw = path.read_bytes()
            text = raw.decode("utf-8")
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            raise ContractError(f"cannot load selected contract {path}: {exc}") from exc
        receipts = check_conditional_references(root, path, text)
        if path == stage_path:
            declared_receipts = receipts
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
        "declared_receipts": declared_receipts,
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
            "declared_receipts",
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
