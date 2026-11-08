#!/usr/bin/env python3
"""Exercise dispatch records through the real Spacedock binary in split-root repos."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import uuid

ROOT = Path(__file__).resolve().parents[1]
WRAPPER = ROOT / "scripts/dispatch_stage.py"
CHECKER = ROOT / "scripts/dispatch_records.py"
BINARY = os.environ.get("SPACEDOCK_BIN")


class DispatchStageTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="dispatch-stage-")
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name).resolve()
        self.repo = self.base / "code"
        self.workflow = self.repo / "docs/dev2"
        self.workflow.mkdir(parents=True)
        self.slug = "dispatch-fixture-" + uuid.uuid4().hex
        self.addCleanup(self.remove_artifacts)
        self.env = {key: value for key, value in os.environ.items()
                    if key not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR")}
        self.env.update(GIT_AUTHOR_NAME="Dispatch Fixture", GIT_COMMITTER_NAME="Dispatch Fixture",
                        GIT_AUTHOR_EMAIL="fixture@example.invalid", GIT_COMMITTER_EMAIL="fixture@example.invalid",
                        GIT_CONFIG_COUNT="2", GIT_CONFIG_KEY_0="commit.gpgsign", GIT_CONFIG_VALUE_0="false",
                        GIT_CONFIG_KEY_1="core.hooksPath", GIT_CONFIG_VALUE_1="/dev/null", PYTHONDONTWRITEBYTECODE="1")
        (self.workflow / "README.md").write_bytes((ROOT / "references/sd/workflow.md").read_bytes())
        (self.repo / ".gitignore").write_text(".worktrees/\n**/.spacedock-state/\n")
        self.call(["git", "init", "--initial-branch=main", self.repo])
        self.git(self.repo, "add", "--", ".gitignore", "docs/dev2/README.md")
        self.git(self.repo, "commit", "-m", "test: workflow")
        self.state = self.workflow / ".spacedock-state"
        self.git(self.repo, "worktree", "add", "--detach", self.state)
        self.git(self.state, "checkout", "--orphan", "spacedock-state/dev2")
        self.git(self.state, "rm", "-rf", ".")
        self.entity = self.state / f"{self.slug}.md"
        self.entity.write_text("---\ntitle: Synthetic dispatch\nvariant: kc-dev-flow-2\nprofile: pilot\n"
                               "status: ideation\n---\n\n## FO alignment\n\nSurfaces: none\nVisible change: none\n")
        self.commit_task()
        self.folder = self.state / self.slug
        self.checklist = self.base / "checklist.txt"
        self.checklist.write_text("Inspect the real dispatch seam\nKeep the received second checklist line\n")
        self.notes = self.base / "notes.txt"
        self.notes.write_text(f"Package root: {ROOT}\nSend your completion message to `main`.\n"
                              "Keep this second scope-notes line verbatim.\n")
        self.spy = self.base / "spy"
        self.marker = self.base / "called"
        self.spy.write_text(f"#!{sys.executable}\nfrom pathlib import Path\nimport sys\n"
                            f"Path({str(self.marker)!r}).write_text('called')\nsys.exit(0)\n")
        self.spy.chmod(0o755)

    def remove_artifacts(self):
        for path in Path("/tmp/spacedock-dispatch").glob(f"*{self.slug}*"):
            if path.is_file():
                path.unlink()

    def call(self, args, expected=0):
        result = subprocess.run(list(map(str, args)), cwd=self.base, env=self.env,
                                capture_output=True, text=True, timeout=30)
        if os.environ.get("DISPATCH_STAGE_LOG"):
            with Path(os.environ["DISPATCH_STAGE_LOG"]).open("a") as log:
                log.write(json.dumps(dict(argv=list(map(str, args)), exit=result.returncode,
                                          stdout=result.stdout, stderr=result.stderr)) + "\n")
        if expected is not None:
            self.assertEqual(result.returncode, expected, (args, result.stdout, result.stderr))
        return result

    def git(self, root, *args):
        return self.call(["git", "-C", root, *args]).stdout.strip()

    def commit_task(self):
        self.git(self.state, "add", "--", self.entity.name)
        self.git(self.state, "commit", "-m", "test: task")

    def set_stage(self, stage):
        self.entity.write_text(self.entity.read_text().replace("status: ideation", f"status: {stage}"))
        self.commit_task()

    def build(self, stage="ideation", extra=(), expected=0):
        return self.call([sys.executable, "-B", WRAPPER, "--workflow-dir", self.workflow,
                          "--entity-path", self.entity, "--stage", stage, "--model", "fixture-model",
                          "--checklist-file", self.checklist, "--scope-notes-file", self.notes,
                          "--spacedock", BINARY, "--host", "codex", *extra], expected)

    def record(self, stage="ideation", number=1):
        return self.folder / "dispatch" / f"{stage}-{number}.md"

    def assert_committed(self, path, subject):
        self.assertEqual(self.git(self.state, "log", "-1", "--format=%s", "--", path), subject)
        self.assertEqual(self.git(self.state, "show", f"HEAD:{path.relative_to(self.state)}"), path.read_text().strip())
        self.assertEqual(self.git(self.state, "status", "--porcelain", "--", path), "")

    def test_stamp_commits_complete_record_and_exact_inputs(self):
        dispatched = self.git(self.workflow, "rev-parse", "HEAD")
        result = self.build(extra=("--roster", "fixture roster", "--note", "README fixture"))
        envelope = json.loads(result.stdout)
        record = self.record()
        self.assert_committed(record, f"dispatch: {self.slug} entering ideation")
        self.call([sys.executable, "-B", CHECKER, self.folder])
        self.call([sys.executable, "-B", CHECKER, "--names", "--strict", record])
        text = record.read_text()
        self.assertIn(f"Dispatched: {dispatched} (workflow checkout, README fixture)", text)
        self.assertIn("Model: fixture-model\nRoster: fixture roster", text)
        received = Path(envelope["dispatch_file_path"]).read_text()
        for heading, source in (("Checklist", self.checklist), ("Scope notes", self.notes)):
            section = text.split(f"## {heading}\n", 1)[1].split("\n## ", 1)[0]
            for line in source.read_text().splitlines():
                if line.strip():
                    self.assertIn(line, section)
                    self.assertIn(line, received)

    def test_incomplete_record_does_not_build_or_change_state(self):
        self.notes.write_text("Send your completion message to `main`.\n")
        head, task = self.git(self.state, "rev-parse", "HEAD"), self.entity.read_bytes()
        held = self.build(extra=("--spacedock", self.spy), expected=1)
        self.assertTrue(held.stderr.splitlines()[0].startswith("dispatch_stage: dispatch not built;"))
        self.assertIn("needs a 'Package root:' line", held.stderr)
        self.assertEqual(held.stdout, "")
        self.assertFalse(list((self.folder / "dispatch").glob("*.md")))
        self.assertEqual(self.git(self.state, "rev-parse", "HEAD"), head)
        self.assertEqual(self.entity.read_bytes(), task)
        self.assertFalse(self.marker.exists())

    def test_validation_candidate_is_required_before_build(self):
        self.set_stage("validation")
        held = self.build("validation", ("--spacedock", self.spy), expected=1)
        self.assertIn("no 'Candidate: <40-hex head>' line", held.stderr)
        self.assertFalse(self.record("validation").exists())
        invalid = self.build("validation", ("--candidate", "abc", "--spacedock", self.spy), expected=2)
        self.assertIn("--candidate must be a full 40-hex SHA", invalid.stderr)
        self.assertFalse(self.record("validation").exists())
        self.assertFalse(self.marker.exists())

    def test_candidates_and_feedback_flags_reach_real_build(self):
        self.set_stage("validation")
        sha = self.git(self.repo, "rev-parse", "HEAD")
        self.build("validation", ("--candidate", sha, "--candidate", "a" * 40))
        self.assertIn(f"Candidate: {sha}\nCandidate: {'a' * 40}", self.record("validation").read_text())
        feedback = self.base / "feedback.txt"
        feedback.write_text("Repair the selected fixture seam.\n")
        self.entity.write_text(self.entity.read_text().replace("status: validation", "status: implementation"))
        self.commit_task()
        result = self.build("implementation", ("--feedback-context-file", feedback, "--feedback-reflow"))
        self.assertIn("Repair the selected fixture seam.", Path(json.loads(result.stdout)["dispatch_file_path"]).read_text())

    def test_failed_stamp_removes_uncommitted_record_and_passes_error(self):
        self.set_stage("backlog")
        held = self.build(expected=1)
        self.assertTrue(held.stderr.startswith("dispatch build --stamp:"), held.stderr)
        self.assertFalse(self.record().exists())
        self.assertEqual(held.stdout, "")

    def test_identical_retry_reuses_only_at_adding_commit(self):
        self.build()
        self.build()
        self.assertFalse(self.record(number=2).exists())
        unrelated = self.state / "unrelated.md"
        unrelated.write_text("An unrelated state change.\n")
        self.git(self.state, "add", "--", unrelated.name)
        self.git(self.state, "commit", "-m", "test: unrelated state")
        self.build()
        self.assert_committed(self.record(number=2), f"dispatch: {self.slug} entering ideation")
        self.assertFalse(self.record(number=3).exists())

    def test_failed_build_removes_its_staged_record(self):
        failing = self.base / "stage-and-fail"
        failing.write_text(f"#!{sys.executable}\nimport subprocess, sys\n"
                           f"subprocess.run(['git', '-C', {str(self.state)!r}, 'add', '--', {str(self.record())!r}], check=True)\n"
                           "print('fixture staged then failed', file=sys.stderr)\nsys.exit(7)\n")
        failing.chmod(0o755)
        held = self.build(extra=("--spacedock", failing), expected=7)
        self.assertEqual(held.stderr, "fixture staged then failed\n")
        self.assertFalse(self.record().exists())
        self.assertEqual(self.git(self.state, "status", "--porcelain"), "")

    def test_changed_checklist_creates_next_committed_record(self):
        self.build()
        self.checklist.write_text("A different checklist line\n")
        self.build()
        self.assert_committed(self.record(number=2), f"dispatch: {self.slug} entering ideation")
        self.assertIn("A different checklist line", self.record(number=2).read_text())

    def test_advance_commits_record_and_withholds_envelope_on_commit_failure(self):
        self.set_stage("implementation")
        self.call([BINARY, "dispatch", "build", "--stamp", "--workflow-dir", self.workflow,
                   "--entity-path", self.entity, "--stage", "implementation", "--host", "codex",
                   "--checklist-file", self.checklist, "--scope-notes-file", self.notes])
        result = self.build("implementation", ("--advance",))
        self.assertTrue(json.loads(result.stdout)["prompt"].startswith("Advancing to next stage: implementation."))
        self.assert_committed(self.record("implementation"), f"state: update {self.slug}")
        failing = self.base / "fail-commit"
        failing.write_text(f"#!{sys.executable}\nimport subprocess, sys\n"
                           "if sys.argv[1:3] == ['state', 'commit']:\n"
                           "    print('fixture state commit refused', file=sys.stderr)\n    sys.exit(1)\n"
                           f"sys.exit(subprocess.call([{BINARY!r}, *sys.argv[1:]]))\n")
        failing.chmod(0o755)
        held = self.build("implementation", ("--advance", "--note", "retry", "--symptom", "none", "--spacedock", failing), expected=1)
        self.assertEqual(held.stdout, "")
        self.assertIn("fixture state commit refused", held.stderr)
        self.assertTrue(self.record("implementation", 2).exists())
        self.build("implementation", ("--advance", "--note", "retry", "--symptom", "none"))
        self.assert_committed(self.record("implementation", 2), f"state: update {self.slug}")


if __name__ == "__main__":
    if not BINARY or not shutil.which(BINARY):
        sys.exit("test_dispatch_stage.py: set SPACEDOCK_BIN to the real Spacedock binary")
    unittest.main()
