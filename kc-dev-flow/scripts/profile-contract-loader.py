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

PROFILE_SCHEMA_V2 = "kc-dev-flow-work-profile/v2"
PROFILE_SCHEMA_V3 = "kc-dev-flow-work-profile/v3"
POC_FIELDS = ("poc_decision", "poc_falsifier", "poc_budget", "poc_stop_when")
POC_ARTIFACTS = {"no-code", "disposable", "retained"}
RECOVERY_FIELDS = (
    "recovery_failure",
    "recovery_falsifier",
    "recovery_rollback",
)
RECOVERY_RISKS = {
    "behavior",
    "contract-schema",
    "state-concurrency",
    "security-privacy",
    "runtime-platform",
    "delivery",
    "none",
}
NULL_LIKE = {"null", "~"}
PLACEHOLDER_WORDS = {"tbd", "todo"}
DEVELOPMENT_BRIEF_SECTIONS = (
    "The problem",
    "Accepted outcome",
    "Non-goals",
    "Acceptance criteria",
    "Route-back conditions",
)


class ContractError(RuntimeError):
    """A selected route cannot be loaded safely."""


def _one_field(text: str, pattern: str, label: str) -> str:
    matches = re.findall(pattern, text, flags=re.MULTILINE)
    if len(matches) != 1:
        raise ContractError(f"work item must contain exactly one {label}")
    return matches[0].strip().strip("\"'").strip()


def is_placeholder_scalar(value: str) -> bool:
    normalized = value.strip().strip("\"'").strip()
    folded = normalized.casefold()
    return (
        not normalized
        or normalized in {"[]", "{}", "|"}
        or folded in NULL_LIKE
        or folded in PLACEHOLDER_WORDS
        or re.fullmatch(r"<[^>\n]+>", normalized) is not None
    )


def _optional_field(block: str, field: str) -> str | None:
    matches = re.findall(rf"^  {re.escape(field)}:[ \t]*([^\n#]*?)[ \t]*$", block, re.MULTILINE)
    if len(matches) > 1:
        raise ContractError(f"work item must contain at most one {field}")
    if not matches:
        return None
    value = matches[0].strip().strip("\"'").strip()
    if is_placeholder_scalar(value):
        raise ContractError(f"{field} must be a concrete scalar")
    return value


def validate_admission_brief(path: Path, profile: str) -> str | None:
    """Validate a new Pilot or Production admission without changing its bytes."""
    if profile not in {"pilot-product-slice", "production"}:
        return None
    try:
        raw = path.read_bytes()
        text = raw.decode("utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise ContractError(f"cannot read admission brief {path}: {exc}") from exc

    frontmatter_end = text.find("\n---\n", 4)
    frontmatter = text[4:frontmatter_end]
    receipt_values: list[str] = []
    for field in ("source", "planning-window", "planning-outcome"):
        matches = re.findall(
            rf"^{re.escape(field)}:[ \t]*([^\n#]*?)[ \t]*$",
            frontmatter,
            flags=re.MULTILINE,
        )
        if len(matches) != 1:
            raise ContractError(f"admission must contain exactly one {field}")
        receipt_values.append(matches[0].strip().strip("\"'").strip())
    present = [not is_placeholder_scalar(value) for value in receipt_values]
    if any(present) and not all(present):
        raise ContractError("Planning Receipt must be complete or absent")

    if re.search(r"^## Acceptance evidence\s*$", text, re.MULTILINE):
        raise ContractError(
            "new admission cannot contain Acceptance evidence with canonical criteria"
        )
    sections: list[str] = []
    for heading in DEVELOPMENT_BRIEF_SECTIONS:
        matches = list(
            re.finditer(rf"^## {re.escape(heading)}\s*$", text, re.MULTILINE)
        )
        if len(matches) != 1:
            raise ContractError(f"Development Brief must contain exactly one {heading}")
        start = matches[0].end()
        next_heading = re.search(r"^##\s+", text[start:], re.MULTILINE)
        end = start + next_heading.start() if next_heading else len(text)
        section = text[start:end].strip()
        if is_placeholder_scalar(section):
            raise ContractError(f"Development Brief {heading} must be concrete")
        sections.append(f"## {heading}\n\n{section}")

    non_goals = [
        line[2:].strip()
        for line in sections[2].splitlines()
        if line.startswith("- ")
    ]
    if not non_goals or any(is_placeholder_scalar(item) for item in non_goals):
        raise ContractError("Development Brief Non-goals must be a concrete list")
    criteria_lines = [
        line for line in sections[3].splitlines() if line.startswith("- ")
    ]
    criteria = [
        re.fullmatch(r"- \*\*AC-(\d+)\*\*\s+(.+)", line) for line in criteria_lines
    ]
    if (
        not criteria
        or any(match is None for match in criteria)
        or [int(match.group(1)) for match in criteria if match] != list(
            range(1, len(criteria) + 1)
        )
        or any(is_placeholder_scalar(match.group(2)) for match in criteria if match)
    ):
        raise ContractError(
            "Acceptance criteria must use unique ascending concrete AC-N bullets"
        )
    return hashlib.sha256("\n\n".join(sections).encode("utf-8")).hexdigest()


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
        frontmatter, r"^status:[ \t]*([^\n#]+?)[ \t]*$", "frontmatter status"
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
    schema = _one_field(block, r"^  schema:[ \t]*([^\n#]+?)[ \t]*$", "profile schema")
    if schema not in {PROFILE_SCHEMA_V2, PROFILE_SCHEMA_V3}:
        raise ContractError(f"unsupported work profile schema: {schema}")
    profile = _one_field(block, r"^  selected:[ \t]*([^\n#]+?)[ \t]*$", "selected profile")
    if profile not in ROUTES:
        raise ContractError(f"unsupported profile: {profile}")
    if schema == PROFILE_SCHEMA_V2 and profile == "poc-exploration":
        raise ContractError(
            "active v2 POC must finish on v3.x or be Captain re-recorded as v3"
        )

    poc_values: dict[str, str] = {}
    if schema == PROFILE_SCHEMA_V3 and profile == "poc-exploration":
        for field in POC_FIELDS:
            value = _one_field(
                block,
                rf"^  {field}:[ \t]*([^\n#]*?)[ \t]*$",
                field,
            )
            if is_placeholder_scalar(value):
                raise ContractError(f"{field} must be a concrete scalar")
            poc_values[field] = value
        artifact, safety = (_optional_field(block, field) for field in ("poc_artifact", "poc_safety_boundary"))
        if (artifact is None) != (safety is None):
            raise ContractError("poc_artifact and poc_safety_boundary must appear together")
        if artifact is not None and artifact not in POC_ARTIFACTS:
            raise ContractError("poc_artifact must be no-code, disposable, or retained")
        minutes_text = _optional_field(block, "poc_decision_ready_minutes")
        minutes = 15 if minutes_text is None else int(minutes_text) if minutes_text.isdigit() else 0
        if minutes < 1:
            raise ContractError("poc_decision_ready_minutes must be a positive integer")
        reason = _optional_field(block, "poc_decision_ready_reason")
        if minutes != 15 and reason is None:
            raise ContractError("a non-15 poc_decision_ready_minutes requires a reason")
        poc_values["poc_decision_ready_minutes"] = minutes
        poc_values["poc_proof_path"] = "direct" if artifact in {"no-code", "disposable"} and safety == "none" else "fresh"
        for field, value in (("poc_artifact", artifact), ("poc_safety_boundary", safety), ("poc_decision_ready_reason", reason)):
            if value is not None:
                poc_values[field] = value

    route_text = _one_field(block, r"^  route:[ \t]*([^\n#]+?)[ \t]*$", "profile route")
    if not (route_text.startswith("[") and route_text.endswith("]")):
        raise ContractError("profile route must be an inline list")
    receipt_route = [
        stage.strip().strip("\"'")
        for stage in route_text[1:-1].split(",")
        if stage.strip()
    ]
    expected_route = [logical for logical, _next in ROUTES[profile].values()]
    recovery_route = ["build", "verify"]
    is_recovery = receipt_route == recovery_route
    recovery_values: dict[str, object] = {}
    if is_recovery:
        if schema != PROFILE_SCHEMA_V3 or profile != "production":
            raise ContractError("Production recovery requires a v3 production receipt")
        recovery_keys = set(
            re.findall(r"^  (recovery_[a-z0-9_]+|review_risks):", block, re.MULTILINE)
        )
        expected_recovery_keys = {*RECOVERY_FIELDS, "review_risks"}
        if recovery_keys != expected_recovery_keys:
            raise ContractError(
                "Production recovery permits only recovery_failure, "
                "recovery_falsifier, recovery_rollback, and review_risks"
            )
        for field in RECOVERY_FIELDS:
            value = _one_field(
                block,
                rf"^  {field}:[ \t]*([^\n#]*?)[ \t]*$",
                field,
            )
            if is_placeholder_scalar(value):
                raise ContractError(f"{field} must be a concrete scalar")
            recovery_values[field] = value
        risks_text = _one_field(
            block, r"^  review_risks:[ \t]*([^\n#]*?)[ \t]*$", "review_risks"
        )
        if not (risks_text.startswith("[") and risks_text.endswith("]")):
            raise ContractError("review_risks must be an inline list")
        review_risks = [
            risk.strip().strip("\"'")
            for risk in risks_text[1:-1].split(",")
            if risk.strip()
        ]
        if (
            not review_risks
            or len(review_risks) != len(set(review_risks))
            or any(risk not in RECOVERY_RISKS for risk in review_risks)
            or ("none" in review_risks and review_risks != ["none"])
        ):
            raise ContractError("review_risks must contain named risks or only none")
        recovery_values["review_risks"] = review_risks
    elif receipt_route != expected_route:
        raise ContractError(
            f"stale route for {profile}: expected {expected_route}, got {receipt_route}"
        )

    first_workflow_stage = next(iter(ROUTES[profile]))
    if workflow_stage == first_workflow_stage:
        sprint = _one_field(
            frontmatter, r"^sprint:[ \t]*([^\n#]+?)[ \t]*$", "frontmatter sprint"
        )
        if (
            not sprint
            or sprint.casefold() in {"null", "~", "true", "false"}
            or sprint[0] in "[{&*!|>"
        ):
            raise ContractError("frontmatter sprint must name an iteration")
        sprint_readiness = _one_field(
            frontmatter,
            r"^sprint-readiness:[ \t]*([^\n#]+?)[ \t]*$",
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
        **poc_values,
        **recovery_values,
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


def load_contracts(
    root: Path, work_item: Path, *, validate_admission: bool = False
) -> dict[str, object]:
    root = root.expanduser().resolve()
    receipt = resolve_work_item(work_item)
    development_brief_sha256 = (
        validate_admission_brief(work_item, receipt["profile"])
        if validate_admission
        else None
    )
    profile = receipt["profile"]
    workflow_stage = receipt["workflow_stage"]
    route = ROUTES[profile]
    if "recovery_failure" in receipt and workflow_stage == "ideation":
        return {
            "schema": "kc-dev-flow-profile-contract/v2",
            "work_item": receipt["path"],
            "work_item_sha256": receipt["sha256"],
            "receipt_schema": receipt["schema"],
            "profile": profile,
            "workflow_stage": workflow_stage,
            "logical_stage": None,
            "next_workflow_stage": "implementation",
            "skip_to_workflow_stage": "implementation",
            "review_risks": receipt["review_risks"],
            "declared_receipts": [],
            "loaded": [],
        }
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

    result = {
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
    if development_brief_sha256 is not None:
        result["development_brief_sha256"] = development_brief_sha256
    if "recovery_failure" in receipt:
        result["review_risks"] = receipt["review_risks"]
    if profile == "poc-exploration":
        for key in ("poc_artifact", "poc_safety_boundary", "poc_decision_ready_minutes", "poc_decision_ready_reason", "poc_proof_path"):
            if key in receipt:
                result[key] = receipt[key]
    if logical_stage == "build":
        result["implementation_exit_observation_declared"] = (
            receipt.get("poc_proof_path") != "direct"
            if profile == "poc-exploration"
            else receipt.get("review_risks") != ["none"]
        )
    return result


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
    for key in (
        "skip_to_workflow_stage",
        "review_risks",
        "implementation_exit_observation_declared",
        "poc_artifact", "poc_safety_boundary", "poc_decision_ready_minutes",
        "poc_decision_ready_reason", "poc_proof_path",
        "development_brief_sha256",
    ):
        if key in contract:
            header[key] = contract[key]
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
    parser.add_argument("--validate-admission", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        contract = load_contracts(
            args.contracts_root,
            args.work_item,
            validate_admission=args.validate_admission,
        )
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
