#!/usr/bin/env python3
import contextlib
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("package_version", Path(__file__).with_name("package_version.py"))
pv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pv)


class PackageVersionTest(unittest.TestCase):
    def run_on(self, text, loaded=(0, 18, 1)):
        with tempfile.TemporaryDirectory() as d:
            readme = Path(d, "README.md")
            readme.write_text(text)
            old, pv.loaded = pv.loaded, lambda: loaded
            out = io.StringIO()
            try:
                with contextlib.redirect_stdout(out):
                    return pv.main([str(readme)]), out.getvalue()
            finally:
                pv.loaded = old

    def line(self, version):
        return f"# Development workflow\n<!-- kc-dev-flow-2 {version} x-release-please-version -->\n"

    def test_an_older_loaded_package_holds(self):
        code, out = self.run_on(self.line("0.18.1"), loaded=(0, 17, 0))
        self.assertEqual(code, 1)
        self.assertIn("older than the README's 0.18.1", out)

    def test_versions_compare_as_numbers_not_text(self):
        self.assertEqual(self.run_on(self.line("0.9.0"), loaded=(0, 10, 0))[0], 0)
        self.assertEqual(self.run_on(self.line("0.10.0"), loaded=(0, 9, 0))[0], 1)

    def test_a_matching_or_newer_package_passes(self):
        self.assertIn("matches", self.run_on(self.line("0.18.1"))[1])
        code, out = self.run_on(self.line("0.18.0"))
        self.assertEqual(code, 0)
        self.assertIn("re-sync it", out)

    def test_a_readme_without_the_line_passes_and_says_so(self):
        code, out = self.run_on("# Development workflow\n")
        self.assertEqual(code, 0)
        self.assertIn("no kc-dev-flow-2 release line", out)

    def test_the_package_template_carries_the_line_and_matches_its_manifest(self):
        template = pv.PACKAGE / "references/sd/workflow.md"
        found = pv.MARK.search(template.read_text())
        self.assertIsNotNone(found)
        self.assertEqual(tuple(int(n) for n in found.groups()), pv.loaded())

    def test_usage_error(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(pv.main([]), 2)
            self.assertEqual(pv.main(["/no/such/README.md"]), 2)


if __name__ == "__main__":
    unittest.main()
