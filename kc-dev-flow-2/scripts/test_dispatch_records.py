import contextlib
import importlib.util
import io
import os
from pathlib import Path
import subprocess
import tempfile
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
AMENDMENTS = ("\n## Captain amendments\n\n### Amendment 1 \u2014 2026-10-17, chat\nCaptain: x\n\n"
              "### Amendment 2 \u2014 2026-10-18, chat\nCaptain: y\n")
NOTES_WITH_BOTH = COMPLETE.replace("Package root:", "ADR: 0020\nMigration: 0007\nPackage root:")


class TaskFactTests(unittest.TestCase):
    def run_names(self, task, records, target="implementation-1.md", folder="task"):
        with tempfile.TemporaryDirectory() as d:
            if task is not None:
                Path(d, folder).parent.mkdir(parents=True, exist_ok=True)
                Path(d, f"{folder}.md").write_text(f"---\nprofile: pilot\n---\n\n# task\n{task}")
            for name, text in records.items():
                Path(d, folder, "dispatch", name).parent.mkdir(parents=True, exist_ok=True)
                Path(d, folder, "dispatch", name).write_text(text)
            with contextlib.redirect_stdout(io.StringIO()) as out:
                code = records_module.main(["--names", str(Path(d, folder, "dispatch", target))])
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
        self.assertEqual(self.run_names("\n## Notes\n\n### Amendment 1 \u2014 2026-10-17\n", {"implementation-1.md": COMPLETE}), (0, []))

    def test_an_archived_task_folder_is_judged_beside_its_own_task_file(self):
        code, out = self.run_names(AMENDMENTS, {"implementation-1.md": COMPLETE}, folder="_archive/task")
        self.assertEqual(code, 1)
        self.assertEqual(len(out), 2)


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


if __name__ == "__main__":
    unittest.main()
