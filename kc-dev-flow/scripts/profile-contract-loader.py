#!/usr/bin/env python3
"""Load the shared core and one selected profile-stage contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
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
PACKAGE_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = PACKAGE_ROOT / "contract-manifest.json"
MANIFEST_SCHEMA = "kc-dev-flow-contract-manifest/v1"
STAGE_PIN_SCHEMA = "kc-dev-flow-stage-pin/v1"
LOCAL_PROFILE_START = "<!-- kc-dev-flow-static-local-profile:start -->"
LOCAL_PROFILE_END = "<!-- kc-dev-flow-static-local-profile:end -->"


class ContractError(RuntimeError):
    """A selected route cannot be loaded safely."""


def _json_object(raw: bytes, label: str) -> dict[str, object]:
    """Decode one JSON object while refusing duplicate keys."""

    def unique_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise ContractError(f"{label} contains duplicate key {key!r}")
            result[key] = value
        return result

    try:
        value = json.loads(raw, object_pairs_hook=unique_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot parse {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"{label} must be one JSON object")
    return value


def load_installed_package() -> dict[str, object]:
    """Validate the package beside this loader and bind its declared bytes."""
    try:
        manifest_raw = MANIFEST_PATH.read_bytes()
        package_raw = (PACKAGE_ROOT / "plugin.json").read_bytes()
    except OSError as exc:
        raise ContractError(f"installed package metadata unavailable: {exc}") from exc
    manifest = _json_object(manifest_raw, "installed contract manifest")
    package = _json_object(package_raw, "installed plugin metadata")
    if manifest.get("schema") != MANIFEST_SCHEMA:
        raise ContractError("installed contract manifest schema is unsupported")
    if package.get("name") != "kc-dev-flow":
        raise ContractError("installed plugin metadata does not name kc-dev-flow")
    version = package.get("version")
    if not isinstance(version, str) or not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version):
        raise ContractError("installed plugin version is invalid")
    contract_interface = manifest.get("contract_interface")
    local_interface = manifest.get("local_profile_interface")
    resources = manifest.get("resources")
    if contract_interface != "kc-dev-flow-profile-contract/v3":
        raise ContractError("installed contract interface is unsupported")
    if not isinstance(local_interface, dict) or not isinstance(
        local_interface.get("schema"), str
    ):
        raise ContractError("installed local-profile interface is invalid")
    required_bindings = local_interface.get("required_bindings")
    if (
        not isinstance(required_bindings, list)
        or not required_bindings
        or any(not isinstance(item, str) or not item for item in required_bindings)
        or len(required_bindings) != len(set(required_bindings))
    ):
        raise ContractError("installed local-profile bindings are invalid")
    if (
        not isinstance(resources, list)
        or not resources
        or any(not isinstance(item, str) or not item for item in resources)
        or len(resources) != len(set(resources))
    ):
        raise ContractError("installed resource inventory is invalid")

    digest = hashlib.sha256()
    digest.update(b"manifest\0")
    digest.update(manifest_raw)
    resource_hashes: list[dict[str, object]] = []
    for declared in resources:
        relative = Path(declared)
        if relative.is_absolute() or ".." in relative.parts:
            raise ContractError(f"installed resource path escapes package: {declared!r}")
        path = (PACKAGE_ROOT / relative).resolve()
        if not path.is_relative_to(PACKAGE_ROOT) or not path.is_file():
            raise ContractError(f"installed resource missing: {declared}")
        try:
            raw = path.read_bytes()
        except OSError as exc:
            raise ContractError(f"installed resource unreadable: {declared}: {exc}") from exc
        digest.update(b"resource\0")
        digest.update(declared.encode("utf-8"))
        digest.update(b"\0")
        digest.update(raw)
        resource_hashes.append(
            {
                "path": declared,
                "sha256": hashlib.sha256(raw).hexdigest(),
                "bytes": len(raw),
            }
        )
    return {
        "version": version,
        "contract_interface": contract_interface,
        "local_profile_interface": local_interface,
        "contract_digest": digest.hexdigest(),
        "resources": resource_hashes,
    }


def read_local_profile(
    path: Path, interface: dict[str, object]
) -> dict[str, object]:
    """Read only the marked Local Profile and validate its machine binding."""
    path = path.expanduser().resolve()
    try:
        raw = path.read_bytes()
        text = raw.decode("utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise ContractError(f"cannot read Local Profile {path}: {exc}") from exc
    if text.count(LOCAL_PROFILE_START) != 1 or text.count(LOCAL_PROFILE_END) != 1:
        raise ContractError("Local Profile must contain one ordered marker pair")
    start = text.index(LOCAL_PROFILE_START) + len(LOCAL_PROFILE_START)
    end = text.index(LOCAL_PROFILE_END)
    if start >= end:
        raise ContractError("Local Profile markers are out of order")
    block = text[start:end].lstrip("\n")
    if not block.startswith("## Local Profile\n"):
        raise ContractError("Local Profile heading must immediately follow its start marker")
    rows: dict[str, str] = {}
    for line in block.splitlines():
        match = re.fullmatch(r"\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|", line)
        if not match or match.group(1) in {"Role", "---"}:
            continue
        name, value = match.group(1).strip(), match.group(2).strip()
        if name in rows:
            raise ContractError(f"Local Profile duplicates binding {name!r}")
        rows[name] = value
    required = interface["required_bindings"]
    missing = [name for name in required if name not in rows]
    if missing:
        raise ContractError("Local Profile is missing bindings: " + ", ".join(missing))
    expected = str(interface["schema"])
    if rows["Installed contract interface"].strip("`") != expected:
        raise ContractError(
            f"LOCAL_PROFILE_REFIT_REQUIRED: {path} Installed contract interface "
            f"must be {expected}; review Local mods {rows.get('Local mods', 'none')}"
        )
    return {
        "path": path.as_posix(),
        "sha256": hashlib.sha256(block.encode("utf-8")).hexdigest(),
        "interface": expected,
        "local_mods": rows.get("Local mods", "none"),
    }


def read_stage_pin(path: Path) -> dict[str, object] | None:
    path = path.expanduser().resolve()
    if not path.exists():
        return None
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise ContractError(f"cannot read stage pin {path}: {exc}") from exc
    pin = _json_object(raw, "stage pin")
    if pin.get("schema") != STAGE_PIN_SCHEMA:
        raise ContractError("stage pin schema is unsupported")
    return pin


def bind_stage_pin(
    contract: dict[str, object],
    package: dict[str, object],
    local_profile: dict[str, object],
    attempt: str,
    previous: dict[str, object] | None,
    *,
    accept_local_profile_refit: bool = False,
) -> dict[str, object]:
    if not attempt or len(attempt.encode("utf-8")) > 160:
        raise ContractError("stage attempt must be a non-empty bounded identifier")
    current_stage = str(contract["workflow_stage"])
    interface = str(package["local_profile_interface"]["schema"])
    if previous is not None and previous.get("workflow_stage") == current_stage:
        exact = {
            "attempt": attempt,
            "plugin_version": package["version"],
            "contract_digest": package["contract_digest"],
            "work_item_sha256": contract["work_item_sha256"],
            "local_profile_interface": interface,
        }
        if any(previous.get(key) != value for key, value in exact.items()):
            raise ContractError(
                "ACTIVE_STAGE_PIN_MISMATCH: restore the pinned plugin version and bytes"
            )
        return previous
    if previous is not None:
        if previous.get("next_workflow_stage") != current_stage:
            raise ContractError(
                "STAGE_PIN_TRANSITION_MISMATCH: current stage is not the pinned next stage"
            )
        if previous.get("work_item") != contract["work_item"]:
            raise ContractError("STAGE_PIN_TRANSITION_MISMATCH: work item identity changed")
        if (
            previous.get("local_profile_interface") != interface
            and not accept_local_profile_refit
        ):
            raise ContractError(
                "LOCAL_PROFILE_REFIT_REQUIRED: "
                f"{local_profile['path']} Installed contract interface and declared "
                f"Local mods {local_profile['local_mods']} require review before dispatch"
            )
    return {
        "schema": STAGE_PIN_SCHEMA,
        "work_item": contract["work_item"],
        "work_item_sha256": contract["work_item_sha256"],
        "profile": contract["profile"],
        "workflow_stage": current_stage,
        "logical_stage": contract["logical_stage"],
        "next_workflow_stage": contract["next_workflow_stage"],
        "attempt": attempt,
        "plugin_version": package["version"],
        "contract_digest": package["contract_digest"],
        "local_profile_interface": interface,
        "local_profile_sha256": local_profile["sha256"],
    }


def write_stage_pin(path: Path, pin: dict[str, object]) -> None:
    path = path.expanduser().resolve()
    if not path.parent.is_dir():
        raise ContractError(f"stage pin parent does not exist: {path.parent}")
    raw = (json.dumps(pin, sort_keys=True, separators=(",", ":")) + "\n").encode(
        "utf-8"
    )
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=path.parent, prefix=f".{path.name}.", delete=False
        ) as temporary:
            temporary_name = temporary.name
            temporary.write(raw)
            temporary.flush()
            os.fsync(temporary.fileno())
        os.replace(temporary_name, path)
        if path.read_bytes() != raw:
            raise ContractError(f"stage pin readback failed: {path}")
    except OSError as exc:
        raise ContractError(f"cannot write stage pin {path}: {exc}") from exc
    finally:
        if temporary_name is not None:
            try:
                Path(temporary_name).unlink(missing_ok=True)
            except OSError:
                pass


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
    declared_receipt_fields: list[bool] = []
    for field in ("source", "planning-window", "planning-outcome"):
        matches = re.findall(
            rf"^{re.escape(field)}:[ \t]*([^\n#]*?)[ \t]*$",
            frontmatter,
            flags=re.MULTILINE,
        )
        if len(matches) > 1:
            raise ContractError(f"admission must not repeat {field}")
        declared_receipt_fields.append(bool(matches))
        receipt_values.append(
            matches[0].strip().strip("\"'").strip() if matches else ""
        )
    if any(declared_receipt_fields) and not all(declared_receipt_fields):
        raise ContractError("Planning Receipt must be complete or absent")
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
            "Acceptance criteria must use unique ascending concrete bullets "
            "formatted exactly as `- **AC-N** <text>`"
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
    """Refuse a stage contract that names a reference absent from the package,
    and return this contract's own declared non-null receipt names.

    The reference itself stays unread until its trigger fires; only its presence
    is checked, so an incomplete vendor fails at load instead of silently
    dropping the capability the stage declares. Presence alone is not enough:
    the resolved target must stay inside the contracts root, so an absolute
    path, a `..` escape, or a symlink out of the tree cannot satisfy the check
    with a file outside the selected installed package.

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
                    f"{declared_path!r}, which is not installed at {target}"
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


def load_installed_contracts(
    work_item: Path,
    *,
    validate_admission: bool = False,
    local_profile_path: Path | None = None,
    stage_pin_path: Path | None = None,
    stage_attempt: str | None = None,
    persist_stage_pin: bool = False,
    accept_local_profile_refit: bool = False,
) -> dict[str, object]:
    """Load contracts from this installed package and optionally bind a stage pin."""
    previous = read_stage_pin(stage_pin_path) if stage_pin_path is not None else None
    try:
        package = load_installed_package()
    except ContractError as exc:
        if previous is not None:
            try:
                receipt = resolve_work_item(work_item)
            except ContractError:
                raise exc
            if previous.get("workflow_stage") == receipt.get("workflow_stage"):
                raise ContractError(f"ACTIVE_STAGE_PIN_MISMATCH: {exc}") from exc
        raise
    contract = load_contracts(
        PACKAGE_ROOT / "references",
        work_item,
        validate_admission=validate_admission,
    )
    contract.update(
        {
            "schema": package["contract_interface"],
            "plugin_version": package["version"],
            "contract_digest": package["contract_digest"],
            "local_profile_interface": package["local_profile_interface"]["schema"],
        }
    )
    if local_profile_path is None:
        if stage_pin_path is not None or stage_attempt is not None or persist_stage_pin:
            raise ContractError("stage pinning requires --local-profile")
        return contract
    local_profile = read_local_profile(
        local_profile_path, package["local_profile_interface"]
    )
    contract["local_profile"] = local_profile
    if stage_pin_path is None and stage_attempt is None and not persist_stage_pin:
        return contract
    if stage_pin_path is None or stage_attempt is None:
        raise ContractError("stage pinning requires --stage-pin and --stage-attempt")
    pin = bind_stage_pin(
        contract,
        package,
        local_profile,
        stage_attempt,
        previous,
        accept_local_profile_refit=accept_local_profile_refit,
    )
    contract["stage_pin"] = pin
    if persist_stage_pin:
        write_stage_pin(stage_pin_path, pin)
        if read_stage_pin(stage_pin_path) != pin:
            raise ContractError(f"stage pin verification failed: {stage_pin_path}")
    return contract


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
        "plugin_version",
        "contract_digest",
        "local_profile_interface",
        "local_profile",
        "stage_pin",
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
    parser.add_argument("--work-item", type=Path, required=True)
    parser.add_argument("--local-profile", type=Path)
    parser.add_argument("--stage-pin", type=Path)
    parser.add_argument("--stage-attempt")
    parser.add_argument("--write-stage-pin", action="store_true")
    parser.add_argument("--accept-local-profile-refit", action="store_true")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--validate-admission", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        contract = load_installed_contracts(
            args.work_item,
            validate_admission=args.validate_admission,
            local_profile_path=args.local_profile,
            stage_pin_path=args.stage_pin,
            stage_attempt=args.stage_attempt,
            persist_stage_pin=args.write_stage_pin,
            accept_local_profile_refit=args.accept_local_profile_refit,
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
