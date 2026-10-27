import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


adr = load("adr_lint", "adr_lint.py")
TEMPLATE = (ROOT / "references/adr-template.md").read_text()


def record(number, status="Accepted", body=None):
    text = body if body is not None else TEMPLATE
    return text.replace("# NNNN.", f"# {number}.").replace("Date: YYYY-MM-DD", "Date: 2026-09-23").replace(
        "## Status\n\nAccepted", f"## Status\n\n{status}")


class AdrLintTests(unittest.TestCase):
    def run_lint(self, files, *require):
        with tempfile.TemporaryDirectory() as d:
            for name, text in files.items():
                Path(d, name).write_text(text)
            return adr.main([d, "--require", *require]) if require else adr.main([d])

    def test_the_template_itself_is_a_valid_record(self):
        self.assertEqual(self.run_lint({"0002-first.md": record(2)}, "2"), 0)

    def test_each_format_rule_refuses(self):
        cases = {
            "missing words": record(2).replace("**Words:**", "Words:"),
            "missing options": record(2).replace("**Options considered:**", "Options:"),
            "section order": record(2).replace("## Context", "## Background"),
            "bad status": record(2, status="Done"),
            "dangling supersede": record(2, status="Superseded by 0009"),
            "title number": record(3),
            "no date": record(2).replace("Date: 2026-09-23", ""),
        }
        for label, text in cases.items():
            with self.subTest(label):
                self.assertEqual(self.run_lint({"0002-first.md": text}), 1)

    def test_a_required_record_needs_the_recommended_line_and_an_old_one_does_not(self):
        old = record(2).replace("**Recommended:**", "Recommended:")
        self.assertEqual(self.run_lint({"0002-first.md": old}), 0)
        self.assertEqual(self.run_lint({"0002-first.md": old}, "2"), 1)
        self.assertEqual(self.run_lint({"0002-first.md": old, "0003-second.md": record(3)}, "3"), 0)

    def lint_output(self, args):
        import contextlib, io
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = adr.main(args)
        return code, out.getvalue()

    def test_since_requires_every_record_changed_after_the_base_and_no_other(self):
        old = record(2).replace("**Recommended:**", "Recommended:")
        with tempfile.TemporaryDirectory() as d:
            git = lambda *a: subprocess.run(["git", "-C", d, *a], check=True, capture_output=True, text=True).stdout
            git("init", "-q")
            for n in (2, 3, 4):
                Path(d, f"000{n}-r.md").write_text(old.replace("# 2.", f"# {n}."))
            git("add", ".")
            git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "base")
            base = git("rev-parse", "HEAD").strip()
            Path(d, "0003-r.md").write_text(Path(d, "0003-r.md").read_text() + "\nAmended.\n")
            Path(d, "0005-r.md").write_text(old.replace("# 2.", "# 5."))
            code, out = self.lint_output([d, "--since", base])
            self.assertEqual(code, 1)
            self.assertIn("required ADR 0003", out)
            self.assertIn("required ADR 0005", out)
            self.assertNotIn("0002", out)
            self.assertNotIn("0004", out)
            for n in (3, 5):
                f = Path(d, f"000{n}-r.md")
                f.write_text(f.read_text().replace("**Options considered:**", "**Recommended:** not recorded\n\n**Options considered:**"))
            self.assertEqual(self.lint_output([d, "--since", base])[0], 0)
            self.assertEqual(self.lint_output([d, "--since", "no-such-commit"])[0], 2)
        with tempfile.TemporaryDirectory() as d:
            Path(d, "0002-r.md").write_text(record(2))
            self.assertEqual(self.lint_output([d, "--since", "HEAD"])[0], 2)
            code, out = self.lint_output([d])
            self.assertEqual(code, 0)
            self.assertIn("changed records not checked", out)

    def test_since_lets_a_legacy_record_take_a_forward_line(self):
        legacy = "# Old architecture notes\n\nStatus: Legacy\n\nfree-form text\n"
        with tempfile.TemporaryDirectory() as d:
            git = lambda *a: subprocess.run(["git", "-C", d, *a], check=True, capture_output=True, text=True).stdout
            git("init", "-q")
            Path(d, "0001-old.md").write_text(legacy)
            git("add", ".")
            git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "base")
            base = git("rev-parse", "HEAD").strip()
            Path(d, "0001-old.md").write_text(legacy + "\n> Amended by ADR 0002.\n")
            self.assertEqual(self.lint_output([d, "--since", base])[0], 0)
            self.assertEqual(self.lint_output([d, "--since", base, "--require", "1"])[0], 1)

    def test_an_amended_older_record_says_not_recorded_and_the_refusal_says_how(self):
        old = record(2).replace("**Recommended:**", "Recommended:")
        amended = old.replace("**Options considered:**", "**Recommended:** not recorded\n\n**Options considered:**")
        self.assertEqual(self.run_lint({"0002-first.md": amended}, "2"), 0)
        with tempfile.TemporaryDirectory() as d:
            Path(d, "0002-first.md").write_text(old)
            import contextlib, io
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                self.assertEqual(adr.main([d, "--require", "2"]), 1)
            self.assertIn("not recorded", out.getvalue())

    def test_file_names_and_numbers(self):
        self.assertEqual(self.run_lint({"2-first.md": record(2)}), 1)
        self.assertEqual(self.run_lint({"0002-first.md": record(2), "0002-second.md": record(2)}), 1)

    def test_legacy_is_skipped_but_cannot_satisfy_a_required_record(self):
        legacy = "# Old architecture notes\n\nStatus: Legacy\n\nfree-form text\n"
        self.assertEqual(self.run_lint({"0001-old.md": legacy, "0002-new.md": record(2)}, "2"), 0)
        self.assertEqual(self.run_lint({"0001-old.md": legacy}, "1"), 1)
        self.assertEqual(self.run_lint({"0002-new.md": record(2)}, "3"), 1)


def protecting(number, *paths, status="Accepted"):
    lines = "\n".join(f"- `{path}` — the read-back before mailing" for path in paths)
    return record(number, status).replace("**Protects:** none", f"**Protects:**\n{lines}")


class ProtectedPathTests(unittest.TestCase):
    def lint(self, adrs, sites, *extra):
        import contextlib, io
        with tempfile.TemporaryDirectory() as d:
            for name, text in adrs.items():
                Path(d, "docs/adr", name).parent.mkdir(parents=True, exist_ok=True)
                Path(d, "docs/adr", name).write_text(text)
            for name, text in sites.items():
                Path(d, name).parent.mkdir(parents=True, exist_ok=True)
                Path(d, name).write_text(text)
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = adr.main([str(Path(d, "docs/adr")), "--root", d, *extra])
            return code, out.getvalue()

    def test_the_template_carries_a_none_label_and_an_adr_without_the_line_passes(self):
        self.assertIn("**Protects:** none", TEMPLATE)
        self.assertEqual(self.lint({"0002-a.md": record(2)}, {})[0], 0)
        self.assertEqual(self.lint({"0002-a.md": record(2).replace("**Protects:** none\n\n", "")}, {})[0], 0)

    def test_a_listed_file_that_is_missing_fails_and_names_the_adr_and_path(self):
        code, out = self.lint({"0002-a.md": protecting(2, "src/mailer.js")}, {})
        self.assertEqual(code, 1)
        self.assertIn("0002-a.md: protects src/mailer.js, which does not exist", out)

    def test_a_listed_file_without_a_pointer_fails_and_suggests_the_full_name(self):
        code, out = self.lint({"0002-a.md": protecting(2, "src/mailer.js")}, {"src/mailer.js": "send()\n"})
        self.assertEqual(code, 1)
        self.assertIn("src/mailer.js has no pointer; add a comment line 'see docs/adr/0002-a.md'", out)

    def test_a_pointer_to_a_different_adr_does_not_count(self):
        adrs = {"0002-a.md": protecting(2, "src/mailer.js"), "0003-b.md": record(3)}
        self.assertEqual(self.lint(adrs, {"src/mailer.js": "// see docs/adr/0003-b.md\n"})[0], 1)

    def test_a_correct_pointer_passes_in_full_path_and_number_only_forms(self):
        for text in ("// see docs/adr/0002-a.md\n", "# (docs/adr/0002)\n", "<!-- see docs/adr/0002-a.md -->\n"):
            with self.subTest(text):
                self.assertEqual(self.lint({"0002-a.md": protecting(2, "src/mailer.js")}, {"src/mailer.js": text})[0], 0)

    def test_a_longer_number_is_not_the_same_adr(self):
        site = {"src/mailer.js": "// see docs/adr/00021-x.md\n"}
        self.assertEqual(self.lint({"0002-a.md": protecting(2, "src/mailer.js")}, site)[0], 1)

    def test_the_pointer_uses_the_real_adr_folder(self):
        import contextlib, io
        with tempfile.TemporaryDirectory() as d:
            Path(d, "doc/decisions").mkdir(parents=True)
            Path(d, "doc/decisions/0002-a.md").write_text(protecting(2, "src/mailer.js"))
            Path(d, "src").mkdir()
            Path(d, "src/mailer.js").write_text("// see docs/adr/0002-a.md\n")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(adr.main([str(Path(d, "doc/decisions")), "--root", d]), 1)
            Path(d, "src/mailer.js").write_text("// see doc/decisions/0002-a.md\n")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(adr.main([str(Path(d, "doc/decisions")), "--root", d]), 0)

    def test_an_adr_folder_outside_the_root_asks_for_root(self):
        import contextlib, io
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as other:
            Path(d, "0002-a.md").write_text(protecting(2, "src/mailer.js"))
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                self.assertEqual(adr.main([d, "--root", other]), 1)
            self.assertIn("pass --root", out.getvalue())

    def test_a_file_pointing_at_a_superseded_adr_fails_naming_file_and_newer_adr(self):
        adrs = {"0002-a.md": protecting(2, "src/mailer.js", status="Superseded by 0003"),
                "0003-b.md": protecting(3, "src/mailer.js")}
        code, out = self.lint(adrs, {"src/mailer.js": "// see docs/adr/0002-a.md\n// see docs/adr/0003-b.md\n"})
        self.assertEqual(code, 1)
        self.assertIn("src/mailer.js: points at ADR 0002, Superseded by 0003", out)

    def test_the_same_file_pointing_only_at_the_newer_adr_passes(self):
        adrs = {"0002-a.md": protecting(2, "src/mailer.js", status="Superseded by 0003"),
                "0003-b.md": protecting(3, "src/mailer.js")}
        self.assertEqual(self.lint(adrs, {"src/mailer.js": "// see docs/adr/0003-b.md\n"})[0], 0)

    def test_only_accepted_adrs_must_have_their_file(self):
        for status in ("Proposed", "Deprecated"):
            with self.subTest(status):
                self.assertEqual(self.lint({"0002-a.md": protecting(2, "src/gone.js", status=status)}, {})[0], 0)
        adrs = {"0002-a.md": protecting(2, "src/gone.js", status="Superseded by 0003"), "0003-b.md": record(3)}
        self.assertEqual(self.lint(adrs, {})[0], 0)

    def test_malformed_entries_fail(self):
        base = protecting(2, "src/mailer.js")
        cases = {
            "no backticks": base.replace("- `src/mailer.js`", "- src/mailer.js"),
            "absolute path": base.replace("`src/mailer.js`", "`/src/mailer.js`"),
            "parent part": base.replace("`src/mailer.js`", "`../mailer.js`"),
            "text with no list": record(2).replace("**Protects:** none", "**Protects:** maybe"),
        }
        for label, text in cases.items():
            with self.subTest(label):
                self.assertEqual(self.lint({"0002-a.md": text}, {"src/mailer.js": "// see docs/adr/0002-a.md\n"})[0], 1)

    def test_a_file_no_adr_lists_is_not_scanned(self):
        adrs = {"0002-a.md": record(2, "Superseded by 0003"), "0003-b.md": protecting(3, "src/mailer.js")}
        sites = {"src/mailer.js": "// see docs/adr/0003-b.md\n", "src/other.js": "// see docs/adr/0002-a.md\n",
                 "README.md": "docs/adr/0002-a.md\n"}
        self.assertEqual(self.lint(adrs, sites)[0], 0)


if __name__ == "__main__":
    unittest.main()
