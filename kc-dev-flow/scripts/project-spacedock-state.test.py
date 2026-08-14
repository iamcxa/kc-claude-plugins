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
        applied = projector.apply_fake(first, [])
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
            self.workflow, [task], target, profile="generic", **self.provenance
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
            self.workflow, [owned, linked], target, profile="generic", **self.provenance
        )
        by_slug = {item["slug"]: item["desired"] for item in plan["entities"]}

        self.assertEqual("CLOSED", by_slug["owned"]["issue_state"])
        self.assertEqual("OPEN", by_slug["linked"]["issue_state"])

    def test_missing_explicit_issue_is_a_conflict_before_mutation(self) -> None:
        task = projector.parse_entity_text(
            entity("Missing", "building", issue=404), slug="missing"
        )
        plan = projector.plan_projection(
            self.workflow, [task], [], profile="generic", **self.provenance
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
            self.workflow, [task], target, profile="generic", **self.provenance
        )
        desired = plan["entities"][0]["desired"]

        self.assertEqual("Human title", desired["title"])
        self.assertEqual("CLOSED", desired["issue_state"])
        self.assertTrue(desired["body"].startswith("Human body\n\n"))
        self.assertEqual("linked", desired["receipt"]["ownership"])

    def test_duplicate_explicit_issue_references_fail_closed(self) -> None:
        tasks = [
            projector.parse_entity_text(entity("One", "building", issue=22), slug="one"),
            projector.parse_entity_text(entity("Two", "building", issue='"22"'), slug="two"),
        ]

        with self.assertRaisesRegex(projector.ProjectionError, "duplicate entity Issue"):
            projector.plan_projection(
                self.workflow, tasks, [], profile="generic", **self.provenance
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
            **self.provenance,
        )
        target = projector.apply_fake(baseline_plan, linked_target)
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
            self.workflow, [owned, linked], target, profile="generic", **self.provenance
        )
        applied = projector.apply_fake(archive_plan, target)
        by_slug = {
            projector.parse_receipt(item["body"])["slug"]: item
            for item in applied
            if projector.parse_receipt(item["body"])
        }

        self.assertEqual("CLOSED", by_slug["owned"]["issue_state"])
        self.assertEqual("OPEN", by_slug["linked"]["issue_state"])
        self.assertTrue(projector.parse_receipt(by_slug["owned"]["body"])["archived"])
        self.assertEqual(before_foreign, applied[-1])

        no_op = projector.plan_projection(
            self.workflow, [owned, linked], applied, profile="generic", **self.provenance
        )
        self.assertEqual([], no_op["mutations"])

    def test_missing_tombstone_is_conflict_without_mutation(self) -> None:
        task = projector.parse_entity_text(entity("Gone", "building"), slug="gone")
        baseline = projector.apply_fake(
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

    def test_freshness_is_time_bearing_and_snapshot_is_deterministic(self) -> None:
        self.assertEqual("MISSING", projector.freshness_status(None, now=1000, window=300))
        self.assertEqual("CURRENT", projector.freshness_status(800, now=1000, window=300))
        self.assertEqual("STALE", projector.freshness_status(699, now=1000, window=300))

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
        self.assertNotIn("observed_at", first)

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
        target = projector.apply_fake(first, [])
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
        created = projector.apply_fake(
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
            }
        ]
        target = projector.merge_repository_issues([], issues)
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
            self.assertEqual(2, workflow.count("actions/checkout@v7"))
            self.assertIn("actions/upload-artifact@v7", workflow)
            self.assertNotIn("push:", workflow)
            self.assertNotIn("PVT_example", workflow)

            script = target / ".github/scripts/project-spacedock-state.py"
            script.write_text(script.read_text() + "# drift\n")
            drifted = installer.audit_installation(target, config)
            by_path = {item["path"]: item for item in drifted["files"]}
            self.assertFalse(drifted["clean"])
            self.assertEqual("UPDATE", by_path[".github/scripts/project-spacedock-state.py"]["action"])


if __name__ == "__main__":
    unittest.main()
