#!/usr/bin/env python3
"""Mutation checks on disposable copies of the static comparison scaffold."""

import importlib.util
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("flow_lint", ROOT / "scripts/lint-skills.py")
lint = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lint)
SHIPPED = list(lint.WORKFLOW_BUDGET_STEPS)


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

    def test_observer_keeps_its_declared_model(self):
        self.change("agents/observer.md", "model: sonnet", "model: inherit")
        self.refuses("observer agent: existing sonnet/high policy changed")

    def test_bare_script_name(self):
        self.change("skills/implementation/principles.md", "<package>/scripts/comment_ratio.py", "comment_ratio.py")
        self.refuses("skills/implementation/principles.md: script comment_ratio.py is named without")

    def test_script_named_by_link_label_only(self):
        self.change("skills/learn/SKILL.md", "[learning recorder]", "[learning.py]")
        self.refuses("skills/learn/SKILL.md: script learning.py is named without")

    def test_extension_script_named_without_its_extension_path(self):
        self.change("extensions/roborev/EXTENSION.md", "<package>/extensions/roborev/roborev_gate.py", "<package>/scripts/roborev_gate.py")
        self.refuses("extensions/roborev/EXTENSION.md: script roborev_gate.py is named without <package>/extensions/roborev/")

    def test_machine_path_placeholder(self):
        self.change("skills/learn/SKILL.md", "<package>/scripts/learning.py --repo \"$CODE_ROOT\" release",
                    "/absolute/plugin/scripts/learning.py --repo \"$CODE_ROOT\" release")
        self.refuses("skills/learn/SKILL.md: package path must be <package>/scripts/NAME")

    def test_brace_placeholder(self):
        self.change("references/sd/adoption.md", "python3 <package>/scripts/poc_readme.py derive",
                    "python3 {package}/scripts/poc_readme.py derive")
        self.refuses("references/sd/adoption.md: package path must be <package>/scripts/NAME")

    def test_package_placeholder_without_root_line(self):
        self.change("skills/implementation/SKILL.md", "Package root: ${CLAUDE_PLUGIN_ROOT}\n", "")
        self.refuses("skills/implementation/SKILL.md: uses <package> but has no 'Package root:' line")

    def workflow_text(self):
        return (self.root / "references/sd/workflow.md").read_text()

    def with_words(self, delta):
        path = self.root / "references/sd/workflow.md"
        text = path.read_text()
        path.write_text(text + "\nfiller" * delta if delta > 0 else text.rsplit(None, -delta)[0] + "\n")
        return len(path.read_text().split())

    def budget_with(self, steps):
        patch = mock.patch.object(lint, "WORKFLOW_BUDGET_STEPS", steps)
        patch.start()
        self.addCleanup(patch.stop)

    def test_workflow_over_its_word_budget(self):
        self.with_words(lint.workflow_budget(SHIPPED) - len(self.workflow_text().split()) + 1)
        self.refuses(f"exceeds the budget of {lint.workflow_budget()}")
        self.refuses("raise step")

    def test_workflow_under_its_word_budget_names_the_cut_step(self):
        self.with_words(-1)
        self.refuses(f"is 1 under the budget of {lint.workflow_budget()}")
        self.refuses("cut step of -1")

    def test_workflow_equal_to_its_word_budget_passes_and_prints_the_count(self):
        self.assertEqual(len(self.workflow_text().split()), lint.workflow_budget())
        result = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/lint-skills.py"), "--root", str(self.root)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout)
        n = lint.workflow_budget()
        self.assertIn(f"{n} of {n} words", result.stdout)

    def test_a_raise_step_needs_the_captains_quoted_words_and_a_loaded_moment(self):
        count = self.with_words(7)
        base = SHIPPED
        raised = dict(delta=count - lint.workflow_budget(SHIPPED), why="a rule FO reads only at startup")
        full = dict(raised, captain="\u300cthe added text is read once\u300d (chat)", loaded="startup")
        cases = {
            "no captain": (dict(raised, loaded="startup"), "'captain' has no quoted words"),
            "captain without a quote": (dict(raised, captain="approved", loaded="startup"), "'captain' has no quoted words"),
            "empty quote": (dict(raised, captain="\u300c \u300d", loaded="startup"), "'captain' has no quoted words"),
            "no loaded": (dict(raised, captain="\u300cyes\u300d"), "has no 'loaded' moment"),
        }
        for label, (step, expected) in cases.items():
            with self.subTest(label):
                self.budget_with([*base, step])
                errors = lint.lint_tree(self.root)
                self.assertTrue(any(expected in e and f"WORKFLOW_BUDGET_STEPS[{len(base)}]" in e for e in errors), errors)
        self.budget_with([*base, full])
        self.assertEqual(lint.lint_tree(self.root), [])

    def test_a_cut_step_needs_only_a_reason_and_a_step_without_one_is_refused(self):
        count = self.with_words(-3)
        cut = dict(delta=count - lint.workflow_budget(SHIPPED), why="moved to a script message")
        self.budget_with([*SHIPPED, cut])
        self.assertEqual(lint.lint_tree(self.root), [])
        self.budget_with([*SHIPPED, dict(delta=cut["delta"])])
        self.refuses("has no 'why'")

    def test_a_ledger_whose_sum_differs_from_the_count_is_refused_either_way(self):
        for drift in (1, -1):
            with self.subTest(drift):
                self.budget_with([*SHIPPED, dict(delta=drift, why="x", captain="\u300cx\u300d", loaded="x")])
                self.refuses("under the budget" if drift > 0 else "exceeds the budget")

    def test_a_passage_copied_from_the_workflow_into_another_file(self):
        source = (self.root / "references/sd/workflow.md").read_text()
        passage = " ".join(source.split("## Affected documents", 1)[1].split()[:20])
        path = self.root / "skills/validation/principles.md"
        path.write_text(path.read_text() + "\n" + passage.upper() + "\n")
        self.refuses("skills/validation/principles.md: repeats")

    def test_the_known_overlap_is_listed_and_a_new_one_is_not(self):
        self.assertEqual(lint.lint_tree(self.root), [])
        self.change("skills/implementation/principles.md", "\n", "\nIdeation writes no repository file, branch or commit; the design, the criteria and any ADR draft live in the task file.\n")
        self.refuses("skills/implementation/principles.md: repeats")

    def test_cli_exits_one_naming_the_file(self):
        self.change("skills/implementation/principles.md", "<package>/scripts/comment_ratio.py", "comment_ratio.py")
        result = subprocess.run([sys.executable, str(ROOT / "scripts/lint-skills.py"), "--root", str(self.root)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("skills/implementation/principles.md", result.stdout)

    def test_existing_frontmatter_validator_is_used(self):
        path = self.root / "skills/validation/SKILL.md"
        body = path.read_text()
        description = next(line for line in body.splitlines() if line.startswith("description:"))
        path.write_text(body.replace(description, "description:", 1))
        self.refuses("frontmatter:")


if __name__ == "__main__":
    unittest.main(verbosity=2)
