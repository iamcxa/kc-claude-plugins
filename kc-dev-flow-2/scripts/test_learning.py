#!/usr/bin/env python3
"""Exercise local learning ownership and persistence in disposable Git repositories."""

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name("learning.py")
ENTRY = {"Applicability": "Synthetic import path", "Practice": "Check encoding", "Evidence": "Synthetic case A"}
NEW = {"Applicability": "Synthetic export path", "Practice": "Check header order", "Evidence": "Synthetic case B"}


class LearningTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.repo = self.base / "repo"
        subprocess.run(["git", "init", "-q", "--initial-branch=main", self.repo], check=True)
        subprocess.run(["git", "-C", self.repo, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                        "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null",
                        "commit", "--allow-empty", "-qm", "test: seed disposable repo"], check=True)
        self.pack = {"schema_version": 1, "workflow": "docs/dev2", "task_id": "task-1",
                     "variant": "kc-dev-flow-2", "profile": "pilot", "closed": True,
                     "merged": True, "verdict": "passed", "learning_task": False,
                     "closure_revision": "a" * 40, "landed_revision": "b" * 40,
                     "pr": "example/project#1", "evidence": ["Synthetic primary reference"],
                     "learning": [ENTRY], "project_rules": ["No authority changes"]}
        self.input = self.base / "input.json"
        self.write_pack()

    def write_pack(self):
        self.input.write_text(json.dumps(self.pack))

    def argv(self, *args, repo=None):
        return [sys.executable, str(SCRIPT), "--repo", str(repo or self.repo), *map(str, args)]

    def cli(self, *args, code=0, repo=None):
        result = subprocess.run(self.argv(*args, repo=repo), capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def claim(self):
        return self.cli("claim", "--input", self.input, "--owner", "session-fixture")

    def record_path(self, job):
        return self.repo / ".git/kc-dev-flow-2/learning" / job / "record.json"

    def result_file(self, decisions):
        path = self.base / "evaluation.json"
        path.write_text(json.dumps({"schema_version": 1, "decisions": decisions}))
        return path

    def decision(self, action, item=None):
        return {"action": action, "entry": item, "reason": "Synthetic schema/control input only",
                "evidence": [] if action == "no-change" else ["Synthetic primary reference"]}

    def complete(self, claim, path, code=0):
        return self.cli("complete", "--job", claim["job"], "--token", claim["token"], "--result", path, code=code)

    def recover(self, claim, owner_state="stopped", expected=None, code=0):
        observed = self.cli("read", "--job", claim["job"])
        return self.cli("recover", "--job", claim["job"], "--expected", expected or observed["digest"],
                        "--owner-state", owner_state, "--reason", "Synthetic owner-stop attestation",
                        "--input", self.input, "--owner", "replacement-fixture", code=code)

    def test_three_outcomes_and_mixed_preserve_project_files(self):
        (self.repo / "learning.md").write_text("existing rules\n")
        (self.repo / "AGENTS.md").write_text("existing authority\n")
        for number, actions in enumerate((("add",), ("no-change",), ("remove",), ("remove", "add", "no-change"))):
            with self.subTest(actions=actions):
                self.pack["task_id"] = f"task-{number}"
                self.write_pack()
                claim = self.claim()
                decisions = [self.decision(action, NEW if action == "add" else ENTRY if action == "remove" else None) for action in actions]
                done = self.complete(claim, self.result_file(decisions))
                self.assertEqual(done["state"], "completed")
                self.assertEqual(done["evaluation"]["decisions"], decisions)
                self.assertNotIn("token", done)
                if actions == ("no-change",):
                    self.assertIsNone(done["proposal"])
                else:
                    self.assertEqual(done["proposal"]["add"], [NEW] if "add" in actions else [])
                    self.assertEqual(done["proposal"]["remove"], [ENTRY] if "remove" in actions else [])
                self.assertEqual(self.cli("read", "--job", claim["job"]), done)
        self.assertEqual((self.repo / "learning.md").read_text(), "existing rules\n")
        self.assertEqual((self.repo / "AGENTS.md").read_text(), "existing authority\n")

    def test_linked_worktree_multiprocess_claim_race(self):
        other = self.base / "other"
        subprocess.run(["git", "-C", self.repo, "worktree", "add", "--detach", other], capture_output=True, check=True)
        processes = [subprocess.Popen(self.argv("claim", "--input", self.input, "--owner", f"session-{i}",
                                               repo=other if i % 2 else self.repo), stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE, text=True) for i in range(24)]
        values = [json.loads(process.communicate(timeout=20)[0]) for process in processes]
        winners = [value for value in values if value.get("claimed")]
        self.assertEqual(len(winners), 1, values)
        self.assertEqual(len(list((self.repo / ".git/kc-dev-flow-2/learning").iterdir())), 1)
        done = self.complete(winners[0], self.result_file([self.decision("no-change")]))
        self.assertEqual(self.cli("read", "--job", winners[0]["job"], repo=other), done)
        duplicate = self.claim()
        self.assertEqual(duplicate["state"], "completed")
        self.assertNotIn("token", duplicate)

    def test_ineligible_and_invalid_input_create_no_claim(self):
        original = copy.deepcopy(self.pack)
        for field, value in (("closed", False), ("merged", False), ("verdict", "rejected"),
                             ("learning_task", True), ("profile", "unknown"), ("variant", "other"),
                             ("closure_revision", ""), ("evidence", [])):
            self.pack = {**original, field: value}
            self.write_pack()
            self.assertEqual(self.claim()["state"], "ineligible")
        self.pack = {**original, "closed": "true"}
        self.write_pack()
        self.cli("claim", "--input", self.input, "--owner", "fixture", code=1)
        self.pack = original
        self.write_pack()
        self.cli("claim", "--input", self.input, "--owner", " ", code=1)
        self.assertFalse((self.repo / ".git/kc-dev-flow-2").exists())

    def test_invalid_completion_keeps_token_repairable_and_success_immutable(self):
        claim = self.claim()
        path = self.record_path(claim["job"])
        before = path.read_bytes()
        bad = [self.decision("add", ENTRY), self.decision("remove", NEW), self.decision("no-change", ENTRY),
               {**self.decision("add", NEW), "evidence": ["not supplied in pack"]}]
        for decision in bad:
            self.complete(claim, self.result_file([decision]), code=1)
            self.assertEqual(path.read_bytes(), before)
        result = self.result_file([self.decision("add", NEW)])
        done = self.complete(claim, result)
        completed = path.read_bytes()
        self.complete(claim, result, code=1)
        self.recover(claim, code=1)
        self.assertEqual(path.read_bytes(), completed)
        self.assertEqual(done["state"], "completed")

    def test_interruption_requires_stopped_attestation_and_revokes_token(self):
        claim = self.claim()  # The claiming process has exited; that is not proof its owner stopped.
        seen = self.cli("read", "--job", claim["job"])
        self.assertEqual(seen["state"], "pending")
        self.assertIn("unverified", seen["owner_status"])
        before = self.record_path(claim["job"]).read_bytes()
        for owner in ("running", "unknown"):
            self.recover(claim, owner_state=owner, code=1)
        self.recover(claim, expected="0" * 64, code=1)
        self.assertEqual(self.record_path(claim["job"]).read_bytes(), before)
        replacement = self.recover(claim)
        self.assertNotEqual(replacement["token"], claim["token"])
        result = self.result_file([self.decision("no-change")])
        self.complete(claim, result, code=1)
        self.assertEqual(self.complete(replacement, result)["state"], "completed")
        self.assertEqual(next(self.record_path(claim["job"]).parent.glob("prior-*.json")).read_bytes(), before)

    def test_torn_and_missing_record_are_uncertain_not_automatic_retries(self):
        for raw in (b'{"state":', None):
            self.pack["task_id"] += "x"
            self.write_pack()
            claim = self.claim()
            path = self.record_path(claim["job"])
            if raw is None:
                path.unlink()
            else:
                path.write_bytes(raw)
            self.assertEqual(self.cli("read", "--job", claim["job"])["state"], "uncertain")
            again = self.claim()
            self.assertEqual(again["state"], "uncertain")
            self.assertNotIn("token", again)
            renewed = self.recover(claim)
            self.assertTrue(renewed["claimed"])
            self.complete(claim, self.result_file([self.decision("no-change")]), code=1)

    def test_process_crash_during_publication_preserves_uncertainty_or_prior_record(self):
        crash = ("import importlib.util,os,sys; sys.dont_write_bytecode=True; "
                 "spec=importlib.util.spec_from_file_location('learning',sys.argv[1]); "
                 "m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); "
                 "m.os.replace=lambda *args: os._exit(73); "
                 "sys.argv=sys.argv[1:]; m.main()")
        claim_args = self.argv("claim", "--input", self.input, "--owner", "crashed-owner")[2:]
        result = subprocess.run([sys.executable, "-c", crash, str(SCRIPT), *claim_args], capture_output=True)
        self.assertEqual(result.returncode, 73, result.stderr)
        uncertain = self.claim()
        self.assertEqual(uncertain["state"], "uncertain")
        renewed = self.recover(uncertain)
        path = self.record_path(renewed["job"])
        before = path.read_bytes()
        complete_args = self.argv("complete", "--job", renewed["job"], "--token", renewed["token"],
                                  "--result", self.result_file([self.decision("no-change")]))[2:]
        result = subprocess.run([sys.executable, "-c", crash, str(SCRIPT), *complete_args], capture_output=True)
        self.assertEqual(result.returncode, 73, result.stderr)
        self.assertEqual(path.read_bytes(), before)
        recovered = self.recover(renewed)
        self.assertEqual(self.complete(recovered, self.result_file([self.decision("no-change")]))["state"], "completed")

    def test_foreign_token_evidence_change_and_path_traversal_refused(self):
        claim = self.claim()
        self.pack["evidence"].append("changed supplied facts")
        self.write_pack()
        self.cli("claim", "--input", self.input, "--owner", "fixture", code=1)
        self.recover(claim, code=1)
        wrong = {**claim, "token": "0" * 64}
        self.complete(wrong, self.result_file([self.decision("no-change")]), code=1)
        self.cli("read", "--job", "../../elsewhere", code=1)
        self.assertEqual(self.cli("read", "--job", claim["job"])["state"], "pending")

    def test_concurrent_completion_publishes_one_whole_result(self):
        claim = self.claim()
        result = self.result_file([self.decision("add", NEW)])
        args = self.argv("complete", "--job", claim["job"], "--token", claim["token"], "--result", result)
        processes = [subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for _ in range(8)]
        values = [json.loads(process.communicate(timeout=20)[0]) for process in processes]
        self.assertEqual(sum(value.get("state") == "completed" for value in values), 1, values)
        observed = self.cli("read", "--job", claim["job"])
        self.assertEqual(observed["proposal"], {"add": [NEW], "remove": []})
        self.assertEqual(observed["evaluation"]["decisions"], [self.decision("add", NEW)])


if __name__ == "__main__":
    unittest.main(verbosity=2)
