import contextlib
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("dispatch_records", Path(__file__).with_name("dispatch_records.py"))
records = importlib.util.module_from_spec(spec)
spec.loader.exec_module(records)

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


class DispatchRecordTests(unittest.TestCase):
    def check(self, files, target=None):
        with tempfile.TemporaryDirectory() as d:
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

    def test_a_task_without_records_fails(self):
        self.assertEqual(self.check({})[0], 1)

    def test_wrong_arguments_are_a_usage_error(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(records.main([]), 2)


if __name__ == "__main__":
    unittest.main()
