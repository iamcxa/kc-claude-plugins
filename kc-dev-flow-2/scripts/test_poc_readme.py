import importlib.util
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile
import unittest

from test_sd_dispatch import TEAM_RULE, assert_team

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("poc_readme", ROOT / "scripts/poc_readme.py")
poc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(poc)
SOURCE = (ROOT / "references/sd/workflow.md").read_text()


class DeriveTests(unittest.TestCase):
    def recipe(self, source, summary="External rounds: 0\n", *, mode="valid", omit=False, ignore=False, swap=False):
        commands = re.findall(r"FO runs `(python3 <package>/scripts/delivery_gate.py question [^`]+)`", source)
        self.assertEqual(len(commands), 1)
        command = commands[0]
        self.assertIn("--summary-file <summary file>", command)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            task, question, proposed, prepared = [root / name for name in ("task.md", "question", "summary", "prepared")]
            task.write_text("---\nprofile: pilot\n---\n\n## FO alignment\nSurfaces: none\n")
            question.write_text("Sufficiency: accepted criteria.\nNecessity: summary location.\n")
            proposed.write_text(summary)
            (root / "README.md").write_text("---\ntrunk: main\nsecond-reviewer: ''\nextensions: []\n---\n")
            if mode == "unreadable":
                proposed.unlink()
            if mode == "bad-config":
                (root / "README.md").write_text("---\ntrunk: main\nsecond-reviewer: copilot\nextensions: []\n---\n")
            if omit:
                command = command.replace(" --summary-file <summary file>", "")
            for token, value in (("python3", shlex.quote(sys.executable) + " -B"), ("<package>", shlex.quote(str(ROOT))),
                                 ("<task>", shlex.quote(str(task))), ("<question file>", shlex.quote(str(question))),
                                 ("<summary file>", shlex.quote(str(proposed)))):
                command = command.replace(token, value)
            recorder = root / "prepare.py"
            recorder.write_text("from pathlib import Path\nimport sys\nPath(sys.argv[2]).write_bytes(Path(sys.argv[1]).read_bytes())\n")
            forward = question if swap else proposed
            script = command + "\ncode=$?\n" + ("" if ignore else 'test "$code" -eq 0 || exit "$code"\n')
            script += shlex.join([sys.executable, "-B", str(recorder), str(forward), str(prepared)])
            done = subprocess.run(["/bin/sh", "-c", script], cwd=d, capture_output=True, text=True)
            return done.returncode, prepared.read_bytes() if prepared.exists() else None, done.stdout

    def test_delivery_recipe_holds_nonzero_and_forwards_checked_summary_in_both_routes(self):
        for source in (SOURCE, poc.derive(SOURCE)):
            for summary, mode, expected in (("External rounds: 0\n", "valid", 0), ("", "valid", 1),
                                             ("External rounds: -1\n", "valid", 1),
                                             ("External rounds: 0\n", "unreadable", 2),
                                             ("External rounds: 0\n", "bad-config", 2)):
                with self.subTest(mode=mode, summary=summary):
                    code, prepared, out = self.recipe(source, summary, mode=mode)
                    self.assertEqual(code, expected, out)
                    self.assertEqual(prepared, summary.encode() if expected == 0 else None)
            self.assertEqual(self.recipe(source, omit=True)[0], 0)
            for mutant in (source.replace("FO runs `python3 <package>/scripts/delivery_gate.py question", "FO skips `python3 <package>/scripts/delivery_gate.py question"),
                           source.replace(" --summary-file <summary file>", "")):
                with self.assertRaises(AssertionError):
                    self.recipe(mutant)
            self.assertIsNotNone(self.recipe(source, "", omit=True)[1])
            self.assertIsNotNone(self.recipe(source, "", ignore=True)[1])
            self.assertNotEqual(self.recipe(source, swap=True)[1], b"External rounds: 0\n")

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
        self.assertEqual(lines[entry + 1], "      gate: true")
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
