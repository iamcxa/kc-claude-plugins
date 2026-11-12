#!/usr/bin/env python3
"""Exercise dispatch records through the real Spacedock binary in split-root repos."""

import json
from contextlib import nullcontext
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
import uuid
import scratch

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
        remote = self.base / "dispatch-code.git"
        self.call(["git", "init", "--bare", remote])
        self.git(self.repo, "remote", "add", "origin", str(remote))
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
        self.scratch_namespace = scratch.repository(self.repo, self.state)
        self.checklist = self.base / "checklist.txt"
        self.checklist.write_text("Inspect the real dispatch seam\nKeep the received second checklist line\n")
        self.notes = self.base / "notes.txt"
        self.notes.write_text(f"Package root: {ROOT}\nSend your completion message to `main`.\n"
                              "Keep this second scope-notes line verbatim.\n")
        self.spy = self.base / "spy"
        self.marker = self.base / "called"
        self.spy.write_text(f"#!{sys.executable}\nfrom pathlib import Path\nimport subprocess, sys\n"
                            f"Path({str(self.marker)!r}).write_text('called')\n"
                            f"sys.exit(subprocess.call([{BINARY!r}, *sys.argv[1:]]))\n")
        self.spy.chmod(0o755)

    def remove_artifacts(self):
        shutil.rmtree(scratch.BASE / self.scratch_namespace / self.slug, ignore_errors=True)
        namespace = scratch.BASE / self.scratch_namespace
        if namespace.is_dir() and not any(namespace.iterdir()):
            namespace.rmdir()
        for path in Path("/tmp/spacedock-dispatch").glob(f"*{self.slug}*"):
            if path.is_file():
                path.unlink()

    def call(self, args, expected=0, child_env=None, data=None, stderr_path=None):
        with stderr_path.open("w") if stderr_path else nullcontext(subprocess.PIPE) as stderr:
            result = subprocess.run(list(map(str, args)), cwd=self.base, env=child_env or self.env,
                                    input=data, stdout=subprocess.PIPE, stderr=stderr, text=True, timeout=30)
        if stderr_path:
            result.stderr = stderr_path.read_text()
        if os.environ.get("DISPATCH_STAGE_LOG"):
            with Path(os.environ["DISPATCH_STAGE_LOG"]).open("a") as log:
                log.write(json.dumps(dict(argv=list(map(str, args)), exit=result.returncode,
                                          stdout=result.stdout, stderr=result.stderr)) + "\n")
        if expected is not None:
            self.assertEqual(result.returncode, expected, (args, result.stdout, result.stderr))
        return result

    def git(self, root, *args):
        return self.call(["git", "--literal-pathspecs", "-C", root, *args]).stdout.strip()

    def commit_task(self):
        self.git(self.state, "add", "--", self.entity.relative_to(self.state))
        self.git(self.state, "commit", "-m", "test: task")

    def set_stage(self, stage):
        self.entity.write_text(self.entity.read_text().replace("status: ideation", f"status: {stage}"))
        self.commit_task()

    def build(self, stage="ideation", extra=(), expected=0, cleanup_spy=False, child_env=None, stderr_path=None):
        launch = [sys.executable, "-B", WRAPPER]
        if cleanup_spy:
            script = ("import sys; from pathlib import Path; sys.path.insert(0, sys.argv.pop(1)); "
                      "import dispatch_stage as subject; original = subject.remove_uncommitted; "
                      "marker = Path(sys.argv.pop(1)); "
                      "subject.remove_uncommitted = lambda *a: (marker.write_text('called'), original(*a))[1]; "
                      "sys.exit(subject.main())")
            launch = [sys.executable, "-B", "-c", script, WRAPPER.parent, self.base / "cleanup-called"]
        return self.call([*launch, "--workflow-dir", self.workflow,
                          "--entity-path", self.entity, "--stage", stage, "--model", "fixture-model",
                          "--checklist-file", self.checklist, "--scope-notes-file", self.notes,
                          "--spacedock", BINARY, "--host", "codex", *extra], expected, child_env, stderr_path=stderr_path)

    def record(self, stage="ideation", number=1):
        return self.folder / "dispatch" / f"{stage}-{number}.md"

    def role(self, role="engineering-reviewer", extra=(), expected=0):
        return self.call([sys.executable, "-B", WRAPPER, "--workflow-dir", self.workflow,
                          "--entity-path", self.entity, "--role", role, "--model", "opus",
                          "--checklist-file", self.checklist, "--scope-notes-file", self.notes,
                          "--spacedock", BINARY, *extra], expected)

    def test_budget_line_and_spent_cycles_are_printed_before_build(self):
        for value, suffix in (("One cycle per stage.", ""),):
            with self.subTest(value=value):
                self.entity.write_text(self.entity.read_text() + f"\n## Budget\n- {value}\n")
                self.set_stage("implementation")
                result = self.build("implementation", ("--symptom", "none"))
                self.assertIn(f"budget: Budget: {value}; spent implementation 1, validation 0{suffix}", result.stderr)
                self.assertIn(f"Budget: {value}\n", self.record("implementation").read_text())
                self.assertTrue(Path(json.loads(result.stdout)["dispatch_file_path"]).is_file())

    def test_uncountable_budget_stdout_is_forwarded(self):
        self.entity.write_text(self.entity.read_text() + "\n## Budget\n- at most 3 days\n")
        self.set_stage("validation")
        result = self.build("validation", ("--candidate", "a" * 40, "--symptom", "none"))
        self.assertIn("budget: Budget: at most 3 days; spent implementation 0, validation 1; states no cycles", result.stderr)
        self.assertIn("Budget: at most 3 days\n", self.record("validation").read_text())

    def test_worth_requirement_uses_native_stage_for_yaml_status_values(self):
        original = self.entity.read_text()
        design = ("\n## PRFAQ\nA bounded CLI result.\n\n## Acceptance criteria\n"
                  "**AC-1** Bounded result. Evidence: one CLI run.\n")
        for path in (self.entity, self.folder / "index.md"):
            path.parent.mkdir(exist_ok=True)
            for status in ("ideation", "ideation # ready for review", "'ideation' # review", '"ideation" # review'):
                with self.subTest(status=status, path=path.name):
                    text = original.replace("status: ideation", "status: " + status) + design
                    path.write_text(text)
                    native = self.call([BINARY, "status", "--workflow-dir", self.workflow,
                                        "--read", path, "--json"])
                    self.assertEqual(json.loads(native.stdout)["frontmatter"]["status"], "ideation")
                    checker = ROOT / "scripts/design_surfaces.py"
                    refused = self.call([sys.executable, "-B", checker, "check", path], expected=1)
                    self.assertIn("design needs '### Worth questions'", refused.stdout)
                    self.assertEqual(path.read_text(), text)
                    path.write_text(text.replace("## PRFAQ\n", "## PRFAQ\n### Worth questions\nAsked, without, premise.\n"))
                    self.call([sys.executable, "-B", checker, "check", path])

    def test_unreadable_native_stage_does_not_make_design_presentable(self):
        self.entity.write_text(self.entity.read_text().replace("status: ideation", "status: ideation # review")
                               + "\n## PRFAQ\nresult\n## Acceptance criteria\n**AC-1** result\n")
        binary = self.base / "unreadable-stage"
        cases = (None, "not json", json.dumps({"command": "read", "path": str(self.entity), "frontmatter": {"status": 1}}),
                 json.dumps({"command": "read", "path": "/another/task.md", "frontmatter": {"status": "done"}}))
        for output in cases:
            with self.subTest(output=output):
                if output is not None:
                    binary.write_text(f"#!{sys.executable}\nprint({output!r})\n")
                    binary.chmod(0o755)
                result = self.call([sys.executable, "-B", ROOT / "scripts/design_surfaces.py", "check", self.entity],
                                   expected=1, child_env={**self.env, "SPACEDOCK_BIN": str(binary)})
                self.assertIn("cannot read stage for Worth questions", result.stdout)
                self.assertNotIn("design surfaces presentable", result.stdout)

    def test_budget_hold_removes_record_and_skips_build_until_amended(self):
        self.entity.write_text(self.entity.read_text() + "\n## Budget\n- One cycle per stage.\n")
        self.set_stage("implementation")
        self.build("implementation", ("--symptom", "none"))
        held = self.build("implementation", ("--symptom", "failing contract", "--spacedock", self.spy), expected=1)
        self.assertIn("budget exceeded; hold for the Captain", held.stderr)
        self.assertIn("Symptom: failing contract", held.stderr)
        self.assertEqual(held.stdout, "")
        self.assertFalse(self.marker.exists())
        self.assertFalse(self.record("implementation", 2).exists())
        self.entity.write_text(self.entity.read_text() + "\n## Captain amendments\n"
                               "### Amendment 1 — 2026-11-11, chat\nCaptain: 「approved」\n"
                               "Asked: approve two cycles per stage\nBudget: two cycles per stage\nSupersedes: none\n")
        self.commit_task()
        self.checklist.write_text(self.checklist.read_text() + "Captain amendment 1\n")
        resumed = self.build("implementation", ("--symptom", "failing contract", "--spacedock", self.spy))
        self.assertTrue(self.marker.exists())
        self.assertIn("spent implementation 2, validation 0", resumed.stderr)
        self.assertIn("Budget: two cycles per stage\n", self.record("implementation", 2).read_text())

    def test_total_cap_holds_before_build_and_keeps_existing_results(self):
        self.entity.write_text(self.entity.read_text() + "\n## Budget\n- 240 累計代理分鐘、最多 1 次派工，含一輪修正\n")
        self.set_stage("implementation")
        first = self.build("implementation", ("--symptom", "none"))
        self.assertIn("total dispatches 1", first.stderr)
        self.assertIn("minutes not counted", first.stderr)
        results = self.repo / "results.txt"
        results.write_text("retained work")
        held = self.build("implementation", ("--symptom", "new gap", "--spacedock", self.spy), expected=1)
        self.assertIn("keep the results, report the remaining work and stop adding", held.stderr)
        self.assertIn("unless the Captain replaces this outcome", held.stderr)
        self.assertEqual(results.read_text(), "retained work")
        self.assertFalse(self.marker.exists())
        self.assertFalse(self.record("implementation", 2).exists())

    def test_role_commits_complete_record_before_printing_exact_inputs(self):
        dispatched = self.git(self.workflow, "rev-parse", "HEAD")
        result = self.role(extra=("--roster", "fixture roster", "--note", "role fixture"))
        record = self.record("engineering-reviewer")
        self.assert_committed(record, f"state: update {self.slug}")
        text = record.read_text()
        self.assertTrue(text.startswith(f"# engineering-reviewer-1\nDispatched: {dispatched} "
                         "(workflow checkout, role fixture)\nModel: opus\nRoster: fixture roster\n\n"
                         f"## Checklist\n{self.checklist.read_text()}\n## Scope notes\n{self.notes.read_text()}"))
        self.assertEqual(sum(line.startswith('Scratch: /tmp/dev2/') for line in text.splitlines()), 1)
        self.assertEqual(result.stdout.encode(), record.read_bytes())
        self.assertNotIn('failed', result.stderr)
        self.call([sys.executable, "-B", CHECKER, self.folder])
        self.call([sys.executable, "-B", CHECKER, "--names", "--strict", record])

    def test_role_rejects_incomplete_scope_notes_without_prompt_or_record(self):
        self.notes.write_text("Review the package changes.\n")
        head = self.git(self.state, "rev-parse", "HEAD")
        held = self.role(expected=1)
        self.assertEqual(held.stdout, "")
        self.assertIn("needs a 'Package root:' line", held.stderr)
        self.assertIn("scope-notes line naming main as the completion recipient", held.stderr)
        self.assertEqual(self.git(self.state, "rev-parse", "HEAD"), head)
        self.assertFalse(self.record("engineering-reviewer").exists())
        self.assertEqual(self.git(self.state, "status", "--porcelain"), "")

    def test_role_commit_failure_withholds_prompt_and_retry_reuses_committed_record(self):
        failing = self.base / "fail-role-commit"
        failing.write_text(f"#!{sys.executable}\nimport subprocess, sys\n"
                           "if sys.argv[1:3] == ['state', 'commit']:\n"
                           "    print('fixture state commit refused', file=sys.stderr)\n    sys.exit(1)\n"
                           f"sys.exit(subprocess.call([{BINARY!r}, *sys.argv[1:]]))\n")
        failing.chmod(0o755)
        head = self.git(self.state, "rev-parse", "HEAD")
        held = self.role(extra=("--spacedock", failing), expected=1)
        self.assertEqual(held.stdout, "")
        self.assertIn("fixture state commit refused", held.stderr)
        record = self.record("engineering-reviewer")
        pending = record.read_bytes()
        self.assertEqual(self.git(self.state, "rev-parse", "HEAD"), head)
        refused = self.role(expected=1)
        self.assertEqual(refused.stdout, "")
        self.assertIn(str(record), refused.stderr)
        self.assertEqual(record.read_bytes(), pending)
        self.call([BINARY, "state", "commit", self.slug, "--workflow-dir", self.workflow])
        result = self.role()
        self.assertEqual(result.stdout.encode(), pending)
        self.assert_committed(record, f"state: update {self.slug}")
        self.assertFalse(self.record("engineering-reviewer", 2).exists())

    def test_role_skips_build_and_pending_hold_while_a_chief_engineer_call_is_owed(self):
        self.entity.write_text(self.entity.read_text() + "\n## Stage Report: implementation\n" * 5)
        self.commit_task()
        owed = self.call([sys.executable, "-B", ROOT / "scripts/role_triggers.py",
                          self.state, self.slug], expected=1)
        self.assertIn("chief-engineer", owed.stdout)
        argv_log = self.base / "role-argv.jsonl"
        self.spy.write_text(f"#!{sys.executable}\nfrom pathlib import Path\nimport json, subprocess, sys\n"
                            f"with Path({str(argv_log)!r}).open('a') as log:\n"
                            "    log.write(json.dumps(sys.argv[1:]) + '\\n')\n"
                            f"sys.exit(subprocess.call([{BINARY!r}, *sys.argv[1:]]))\n")
        result = self.role("chief-engineer", ("--spacedock", self.spy), expected=None)
        calls = [json.loads(line) for line in argv_log.read_text().splitlines()]
        self.assertTrue(any(args[:2] == ["state", "commit"] for args in calls), calls)
        self.assertFalse(any(args[:2] == ["dispatch", "build"] for args in calls), calls)
        self.assertEqual(result.returncode, 0, (result.stdout, result.stderr))

    def test_role_checks_the_opus_model_floor(self):
        head = self.git(self.state, "rev-parse", "HEAD")
        held = self.role(extra=("--model", "sonnet"), expected=1)
        self.assertIn("opus", held.stderr)
        self.assertEqual(held.stdout, "")
        self.assertFalse(self.record("engineering-reviewer").exists())
        self.assertEqual(self.git(self.state, "rev-parse", "HEAD"), head)
        for model in ("opus", "gpt-6-astra (Codex via Paseo, thinking xhigh)"):
            with self.subTest(model=model):
                result = self.role(extra=("--model", model))
                self.assertIn(f"Model: {model}\n", result.stdout)

    def test_role_rejects_stage_only_flags_and_unknown_roles(self):
        flags = [("--stage", "implementation"), ("--advance",), ("--bare-mode",), ("--host", "codex"),
                 ("--candidate", "a" * 40), ("--symptom", "same failure"),
                 ("--feedback-context-file", str(self.notes)), ("--feedback-reflow",),
                 ("--role", "design-director")]
        before = self.scope_snapshot()
        for extra in flags:
            with self.subTest(extra=extra):
                held = self.role(extra=extra, expected=2)
                self.assertEqual(held.stdout, "")
                self.assertEqual(self.scope_snapshot(), before)

    def test_role_numbering_is_per_role_and_retries_reuse_the_latest_record(self):
        first = self.role()
        self.assertEqual(self.role().stdout, first.stdout)
        self.assertFalse(self.record("engineering-reviewer", 2).exists())
        self.role(extra=("--note", "second call"))
        self.assertTrue(self.record("engineering-reviewer", 2).exists())
        self.role("chief-engineer")
        self.assertTrue(self.record("chief-engineer").exists())
        self.assertFalse(self.record("chief-engineer", 2).exists())

    def assert_input_bytes(self, role, newline):
        checklist = "Inspect exact bytes\n保留第二行\n".replace("\n", newline).encode("utf-8")
        notes = (f"Package root: {ROOT}\nSend your completion message to `main`.\n"
                 "保留範圍文字\n").replace("\n", newline).encode("utf-8")
        self.checklist.write_bytes(checklist)
        self.notes.write_bytes(notes)
        kind = "engineering-reviewer" if role else "ideation"
        command = [sys.executable, "-B", WRAPPER, "--workflow-dir", self.workflow,
                   "--entity-path", self.entity, "--role" if role else "--stage", kind,
                   "--model", "opus", "--checklist-file", self.checklist,
                   "--scope-notes-file", self.notes, "--spacedock", BINARY]
        if not role:
            command += ["--host", "codex"]
        result = subprocess.run(list(map(str, command)), cwd=self.base, env=self.env,
                                capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        record = self.record(kind)
        disk = record.read_bytes()
        dispatched = self.git(self.workflow, "rev-parse", "HEAD")
        expected = (f"# {kind}-1\nDispatched: {dispatched} (workflow checkout)\nModel: opus\n"
                    + ("" if role else "Budget: not recorded\n") + "\n"
                    "## Checklist\n").encode("utf-8") + checklist + b"\n## Scope notes\n" + notes
        self.assertIn(checklist, disk)
        self.assertIn(notes, disk)
        self.assertTrue(disk.startswith(expected))
        self.assertEqual(sum(line.startswith(b'Scratch: /tmp/dev2/') for line in disk.splitlines()), 1)
        committed = subprocess.run(["git", "-C", str(self.state), "show",
                                    f"HEAD:{record.relative_to(self.state)}"],
                                   env=self.env, check=True, capture_output=True).stdout
        self.assertEqual(committed, disk)
        if role:
            self.assertEqual(result.stdout, disk)
            retry = subprocess.run(list(map(str, command)), cwd=self.base, env=self.env,
                                   capture_output=True, timeout=30)
            self.assertEqual(retry.returncode, 0, retry.stderr)
            self.assertEqual(retry.stdout, disk)
            self.assertFalse(self.record(kind, 2).exists())

    def test_role_crlf_inputs_keep_raw_bytes(self):
        self.assert_input_bytes(True, "\r\n")

    def test_stage_crlf_inputs_keep_raw_bytes(self):
        self.assert_input_bytes(False, "\r\n")

    def test_role_lf_inputs_keep_raw_bytes(self):
        self.assert_input_bytes(True, "\n")

    def test_stage_lf_inputs_keep_raw_bytes(self):
        self.assert_input_bytes(False, "\n")

    def test_lf_record_matches_legacy_input_reading(self):
        import dispatch_stage as subject

        for role in (True, False):
            with self.subTest(role=role):
                argv = ["--workflow-dir", str(self.workflow), "--entity-path", str(self.entity),
                        "--role" if role else "--stage", "engineering-reviewer" if role else "ideation",
                        "--model", "opus", "--checklist-file", str(self.checklist),
                        "--scope-notes-file", str(self.notes)]
                args, dispatched, checklist, notes = subject.parse_args(argv)
                before = subject.record_text(args, 1, dispatched, self.checklist.read_text(), self.notes.read_text())
                after = subject.record_text(args, 1, dispatched, checklist, notes)
                self.assertEqual(before.encode("utf-8"), after.encode("utf-8"))

    def test_scratch_in_record_and_real_dispatch_artifact_without_changing_input(self):
        original = self.notes.read_bytes()
        result = self.build()
        record = self.record().read_text()
        expected = f'Scratch: /tmp/dev2/{self.scratch_namespace}/{self.slug}/ideation-1'
        self.assertEqual(record.splitlines().count(expected), 1)
        artifact = Path(json.loads(result.stdout)['dispatch_file_path']).read_text()
        self.assertEqual(artifact.splitlines().count(expected), 1)
        self.assertIn('Not archived (private): <what>; reproduce: <command>', artifact)
        self.assertIn(str(ROOT / 'scripts/scratch.py') + ' close ', artifact)
        self.assertEqual(self.notes.read_bytes(), original)

    def test_scope_notes_outside_scratch_refuse_before_record_and_build(self):
        for path in ('/tmp/x', '/private/tmp/x',
                     f'/tmp/dev2/{self.scratch_namespace}/{self.slug}/ideation-1/../escape'):
            with self.subTest(path=path):
                self.notes.write_text(f'Package root: {ROOT}\nSend your completion message to `main`.\nRead {path}\n')
                result = self.build(extra=('--spacedock', self.spy), expected=1)
                self.assertIn('outside', result.stderr)
                self.assertFalse(self.marker.exists())
                self.assertFalse(self.record().exists())

    def test_scope_notes_inside_scratch_are_kept(self):
        self.notes.write_text(self.notes.read_text() + f'Use /tmp/dev2/{self.scratch_namespace}/{self.slug}/ideation-1/checkout\n')
        self.build()
        self.assertIn(self.notes.read_bytes(), self.record().read_bytes())

    def test_foreign_root_owner_refuses_before_build_or_notes_write(self):
        root = scratch.claim_root(self.repo, self.folder, 'ideation-1')
        notes = root / 'scope-notes.md'
        notes.write_text('peer notes')
        (root / '.owner.json').write_text('{"repository":"foreign"}')
        result = self.build(extra=('--spacedock', self.spy), expected=1)
        self.assertIn('ownership', result.stderr)
        self.assertFalse(self.marker.exists())
        self.assertFalse(self.record().exists())
        self.assertEqual(notes.read_text(), 'peer notes')

    def assert_committed(self, path, subject):
        self.assertEqual(self.git(self.state, "log", "-1", "--format=%s", "--", path), subject)
        root = Path(self.git(self.state, "rev-parse", "--show-toplevel"))
        self.assertEqual(self.git(self.state, "show", f"HEAD:{path.relative_to(root)}"), path.read_text().strip())
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
        self.assertIn("Model: fixture-model\nBudget: not recorded\nRoster: fixture roster", text)
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

    def owe_reviewer(self):
        self.entity.write_text(self.entity.read_text() + "\n## Captain amendments\n\n"
                               "### Amendment 1 — 2026-11-09, chat\nCaptain: 「Use the revised design」 (chat)\n"
                               "Supersedes: none\nDesign: revised design\n")
        self.commit_task()
        self.checklist.write_text(self.checklist.read_text() + "Apply Captain amendment 1\n")

    def assert_role_hold_then_release(self, stage):
        self.set_stage(stage)
        self.owe_reviewer()
        extra = ("--spacedock", self.spy, * (("--candidate", "a" * 40) if stage == "validation" else ()))
        head = self.git(self.state, "rev-parse", "HEAD")
        held = self.build(stage, extra, expected=1)
        self.assertIn("dispatch not built", held.stderr)
        self.assertIn("next:", held.stderr)
        self.assertIn("engineering-reviewer", held.stderr)
        self.assertEqual(held.stdout, "")
        self.assertFalse(self.marker.exists())
        self.assertFalse(self.record(stage).exists())
        self.assertEqual(self.git(self.state, "status", "--porcelain"), "")
        self.assertEqual(self.git(self.state, "rev-parse", "HEAD"), head)
        self.entity.write_text(self.entity.read_text().replace("## FO alignment\n", "## FO alignment\n\n"
                               "Reviewer: kc-dev-flow-2:engineering-reviewer opus 2026-11-09 — reviewed amendments\n"))
        self.commit_task()
        self.build(stage, extra)
        self.assertTrue(self.marker.exists())
        self.assert_committed(self.record(stage), f"dispatch: {self.slug} entering {stage}")

    def test_implementation_refuses_an_owed_call_before_build_and_a_call_releases_it(self):
        self.assert_role_hold_then_release("implementation")

    def test_validation_refuses_an_owed_call_before_build_and_a_call_releases_it(self):
        self.assert_role_hold_then_release("validation")

    def test_ideation_builds_even_when_a_call_is_owed(self):
        self.owe_reviewer()
        self.build(extra=("--spacedock", self.spy))
        self.assertTrue(self.marker.exists())

    def test_the_third_dispatch_counts_before_it_is_committed(self):
        self.set_stage("implementation")
        self.build("implementation", ("--symptom", "same failure"))
        self.build("implementation", ("--symptom", "same failure", "--note", "second"))
        held = self.build("implementation", ("--symptom", "same failure", "--note", "third",
                                               "--spacedock", self.spy), expected=1)
        self.assertIn("3 implementation dispatches", held.stderr)
        self.assertIn("dispatch not built", held.stderr)
        self.assertFalse(self.marker.exists())
        self.assertFalse(self.record("implementation", 3).exists())
        self.assertEqual(self.git(self.state, "status", "--porcelain"), "")

    def test_an_unresolvable_committed_task_holds_on_exit_two(self):
        self.set_stage("implementation")
        self.git(self.state, "rm", "--cached", "--", self.entity)
        ignore = self.state / ".gitignore"
        ignore.write_text(self.entity.name + "\n")
        self.git(self.state, "add", "--", ignore)
        self.git(self.state, "commit", "-m", "test: task is absent from committed bytes")
        held = self.build("implementation", ("--spacedock", self.spy), expected=1)
        self.assertIn("dispatch not built", held.stderr)
        self.assertIn("no task file", held.stderr)
        self.assertFalse(self.marker.exists())
        self.assertFalse(self.record("implementation").exists())
        self.assertEqual(self.git(self.state, "status", "--porcelain"), "")

    def test_a_missing_role_checker_refuses_before_build(self):
        self.set_stage("implementation")
        script = ("import sys; from pathlib import Path; sys.path.insert(0, sys.argv.pop(1)); "
                  "import dispatch_stage as subject; subject.SCRIPTS = Path(sys.argv.pop(1)); "
                  "sys.exit(subject.main())")
        held = self.call([sys.executable, "-B", "-c", script, WRAPPER.parent, self.base / "missing-package-scripts",
                          "--workflow-dir", self.workflow, "--entity-path", self.entity, "--stage", "implementation",
                          "--model", "fixture-model", "--checklist-file", self.checklist,
                          "--scope-notes-file", self.notes, "--spacedock", self.spy, "--host", "codex"], expected=1)
        self.assertIn("dispatch not built", held.stderr)
        self.assertIn("role_triggers.py", held.stderr)
        self.assertFalse(self.marker.exists())
        self.assertFalse(self.record("implementation").exists())
        self.assertEqual(self.git(self.state, "status", "--porcelain"), "")

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

    def test_successful_same_symptom_forwards_one_reminder_before_real_build(self):
        self.set_stage("implementation")
        first = self.build("implementation", ("--symptom", "same failure"))
        self.assertNotIn("step back:", first.stderr)
        stderr_path = self.base / "wrapper-stderr.txt"
        observation = self.base / "before-build.json"
        observer = self.base / "observe-and-build"
        observer.write_text(f"#!{sys.executable}\nimport json, subprocess, sys\nfrom pathlib import Path\n"
                            f"Path({str(observation)!r}).write_text(json.dumps(dict(stderr=Path({str(stderr_path)!r}).read_text())))\n"
                            f"sys.exit(subprocess.call([{BINARY!r}, *sys.argv[1:]]))\n")
        observer.chmod(0o755)
        result = self.build("implementation", ("--symptom", "same failure", "--note", "second round",
                                                "--spacedock", observer), stderr_path=stderr_path)
        marker = f'{self.record("implementation", 2)}:1: step back: 2 implementation dispatches name symptom "same failure";'
        questions = ("which Captain words does this serve", "what breaks without it",
                     "which single premise would make the task unneeded, and what cheap test checks it now?")
        before_build = json.loads(observation.read_text())["stderr"]
        for text in (marker, *questions):
            self.assertEqual(result.stderr.count(text), 1, "successful check reminder was lost or duplicated")
            self.assertEqual(before_build.count(text), 1, "reminder was not visible before building")
        self.assertTrue(Path(json.loads(result.stdout)["dispatch_file_path"]).is_file())
        self.assertNotIn("dispatch record(s) complete", result.stdout)
        self.assert_committed(self.record("implementation", 2), f"dispatch: {self.slug} entering implementation")
        for flags in ((self.folder,), ("--names", "--strict", self.record("implementation", 2))):
            checked = self.call([sys.executable, "-B", CHECKER, *flags])
            self.assertIn(marker, checked.stderr)

    def test_successful_checks_keep_distinct_other_stage_warnings(self):
        self.set_stage("validation")
        validation = ("--candidate", "a" * 40, "--symptom", "previous failure")
        self.build("validation", validation)
        self.build("validation", (*validation, "--note", "second round"))
        self.entity.write_text(self.entity.read_text().replace("status: validation", "status: implementation"))
        self.commit_task()
        self.build("implementation", ("--symptom", "current failure"))
        result = self.build("implementation", ("--symptom", "current failure", "--note", "second round"))
        for stage, symptom in (("validation", "previous failure"), ("implementation", "current failure")):
            marker = f'{self.record(stage, 2)}:1: step back: 2 {stage} dispatches name symptom "{symptom}";'
            self.assertEqual(result.stderr.count(marker), 1, "a distinct reminder was lost or shared reminder duplicated")
        self.assertTrue(Path(json.loads(result.stdout)["dispatch_file_path"]).is_file())

    def assert_existing_record_is_preserved(self, staged=False, missing=False):
        record = self.record()
        record.parent.mkdir(parents=True)
        original = b"Prepared dispatch record\r\nKeep these original bytes.\r\n"
        record.write_bytes(original)
        if staged:
            self.git(self.state, "add", "--", record)
            original = b"Working copy differs from its staged content.\r\n"
            record.write_bytes(original)
        if missing:
            record.unlink()
        index = self.git(self.state, "ls-files", "--stage", "--", record)
        status = self.git(self.state, "status", "--porcelain", "--", record)
        head, task = self.git(self.state, "rev-parse", "HEAD"), self.entity.read_bytes()
        held = self.build(extra=("--spacedock", self.spy), expected=1)
        self.assertEqual(record.exists(), not missing, "pre-existing record was removed or recreated")
        if not missing:
            self.assertEqual(record.read_bytes(), original)
        self.assertEqual(self.git(self.state, "ls-files", "--stage", "--", record), index)
        self.assertEqual(self.git(self.state, "status", "--porcelain", "--", record), status)
        self.assertEqual(self.git(self.state, "rev-parse", "HEAD"), head)
        self.assertEqual(self.entity.read_bytes(), task)
        self.assertEqual(held.stdout, "")
        self.assertIn(str(record), held.stderr)
        self.assertNotIn("needs a 'Package root:' line", held.stderr)
        self.assertFalse(self.marker.exists())

    def test_preexisting_untracked_record_survives_refused_build(self):
        self.assert_existing_record_is_preserved()

    def test_preexisting_staged_record_survives_refused_build(self):
        self.assert_existing_record_is_preserved(staged=True)

    def test_preexisting_index_entry_without_worktree_file_is_preserved(self):
        self.assert_existing_record_is_preserved(staged=True, missing=True)

    def scope_seed(self, layout="flat", route="fresh"):
        self.env["GIT_OPTIONAL_LOCKS"] = "0"
        if layout == "folder":
            self.folder.mkdir()
            destination = self.folder / "index.md"
            self.git(self.state, "mv", "--", self.entity, destination)
            self.entity = destination
            self.commit_task()
        self.older = self.folder / "dispatch/validation-1.md"
        self.older.parent.mkdir(parents=True, exist_ok=True)
        self.older.write_text(f"# validation-1\nDispatched: {'a' * 40}\nModel: fixture\nCandidate: {'a' * 40}\n"
                              f"\n## Checklist\nInspect the previous artifact.\n\n## Scope notes\n{self.notes.read_text()}")
        self.report = self.folder / "review/nested/report.md"
        self.report.parent.mkdir(parents=True)
        self.report.write_text("Original companion report.\n")
        self.literal = self.folder / "review/[literal] space\nreport.md"
        self.literal.write_text("Literal path report.\n")
        self.outside = self.state / "other-task.txt"
        self.outside.write_text("Outside HEAD bytes.\n")
        (self.state / "rename-source.txt").write_text("Outside rename source.\n")
        self.git(self.state, "add", "--", self.folder, self.outside, self.state / "rename-source.txt")
        self.git(self.state, "commit", "-m", "test: clean task scope")
        stage, extra = "ideation", ()
        if route == "advance":
            self.set_stage("implementation")
            self.build("implementation")
            stage, extra = "implementation", ("--advance",)
        elif route in ("retry", "new-round"):
            self.build()
            if route == "new-round":
                history = self.state / "outside-history.txt"
                history.write_text("An unrelated state commit.\n")
                self.git(self.state, "add", "--", history)
                self.git(self.state, "commit", "-m", "test: outside history")
        return stage, extra

    def scope_snapshot(self):
        files = {}
        for root in (self.state, *getattr(self, "extra_roots", [])):
            paths = [root]
            if root.is_dir() and not root.is_symlink():
                for parent, directories, names in os.walk(root, followlinks=False):
                    directories[:] = [name for name in directories if name != ".git"]
                    paths += [Path(parent) / name for name in directories + names if name != ".git"]
            for path in paths:
                info = path.lstat()
                value = [stat.S_IFMT(info.st_mode), stat.S_IMODE(info.st_mode)]
                value.append(os.readlink(path) if path.is_symlink() else path.read_bytes().hex() if path.is_file() else None)
                files[str(path)] = value
        return dict(head=self.git(self.state, "rev-parse", "HEAD"), files=files,
                    index=self.call(["git", "-C", self.state, "ls-files", "--stage", "--debug", "-z"]).stdout,
                    flags=self.call(["git", "-C", self.state, "ls-files", "-v", "-z"]).stdout)

    def dirty_outside(self):
        self.outside.write_text("Outside staged bytes.\n")
        self.git(self.state, "add", "--", self.outside)
        self.outside.write_text("Outside working bytes, different again.\n")
        (self.state / "untracked-other-task.txt").write_text("Outside untracked bytes.\n")

    def scope_dirty(self, path, change):
        original = path.read_bytes() if path.exists() else b"Prepared record.\n"
        edited = original + b"A preserved edit.\n"
        if change in ("staged-only", "equal-change", "partial"):
            path.write_bytes(edited)
            self.git(self.state, "add", "--", path)
            if change != "equal-change":
                path.write_bytes(original if change == "staged-only" else edited + b"Working-only edit.\n")
        elif change in ("worktree-only", "literal"):
            path.write_bytes(edited)
        elif change in ("untracked", "staged-add", "staged-add-missing", "intent-to-add", "ignored-existing"):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(edited)
            if change in ("staged-add", "staged-add-missing", "intent-to-add"):
                self.git(self.state, "add", *("-N",) if change == "intent-to-add" else (), "--", path)
            if change == "staged-add-missing":
                path.unlink()
        elif change == "staged-delete":
            self.git(self.state, "rm", "--cached", "--", path)
        elif change == "unstaged-delete":
            path.unlink()
        elif change == "both-delete":
            self.git(self.state, "rm", "-f", "--", path)
        elif change == "mode-change":
            path.chmod(path.stat().st_mode | stat.S_IXUSR)
            self.env.update(GIT_CONFIG_COUNT="3", GIT_CONFIG_KEY_2="core.filemode", GIT_CONFIG_VALUE_2="false")
        elif change == "type-change":
            external = self.base / "external-target"
            external.write_text("External bytes must survive.\n")
            self.extra_roots = [external]
            path.unlink()
            path.symlink_to(external)
        elif change in ("assume-unchanged", "skip-worktree"):
            self.git(self.state, "update-index", "--" + change, "--", path)
            path.write_bytes(edited)
        elif change == "stat-spoof":
            info = path.stat()
            path.write_bytes(b"X" + original[1:])
            os.utime(path, ns=(info.st_atime_ns, info.st_mtime_ns))
            self.env.update(GIT_CONFIG_COUNT="4", GIT_CONFIG_KEY_2="core.trustctime", GIT_CONFIG_VALUE_2="false",
                            GIT_CONFIG_KEY_3="core.checkStat", GIT_CONFIG_VALUE_3="minimal")
        elif change == "rename-out":
            self.git(self.state, "mv", "--", path, self.state / "renamed-outside.txt")
        elif change == "rename-in":
            path = self.folder / "review/renamed-inside.txt"
            self.git(self.state, "mv", "--", self.state / "rename-source.txt", path)
        elif change == "conflict":
            relative = path.relative_to(self.state)
            oid = self.call(["git", "-C", self.state, "hash-object", "-w", "--stdin"], data="Conflict version\n").stdout.strip()
            entries = f"0 {'0' * 40}\t{relative}\n" + "".join(f"100644 {oid} {stage}\t{relative}\n" for stage in (1, 2, 3))
            self.call(["git", "-C", self.state, "update-index", "--index-info"], data=entries)
        else:
            raise AssertionError(change)
        return path

    def assert_scope_refusal(self, scenario, path, stage, extra, child_env=None, real_builder=False):
        before = self.scope_snapshot()
        result = self.build(stage, extra if real_builder else (*extra, "--spacedock", self.spy),
                            expected=None, cleanup_spy=True, child_env=child_env)
        after = self.scope_snapshot()
        builder_called = self.marker.exists()
        cleanup_called = (self.base / "cleanup-called").exists()
        if os.environ.get("DISPATCH_SCOPE_LOG"):
            with Path(os.environ["DISPATCH_SCOPE_LOG"]).open("a") as log:
                log.write(json.dumps(dict(scenario=scenario, before=before, after=after, exit=result.returncode,
                                          stdout=result.stdout, stderr=result.stderr,
                                          builder_called=builder_called, cleanup_called=cleanup_called)) + "\n")
        self.assertEqual(after, before, "refusal changed scoped or outside state")
        self.assertNotEqual(result.returncode, 0, "dirty task scope was admitted")
        self.assertTrue(result.stderr.startswith("dispatch_stage: dispatch not built;"), result.stderr)
        self.assertIn(repr(str(path)), result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertFalse(builder_called, "builder ran on a dirty scope")
        self.assertFalse(cleanup_called, "cleanup ran on a dirty scope")

    def test_retry_preserves_staged_record_with_worktree_at_head(self):
        stage, extra = self.scope_seed(route="retry")
        path = self.scope_dirty(self.record(), "staged-only")
        self.dirty_outside()
        self.assert_scope_refusal("reported-retry", path, stage, extra, real_builder=True)

    def test_scope_preservation_matrix(self):
        scenarios = []
        for layout in ("flat", "folder"):
            for location, route in (("task", "fresh"), ("older", "new-round"), ("report", "fresh"),
                                    ("reused", "retry"), ("reused", "advance")):
                scenarios += [(layout, route, location, state) for state in ("staged-only", "worktree-only", "equal-change", "partial")]
            scenarios += [(layout, "fresh", "report", state) for state in
                          ("staged-delete", "unstaged-delete", "both-delete", "mode-change", "type-change", "conflict",
                           "assume-unchanged", "skip-worktree", "stat-spoof", "rename-out", "rename-in")]
            scenarios += [(layout, route, "new-record", state) for route in ("fresh", "new-round", "advance")
                          for state in ("untracked", "staged-add", "staged-add-missing", "intent-to-add")]
            scenarios += [(layout, "fresh", "literal", "literal"), (layout, "fresh", "new-record", "ignored-existing"),
                          (layout, "fresh", "new-report", "untracked")]
        selected = [row for row in scenarios if not os.environ.get("DISPATCH_SCOPE_CASE")
                    or ":".join(row) == os.environ["DISPATCH_SCOPE_CASE"]]
        self.assertTrue(selected, "unknown scope matrix case")
        for layout, route, location, change in selected:
            scenario = ":".join((layout, route, location, change))
            with self.subTest(scenario=scenario):
                fixture = type(self)("test_scope_preservation_matrix")
                try:
                    fixture.setUp()
                    stage, extra = fixture.scope_seed(layout, route)
                    if location == "new-record":
                        number = 1 if route == "fresh" else 2
                        path = fixture.record(stage, number)
                        if route == "advance":
                            extra += ("--note", "next", "--symptom", "none")
                        if change == "ignored-existing":
                            ignore = fixture.state / ".gitignore"
                            ignore.write_text(f"/{path.relative_to(fixture.state)}\n")
                            fixture.git(fixture.state, "add", "--", ignore)
                            fixture.git(fixture.state, "commit", "-m", "test: ignored target")
                    else:
                        path = {"task": fixture.entity, "older": fixture.older, "report": fixture.report,
                                "reused": fixture.record(stage), "literal": fixture.literal,
                                "new-report": fixture.folder / "review/untracked/deep.txt"}[location]
                    path = fixture.scope_dirty(path, change)
                    fixture.dirty_outside()
                    fixture.assert_scope_refusal(scenario, path, stage, extra)
                finally:
                    fixture.doCleanups()

    def outside_snapshot(self):
        relative = self.outside.relative_to(self.state)
        return (self.outside.read_bytes(), self.git(self.state, "show", f":{relative}"),
                self.git(self.state, "ls-files", "--stage", "--", relative),
                (self.state / "untracked-other-task.txt").read_bytes())

    def test_real_builder_allowed_routes_preserve_other_tasks(self):
        for layout in ("flat", "folder"):
            with self.subTest(layout=layout):
                fixture = type(self)("test_real_builder_allowed_routes_preserve_other_tasks")
                try:
                    fixture.setUp()
                    fixture.scope_seed(layout)
                    fixture.dirty_outside()
                    outside = fixture.outside_snapshot()
                    first_head = fixture.git(fixture.state, "rev-parse", "HEAD")
                    fixture.build()
                    fixture.assert_committed(fixture.record(), f"dispatch: {fixture.slug} entering ideation")
                    fixture.assertEqual(fixture.outside_snapshot(), outside)
                    changed = fixture.git(fixture.state, "diff", "--name-only", first_head, "HEAD").splitlines()
                    fixture.assertTrue(changed)
                    fixture.assertTrue(all(path == fixture.entity.relative_to(fixture.state).as_posix()
                                           or path.startswith(fixture.slug + "/") for path in changed), changed)
                    held = fixture.build(expected=1)
                    fixture.assertIn("git commit failed:", held.stderr)
                    fixture.assertEqual(held.stdout, "")
                    fixture.assertEqual(fixture.outside_snapshot(), outside)
                    fixture.git(fixture.state, "restore", "--staged", "--", fixture.outside)
                    fixture.build()
                    fixture.assertFalse(fixture.record(number=2).exists())
                    fixture.dirty_outside()
                    fixture.assertEqual(fixture.outside_snapshot(), outside)
                    fixture.checklist.write_text("Changed actual dispatch inputs.\n")
                    fixture.build(extra=("--symptom", "changed inputs"))
                    fixture.assert_committed(fixture.record(number=2), f"dispatch: {fixture.slug} entering ideation")
                    fixture.assertEqual(fixture.outside_snapshot(), outside)
                    history = fixture.state / "later-task.txt"
                    history.write_text("Independent later commit.\n")
                    fixture.git(fixture.state, "add", "--", history)
                    fixture.git(fixture.state, "commit", "-m", "test: later task", "--", history)
                    fixture.build(extra=("--symptom", "changed inputs"))
                    fixture.assertTrue(fixture.record(number=3).exists())
                    fixture.assertEqual(fixture.outside_snapshot(), outside)
                    fixture.report.write_text("Owner intentionally reconciled the report.\n")
                    fixture.git(fixture.state, "add", "--", fixture.report)
                    fixture.git(fixture.state, "commit", "-m", "test: reconcile scope", "--", fixture.report)
                    fixture.build(extra=("--symptom", "owner reconciliation"))
                    fixture.assertTrue(fixture.record(number=4).exists())
                    fixture.assertEqual(fixture.outside_snapshot(), outside)
                    fixture.entity.write_text(fixture.entity.read_text().replace("status: ideation", "status: implementation"))
                    fixture.git(fixture.state, "add", "--", fixture.entity)
                    fixture.git(fixture.state, "commit", "-m", "test: implementation", "--", fixture.entity)
                    fixture.build("implementation")
                    fixture.build("implementation", ("--advance", "--note", "advance-route", "--symptom", "none"))
                    fixture.assert_committed(fixture.record("implementation", 2), f"state: update {fixture.slug}")
                    fixture.assertEqual(fixture.outside_snapshot(), outside)
                finally:
                    fixture.doCleanups()

    def test_committed_then_assembly_failure_keeps_record_for_retry(self):
        failing = self.base / "commit-then-fail"
        failing.write_text(f"#!{sys.executable}\nimport subprocess, sys\n"
                           f"result = subprocess.run([{BINARY!r}, *sys.argv[1:]], capture_output=True, text=True)\n"
                           "sys.stderr.write(result.stderr)\n"
                           "if result.returncode: sys.exit(result.returncode)\n"
                           "print('fixture assembly failed after commit', file=sys.stderr)\nsys.exit(8)\n")
        failing.chmod(0o755)
        held = self.build(extra=("--spacedock", failing), expected=8)
        self.assertEqual(held.stdout, "")
        self.assertIn("fixture assembly failed after commit", held.stderr)
        self.assert_committed(self.record(), f"dispatch: {self.slug} entering ideation")
        content = self.record().read_bytes()
        self.build()
        self.assertEqual(self.record().read_bytes(), content)
        self.assertFalse(self.record(number=2).exists())

    def test_scope_git_failure_is_a_nonmutating_hold(self):
        stage, extra = self.scope_seed()
        bin_dir = self.base / "bin"
        bin_dir.mkdir()
        real_git = shutil.which("git")
        shim = bin_dir / "git"
        shim.write_text(f"#!{sys.executable}\nimport os, sys\n"
                        "if 'ls-tree' in sys.argv: sys.exit(9)\n"
                        f"os.execv({real_git!r}, [{real_git!r}, *sys.argv[1:]])\n")
        shim.chmod(0o755)
        env = {**self.env, "PATH": str(bin_dir) + os.pathsep + self.env["PATH"]}
        self.assert_scope_refusal("scope-git-failure", self.entity, stage, extra, child_env=env)

    def test_inline_scope_uses_the_real_commit_unit(self):
        entity = self.workflow / self.entity.name
        entity.write_bytes(self.entity.read_bytes())
        readme = self.workflow / "README.md"
        readme.write_text(readme.read_text().replace("state: .spacedock-state", "state: $inline"))
        self.git(self.repo, "add", "--", entity, readme)
        self.git(self.repo, "commit", "-m", "test: inline state")
        self.entity, self.state = entity, self.workflow
        self.folder = self.state / self.slug
        self.env["GIT_OPTIONAL_LOCKS"] = "0"
        self.build()
        self.assert_committed(self.record(), f"dispatch: {self.slug} entering ideation")
        dispatched = self.git(self.repo, "rev-parse", "HEAD")
        self.build()
        self.assertIn(f"Dispatched: {dispatched}", self.record(number=2).read_text())
        path = self.scope_dirty(self.entity, "staged-only")
        self.assert_scope_refusal("inline-staged-task", path, "ideation", ())

    def test_symlinked_entity_is_a_nonmutating_hold(self):
        external = self.base / "external-task.md"
        external.write_bytes(self.entity.read_bytes())
        self.extra_roots = [external]
        self.entity.unlink()
        self.entity.symlink_to(external)
        self.assert_scope_refusal("symlinked-task", self.entity, "ideation", ())

    def test_unsupported_companion_and_dangling_target_are_preserved(self):
        for kind in ("companion", "dangling"):
            with self.subTest(kind=kind):
                fixture = type(self)("test_unsupported_companion_and_dangling_target_are_preserved")
                try:
                    fixture.setUp()
                    if kind == "companion":
                        external = fixture.base / "external"
                        external.mkdir()
                        (external / "sentinel.txt").write_text("External content.\n")
                        fixture.folder.symlink_to(external, target_is_directory=True)
                        fixture.extra_roots = [external]
                        path = fixture.folder
                    else:
                        path = fixture.record()
                        path.parent.mkdir(parents=True)
                        ignore = fixture.state / ".gitignore"
                        ignore.write_text(f"/{fixture.slug}/dispatch/ideation-1.md\n")
                        fixture.git(fixture.state, "add", "--", ignore)
                        fixture.git(fixture.state, "commit", "-m", "test: ignored dangling target")
                        path.symlink_to(fixture.base / "absent-external-target")
                    fixture.assert_scope_refusal("unsupported-" + kind, path, "ideation", ())
                finally:
                    fixture.doCleanups()

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
        pending = self.record("implementation", 2).read_bytes()
        refused = self.build("implementation", ("--advance", "--note", "retry", "--symptom", "none"), expected=1)
        self.assertIn(str(self.record("implementation", 2)), refused.stderr)
        self.assertEqual(self.record("implementation", 2).read_bytes(), pending)
        self.call([BINARY, "state", "commit", self.slug, "--workflow-dir", self.workflow])
        self.build("implementation", ("--advance", "--note", "retry", "--symptom", "none"))
        self.assert_committed(self.record("implementation", 2), f"state: update {self.slug}")
        self.assertFalse(self.record("implementation", 3).exists())


if __name__ == "__main__":
    if not BINARY or not shutil.which(BINARY):
        sys.exit("test_dispatch_stage.py: set SPACEDOCK_BIN to the real Spacedock binary")
    unittest.main()
