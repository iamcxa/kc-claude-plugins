#!/usr/bin/env python3
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("workflow_checkout.py")
PACKAGE = SCRIPT.parents[1]
IDENTITY = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
            "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull}
README = "---\ntrunk: main\nstate: .spacedock-state\n---\n# Development workflow\n{}\n"


def git(where, *args):
    done = subprocess.run(["git", "-C", str(where), *args], capture_output=True, text=True, env={**os.environ, **IDENTITY})
    assert done.returncode == 0, f"git {args}: {done.stderr}"
    return done.stdout.strip()


def check(readme, env=None):
    done = subprocess.run([sys.executable, str(SCRIPT), str(readme)], capture_output=True, text=True,
                          env={**os.environ, **IDENTITY, **(env or {})})
    return done.returncode, done.stdout


class WorkflowCheckoutTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.origin = root / "origin.git"
        git(root, "init", "--bare", "-b", "main", str(self.origin))
        self.a = root / "a"
        git(root, "clone", str(self.origin), str(self.a))
        git(self.a, "checkout", "-B", "main")
        (self.a / "docs/dev2").mkdir(parents=True)
        self.write(self.a, "v1")
        self.old = self.commit(self.a, "v1")
        git(self.a, "push", "-u", "origin", "main")

    def write(self, repo, body):
        (repo / "docs/dev2/README.md").write_text(README.format(body))

    def commit(self, repo, message, *paths):
        git(repo, "add", "-A")
        git(repo, "commit", "-m", message)
        return git(repo, "rev-parse", "HEAD")

    def clone(self, name):
        target = Path(self.tmp.name) / name
        git(self.tmp.name, "clone", str(self.origin), str(target))
        return target

    def push_readme_change(self):
        self.write(self.a, "v2")
        self.commit(self.a, "v2")
        git(self.a, "push", "origin", "main")

    def test_a_checkout_behind_the_trunk_fails_and_names_the_remedy(self):
        stale = self.clone("stale")
        self.push_readme_change()
        git(stale, "checkout", "--detach", self.old)
        code, out = check(stale / "docs/dev2/README.md")
        self.assertEqual(code, 1)
        self.assertIn("differs from origin/main", out)
        self.assertIn(f"git -C {stale} checkout --detach origin/main", out)

    def test_a_readme_equal_to_the_trunks_passes_even_at_another_commit(self):
        current = self.clone("current")
        self.assertEqual(check(current / "docs/dev2/README.md")[0], 0)
        (self.a / "other.txt").write_text("x")
        self.commit(self.a, "unrelated")
        git(self.a, "push", "origin", "main")
        code, out = check(current / "docs/dev2/README.md")
        self.assertEqual(code, 0)
        self.assertIn("matches origin/main", out)
        git(current, "pull", "--ff-only")
        self.assertNotEqual(git(current, "rev-parse", "HEAD"), self.old)
        git(current, "checkout", "--detach", self.old)
        self.assertEqual(check(current / "docs/dev2/README.md")[0], 0)

    def test_the_bytes_on_disk_decide_not_the_committed_ones(self):
        current = self.clone("current")
        readme = current / "docs/dev2/README.md"
        with readme.open("a") as handle:
            handle.write("\nlocal edit\n")
        self.assertEqual(check(readme)[0], 1)
        git(current, "checkout", "--", "docs/dev2/README.md")
        self.assertEqual(check(readme)[0], 0)

    def test_a_stale_remote_tracking_ref_does_not_hide_staleness(self):
        stale = self.clone("stale")
        self.assertEqual(git(stale, "rev-parse", "origin/main"), self.old)
        self.push_readme_change()
        self.assertEqual(git(stale, "rev-parse", "origin/main"), self.old)
        code, out = check(stale / "docs/dev2/README.md")
        self.assertEqual(code, 1)
        self.assertIn("differs from origin/main", out)

    def test_a_readme_ahead_of_the_trunk_also_holds_and_a_branch_gets_a_branch_remedy(self):
        work = self.clone("work")
        git(work, "checkout", "-b", "feature")
        self.write(work, "ahead")
        self.commit(work, "ahead")
        code, out = check(work / "docs/dev2/README.md")
        self.assertEqual(code, 1)
        self.assertIn("bring branch feature level with origin/main", out)
        self.assertNotIn("checkout --detach", out)

    def test_a_crlf_readme_does_not_hash_equal_to_the_lf_trunk_blob_through_a_clean_filter(self):
        work = self.clone("work")
        (work / ".gitattributes").write_text("*.md text eol=lf\n")
        self.commit(work, "attributes")
        git(work, "push", "origin", "main")
        readme = work / "docs/dev2/README.md"
        self.assertEqual(check(readme)[0], 0)
        readme.write_bytes(readme.read_bytes().replace(b"\n", b"\r\n"))
        self.assertEqual(git(work, "hash-object", "docs/dev2/README.md"), git(work, "rev-parse", "origin/main:docs/dev2/README.md"))
        code, out = check(readme)
        self.assertEqual(code, 1)
        self.assertIn("differs from origin/main", out)

    def test_the_printed_remedy_runs_as_typed_when_the_checkout_path_has_a_space(self):
        stale = self.clone("stale checkout")
        self.push_readme_change()
        git(stale, "checkout", "--detach", self.old)
        code, out = check(stale / "docs/dev2/README.md")
        self.assertEqual(code, 1)
        remedy = out.split("Remedy: ", 1)[1].strip()
        done = subprocess.run(["sh", "-c", remedy], cwd="/", capture_output=True, text=True, env={**os.environ, **IDENTITY})
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(git(stale, "rev-parse", "HEAD"), git(stale, "rev-parse", "origin/main"))

    def test_an_unreachable_origin_is_unverifiable_not_a_pass(self):
        current = self.clone("current")
        git(current, "remote", "set-url", "origin", "/nonexistent/origin.git")
        code, out = check(current / "docs/dev2/README.md")
        self.assertEqual(code, 2)
        self.assertIn("cannot fetch origin/main", out)

    def test_a_readme_without_a_trunk_key_is_unverifiable(self):
        current = self.clone("current")
        (current / "docs/dev2/README.md").write_text("---\nstate: x\n---\n# Development workflow\n")
        code, out = check(current / "docs/dev2/README.md")
        self.assertEqual(code, 2)
        self.assertIn("declares no trunk: key", out)

    def test_a_readme_outside_a_git_work_tree_is_unverifiable(self):
        with tempfile.TemporaryDirectory() as bare:
            readme = Path(bare, "README.md")
            readme.write_text(README.format("x"))
            code, out = check(readme, env={"GIT_CEILING_DIRECTORIES": str(Path(bare).parent)})
            self.assertEqual(code, 2)
            self.assertIn("not inside a git work tree", out)

    def test_a_readme_not_on_the_trunk_is_unverifiable(self):
        current = self.clone("current")
        (current / "docs/other").mkdir()
        (current / "docs/other/README.md").write_text(README.format("new workflow"))
        code, out = check(current / "docs/other/README.md")
        self.assertEqual(code, 2)
        self.assertIn("docs/other/README.md is not tracked on origin/main", out)

    def test_usage_error(self):
        self.assertEqual(subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True).returncode, 2)
        self.assertEqual(check("/no/such/README.md")[0], 2)

    def test_the_instruction_is_in_the_skill_and_the_workflow_template(self):
        named = "<package>/scripts/workflow_checkout.py"
        for path in ("skills/dev/SKILL.md", "references/sd/workflow.md"):
            self.assertTrue(named in (PACKAGE / path).read_text(), f"{path} does not name {named}")


if __name__ == "__main__":
    unittest.main()
