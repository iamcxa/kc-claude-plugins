#!/usr/bin/env python3
"""Validate and delegate the declared KC Dev Flow POC close path."""

from __future__ import annotations

import argparse
import importlib.util
import json
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


def parse_handoff(text: str, direction: str) -> tuple[str, str, str]:
    block = one_yaml_section(text, "POC handoff", "poc_handoff")
    disposition = one_field(block, "disposition")
    to = one_field(block, "to", concrete=False)
    reason = one_field(block, "reason", concrete=False)
    if direction in {"stop", "change"}:
        if disposition != "not_applicable":
            raise CloseError(f"{direction} requires not_applicable")
        if to or reason:
            raise CloseError("not_applicable requires empty to and reason")
    elif disposition not in {"created", "deferred", "declined"}:
        raise CloseError("proceed requires created, deferred, or declined")
    elif disposition == "created":
        if LOADER.is_placeholder_scalar(to):
            raise CloseError("created requires a concrete to")
        if reason:
            raise CloseError("created requires an empty reason")
    else:
        if to:
            raise CloseError(f"{disposition} requires an empty to")
        if LOADER.is_placeholder_scalar(reason):
            raise CloseError(f"{disposition} requires a concrete reason")
    return disposition, to, reason


def validate(path: Path, phase: str) -> tuple[str, str, tuple[str, str, str] | None]:
    if phase not in {"prepare", "consume"}:
        raise CloseError(f"unsupported close phase: {phase}")
    text, item_id = read_work_item(path)
    direction = parse_outcome(text)
    handoff = parse_handoff(text, direction) if phase == "consume" else None
    return item_id, direction, handoff


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


def find_downstream(
    spacedock: Path, workflow_dir: Path, source_id: str
) -> dict[str, object] | None:
    result = invoke_spacedock(
        spacedock,
        [
            "status",
            "--workflow-dir",
            str(workflow_dir),
            "--where",
            f"source=poc:{source_id}",
            "--archived",
            "--all-fields",
            "--json",
        ],
    )
    try:
        document = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise CloseError(f"Spacedock status returned invalid JSON: {exc}") from exc
    entities = document.get("entities")
    if not isinstance(entities, list) or not all(
        isinstance(entity, dict) for entity in entities
    ):
        raise CloseError("Spacedock status returned no entity list")
    if len(entities) > 1:
        raise CloseError(
            f"source poc:{source_id} resolves to multiple downstream items"
        )
    return entities[0] if entities else None


def validate_delivery_body(path: Path, source_id: str) -> str:
    try:
        text = path.expanduser().resolve().read_text(encoding="utf-8")
    except OSError as exc:
        raise CloseError(f"cannot read downstream body {path}: {exc}") from exc
    if "## Work profile receipt" in text:
        raise CloseError("downstream body must not preselect a work profile")
    if not text.startswith("---\n"):
        raise CloseError("downstream body is missing leading frontmatter")
    frontmatter_end = text.find("\n---\n", 4)
    if frontmatter_end < 0:
        raise CloseError("downstream body frontmatter is unterminated")
    frontmatter = text[4:frontmatter_end]
    try:
        fields = {
            name: LOADER._one_field(
                frontmatter, rf"^{name}:[ \t]*([^\n#]+?)[ \t]*$", f"downstream {name}"
            )
            for name in ("source", "status")
        }
    except LOADER.ContractError as exc:
        raise CloseError(str(exc)) from exc
    expected = f"poc:{source_id}"
    if fields["source"] != expected:
        raise CloseError(f"downstream source must be {expected}")
    if fields["status"] != "backlog":
        raise CloseError("downstream status must be backlog")
    if re.search(
        r"^(?:sprint:[ \t]*[^ \t#\n]|sprint-readiness:[ \t]*ready[ \t]*$)",
        frontmatter, re.MULTILINE,
    ):
        raise CloseError("downstream body must stay deferred")
    return text


def emit_result(disposition: str, entity: dict[str, object]) -> None:
    item_id = entity.get("id")
    slug = entity.get("slug")
    if not isinstance(item_id, str) or not isinstance(slug, str):
        raise CloseError(f"downstream identity is incomplete: {entity!r}")
    print(
        json.dumps(
            {"disposition": disposition, "id": item_id, "slug": slug},
            sort_keys=True,
        )
    )


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
    create = commands.add_parser("create")
    create.add_argument("--slug", required=True)
    create.add_argument("--body", type=Path, required=True)

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
        item_id, _outcome, _handoff = validate(args.work_item, "prepare")
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

    text, source_id = read_work_item(args.work_item)
    direction = parse_outcome(text)
    if args.command == "create":
        if direction != "proceed":
            raise CloseError("downstream creation requires direction proceed")
        existing = find_downstream(spacedock, workflow_dir, source_id)
        if existing is not None:
            emit_result("reused", existing)
            return 0
        body = validate_delivery_body(args.body, source_id)
        result = invoke_spacedock(
            spacedock,
            [
                "new",
                args.slug,
                "--workflow-dir",
                str(workflow_dir),
            ],
            input_text=body,
        )
        sys.stdout.write(result.stdout)
        created = find_downstream(spacedock, workflow_dir, source_id)
        if created is None:
            raise CloseError(
                "Spacedock new succeeded but the canonical source did not resolve"
            )
        emit_result("created", created)
        return 0

    item_id, _outcome, handoff = validate(args.work_item, "consume")
    disposition, to, _reason = handoff
    if disposition == "created":
        downstream = find_downstream(spacedock, workflow_dir, item_id)
        if downstream is None or downstream.get("id") != to:
            raise CloseError(
                "created handoff.to must resolve to the sole canonical downstream item"
            )
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
