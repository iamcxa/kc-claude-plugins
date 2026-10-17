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

REPLACEMENT = "**AC-3**: Amended by Captain, amendment 1: the new outcome.\n"
TWICE = """
## Captain amendments

### Amendment 1 — 2026-09-30, chat
Captain: 「one」 (chat)
Supersedes: AC-2
Superseded text:
**AC-2**: the old outcome.

### Amendment 2 — 2026-10-01, chat
Captain: 「two」 (chat)
Supersedes: AC-3
Superseded text:
**AC-3**: Amended by Captain, amendment 1: the first replacement.
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
    def errors(self, extra, criteria="**AC-1**: a driver sees seats.\n" + REPLACEMENT, module=ds):
        text = BASE.split("## Acceptance criteria")[0] + "## Acceptance criteria\n\n" + criteria + extra
        with tempfile.TemporaryDirectory() as d:
            return module.check_task(write_task(d, text))

    def test_a_relocated_criterion_none_no_amendments_and_a_fenced_example_pass(self):
        self.assertEqual(self.errors(AMENDMENT), [])
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

    def test_an_entry_holding_a_criterion_its_supersedes_line_does_not_name_is_refused(self):
        errors = self.errors(AMENDMENT.replace("Supersedes: AC-2", "Supersedes: none"))
        self.assertTrue(any("'### Amendment 1" in e and "holds AC-2 but its 'Supersedes:' line does not name them" in e for e in errors), errors)
        two = AMENDMENT.replace("**AC-2**: the old outcome.\n", "**AC-1**: kept.\n**AC-2**: the old outcome.\n")
        errors = self.errors(two.replace("Supersedes: AC-2", "Supersedes: AC-1"), REPLACEMENT)
        self.assertTrue(any("holds AC-2 but" in e for e in errors), errors)
        self.assertFalse(any("holds AC-1" in e for e in errors), errors)

    def test_naming_every_moved_id_and_a_bold_on_the_captain_line_alone_pass(self):
        self.assertEqual(self.errors(AMENDMENT.replace("Captain: 「keep", "Captain: **AC-9** 「keep")), [])
        two = AMENDMENT.replace("**AC-2**: the old outcome.\n", "**AC-1**: kept.\n**AC-2**: the old outcome.\n")
        self.assertEqual(self.errors(two.replace("Supersedes: AC-2", "Supersedes: AC-1, AC-2"), REPLACEMENT), [])

    def test_superseding_entries_need_a_criterion_with_the_amendment_phrase(self):
        no_phrase = "**AC-1**: a driver sees seats.\n**AC-3**: the new outcome.\n"
        errors = self.errors(AMENDMENT, no_phrase)
        self.assertTrue(any("supersedes AC-2 but no criterion says 'Amended by Captain, amendment 1'" in e for e in errors), errors)
        self.assertEqual(self.errors(AMENDMENT), [])
        other = "**AC-1**: a driver sees seats.\n**AC-3**: Amended by Captain, amendment 2: the new outcome.\n"
        self.assertTrue(self.errors(AMENDMENT, other))
        intro = "Amended by Captain, amendment 1, is written on the criteria below.\n**AC-1**: a driver sees seats.\n"
        self.assertTrue(self.errors(AMENDMENT, intro))
        tenth = AMENDMENT.replace("Amendment 1", "Amendment 10")
        self.assertTrue(self.errors(tenth), "amendment 1's phrase must not satisfy amendment 10")

    def test_a_replacement_later_moved_by_another_entry_still_satisfies_the_entry_that_wrote_it(self):
        self.assertEqual(self.errors(TWICE, "**AC-1**: a driver sees seats.\n**AC-4**: Amended by Captain, amendment 2: newest.\n"), [])
        errors = self.errors(TWICE, "**AC-1**: a driver sees seats.\n**AC-4**: the newest.\n")
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("Amendment 2", errors[0])

    def test_no_replacement_on_the_supersedes_line_waives_the_replacement_rule(self):
        waived = AMENDMENT.replace("Supersedes: AC-2", "Supersedes: AC-2 (no replacement: moved to a new task)")
        self.assertEqual(self.errors(waived, "**AC-1**: a driver sees seats.\n"), [])

    def test_an_id_inside_the_waiver_reason_is_not_named(self):
        held = AMENDMENT.replace("**AC-2**: the old outcome.\n", "**AC-1**: kept.\n**AC-2**: the old outcome.\n")
        errors = self.errors(held.replace("Supersedes: AC-2", "Supersedes: AC-1 (no replacement: AC-2 moved to a new task)"), REPLACEMENT)
        self.assertTrue(any("holds AC-2 but" in e for e in errors), errors)
        stays = AMENDMENT.replace("Supersedes: AC-2", "Supersedes: AC-2 (no replacement: AC-1 stays declared)")
        self.assertEqual(self.errors(stays, "**AC-1**: a driver sees seats.\n"), [])

    def test_an_indented_sibling_heading_ends_the_criteria_section(self):
        for heading in (" ## Notes", "\t## Notes", "\xa0## Notes"):
            with self.subTest(repr(heading)):
                criteria = "**AC-1**: a driver sees seats.\n**AC-3**: the new outcome.\n\n" + heading + "\n**AC-9**: Amended by Captain, amendment 1: evidence prose.\n"
                errors = self.errors(AMENDMENT, criteria)
                self.assertTrue(any("supersedes AC-2 but no criterion says" in e for e in errors), errors)

    def test_the_marker_counts_only_on_a_declaration_line(self):
        prose = "**AC-1**: a driver sees seats.\n**AC-3**: the new outcome.\nVerified by: a test quoting Amended by Captain, amendment 1.\n"
        errors = self.errors(AMENDMENT, prose)
        self.assertTrue(any("supersedes AC-2 but no criterion says" in e for e in errors), errors)

    def test_the_marker_shapes_the_corpus_writes_pass(self):
        for label, line in {
            "colon": "**AC-3**: Amended by Captain, amendment 1: the new outcome.\n",
            "space": "**AC-3** Amended by Captain, amendment 1. The new outcome.\n",
            "list item": "- **AC-3** Amended by Captain, amendment 1. The new outcome.\n",
            "parenthesis": "**AC-3** (Amended by Captain, amendment 1; replaces AC-2): the new outcome.\n",
            "inside the bold": "**AC-3 — the new outcome. Amended by Captain, amendment 1 (replaces AC-2).** Its text.\n",
        }.items():
            with self.subTest(label):
                self.assertEqual(self.errors(AMENDMENT, "**AC-1**: a driver sees seats.\n" + line), [])

    def test_a_bold_id_in_evidence_prose_is_not_a_moved_criterion(self):
        cited = AMENDMENT.replace("**AC-2**: the old outcome.\n", "**AC-2**: the old outcome.\nVerified by: a test; see **AC-5** for the shared fixture.\n")
        self.assertEqual(self.errors(cited), [])

    def test_the_design_line_is_not_read(self):
        text = AMENDMENT.replace("Supersedes: AC-2\n", "Supersedes: AC-2\nDesign: the whole paragraph, reworded by FO beyond his words.\n")
        self.assertEqual(self.errors(text), [])

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
        self.assertTrue(self.errors(AMENDMENT, BOTH + REPLACEMENT))
        self.assertEqual(self.errors(AMENDMENT, BOTH + REPLACEMENT, mutant), [])

    def test_mutation_dropping_the_moved_criterion_rule_fails_its_case(self):
        mutant = mutated("        if held - named:\n", "        if False:\n")
        text = AMENDMENT.replace("Supersedes: AC-2", "Supersedes: none")
        self.assertTrue(self.errors(text))
        self.assertEqual(self.errors(text, module=mutant), [])

    def test_mutation_dropping_the_replacement_rule_fails_its_case(self):
        mutant = mutated("        if named and not waiver and not any", "        if False and not any")
        self.assertTrue(self.errors(AMENDMENT, "**AC-1**: a driver sees seats.\n"))
        self.assertEqual(self.errors(AMENDMENT, "**AC-1**: a driver sees seats.\n", mutant), [])

    def test_mutation_dropping_the_other_entry_lookup_fails_its_case(self):
        mutant = mutated("live + others", "live")
        criteria = "**AC-1**: a driver sees seats.\n**AC-4**: Amended by Captain, amendment 2: newest.\n"
        self.assertEqual(self.errors(TWICE, criteria), [])
        self.assertEqual(len(self.errors(TWICE, criteria, mutant)), 1)

    def test_mutation_counting_a_non_declaration_line_as_the_marker_fails_its_cases(self):
        mutant = mutated("live = declarations(section(lines, AC_HEADING) or [])", 'live = [("", l) for l in section(lines, AC_HEADING) or []]')
        intro = "Amended by Captain, amendment 1, is written on the criteria below.\n**AC-1**: a driver sees seats.\n"
        prose = "**AC-1**: a driver sees seats.\n**AC-3**: the new outcome.\nVerified by: a test quoting Amended by Captain, amendment 1.\n"
        for criteria in (intro, prose):
            self.assertTrue(self.errors(AMENDMENT, criteria))
            self.assertEqual(self.errors(AMENDMENT, criteria, mutant), [])

    def test_mutation_restoring_the_plain_section_end_fails_its_cases(self):
        mutant = mutated("if SECTION_END.match(lines[i])", 'if lines[i].startswith("## ")')
        for heading in (" ## Notes", "\t## Notes", "\xa0## Notes"):
            criteria = "**AC-1**: a driver sees seats.\n**AC-3**: the new outcome.\n\n" + heading + "\n**AC-9**: Amended by Captain, amendment 1: evidence prose.\n"
            self.assertTrue(self.errors(AMENDMENT, criteria))
            self.assertEqual(self.errors(AMENDMENT, criteria, mutant), [])

    def test_mutation_dropping_the_waiver_fails_its_case(self):
        mutant = mutated("not waiver and not any", "not any")
        waived = AMENDMENT.replace("Supersedes: AC-2", "Supersedes: AC-2 (no replacement: moved to a new task)")
        self.assertEqual(self.errors(waived, "**AC-1**: a driver sees seats.\n"), [])
        self.assertTrue(self.errors(waived, "**AC-1**: a driver sees seats.\n", mutant))

    def test_mutation_reading_the_design_line_fails_its_case(self):
        mutant = mutated("DECLARATION_LINE.match(line)", "AC_DECLARATION.search(line)")
        text = AMENDMENT.replace("Supersedes: AC-2\n", "Supersedes: AC-2\nDesign: **AC-9** names a paragraph.\n")
        self.assertEqual(self.errors(text), [])
        self.assertTrue(self.errors(text, module=mutant))

    def test_mutation_reading_a_bold_id_anywhere_on_a_line_fails_its_case(self):
        mutant = mutated("DECLARATION_LINE.match(line)", "AC_DECLARATION.search(line)")
        cited = AMENDMENT.replace("**AC-2**: the old outcome.\n", "**AC-2**: the old outcome.\nVerified by: a test; see **AC-5** for the shared fixture.\n")
        self.assertEqual(self.errors(cited), [])
        self.assertTrue(self.errors(cited, module=mutant))

    def test_mutation_reading_the_id_list_past_the_waiver_text_fails_its_case(self):
        mutant = mutated("value[:waiver.start()] if waiver else value", "value")
        held = AMENDMENT.replace("**AC-2**: the old outcome.\n", "**AC-1**: kept.\n**AC-2**: the old outcome.\n")
        text = held.replace("Supersedes: AC-2", "Supersedes: AC-1 (no replacement: AC-2 moved to a new task)")
        self.assertTrue(self.errors(text, REPLACEMENT))
        self.assertEqual(self.errors(text, REPLACEMENT, mutant), [])

    def test_mutation_dropping_the_captain_rule_fails_its_case(self):
        mutant = mutated("        if not CAPTAIN_WORDS.search(entry):\n", "        if False:\n")
        text = AMENDMENT.replace("Captain: 「keep the count per slot」 (gate reason)\n", "")
        self.assertTrue(self.errors(text))
        self.assertEqual(self.errors(text, module=mutant), [])

    def test_mutation_dropping_the_fence_skip_flags_a_fenced_example(self):
        mutant = mutated("        elif not inside:\n            kept.append(line)\n", "        else:\n            kept.append(line)\n")
        self.assertEqual(self.errors(FENCED_EXAMPLE), [])
        self.assertTrue(self.errors(FENCED_EXAMPLE, module=mutant))


REPORT = """tob_security_review:
  pr: none
  findings:
    - file: "design"
      severity: HIGH
      title: "first"
    - file: "design"
      severity: MEDIUM
      title: "second"
    - file: "design"
      severity: LOW
      title: "third"
"""

REVIEW_LINES = """Security review: security/ideation-1.yaml
Security focus file: none
Security finding 1: AC-2
Security finding 2: declined: the design accepts and bounds it
Security finding 3: Needs decision: publish the file or not
"""

PROD = """---
title: a prod task
profile: prod
status: ideation
---

## FO alignment

Surfaces: none
Visible change: none

## Design

### Security review

{review}
## Acceptance criteria

**AC-1**: a.
Verified by: a test.
**AC-2**: b.
Verified by: a test.
"""


class SecurityReviewTests(unittest.TestCase):
    def run_check(self, review=REVIEW_LINES, report=REPORT, module=ds, profile="prod", status="ideation", outside=False):
        text = PROD.format(review=review).replace("profile: prod", f"profile: {profile}").replace("status: ideation", f"status: {status}")
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d, "task", "security")
            folder.mkdir(parents=True)
            if report is not None:
                folder.joinpath("ideation-1.yaml").write_text(report)
                if outside:
                    Path(d, "x.yaml").write_text(report)
            path = Path(d, "task.md")
            path.write_text(text)
            notes = []
            return module.check_task(path, notes=notes), notes

    def refused(self, why, **kwargs):
        errors, _ = self.run_check(**kwargs)
        self.assertEqual(len([e for e in errors if why in e]), 1, errors)
        return errors

    def test_a_reviewed_prod_design_passes_and_prints_one_short_line(self):
        errors, notes = self.run_check()
        self.assertEqual(errors, [])
        self.assertEqual(notes, ["security review security/ideation-1.yaml: 3 findings, 1 acceptance criteria, 1 declined, 1 decisions"])
        self.assertLessEqual(len(notes[0].split()), 12)

    def test_each_refusal_names_its_own_reason(self):
        lines = REVIEW_LINES
        cases = {
            "no review line": (lines.replace("Security review: security/ideation-1.yaml\n", ""), "needs a 'Security review:' line"),
            "not run": (lines.replace("security/ideation-1.yaml", "not run: kc-pr-flow not installed", 1), "security review not run"),
            "missing report": (lines.replace("ideation-1.yaml", "ideation-9.yaml", 1), "not a report file inside the task folder"),
            "absolute path": (lines.replace("security/ideation-1.yaml", "/etc/hosts", 1), "not a report file inside the task folder"),
            "no focus line": (lines.replace("Security focus file: none\n", ""), "needs a 'Security focus file:' line"),
            "finding without a line": (lines.replace("Security finding 2: declined: the design accepts and bounds it\n", ""), "report finding 2 has no"),
            "undeclared criterion": (lines.replace("finding 1: AC-2", "finding 1: AC-99"), "report finding 1 has no"),
            "empty decline": (lines.replace("declined: the design accepts and bounds it", "declined:"), "report finding 2 has no"),
            "declined high": (lines.replace("finding 1: AC-2", "finding 1: declined: accepted"), "report finding 1 has no"),
            "extra line": (lines + "Security finding 4: Needs decision: x\n", "'Security finding 4:' has no finding"),
        }
        for label, (review, why) in cases.items():
            with self.subTest(label):
                self.refused(why, review=review)

    def test_a_file_that_is_not_a_review_report_and_a_path_leaving_the_task_folder_are_refused(self):
        self.refused("is not a tob_security_review report", report="findings:\n  - severity: LOW\n")
        self.refused("is not a tob_security_review report", report="tob_security_review:\n  pr: none\n")
        self.refused("not a report file inside the task folder", review=REVIEW_LINES.replace("security/ideation-1.yaml", "../x.yaml", 1), outside=True)

    def test_a_task_of_another_profile_or_past_ideation_is_unchanged(self):
        for profile, status in (("pilot", "ideation"), ("poc", "ideation"), ("prod", "implementation")):
            with self.subTest(profile=profile, status=status):
                errors, notes = self.run_check(review="", report=None, profile=profile, status=status)
                self.assertEqual((errors, notes), ([], []))

    def test_a_declined_medium_and_an_acceptance_criterion_on_any_severity_pass(self):
        errors, _ = self.run_check(review=REVIEW_LINES.replace("finding 1: AC-2", "finding 1: AC-1"))
        self.assertEqual(errors, [])

    def test_quoted_frontmatter_values_are_still_a_prod_ideation_task(self):
        for quote in ('"', "'"):
            with self.subTest(quote=quote):
                errors, _ = self.run_check(review="", report=None, profile=f"{quote}prod{quote}", status=f"{quote}ideation{quote}")
                self.assertTrue(any("needs a 'Security review:' line" in e for e in errors), errors)

    def test_a_bold_acceptance_id_in_design_prose_is_not_a_declared_criterion(self):
        review = REVIEW_LINES.replace("finding 1: AC-2", "finding 1: AC-77") + "\n**AC-77**: a claim made in the design, not a criterion.\n"
        self.refused("report finding 1 has no", review=review)

    def test_a_quoted_severity_still_counts_as_a_finding(self):
        quoted = REPORT.replace("severity: HIGH", 'severity: "HIGH"')
        self.refused("report finding 1 has no", review=REVIEW_LINES.replace("finding 1: AC-2", "finding 1: declined: accepted"), report=quoted)
        errors, notes = self.run_check(report=quoted)
        self.assertEqual((errors, len(notes)), ([], 1))

    def test_a_report_with_an_empty_findings_list_passes_with_no_finding_lines(self):
        errors, notes = self.run_check(review="Security review: security/ideation-1.yaml\nSecurity focus file: none\n", report="tob_security_review:\n  pr: none\n  findings: []\n")
        self.assertEqual(errors, [])
        self.assertIn("0 findings", notes[0])

    def test_a_findings_item_with_no_severity_is_not_counted_as_zero_findings(self):
        truncated = "tob_security_review:\n  pr: none\n  findings:\n    - file: \"design\"\n      title: \"cut off before its severity\"\n"
        errors, notes = self.run_check(review="Security review: security/ideation-1.yaml\nSecurity focus file: none\n", report=truncated)
        self.assertTrue(errors, f"a report whose only finding has no severity passed: {notes}")

    def test_a_findings_item_with_no_severity_among_others_is_not_dropped(self):
        partial = REPORT + '    - file: "design"\n      title: "fourth, no severity"\n'
        errors, notes = self.run_check(report=partial)
        self.assertTrue(errors, f"a 4-item report with 3 severities passed: {notes}")

    def test_mutation_dropping_the_security_call_lets_a_missing_review_pass(self):
        mutant = mutated("summary = check_security(path, plain, declared, errors)", "summary = None")
        review = REVIEW_LINES.replace("Security review: security/ideation-1.yaml\n", "")
        self.assertTrue(self.run_check(review=review)[0])
        self.assertEqual(self.run_check(review=review, module=mutant)[0], [])

    def test_mutation_dropping_the_severity_test_lets_a_declined_high_pass(self):
        mutant = mutated(' and severities[number - 1] in ("MEDIUM", "LOW")', "")
        review = REVIEW_LINES.replace("finding 1: AC-2", "finding 1: declined: accepted")
        self.assertTrue(self.run_check(review=review)[0])
        self.assertEqual(self.run_check(review=review, module=mutant)[0], [])

    def test_mutation_dropping_the_not_run_rule_changes_its_reason(self):
        mutant = mutated('if value.lower().startswith("not run"):', "if False:")
        review = REVIEW_LINES.replace("security/ideation-1.yaml", "not run: kc-pr-flow not installed", 1)
        self.assertTrue(any("security review not run" in e for e in self.run_check(review=review)[0]))
        self.assertFalse(any("security review not run" in e for e in self.run_check(review=review, module=mutant)[0]))

    def test_mutation_dropping_the_folder_rule_lets_a_path_outside_pass(self):
        mutant = mutated(' or ".." in Path(value).parts', "")
        review = REVIEW_LINES.replace("security/ideation-1.yaml", "../x.yaml", 1)
        self.assertTrue(self.run_check(review=review, outside=True)[0])
        self.assertEqual(self.run_check(review=review, outside=True, module=mutant)[0], [])

    def test_mutation_reading_ids_from_the_whole_task_accepts_a_prose_id(self):
        mutant = mutated("summary = check_security(path, plain, declared, errors)", "summary = check_security(path, plain, set(AC_DECLARATION.findall(plain)), errors)")
        review = REVIEW_LINES.replace("finding 1: AC-2", "finding 1: AC-77") + "\n**AC-77**: a claim made in the design, not a criterion.\n"
        self.assertTrue(self.run_check(review=review)[0])
        self.assertEqual(self.run_check(review=review, module=mutant)[0], [])

    def test_mutation_matching_unquoted_frontmatter_only_skips_a_quoted_prod_task(self):
        mutant = mutated(r'''r"""^profile:[ \t]*["']?([^\s"']+)["']?[ \t]*$"""''', r'r"^profile:[ \t]*(\S+)[ \t]*$"')
        kwargs = dict(review="", report=None, profile='"prod"', status="ideation")
        self.assertTrue(self.run_check(**kwargs)[0])
        self.assertEqual(self.run_check(module=mutant, **kwargs)[0], [])

    def test_mutation_dropping_the_findings_key_rule_accepts_a_report_without_findings(self):
        mutant = mutated(" and REPORT_FINDINGS_KEY.search(text)", "")
        bare = "tob_security_review:\n  pr: none\n"
        review = "Security review: security/ideation-1.yaml\nSecurity focus file: none\n"
        self.assertTrue(self.run_check(review=review, report=bare)[0])
        try:
            errors = self.run_check(review=review, report=bare, module=mutant)[0]
        except AttributeError:
            errors = ["crash"]
        self.assertFalse(any("is not a tob_security_review report" in e for e in errors), errors)

    def test_mutation_dropping_the_quote_strip_refuses_a_quoted_severity(self):
        mutant = mutated('.strip().strip("\\"\'")', ".strip()")
        quoted = REPORT.replace("severity: HIGH", 'severity: "HIGH"')
        self.assertEqual(self.run_check(report=quoted)[0], [])
        self.assertTrue(any("with severity '\"HIGH\"'" in e for e in self.run_check(report=quoted, module=mutant)[0]))

    NONE = "Security review: security/ideation-1.yaml\nSecurity focus file: none\n"

    def report_errors(self, report, review=None):
        return self.run_check(review=review or self.NONE, report=report)[0]

    def test_an_item_with_no_severity_is_refused_by_its_number(self):
        report = REPORT.replace('      severity: MEDIUM\n', "")
        self.refused("has findings item 2 with no 'severity:' line", report=report)

    def test_an_unknown_severity_value_is_refused_by_its_number(self):
        for label, value in {"off the scale": "SEVERE", "lower case": "high", "the template echoed": "CRITICAL | HIGH | MEDIUM | LOW", "empty": ""}.items():
            with self.subTest(label):
                report = REPORT.replace("severity: MEDIUM", f"severity: {value}")
                self.refused(f"has findings item 2 with severity '{value}', not one of CRITICAL, HIGH, MEDIUM, LOW", report=report)

    def test_a_truncated_item_is_refused(self):
        head = "tob_security_review:\n  pr: none\n  findings:\n"
        cases = {
            "cut after the file line": (head + '    - file: "design"\n', "findings item 1 with no 'severity:' line"),
            "cut inside the severity value": (head + '    - file: "design"\n      severity:', "findings item 1 with severity ''"),
            "cut after the dash": (head + "    -", "findings item 1 that is not a 'key: value' entry"),
            "a bare string item": (head + "    - cut off here", "findings item 1 that is not a 'key: value' entry"),
        }
        for label, (report, why) in cases.items():
            with self.subTest(label):
                self.refused(why, report=report, review=self.NONE)

    def test_a_findings_value_that_is_not_a_list_is_refused(self):
        head = "tob_security_review:\n  pr: none\n"
        cases = {
            "a word": (head + "  findings: none\n", "findings' value that is not a list"),
            "a mapping": (head + "  findings:\n    file: x\n    severity: HIGH\n", "findings' value that is not a list"),
            "nothing under the key": (head + "  findings:\n  clean_patterns:\n    - ok\n", "findings' key with no items"),
            "the key at the end of a cut file": (head + "  findings:\n", "findings' key with no items"),
            "items at two indents": (head + "  findings:\n    - severity: LOW\n   - severity: HIGH\n", "items do not share one indent"),
        }
        for label, (report, why) in cases.items():
            with self.subTest(label):
                self.refused(why, report=report, review=self.NONE)

    def test_a_dash_and_a_severity_inside_a_block_scalar_are_not_items(self):
        report = (
            "tob_security_review:\n  pr: none\n  findings:\n"
            '    - file: "design"\n'
            "      description: |\n"
            "        Steps:\n"
            "        - file: not an item\n"
            "        - severity: HIGH\n"
            "        severity: CRITICAL\n"
            "      severity: LOW\n"
            "      title: after the block\n"
            "  clean_patterns:\n    - ok\n"
        )
        errors, notes = self.run_check(review=self.NONE + "Security finding 1: declined: accepted\n", report=report)
        self.assertEqual(errors, [])
        self.assertIn("1 findings, 0 acceptance criteria, 1 declined", notes[0])

    def test_a_severity_may_sit_on_any_line_of_its_item(self):
        report = "tob_security_review:\n  pr: none\n  findings:\n    - severity: LOW\n      file: a\n    - file: b\n      title: t\n      severity: MEDIUM  # trailing comment\n  findings_note: x\n"
        errors, notes = self.run_check(review=self.NONE + "Security finding 1: declined: a\nSecurity finding 2: declined: b\n", report=report)
        self.assertEqual(errors, [])
        self.assertIn("2 findings", notes[0])

    def test_mutation_defaulting_a_missing_severity_hides_the_item(self):
        mutant = mutated('if b.startswith("severity:")), None)', 'if b.startswith("severity:")), "severity: LOW")')
        report = REPORT.replace('      severity: MEDIUM\n', "")
        why = "has findings item 2 with no 'severity:' line"
        self.assertTrue(any(why in e for e in self.run_check(report=report)[0]))
        self.assertFalse(any(why in e for e in self.run_check(report=report, module=mutant)[0]))

    def test_mutation_dropping_the_scale_test_accepts_an_unknown_severity(self):
        mutant = mutated("if value not in SEVERITY_SCALE:", "if False:")
        report = REPORT.replace("severity: MEDIUM", "severity: SEVERE")
        self.assertTrue(any("not one of" in e for e in self.run_check(report=report)[0]))
        self.assertFalse(any("not one of" in e for e in self.run_check(report=report, module=mutant)[0]))

    def test_mutation_dropping_the_value_rule_reads_a_scalar_as_a_list(self):
        mutant = mutated("    if rest:\n", "    if False:\n")
        report = "tob_security_review:\n  pr: none\n  findings: none\n"
        why = "findings' value that is not a list"
        self.assertTrue(any(why in e for e in self.report_errors(report)))
        self.assertFalse(any(why in e for e in self.run_check(review=self.NONE, report=report, module=mutant)[0]))

    def test_mutation_dropping_the_empty_rule_passes_a_key_with_no_items(self):
        mutant = mutated("    if not items:\n", "    if False:\n")
        report = "tob_security_review:\n  pr: none\n  findings:\n"
        self.assertTrue(self.report_errors(report))
        self.assertEqual(self.run_check(review=self.NONE, report=report, module=mutant)[0], [])

    def test_mutation_dropping_the_empty_list_literal_refuses_findings_of_nothing(self):
        mutant = mutated('if rest == "[]":', "if False:")
        report = "tob_security_review:\n  pr: none\n  findings: []\n"
        self.assertEqual(self.report_errors(report), [])
        self.assertTrue(self.run_check(review=self.NONE, report=report, module=mutant)[0])

    def test_mutation_counting_any_dash_as_an_item_splits_a_block_scalar(self):
        mutant = mutated("        if depth == item_indent:\n            items.append([])", "        if marker:\n            items.append([])")
        report = (
            "tob_security_review:\n  pr: none\n  findings:\n"
            '    - file: "design"\n      description: |\n        - a step\n      severity: LOW\n'
        )
        review = self.NONE + "Security finding 1: declined: accepted\n"
        self.assertEqual(self.run_check(review=review, report=report)[0], [])
        self.assertTrue(self.run_check(review=review, report=report, module=mutant)[0])

    def test_mutation_reading_severity_at_any_depth_takes_one_from_a_block_scalar(self):
        mutant = mutated("[b for d, b in item[1:] if d == key_indent]", "[b for d, b in item[1:]]")
        report = (
            "tob_security_review:\n  pr: none\n  findings:\n"
            '    - file: "design"\n      description: |\n        severity: HIGH\n      severity: LOW\n'
        )
        review = self.NONE + "Security finding 1: declined: accepted\n"
        self.assertEqual(self.run_check(review=review, report=report)[0], [])
        self.assertTrue(self.run_check(review=review, report=report, module=mutant)[0])

    def test_mutation_dropping_the_key_value_rule_changes_a_bare_item_reason(self):
        mutant = mutated("if not first or not ITEM_FIRST_KEY.match(item[0][1][first.end():]):", "if not first:")
        report = "tob_security_review:\n  pr: none\n  findings:\n    - cut off here\n"
        why = "not a 'key: value' entry"
        self.assertTrue(any(why in e for e in self.report_errors(report)))
        self.assertFalse(any(why in e for e in self.run_check(review=self.NONE, report=report, module=mutant)[0]))

    def test_mutation_dropping_the_indent_rule_swallows_a_misindented_item(self):
        mutant = mutated("        if depth < item_indent or (depth == item_indent and not marker):", "        if False:")
        report = "tob_security_review:\n  pr: none\n  findings:\n    - severity: LOW\n   - severity: HIGH\n"
        review = self.NONE + "Security finding 1: declined: accepted\n"
        self.assertTrue(self.run_check(review=review, report=report)[0])
        self.assertEqual(self.run_check(review=review, report=report, module=mutant)[0], [])


if __name__ == "__main__":
    unittest.main()
