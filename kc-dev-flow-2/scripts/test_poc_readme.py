import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("poc_readme", ROOT / "scripts/poc_readme.py")
poc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(poc)
SOURCE = (ROOT / "references/sd/workflow.md").read_text()


class DeriveTests(unittest.TestCase):
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
        expected = lines[:entry] + lines[entry + 2:start] + lines[end:]
        self.assertEqual(lines[entry + 1], "      gate: true")
        self.assertEqual(poc.derive(SOURCE), "\n".join(expected))

    def test_the_source_has_no_link_that_breaks_once_copied_into_an_adopter(self):
        import re
        self.assertEqual(re.findall(r"\]\((?!https?://)[^)#]+\)", SOURCE), [])

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
