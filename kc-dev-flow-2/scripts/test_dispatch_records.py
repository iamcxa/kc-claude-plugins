import contextlib
import hashlib
import shutil
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
                if "record_text" in case:
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
  'ruling_commit': None,
  'record_text': '# validation-2\n'
                 '\n'
                 'Dispatched: e57feb6eec956b74a1d4b29f26f1d0a7d1693785 (workflow checkout, kc-dev-flow-2 0.32.1 '
                 'README); batch 9\n'
                 'Candidate: 9a70a3350436fac9e51d0795b3b4299693f020f8\n'
                 "Model: gpt-6-astra (Codex via Paseo, thinking high; the Captain's interim dispatch directive, chat "
                 '2026-10-26: 「接下來派工結束後新的派工盡量用 sol / astra，推理等級可以比 claude 高一級」)\n'
                 '\n'
                 '## Checklist\n'
                 '\n'
                 'Independent verdict on PR #742 head 9a70a335 against every acceptance criterion in the task file, '
                 're-running each evidence command and at least one falsifier per criterion yourself, and judging each '
                 'limit the implementation report states\n'
                 "Second validation on the same head after validation-1's F1 (missing native placement receipt): judge "
                 "AC-2 and AC-6 from FO's native placement trial in the task folder, "
                 'paseo-codex-dispatch-practice/validation-1/native-placement-trial.md with its two JSON receipts '
                 '(success run with --new-workspace local --cwd placed the agent in the worktree; plain --cwd control '
                 "from an agent caller inherited the caller's workspace); Captain amendment 1 applies; AC-3 and AC-4 "
                 "evidence is FO's publication (push of 9a70a335, Draft PR #742 by FO, RoboRev evidence=roborev:1296 "
                 "clean on 9a70a3350); validation-1's F2 is Polish\n"
                 'A minimal acceptance script the Captain can run (three to six steps, exact commands, expected '
                 'output), run by you exactly as written in a fresh bash shell, with its observed output; '
                 '/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.32.1/scripts/adr_lint.py '
                 'docs/adr --since <base> with its exit code; your verdict naming the head, with findings classified '
                 "by the workflow's Review-finding disposition\n"
                 '\n'
                 '## Scope notes\n'
                 '\n'
                 'Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.32.1\n'
                 '\n'
                 'Number guards: ADR: 0042\n'
                 '\n'
                 'Profile: pilot. Candidate: iamcxa/kc-claude-plugins PR #742, head '
                 '9a70a3350436fac9e51d0795b3b4299693f020f8, base origin/main. This task; other PRs may be in flight '
                 'and are not your candidate. Check the candidate out detached in a throwaway worktree and remove it '
                 'after. Commit your stage report with `spacedock state commit paseo-codex-dispatch-practice '
                 '--workflow-dir '
                 '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2`. '
                 'Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not '
                 'push, comment on any PR, request reviews or mark ready.\n'
                 '\n'
                 "Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered "
                 'here).\n'},
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
  'ruling_commit': None,
  'record_text': '# validation-2-message-1\n'
                 '\n'
                 'Dispatched: e57feb6eec956b74a1d4b29f26f1d0a7d1693785 (workflow checkout, kc-dev-flow-2 0.32.1 '
                 'README); batch 9, follow-up message to the validation-2 worker (Paseo 850ab15c), answering its AC-6 '
                 'trace question\n'
                 'Candidate: 9a70a3350436fac9e51d0795b3b4299693f020f8\n'
                 "Model: gpt-6-astra (Codex via Paseo, thinking high; the same worker as validation-2; the Captain's "
                 'interim dispatch directive, chat 2026-10-26: 「接下來派工結束後新的派工盡量用 sol / astra，推理等級可以比 claude 高一級」)\n'
                 '\n'
                 '## Checklist\n'
                 '\n'
                 "Judge AC-6's build-to-spawn transport from your own dispatch as the only existing trace: `spacedock "
                 'dispatch build` wrote '
                 '/tmp/spacedock-dispatch/5c030106-8d82-4542-855e-1498b2563c69-spacedock-ensign-paseo-codex-dispatch-practice-validation.md '
                 '(sha256 6d78f0c89090c8c0c2aaba3d88544456346027f21ba6bf609ae7dee4316ac106 at this message), and FO '
                 'spawned you through Paseo MCP create_agent with provider codex/gpt-6-astra, settings modeId '
                 'auto-review and thinkingOptionId high, and an initialPrompt that names that file plus three FO '
                 "sentences (the Codex ensign skill path, the Codex package path, and FO's reading of PR #742's "
                 'checks); read your own Paseo status and first activity to compare\n'
                 'State its limits as found: that spawn was placed by the old practice (no workspace binding; your cwd '
                 "is the FO workspace), FO's wrapper adds sentences around the generated pointer rather than passing "
                 "it unchanged, and no trace uses the candidate's `--new-workspace local --cwd` route with a generated "
                 'dispatch\n'
                 'Return F1 as still open or closed on that evidence; FO creates no further test agents for this '
                 'validation\n'
                 '\n'
                 '## Scope notes\n'
                 '\n'
                 'Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.32.1\n'
                 '\n'
                 'Everything in validation-2 stands. Never run `git remote set-url` or any `git config` write in a '
                 'worktree of this repository.\n'
                 '\n'
                 "Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered "
                 'here); through Paseo, your final reply is that message.\n'},
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
  'ruling_commit': None,
  'record_text': '# validation-4\n'
                 '\n'
                 'Dispatched: e57feb6eec956b74a1d4b29f26f1d0a7d1693785 (workflow checkout, kc-dev-flow-2 0.32.1 '
                 'README); batch 9\n'
                 'Candidate: 9a70a3350436fac9e51d0795b3b4299693f020f8\n'
                 'Model: gpt-6-astra (Codex via Paseo, thinking high; spawned by FO through the candidate route: paseo '
                 'agent run --new-workspace local --cwd <implementation worktree> with the generated prompt passed '
                 "unchanged; the Captain's interim dispatch directive, chat 2026-10-26: 「接下來派工結束後新的派工盡量用 sol / "
                 'astra，推理等級可以比 claude 高一級」)\n'
                 '\n'
                 '## Checklist\n'
                 '\n'
                 'Independent verdict on PR #742 head 9a70a335 against every acceptance criterion in the task file, '
                 're-running each evidence command and at least one falsifier per criterion yourself, and judging each '
                 'limit the implementation report states\n'
                 "Third validation on the same head, for validation-2's open F1 (integrated build-to-spawn transport) "
                 'only, plus a recheck that nothing else changed: you were spawned by FO through the candidate route, '
                 '`paseo agent run --new-workspace local --cwd` at the implementation worktree, with the prompt '
                 '`dispatch build` generated passed unchanged as the whole initial prompt; compare your own Paseo '
                 'status and first activity with this record (provider, model, thinking, mode, cwd, workspace, prompt '
                 "bytes) and with the assignment file's bytes; FO's create_agent workspaceId trial (agent ddf30e67) is "
                 'in paseo-codex-dispatch-practice/validation-3/; PR #742 checks on this head were read by FO: '
                 'adr-path-check, unit tests (python3), multi-profile route gate (live Spacedock), version parity and '
                 'GitGuardian pass\n'
                 'A minimal acceptance script the Captain can run (three to six steps, exact commands, expected '
                 'output), run by you exactly as written in a fresh bash shell, with its observed output; '
                 '/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.32.1/scripts/adr_lint.py '
                 'docs/adr --since <base> with its exit code; your verdict naming the head, with findings classified '
                 "by the workflow's Review-finding disposition\n"
                 '\n'
                 '## Scope notes\n'
                 '\n'
                 'Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.32.1\n'
                 '\n'
                 'Number guards: ADR: 0042\n'
                 '\n'
                 'Profile: pilot. Candidate: iamcxa/kc-claude-plugins PR #742, head '
                 '9a70a3350436fac9e51d0795b3b4299693f020f8, base origin/main. This task; other PRs may be in flight '
                 'and are not your candidate. Check the candidate out detached in a throwaway worktree and remove it '
                 'after. Commit your stage report with `spacedock state commit paseo-codex-dispatch-practice '
                 '--workflow-dir '
                 '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2`. '
                 'Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not '
                 'push, comment on any PR, request reviews or mark ready.\n'
                 '\n'
                 "Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered "
                 'here).\n'},
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
  'ruling_commit': None,
  'record_text': '# validation-3-message-1\n'
                 '\n'
                 'Dispatched: e57feb6eec956b74a1d4b29f26f1d0a7d1693785 (workflow checkout, kc-dev-flow-2 0.32.1 '
                 'README); batch 9, follow-up message to the validation-3 worker (Paseo 1d987cbe), answering its '
                 'request for the build and spawn commands\n'
                 'Candidate: 9a70a3350436fac9e51d0795b3b4299693f020f8\n'
                 "Model: gpt-6-astra (Codex via Paseo, thinking high; the same worker as validation-3; the Captain's "
                 'interim dispatch directive, chat 2026-10-26: 「接下來派工結束後新的派工盡量用 sol / astra，推理等級可以比 claude 高一級」)\n'
                 '\n'
                 '## Checklist\n'
                 '\n'
                 "Read paseo-codex-dispatch-practice/validation-3/build-to-spawn-sequence.md: FO's four tool calls "
                 'from the validate.py call (which runs `spacedock dispatch build`) to the `paseo agent run` spawn, '
                 "verbatim and in order; do not read FO's session transcript, which holds unrelated conversation\n"
                 'Judge AC-2\'s "no operation inserted between Spacedock build and immediate spawn" on it as found: FO '
                 "inserted two operations (reading the create_agent trial's activity, then writing receipts and "
                 'running `spacedock state commit`), about 28 seconds between build and spawn\n'
                 "Judge AC-6's unchanged prompt and fields from your own status, first activity, generated-prompt.txt "
                 'and the spawn command in call 4\n'
                 '\n'
                 '## Scope notes\n'
                 '\n'
                 'Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.32.1\n'
                 '\n'
                 'Everything in validation-3 stands. Never run `git remote set-url` or any `git config` write in a '
                 'worktree of this repository.\n'
                 '\n'
                 "Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered "
                 'here); through Paseo, your final reply is that message.\n'},
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
  'ruling_commit': 'd24235a4c759f908770a7a93ee215b87c225c496',
  'record_text': '# validation-6\n'
                 '\n'
                 'Dispatched: e57feb6eec956b74a1d4b29f26f1d0a7d1693785 (workflow checkout, kc-dev-flow-2 0.32.1 '
                 'README); batch 9\n'
                 'Candidate: 9a70a3350436fac9e51d0795b3b4299693f020f8\n'
                 'Model: gpt-6-astra (Codex via Paseo, thinking high; FO builds this dispatch and spawns it in the '
                 'same shell command, nothing between, through the candidate route: paseo agent run --new-workspace '
                 "local --cwd <implementation worktree> with the generated prompt unchanged; the Captain's interim "
                 'dispatch directive, chat 2026-10-26: 「接下來派工結束後新的派工盡量用 sol / astra，推理等級可以比 claude 高一級」)\n'
                 '\n'
                 '## Checklist\n'
                 '\n'
                 'Independent verdict on PR #742 head 9a70a335 against every acceptance criterion in the task file, '
                 're-running each evidence command and at least one falsifier per criterion yourself, and judging each '
                 'limit the implementation report states\n'
                 "Fourth validation on the same head, for validation-3's F1 only (immediate-spawn order), under the "
                 "Captain's validation-gate hold (「准」, 2026-10-28): FO ran this record's build (inside validate.py) "
                 'and the spawn in one shell command with no other operation between; FO saves that exact command line '
                 "and its timestamps to paseo-codex-dispatch-practice/validation-4/ after you start; judge AC-2's "
                 "order and AC-6's unchanged prompt and fields from your own Paseo status and first activity and that "
                 'receipt; recheck nothing else changed at the head\n'
                 'A minimal acceptance script the Captain can run (three to six steps, exact commands, expected '
                 'output), run by you exactly as written in a fresh bash shell, with its observed output; '
                 '/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.32.1/scripts/adr_lint.py '
                 'docs/adr --since <base> with its exit code; your verdict naming the head, with findings classified '
                 "by the workflow's Review-finding disposition\n"
                 '\n'
                 '## Scope notes\n'
                 '\n'
                 'Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.32.1\n'
                 '\n'
                 'Number guards: ADR: 0042\n'
                 '\n'
                 'Profile: pilot. Candidate: iamcxa/kc-claude-plugins PR #742, head '
                 '9a70a3350436fac9e51d0795b3b4299693f020f8, base origin/main. This task; other PRs may be in flight '
                 'and are not your candidate. Check the candidate out detached in a throwaway worktree and remove it '
                 'after. Commit your stage report with `spacedock state commit paseo-codex-dispatch-practice '
                 '--workflow-dir '
                 '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2`. '
                 'Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not '
                 'push, comment on any PR, request reviews or mark ready.\n'
                 '\n'
                 "Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered "
                 'here).\n'},
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
  'ruling_commit': 'd24235a4c759f908770a7a93ee215b87c225c496',
  'record_text': '# validation-4-message-1\n'
                 '\n'
                 'Dispatched: e57feb6eec956b74a1d4b29f26f1d0a7d1693785 (workflow checkout, kc-dev-flow-2 0.32.1 '
                 'README); batch 9, follow-up message to the validation-4 worker (Paseo b23132a3), answering its '
                 'receipt-defect report\n'
                 'Candidate: 9a70a3350436fac9e51d0795b3b4299693f020f8\n'
                 "Model: gpt-6-astra (Codex via Paseo, thinking high; the same worker as validation-4; the Captain's "
                 'interim dispatch directive, chat 2026-10-26: 「接下來派工結束後新的派工盡量用 sol / astra，推理等級可以比 claude 高一級」)\n'
                 '\n'
                 '## Checklist\n'
                 '\n'
                 'Read the appended "Correction, 2026-10-28 (FO)" section of '
                 'paseo-codex-dispatch-practice/validation-4/build-and-spawn.md: the original build-and-spawn tool '
                 'call (2026-10-28T14:42:10.210Z UTC) verbatim, with the wrong block kept above it\n'
                 'Use the assignment file hash it states (sha256 '
                 'aaf3881ac0baef72d55622205b7f5810e20f38a6693a98a0a12593dfc23ee512, modified 14:42:14.727Z), noting FO '
                 'did not hash it at build time\n'
                 "Judge AC-2's order and AC-6's fields on that receipt, your own Paseo status and first activity, and "
                 'treat the receipt defect as found\n'
                 '\n'
                 '## Scope notes\n'
                 '\n'
                 'Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.32.1\n'
                 '\n'
                 'Everything in validation-4 stands. Never run `git remote set-url` or any `git config` write in a '
                 'worktree of this repository.\n'
                 '\n'
                 "Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered "
                 'here); through Paseo, your final reply is that message.\n'},
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



ADR_DESIGN = "\n## Design\n\nWrite `docs/adr/<FO-reserved-number>-a-decision.md`.\n"
ADR_TASK = "---\nprofile: pilot\n---\n" + ADR_DESIGN


class DesignAdrTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.task = self.root / "task.md"
        self.record = self.root / "task/dispatch/implementation-1.md"
        self.record.parent.mkdir(parents=True)
        self.task.write_text(ADR_TASK)
        self.record.write_text(COMPLETE)

    def cli(self, mode="--names", script=None):
        args = [mode, str(self.record)] if mode == "--names" else list(mode)
        done = subprocess.run([sys.executable, "-B", str(script or Path(records.__file__)), *args],
                              capture_output=True, text=True)
        return done.returncode, done.stdout + done.stderr

    def assert_missing(self, only=True):
        code, out = self.cli()
        self.assertEqual(code, 1, out)
        expected = f"{self.record}:1: {records.ADR_RESERVATION_ERROR}\n"
        self.assertEqual(out if only else out.splitlines(keepends=True)[0], expected)
        return out[len(expected):]

    def test_raw_740_bytes_refuse_then_allocator_recovery_and_missing_line_controls(self):
        for text, digest in ((RAW_ADR_TASK, "9cdb2a04175c91eb996fb8c314067cfd6fe5fe4636ef399b97fc0effa4288406"),
                             (RAW_ADR_RECORD, "5f80555583c521fc2f21cca8ea407d542335b8d371a8f34c934e8b1b40ae6c20")):
            self.assertEqual(hashlib.sha256(text.encode()).hexdigest(), digest)
        self.task.write_text(RAW_ADR_TASK)
        self.record.write_text(RAW_ADR_RECORD)
        baseline_error = self.assert_missing(only=False)
        self.assertIn("Captain amendment form", baseline_error)
        self.assertIn("docs/adr/<FO-reserved-number>-seed-admission-enforces-required-fields.md", RAW_ADR_TASK)
        def git(*args):
            done = subprocess.run(["git", "-C", str(self.root), *args], capture_output=True, text=True,
                                  env={**os.environ, **IDENTITY})
            self.assertEqual(done.returncode, 0, done.stderr)
        git("init", "-b", "main")
        git("add", "task.md", "task/dispatch/implementation-1.md")
        git("commit", "-m", "raw replay")
        result = subprocess.run([sys.executable, "-B", str(Path(records.__file__).with_name("number_guards.py")),
                                 "reserve", "--kind", "adr", "--repo", str(self.root), "--base", "HEAD",
                                 "--state-dir", str(self.root), "--task", str(self.task)], capture_output=True, text=True)
        self.assertEqual((result.returncode, result.stdout, result.stderr), (0, "ADR: 0001\n", ""))
        repaired = RAW_ADR_TASK + "\n## Number guards\n" + result.stdout
        self.task.write_text(repaired)
        self.record.write_text(RAW_ADR_RECORD + result.stdout)
        self.assertEqual(self.cli(), (1, baseline_error))
        for number in ("", "Migration: 0001\n"):
            with self.subTest(number=number):
                self.task.write_text(RAW_ADR_TASK + "\n## Number guards\n" + number)
                self.record.write_text(RAW_ADR_RECORD + result.stdout + number)
                self.assertEqual(self.assert_missing(only=False), baseline_error)
        self.task.write_text(repaired)
        self.record.write_text(RAW_ADR_RECORD)
        code, out = self.cli()
        self.assertEqual(code, 1, out)
        self.assertIn("reserved line 'ADR: 0001' missing from scope notes", out)
        self.assertNotIn("design ADR placeholder", out)

    def test_profiles_layouts_and_first_repeated_message_records(self):
        for index in (False, True):
            task = self.root / "task/index.md" if index else self.root / "task.md"
            self.task.unlink(missing_ok=True)
            self.task = task
            for profile in ("pilot", "prod", "poc", "other"):
                self.task.write_text(ADR_TASK.replace("pilot", profile))
                for name in ("implementation-1.md", "implementation-2.md", "implementation-2-message-1.md",
                             "ideation-1.md", "implementation-0.md", "implementation-01.md", "implementation-2-message-0.md"):
                    self.record = self.record.with_name(name)
                    self.record.write_text(COMPLETE)
                    with self.subTest(index=index, profile=profile, name=name):
                        expected = profile in {"pilot", "prod"} and bool(records.IMPLEMENTATION_RECORD.fullmatch(name))
                        self.assertEqual(self.cli()[0], int(expected))
        self.record = self.record.with_name("validation-1.md")
        self.record.write_text(COMPLETE.replace("Model: sonnet", "Candidate: " + HEAD + "\nModel: sonnet"))
        self.assertEqual(self.cli(), (0, ""))

    def test_supported_paths_heading_suffixes_lists_tables_and_inline_code(self):
        for heading in ("## Design", "## Design — replacement", "## Design: replacement"):
            for path in ("docs/adr/<FO-reserved-number>-a.md", "docs/adr/<reserved number>-<short title>.md"):
                for form in (path, f"- `{path}`", f"| deliverable | `{path}` |", f"### Record\n#### File\n{path}"):
                    with self.subTest(heading=heading, form=form):
                        self.task.write_text("---\nprofile: pilot\n---\n" + heading + "\n" + form)
                        self.assert_missing()

    def test_history_quotes_fences_numbered_paths_and_authorized_current_design_replacement(self):
        for text in ("", "## Other design\n" + ADR_DESIGN.split("\n", 3)[-1],
                     "## Design\ndocs/adr/0041-existing.md\nADR required approved ruling",
                     "## Stage Report: ideation\ndocs/adr/<reserved number>-old.md",
                     ADR_DESIGN + "\n## Design — revised\nThe authorized revision removes the deliverable.\n## Stage Report: ideation\n" + ADR_DESIGN.replace("## Design", "### Old Design"),
                     "## Design\n> docs/adr/<n>-quoted.md\n   > docs/adr/<n>-indented.md",
                     "## Design\n```md\n## Design\ndocs/adr/<n>-example.md\n```\n",
                     "## Design\n~~~md\ndocs/adr/<n>-example.md\n~~~\n",
                     "## Design\ndocs/adr/<>-empty.md\ndocs/adr/<n>-.md\ndocs/adr/<two\nlines>-x.md"):
            with self.subTest(text=text):
                self.task.write_text("---\nprofile: pilot\n---\n" + text)
                self.assertEqual(self.cli(), (0, ""))
        self.task.write_text(ADR_TASK + "```\n## Design\nNo ADR\n```\n## Stage Report: ideation\nNothing\n")
        self.assert_missing()
        self.task.write_text(ADR_TASK.replace("Write", "Do not write"))
        self.assert_missing()

    def test_reservation_parser_scope_copy_and_unrelated_modes_remain_unchanged(self):
        for number in ("0020", "20"):
            self.task.write_text(ADR_TASK + "\n## Number guards\nADR: " + number + "\n")
            self.record.write_text(COMPLETE + "ADR: 0020\n")
            self.assertEqual(self.cli(), (0, ""))
            self.record.write_text(COMPLETE)
            self.assertIn("reserved line", self.cli()[1])
            for name in ("implementation-2.md", "implementation-1-message-1.md"):
                self.record = self.record.with_name(name)
                self.record.write_text(COMPLETE)
                self.assertEqual(self.cli(), (0, ""))
            self.record = self.record.with_name("implementation-1.md")
        self.task.write_text(ADR_TASK)
        self.assert_missing()
        self.assertEqual(self.cli([str(self.record.parent.parent)])[0], 0)
        readme = self.root / "README.md"
        readme.write_text(WORKFLOW)
        self.task.write_text(ADR_TASK + "\n## Stage Report: implementation\n- DONE: work\n")
        self.assertEqual(self.cli(["--readme", str(readme), "--coverage", str(self.task), "--stage", "implementation"])[0], 0)
        for args in (("init", "-b", "main"), ("add", "task.md", "task/dispatch", "README.md"), ("commit", "-m", "records")):
            done = subprocess.run(["git", "-C", str(self.root), *args], capture_output=True, env={**os.environ, **IDENTITY})
            self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(self.cli(["--newest", str(self.root), "task"]), (0, ""))

    def test_actual_cli_controls_disposable_build_spawn_recorders_and_reading_cost(self):
        def dispatch():
            log = self.root / "calls"
            log.unlink(missing_ok=True)
            env = {**os.environ, "CHECKER": records.__file__, "RECORD": str(self.record), "LOG": str(log)}
            done = subprocess.run(["sh", "-c", '"$PYTHON" -B "$CHECKER" --names "$RECORD" && '
                                   'printf "build\\n" >> "$LOG" && printf "spawn\\n" >> "$LOG"'],
                                  capture_output=True, text=True, env={**env, "PYTHON": sys.executable})
            return done.returncode, done.stdout + done.stderr, log.read_text().splitlines() if log.exists() else []
        before = (self.task.read_bytes(), self.record.read_bytes())
        code, out, calls = dispatch()
        self.assertEqual((code, calls), (1, []))
        self.assertEqual(len(out.split()), 27)
        self.assertEqual(before, (self.task.read_bytes(), self.record.read_bytes()))
        self.task.write_text(ADR_TASK + "\n## Number guards\nADR: 0020\n")
        self.record.write_text(COMPLETE + "ADR: 0020\n")
        self.assertEqual(dispatch(), (0, "", ["build", "spawn"]))


class DesignAdrMutationTests(unittest.TestCase):
    def test_each_named_falsifier_breaks_a_behavioral_control_without_caches(self):
        cases = (
            ("no-predicate", "dispatch_records.py", 'and not facts["adr"] and design_adr_placeholder(task.read_text())', 'and False',
             "test_dispatch_records.DesignAdrTests.test_raw_740_bytes_refuse_then_allocator_recovery_and_missing_line_controls"),
            ("disconnected", "dispatch_records.py", 'check_task_facts(args[1:])', '0',
             "test_dispatch_records.DesignAdrTests.test_raw_740_bytes_refuse_then_allocator_recovery_and_missing_line_controls"),
            ("scope-only", "dispatch_records.py", 'not facts["adr"] and design_adr_placeholder', 'not facts["adr"] and "ADR: " not in path.read_text() and design_adr_placeholder',
             "test_dispatch_records.DesignAdrTests.test_raw_740_bytes_refuse_then_allocator_recovery_and_missing_line_controls"),
            ("migration-only", "dispatch_records.py", 'not facts["adr"] and design_adr_placeholder', 'not (facts["adr"] or facts["migration"]) and design_adr_placeholder',
             "test_dispatch_records.DesignAdrTests.test_raw_740_bytes_refuse_then_allocator_recovery_and_missing_line_controls"),
            ("poc-refusal", "dispatch_records.py", 'in {"pilot", "prod"}', 'in {"pilot", "prod", "poc"}',
             "test_dispatch_records.DesignAdrTests.test_profiles_layouts_and_first_repeated_message_records"),
            ("skip-continuation", "dispatch_records.py", 'IMPLEMENTATION_RECORD.fullmatch(path.name)', 'path.name == "implementation-1.md"',
             "test_dispatch_records.DesignAdrTests.test_profiles_layouts_and_first_repeated_message_records"),
            ("quoted-example", "dispatch_records.py", 'if not line.lstrip().startswith(">")', 'if True',
             "test_dispatch_records.DesignAdrTests.test_history_quotes_fences_numbered_paths_and_authorized_current_design_replacement"),
            ("fenced-example", "dispatch_records.py", 'for line in outside_fences(unquoted):', 'for line in unquoted.splitlines():',
             "test_dispatch_records.DesignAdrTests.test_history_quotes_fences_numbered_paths_and_authorized_current_design_replacement"),
            ("first-design", "dispatch_records.py", '                design = []', '                pass',
             "test_dispatch_records.DesignAdrTests.test_history_quotes_fences_numbered_paths_and_authorized_current_design_replacement"),
            ("no-diagnostic-parser", "laws_check.py", 'r"design ADR placeholder has no reserved ADR|"', 'r""',
             "test_laws_check.L2Test.test_missing_design_adr_is_an_event_violation_even_after_later_repair"),
            ("today-not-event", "laws_check.py", 'f"{commit}:{folder}.md"', 'f"HEAD:{folder}.md"',
             "test_laws_check.L2Test.test_missing_design_adr_is_an_event_violation_even_after_later_repair"),
        )
        with tempfile.TemporaryDirectory() as tmp:
            scripts = Path(tmp) / "scripts"
            shutil.copytree(Path(__file__).parent, scripts, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            for label, name, old, new, target in cases:
                with self.subTest(mutation=label):
                    path = scripts / name
                    original = path.read_text()
                    self.assertIn(old, original)
                    path.write_text(original.replace(old, new, 1))
                    done = subprocess.run([sys.executable, "-B", "-m", "unittest", target, "-q"], cwd=scripts,
                                          env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, capture_output=True, text=True)
                    path.write_text(original)
                    self.assertNotEqual(done.returncode, 0, label + done.stdout + done.stderr)
                    self.assertIn("AssertionError", done.stderr, label + done.stderr)
                    self.assertFalse(list(scripts.rglob("*.pyc")))

RAW_ADR_TASK = (
    '---\n'
    "title: The seed check refuses a task missing its schema's required fields\n"
    'variant: kc-dev-flow-2\n'
    'profile: pilot\n'
    'merge: pr\n'
    'status: implementation\n'
    'gates:\n'
    '    version: 1\n'
    '    records:\n'
    '        - id: gate:seed-check-requires-schema-fields:backlog\n'
    '          stage: backlog\n'
    '          attempts:\n'
    '            - id: gate-attempt:seed-check-requires-schema-fields-backlog-1\n'
    '              briefing:\n'
    '                id: briefing:seed-check-requires-schema-fields:backlog:attempt-1:revision-1\n'
    '                digest: sha256:dc63436ce0050258853ef8628ce43caff1e38886de1223d255cb4d35acb051bd\n'
    '                room-ref: ./seed-check-requires-schema-fields/review/backlog/briefing-1\n'
    '              resolution:\n'
    '                type: Resolution\n'
    '                id: resolution:spacedock:seed-check-requires-schema-fields:backlog:1\n'
    '                briefing: briefing:seed-check-requires-schema-fields:backlog:attempt-1:revision-1\n'
    '                by: person:captain\n'
    '                at: "2026-10-27T15:13:15.991672Z"\n'
    '                decision: approve\n'
    "                reason: Captain 「全准」 (chat, 2026-10-27) answering 「需要你決定：第 8 批 7 張任務的待辦關卡，要不要一起批准進入設計階段？同時把已經做完的 `peers-paseo-host-binding` 關掉。我建議全部批准，也關掉那張。」; accepts FO's recommendation\n"
    '              application:\n'
    '                target-stage: ideation\n'
    '                state: consumed\n'
    '        - id: gate:seed-check-requires-schema-fields:ideation\n'
    '          stage: ideation\n'
    '          attempts:\n'
    '            - id: gate-attempt:seed-check-requires-schema-fields-ideation-1\n'
    '              briefing:\n'
    '                id: briefing:seed-check-requires-schema-fields:ideation:attempt-1:revision-1\n'
    '                digest: sha256:64caa608237851af576a889ee7df38d34e811cbcc80b966c360e3ec02083082c\n'
    '                room-ref: ./seed-check-requires-schema-fields/review/ideation/briefing-1\n'
    '              resolution:\n'
    '                type: Resolution\n'
    '                id: resolution:spacedock:seed-check-requires-schema-fields:ideation:1\n'
    '                briefing: briefing:seed-check-requires-schema-fields:ideation:attempt-1:revision-1\n'
    '                by: person:captain\n'
    '                at: "2026-10-27T15:56:24.036692Z"\n'
    '                decision: approve\n'
    "                reason: Captain 「其他全照建議」 (chat, 2026-10-27) answering 「需要你決定：第 8 批的設計，照首席工程師的建議一起處理，可以嗎？6 張進入實作，1 張直接關掉，再送一份 issue 給 Spacedock。我和首席工程師都建議照這樣做。」, after he declined a second, unanchored batch review (「不須要」); accepts FO's recommendation\n"
    '              application:\n'
    '                target-stage: implementation\n'
    '                state: consumed\n'
    '---\n'
    '\n'
    '## Scope\n'
    '\n'
    "- Source: the Captain 「同意開 1 到 5，第 6 項併進「GPT 夥伴」提案」 (chat, 2026-10-27), answering FO's list of package-issue candidates (items 2 to 5 relayed by the relay FO, Paseo 1671c3a9, from its pair-once and room-specs-follow-web-part-select observer reports; item 1 relayed by the kc-ops-inbox FO, Paseo 46c2ebdf).\n"
    "- Bite: relay room-specs-follow-web-part-select had no budget, no stop condition and no `id:`, yet `design_surfaces.py check --seed` passed (relay FO's report).\n"
    '- Upstream first: `scripts/design_surfaces.py` (`check --seed`), the workflow README schema, Spacedock `new`.\n'
    '\n'
    '## FO alignment\n'
    '\n'
    'Alignment: needed before ideation; where the check runs is a package design choice.\n'
    'Surfaces: none\n'
    'Visible change: none\n'
    'Release review: not needed: workflow maintenance, on no journey map.\n'
    "Result: aligned 2026-10-27 on the outcome by the Captain's 「全准」 answering this task's backlog briefing-1 question, which named the seed check refusing a task missing its schema's required fields; which fields are required is put to him at the ideation gate.\n"
    "Reviewer: kc-dev-flow-2:chief-engineer opus 2026-10-27 — batch 8 review at the ideation gate (the Captain's batch ruling 2026-10-27): per-task disposition, the Captain's decisions, order and batch risk.\n"
    '\n'
    '## PRFAQ\n'
    '\n'
    "The seed check will tell the First Officer (FO) which required task fields are missing before asking the Captain to admit a task. It will check the package workflow's declared seed contract, retain the existing surface checks, and leave the task unchanged. A passing seed will still not prove that the Captain approved its contents.\n"
    '\n'
    '**Who benefits?** FO gets a field-specific refusal before the backlog gate, instead of learning after delivery that the task omitted its bounds. The observed Relay task is the acceptance example.\n'
    '\n'
    '**Why here?** This is a repair of the existing `design_surfaces.py check --seed` seam, not a new Spacedock hook or schema framework. Spacedock creates task identity; the package owns its required seed content. ADR 0027, “FO-write rules are checked by the script FO already runs at the write,” supports using that existing check. Skipping it can still bypass the refusal.\n'
    '\n'
    '**What is optional?** Surface artifacts and finished acceptance criteria are due after ideation, not at seed admission. Pull-request, worktree, gate, journey and number-reservation records are filled at their respective lifecycle steps, not invented to satisfy this check.\n'
    '\n'
    "**Will old tasks be rewritten?** No. The new field checks run only in `check --seed`, regardless of the task's recorded stage, so an explicit historical replay can expose incompatibility. Default `check` retains its present behavior. Ordinary seed calls remain at backlog admission and the existing idle reminder; this task neither reopens archived gates nor backfills any task. Existing backlog tasks must obtain real missing values from their scope owner before their next admission check.\n"
    '\n'
    '**What is not promised?** Presence is not approval or adequacy. The checker does not infer a budget, decide whether prose is a good stop condition, parse arbitrary README prose into a schema, validate every YAML feature, prevent direct dispatch, or change the proof-of-concept route. No hosted resource, credential, production obligation or CI trigger is added.\n'
    '\n'
    '## Design\n'
    '\n'
    '### Source chain and existing behavior\n'
    '\n'
    '- Code source: fetched `origin/main` at `8bf4f3582411e8e4238f19fbadda8ddeca6767be`; released package version in `kc-dev-flow-2/.claude-plugin/plugin.json` is `0.32.0`. The supplied Codex package is `/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.32.0`; its `scripts/design_surfaces.py` bytes equal that source revision. All package-script runs in this stage used this supplied package.\n'
    '- Spacedock first: read its own `internal/status/new.go`, `docs/schema/entity.mdschema.yml`, `skills/first-officer/references/fo-write-core.md` in the supplied Spacedock 0.27.3 package, plus native `spacedock new --help`. Its slug route deliberately omits `id` when stdin omits it; the slug is identity. The installed executable reports 0.27.2, so source and executable versions are separately named. A disposable native replay confirmed both omitted-id and matching-explicit-id inputs create successfully, exit 0. The former output has no stored id; the latter retains `id: with-id`. No upstream defect is claimed and no upstream change is needed for the recommendation below.\n'
    '- Package second: `references/sd/workflow.md` Schema and Task Template explicitly require/illustrate a stored `id`. The adopted workflow repeats that requirement despite `id-style: slug`. `check_task()` returns from its seed branch after only the FO-alignment surface checks; it reads neither these five required frontmatter fields nor Scope bounds. This is the demonstrated missing seam.\n'
    "- Sibling adopters third, read only: Relay `beirut-dev2`, Web `dev2-fo`, and QNow `qnow-adopt-dev2` each have `docs/dev2/README.md` with `id-style: slug` and the same Schema paragraph. Relay's archived `room-specs-follow-web-part-select.md` has Scope and a separate Non-goals section but no stored `id`, budget or stop condition. Both installed check modes return 0 on it.\n"
    '- Bounded search: inspected the checker and its tests, then searched every package caller/import of `design_surfaces`. `pr_watch.py seeds()` invokes seed mode and replaces diagnostic detail with “fix its ## FO alignment”; the observer skill invokes seed mode on historical backlog snapshots and currently labels exit 1 a violation. Other consumers import existing symbols or run default mode; preserve those interfaces. External/manual invocations beyond the package are not exhaustively known.\n'
    "- Prior decisions: read Accepted ADR 0027 and ADR 0020, “A rise in the workflow word budget needs a Captain ruling recorded with it,” at the source revision. Searched state `Override:` gate-reason lines; none concerns seed fields, their format or this id conflict. The no-phrase-check ruling inside ADR 0027 rules out claiming that recognizing words proves a person's intent.\n"
    '\n'
    '### Required and optional fields\n'
    '\n'
    'This is what the current workflow README says, before the proposed enforcement changes:\n'
    '\n'
    '| Location | Required by current README | Not a required seed field |\n'
    '| --- | --- | --- |\n'
    "| Frontmatter | `id`, `title`, `status`, `variant: kc-dev-flow-2`, the user's selected `profile` | `merge`, `worktree`, `pr` appear in the template but are not listed by Schema as mandatory seed fields; existing delivery rules still apply later |\n"
    '| Body | Approved outcome, scope, non-goals, budget, stop condition | Specific labels for those concepts are not currently mandated |\n'
    '| Later design | Bold acceptance-criterion declarations with individual evidence clauses | Finished criteria, previews, schema artifacts and reviews are not demanded by seed mode |\n'
    '| Conditional lifecycle | Journey fields when assigned to a release, number reservations when needed, Spacedock-owned gate/report state | No blanket demand for journey, migration, ADR, completion, verdict or gate fields at seed admission |\n'
    '\n'
    "The five-stage route admits `pilot` or `prod`; the separate proof-of-concept workflow admits `poc`. Profile/route compatibility remains FO's existing check. This design adds missing-field refusal, not a new generic workflow graph validator. Unknown extension fields are preserved and ignored by this new check.\n"
    '\n'
    "### Proposed contract, subject to the Captain's decision\n"
    '\n'
    'Keep the five explicitly declared frontmatter fields, including stored `id`. For slug workflows, FO supplies the matching slug as `id` in stdin to `spacedock new`; the native replay shows this supported route. Never synthesize an id from the filename inside the checker: that would silently waive the README requirement. Flat and folder-form tasks have the same required fields.\n'
    '\n'
    "Require a non-empty `## Scope` section for the outcome/scope, and non-empty Non-goals, Budget and Stop condition records. Accept either a labeled line inside Scope (optional `- ` or `* ` bullet), or its own level-two section; accept singular/plural Non-goal(s) and Stop condition(s). This retains Relay's existing separate Non-goals section. Ignore examples inside backtick or tilde code fences and nested frontmatter keys; a similarly named line in a report, quote or unrelated section must not satisfy the field. This explicit form is a proposed schema clarification, not a claim that old free prose violated a previously mandated format.\n"
    '\n'
    "Read only the opening frontmatter mapping. Absent fields, empty/whitespace-only values, empty quoted strings, YAML null (`null`, `~`, or an empty value/comment), and unfilled angle-bracket placeholders fail with the field name. Support the ordinary plain/quoted scalar forms used by Spacedock; safely read inline comments and quoted colons. Reject ambiguous duplicate required keys or unsupported mapping/list/block-scalar values for a required scalar, rather than treating their punctuation as content. This is a bounded parser for these fields, not a new YAML dependency or validation of Spacedock's nested gate mapping. Test the boundary explicitly. Body labels require content, not an unfilled angle-bracket placeholder; the script does not decide whether a non-empty value is truthful or adequate.\n"
    '\n'
    "Add a small seed-field helper in `design_surfaces.py` and call it only in the seed branch, retaining all existing errors. A malformed or missing frontmatter block emits one structural error; otherwise list field defects in stable schema order, followed by body fields and existing alignment defects. Read errors are reported as a diagnostic/nonzero exit, not a traceback or pass. Preserve existing exit semantics: valid seed 0, rejected seed 1; argument errors remain 2. Do not infer a required-field list by scraping arbitrary prose at runtime: this package check implements this package's documented contract, with fixtures pinning their agreement.\n"
    '\n'
    'The new success line is `<task>: seed fields and FO alignment recorded`. Example Relay refusals are `<task>: missing required frontmatter field: id`, `<task>: missing required body field: Budget`, and `<task>: missing required body field: Stop condition`. `pr_watch.py seeds()` must tell FO to “fix the reported seed fields and run” the check rather than only fix FO alignment; its existing stage/readiness filters remain. No new remote call is needed.\n'
    '\n'
    "The observer's historical replay rule gains: “For a seed-field failure on a historical copy, report current-schema incompatibility; call it a historical violation only if the README at that event required the same form.” Missing event-time schema evidence is `can't tell`. Old surface failures retain their existing interpretation. This prevents a new labeling requirement being misreported as an old operator failure.\n"
    '\n'
    '```mermaid\n'
    'flowchart TD\n'
    '    A[FO records Captain-provided scope and required seed fields] --> B[FO runs existing seed check before backlog gate]\n'
    '    B --> C{Required fields and alignment present?}\n'
    '    C -- No --> D[Checker prints missing fields and exits 1]\n'
    '    D --> E[FO holds gate and obtains missing facts or a Captain decision]\n'
    '    E --> A\n'
    '    C -- Yes --> F[Checker exits 0]\n'
    '    F --> G[FO prepares backlog gate]\n'
    '    G --> H{Captain approves?}\n'
    "    H -- No --> I[Stop or revise within the Captain's direction]\n"
    '    H -- Yes --> J[FO dispatches ideation]\n'
    '```\n'
    '\n'
    'The actors, order, refusal, approval and stop above match the prose. Skipping the check is an acknowledged unsupported bypass, not a hidden automatic hook. Mermaid was reviewed against the prose; a rendered diagram was not exercised in this stage. `Surfaces: none` owes this PRFAQ/diagram, not a UI preview.\n'
    '\n'
    '### Proposed workflow wording\n'
    '\n'
    'Replace the Schema paragraph with the following text, retaining the separate stage and profile ownership rules:\n'
    '\n'
    "> Record non-empty `id`, `title`, `status`, `variant: kc-dev-flow-2`, and the user's selected `profile`. For `id-style: slug`, supply the slug as `id` to `spacedock new`; otherwise it omits that field. The five-stage route accepts `pilot` or `prod`; the POC adaptation removes ideation from frontmatter and Stages and accepts `poc` only. Before admission and dispatch, FO holds an unknown/mismatched profile; SD does not enforce this rule. Preserve approved outcome and scope under `## Scope`, with non-empty `Non-goals:`, `Budget:` and `Stop condition:` lines or matching level-two sections. Use bold **AC-N** declarations with individual evidence clauses.\n"
    '\n'
    "In the seed-check bullet replace “An FO that skips this step still dispatches; the worker's own check is the backstop.” with “An FO that skips this step still dispatches; no runtime hook blocks it.” Default mode is deliberately not a backstop for these new seed fields.\n"
    '\n'
    "Replace the Task Template's Scope placeholder with:\n"
    '\n'
    '```text\n'
    '<Approved outcome and scope.>\n'
    'Non-goals: <exclusions>\n'
    'Budget: <approved bound>\n'
    'Stop condition: <when to return to the Captain>\n'
    '```\n'
    '\n'
    "The package README's description of seed mode changes from “checks the FO record” to “checks seed fields and the FO record.” CLI help must describe seed fields too. The proof-of-concept derivative must still omit the seed gate and ideation; update its derivation fixtures if the revised Schema text changes their anchors, without adding a new proof-of-concept obligation.\n"
    '\n'
    '### Replay evidence and its limits\n'
    '\n'
    'The disposable classifier models missing/non-empty field and body-record presence only; it is not an implementation candidate and does not prove the proposed quoting, duplicate-key, placeholder or fence-edge handling. The existing package was actually executed in both modes on every committed entity at the snapshots below. Each input stayed unchanged during its two runs, and its SHA-256 matched `git show <state>:<path>` afterwards: 164 of 164 matches. No adopter task was edited.\n'
    '\n'
    '| Corpus | Pinned state commit | Files | Current seed: pass/fail | Proposed seed: pass/fail | Current default: pass/fail |\n'
    '| --- | --- | --- | --- | --- | --- |\n'
    '| This workflow, active and archive | `0d8847df7b0ef6e9046d8ff99dd6331bff010d2b` | 163 (69 active, 94 archived) | 140 / 23 | 0 / 163 | 73 / 90 |\n'
    '| Relay named example | `d20ff925992d34e70808b4291b32560afbc7fee5` | 1 | 1 / 0 | 0 / 1 | 1 / 0 |\n'
    '\n'
    'The 140 newly refused local seeds comprise 59 active and 81 archived tasks. All 23 existing failures retain failure; new diagnostics are additive. New default-mode enforcement is not proposed: its 73/90 result is the baseline, not a claimed future candidate pass. Relay currently prints `room-specs-follow-web-part-select.md: FO alignment recorded`; the proposal adds exactly id/Budget/Stop condition refusals. Its task SHA-256 is `a385615b692934c41a1c1664d3b1444cc09020cb03622c1ec7c0e95ed2ec0fa6`.\n'
    '\n'
    "Across the 163 local files the classifier finds no usable id in 162, Budget in 156, Stop condition in 157, Non-goals in 62, Scope in 16, and profile in 2. These are current-form compatibility findings, not claims that all these tasks lacked the underlying human decision. Every newly refused group is listed below for FO's ordering and migration assessment. No bulk repair is authorized.\n"
    '\n'
    '- Non-goals, Budget, Stop condition (1): `journey-server-host-pilot/index.md`.\n'
    '\n'
    '- id (2): `_archive/ops-metric-event-protocol.md`, `ops-inbox-r1-setup-and-isolation.md`.\n'
    '\n'
    '- id, Budget, Stop condition (93): `_archive/adr-protected-path-guard.md`, `_archive/agent-reads-governing-adr.md`, `_archive/board-optout.md`, `_archive/captain-question-load.md`, `_archive/chat-only-evidence-observer-blind.md`, `_archive/codex-reader-counts-code-review-only.md`, `_archive/codex-review-hang-detected.md`, `_archive/codex-review-round3-followups.md`, `_archive/commissioned-by-names-spacedock.md`, `_archive/copilot-quota-refusal-is-not-a-review.md`, `_archive/db-surface-without-migrations.md`, `_archive/delivery-gate-reads-folder-tasks.md`, `_archive/delivery-gate-settles-skipped-checks.md`, `_archive/delivery-gate-verdict-form.md`, `_archive/design-director-runs-ui-design-review.md`, `_archive/dev2-laws-check.md`, `_archive/extension-defaults-and-install-choice.md`, `_archive/extension-instruction-reaches-dispatch.md`, `_archive/fo-batch-sittings.md`, `_archive/fo-lifecycle-mod.md`, `_archive/fo-record-checks.md`, `_archive/fo-write-checks.md`, `_archive/fo-write-rules-checked.md`, `_archive/fo-written-lines-checked-before-dispatch.md`, `_archive/followup-dispatch-records-checked.md`, `_archive/followup-dispatch-records-round3-followups.md`, `_archive/idle-names-failing-seeds.md`, `_archive/journey-render-keeps-annotations.md`, `_archive/kc-adr-tools-with-dev2-copy.md`, `_archive/learn-delivery-follow-through.md`, `_archive/learn-delivery-round3-followups.md`, `_archive/merge-ask-holds-missing-clauses.md`, `_archive/names-check-before-dispatch.md`, `_archive/new-work-starts-from-a-story-map.md`, `_archive/observer-before-merge-guard.md`, `_archive/observer-check-round3-followups.md`, `_archive/patch-0102.md`, `_archive/patch-0103.md`, `_archive/peers-paseo-host-binding.md`, `_archive/poc-no-migrations.md`, `_archive/pr-watch-round3-followups.md`, `_archive/pr-watch-state-per-session.md`, `_archive/pr-watch-tasks-round3-followups.md`, `_archive/reflow-order.md`, `_archive/release-acceptance/index.md`, `_archive/release-review-staleness-held-at-dispatch.md`, `_archive/release-review.md`, `_archive/release-walk-picky-reviewers-and-director.md`, `_archive/replay-control-arm-round3-followups.md`, `_archive/review-followups-0102.md`, `_archive/role-triggers-owe-ce-on-review-drift.md`, `_archive/special-role-calls-fire-when-needed.md`, `_archive/stage-report-correction-path.md`, `_archive/worker-completion-goes-to-main.md`, `_archive/worker-knows-the-team-and-asks-early.md`, `_archive/workflow-checkout-must-match-trunk-readme.md`, `_archive/workflow-gaps-from-qnow-1270.md`, `adoption-asks-which-extensions.md`, `adr-required-statement.md`, `adr-silent-undo-probe.md`, `agents-md-holds-instructions.md`, `autopilot-l3-dogfood-spacedock-bridge.md`, `built-screen-check-round3-followups.md`, `claims-name-their-source.md`, `comment-check-reaches-delivery-gate.md`, `deprecate-kc-dev-flow-v1.md`, `design-director-model-follows-task.md`, `design-surfaces-task-dir-crash.md`, `dispatch-sets-reasoning-effort.md`, `fo-asks-to-raise-concurrency.md`, `fo-interviews-extension.md`, `fo-narrates-outward-writes.md`, `fo-write-checks-parse-top-level.md`, `gate-presentation-asks-one-thing-plainly.md`, `gpt-partner-extension-proposal.md`, `interrogation-strangers-isolated.md`, `journey-canvas-hosted-poc.md`, `journey-card-notes.md`, `journey-map-contract-round3-followups.md`, `journey-review-check-round3-followups.md`, `kc-adr-dev2-sharing-better-way.md`, `learn-names-agents-md-candidates.md`, `merge-check-reads-two-pr-tasks.md`, `merge-guard-stops-unasked-merges.md`, `new-work-checks-what-exists-first.md`, `override-recorded-when-captain-departs.md`, `prod-split-owes-chief-engineer-route-review.md`, `product-review-path-before-backlog.md`, `read-adr-honors-adr-folder.md`, `release-walk-due-trigger.md`, `retire-task-with-unconsumed-approval.md`, `rewalk-binds-prior-and-carries-complaints.md`, `workflow-checkout-round3-followups.md`.\n'
    '\n'
    '- id, Non-goals, Budget (1): `_archive/kc-decision-log-p1/index.md`.\n'
    '\n'
    '- id, Non-goals, Budget, Stop condition (36): `_archive/amendment-form-check.md`, `_archive/codex-reader-reads-receipt-marker.md`, `_archive/codex-reader-resolved-mark-adr.md`, `_archive/codex-reader-same-head-unresolved.md`, `_archive/dispatch-and-report-hygiene.md`, `_archive/ideation-gaps.md`, `_archive/merge-gatekeeper.md`, `_archive/migration-and-number-guards.md`, `_archive/number-guards-readme-shrink.md`, `_archive/override-reaches-gate-and-criteria-wait.md`, `_archive/peers-rules-name-each-host-binding.md`, `_archive/prod-security-validation-gate.md`, `_archive/review-cadence.md`, `_archive/special-role-triggers.md`, `_archive/ui-design-review-in-ideation.md`, `_archive/worker-loads-declared-package.md`, `_archive/workflow-budget-ratchet.md`, `archive-waits-for-observer-report.md`, `batch-reaches-each-gate-together.md`, `captain-ruling-sources-checked.md`, `copilot-not-run-line-carries-quote.md`, `dispatch-carries-reserved-adr-number.md`, `fo-tries-what-it-asks-the-captain.md`, `gate-summary-names-each-decline.md`, `ideation-preview-is-one-static-file.md`, `idle-hook-names-merged-tasks-without-learn.md`, `journey-fold-answers-open-placeholders.md`, `journey-probe-finds-nested-maps.md`, `observer-check-learn-only-when-listed.md`, `paseo-codex-dispatch-practice.md`, `repair-dispatch-asks-for-sibling-sites.md`, `reused-worker-dispatch-leaves-a-record.md`, `reviewer-negative-claim-shows-reach.md`, `seed-check-requires-schema-fields.md`, `superseded-criterion-without-dispatch-caught.md`, `workflow-readme-in-invocation-test.md`.\n'
    '\n'
    '- id, Non-goals, Stop condition (1): `_archive/kc-decision-log-cli.md`.\n'
    '\n'
    '- id, Scope, Non-goals, Budget, Stop condition (2): `_archive/journey-map-dev2-contract.md`, `_archive/prod-security-review-gates.md`.\n'
    '\n'
    '- id, Stop condition (3): `_archive/kc-adr-format-source.md`, `_archive/read-adr-reporting-rule-followup.md`, `kc-decision-log-handoff-trial.md`.\n'
    '\n'
    '- id, profile, Budget, Stop condition (1): `paseo-fo-board.md`.\n'
    '\n'
    'Reproduction: use the supplied 0.32.0 package, the state roots named in Source chain, and the pinned commits above. Enumerate tracked flat `<slug>.md` and `<slug>/index.md` entities at the state root and `_archive/`, excluding README and ancillary task folders. Run `python3 <package>/scripts/design_surfaces.py check --seed <task>` and `check <task>` per entity, recording stdout and exit. Compare bytes with `git show <state>:<path>` and reject a run on changed input; default mode also reads existing artifacts/history. The classifier used for the proposed missing-field projection is below. Feed it each pinned task text; projected seed exit is 1 when either the actual seed exit is nonzero or this list is nonempty. This is a research predicate, not shipping code.\n'
    '\n'
    '```python\n'
    'import re\n'
    '# ds is the supplied package scripts/design_surfaces.py module.\n'
    'def absent(text):\n'
    ' fm=ds.FRONTMATTER.match(text); fields={}\n'
    ' for l in (fm[1].splitlines() if fm else []):\n'
    "  m=re.match(r'^([\\w-]+):[ \\t]*(.*)$',l)\n"
    '  if m: fields[m[1]]=m[2].strip().strip(\'\\"\\\'\')\n'
    " missing=[k for k in ('id','title','status','variant','profile') if fields.get(k,'').lower() in ('','null','~')]\n"
    ' body=text[fm.end():] if fm else text\n'
    " plain='\\n'.join(ds.unfenced(body.splitlines()))\n"
    " scope=re.search(r'^## Scope\\s*\\n(.*?)(?=^## |\\Z)',plain,re.M|re.S)\n"
    " scope=scope[1] if scope else ''\n"
    " if not scope.strip(): missing.append('Scope')\n"
    " for label,pat in [('Non-goals',r'Non-goals?'),('Budget',r'Budget'),('Stop condition',r'Stop conditions?')]:\n"
    "  line=re.search(r'^(?:[-*] )?'+pat+r':[ \\t]*\\S[^\\n]*',scope,re.M|re.I)\n"
    "  section=re.search(r'^## '+pat+r'[ \\t]*\\n(.*?)(?=^## |\\Z)',plain,re.M|re.S|re.I)\n"
    '  if not line and not (section and section[1].strip()):missing.append(label)\n'
    ' return missing\n'
    '```\n'
    '\n'
    '### Words FO reads at each lifecycle moment\n'
    '\n'
    'Counts use whitespace splitting, as `lint-skills.py` does. Before is the pinned 0.32.0 source; after is the literal proposed wording above, not a built candidate. Path, task and PR placeholders each count as one token. Count both a newly printed diagnostic and the instruction that makes FO run it. This is not a word-saving claim.\n'
    '\n'
    '| Moment and measured passages/output | Before | Proposed after |\n'
    '| --- | --- | --- |\n'
    '| Entry/startup or full resume: package README + adopted workflow source + package mod | 3067 + 5565 + 48 = 8680 | 3070 + 5577 + 48 = 8695 |\n'
    '| Backlog admission, good seed: Seed check bullet + success output | 40 + 4 = 44 | 38 + 7 = 45 |\n'
    '| Backlog admission, Relay-shaped missing id/bounds: bullet + output | 40 + 4 = 44 | 38 + 19 = 57 |\n'
    '| Idle on an open PR, no backlog seed defect: package mod | 48 | 48; all existing PR fact/reviewer/next output unchanged |\n'
    '| Idle on an open or merged PR, one backlog seed newly refused | 48 + 0 = 48 | 48 + 28 = 76; the reminder uses “fix the reported seed fields and run” (the replacement itself remains seven words) |\n'
    '| Idle on a merged PR: package mod + learn extension | 48 + 282 = 330 | 330; existing observer/sentinel/learn step output unchanged |\n'
    '| After archive: learn extension | 282 | 282; learn instructions/output unchanged; historical seed findings have the qualification below |\n'
    '| Merge ask: Delivery authority + Extensions sections | 461 + 224 = 685 | 685; delivery-check output unchanged |\n'
    '\n'
    "These are the task's affected and neighboring package instruction passages, not total model context: unchanged Spacedock runtime instructions, review payloads and variable-length task/report text are excluded equally. No reduction of total FO reading is claimed. Open/merged-PR script output stays byte-identical when no backlog seed newly fails; a new seed reminder is an intended extra read. The observer worker loads 27 extra words (the exact sentence above), and FO sees that distinction in any historical finding; report length depends on the number of findings and is not a fixed saving. Validation must compare complete emitted output on the same controlled lifecycle fixtures, not substitute this table for runtime measurement.\n"
    '\n'
    "The workflow source grows by 12 words, 5565 to 5577 (Schema +4, seed-bypass sentence -2, template +10). Under ADR 0020 this requires the Captain's actual approval quote and `loaded: startup/resume` on the +12 budget step; do not insert a quote until the decision below is answered. The package README grows by 3 words. Nothing moves into a hidden always-read file.\n"
    '\n'
    '### Captain decision\n'
    '\n'
    '**Approve the explicit seed contract above, keeping stored `id` as the current README requires, plus labeled body bounds?** Recommendation: approve it as one schema decision, including the measured +12 workflow words. The choices are coupled: the chosen schema determines both which seeds fail and the creation instructions FO must follow.\n'
    '\n'
    'This catches the observed omission in the existing check, makes no upstream change, and permits the native `spacedock new` route by supplying a matching id. What gets worse: a redundant id must be supplied in slug workflows, 140 currently passing local seeds would fail if replayed, and old free-form body records may need explicit labels before a future admission. Missing scope/budget values must be decided, not guessed by a worker. Alternative: align the README with Spacedock by making id optional in slug workflows and enforce only the remaining fields; that reduces redundant data but changes the currently written requirement and needs an explicit schema choice. Neither option is approved by this ideation report.\n'
    '\n'
    "If approved, land one decision record titled “Seed admission enforces the workflow's explicit required fields”; leave its number to FO at implementation dispatch. The record distinguishes current schema compatibility from historical operator fault and records the seed-only scope. No other Captain decision is needed for parser/test placement. The recommended implementation bound is this package check and its existing consumers, with no adopter migration; stop and return to FO if implementation needs an upstream creation change, an additional persistent schema service, or automatic legacy repair. This is a recommendation for the gate, not a retroactive addition to this task's accepted Scope or budget.\n"
    '\n'
    '### Batch overlap\n'
    '\n'
    'Planned implementation files, all relative to the code repository:\n'
    '\n'
    '- `kc-dev-flow-2/scripts/design_surfaces.py`, `scripts/test_design_surfaces.py`: seed-field behavior and counterexamples; preserve all existing default-mode imports/output.\n'
    '- `kc-dev-flow-2/scripts/pr_watch.py`, `scripts/test_pr_watch.py`: correct the seed reminder and prove the actual seed subprocess reaches it; no new provider calls.\n'
    '- `kc-dev-flow-2/references/sd/workflow.md`, `scripts/lint-skills.py`: schema/template/bypass wording and the Captain-backed +12 budget step.\n'
    '- `kc-dev-flow-2/scripts/test_sd_dispatch.py`: update real seed fixtures and verify the native backlog definition still carries the check.\n'
    '- `kc-dev-flow-2/scripts/poc_readme.py`, `scripts/test_poc_readme.py`: only if the revised Schema changes a derivation anchor; preserve no-ideation/no-seed-gate output. These are conditional file touches, not permission to redesign that route.\n'
    '- `kc-dev-flow-2/README.md`, `skills/observer/SKILL.md`: accurate seed-mode description and historical-replay qualification.\n'
    '- `docs/adr/<FO-reserved-number>-seed-admission-enforces-required-fields.md`: the accepted ruling, if the Captain approves it. No existing ADR rewrite or index-file edit is proposed; `docs/adr/` is a shared number namespace. No adopted README, other task, CI workflow, release manifest or Spacedock source is changed by this design stage or automatically by the feature.\n'
    '\n'
    'Paths prefixed only with `scripts/` or `skills/` in the first list are under `kc-dev-flow-2/`.\n'
    '\n'
    '| Other task (task slug) | Shared file/check, based on current task record | Ordering consequence |\n'
    '| --- | --- | --- |\n'
    '| archive-waits-for-observer-report (archive waits for committed observer evidence) | Its newly written design directly shares `kc-dev-flow-2/README.md`, `scripts/test_sd_dispatch.py` and the ADR number namespace; it also changes mod/learn/adoption/recovery files outside this task. It leaves workflow/lint/watcher unchanged. | Serialize README/dispatch-fixture edits; preserve its upstream-dependent prerequisite and this historical-replay qualification independently. |\n'
    '| idle-hook-names-merged-tasks-without-learn (idle reminder for missing learning) | `scripts/pr_watch.py`, its tests, and startup/idle output measurement | Implement after that task or serialize watcher edits; rerun both sets of lifecycle fixtures. |\n'
    '| copilot-not-run-line-carries-quote (review refusal includes evidence quote) | No direct overlap in its current Scope: delivery checker and Copilot reader; shared end-to-end lifecycle measurement only | Independent code work; do not overwrite its merge-output assertions. |\n'
    '| dispatch-carries-reserved-adr-number (dispatch repeats reserved decision number) | Its newly written recommendation changes only its task record, no package files; dispatch checking imports helpers from this checker. | No ordering dependency under that recommendation; preserve imports and rerun dispatch tests. Recheck only if the Captain chooses broader coverage. |\n'
    '| seed-check-requires-schema-fields (this task: required seed fields) | Owns the file list above | Own task only; no sibling-state repair. |\n'
    '| journey-probe-finds-nested-maps (adoption finds nested journey maps) | Scope names adoption reference; no direct file overlap established. Adoption/POC tests may share integration coverage. | Independent unless its final design touches shared tests or README. |\n'
    "| read-adr-honors-adr-folder (decision reader respects supplied folder) | Source and copied read-ADR skill plus copy-sync script; none of this task's runtime files | Independent; consume whatever reader rule lands without editing its files. |\n"
    '| adr-required-statement (implementation states its decision records) | Historical design shares workflow/POC files and the ADR namespace, but the Captain closed it on 2026-10-20; its validation frontmatter is stale. | Do not wait for, land or revive that branch. Coordinate those files only if FO records a reopening. |\n'
    '| journey-server-host-pilot (private journey server on two hosts) | Current folder-form task changes journey-server package/docs; no seed file overlap, only ADR number namespace | Independent code; FO allocates distinct decision numbers. |\n'
    '| ops-inbox-r1-setup-and-isolation (signed events and isolated setup) | `kc-ops-inbox/**` and its workflow; no direct seed-file overlap, shared ADR namespace | Independent; its task is read-only input to the replay. |\n'
    '| pr-review-lite-value-pilot (supervised comparison of review routes) | Review-capability package scripts; no direct file/check overlap found | Independent. |\n'
    '| adr-silent-undo-probe (measure accidental reversal of an earlier ruling) | Held here and moved by Captain amendment to `adr-silent-undo-poc` in the POC workflow; no shipped package overlap declared | Do not redispatch this copy; the experiment grants no authority to change ADR rules. |\n'
    '| comment-check-reaches-delivery-gate (delivery checks comment evidence) | The Captain closed it on 2026-10-20 with the recommendation not to build; no live edit is inferred from its stale ideation status. Existing `delivery_gate.py` still imports this checker. | Do not revive its design. Preserve exported helpers and run the existing delivery consumer suite. |\n'
    '| journey-canvas-hosted-poc (prove a hosted shared canvas) | Journey hosting/canvas; no direct seed-file overlap found | Independent; no hosting action belongs in this task. |\n'
    '\n'
    'The current work state is shared and other stages remain live. The table describes read-only task-record evidence, not current remote PR status or an ownership grant. GitHub API state was not queried; the assignment uses git/local evidence. Proposed work must recheck the neighboring designs at dispatch because several batch tasks are still in ideation.\n'
    '\n'
    'Recommended order: coordinate the shared watcher files with `idle-hook-names-merged-tasks-without-learn`, and serialize README/dispatch-test edits with `archive-waits-for-observer-report`; then rebase this implementation and rerun corpus/consumer checks. Do not wait for or revive the closed ADR-statement/comment-check tasks. The reserved-number task currently recommends no source change. Other named tasks have no established same-file dependency. FO owns that ordering.\n'
    '\n'
    '## Acceptance criteria\n'
    '\n'
    '**AC-1**: Seed mode refuses each absent or empty required frontmatter field with a field-specific diagnostic and exit 1; a complete seed with no optional fields exits 0, in flat and folder form.\n'
    'Verified by: in `test_design_surfaces.py`, start with one complete seed, delete or blank each of the five fields individually, then restore it. Include quoted empty/null/comment-only/placeholder values, nested lookalikes, body lookalikes, malformed frontmatter and ambiguous duplicate keys. Verify input bytes unchanged. Falsifier: remove the new seed-field call or search the entire text instead of opening top-level frontmatter; each must make a named negative case pass and fail the test. Future implementation evidence; the current checker gap was observed, not fixed.\n'
    '\n'
    '**AC-2**: Scope and the three explicit body records are required in the accepted forms, without treating fenced examples, unrelated sections or empty labels as content; no missing value is invented.\n'
    "Verified by: a complete seed using Scope labels and one using dedicated sections both pass; remove each field separately and test backtick/tilde fenced impostors and headings in quotes. Relay's unchanged pinned task produces exactly the new id/Budget/Stop-condition reasons in seed mode. Falsifier: accept label-only content, scan all body sections, or remove fence exclusion; the corresponding impostor must flip from refused to accepted. Future implementation evidence; the disposable classifier covered the ordinary historical forms only.\n"
    '\n'
    "**AC-3**: The unchanged `spacedock new` mechanism can create a compliant slug seed when given the matching stored id; it does not itself enforce the package's required bounds.\n"
    'Verified by: in a disposable workflow, run the selected native binary on otherwise identical complete stdin with id omitted and with `id: <slug>` supplied. Creation succeeds for both; the proposed seed check refuses the first and passes the second. Include folder creation and a mismatching supplied id, which native Spacedock refuses. Falsifier: treating filename identity as the stored field makes the omitted-id negative case pass. Current evidence: the installed 0.27.2 executable created both omission and matching-id flat cases; the proposed-check/folder/mismatch matrix remains future work.\n'
    '\n'
    '**AC-4**: The refusal reaches the existing backlog/idle route with useful wording, while default `check`, imported helpers, optional fields and the proof-of-concept route preserve their behavior.\n'
    'Verified by: run `test_pr_watch.py`, `test_sd_dispatch.py --sd-plugin-root <selected Spacedock package>`, `test_poc_readme.py`, `test_dispatch_records.py`, `test_delivery_gate.py` and checker tests at the candidate. Use one backlog/needs-preparation task with valid alignment but missing id, invoking the actual seed subprocess rather than a stubbed refusal; require the reminder naming seed fields. Verify non-backlog rows stay filtered and a POC workflow gets no seed/ideation gate. Falsifier: suppress the helper call, keep the old FO-alignment-only instruction, or move the new field check before the seed branch; the relevant test must fail. Future evidence, not tested as a candidate in this stage.\n'
    '\n'
    '**AC-5**: Every changed corpus verdict is explained at the exact implementation candidate, with no silent archive/adopter repairs and no historical fault inferred solely from the new format.\n'
    "Verified by: execute base and candidate in both modes over all 163 pinned local tasks plus Relay, then repeat on all newly committed entities present at implementation time; retain path, input digest, exit and output. Seed changes must match accepted required-field failures; default outputs/exits must remain unchanged on identical history/artifacts. Test the observer instruction against an old free-prose snapshot and its event-time README, yielding current incompatibility or `can't tell`, not invented old-format violation. Falsifier: make seed enforcement unconditional or remove the historical qualification; the default comparison or retrospective case fails. Current evidence is the 164-file base run and explicit design projection above, not a candidate comparison.\n"
    '\n'
    '**AC-6**: Documentation, native dispatch fixtures and lifecycle wording agree with the approved schema; word changes and the durable ruling are explicit.\n'
    'Verified by: run package lint at the final rebased candidate with the actual Captain quote for any positive budget step, the POC/dispatch checks above, and compare complete output on fixed startup, valid/refused backlog, open/merged idle, archive and merge-ask scenarios using whitespace counts. Keep all baseline passages in both counts; show new diagnostics rather than claiming a saving. Run the existing ADR lint for the number FO reserves. Falsifier: count only workflow.md, drop a newly printed seed reminder, leave a template placeholder passing, remove the budget quote, or assert an old historical violation without matching old schema evidence; each must fail its declared check/review. Current evidence: literal proposed wording measures +12 workflow words and +3 package-README words; shipping checks remain future work.\n'
    '\n'
    '**AC-7**: The feature remains a read-only package seed check with no new upstream hook, provider request, automatic task migration or CI trigger.\n'
    'Verified by: run the seed matrix with input byte comparisons and network/process calls observed; inspect the named-file candidate diff and run the relevant existing package tests already selected by the current CI workflow. No implementation change outside the approved files without FO routing. Falsifier: add task mutation, a remote request, seed enforcement to default mode, or a new CI trigger; the byte comparison/call observation/diff review must fail. CI cost per PR was not measured in this design stage; no CI configuration change is proposed.\n'
    '\n'
    '## Captain amendments\n'
    '\n'
    '### Amendment 1 — 2026-10-27, chat\n'
    'Captain: 「其他全照建議」 (chat, 2026-10-27)\n'
    "Asked: 「需要你決定：第 8 批的設計，照首席工程師的建議一起處理，可以嗎？6 張進入實作，1 張直接關掉，再送一份 issue 給 Spacedock。我和首席工程師都建議照這樣做。」, with this task's row 「任務缺必要欄位要擋 ｜ 縮小範圍 ｜ `id` 改成可不寫（Spacedock 本來就不寫，163 個裡有 162 個沒有）；只要求「不做的事」「預算」「停止條件」三項；只檢查新任務」\n"
    'Supersedes: AC-1, AC-3 and AC-4 as written (the implementation worker restates them for an optional stored id under id-style: slug, the three required body records, and new seeds only with replay counts reported)\n'
    '\n'
    '## Stage Report: ideation\n'
    '\n'
    "- DONE: A design for /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.32.0/scripts/design_surfaces.py check --seed to refuse a task missing a field the workflow README's schema actually requires (read the README schema first and list which fields are required and which optional), replayed over every task file in this workflow and the relay room-specs-follow-web-part-select task read only\n"
    '  `## Design`: README-required/optional fields listed; source chain checked; native slug creation exercised. Actual 164-file base replay plus explicitly non-shipping field projection; 140 local and 1 Relay seeds newly refuse. Removing required-field enforcement would preserve their old passing result.\n'
    '- DONE: A `### Batch overlap` section naming each file the design would change and each other batch task (archive-waits-for-observer-report, idle-hook-names-merged-tasks-without-learn, copilot-not-run-line-carries-quote, dispatch-carries-reserved-adr-number, seed-check-requires-schema-fields, journey-probe-finds-nested-maps, read-adr-honors-adr-folder) and live task of other sessions (adr-required-statement, journey-server-host-pilot, ops-inbox-r1-setup-and-isolation, pr-review-lite-value-pilot, adr-silent-undo-probe, comment-check-reaches-delivery-gate, journey-canvas-hosted-poc (driven by other sessions; read only)) that changes the same file or check, so FO can order implementation\n'
    '  `### Batch overlap`: all seven batch tasks and seven named other-session records mapped to files/checks; refreshed against new sibling designs and Captain-recorded closures rather than trusting stale frontmatter.\n'
    '- DONE: The words FO reads at each lifecycle moment, before and after, per root learning.md "Measure the words FO reads at each moment, not one file\'s size"\n'
    '  `### Words FO reads at each lifecycle moment`: source/proposed whitespace counts and output branches; workflow 5565→5577, package README +3, missing Relay seed 44→57 words. Full runtime emission comparison remains implementation evidence.\n'
    '- DONE: Acceptance criteria with reproducible evidence clauses and falsifiers, and unresolved decisions for the Captain, each with a recommendation and what gets worse under it\n'
    '  `## Acceptance criteria`: seven individually named evidence plans and falsifiers; `### Captain decision` makes one coupled schema choice, recommends keeping stored id and explicit bounds, and states compatibility/reading costs.\n'
    '- DONE: Current design artifact check\n'
    '  Supplied 0.32.0 `design_surfaces.py check <task>` exits 0: `seed-check-requires-schema-fields.md: design surfaces presentable`; Scope/frontmatter preserved. Mermaid prose agreement reviewed; rendering not exercised.\n'
    '- SKIPPED: AC-1 implementation acceptance proof\n'
    '  Candidate missing/empty/ambiguous scalar matrix not implemented; current seed omission reproduced and acceptance falsifiers recorded.\n'
    '- SKIPPED: AC-2 implementation acceptance proof\n'
    '  Candidate body/fence matrix not implemented; historical ordinary-form classifier projects Relay id/Budget/Stop-condition refusal.\n'
    '- SKIPPED: AC-3 implementation acceptance proof\n'
    '  Native 0.27.2 flat omission and matching-id creation both exit 0; candidate refusal, folder and mismatch matrix not yet verified.\n'
    '- SKIPPED: AC-4 implementation acceptance proof\n'
    '  Candidate consumer/POC checks not run; existing caller/import paths inspected and behavioral integration falsifiers specified.\n'
    '- SKIPPED: AC-5 implementation acceptance proof\n'
    '  164 base task runs in each mode completed with all input hashes matching pinned state; actual candidate comparison and historical observer qualification remain unverified.\n'
    '- SKIPPED: AC-6 implementation acceptance proof\n'
    '  Proposed literal words measured; shipping lint, actual lifecycle output, Captain-backed budget entry and reserved ADR remain future work.\n'
    '- SKIPPED: AC-7 implementation acceptance proof\n'
    '  No package/adopter/CI source changed in ideation; candidate byte/network/diff checks remain future work; CI cost not measured.\n'
    '\n'
    '### Summary\n'
    '\n'
    'Designed a seed-only repair against released 0.32.0, with required/optional schema fields, native Spacedock evidence, a 164-task replay and refreshed batch ordering. The Captain still decides the explicit schema, including stored id despite native slug omission and the +12 workflow-word cost; no implementation, historical migration or remote PR claim is made. This report completes the pilot ideation assignment only.\n'
)

RAW_ADR_RECORD = (
    '# implementation-1\n'
    '\n'
    'Dispatched: 8bf4f3582411e8e4238f19fbadda8ddeca6767be (workflow checkout, kc-dev-flow-2 0.32.0 README); batch 8, first implementation dispatch\n'
    "Model: gpt-6.1-sol (Codex via Paseo, thinking high; the Captain's interim dispatch directive, chat 2026-10-26: 「接下來派工結束後新的派工盡量用 sol / astra，推理等級可以比 claude 高一級」)\n"
    '\n'
    '## Checklist\n'
    '\n'
    "One Draft PR (Conventional Commit title scoped to the plugin) from a branch off origin/main (8bf4f3582411e8e4238f19fbadda8ddeca6767be) implementing the approved design and acceptance criteria in the task file; the kc-dev-flow-2/scripts/design_surfaces.py seed check, README schema and kc-dev-flow-2/scripts/pr_watch.py seeds() changes the design names, with Captain amendment 1 applied: a stored id optional under id-style: slug; Non-goals, Budget and Stop condition required; new seeds only, with the replay counts reported and not enforced on existing tasks; restate AC-1, AC-3 and AC-4 marked 'Amended by Captain, amendment 1'. Stack on idle-hook-names-merged-tasks-without-learn: base your branch on origin/spacedock-ensign/idle-hook-names-merged-tasks-without-learn (207c0a7e), not origin/main, because both change kc-dev-flow-2/scripts/pr_watch.py and that PR (#737) lands first; only the files the design names\n"
    'Every acceptance criterion green with the evidence each names; each falsifier shown failing by a mutation you run (python3 -B, caches cleared)\n'
    'kc-dev-flow-2/scripts/lint-skills.py (the repository copy CI runs), /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.32.0/scripts/adr_lint.py docs/adr --since <base> exit 0; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.32.0/scripts/number_guards.py check exit 0; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.32.0/scripts/comment_ratio.py within its maximum; roborev evidence= line; push without force and without -u; PR body written for FO; FO reads CI on the PR head; CI cost measured or stated as not measured\n'
    '\n'
    '## Scope notes\n'
    '\n'
    'Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.32.0\n'
    '\n'
    "Profile: pilot. Approved design: ## Design and ## Acceptance criteria in the task file; ideation gate approved; the Captain's words are in the task's ideation gate record (read them there; this line does not restate them) and any ## Captain amendments. If a word-budget raise step is needed, quote the Captain's words from that gate record. If a change needs a file the design does not list, stop and return to FO.\n"
    '\n'
    'Delivery: one pull request in iamcxa/kc-claude-plugins, in the worktree `dispatch build` made for you; `git fetch origin` first and base the branch on origin/main. Push the branch without force and without -u under the Captain\'s standing grant in his global instructions (~/.claude/CLAUDE.md, Autonomous action boundaries): "No ask on a repo Kent owns: push a branch and open a Draft PR once the work cleared its own bar". Your sandbox may not reach the GitHub API: do not run gh; write the PR title (Conventional Commit, scoped to the plugin) on the first line and the body after it to /tmp/impl-seed-check-requires-schema-fields-pr.md, and FO opens the Draft PR and reads its CI. Do not bump versions. Stage named files only, no empty commits. If a push is refused by the permission check, stop and report it; do not work around it.\n'
    '\n'
    'Before reporting, commit and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.32.0/extensions/roborev/roborev_gate.py --repo <worktree> --base <base sha>`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report.\n'
    '\n'
    'If you correct your stage report, append a complete new report under the exact heading `## Stage Report: implementation`, every item DONE or SKIPPED with its evidence, ending in a `### Summary` that says it supersedes the earlier one.\n'
    '\n'
    'Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not request reviews, comment on any PR, mark ready or merge.\n'
    '\n'
    "Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).\n"
)


if __name__ == "__main__":
    unittest.main()
