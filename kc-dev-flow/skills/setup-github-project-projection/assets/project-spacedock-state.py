#!/usr/bin/env python3
"""Deterministic Spacedock projection planner.

The POC deliberately owns no network client. It converts pinned workflow/entity
bytes plus an observed target snapshot into a closed mutation plan. GitHub I/O is
an adapter boundary layered on this planner after credential and trigger proof.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import pathlib
import re
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from typing import Any


VERSION = "0.1.0"
RECEIPT_START = "<!-- spacedock-projection:v1"
RECEIPT_END = "-->"
SUMMARY_START = "<!-- spacedock-projection-summary:v1 -->"
SUMMARY_END = "<!-- /spacedock-projection-summary:v1 -->"
COMPARED_RECEIPT_KEYS = {
    "schema",
    "identity",
    "slug",
    "entity_id",
    "entity_digest",
    "projector_version",
    "projector_digest",
    "ownership",
    "archived",
}


class ProjectionError(ValueError):
    """Raised when source bytes cannot be projected safely."""


class GitHubRestClient:
    """Small REST 2026-03-10 transport with separate repository/project tokens."""

    def __init__(self, repository_token: str, project_token: str) -> None:
        if not repository_token or not project_token:
            raise ProjectionError("both repository and Project credentials are required")
        self._tokens = {"repository": repository_token, "project": project_token}

    def request(
        self,
        method: str,
        path: str,
        *,
        authority: str,
        body: dict[str, Any] | None = None,
    ) -> Any:
        payload, _headers = self._request(method, path, authority=authority, body=body)
        return payload

    def _request(
        self,
        method: str,
        path: str,
        *,
        authority: str,
        body: dict[str, Any] | None = None,
    ) -> tuple[Any, Any]:
        data = _canonical(body).encode() if body is not None else None
        url = path if path.startswith("https://api.github.com/") else f"https://api.github.com/{path.lstrip('/')}"
        request = urllib.request.Request(
            url,
            data=data,
            method=method,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self._tokens[authority]}",
                "X-GitHub-Api-Version": "2026-03-10",
                "User-Agent": "spacedock-projector/0.1",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = response.read()
                headers = response.headers
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:500]
            raise ProjectionError(
                f"GitHub {method} {path} failed with HTTP {exc.code}: {detail}"
            ) from exc
        return (json.loads(payload) if payload else None), headers

    def request_all(self, path: str, *, authority: str) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        next_path: str | None = path
        while next_path is not None:
            payload, headers = self._request("GET", next_path, authority=authority)
            page = _unwrap(payload)
            if not isinstance(page, list):
                raise ProjectionError(f"GitHub pagination endpoint {path!r} did not return a list")
            result.extend(page)
            link = headers.get("Link", "")
            match = re.search(r'<([^>]+)>; rel="next"', link)
            next_path = match.group(1) if match else None
        return result


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: bytes | str) -> str:
    if isinstance(value, str):
        value = value.encode("utf-8")
    return hashlib.sha256(value).hexdigest()


def _frontmatter_lines(text: str) -> list[str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ProjectionError("missing opening frontmatter delimiter")
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return lines[1:index]
    raise ProjectionError("missing closing frontmatter delimiter")


def _scalar(raw: str) -> Any:
    value = raw.strip()
    if not value or value in {"null", "~"}:
        return None
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    if re.fullmatch(r"-?[0-9]+", value):
        return int(value)
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def parse_workflow_text(text: str) -> dict[str, Any]:
    """Parse the commissioned workflow subset needed by the projector."""

    lines = _frontmatter_lines(text)
    top: dict[str, Any] = {}
    stages: list[dict[str, Any]] = []
    in_stages = False
    in_states = False
    current: dict[str, Any] | None = None

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        if indent == 0:
            in_stages = stripped == "stages:"
            in_states = False
            current = None
            if ":" in stripped and not in_stages:
                key, raw = stripped.split(":", 1)
                top[key] = _scalar(raw)
            continue
        if in_stages and indent == 2 and stripped == "states:":
            in_states = True
            continue
        if in_states and indent == 4 and stripped.startswith("- name:"):
            current = {"name": _scalar(stripped.split(":", 1)[1])}
            stages.append(current)
            continue
        if in_states and current is not None and indent >= 6 and ":" in stripped:
            key, raw = stripped.split(":", 1)
            current[key] = _scalar(raw)

    names = [stage.get("name") for stage in stages]
    if not names or any(not isinstance(name, str) or not name for name in names):
        raise ProjectionError("workflow declares no usable stages.states[]")
    if len(names) != len(set(names)):
        raise ProjectionError("workflow stage names must be unique")
    initial = [stage["name"] for stage in stages if stage.get("initial") is True]
    terminal = [stage["name"] for stage in stages if stage.get("terminal") is True]
    if len(initial) != 1 or len(terminal) != 1:
        raise ProjectionError("workflow must declare exactly one initial and terminal stage")

    return {
        "entity_type": top.get("entity-type"),
        "id_style": top.get("id-style"),
        "state": top.get("state"),
        "trunk": top.get("trunk"),
        "stages": names,
        "initial_stage": initial[0],
        "terminal_stage": terminal[0],
        "source_digest": _digest(text),
    }


def parse_entity_text(text: str, *, slug: str, archived: bool = False) -> dict[str, Any]:
    """Parse flat entity frontmatter while preserving unknown keys as data."""

    values: dict[str, Any] = {}
    for line in _frontmatter_lines(text):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith((" ", "\t")) or ":" not in line:
            raise ProjectionError(f"entity {slug!r} has unsupported nested frontmatter")
        key, raw = line.split(":", 1)
        if key in values:
            raise ProjectionError(f"entity {slug!r} repeats field {key!r}")
        values[key] = _scalar(raw)
    for required in ("title", "status", "source"):
        if not values.get(required):
            raise ProjectionError(f"entity {slug!r} is missing {required!r}")
    if isinstance(values.get("issue"), str) and values["issue"].isdigit():
        values["issue"] = int(values["issue"])
    values["_slug"] = slug
    values["_archived"] = archived
    values["_content_digest"] = _digest(text)
    return values


def _identity(repository: str, workflow_dir: str, slug: str) -> str:
    return f"{repository}:{workflow_dir}:{slug}"


def parse_receipt(body: str | None) -> dict[str, Any] | None:
    if not body:
        return None
    pattern = re.compile(
        re.escape(RECEIPT_START) + r"\n(?P<payload>\{.*?\})\n" + re.escape(RECEIPT_END),
        re.DOTALL,
    )
    match = pattern.search(body)
    if not match:
        return None
    try:
        value = json.loads(match.group("payload"))
    except json.JSONDecodeError as exc:
        raise ProjectionError("malformed projection receipt") from exc
    return value if isinstance(value, dict) else None


def _body_with_receipt(body: str | None, receipt: dict[str, Any]) -> str:
    marker = f"{RECEIPT_START}\n{_canonical(receipt)}\n{RECEIPT_END}"
    if not body:
        return marker
    pattern = re.compile(
        re.escape(RECEIPT_START) + r"\n\{.*?\}\n" + re.escape(RECEIPT_END),
        re.DOTALL,
    )
    if pattern.search(body):
        return pattern.sub(marker, body)
    return f"{body.rstrip()}\n\n{marker}"


def _inline(value: Any, *, limit: int = 300) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    return text[:limit]


def _projector_summary(
    entity: dict[str, Any], *, repository: str, workflow_dir: str, state_ref: str
) -> str:
    return "\n".join(
        (
            SUMMARY_START,
            "This Issue is a read-only projection from Spacedock.",
            "",
            f"- Entity: `{_inline(entity['_slug'])}`",
            f"- Stage: `{_inline(entity['status'])}`",
            f"- Workflow: `{_inline(repository)}:{_inline(workflow_dir)}`",
            f"- State ref: `{_inline(state_ref)}`",
            f"- Source: {_inline(entity['source'])}",
            SUMMARY_END,
        )
    )


def _receipt_core(receipt: dict[str, Any] | None) -> dict[str, Any] | None:
    if receipt is None:
        return None
    return {key: receipt.get(key) for key in sorted(COMPARED_RECEIPT_KEYS)}


def _generic_status(
    workflow: dict[str, Any], stage: str, status_options: list[str]
) -> str | None:
    if stage == workflow["initial_stage"]:
        candidates = ("Backlog", "Todo")
    elif stage == workflow["terminal_stage"]:
        candidates = ("Done",)
    else:
        candidates = ("In progress", "In Progress")
    return next((candidate for candidate in candidates if candidate in status_options), None)


def _target_by_identity(target_items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for item in target_items:
        receipt = parse_receipt(item.get("body"))
        if receipt and isinstance(receipt.get("identity"), str):
            if receipt["identity"] in result:
                raise ProjectionError(f"duplicate target identity {receipt['identity']!r}")
            result[receipt["identity"]] = item
    return result


def status_options_from_rest(fields: list[dict[str, Any]]) -> list[str]:
    for field in fields:
        if field.get("name") == "Status" and field.get("data_type") == "single_select":
            return [
                option["name"]["raw"]
                for option in field.get("options", [])
                if isinstance(option.get("name"), dict)
                and isinstance(option["name"].get("raw"), str)
            ]
    return []


def target_items_from_rest(
    fields: list[dict[str, Any]], items: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Normalize GitHub Projects REST 2026-03-10 observations."""

    field_names = {
        field["id"]: field["name"]
        for field in fields
        if isinstance(field.get("id"), int) and isinstance(field.get("name"), str)
    }
    result: list[dict[str, Any]] = []
    for item in items:
        content = item.get("content") or {}
        if content.get("number") is None:
            continue
        values: dict[str, Any] = {}
        for value in item.get("fields", []):
            field_name = field_names.get(value.get("id"), value.get("name"))
            raw_value = value.get("value")
            if isinstance(raw_value, dict) and isinstance(raw_value.get("name"), dict):
                raw_value = raw_value["name"].get("raw")
            elif isinstance(raw_value, dict) and "raw" in raw_value:
                raw_value = raw_value.get("raw")
            if isinstance(field_name, str):
                values[field_name] = raw_value
        result.append(
            {
                "item_id": item.get("id"),
                "item_node_id": item.get("node_id"),
                "issue_number": content.get("number"),
                "issue_id": content.get("id"),
                "title": content.get("title"),
                "issue_state": str(content.get("state", "open")).upper(),
                "body": content.get("body") or "",
                "fields": values,
            }
        )
    return result


def merge_repository_issues(
    target_items: list[dict[str, Any]],
    issues: list[dict[str, Any]],
    *,
    linked_issue_numbers: set[int] | None = None,
) -> list[dict[str, Any]]:
    """Include stranded managed Issues and explicitly linked human Issues."""

    result = copy.deepcopy(target_items)
    projected_numbers = {item.get("issue_number") for item in result}
    linked_issue_numbers = linked_issue_numbers or set()
    for issue in issues:
        if issue.get("pull_request") or issue.get("number") in projected_numbers:
            continue
        body = issue.get("body") or ""
        if parse_receipt(body) is None and issue.get("number") not in linked_issue_numbers:
            continue
        result.append(
            {
                "item_id": None,
                "item_node_id": None,
                "issue_number": issue.get("number"),
                "issue_id": issue.get("id"),
                "title": issue.get("title"),
                "issue_state": str(issue.get("state", "open")).upper(),
                "body": body,
                "fields": {},
            }
        )
    return result


def _project_base(config: dict[str, Any]) -> str:
    project = config["project"]
    prefix = "users" if project["owner_type"] == "user" else "orgs"
    return f"{prefix}/{project['owner']}/projectsV2/{project['number']}"


def validate_config(config: dict[str, Any]) -> None:
    if config.get("schema") != "spacedock-project-config/v1":
        raise ProjectionError("unsupported projection config schema")
    for name in ("repository", "trunk_ref", "state_ref", "workflow_dir", "profile"):
        if not isinstance(config.get(name), str) or not config[name]:
            raise ProjectionError(f"configuration requires non-empty {name!r}")
    if config["profile"] not in {"generic", "kc-dev-flow"}:
        raise ProjectionError("unsupported mapping profile")
    project = config.get("project")
    if not isinstance(project, dict) or project.get("owner_type") not in {"user", "organization"}:
        raise ProjectionError("configuration requires a user or organization Project")
    if not isinstance(project.get("owner"), str) or not isinstance(project.get("number"), int):
        raise ProjectionError("configuration requires Project owner and number")
    if not isinstance(project.get("node_id"), str) or not project["node_id"]:
        raise ProjectionError("configuration requires the pinned Project node ID")
    if config.get("external_apply_enabled"):
        credential = config.get("credential") or {}
        if any(
            not credential.get(name)
            for name in (
                "token_type",
                "permissions",
                "expiry",
                "rotation_owner",
                "fallback_blast_radius",
            )
        ) or credential.get("token_type") == "unresolved":
            raise ProjectionError("external apply requires a complete credential receipt")
        if project["owner_type"] == "user" and credential.get("token_type") != "classic-pat":
            raise ProjectionError("the REST adapter for a user-owned Project requires classic-pat")


def _unwrap(value: Any) -> Any:
    return value.get("value") if isinstance(value, dict) and "value" in value else value


def observe_github(
    client: Any,
    config: dict[str, Any],
    *,
    linked_issue_numbers: set[int] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Read all POC inputs before planning any write."""

    repository = config["repository"]
    project_base = _project_base(config)
    client.request("GET", f"repos/{repository}", authority="repository")
    project = client.request("GET", project_base, authority="project")
    if _unwrap(project).get("node_id") != config["project"]["node_id"]:
        raise ProjectionError("configured Project node ID does not match live Project")
    request_all = getattr(client, "request_all", None)
    fields = (
        request_all(f"{project_base}/fields", authority="project")
        if request_all
        else _unwrap(client.request("GET", f"{project_base}/fields", authority="project"))
    )
    field_ids = ",".join(str(field["id"]) for field in fields if isinstance(field.get("id"), int))
    suffix = f"?fields={urllib.parse.quote(field_ids)}" if field_ids else ""
    items_path = f"{project_base}/items{suffix}"
    issues_path = f"repos/{repository}/issues?state=all&per_page=100"
    items = (
        request_all(items_path, authority="project")
        if request_all
        else _unwrap(client.request("GET", items_path, authority="project"))
    )
    issues = (
        request_all(issues_path, authority="repository")
        if request_all
        else _unwrap(client.request("GET", issues_path, authority="repository"))
    )
    normalized = target_items_from_rest(fields, items)
    return fields, merge_repository_issues(
        normalized, issues, linked_issue_numbers=linked_issue_numbers
    )


def _single_select_options(field: dict[str, Any]) -> dict[str, str]:
    return {
        option["name"]["raw"]: option["id"]
        for option in field.get("options", [])
        if isinstance(option.get("id"), str)
        and isinstance(option.get("name"), dict)
        and isinstance(option["name"].get("raw"), str)
    }


def _field_by_name(fields: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        field["name"]: field
        for field in fields
        if isinstance(field.get("name"), str)
    }


def required_project_schema(plan: dict[str, Any]) -> dict[str, list[str]]:
    values: dict[str, set[str]] = {}
    for entity in plan["entities"]:
        desired = entity.get("desired")
        if not desired:
            continue
        for name, value in desired["fields"].items():
            if name == "Status":
                continue
            values.setdefault(name, set()).add(str(value))
    return {name: sorted(options) for name, options in sorted(values.items())}


def validate_project_schema(
    plan: dict[str, Any], fields: list[dict[str, Any]], *, allow_missing: bool
) -> None:
    by_name = _field_by_name(fields)
    for name, required_options in required_project_schema(plan).items():
        field = by_name.get(name)
        if field is None:
            if allow_missing:
                continue
            raise ProjectionError(f"required Project field {name!r} is missing")
        if field.get("data_type") != "single_select":
            raise ProjectionError(f"Project field {name!r} is not single_select")
        missing = sorted(set(required_options) - set(_single_select_options(field)))
        if missing:
            raise ProjectionError(f"Project field {name!r} lacks options {missing!r}")


def project_schema_plan(
    plan: dict[str, Any], fields: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    by_name = _field_by_name(fields)
    result: list[dict[str, Any]] = []
    for name, required_options in required_project_schema(plan).items():
        field = by_name.get(name)
        if field is None:
            result.append(
                {"action": "CREATE_FIELD", "field": name, "options": required_options}
            )
            continue
        existing = _single_select_options(field)
        missing = sorted(set(required_options) - set(existing))
        result.append(
            {
                "action": "UPDATE_FIELD_OPTIONS" if missing else "NO_CHANGE",
                "field": name,
                "missing_options": missing,
            }
        )
    return result


def apply_github_plan(
    client: Any,
    config: dict[str, Any],
    plan: dict[str, Any],
    fields: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Apply a conflict-free plan through resumable Issue then Project writes."""

    conflicts = [item for item in plan["entities"] if item["classification"] == "CONFLICT"]
    if conflicts or plan["orphans"]:
        raise ProjectionError("conflicts must be resolved before external apply")
    validate_project_schema(plan, fields, allow_missing=True)
    project_base = _project_base(config)
    operations: list[dict[str, Any]] = []
    by_name = _field_by_name(fields)
    for name, options in required_project_schema(plan).items():
        if name in by_name:
            continue
        response = client.request(
            "POST",
            f"{project_base}/fields",
            authority="project",
            body={
                "name": name,
                "data_type": "single_select",
                "single_select_options": [
                    {"name": option, "color": "GRAY", "description": "Spacedock derived value"}
                    for option in options
                ],
            },
        )
        field = _unwrap(response)
        fields.append(field)
        by_name[name] = field
        operations.append({"action": "CREATE_FIELD", "field": name})
    validate_project_schema(plan, fields, allow_missing=False)

    repository = config["repository"]
    for mutation in plan["mutations"]:
        desired = mutation["desired"]
        issue_number = mutation.get("current_issue_number") or desired.get("issue_number")
        issue_id: int | None = None
        issue_payload = {
            "title": desired["title"],
            "body": desired["body"],
            "state": desired["issue_state"].lower(),
        }
        if issue_number is None:
            issue = client.request(
                "POST",
                f"repos/{repository}/issues",
                authority="repository",
                body=issue_payload,
            )
            issue_number = issue["number"]
            issue_id = issue["id"]
            operations.append({"action": "CREATE_ISSUE", "issue_number": issue_number})
        else:
            issue = client.request(
                "PATCH",
                f"repos/{repository}/issues/{issue_number}",
                authority="repository",
                body=issue_payload,
            )
            issue_id = issue["id"]
            operations.append({"action": "UPDATE_ISSUE", "issue_number": issue_number})

        item_id = mutation.get("current_item_id")
        if item_id is None:
            item = client.request(
                "POST",
                f"{project_base}/items",
                authority="project",
                body={"type": "Issue", "id": issue_id},
            )
            item_id = _unwrap(item)["id"]
            operations.append({"action": "ADD_PROJECT_ITEM", "issue_number": issue_number})

        field_values: list[dict[str, Any]] = []
        for name, value in desired["fields"].items():
            field = by_name.get(name)
            if field is None:
                raise ProjectionError(f"Project field {name!r} is unavailable")
            option_id = _single_select_options(field).get(str(value))
            if option_id is None:
                raise ProjectionError(f"Project field {name!r} lacks value {value!r}")
            field_values.append({"id": field["id"], "value": option_id})
        client.request(
            "PATCH",
            f"{project_base}/items/{item_id}",
            authority="project",
            body={"fields": field_values},
        )
        operations.append({"action": "UPDATE_FIELDS", "issue_number": issue_number})
    return operations


def _same_managed_state(current: dict[str, Any], desired: dict[str, Any]) -> bool:
    return all(
        (
            current.get("title") == desired["title"],
            current.get("issue_state") == desired["issue_state"],
            all(
                current.get("fields", {}).get(name) == value
                for name, value in desired["fields"].items()
            ),
            _receipt_core(parse_receipt(current.get("body")))
            == _receipt_core(desired["receipt"]),
        )
    )


def plan_projection(
    workflow: dict[str, Any],
    entities: list[dict[str, Any]],
    target_items: list[dict[str, Any]],
    *,
    profile: str,
    repository: str,
    workflow_dir: str,
    state_ref: str,
    trunk_commit: str,
    state_commit: str,
    projector_version: str,
    projector_digest: str,
    status_options: list[str] | None = None,
) -> dict[str, Any]:
    """Create a deterministic plan without mutating source or target state."""

    if profile not in {"generic", "kc-dev-flow"}:
        raise ProjectionError(f"unsupported profile {profile!r}")
    target_by_identity = _target_by_identity(target_items)
    target_by_issue = {
        item.get("issue_number"): item
        for item in target_items
        if isinstance(item.get("issue_number"), int)
    }
    seen_slugs: set[str] = set()
    issue_counts = Counter(
        entity.get("issue") for entity in entities if isinstance(entity.get("issue"), int)
    )
    duplicate_issues = sorted(issue for issue, count in issue_counts.items() if count > 1)
    if duplicate_issues:
        raise ProjectionError(f"duplicate entity Issue references {duplicate_issues!r}")
    entity_id_counts = Counter(
        entity.get("id") for entity in entities if isinstance(entity.get("id"), str) and entity.get("id")
    )
    duplicate_entity_ids = sorted(
        entity_id for entity_id, count in entity_id_counts.items() if count > 1
    )
    if duplicate_entity_ids:
        raise ProjectionError(f"duplicate entity IDs {duplicate_entity_ids!r}")
    entity_results: list[dict[str, Any]] = []
    mutations: list[dict[str, Any]] = []

    for entity in sorted(entities, key=lambda item: item["_slug"]):
        slug = entity["_slug"]
        if slug in seen_slugs:
            raise ProjectionError(f"duplicate entity slug {slug!r}")
        seen_slugs.add(slug)
        stage = entity["status"]
        identity = _identity(repository, workflow_dir, slug)
        if stage not in workflow["stages"]:
            entity_results.append(
                {
                    "slug": slug,
                    "classification": "CONFLICT",
                    "reason": "unknown_stage",
                    "desired": None,
                    "missing_optional": [],
                }
            )
            continue

        explicit_issue = entity.get("issue")
        current = target_by_identity.get(identity)
        if current is None and isinstance(explicit_issue, int):
            current = target_by_issue.get(explicit_issue)
        if isinstance(explicit_issue, int) and current is None:
            entity_results.append(
                {
                    "slug": slug,
                    "classification": "CONFLICT",
                    "reason": "missing_linked_issue",
                    "desired": None,
                    "missing_optional": [],
                }
            )
            continue
        current_receipt = parse_receipt(current.get("body")) if current else None
        ownership = (
            current_receipt.get("ownership")
            if current_receipt and current_receipt.get("ownership") in {"projector", "linked"}
            else "linked" if isinstance(explicit_issue, int) else "projector"
        )
        fields = {"SD Stage": stage}
        target_status = _generic_status(workflow, stage, status_options or [])
        if target_status is not None:
            fields["Status"] = target_status
        missing_optional: list[str] = []
        if profile == "kc-dev-flow":
            product = entity.get("product")
            sprint = entity.get("sprint")
            if product:
                fields["SD Product"] = product
            else:
                missing_optional.append("product")
            if not sprint:
                missing_optional.append("sprint")

        receipt = {
            "schema": "spacedock-projection-receipt/v1",
            "identity": identity,
            "slug": slug,
            "entity_id": entity.get("id") or None,
            "state_ref": state_ref,
            "trunk_commit": trunk_commit,
            "state_commit": state_commit,
            "entity_digest": entity["_content_digest"],
            "projector_version": projector_version,
            "projector_digest": projector_digest,
            "ownership": ownership,
            "archived": bool(entity.get("_archived")),
        }
        base_body = (
            current.get("body")
            if ownership == "linked" and current
            else _projector_summary(
                entity,
                repository=repository,
                workflow_dir=workflow_dir,
                state_ref=state_ref,
            )
        )
        if ownership == "linked":
            desired_issue_state = current.get("issue_state", "OPEN") if current else "OPEN"
        else:
            desired_issue_state = (
                "CLOSED"
                if entity.get("_archived") or stage == workflow["terminal_stage"]
                else "OPEN"
            )
        desired = {
            "identity": identity,
            "title": current.get("title", entity["title"]) if ownership == "linked" and current else entity["title"],
            "issue_number": explicit_issue if isinstance(explicit_issue, int) else current.get("issue_number") if current else None,
            "issue_state": desired_issue_state,
            "body": _body_with_receipt(base_body, receipt),
            "fields": fields,
            "receipt": receipt,
        }
        if current is None:
            action = "CREATE"
        elif _same_managed_state(current, desired):
            action = "NO_CHANGE"
        else:
            action = "UPDATE"
        classification = "PARTIAL" if missing_optional else action
        entity_result = {
            "slug": slug,
            "classification": classification,
            "action": action,
            "desired": desired,
            "missing_optional": missing_optional,
        }
        entity_results.append(entity_result)
        if action in {"CREATE", "UPDATE"}:
            mutations.append(
                {
                    "action": action,
                    "identity": identity,
                    "current_item_id": current.get("item_id") if current else None,
                    "current_issue_number": current.get("issue_number") if current else None,
                    "desired": desired,
                }
            )

    current_identities = {
        _identity(repository, workflow_dir, entity["_slug"]) for entity in entities
    }
    orphans: list[dict[str, Any]] = []
    for identity, item in sorted(target_by_identity.items()):
        receipt = parse_receipt(item.get("body"))
        if identity.startswith(f"{repository}:{workflow_dir}:") and identity not in current_identities:
            orphans.append(
                {
                    "identity": identity,
                    "classification": "CONFLICT",
                    "reason": "missing_archive_tombstone",
                    "item_id": item.get("item_id"),
                    "receipt": receipt,
                }
            )

    return {
        "schema": "spacedock-projection-plan/v1",
        "profile": profile,
        "repository": repository,
        "workflow_dir": workflow_dir,
        "state_ref": state_ref,
        "trunk_commit": trunk_commit,
        "state_commit": state_commit,
        "projector_version": projector_version,
        "projector_digest": projector_digest,
        "status_options": status_options or [],
        "workflow": workflow,
        "entities": entity_results,
        "orphans": orphans,
        "mutations": mutations,
    }


def apply_fake(plan: dict[str, Any], target_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Apply a plan to an in-memory target for contract tests only."""

    result = copy.deepcopy(target_items)
    next_issue = max((item.get("issue_number", 0) or 0 for item in result), default=0) + 1
    for mutation in plan["mutations"]:
        desired = mutation["desired"]
        if mutation["action"] == "CREATE":
            issue_number = desired.get("issue_number")
            if not isinstance(issue_number, int):
                issue_number = next_issue
                next_issue += 1
            result.append(
                {
                    "item_id": f"FAKE-{len(result) + 1}",
                    "issue_number": issue_number,
                    "title": desired["title"],
                    "issue_state": desired["issue_state"],
                    "body": desired["body"],
                    "fields": copy.deepcopy(desired["fields"]),
                }
            )
            continue
        matched = False
        for item in result:
            if (
                mutation.get("current_item_id") is not None
                and item.get("item_id") == mutation["current_item_id"]
            ) or (
                mutation.get("current_issue_number") is not None
                and item.get("issue_number") == mutation["current_issue_number"]
            ):
                item.update(
                    {
                        "title": desired["title"],
                        "issue_state": desired["issue_state"],
                        "body": desired["body"],
                        "fields": copy.deepcopy(desired["fields"]),
                    }
                )
                matched = True
                break
        if not matched:
            raise ProjectionError(f"fake target lost update identity {mutation['identity']!r}")
    return result


def freshness_status(last_success: int | None, *, now: int, window: int) -> str:
    if window <= 0:
        raise ProjectionError("freshness window must be positive")
    if last_success is None:
        return "MISSING"
    return "CURRENT" if now - last_success <= window else "STALE"


def build_status_snapshot(plan: dict[str, Any]) -> dict[str, Any]:
    stages = [item["desired"]["fields"]["SD Stage"] for item in plan["entities"] if item["desired"]]
    members = [
        {
            "identity": item["desired"]["identity"],
            "entity_digest": item["desired"]["receipt"]["entity_digest"],
        }
        for item in plan["entities"]
        if item["desired"]
    ]
    return {
        "schema": "spacedock-status-snapshot/v1",
        "repository": plan["repository"],
        "workflow_dir": plan["workflow_dir"],
        "state_ref": plan["state_ref"],
        "trunk_commit": plan["trunk_commit"],
        "state_commit": plan["state_commit"],
        "projector_version": plan["projector_version"],
        "projector_digest": plan["projector_digest"],
        "member_set_digest": _digest(_canonical(sorted(members, key=lambda item: item["identity"]))),
        "stage_counts": dict(sorted(Counter(stages).items())),
        "terminal_count": sum(stage == plan["workflow"]["terminal_stage"] for stage in stages),
        "conflict_count": sum(item["classification"] == "CONFLICT" for item in plan["entities"])
        + len(plan["orphans"]),
    }


def _load_entities(state_dir: pathlib.Path) -> list[dict[str, Any]]:
    entities: list[dict[str, Any]] = []
    for path in sorted(state_dir.rglob("*.md")):
        relative = path.relative_to(state_dir)
        directories = relative.parts[:-1]
        if any(part.startswith("_") and part != "_archive" for part in directories):
            continue
        text = path.read_text()
        try:
            frontmatter = _frontmatter_lines(text)
        except ProjectionError:
            continue
        flat_keys = {
            line.split(":", 1)[0]
            for line in frontmatter
            if line and not line.startswith((" ", "\t")) and ":" in line
        }
        baseline = {"title", "status", "source"}
        if not flat_keys.intersection(baseline):
            continue
        archived = "_archive" in directories
        slug = path.parent.name if path.name == "index.md" else path.stem
        entities.append(parse_entity_text(text, slug=slug, archived=archived))
    return entities


def _git_commit(path: pathlib.Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def reconcile(
    config: dict[str, Any],
    *,
    trunk_dir: pathlib.Path,
    state_dir: pathlib.Path,
    client: Any,
) -> dict[str, Any]:
    validate_config(config)
    workflow_path = trunk_dir / config["workflow_dir"] / "README.md"
    workflow = parse_workflow_text(workflow_path.read_text())
    entities = _load_entities(state_dir)
    selection = config.get("entity_selection") or []
    if selection:
        available = {entity["_slug"]: entity for entity in entities}
        missing = sorted(set(selection) - set(available))
        if missing:
            raise ProjectionError(f"configured entity selection is missing {missing!r}")
        entities = [available[slug] for slug in sorted(set(selection))]
    linked_issue_numbers = {
        entity["issue"] for entity in entities if isinstance(entity.get("issue"), int)
    }
    fields, target = observe_github(
        client, config, linked_issue_numbers=linked_issue_numbers
    )
    projector_path = pathlib.Path(__file__)
    provenance = {
        "profile": config["profile"],
        "repository": config["repository"],
        "workflow_dir": config["workflow_dir"],
        "state_ref": config["state_ref"],
        "trunk_commit": _git_commit(trunk_dir),
        "state_commit": _git_commit(state_dir),
        "projector_version": VERSION,
        "projector_digest": _digest(projector_path.read_bytes()),
        "status_options": status_options_from_rest(fields),
    }
    plan = plan_projection(workflow, entities, target, **provenance)
    snapshot = build_status_snapshot(plan)
    result: dict[str, Any] = {
        "schema": "spacedock-project-reconcile-result/v1",
        "mode": "apply" if config.get("external_apply_enabled") else "dry-run",
        "plan": plan,
        "snapshot": snapshot,
        "operations": [],
        "project_schema_plan": project_schema_plan(plan, fields),
    }
    if config.get("external_apply_enabled"):
        result["operations"] = apply_github_plan(client, config, plan, fields)
        refreshed_fields, refreshed_target = observe_github(
            client, config, linked_issue_numbers=linked_issue_numbers
        )
        converged = plan_projection(
            workflow,
            entities,
            refreshed_target,
            **{**provenance, "status_options": status_options_from_rest(refreshed_fields)},
        )
        if converged["mutations"] or converged["orphans"]:
            raise ProjectionError("post-apply observation did not converge to zero mutations")
        result["converged_plan"] = converged
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", action="version", version=VERSION)
    subparsers = parser.add_subparsers(dest="command", required=True)
    plan_parser = subparsers.add_parser("plan", help="render a deterministic projection plan")
    plan_parser.add_argument("--workflow-readme", type=pathlib.Path, required=True)
    plan_parser.add_argument("--state-dir", type=pathlib.Path, required=True)
    plan_parser.add_argument("--target-state", type=pathlib.Path, required=True)
    plan_parser.add_argument("--profile", choices=("generic", "kc-dev-flow"), default="generic")
    plan_parser.add_argument("--repository", required=True)
    plan_parser.add_argument("--workflow-dir", required=True)
    plan_parser.add_argument("--state-ref", required=True)
    plan_parser.add_argument("--trunk-commit", required=True)
    plan_parser.add_argument("--state-commit", required=True)
    reconcile_parser = subparsers.add_parser(
        "reconcile", help="observe and optionally apply the configured GitHub projection"
    )
    reconcile_parser.add_argument("--config", type=pathlib.Path, required=True)
    reconcile_parser.add_argument("--trunk-dir", type=pathlib.Path, required=True)
    reconcile_parser.add_argument("--state-dir", type=pathlib.Path, required=True)
    reconcile_parser.add_argument("--output", type=pathlib.Path, required=True)

    args = parser.parse_args()
    if args.command == "reconcile":
        config = json.loads(args.config.read_text())
        args.output.parent.mkdir(parents=True, exist_ok=True)
        try:
            client = GitHubRestClient(
                os.environ.get("SPACEDOCK_REPOSITORY_TOKEN", ""),
                os.environ.get("SPACEDOCK_PROJECT_TOKEN", ""),
            )
            result = reconcile(
                config,
                trunk_dir=args.trunk_dir,
                state_dir=args.state_dir,
                client=client,
            )
        except Exception as exc:
            failure = {
                "schema": "spacedock-project-reconcile-result/v1",
                "mode": "failed",
                "error": f"{type(exc).__name__}: {exc}",
            }
            args.output.write_text(json.dumps(failure, indent=2, sort_keys=True) + "\n")
            print(json.dumps(failure, sort_keys=True))
            return 1
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(
            json.dumps(
                {"mode": result["mode"], "snapshot": result["snapshot"]},
                sort_keys=True,
            )
        )
        return 0

    projector_digest = _digest(pathlib.Path(__file__).read_bytes())
    workflow = parse_workflow_text(args.workflow_readme.read_text())
    entities = _load_entities(args.state_dir)
    target = json.loads(args.target_state.read_text())
    plan = plan_projection(
        workflow,
        entities,
        target,
        profile=args.profile,
        repository=args.repository,
        workflow_dir=args.workflow_dir,
        state_ref=args.state_ref,
        trunk_commit=args.trunk_commit,
        state_commit=args.state_commit,
        projector_version=VERSION,
        projector_digest=projector_digest,
    )
    print(json.dumps(plan, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
