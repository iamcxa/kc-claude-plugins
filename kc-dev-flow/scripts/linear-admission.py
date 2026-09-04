#!/usr/bin/env python3
"""Read one Linear admission and emit a success-only dispatch envelope."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


API_URL = "https://api.linear.app/graphql"
ACTIVE_TYPES = {"unstarted", "started"}
FIELDS = ("source", "planning-window", "planning-outcome")
ACCEPTED_GOAL_HEADING = "Accepted outcome"
LEGACY_GOAL_HEADING = "Goal"


class AdmissionError(RuntimeError):
    """A fail-closed admission refusal safe to show without provider data."""


def digest(value: object) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def git(state: Path, *args: str, timeout: float) -> bytes:
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
        result = subprocess.run(
            ["git", "-C", str(state), *args],
            env=env,
            capture_output=True,
            check=False,
            timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise AdmissionError("state repository unavailable") from exc
    if result.returncode != 0:
        raise AdmissionError("state repository unavailable")
    return result.stdout


def frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        raise AdmissionError("committed work item has no frontmatter")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise AdmissionError("committed work item has invalid frontmatter")
    values: dict[str, str] = {}
    for line in text[4:end].splitlines():
        match = re.fullmatch(r"([a-z][a-z0-9-]*):[ \t]*(.*)", line)
        if match and match.group(1) not in values:
            values[match.group(1)] = match.group(2).strip().strip("\"'").strip()
    return values


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


def accepted_goal(text: str) -> str:
    present = [
        heading
        for heading in (ACCEPTED_GOAL_HEADING, LEGACY_GOAL_HEADING)
        if re.search(rf"^## {re.escape(heading)}\s*$", text, re.MULTILINE)
    ]
    if len(present) > 1:
        raise AdmissionError(
            "planning description carries both '## Accepted outcome' and the legacy '## Goal'"
        )
    if not present:
        raise AdmissionError("planning description needs one '## Accepted outcome' section")
    return section(text, present[0])


def normalized_item(text: str) -> dict[str, object]:
    fields = frontmatter(text)
    try:
        source, window, outcome = (fields[name] for name in FIELDS)
    except (KeyError, ValueError) as exc:
        raise AdmissionError("committed snapshot is missing a Planning Receipt") from exc
    goal = section(text, "Accepted outcome")
    non_goals = [
        line[2:].strip() for line in section(text, "Non-goals").splitlines()
        if line.startswith("- ")
    ]
    if not non_goals or any(not item for item in non_goals):
        raise AdmissionError("committed snapshot Non-goals must be a '- ' bullet list")
    if not all((source, window, outcome)):
        raise AdmissionError("committed snapshot has incomplete five-field data")
    return {
        "source": source,
        "planning-window": window,
        "planning-outcome": outcome,
        "accepted-goal": goal,
        "non-goals": non_goals,
    }


class Linear:
    def __init__(self, key: str, endpoint: str, deadline: float):
        self.key = key
        self.endpoint = endpoint
        self.deadline = deadline

    def query(self, query: str, variables: dict[str, object]) -> dict[str, object]:
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            raise AdmissionError("Linear read timed out")
        request = urllib.request.Request(
            self.endpoint,
            data=json.dumps({"query": query, "variables": variables}).encode("utf-8"),
            headers={"Authorization": self.key, "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=remaining) as response:
                payload = json.load(response)
        except urllib.error.HTTPError as exc:
            if exc.code in {401, 403}:
                raise AdmissionError("Linear authentication refused") from exc
            raise AdmissionError("Linear transport refused") from exc
        except (OSError, ValueError, TimeoutError) as exc:
            raise AdmissionError("Linear read unavailable") from exc
        if not isinstance(payload, dict) or payload.get("errors") or not isinstance(payload.get("data"), dict):
            raise AdmissionError("Linear returned invalid GraphQL data")
        return payload["data"]


ISSUE_QUERY = """query AdmissionIssue($id: String!) {
  viewer { organization { id urlKey } }
  issue(id: $id) { id identifier url branchName description state { type }
    project { id name content } cycle { id startsAt endsAt } }
}"""
PROJECT_QUERY = """query AdmissionProject($id: String!) {
  project(id: $id) { id name content }
}"""
ISSUES_QUERY = """query AdmissionSet($project: ID!, $cycle: ID!, $after: String) {
  issues(first: 50, after: $after, filter: { project: { id: { eq: $project } }
    cycle: { id: { eq: $cycle } } state: { type: { in: ["unstarted", "started"] } } }) {
    nodes { id identifier url description state { type }
      project { id name content } cycle { id startsAt endsAt } }
    pageInfo { hasNextPage endCursor }
  }
}"""


def issue_identifier(source: str) -> str:
    match = re.search(r"/issue/([A-Z][A-Z0-9]*-\d+)(?:/|$)", source)
    if not match:
        raise AdmissionError("snapshot source is not a Linear issue URL")
    return match.group(1)


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
        "accepted-goal": accepted_goal(description),
        "non-goals": non_goals,
    }


def run_loader(args: argparse.Namespace, deadline: float) -> dict[str, object]:
    loader = args.profile_loader.expanduser().resolve()
    if not loader.is_file():
        raise AdmissionError("admission profile loader unavailable")
    try:
        result = subprocess.run(
            [sys.executable, str(loader), "--work-item", str(args.work_item),
             "--local-profile", str(args.local_profile), "--format", "json",
             "--validate-admission"],
            text=True, capture_output=True, timeout=max(0.01, deadline - time.monotonic())
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise AdmissionError("admission profile loader unavailable") from exc
    if result.returncode != 0:
        raise AdmissionError("admission profile contract refused")
    try:
        loaded = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise AdmissionError("admission profile loader returned invalid data") from exc
    if not loaded.get("development_brief_sha256"):
        raise AdmissionError("admission profile guard was not applied")
    return loaded


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workflow-dir", type=Path, required=True)
    parser.add_argument("--work-item", type=Path, required=True)
    parser.add_argument("--profile-loader", type=Path, required=True)
    parser.add_argument("--local-profile", type=Path, required=True)
    parser.add_argument("--linear-workspace", required=True)
    parser.add_argument("--state-revision", required=True)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--graphql-url", default=API_URL, help=argparse.SUPPRESS)
    return parser.parse_args()


def main() -> int:
    started = time.monotonic()
    try:
        args = parse_args()
        if not (0 < args.timeout <= 60):
            raise AdmissionError("timeout must be between 0 and 60 seconds")
        deadline = started + args.timeout
        key = os.environ.get("LINEAR_API_KEY", "")
        workspace_id = os.environ.get("CONDUCTOR_WORKSPACE_ID", "")
        if not key:
            raise AdmissionError("LINEAR_API_KEY is unavailable")
        if args.graphql_url != API_URL:
            host = urllib.parse.urlparse(args.graphql_url).hostname
            if not key.startswith("test-") or host not in {"127.0.0.1", "localhost"}:
                raise AdmissionError("test endpoint requires a synthetic key and loopback host")

        state = (args.workflow_dir / ".spacedock-state").resolve()
        if not state.is_dir():
            raise AdmissionError("state authority is not <workflow-dir>/.spacedock-state")
        work_item = args.work_item.resolve()
        profile_loader = args.profile_loader.expanduser().resolve()
        comparator = profile_loader.parent / "engage-reconcile.py"
        if not comparator.is_file():
            raise AdmissionError("installed planning comparator unavailable")
        if not work_item.is_relative_to(state) or not re.fullmatch(r"[0-9a-f]{40}", args.state_revision):
            raise AdmissionError("work item or state revision is not exact")
        head = git(state, "rev-parse", "HEAD", timeout=max(0.01, deadline - time.monotonic())).decode().strip()
        if head != args.state_revision or git(state, "status", "--porcelain", timeout=max(0.01, deadline - time.monotonic())).strip():
            raise AdmissionError("state checkout is dirty or not at the pinned revision")
        entries = git(
            state, "ls-tree", "-r", "-z", "--format=%(objectmode) %(path)",
            args.state_revision, timeout=max(0.01, deadline - time.monotonic())
        ).decode("utf-8").split("\0")
        modes = {entry.split(" ", 1)[1]: entry.split(" ", 1)[0] for entry in entries if " " in entry}
        relative = work_item.relative_to(state).as_posix()
        if modes.get(relative) not in {"100644", "100755"}:
            raise AdmissionError("work item is not a committed regular file")
        committed = git(
            state, "cat-file", "blob", f"{args.state_revision}:{relative}",
            timeout=max(0.01, deadline - time.monotonic())
        )
        if work_item.read_bytes() != committed:
            raise AdmissionError("work item bytes do not match the pinned revision")
        engaged = frontmatter(committed.decode("utf-8"))
        sprint = engaged.get("sprint")
        if not sprint:
            raise AdmissionError("engaged work item has no sprint")
        snapshots: list[dict[str, object]] = []
        for path, mode in modes.items():
            if mode not in {"100644", "100755"} or not path.endswith(".md"):
                continue
            raw = git(state, "cat-file", "blob", f"{args.state_revision}:{path}", timeout=max(0.01, deadline - time.monotonic()))
            try:
                text = raw.decode("utf-8")
                fields = frontmatter(text)
            except (UnicodeDecodeError, AdmissionError):
                continue
            if path.startswith("_archive/") or fields.get("status") == "done":
                continue
            if fields.get("sprint") == sprint and fields.get("sprint-readiness") == "ready":
                snapshots.append(normalized_item(text))
        if not snapshots or len({str(item["source"]) for item in snapshots}) != len(snapshots):
            raise AdmissionError("committed snapshot is missing or duplicated")
        snapshots.sort(key=lambda item: str(item["source"]))
        expected_window, expected_outcome = engaged.get("planning-window"), engaged.get("planning-outcome")
        if any(
            item["planning-window"] != expected_window or item["planning-outcome"] != expected_outcome
            for item in snapshots
        ):
            raise AdmissionError("committed snapshot mixes planning scopes")
        loader = run_loader(args, deadline)
        if loader.get("work_item_sha256") != hashlib.sha256(committed).hexdigest():
            raise AdmissionError("loader and pinned work-item hashes differ")

        cycle_match = re.fullmatch(r"Linear Cycle ([0-9a-f-]{36}) .+", str(expected_window))
        project_match = re.fullmatch(r"Linear Project ([0-9a-f-]{36}) .+ sha256:[0-9a-f]{64}", str(expected_outcome))
        if not cycle_match or not project_match:
            raise AdmissionError("Planning Receipt is not a bound Linear tuple")
        linear = Linear(key, args.graphql_url, deadline)
        engaged_live = linear.query(ISSUE_QUERY, {"id": issue_identifier(str(engaged["source"]))})
        delivery = delivery_binding(
            engaged_live.get("issue"),
            str(engaged["source"]),
            max(0.01, deadline - time.monotonic()),
        )
        viewer = engaged_live.get("viewer")
        organization = viewer.get("organization") if isinstance(viewer, dict) else None
        if not isinstance(organization, dict) or organization.get("urlKey") != args.linear_workspace:
            raise AdmissionError("Linear organization mismatch")
        project = linear.query(PROJECT_QUERY, {"id": project_match.group(1)}).get("project")
        if not isinstance(project, dict):
            raise AdmissionError("Linear Project is missing")
        cursor: str | None = None
        issues: list[dict[str, object]] = []
        seen_cursors: set[str] = set()
        while True:
            data = linear.query(
                ISSUES_QUERY,
                {"project": project_match.group(1), "cycle": cycle_match.group(1), "after": cursor},
            ).get("issues")
            if not isinstance(data, dict) or not isinstance(data.get("nodes"), list) or not isinstance(data.get("pageInfo"), dict):
                raise AdmissionError("Linear pagination is malformed")
            issues.extend(data["nodes"])
            page = data["pageInfo"]
            if not page.get("hasNextPage"):
                break
            cursor = page.get("endCursor")
            if not isinstance(cursor, str) or cursor in seen_cursors:
                raise AdmissionError("Linear pagination is incomplete")
            seen_cursors.add(cursor)
        by_url = {str(issue.get("url")): issue for issue in issues if isinstance(issue, dict)}
        for snapshot in snapshots:
            source = str(snapshot["source"])
            if source not in by_url:
                current = linear.query(ISSUE_QUERY, {"id": issue_identifier(source)}).get("issue")
                if isinstance(current, dict) and isinstance(current.get("state"), dict) and current["state"].get("type") in ACTIVE_TYPES:
                    by_url[str(current.get("url"))] = current
        current_items = sorted(
            (live_item(issue) for issue in by_url.values()),
            key=lambda item: str(item["source"]),
        )

        with tempfile.TemporaryDirectory(prefix="linear-admission-") as temporary:
            temporary_path = Path(temporary)
            snapshot_path, current_path = temporary_path / "snapshot.json", temporary_path / "current.json"
            snapshot_path.write_text(json.dumps(snapshots), encoding="utf-8")
            current_path.write_text(json.dumps(current_items), encoding="utf-8")
            try:
                compared = subprocess.run(
                    [sys.executable, str(comparator), "--snapshot", str(snapshot_path),
                     "--current", str(current_path), "--expected-source", str(engaged["source"]),
                     "--expected-window", str(expected_window), "--expected-outcome", str(expected_outcome)],
                    text=True, capture_output=True, timeout=max(0.01, deadline - time.monotonic())
                )
            except (OSError, subprocess.TimeoutExpired) as exc:
                raise AdmissionError("planning comparator unavailable") from exc
        try:
            reconciliation = json.loads(compared.stdout)
        except json.JSONDecodeError as exc:
            raise AdmissionError("planning comparator returned invalid output") from exc
        empty = all(reconciliation.get(name) == [] for name in ("added", "removed", "changed", "moved"))
        if compared.returncode != 0 or reconciliation.get("status") != "clean" or not empty:
            classified = {
                name: reconciliation.get(name)
                for name in ("added", "removed", "changed", "moved", "status")
            }
            raise AdmissionError(
                "planning reconcile stopped: "
                + json.dumps(classified, sort_keys=True, separators=(",", ":"))
            )
        final_head = git(
            state, "rev-parse", "HEAD", timeout=max(0.01, deadline - time.monotonic())
        ).decode().strip()
        final_status = git(
            state, "status", "--porcelain", timeout=max(0.01, deadline - time.monotonic())
        ).strip()
        if final_head != args.state_revision or final_status or work_item.read_bytes() != committed:
            raise AdmissionError("state or work-item revision changed during admission")
        contract_hashes = [
            {"path": item["path"], "sha256": item["sha256"]}
            for item in loader.get("loaded", []) if isinstance(item, dict)
        ]
        envelope = {
            "schema": "kc-dev-flow-dispatch-envelope/v1",
            "linear_organization": organization["urlKey"],
            "delivery": delivery,
            "work_item_sha256": hashlib.sha256(committed).hexdigest(),
            "state_revision": args.state_revision,
            "snapshot_sha256": digest(snapshots),
            "live_read_sha256": digest(current_items),
            "reconcile": reconciliation,
            "development_brief_sha256": loader["development_brief_sha256"],
            "plugin_version": loader["plugin_version"],
            "contract_digest": loader["contract_digest"],
            "local_profile_interface": loader["local_profile_interface"],
            "profile_contract_hashes": contract_hashes,
            "command_elapsed_ms": round((time.monotonic() - started) * 1000),
        }
        if workspace_id:
            envelope["conductor_workspace_id"] = workspace_id
        sys.stdout.write(json.dumps(envelope, sort_keys=True, separators=(",", ":")) + "\n")
        return 0
    except AdmissionError as exc:
        print(f"linear admission: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"linear admission: unexpected refusal ({type(exc).__name__})", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
