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

    def delivery_fixture(self, changed=True):
        claim = self.claim()
        result = self.complete(claim, self.result_file([self.decision("add", NEW) if changed else self.decision("no-change")]))
        head = subprocess.check_output(["git", "-C", self.repo, "rev-parse", "HEAD"], text=True).strip()
        plan = {"schema_version": 1, "result_digest": result["digest"], "repository": "example/project",
                "branch": "learning/" + claim["job"], "marker": "<!-- kc-dev-flow-2 learning " + claim["job"] + " -->",
                "base_branch": "main", "base_commit": head, "candidate_commit": head,
                "source_learning_blob": "absent", "candidate_learning_blob": "c" * 40,
                "worktree": str(self.base / "isolated-candidate"), "title": "Synthetic learning proposal"}
        plan["body"] = "Synthetic provider simulation only.\n" + plan["marker"] + "\n"
        self.plan = self.base / "plan.json"
        self.plan.write_text(json.dumps(plan))
        return claim, plan

    def observed(self, plan, state, draft=True):
        value = {key: plan[key] for key in ("repository", "branch", "candidate_commit", "marker")}
        value.update(state=state, pr="example/project#2" if state in ("open", "merged", "closed") else None,
                     merge_commit="d" * 40 if state == "merged" else None,
                     draft=draft if state in ("open", "merged", "closed") else None,
                     evidence=["Synthetic provider response, not real remote evidence"])
        path = self.base / "observation.json"
        path.write_text(json.dumps(value))
        return path

    def deliver(self, claim, code=0):
        return self.cli("delivery-claim", "--job", claim["job"], "--owner", "delivery-owner", "--plan", self.plan, code=code)

    def reconcile(self, claim, plan, state, expected=None, owner_state="stopped", code=0):
        record = self.cli("notices", "--all")["notices"][0]
        return self.cli("delivery-recover", "--job", claim["job"], "--expected", expected or record["delivery"]["digest"],
                        "--owner-state", owner_state, "--reason", "Synthetic owner stopped; provider lookup inspected",
                        "--owner", "new-owner", "--plan", self.plan, "--observation", self.observed(plan, state), code=code)

    def test_notices_no_directory_creation_and_digest_ack(self):
        self.assertEqual(self.cli("notices"), {"notices": []})
        self.assertEqual(self.cli("notices", "--all"), {"notices": []})
        self.assertEqual(self.cli("read", "--job", "a" * 64)["state"], "missing")
        self.assertFalse((self.repo / ".git/kc-dev-flow-2").exists())
        claim = self.claim()
        pending = self.cli("notices")["notices"][0]
        self.assertNotIn("token", json.dumps(pending))
        self.cli("ack", "--job", claim["job"], "--expected", pending["notice_digest"])
        self.assertEqual(self.cli("notices"), {"notices": []})
        self.complete(claim, self.result_file([self.decision("no-change")]))
        self.cli("ack", "--job", claim["job"], "--expected", pending["notice_digest"], code=1)
        done = self.cli("notices")["notices"][0]
        self.assertIsNone(done["proposal"])
        self.cli("ack", "--job", claim["job"], "--expected", done["notice_digest"])
        acknowledgement = self.record_path(claim["job"]).parent / "acknowledgement.json"
        acknowledgement.write_text('{"digest":')
        self.assertTrue(self.cli("notices")["notices"][0]["unread"])
        self.assertEqual(acknowledgement.read_text(), '{"digest":')

    def test_no_change_and_mismatched_plan_cannot_claim_delivery(self):
        claim, plan = self.delivery_fixture(changed=False)
        self.deliver(claim, code=1)
        self.assertFalse((self.record_path(claim["job"]).parent / "delivery.json").exists())
        self.pack["task_id"] = "changed-task"
        self.write_pack()
        claim, plan = self.delivery_fixture()
        for field, value in (("result_digest", "0" * 64), ("branch", "arbitrary"), ("marker", "wrong"), ("base_branch", "bad..branch")):
            self.plan.write_text(json.dumps({**plan, field: value}))
            self.deliver(claim, code=1)
        self.assertFalse((self.record_path(claim["job"]).parent / "delivery.json").exists())

    def test_delivery_claim_race_and_interrupted_remote_response(self):
        claim, plan = self.delivery_fixture()
        result_bytes = self.record_path(claim["job"]).read_bytes()
        commands = self.argv("delivery-claim", "--job", claim["job"], "--owner", "racing-owner", "--plan", self.plan)
        processes = [subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for _ in range(12)]
        values = [json.loads(process.communicate(timeout=20)[0]) for process in processes]
        winners = [value for value in values if value.get("delivery_claimed")]
        self.assertEqual(len(winners), 1, values)
        winner = winners[0]
        # Simulated provider accepted one send; caller died before recording its response.
        remote = self.base / "simulated-provider.json"
        remote.write_text(json.dumps({"pr": "example/project#2", "sends": 1, "candidate": plan["candidate_commit"]}))
        replay = self.deliver(claim)
        self.assertNotIn("delivery_token", replay)
        self.assertEqual(replay["delivery"]["state"], "uncertain")
        self.cli("ack", "--job", claim["job"], "--expected", replay["notice_digest"])
        self.assertEqual(self.cli("notices"), {"notices": []})
        inspectable = self.cli("notices", "--all")["notices"][0]
        self.assertEqual(inspectable["delivery"]["digest"], replay["delivery"]["digest"])
        self.assertNotIn("token", json.dumps(inspectable))
        recovered = self.reconcile(claim, plan, "open")
        self.assertFalse(recovered["delivery_claimed"])
        self.assertEqual(json.loads(remote.read_text())["sends"], 1)
        self.cli("delivery-record", "--job", claim["job"], "--token", winner["delivery_token"],
                 "--observation", self.observed(plan, "open"), code=1)
        self.assertEqual(self.record_path(claim["job"]).read_bytes(), result_bytes)
        self.assertEqual(self.cli("notices")["notices"][0]["delivery"]["state"], "open")

    def test_delivery_recovery_and_observation_boundaries(self):
        claim, plan = self.delivery_fixture()
        sent = self.deliver(claim)
        self.reconcile(claim, plan, "absent", owner_state="running", code=1)
        self.reconcile(claim, plan, "unknown", code=1)
        self.reconcile(claim, plan, "absent", expected="0" * 64, code=1)
        renewed = self.reconcile(claim, plan, "absent")
        self.assertTrue(renewed["delivery_claimed"])
        self.assertNotEqual(sent["delivery_token"], renewed["delivery_token"])
        bad = self.observed(plan, "open")
        value = json.loads(bad.read_text()); value["candidate_commit"] = "f" * 40
        bad.write_text(json.dumps(value))
        self.cli("delivery-record", "--job", claim["job"], "--token", renewed["delivery_token"], "--observation", bad, code=1)
        # A matching existing PR already made ready is an observation, not new creation.
        opened = self.cli("delivery-record", "--job", claim["job"], "--token", renewed["delivery_token"],
                          "--observation", self.observed(plan, "open", draft=False))
        self.assertEqual(opened["delivery"]["state"], "open")
        self.reconcile(claim, plan, "absent", code=1)
        merged = self.cli("delivery-record", "--job", claim["job"], "--token", renewed["delivery_token"],
                         "--observation", self.observed(plan, "merged", draft=False))
        self.cli("ack", "--job", claim["job"], "--expected", opened["notice_digest"], code=1)
        before = (self.record_path(claim["job"]).parent / "delivery.json").read_bytes()
        self.cli("delivery-record", "--job", claim["job"], "--token", renewed["delivery_token"],
                 "--observation", self.observed(plan, "open"), code=1)
        self.reconcile(claim, plan, "closed", code=1)
        self.assertEqual((self.record_path(claim["job"]).parent / "delivery.json").read_bytes(), before)
        self.assertEqual(merged["delivery"]["observation"]["merge_commit"], "d" * 40)

    def test_torn_delivery_is_visible_and_requires_explicit_reconciliation(self):
        claim, plan = self.delivery_fixture()
        self.deliver(claim)
        path = self.record_path(claim["job"]).parent / "delivery.json"
        path.write_bytes(b'{"state":')
        for output in (self.deliver(claim), self.cli("notices")["notices"][0]):
            self.assertEqual(output["delivery"]["state"], "uncertain")
            self.assertNotIn("delivery_token", output)
        self.assertEqual(path.read_bytes(), b'{"state":')
        renewed = self.reconcile(claim, plan, "absent")
        self.assertTrue(renewed["delivery_claimed"])
        archived = list(path.parent.glob("prior-delivery-*.json"))
        self.assertEqual(len(archived), 1)
        self.assertEqual(archived[0].read_bytes(), b'{"state":')


if __name__ == "__main__":
    unittest.main(verbosity=2)
