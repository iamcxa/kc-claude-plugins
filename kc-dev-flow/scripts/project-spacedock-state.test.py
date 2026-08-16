#!/usr/bin/env python3
"""Contract tests for the vendored Spacedock-to-GitHub projector."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import pathlib
import tempfile
import types
import unittest
import urllib.error
from datetime import datetime, timezone
from unittest import mock


ROOT = pathlib.Path(__file__).resolve().parents[1]
PROJECTOR = (
    ROOT
    / "skills"
    / "setup-github-project-projection"
    / "assets"
    / "project-spacedock-state.py"
)

spec = importlib.util.spec_from_file_location("project_spacedock_state", PROJECTOR)
assert spec and spec.loader
projector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(projector)

INSTALLER = (
    ROOT
    / "skills"
    / "setup-github-project-projection"
    / "assets"
    / "install-projection.py"
)
installer_spec = importlib.util.spec_from_file_location("install_projection", INSTALLER)
assert installer_spec and installer_spec.loader
installer = importlib.util.module_from_spec(installer_spec)
installer_spec.loader.exec_module(installer)


WORKFLOW = """---
commissioned-by: spacedock@0.26.0
entity-type: task
id-style: slug
state: .spacedock-state
trunk: main
stages:
  states:
    - name: inbox
      initial: true
    - name: building
    - name: checking
    - name: released
      terminal: true
---
# Fixture workflow
"""


def entity(title: str, status: str, **fields: object) -> str:
    frontmatter = [
        "---",
        "id:",
        f"title: {title}",
        f"status: {status}",
        "score:",
        "source: fixture",
        "worktree:",
    ]
    frontmatter.extend(f"{key}: {value}" for key, value in fields.items())
    frontmatter.extend(["---", "", "Fixture body."])
    return "\n".join(frontmatter)


def entity_with_id(
    title: str, status: str, stored_id: str, *, body: str = "Fixture body."
) -> str:
    return "\n".join(
        (
            "---",
            f"id: {stored_id}",
            f"title: {title}",
            f"status: {status}",
            "score:",
            "source: fixture",
            "worktree:",
            "---",
            "",
            body,
        )
    )


def apply_fake(plan: dict[str, object], target_items: list[dict[str, object]]):
    """Apply a plan to an in-memory target without shipping test code."""

    result = copy.deepcopy(target_items)
    next_issue = max((item.get("issue_number", 0) or 0 for item in result), default=0) + 1
    for mutation in plan["mutations"]:
        desired = mutation["desired"]
        if mutation["action"] == "CREATE":
            issue_number = desired.get("issue_number")
            if desired.get("content_type") == "Issue" and not isinstance(issue_number, int):
                issue_number = next_issue
                next_issue += 1
            result.append(
                {
                    "item_id": len(result) + 1,
                    "content_type": desired["content_type"],
                    "content_node_id": f"DI-FAKE-{len(result) + 1}",
                    "issue_number": issue_number,
                    "issue_id": None,
                    "repository": None,
                    "title": desired["title"],
                    "issue_state": desired.get("issue_state"),
                    "body": desired["body"],
                    "fields": copy.deepcopy(desired["fields"]),
                    "labels": copy.deepcopy(desired.get("labels", [])),
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
                if mutation.get("ownership") == "linked":
                    item["fields"] = copy.deepcopy(desired["fields"])
                    if item.get("item_id") is None:
                        item["item_id"] = f"FAKE-LINKED-{item.get('issue_number')}"
                else:
                    item.update(
                        {
                            "content_type": desired["content_type"],
                            "title": desired["title"],
                            "issue_state": desired.get("issue_state"),
                            "body": desired["body"],
                            "fields": copy.deepcopy(desired["fields"]),
                            "labels": copy.deepcopy(desired.get("labels", [])),
                        }
                    )
                matched = True
                break
        if not matched:
            raise projector.ProjectionError(
                f"fake target lost update identity {mutation['identity']!r}"
            )
    return result


class NoWriteClient:
    def __init__(self) -> None:
        self.calls: list[object] = []

    def request(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        raise AssertionError("preflight refusal must happen before a write")

    graphql = request


class ProjectorContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.workflow = projector.parse_workflow_text(WORKFLOW)
        self.provenance = {
            "repository": "example/repo",
            "workflow_dir": "docs/dev",
            "state_ref": "spacedock-state/dev",
            "trunk_commit": "a" * 40,
            "state_commit": "b" * 40,
            "projector_version": "0.1.0",
            "projector_digest": hashlib.sha256(PROJECTOR.read_bytes()).hexdigest(),
            "status_options": ["Todo", "In Progress", "Done"],
        }

    def binding(self, slug: str, number: int) -> dict[str, str]:
        return {slug: f"example/repo#{number}"}

    def plan(self, tasks, current=(), *, workflow=None, **provenance):
        return projector.plan_projection(
            workflow or self.workflow,
            tasks,
            list(current),
            profile="generic",
            **{**self.provenance, **provenance},
        )

    def projected(self, task, **provenance):
        return apply_fake(self.plan([task], **provenance), [])[0]

    def fields(
        self,
        *,
        stages: tuple[str, ...] = ("building",),
        statuses: tuple[str, ...] = ("In Progress",),
        products: tuple[str, ...] = (),
    ) -> list[dict[str, object]]:
        fields = [
            {
                "id": 10,
                "name": "Status",
                "data_type": "single_select",
                "options": [
                    {
                        "id": {
                            "In Progress": "progress",
                            "Todo": "todo",
                            "Backlog": "backlog",
                            "Done": "done",
                        }.get(value, value.lower().replace(" ", "-")),
                        "name": {"raw": value},
                    }
                    for value in statuses
                ],
            },
            {
                "id": 11,
                "name": "SD Stage",
                "data_type": "single_select",
                "options": [
                    {"id": value, "name": {"raw": value}} for value in stages
                ],
            },
            {"id": 12, "name": "SD Identity", "data_type": "text"},
        ]
        if products:
            fields.append({
                "id": 13,
                "name": "SD Product",
                "data_type": "single_select",
                "options": [
                    {"id": value, "name": {"raw": value}} for value in products
                ],
            })
        return fields

    def apply_config(self, cap: int = 10) -> dict[str, object]:
        return {
            "repository": "example/repo",
            "approval": {"max_mutations_per_run": cap},
            "project": {
                "owner_type": "user",
                "owner": "example",
                "number": 1,
                "node_id": "PVT_example",
            },
        }

    def assert_apply_refuses(self, pattern, plan, fields, config=None):
        client = NoWriteClient()
        with self.assertRaisesRegex(projector.ProjectionError, pattern):
            projector.apply_github_plan(
                client, config or self.apply_config(), plan, fields
            )
        self.assertEqual([], client.calls)

    def test_dynamic_stages_and_missing_kc_fields_remain_projectable(self) -> None:
        task = projector.parse_entity_text(
            entity("Portable task", "building"), slug="portable-task"
        )

        generic = projector.plan_projection(
            self.workflow, [task], [], profile="generic", **self.provenance
        )
        kc = projector.plan_projection(
            self.workflow, [task], [], profile="kc-dev-flow", **self.provenance
        )

        self.assertEqual(["inbox", "building", "checking", "released"], self.workflow["stages"])
        self.assertEqual("CREATE", generic["entities"][0]["classification"])
        self.assertEqual("building", generic["entities"][0]["desired"]["fields"]["SD Stage"])
        self.assertEqual("In Progress", generic["entities"][0]["desired"]["fields"]["Status"])
        self.assertEqual("PARTIAL", kc["entities"][0]["classification"])
        self.assertNotIn("SD Product", kc["entities"][0]["desired"]["fields"])
        self.assertEqual(["product", "sprint"], kc["entities"][0]["missing_optional"])
        self.assertEqual(
            "Todo",
            projector._generic_status(
                self.workflow, self.workflow["initial_stage"], ["Backlog", "Todo"]
            ),
        )

        without_options = projector.plan_projection(
            self.workflow,
            [task],
            [],
            profile="generic",
            **{key: value for key, value in self.provenance.items() if key != "status_options"},
        )
        self.assertNotIn("Status", without_options["entities"][0]["desired"]["fields"])

    def test_create_apply_and_identical_rerun_converge_to_no_change(self) -> None:
        task = projector.parse_entity_text(entity("One", "building"), slug="one")
        first = projector.plan_projection(
            self.workflow, [task], [], profile="generic", **self.provenance
        )
        applied = apply_fake(first, [])
        applied[0]["fields"]["Human field"] = "preserve me"
        second = projector.plan_projection(
            self.workflow, [task], applied, profile="generic", **self.provenance
        )

        self.assertEqual("CREATE", first["entities"][0]["classification"])
        self.assertEqual("DraftIssue", first["entities"][0]["desired"]["content_type"])
        self.assertIsNone(first["entities"][0]["desired"]["issue_number"])
        self.assertEqual("NO_CHANGE", second["entities"][0]["classification"])
        self.assertEqual([], second["mutations"])
        receipt = projector.parse_receipt(applied[0]["body"])
        self.assertEqual("spacedock-projection-receipt/v2", receipt["schema"])
        self.assertEqual("example/repo:docs/dev:one", receipt["identity"])
        self.assertEqual(self.provenance["projector_digest"], receipt["projector_digest"])
        self.assertEqual("[one] One", applied[0]["title"])
        self.assertTrue(applied[0]["body"].startswith("Fixture body.\n\n<!-- spacedock-projection:v1"))
        self.assertNotIn("This Issue is a read-only projection from Spacedock.", applied[0]["body"])
        self.assertNotIn("worktree", applied[0]["body"])
        self.assertEqual("example/repo:docs/dev:one", applied[0]["fields"]["SD Identity"])
        self.assertEqual("DraftIssue", applied[0]["content_type"])
        self.assertEqual([], applied[0]["labels"])

        moved_refs = {
            **self.provenance,
            "trunk_commit": "c" * 40,
            "state_commit": "d" * 40,
        }
        across_unrelated_commits = projector.plan_projection(
            self.workflow, [task], applied, profile="generic", **moved_refs
        )
        self.assertEqual("NO_CHANGE", across_unrelated_commits["entities"][0]["classification"])
        self.assertEqual([], across_unrelated_commits["mutations"])

        changed_projector = projector.plan_projection(
            self.workflow,
            [task],
            applied,
            profile="generic",
            **{**moved_refs, "projector_digest": "e" * 64},
        )
        self.assertEqual("UPDATE", changed_projector["entities"][0]["classification"])

    def test_sd_b32_title_uses_shortest_unique_prefix_from_whole_population(self) -> None:
        workflow = projector.parse_workflow_text(WORKFLOW.replace("id-style: slug", "id-style: sd-b32"))
        tasks = [
            projector.parse_entity_text(entity_with_id(title, "building", stored_id), slug=slug)
            for title, stored_id, slug in (
                ("Alpha", "ab0000000000000000000000", "alpha"),
                ("Beta", "ab1000000000000000000000", "beta"),
                ("Gamma", "cd0000000000000000000000", "gamma"),
            )
        ]
        plan = self.plan(tasks, workflow=workflow)
        titles = {item["slug"]: item["desired"]["title"] for item in plan["entities"]}
        self.assertEqual(
            {"alpha": "[ab0] Alpha", "beta": "[ab1] Beta", "gamma": "[cd] Gamma"},
            titles,
        )

        projector._assign_short_ids(workflow, tasks)
        selected = self.plan([tasks[0]], workflow=workflow)
        self.assertEqual("[ab0] Alpha", selected["entities"][0]["desired"]["title"])

    def test_entity_body_is_normalized_markdown_and_converges(self) -> None:
        source = entity_with_id("Body", "building", "body-id", body="# Context\n\nDetails")
        lf = projector.parse_entity_text(source, slug="body")
        lf_plan = self.plan([lf])
        crlf_plan = self.plan(
            [projector.parse_entity_text(source.replace("\n", "\r\n"), slug="body")]
        )
        self.assertTrue(lf_plan["entities"][0]["desired"]["body"].startswith("# Context\n\nDetails\n"))
        self.assertEqual(
            projector._body_without_receipt(lf_plan["entities"][0]["desired"]["body"]),
            projector._body_without_receipt(crlf_plan["entities"][0]["desired"]["body"]),
        )

        observed = apply_fake(lf_plan, [])[0]
        observed["body"] = projector._body_with_receipt(
            "# Context\r\n\r\nDetails\r\n",
            lf_plan["entities"][0]["desired"]["receipt"],
        )
        round_trip = self.plan([lf], [observed])
        self.assertEqual("NO_CHANGE", round_trip["entities"][0]["classification"])
        self.assertEqual([], round_trip["mutations"])

        hard_break = projector.parse_entity_text(
            entity_with_id("Hard break", "building", "hard-break-id", body="Hard break  "),
            slug="hard-break",
        )
        hard_break_plan = self.plan([hard_break])
        hard_break_rerun = self.plan([hard_break], apply_fake(hard_break_plan, []))
        self.assertEqual("NO_CHANGE", hard_break_rerun["entities"][0]["classification"])
        self.assertEqual([], hard_break_rerun["mutations"])

    def test_v2_identity_refuses_missing_receipt_but_resumes_missing_field(self) -> None:
        task = projector.parse_entity_text(entity("One", "building"), slug="one")
        baseline = self.projected(task)

        missing_receipt = copy.deepcopy(baseline)
        missing_receipt["body"] = "Fixture body.\n"
        repair = self.plan([task], [missing_receipt])
        self.assertEqual("CONFLICT", repair["entities"][0]["classification"])
        self.assertEqual("missing_receipt_anchor", repair["entities"][0]["reason"])
        self.assertEqual([], repair["mutations"])

        missing_field = copy.deepcopy(baseline)
        missing_field["fields"].pop("SD Identity")
        resume = self.plan([task], [missing_field])
        self.assertEqual("UPDATE", resume["entities"][0]["classification"])
        self.assertTrue(resume["mutations"][0]["field_update_required"])

        disagreement = copy.deepcopy(baseline)
        disagreement["fields"]["SD Identity"] = "example/repo:docs/dev:other"
        conflict = self.plan([task], [disagreement])
        self.assertEqual("CONFLICT", conflict["entities"][0]["classification"])
        self.assertEqual("identity_anchor_mismatch", conflict["entities"][0]["reason"])
        self.assertEqual([], conflict["mutations"])

        duplicate = copy.deepcopy(baseline)
        duplicate["item_id"] = "FAKE-duplicate"
        duplicate["issue_number"] = 99
        duplicate_plan = self.plan([task], [baseline, duplicate])
        self.assertEqual("CONFLICT", duplicate_plan["entities"][0]["classification"])
        self.assertEqual("duplicate_identity_anchor", duplicate_plan["entities"][0]["reason"])
        self.assertEqual([], duplicate_plan["mutations"])

    def test_non_draft_identity_blocks_duplicate_create(self) -> None:
        """Catch a stale non-Draft identity being reused as a new Draft."""

        task = projector.parse_entity_text(entity("One", "building"), slug="one")
        stale = self.projected(task)
        stale.update(
            {
                "content_type": "Issue",
                "repository": "example/repo",
                "issue_number": 229,
                "issue_id": 31,
                "issue_identity": "example/repo#229",
            }
        )

        plan = self.plan([task], [stale])

        self.assertEqual("CONFLICT", plan["entities"][0]["classification"])
        self.assertEqual("non_draft_identity", plan["entities"][0]["reason"])
        self.assertEqual([], plan["mutations"])

    def test_missing_project_field_refuses_before_first_write(self) -> None:
        task = projector.parse_entity_text(entity("One", "building"), slug="one")
        plan = self.plan([task])
        fields = self.fields()
        fields.pop()
        self.assert_apply_refuses("SD Identity.*missing", plan, fields)

    def test_missing_explicit_issue_is_a_conflict_before_mutation(self) -> None:
        task = projector.parse_entity_text(
            entity("Missing", "building", issue=404), slug="missing"
        )
        plan = projector.plan_projection(
            self.workflow,
            [task],
            [],
            profile="generic",
            linked_issue_bindings=self.binding("missing", 404),
            **self.provenance,
        )

        self.assertEqual("CONFLICT", plan["entities"][0]["classification"])
        self.assertEqual("missing_linked_issue", plan["entities"][0]["reason"])
        self.assertEqual([], plan["mutations"])

    def test_explicit_human_issue_preserves_title_body_and_state(self) -> None:
        task = projector.parse_entity_text(
            entity("SD title", "building", issue='"22"'), slug="linked"
        )
        target = projector.merge_linked_issues(
            [],
            [
                {
                    "id": 31,
                    "number": 22,
                    "title": "Human title",
                    "state": "closed",
                    "body": "Human body",
                }
            ],
            repository="example/repo",
        )
        plan = projector.plan_projection(
            self.workflow,
            [task],
            target,
            profile="generic",
            linked_issue_bindings=self.binding("linked", 22),
            **self.provenance,
        )
        desired = plan["entities"][0]["desired"]

        self.assertEqual(22, task["issue"])
        self.assertEqual("Human title", desired["title"])
        self.assertEqual("CLOSED", desired["issue_state"])
        self.assertEqual("Human body", desired["body"])
        self.assertEqual("linked", desired["receipt"]["ownership"])

    def test_duplicate_explicit_issue_references_fail_closed(self) -> None:
        tasks = [
            projector.parse_entity_text(entity("One", "building", issue=22), slug="one"),
            projector.parse_entity_text(entity("Two", "building", issue='"22"'), slug="two"),
        ]

        with self.assertRaisesRegex(projector.ProjectionError, "duplicate entity Issue"):
            projector.plan_projection(
                self.workflow,
                tasks,
                [],
                profile="generic",
                linked_issue_bindings={
                    "one": "example/repo#22",
                    "two": "example/repo#22",
                },
                **self.provenance,
            )

    def test_archive_completes_draft_preserves_linked_and_ignores_foreign(self) -> None:
        owned = projector.parse_entity_text(
            entity("Owned", "released"), slug="owned", archived=True
        )
        linked = projector.parse_entity_text(
            entity("Linked", "released", issue=22), slug="linked", archived=True
        )
        baseline_entities = [
            projector.parse_entity_text(entity("Owned", "building"), slug="owned"),
            projector.parse_entity_text(entity("Linked", "building", issue=22), slug="linked"),
        ]
        linked_target = projector.merge_linked_issues(
            [],
            [{"id": 31, "number": 22, "title": "Linked", "state": "open", "body": ""}],
            repository="example/repo",
        )
        baseline_plan = projector.plan_projection(
            self.workflow,
            baseline_entities,
            linked_target,
            profile="generic",
            linked_issue_bindings=self.binding("linked", 22),
            **self.provenance,
        )
        target = apply_fake(baseline_plan, linked_target)
        target.append(
            {
                "item_id": "FOREIGN",
                "issue_number": 99,
                "title": "Owned",
                "issue_state": "OPEN",
                "body": "human item without receipt",
                "fields": {"SD Stage": "building"},
            }
        )
        before_foreign = copy.deepcopy(target[-1])

        archive_plan = projector.plan_projection(
            self.workflow,
            [owned, linked],
            target,
            profile="generic",
            linked_issue_bindings=self.binding("linked", 22),
            **self.provenance,
        )
        applied = apply_fake(archive_plan, target)
        by_slug = {
            projector.parse_receipt(item["body"])["slug"]: item
            for item in applied
            if projector.parse_receipt(item["body"])
        }

        self.assertEqual("DraftIssue", by_slug["owned"]["content_type"])
        self.assertEqual("Done", by_slug["owned"]["fields"]["Status"])
        self.assertEqual(
            "OPEN",
            next(item for item in applied if item["issue_number"] == 22)["issue_state"],
        )
        self.assertTrue(projector.parse_receipt(by_slug["owned"]["body"])["archived"])
        self.assertEqual(before_foreign, applied[-1])

        no_op = projector.plan_projection(
            self.workflow,
            [owned, linked],
            applied,
            profile="generic",
            linked_issue_bindings=self.binding("linked", 22),
            **self.provenance,
        )
        self.assertEqual([], no_op["mutations"])

    def test_missing_tombstone_is_conflict_without_mutation(self) -> None:
        task = projector.parse_entity_text(entity("Gone", "building"), slug="gone")
        baseline = apply_fake(
            projector.plan_projection(
                self.workflow, [task], [], profile="generic", **self.provenance
            ),
            [],
        )

        missing = projector.plan_projection(
            self.workflow, [], baseline, profile="generic", **self.provenance
        )

        self.assertEqual("CONFLICT", missing["orphans"][0]["classification"])
        self.assertEqual("missing_archive_tombstone", missing["orphans"][0]["reason"])
        self.assertEqual([], missing["mutations"])

    def test_rest_observation_uses_numeric_field_ids_not_cli_display_keys(self) -> None:
        fields = [
            {
                "id": 10,
                "name": "Status",
                "data_type": "single_select",
                "options": [
                    {"id": "todo", "name": {"raw": "Todo"}},
                    {"id": "done", "name": {"raw": "Done"}},
                ],
            },
            {"id": 11, "name": "SD Stage", "data_type": "single_select"},
        ]
        items = [
            {
                "id": 21,
                "node_id": "PVTI_fixture",
                "content": {
                    "id": 31,
                    "number": 1,
                    "title": "Observed",
                    "state": "open",
                    "body": "human body",
                    "repository_url": "https://api.github.com/repos/example/repo",
                },
                "fields": [
                    {"id": 10, "value": {"id": "todo", "name": {"raw": "Todo"}}},
                    {"id": 11, "value": {"id": "inbox", "name": {"raw": "inbox"}}},
                ],
            }
        ]

        observed = projector.target_items_from_rest(fields, items)

        self.assertEqual(["Todo", "Done"], projector.status_options_from_rest(fields))
        self.assertEqual(21, observed[0]["item_id"])
        self.assertEqual("OPEN", observed[0]["issue_state"])
        self.assertEqual({"Status": "Todo", "SD Stage": "inbox"}, observed[0]["fields"])

    def test_rest_observation_normalizes_draft_content_for_stable_updates(self) -> None:
        """Catch dropping DraftIssue items or losing the node ID needed for updates."""

        fields = [{"id": 12, "name": "SD Identity", "data_type": "text"}]
        items = [
            {
                "id": 21,
                "node_id": "PVTI_fixture",
                "content_type": "DraftIssue",
                "content": {
                    "id": 31,
                    "node_id": "DI_fixture",
                    "title": "[one] One",
                    "body": "Fixture body.",
                },
                "fields": [
                    {"id": 12, "value": {"raw": "example/repo:docs/dev:one"}}
                ],
            }
        ]

        observed = projector.target_items_from_rest(fields, items)

        self.assertEqual(1, len(observed))
        self.assertEqual("DraftIssue", observed[0]["content_type"])
        self.assertEqual("DI_fixture", observed[0]["content_node_id"])
        self.assertIsNone(observed[0]["issue_number"])
        self.assertEqual("[one] One", observed[0]["title"])
        self.assertEqual(
            "example/repo:docs/dev:one", observed[0]["fields"]["SD Identity"]
        )

    def test_observation_fetches_only_explicit_linked_issues(self) -> None:
        """Catch steady-state reconcile rediscovering removed legacy Issues."""

        class Client:
            def __init__(self) -> None:
                self.paths: list[str] = []

            def request(self, method, path, *, authority, body=None):
                self.paths.append(path)
                if path == "repos/example/repo":
                    return {}
                if path == "users/example/projectsV2/1":
                    return {"value": {"node_id": "PVT_example"}}
                if path == "repos/example/repo/issues/7":
                    return {
                        "id": 70,
                        "number": 7,
                        "title": "Human issue",
                        "state": "open",
                        "body": "Human body",
                        "labels": [],
                        "user": {"login": "human"},
                    }
                raise AssertionError(f"unexpected request {path}")

            def request_all(self, path, *, authority):
                self.paths.append(path)
                if path.endswith("/fields"):
                    return []
                if "/items" in path:
                    return []
                raise AssertionError(f"unexpected collection request {path}")

        client = Client()
        _, items = projector.observe_github(
            client,
            {
                "repository": "example/repo",
                "workflow_dir": "docs/dev",
                "project": {
                    "owner_type": "user",
                    "owner": "example",
                    "number": 1,
                    "node_id": "PVT_example",
                },
            },
            linked_issue_numbers={7},
        )

        self.assertEqual([7], [item["issue_number"] for item in items])
        self.assertNotIn(
            "repos/example/repo/issues?state=all&per_page=100", client.paths
        )

    def test_apply_creates_a_draft_and_sets_fields_without_issue_writes(self) -> None:
        """Catch routing default projection through repository Issue mutation."""

        task = projector.parse_entity_text(entity("One", "building"), slug="one")
        plan = self.plan([task])
        fields = self.fields()

        class Client:
            def __init__(self) -> None:
                self.calls: list[tuple[str, str, str, object]] = []

            def request(self, method, path, *, authority, body=None):
                self.calls.append((method, path, authority, body))
                if method == "GET" and "/labels?" in path:
                    return [{"name": "spacedock:managed"}]
                if method == "POST" and path.endswith("/issues"):
                    return {"id": 31, "number": 7}
                if method == "POST" and path.endswith("/items"):
                    return {"value": {"id": 21}}
                return {}

            def graphql(self, query, variables, *, authority):
                self.calls.append(("GRAPHQL", "addProjectV2DraftIssue", authority, variables))
                return {
                    "addProjectV2DraftIssue": {
                        "projectItem": {
                            "id": "PVTI_fixture",
                            "fullDatabaseId": "21",
                            "content": {"id": "DI_fixture"},
                        }
                    }
                }

        client = Client()
        operations = projector.apply_github_plan(
            client,
            self.apply_config(4),
            plan,
            fields,
        )

        self.assertEqual(
            ["CREATE_DRAFT", "UPDATE_FIELDS"],
            [operation["action"] for operation in operations],
        )
        self.assertFalse(any(authority == "repository" for _, _, authority, _ in client.calls))
        self.assertEqual("PVT_example", client.calls[0][3]["projectId"])
        self.assertEqual("[one] One", client.calls[0][3]["title"])
        self.assertIn("Fixture body.", client.calls[0][3]["body"])
        self.assertEqual("users/example/projectsV2/1/items/21", client.calls[1][1])

    def test_apply_updates_existing_draft_content_in_place(self) -> None:
        """Catch leaving stale Draft prose or replacing the Project item identity."""

        task = projector.parse_entity_text(entity("One", "building"), slug="one")
        current = apply_fake(self.plan([task]), [])[0]
        current.update(
            {
                "content_type": "DraftIssue",
                "content_node_id": "DI_fixture",
                "issue_number": None,
                "issue_id": None,
                "repository": None,
                "title": "Stale title",
            }
        )
        current["body"] = current["body"].replace("Fixture body.", "Human edit.")
        plan = self.plan([task], [current])
        fields = self.fields()

        class Client:
            def __init__(self) -> None:
                self.calls = []

            def request(self, method, path, *, authority, body=None):
                self.calls.append((method, path, authority, body))
                return {}

            def graphql(self, query, variables, *, authority):
                self.calls.append(("GRAPHQL", "updateProjectV2DraftIssue", authority, variables))
                return {"updateProjectV2DraftIssue": {"draftIssue": {"id": "DI_fixture"}}}

        client = Client()
        operations = projector.apply_github_plan(
            client,
            self.apply_config(1),
            plan,
            fields,
        )

        self.assertEqual(["UPDATE_DRAFT"], [item["action"] for item in operations])
        self.assertEqual("DI_fixture", client.calls[0][3]["draftIssueId"])
        self.assertEqual("[one] One", client.calls[0][3]["title"])
        self.assertIn("Fixture body.", client.calls[0][3]["body"])
        self.assertNotIn("Human edit.", client.calls[0][3]["body"])
        self.assertFalse(any(authority == "repository" for _, _, authority, _ in client.calls))

    def test_existing_single_select_missing_an_option_refuses_before_write(self) -> None:
        task = projector.parse_entity_text(entity("One", "building"), slug="one")
        plan = projector.plan_projection(
            self.workflow, [task], [], profile="generic", **self.provenance
        )
        fields = [
            {
                "id": 10,
                "node_id": "PVTF_status",
                "name": "Status",
                "data_type": "single_select",
                "options": [{"id": "progress", "name": {"raw": "In Progress"}}],
            },
            {
                "id": 11,
                "node_id": "PVTF_stage",
                "name": "SD Stage",
                "data_type": "single_select",
                "options": [
                    {
                        "id": "inbox",
                        "name": {"raw": "inbox"},
                        "color": "BLUE",
                        "description": {"raw": "human description"},
                    }
                ],
            },
            {"id": 12, "name": "SD Identity", "data_type": "text"},
        ]

        self.assert_apply_refuses("lacks options", plan, fields)

    def test_partial_draft_resumes_with_field_update_only(self) -> None:
        task = projector.parse_entity_text(entity("One", "building"), slug="one")
        target = apply_fake(self.plan([task]), [])
        target[0]["fields"].pop("SD Identity")
        plan = projector.plan_projection(
            self.workflow, [task], target, profile="generic", **self.provenance
        )
        mutation = plan["mutations"][0]

        self.assertEqual(target[0]["item_id"], mutation["current_item_id"])
        self.assertFalse(mutation["content_update_required"])
        self.assertTrue(mutation["field_update_required"])

        class ResumeClient:
            def __init__(self) -> None:
                self.calls = []

            def request(self, method, path, *, authority, body=None):
                self.calls.append((method, path, authority))
                return {}

            def graphql(self, *args, **kwargs):
                raise AssertionError("unchanged Draft content must not be rewritten")

        fields = self.fields()
        client = ResumeClient()
        operations = projector.apply_github_plan(
            client,
            self.apply_config(),
            plan,
            fields,
        )
        self.assertEqual(["UPDATE_FIELDS"], [item["action"] for item in operations])
        self.assertTrue(all(authority == "project" for _, _, authority in client.calls))

    def test_external_user_project_apply_requires_classic_pat_receipt(self) -> None:
        config = {
            "schema": "spacedock-project-config/v1",
            "repository": "example/repo",
            "trunk_ref": "main",
            "state_ref": "spacedock-state/dev",
            "workflow_dir": "docs/dev",
            "profile": "generic",
            "external_apply_enabled": True,
            "credential": {
                "token_type": "fine-grained-pat",
                "permissions": "Projects write",
                "expiry": "2026-09-01",
                "rotation_owner": "example",
                "fallback_blast_radius": "repository secret",
            },
            "project": {
                "owner_type": "user",
                "owner": "example",
                "number": 1,
                "node_id": "PVT_example",
            },
        }

        with self.assertRaisesRegex(projector.ProjectionError, "requires classic-pat"):
            projector.validate_config(config)

    def test_entity_loader_skips_docs_and_recognizes_nested_archive(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            state = pathlib.Path(directory)
            (state / "README.md").write_text("# State documentation\n")
            archive = state / "product" / "_archive"
            archive.mkdir(parents=True)
            (archive / "old.md").write_text(entity("Old", "released"))

            loaded = projector._load_entities(state)

        self.assertEqual(1, len(loaded))
        self.assertEqual("old", loaded[0]["_slug"])
        self.assertTrue(loaded[0]["_archived"])

    def test_installer_is_dry_run_first_and_audits_exact_vendored_bytes(self) -> None:
        args = types.SimpleNamespace(
            repository="example/repo",
            trunk_ref="main",
            state_ref="spacedock-state/dev",
            workflow_dir="docs/dev",
            profile="generic",
            entity=[],
            project_owner_type="user",
            project_owner="example",
            project_number=1,
            project_id="PVT_example",
            project_secret_name="SPACEDOCK_PROJECT_TOKEN",
            project_token_type="unresolved",
            project_token_permissions=None,
            credential_expiry=None,
            rotation_owner=None,
            fallback_blast_radius=None,
            schedule_interval_minutes=15,
            enable_external_apply=False,
        )
        config = installer.build_config(args)
        with tempfile.TemporaryDirectory() as directory:
            target = pathlib.Path(directory)
            planned = installer.installation_plan(target, config)
            self.assertEqual({"CREATE"}, {item["action"] for item in planned["files"]})
            self.assertEqual([], planned["external_mutations"])
            self.assertFalse((target / ".github").exists())

            installer.write_installation(target, config)
            audit = installer.audit_installation(target, config)
            self.assertTrue(audit["clean"])
            workflow = (target / ".github/workflows/spacedock-project-sync.yml").read_text()
            self.assertIn("workflow_dispatch:", workflow)
            self.assertIn('cron: "*/15 * * * *"', workflow)
            self.assertIn("cancel-in-progress: false", workflow)
            self.assertEqual(2, workflow.count("actions/checkout@3d3c42e5"))
            self.assertIn("actions/upload-artifact@043fb46d", workflow)
            self.assertNotIn("push:", workflow)
            self.assertNotIn("PVT_example", workflow)

            script = target / ".github/scripts/project-spacedock-state.py"
            self.assertEqual(PROJECTOR.read_bytes(), script.read_bytes())
            script.write_text(script.read_text() + "# drift\n")
            drifted = installer.audit_installation(target, config)
            by_path = {item["path"]: item for item in drifted["files"]}
            self.assertFalse(drifted["clean"])
            self.assertEqual("UPDATE", by_path[".github/scripts/project-spacedock-state.py"]["action"])

    def test_full_repository_identity_prevents_cross_repo_issue_collision(self) -> None:
        fields: list[dict[str, object]] = []
        items = [
            {
                "id": 1,
                "content": {
                    "id": 101,
                    "number": 22,
                    "title": "Foreign",
                    "state": "open",
                    "body": "",
                    "repository_url": "https://api.github.com/repos/other/repo",
                },
                "fields": [],
            },
            {
                "id": 2,
                "content": {
                    "id": 102,
                    "number": 22,
                    "title": "Local",
                    "state": "open",
                    "body": "",
                    "repository_url": "https://api.github.com/repos/example/repo",
                },
                "fields": [],
            },
        ]
        target = projector.target_items_from_rest(fields, items)
        task = projector.parse_entity_text(
            entity("SD title", "building", issue=22), slug="linked"
        )

        plan = projector.plan_projection(
            self.workflow,
            [task],
            target,
            profile="generic",
            linked_issue_bindings=self.binding("linked", 22),
            **self.provenance,
        )

        self.assertEqual("example/repo#22", target[1]["issue_identity"])
        self.assertEqual(2, plan["mutations"][0]["current_item_id"])
        self.assertEqual("Local", plan["entities"][0]["desired"]["title"])
        task = projector.parse_entity_text(entity("Owned", "building"), slug="owned")
        foreign = apply_fake(
            projector.plan_projection(
                self.workflow, [task], [], profile="generic", **self.provenance
            ),
            [],
        )[0]
        foreign.update(
            {
                "repository": "other/repo",
                "issue_identity": "other/repo#1",
                "issue_number": 1,
            }
        )

        plan = projector.plan_projection(
            self.workflow, [task], [foreign], profile="generic", **self.provenance
        )

        self.assertEqual("CREATE", plan["entities"][0]["action"])
        self.assertIsNone(plan["mutations"][0]["current_issue_number"])

    def test_linked_issue_apply_never_patches_issue_bytes(self) -> None:
        task = projector.parse_entity_text(
            entity("SD title", "building", issue=22), slug="linked"
        )
        target = projector.merge_linked_issues(
            [],
            [{"id": 31, "number": 22, "title": "Human", "state": "open", "body": "Body"}],
            repository="example/repo",
        )
        plan = projector.plan_projection(
            self.workflow,
            [task],
            target,
            profile="generic",
            linked_issue_bindings=self.binding("linked", 22),
            **self.provenance,
        )
        fields = self.fields()

        class Client:
            def __init__(self) -> None:
                self.calls = []

            def request(self, method, path, *, authority, body=None):
                self.calls.append((method, path, authority, body))
                if method == "POST" and path.endswith("/items"):
                    return {"value": {"id": 21}}
                return {}

        client = Client()
        operations = projector.apply_github_plan(
            client,
            self.apply_config(5),
            plan,
            fields,
        )

        self.assertFalse(any("/issues/22" in path for _, path, _, _ in client.calls))
        self.assertEqual(
            ["ADD_PROJECT_ITEM", "UPDATE_FIELDS"],
            [operation["action"] for operation in operations],
        )

    def test_projection_envelope_expires_and_pins_installed_projector(self) -> None:
        config = {
            "schema": "spacedock-project-config/v1",
            "repository": "example/repo",
            "trunk_ref": "main",
            "state_ref": "spacedock-state/dev",
            "workflow_dir": "docs/dev",
            "profile": "generic",
            "entity_selection": ["one"],
            "external_apply_enabled": True,
            "credential": {
                "token_type": "classic-pat",
                "permissions": "project, repo",
                "expiry": "2026-08-20T00:00:00Z",
                "rotation_owner": "example",
                "fallback_blast_radius": "repository secret",
            },
            "project": {
                "owner_type": "user",
                "owner": "example",
                "number": 1,
                "node_id": "PVT_example",
            },
            "approval": {
                "scope": "selected",
                "expires_at": "2026-08-15T00:00:00Z",
                "projector_digest": self.provenance["projector_digest"],
                "max_mutations_per_run": 5,
                "linked_issues": {},
            },
        }

        projector.validate_config(
            config,
            installed_projector_digest=self.provenance["projector_digest"],
            now=datetime(2026, 8, 14, tzinfo=timezone.utc),
        )
        with self.assertRaisesRegex(projector.ProjectionError, "expired"):
            projector.validate_config(
                config,
                installed_projector_digest=self.provenance["projector_digest"],
                now=datetime(2026, 8, 16, tzinfo=timezone.utc),
            )
        with self.assertRaisesRegex(projector.ProjectionError, "projector digest"):
            projector.validate_config(
                config,
                installed_projector_digest="f" * 64,
                now=datetime(2026, 8, 14, tzinfo=timezone.utc),
            )

    def test_selected_scope_requires_nonempty_subset_and_suppresses_global_orphans(self) -> None:
        with self.assertRaisesRegex(projector.ProjectionError, "non-empty entity selection"):
            projector.validate_approval_scope(
                {"scope": "selected", "linked_issues": {}}, []
            )

        task = projector.parse_entity_text(entity("Selected", "building"), slug="selected")
        orphan = apply_fake(
            projector.plan_projection(
                self.workflow,
                [projector.parse_entity_text(entity("Other", "building"), slug="other")],
                [],
                profile="generic",
                **self.provenance,
            ),
            [],
        )
        plan = projector.plan_projection(
            self.workflow,
            [task],
            orphan,
            profile="generic",
            detect_orphans=False,
            **self.provenance,
        )
        self.assertEqual([], plan["orphans"])

    def test_nested_unknown_fields_are_unmapped_but_optional_types_fail_closed(self) -> None:
        nested = entity("Nested", "building") + "\n"
        nested = nested.replace(
            "source: fixture",
            "source: fixture\ndepends-on:\n  - another-task",
        )
        parsed = projector.parse_entity_text(nested, slug="nested")
        self.assertIsNone(parsed["depends-on"])

        with self.assertRaisesRegex(projector.ProjectionError, "issue.*positive integer"):
            projector.parse_entity_text(
                entity("Bad issue", "building", issue="true"), slug="bad-issue"
            )
        with self.assertRaisesRegex(projector.ProjectionError, "product.*string"):
            projector.parse_entity_text(
                entity("Bad product", "building", product=7), slug="bad-product"
            )

    def test_mutation_cap_refuses_entire_plan_before_first_write(self) -> None:
        task = projector.parse_entity_text(entity("One", "building"), slug="one")
        plan = projector.plan_projection(
            self.workflow, [task], [], profile="generic", **self.provenance
        )

        self.assert_apply_refuses(
            "mutation cap", plan, self.fields(), self.apply_config(1)
        )

    def test_issue_identity_preflight_refuses_before_schema_or_label_write(self) -> None:
        task = projector.parse_entity_text(entity("One", "building"), slug="one")
        plan = projector.plan_projection(
            self.workflow, [task], [], profile="generic", **self.provenance
        )
        plan["mutations"][0].update(
            {
                "current_issue_number": 7,
                "current_issue_id": 31,
                "current_repository": "other/repo",
            }
        )

        self.assert_apply_refuses("repository does not match", plan, [])

    def test_installed_workflow_pins_actions_and_default_branch_identity(self) -> None:
        workflow = (
            ROOT
            / "skills/setup-github-project-projection/assets/spacedock-project-sync.yml"
        ).read_text()
        self.assertIn(
            "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1", workflow
        )
        self.assertIn(
            "actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a", workflow
        )
        self.assertIn('GITHUB_REF_TYPE', workflow)
        self.assertIn('refs/heads/', workflow)
        self.assertIn("ref: ${{ github.sha }}", workflow)

    def test_dogfood_workflow_executes_the_canonical_projector_only(self) -> None:
        repository = ROOT.parent
        workflow = (
            repository / ".github/workflows/spacedock-project-sync.yml"
        ).read_text()
        canonical = (
            "projection-trunk/kc-dev-flow/skills/"
            "setup-github-project-projection/assets/project-spacedock-state.py"
        )

        self.assertIn(f"python3 {canonical} reconcile", workflow)
        self.assertFalse(
            (repository / ".github/scripts/project-spacedock-state.py").exists()
        )
        portable = (
            ROOT
            / "skills/setup-github-project-projection/assets/"
            "spacedock-project-sync.yml"
        ).read_text()
        self.assertIn(
            "python3 projection-trunk/.github/scripts/project-spacedock-state.py reconcile",
            portable,
        )

    def test_explicit_issue_and_existing_receipt_identity_mismatch_conflict(self) -> None:
        baseline = projector.parse_entity_text(entity("Linked", "building"), slug="linked")
        current = apply_fake(
            projector.plan_projection(
                self.workflow, [baseline], [], profile="generic", **self.provenance
            ),
            [],
        )[0]
        current["issue_number"] = 33
        current["issue_identity"] = "example/repo#33"
        linked = projector.parse_entity_text(
            entity("Linked", "building", issue=22), slug="linked"
        )

        plan = projector.plan_projection(
            self.workflow,
            [linked],
            [current],
            profile="generic",
            linked_issue_bindings=self.binding("linked", 22),
            **self.provenance,
        )

        self.assertEqual("CONFLICT", plan["entities"][0]["classification"])
        self.assertEqual("explicit_issue_identity_mismatch", plan["entities"][0]["reason"])
        self.assertEqual([], plan["mutations"])

    def test_mixed_conflict_and_create_refuses_before_any_write(self) -> None:
        tasks = [
            projector.parse_entity_text(entity("Create", "building"), slug="create"),
            projector.parse_entity_text(
                entity("Missing", "building", issue=404), slug="missing"
            ),
        ]
        plan = projector.plan_projection(
            self.workflow,
            tasks,
            [],
            profile="generic",
            linked_issue_bindings=self.binding("missing", 404),
            **self.provenance,
        )
        self.assertEqual(1, len(plan["mutations"]))

        self.assert_apply_refuses("conflicts", plan, [])

    def test_partial_apply_keeps_append_only_operation_journal(self) -> None:
        task = projector.parse_entity_text(entity("One", "building"), slug="one")
        plan = projector.plan_projection(
            self.workflow, [task], [], profile="generic", **self.provenance
        )
        fields = self.fields()

        class Client:
            def request(self, method, path, *, authority, body=None):
                raise projector.ProjectionError("injected Project failure")

            def graphql(self, query, variables, *, authority):
                return {
                    "addProjectV2DraftIssue": {
                        "projectItem": {
                            "id": "PVTI_fixture",
                            "fullDatabaseId": "21",
                            "content": {"id": "DI_fixture"},
                        }
                    }
                }

        journal: list[dict[str, object]] = []
        with self.assertRaisesRegex(projector.ProjectionError, "injected"):
            projector.apply_github_plan(
                Client(),
                self.apply_config(3),
                plan,
                fields,
                journal=journal,
            )
        self.assertEqual(
            [{"action": "CREATE_DRAFT", "identity": "example/repo:docs/dev:one"}],
            journal,
        )

    def test_rest_client_retries_transient_http_with_bounded_retry_after(self) -> None:
        waits: list[float] = []

        class Response:
            headers: dict[str, str] = {}

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return None

            def read(self):
                return b'{"ok":true}'

        error = urllib.error.HTTPError(
            "https://api.github.com/test",
            503,
            "unavailable",
            {"Retry-After": "60"},
            None,
        )
        with mock.patch.object(
            projector.urllib.request, "urlopen", side_effect=[error, Response()]
        ):
            client = projector.GitHubRestClient("repo", "project", sleep=waits.append)
            self.assertEqual({"ok": True}, client.request("GET", "test", authority="repository"))

        self.assertEqual([10.0], waits)

    def test_production_reconcile_converges_end_to_end(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            trunk = root / "trunk"
            state = root / "state"
            (trunk / "docs/dev").mkdir(parents=True)
            state.mkdir()
            (trunk / "docs/dev/README.md").write_text(WORKFLOW)
            (state / "one.md").write_text(entity("One", "building"))

            digest = hashlib.sha256(PROJECTOR.read_bytes()).hexdigest()
            config = {
                "schema": "spacedock-project-config/v1",
                "repository": "example/repo",
                "trunk_ref": "main",
                "state_ref": "spacedock-state/dev",
                "workflow_dir": "docs/dev",
                "profile": "generic",
                "entity_selection": [],
                "external_apply_enabled": True,
                "credential": {
                    "token_type": "classic-pat",
                    "permissions": "project, repo",
                    "expiry": "2099-01-02T00:00:00Z",
                    "rotation_owner": "example",
                    "fallback_blast_radius": "repository secret",
                },
                "project": {
                    "owner_type": "user",
                    "owner": "example",
                    "number": 1,
                    "node_id": "PVT_example",
                },
                "approval": {
                    "scope": "workflow",
                    "expires_at": "2099-01-01T00:00:00Z",
                    "projector_digest": digest,
                    "max_mutations_per_run": 5,
                    "linked_issues": {},
                },
            }

            class Client:
                def __init__(self) -> None:
                    self.items: list[dict[str, object]] = []
                    self.fields = [
                        {
                            "id": 10,
                            "name": "Status",
                            "data_type": "single_select",
                            "options": [
                                {"id": "progress", "name": {"raw": "In Progress"}}
                            ],
                        },
                        {
                            "id": 11,
                            "name": "SD Stage",
                            "data_type": "single_select",
                            "options": [
                                {"id": "building", "name": {"raw": "building"}}
                            ],
                        },
                        {"id": 12, "name": "SD Identity", "data_type": "text"},
                    ]

                def request_all(self, path, *, authority):
                    if path.endswith("/fields"):
                        return self.fields
                    if "/items" in path:
                        return self.items
                    return []

                def request(self, method, path, *, authority, body=None):
                    if method == "GET" and path == "repos/example/repo":
                        return {"default_branch": "main"}
                    if method == "GET" and path.endswith("projectsV2/1"):
                        return {"value": {"node_id": "PVT_example"}}
                    if method == "PATCH" and "/items/" in path:
                        self.items[0]["fields"] = [
                            {
                                "id": field["id"],
                                "value": (
                                    {"raw": field["value"]}
                                    if field["id"] == 12
                                    else {
                                        "id": field["value"],
                                        "name": {
                                            "raw": "building"
                                            if field["id"] == 11
                                            else "In Progress"
                                        },
                                    }
                                ),
                            }
                            for field in body["fields"]
                        ]
                        return {}
                    raise AssertionError((method, path, authority, body))

                def graphql(self, query, variables, *, authority):
                    self.items.append(
                        {
                            "id": 21,
                            "node_id": "PVTI_fixture",
                            "content_type": "DraftIssue",
                            "content": {
                                "id": 31,
                                "node_id": "DI_fixture",
                                "title": variables["title"],
                                "body": variables["body"],
                            },
                            "fields": [],
                        }
                    )
                    return {
                        "addProjectV2DraftIssue": {
                            "projectItem": {
                                "id": "PVTI_fixture",
                                "fullDatabaseId": "21",
                                "content": {"id": "DI_fixture"},
                            }
                        }
                    }

            with mock.patch.object(projector, "_git_commit", side_effect=["a" * 40, "b" * 40]):
                result = projector.reconcile(
                    config, trunk_dir=trunk, state_dir=state, client=Client()
                )

        self.assertEqual("apply", result["mode"])
        self.assertEqual(
            ["CREATE_DRAFT", "UPDATE_FIELDS"],
            [operation["action"] for operation in result["operations"]],
        )
        self.assertNotIn("snapshot", result)
        self.assertEqual([], result["converged_plan"]["mutations"])


if __name__ == "__main__":
    unittest.main()
