#!/usr/bin/env python3
"""Validate and delegate the declared KC Dev Flow POC close path."""

from __future__ import annotations

import argparse
import importlib.util
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
LOADER_PATH = HERE / "profile-contract-loader.py"


class CloseError(RuntimeError):
    pass


def load_profile_loader():
    spec = importlib.util.spec_from_file_location("profile_contract_loader", LOADER_PATH)
    if spec is None or spec.loader is None:
        raise CloseError(f"cannot import profile loader at {LOADER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


LOADER = load_profile_loader()


def read_work_item(path: Path) -> tuple[str, str]:
    path = path.expanduser().resolve()
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise CloseError(f"cannot read work item {path}: {exc}") from exc
    try:
        receipt = LOADER.resolve_work_item(path)
    except LOADER.ContractError as exc:
        raise CloseError(str(exc)) from exc
    if receipt["schema"] != LOADER.PROFILE_SCHEMA_V3:
        raise CloseError("POC close path requires kc-dev-flow-work-profile/v3")
    if receipt["profile"] != "poc-exploration":
        raise CloseError("POC close path requires selected profile poc-exploration")
    if receipt["workflow_stage"] != "validation":
        raise CloseError("POC close path requires work item status validation")

    frontmatter_end = text.find("\n---\n", 4)
    if not text.startswith("---\n") or frontmatter_end < 0:
        raise CloseError("work item frontmatter is invalid")
    try:
        item_id = LOADER._one_field(
            text[4:frontmatter_end],
            r"^id:\s*([^\n#]+?)\s*$",
            "frontmatter id",
        )
    except LOADER.ContractError as exc:
        raise CloseError(str(exc)) from exc
    return text, item_id


def one_yaml_section(text: str, heading: str, root_key: str) -> str:
    headings = list(re.finditer(rf"^## {re.escape(heading)}\s*$", text, re.MULTILINE))
    if len(headings) != 1:
        raise CloseError(f"work item must contain exactly one {heading}")
    start = headings[0].end()
    next_heading = re.search(r"^##\s+", text[start:], re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(text)
    section = text[start:end]
    blocks = [
        block
        for block in re.findall(r"\x60\x60\x60(?:yaml|yml)\s*\n(.*?)\x60\x60\x60", section, re.DOTALL)
        if re.search(rf"^{re.escape(root_key)}:\s*$", block, re.MULTILINE)
    ]
    if len(blocks) != 1:
        raise CloseError(f"{heading} must contain one YAML {root_key}")
    return blocks[0]


def one_field(block: str, field: str, *, concrete: bool = True) -> str:
    matches = re.findall(
        rf"^  {re.escape(field)}:[ \t]*([^\n#]*?)[ \t]*$",
        block,
        flags=re.MULTILINE,
    )
    if len(matches) != 1:
        raise CloseError(f"work item must contain exactly one {field}")
    value = matches[0].strip().strip("\"'").strip()
    if concrete and LOADER.is_placeholder_scalar(value):
        raise CloseError(f"{field} must be a concrete scalar")
    return value


def parse_outcome(text: str) -> str:
    block = one_yaml_section(text, "POC outcome", "poc_outcome")
    direction = one_field(block, "direction")
    if direction not in {"proceed", "stop", "change"}:
        raise CloseError("direction must be proceed, stop, or change")
    for field in ("evidence", "strongest_limit", "reversal_fact", "cleanup"):
        one_field(block, field)
    return direction


def validate(path: Path, phase: str) -> tuple[str, str]:
    if phase not in {"prepare", "consume"}:
        raise CloseError(f"unsupported close phase: {phase}")
    text, item_id = read_work_item(path)
    direction = parse_outcome(text)
    return item_id, direction


def invoke_spacedock(
    spacedock: Path,
    arguments: list[str],
    *,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [str(spacedock), *arguments],
        input=input_text,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        sys.stdout.write(result.stdout)
        sys.stderr.write(result.stderr)
        raise SystemExit(result.returncode)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    configured = os.environ.get("SPACEDOCK_BIN") or shutil.which("spacedock")
    parser.add_argument("--spacedock-bin", type=Path, default=configured)
    parser.add_argument("--workflow-dir", type=Path, required=True)
    parser.add_argument("--work-item", type=Path, required=True)
    commands = parser.add_subparsers(dest="command", required=True)

    prepare = commands.add_parser("prepare")
    prepare.add_argument("--question", required=True)
    prepare.add_argument("--artifact", required=True)
    prepare.add_argument("--summary", required=True)
    commands.add_parser("consume")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.spacedock_bin is None:
        raise CloseError("spacedock executable is required")
    spacedock = args.spacedock_bin.expanduser().resolve()
    if not spacedock.is_file() or not os.access(spacedock, os.X_OK):
        raise CloseError(f"spacedock executable is not runnable: {spacedock}")
    workflow_dir = args.workflow_dir.expanduser().resolve()

    if args.command == "prepare":
        item_id, _outcome = validate(args.work_item, "prepare")
        command = [
            "gate",
            "prepare",
            item_id,
            "--workflow-dir",
            str(workflow_dir),
            "--question",
            args.question,
            "--artifact",
            args.artifact,
            "--summary",
            args.summary,
        ]
        result = invoke_spacedock(spacedock, command)
        sys.stdout.write(result.stdout)
        sys.stderr.write(result.stderr)
        return 0

    item_id, _outcome = validate(args.work_item, "consume")
    result = invoke_spacedock(
        spacedock,
        [
            "gate",
            "consume",
            item_id,
            "--workflow-dir",
            str(workflow_dir),
        ],
    )
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CloseError as exc:
        print(f"POC close guard: {exc}", file=sys.stderr)
        raise SystemExit(2)
