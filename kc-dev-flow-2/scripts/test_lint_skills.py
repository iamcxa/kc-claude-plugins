#!/usr/bin/env python3
"""Mutation checks on disposable copies of the static comparison scaffold."""

import importlib.util
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("flow_lint", ROOT / "scripts/lint-skills.py")
lint = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lint)


class RouteMutationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "kc-dev-flow-2"
        shutil.copytree(ROOT, self.root)

    def change(self, relative, old, new):
        path = self.root / relative
        text = path.read_text()
        self.assertIn(old, text, "mutation must actually change its fixture")
        path.write_text(text.replace(old, new, 1))

    def refuses(self, expected):
        errors = lint.lint_tree(self.root)
        self.assertTrue(any(expected in error for error in errors), errors)

    def test_valid_scaffold(self):
        self.assertEqual(lint.lint_tree(self.root), [])

    def test_missing_profile_reference(self):
        (self.root / "skills/implementation/profiles/pilot.md").unlink()
        self.refuses("profiles/pilot.md")

    def test_cross_profile_route(self):
        self.change("skills/implementation/SKILL.md", "(profiles/poc.md)", "(profiles/prod.md)")
        self.refuses("route must link to skills/implementation/profiles/poc.md")

    def test_cross_stage_route(self):
        self.change("skills/validation/SKILL.md", "(profiles/pilot.md)", "(../implementation/profiles/pilot.md)")
        self.refuses("route must link to skills/validation/profiles/pilot.md")

    def test_wrong_shared_principle(self):
        self.change("skills/ideation/SKILL.md", "../../references/profiles/pilot.md", "../../references/profiles/prod.md")
        self.refuses("route must link to references/profiles/pilot.md")

    def test_unknown_profile(self):
        self.change("skills/implementation/SKILL.md", "| poc | active |", "| experimental | active |")
        self.refuses("profile coverage")

    def test_duplicate_profile(self):
        self.change("skills/implementation/SKILL.md", "| pilot | active |", "| poc | active |")
        self.refuses("duplicate profile")

    def test_missing_markdown_table_separator(self):
        self.change("skills/implementation/SKILL.md", "| --- | --- | --- | --- |", "Plain prose is not a table separator.")
        self.refuses("invalid profile table separator")

    def test_reversed_routing_markers(self):
        relative = "skills/implementation/SKILL.md"
        self.change(relative, "<!-- profile-routes -->", "<!-- temporary-marker -->")
        self.change(relative, "<!-- /profile-routes -->", "<!-- profile-routes -->")
        self.change(relative, "<!-- temporary-marker -->", "<!-- /profile-routes -->")
        self.refuses("expected one ordered profile routing table")

    def test_poc_cannot_declare_ideation_active(self):
        self.change("skills/ideation/SKILL.md", "| poc | skip |", "| poc | active |")
        self.refuses("availability must be skip")

    def test_missing_principles(self):
        (self.root / "skills/validation/principles.md").unlink()
        self.refuses("validation/principles.md")

    def test_external_reference_symlink(self):
        target = self.root / "references/profiles/poc.md"
        outside = self.root.parent / "external.md"
        target.rename(outside)
        target.symlink_to(outside)
        self.refuses("reference escapes the variant tree")

    def test_old_variant_invocation(self):
        self.change("skills/chief-engineer/SKILL.md", "kc-dev-flow-2:engineering-reviewer", "kc-dev-flow:science-officer")
        self.refuses("unknown variant skill")

    def test_role_binding_and_model_policy(self):
        self.change("agents/engineering-reviewer.md", "model: opus", "model: inherit")
        self.change("agents/chief-engineer.md", '["kc-dev-flow-2:chief-engineer"]', '["kc-dev-flow:chief-engineer"]')
        self.refuses("opus/xhigh policy changed")
        self.refuses("expected exact variant skill binding")

    def test_existing_frontmatter_validator_is_used(self):
        path = self.root / "skills/validation/SKILL.md"
        body = path.read_text()
        description = next(line for line in body.splitlines() if line.startswith("description:"))
        path.write_text(body.replace(description, "description:", 1))
        self.refuses("frontmatter:")


if __name__ == "__main__":
    unittest.main(verbosity=2)
