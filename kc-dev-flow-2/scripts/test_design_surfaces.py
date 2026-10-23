import contextlib
import importlib.util
import io
import os
from pathlib import Path
import subprocess
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
    module.__file__ = str(ROOT / "scripts/design_surfaces.py")
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

    def test_the_two_messages_the_readme_does_not_restate_are_worded_as_pointed_at(self):
        self.assertTrue(any("missing '## Acceptance criteria' section" in e for e in self.errors("")))
        empty = self.errors("## Acceptance criteria\n\n## Next\n")
        self.assertTrue(any("'## Acceptance criteria' declares no criterion (a '**AC-<id>**' bold line)" in e for e in empty), empty)

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
    def run_check(self, review=REVIEW_LINES, report=REPORT, module=ds, profile="prod", status="ideation", outside=False, folder_form=False, extra=None):
        text = PROD.format(review=review).replace("profile: prod", f"profile: {profile}").replace("status: ideation", f"status: {status}")
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d, "task", "security")
            folder.mkdir(parents=True)
            task_file = Path(d, "task", "index.md") if folder_form else Path(d, "task.md")
            if report is not None:
                folder.joinpath("ideation-1.yaml").write_text(report)
                if outside:
                    Path(d, "x.yaml").write_text(report)
            for later, body in (extra or {}).items():
                folder.joinpath(later).write_text(body)
            path = task_file
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

    def test_the_same_report_passes_for_a_flat_task_and_for_a_folder_task(self):
        flat, flat_notes = self.run_check()
        folder, folder_notes = self.run_check(folder_form=True)
        self.assertEqual((flat, folder), ([], []))
        self.assertEqual(folder_notes, flat_notes)

    def test_a_folder_task_with_no_report_in_its_own_folder_is_still_refused(self):
        self.refused("not a report file inside the task folder", report=None, folder_form=True)

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
        self.refused("has 0 'findings:' lines", report="tob_security_review:\n  pr: none\n")
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

    def test_two_review_lines_are_refused_so_a_rerun_cannot_leave_an_older_report_binding(self):
        later = {"ideation-2.yaml": NEWER_SECURITY_REPORT}
        self.refused("2 'Security review:' lines", review=REVIEW_LINES + "Security review: security/ideation-2.yaml\n", extra=later)
        self.refused("2 'Security review:' lines", review=REVIEW_LINES + "Security review: security/ideation-1.yaml\n")
        self.refused("2 'Security review:' lines", review="Security review: security/ideation-2.yaml\n" + REVIEW_LINES, extra=later)

    def test_two_dispositions_for_one_security_finding_number_are_refused(self):
        for extra in ("Security finding 2: Needs decision: x\n", "Security finding 1: AC-2\n", "Security finding 02: AC-2\n"):
            with self.subTest(extra=extra):
                self.refused("'Security finding", review=REVIEW_LINES + extra)
                errors, _ = self.run_check(review=REVIEW_LINES + extra)
                self.assertTrue(any("appears more than once" in e for e in errors), errors)

    def test_mutation_dropping_the_security_review_count_lets_two_lines_pass(self):
        mutant = mutated("""if len(REVIEW_LINE.findall(body)) > 1:""", "if False:")
        review = REVIEW_LINES + "Security review: security/ideation-2.yaml\n"
        later = {"ideation-2.yaml": NEWER_SECURITY_REPORT}
        self.assertTrue(self.run_check(review=review, extra=later)[0])
        self.assertEqual(self.run_check(review=review, extra=later, module=mutant)[0], [])

    def test_mutation_dropping_the_security_duplicate_check_lets_two_dispositions_pass(self):
        mutant = mutated("repeated(FINDING_LINE.findall(body), \"Security\", name, errors)", "None")
        review = REVIEW_LINES + "Security finding 2: Needs decision: x\n"
        self.assertTrue(self.run_check(review=review)[0])
        self.assertEqual(self.run_check(review=review, module=mutant)[0], [])

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

    def test_mutation_reading_a_folder_task_as_a_flat_task_refuses_its_own_report(self):
        mutant = mutated('path.parent if path.name == "index.md" else path.parent / path.stem', "path.parent / path.stem")
        self.assertEqual(self.run_check(folder_form=True)[0], [])
        errors = self.run_check(folder_form=True, module=mutant)[0]
        self.assertEqual(len([e for e in errors if "not a report file inside the task folder" in e]), 1, errors)

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

    def test_a_dash_inside_a_block_scalar_is_not_an_item(self):
        report = (
            "tob_security_review:\n  pr: none\n  findings:\n"
            '    - file: "design"\n'
            "      description: |\n"
            "        Steps:\n"
            "        - file: not an item\n"
            "        - a step\n"
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
        mutant = mutated("if value not in scale:", "if False:")
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
            '    - file: "design"\n      description: |\n        severity: HIGH\n'
        )
        why = "has findings item 1 with no 'severity:' line"
        self.assertTrue(any(why in e for e in self.run_check(review=self.NONE, report=report)[0]))
        self.assertFalse(any(why in e for e in self.run_check(review=self.NONE, report=report, module=mutant)[0]))

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
        why = "items do not share one indent"
        self.assertTrue(any(why in e for e in self.run_check(review=review, report=report)[0]))
        self.assertFalse(any(why in e for e in self.run_check(review=review, report=report, module=mutant)[0]))

    def test_a_second_root_line_at_column_zero_is_refused(self):
        why = "2 'tob_security_review:' lines at column 0, expected exactly 1"
        self.refused(why, report=REPORT + "tob_security_review:\n  pr: none\n")

    def test_an_indented_root_line_is_not_a_second_root(self):
        errors, _ = self.run_check(report=REPORT + "  note: |\n    tob_security_review:\n")
        self.assertEqual(errors, [])

    def test_a_second_findings_line_is_refused_in_a_scalar_and_as_a_key(self):
        why = "has 2 'findings:' lines, expected exactly 1"
        self.refused(why, report=REPORT + "  note: |\n    findings:\n")
        self.refused(why, report=REPORT + "  more:\n    findings: []\n")
        self.refused(why, report=REPORT + "  more:\n    - findings: []\n")

    def test_a_findings_key_that_is_not_a_direct_child_of_the_root_is_refused(self):
        why = "'findings:' line that is not a direct child of 'tob_security_review:'"
        cases = {
            "nested one level down (review:5555839646)": "tob_security_review:\n  metadata:\n    findings: []\n",
            "nested with items": "tob_security_review:\n  metadata:\n    findings:\n      - severity: HIGH\n",
            "under a second top-level key": "tob_security_review:\n  pr: none\nother:\n  findings: []\n",
            "before the root line": "  findings: []\ntob_security_review:\n  pr: none\n",
            "as a list item key": "tob_security_review:\n  - findings: []\n",
            "at column zero": "tob_security_review:\nfindings: []\n",
        }
        for label, report in cases.items():
            with self.subTest(label):
                self.refused(why, report=report, review=self.NONE)

    def test_a_comment_or_blank_line_before_findings_does_not_move_its_depth(self):
        report = "tob_security_review:\n\n  # the reviewer's note\n  pr: none\n  findings: []\n"
        self.assertEqual(self.report_errors(report), [])

    def test_a_severity_line_outside_the_parsed_items_is_refused(self):
        why = "has 2 'severity:' lines but 1 in its findings items"
        one = "tob_security_review:\n  pr: none\n  findings:\n    - file: a\n      severity: LOW\n"
        self.refused(why, report=one + "      description: |\n        severity: HIGH\n", review=self.NONE + "Security finding 1: declined: a\n")
        self.refused("has 1 'severity:' lines but 0 in its findings items", report="tob_security_review:\n  pr: none\n  findings: []\n  limitations:\n    - severity: HIGH\n", review=self.NONE)
        self.refused("has 4 'severity:' lines but 3 in its findings items", report=REPORT + "  limitations:\n    - severity: HIGH\n")

    def test_a_root_key_that_carries_a_value_is_refused_so_its_children_are_not_scalar_text(self):
        why = "'tob_security_review:' line with a value after its colon"
        cases = {
            "a block scalar (roborev:765)": "tob_security_review: |\n  pr: none\n  findings:\n    - severity: LOW\n",
            "a flow mapping": "tob_security_review: {pr: none}\n  findings: []\n",
            "a word": "tob_security_review: none\n  findings: []\n",
        }
        for label, report in cases.items():
            with self.subTest(label):
                self.refused(why, report=report, review=self.NONE)
        self.assertEqual(self.report_errors("tob_security_review:  # the reviewer's note\n  pr: none\n  findings: []\n"), [])

    def test_mutation_dropping_the_root_value_rule_reads_a_scalar_root_as_a_mapping(self):
        mutant = mutated("    if len(roots) == 1 and root_value(text, roots[0]):", "    if False:")
        report = "tob_security_review: |\n  pr: none\n  findings: []\n"
        why = "line with a value after its colon"
        self.assertTrue(any(why in e for e in self.report_errors(report)))
        self.assertEqual(self.run_check(review=self.NONE, report=report, module=mutant)[0], [])

    def test_mutation_dropping_the_root_count_accepts_a_second_root(self):
        mutant = mutated("if len(roots) != 1:", "if not roots:")
        report = REPORT + "tob_security_review:\n  pr: none\n"
        why = "2 'tob_security_review:' lines"
        self.assertTrue(any(why in e for e in self.run_check(report=report)[0]))
        self.assertFalse(any(why in e for e in self.run_check(report=report, module=mutant)[0]))

    def test_mutation_dropping_the_findings_count_accepts_a_second_findings_line(self):
        mutant = mutated("if len(keys) != 1:", "if not keys:")
        report = REPORT + "  note: |\n    findings:\n"
        why = "has 2 'findings:' lines"
        self.assertTrue(any(why in e for e in self.run_check(report=report)[0]))
        self.assertFalse(any(why in e for e in self.run_check(report=report, module=mutant)[0]))

    def test_mutation_dropping_the_direct_child_rule_reads_a_nested_findings_as_the_list(self):
        mutant = mutated("if not problems and not findings_is_direct_child(text, roots[0], keys[0]):", "if False:")
        report = "tob_security_review:\n  metadata:\n    findings: []\n"
        self.assertTrue(self.report_errors(report))
        self.assertEqual(self.run_check(review=self.NONE, report=report, module=mutant)[0], [])

    def test_mutation_dropping_the_severity_count_accepts_a_severity_line_the_parser_skipped(self):
        mutant = mutated("if plain != len(severities):", "if False:")
        report = "tob_security_review:\n  pr: none\n  findings: []\n  limitations:\n    - severity: HIGH\n"
        why = "'severity:' lines but"
        self.assertTrue(any(why in e for e in self.report_errors(report)))
        self.assertFalse(any(why in e for e in self.run_check(review=self.NONE, report=report, module=mutant)[0]))


DESIGN_REPORT = """design_review:
  preview: preview.html
  findings:
    - severity: MAJOR
      dimension: hierarchy
      where: after-desktop.png
      seen: the count is stated twice
      fix: keep one
    - severity: MINOR
      dimension: spacing
      where: after-desktop.png
      seen: tight inset
      fix: widen it
    - severity: MAJOR
      dimension: consistency
      where: after-phone.png
      seen: opposite chevrons
      fix: one convention
  limitations:
    - the operable preview was not opened
"""

DESIGN_LINES = """Design review: design/ideation-1.yaml
Design finding 1: fixed: the header is one line in preview.html
Design finding 2: declined: the inset matches the shell
Design finding 3: AC-2
Decline check: design/declines-1.yaml
"""

DECLINE_REPORT = """design_decline_check:
  adrs_read: none
  rulings:
    - finding: 2
      ruling: upheld
      evidence: after-desktop.png shows the inset equal to the shell's
      change: none
"""

NEWER_DESIGN_REPORT = """design_review:
  preview: preview.html
  findings:
    - severity: MAJOR
      dimension: hierarchy
      where: after-desktop.png
      seen: the redrawn count is still stated twice
      fix: keep one
"""

NEWER_SECURITY_REPORT = """tob_security_review:
  pr: none
  findings:
    - file: "design"
      severity: HIGH
      title: "new"
"""


UI = """---
title: a ui task
profile: pilot
status: ideation
---

## FO alignment

Surfaces: ui
Visible change: a person sees a panel.

## Design

UI proposal: a panel.
Preview: preview.html

### Design review

{review}
## Acceptance criteria

**AC-1**: a.
Verified by: a test.
**AC-2**: b.
Verified by: a test.
"""


class DesignReviewTests(unittest.TestCase):
    def run_check(self, review=DESIGN_LINES, report=DESIGN_REPORT, module=ds, profile="pilot", status="ideation", surfaces="ui", outside=False, folder_form=False, previews="Preview: preview.html\n", extra=None, declines=DECLINE_REPORT):
        text = UI.format(review=review).replace("Preview: preview.html\n", previews).replace("profile: pilot", f"profile: {profile}").replace("status: ideation", f"status: {status}")
        visible = "a person sees a panel." if "ui" in surfaces else "none"
        text = text.replace("Surfaces: ui\nVisible change: a person sees a panel.", f"Surfaces: {surfaces}\nVisible change: {visible}")
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d, "task", "design")
            folder.mkdir(parents=True)
            Path(d, "task", "preview.html").write_text("<html></html>")
            Path(d, "preview.html").write_text("<html></html>")
            task_file = Path(d, "task", "index.md") if folder_form else Path(d, "task.md")
            if report is not None:
                folder.joinpath("ideation-1.yaml").write_text(report)
                if outside:
                    Path(d, "x.yaml").write_text(report)
            if declines is not None:
                folder.joinpath("declines-1.yaml").write_text(declines)
            for later, body in (extra or {}).items():
                folder.joinpath(later).write_text(body)
            task_file.write_text(text)
            notes = []
            return module.check_task(task_file, notes=notes), notes

    def refused(self, why, **kwargs):
        errors, _ = self.run_check(**kwargs)
        self.assertEqual(len([e for e in errors if why in e]), 1, errors)
        return errors

    def test_a_reviewed_ui_design_passes_and_prints_its_summary_preview_and_upheld_decline(self):
        errors, notes = self.run_check()
        self.assertEqual(errors, [])
        self.assertEqual(notes[0], "design review design/ideation-1.yaml: 3 findings, 1 fixed, 1 criteria, 1 declined, 0 decisions; decline check design/declines-1.yaml: 1 upheld, 0 overruled, 0 decisions in 0 groups")
        self.assertEqual(notes[2:], ["upheld decline 2: the inset matches the shell"])

    def test_a_review_without_a_decline_prints_one_short_line_and_the_preview(self):
        lines = DESIGN_LINES.replace("declined: the inset matches the shell", "Needs decision: x").replace("Decline check: design/declines-1.yaml\n", "")
        errors, notes = self.run_check(review=lines, declines=None)
        self.assertEqual(errors, [])
        self.assertEqual(notes[0], "design review design/ideation-1.yaml: 3 findings, 1 fixed, 1 criteria, 0 declined, 1 decisions")
        self.assertLessEqual(len(notes[0].split()), 14)
        self.assertEqual(len(notes), 2)

    def test_a_folder_task_passes_with_its_own_report(self):
        self.assertEqual(self.run_check(folder_form=True)[0], [])

    def test_each_refusal_names_its_own_reason(self):
        lines = DESIGN_LINES
        cases = {
            "no review line": (lines.replace("Design review: design/ideation-1.yaml\n", ""), "needs a 'Design review:' line"),
            "not run": (lines.replace("design/ideation-1.yaml", "not run: no agent could be dispatched", 1), "design review not run"),
            "missing report": (lines.replace("ideation-1.yaml", "ideation-9.yaml", 1), "not a report file inside the task folder"),
            "absolute path": (lines.replace("design/ideation-1.yaml", "/etc/hosts", 1), "not a report file inside the task folder"),
            "finding without a line": (lines.replace("Design finding 2: declined: the inset matches the shell\n", ""), "report finding 2 has no"),
            "undeclared criterion": (lines.replace("finding 3: AC-2", "finding 3: AC-99"), "report finding 3 has no"),
            "empty decline": (lines.replace("declined: the inset matches the shell", "declined:"), "report finding 2 has no"),
            "empty fixed": (lines.replace("fixed: the header is one line in preview.html", "fixed:"), "report finding 1 has no"),
            "declined major": (lines.replace("finding 3: AC-2", "finding 3: declined: accepted"), "report finding 3 has no"),
            "extra line": (lines + "Design finding 4: Needs decision: x\n", "'Design finding 4:' has no finding"),
        }
        for label, (review, why) in cases.items():
            with self.subTest(label):
                self.refused(why, review=review)

    def test_a_report_of_the_wrong_shape_or_for_another_preview_is_refused(self):
        self.refused("is not a design_review report", report=DESIGN_REPORT.replace("design_review:", "tob_security_review:"))
        self.refused("severity 'HIGH', not one of MAJOR, MINOR", report=DESIGN_REPORT.replace("severity: MAJOR", "severity: HIGH", 1))
        self.refused("reviewed preview 'other.html' but the task's 'Preview:' line names 'preview.html'", report=DESIGN_REPORT.replace("preview: preview.html", "preview: other.html"))
        self.refused("has 0 'preview:' lines directly under", report=DESIGN_REPORT.replace("  preview: preview.html\n", ""))
        self.refused("not a report file inside the task folder", review=DESIGN_LINES.replace("design/ideation-1.yaml", "../x.yaml", 1), outside=True)

    def test_a_ui_task_past_ideation_or_without_ui_is_unchanged(self):
        for kwargs in ({"status": "implementation"}, {"status": "validation"}, {"surfaces": "none"}):
            with self.subTest(**kwargs):
                errors, notes = self.run_check(review="", report=None, **kwargs)
                self.assertEqual((errors, notes), ([], []))

    def test_a_prod_ui_task_owes_both_reviews(self):
        errors, _ = self.run_check(profile="prod")
        self.assertTrue(any("needs a 'Security review:' line" in e for e in errors), errors)
        self.assertFalse(any("Design review" in e for e in errors), errors)

    def test_an_empty_findings_list_passes_with_no_finding_lines(self):
        errors, notes = self.run_check(review="Design review: design/ideation-1.yaml\n", report="design_review:\n  preview: preview.html\n  findings: []\n")
        self.assertEqual(errors, [])
        self.assertIn("0 findings", notes[0])

    def test_two_dispositions_for_one_finding_number_are_refused(self):
        for extra in ("Design finding 2: Needs decision: x\n", "Design finding 1: declined: y\n"):
            with self.subTest(extra=extra):
                errors, _ = self.run_check(review=DESIGN_LINES + extra)
                self.assertTrue(any("appears more than once" in e for e in errors), errors)

    def test_the_preview_is_exactly_one_direct_child_of_the_root(self):
        nested = DESIGN_REPORT.replace("      seen: tight inset\n", "      seen: tight inset\n      preview: preview.html\n")
        cases = {
            "only a nested preview": nested.replace("  preview: preview.html\n", "", 1),
            "nested first, direct names another": nested.replace("  preview: preview.html\n", "", 1).replace("  limitations:", "  preview: other.html\n  limitations:"),
            "a preview under another top-level mapping": DESIGN_REPORT.replace("  preview: preview.html\n", "", 1) + "other:\n  preview: preview.html\n",
            "two direct previews": DESIGN_REPORT.replace("  preview: preview.html\n", "  preview: preview.html\n  preview: other.html\n", 1),
        }
        for label, report in cases.items():
            with self.subTest(label):
                errors, _ = self.run_check(report=report)
                self.assertTrue(errors, "passed: " + label)

    def test_a_report_naming_any_of_several_preview_lines_passes(self):
        previews = "Preview: preview.html\nPreview: second.html\n"
        self.assertEqual(self.run_check(previews=previews, report=DESIGN_REPORT.replace("preview: preview.html", "preview: second.html"))[0], [])
        self.assertEqual(self.run_check(previews=previews)[0], [])
        self.refused("reviewed preview 'other.html'", previews=previews, report=DESIGN_REPORT.replace("preview: preview.html", "preview: other.html"))

    def test_limitations_are_not_read_so_an_unshown_state_beside_no_findings_passes(self):
        report = "design_review:\n  preview: preview.html\n  findings: []\n  limitations:\n    - the dark theme is not shown\n"
        errors, _ = self.run_check(review="Design review: design/ideation-1.yaml\n", report=report)
        self.assertEqual(errors, [])

    def test_two_review_lines_are_refused_even_when_the_first_names_a_valid_report(self):
        later = {"ideation-2.yaml": NEWER_DESIGN_REPORT}
        self.refused("2 'Design review:' lines", review=DESIGN_LINES + "Design review: design/ideation-2.yaml\n", extra=later)
        self.refused("2 'Design review:' lines", review=DESIGN_LINES + "Design review: design/ideation-1.yaml\n")
        self.refused("2 'Design review:' lines", review="Design review: design/ideation-2.yaml\n" + DESIGN_LINES, extra=later)

    def test_a_second_surfaces_line_cannot_switch_the_design_review_off(self):
        two = "Surfaces: none\nVisible change: none\nSurfaces: ui\n"
        text = UI.format(review="").replace("Surfaces: ui\nVisible change: a person sees a panel.\n", two)
        with tempfile.TemporaryDirectory() as d:
            path = write_task(d, text)
            errors = ds.check_task(path)
            self.assertEqual(len([e for e in errors if "2 'Surfaces:' lines" in e]), 1, errors)
            self.assertEqual(ds.main(["check", "--seed", str(path)]), 1)

    def test_mutation_dropping_the_design_review_count_lets_two_lines_pass(self):
        mutant = mutated("""if len(DESIGN_REVIEW_LINE.findall(body)) > 1:""", "if False:")
        review = DESIGN_LINES + "Design review: design/ideation-2.yaml\n"
        later = {"ideation-2.yaml": NEWER_DESIGN_REPORT}
        self.assertTrue(self.run_check(review=review, extra=later)[0])
        self.assertEqual(self.run_check(review=review, extra=later, module=mutant)[0], [])

    def test_mutation_dropping_the_surfaces_count_lets_a_second_line_hide_ui(self):
        mutant = mutated("""if len(SURFACES.findall(fo)) > 1:""", "if False:")
        text = UI.format(review="").replace("Surfaces: ui\nVisible change: a person sees a panel.\n", "Surfaces: none\nVisible change: none\nSurfaces: ui\n")
        with tempfile.TemporaryDirectory() as d:
            path = write_task(d, text)
            self.assertTrue(ds.check_task(path))
            self.assertEqual(mutant.check_task(path), [])

    def test_mutation_dropping_the_design_call_lets_a_missing_review_pass(self):
        mutant = mutated("summary = check_design_review(path, plain, declared, shown, errors)", "summary = None")
        review = DESIGN_LINES.replace("Design review: design/ideation-1.yaml\n", "")
        self.assertTrue(self.run_check(review=review)[0])
        self.assertEqual(self.run_check(review=review, module=mutant)[0], [])

    def test_mutation_dropping_the_minor_test_lets_a_declined_major_pass(self):
        mutant = mutated(' and severities[number - 1] == "MINOR"', "")
        review = DESIGN_LINES.replace("finding 3: AC-2", "finding 3: declined: accepted")
        both = DECLINE_REPORT + "    - finding: 3\n      ruling: upheld\n      evidence: x\n      change: none\n"
        self.assertTrue(self.run_check(review=review, declines=both)[0])
        self.assertEqual(self.run_check(review=review, declines=both, module=mutant)[0], [])

    def test_mutation_dropping_the_preview_rule_lets_another_preview_pass(self):
        mutant = mutated('elif named[0].strip().strip("\\"\'") not in previews:', "elif False:")
        report = DESIGN_REPORT.replace("preview: preview.html", "preview: other.html")
        self.assertTrue(self.run_check(report=report)[0])
        self.assertEqual(self.run_check(report=report, module=mutant)[0], [])

    def test_mutation_using_the_security_scale_accepts_a_high_design_finding(self):
        mutant = mutated("report_severities(text, DESIGN_SCALE)", "report_severities(text)")
        report = DESIGN_REPORT.replace("severity: MAJOR", "severity: HIGH", 1)
        self.assertTrue(self.run_check(report=report)[0])
        self.assertTrue(any("MAJOR" in e for e in self.run_check(report=DESIGN_REPORT, module=mutant)[0]))

    def test_mutation_gating_on_ideation_alone_refuses_a_task_without_ui(self):
        mutant = mutated('if "ui" in surfaces and status and status.group(1) == "ideation":', 'if status and status.group(1) == "ideation":')
        self.assertEqual(self.run_check(review="", report=None, surfaces="none")[0], [])
        self.assertTrue(self.run_check(review="", report=None, surfaces="none", module=mutant)[0])

    def test_mutation_dropping_the_fixed_rule_refuses_a_fixed_finding(self):
        mutant = mutated('elif re.match(r"fixed:\\s*\\S", entry):', "elif False:")
        self.assertEqual(self.run_check()[0], [])
        self.assertTrue(any("report finding 1 has no" in e for e in self.run_check(module=mutant)[0]))

    def test_mutation_dropping_the_duplicate_rule_lets_two_dispositions_pass(self):
        mutant = mutated("repeated(DESIGN_FINDING_LINE.findall(body), \"Design\", name, errors)", "None")
        review = DESIGN_LINES + "Design finding 1: fixed: again\n"
        self.assertTrue(self.run_check(review=review)[0])
        self.assertEqual(self.run_check(review=review, module=mutant)[0], [])

    def test_mutation_dropping_the_one_preview_rule_lets_two_direct_previews_pass(self):
        mutant = mutated("if len(named) != 1:", "if False:")
        report = DESIGN_REPORT.replace("  preview: preview.html\n", "  preview: preview.html\n  preview: preview.html\n", 1)
        self.assertTrue(self.run_check(report=report)[0])
        self.assertEqual(self.run_check(report=report, module=mutant)[0], [])

    def test_mutation_reading_the_preview_at_any_indent_takes_a_nested_one(self):
        mutant = mutated('rf"^{child}preview:', 'rf"^[ \\t]+preview:')
        report = DESIGN_REPORT.replace("  preview: preview.html\n", "", 1).replace("      seen: tight inset\n", "      seen: tight inset\n      preview: preview.html\n")
        self.assertTrue(self.run_check(report=report)[0])
        self.assertEqual(self.run_check(report=report, module=mutant)[0], [])

    def test_mutation_searching_the_whole_report_takes_a_preview_of_another_mapping(self):
        mutant = mutated('re.findall(rf"^{child}preview:[ \\t]*(.*)$", block, re.M)', 're.findall(rf"^{child}preview:[ \\t]*(.*)$", text, re.M)')
        report = DESIGN_REPORT.replace("  preview: preview.html\n", "", 1) + "other:\n  preview: preview.html\n"
        self.assertTrue(self.run_check(report=report)[0])
        self.assertEqual(self.run_check(report=report, module=mutant)[0], [])

    def test_mutation_matching_only_the_first_preview_line_refuses_the_second(self):
        mutant = mutated('shown = [v.strip() for v in PREVIEW.findall("\\n".join(unfenced(body.split("\\n"))))]', 'shown = [v.strip() for v in PREVIEW.findall("\\n".join(unfenced(body.split("\\n"))))][:1]')
        previews = "Preview: preview.html\nPreview: second.html\n"
        report = DESIGN_REPORT.replace("preview: preview.html", "preview: second.html")
        self.assertEqual(self.run_check(previews=previews, report=report)[0], [])
        self.assertTrue(self.run_check(previews=previews, report=report, module=mutant)[0])

    def test_a_fenced_preview_line_cannot_bind_a_report(self):
        previews = "Preview: preview.html\n\n```\nPreview: fake.html\n```\n"
        report = DESIGN_REPORT.replace("preview: preview.html", "preview: fake.html")
        errors, _ = self.run_check(previews=previews, report=report)
        self.assertEqual(len([e for e in errors if "reviewed preview 'fake.html'" in e]), 1, errors)
        self.assertEqual(self.run_check(previews=previews)[0], [])

    def test_mutation_reading_preview_candidates_from_the_raw_body_lets_a_fenced_one_bind(self):
        mutant = mutated('shown = [v.strip() for v in PREVIEW.findall("\\n".join(unfenced(body.split("\\n"))))]', "shown = [v.strip() for v in PREVIEW.findall(body)]")
        previews = "Preview: preview.html\n\n```\nPreview: fake.html\n```\n"
        report = DESIGN_REPORT.replace("preview: preview.html", "preview: fake.html")
        self.assertTrue(self.run_check(previews=previews, report=report)[0])
        self.assertEqual(self.run_check(previews=previews, report=report, module=mutant)[0], [])


class FencedFoAlignmentTests(unittest.TestCase):
    QUOTED = BASE + """
## Notes

The seed form looks like this:

```
## FO alignment

Surfaces: none
Visible change: none
```
"""

    def test_a_task_quoting_a_fenced_fo_alignment_passes_check_and_seed(self):
        with tempfile.TemporaryDirectory() as d:
            path = write_task(d, self.QUOTED)
            self.assertEqual(ds.check_task(path), [])
            self.assertEqual(ds.check_task(path, seed=True), [])
            self.assertEqual(ds.main(["check", str(path)]), 0)
            self.assertEqual(ds.main(["check", "--seed", str(path)]), 0)

    def test_mutation_reading_the_fo_alignment_from_raw_text_refuses_the_quoting_task(self):
        mutant = mutated(
            '    _, body = split_fo(text)\n    fo, _ = split_fo("\\n".join(unfenced(text.split("\\n"))))\n',
            "    fo, body = split_fo(text)\n")
        with tempfile.TemporaryDirectory() as d:
            path = write_task(d, self.QUOTED)
            self.assertEqual(ds.check_task(path), [])
            self.assertTrue(any("'Surfaces:' lines, expected exactly 1" in e for e in mutant.check_task(path)))
            self.assertTrue(any("'Surfaces:' lines, expected exactly 1" in e for e in mutant.check_task(path, seed=True)))


GATED = """---
title: seats
profile: pilot
status: ideation
gates:
    version: 1
    records:
        - id: gate:t:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:t-backlog-1
              briefing:
                id: briefing:t:backlog:attempt-1:revision-1
                room-ref: ./t/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:t:backlog:1
                by: person:captain
                at: "2026-10-20T04:56:55Z"
                decision: approve
                reason: ok
---

# Task

## Scope

- Source: issue 1.
- Bite: the first thing.
- Non-goals: to be set at ideation.

## FO alignment

Surfaces: none
Visible change: none

## Acceptance criteria

**AC-1**: a driver sees seats.
"""
AMENDED = """
## Captain amendments

### Amendment 1 — 2026-10-20, chat
Captain: 「also this」 (chat)
Supersedes: none
"""
GIT_ENV = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.invalid",
           "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull}


class ScopeCheckTests(unittest.TestCase):
    """A Scope change after the backlog gate, on a task in a linked git worktree (as a split-root state checkout is, its .git a file)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        self.main = base / "main"
        self.work = base / "work"
        self.git(base, "init", "-q", str(self.main))
        self.write(self.main / "README.md", "state\n")
        self.git(self.main, "add", "README.md")
        self.git(self.main, "commit", "-q", "-m", "init")
        self.git(self.main, "worktree", "add", "-q", "--detach", str(self.work), "HEAD")
        self.task = self.work / "t.md"
        self.write(self.task, GATED)
        self.commit("t.md", "task")
        sha = self.git(self.work, "rev-parse", "HEAD").stdout.strip()
        room = self.work / "t" / "review" / "backlog" / "briefing-1"
        room.mkdir(parents=True)
        self.write(room / "index.json", f'{{"artifacts": [{{"uri": "git-root://state/{sha}/t.md"}}]}}')
        self.commit("t/review/backlog/briefing-1/index.json", "briefing")
        self.sha = sha

    def git(self, cwd, *args):
        return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, check=True, env={**os.environ, **GIT_ENV})

    @staticmethod
    def write(path, text):
        Path(path).write_text(text)

    def commit(self, rel, message):
        self.git(self.work, "add", rel)
        self.git(self.work, "commit", "-q", "-m", message)
        return self.git(self.work, "rev-parse", "HEAD").stdout.strip()

    def edit(self, old, new, task=None):
        task = task or self.task
        text = task.read_text()
        assert old in text, old
        task.write_text(text.replace(old, new, 1))

    def run_main(self, task=None, module=ds):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = module.main(["check", str(task or self.task)])
        return code, out.getvalue()

    def add_line(self, line="- Captain asked for one more thing."):
        self.edit("- Non-goals: to be set", line + "\n- Non-goals: to be set")

    def amend(self):
        self.task.write_text(self.task.read_text().rstrip("\n") + "\n" + AMENDED)

    def test_an_unchanged_scope_is_clean_and_prints_the_presentable_line(self):
        self.assertEqual(ds.scope_hold(self.task), ("clean", self.sha))
        self.assertEqual(self.run_main(), (0, "t.md: design surfaces presentable\n"))

    def test_a_scope_line_added_after_the_backlog_gate_holds_with_a_line_addressed_to_fo(self):
        self.add_line()
        code, out = self.run_main()
        self.assertEqual(code, 1)
        self.assertEqual(ds.scope_hold(self.task)[0], "hold")
        self.assertIn(f"Scope changed after the backlog gate ({self.sha[:8]}): \"- Captain asked for one more thing.\"", out)
        self.assertLess(out.index("FO: restore the line"), out.index("Amendment"))
        self.assertIn("with his words verbatim and where he said them", out)
        self.assertTrue(out.rstrip("\n").endswith("A worker that sees this line reports it to FO and edits neither Scope nor amendments."), out)
        self.assertNotIn("presentable", out)

    def test_a_scope_line_removed_after_the_backlog_gate_holds(self):
        self.edit("- Bite: the first thing.\n", "")
        self.assertEqual(ds.scope_hold(self.task)[0], "hold")

    def test_the_hold_reaches_only_a_task_in_ideation(self):
        for stage in ("implementation", "validation", "done"):
            with self.subTest(stage):
                self.task.write_text(GATED.replace("status: ideation", f"status: {stage}"))
                self.add_line()
                self.assertEqual(ds.scope_hold(self.task), ("not run", f"stage is {stage}, not ideation"))
                self.assertEqual(self.run_main(), (0, f"t.md: design surfaces presentable\nscope check not run: stage is {stage}, not ideation\n"))

    def test_an_amendment_committed_with_the_edit_covers_it_and_an_edit_after_it_holds(self):
        self.add_line()
        self.amend()
        self.assertEqual(ds.scope_hold(self.task), ("clean", "working copy"))
        commit = self.commit("t.md", "scope line with its amendment")
        self.assertEqual(ds.scope_hold(self.task), ("clean", commit))
        self.add_line("- A second ask, after the amendment.")
        verdict, line = ds.scope_hold(self.task)
        self.assertEqual(verdict, "hold")
        self.assertIn(f"Scope changed after the newest amendment ({commit[:8]})", line)
        self.assertEqual(self.run_main()[0], 1)
        self.edit("- Bite: the first thing.\n", "")
        self.assertEqual(ds.scope_hold(self.task)[0], "hold")

    def test_an_amendment_heading_outside_the_amendments_section_or_inside_a_fence_is_no_baseline(self):
        heading = "### Amendment 1 — 2026-10-20, chat\nCaptain: 「x」 (chat)\nSupersedes: none\n"
        cases = {"under another section": "\n## Design\n\n" + heading,
                 "fenced under another section": "\n## Design\n\n```\n" + heading + "```\n",
                 "fenced inside the amendments section": "\n## Captain amendments\n\n```\n" + heading + "```\n"}
        for label, extra in cases.items():
            with self.subTest(label):
                self.task.write_text(GATED)
                self.add_line()
                self.task.write_text(self.task.read_text().rstrip("\n") + "\n" + extra)
                self.commit("t.md", "scope line with a look-alike heading")
                verdict, line = ds.scope_hold(self.task)
                self.assertEqual(verdict, "hold", line)
                self.assertIn(f"Scope changed after the backlog gate ({self.sha[:8]})", line)
                self.assertEqual(self.run_main()[0], 1)

    def test_an_earlier_look_alike_heading_with_the_same_number_is_not_the_amendment_commit(self):
        self.task.write_text(GATED.rstrip("\n") + "\n\n## Design\n\n### Amendment 1 — 2026-10-20, chat\n")
        self.commit("t.md", "look-alike heading")
        self.add_line()
        self.commit("t.md", "unrecorded scope line")
        self.amend()
        real = self.commit("t.md", "the recorded amendment")
        self.assertEqual(ds.scope_hold(self.task), ("clean", real))
        self.add_line("- A second ask, after the amendment.")
        verdict, line = ds.scope_hold(self.task)
        self.assertEqual(verdict, "hold", line)
        self.assertIn(f"Scope changed after the newest amendment ({real[:8]})", line)

    def test_an_uncommitted_amendment_covers_an_uncommitted_scope_line(self):
        self.add_line()
        self.amend()
        self.assertEqual(self.run_main(), (0, "t.md: design surfaces presentable\n"))

    def test_the_four_label_prefixes_the_readme_defines_are_filled_without_an_amendment(self):
        for line in ("- Non-goals: nothing else.", "Budget: one day.", "- Stop condition: green CI.", "Follow-up: a later task."):
            with self.subTest(line):
                self.task.write_text(GATED)
                self.add_line(line)
                self.assertEqual(ds.scope_hold(self.task)[0], "clean")

    def test_an_edit_outside_scope_is_not_a_scope_change(self):
        self.edit("**AC-1**: a driver sees seats.", "**AC-1**: a driver sees seats left.")
        self.assertEqual(ds.scope_hold(self.task)[0], "clean")

    def test_a_task_the_check_cannot_judge_prints_why_and_exits_zero(self):
        self.add_line()
        self.edit("decision: approve", "decision: revise")
        self.assertEqual(self.run_main(), (0, "t.md: design surfaces presentable\nscope check not run: no closed backlog approval\n"))
        self.edit("decision: revise", "decision: approve")
        index = self.work / "t" / "review" / "backlog" / "briefing-1" / "index.json"
        original = index.read_text()
        index.write_text(original.replace(self.sha, "0" * 40))
        self.assertEqual(ds.scope_hold(self.task), ("not run", "backlog sha not readable by git"))
        index.write_text("not json")
        self.assertEqual(ds.scope_hold(self.task), ("not run", "backlog briefing unreadable"))
        index.unlink()
        self.assertEqual(ds.scope_hold(self.task), ("not run", "backlog briefing unreadable"))

    def test_a_task_extracted_without_git_history_is_not_run_as_the_observer_replays_it(self):
        self.add_line()
        plain = Path(self.tmp.name) / "plain"
        subprocess.run(["git", "-C", str(self.work), "archive", "HEAD", "t.md", "t", "--format=tar", "-o", str(Path(self.tmp.name) / "x.tar")], check=True)
        plain.mkdir()
        subprocess.run(["tar", "-x", "-C", str(plain), "-f", str(Path(self.tmp.name) / "x.tar")], check=True)
        (plain / "t.md").write_text(self.task.read_text())
        self.assertEqual(ds.scope_hold(plain / "t.md"), ("not run", "not in a git checkout"))
        self.assertEqual(self.run_main(plain / "t.md")[0], 0)

    def test_seed_mode_never_reads_git(self):
        self.add_line()
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(ds.main(["check", "--seed", str(self.task)]), 0)
        self.assertEqual(out.getvalue(), "t.md: FO alignment recorded\n")

    def amended_commit(self):
        self.add_line()
        self.amend()
        return self.commit("t.md", "scope line with its amendment")

    def test_mutation_letting_any_amendment_exempt_every_later_edit_turns_the_edit_after_it_clean(self):
        self.amended_commit()
        self.add_line("- A second ask, after the amendment.")
        mutant = mutated("    if newer:\n        found = introducing_commit(task, max(newer))",
                         '    if newer:\n        return "clean", "any amendment"\n        found = introducing_commit(task, max(newer))')
        self.assertEqual((ds.scope_hold(self.task)[0], mutant.scope_hold(self.task)[0]), ("hold", "clean"))

    def test_mutation_reading_amendment_headings_from_the_whole_body_clears_a_look_alike_heading(self):
        self.add_line()
        self.task.write_text(self.task.read_text().rstrip("\n") + "\n\n## Design\n\n### Amendment 1 — 2026-10-20, chat\n")
        self.commit("t.md", "scope line with a look-alike heading")
        mutant = mutated('amendment_entries(body.split("\\n")) or []', 're.split(r"(?m)^(?=### )", body)[1:]')
        self.assertEqual((ds.scope_hold(self.task)[0], mutant.scope_hold(self.task)[0]), ("hold", "clean"))

    def test_mutation_reading_only_the_backlog_sha_holds_a_scope_change_an_amendment_records(self):
        self.amended_commit()
        mutant = mutated("    if newer:\n        found = introducing_commit", "    if False:\n        found = introducing_commit")
        self.assertEqual((ds.scope_hold(self.task)[0], mutant.scope_hold(self.task)[0]), ("clean", "hold"))

    def test_mutation_dropping_the_label_exemption_holds_a_non_goals_fill(self):
        self.add_line("- Non-goals: nothing else.")
        mutant = mutated("and not SCOPE_EXEMPT.match(l)]", "]")
        self.assertEqual((ds.scope_hold(self.task)[0], mutant.scope_hold(self.task)[0]), ("clean", "hold"))

    def test_mutation_dropping_the_stage_gate_holds_an_implementation_run(self):
        self.task.write_text(GATED.replace("status: ideation", "status: implementation"))
        self.add_line()
        mutant = mutated('if not status or status.group(1) != "ideation":', "if not status:")
        self.assertEqual((ds.scope_hold(self.task)[0], mutant.scope_hold(self.task)[0]), ("not run", "hold"))

    def test_the_hold_wording_orders_restore_before_amendment_and_ends_with_the_worker_sentence(self):
        self.add_line()
        swapped = mutated("FO: restore the line; add an '### Amendment N' with 'Supersedes: none' only if ", "FO: add an '### Amendment N' with 'Supersedes: none' only if the Captain asked for it, restore the line otherwise; ")
        code, out = self.run_main(module=swapped)
        self.assertGreater(out.index("restore the line"), out.index("Amendment"))
        _, real = self.run_main()
        self.assertLess(real.index("restore the line"), real.index("Amendment"))


MINORS = """design_review:
  preview: preview.html
  findings:
    - severity: MINOR
      dimension: spacing
      where: a.png
      seen: one
      fix: one
    - severity: MINOR
      dimension: spacing
      where: a.png
      seen: two
      fix: two
    - severity: MINOR
      dimension: spacing
      where: a.png
      seen: three
      fix: three
"""


def ruled(*items):
    out = "design_decline_check:\n  adrs_read: none\n  rulings:\n"
    for number, ruling, extra in items:
        out += f"    - finding: {number}\n      ruling: {ruling}\n      evidence: seen in a.png\n      change: change {number}\n"
        out += "".join(f"      {key}: {value}\n" for key, value in extra.items())
    return out


class MutantMixin:
    def mutation(self, old, new, why, runner, **kwargs):
        """The real script reports `why` exactly once; the script with `old` replaced reports it nowhere."""
        mutant = mutated(old, new)
        real = runner(**kwargs)[0]
        self.assertEqual(len([e for e in real if why in e]), 1, real)
        try:
            broken = runner(module=mutant, **kwargs)[0]
        except Exception as crash:
            broken = [f"crash {crash!r}"]
        self.assertFalse(any(why in e for e in broken), broken)


class DeclineCheckTests(MutantMixin, unittest.TestCase):
    run_check = DesignReviewTests.run_check

    def refused(self, why, **kwargs):
        errors, _ = self.run_check(**kwargs)
        self.assertEqual(len([e for e in errors if why in e]), 1, errors)

    def three(self, *dispositions):
        lines = "Design review: design/ideation-1.yaml\n" + "".join(f"Design finding {n}: {d}\n" for n, d in enumerate(dispositions, 1))
        return lines + "Decline check: design/declines-1.yaml\n"

    def test_a_declined_finding_without_a_decline_check_line_is_refused(self):
        self.mutation('elif tally["declined"]:', "elif False:", "needs a 'Decline check:' line", self.run_check,
                      review=DESIGN_LINES.replace("Decline check: design/declines-1.yaml\n", ""), declines=None)

    def test_two_decline_check_lines_are_refused(self):
        self.mutation("if len(checks) > 1:", "if False:", "2 'Decline check:' lines", self.run_check,
                      review=DESIGN_LINES + "Decline check: design/declines-1.yaml\n")

    def test_a_decline_check_naming_a_missing_file_or_the_wrong_shape_is_refused(self):
        self.refused("'Decline check:' names 'design/declines-9.yaml'", review=DESIGN_LINES.replace("declines-1", "declines-9"))
        self.refused("is not a design_decline_check report", declines=DECLINE_REPORT.replace("design_decline_check:", "design_review:"))

    def test_a_declined_finding_with_no_ruling_is_refused(self):
        self.mutation("""errors.append(f"{name}: declined finding {number} has no ruling in '{value}'")""", "pass",
                      "declined finding 2 has no ruling", self.run_check, declines=ruled())

    def test_an_upheld_ruling_for_a_finding_that_is_not_declined_is_refused(self):
        self.mutation("""if item["ruling"] == "upheld" and number not in declined:""", "if False:",
                      "upholds finding 1, which is not a declined finding", self.run_check,
                      declines=ruled((1, "upheld", {}), (2, "upheld", {})))

    def test_a_ruling_for_a_finding_the_review_does_not_list_is_refused(self):
        self.mutation("if not isinstance(number, int) or not 1 <= number <= found:", "if not isinstance(number, int):",
                      "rules finding 9, which the review does not list", self.run_check,
                      declines=ruled((2, "upheld", {}), (9, "overruled", {})))
        self.refused("rules finding 2 more than once", declines=ruled((2, "upheld", {}), (2, "upheld", {})))
        self.refused("rules finding 2 as 'maybe'", declines=ruled((2, "maybe", {})))

    def test_a_ruling_outside_the_rulings_list_does_not_count(self):
        elsewhere = "design_decline_check:\n  adrs_read: none\n  rulings:\n  notes:\n    - finding: 2\n      ruling: upheld\n      evidence: e\n      change: none\n"
        after = ruled() + "other:\n  rulings:\n    - finding: 2\n      ruling: upheld\n      evidence: e\n      change: none\n"
        mutant = mutated("lines = rulings_lines(text)", "lines = text.split(chr(10))")
        for label, report in {"another key": elsewhere, "after the root": after}.items():
            with self.subTest(label):
                self.refused("declined finding 2 has no ruling", declines=report)
                self.assertEqual(self.run_check(declines=report, module=mutant)[0], [])
        fenced = "```yaml\n" + DECLINE_REPORT + "```\n"
        self.assertEqual(self.run_check(declines=fenced)[0], [])

    def test_a_ruling_missing_its_evidence_or_change_is_refused(self):
        mutant = mutated("elif missing := [key for key in RULING_REQUIRED if key not in item]:", "elif False:")
        for key in ("evidence", "change"):
            with self.subTest(key):
                report = "".join(line for line in DECLINE_REPORT.splitlines(True) if not line.lstrip().startswith(key + ":"))
                self.refused(f"rules finding 2 without '{key}'", declines=report)
                self.assertEqual(self.run_check(declines=report, module=mutant)[0], [])

    def test_a_declined_finding_ruled_overruled_or_decision_is_refused(self):
        self.mutation("""elif ruled[number]["ruling"] != "upheld":""", "elif False:",
                      "declined finding 2 is ruled overruled", self.run_check, declines=ruled((2, "overruled", {})))
        self.refused("declined finding 2 is ruled decision",
                     declines=ruled((2, "decision", {"kind": "other-task", "owner": "T5"})))

    def test_an_overruled_decline_redisposed_passes_and_counts(self):
        review = self.three("declined: one", "fixed: redrawn", "declined: three")
        declines = ruled((1, "upheld", {}), (2, "overruled", {}), (3, "upheld", {}))
        errors, notes = self.run_check(review=review, report=MINORS, declines=declines)
        self.assertEqual(errors, [])
        self.assertTrue(notes[0].endswith("; decline check design/declines-1.yaml: 2 upheld, 1 overruled, 0 decisions in 0 groups"), notes[0])
        self.assertEqual([n for n in notes if n.startswith("upheld decline")], ["upheld decline 1: one", "upheld decline 3: three"])

    def test_the_gate_material_lists_each_upheld_decline_not_a_count(self):
        review = self.three("declined: one", "fixed: redrawn", "declined: three")
        declines = ruled((1, "upheld", {}), (2, "overruled", {}), (3, "upheld", {}))
        mutant = mutated("""notes = [f"upheld {word} {n}: {lines[n].split(':', 1)[1].strip()}" for n in upheld]""", "notes = []")
        self.assertEqual(len([n for n in self.run_check(review=review, report=MINORS, declines=declines)[1] if n.startswith("upheld decline")]), 2)
        self.assertEqual([n for n in self.run_check(review=review, report=MINORS, declines=declines, module=mutant)[1] if n.startswith("upheld")], [])

    def test_a_host_component_decline_needs_its_name_and_declaration_path(self):
        bare = DESIGN_LINES.replace("declined: the inset", "declined: host component Input: the inset")
        self.mutation("if HOST_REASON.match(entry) and not HOST_FORM.match(entry):", "if False:",
                      "declines a host component without", self.run_check, review=bare)
        named = DESIGN_LINES.replace("declined: the inset", "declined: host component Input at ui.d.ts: the inset")
        self.assertEqual(self.run_check(review=named)[0], [])

    def test_a_decision_ruling_needs_a_line_a_kind_and_an_owner(self):
        two = self.three("declined: one", "Needs decision: two ADR: Plugin buttons", "declined: three")
        good = ruled((1, "upheld", {}), (2, "decision", {"kind": "host-look", "owner": "Captain"}), (3, "upheld", {}))
        self.assertEqual(self.run_check(review=two, report=MINORS, declines=good)[0], [])
        self.mutation("if number not in declined and not NEEDS_DECISION.match(entry):", "if False:",
                      "needs a 'Design finding 2: Needs decision:' line", self.run_check,
                      review=self.three("declined: one", "fixed: two", "declined: three"), report=MINORS, declines=good)
        for label, extra in {"bad kind": {"kind": "elsewhere", "owner": "Captain"}, "no owner": {"kind": "host-look"}, "no kind": {"owner": "Captain"}}.items():
            with self.subTest(label):
                self.mutation("if kind not in KINDS or not owner:", "if False:", "needs a kind of host-look, other-task, recorded-ruling and an owner",
                              self.run_check, review=two, report=MINORS,
                              declines=ruled((1, "upheld", {}), (2, "decision", extra), (3, "upheld", {})))

    def test_a_host_look_decision_must_end_with_the_adr_title(self):
        plain = self.three("declined: one", "Needs decision: two", "declined: three")
        host = ruled((1, "upheld", {}), (2, "decision", {"kind": "host-look", "owner": "Captain"}), (3, "upheld", {}))
        self.mutation('elif titled and kind == "host-look" and not item.get("adr") and not ADR_TITLE.search(entry):', "elif False:",
                      "is a host-look decision and must end 'ADR: <short title>'", self.run_check, review=plain, report=MINORS, declines=host)
        other = ruled((1, "upheld", {}), (2, "decision", {"kind": "other-task", "owner": "T5"}), (3, "upheld", {}))
        self.assertEqual(self.run_check(review=plain, report=MINORS, declines=other)[0], [])

    def test_decisions_of_one_kind_and_owner_print_once(self):
        review = self.three("Needs decision: a ADR: Plugin buttons", "Needs decision: b ADR: Plugin buttons", "Needs decision: c ADR: Plugin buttons") + "Design finding 4: Needs decision: d\n"
        report = MINORS + "    - severity: MINOR\n      dimension: spacing\n      where: a.png\n      seen: four\n      fix: four\n"
        declines = ruled((1, "decision", {"kind": "host-look", "owner": "Captain"}), (2, "decision", {"kind": "host-look", "owner": " captain "}),
                         (3, "decision", {"kind": "host-look", "owner": "Product"}), (4, "decision", {"kind": "other-task", "owner": "T5"}))
        errors, notes = self.run_check(review=review, report=report, declines=declines)
        self.assertEqual(errors, [])
        self.assertIn("4 decisions in 3 groups", notes[0])
        self.assertEqual([n for n in notes if n.startswith("decision")],
                         ["decision host-look, owner Captain (findings 1, 2): change 1", "decision host-look, owner Product (findings 3): change 3", "decision other-task, owner T5 (findings 4): change 4"])
        key = "key = (kind, owner.strip().casefold())"
        for new in ("key = (kind, number)", "key = (kind,)", "key = (kind, owner)"):
            with self.subTest(new):
                self.assertNotEqual(self.run_check(review=review, report=report, declines=declines, module=mutated(key, new))[1], notes)

    def test_each_preview_path_is_printed_resolved_and_a_url_as_written(self):
        previews = "Preview: preview.html\nPreview: https://example.test/p\n"
        notes = self.run_check(previews=previews)[1]
        shown = [n for n in notes if n.startswith("preview: ")]
        self.assertEqual(len(shown), 2)
        self.assertTrue(Path(shown[0][len("preview: "):]).is_absolute() and shown[0].endswith("/preview.html"), shown)
        self.assertEqual(shown[1], "preview: https://example.test/p")
        for old, new in (('*(f"preview: {preview}" for preview in preview_lines(path, previews))', "*[]"),
                         ("str(preview_target(task_dir, value))", "value")):
            with self.subTest(new):
                self.assertNotEqual(self.run_check(previews=previews, module=mutated(old, new))[1], notes)


VALIDATION_TASK = """---
title: a ui task
profile: pilot
status: validation
---

## FO alignment

Surfaces: ui
Visible change: a person sees a panel.

## Design

UI proposal: a panel.
Preview: preview.html
{review}
## Acceptance criteria

**AC-1**: a.
Verified by: a test.

{earlier}## Stage Report: validation

{bullet}
{lines}"""

BUILT_REPORT = """design_review:
  preview: design/built-1.png
  findings:
    - severity: MAJOR
      dimension: hierarchy
      where: built-1.png
      seen: the count is stated twice
      fix: keep one
    - severity: MINOR
      dimension: spacing
      where: built-1.png
      seen: tight inset
      fix: widen it
    - severity: MINOR
      dimension: consistency
      where: built-1.png
      seen: chevron
      fix: one convention
"""

BUILT_LINES = """Built screen review: design/validation-1.yaml
Built screen finding 1: F1
Built screen finding 2: declined: the inset matches the shell
Built screen finding 3: Needs decision: the chevron is the host's
Built screen decline check: design/validation-declines-1.yaml
"""


class BuiltScreenTests(MutantMixin, unittest.TestCase):
    def run_check(self, lines=BUILT_LINES, report=BUILT_REPORT, declines=None, shot=b"built screen", status="validation", reviewed=True,
                  previews="Preview: preview.html\n", module=ds,
                  earlier="", bullet="- F1 Behaviour: the count is said twice in the built header"):
        declines = ruled((2, "upheld", {})) if declines is None else declines
        review = "\nDesign review: design/ideation-1.yaml\n" if reviewed else ""
        text = VALIDATION_TASK.format(review=review, lines=lines, earlier=earlier, bullet=bullet).replace("status: validation", f"status: {status}").replace("Preview: preview.html\n", previews)
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d, "task", "design")
            folder.mkdir(parents=True)
            Path(d, "preview.html").write_text("<html></html>")
            folder.joinpath("validation-1.yaml").write_text(report)
            folder.joinpath("validation-declines-1.yaml").write_text(declines)
            if shot is not None:
                folder.joinpath("built-1.png").write_bytes(shot)
            path = Path(d, "task.md")
            path.write_text(text)
            notes = []
            return module.check_task(path, notes=notes), notes

    def not_run(self, **kwargs):
        errors, _ = self.run_check(**kwargs)
        self.assertEqual(len([e for e in errors if "built screen review not run" in e]), 1, errors)

    def test_a_built_screen_review_with_every_disposition_passes_and_prints_its_lines(self):
        errors, notes = self.run_check()
        self.assertEqual(errors, [])
        self.assertEqual(notes[0], "built screen review design/validation-1.yaml: 3 findings, 1 upheld declines, 0 decisions in 0 groups")
        self.assertTrue(Path(notes[1][len("preview: "):]).is_absolute() and notes[1].endswith("/design/built-1.png"), notes)
        self.assertEqual(notes[2:], ["upheld built-screen decline 2: the inset matches the shell"])

    def test_a_ui_task_without_a_built_screen_review_or_waiver_is_refused(self):
        self.not_run(lines="")
        self.not_run(lines="Built screen review: waived\n")
        self.not_run(shot=None)
        self.assertEqual(self.run_check(lines='Built screen review: waived 「skip it」\n')[0], [])

    def test_two_built_screen_review_lines_are_refused(self):
        errors, _ = self.run_check(lines=BUILT_LINES + "Built screen review: design/validation-1.yaml\n")
        self.assertEqual(len([e for e in errors if "2 'Built screen review:' lines" in e]), 1, errors)

    def test_an_ideation_picture_is_not_a_built_screen(self):
        self.not_run(shot=b"<html></html>")
        self.not_run(previews="Preview: task/design\n")
        self.assertEqual(self.run_check(shot=b"different bytes")[0], [])

    def test_a_task_without_a_design_review_or_not_at_validation_is_not_refused(self):
        self.assertEqual(self.run_check(lines="", reviewed=False), ([], []))
        self.assertEqual(self.run_check(lines="", status="implementation"), ([], []))

    def test_each_branch_of_the_screenshot_rule_has_a_mutant_that_passes_what_it_refuses(self):
        gate = 'if "ui" in surfaces and status and status.group(1) == "validation" and DESIGN_REVIEW_LINE.search(plain):'
        cases = {
            "status gate": (gate, 'if "ui" in surfaces and status and DESIGN_REVIEW_LINE.search(plain):', dict(lines="", status="implementation")),
            "design review condition": (gate, 'if "ui" in surfaces and status and status.group(1) == "validation":', dict(lines="", reviewed=False)),
            "file exists": ("or not picture.is_file():", ":", dict(shot=None)),
            "same bytes as a preview": ("if file_digest(picture) in seen:", "if False:", dict(shot=b"<html></html>")),
            "same bytes inside a preview folder": ("if file_digest(picture) in seen:", "if False:", dict(previews="Preview: task/design\n")),
            "quote": ("if not CAPTAIN_QUOTE.search(value):", "if False:", dict(lines="Built screen review: waived\n")),
            "missing line": ("if not reviews:", "if False:", dict(lines="")),
        }
        for label, (old, new, kwargs) in cases.items():
            with self.subTest(label):
                real = self.run_check(**kwargs)[0]
                try:
                    broken = self.run_check(module=mutated(old, new), **kwargs)[0]
                except Exception as crash:
                    broken = [f"crash {crash!r}"]
                refusal = [e for e in real if "built screen review not run" in e]
                if label in ("status gate", "design review condition"):
                    self.assertEqual((real, len(broken)), ([], 1), broken)
                    self.assertIn("built screen review not run", broken[0])
                else:
                    self.assertEqual(len(refusal), 1, real)
                    self.assertFalse(any("built screen review not run" in e for e in broken), broken)

    def test_a_decline_needs_its_ruling_report_and_an_overruled_one_becomes_a_decision(self):
        self.mutation("elif any(DECLINED.match(entry) for entry in lines.values()):", "elif False:",
                      "needs a 'Built screen decline check:' line", self.run_check,
                      lines=BUILT_LINES.replace("Built screen decline check: design/validation-declines-1.yaml\n", ""))
        self.mutation("""elif ruled[number]["ruling"] != "upheld":""", "elif False:", "declined finding 2 is ruled overruled",
                      self.run_check, declines=ruled((2, "overruled", {})))
        moved = BUILT_LINES.replace("declined: the inset matches the shell", "Needs decision: the inset is the host's")
        errors, notes = self.run_check(lines=moved, declines=ruled((2, "decision", {"kind": "host-look", "owner": "Captain"})))
        self.assertEqual(errors, [])
        self.assertEqual(notes[0], "built screen review design/validation-1.yaml: 3 findings, 0 upheld declines, 1 decisions in 1 group")
        self.assertEqual(notes[-1], "decision host-look, owner Captain (findings 2): change 2")
        self.mutation("""errors.append(f"{name}: 'Built screen finding {number}:' names {token}, but the current validation report has no '- {token} <Class>:' bullet")""", "pass",
                      "names F9, but the current validation report has no", self.run_check, lines=BUILT_LINES.replace("finding 1: F1", "finding 1: F9"))
        self.mutation("elif not (severities[number - 1] ==", "elif False and not (severities[number - 1] ==", "built screen finding 3 has no", self.run_check,
                      lines=BUILT_LINES.replace("Built screen finding 3: Needs decision: the chevron is the host's\n", ""))
        self.mutation("""if HOST_REASON.match(entry) and not HOST_FORM.match(entry):""", "if False:", "declines a host component without", self.run_check,
                      lines=BUILT_LINES.replace("declined: the inset", "declined: host component Input: the inset"))

    def test_an_f_bullet_must_be_in_the_current_validation_report(self):
        stale = "## Stage Report: validation\n\n- F1 Behaviour: kept from the first cycle\n\n"
        why = "names F1, but the current validation report has no"
        mutant = mutated("validation_report(body), re.M)", "body, re.M)")
        for label, kwargs in {"earlier cycle only": dict(earlier=stale, bullet="- nothing"), "another stage": dict(bullet="- nothing", earlier="## Stage Report: implementation\n\n- F1 Behaviour: x\n\n")}.items():
            with self.subTest(label):
                self.assertEqual(len([e for e in self.run_check(**kwargs)[0] if why in e]), 1)
                self.assertFalse(any(why in e for e in self.run_check(module=mutant, **kwargs)[0]))
        self.assertEqual(self.run_check(earlier=stale)[0], [])
        self.assertEqual(self.run_check(earlier=stale, bullet="- F1 Behaviour: this cycle")[0], [])

    def test_the_picture_and_the_upheld_lines_reach_the_output(self):
        for old, new in (('f"preview: {picture.resolve()}"', '""'), ('*ruling_notes("built-screen decline", lines, upheld, groups)', "*[]")):
            with self.subTest(new):
                self.assertNotEqual(self.run_check(module=mutated(old, new))[1], self.run_check()[1])


if __name__ == "__main__":
    unittest.main()
