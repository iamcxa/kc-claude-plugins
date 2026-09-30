import importlib.util
from pathlib import Path
import tempfile
import types
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

## Acceptance criteria

**AC-1**: a driver sees seats remaining per slot.
Verified by: a screenshot at the candidate.
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

AMENDMENT = """
## Captain amendments

### Amendment 1 — 2026-09-30, ideation gate
Captain: 「keep the count per slot」 (gate reason)
Supersedes: AC-2
Superseded text:
**AC-2**: the old outcome.
"""

FENCED_EXAMPLE = """
## Design

```
## Captain amendments

### Amendment 1
Supersedes: AC-1
```
"""
BOTH = "**AC-1**: a.\n**AC-2**: b.\n"


def mutated(old, new):
    source = (ROOT / "scripts/design_surfaces.py").read_text()
    assert old in source, "mutation must actually change the script"
    module = types.ModuleType("design_surfaces_mutant")
    exec(compile(source.replace(old, new, 1), "design_surfaces_mutant", "exec"), module.__dict__)
    return module


def write_task(directory, text):
    Path(directory, "preview.html").write_text("<html></html>")
    path = Path(directory, "task.md")
    path.write_text(text)
    return path


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


class SeedModeTests(unittest.TestCase):
    def test_each_seed_rule_refuses_and_exits_1(self):
        cases = {
            "missing heading": (BASE.replace("## FO alignment", "## Notes"), "missing '## FO alignment' section"),
            "missing Surfaces": (BASE.replace("Surfaces: ui, db\n", ""), "needs a non-empty 'Surfaces:' line"),
            "unknown value": (BASE.replace("Surfaces: ui, db", "Surfaces: api"), "unknown value(s) api"),
            "contradictory Visible change": (
                BASE.replace("Visible change: a driver sees seats remaining per slot.", "Visible change: none"),
                "contradicts 'ui'"),
        }
        for label, (text, expected) in cases.items():
            with self.subTest(label), tempfile.TemporaryDirectory() as d:
                path = write_task(d, text)
                errors = ds.check_task(path, seed=True)
                self.assertTrue(any(expected in e for e in errors), errors)
                self.assertEqual(ds.main(["check", "--seed", str(path)]), 1)

    def test_a_ui_seed_owing_its_proposal_passes_seed_and_fails_the_full_check(self):
        text = BASE.replace("UI proposal: add a seats-remaining label to each slot row.\n", "").replace("Preview: preview.html\n", "")
        with tempfile.TemporaryDirectory() as d:
            path = write_task(d, text)
            self.assertEqual(ds.main(["check", "--seed", str(path)]), 0)
            self.assertEqual(ds.main(["check", str(path)]), 1)

    def test_a_seed_without_criteria_passes_seed_mode(self):
        with tempfile.TemporaryDirectory() as d:
            path = write_task(d, BASE.split("## Acceptance criteria")[0])
            self.assertEqual(ds.main(["check", "--seed", str(path)]), 0)

    def test_mutation_dropping_the_heading_rule_from_seed_mode_fails_its_case(self):
        mutant = mutated("""    if not FO_HEADING.search(text):
        errors.append(f"{path.name}: missing '## FO alignment' section")
""", "")
        with tempfile.TemporaryDirectory() as d:
            path = write_task(d, BASE.replace("## FO alignment", "## Notes"))
            self.assertTrue(any("missing '## FO alignment'" in e for e in ds.check_task(path, seed=True)))
            self.assertFalse(any("missing '## FO alignment'" in e for e in mutant.check_task(path, seed=True)))

    def test_mutation_running_the_artifact_rules_in_seed_mode_fails_its_case(self):
        mutant = mutated("    if seed:\n        return errors\n", "")
        text = BASE.replace("UI proposal: add a seats-remaining label to each slot row.\n", "")
        with tempfile.TemporaryDirectory() as d:
            path = write_task(d, text)
            self.assertEqual(ds.check_task(path, seed=True), [])
            self.assertTrue(mutant.check_task(path, seed=True))


class CriteriaTests(unittest.TestCase):
    FIXTURES = {
        "absent": ("", False),
        "level-1 heading": ("# Acceptance criteria\n**AC-1**: x\n", False),
        "plain list": ("## Acceptance criteria\n- AC-1: x\n", False),
        "empty section": ("## Acceptance criteria\n\n## Next\n**AC-2**: y\n", False),
        "unclosed bold": ("## Acceptance criteria\n**AC-1 x\n", False),
        "lowercase heading": ("## acceptance criteria\n**AC-1**: x\n", True),
        "trailing space": ("## Acceptance criteria \n**AC-1**: x\n", True),
        "leading space": (" ## Acceptance criteria\n**AC-1**: x\n", True),
        "leading tab": ("\t## Acceptance criteria\n**AC-1**: x\n", True),
        "leading no-break space": ("\xa0## Acceptance criteria\n**AC-1**: x\n", True),
        "trailing no-break space": ("## Acceptance criteria\xa0\n**AC-1**: x\n", True),
        "uppercase heading": ("## ACCEPTANCE CRITERIA\n**AC-1**: x\n", True),
        "two spaces inside": ("## Acceptance  criteria\n**AC-1**: x\n", False),
        "labelled": ("## Acceptance criteria\n**AC-1 (VALUE)**: x\n", True),
        "valid": ("## Acceptance criteria\n**AC-1**: x\nVerified by: y\n", True),
        "after a sub-heading": ("## Acceptance criteria\n### Group\n**AC-1**: x\n", True),
        "inside a fence": ("## Acceptance criteria\n```\n**AC-1**: x\n```\n", True),
    }

    def errors(self, criteria, module=ds):
        with tempfile.TemporaryDirectory() as d:
            return module.check_task(write_task(d, BASE.split("## Acceptance criteria")[0] + criteria))

    def test_each_fixture_is_accepted_or_refused(self):
        for label, (criteria, accepted) in self.FIXTURES.items():
            with self.subTest(label):
                found = [e for e in self.errors(criteria) if "cceptance criteria" in e]
                self.assertEqual(not found, accepted, found)

    def test_mutation_accepting_a_plain_list_as_a_declaration_fails_its_case(self):
        mutant = mutated(r'r"\*\*(AC-[A-Za-z0-9]+)[^*\n]*\*\*"', r'r"(?:\*\*|- )(AC-[A-Za-z0-9]+)[^*\n]*"')
        plain = "## Acceptance criteria\n- AC-1: x\n"
        self.assertTrue(self.errors(plain))
        self.assertEqual(self.errors(plain, mutant), [])

    def test_mutation_dropping_the_empty_section_rule_fails_its_case(self):
        mutant = mutated("    if not declared:\n", "    if False:\n")
        empty = "## Acceptance criteria\n\n## Next\n"
        self.assertTrue(self.errors(empty))
        self.assertEqual(self.errors(empty, mutant), [])

    def test_mutation_matching_the_heading_case_sensitively_fails_its_case(self):
        mutant = mutated('## Acceptance criteria{GO_SPACE}$", re.I)', '## Acceptance criteria{GO_SPACE}$")')
        lower = "## acceptance criteria\n**AC-1**: x\n"
        self.assertEqual(self.errors(lower), [])
        self.assertTrue(self.errors(lower, mutant))

    def test_mutation_restoring_the_column_zero_anchor_fails_its_cases(self):
        mutant = mutated('rf"^{GO_SPACE}## Acceptance criteria{GO_SPACE}$"', 'r"^## Acceptance criteria[ \\t\\r]*$"')
        for label in ("leading space", "leading tab", "leading no-break space", "trailing no-break space"):
            with self.subTest(label):
                criteria = self.FIXTURES[label][0]
                self.assertEqual(self.errors(criteria), [])
                self.assertTrue(self.errors(criteria, mutant))


class AmendmentTests(unittest.TestCase):
    def errors(self, extra, criteria="**AC-1**: a driver sees seats.\n", module=ds):
        text = BASE.split("## Acceptance criteria")[0] + "## Acceptance criteria\n\n" + criteria + extra
        with tempfile.TemporaryDirectory() as d:
            return module.check_task(write_task(d, text))

    def test_a_relocated_criterion_none_no_amendments_and_a_fenced_example_pass(self):
        self.assertEqual(self.errors(AMENDMENT), [])
        self.assertEqual(self.errors(AMENDMENT.replace("Supersedes: AC-2", "Supersedes: none")), [])
        self.assertEqual(self.errors(""), [])
        self.assertEqual(self.errors(FENCED_EXAMPLE), [])

    def test_an_entry_without_the_captain_line_is_refused(self):
        for label, text in {
            "no line": AMENDMENT.replace("Captain: 「keep the count per slot」 (gate reason)\n", ""),
            "no words": AMENDMENT.replace("「keep the count per slot」 (gate reason)", ""),
        }.items():
            with self.subTest(label):
                errors = self.errors(text)
                self.assertTrue(any("no 'Captain:' line" in e for e in errors), errors)

    def test_a_superseded_id_still_declared_is_refused_including_a_redeclared_id(self):
        errors = self.errors(AMENDMENT, BOTH)
        self.assertTrue(any("supersedes AC-2 but it is still declared" in e for e in errors), errors)
        redeclared = self.errors(AMENDMENT.replace("Supersedes: AC-2", "Supersedes: AC-1"), "**AC-1**: new text.\n")
        self.assertTrue(any("supersedes AC-1" in e for e in redeclared), redeclared)

    def test_the_amendments_heading_matches_in_any_case_and_with_surrounding_space(self):
        for heading in ("## Captain Amendments", "## CAPTAIN AMENDMENTS", " ## Captain amendments", "## Captain amendments\xa0"):
            with self.subTest(heading):
                text = AMENDMENT.replace("## Captain amendments", heading).replace("Captain: 「keep the count per slot」 (gate reason)\n", "")
                errors = self.errors(text)
                self.assertTrue(any("no 'Captain:' line" in e for e in errors), errors)
                self.assertTrue(any("supersedes AC-2 but it is still declared" in e for e in self.errors(
                    AMENDMENT.replace("## Captain amendments", heading), BOTH)))

    def test_mutation_matching_the_amendments_heading_case_sensitively_fails_its_case(self):
        mutant = mutated('## Captain amendments{GO_SPACE}$", re.I)', '## Captain amendments{GO_SPACE}$")')
        text = AMENDMENT.replace("## Captain amendments", "## Captain Amendments")
        self.assertTrue(self.errors(text, BOTH))
        self.assertEqual(self.errors(text, BOTH, mutant), [])

    def test_mutation_dropping_the_disjointness_rule_fails_its_case(self):
        mutant = mutated("& declared", "& set()")
        self.assertTrue(self.errors(AMENDMENT, BOTH))
        self.assertEqual(self.errors(AMENDMENT, BOTH, mutant), [])

    def test_mutation_dropping_the_captain_rule_fails_its_case(self):
        mutant = mutated("        if not CAPTAIN_WORDS.search(entry):\n", "        if False:\n")
        text = AMENDMENT.replace("Captain: 「keep the count per slot」 (gate reason)\n", "")
        self.assertTrue(self.errors(text))
        self.assertEqual(self.errors(text, module=mutant), [])

    def test_mutation_dropping_the_fence_skip_flags_a_fenced_example(self):
        mutant = mutated("        elif not inside:\n            kept.append(line)\n", "        else:\n            kept.append(line)\n")
        self.assertEqual(self.errors(FENCED_EXAMPLE), [])
        self.assertTrue(self.errors(FENCED_EXAMPLE, module=mutant))


if __name__ == "__main__":
    unittest.main()
