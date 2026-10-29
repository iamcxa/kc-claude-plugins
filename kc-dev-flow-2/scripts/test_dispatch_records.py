import contextlib
import importlib.util
import io
import os
import json
import re
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest

spec = importlib.util.spec_from_file_location("dispatch_records", Path(__file__).with_name("dispatch_records.py"))
records = importlib.util.module_from_spec(spec)
spec.loader.exec_module(records)
records_module = records

gate_spec = importlib.util.spec_from_file_location("delivery_gate", Path(__file__).with_name("delivery_gate.py"))
gate = importlib.util.module_from_spec(gate_spec)
gate_spec.loader.exec_module(gate)

HEAD = "d2c96f5152e51de4efdd0ff78f420b9a0238d874"

COMPLETE = """# task — validation, cycle 1

Dispatched: 2026-10-10; state before dispatch commit 22d372bffe5d6352d65ef7c7520a311596caec3d
Model: sonnet

## Checklist

1. Independent verdict on the exact candidate

## Scope notes

Package root: /abs/kc-dev-flow-2
Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
"""


MAIN_LINE = "Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).\n"


NO_EXTENSIONS = "---\nentity-type: task\n---\n"
LISTS_ROBOREV = "---\nentity-type: task\nextensions: [roborev, codex]\n---\n"

IDENTITY = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
BARE = COMPLETE.replace("1. Independent verdict", "1. Run adr_lint.py. Independent")


class DispatchRecordTests(unittest.TestCase):
    def check(self, files, target=None, readme=NO_EXTENSIONS):
        with tempfile.TemporaryDirectory() as d:
            if readme is not None:
                Path(d, "README.md").write_text(readme)
            folder = Path(d, "task")
            (folder / "dispatch").mkdir(parents=True)
            for name, text in files.items():
                (folder / "dispatch" / name).write_text(text)
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = records.main([str(target(folder) if target else folder)])
            return code, out.getvalue()

    def test_a_complete_record_passes_from_the_folder_or_the_task_file(self):
        self.assertEqual(self.check({"validation-1.md": COMPLETE})[0], 0)
        self.assertEqual(self.check({"validation-1.md": COMPLETE}, lambda f: f.with_suffix(".md"))[0], 0)

    def test_each_missing_part_fails_and_is_named(self):
        cases = {
            "'Dispatched:' line": COMPLETE.replace("22d372bffe5d6352d65ef7c7520a311596caec3d", "22d372bff"),
            "'Model:' line": COMPLETE.replace("Model: sonnet\n", ""),
            "'## Checklist' section": COMPLETE.replace("1. Independent verdict on the exact candidate\n", ""),
            "'## Scope notes' section": COMPLETE.replace("## Scope notes\n\nPackage root: /abs/kc-dev-flow-2\n" + MAIN_LINE, ""),
            "scope-notes line naming main": COMPLETE.replace(MAIN_LINE, ""),
        }
        for part, text in cases.items():
            with self.subTest(part):
                code, out = self.check({"implementation-3.md": text, "validation-1.md": COMPLETE})
                self.assertEqual(code, 1)
                self.assertIn(f"implementation-3.md: needs", out)
                self.assertIn(part, out)
                self.assertNotIn("validation-1.md", out)

    def test_the_completion_recipient_line_is_judged_by_its_recipient_and_its_section(self):
        for line in ("Completion message to `main`.", "completion to `main`", "Send your phase-1 report and your completion message to main."):
            with self.subTest(line):
                self.assertEqual(self.check({"a-1.md": COMPLETE.replace(MAIN_LINE, line + "\n")})[0], 0)
        for label, text in (
                ("team-lead", COMPLETE.replace(MAIN_LINE, "Send completion to team-lead.\n")),
                ("another branch", COMPLETE.replace(MAIN_LINE, "Send your completion message to `main-branch`.\n")),
                ("outside the section", COMPLETE.replace(MAIN_LINE, "").replace("1. Independent", MAIN_LINE + "1. Independent"))):
            with self.subTest(label):
                code, out = self.check({"a-1.md": text})
                self.assertEqual(code, 1)
                self.assertIn("a-1.md: needs a scope-notes line naming main as the completion recipient", out)

    def test_the_package_root_line_must_be_absolute_and_inside_the_scope_notes(self):
        moved = COMPLETE.replace("Package root: /abs/kc-dev-flow-2\n", "").replace("## Checklist\n", "Package root: /abs/kc-dev-flow-2\n## Checklist\n")
        for label, text in (
                ("deleted", COMPLETE.replace("Package root: /abs/kc-dev-flow-2\n", "")),
                ("above the checklist", moved),
                ("relative", COMPLETE.replace("/abs/kc-dev-flow-2", "kc-dev-flow-2/0.21.0"))):
            with self.subTest(label):
                code, out = self.check({"implementation-3.md": text, "validation-1.md": COMPLETE})
                self.assertEqual(code, 1)
                self.assertIn("implementation-3.md: needs a 'Package root:' line with an absolute path in its scope notes", out)
                self.assertNotIn("validation-1.md", out)

    def test_a_checklist_that_only_names_other_records_fails_but_one_citing_a_sibling_beside_real_lines_passes(self):
        pointer = COMPLETE.replace("1. Independent verdict on the exact candidate\n", "Same checklist as validation-1.\n")
        two_lines = COMPLETE.replace("1. Independent verdict on the exact candidate\n", "Same checklist as validation-1.\nSee validation-1 for the items.\n")
        beside_real = COMPLETE.replace("1. Independent verdict on the exact candidate\n",
                                       "1. Repeat the check from validation-1\n2. Independent verdict on the exact candidate\n")
        for label, text in (("one line", pointer), ("two lines", two_lines)):
            with self.subTest(label):
                code, out = self.check({"validation-1.md": COMPLETE, "validation-2.md": text})
                self.assertEqual(code, 1)
                self.assertEqual(out.splitlines(), ["validation-2.md: needs a checklist of its own, not only a reference to another dispatch record"])
        self.assertEqual(self.check({"validation-1.md": COMPLETE, "validation-2.md": beside_real})[0], 0)

    def test_an_action_that_names_a_sibling_record_is_a_checklist_of_its_own(self):
        one_action = "Verify the fix requested in validation-1 satisfies AC-1.\n"
        two_actions = "Verify validation-1 findings are fixed.\nRe-run the replays named in validation-1 and report each result.\n"
        for label, lines in (("one action", one_action), ("two actions", two_actions), ("one verb", "Verify validation-1.\n")):
            with self.subTest(label):
                text = COMPLETE.replace("1. Independent verdict on the exact candidate\n", lines)
                self.assertEqual(self.check({"validation-1.md": COMPLETE, "validation-2.md": text})[0], 0)

    def test_a_pointer_in_other_wording_still_fails_and_a_line_without_a_record_name_or_with_other_words_passes(self):
        for line in ("Identical to validation-1 and validation-3.", "- see validation-1", "The same items as in validation-1"):
            with self.subTest(line):
                text = COMPLETE.replace("1. Independent verdict on the exact candidate\n", line + "\n")
                code, out = self.check({"validation-1.md": COMPLETE, "validation-2.md": text, "validation-3.md": COMPLETE})
                self.assertEqual(code, 1)
                self.assertEqual(out.splitlines(), ["validation-2.md: needs a checklist of its own, not only a reference to another dispatch record"])
        for line in ("Reuse the checklist of validation-1.", "Same items as in the checklist."):
            with self.subTest(line):
                text = COMPLETE.replace("1. Independent verdict on the exact candidate\n", line + "\n")
                self.assertEqual(self.check({"validation-1.md": COMPLETE, "validation-2.md": text})[0], 0)

    def test_a_pointer_may_name_the_record_with_a_path_an_md_suffix_or_a_link(self):
        for line in ("Same checklist as validation-1.md.", "Same checklist as `validation-1.md`.",
                     "Same checklist as [validation-1](validation-1.md).", "Same checklist as [validation-1](./validation-1.md)",
                     "Same checklist as ./dispatch/validation-1.md", "Same checklist as [validation-1](../dispatch/validation-1.md)."):
            with self.subTest(line):
                text = COMPLETE.replace("1. Independent verdict on the exact candidate\n", line + "\n")
                code, out = self.check({"validation-1.md": COMPLETE, "validation-2.md": text})
                self.assertEqual(code, 1)
                self.assertEqual(out.splitlines(), ["validation-2.md: needs a checklist of its own, not only a reference to another dispatch record"])

    def test_a_link_beside_an_action_or_a_longer_file_name_is_not_a_pointer(self):
        for line in ("Verify [validation-1](validation-1.md) findings are fixed.", "Same checklist as my-validation-1.md",
                     "Same checklist as validation-1.mdx"):
            with self.subTest(line):
                text = COMPLETE.replace("1. Independent verdict on the exact candidate\n", line + "\n")
                self.assertEqual(self.check({"validation-1.md": COMPLETE, "validation-2.md": text})[0], 0)

    def test_a_pointer_line_followed_by_a_real_line_is_a_checklist_of_its_own(self):
        text = COMPLETE.replace("1. Independent verdict on the exact candidate\n",
                                "Same checklist as validation-1.\n2. Independent verdict on the exact candidate\n")
        self.assertEqual(self.check({"validation-1.md": COMPLETE, "validation-2.md": text})[0], 0)

    def test_a_record_naming_itself_in_a_pointer_line_is_not_a_pointer(self):
        text = COMPLETE.replace("1. Independent verdict on the exact candidate\n", "Same checklist as validation-2.\n")
        self.assertEqual(self.check({"validation-1.md": COMPLETE, "validation-2.md": text})[0], 0)

    def test_a_record_name_inside_a_longer_name_or_the_records_own_name_is_not_a_pointer(self):
        for line in ("Same as validation-10.", "Continue validation-2 work.", "Re-run my-validation-1 items."):
            with self.subTest(line):
                text = COMPLETE.replace("1. Independent verdict on the exact candidate\n", line + "\n")
                self.assertEqual(self.check({"validation-1.md": COMPLETE, "validation-2.md": text})[0], 0)

    def test_a_task_without_records_fails(self):
        self.assertEqual(self.check({})[0], 1)

    def names(self, text, name="validation-1.md"):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d, "pkg")
            (root / "scripts").mkdir(parents=True)
            (root / "extensions" / "roborev").mkdir(parents=True)
            (root / "scripts" / "adr_lint.py").write_text("")
            (root / "scripts" / "lint-skills.py").write_text("")
            (root / "extensions" / "roborev" / "roborev_gate.py").write_text("")
            record = Path(d, name)
            record.write_text(text)
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = records.main(["--names", str(record)], package=root)
            return code, out.getvalue().replace(str(record), name)

    def test_bare_names_of_scripts_and_extension_scripts_are_listed_with_file_and_line(self):
        text = COMPLETE.replace("1. Independent verdict on the exact candidate\n",
                                "1. Run `roborev_gate.py` and lint-skills.py\n2. Then adr_lint.py, adr_lint.py again\n")
        code, out = self.names(text)
        self.assertEqual(code, 1)
        self.assertEqual(out.splitlines(), [
            "validation-1.md:8: bare package script name roborev_gate.py",
            "validation-1.md:8: bare package script name lint-skills.py",
            "validation-1.md:9: bare package script name adr_lint.py"])

    def test_a_name_with_any_directory_part_or_not_in_the_package_is_not_judged(self):
        text = COMPLETE.replace("1. Independent verdict on the exact candidate\n", (
            "1. Run /abs/pkg/scripts/adr_lint.py, <package>/scripts/adr_lint.py, scripts/adr_lint.py,"
            " ./lint-skills.py and ~/roborev_gate.py\n2. Edit other_tool.py and adr_lint.pyc\n"))
        self.assertEqual(self.names(text), (0, ""))

    def test_only_the_checklist_and_scope_notes_sections_are_scanned_unless_the_file_has_neither(self):
        outside = COMPLETE.replace("# task — validation, cycle 1\n", "# task — validation, cycle 1\nSee adr_lint.py.\n")
        self.assertEqual(self.names(outside), (0, ""))
        later = COMPLETE + "\n## Notes\nadr_lint.py\n"
        self.assertEqual(self.names(later), (0, ""))
        self.assertEqual(self.names("Run adr_lint.py\n"), (1, "validation-1.md:1: bare package script name adr_lint.py\n"))

    def test_names_asks_for_a_candidate_line_in_a_validation_record_exactly_as_the_merge_gate_reads_it(self):
        def run(name, text, folder="dispatch"):
            with tempfile.TemporaryDirectory() as d:
                task = Path(d, "task.md")
                path = Path(d, "task", folder, name)
                path.parent.mkdir(parents=True)
                path.write_text(text)
                with contextlib.redirect_stdout(io.StringIO()) as out:
                    code = records.main(["--names", str(path)])
                found = gate.dispatched_candidates(task)[0] if folder == "dispatch" and name == "validation-1.md" else None
                return code, out.getvalue().replace(str(path), name), found

        want = "validation-1.md:1: no 'Candidate: <40-hex head>' line; add one per head to validate above the first '## ' heading, then run this check again\n"
        self.assertEqual(run("validation-1.md", COMPLETE)[:2], (1, want))
        with_line = COMPLETE.replace("Model: sonnet\n", f"Model: sonnet\nCandidate: {HEAD}\n")
        self.assertEqual(run("validation-1.md", with_line)[:2], (0, ""))
        for name, folder in (("implementation-1.md", "dispatch"), ("ideation-1.md", "dispatch"), ("validation-1.md", "elsewhere"),
                             ("validation-x.md", "dispatch")):
            self.assertEqual(run(name, COMPLETE, folder)[:2], (0, ""), (name, folder))
        for label, line in (("40-hex", f"Candidate: {HEAD}"), ("39-hex", f"Candidate: {HEAD[:39]}"),
                            ("uppercase", f"Candidate: {HEAD.upper()}"), ("trailing text", f"Candidate: {HEAD} head"),
                            ("trailing space", f"Candidate: {HEAD}  ")):
            with self.subTest(label):
                code, _, found = run("validation-1.md", COMPLETE.replace("Model: sonnet\n", f"Model: sonnet\n{line}\n"))
                self.assertEqual(code == 0, bool(found))
        below = COMPLETE + f"\nCandidate: {HEAD}\n"
        code, _, found = run("validation-1.md", below)
        self.assertEqual((code, bool(found)), (1, False))

    def test_the_default_mode_does_not_scan_names(self):
        bare = COMPLETE.replace("1. Independent", "1. Run adr_lint.py. Independent")
        self.assertEqual(self.check({"validation-1.md": bare})[0], 0)

    def test_names_runs_against_the_real_package_and_needs_a_file(self):
        with tempfile.TemporaryDirectory() as d:
            record = Path(d, "r.md")
            record.write_text("## Checklist\n\nrun roborev_gate.py\n")
            with contextlib.redirect_stdout(io.StringIO()) as out:
                self.assertEqual(records.main(["--names", str(record)]), 1)
            self.assertIn("bare package script name roborev_gate.py", out.getvalue())
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(records.main(["--names"]), 2)

    def test_wrong_arguments_are_a_usage_error(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(records.main([]), 2)
            for args in (["--newest"], ["--newest", "state"], ["--newest", "a", "b", "c"]):
                self.assertEqual(records.main(args), 2, args)


GUARDS = "\n## Number guards\n\nADR: 0020\nMigration: 0007\n"
AMENDMENTS = ("\n## Captain amendments\n\n### Amendment 1 \u2014 2026-10-17, chat\nCaptain: x\nSupersedes: none\n\n"
              "### Amendment 2 \u2014 2026-10-18, chat\nCaptain: y\nSupersedes: none\n")
NOTES_WITH_BOTH = COMPLETE.replace("Package root:", "ADR: 0020\nMigration: 0007\nPackage root:")


class TaskFactTests(unittest.TestCase):
    def run_names(self, task, records, target="implementation-1.md", folder="task", index=False, module=None):
        with tempfile.TemporaryDirectory() as d:
            if task is not None:
                entry = Path(d, folder, "index.md") if index else Path(d, f"{folder}.md")
                entry.parent.mkdir(parents=True, exist_ok=True)
                entry.write_text(f"---\nprofile: pilot\n---\n\n# task\n{task}")
            for name, text in records.items():
                Path(d, folder, "dispatch", name).parent.mkdir(parents=True, exist_ok=True)
                Path(d, folder, "dispatch", name).write_text(text)
            with contextlib.redirect_stdout(io.StringIO()) as out:
                code = (module or records_module).main(["--names", str(Path(d, folder, "dispatch", target))])
            return code, out.getvalue().replace(d + "/", "").splitlines()

    def test_a_first_implementation_record_must_carry_each_reserved_line_in_its_scope_notes(self):
        code, out = self.run_names(GUARDS, {"implementation-1.md": COMPLETE})
        self.assertEqual(code, 1)
        self.assertEqual([line.split(";")[0] for line in out], [
            "task/dispatch/implementation-1.md:1: reserved line 'ADR: 0020' missing from scope notes",
            "task/dispatch/implementation-1.md:1: reserved line 'Migration: 0007' missing from scope notes"])
        self.assertEqual(self.run_names(GUARDS, {"implementation-1.md": NOTES_WITH_BOTH}), (0, []))
        short = COMPLETE.replace("Package root:", "ADR: 20\nMigration: 7\nPackage root:")
        self.assertEqual(self.run_names(GUARDS, {"implementation-1.md": short}), (0, []))

    def test_a_folder_task_is_judged_for_reserved_lines_like_a_flat_task(self):
        flat = self.run_names(GUARDS, {"implementation-1.md": COMPLETE})
        self.assertEqual(flat[0], 1)
        self.assertEqual(self.run_names(GUARDS, {"implementation-1.md": COMPLETE}, index=True), flat)
        self.assertEqual(self.run_names(GUARDS, {"implementation-1.md": NOTES_WITH_BOTH}, index=True), (0, []))

    def test_a_folder_task_given_by_index_names_its_dispatch_records(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d, "task", "dispatch").mkdir(parents=True)
            Path(d, "task", "index.md").write_text("---\nprofile: pilot\n---\n")
            Path(d, "task", "dispatch", "implementation-1.md").write_text(COMPLETE)
            with contextlib.redirect_stdout(io.StringIO()) as out:
                records_module.main([str(Path(d, "task", "index.md"))])
            self.assertNotIn("no dispatch records", out.getvalue())

    def test_a_reserved_number_named_only_outside_the_scope_notes_or_inside_a_longer_number_is_missing(self):
        in_checklist = COMPLETE.replace("1. Independent", "1. ADR: 0020 and Migration: 0007. Independent")
        self.assertEqual(self.run_names(GUARDS, {"implementation-1.md": in_checklist})[0], 1)
        longer = COMPLETE.replace("Package root:", "ADR: 0200\nMigration: 0070\nPackage root:")
        self.assertEqual(len(self.run_names(GUARDS, {"implementation-1.md": longer})[1]), 2)

    def test_a_reserved_number_named_inside_a_prose_line_is_missing_and_the_line_forms_FO_writes_pass(self):
        prose = COMPLETE.replace("Package root:", "This does not use ADR: 0020 or Migration: 0007 because it is unrelated.\nPackage root:")
        code, out = self.run_names(GUARDS, {"implementation-1.md": prose})
        self.assertEqual((code, len(out)), (1, 2))
        for notes in ("- ADR: 0020\n- Migration: 0007", "ADR: 0020 (reserved; write docs/adr/0020-x.md)\nMigration: 0007",
                      "Number guards: ADR: 0020\nMigration: 0007", "  ADR: 0020\n\tMigration: 0007"):
            with self.subTest(notes):
                record = COMPLETE.replace("Package root:", notes + "\nPackage root:")
                self.assertEqual(self.run_names(GUARDS, {"implementation-1.md": record}), (0, []))

    def test_only_the_first_implementation_record_of_a_task_with_a_task_file_is_judged_for_reserved_lines(self):
        self.assertEqual(self.run_names(GUARDS, {"implementation-2.md": COMPLETE}, "implementation-2.md"), (0, []))
        self.assertEqual(self.run_names(GUARDS, {"ideation-1.md": COMPLETE}, "ideation-1.md"), (0, []))
        self.assertEqual(self.run_names(None, {"implementation-1.md": COMPLETE}), (0, []))
        self.assertEqual(self.run_names("", {"implementation-1.md": COMPLETE}), (0, []))

    def test_a_captain_amendment_must_be_named_in_a_checklist_of_the_task_this_record_included(self):
        code, out = self.run_names(AMENDMENTS, {"implementation-1.md": COMPLETE})
        self.assertEqual(code, 1)
        self.assertEqual([line.split(";")[0] for line in out], [
            "task/dispatch/implementation-1.md:1: Captain amendment 1 named in no dispatch checklist",
            "task/dispatch/implementation-1.md:1: Captain amendment 2 named in no dispatch checklist"])
        names_one = COMPLETE.replace("1. Independent", "1. Captain amendment 1. Independent")
        code, out = self.run_names(AMENDMENTS, {"implementation-1.md": names_one})
        self.assertEqual((code, len(out)), (1, 1))
        both = COMPLETE.replace("1. Independent", "1. Captain amendments 1 and 2. Independent")
        self.assertEqual(self.run_names(AMENDMENTS, {"implementation-1.md": both}), (0, []))
        earlier = {"implementation-1.md": names_one, "implementation-2.md": COMPLETE.replace("1. Independent", "1. Amendment 2. Independent")}
        self.assertEqual(self.run_names(AMENDMENTS, earlier, "implementation-2.md"), (0, []))

    def test_an_amendment_list_with_an_oxford_comma_names_every_number(self):
        for phrase in ("Captain amendments 1, 2, and 3", "Captain amendments 1, 2 and 3", "Captain amendments 1 and 2", "Captain amendments 1, 2"):
            with self.subTest(phrase):
                three = AMENDMENTS + "\n### Amendment 3 \u2014 2026-10-19\nCaptain: z\nSupersedes: none\n"
                rec = COMPLETE.replace("1. Independent", f"1. {phrase}. Independent")
                code, out = self.run_names(three, {"implementation-1.md": rec})
                expected = 0 if phrase.endswith("3") else 1
                self.assertEqual(code, expected, out)

    def test_an_amendment_named_outside_a_checklist_or_by_a_bare_number_is_unnamed(self):
        in_notes = COMPLETE.replace("Package root:", "Captain amendment 1 and 2.\nPackage root:")
        self.assertEqual(len(self.run_names(AMENDMENTS, {"implementation-1.md": in_notes})[1]), 2)
        plain = COMPLETE.replace("1. Independent", "1. Items 1 and 2 of the list. Independent")
        self.assertEqual(len(self.run_names(AMENDMENTS, {"implementation-1.md": plain})[1]), 2)

    def test_the_amendments_heading_is_read_like_design_surfaces_does_and_fenced_entries_are_skipped(self):
        for heading in ("## CAPTAIN AMENDMENTS", " ## Captain amendments"):
            with self.subTest(heading):
                code, _ = self.run_names(AMENDMENTS.replace("## Captain amendments", heading), {"implementation-1.md": COMPLETE})
                self.assertEqual(code, 1)
        fenced = "\n## Captain amendments\n\n```\n### Amendment 1 \u2014 2026-10-17\n```\n"
        self.assertEqual(self.run_names(fenced, {"implementation-1.md": COMPLETE}), (0, []))
        self.assertTrue(any("outside" in line for line in self.run_names("\n## Notes\n\n### Amendment 1 \u2014 2026-10-17\n", {"implementation-1.md": COMPLETE})[1]))

    def test_an_archived_task_folder_is_judged_beside_its_own_task_file(self):
        code, out = self.run_names(AMENDMENTS, {"implementation-1.md": COMPLETE}, folder="_archive/task")
        self.assertEqual(code, 1)
        self.assertEqual(len(out), 2)

    def test_an_ideation_record_is_refused_when_its_task_owes_a_result_line(self):
        needed = "\n## FO alignment\n\nAlignment: needed before ideation: which checks run where.\nSurfaces: none\n"
        code, out = self.run_names(needed, {"ideation-1.md": COMPLETE}, "ideation-1.md")
        self.assertEqual(code, 1)
        self.assertEqual([line.split(";")[0] for line in out],
                         ["task/dispatch/ideation-1.md:1: '## FO alignment' records alignment as needed with no 'Result:' line"])
        cases = {"result recorded": needed.replace("Surfaces:", "Result: aligned by his answer.\nSurfaces:"),
                 "alignment not needed": needed.replace("needed before ideation: which checks run where", "not needed"),
                 "alignment line only in a fence": "\n## FO alignment\n\n```\nAlignment: needed\n```\nSurfaces: none\n",
                 "another spelling": "\n## FO alignment\n\nNeeded at ideation: yes.\nSurfaces: none\n"}
        for label, task in cases.items():
            with self.subTest(label):
                self.assertEqual(self.run_names(task, {"ideation-1.md": COMPLETE}, "ideation-1.md"), (0, []))
        self.assertEqual(self.run_names(needed, {"implementation-1.md": COMPLETE}), (0, []))

    def test_mutation_dropping_the_result_check_lets_the_record_pass(self):
        needed = "\n## FO alignment\n\nAlignment: needed before ideation: x.\n"
        source = Path(__file__).with_name("dispatch_records.py").read_text()
        old = " and alignment_owes_result(text):"
        self.assertEqual(source.count(old), 1)
        mutant = types.ModuleType("dispatch_records_mutant")
        mutant.__file__ = str(Path(__file__).with_name("dispatch_records.py"))
        exec(compile(source.replace(old, " and False:"), mutant.__file__, "exec"), mutant.__dict__)
        self.assertEqual(self.run_names(needed, {"ideation-1.md": COMPLETE}, "ideation-1.md")[0], 1)
        self.assertEqual(self.run_names(needed, {"ideation-1.md": COMPLETE}, "ideation-1.md", module=mutant)[0], 0)

    def test_a_backslash_quote_on_an_amendment_line_is_refused_unless_it_sits_in_a_moved_criterion(self):
        named = COMPLETE.replace("1. Independent", "1. Captain amendment 1. Independent")
        task = "\n## Captain amendments\n\n### Amendment 1 \u2014 2026-10-17, chat\nCaptain: x\nAsked: {asked}\nSupersedes: none\n{tail}"
        code, out = self.run_names(task.format(asked='he said \\"yes\\"', tail=""), {"implementation-1.md": named})
        self.assertEqual((code, [line.split(";")[0] for line in out]),
                         (1, ["task/dispatch/implementation-1.md:1: Captain amendment 1 Asked line holds a backslash-quote copied from JSON"]))
        moved = task.format(asked="he said yes", tail='Superseded text:\n**AC-1**: a \\"quoted\\" word.\n')
        self.assertEqual(self.run_names(moved, {"implementation-1.md": named}), (0, []))
        self.assertEqual(self.run_names(task.format(asked="he said yes", tail=""), {"implementation-1.md": named}), (0, []))
        for other in ('Design: the \\"old\\" paragraph.\n', 'a continuation with \\"x\\"\n'):
            with self.subTest(other):
                self.assertEqual(self.run_names(task.format(asked="he said yes", tail=other), {"implementation-1.md": named}), (0, []))


ROBOREV_PATH = "/abs/kc-dev-flow-2/extensions/roborev/roborev_gate.py"


class ExtensionInstructionTests(unittest.TestCase):
    def run_main(self, folder, *flags):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = records.main([*flags, str(folder)])
        return code, out.getvalue()

    def check(self, files, readme=LISTS_ROBOREV, flags=()):
        with tempfile.TemporaryDirectory() as d:
            if readme is not None:
                Path(d, "README.md").write_text(readme)
            folder = Path(d, "task")
            (folder / "dispatch").mkdir(parents=True)
            for name, text in files.items():
                (folder / "dispatch" / name).write_text(text)
            return self.run_main(folder, *flags)

    def test_a_first_implementation_record_without_the_instruction_fails_and_names_the_extension(self):
        code, out = self.check({"implementation-1.md": COMPLETE})
        self.assertEqual(code, 1)
        self.assertIn("implementation-1.md: roborev worker instruction is absent", out)
        self.assertIn("EXTENSION.md", out)

    def test_the_root_substituted_path_or_a_not_run_reason_passes(self):
        for line in (f"Before reporting, run python3 {ROBOREV_PATH} --repo w --base b",
                     f"`python3 {ROBOREV_PATH}`", "roborev not run: the daemon is down on this machine"):
            with self.subTest(line):
                self.assertEqual(self.check({"implementation-1.md": COMPLETE + line + "\n"})[0], 0)
        under_checklist = COMPLETE.replace("1. Independent", f"python3 {ROBOREV_PATH}\n1. Independent")
        self.assertEqual(self.check({"implementation-1.md": under_checklist})[0], 0)

    def test_the_placeholder_the_bare_name_and_an_empty_reason_each_fail(self):
        absent, placeholder = "worker instruction is absent", "worker instruction has an unsubstituted <package>"
        cases = [
            ("python3 <package>/extensions/roborev/roborev_gate.py --repo w", placeholder),
            ("python3 roborev_gate.py --repo w", absent),
            ("roborev not run:", absent),
            (f"python3 x{ROBOREV_PATH}", absent),
        ]
        for line, message in cases:
            with self.subTest(line):
                code, out = self.check({"implementation-1.md": COMPLETE + line + "\n"})
                self.assertEqual(code, 1)
                self.assertIn(message, out)
                self.assertNotIn(placeholder if message == absent else absent, out)

    def test_a_path_that_continues_past_the_script_name_is_absent_and_one_that_ends_there_passes(self):
        for tail in (".bak", "x", "-old", "~", ".orig"):
            with self.subTest(tail):
                code, out = self.check({"implementation-1.md": COMPLETE + f"python3 {ROBOREV_PATH}{tail} --repo w\n"})
                self.assertEqual(code, 1)
                self.assertIn("worker instruction is absent", out)
        for tail in (".", ",", "`", ")", "\"", ""):
            with self.subTest(repr(tail)):
                text = COMPLETE + f"Run ({ROBOREV_PATH}{tail} then report\n"
                self.assertEqual(self.check({"implementation-1.md": text})[0], 0)

    def test_only_listed_followers_end_the_script_path(self):
        for tail in ("/extra", "/", ":", ";", "=", "]", "}", ">", "|", "&", "\\", "#", "?", "!", "....", "'x", "`)x", ".)x"):
            with self.subTest(tail):
                code, out = self.check({"implementation-1.md": COMPLETE + f"python3 {ROBOREV_PATH}{tail} --repo w\n"})
                self.assertEqual(code, 1)
                self.assertIn("worker instruction is absent", out)
        for tail in (" ", "\t", ".", ",", "`", ")", "\"", "'", "..", "`)", ".)", ".,", "`).", "\"`)"):
            with self.subTest(repr(tail)):
                text = COMPLETE + f"Run ({ROBOREV_PATH}{tail} then report\n"
                self.assertEqual(self.check({"implementation-1.md": text})[0], 0)
        for ending in ("", "\n", ".", ".\n"):
            with self.subTest(repr(ending)):
                self.assertEqual(self.check({"implementation-1.md": COMPLETE + f"Run {ROBOREV_PATH}{ending}"})[0], 0)

    def test_journey_map_and_release_acceptance_stay_quiet_without_an_acceptance_instruction(self):
        readme = "---\nentity-type: task\nextensions: [learn, peers, journey-map, release-acceptance, codex]\n---\n"
        code, out = self.check({"implementation-1.md": COMPLETE}, readme=readme)
        self.assertEqual(code, 0, out)
        self.assertNotIn("journey-map", out)
        self.assertNotIn("release-acceptance", out)
        for name in ("journey-map", "release-acceptance"):
            text = Path(records.PACKAGE, "extensions", name, "EXTENSION.md").read_text()
            self.assertIn("under `docs/journey/`; ", text)

    def test_release_acceptance_turns_loud_when_its_bullet_carries_the_instruction_label(self):
        readme = "---\nentity-type: task\nextensions: [release-acceptance]\n---\n"
        source = Path(records.PACKAGE, "extensions", "release-acceptance", "EXTENSION.md").read_text()
        label = "- **Acceptance task's implementation scope notes:** FO adds"
        self.assertIn(label, source)
        loud = source.replace(label, "- **Joins:** implementation\n- **Instruction FO adds to the scope notes:** "
                                     "run python3 <package>/extensions/release-acceptance/release_acceptance.py; FO adds", 1)
        with tempfile.TemporaryDirectory() as d:
            package = Path(d, "pkg")
            (package / "extensions" / "release-acceptance").mkdir(parents=True)
            (package / "extensions" / "release-acceptance" / "EXTENSION.md").write_text(loud)
            Path(d, "README.md").write_text(readme)
            folder = Path(d, "task")
            (folder / "dispatch").mkdir(parents=True)
            (folder / "dispatch" / "implementation-1.md").write_text(COMPLETE)
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = records.main([str(folder)], package=package)
        self.assertEqual(code, 1)
        self.assertIn("release-acceptance worker instruction is absent", out.getvalue())

    def test_an_unlisted_extension_is_not_checked(self):
        self.assertEqual(self.check({"implementation-1.md": COMPLETE}, readme=NO_EXTENSIONS)[0], 0)
        self.assertEqual(self.check({"implementation-1.md": COMPLETE}, readme="---\nentity-type: task\nextensions: [codex]\n---\n")[0], 0)

    def test_a_validation_record_without_the_instruction_is_not_checked(self):
        complete = COMPLETE + f"python3 {ROBOREV_PATH}\n"
        self.assertEqual(self.check({"implementation-1.md": complete, "validation-1.md": COMPLETE})[0], 0)
        self.assertEqual(self.check({"validation-1.md": COMPLETE})[0], 0)

    def test_a_later_implementation_record_without_the_instruction_is_not_checked(self):
        complete = COMPLETE + f"python3 {ROBOREV_PATH}\n"
        self.assertEqual(self.check({"implementation-1.md": complete, "implementation-2.md": COMPLETE})[0], 0)

    def test_every_shipped_instruction_is_read_from_its_extension_file(self):
        shipped = [p.name for p in Path(records.PACKAGE, "extensions").iterdir() if p.is_dir()]
        found = {name: (stage, paths) for name, stage, paths in records.declared_instructions(records.PACKAGE, shipped)}
        self.assertEqual(found["roborev"], ("implementation", ["extensions/roborev/roborev_gate.py"]))
        for name in shipped:
            text = Path(records.PACKAGE, "extensions", name, "EXTENSION.md").read_text()
            self.assertEqual("Instruction FO adds" in text, name in found, name)

    def test_no_readme_is_said_not_skipped_and_leaves_the_exit_code_alone(self):
        code, out = self.check({"implementation-1.md": COMPLETE}, readme=None)
        self.assertEqual(code, 0)
        self.assertRegex(out, r"extensions not checked: no workflow README above \S+task")
        self.assertIn("1 dispatch record(s) complete", out)
        self.assertEqual(self.check({"implementation-1.md": COMPLETE.replace("Model: sonnet\n", "")}, readme=None)[0], 1)

    def test_the_nearest_readme_with_an_entity_type_is_used_and_a_plain_one_is_skipped(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d, "README.md").write_text(LISTS_ROBOREV)
            folder = Path(d, "state", "_archive", "task")
            (folder / "dispatch").mkdir(parents=True)
            (folder / "dispatch" / "implementation-1.md").write_text(COMPLETE)
            Path(d, "state", "README.md").write_text("# not a workflow README\n")
            code, out = self.run_main(folder)
        self.assertEqual(code, 1)
        self.assertIn("roborev worker instruction is absent", out)

    def test_readme_flag_supplies_the_file_and_a_missing_path_exits_2(self):
        with tempfile.TemporaryDirectory() as d:
            readme = Path(d, "elsewhere.md")
            readme.write_text(LISTS_ROBOREV)
            folder = Path(d, "a", "task")
            (folder / "dispatch").mkdir(parents=True)
            (folder / "dispatch" / "implementation-1.md").write_text(COMPLETE)
            code, out = self.run_main(folder, "--readme", str(readme))
            self.assertEqual(code, 1)
            self.assertIn("roborev worker instruction is absent", out)
            self.assertNotIn("not checked", out)
            code, out = self.run_main(folder, "--readme", str(Path(d, "missing.md")))
            self.assertEqual(code, 2)
            self.assertIn("no such file", out)
            self.assertEqual(self.run_main(folder, "--readme")[0], 2)


class NewestTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.state = Path(tmp.name, "state")
        self.state.mkdir()
        self.git("init", "-q", "-b", "main")

    def git(self, *args):
        done = subprocess.run(["git", "-C", str(self.state), *args], capture_output=True, text=True, env={**os.environ, **IDENTITY})
        self.assertEqual(done.returncode, 0, done.stderr)

    def commit(self, slug, name, text):
        path = self.state / slug / "dispatch" / f"{name}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        self.git("add", "-A")
        self.git("commit", "-qm", f"{slug} {name}")

    def newest(self, slug="task", state=None):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = records.main(["--newest", str(state or self.state), slug])
        return code, out.getvalue().replace(str(self.state), "STATE")

    def test_the_newest_record_is_scanned_and_its_lines_are_printed(self):
        self.commit("task", "implementation-2", BARE)
        self.assertEqual(self.newest(), (1, "STATE/task/dispatch/implementation-2.md:8: bare package script name adr_lint.py\n"))

    def test_an_older_bare_record_is_not_reported_once_a_newer_one_is_clean(self):
        self.commit("task", "implementation-1", BARE)
        self.commit("task", "implementation-2", COMPLETE)
        self.assertEqual(self.newest(), (0, ""))

    def test_a_newer_bare_record_is_reported_over_an_older_clean_one_and_other_tasks_are_ignored(self):
        self.commit("task", "implementation-1", COMPLETE)
        self.commit("other", "implementation-1", BARE)
        self.commit("task", "validation-1", BARE)
        self.commit("other", "validation-1", COMPLETE)
        code, out = self.newest()
        self.assertEqual((code, out.count("\n")), (1, 1))
        self.assertIn("task/dispatch/validation-1.md:8:", out)

    def test_the_file_is_read_as_it_is_on_disk_not_as_committed(self):
        self.commit("task", "implementation-1", BARE)
        (self.state / "task/dispatch/implementation-1.md").write_text(COMPLETE)
        self.assertEqual(self.newest(), (0, ""))

    def test_a_validation_record_without_a_candidate_line_is_not_reported_as_newest(self):
        self.commit("task", "validation-1", COMPLETE)
        self.assertEqual(self.newest(), (0, ""))

    def test_a_task_without_records_exits_clean_and_an_unreadable_state_exits_2(self):
        self.commit("other", "implementation-1", BARE)
        self.assertEqual(self.newest("task"), (0, ""))
        with tempfile.TemporaryDirectory() as plain:
            code, out = self.newest(state=plain)
        self.assertEqual(code, 2)
        self.assertIn("git cannot read the dispatch records", out)



WORKFLOW = """---
entity-type: task
stages:
  states:
    - name: backlog
      initial: true
    - name: ideation
    - name: implementation
    - name: validation
    - name: done
      terminal: true
---
"""


class CoverageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.readme = self.root / "README.md"
        self.readme.write_text(WORKFLOW)
        self.task = self.root / "task.md"
        self.task.write_text("## Stage Report: implementation\n")
        self.folder = self.root / "task"

    def run_cli(self, stage="implementation", task=None, extra=()):
        done = subprocess.run([sys.executable, "-B", str(Path(records.__file__)),
                               "--coverage", str(task or self.task), "--stage", stage, *extra],
                              text=True, capture_output=True)
        self.assertEqual(done.stderr, "")
        return done.returncode, done.stdout

    def record(self, name):
        dispatch = self.folder / "dispatch"
        dispatch.mkdir(parents=True, exist_ok=True)
        (dispatch / name).write_text(COMPLETE)

    def test_historical_064e61a15_redacted_replay_stops_before_advancement_and_gate(self):
        self.task.write_text("## Stage Report: implementation\n\n## Stage Report: validation\n")
        self.record("ideation-1.md")
        self.record("ideation-2.md")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(records.main([str(self.task)]), 0)
        self.assertEqual(out.getvalue(), "2 dispatch record(s) complete\n")
        for stage, action in (("implementation", "advance"), ("validation", "prepare gate")):
            calls = []
            code, output = self.run_cli(stage)
            if code == 0:
                calls.append(action)
            self.assertEqual(calls, [])
            self.assertEqual(code, 1)
            self.assertIn(f"no dispatch record for completed {stage}; hold advancement and gate preparation", output)
            self.record(f"{stage}-1.md")
            code, output = self.run_cli(stage)
            if code == 0:
                calls.append(action)
            self.assertEqual(calls, [action])
            self.assertEqual(output, f"dispatch coverage complete: {stage}\n")

    def test_fences_exact_stage_and_no_report(self):
        for body in ("", "## Stage Report: implementation-extra\n",
                     "```md\n## Stage Report: implementation\n```\n",
                     "~~~md\n## Stage Report: implementation\n~~~\n",
                     "## Stage Report: ideation\n"):
            self.task.write_text(body)
            self.assertEqual(self.run_cli(), (0, "dispatch coverage not due: implementation\n"))

    def test_both_layouts_and_message_record_do_not_count_repaired_reports(self):
        self.record("implementation-2-message-1.md")
        body = "## Stage Report: implementation (cycle 3)\n## Stage Report: implementation\n"
        for task in (self.task, self.folder / "index.md"):
            task.write_text(body)
            self.assertEqual(self.run_cli(task=task), (0, "dispatch coverage complete: implementation\n"))
        self.task.write_text("## Stage Report: ideation\n## Stage Report: validation\n")
        self.record("validation-1.md")
        self.assertEqual(self.run_cli("validation")[0], 0)

    def test_invalid_record_names_and_directory_do_not_cover(self):
        for name in ("implementation-0.md", "implementation-01.md", "implementation-1-message-0.md",
                     "implementation-other-1.md", "validation-1.md", "implementation-1.txt"):
            self.record(name)
        (self.folder / "dispatch/implementation-9.md").mkdir()
        self.assertEqual(self.run_cli()[0], 1)

    def test_invalid_stage_missing_or_unreadable_task_and_workflow_are_errors(self):
        for stage in ("backlog", "done", "unknown", "implementation-extra"):
            self.assertEqual(self.run_cli(stage)[0], 2)
        self.assertEqual(self.run_cli(task=self.root / "missing.md")[0], 2)
        self.task.write_bytes(b"\xff")
        self.assertEqual(self.run_cli()[0], 2)
        self.task.write_text("")
        self.readme.write_text("no workflow")
        self.assertEqual(self.run_cli(extra=("--readme", str(self.readme)))[0], 2)

    def test_poc_rejects_ideation_and_override_reads_without_mutation(self):
        self.readme.write_text(WORKFLOW.replace("    - name: ideation\n", ""))
        self.assertEqual(self.run_cli("ideation")[0], 2)
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(self.run_cli(extra=("--readme", str(self.readme)))[0], 1)
        self.assertEqual(before, {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()})




class AmendmentDispatchFormTests(unittest.TestCase):
    run_names = TaskFactTests.run_names

    def test_form_errors_have_record_and_task_locations_without_worker_move_checks(self):
        text = "\n## Number guards\n### Amendment 1 — 2026-10-29\nCaptain: x\nSupersedes: AC-1 to AC-3\n"
        code, out = self.run_names(text, {"implementation-1.md": COMPLETE})
        self.assertEqual(code, 1)
        self.assertTrue(any("implementation-1.md:1: Captain amendment form at task.md:" in line and "outside" in line for line in out), out)
        valid = text.replace("## Number guards", "## Captain amendments").replace("AC-1 to AC-3", "AC-1, AC-2 and AC-3")
        code, out = self.run_names(valid, {"implementation-1.md": COMPLETE.replace("1. Independent", "1. Captain amendment 1. Independent")})
        self.assertEqual((code, out), (0, []))


REPORT = "## Stage Report: validation\n\n### Findings\n\n- **F1** Needs decision: Captain must settle scope.\n"
AMENDMENT = "\n## Captain amendments\n\n### Amendment 1 — 2026-10-29, chat\nCaptain: 「同意」\nAsked: May validation run again?\nSupersedes: none\n"


def native_ruling(slug="task", stage="validation", actor="person:captain", kind="resolution", reason="Proceed", at="2026-10-29"):
    return ("gates:\n  records:\n    - stage: " + stage + "\n      attempts:\n"
            f"        - id: gate-attempt:{slug}-{stage}-1\n          {kind}:\n"
            f"            by: {actor}\n            at: {at}\n            reason: {reason}\n            decision: hold\n")


class LiveValidationRulingTests(unittest.TestCase):
    def setUp(self):
        import shutil
        self.shutil = shutil
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.fixture_number = 0
        self.new_state()

    def new_state(self, body=REPORT, native="", slug="task"):
        self.fixture_number += 1
        self.root = Path(self.tmp.name, f"state-{self.fixture_number}")
        self.root.mkdir()
        self.git("init", "-b", "main")
        self.task = self.root / f"{slug}.md"
        self.record = self.root / slug / "dispatch/validation-2.md"
        self.record.parent.mkdir(parents=True)
        self.record.write_text(COMPLETE.replace("Model:", f"Candidate: {HEAD}\nModel:"))
        self.save(body, native)
        self.commit("report")

    def git(self, *args, root=None):
        done = subprocess.run(["git", "-C", str(root or self.root), *args], capture_output=True, text=True,
                              env={**os.environ, **IDENTITY, "GIT_CONFIG_GLOBAL": os.devnull,
                                   "GIT_CONFIG_SYSTEM": os.devnull})
        self.assertEqual(done.returncode, 0, done.stderr)
        return done.stdout.strip()

    def save(self, body, native=""):
        self.task.write_text("---\ntitle: task\nprofile: pilot\n" + native + "---\n\n" + body)

    def commit(self, message):
        self.git("add", "--", ".")
        self.git("commit", "-m", message)
        return self.git("rev-parse", "HEAD")

    def cli(self, *files, mode="--names", cwd=None):
        done = subprocess.run([sys.executable, "-B", str(Path(records.__file__)), mode,
                               *map(str, files or (self.record,))], capture_output=True, text=True, cwd=cwd,
                              env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        return done.returncode, done.stdout + done.stderr

    def assert_hold(self, code=1):
        result, out = self.cli()
        self.assertEqual(result, code, out)
        self.assertIn("hold dispatch", out)
        return out

    def test_fresh_followup_and_filename_one_hold_then_native_ruling_clears_without_input_edits(self):
        for name in ("validation-2.md", "validation-2-message-1.md", "validation-1.md"):
            self.record = self.record.with_name(name)
            self.record.write_text(COMPLETE.replace("Model:", f"Candidate: {HEAD}\nModel:"))
            before = self.record.read_bytes()
            self.assert_hold()
            self.assertEqual(self.record.read_bytes(), before)
        self.save(REPORT, native_ruling())
        self.commit("Captain ruling")
        self.assertEqual(self.cli(), (0, ""))
        self.assertEqual(self.record.read_bytes(), before)

    def test_freeform_then_on_touch_amendment_and_partial_supported_ruling(self):
        freeform = "\n## Feedback Cycles\nCaptain: 「同意」 answering May validation run again?\n"
        self.save(REPORT + freeform)
        self.commit("legacy authority")
        self.assert_hold()
        self.save(REPORT + freeform + AMENDMENT)
        self.commit("record verified original words on touch")
        self.record.write_text(self.record.read_text().replace("Independent verdict", "Captain amendment 1; Independent verdict"))
        self.assertEqual(self.cli(), (0, ""))
        partial = AMENDMENT.replace("May validation run again?", "Only F3's site ceiling?")
        self.save(REPORT + "\n- F4 Needs decision: another choice.\n" + partial)
        self.commit("new report")
        self.assert_hold(2)

    def test_supported_partial_reply_clears_structure_with_semantics_left_to_observer(self):
        self.new_state(REPORT + "- F4 Needs decision: unrelated product choice.\n")
        self.save(REPORT + "- F4 Needs decision: unrelated product choice.\n" + AMENDMENT.replace("May validation run again?", "Only F1?"))
        self.commit("partial Captain reply")
        self.record.write_text(self.record.read_text().replace("Independent verdict", "Captain amendment 1; Independent verdict"))
        self.assertEqual(self.cli(), (0, ""))

    def test_old_and_same_commit_rulings_do_not_clear(self):
        for where in ("old", "same"):
            with self.subTest(where=where):
                base = REPORT if where == "same" else "## Scope\nWork\n"
                self.new_state(base, native_ruling())
                if where == "old":
                    self.save(REPORT, native_ruling())
                    self.commit("report after ruling")
                self.assert_hold()

    def test_edited_old_gate_or_amendment_keeps_its_original_identity(self):
        for amendment in (False, True):
            with self.subTest(amendment=amendment):
                original = AMENDMENT if amendment else ""
                self.new_state("## Scope\nWork\n" + original, "" if amendment else native_ruling(reason="old"))
                self.save(REPORT + original, "" if amendment else native_ruling(reason="old"))
                self.commit("report")
                self.save(REPORT + original.replace("「同意」", "「重跑」"),
                          "" if amendment else native_ruling(reason="rerun"))
                self.commit("edit old entry")
                self.record.write_text(self.record.read_text().replace("Independent verdict", "Captain amendment 1; Independent verdict"))
                self.assert_hold()

    def test_other_stage_task_actor_empty_reason_time_and_withdrawal_do_not_clear(self):
        cases = [
            native_ruling(stage="ideation"), native_ruling(slug="other"),
            native_ruling(actor="agent:first-officer"), native_ruling(actor="agent:worker"),
            native_ruling(reason=""), native_ruling(at=""), native_ruling(kind="withdrawal"),
            native_ruling() + "          withdrawal:\n            reason: withdrawn\n",
        ]
        for i, native in enumerate(cases):
            with self.subTest(i=i):
                self.save(REPORT, native)
                self.commit(f"invalid ruling {i}")
                self.assert_hold()

    def test_uncommitted_ruling_does_not_clear_and_uncommitted_report_is_evidence_error(self):
        self.save(REPORT, native_ruling())
        self.assert_hold()
        self.save(REPORT.replace("settle", "choose"))
        self.assert_hold(2)

    def test_rewritten_or_deleted_then_reintroduced_report_cannot_reset_clock(self):
        self.save(REPORT.replace("settle", "choose"), native_ruling())
        self.commit("rewrite report")
        self.assert_hold(2)

    def test_deleted_then_reintroduced_report_is_an_evidence_error(self):
        self.save("## Scope\nWork\n")
        self.commit("delete report")
        self.save(REPORT, native_ruling())
        self.commit("reintroduce report beside ruling")
        self.assert_hold(2)

    def test_divergent_report_origins_and_duplicate_task_paths_are_evidence_errors(self):
        self.new_state("## Scope\nWork\n")
        self.git("branch", "side")
        self.save(REPORT)
        self.commit("first report origin")
        self.git("checkout", "side")
        self.save(REPORT)
        self.commit("second independent report origin")
        self.git("checkout", "main")
        self.git("merge", "--no-ff", "side", "-m", "merge identical report bytes")
        self.assert_hold(2)
        self.new_state()
        duplicate = self.root / "task/index.md"
        duplicate.write_text(self.task.read_text())
        self.commit("ambiguous task identities")
        self.assert_hold(2)

    def test_fences_closed_checklist_mentions_and_newest_report_selection(self):
        cases = [
            "## Scope\n\n```md\n" + REPORT + "\n```\n",
            REPORT.replace("Needs decision:", "Needs decision (CLOSED):"),
            REPORT.replace("- **F1** Needs decision:", "- DONE: checklist mentions F1 Needs decision:"),
            REPORT + "\n## Stage Report: validation (cycle 2)\n\n- DONE: passed\n",
            REPORT.replace("- **F1**", "> - **F1**"),
        ]
        for body in cases:
            with self.subTest(body=body):
                self.save(body)
                self.commit("no open newest findings")
                self.assertEqual(self.cli(), (0, ""))

    def test_punctuation_and_closed_findings_in_same_report(self):
        self.new_state("## Stage Report: validation (cycle 2)\n"
                  "- F2: Needs decision — choose.\n* **F3 Needs decision:** choose.\n"
                  "- F4 Needs decision: CLOSED — settled.\n")
        out = self.assert_hold()
        self.assertIn("findings F2,F3;", out)
        self.assertNotIn("F4", out)

    def test_flat_folder_and_archive_moves_preserve_committed_report_identity(self):
        report_sha = self.git("rev-parse", "HEAD")
        for relative in ("task/index.md", "_archive/task/index.md", "_archive/task.md"):
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            self.task.rename(target)
            self.task = target
            folder = target.parent if target.name == "index.md" else target.with_suffix("")
            folder.mkdir(exist_ok=True)
            if self.record.parent.parent != folder:
                self.shutil.move(str(self.record.parent), str(folder / "dispatch"))
                self.record = folder / "dispatch" / self.record.name
            self.commit("move task")
            self.assertIn(report_sha, self.assert_hold())
        self.save(REPORT, native_ruling())
        self.commit("ruling after archive")
        self.assertEqual(self.cli(), (0, ""))

    def test_shallow_and_broken_established_git_roots_are_evidence_errors(self):
        clone = Path(self.tmp.name, "shallow")
        self.git("clone", "--depth=1", self.root.as_uri(), str(clone))
        record = clone / self.record.relative_to(self.root)
        code, out = self.cli(record)
        self.assertEqual(code, 2, out)
        self.assertIn("shallow-history", out)
        broken = Path(self.tmp.name, "broken")
        self.shutil.copytree(self.root, broken, ignore=self.shutil.ignore_patterns(".git"))
        (broken / ".git").write_text("gitdir: /missing-git-root\n")
        code, out = self.cli(broken / self.record.relative_to(self.root))
        self.assertEqual(code, 2, out)
        self.assertIn("git-history-unreadable", out)

    def test_plain_copy_skips_only_new_predicate_independent_of_cwd(self):
        plain = Path(self.tmp.name, "plain")
        self.shutil.copytree(self.root, plain, ignore=self.shutil.ignore_patterns(".git"))
        copied = plain / self.record.relative_to(self.root)
        for cwd in (self.root, plain):
            self.assertEqual(self.cli(copied, cwd=cwd), (0, ""))
            self.assertEqual(self.cli(cwd=cwd)[0], 1)
        for record in (self.record, copied):
            record.write_text(record.read_text().replace("Independent verdict", "run adr_lint.py; Independent verdict"))
            code, out = self.cli(record)
            self.assertEqual(code, 1, out)
            self.assertIn("bare package script name adr_lint.py", out)

    def test_newest_folder_and_coverage_keep_their_existing_contracts(self):
        self.assertEqual(self.cli(self.root, "task", mode="--newest"), (0, ""))
        done = subprocess.run([sys.executable, "-B", records.__file__, str(self.record.parent.parent)],
                              capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertNotIn("ruling", done.stdout)

    def test_refusal_recovery_once_and_reading_cost(self):
        another = self.record.with_name("validation-2-message-1.md")
        another.write_text(self.record.read_text())
        code, out = self.cli(self.record, another)
        self.assertEqual(code, 1, out)
        self.assertEqual(out.count(records.RECOVERY), 1)
        code, out = self.cli()
        self.assertEqual(len(out.split()), 56, out)
        self.save(REPORT.replace("settle", "choose"))
        code, out = self.cli()
        self.assertEqual((code, len(out.split())), (2, 16), out)




class SavedValidationRulingTests(unittest.TestCase):
    setUp = LiveValidationRulingTests.setUp
    new_state = LiveValidationRulingTests.new_state
    git = LiveValidationRulingTests.git
    save = LiveValidationRulingTests.save
    commit = LiveValidationRulingTests.commit
    cli = LiveValidationRulingTests.cli
    assert_hold = LiveValidationRulingTests.assert_hold
    def test_pinned_event_prefixes_four_refused_two_pass_and_amendment_restorations(self):
        counts = {0: 0, 1: 0}
        incident = []
        amendment_only = 0
        for case in SAVED_RULING_CASES:
            with self.subTest(source=case["dispatch_commit"], task=case["task"], record=case["record"]):
                self.assertEqual(len(case["report_commit"]), 40)
                self.assertEqual(len(case["dispatch_commit"]), 40)
                self.new_state(case["body"], slug=case["task"])
                self.record = self.record.with_name(case["record"])
                self.record.write_text(COMPLETE.replace("Model:", f"Candidate: {HEAD}\nModel:"))
                native = ""
                for entry in case["native"]:
                    native += ("gates:\n  records:\n    - stage: " + entry["stage"] + "\n      attempts:\n"
                               "        - id: " + entry["attempt"] + "\n          resolution:\n"
                               "            by: " + entry["by"] + "\n"
                               "            at: " + entry["at"] + "\n"
                               "            reason: " + json.dumps(entry["reason"], ensure_ascii=False) + "\n")
                amendments = "\n## Captain amendments\n\n" + "\n\n".join(case["amendments"]) if case["amendments"] else ""
                if native or amendments:
                    self.save(case["body"] + amendments, native)
                    self.commit("supported ruling before source event " + case["dispatch_commit"])
                if amendments:
                    mentions = ", ".join("Captain amendment " + re.search(r"Amendment (\d+)", a)[1]
                                         for a in case["amendments"])
                    self.record.write_text(self.record.read_text().replace("Independent verdict", mentions + "; Independent verdict"))
                self.record.write_text(self.record.read_text() + "\nSource event: " + case["dispatch_commit"] + "\n")
                self.commit("dispatch source " + case["dispatch_commit"])
                original = (self.task.read_bytes(), self.record.read_bytes())
                legacy = bool(case["amendments"] and not case["native"])
                if legacy:
                    self.record.write_text(case["record_text"])
                predicate = subprocess.run([sys.executable, "-B", "-c",
                    "import sys; sys.path.insert(0, sys.argv[1]); import dispatch_records as d; "
                    "sys.exit(d.check_validation_rulings([sys.argv[2]]))",
                    str(Path(records.__file__).parent), str(self.record)], capture_output=True, text=True)
                self.assertEqual(predicate.returncode, 0 if case["prototype"] == "PASS" else 1, predicate.stdout)
                original = (self.task.read_bytes(), self.record.read_bytes())
                expected = 0 if case["prototype"] == "PASS" and not legacy else 1
                code, out = self.cli()
                self.assertEqual(code, expected, out)
                self.assertEqual((self.task.read_bytes(), self.record.read_bytes()), original)
                counts[predicate.returncode] += 1
                if legacy:
                    self.assertIn("Supersedes:", out)
                    supported = amendments
                    supported = re.sub(r"(?m)^Supersedes:.*$", "Supersedes: none", supported)
                    self.save(case["body"] + supported, native)
                    self.commit("supported-form positive control; legacy source unchanged in fixture")
                    self.record.write_text(COMPLETE.replace("Model:", f"Candidate: {HEAD}\nModel:").replace(
                        "Independent verdict", mentions + "; Independent verdict"))
                    self.assertEqual(self.cli(), (0, ""))

                if predicate.returncode == 1:
                    self.assertIn(f"report {case['report_ordinal']} at", out)
                if case["task"] == "paseo-codex-dispatch-practice":
                    incident.append(code)
                if case["amendments"] and not case["native"]:
                    amendment_only += 1
        self.assertEqual(counts, {0: 15, 1: 12})
        self.assertEqual(incident, [1, 1, 1, 1, 0, 0])
        self.assertEqual(amendment_only, 3)

    def test_seven_adjudications_and_legacy_actual_rerun_cost_remain_explicit(self):
        evidence = {
            ("agent-review-identity", "validation-1.md"):
                ("retrospective record addition", "F3: missing saved records; records existed in temporary dispatch files"),
            ("pair-once", "validation-2.md"):
                ("partial reply", "Captain 「可以」 to the 500 ceiling; F4/F5/F6 wait for Captain at the gate"),
            ("pair-once", "validation-3.md"):
                ("older reply", "F21–F30 introduced; F4/F5/F6 and F23/F24/F25 left unchanged"),
            ("briefing-frame-and-controls", "validation-2.md"):
                ("deferred decisions", "implementation fixes F1–F5; F6/F7 not reopened"),
            ("frame-reaches-window-bottom", "validation-2.md"):
                ("FO authorization", "Validation F1 repaired as the FO authorizes against earlier Captain words"),
            ("hidden-file-draws-diagrams", "validation-2.md"):
                ("FO direction", "F2 owned, repaired by FO direction; no later Captain reply"),
            ("production-operations", "validation-4.md"):
                ("conflicting attribution", "FO ruling, 2026-10-18; worker says your 2026-10-17 ruling"),
        }
        cases = {(c["task"], c["record"]): c for c in SAVED_RULING_CASES}
        for key, (judgment, saved_evidence) in evidence.items():
            case = cases[key]
            self.assertEqual(case["prototype"], "REFUSE", (judgment, saved_evidence))
            self.assertFalse(case["native"] or case["amendments"])
            self.new_state(case["body"] + "\n## Saved evidence\n" + saved_evidence + "\n", slug=case["task"])
            self.assert_hold()
        legacy = cases[("merge-gatekeeper", "validation-2.md")]
        self.new_state(legacy["body"], slug=legacy["task"])
        self.save(legacy["body"] + "\n## Feedback Cycles\nCaptain: 「同意」\nAsked: authorize repair/revalidation?\n")
        self.commit("free-form ruling from d82950c34a85d23dd43551910618faf9552392e6..da4d899707f2c74faee906d030d40b547726be14")
        self.assert_hold()
        self.save(legacy["body"] + AMENDMENT.replace("May validation run again?", "authorize repair/revalidation?"))
        self.commit("faithful on-touch supported entry")
        self.record.write_text(self.record.read_text().replace("Independent verdict", "Captain amendment 1; Independent verdict"))
        self.assertEqual(self.cli(), (0, ""))


SAVED_RULING_CASES = [{'corpus': 'dev2',
  'tip': '731a165dfdf02549a9d13b0624174351e8a6d7be',
  'task': 'fo-interviews-extension',
  'record': 'validation-2.md',
  'report_commit': '9d6dfcda08069c02ed4e45f72238de2b716afda7',
  'dispatch_commit': '66ade90793a47a716cb55425bc4fbb57c6b15fec',
  'report_ordinal': 1,
  'prototype': 'PASS',
  'body': '## Stage Report: validation\n'
          '\n'
          '- F1 Needs decision: The accepted operational evidence is missing (AC-1/2/5/6/7); fixture success cannot '
          'justify delivery.\n'
          "- F2 Needs decision: The mandatory named-record check fails on an inherited ADR outside this task's "
          'four-document scope.\n',
  'native': [{'attempt': 'gate-attempt:fo-interviews-extension-validation-1',
              'stage': 'validation',
              'kind': 'resolution',
              'by': 'person:captain',
              'at': '2026-10-28T14:29:16.661321Z',
              'reason': "The Captain 「准」 (chat, 2026-10-28), answering FO's joint batch-9 delivery sitting of four "
                        'gates whose ask was 「決定：四張全照建議（#743 合併、#744 接著合併、#742 我補一次再驗收、#745 提早跑第 4 '
                        "輪訪談並照上面修）；如果哪張要改，直接說。」; accepts FO's recommendation to hold this task at validation and the "
                        'steps the gate question names.',
              'decision': 'hold'}],
  'amendments': ['### Amendment 2 — 2026-10-28, validation gate (batch-9 joint delivery sitting)\n'
                 'Captain: 「准」 (chat, 2026-10-28)\n'
                 'Asked: 「決定：四張全照建議（#743 合併、#744 接著合併、#742 我補一次再驗收、#745 提早跑第 4 輪訪談並照上面修）；如果哪張要改，直接說。」; gate question: '
                 'Hold fo-interviews-extension at validation until it has operational evidence? FO recommends hold; '
                 'approving accepts it and these four steps: the Captain asks for an early targeted interview round 4 '
                 'under the candidate extension text (one or two extensions, the five FOs, about ten bundled sends, no '
                 'test agents) as the evidence validation found missing; a repair lists `fo-feedback` in this '
                 "workflow's README `extensions:` and removes the 30-mutation claim from the PR body (validation "
                 "inverted the policy and those fixtures still passed); AC-2's live three-batch cadence is shown at "
                 'the first due round, not before merge, recorded as a Captain amendment; #745 merges after #744, '
                 'whose batch rule it reads. F2 is declined (adr_lint.py --require names the ADRs a change adds or '
                 'updates; #745 adds or updates none).\n'
                 'Supersedes: AC-2']},
 {'corpus': 'dev2',
  'tip': '731a165dfdf02549a9d13b0624174351e8a6d7be',
  'task': 'fo-interviews-extension',
  'record': 'validation-3.md',
  'report_commit': 'f9cd8f92bd60c15085d8dfdc09d67f2acc87ccd9',
  'dispatch_commit': 'ee195fef9685b7772d6c95d38d3b42283cde9f9e',
  'report_ordinal': 2,
  'prototype': 'PASS',
  'body': '## Stage Report: validation\n'
          '\n'
          '- F1 Needs decision: The accepted operational evidence is missing (AC-1/2/5/6/7); fixture success cannot '
          'justify delivery.\n'
          "- F2 Needs decision: The mandatory named-record check fails on an inherited ADR outside this task's "
          'four-document scope.\n'
          '\n'
          '## Stage Report: validation\n'
          '\n'
          '- F1 Needs decision, narrowed: Remaining accepted native-evidence boundary is unmet.\n',
  'native': [{'attempt': 'gate-attempt:fo-interviews-extension-validation-2',
              'stage': 'validation',
              'kind': 'resolution',
              'by': 'person:captain',
              'at': '2026-10-28T16:04:51.196425Z',
              'reason': "The Captain 「准」 (chat, 2026-10-29), answering FO's second batch-9 delivery sitting whose ask "
                        "was 「決定：三張全照建議（合併 #744、合併 #742、#745 改條件後在 #744 之後合併）；如果哪張要改，直接說。」; accepts FO's "
                        'recommendation for this task as stated in the gate question.',
              'decision': 'approve'}],
  'amendments': ['### Amendment 3 — 2026-10-29, validation gate (second batch-9 delivery sitting)\n'
                 'Captain: 「准」 (chat, 2026-10-29)\n'
                 'Asked: 「決定：三張全照建議（合併 #744、合併 #742、#745 改條件後在 #744 之後合併）；如果哪張要改，直接說。」; gate question: Approve '
                 'fo-interviews-extension with its remaining native criteria shown at first occurrence, and merge '
                 'iamcxa/kc-claude-plugins#745 at head bd328daf6e64a73ad5e54f7288803295cae9ef68 after #744? FO '
                 'recommends approve; approving accepts that recommendation and records it as Captain amendment 3: the '
                 'criteria validation-2 left unmet (optional adoption, interrupted-round recovery, actual reading '
                 'counts and pending-send comparability) are shown the first time each happens in a real round, not '
                 'before merge, as amendment 2 already did for the three-batch cadence. It covers later '
                 'external-review rounds on this PR, merging this full head after FO reruns delivery_gate.py check '
                 'unless he says he merges or holds, and removing its clean, pushed worktree; FO merges this one PR '
                 'only; every other PR, the Release PR included, is asked one at a time.\n'
                 'Supersedes: none']},
 {'corpus': 'dev2',
  'tip': '731a165dfdf02549a9d13b0624174351e8a6d7be',
  'task': 'idle-hook-names-merged-tasks-without-learn',
  'record': 'validation-2.md',
  'report_commit': 'a20f15267689a47c58111466acada1c0b2c42b0d',
  'dispatch_commit': '58db1043408988c65a3998c28ec3792cf7c29aeb',
  'report_ordinal': 1,
  'prototype': 'PASS',
  'body': '## Stage Report: validation\n'
          '\n'
          "- F1 Needs decision: Amendment 1's quoted Asked requires no repeated naming after ineligibility, whereas "
          'AC-8 and the full-history design require repetition. Released user/workflow: FO idle scan after a '
          'legacy-profile learn hold; observed harm: every idle pass repeats an unactionable instruction; affected '
          'boundary: captain-ruling[2026-10-27] no-repeat words conflict with value-ac[AC-8] explicit repeat; trigger: '
          'acceptance.sh step 3, real recorder and watcher CLI, unchanged archived task. FO must reconcile the '
          'governing requirement before repair authorization or delivery; the validator has made neither choice.\n',
  'native': [],
  'amendments': ['### Amendment 2 — 2026-10-28, chat\n'
                 'Captain: 「全准」 (chat, 2026-10-28)\n'
                 "Asked: FO's batch-8 merge sitting, item 「**三、#737 閒置檢查：照首席工程師的方案修** - **怎麼修：** learn "
                 '判為「不適用」的任務，閒置檢查直接跳過，判斷依據是任務檔開頭的類型和規格欄位，只改原本那三個檔案，不另外存紀錄。 - **變差的地方：** 判斷規則是複製 learn '
                 '的，沒有共用；因為其他原因被判不適用的任務，仍然會重複出現。 - 修好、驗證過後，再拿合併詢問給你。」\n'
                 'Supersedes: AC-8 as written (the implementation worker restates it: an archived task whose variant '
                 "or profile learn rejects is skipped by the scan, with a parity test against learning.py's "
                 'eligibility, in the three approved files and with no new record)'],
  'record_text': '# validation-2\n'
                 '\n'
                 'Dispatched: 8bf4f3582411e8e4238f19fbadda8ddeca6767be (workflow checkout, kc-dev-flow-2 0.32.0 '
                 'README); batch 8\n'
                 'Candidate: aa0f280f8e94f8b5549b4a8cd26fe30560a9842c\n'
                 "Model: gpt-6-astra (Codex via Paseo, thinking high; the Captain's interim dispatch directive, chat "
                 '2026-10-26: 「接下來派工結束後新的派工盡量用 sol / astra，推理等級可以比 claude 高一級」)\n'
                 '\n'
                 '## Checklist\n'
                 '\n'
                 'Independent verdict on PR #737 head aa0f280f against every acceptance criterion in the task file, '
                 're-running each evidence command and at least one falsifier per criterion yourself, and judging each '
                 'limit the implementation report states\n'
                 'Recheck the Cycle 1 repair under Captain amendment 2: an archived task whose variant or profile '
                 'learn rejects is skipped by the scan, with a parity test against kc-dev-flow-2/scripts/learning.py '
                 'eligibility for those fields; the three approved files only; validation-1 F1 resolved; RoboRev on '
                 'this head (FO, 2026-10-28): clean on aa0f280f8, evidence=roborev:1271; CI on this head read by FO: 4 '
                 'of 4 pass\n'
                 'A minimal acceptance script the Captain can run (three to six steps, exact commands, expected '
                 'output), run by you exactly as written in a fresh bash shell, with its observed output; '
                 '/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.32.0/scripts/adr_lint.py '
                 'docs/adr --since <base> with its exit code; your verdict naming the head, with findings classified '
                 "by the workflow's Review-finding disposition\n"
                 '\n'
                 '## Scope notes\n'
                 '\n'
                 'Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.32.0\n'
                 '\n'
                 'Profile: pilot. Candidate: iamcxa/kc-claude-plugins PR #737, head '
                 'aa0f280f8e94f8b5549b4a8cd26fe30560a9842c, base origin/main. This task; other PRs may be in flight '
                 'and are not your candidate. Check the candidate out detached in a throwaway worktree and remove it '
                 'after. Commit your stage report with `spacedock state commit '
                 'idle-hook-names-merged-tasks-without-learn --workflow-dir '
                 '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2`. '
                 'Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not '
                 'push, comment on any PR, request reviews or mark ready.\n'
                 '\n'
                 "Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered "
                 'here).\n'},
 {'corpus': 'dev2',
  'tip': '731a165dfdf02549a9d13b0624174351e8a6d7be',
  'task': 'merge-gatekeeper',
  'record': 'validation-2.md',
  'report_commit': 'd82950c34a85d23dd43551910618faf9552392e6',
  'dispatch_commit': 'da4d899707f2c74faee906d030d40b547726be14',
  'report_ordinal': 1,
  'prototype': 'REFUSE',
  'body': '## Stage Report: validation\n'
          '\n'
          '- F4 Needs decision: security finding 1 (above); it also covers `docs/journey`, `docs/ship-flow`, '
          '`docs/plan-flow` under docs-only, which I could not show agents do or do not load.\n',
  'native': [],
  'amendments': []},
 {'corpus': 'dev2',
  'tip': '731a165dfdf02549a9d13b0624174351e8a6d7be',
  'task': 'paseo-codex-dispatch-practice',
  'record': 'validation-2.md',
  'report_commit': '1e17be9a0734eb1b122b83335bb7ff96a3a331cb',
  'dispatch_commit': '60d765ac2ed6bda644cd3f94de0c58dae981a860',
  'report_ordinal': 1,
  'prototype': 'REFUSE',
  'body': '## Stage Report: validation\n'
          '\n'
          '- F1 Needs decision: The enabled Paseo/Codex FO-to-worker journey owes real placement and unchanged runtime '
          'fields under value-ac[AC-2] and value-ac[AC-6]. Harm is not demonstrated; the trigger evidence is the '
          "inherited colombo launch root and absent native success/control receipts. FO's instruction to report not "
          "verified does not amend the Captain's criteria. Return the missing-proof decision to the Captain: authorize "
          'the disposable native comparison, or explicitly amend acceptance; do not infer a waiver or repair product '
          'bytes.\n',
  'native': [],
  'amendments': [],
  'ruling_commit': None},
 {'corpus': 'dev2',
  'tip': '731a165dfdf02549a9d13b0624174351e8a6d7be',
  'task': 'paseo-codex-dispatch-practice',
  'record': 'validation-2-message-1.md',
  'report_commit': '1e17be9a0734eb1b122b83335bb7ff96a3a331cb',
  'dispatch_commit': 'c9bf77a5e68d1809826044df316ec3d8904bced6',
  'report_ordinal': 1,
  'prototype': 'REFUSE',
  'body': '## Stage Report: validation\n'
          '\n'
          '- F1 Needs decision: The enabled Paseo/Codex FO-to-worker journey owes real placement and unchanged runtime '
          'fields under value-ac[AC-2] and value-ac[AC-6]. Harm is not demonstrated; the trigger evidence is the '
          "inherited colombo launch root and absent native success/control receipts. FO's instruction to report not "
          "verified does not amend the Captain's criteria. Return the missing-proof decision to the Captain: authorize "
          'the disposable native comparison, or explicitly amend acceptance; do not infer a waiver or repair product '
          'bytes.\n',
  'native': [],
  'amendments': [],
  'ruling_commit': None},
 {'corpus': 'dev2',
  'tip': '731a165dfdf02549a9d13b0624174351e8a6d7be',
  'task': 'paseo-codex-dispatch-practice',
  'record': 'validation-4.md',
  'report_commit': 'e0dc64f886cf80e7579551a4002a05b4c603f1c9',
  'dispatch_commit': 'ef0ca5a2a6b1ea1fa975ff46872e2b396bd5a6bd',
  'report_ordinal': 2,
  'prototype': 'REFUSE',
  'body': '## Stage Report: validation\n'
          '\n'
          '- F1 Needs decision: The enabled Paseo/Codex FO-to-worker journey owes real placement and unchanged runtime '
          'fields under value-ac[AC-2] and value-ac[AC-6]. Harm is not demonstrated; the trigger evidence is the '
          "inherited colombo launch root and absent native success/control receipts. FO's instruction to report not "
          "verified does not amend the Captain's criteria. Return the missing-proof decision to the Captain: authorize "
          'the disposable native comparison, or explicitly amend acceptance; do not infer a waiver or repair product '
          'bytes.\n'
          '\n'
          '## Stage Report: validation\n'
          '\n'
          '- F1 Needs decision (still open, narrower): released user/workflow = FO dispatching an opted-in Paseo Codex '
          'worker; observable harm = none demonstrated, but full accepted proof absent; boundary = value-ac[AC-2] '
          'immediate-spawn order and value-ac[AC-6] unchanged generated prompt/fields; trigger = committed '
          'validation-2-message-1 plus independently read native/self activities. Placement is resolved, integrated '
          'transport is not. Captain must decide whether to amend the acceptance boundary or retain the missing proof '
          'obligation; FO declines more trial agents in this validation, which does not waive an AC.\n',
  'native': [],
  'amendments': [],
  'ruling_commit': None},
 {'corpus': 'dev2',
  'tip': '731a165dfdf02549a9d13b0624174351e8a6d7be',
  'task': 'paseo-codex-dispatch-practice',
  'record': 'validation-3-message-1.md',
  'report_commit': 'e0dc64f886cf80e7579551a4002a05b4c603f1c9',
  'dispatch_commit': 'e5dd5a3e5e4caeb4100db7748399e3b9adcd34ac',
  'report_ordinal': 2,
  'prototype': 'REFUSE',
  'body': '## Stage Report: validation\n'
          '\n'
          '- F1 Needs decision: The enabled Paseo/Codex FO-to-worker journey owes real placement and unchanged runtime '
          'fields under value-ac[AC-2] and value-ac[AC-6]. Harm is not demonstrated; the trigger evidence is the '
          "inherited colombo launch root and absent native success/control receipts. FO's instruction to report not "
          "verified does not amend the Captain's criteria. Return the missing-proof decision to the Captain: authorize "
          'the disposable native comparison, or explicitly amend acceptance; do not infer a waiver or repair product '
          'bytes.\n'
          '\n'
          '## Stage Report: validation\n'
          '\n'
          '- F1 Needs decision (still open, narrower): released user/workflow = FO dispatching an opted-in Paseo Codex '
          'worker; observable harm = none demonstrated, but full accepted proof absent; boundary = value-ac[AC-2] '
          'immediate-spawn order and value-ac[AC-6] unchanged generated prompt/fields; trigger = committed '
          'validation-2-message-1 plus independently read native/self activities. Placement is resolved, integrated '
          'transport is not. Captain must decide whether to amend the acceptance boundary or retain the missing proof '
          'obligation; FO declines more trial agents in this validation, which does not waive an AC.\n',
  'native': [],
  'amendments': [],
  'ruling_commit': None},
 {'corpus': 'dev2',
  'tip': '731a165dfdf02549a9d13b0624174351e8a6d7be',
  'task': 'paseo-codex-dispatch-practice',
  'record': 'validation-6.md',
  'report_commit': '0e5b6f59a8e5a067b2739bf1b78863d96399240f',
  'dispatch_commit': '28b366c0cf8bbf2dedc658543850de5a860834a8',
  'report_ordinal': 3,
  'prototype': 'PASS',
  'body': '## Stage Report: validation\n'
          '\n'
          '- F1 Needs decision: The enabled Paseo/Codex FO-to-worker journey owes real placement and unchanged runtime '
          'fields under value-ac[AC-2] and value-ac[AC-6]. Harm is not demonstrated; the trigger evidence is the '
          "inherited colombo launch root and absent native success/control receipts. FO's instruction to report not "
          "verified does not amend the Captain's criteria. Return the missing-proof decision to the Captain: authorize "
          'the disposable native comparison, or explicitly amend acceptance; do not infer a waiver or repair product '
          'bytes.\n'
          '\n'
          '## Stage Report: validation\n'
          '\n'
          '- F1 Needs decision (still open, narrower): released user/workflow = FO dispatching an opted-in Paseo Codex '
          'worker; observable harm = none demonstrated, but full accepted proof absent; boundary = value-ac[AC-2] '
          'immediate-spawn order and value-ac[AC-6] unchanged generated prompt/fields; trigger = committed '
          'validation-2-message-1 plus independently read native/self activities. Placement is resolved, integrated '
          'transport is not. Captain must decide whether to amend the acceptance boundary or retain the missing proof '
          'obligation; FO declines more trial agents in this validation, which does not waive an AC.\n'
          '\n'
          '## Stage Report: validation\n'
          '\n'
          '- F1 Needs decision (narrowed to immediate-spawn order): released user/normal workflow = FO using the '
          'enabled Paseo Codex procedure; observable harm = the accepted order is not followed, with no stale '
          'assignment or product damage observed; boundary = value-ac[AC-2] no intervening operation, plus the '
          "retained Spacedock next-host-action contract; trigger = FO's committed four-call sequence and "
          'validation-3-message-1. Unchanged-prompt/native-field proof is now supplied; the remaining gap belongs to '
          "FO's execution/evidence, not candidate code. A conforming next-action trace is still required unless the "
          'Captain amends the accepted boundary.\n',
  'native': [{'attempt': 'gate-attempt:paseo-codex-dispatch-practice-validation-1',
              'stage': 'validation',
              'kind': 'resolution',
              'by': 'person:captain',
              'at': '2026-10-28T14:29:13.030894Z',
              'reason': "The Captain 「准」 (chat, 2026-10-28), answering FO's joint batch-9 delivery sitting of four "
                        'gates whose ask was 「決定：四張全照建議（#743 合併、#744 接著合併、#742 我補一次再驗收、#745 提早跑第 4 '
                        "輪訪談並照上面修）；如果哪張要改，直接說。」; accepts FO's recommendation to hold this task at validation and the "
                        'steps the gate question names.',
              'decision': 'hold'}],
  'amendments': [],
  'ruling_commit': 'd24235a4c'},
 {'corpus': 'dev2',
  'tip': '731a165dfdf02549a9d13b0624174351e8a6d7be',
  'task': 'paseo-codex-dispatch-practice',
  'record': 'validation-4-message-1.md',
  'report_commit': '0e5b6f59a8e5a067b2739bf1b78863d96399240f',
  'dispatch_commit': '034da3d06c015f9aba60256de9d557fb4944d05f',
  'report_ordinal': 3,
  'prototype': 'PASS',
  'body': '## Stage Report: validation\n'
          '\n'
          '- F1 Needs decision: The enabled Paseo/Codex FO-to-worker journey owes real placement and unchanged runtime '
          'fields under value-ac[AC-2] and value-ac[AC-6]. Harm is not demonstrated; the trigger evidence is the '
          "inherited colombo launch root and absent native success/control receipts. FO's instruction to report not "
          "verified does not amend the Captain's criteria. Return the missing-proof decision to the Captain: authorize "
          'the disposable native comparison, or explicitly amend acceptance; do not infer a waiver or repair product '
          'bytes.\n'
          '\n'
          '## Stage Report: validation\n'
          '\n'
          '- F1 Needs decision (still open, narrower): released user/workflow = FO dispatching an opted-in Paseo Codex '
          'worker; observable harm = none demonstrated, but full accepted proof absent; boundary = value-ac[AC-2] '
          'immediate-spawn order and value-ac[AC-6] unchanged generated prompt/fields; trigger = committed '
          'validation-2-message-1 plus independently read native/self activities. Placement is resolved, integrated '
          'transport is not. Captain must decide whether to amend the acceptance boundary or retain the missing proof '
          'obligation; FO declines more trial agents in this validation, which does not waive an AC.\n'
          '\n'
          '## Stage Report: validation\n'
          '\n'
          '- F1 Needs decision (narrowed to immediate-spawn order): released user/normal workflow = FO using the '
          'enabled Paseo Codex procedure; observable harm = the accepted order is not followed, with no stale '
          'assignment or product damage observed; boundary = value-ac[AC-2] no intervening operation, plus the '
          "retained Spacedock next-host-action contract; trigger = FO's committed four-call sequence and "
          'validation-3-message-1. Unchanged-prompt/native-field proof is now supplied; the remaining gap belongs to '
          "FO's execution/evidence, not candidate code. A conforming next-action trace is still required unless the "
          'Captain amends the accepted boundary.\n',
  'native': [{'attempt': 'gate-attempt:paseo-codex-dispatch-practice-validation-1',
              'stage': 'validation',
              'kind': 'resolution',
              'by': 'person:captain',
              'at': '2026-10-28T14:29:13.030894Z',
              'reason': "The Captain 「准」 (chat, 2026-10-28), answering FO's joint batch-9 delivery sitting of four "
                        'gates whose ask was 「決定：四張全照建議（#743 合併、#744 接著合併、#742 我補一次再驗收、#745 提早跑第 4 '
                        "輪訪談並照上面修）；如果哪張要改，直接說。」; accepts FO's recommendation to hold this task at validation and the "
                        'steps the gate question names.',
              'decision': 'hold'}],
  'amendments': [],
  'ruling_commit': 'd24235a4c'},
 {'corpus': 'relay',
  'tip': '7fbde2c526769e0968d05fac858fc63b31c6274c',
  'task': 'agent-review-identity',
  'record': 'validation-1.md',
  'report_commit': 'bfe1238e5d10a9be4deb43a090bead8b6101ee3a',
  'dispatch_commit': '7ea4bf019eb6a80223ca24c5a53047c0513566fb',
  'report_ordinal': 1,
  'prototype': 'REFUSE',
  'body': '## Stage Report: validation\n'
          '\n'
          '- F1 Needs decision (Captain): AC-3(c) says a resend of the same bytes answers 503; on the real v0.3.15 '
          'build it answers 400 because the old validator rejects the `agent:` actor before it reads storage. The 503 '
          'appears only for the own-session `read`. `hosted-review-room.md` states 400, so the document is right and '
          'the criterion text is stale; the criterion was not edited. Protected value: AC-3(c) wording only; no user '
          'harm.\n',
  'native': [],
  'amendments': []},
 {'corpus': 'relay',
  'tip': '7fbde2c526769e0968d05fac858fc63b31c6274c',
  'task': 'pair-once',
  'record': 'validation-2.md',
  'report_commit': '13a672cb0ae50a450dee37e6d73945583514d00f',
  'dispatch_commit': '6cf9d342df3b094fa8e2a5685b072215ab016efc',
  'report_ordinal': 1,
  'prototype': 'REFUSE',
  'body': '## Stage Report: validation\n'
          '\n'
          '- F3 Needs decision: security finding 1 (HIGH). The site-wide daily ceiling on starting a pairing '
          '(`RELAY_PAIR_SITE_DAILY_LIMIT`, default 500) can be spent by an outsider with no account. The attacker '
          'mints fresh device ids, and each address has 10 an hour. Once spent, every `rr pair` gets 429 until UTC '
          'midnight. The address and device slots are also taken before the site slot refuses, and are not given back. '
          'AC-1 prescribes this ceiling. The FO\'s follow-up 4 refused the same shape for wrong codes ("one attacker '
          'becomes a site-wide outage"). The FO decides: keep it, raise the default, reserve an allowance for '
          'registered devices, or release the slots on refusal.\n'
          '- F4 Needs decision: AC-25\'s menu clause ("Paired computers" in the name-card menu) is not built. The '
          'implementation says Web refuses an unknown action kind. Verified: Web `a790e3a` `src/review-shell.js` '
          '`IDENTITY_ACTION_KINDS` throws `invalid-identity` for any other kind, so adding the item now would break '
          "the Room on today's Web. No FO follow-up and no line of the Design's Slicing places this clause outside "
          'slice 1. FO to rule it slice 2 and route it to the Web FO.\n'
          '- F5 Needs decision: AC-2\'s text says signed-out `/pair/authorize` and `/pair` "show \'Sign in to pair\'". '
          'The candidate follows the later Design paragraph instead: the same-computer page goes straight to sign-in, '
          'and the signed-out code page\'s button reads "Sign in to continue" (rendered `code-signed-out.html`). FO to '
          "amend AC-2's words or rule otherwise. The implementation raised this earlier and got no reply.\n"
          '- F6 Needs decision: two accepted criteria give one action two names (built screen review 1, finding 1). '
          'AC-21\'s approved page says "choose Unpair on the done page or in Paired computers", but AC-24\'s Paired '
          'computers button is "Remove". The candidate matches both criteria verbatim.\n'
          "- F7 Needs decision: built screen review 2, finding 1 (MAJOR). On a 390x844 phone the Design's pinned "
          "button bar covers part of the code-flow confirm page at first paint. The computer name is the requester's "
          'own choice, up to 64 characters. With a 64-character name from another network, the Network row sits at y '
          '591–627 under a bar whose top is 586, so the anti-phishing cue is hidden at first paint while Yes can be '
          'pressed. It is reachable by scrolling. With a short name only the account email is covered (a 48 px scroll '
          "shows it). AC-20 does not bind first-paint visibility; the pinned bar is the accepted Design's.\n"
          '- F8 Needs decision: built screen 2, finding 2. Paired computers cuts a long name with an ellipsis '
          '(`.comp-main strong` nowrap). The full name shows nowhere on that page, the page where a person checks for '
          "a stranger's computer.\n"
          '- F9 Needs decision: built screen 2, finding 4. "Details" has no disclosure marker, because `summary { '
          'display: flex }` drops the native one.\n'
          '- F10 Needs decision: built screen 2, finding 6, overruled in `design/validation-declines-1.yaml`. Continue '
          'on the locked page carries `disabled` but is drawn like an enabled button. It needs a visible `:disabled` '
          'style.\n'
          '- F11 Needs decision: built screen 2, finding 7. The "said no" ending has no next step, and the cancelled '
          'ending has only advice. The Design gives every ending "one next step on its own line".\n'
          '- F12 Needs decision: built screen 2, finding 8. After 15 s the finishing page hides "rr pair is completing '
          'the pairing." instead of adding the warning below it, and it draws the warning in error red.\n'
          '- F13 Needs decision: built screen 2, finding 9, overruled. "Your terminal will ask you to confirm once '
          'more." touches the red error line with no gap.\n'
          '- F14 Needs decision: built screen 2, finding 14. Measured contrast of the dark-theme Remove confirm button '
          'is 2.47:1 (white on `oklch(0.74 0.16 25)`); light is 5.78:1.\n'
          '- F15 Needs decision: built screen 2, finding 15, overruled. No picture shows the failure messages of Pair, '
          'Unpair and Remove. They need a picture or a named criterion.\n',
  'native': [],
  'amendments': []},
 {'corpus': 'relay',
  'tip': '7fbde2c526769e0968d05fac858fc63b31c6274c',
  'task': 'pair-once',
  'record': 'validation-3.md',
  'report_commit': '08d2bed0c05a152980728973988d6799a77d1f9c',
  'dispatch_commit': 'f342c2d6f11150fc8e3f66a3d4afa9395d20f84f',
  'report_ordinal': 1,
  'prototype': 'REFUSE',
  'body': '## Stage Report: validation\n'
          '\n'
          '- F21 Needs decision (built screen review 3, finding 1, MAJOR): when Remove or Unpair cannot unbind, the '
          'page reads "Try again. The relay was busy, so nothing changed." It has no status icon, no Try again control '
          'and no link back to Paired computers. A full binding chain (`unbindDevice` reason `full`) gets the same '
          '"busy" words, and retrying can never succeed for it. A write contention or a 32-event chain triggers it; '
          'the second is rare. Repair: a next step and a true message for the `full` case.\n'
          '- F22 Needs decision (finding 2): the not-found answer to Remove or Unpair has no link to Paired '
          'computers.\n'
          '- F23 Needs decision (finding 3, decline overruled): relay draws no page for the same-computer Cancel. The '
          "browser posts `error=access_denied` to rr's loopback listener, so rr's own result is that ending. The page "
          'belongs to v0 task `rr-pairs-once`; FO to route it there or add a criterion.\n'
          '- F24 Needs decision (finding 4, decline overruled): no picture or criterion shows the zero-review Remove '
          'dialog or the removal of the last computer. The handler\'s zero case reads "It published no reviews as '
          'you." (`reviewFate(0)`).\n'
          '- F25 Needs decision (finding 6): names over 24 characters are cut to 23 characters plus "…" in the '
          'question, the warning and the buttons. Two computers that share a prefix then read the same there; the card '
          "keeps the full name. This cut is F7's own fix, so the call is a trade-off.\n"
          '- F26 Needs decision (finding 9, decline overruled): the locked code field keeps its solid red border. '
          '`.codein[aria-invalid="true"]` is declared after `.codein:disabled`, so it wins.\n'
          '- F27 Needs decision (security review 2, finding 1, MEDIUM): `issueToken` reads the account from WorkOS '
          "before it checks whether this request's one token was already issued. Measured: 10 device-grant polls after "
          'one approval made 10 WorkOS reads for 1 token, and polls 2–10 answered `invalid_grant`. Bound: about 75 '
          "reads per approved request over its 5-minute window, times the site ceiling of 500 a day. WorkOS's own "
          "limits for that key, which sign-in shares, are not known. Repair: read the request's `token.json` before "
          'the lookup.\n'
          '- F28 Needs decision (security review 2, finding 2, LOW): the new page routes declare no edge `rateLimit`. '
          'Those are `/pair`, `/pair/authorize`, `/pair/result/:ref`, `/account/computers` and the metadata route. The '
          'existing page routes declare 150 a minute (`try-link.mts`, `share.mts`). Each GET is a function call plus '
          'strong reads and writes nothing.\n'
          '- F30 Needs decision: the signed-in leg is not reliably green on this Mac. The owner-link and claim specs '
          "flake under the leg's 4-second link window (`RELAY_OWNER_LINK_TTL_MS=4000`). This is not new in this round: "
          'the same cases fail at 1523d652. Separately, the phone case hung once on closing its own browser after its '
          'measurement had been taken. That is a harness flake, not the assertion. The leg has never run on GitHub. FO '
          'or the Captain decides: widen the window for the leg, quarantine those cases until slice 2 deletes them, or '
          'run the leg on GitHub before the PR is marked ready.\n',
  'native': [],
  'amendments': []},
 {'corpus': 'relay',
  'tip': '7fbde2c526769e0968d05fac858fc63b31c6274c',
  'task': 'pair-once',
  'record': 'validation-4.md',
  'report_commit': 'de3a6f6e9d9191155dff6eda1ce5579ec0dfdd5e',
  'dispatch_commit': '3721da7a6dedad9b0b867f1a50657500bca8ede1',
  'report_ordinal': 2,
  'prototype': 'PASS',
  'body': '## Stage Report: validation\n'
          '\n'
          '- F21 Needs decision (built screen review 3, finding 1, MAJOR): when Remove or Unpair cannot unbind, the '
          'page reads "Try again. The relay was busy, so nothing changed." It has no status icon, no Try again control '
          'and no link back to Paired computers. A full binding chain (`unbindDevice` reason `full`) gets the same '
          '"busy" words, and retrying can never succeed for it. A write contention or a 32-event chain triggers it; '
          'the second is rare. Repair: a next step and a true message for the `full` case.\n'
          '- F22 Needs decision (finding 2): the not-found answer to Remove or Unpair has no link to Paired '
          'computers.\n'
          '- F23 Needs decision (finding 3, decline overruled): relay draws no page for the same-computer Cancel. The '
          "browser posts `error=access_denied` to rr's loopback listener, so rr's own result is that ending. The page "
          'belongs to v0 task `rr-pairs-once`; FO to route it there or add a criterion.\n'
          '- F24 Needs decision (finding 4, decline overruled): no picture or criterion shows the zero-review Remove '
          'dialog or the removal of the last computer. The handler\'s zero case reads "It published no reviews as '
          'you." (`reviewFate(0)`).\n'
          '- F25 Needs decision (finding 6): names over 24 characters are cut to 23 characters plus "…" in the '
          'question, the warning and the buttons. Two computers that share a prefix then read the same there; the card '
          "keeps the full name. This cut is F7's own fix, so the call is a trade-off.\n"
          '- F26 Needs decision (finding 9, decline overruled): the locked code field keeps its solid red border. '
          '`.codein[aria-invalid="true"]` is declared after `.codein:disabled`, so it wins.\n'
          '- F27 Needs decision (security review 2, finding 1, MEDIUM): `issueToken` reads the account from WorkOS '
          "before it checks whether this request's one token was already issued. Measured: 10 device-grant polls after "
          'one approval made 10 WorkOS reads for 1 token, and polls 2–10 answered `invalid_grant`. Bound: about 75 '
          "reads per approved request over its 5-minute window, times the site ceiling of 500 a day. WorkOS's own "
          "limits for that key, which sign-in shares, are not known. Repair: read the request's `token.json` before "
          'the lookup.\n'
          '- F28 Needs decision (security review 2, finding 2, LOW): the new page routes declare no edge `rateLimit`. '
          'Those are `/pair`, `/pair/authorize`, `/pair/result/:ref`, `/account/computers` and the metadata route. The '
          'existing page routes declare 150 a minute (`try-link.mts`, `share.mts`). Each GET is a function call plus '
          'strong reads and writes nothing.\n'
          '- F30 Needs decision: the signed-in leg is not reliably green on this Mac. The owner-link and claim specs '
          "flake under the leg's 4-second link window (`RELAY_OWNER_LINK_TTL_MS=4000`). This is not new in this round: "
          'the same cases fail at 1523d652. Separately, the phone case hung once on closing its own browser after its '
          'measurement had been taken. That is a harness flake, not the assertion. The leg has never run on GitHub. FO '
          'or the Captain decides: widen the window for the leg, quarantine those cases until slice 2 deletes them, or '
          'run the leg on GitHub before the PR is marked ready.\n'
          '\n'
          '## Stage Report: validation\n'
          '\n'
          "- F4 Needs decision: the Paired computers Room-menu clause still needs the Captain's cross-repository scope "
          'ruling; unchanged.\n'
          "- F5 Needs decision: AC-2's sign-in words versus the accepted design's redirect/button; unchanged.\n"
          '- F6 Needs decision: accepted Unpair/Remove naming mismatch; unchanged.\n'
          '- F23 Needs decision: same-computer Cancel ending belongs to the terminal-client task; unchanged.\n'
          '- F24 Needs decision: zero-review/last-computer removal preview and criterion; unchanged.\n'
          '- F25 Needs decision: truncated repeated names versus distinguishability; unchanged.\n'
          '- F30 Needs decision: full signed-in leg passed 2/3, despite the known claim case passing 3/3. '
          '`one-entry.spec.ts:20` and `owner-link.spec.ts:138` each timed out once on a five-second artifact-load '
          'assertion with only “Loading…” shown; both later passed. The visitor case survives slice 2. Causal '
          'attribution and hosted CI remain unverified; no silent repair or quarantine. The previous F17 equivalent '
          'mutation and F19/F20 risk dispositions remain unchanged.\n',
  'native': [{'attempt': 'gate-attempt:pair-once-validation-1',
              'stage': 'validation',
              'kind': 'resolution',
              'by': 'person:captain',
              'at': '2026-10-26T01:13:22.928201Z',
              'reason': 'Captain: 「批准」 (chat, 2026-10-26). Asked: 「要批准嗎？如果上面哪一條你不同意，直接告訴我。」 after the FO listed: '
                        'approval accepts F4 Paired computers menu item in slice 2 with Web task '
                        'signed-out-card-shows-sign-in; F5 AC-2 words follow the accepted design (signed-out redirect '
                        'to sign-in, /pair shows "Sign in to continue"); F6 Unpair/Remove naming plus F24, F25 wording '
                        'to slice 2; F23 same-computer Cancel ending to v0 rr-pairs-once; F29 stays a deferred risk; '
                        'F30 ship the two old timed-out tests as a known flake, test-only follow-up if GitHub CI '
                        'reproduces it; FO pushes spacedock-ensign/pair-once and opens the PR; production held until '
                        'after Tuesday 2026-10-27.',
              'decision': 'approve'}],
  'amendments': ['### Amendment 1 — 2026-10-26, validation gate\n'
                 'Captain: 「批准」 (chat)\n'
                 'Asked: 「要批准嗎？如果上面哪一條你不同意，直接告訴我。」 after 「F5：AC-2（第 2 條驗收條件）的文字改成跟已定案的設計一致。未登入時會先導去登入頁，配對頁上顯示 "Sign in '
                 'to continue"。」 (gate-attempt:pair-once-validation-1)\n'
                 'Supersedes: AC-2',
                 '### Amendment 2 — 2026-10-26, chat\n'
                 'Captain: 「好」 (chat)\n'
                 'Asked: 「要照這樣拿掉同一台電腦的位址比對，並接受這個風險嗎？」\n'
                 'Supersedes: AC-5, AC-20\n'
                 'Design: the sentence of the paragraph beginning "Consent is a press on a page" that reads "On the '
                 'same computer a request from another network than the approving browser is refused before any '
                 'confirm page ("This request did not come from this computer", "So nothing was paired.", "Run rr pair '
                 'again on the computer you are using."), so the same-computer confirm page has no network row."']},
 {'corpus': 'relay',
  'tip': '7fbde2c526769e0968d05fac858fc63b31c6274c',
  'task': 'review-keyword-invocations',
  'record': 'validation-2.md',
  'report_commit': 'cab47ff0dc42eda0b31c43b0087a91266dda68e1',
  'dispatch_commit': '7fd5cab47dc8001f97f7dd6fc2f3200da4239375',
  'report_ordinal': 1,
  'prototype': 'PASS',
  'body': '## Stage Report: validation\n'
          '\n'
          '- F4 Needs decision: Codex Terminal/unset, Terminal/conflicting-Web and Terminal/questions execute bare '
          '`review-apple-terminal`, exit 127; matching/saved/quoted cases use the correct absolute bundled script. '
          'AC-1/18 installed-path proof remains incomplete; companion-scope attribution returns to FO. '
          '`codex-observations.json` identifies each case.\n',
  'native': [{'attempt': 'gate-attempt:review-keyword-invocations-validation-1',
              'stage': 'validation',
              'kind': 'resolution',
              'by': 'person:captain',
              'at': '2026-10-27T15:27:20.516322Z',
              'reason': 'Captain: 「退回修正」 (chat, 2026-10-27). Asked: 「要先退回修正，修好後你再走三個對話嗎？」 after the FO presented '
                        'validation-1 REJECTED with F1 Material, F2 and F3 Polish, F4 Needs decision.',
              'decision': 'revise'}],
  'amendments': []},
 {'corpus': 'relay',
  'tip': '7fbde2c526769e0968d05fac858fc63b31c6274c',
  'task': 'review-keyword-invocations',
  'record': 'validation-3.md',
  'report_commit': 'fbbe82d857f4772865638160b44ae99108bd5f00',
  'dispatch_commit': 'f1a7b9e6fcb53d1457d89842f437fbd0c9eef18f',
  'report_ordinal': 3,
  'prototype': 'PASS',
  'body': '## Stage Report: validation\n'
          '\n'
          '- F4 Needs decision: Codex Terminal/unset, Terminal/conflicting-Web and Terminal/questions execute bare '
          '`review-apple-terminal`, exit 127; matching/saved/quoted cases use the correct absolute bundled script. '
          'AC-1/18 installed-path proof remains incomplete; companion-scope attribution returns to FO. '
          '`codex-observations.json` identifies each case.\n'
          '\n'
          '## Stage Report: validation\n'
          '\n'
          '- F4 Needs decision: unchanged Subspace 0.16.1 instruction causes the observed bare-entry choice in three '
          'fresh Codex scenarios; command-not-found prevents real Terminal review. `value-ac[AC-1]` and '
          '`value-ac[AC-18]` installed-path proof remains incomplete. Exact command/digest/source evidence and all '
          'four fields: `validation-2/evidence.md`, `f4-attribution.json`. No companion repair authorized.\n'
          '\n'
          '## Stage Report: validation\n'
          '\n'
          '- F4 Needs decision: unchanged Subspace 0.16.1 instruction causes the observed bare-entry choice in three '
          'fresh Codex scenarios; command-not-found prevents real Terminal review. `value-ac[AC-1]` successful Codex '
          "installed path and Codex question-path evidence remain incomplete; amended AC-18's one real loop now passes "
          'on Claude. Exact command/digest/source evidence and all four fields: `validation-2/evidence.md`, '
          '`f4-attribution.json`. No companion repair authorized.\n',
  'native': [{'attempt': 'gate-attempt:review-keyword-invocations-validation-2',
              'stage': 'validation',
              'kind': 'resolution',
              'by': 'person:captain',
              'at': '2026-10-27T17:54:51.68037Z',
              'reason': 'Captain: 「說「Spacedock Review」時應該要先去檢查上次使用者的紀錄設定，不要預設當成網頁版。F4 問題應該要處理，可以不擋 852，但必須立即跟進」 (chat, '
                        '2026-10-28). Asked: 「要批准嗎？」 at the validation-2 gate (F4 recommendation: record as a Subspace '
                        'limit, report separately).',
              'decision': 'revise'}],
  'amendments': []},
 {'corpus': 'relay',
  'tip': '7fbde2c526769e0968d05fac858fc63b31c6274c',
  'task': 'rr-pairs-once',
  'record': 'validation-2.md',
  'report_commit': '0650de456ad9b49680455209412695c1f98b7d74',
  'dispatch_commit': '74e8186403fa5a78670bbecc5155b93d3becf3ab',
  'report_ordinal': 1,
  'prototype': 'PASS',
  'body': '## Stage Report: validation\n'
          '\n'
          '- F3 Needs decision: dispatch_records.py exited 1 for missing full Dispatched SHAs in ideation-1.md and '
          'implementation-1.md; the First Officer owns their disposition.\n',
  'native': [{'attempt': 'gate-attempt:rr-pairs-once-validation-1',
              'stage': 'validation',
              'kind': 'resolution',
              'by': 'person:captain',
              'at': '2026-10-28T06:07:15.063886Z',
              'reason': 'Captain: 「退回六項」. Asked: 「可以照這六項退回修正嗎？」 Items: F1, F2, F6, Amendment 2 layout (closes F8), '
                        'sheet step 4 (F7 polish taken in), Amendment 3 pre-publish pairing for web-decision requests.',
              'decision': 'revise'}],
  'amendments': ['### Amendment 3 — 2026-10-28, chat\n'
                 'Captain: 「退回六項」\n'
                 'Asked: 「可以照這六項退回修正嗎？」\n'
                 'Supersedes: AC-9\n'
                 "Design: for a request that needs the owner's web decision (spacedock:review `web decision`, or "
                 '`decision` with Web saved), the remote-review skill runs `subspace-relay-client device` after the '
                 'upload agreement and before publishing. When it reads `paired: no` or an unknown account, it leads '
                 'pairing first (rr pair; the person signs in and approves; `paired: not yet` hands over --confirm) '
                 'and publishes after `paired: yes`. A feedback-only request publishes without that check, as now. The '
                 'Captain\'s reference for the moment: the landing docs\' "Your first review" Web step (deploy preview '
                 '14, docs/review/use/).\n'
                 'Captain (2026-10-28, chat): 「直接配對，因為目前要決策一定要登入，對嗎？」 Asked: 「回「直接配對」或「先問」」. The agent says one '
                 'sentence and runs pair directly; it does not ask first.']},
 {'corpus': 'relay',
  'tip': '7fbde2c526769e0968d05fac858fc63b31c6274c',
  'task': 'rr-pairs-once',
  'record': 'validation-3.md',
  'report_commit': 'da69250a7ff78fb82ab0b178e59a6d32c3fa3f87',
  'dispatch_commit': '2b3abe40173f1983eca960f27309369dd846bf63',
  'report_ordinal': 2,
  'prototype': 'PASS',
  'body': '## Stage Report: validation\n'
          '\n'
          '- F3 Needs decision: dispatch_records.py exited 1 for missing full Dispatched SHAs in ideation-1.md and '
          'implementation-1.md; the First Officer owns their disposition.\n'
          '\n'
          '## Stage Report: validation\n'
          '\n'
          '- F11 Needs decision: director finding 9 clips a raw feedback-error tail at 40 columns; initial fixture '
          'intentionally refuses feedback. Two diagnostic scripts failed their title expectation; the second saved '
          'picture shows the title wrapped by the annotation pane and no feedback yet, with no error. MINOR; '
          'hosted-error behavior unverified; no further attempt.\n',
  'native': [{'attempt': 'gate-attempt:rr-pairs-once-validation-2',
              'stage': 'validation',
              'kind': 'resolution',
              'by': 'person:captain',
              'at': '2026-10-28T07:40:42.245743Z',
              'reason': 'Captain: 「退回」. Asked: 「要不要退回修正，把這兩行改成只在單字之間換行，換行後的下一行縮排在標籤底下？」 Items: F9/F10 word-boundary '
                        'wrap with hanging indent for the code-route check and note lines (approved words unchanged); '
                        'F11 the 40-column feedback error line wrapped the same way.',
              'decision': 'revise'}],
  'amendments': []},
 {'corpus': 'web',
  'tip': '2c3a6dcbfb3a8e178d65151237a0c234351612c0',
  'task': 'briefing-frame-and-controls',
  'record': 'validation-2.md',
  'report_commit': 'ce5a5b8b21be63bf8d858b9e5e750acaebbac158',
  'dispatch_commit': 'bbbe9d936e967a47f96187d55a7a4c3615aa7d25',
  'report_ordinal': 1,
  'prototype': 'REFUSE',
  'body': '## Stage Report: validation\n'
          '\n'
          '- F6 Needs decision: AC-13 on the built page, for the Captain (his bar, D3). Plan fixture, all pictures and '
          'the docs-first order: sol 4/4, terra 4/4 (one borderline: "a plan-review page for deciding whether the plan '
          'is ready"), agy 4/4, so 12 of 12 against the bar the task proposes. Two real briefings, same rule, graded '
          'the same on both builds: the Chinese gate briefing (a merge decision) fails every Codex answer on both '
          'builds (sol 0/4, terra 0/4, agy 3/4 on the candidate; base 0/2, 1/2, 1/2) because they name the decision; '
          'the English proposal is sol 4/4, agy 4/4, terra 2/4 on the candidate against 4/4 on base. No tester took '
          'either page for documentation in any of 72 runs. Exact answers and my grade are in testers/validation-1.md; '
          'he regrades.\n'
          "- F7 Needs decision: Built screen finding 6 above (the reviewer's phone profile row), kind other-task, "
          'owner Captain.\n',
  'native': [],
  'amendments': []},
 {'corpus': 'web',
  'tip': '2c3a6dcbfb3a8e178d65151237a0c234351612c0',
  'task': 'briefing-frame-and-controls',
  'record': 'validation-3.md',
  'report_commit': '90b662d0575c54ac4286f97764d17718ba0bcd36',
  'dispatch_commit': '000a71037df1b0f94215940bf66fdfcb4a7d610a',
  'report_ordinal': 2,
  'prototype': 'PASS',
  'body': '## Stage Report: validation\n'
          '\n'
          '- F6 Needs decision: AC-13 on the built page, for the Captain (his bar, D3). Plan fixture, all pictures and '
          'the docs-first order: sol 4/4, terra 4/4 (one borderline: "a plan-review page for deciding whether the plan '
          'is ready"), agy 4/4, so 12 of 12 against the bar the task proposes. Two real briefings, same rule, graded '
          'the same on both builds: the Chinese gate briefing (a merge decision) fails every Codex answer on both '
          'builds (sol 0/4, terra 0/4, agy 3/4 on the candidate; base 0/2, 1/2, 1/2) because they name the decision; '
          'the English proposal is sol 4/4, agy 4/4, terra 2/4 on the candidate against 4/4 on base. No tester took '
          'either page for documentation in any of 72 runs. Exact answers and my grade are in testers/validation-1.md; '
          'he regrades.\n'
          "- F7 Needs decision: Built screen finding 6 above (the reviewer's phone profile row), kind other-task, "
          'owner Captain.\n'
          '\n'
          '## Stage Report: validation (cycle 2)\n'
          '\n'
          "- F6 Needs decision: unchanged from round 1, the Captain's reading of CL's test on real briefings (AC-13); "
          'not rerun.\n'
          "- F7 Needs decision: unchanged from round 1, the reviewer's phone profile row; not reopened.\n",
  'native': [{'attempt': 'gate-attempt:briefing-frame-and-controls-validation-1',
              'stage': 'validation',
              'kind': 'resolution',
              'by': 'person:captain',
              'at': '2026-10-25T03:53:41.48819Z',
              'reason': 'Captain: approve, by Finish review on Spacedock Review share aeqtgydii5xivl4f '
                        '(2026-10-25T03:53:05Z UTC), no comments. Asked: 「核准外框重設計的驗收：CL 測試以「沒有人把它當成說明文件、計畫類 '
                        '12/12」算過（真實簡報上 Codex 多半只描述內容），讓我推分支、開 PR，CI 全綠就合併？」 (candidate df9b731; FO declines F3 and F8 '
                        'in the gate summary; F7 to its own task)',
              'decision': 'approve'}],
  'amendments': []},
 {'corpus': 'web',
  'tip': '2c3a6dcbfb3a8e178d65151237a0c234351612c0',
  'task': 'frame-reaches-window-bottom',
  'record': 'validation-2.md',
  'report_commit': '1e881bccfefc7d65592285381738dafc6e8fcb3c',
  'dispatch_commit': 'c9013a16b010c0930aba55908aca5b0fc0287b8c',
  'report_ordinal': 1,
  'prototype': 'REFUSE',
  'body': '## Stage Report: validation\n'
          '\n'
          "- F1 Needs decision: at the document's end the thumb's solid part still stops 14 px above the window "
          'bottom. A 14 px edge fade, `.subspace-web-chrome::after` (`linear-gradient(transparent, var(--doc-bg))`) in '
          "`src/review-shell.js` (older than this task, in main), sits over the frame's last 14 px including the "
          "scroll bar column. With the overlay's background removed in a throwaway probe the thumb is solid to 2 px "
          'above the bottom '
          '(design/built-1/desktop-1280-candidate-dark-end-with-the-14px-fade-overlay-removed-probe.png). Gap to solid '
          "is 14 px on the candidate, about 34 px on main. AC-1 as written holds (frame edge); the Captain's 「捲軸會貼到底」 "
          'may want the fade gone at the bar. The task cannot own this: the fade is an earlier feature no ADR '
          'settles.\n',
  'native': [],
  'amendments': []},
 {'corpus': 'web',
  'tip': '2c3a6dcbfb3a8e178d65151237a0c234351612c0',
  'task': 'hidden-file-draws-diagrams',
  'record': 'validation-2.md',
  'report_commit': 'c1d35f75625d03cbbc9d28ea396b39dcadfbf3a4',
  'dispatch_commit': '2bf9fa6d60b66feb122b273f8fbe5c99460d7ac6',
  'report_ordinal': 1,
  'prototype': 'REFUSE',
  'body': '## Stage Report: validation\n'
          '\n'
          '- F2 Needs decision: comment_ratio exit 1 (8.7% > 5%). 7 of 11 added comment lines are `// @ts-check` and '
          '`@param`/`@type` JSDoc in the new spec, which 20 of the 31 sibling specs also carry (tsc excludes '
          '`test/browser`); 2 lines in the source and 2 in the spec are prose. The script cannot pass without dropping '
          'the type lines; the FO decides between accepting by convention and stripping them.\n',
  'native': [],
  'amendments': []},
 {'corpus': 'web',
  'tip': '2c3a6dcbfb3a8e178d65151237a0c234351612c0',
  'task': 'review-page-reads-as-an-app',
  'record': 'validation-2.md',
  'report_commit': 'f393c996ab0f920c987bf35500d764e03da999e9',
  'dispatch_commit': 'acb050d79045cceedaab39d556699f9edce8b1d6',
  'report_ordinal': 1,
  'prototype': 'PASS',
  'body': '## Stage Report: validation\n'
          '\n'
          "- F6 Needs decision: AC-13's bar of 4 of 4 on both viewports is met on a desktop (4 of 4) and not on a "
          'phone (6 of 8; the two "documentation" runs both still name the app header as what decided it). Cycle 2 '
          "already read this as run-to-run noise (AC-27); lowering the bar is the Captain's.\n"
          '- F7 Needs decision: a decided review\'s byline for a reviewer reads "<name> asked for your review" (AC-25, '
          'as built) while ADR 0051 says "asked for your decision once decided" for every viewer (director pass 2b: '
          'decision, kind recorded-ruling): keep AC-25 and amend the ADR by a new record, or change the page.\n',
  'native': [{'attempt': 'gate-attempt:review-page-reads-as-an-app-validation-1',
              'stage': 'validation',
              'kind': 'resolution',
              'by': 'person:captain',
              'at': '2026-10-27T16:43:39.327756Z',
              'reason': 'Captain, chat 2026-10-28: 「ok 兩個都核准」. Asked: 「審閱工具列驗收：核准推分支、開 PR，CI 全綠就合併（D1、D2 照建議）？」 '
                        '(Review share i7p4427an3vdqxv6; candidate 86e3ed1; the question says approving accepts D1 '
                        '(phone first-visitor bar accepted at 6 of 8, retest after release) and D2 (keep the decided '
                        "reviewer byline and correct ADR 0051's sentence before the PR); FO declines F1 to F5 in the "
                        'gate summary; F1 and F3 go to a follow-up before relay sends names)',
              'decision': 'approve'}],
  'amendments': []},
 {'corpus': 'qnow',
  'tip': '2b132074819d4eb6890f3bf731be321032a00442',
  'task': 'owner-picks-visited-branch',
  'record': 'validation-2.md',
  'report_commit': '73c0ab5fc2d88342885ec0d2a8404167b2da9cb3',
  'dispatch_commit': '7bd8ce86bb2db688acfcb46d139a1750a4649cae',
  'report_ordinal': 1,
  'prototype': 'PASS',
  'body': '## Stage Report: validation\n'
          '\n'
          "- F4 Needs decision for the Captain's script only: the design's Captain-run script lacks the "
          '`open-shop-entry` step; the script below is the corrected one (no product change).\n',
  'native': [{'attempt': 'gate-attempt:owner-picks-visited-branch-validation-1',
              'stage': 'validation',
              'kind': 'resolution',
              'by': 'person:captain',
              'at': '2026-10-10T03:03:09.036139Z',
              'reason': 'Captain 2026-10-10: 「准」 after his local acceptance run — deliver '
                        'd34ab1145af0f6af691e8be2f46fbcad0edebedb; the FO declines of F1-F3 accepted with approval, as '
                        'stated in the gate question',
              'decision': 'approve'}],
  'amendments': []},
 {'corpus': 'qnow',
  'tip': '2b132074819d4eb6890f3bf731be321032a00442',
  'task': 'production-operations',
  'record': 'validation-4.md',
  'report_commit': 'fcb7d2f744c554b05191461aa7eeb7920416e81d',
  'dispatch_commit': '2c6b40ca75be22340ae7ebe1069b0275246a0169',
  'report_ordinal': 3,
  'prototype': 'REFUSE',
  'body': '## Stage Report: validation\n'
          '\n'
          '\n'
          '\n'
          '## Stage Report: validation (cycle 2)\n'
          '\n'
          '\n'
          '\n'
          '## Stage Report: validation (cycle 3)\n'
          '\n'
          '- F1 Needs decision, small (not in this range; present since cycle 1). The runbook (Close an entry) says '
          '"the shop\'s staff can still use the office (it does not read the entry\'s open flag)" and ADR 0040 says '
          'the close "does not stop the office, which does not read the flag". At `477cbbd04` that is false: '
          '`branchEntry` in `reception-store.ts` filters `shopEntries.active = true`, and `options` and the staff '
          'booking read through it. Probe (a throwaway pg test on `createReceptionWorld`, deleted): `GET '
          '/api/office/booking-options` answered 200 with 3 services before `UPDATE shop_entries SET active = false` '
          'and 0 after, so staff cannot create a booking at that branch until `open`. Not Material under the '
          "four-field rule: the Captain's AC-6 names owner bookings and the shop 404, the harm is a false sentence "
          'plus an office that stops with the shop, and no field names a protected boundary. It reaches the Captain '
          'through the runbook and ADR 0040 line 41 ("reopens if the office must also be stopped"), so FO should rule: '
          'correct both sentences to say a close also stops staff booking creation (one line each), or change code to '
          'keep the office open (a product call, larger). The implementation report\'s "Limits" bullet repeats the '
          'false claim; roborev cycle 2 (`roborev:815`) did not catch it.\n',
  'native': [],
  'amendments': []},
 {'corpus': 'qnow',
  'tip': '2b132074819d4eb6890f3bf731be321032a00442',
  'task': 'branch-hours-generate-starts',
  'record': 'validation-2.md',
  'report_commit': 'ee9f1ca6a6e9b0e64a026e4b447344d8b99fe8a6',
  'dispatch_commit': 'c6e1c85af83cf3c3770345a2d20f9d98b438dc43',
  'report_ordinal': 1,
  'prototype': 'PASS',
  'body': '## Stage Report: validation\n'
          '\n'
          '- F2 Needs decision: dispatch-record checker exits 1 for Package root placement in implementation-2/3/4 and '
          'validation-1, plus completion-recipient placement in implementation-3/validation-1; their live contents '
          'resolve authority, but FO owns the recorded-format failure.\n'
          '- F3 Needs decision: journey-lint exits 1 on missing yaml; a declared local-yaml resolver attempt then '
          'fails on missing @tldraw/tlschema. No journey lint verdict or plugin repair is claimed.\n',
  'native': [],
  'amendments': ['### Amendment 2 — 2026-10-29\n'
                 '\n'
                 'Captain: 「准」\n'
                 "Source: Ideation gate attempt 2 resolution, recorded reason: 'Captain 2026-10-29: 「准」 — P1 design "
                 'and acceptance criteria approved for implementation; F7 decline accepted with a visible 「無可開始時段」 '
                 'state on the duration row repeated in the save confirm; AC-18 wording as last presented: 「可約開始時間 '
                 "09:00–16:00」 and 「每天最多 6 台（只做此服務時）」'\n"
                 'Supersedes: AC-18 "proposal only, not decided"\n'
                 'Design: AC-18 is decided as the wording last presented: 「可約開始時間 09:00–16:00」 and 「每天最多 6 台（只做此服務時）」, '
                 'with 「每台 3 筆 × 2 台」 kept as the small note in the expanded group only (FO note — implementation '
                 'start). The combined 「每天最多 6 台（每台 3 筆 × 2 台）」 proposal is not the approved text.'],
  'record_text': '# branch-hours-generate-starts — validation cycle 2\n'
                 '\n'
                 'Dispatched: 2026-10-29 from state commit 26b6fcde6c0623b608b11e5552b6c40fd31448c2; base origin/main '
                 '006a79e0a18e90bd8e5d86cc1541aede05cc953e\n'
                 'Candidate: 835ebc6eec26d439e3098ea0eb6fcb39e70063f8\n'
                 'Model: codex gpt-6.1-sol, reasoning xhigh (Paseo agent, fresh)\n'
                 'Package root: /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.33.0\n'
                 'Completion to `main`\n'
                 '\n'
                 '## Checklist\n'
                 '\n'
                 'Independent verdict on AC-1..AC-20 against candidate 835ebc6eec26d439e3098ea0eb6fcb39e70063f8: '
                 're-verify the cycle 4 and 5 repairs (390px weekday cards, finish labels, single and zero start '
                 'groups, conflict alert, owner disabled action, the three guard tests, recovery-record ownership, '
                 'readability fixes) by your own runs; for each criterion validation 1 marked INCOMPLETE, read the '
                 'evidence cycles 1-5 and validation 1 already hold and say whether it suffices, running only what is '
                 'missing for a core case\n'
                 'List every remaining untested permutation as a concrete residual row (criterion, case, why untested, '
                 'what a person would notice if it were wrong) so the Captain can rule row by row; a residual must '
                 'name a case whose representative cases were tested, never a blanket gap\n'
                 'Minimal acceptance script the FO can run verbatim in a fresh shell, updated for this candidate, plus '
                 'python3 <package>/scripts/adr_lint.py docs/adr --since 006a79e0a18e90bd8e5d86cc1541aede05cc953e '
                 '--require 0055 with its exit code\n'
                 'Record the built-screen review lines once the FO names the saved report, and list unverified '
                 'obligations plainly, including that no headed product screenshot exists\n'
                 '\n'
                 '## Scope notes\n'
                 '\n'
                 'Validation 2 of P1 (pilot, release 14). Validation 1 recommended REJECTED at 5c4e42116; FO '
                 'dispositions are in the task file under "FO disposition — validation 1 (2026-10-29)". Implementation '
                 'cycles 4 and 5 repaired the authorized findings; their stage reports and implementation-cycle-4 and '
                 'implementation-cycle-5 folders hold the evidence. Assess the exact candidate '
                 '835ebc6eec26d439e3098ea0eb6fcb39e70063f8; do not repair. A defect is a finding that returns through '
                 'feedback-to implementation.\n'
                 '\n'
                 'Settled by FO, do not report again unless the candidate changes the evidence: F1 browser-bundle '
                 'guard is a separate backlog task (office-browser-bundle-guard); F3 journey-lint dependency is an '
                 'environment limit; AC-18 wording is decided by Captain Amendment 2; capacity in first setup was '
                 'stored, not defaulted (cycle-4 SQL readback). The retained weekly-closure endpoints have no office '
                 'caller; name them under minimal necessity and do not remove them.\n'
                 '\n'
                 'Built-screen review: the design director is reviewing the cycle-5 pictures now. The FO will send you '
                 'the saved report path and its finding dispositions; add `Built screen review: <path>` and one `Built '
                 'screen finding N:` line per finding to your validation report exactly as the FO gives them, then run '
                 'python3 <package>/scripts/design_surfaces.py check on the task file and report its exit code. If the '
                 "FO's message has not arrived when you finish everything else, say so in the report instead of "
                 'writing those lines.\n'
                 '\n'
                 'Headed capture stalled in every earlier cycle; one diagnosed headed attempt is enough before the '
                 'authorised headless fallback of the same server and state. Every UI verdict rests on a DOM read or '
                 "SQL row, never on a screenshot or a tool's exit line. The acceptance harness and run command are in "
                 'implementation-cycle-1/README.md; copy it in temporarily and remove it before you finish. Sign in '
                 'with the authorised Clerk development test number only; change no Clerk setting.\n'
                 '\n'
                 'A verdict with an honest residual list is better than a long run. The Captain rules on the residual '
                 'rows at the gate.\n'
                 '\n'
                 'Package root: /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.33.0\n'
                 'Send your completion to `main` as your final reply.\n'},
 {'corpus': 'qnow',
  'tip': '2b132074819d4eb6890f3bf731be321032a00442',
  'task': 'branch-hours-generate-starts',
  'record': 'validation-3.md',
  'report_commit': 'ee9f1ca6a6e9b0e64a026e4b447344d8b99fe8a6',
  'dispatch_commit': '80c45c4b886b161d29f7671f35690e84a787311d',
  'report_ordinal': 1,
  'prototype': 'PASS',
  'body': '## Stage Report: validation\n'
          '\n'
          '- F2 Needs decision: dispatch-record checker exits 1 for Package root placement in implementation-2/3/4 and '
          'validation-1, plus completion-recipient placement in implementation-3/validation-1; their live contents '
          'resolve authority, but FO owns the recorded-format failure.\n'
          '- F3 Needs decision: journey-lint exits 1 on missing yaml; a declared local-yaml resolver attempt then '
          'fails on missing @tldraw/tlschema. No journey lint verdict or plugin repair is claimed.\n',
  'native': [],
  'amendments': ['### Amendment 2 — 2026-10-29\n'
                 '\n'
                 'Captain: 「准」\n'
                 "Source: Ideation gate attempt 2 resolution, recorded reason: 'Captain 2026-10-29: 「准」 — P1 design "
                 'and acceptance criteria approved for implementation; F7 decline accepted with a visible 「無可開始時段」 '
                 'state on the duration row repeated in the save confirm; AC-18 wording as last presented: 「可約開始時間 '
                 "09:00–16:00」 and 「每天最多 6 台（只做此服務時）」'\n"
                 'Supersedes: AC-18 "proposal only, not decided"\n'
                 'Design: AC-18 is decided as the wording last presented: 「可約開始時間 09:00–16:00」 and 「每天最多 6 台（只做此服務時）」, '
                 'with 「每台 3 筆 × 2 台」 kept as the small note in the expanded group only (FO note — implementation '
                 'start). The combined 「每天最多 6 台（每台 3 筆 × 2 台）」 proposal is not the approved text.'],
  'record_text': '# branch-hours-generate-starts — validation cycle 2 follow-up (message to the running validator)\n'
                 '\n'
                 'Dispatched: 2026-10-29 from state commit 5503c5848dd8fc324aa8ece05d2a421fe0bfe896 as a Paseo '
                 'follow-up message to agent 7907abba\n'
                 'Candidate: 835ebc6eec26d439e3098ea0eb6fcb39e70063f8\n'
                 'Model: codex gpt-6.1-sol, reasoning xhigh (Paseo agent, reused)\n'
                 'Package root: /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.33.0\n'
                 'Completion to `main`\n'
                 '\n'
                 '## Checklist\n'
                 '\n'
                 'Record the built-screen review lines for design/review-4.yaml in the validation report exactly as '
                 'given, assess X1 and X2 as findings with their own F numbers and Material bullets, and report the '
                 'design_surfaces.py check exit code\n'
                 '\n'
                 '## Scope notes\n'
                 '\n'
                 "The director's pass 2a on the cycle-5 pictures is saved as design/review-4.yaml: two MAJOR (X1 "
                 'conflict alert hidden below the fold while 確認並儲存 is disabled; X2 timeline start labels scroll away '
                 'at 390 and 768) and seven MINOR (X3-X9). FO dispositions: X1 and X2 are findings for this '
                 'validation, routed to implementation; X3-X6 are routed by FO to the next implementation cycle; X7 '
                 'and X8 are proposed declines for director pass 2b; X9 is state coverage owned by validation.\n'
                 'Package root: /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.33.0\n'
                 'Send your completion to `main` as your final reply.\n'}]

if __name__ == "__main__":
    unittest.main()
