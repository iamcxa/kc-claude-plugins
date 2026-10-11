import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("replay_dispatch", Path(__file__).with_name("replay_dispatch.py"))
replay = importlib.util.module_from_spec(spec)
spec.loader.exec_module(replay)

FAKE = """#!/usr/bin/env python3
import json, sys, pathlib
args = sys.argv[1:]
out = pathlib.Path(args[args.index("--workflow-dir") + 1]).parent / "shared-dispatch.md"
out.write_text("dispatch for " + args[args.index("--stage") + 1] + "\\n" + " ".join(args))
print(json.dumps({"dispatch_file_path": str(out)}))
"""


def repo(path, files, message="init"):
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q", str(path)], check=True)
    for name, text in files.items():
        (path / name).parent.mkdir(parents=True, exist_ok=True)
        (path / name).write_text(text)
    subprocess.run(["git", "-C", str(path), "add", "."], check=True)
    subprocess.run(["git", "-C", str(path), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", message], check=True)
    return subprocess.run(["git", "-C", str(path), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()


class ReplayDispatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        t = Path(self.tmp.name)
        self.pkg = t / "pkg"
        wf = "kc-dev-flow-2/references/sd/workflow.md"
        repo(self.pkg, {wf: "---\nstages: x\n---\nRule one.\n\nRule two.\n", "kc-dev-flow-2/skills/x/SKILL.md": "s"})
        subprocess.run(["git", "-C", str(self.pkg), "tag", "base"], check=True)
        (self.pkg / wf).write_text("---\nstages: x\n---\nRule one.\n\nRule two, changed.\n")
        subprocess.run(["git", "-C", str(self.pkg), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qam", "new"], check=True)
        self.readme = t / "adopter.md"
        self.readme.write_text("---\nstages: x\ncommissioned-by: adopter\n---\nRule one.\n\nRule two.\n")
        self.state_sha = repo(t / "state", {"task-a.md": "---\nstatus: implementation\n---\nBody.\n"})
        self.code_sha = repo(t / "code", {"app.txt": "code"})
        self.checklist = t / "checklist.txt"
        self.checklist.write_text("Do the thing\n")
        self.inject = t / "inject.md"
        self.inject.write_text("\n### FO declines\n\n- Polish: x.\n")
        self.fake = t / "spacedock"
        self.fake.write_text(FAKE)
        self.fake.chmod(0o755)
        self.run_dir = t / "runs" / "r1"
        self.t = t

    def tearDown(self):
        with contextlib.redirect_stdout(io.StringIO()):
            replay.main(["cleanup", "--run-dir", str(self.run_dir)])
        self.tmp.cleanup()

    def build(self, *extra, task="task-a", base="base"):
        args = ["build", "--run-dir", str(self.run_dir), "--package-repo", str(self.pkg), "--package-ref", "HEAD",
                "--adopter-readme", str(self.readme), "--readme-base-ref", base,
                "--state-repo", str(self.t / "state"), "--state-commit", self.state_sha, "--task", task,
                "--code-repo", str(self.t / "code"), "--code-commit", self.code_sha, "--stage", "implementation",
                "--checklist", str(self.checklist), "--spacedock", str(self.fake), *extra]
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = replay.main(args)
        return code, out.getvalue()

    def test_build_merges_the_readme_checks_out_both_commits_and_keeps_the_dispatch(self):
        code, out = self.build("--inject", str(self.inject))
        self.assertEqual(code, 0, out)
        readme = (self.run_dir / "wf/README.md").read_text()
        self.assertIn("commissioned-by: adopter", readme)
        self.assertIn("Rule two, changed.", readme)
        state = self.run_dir / "wf/.spacedock-state"
        self.assertIn("### FO declines", (state / "task-a.md").read_text())
        status = subprocess.run(["git", "-C", str(state), "status", "--short"], capture_output=True, text=True).stdout
        self.assertEqual(status, "")
        self.assertTrue((self.run_dir / "wf/.worktrees/spacedock-ensign-task-a/app.txt").exists())
        scope = (self.run_dir / "scope.txt").read_text()
        self.assertIn(f"Package root: {self.run_dir / 'package' / 'kc-dev-flow-2'}", scope.replace("/private", ""))
        self.assertIn("TEST HARNESS", scope)
        self.assertIn("dispatch for implementation", (self.run_dir / "dispatch.md").read_text())

    def test_patch_edits_the_task_and_is_committed(self):
        patch = self.t / "edit.diff"
        patch.write_text("--- a/task-a.md\n+++ b/task-a.md\n@@ -3 +3 @@\n-Body.\n+Body, edited.\n")
        code, out = self.build("--patch", str(patch))
        self.assertEqual(code, 0, out)
        state = self.run_dir / "wf/.spacedock-state"
        self.assertIn("Body, edited.", (state / "task-a.md").read_text())
        status = subprocess.run(["git", "-C", str(state), "status", "--short"], capture_output=True, text=True).stdout
        self.assertEqual(status, "")

    def test_a_readme_from_another_base_or_a_missing_task_fails(self):
        self.readme.write_text("---\nstages: y\n---\nUnrelated.\n\nRule two, other.\n")
        code, out = self.build()
        self.assertEqual(code, 1)
        self.assertIn("conflicted", out)
        replay.main(["cleanup", "--run-dir", str(self.run_dir)])
        self.readme.write_text("---\nstages: x\n---\nRule one.\n\nRule two.\n")
        code, out = self.build(task="no-such-task")
        self.assertEqual(code, 1)
        self.assertIn("not found", out)

    def test_cleanup_removes_both_worktrees(self):
        self.assertEqual(self.build()[0], 0)
        with contextlib.redirect_stdout(io.StringIO()):
            replay.main(["cleanup", "--run-dir", str(self.run_dir)])
        for name in ("state", "code"):
            trees = subprocess.run(["git", "-C", str(self.t / name), "worktree", "list"], capture_output=True, text=True).stdout
            self.assertNotIn("runs/r1", trees)
        self.assertFalse(self.run_dir.exists())


if __name__ == "__main__":
    unittest.main()
