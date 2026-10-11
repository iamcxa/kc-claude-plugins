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
"""


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
            "'## Scope notes' section": COMPLETE.replace("## Scope notes\n\nPackage root: /abs/kc-dev-flow-2\n", ""),
        }
        for part, text in cases.items():
            with self.subTest(part):
                code, out = self.check({"implementation-3.md": text, "validation-1.md": COMPLETE})
                self.assertEqual(code, 1)
                self.assertIn(f"implementation-3.md: needs", out)
                self.assertIn(part, out)
                self.assertNotIn("validation-1.md", out)

    def test_a_task_without_records_fails(self):
        self.assertEqual(self.check({})[0], 1)

    def test_wrong_arguments_are_a_usage_error(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(records.main([]), 2)


if __name__ == "__main__":
    unittest.main()
