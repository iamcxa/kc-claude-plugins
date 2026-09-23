import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("design_surfaces", ROOT / "scripts/design_surfaces.py")
ds = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ds)

BASE = """# Design: seats remaining

## FO alignment

Surfaces: ui, db
Visible change: a driver sees seats remaining per slot.

## PRFAQ

UI proposal: add a seats-remaining label to each slot row.
Preview: preview.html

## Surface: db

Migration source: db/migrations/0001_add_seats_reserved.sql

| Column | Type |
| --- | --- |
| seats_reserved | integer |
"""

ERDIAGRAM_TABLE = """| Column | Type |
| --- | --- |
| seats_reserved | integer |
"""

ERDIAGRAM = """```mermaid
erDiagram
    SLOTS ||--o{ BOOKINGS : has
```
"""


class DesignSurfacesTests(unittest.TestCase):
    def write(self, d, text, preview=True):
        if preview:
            Path(d, "preview.html").write_text("<html>preview</html>")
        path = Path(d, "task.md")
        path.write_text(text)
        return path

    def test_a_passing_ui_and_db_task(self):
        with tempfile.TemporaryDirectory() as d:
            path = self.write(d, BASE)
            self.assertEqual(ds.check_task(path), [])
            self.assertEqual(ds.main(["check", str(path)]), 0)

    def test_each_rule_refuses_with_its_own_message(self):
        cases = {
            "missing Surfaces": (
                BASE.replace("Surfaces: ui, db\n", ""),
                "needs a non-empty 'Surfaces:' line"),
            "unknown value": (
                BASE.replace("Surfaces: ui, db", "Surfaces: ui, db, api"),
                "unknown value(s) api"),
            "none combined": (
                BASE.replace("Surfaces: ui, db", "Surfaces: none, ui"),
                "combines 'none' with other values"),
            "missing Visible change": (
                BASE.replace("Visible change: a driver sees seats remaining per slot.\n", ""),
                "needs a 'Visible change:' line"),
            "visible change none contradicts recorded ui": (
                BASE.replace("Visible change: a driver sees seats remaining per slot.", "Visible change: none"),
                "contradicts 'ui'"),
            "visible change without recorded ui": (
                BASE.replace("Surfaces: ui, db", "Surfaces: db"),
                "'Surfaces:' has no 'ui'"),
            "ui without proposal": (
                BASE.replace("UI proposal: add a seats-remaining label to each slot row.\n", ""),
                "needs a 'UI proposal:' line"),
            "ui preview path missing": (
                BASE.replace("Preview: preview.html", "Preview: missing.html"),
                "Preview 'missing.html' does not exist"),
            "db without migration source": (
                BASE.replace("Migration source: db/migrations/0001_add_seats_reserved.sql\n", ""),
                "needs a 'Migration source:' line"),
            "db without table or erDiagram": (
                BASE.replace(ERDIAGRAM_TABLE, "No schema shown here.\n"),
                "erDiagram or a markdown table"),
        }
        for label, (text, expected) in cases.items():
            with self.subTest(label):
                with tempfile.TemporaryDirectory() as d:
                    path = self.write(d, text)
                    errors = ds.check_task(path)
                    self.assertTrue(errors, f"{label}: expected a failure")
                    self.assertTrue(any(expected in e for e in errors), errors)
                    self.assertEqual(ds.main(["check", str(path)]), 1)

    def test_ui_preview_url_is_accepted_without_a_local_file(self):
        text = BASE.replace("Preview: preview.html", "Preview: https://example.com/preview")
        with tempfile.TemporaryDirectory() as d:
            path = self.write(d, text, preview=False)
            self.assertEqual(ds.check_task(path), [])

    def test_db_schema_as_erdiagram_passes(self):
        text = BASE.replace(ERDIAGRAM_TABLE, ERDIAGRAM)
        with tempfile.TemporaryDirectory() as d:
            path = self.write(d, text)
            self.assertEqual(ds.check_task(path), [])


if __name__ == "__main__":
    unittest.main()
