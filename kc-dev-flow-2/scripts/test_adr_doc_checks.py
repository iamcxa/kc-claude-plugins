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
impact = load("doc_impact", "doc_impact.py")
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

    def test_file_names_and_numbers(self):
        self.assertEqual(self.run_lint({"2-first.md": record(2)}), 1)
        self.assertEqual(self.run_lint({"0002-first.md": record(2), "0002-second.md": record(2)}), 1)

    def test_legacy_is_skipped_but_cannot_satisfy_a_required_record(self):
        legacy = "# Old architecture notes\n\nStatus: Legacy\n\nfree-form text\n"
        self.assertEqual(self.run_lint({"0001-old.md": legacy, "0002-new.md": record(2)}, "2"), 0)
        self.assertEqual(self.run_lint({"0001-old.md": legacy}, "1"), 1)
        self.assertEqual(self.run_lint({"0002-new.md": record(2)}, "3"), 1)


class DocImpactTests(unittest.TestCase):
    def test_lists_documents_mentioning_a_changed_symbol_or_path(self):
        with tempfile.TemporaryDirectory() as d:
            git = lambda *a: subprocess.run(["git", "-C", d, *a], check=True, capture_output=True, text=True).stdout
            git("init", "-q")
            git("config", "user.email", "t@example.com")
            git("config", "user.name", "t")
            Path(d, "src").mkdir()
            Path(d, "src/store.ts").write_text("export function readClosures() { return 1 }\n")
            Path(d, "ARCH.md").write_text("Closures are read by readClosures.\n")
            Path(d, "OTHER.md").write_text("Nothing relevant here.\n")
            Path(d, "PATHS.md").write_text("See src/store.ts for storage.\n")
            Path(d, "docs").mkdir()
            Path(d, "docs/map.yaml").write_text("evidence: readClosures\n")
            Path(d, "src/local.ts").write_text("function helper() { const client = 1 }\n")
            Path(d, "NOISE.md").write_text("The client helper is unrelated.\n")
            git("add", ".")
            git("commit", "-q", "-m", "base")
            base = git("rev-parse", "HEAD").strip()
            Path(d, "src/store.ts").write_text("export function readClosures() { return 2 }\n")
            Path(d, "PATHS.md").write_text("See src/store.ts for storage, now twice.\n")
            Path(d, "src/local.ts").write_text("function helper() { const client = 2 }\n")
            git("commit", "-q", "-am", "change")
            rows = {r["doc"]: r for r in impact_rows(d, base)}
            self.assertEqual(set(rows), {"ARCH.md", "PATHS.md", "docs/map.yaml"})
            self.assertEqual(rows["ARCH.md"]["state"], "review")
            self.assertEqual(rows["PATHS.md"]["state"], "updated")


def impact_rows(repo, base):
    import io, json, contextlib
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        impact.main([base, "HEAD", "--repo", repo, "--json"])
    return json.loads(out.getvalue())


if __name__ == "__main__":
    unittest.main()
