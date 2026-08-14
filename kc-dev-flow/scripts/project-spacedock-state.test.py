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


def apply_fake(plan: dict[str, object], target_items: list[dict[str, object]]):
    """Apply a plan to an in-memory target without shipping test code."""

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
                if mutation.get("ownership") == "linked":
                    item["fields"] = copy.deepcopy(desired["fields"])
                    if item.get("item_id") is None:
                        item["item_id"] = f"FAKE-LINKED-{item.get('issue_number')}"
                else:
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
            raise projector.ProjectionError(
                f"fake target lost update identity {mutation['identity']!r}"
            )
    return result


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
        second = projector.plan_projection(
            self.workflow, [task], applied, profile="generic", **self.provenance
        )

        self.assertEqual("CREATE", first["entities"][0]["classification"])
        self.assertEqual("NO_CHANGE", second["entities"][0]["classification"])
        self.assertEqual([], second["mutations"])
        receipt = projector.parse_receipt(applied[0]["body"])
        self.assertEqual("example/repo:docs/dev:one", receipt["identity"])
        self.assertEqual(self.provenance["projector_digest"], receipt["projector_digest"])
        self.assertIn("This Issue is a read-only projection from Spacedock.", applied[0]["body"])
        self.assertIn("- Stage: `building`", applied[0]["body"])
        self.assertIn("- Source: fixture", applied[0]["body"])
        self.assertNotIn("worktree", applied[0]["body"])

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

    def test_quoted_issue_number_selects_linked_ownership(self) -> None:
        task = projector.parse_entity_text(
            entity("Linked", "building", issue='"22"'), slug="linked"
        )
        target = projector.merge_repository_issues(
            [],
            [{"id": 31, "number": 22, "title": "Linked", "state": "open", "body": ""}],
            linked_issue_numbers={22},
        )
        plan = projector.plan_projection(
            self.workflow,
            [task],
            target,
            profile="generic",
            linked_issue_bindings=self.binding("linked", 22),
            **self.provenance,
        )

        self.assertEqual(22, task["issue"])
        self.assertEqual(22, plan["entities"][0]["desired"]["issue_number"])
        self.assertEqual("linked", plan["entities"][0]["desired"]["receipt"]["ownership"])

    def test_terminal_stage_closes_only_projector_owned_issue(self) -> None:
        owned = projector.parse_entity_text(entity("Owned", "released"), slug="owned")
        linked = projector.parse_entity_text(
            entity("Linked", "released", issue=22), slug="linked"
        )
        target = projector.merge_repository_issues(
            [],
            [{"id": 31, "number": 22, "title": "Linked", "state": "open", "body": ""}],
            linked_issue_numbers={22},
        )

        plan = projector.plan_projection(
            self.workflow,
            [owned, linked],
            target,
            profile="generic",
            linked_issue_bindings=self.binding("linked", 22),
            **self.provenance,
        )
        by_slug = {item["slug"]: item["desired"] for item in plan["entities"]}

        self.assertEqual("CLOSED", by_slug["owned"]["issue_state"])
        self.assertEqual("OPEN", by_slug["linked"]["issue_state"])

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
            entity("SD title", "building", issue=22), slug="linked"
        )
        target = projector.merge_repository_issues(
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
            linked_issue_numbers={22},
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

    def test_archive_closes_owned_preserves_linked_and_ignores_foreign(self) -> None:
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
        linked_target = projector.merge_repository_issues(
            [],
            [{"id": 31, "number": 22, "title": "Linked", "state": "open", "body": ""}],
            linked_issue_numbers={22},
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

        self.assertEqual("CLOSED", by_slug["owned"]["issue_state"])
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

    def test_snapshot_is_deterministic_and_reports_missing_liveness(self) -> None:
        tasks = [
            projector.parse_entity_text(entity("A", "building"), slug="a"),
            projector.parse_entity_text(entity("B", "released"), slug="b"),
        ]
        plan = projector.plan_projection(
            self.workflow, tasks, [], profile="generic", **self.provenance
        )
        first = projector.build_status_snapshot(plan)
        second = projector.build_status_snapshot(json.loads(json.dumps(plan)))
        self.assertEqual(first, second)
        self.assertEqual({"building": 1, "released": 1}, first["stage_counts"])
        self.assertEqual(1, first["terminal_count"])
        self.assertEqual("MISSING", first["projection_freshness"])
        self.assertNotIn("observed_at", first)
        self.assertEqual(
            "CURRENT",
            projector.build_status_snapshot(
                plan, last_success=800, observed_at=1000, freshness_window=300
            )["projection_freshness"],
        )
        self.assertEqual(
            "STALE",
            projector.build_status_snapshot(
                plan, last_success=699, observed_at=1000, freshness_window=300
            )["projection_freshness"],
        )

    def test_status_snapshot_qualifies_project_and_sprint_metrics(self) -> None:
        task = projector.parse_entity_text(
            entity("Sprint task", "building", sprint="S3"), slug="sprint-task"
        )
        task["goal"] = "Prove projection"
        task["exit-criteria"] = "Zero mutation rerun"
        plan = projector.plan_projection(
            self.workflow, [task], [], profile="generic", **self.provenance
        )
        snapshot = projector.build_status_snapshot(
            plan,
            project={
                "owner_type": "user",
                "owner": "example",
                "number": 1,
                "node_id": "PVT_example",
            },
        )

        self.assertEqual("PVT_example", snapshot["project"]["node_id"])
        self.assertEqual("MISSING", snapshot["projection_freshness"])
        self.assertEqual("example/repo:docs/dev:sprint:S3", snapshot["sprints"][0]["identity"])
        self.assertEqual(1, snapshot["sprints"][0]["member_count"])
        self.assertEqual(1, len(snapshot["available_goal_digests"]))
        self.assertEqual(1, len(snapshot["available_exit_digests"]))

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

    def test_rest_apply_uses_separate_authorities_and_convergent_operations(self) -> None:
        task = projector.parse_entity_text(entity("One", "building"), slug="one")
        plan = projector.plan_projection(
            self.workflow, [task], [], profile="generic", **self.provenance
        )
        fields = [
            {
                "id": 10,
                "name": "Status",
                "data_type": "single_select",
                "options": [
                    {"id": "progress", "name": {"raw": "In Progress"}},
                ],
            },
            {
                "id": 11,
                "name": "SD Stage",
                "data_type": "single_select",
                "options": [
                    {"id": name, "name": {"raw": name}}
                    for name in self.workflow["stages"]
                ],
            },
        ]

        class FakeClient:
            def __init__(self) -> None:
                self.calls: list[tuple[str, str, str, object]] = []

            def request(self, method, path, *, authority, body=None):
                self.calls.append((method, path, authority, body))
                if method == "POST" and path.endswith("/issues"):
                    return {"id": 31, "number": 7}
                if method == "POST" and path.endswith("/items"):
                    return {"value": {"id": 21}}
                return {"id": 31, "number": 7}

        client = FakeClient()
        config = {
            "repository": "example/repo",
            "approval": {"max_mutations_per_run": 10},
            "project": {
                "owner_type": "user",
                "owner": "example",
                "number": 1,
                "node_id": "PVT_example",
            },
        }
        operations = projector.apply_github_plan(client, config, plan, fields)

        self.assertEqual(
            ["CREATE_ISSUE", "ADD_PROJECT_ITEM", "UPDATE_FIELDS"],
            [operation["action"] for operation in operations],
        )
        self.assertEqual("repository", client.calls[0][2])
        self.assertEqual("project", client.calls[1][2])
        self.assertEqual("project", client.calls[2][2])
        self.assertEqual(
            {"fields": [{"id": 11, "value": "building"}, {"id": 10, "value": "progress"}]},
            client.calls[2][3],
        )

    def test_foreign_project_fields_do_not_prevent_no_change(self) -> None:
        task = projector.parse_entity_text(entity("One", "building"), slug="one")
        first = projector.plan_projection(
            self.workflow, [task], [], profile="generic", **self.provenance
        )
        target = apply_fake(first, [])
        target[0]["fields"]["Human field"] = "preserve me"

        second = projector.plan_projection(
            self.workflow, [task], target, profile="generic", **self.provenance
        )

        self.assertEqual("NO_CHANGE", second["entities"][0]["classification"])
        self.assertEqual([], second["mutations"])

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
        ]

        class FakeClient:
            def __init__(self) -> None:
                self.calls = []

            def request(self, method, path, *, authority, body=None):
                self.calls.append((method, path, authority, body))
                raise AssertionError("schema refusal must happen before a write")

        client = FakeClient()
        config = {
            "repository": "example/repo",
            "approval": {"max_mutations_per_run": 10},
            "project": {
                "owner_type": "user",
                "owner": "example",
                "number": 1,
                "node_id": "PVT_example",
            },
        }
        with self.assertRaisesRegex(projector.ProjectionError, "lacks options"):
            projector.apply_github_plan(client, config, plan, fields)
        self.assertEqual([], client.calls)
        self.assertEqual(
            "UPDATE_FIELD_OPTIONS", projector.project_schema_plan(plan, fields)[0]["action"]
        )

    def test_stranded_receipt_issue_resumes_without_duplicate_issue(self) -> None:
        task = projector.parse_entity_text(entity("One", "building"), slug="one")
        created = apply_fake(
            projector.plan_projection(
                self.workflow, [task], [], profile="generic", **self.provenance
            ),
            [],
        )[0]
        issues = [
            {
                "id": 31,
                "number": created["issue_number"],
                "title": created["title"],
                "state": "open",
                "body": created["body"],
                "user": {"login": "github-actions[bot]"},
            }
        ]
        target = projector.merge_repository_issues([], issues, repository="example/repo")
        plan = projector.plan_projection(
            self.workflow, [task], target, profile="generic", **self.provenance
        )
        mutation = plan["mutations"][0]

        self.assertEqual(created["issue_number"], mutation["current_issue_number"])
        self.assertIsNone(mutation["current_item_id"])

        class ResumeClient:
            def __init__(self) -> None:
                self.calls = []

            def request(self, method, path, *, authority, body=None):
                self.calls.append((method, path, authority))
                if method == "PATCH" and "/issues/" in path:
                    return {"id": 31, "number": created["issue_number"]}
                if method == "POST" and path.endswith("/items"):
                    return {"value": {"id": 21}}
                return {}

        fields = [
            {
                "id": 10,
                "name": "Status",
                "data_type": "single_select",
                "options": [{"id": "progress", "name": {"raw": "In Progress"}}],
            },
            {
                "id": 11,
                "name": "SD Stage",
                "data_type": "single_select",
                "options": [{"id": "building", "name": {"raw": "building"}}],
            },
        ]
        client = ResumeClient()
        projector.apply_github_plan(
            client,
            {
                "repository": "example/repo",
                "approval": {"max_mutations_per_run": 10},
                "project": {
                    "owner_type": "user",
                    "owner": "example",
                    "number": 1,
                    "node_id": "PVT_example",
                },
            },
            plan,
            fields,
        )
        self.assertEqual("PATCH", client.calls[0][0])
        self.assertEqual("repository", client.calls[0][2])
        self.assertFalse(
            any(method == "POST" and path.endswith("/issues") for method, path, _ in client.calls)
        )

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

    def test_foreign_repository_receipt_cannot_own_local_issue_number(self) -> None:
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

    def test_todo_wins_when_project_exposes_todo_and_backlog(self) -> None:
        self.assertEqual(
            "Todo",
            projector._generic_status(
                self.workflow,
                self.workflow["initial_stage"],
                ["Backlog", "Todo", "In Progress", "Done"],
            ),
        )

    def test_linked_issue_apply_never_patches_issue_bytes(self) -> None:
        task = projector.parse_entity_text(
            entity("SD title", "building", issue=22), slug="linked"
        )
        target = projector.merge_repository_issues(
            [],
            [{"id": 31, "number": 22, "title": "Human", "state": "open", "body": "Body"}],
            repository="example/repo",
            linked_issue_numbers={22},
        )
        plan = projector.plan_projection(
            self.workflow,
            [task],
            target,
            profile="generic",
            linked_issue_bindings=self.binding("linked", 22),
            **self.provenance,
        )
        fields = [
            {
                "id": 10,
                "name": "Status",
                "data_type": "single_select",
                "options": [{"id": "progress", "name": {"raw": "In Progress"}}],
            },
            {
                "id": 11,
                "name": "SD Stage",
                "data_type": "single_select",
                "options": [{"id": "building", "name": {"raw": "building"}}],
            },
        ]

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
            {
                "repository": "example/repo",
                "project": {
                    "owner_type": "user",
                    "owner": "example",
                    "number": 1,
                    "node_id": "PVT_example",
                },
                "approval": {"max_mutations_per_run": 5},
            },
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

        class Client:
            def __init__(self) -> None:
                self.calls = []

            def request(self, method, path, *, authority, body=None):
                self.calls.append((method, path))
                raise AssertionError("cap must refuse before writes")

        client = Client()
        fields = [
            {
                "id": 10,
                "name": "Status",
                "data_type": "single_select",
                "options": [{"id": "progress", "name": {"raw": "In Progress"}}],
            },
            {
                "id": 11,
                "name": "SD Stage",
                "data_type": "single_select",
                "options": [{"id": "building", "name": {"raw": "building"}}],
            },
        ]
        config = {
            "repository": "example/repo",
            "project": {
                "owner_type": "user",
                "owner": "example",
                "number": 1,
                "node_id": "PVT_example",
            },
            "approval": {"max_mutations_per_run": 2},
        }
        with self.assertRaisesRegex(projector.ProjectionError, "mutation cap"):
            projector.apply_github_plan(client, config, plan, fields)
        self.assertEqual([], client.calls)

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

    def test_forged_public_receipts_are_ignored_but_bot_receipts_can_resume(self) -> None:
        task = projector.parse_entity_text(entity("One", "building"), slug="one")
        created = apply_fake(
            projector.plan_projection(
                self.workflow, [task], [], profile="generic", **self.provenance
            ),
            [],
        )[0]
        forged = {
            "id": 1,
            "number": 1,
            "title": "Forged",
            "state": "open",
            "body": created["body"],
            "user": {"login": "attacker"},
        }
        trusted = {
            **forged,
            "id": 2,
            "number": 2,
            "title": "Trusted",
            "user": {"login": "github-actions[bot]"},
        }
        malformed = {
            **forged,
            "id": 3,
            "number": 3,
            "body": "<!-- spacedock-projection:v1\nnot-json\n-->",
        }

        observed = projector.merge_repository_issues(
            [],
            [forged, trusted, malformed],
            repository="example/repo",
            managed_identity_prefix="example/repo:docs/dev:",
        )

        self.assertEqual([2], [item["issue_number"] for item in observed])

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

        class Client:
            calls: list[object] = []

            def request(self, *args, **kwargs):
                self.calls.append((args, kwargs))
                raise AssertionError("conflict must refuse before writes")

        client = Client()
        with self.assertRaisesRegex(projector.ProjectionError, "conflicts"):
            projector.apply_github_plan(
                client,
                {
                    "repository": "example/repo",
                    "project": {
                        "owner_type": "user",
                        "owner": "example",
                        "number": 1,
                        "node_id": "PVT_example",
                    },
                    "approval": {"max_mutations_per_run": 10},
                },
                plan,
                [],
            )
        self.assertEqual([], client.calls)

    def test_partial_apply_keeps_append_only_operation_journal(self) -> None:
        task = projector.parse_entity_text(entity("One", "building"), slug="one")
        plan = projector.plan_projection(
            self.workflow, [task], [], profile="generic", **self.provenance
        )
        fields = [
            {
                "id": 10,
                "name": "Status",
                "data_type": "single_select",
                "options": [{"id": "progress", "name": {"raw": "In Progress"}}],
            },
            {
                "id": 11,
                "name": "SD Stage",
                "data_type": "single_select",
                "options": [{"id": "building", "name": {"raw": "building"}}],
            },
        ]

        class Client:
            def request(self, method, path, *, authority, body=None):
                if method == "POST" and path.endswith("/issues"):
                    return {"id": 31, "number": 7}
                raise projector.ProjectionError("injected Project failure")

        journal: list[dict[str, object]] = []
        with self.assertRaisesRegex(projector.ProjectionError, "injected"):
            projector.apply_github_plan(
                Client(),
                {
                    "repository": "example/repo",
                    "project": {
                        "owner_type": "user",
                        "owner": "example",
                        "number": 1,
                        "node_id": "PVT_example",
                    },
                    "approval": {"max_mutations_per_run": 3},
                },
                plan,
                fields,
                journal=journal,
            )
        self.assertEqual([{"action": "CREATE_ISSUE", "issue_number": 7}], journal)

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
                    self.issues: list[dict[str, object]] = []
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
                    ]

                def request_all(self, path, *, authority):
                    if path.endswith("/fields"):
                        return self.fields
                    if "/items" in path:
                        return self.items
                    return self.issues

                def request(self, method, path, *, authority, body=None):
                    if method == "GET" and path == "repos/example/repo":
                        return {"default_branch": "main"}
                    if method == "GET" and path.endswith("projectsV2/1"):
                        return {"value": {"node_id": "PVT_example"}}
                    if method == "POST" and path.endswith("/issues"):
                        issue = {
                            "id": 31,
                            "number": 7,
                            "title": body["title"],
                            "state": body["state"],
                            "body": body["body"],
                            "user": {"login": "github-actions[bot]"},
                        }
                        self.issues.append(issue)
                        return issue
                    if method == "POST" and path.endswith("/items"):
                        issue = next(item for item in self.issues if item["id"] == body["id"])
                        project_item = {
                            "id": 21,
                            "node_id": "PVTI_fixture",
                            "content": {
                                **issue,
                                "repository_url": "https://api.github.com/repos/example/repo",
                            },
                            "fields": [],
                        }
                        self.items.append(project_item)
                        return {"value": {"id": 21}}
                    if method == "PATCH" and "/items/" in path:
                        self.items[0]["fields"] = [
                            {"id": field["id"], "value": {"id": field["value"], "name": {"raw": "building" if field["id"] == 11 else "In Progress"}}}
                            for field in body["fields"]
                        ]
                        return {}
                    raise AssertionError((method, path, authority, body))

            with mock.patch.object(projector, "_git_commit", side_effect=["a" * 40, "b" * 40]):
                result = projector.reconcile(
                    config, trunk_dir=trunk, state_dir=state, client=Client()
                )

        self.assertEqual("apply", result["mode"])
        self.assertEqual(
            ["CREATE_ISSUE", "ADD_PROJECT_ITEM", "UPDATE_FIELDS"],
            [operation["action"] for operation in result["operations"]],
        )
        self.assertEqual([], result["converged_plan"]["mutations"])


if __name__ == "__main__":
    unittest.main()
