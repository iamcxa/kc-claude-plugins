import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("comment_ratio", ROOT / "scripts/comment_ratio.py")
ratio = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ratio)

DIFF = """\
+++ b/app/a.ts
+// narrates the change
+const a = 1;
+/**
+ * block
+ */
+
+const b = a * 2;
+++ b/app/b.tsx
+{/* jsx
+   note */}
+return <p />;
+++ b/db/0001.sql
+-- why the index
+CREATE INDEX i ON t (c);
+++ b/tool.py
+# note
+x = "# not a comment"
+++ b/README.md
+// not counted: no comment syntax for this file type
"""


class CountTests(unittest.TestCase):
    def test_counts_line_and_block_comments_per_file_type(self):
        added, comments = ratio.count(DIFF)
        self.assertEqual(comments["app/a.ts"], 4)
        self.assertEqual(added["app/a.ts"], 6)
        self.assertEqual(comments["app/b.tsx"], 2)
        self.assertEqual(comments["db/0001.sql"], 1)
        self.assertEqual(comments["tool.py"], 1)
        self.assertEqual(comments["README.md"], 0)

    def test_a_block_comment_does_not_leak_into_the_next_file(self):
        added, comments = ratio.count("+++ b/a.ts\n+/* open\n+++ b/c.ts\n+const c = 1;\n")
        self.assertEqual(comments["c.ts"], 0)


class CliTests(unittest.TestCase):
    def run_tool(self, added, *extra, readme=None, base=None):
        with tempfile.TemporaryDirectory() as repo:
            git = lambda *a: subprocess.run(["git", "-C", repo, *a], check=True, capture_output=True, text=True)
            git("init", "-q")
            git("config", "user.email", "t@example.com")
            git("config", "user.name", "t")
            Path(repo, "a.ts").write_text("// old\nconst a = 1;\n")
            git("add", ".")
            git("commit", "-qm", "base")
            head = git("rev-parse", "HEAD").stdout.strip()
            Path(repo, "a.ts").write_text("// old\nconst a = 1;\n" + "".join(line + "\n" for line in added))
            git("commit", "-qam", "candidate")
            args = list(extra)
            if readme is not None:
                Path(repo, "wf").mkdir()
                if readme:
                    Path(repo, "wf/README.md").write_text(readme)
                args += ["--workflow-dir", str(Path(repo, "wf"))]
            return subprocess.run(
                ["python3", str(ROOT / "scripts/comment_ratio.py"), base or head, "HEAD", "--repo", repo, *args],
                capture_output=True, text=True,
            )

    def test_reports_the_ratio_of_what_the_candidate_adds_over_its_base(self):
        done = self.run_tool(["// new", "const b = 2;", "const c = 3;", "const d = 4;"])
        self.assertEqual(done.returncode, 0)
        self.assertIn("code lines 4, comment lines 1, 25.0%", done.stdout)

    def test_a_ratio_over_the_maximum_exits_1(self):
        done = self.run_tool(["// note"] * 8 + ["const x = 1;"] * 40, "--max", "5")
        self.assertEqual(done.returncode, 1)
        self.assertIn("FAIL: 16.7% is above the maximum 5%", done.stdout)

    def test_a_ratio_at_the_maximum_exits_0(self):
        done = self.run_tool(["// note"] + ["const x = 1;"] * 19, "--max", "5")
        self.assertEqual(done.returncode, 0)
        self.assertIn("code lines 20, comment lines 1, 5.0%", done.stdout)
        self.assertIn("maximum 5% (--max) met", done.stdout)

    def test_below_the_floor_the_ratio_is_reported_and_not_enforced(self):
        done = self.run_tool(["// note"] * 5, "--max", "5")
        self.assertEqual(done.returncode, 0)
        self.assertIn("code lines 5, comment lines 5, 100.0%", done.stdout)
        self.assertIn("not enforced: 5 code lines added, fewer than 20", done.stdout)

    def test_the_package_default_is_5_percent_without_a_flag_or_key(self):
        added = ["// note"] * 2 + ["const x = 1;"] * 18
        done = self.run_tool(added)
        self.assertEqual(done.returncode, 1)
        self.assertIn("above the maximum 5% (package default)", done.stdout)

    def test_a_readme_key_overrides_the_default_and_the_flag_overrides_the_key(self):
        added = ["// note"] * 2 + ["const x = 1;"] * 18
        readme = "---\ncomment-ratio-max: 10\nstate: .spacedock-state\n---\n"
        allowed = self.run_tool(added, readme=readme)
        self.assertEqual(allowed.returncode, 0)
        self.assertIn("maximum 10%", allowed.stdout)
        self.assertEqual(self.run_tool(added, "--max", "5", readme=readme).returncode, 1)

    def test_a_readme_without_the_key_keeps_the_default(self):
        added = ["// note"] * 2 + ["const x = 1;"] * 18
        done = self.run_tool(added, readme="---\nstate: .spacedock-state\n---\n")
        self.assertEqual(done.returncode, 1)
        self.assertIn("(package default)", done.stdout)

    def test_an_unreadable_readme_or_a_bad_value_exits_2(self):
        for readme in ("", "---\ncomment-ratio-max: five\n---\n", "---\ncomment-ratio-max: -1\n---\n"):
            with self.subTest(readme=readme):
                self.assertEqual(self.run_tool(["const b = 2;"], readme=readme).returncode, 2)
        self.assertEqual(self.run_tool(["const b = 2;"], "--max", "nan").returncode, 2)

    def test_each_citation_class_exits_1_and_names_the_line(self):
        cases = {
            "task numbering": "// Decision 3: keep this",
            "task numbering cycle": "// added in cycle-2",
            "task numbering Round": "// Round 3 fix",
            "task numbering AC": "// AC-1 covers this",
            "task numbering Finding": "// Finding 4 is closed here",
            "task numbering Task": "// Task 7 moved this",
            "task numbering Decisions": "// Decisions 10 and 11 settle this",
            "task numbering ACs": "// ACs 1-4 cover this",
            "task numbering Findings": "// Findings 2 and 3 are closed here",
            "task numbering Rounds": "// Rounds 2 and 3 found this",
            "review provenance Codex": "// Codex asked for this",
            "review provenance review of": "// after the review of the head",
            "review follow-up": "// per the review follow-up",
            "reviewer's": "// the reviewer's request",
            "PR number": "// see PR #12",
            "issue number": "// fixes #345",
            "file:line": "// see helper.ts:88",
        }
        for name, comment in cases.items():
            with self.subTest(name):
                done = self.run_tool([comment, "const b = 2;"])
                self.assertEqual(done.returncode, 1, done.stdout)
                self.assertIn(f"CITE a.ts: {comment}", done.stdout)

    def test_an_unresolvable_ref_exits_2_with_one_line_naming_it(self):
        done = self.run_tool(["const b = 2;"], base="nope")
        self.assertEqual(done.returncode, 2, done.stderr)
        self.assertEqual(len(done.stderr.strip().splitlines()), 1, done.stderr)
        self.assertIn("nope", done.stderr)
        self.assertNotIn("Traceback", done.stderr)

    def test_a_line_naming_an_adr_is_exempt_and_plain_comments_pass(self):
        for comment in ("// Decision 3 is ADR 0004", "// Round 2 is in docs/adr/0004-x.md", "// retry is idempotent"):
            with self.subTest(comment):
                self.assertEqual(self.run_tool([comment, "const b = 2;"]).returncode, 0)

    def test_citations_fail_with_or_without_a_maximum_and_below_the_floor(self):
        done = self.run_tool(["// Round 3 fix", "const b = 2;"], "--max", "100")
        self.assertEqual(done.returncode, 1)
        self.assertIn("CITE a.ts: // Round 3 fix", done.stdout)


if __name__ == "__main__":
    unittest.main()
