import contextlib
import io
import importlib.util
import json
from pathlib import Path
import re
import shlex
import sys
import tempfile
import unittest

from unittest import mock

from test_sd_dispatch import TEAM_RULE, assert_team
from test_delivery_gate import gate, TASK, captain_record, readme, stubbed, quiet_roles, delivery_commands, assert_record_contract

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("poc_readme", ROOT / "scripts/poc_readme.py")
poc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(poc)
SOURCE = (ROOT / "references/sd/workflow.md").read_text()


class DeriveTests(unittest.TestCase):
    def recipe(self, source, *, mode="valid", ignore=False, swap=False):
        commands = delivery_commands(source)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            task, question = root / "task.md", root / "question"
            task.write_text(TASK)
            question.write_text("Review this candidate. Accept these observations?\n")
            readme(root)
            captain_record(task)
            values = {"task": str(task), "question": str(question), "owner/repo": "o/r", "N": "9"}
            with stubbed(root), quiet_roles(), mock.patch.object(gate, "reviewer_facts", return_value=[]), contextlib.redirect_stdout(io.StringIO()) as out:
                code = 0
                for name in ("check", "question"):
                    command = next(c for c in commands if shlex.split(c)[0] == name)
                    if name == "question":
                        path = next((gate.task_folder(task) / "merge").glob("*.json"))
                        values["record"] = str(path)
                        if mode == "changed":
                            question.write_text(question.read_text() + "Changed after check.\n")
                        if mode == "unreadable":
                            path.unlink()
                    args = shlex.split(re.sub(r"<([^>]+)>", lambda m: shlex.quote(values[m[1]]), command))
                    code = gate.main(args)
                    if code and not ignore:
                        return code, None, out.getvalue()
                data = path.read_bytes()
                assert_record_contract(self, json.loads(data))
                prepared = (question if swap else path).read_bytes()
                self.assertEqual(prepared, data)
                return code, prepared, out.getvalue()

    def test_delivery_recipe_binds_the_record_and_holds_changed_sources_in_both_routes(self):
        for source in (SOURCE, poc.derive(SOURCE)):
            for mode, expected in (("valid", 0), ("changed", 1), ("unreadable", 1)):
                with self.subTest(mode=mode):
                    code, prepared, out = self.recipe(source, mode=mode)
                    self.assertEqual(code, expected, out)
                    self.assertEqual(prepared is not None, expected == 0)
            with self.assertRaises(AssertionError):
                self.recipe(source, swap=True)
            code, prepared, _ = self.recipe(source, mode="changed", ignore=True)
            self.assertEqual(code, 1)
            self.assertIsNotNone(prepared)

    def test_the_source_derives_to_four_stages_that_never_route_through_ideation(self):
        derived = poc.derive(SOURCE)
        names = [l.split(": ")[1] for l in derived.split("\n") if l.startswith("    - name: ")]
        self.assertEqual(names, ["backlog", "implementation", "validation", "done"])
        stray = [l for l in derived.split("\n") if "ideation" in l.lower()
                 and "the POC adaptation" not in l and "removes ideation from both" not in l]
        self.assertEqual(stray, [])

    def test_only_the_ideation_entry_and_section_are_removed(self):
        lines = SOURCE.split("\n")
        entry = lines.index("    - name: ideation")
        start = lines.index("### `ideation`")
        end = lines.index("### `implementation`")
        after = next(i for i in range(entry + 1, len(lines)) if not lines[i].startswith("      "))
        expected = lines[:entry] + lines[after:start] + lines[end:]
        self.assertIn("      model: opus", lines[entry + 1:after])
        self.assertIn("      gate: true", lines[entry + 1:after])
        self.assertEqual(poc.derive(SOURCE), "\n".join(expected))

    def test_the_derived_poc_readme_carries_the_migration_rule_to_both_worker_stages(self):
        derived = poc.derive(SOURCE)
        bullet = next(b for b in derived.split("\n- **") if b.startswith("POC.**"))
        for phrase in ("FAIL R6", "boundary-crossed: persistent-state", "not repaired in\n  place", "reserves no number"):
            self.assertIn(phrase, bullet)
        for stage in ("implementation", "validation"):
            start = derived.index(f"    - name: {stage}\n")
            end = derived.index("\n    - name:", start)
            self.assertIn("        - Number guards", derived[start:end])

    def test_team_survives_derivation_with_context_in_both_worker_stages(self):
        derived = poc.derive(SOURCE)
        assert_team(derived)
        self.assertIn(TEAM_RULE, derived)
        for stage in ("implementation", "validation"):
            start = derived.index(f"    - name: {stage}\n")
            end = derived.index("\n    - name:", start)
            self.assertIn("        - Dispatch facts", derived[start:end])

    def test_the_number_guards_section_names_the_adr_path_default_the_script_cannot_tell_its_reader(self):
        section = SOURCE.split("\n## Number guards\n")[1].split("\n## ")[0]
        self.assertIn("`adr-path:` (default `docs/adr`)", section)

    def test_the_source_has_no_link_that_breaks_once_copied_into_an_adopter(self):
        import re
        self.assertEqual(re.findall(r"\]\((?!https?://)[^)#]+\)", SOURCE), [])

    def test_batch_presentation_survives_poc_derivation_outside_worker_context(self):
        section = SOURCE.split("\n## Batch gates\n", 1)[1].split("\n## ", 1)[0]
        self.assertIn("## Batch gates\n" + section, poc.derive(SOURCE))
        self.assertIn("present the batch in one sitting", section)
        self.assertIn("Unbatched tasks retain ordinary gates", section)
        self.assertNotIn("        - Batch gates", poc.derive(SOURCE))

    def test_check_reports_drift_and_accepts_a_fresh_derivation(self):
        with tempfile.TemporaryDirectory() as d:
            five, poc_path = Path(d, "five.md"), Path(d, "poc.md")
            five.write_text(SOURCE)
            poc_path.write_text(poc.derive(SOURCE))
            self.assertEqual(poc.main(["check", str(poc_path), str(five)]), 0)
            five.write_text(SOURCE.replace("trunk: main", "trunk: next"))
            self.assertEqual(poc.main(["check", str(poc_path), str(five)]), 1)



if __name__ == "__main__":
    unittest.main()
