#!/usr/bin/env python3
"""plan-lint's own admission checks for L4 (`live_item`, `delivery_binding`).

Owned by plan-flow, not kc-dev-flow: moved out of kc-dev-flow's now-removed
`linear-admission.py` so plan-lint.py carries its own logic instead of
reaching into another package's scripts directory.
"""
from __future__ import annotations

import hashlib
import os
import re
import subprocess


class AdmissionError(RuntimeError):
    """A fail-closed admission refusal safe to show without provider data."""


def section(text: str, heading: str) -> str:
    matches = list(re.finditer(rf"^## {re.escape(heading)}\s*$", text, re.MULTILINE))
    if len(matches) != 1:
        raise AdmissionError(f"planning description needs one {heading} section")
    start = matches[0].end()
    following = re.search(r"^##\s+", text[start:], re.MULTILINE)
    value = text[start : start + following.start() if following else len(text)].strip()
    if not value or re.fullmatch(r"(?:TBD|TODO|<[^>]+>)", value, re.IGNORECASE):
        raise AdmissionError(f"planning description has invalid {heading}")
    return value


def issue_identifier(source: str) -> str:
    match = re.search(r"/issue/([A-Z][A-Z0-9]*-\d+)(?:/|$)", source)
    if not match:
        raise AdmissionError("snapshot source is not a Linear issue URL")
    return match.group(1)


def live_item(issue: object) -> dict[str, object]:
    if not isinstance(issue, dict):
        raise AdmissionError("Linear issue is missing")
    for field in ("url", "description", "state"):
        if not issue.get(field):
            raise AdmissionError("Linear issue is malformed")
    project = issue.get("project")
    cycle = issue.get("cycle")
    if isinstance(project, dict):
        name, content = project.get("name"), project.get("content")
        if not isinstance(name, str) or not isinstance(content, str):
            raise AdmissionError("Linear Project is malformed")
        outcome = (
            f"Linear Project {project.get('id')} {name} sha256:"
            + hashlib.sha256(f"{name}\n{content}".encode("utf-8")).hexdigest()
        )
    else:
        outcome = "Linear Project absent"
    if isinstance(cycle, dict):
        window = f"Linear Cycle {cycle.get('id')} {cycle.get('startsAt')}/{cycle.get('endsAt')}"
    else:
        window = "Linear Cycle absent"
    description = str(issue["description"])
    non_goals = [
        line[2:].strip() for line in section(description, "Non-goals").splitlines()
        if line[:2] in {"- ", "* "}
    ]
    if not non_goals:
        raise AdmissionError("Linear issue has no complete Non-goals")
    return {
        "source": issue["url"],
        "planning-window": window,
        "planning-outcome": outcome,
        "accepted-goal": section(description, "Accepted outcome"),
        "non-goals": non_goals,
    }


def delivery_binding(issue: object, source: str, timeout: float) -> dict[str, str]:
    if not isinstance(issue, dict) or issue.get("url") != source:
        raise AdmissionError("Linear delivery source does not match the engaged item")
    identifier = issue.get("identifier")
    branch = issue.get("branchName")
    if not isinstance(identifier, str) or not re.fullmatch(r"[A-Z][A-Z0-9]*-\d+", identifier):
        raise AdmissionError("Linear delivery identifier is invalid")
    if identifier != issue_identifier(source):
        raise AdmissionError("Linear delivery identifier does not match the engaged source")
    if not isinstance(branch, str) or not branch or len(branch.encode("utf-8")) > 240:
        raise AdmissionError("Linear delivery branch is invalid")
    env = os.environ.copy()
    env.update(
        {
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_NO_REPLACE_OBJECTS": "1",
            "GIT_OPTIONAL_LOCKS": "0",
        }
    )
    try:
        checked = subprocess.run(
            ["git", "check-ref-format", "--branch", branch],
            env=env,
            capture_output=True,
            check=False,
            timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise AdmissionError("Linear delivery branch validation unavailable") from exc
    if checked.returncode != 0 or not re.search(
        rf"(?:^|[/_-]){re.escape(identifier)}(?:$|[/_-])", branch, re.IGNORECASE
    ):
        raise AdmissionError("Linear delivery branch does not bind the engaged issue")
    return {"branch": branch, "close_line": f"Fixes {identifier}"}
