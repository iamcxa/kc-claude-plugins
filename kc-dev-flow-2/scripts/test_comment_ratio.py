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
    def test_reports_the_ratio_of_what_the_candidate_adds_over_its_base(self):
        with tempfile.TemporaryDirectory() as repo:
            git = lambda *a: subprocess.run(["git", "-C", repo, *a], check=True, capture_output=True, text=True)
            git("init", "-q")
            git("config", "user.email", "t@example.com")
            git("config", "user.name", "t")
            Path(repo, "a.ts").write_text("// old\nconst a = 1;\n")
            git("add", ".")
            git("commit", "-qm", "base")
            base = git("rev-parse", "HEAD").stdout.strip()
            Path(repo, "a.ts").write_text("// old\nconst a = 1;\n// new\nconst b = 2;\nconst c = 3;\nconst d = 4;\n")
            git("commit", "-qam", "candidate")
            out = subprocess.run(
                ["python3", str(ROOT / "scripts/comment_ratio.py"), base, "HEAD", "--repo", repo],
                check=True, capture_output=True, text=True,
            ).stdout
        self.assertIn("code lines 4, comment lines 1, 25.0%", out)


if __name__ == "__main__":
    unittest.main()
