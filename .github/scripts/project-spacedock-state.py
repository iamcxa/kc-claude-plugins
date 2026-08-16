#!/usr/bin/env python3
"""Deterministic Spacedock projection planner and bounded GitHub REST adapter."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import pathlib
import re
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import date, datetime, time as datetime_time, timezone
from email.utils import parsedate_to_datetime
from typing import Any


VERSION = "0.1.0"
RECEIPT_START = "<!-- spacedock-projection:v1"
RECEIPT_END = "-->"
MANAGED_LABEL = "spacedock:managed"
IDENTITY_FIELD = "SD Identity"
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
RECEIPT_REQUIRED_TYPES = {
    "schema": str,
    "identity": str,
    "slug": str,
    "entity_digest": str,
    "projector_version": str,
    "projector_digest": str,
    "ownership": str,
    "archived": bool,
}
MANAGED_ENTITY_FIELDS = {
    "id",
    "title",
    "status",
    "score",
    "source",
    "worktree",
    "issue",
    "product",
    "sprint",
}
ADD_DRAFT_MUTATION = """
mutation AddProjectDraft($projectId: ID!, $title: String!, $body: String!) {
  addProjectV2DraftIssue(
    input: {projectId: $projectId, title: $title, body: $body}
  ) {
    projectItem {
      id
      fullDatabaseId
      content { ... on DraftIssue { id } }
    }
  }
}
"""
UPDATE_DRAFT_MUTATION = """
mutation UpdateProjectDraft($draftIssueId: ID!, $title: String!, $body: String!) {
  updateProjectV2DraftIssue(
    input: {draftIssueId: $draftIssueId, title: $title, body: $body}
  ) {
    draftIssue { id }
  }
}
"""


class ProjectionError(ValueError):
    """Raised when source bytes cannot be projected safely."""


class GitHubRestClient:
    """Small REST 2026-03-10 transport with separate repository/project tokens."""

    def __init__(
        self,
        repository_token: str,
        project_token: str,
        *,
        sleep: Any = time.sleep,
        max_attempts: int = 3,
    ) -> None:
        if not repository_token or not project_token:
            raise ProjectionError("both repository and Project credentials are required")
        self._tokens = {"repository": repository_token, "project": project_token}
        self._sleep = sleep
        self._max_attempts = max_attempts

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
        for attempt in range(1, self._max_attempts + 1):
            try:
                with urllib.request.urlopen(request, timeout=30) as response:
                    payload = response.read()
                    headers = response.headers
                return (json.loads(payload) if payload else None), headers
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode("utf-8", errors="replace")[:500]
                retryable = exc.code in {429, 500, 502, 503, 504}
                if not retryable or attempt == self._max_attempts:
                    raise ProjectionError(
                        f"GitHub {method} {path} failed with HTTP {exc.code}: {detail}"
                    ) from exc
                self._sleep(_retry_delay(exc.headers.get("Retry-After"), attempt))
            except urllib.error.URLError as exc:
                if attempt == self._max_attempts:
                    raise ProjectionError(f"GitHub {method} {path} transport failed: {exc}") from exc
                self._sleep(min(2 ** (attempt - 1), 10))
        raise AssertionError("retry loop exhausted without returning or raising")

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

    def graphql(
        self, query: str, variables: dict[str, Any], *, authority: str
    ) -> dict[str, Any]:
        payload = self.request(
            "POST",
            "graphql",
            authority=authority,
            body={"query": query, "variables": variables},
        )
        if not isinstance(payload, dict):
            raise ProjectionError("GitHub GraphQL response is not an object")
        errors = payload.get("errors")
        if errors:
            raise ProjectionError(f"GitHub GraphQL mutation failed: {_canonical(errors)[:500]}")
        data = payload.get("data")
        if not isinstance(data, dict):
            raise ProjectionError("GitHub GraphQL response lacks data")
        return data


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: bytes | str) -> str:
    if isinstance(value, str):
        value = value.encode("utf-8")
    return hashlib.sha256(value).hexdigest()


def _retry_delay(raw: str | None, attempt: int) -> float:
    if raw:
        try:
            return min(max(float(raw), 0.0), 10.0)
        except ValueError:
            try:
                parsed = parsedate_to_datetime(raw)
                return min(max((parsed - datetime.now(timezone.utc)).total_seconds(), 0.0), 10.0)
            except (TypeError, ValueError, OverflowError):
                pass
    return float(min(2 ** (attempt - 1), 10))


def _frontmatter_lines(text: str) -> list[str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ProjectionError("missing opening frontmatter delimiter")
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return lines[1:index]
    raise ProjectionError("missing closing frontmatter delimiter")


def _normalize_markdown(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n").rstrip("\n")
    return f"{normalized}\n" if normalized else ""


def _entity_markdown(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = normalized.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        raise ProjectionError("missing opening frontmatter delimiter")
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            body = "".join(lines[index + 1 :])
            if body.startswith("\n"):
                body = body[1:]
            return _normalize_markdown(body)
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
    parent_key: str | None = None
    for line in _frontmatter_lines(text):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith((" ", "\t")):
            if parent_key in MANAGED_ENTITY_FIELDS:
                raise ProjectionError(
                    f"entity {slug!r} has nested data under managed field {parent_key!r}"
                )
            continue
        if ":" not in line:
            raise ProjectionError(f"entity {slug!r} has malformed frontmatter")
        key, raw = line.split(":", 1)
        if key in values:
            raise ProjectionError(f"entity {slug!r} repeats field {key!r}")
        values[key] = _scalar(raw)
        parent_key = key
    for required in ("title", "status", "source"):
        if not isinstance(values.get(required), str) or not values[required]:
            raise ProjectionError(f"entity {slug!r} is missing {required!r}")
    if isinstance(values.get("issue"), str) and values["issue"].isdigit():
        values["issue"] = int(values["issue"])
    issue = values.get("issue")
    if issue is not None and (isinstance(issue, bool) or not isinstance(issue, int) or issue <= 0):
        raise ProjectionError(f"entity {slug!r} issue must be a positive integer")
    for optional in ("id", "product", "sprint"):
        value = values.get(optional)
        if value is not None and (not isinstance(value, str) or not value):
            raise ProjectionError(f"entity {slug!r} {optional} must be a non-empty string")
    values["_slug"] = slug
    values["_archived"] = archived
    values["_content_digest"] = _digest(text)
    values["_body"] = _entity_markdown(text)
    return values


def _identity(repository: str, workflow_dir: str, slug: str) -> str:
    return f"{repository}:{workflow_dir}:{slug}"


def _assign_short_ids(
    workflow: dict[str, Any], entities: list[dict[str, Any]]
) -> None:
    style = workflow.get("id_style") or "sequential"
    if style not in {"slug", "sequential", "sd-b32"}:
        raise ProjectionError(f"unsupported id-style {style!r}")
    if style == "slug":
        for entity in entities:
            entity["_short_id"] = entity["_slug"]
        return
    if style == "sequential":
        for entity in entities:
            entity["_short_id"] = entity.get("id") or entity["_slug"]
        return
    stored_ids = [entity.get("id") for entity in entities]
    if any(
        not isinstance(value, str)
        or not re.fullmatch(r"[0123456789abcdefghjkmnpqrstvwxyz]{24}", value)
        for value in stored_ids
    ):
        raise ProjectionError("sd-b32 projection requires valid 24-character entity IDs")
    for entity in entities:
        value = entity["id"]
        length = 2
        while length < len(value) and sum(
            other.startswith(value[:length]) for other in stored_ids
        ) > 1:
            length += 1
        entity["_short_id"] = value[:length]


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
    if not isinstance(value, dict):
        raise ProjectionError("projection receipt must be a JSON object")
    for key, expected_type in RECEIPT_REQUIRED_TYPES.items():
        if not isinstance(value.get(key), expected_type):
            raise ProjectionError(f"projection receipt has invalid {key!r}")
    if value["schema"] not in {
        "spacedock-projection-receipt/v1",
        "spacedock-projection-receipt/v2",
    }:
        raise ProjectionError("unsupported projection receipt schema")
    if value["ownership"] not in {"projector", "linked"}:
        raise ProjectionError("projection receipt has invalid ownership")
    if not re.fullmatch(r"[0-9a-f]{64}", value["entity_digest"]):
        raise ProjectionError("projection receipt has invalid entity digest")
    if not re.fullmatch(r"[0-9a-f]{64}", value["projector_digest"]):
        raise ProjectionError("projection receipt has invalid projector digest")
    entity_id = value.get("entity_id")
    if entity_id is not None and not isinstance(entity_id, str):
        raise ProjectionError("projection receipt has invalid entity ID")
    return value


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
    visible_body = body.rstrip("\r\n")
    return f"{visible_body}\n\n{marker}"


def _body_without_receipt(body: str | None) -> str:
    if not body:
        return ""
    pattern = re.compile(
        re.escape(RECEIPT_START) + r"\n\{.*?\}\n" + re.escape(RECEIPT_END),
        re.DOTALL,
    )
    return _normalize_markdown(pattern.sub("", body).rstrip("\r\n"))


def _normalized_labels(item: dict[str, Any]) -> set[str]:
    return {
        label
        for label in item.get("labels", [])
        if isinstance(label, str) and label
    }


def _receipt_core(receipt: dict[str, Any] | None) -> dict[str, Any] | None:
    if receipt is None:
        return None
    return {key: receipt.get(key) for key in sorted(COMPARED_RECEIPT_KEYS)}


def _generic_status(
    workflow: dict[str, Any], stage: str, status_options: list[str]
) -> str | None:
    if stage == workflow["initial_stage"]:
        candidates = ("Todo", "Backlog")
    elif stage == workflow["terminal_stage"]:
        candidates = ("Done",)
    else:
        candidates = ("In progress", "In Progress")
    return next((candidate for candidate in candidates if candidate in status_options), None)


def _target_by_identity(
    target_items: list[dict[str, Any]],
    *,
    repository: str | None = None,
    workflow_dir: str | None = None,
) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    prefix = f"{repository}:{workflow_dir}:" if repository and workflow_dir else None
    for item in target_items:
        if repository and item.get("repository") not in {None, repository}:
            continue
        receipt = parse_receipt(item.get("body"))
        receipt_identity = receipt.get("identity") if receipt else None
        field_identity = (item.get("fields") or {}).get(IDENTITY_FIELD)
        identities = {
            value
            for value in (receipt_identity, field_identity)
            if isinstance(value, str) and (prefix is None or value.startswith(prefix))
        }
        indexed = item
        if (
            isinstance(receipt_identity, str)
            and isinstance(field_identity, str)
            and receipt_identity != field_identity
        ):
            indexed = {**item, "_identity_conflict": "identity_anchor_mismatch"}
        for identity in identities:
            if identity in result:
                result[identity] = {
                    **result[identity],
                    "_identity_conflict": "duplicate_identity_anchor",
                }
            else:
                result[identity] = indexed
    return result


def _repository_from_url(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    match = re.search(r"(?:api\.github\.com/repos/|github\.com/)([^/]+/[^/#]+)", value)
    return match.group(1) if match else None


def _issue_identity(repository: str, number: int) -> str:
    return f"{repository}#{number}"


def _label_names(raw_labels: Any) -> list[str]:
    if not isinstance(raw_labels, list):
        return []
    names: list[str] = []
    for label in raw_labels:
        name = (
            label
            if isinstance(label, str)
            else label.get("name") if isinstance(label, dict) else None
        )
        if isinstance(name, dict):
            name = name.get("raw")
        if isinstance(name, str) and name:
            names.append(name)
    return sorted(set(names))


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
        content_type = item.get("content_type") or "Issue"
        if content_type not in {"DraftIssue", "Issue"}:
            continue
        content = item.get("content") or {}
        content_repository: str | None = None
        issue_number: int | None = None
        issue_identity: str | None = None
        if content_type == "Issue":
            if (
                isinstance(content.get("number"), bool)
                or not isinstance(content.get("number"), int)
                or content["number"] <= 0
            ):
                continue
            issue_number = content["number"]
            content_repository = _repository_from_url(content.get("repository_url"))
            if content_repository is None:
                raise ProjectionError("Project Issue observation lacks repository identity")
            issue_identity = _issue_identity(content_repository, issue_number)
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
                "content_type": content_type,
                "content_node_id": content.get("node_id"),
                "issue_number": issue_number,
                "repository": content_repository,
                "issue_identity": issue_identity,
                "issue_id": content.get("id") if content_type == "Issue" else None,
                "author_login": (content.get("user") or {}).get("login"),
                "title": content.get("title"),
                "issue_state": (
                    str(content.get("state", "open")).upper()
                    if content_type == "Issue"
                    else None
                ),
                "body": content.get("body") or "",
                "fields": values,
                "labels": (
                    _label_names(content.get("labels"))
                    if content_type == "Issue"
                    else []
                ),
            }
        )
    return result


def merge_repository_issues(
    target_items: list[dict[str, Any]],
    issues: list[dict[str, Any]],
    *,
    repository: str | None = None,
    linked_issue_numbers: set[int] | None = None,
    managed_identity_prefix: str | None = None,
    trusted_automation_authors: set[str] | None = None,
) -> list[dict[str, Any]]:
    """Include stranded managed Issues and explicitly linked human Issues."""

    result = copy.deepcopy(target_items)
    projected_identities = {
        item.get("issue_identity")
        or (
            _issue_identity(repository, item["issue_number"])
            if repository and isinstance(item.get("issue_number"), int)
            else None
        )
        for item in result
    }
    linked_issue_numbers = linked_issue_numbers or set()
    trusted_automation_authors = trusted_automation_authors or {"github-actions[bot]"}
    for issue in issues:
        number = issue.get("number")
        issue_identity = (
            _issue_identity(repository, number)
            if repository and isinstance(number, int)
            else None
        )
        if issue.get("pull_request") or issue_identity in projected_identities:
            continue
        body = issue.get("body") or ""
        linked = number in linked_issue_numbers
        try:
            receipt = parse_receipt(body)
        except ProjectionError:
            if linked:
                raise
            continue
        author_login = (issue.get("user") or {}).get("login")
        issue_labels = _label_names(issue.get("labels"))
        trusted_receipt = bool(
            receipt
            and author_login in trusted_automation_authors
            and (
                managed_identity_prefix is None
                or receipt["identity"].startswith(managed_identity_prefix)
            )
        )
        label_only_candidate = MANAGED_LABEL in issue_labels and receipt is None
        if not linked and not trusted_receipt and not label_only_candidate:
            continue
        result.append(
            {
                "item_id": None,
                "item_node_id": None,
                "issue_number": number,
                "repository": repository,
                "issue_identity": issue_identity,
                "issue_id": issue.get("id"),
                "author_login": author_login,
                "title": issue.get("title"),
                "issue_state": str(issue.get("state", "open")).upper(),
                "body": body,
                "fields": {},
                "labels": issue_labels,
            }
        )
    return result


def _project_base(config: dict[str, Any]) -> str:
    project = config["project"]
    prefix = "users" if project["owner_type"] == "user" else "orgs"
    return f"{prefix}/{project['owner']}/projectsV2/{project['number']}"


def _timestamp(value: Any, *, end_of_day: bool = False) -> datetime:
    if not isinstance(value, str) or not value:
        raise ProjectionError("approval and credential expiry must be ISO-8601 strings")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", normalized):
            parsed_date = date.fromisoformat(normalized)
            parsed = datetime.combine(
                parsed_date,
                datetime_time.max if end_of_day else datetime_time.min,
                tzinfo=timezone.utc,
            )
        else:
            parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ProjectionError(f"invalid ISO-8601 expiry {value!r}") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def validate_approval_scope(approval: dict[str, Any], selection: list[Any]) -> None:
    scope = approval.get("scope")
    if scope not in {"selected", "workflow"}:
        raise ProjectionError("approval scope must be 'selected' or 'workflow'")
    if not isinstance(selection, list) or any(
        not isinstance(slug, str) or not slug for slug in selection
    ):
        raise ProjectionError("entity selection must contain non-empty slugs")
    if len(selection) != len(set(selection)):
        raise ProjectionError("entity selection contains duplicate slugs")
    if scope == "selected" and not selection:
        raise ProjectionError("selected approval requires a non-empty entity selection")
    if scope == "workflow" and selection:
        raise ProjectionError("workflow approval cannot include an entity selection")


def _validate_linked_bindings(bindings: Any, repository: str) -> None:
    if not isinstance(bindings, dict):
        raise ProjectionError("approval linked_issues must be an object")
    pattern = re.compile(r"(?P<repository>[^\s/#]+/[^\s/#]+)#(?P<number>[1-9][0-9]*)")
    for slug, identity in bindings.items():
        if not isinstance(slug, str) or not slug or not isinstance(identity, str):
            raise ProjectionError("linked Issue bindings require non-empty slug and identity")
        match = pattern.fullmatch(identity)
        if not match or match.group("repository") != repository:
            raise ProjectionError(
                f"linked Issue binding for {slug!r} must use {repository}#number"
            )


def validate_config(
    config: dict[str, Any],
    *,
    installed_projector_digest: str | None = None,
    now: datetime | None = None,
) -> None:
    if config.get("schema") != "spacedock-project-config/v1":
        raise ProjectionError("unsupported projection config schema")
    if not isinstance(config.get("external_apply_enabled"), bool):
        raise ProjectionError("external_apply_enabled must be boolean")
    for name in ("repository", "trunk_ref", "state_ref", "workflow_dir", "profile"):
        if not isinstance(config.get(name), str) or not config[name]:
            raise ProjectionError(f"configuration requires non-empty {name!r}")
    if config["profile"] not in {"generic", "kc-dev-flow"}:
        raise ProjectionError("unsupported mapping profile")
    project = config.get("project")
    if not isinstance(project, dict) or project.get("owner_type") not in {"user", "organization"}:
        raise ProjectionError("configuration requires a user or organization Project")
    if (
        not isinstance(project.get("owner"), str)
        or not project["owner"]
        or isinstance(project.get("number"), bool)
        or not isinstance(project.get("number"), int)
        or project["number"] <= 0
    ):
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
        approval = config.get("approval")
        if not isinstance(approval, dict):
            raise ProjectionError("external apply requires a reviewed approval envelope")
        validate_approval_scope(approval, config.get("entity_selection") or [])
        digest = approval.get("projector_digest")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ProjectionError("approval requires a SHA-256 projector digest")
        if installed_projector_digest is None or digest != installed_projector_digest:
            raise ProjectionError("approval projector digest does not match installed projector digest")
        cap = approval.get("max_mutations_per_run")
        if isinstance(cap, bool) or not isinstance(cap, int) or cap <= 0:
            raise ProjectionError("approval mutation cap must be a positive integer")
        _validate_linked_bindings(approval.get("linked_issues"), config["repository"])
        approval_expiry = _timestamp(approval.get("expires_at"))
        credential_expiry = _timestamp(credential.get("expiry"), end_of_day=True)
        if approval_expiry > credential_expiry:
            raise ProjectionError("approval expiry cannot exceed credential expiry")
        current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
        if current >= approval_expiry:
            raise ProjectionError("projection approval envelope has expired")


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
        normalized,
        issues,
        repository=repository,
        linked_issue_numbers=linked_issue_numbers,
        managed_identity_prefix=f"{repository}:{config['workflow_dir']}:",
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


def required_project_schema(plan: dict[str, Any]) -> dict[str, dict[str, Any]]:
    values: dict[str, set[str]] = {}
    for entity in plan["entities"]:
        desired = entity.get("desired")
        if not desired:
            continue
        for name, value in desired["fields"].items():
            if name == "Status":
                continue
            values.setdefault(name, set()).add(str(value))
    return {
        name: (
            {"data_type": "text"}
            if name == IDENTITY_FIELD
            else {"data_type": "single_select", "options": sorted(options)}
        )
        for name, options in sorted(values.items())
    }


def validate_project_schema(
    plan: dict[str, Any], fields: list[dict[str, Any]], *, allow_missing: bool
) -> None:
    by_name = _field_by_name(fields)
    for name, requirement in required_project_schema(plan).items():
        field = by_name.get(name)
        if field is None:
            if allow_missing:
                continue
            raise ProjectionError(f"required Project field {name!r} is missing")
        data_type = requirement["data_type"]
        if field.get("data_type") != data_type:
            raise ProjectionError(f"Project field {name!r} is not {data_type}")
        if data_type == "single_select":
            missing = sorted(
                set(requirement["options"]) - set(_single_select_options(field))
            )
            if missing:
                raise ProjectionError(f"Project field {name!r} lacks options {missing!r}")


def project_schema_plan(
    plan: dict[str, Any], fields: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    by_name = _field_by_name(fields)
    result: list[dict[str, Any]] = []
    for name, requirement in required_project_schema(plan).items():
        field = by_name.get(name)
        if field is None:
            result.append(
                {
                    "action": "CREATE_FIELD",
                    "field": name,
                    "data_type": requirement["data_type"],
                    "options": requirement.get("options", []),
                }
            )
            continue
        data_type = requirement["data_type"]
        if field.get("data_type") != data_type:
            result.append(
                {
                    "action": "CONFLICT_FIELD_TYPE",
                    "field": name,
                    "data_type": data_type,
                    "observed_data_type": field.get("data_type"),
                    "missing_options": [],
                }
            )
            continue
        existing = _single_select_options(field) if data_type == "single_select" else {}
        missing = sorted(set(requirement.get("options", [])) - set(existing))
        result.append(
            {
                "action": "UPDATE_FIELD_OPTIONS" if missing else "NO_CHANGE",
                "field": name,
                "data_type": data_type,
                "missing_options": missing,
            }
        )
    return result


def apply_github_plan(
    client: Any,
    config: dict[str, Any],
    plan: dict[str, Any],
    fields: list[dict[str, Any]],
    *,
    journal: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Apply a conflict-free plan through resumable content then field writes."""

    conflicts = [item for item in plan["entities"] if item["classification"] == "CONFLICT"]
    if conflicts or plan["orphans"]:
        raise ProjectionError("conflicts must be resolved before external apply")
    repository = config["repository"]
    for mutation in plan["mutations"]:
        desired_type = mutation["desired"].get("content_type")
        issue_number = mutation.get("current_issue_number")
        issue_id = mutation.get("current_issue_id")
        if issue_number is not None and mutation.get("current_repository") != repository:
            raise ProjectionError("observed Issue repository does not match configured repository")
        if mutation.get("ownership") == "linked" and (
            not isinstance(issue_number, int) or not isinstance(issue_id, int)
        ):
            raise ProjectionError("linked Issue observation lacks stable Issue identity")
        if (
            desired_type == "Issue"
            and issue_number is not None
            and mutation.get("current_item_id") is None
            and not isinstance(issue_id, int)
        ):
            raise ProjectionError("stranded Issue observation lacks stable Issue identity")
        if (
            desired_type == "DraftIssue"
            and mutation.get("current_item_id") is not None
            and mutation.get("current_content_type") == "DraftIssue"
            and not isinstance(mutation.get("current_content_node_id"), str)
        ):
            raise ProjectionError("Draft observation lacks stable content node ID")
    validate_project_schema(plan, fields, allow_missing=True)
    project_base = _project_base(config)
    operations = journal if journal is not None else []
    by_name = _field_by_name(fields)
    planned_writes = sum(name not in by_name for name in required_project_schema(plan))
    for mutation in plan["mutations"]:
        desired_type = mutation["desired"].get("content_type")
        if desired_type == "DraftIssue" and (
            mutation.get("current_item_id") is None
            or mutation.get("content_update_required")
        ):
            planned_writes += 1
        if desired_type == "Issue" and mutation.get("current_item_id") is None:
            planned_writes += 1
        if mutation.get("field_update_required"):
            planned_writes += 1
    cap = (config.get("approval") or {}).get("max_mutations_per_run")
    if isinstance(cap, bool) or not isinstance(cap, int) or cap <= 0:
        raise ProjectionError("external apply requires a positive mutation cap")
    if planned_writes > cap:
        raise ProjectionError(
            f"planned {planned_writes} writes exceed mutation cap {cap}"
        )
    for name, requirement in required_project_schema(plan).items():
        if name in by_name:
            continue
        data_type = requirement["data_type"]
        field_payload: dict[str, Any] = {"name": name, "data_type": data_type}
        if data_type == "single_select":
            field_payload["single_select_options"] = [
                {"name": option, "color": "GRAY", "description": "Spacedock derived value"}
                for option in requirement["options"]
            ]
        response = client.request(
            "POST",
            f"{project_base}/fields",
            authority="project",
            body=field_payload,
        )
        field = {**field_payload, **_unwrap(response)}
        fields.append(field)
        by_name[name] = field
        operations.append({"action": "CREATE_FIELD", "field": name})
    validate_project_schema(plan, fields, allow_missing=False)

    for mutation in plan["mutations"]:
        desired = mutation["desired"]
        desired_type = desired.get("content_type")
        issue_number = mutation.get("current_issue_number") or desired.get("issue_number")
        issue_id: int | None = mutation.get("current_issue_id")
        item_id = mutation.get("current_item_id")
        if desired_type == "DraftIssue":
            if item_id is None:
                data = client.graphql(
                    ADD_DRAFT_MUTATION,
                    {
                        "projectId": config["project"]["node_id"],
                        "title": desired["title"],
                        "body": desired["body"],
                    },
                    authority="project",
                )
                project_item = (data.get("addProjectV2DraftIssue") or {}).get(
                    "projectItem"
                )
                if not isinstance(project_item, dict):
                    raise ProjectionError("Draft creation response lacks Project item")
                raw_item_id = project_item.get("fullDatabaseId")
                try:
                    item_id = int(raw_item_id)
                except (TypeError, ValueError) as exc:
                    raise ProjectionError(
                        "Draft creation response lacks numeric Project item ID"
                    ) from exc
                content = project_item.get("content") or {}
                if not isinstance(content.get("id"), str):
                    raise ProjectionError("Draft creation response lacks content node ID")
                operations.append(
                    {"action": "CREATE_DRAFT", "identity": mutation["identity"]}
                )
            elif mutation.get("content_update_required"):
                draft_id = mutation.get("current_content_node_id")
                if not isinstance(draft_id, str):
                    raise ProjectionError("Draft update lacks content node ID")
                client.graphql(
                    UPDATE_DRAFT_MUTATION,
                    {
                        "draftIssueId": draft_id,
                        "title": desired["title"],
                        "body": desired["body"],
                    },
                    authority="project",
                )
                operations.append(
                    {"action": "UPDATE_DRAFT", "identity": mutation["identity"]}
                )
        elif mutation.get("ownership") == "linked" and item_id is None:
            item = client.request(
                "POST",
                f"{project_base}/items",
                authority="project",
                body={"type": "Issue", "id": issue_id},
            )
            item_id = _unwrap(item)["id"]
            operations.append({"action": "ADD_PROJECT_ITEM", "issue_number": issue_number})
        elif desired_type != "Issue":
            raise ProjectionError(f"unsupported desired content type {desired_type!r}")

        if mutation.get("field_update_required"):
            field_values: list[dict[str, Any]] = []
            for name, value in desired["fields"].items():
                field = by_name.get(name)
                if field is None:
                    raise ProjectionError(f"Project field {name!r} is unavailable")
                if field.get("data_type") == "text":
                    field_values.append({"id": field["id"], "value": str(value)})
                else:
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
            operations.append(
                {
                    "action": "UPDATE_FIELDS",
                    "identity": mutation["identity"],
                    "issue_number": issue_number,
                }
            )
    return operations


def _same_managed_state(current: dict[str, Any], desired: dict[str, Any]) -> bool:
    if desired["receipt"]["ownership"] == "linked":
        return current.get("item_id") is not None and all(
            current.get("fields", {}).get(name) == value
            for name, value in desired["fields"].items()
        )
    common = (
        current.get("content_type") == desired["content_type"],
        current.get("item_id") is not None,
        current.get("title") == desired["title"],
        all(
            current.get("fields", {}).get(name) == value
            for name, value in desired["fields"].items()
        ),
        _body_without_receipt(current.get("body"))
        == _body_without_receipt(desired.get("body")),
        _receipt_core(parse_receipt(current.get("body")))
        == _receipt_core(desired["receipt"]),
    )
    if desired["content_type"] == "DraftIssue":
        return all(common)
    return all(
        (*common, current.get("issue_state") == desired["issue_state"], MANAGED_LABEL in _normalized_labels(current))
    )


def _same_projector_content_bytes(
    current: dict[str, Any], desired: dict[str, Any]
) -> bool:
    same_content = (
        current.get("title") == desired["title"],
        _body_without_receipt(current.get("body"))
        == _body_without_receipt(desired.get("body")),
        _receipt_core(parse_receipt(current.get("body")))
        == _receipt_core(desired["receipt"]),
    )
    if desired["content_type"] == "DraftIssue":
        return all(same_content)
    return all((*same_content, current.get("issue_state") == desired["issue_state"]))


def _conflict(slug: str, reason: str) -> dict[str, Any]:
    return {
        "slug": slug,
        "classification": "CONFLICT",
        "reason": reason,
        "desired": None,
        "missing_optional": [],
    }


def _validate_entity_population(entities: list[dict[str, Any]]) -> None:
    for field, label in (("_slug", "slugs"), ("issue", "Issue references"), ("id", "IDs")):
        values = [
            entity.get(field)
            for entity in entities
            if entity.get(field) is not None and not isinstance(entity.get(field), bool)
        ]
        duplicates = sorted(value for value, count in Counter(values).items() if count > 1)
        if duplicates:
            raise ProjectionError(f"duplicate entity {label} {duplicates!r}")


def _resolve_target(
    entity: dict[str, Any],
    *,
    identity: str,
    repository: str,
    target_by_identity: dict[str, dict[str, Any]],
    target_by_issue: dict[str, dict[str, Any]],
    linked_issue_bindings: dict[str, str],
) -> tuple[dict[str, Any] | None, str, str | None]:
    slug = entity["_slug"]
    explicit_issue = entity.get("issue")
    ownership = "linked" if isinstance(explicit_issue, int) else "projector"
    current = target_by_identity.get(identity)
    if isinstance(explicit_issue, int):
        explicit_identity = _issue_identity(repository, explicit_issue)
        if linked_issue_bindings.get(slug) != explicit_identity:
            return None, ownership, "unapproved_linked_issue"
        if current is not None:
            current_identity = current.get("issue_identity") or _issue_identity(
                repository, current["issue_number"]
            )
            if current_identity != explicit_identity:
                return None, ownership, "explicit_issue_identity_mismatch"
        else:
            current = target_by_issue.get(explicit_identity)
        if current is None:
            return None, ownership, "missing_linked_issue"
    receipt = parse_receipt(current.get("body")) if current else None
    if current and current.get("_identity_conflict"):
        return None, ownership, str(current["_identity_conflict"])
    if receipt and receipt["ownership"] != ownership:
        return None, ownership, "ownership_mismatch"
    if current and ownership == "projector" and receipt is None:
        return None, ownership, "missing_receipt_anchor"
    return current, ownership, None


def _desired_fields(
    workflow: dict[str, Any],
    entity: dict[str, Any],
    *,
    profile: str,
    status_options: list[str],
) -> tuple[dict[str, str], list[str]]:
    fields = {"SD Stage": entity["status"]}
    target_status = _generic_status(workflow, entity["status"], status_options)
    if target_status is not None:
        fields["Status"] = target_status
    missing_optional: list[str] = []
    if profile == "kc-dev-flow":
        if entity.get("product"):
            fields["SD Product"] = entity["product"]
        else:
            missing_optional.append("product")
        if not entity.get("sprint"):
            missing_optional.append("sprint")
    return fields, missing_optional


def _projection_receipt(
    entity: dict[str, Any],
    *,
    identity: str,
    ownership: str,
    state_ref: str,
    trunk_commit: str,
    state_commit: str,
    projector_version: str,
    projector_digest: str,
) -> dict[str, Any]:
    return {
        "schema": "spacedock-projection-receipt/v2",
        "identity": identity,
        "slug": entity["_slug"],
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


def _desired_issue(
    workflow: dict[str, Any],
    entity: dict[str, Any],
    current: dict[str, Any] | None,
    *,
    identity: str,
    ownership: str,
    fields: dict[str, str],
    receipt: dict[str, Any],
) -> dict[str, Any]:
    linked = ownership == "linked"
    issue_state = (
        current.get("issue_state", "OPEN")
        if linked and current
        else "CLOSED"
        if entity.get("_archived") or entity["status"] == workflow["terminal_stage"]
        else "OPEN"
    )
    body = (
        current.get("body", "")
        if linked and current
        else _body_with_receipt(
            entity["_body"],
            receipt,
        )
    )
    return {
        "identity": identity,
        "content_type": "Issue" if linked else "DraftIssue",
        "title": (
            current.get("title", entity["title"])
            if linked and current
            else f"[{entity['_short_id']}] {entity['title']}"
        ),
        "issue_number": (
            entity["issue"]
            if isinstance(entity.get("issue"), int)
            else current.get("issue_number") if current else None
        ),
        "issue_state": issue_state,
        "body": body,
        "fields": fields,
        "labels": [],
        "receipt": receipt,
    }


def _orphan_conflicts(
    target_by_identity: dict[str, dict[str, Any]],
    current_identities: set[str],
    *,
    prefix: str,
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for identity, item in sorted(target_by_identity.items()):
        if identity.startswith(prefix) and identity not in current_identities:
            result.append(
                {
                    "identity": identity,
                    "classification": "CONFLICT",
                    "reason": "missing_archive_tombstone",
                    "item_id": item.get("item_id"),
                    "receipt": parse_receipt(item.get("body")),
                }
            )
    return result


def _plan_entity(
    workflow: dict[str, Any],
    entity: dict[str, Any],
    *,
    profile: str,
    repository: str,
    workflow_dir: str,
    state_ref: str,
    trunk_commit: str,
    state_commit: str,
    projector_version: str,
    projector_digest: str,
    status_options: list[str],
    target_by_identity: dict[str, dict[str, Any]],
    target_by_issue: dict[str, dict[str, Any]],
    linked_issue_bindings: dict[str, str],
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    slug = entity["_slug"]
    identity = _identity(repository, workflow_dir, slug)
    if entity["status"] not in workflow["stages"]:
        return _conflict(slug, "unknown_stage"), None
    current, ownership, conflict = _resolve_target(
        entity,
        identity=identity,
        repository=repository,
        target_by_identity=target_by_identity,
        target_by_issue=target_by_issue,
        linked_issue_bindings=linked_issue_bindings,
    )
    if conflict:
        return _conflict(slug, conflict), None
    fields, missing_optional = _desired_fields(
        workflow, entity, profile=profile, status_options=status_options
    )
    fields[IDENTITY_FIELD] = identity
    receipt = _projection_receipt(
        entity,
        identity=identity,
        ownership=ownership,
        state_ref=state_ref,
        trunk_commit=trunk_commit,
        state_commit=state_commit,
        projector_version=projector_version,
        projector_digest=projector_digest,
    )
    desired = _desired_issue(
        workflow,
        entity,
        current,
        identity=identity,
        ownership=ownership,
        fields=fields,
        receipt=receipt,
    )
    source_metadata = {
        "product": entity.get("product"),
        "sprint": entity.get("sprint"),
        "sprint_identity": (
            f"{repository}:{workflow_dir}:sprint:{entity['sprint']}"
            if entity.get("sprint")
            else None
        ),
        "goal_digest": (
            _digest(_canonical(entity["goal"])) if entity.get("goal") else None
        ),
        "exit_digest": (
            _digest(_canonical(entity.get("exit-criteria") or entity.get("exit_criteria")))
            if entity.get("exit-criteria") or entity.get("exit_criteria")
            else None
        ),
    }
    action = (
        "CREATE"
        if current is None
        else "NO_CHANGE" if _same_managed_state(current, desired) else "UPDATE"
    )
    result = {
        "slug": slug,
        "classification": "PARTIAL" if missing_optional else action,
        "action": action,
        "desired": desired,
        "missing_optional": missing_optional,
        "source_metadata": source_metadata,
    }
    if action == "NO_CHANGE":
        return result, None
    mutation = {
        "action": action,
        "identity": identity,
        "current_item_id": current.get("item_id") if current else None,
        "current_content_type": current.get("content_type") if current else None,
        "current_content_node_id": current.get("content_node_id") if current else None,
        "current_issue_number": current.get("issue_number") if current else None,
        "current_issue_id": current.get("issue_id") if current else None,
        "current_repository": current.get("repository") if current else None,
        "ownership": ownership,
        "content_update_required": bool(
            current
            and ownership == "projector"
            and not _same_projector_content_bytes(current, desired)
        ),
        "issue_update_required": False,
        "field_update_required": bool(
            current is None
            or current.get("item_id") is None
            or any(
                current.get("fields", {}).get(name) != value
                for name, value in desired["fields"].items()
            )
        ),
        "desired": desired,
    }
    return result, mutation


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
    linked_issue_bindings: dict[str, str] | None = None,
    detect_orphans: bool = True,
) -> dict[str, Any]:
    """Create a deterministic plan without mutating source or target state."""

    if profile not in {"generic", "kc-dev-flow"}:
        raise ProjectionError(f"unsupported profile {profile!r}")
    _validate_entity_population(entities)
    if any(not entity.get("_short_id") for entity in entities):
        _assign_short_ids(workflow, entities)
    draft_items = [
        item for item in target_items if item.get("content_type") == "DraftIssue"
    ]
    target_by_identity = _target_by_identity(
        draft_items, repository=repository, workflow_dir=workflow_dir
    )
    legacy_issue_items = []
    invalid_legacy_by_identity: dict[str, list[dict[str, Any]]] = {}
    identity_prefix = f"{repository}:{workflow_dir}:"
    for item in target_items:
        if item.get("content_type") not in {None, "Issue"}:
            continue
        receipt = parse_receipt(item.get("body"))
        field_identity = (item.get("fields") or {}).get(IDENTITY_FIELD)
        if not (
            (receipt and receipt.get("ownership") == "projector")
            or MANAGED_LABEL in _normalized_labels(item)
        ):
            continue
        receipt_identity = receipt.get("identity") if receipt else None
        is_valid_residue = (
            receipt is not None
            and receipt.get("schema") == "spacedock-projection-receipt/v2"
            and receipt.get("ownership") == "projector"
            and item.get("author_login") == "github-actions[bot]"
            and field_identity == receipt_identity
        )
        if is_valid_residue:
            legacy_issue_items.append(item)
            continue
        for candidate_identity in {receipt_identity, field_identity}:
            if isinstance(candidate_identity, str) and candidate_identity.startswith(
                identity_prefix
            ):
                invalid_legacy_by_identity.setdefault(candidate_identity, []).append(item)
    legacy_by_identity = _target_by_identity(
        legacy_issue_items, repository=repository, workflow_dir=workflow_dir
    )
    target_by_issue = {
        item.get("issue_identity") or _issue_identity(repository, item["issue_number"]): item
        for item in target_items
        if isinstance(item.get("issue_number"), int)
    }
    unidentified_managed = []
    for item in target_items:
        if item.get("repository") not in {None, repository}:
            continue
        receipt = parse_receipt(item.get("body"))
        field_identity = (item.get("fields") or {}).get(IDENTITY_FIELD)
        has_anchor = receipt is not None or isinstance(field_identity, str)
        if not has_anchor and MANAGED_LABEL not in _normalized_labels(item):
            continue
        identities = (
            receipt.get("identity") if receipt else None,
            field_identity,
        )
        if not any(
            isinstance(value, str) and value.startswith(identity_prefix)
            for value in identities
        ):
            unidentified_managed.append(item)
    bindings = linked_issue_bindings or {}
    entity_results: list[dict[str, Any]] = []
    mutations: list[dict[str, Any]] = []
    migration_residues: list[dict[str, Any]] = []

    for entity in sorted(entities, key=lambda item: item["_slug"]):
        identity = _identity(repository, workflow_dir, entity["_slug"])
        result, mutation = _plan_entity(
            workflow,
            entity,
            profile=profile,
            repository=repository,
            workflow_dir=workflow_dir,
            state_ref=state_ref,
            trunk_commit=trunk_commit,
            state_commit=state_commit,
            projector_version=projector_version,
            projector_digest=projector_digest,
            status_options=status_options or [],
            target_by_identity=target_by_identity,
            target_by_issue=target_by_issue,
            linked_issue_bindings=bindings,
        )
        residue = legacy_by_identity.get(identity)
        if invalid_legacy_by_identity.get(identity):
            result = _conflict(entity["_slug"], "untrusted_issue_migration_residue")
            mutation = None
        elif residue and residue.get("_identity_conflict"):
            result = _conflict(entity["_slug"], str(residue["_identity_conflict"]))
            mutation = None
        elif residue:
            migration_residues.append(
                {
                    "identity": identity,
                    "item_id": residue.get("item_id"),
                    "issue_number": residue.get("issue_number"),
                }
            )
        if (
            mutation
            and mutation["action"] == "CREATE"
            and mutation["ownership"] == "projector"
            and unidentified_managed
        ):
            result = _conflict(entity["_slug"], "managed_candidate_missing_identity")
            mutation = None
        entity_results.append(result)
        if mutation:
            mutations.append(mutation)

    current_identities = {
        _identity(repository, workflow_dir, entity["_slug"]) for entity in entities
    }
    orphans = (
        _orphan_conflicts(
            target_by_identity,
            current_identities,
            prefix=f"{repository}:{workflow_dir}:",
        )
        if detect_orphans
        else []
    )
    if detect_orphans:
        orphans.extend(
            {
                "identity": None,
                "classification": "CONFLICT",
                "reason": "managed_item_missing_identity",
                "item_id": item.get("item_id"),
                "issue_number": item.get("issue_number"),
                "receipt": None,
            }
            for item in unidentified_managed
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
        "migration_residues": migration_residues,
        "mutations": mutations,
    }


def freshness_status(last_success: int | None, *, now: int, window: int) -> str:
    if window <= 0:
        raise ProjectionError("freshness window must be positive")
    if last_success is None:
        return "MISSING"
    return "CURRENT" if now - last_success <= window else "STALE"


def build_status_snapshot(
    plan: dict[str, Any],
    *,
    project: dict[str, Any] | None = None,
    last_success: int | None = None,
    observed_at: int | None = None,
    freshness_window: int | None = None,
) -> dict[str, Any]:
    stages = [item["desired"]["fields"]["SD Stage"] for item in plan["entities"] if item["desired"]]
    members = [
        {
            "identity": item["desired"]["identity"],
            "entity_digest": item["desired"]["receipt"]["entity_digest"],
        }
        for item in plan["entities"]
        if item["desired"]
    ]
    sprint_members: dict[str, list[str]] = {}
    goal_digests: set[str] = set()
    exit_digests: set[str] = set()
    for item in plan["entities"]:
        metadata = item.get("source_metadata") or {}
        sprint_identity = metadata.get("sprint_identity")
        if isinstance(sprint_identity, str) and item.get("desired"):
            sprint_members.setdefault(sprint_identity, []).append(item["desired"]["identity"])
        if isinstance(metadata.get("goal_digest"), str):
            goal_digests.add(metadata["goal_digest"])
        if isinstance(metadata.get("exit_digest"), str):
            exit_digests.add(metadata["exit_digest"])
    projection_freshness = (
        freshness_status(last_success, now=observed_at, window=freshness_window)
        if observed_at is not None and freshness_window is not None
        else "MISSING"
    )
    return {
        "schema": "spacedock-status-snapshot/v1",
        "repository": plan["repository"],
        "workflow_dir": plan["workflow_dir"],
        "state_ref": plan["state_ref"],
        "trunk_commit": plan["trunk_commit"],
        "state_commit": plan["state_commit"],
        "projector_version": plan["projector_version"],
        "projector_digest": plan["projector_digest"],
        "project": (
            {
                "owner_type": project.get("owner_type"),
                "owner": project.get("owner"),
                "number": project.get("number"),
                "node_id": project.get("node_id"),
            }
            if project
            else None
        ),
        "projection_freshness": projection_freshness,
        "member_set_digest": _digest(_canonical(sorted(members, key=lambda item: item["identity"]))),
        "sprints": [
            {
                "identity": identity,
                "member_count": len(identities),
                "member_set_digest": _digest(_canonical(sorted(identities))),
            }
            for identity, identities in sorted(sprint_members.items())
        ],
        "available_goal_digests": sorted(goal_digests),
        "available_exit_digests": sorted(exit_digests),
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


def _select_entities(
    entities: list[dict[str, Any]], selection: list[str], *, scope: str
) -> list[dict[str, Any]]:
    slugs = [entity["_slug"] for entity in entities]
    duplicates = sorted(slug for slug, count in Counter(slugs).items() if count > 1)
    if duplicates:
        raise ProjectionError(f"duplicate entity slugs {duplicates!r}")
    validate_approval_scope({"scope": scope, "linked_issues": {}}, selection)
    if scope == "workflow":
        return entities
    available = {entity["_slug"]: entity for entity in entities}
    missing = sorted(set(selection) - set(available))
    if missing:
        raise ProjectionError(f"configured entity selection is missing {missing!r}")
    return [available[slug] for slug in sorted(selection)]


def reconcile(
    config: dict[str, Any],
    *,
    trunk_dir: pathlib.Path,
    state_dir: pathlib.Path,
    client: Any,
    journal: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    projector_path = pathlib.Path(__file__)
    projector_digest = _digest(projector_path.read_bytes())
    validate_config(config, installed_projector_digest=projector_digest)
    workflow_path = trunk_dir / config["workflow_dir"] / "README.md"
    workflow = parse_workflow_text(workflow_path.read_text())
    entities = _load_entities(state_dir)
    _assign_short_ids(workflow, entities)
    approval = config.get("approval") or {"scope": "workflow", "linked_issues": {}}
    selection = config.get("entity_selection") or []
    if config.get("external_apply_enabled"):
        entities = _select_entities(entities, selection, scope=approval["scope"])
    elif selection:
        entities = _select_entities(entities, selection, scope="selected")
    linked_issue_numbers = {
        entity["issue"] for entity in entities if isinstance(entity.get("issue"), int)
    }
    fields, target = observe_github(
        client, config, linked_issue_numbers=linked_issue_numbers
    )
    provenance = {
        "profile": config["profile"],
        "repository": config["repository"],
        "workflow_dir": config["workflow_dir"],
        "state_ref": config["state_ref"],
        "trunk_commit": _git_commit(trunk_dir),
        "state_commit": _git_commit(state_dir),
        "projector_version": VERSION,
        "projector_digest": projector_digest,
        "status_options": status_options_from_rest(fields),
        "linked_issue_bindings": approval.get("linked_issues") or {},
        "detect_orphans": approval.get("scope") != "selected",
    }
    plan = plan_projection(workflow, entities, target, **provenance)
    snapshot = build_status_snapshot(plan, project=config["project"])
    result: dict[str, Any] = {
        "schema": "spacedock-project-reconcile-result/v1",
        "mode": "apply" if config.get("external_apply_enabled") else "dry-run",
        "plan": plan,
        "snapshot": snapshot,
        "operations": [],
        "project_schema_plan": project_schema_plan(plan, fields),
    }
    if config.get("external_apply_enabled"):
        result["operations"] = apply_github_plan(
            client, config, plan, fields, journal=journal
        )
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
        args.output.parent.mkdir(parents=True, exist_ok=True)
        journal: list[dict[str, Any]] = []
        try:
            config = json.loads(args.config.read_text())
            client = GitHubRestClient(
                os.environ.get("SPACEDOCK_REPOSITORY_TOKEN", ""),
                os.environ.get("SPACEDOCK_PROJECT_TOKEN", ""),
            )
            result = reconcile(
                config,
                trunk_dir=args.trunk_dir,
                state_dir=args.state_dir,
                client=client,
                journal=journal,
            )
        except Exception as exc:
            failure = {
                "schema": "spacedock-project-reconcile-result/v1",
                "mode": "failed",
                "error": f"{type(exc).__name__}: {exc}",
                "operations": journal,
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
