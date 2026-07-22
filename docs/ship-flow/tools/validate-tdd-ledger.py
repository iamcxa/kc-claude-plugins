#!/usr/bin/env python3
"""Validate ship-flow plan TDD contracts and emit a layer-indexed ledger.

This intentionally uses only Python 3.8+ stdlib so adopter repos can run it
without installing ship-flow runtime dependencies.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


VALID_LAYERS = {"L1", "L2", "L3", "L4", "L5", "L6", "L7"}
LOW_CONFIDENCE_COMMANDS = {"true", "false", ":", "echo ok", "echo pass"}
COMMAND_STARTERS = {
    "bash",
    "bun",
    "cargo",
    "cd",
    "deno",
    "go",
    "grep",
    "ls",
    "make",
    "node",
    "npm",
    "npx",
    "pnpm",
    "python",
    "python3",
    "ruby",
    "sh",
    "test",
    "tsx",
    "uv",
    "yarn",
}


@dataclass
class Finding:
    task_id: str
    severity: str
    message: str


def compact(text: str) -> str:
    return re.sub(r"[ \t]+", " ", text.strip())


def split_sections(markdown: str) -> list[tuple[str, str]]:
    sections: list[tuple[str, list[str]]] = [("document", [])]
    for line in markdown.splitlines():
        if re.match(r"^#{1,6}\s+", line):
            header = re.sub(r"^#{1,6}\s+", "", line).strip()
            sections.append((header, [line]))
        else:
            sections[-1][1].append(line)
    return [(header, "\n".join(lines)) for header, lines in sections if "\n".join(lines).strip()]


def task_id_for(header: str, text: str) -> str:
    explicit_match = re.search(r"(?im)^\s*(?:task_id|id):\s*(T\d+(?:\.\d+)?)\b", text)
    if explicit_match:
        return explicit_match.group(1)
    header_match = re.match(r"^T\d+(?:\.\d+)?\b", header.strip())
    if header_match:
        return header_match.group(0)
    return ""


def is_task_section(header: str, text: str) -> bool:
    if re.search(r"(?im)^\s*(?:task_id|id):\s*T\d+(?:\.\d+)?\b", text):
        return True
    if re.search(r"(?im)^\s*tdd_contract:\s*$", text):
        return True
    if skip_rationale(text):
        return True
    if re.match(r"^T\d+(?:\.\d+)?\b", header.strip()):
        return bool(
            declared_layer_for(text)
            or extract_field(text, "red_command")
            or extract_field(text, "green_command")
            or extract_field(text, "expected_red_failure")
            or extract_field(text, "refactor_check")
        )
    return False


def declared_layer_for(text: str) -> str:
    match = re.search(r"(?im)^\s*(?:\*\*)?layer(?:\*\*)?:\s*([^\n#]+)", text)
    if not match:
        return ""
    value = match.group(1).strip().strip("`").lower()
    if "meta" in value:
        return "meta"
    layer_match = re.search(r"\bL([1-7])\b", value, re.IGNORECASE)
    if layer_match:
        return f"L{layer_match.group(1)}"
    numeric_match = re.search(r"\b([1-7])\b", value)
    if numeric_match:
        return f"L{numeric_match.group(1)}"
    return compact(match.group(1))


def field_name_for(line: str) -> str:
    normalized = line.strip().replace("**", "")
    match = re.match(r"^([A-Za-z_][A-Za-z0-9_ -]*):\s*(?:\|)?\s*$", normalized)
    if not match:
        return ""
    return re.sub(r"[\s-]+", "_", match.group(1).strip().lower())


def path_like_line(line: str) -> str:
    return line.strip().lstrip("- ").strip("`")


def scoped_path_lines(text: str) -> str:
    mutation_scopes = {"owned_paths", "owned_path", "writes", "write", "files", "file", "paths", "path"}
    collected: list[str] = []
    capture = False
    for line in text.splitlines():
        field_name = field_name_for(line)
        if field_name:
            capture = field_name in mutation_scopes
            continue
        if not capture:
            continue
        candidate = path_like_line(line)
        if "/" in candidate or re.search(r"\.(ts|tsx|js|jsx|sql|yaml|yml|sh|py|md)\b", candidate):
            collected.append(candidate)
    if collected:
        return "\n".join(collected)
    return "\n".join(
        path_like_line(line)
        for line in text.splitlines()
        if "/" in line or re.search(r"\.(ts|tsx|js|jsx|sql|yaml|yml|sh|py|md)\b", line)
    )


def infer_layer(text: str) -> str:
    lowered = text.lower()
    path_lines = scoped_path_lines(text).lower()
    hints = [
        ("L7", [r"(^|/)(e2e|uat|browser|smoke)(/|$)", r"\.claude/e2e"]),
        ("L6", [r"\.(tsx|jsx)\b", r"(^|/)(components?|frontend|ui)(/|$)"]),
        ("L5", [r"(^|/)(routers?|routes?|controllers?|endpoints?|api)(/|$)", r"router\.(ts|js)", r"router\.spec"]),
        ("L4", [r"(^|/)(api-contract|contract)(/|$)", r"\.schemas\.ts\b", r"round-trip"]),
        ("L3", [r"(^|/)(infrastructure|adapter|repository|fstore)(/|$)", r"(adapter|repository|action-publisher)\.(ts|js)"]),
        ("L2", [r"(^|/)domain(/|$)", r"(decider|evolve|saga|aggregate)\.(ts|js)"]),
        ("L1", [r"(^|/)(migrations?|schema)(/|$)", r"\.table\.ts\b", r"schema parity", r"rls"]),
    ]
    for layer, patterns in hints:
        if any(re.search(pattern, path_lines) for pattern in patterns):
            return layer
    fallback_hints = [
        ("L4", ["strict().parse", "strict-parse", "zod"]),
        ("L7", ["runtime flow"]),
    ]
    for layer, needles in fallback_hints:
        if any(needle in lowered for needle in needles):
            return layer
    return ""


def extract_field(text: str, field: str) -> str:
    lines = text.splitlines()
    field_re = re.compile(rf"^\s*{re.escape(field)}:\s*(.*)$")
    prose_re = re.compile(rf"^\s*(?:\*\*)?{field.replace('_', ' ').title()}(?:\*\*)?:\s*(.*)$", re.IGNORECASE)
    next_field_re = re.compile(r"^\s{0,8}[A-Za-z_][A-Za-z0-9_]*:\s*")
    for idx, line in enumerate(lines):
        match = field_re.match(line) or prose_re.match(line)
        if not match:
            continue
        tail = match.group(1).strip()
        if tail and tail != "|":
            return tail.strip('"').strip("'")
        collected: list[str] = []
        for next_line in lines[idx + 1 :]:
            if next_line.strip().startswith("```"):
                break
            if next_field_re.match(next_line) and collected:
                break
            collected.append(next_line.strip())
        return "\n".join(line for line in collected if line).strip()
    return ""


def skip_rationale(text: str) -> str:
    match = re.search(r"TDD:\s*skip\s*--\s*([^\n`]+)", text, re.IGNORECASE)
    return compact(match.group(1)) if match else ""


def command_quality(command: str) -> str:
    normalized = compact(command)
    if not normalized:
        return "missing"
    if normalized.lower() in LOW_CONFIDENCE_COMMANDS:
        return "low_confidence"
    if len(normalized) < 8:
        return "low_confidence"
    lines = [line.strip() for line in normalized.splitlines() if line.strip() and not line.strip().startswith("#")]
    if not lines:
        return "low_confidence"
    for line in lines:
        first = re.split(r"\s+", line, maxsplit=1)[0]
        if first.startswith("./"):
            first = first[2:]
        if first in COMMAND_STARTERS or "&&" in line or "|" in line or line.startswith("! "):
            return "executable"
    return "prose_like"


def is_docs_only(text: str) -> bool:
    lowered = text.lower()
    if "docs-only" in lowered or "stage-artifact" in lowered or "pre-flight" in lowered:
        return True
    if re.search(r"(?m)^\s*-\s+docs/", text) and not re.search(r"(?m)^\s*-\s+(apps|packages|domains|src|lib)/", text):
        return True
    return False


def extract_records(plan_path: Path) -> list[dict]:
    markdown = plan_path.read_text(encoding="utf-8", errors="replace")
    records: list[dict] = []
    for header, text in split_sections(markdown):
        if not is_task_section(header, text):
            continue
        task_id = task_id_for(header, text)
        if not task_id:
            continue
        declared_layer = declared_layer_for(text)
        inferred_layer = infer_layer(text)
        layer = inferred_layer or (declared_layer if declared_layer in VALID_LAYERS else "")
        rationale = skip_rationale(text)
        applicable = not bool(rationale)
        record = {
            "task_id": task_id,
            "surface": compact(header),
            "path": str(plan_path),
            "declared_layer": declared_layer,
            "inferred_layer": inferred_layer,
            "layer": layer,
            "layer_drift": bool(declared_layer and inferred_layer and declared_layer != inferred_layer),
            "applicable": applicable,
            "skip_rationale": rationale,
            "red_command": extract_field(text, "red_command"),
            "expected_red_failure": extract_field(text, "expected_red_failure"),
            "green_command": extract_field(text, "green_command"),
            "refactor_check": extract_field(text, "refactor_check"),
            "command_quality": {},
            "docs_only": is_docs_only(text),
        }
        record["command_quality"] = {
            "red_command": command_quality(record["red_command"]),
            "green_command": command_quality(record["green_command"]),
            "refactor_check": command_quality(record["refactor_check"]) if record["refactor_check"] else "missing",
        }
        records.append(record)
    return records


def validate(records: list[dict]) -> list[Finding]:
    findings: list[Finding] = []
    for record in records:
        task_id = record["task_id"] or "<unknown>"
        layer = record["layer"]
        if record["applicable"]:
            if layer not in VALID_LAYERS:
                findings.append(Finding(task_id, "BLOCKING", f"applicable task has invalid layer `{layer or 'missing'}`"))
            if record["declared_layer"] == "meta" and record["inferred_layer"] in VALID_LAYERS and not record["docs_only"]:
                findings.append(
                    Finding(
                        task_id,
                        "BLOCKING",
                        f"code-bearing task declares meta but inferred {record['inferred_layer']}",
                    )
                )
            missing = [
                field
                for field in ["red_command", "expected_red_failure", "green_command", "refactor_check"]
                if not record[field]
            ]
            if missing:
                findings.append(Finding(task_id, "BLOCKING", f"missing tdd_contract fields: {', '.join(missing)}"))
            for field in ["red_command", "green_command"]:
                quality = record["command_quality"][field]
                if quality != "executable":
                    findings.append(Finding(task_id, "BLOCKING", f"{field} is {quality}, expected executable command"))
        else:
            if not record["skip_rationale"]:
                findings.append(Finding(task_id, "BLOCKING", "TDD skip missing rationale"))
            if record["declared_layer"] == "meta" and record["inferred_layer"] in VALID_LAYERS and not record["docs_only"]:
                findings.append(
                    Finding(
                        task_id,
                        "WARNING",
                        f"skipped task declares meta but inferred {record['inferred_layer']}; verify skip rationale",
                    )
                )
    if not records:
        findings.append(Finding("<plan>", "BLOCKING", "no task records found"))
    return findings


def comparable_record(record: dict) -> dict:
    comparable = dict(record)
    comparable["path"] = ""
    return comparable


def validate_persisted_ledger(records: list[dict], ledger_path: Path) -> list[Finding]:
    if not ledger_path.exists():
        return [Finding("<ledger>", "BLOCKING", f"tdd-ledger.jsonl missing: {ledger_path}")]

    persisted: list[dict] = []
    try:
        for line_no, line in enumerate(ledger_path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                return [
                    Finding(
                        "<ledger>",
                        "BLOCKING",
                        f"tdd-ledger.jsonl line {line_no} is not an object; regenerate tdd-ledger.jsonl",
                    )
                ]
            persisted.append(value)
    except json.JSONDecodeError as exc:
        return [
            Finding(
                "<ledger>",
                "BLOCKING",
                f"tdd-ledger.jsonl invalid JSON at line {exc.lineno}; regenerate tdd-ledger.jsonl",
            )
        ]

    expected = [comparable_record(record) for record in records]
    actual = [comparable_record(record) for record in persisted]
    if actual != expected:
        return [
            Finding(
                "<ledger>",
                "BLOCKING",
                "persisted tdd-ledger.jsonl does not match current plan; regenerate tdd-ledger.jsonl",
            )
        ]
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate ship-flow plan TDD contracts and layer ledger.")
    parser.add_argument("--plan", type=Path, required=True, help="Path to plan.md")
    parser.add_argument("--emit-jsonl", action="store_true", help="Emit normalized ledger records to stdout")
    parser.add_argument(
        "--require-ledger-jsonl",
        type=Path,
        help="Require an existing tdd-ledger.jsonl that exactly matches the current plan records",
    )
    args = parser.parse_args()

    records = extract_records(args.plan)
    findings = validate(records)
    if args.require_ledger_jsonl:
        findings.extend(validate_persisted_ledger(records, args.require_ledger_jsonl))

    if args.emit_jsonl:
        for record in records:
            print(json.dumps(record, ensure_ascii=False, sort_keys=True))
    else:
        if not findings:
            print(f"status=pass records={len(records)}")

    for finding in findings:
        print(f"{finding.severity}: {finding.task_id}: {finding.message}", file=sys.stderr)
    if findings:
        print(f"status=fail findings={len(findings)}", file=sys.stderr)

    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
