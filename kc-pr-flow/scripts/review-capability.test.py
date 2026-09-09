#!/usr/bin/env python3
"""Behavioral checks for the default-off profiled review journey."""

import contextlib
import copy
import importlib.util
import inspect
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
import warnings
from unittest.mock import patch

HERE = pathlib.Path(__file__).resolve().parent
def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


protocol = module("capability", HERE / "review-capability.py")


def clean_reply(request):
    return {
        **{k: request[k] for k in ("identity", "plan_rev", "plan_hash", "bundle_revision", "bundle_hash", "capability")},
        "schema": "kc-pr-flow.capability-result/v1", "status": "succeeded",
        "usage": dict(input_tokens=None, output_tokens=None, total_tokens=None),
        "answers": [dict(question_id=q, assessment="clean", contributions=[],
                         evidence_refs=[p["id"] for group in request["evidence"] for p in group["material"]])
                    for q in request["question_ids"]],
    }


def provider_reply(answer):
    return {"structured_output": answer, "modelUsage": {"fixture": {}}, "total_cost_usd": 0.01,
            "usage": dict(input_tokens=10, output_tokens=2, cache_creation_input_tokens=0, cache_read_input_tokens=0)}


def rehash_bundle(prepared):
    bundle = prepared["bundle"]
    bundle["bundle_hash"] = protocol.digest({k: v for k, v in bundle.items() if k != "bundle_hash"})


class PlannerTests(unittest.TestCase):
    @contextlib.contextmanager
    def launcher(self, program=None, enabled="on"):
        with tempfile.TemporaryDirectory() as root:
            root = pathlib.Path(root)
            marker, stub = root / "model-called", root / "claude"
            stub.write_text("#!/usr/bin/env python3\n" + program if program else
                            '#!/bin/sh\ntouch "' + str(marker) + '"\nexit 99\n')
            stub.chmod(0o700)
            environment = {**os.environ, "PATH": str(root) + os.pathsep + os.environ["PATH"],
                           "CLAUDE_PLUGIN_ROOT": str(HERE.parent), "KC_PR_FLOW_REVIEW_TYPED": enabled,
                           "KC_PR_FLOW_PROFILED_REVIEW": enabled, "REVIEW_WORKTREE": str(root),
                           "REVIEW_RUN_DIR": str(root / "run"), "REVIEW_MODEL": "fixture"}
            yield root, environment
            if program is None:
                self.assertFalse(marker.exists(), "this route must not launch the CLI")

    def assert_provider_report(self, prepared, event):
        stem = pathlib.Path(prepared["directory"]) / f"provider-{event['capability']}-{event['attempt']}"
        raw, envelope = stem.with_suffix(".raw").read_text(), protocol.read_json(stem.with_suffix(".json"))
        self.assertEqual(json.loads(raw), envelope)
        request = next(r for r in protocol.requests(prepared) if r["capability"] == event["capability"])
        self.assertEqual(event["payload_sha256"], protocol.digest({"request": request, "provider_envelope": envelope}))
        if event["result"] == "succeeded":
            self.assertEqual(envelope["total_cost_usd"], 0.01)
            self.assertEqual(envelope["usage"]["input_tokens"], 10)
            self.assertEqual(envelope["usage"]["output_tokens"], 2)
        else:
            self.assertEqual(raw, "null\n")
            self.assertIsNone(envelope)

    def collect(self, directory, reply, outcome="succeeded", attempt=1):
        capability = reply["capability"] if isinstance(reply, dict) else reply
        response = {"response_file": protocol.store(directory / f"reply-{capability}-{attempt}.json", reply)} if isinstance(reply, dict) else {}
        run, packet = self.cli(collect_dir=directory, capability=capability, attempt=attempt,
                               attempt_result=outcome, **response)
        self.assertEqual(run.returncode, 0, run.stderr)
        return packet

    def judgment(self, prepared, results, fallbacks=()):
        questions = []
        code_ref = next((p["id"] for p in prepared["bundle"]["pointers"] if "pointer" in p), None)
        for manifest in prepared["plan"]["manifests"]:
            answer = next((r["answers"][0] for r in results if r.get("capability") == manifest["id"] and r.get("answers")), {})
            provided = any(f.get("result", {}).get("capability") == manifest["id"] for f in fallbacks)
            assessment = answer.get("assessment", "clean" if provided else "incomplete_required")
            refs = ([code_ref] if code_ref else []) + [p["id"] for p in prepared["bundle"]["pointers"] if p["evidence_class"] in manifest.get("required_any_evidence", [])]
            if not answer and not provided:
                refs = []
            questions.append({"question_id": manifest["questions"][0], "assessment": assessment,
                              "reason": "The supplied source supports this assessment.", "evidence_refs": refs,
                              "contributions": [{"ordinal": n, "disposition": "accept", "reason": "The cited source supports this claim.", "evidence_refs": refs}
                                                for n, _ in enumerate(answer.get("contributions", []), 1)]})
        return {"schema": "kc-pr-flow.reviewer-judgment/v1", "identity": prepared["identity"],
                "plan_hash": prepared["plan"]["plan_hash"], "bundle_hash": prepared["bundle"]["bundle_hash"],
                "results_hash": protocol.digest(results), "fallbacks_hash": protocol.digest(fallbacks), "questions": questions}

    def collate(self, prepared, results, fallbacks=()):
        return protocol.collate(prepared, results, fallbacks, self.judgment(prepared, results, fallbacks))

    def finish(self, prepared, results, fallbacks=()):
        return protocol.finish(prepared, results, fallbacks, self.judgment(prepared, results, fallbacks))

    def test_missing_goal_cannot_claim_goal_alignment(self):
        with self.prepared_results(goal_kind=None) as (prepared, results):
            self.assertNotIn("goal_alignment", [r["capability"] for r in protocol.requests(prepared)])
            result = self.collate(prepared, results)
            decision = result["protocol_decision"]
            self.assertEqual(["goal_alignment"], decision["gaps"])
            self.assertEqual(decision["event"], "COMMENT")

    def test_goal_material_reaches_selected_request_unchanged(self):
        for kind in ("pr_body", "issue", "review_comment"):
            with self.subTest(kind=kind), self.prepared_results(goal_kind=kind) as (prepared, results):
                request = next(r for r in protocol.requests(prepared) if r["capability"] == "goal_alignment")
                goals = [p for g in request["evidence"] for p in g["material"] if p["evidence_class"] == kind]
                self.assertEqual(goals, prepared["shape_bundle"]["pointers"])
                self.assertEqual(goals[0]["material"], "Set the example value to 2.")
                self.assertEqual(self.collate(prepared, results)["protocol_decision"]["gaps"], [])

    def test_goal_input_and_revision_drift_refuse(self):
        with self.prepared_results() as (prepared, results):
            goal = prepared["shape_bundle"]["pointers"][0]
            original = {k: goal[k] for k in ("identity", "evidence_class", "locator", "material")}
            for text in ("", "  ", original["locator"], "https://example.com/issue/1"):
                self.assertEqual(protocol.freeze_goals([{**original, "material": text}], self.identity), [])
            changed = {**original, "identity": {**self.identity, "head_sha": "a" * 40}}
            self.assertRaises(protocol.Invalid, protocol.freeze_goals, [changed], self.identity)
            request = next(r for r in protocol.requests(prepared) if r["capability"] == "goal_alignment")
            answer = copy.deepcopy(next(r for r in results if r["capability"] == "goal_alignment"))
            answer["answers"][0]["evidence_refs"].remove(goal["id"])
            self.assertRaises(protocol.Invalid, protocol.validate_result, request, answer)
            for mutation in ("content", "identity", "remove"):
                changed = copy.deepcopy(prepared)
                bundle = changed["bundle"]
                target = next(p for p in bundle["pointers"] if p["id"] == goal["id"])
                if mutation == "remove":
                    bundle["pointers"].remove(target)
                    next(b for b in bundle["bindings"] if b["evidence_class"] == "pr_body").update(refs=[], missing="unavailable")
                elif mutation == "content":
                    target["material"] = "A different objective."
                else:
                    target["identity"]["head_sha"] = "a" * 40
                rehash_bundle(changed)
                with self.subTest(mutation=mutation):
                    self.assertRaises(protocol.Invalid, protocol.requests, changed)

    def test_missing_reviewer_judgment_cannot_approve(self):
        with self.prepared_results() as (prepared, results):
            decision = protocol.collate(prepared, results)["protocol_decision"]
            self.assertEqual(decision["event"], "COMMENT")
            self.assertEqual(decision["gaps"], prepared["plan"]["questions"])

    def test_reviewer_gap_and_confirmed_high_reach_existing_confirmation(self):
        with self.prepared_results() as (prepared, results):
            answer = self.contribution(results[0])
            answer["contributions"].append({**answer["contributions"][0], "claim_key": "unresolved-claim"})
            judgment = self.judgment(prepared, results)
            judgment["questions"][0]["assessment"] = "incomplete_required"
            judgment["questions"][0]["contributions"][1]["disposition"] = "unresolved"
            judgment["questions"][0]["contributions"].reverse()
            question = judgment["questions"][1]
            question["assessment"] = "incomplete_required"
            question["reason"] = "The selected material does not resolve this question."
            result = protocol.finish(prepared, results, reviewer=judgment)
            self.assertIn("confirmation_projection", result, result)
            self.assertFalse(result["confirmation_projection"]["approve_eligible"])
            self.assertEqual(result["protocol_decision"]["event"], "REQUEST_CHANGES")
            self.assertEqual(result["protocol_decision"]["gaps"], [q["question_id"] for q in judgment["questions"][:2]])
            self.assertEqual(result["protocol_decision"]["findings"][0]["severity"], "HIGH")
            self.assertTrue(all(o["adapter_attempts"][-1]["result"] == "succeeded" for o in result["policy"]["obligations"]))

    def test_decision_cannot_drop_judgment_or_lower_confirmed_severity(self):
        with self.prepared_results() as (prepared, results):
            self.contribution(results[0])
            decision = self.collate(prepared, results)["protocol_decision"]
            changed = copy.deepcopy(decision)
            changed["reviewer_judgment"] = None
            self.assertRaises(protocol.Invalid, protocol.check_decision, prepared, changed)
            changed = copy.deepcopy(decision)
            changed["findings"][0]["severity"] = "LOW"
            changed["confirmation_input"]["blocker_refs"] = []
            changed["event"] = "APPROVE"
            self.assertRaises(protocol.Invalid, protocol.check_decision, prepared, changed)
            changed = copy.deepcopy(decision)
            changed["findings"] = []
            changed["terminals"][0].update(state="clean", finding_refs=[])
            changed["confirmation_input"]["blocker_refs"] = []
            changed["event"] = "APPROVE"
            self.assertRaises(protocol.Invalid, protocol.check_decision, prepared, changed)

    def test_reviewer_rejection_and_invalid_judgments(self):
        with self.prepared_results() as (prepared, results):
            self.contribution(results[0])
            accepted = self.judgment(prepared, results)
            rejected = copy.deepcopy(accepted)
            rejected["questions"][0]["assessment"] = "clean"
            rejected["questions"][0]["contributions"][0].update(disposition="reject", reason="The cited assignment already sets the required value.")
            decision = protocol.collate(prepared, results, reviewer=rejected)["protocol_decision"]
            self.assertEqual(decision["event"], "APPROVE")
            self.assertEqual(decision["reviewer_input"]["questions"][0]["result"], results[0])
            self.assertEqual(decision["reviewer_judgment"], rejected)
            for field in ("plan_hash", "bundle_hash", "results_hash", "fallbacks_hash"):
                changed = {**accepted, field: "a" * 64}
                self.assertRaises(protocol.Invalid, protocol.collate, prepared, results, (), changed)
            for mutation in ("duplicate", "omitted", "reason", "reference", "unresolved", "severity", "identity"):
                changed = copy.deepcopy(accepted)
                q = changed["questions"][0]
                if mutation == "duplicate":
                    changed["questions"].append(copy.deepcopy(q))
                elif mutation == "omitted":
                    q["contributions"] = []
                elif mutation == "reason":
                    q["contributions"][0]["reason"] = " "
                elif mutation == "reference":
                    q["contributions"][0]["evidence_refs"] = ["a" * 64]
                elif mutation == "unresolved":
                    q["contributions"][0]["disposition"] = "unresolved"
                elif mutation == "severity":
                    q["contributions"][0]["severity"] = "LOW"
                else:
                    changed["identity"]["head_sha"] = "a" * 40
                with self.subTest(mutation=mutation):
                    self.assertRaises(protocol.Invalid, protocol.collate, prepared, results, (), changed)
            missing = copy.deepcopy(accepted)
            missing["questions"].pop()
            self.assertEqual(protocol.collate(prepared, results, reviewer=missing)["protocol_decision"]["gaps"], [accepted["questions"][-1]["question_id"]])

    def test_cli_hands_off_to_reviewer_and_preserves_finalized_bytes(self):
        with self.host_run(native=False) as (directory, pending, _, _environment):
            self.assert_finalization(directory, pending)

    def assert_finalization(self, directory, pending):
        self.assertEqual(pending["pending_finalization"], str(directory))
        packet = protocol.validate(pending["reviewer_request"], "ReviewerRequest")
        event_file = next((directory / "state").rglob("events.jsonl"))
        self.assertEqual(len(event_file.read_text().splitlines()), 1)
        pending_bytes = event_file.read_bytes()
        run, _ = self.cli(finalize_dir=directory)
        self.assertEqual(run.returncode, 2)
        self.assertEqual(event_file.read_bytes(), pending_bytes)
        self.assertFalse((directory / "result.json").exists())
        data = protocol.read_json(directory / "dispatched.json")
        self.assertEqual(data["prepared"]["plan"]["review_config"]["modes"]["pr_archetype"], "bugfix")
        judgment = self.judgment(data["prepared"], data["results"])
        review_file = protocol.store(directory / "reviewer.json", judgment)
        run, final = self.cli(finalize_dir=directory, reviewer_judgment_file=review_file, pr_archetype="refactor")
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertTrue(final["confirmation_projection"]["approve_eligible"])
        self.assertEqual(final["protocol_decision"]["reviewer_input"], packet)
        self.assertEqual(final["protocol_decision"]["reviewer_judgment"], judgment)
        self.assertEqual(final["policy"]["review_config"]["modes"]["pr_archetype"], "bugfix")
        paths = [event_file, directory / "result.json", directory / "audit.json"]
        sealed = [p.read_bytes() for p in paths]
        run, _ = self.cli(finalize_dir=directory, reviewer_judgment_file=review_file)
        self.assertEqual(run.returncode, 2)
        self.assertEqual([p.read_bytes() for p in paths], sealed)

    def test_actual_rehydrate_projection_mismatch_is_terminal(self):
        with self.prepared_results() as (prepared, results):
            private = pathlib.Path(prepared["directory"]) / "boundary-probe"
            (private / "scripts").mkdir(parents=True)
            shutil.copytree(HERE.parent / "schemas", private / "schemas")
            shutil.copy(HERE / "review-capability.py", private / "scripts/review-capability.py")
            wrapper = private / "scripts/review-runtime.sh"
            wrapper.write_text(
                '#!/usr/bin/env bash\nset -o pipefail\nif [ "$1" = rehydrate-interactive ]; then\n'
                + "bash " + str(HERE / "review-runtime.sh")
                + " \"$@\" | jq ' .approve_eligible = (.approve_eligible | not) '\n"
                + "else\nbash " + str(HERE / "review-runtime.sh")
                + ' "$@"\nfi\n'
            )
            probe = module("boundary_probe", private / "scripts/review-capability.py")
            result = probe.finish(prepared, results)
            self.assertEqual(result["reason"], "projection_mismatch")
            protocol.validate(result, "RunTerminal")

    @contextlib.contextmanager
    def host_run(self, native=True, **fixture):
        program = None if native else (inspect.getsource(clean_reply) +
                  "\nimport json,sys\nprint(json.dumps({'structured_output':clean_reply(json.load(sys.stdin))}))\n")
        with self.prepared_results(**fixture) as (prepared, _), self.launcher(program) as (_, environment):
            directory = pathlib.Path(prepared["directory"])
            intake = protocol.store(directory / "intake.json", self.identity)
            goal = prepared["shape_bundle"]["pointers"][0]
            goals = protocol.store(directory / "goals.json", [
                {k: goal[k] for k in ("identity", "evidence_class", "locator", "material")}
            ])
            run_dir = directory / "host-run"
            run, packet = self.cli(environment=environment, identity_file=intake,
                                   repo_worktree=prepared["repository_path"], run_dir=run_dir,
                                   goal_material_file=goals, pr_archetype="bugfix",
                                   **({"prepare_only": True} if native else {"model": "fixture"}))
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(packet["pending_dispatch" if native else "pending_finalization"], str(run_dir))
            replies = []
            expected = protocol.requests(protocol.read_json(run_dir / "host-progress.json")["prepared"]) if native else []
            for entry, original in zip(packet.get("request_files", []), expected):
                view = protocol.read_json(entry["request_file"])
                for group in view["request"]["evidence"]:
                    for material in group["material"]:
                        material["material"] = "".join(view["materials"][material["id"]])
                    for observation in group["test_observations"]:
                        if "diagnostics" in observation:
                            observation["diagnostics"].update({k: "".join(observation["diagnostics"][k]) for k in ("stdout", "stderr")})
                self.assertEqual(view["request"], original)
                self.assertEqual(entry["capability"], original["capability"])
                replies.append(clean_reply(protocol.validate(view["request"], "CapabilityRequest")))
            self.assertEqual(len(replies), len(expected))
            yield run_dir, packet, replies, environment

    def test_host_dispatch_reaches_existing_finalization_without_a_model(self):
        with self.host_run() as (directory, packet, replies, environment):
            self.assertFalse((directory / "dispatched.json").exists())
            for reply in replies:
                raw = b"```json\n" + protocol.canonical(reply) + b"\n```"
                response = protocol.store(directory / f"reply-{reply['capability']}.raw", raw, raw=True)
                run, pending = self.cli(collect_dir=directory, capability=reply["capability"],
                                        attempt=1, attempt_result="succeeded", response_file=response)
                self.assertEqual(run.returncode, 0, run.stderr)
                self.assertEqual(pending["attempt_result"], "succeeded")
                self.assertEqual((directory / f"provider-{reply['capability']}-1.raw").read_bytes(), raw)
            data = protocol.read_json(directory / "dispatched.json")
            self.assertEqual(data["results"], replies)
            self.assertEqual(data["prepared"]["identity"], packet["identity"])
            self.assert_finalization(directory, pending)

    def test_host_collection_retains_invalid_replies_as_failed_attempts(self):
        mutations = ("json", "null", "duplicate", "identity", "answers", "oversized", "expansion", "nonfinite")
        for mutation, wrapped in [(m, w) for m in mutations for w in (False, True)] + [(m, True) for m in ("prose", "multiple", "language")]:
            with self.subTest(mutation=mutation, wrapped=wrapped), self.host_run() as (directory, packet, replies, environment):
                reply = copy.deepcopy(replies[0])
                if mutation == "identity":
                    reply["identity"]["head_sha"] = "a" * 40
                if mutation == "answers":
                    reply["answers"] = []
                if mutation == "expansion":
                    reply = {"schema": "kc-pr-flow.expansion-request/v1"}
                raw = (b"{" if mutation == "json" else b'{"schema":1,"schema":2}' if mutation == "duplicate"
                       else b"null" if mutation == "null"
                       else b" " * 1048577 if mutation == "oversized"
                       else b'{"usage":NaN}' if mutation == "nonfinite" else protocol.canonical(reply))
                if wrapped:
                    raw = b"```json\n" + raw + b"\n```"
                if mutation == "prose":
                    raw += b"\nReasoning outside the result."
                if mutation == "multiple":
                    raw += b"\n" + raw
                if mutation == "language":
                    raw = raw.replace(b"```json", b"```python", 1)
                response = protocol.store(directory / "response.raw", raw, raw=True)
                capability = replies[0]["capability"]
                run, pending = self.cli(environment=environment, collect_dir=directory, capability=capability,
                                        attempt=1, attempt_result="succeeded", response_file=response)
                self.assertEqual(run.returncode, 0, run.stderr)
                self.assertEqual(pending["attempt_result"], "terminal_failure")
                self.assertNotIn(capability, [r["capability"] for r in pending["remaining"]])
                data = protocol.read_json(directory / "host-progress.json")
                self.assertEqual(data["results"], [])
                self.assertEqual(data["prepared"]["attempts"][capability][0]["result"], "terminal_failure")
                self.assertEqual((directory / f"provider-{capability}-1.raw").read_bytes(), raw)
                self.assertEqual(self.collate(data["prepared"], data["results"])["protocol_decision"]["event"], "COMMENT")

    def test_host_collection_rejects_unassigned_repeated_and_misordered_attempts(self):
        with self.host_run() as (directory, packet, replies, environment):
            response = protocol.store(directory / "reply.json", replies[0])
            arguments = dict(collect_dir=directory, capability=replies[0]["capability"], attempt=1,
                             attempt_result="succeeded", response_file=response)
            original = (directory / "host-progress.json").read_bytes()
            for delta in ({"capability": "not-assigned"}, {"attempt": 2}, {"response_file": ""},
                          {"finalize_dir": directory}, {"prepare_only": True}):
                with self.subTest(delta=delta):
                    run, _ = self.cli(**{**arguments, **delta})
                    self.assertEqual(run.returncode, 2)
                    self.assertEqual((directory / "host-progress.json").read_bytes(), original)
                    self.assertEqual(list(directory.glob("provider-*")), [])
            run, _ = self.cli(finalize_dir=directory)
            self.assertEqual(run.returncode, 2)
            run, pending = self.cli(environment={**environment, "KC_PR_FLOW_REVIEW_TYPED": "off",
                                                "KC_PR_FLOW_PROFILED_REVIEW": "off"}, **arguments)
            self.assertEqual(run.returncode, 0, run.stderr)
            sealed = (directory / "host-progress.json").read_bytes()
            run, _ = self.cli(**arguments)
            self.assertEqual(run.returncode, 2)
            self.assertEqual((directory / "host-progress.json").read_bytes(), sealed)

    def test_host_retry_exhaustion_and_unavailable_calls_remain_incomplete(self):
        with self.host_run() as (directory, packet, replies, environment):
            capability = replies[0]["capability"]
            for ordinal in (1, 2):
                pending = self.collect(directory, capability, "transient_failure", ordinal)
                if ordinal == 1:
                    self.assertIn({"capability": capability, "attempt": 2}, pending["remaining"])
                else:
                    self.assertEqual(pending["attempt_result"], "terminal_failure")
                    self.assertNotIn(capability, [r["capability"] for r in pending["remaining"]])
            for reply in replies[1:]:
                pending = self.collect(directory, reply["capability"], "unavailable")
            self.assertEqual(pending["pending_finalization"], str(directory))
            data = protocol.read_json(directory / "dispatched.json")
            decision = self.collate(data["prepared"], data["results"])["protocol_decision"]
            self.assertEqual(decision["event"], "COMMENT")
            self.assertEqual(decision["gaps"], data["prepared"]["plan"]["questions"])
            self.assertEqual(len(data["prepared"]["attempts"][capability]), 2)
            sealed = {p: p.read_bytes() for p in (directory / "host-progress.json", directory / "dispatched.json")}
            run, _ = self.cli(collect_dir=directory, capability=capability, attempt=2, attempt_result="succeeded")
            self.assertEqual(run.returncode, 2)
            self.assertEqual({p: p.read_bytes() for p in sealed}, sealed)

    def test_host_transient_retry_can_recover(self):
        with self.host_run() as (directory, packet, replies, environment):
            self.collect(directory, replies[0]["capability"], "transient_failure")
            self.collect(directory, replies[0], attempt=2)
            data = protocol.read_json(directory / "host-progress.json")
            self.assertEqual(data["results"], replies[:1])
            self.assertEqual([a["result"] for a in data["prepared"]["attempts"][replies[0]["capability"]]],
                             ["transient_failure", "succeeded"])

    def test_host_collection_preserves_bindings_order_and_unknown_usage(self):
        with self.host_run() as (directory, packet, replies, environment):
            progress = directory / "host-progress.json"
            original = progress.read_bytes()
            data = protocol.read_json(progress)
            reply_file = protocol.store(directory / "reply.json", replies[0])
            arguments = dict(collect_dir=directory, capability=replies[0]["capability"], attempt=1,
                             attempt_result="succeeded", response_file=reply_file)
            changed = copy.deepcopy(data)
            changed["prepared"]["directory"] = str(directory.parent)
            progress.write_bytes(protocol.canonical(changed))
            run, _ = self.cli(**arguments)
            self.assertEqual(run.returncode, 2)
            self.assertEqual(list(directory.glob("provider-*")), [])
            changed = copy.deepcopy(data)
            changed["prepared"]["binding"]["plan_hash"] = "f" * 64
            progress.write_bytes(protocol.canonical(changed))
            run, terminal = self.cli(**arguments)
            self.assertEqual(terminal["reason"], "configuration_change")
            self.assertEqual(terminal["identity"], data["prepared"]["identity"])
            progress.write_bytes(original)
            repo = data["prepared"]["repository_path"]
            protocol.git(repo, "checkout", "--detach", self.identity["base_sha"])
            run, terminal = self.cli(**arguments)
            self.assertEqual(terminal["status"], "INVALIDATED")
            self.assertEqual(progress.read_bytes(), original)
            protocol.git(repo, "checkout", "--detach", self.identity["head_sha"])
            for reply in reversed(replies):
                supplied = {**reply, "usage": dict(input_tokens=123, output_tokens=456, total_tokens=579)}
                self.collect(directory, supplied)
                raw = protocol.read_json(directory / f"provider-{reply['capability']}-1.json")
                self.assertEqual(raw["usage"], supplied["usage"])
            collected = protocol.read_json(directory / "dispatched.json")
            self.assertEqual(collected["results"], replies)
            self.assertTrue(all(e["started_ns"] is None and e["finished_ns"] is None
                                for e in collected["prepared"]["audit"] if e["event_type"] == "invoked"))

    def test_host_collection_keeps_expansion_requests_unsupported(self):
        with self.host_run() as (directory, packet, replies, environment):
            expansion = {"schema": "kc-pr-flow.expansion-request/v1", "cause": "Need more evidence.",
                         "question_ids": [], "evidence_classes": [], "reserve_charge": 1}
            response = protocol.store(directory / "expansion.json", expansion)
            run, _ = self.cli(collect_dir=directory, capability=replies[0]["capability"], attempt=1,
                              attempt_result="succeeded", response_file=response)
            self.assertEqual(run.returncode, 0, run.stderr)
            data = protocol.read_json(directory / "host-progress.json")
            self.assertEqual(self.collate(data["prepared"], data["results"])["reason"], "unsupported_expansion")

    def test_host_exports_existing_result_schema_without_unrelated_contracts(self):
        with self.host_run() as (directory, packet, replies, environment):
            schema = protocol.read_json(packet["result_schema_file"])
            self.assertEqual(schema["$ref"], "#/$defs/CapabilityResult")
            self.assertLess(len(schema["$defs"]), len(protocol.SCHEMA["$defs"]))
            for name, definition in schema["$defs"].items():
                self.assertEqual(definition, protocol.SCHEMA["$defs"][name])
            pending = [schema]
            while pending:
                value = pending.pop()
                if isinstance(value, dict):
                    if "$ref" in value:
                        self.assertIn(value["$ref"].split("/")[-1], schema["$defs"])
                    pending.extend(value.values())
                elif isinstance(value, list):
                    pending.extend(value)

    def test_host_files_are_lossless_bounded_and_not_inline(self):
        content = "value = 2\n# " + '\\"雪😀' * 7000 + "\n"
        with self.host_run(head_content=content) as (directory, packet, replies, environment):
            self.assertNotIn("requests", packet)
            self.assertNotIn("result_schema", packet)
            self.assertLess(len(protocol.canonical(packet)), 8192)
            self.assertEqual(packet["timeout_seconds"], 120)
            for path in [packet["result_schema_file"], *(p["request_file"] for p in packet["request_files"])]:
                path = pathlib.Path(path)
                self.assertEqual(path.parent, directory)
                self.assertEqual(path.stat().st_mode & 0o777, 0o600)
                self.assertLessEqual(max(map(len, path.read_bytes().splitlines())), 2048)
            self.collect(directory, replies[0])

    def test_host_refuses_missing_changed_cross_assignment_and_symlink_inputs(self):
        with self.host_run() as (directory, packet, replies, environment):
            paths = [pathlib.Path(packet["result_schema_file"]), pathlib.Path(packet["request_files"][0]["request_file"])]
            other = pathlib.Path(packet["request_files"][1]["request_file"])
            for path in paths:
                original = path.read_bytes()
                for mutation in (None, b"{}\n", other.read_bytes(), "symlink"):
                    with self.subTest(path=path.name, mutation=str(mutation)[:20]):
                        path.unlink()
                        if mutation == "symlink":
                            path.symlink_to(other)
                        elif mutation is not None:
                            path.write_bytes(mutation)
                        run, refused = self.cli(collect_dir=directory, capability=replies[0]["capability"],
                                                 attempt=1, attempt_result="unavailable")
                        self.assertNotEqual(run.returncode, 0)
                        self.assertEqual(refused["status"], "REQUEST_INVALID")
                        self.assertFalse((directory / "dispatched.json").exists())
                        if path.exists():
                            path.unlink()
                        path.write_bytes(original)
            self.collect(directory, replies[0])

    def test_native_skill_supplies_files_and_collects_read_only_workers(self):
        text = (HERE.parent / "skills/kc-pr-review/SKILL.md").read_text()
        profiled = text.split("### Default-off profiled Lite route", 1)[1].split("Accept PR number", 1)[0]
        for required in ("--prepare-only", "request_files", "result_schema_file", "kc-pr-flow:review-capability-worker",
                         "--collect-dir", "--attempt-result", "--response-file", "cancel"):
            self.assertIn(required, profiled)
        worker = (HERE.parent / "agents/review-capability-worker.md").read_text()
        frontmatter = worker.split("---", 2)[1].splitlines()
        self.assertIn("tools: Read", frontmatter)
        self.assertIn("model: inherit", frontmatter)
        for required in ("request_file", "result_schema_file", "materials", "without a separator", "not single-file isolation"):
            self.assertIn(required, worker)
        self.assertIn("CLAUDE.md", worker)
        self.assertIn("return JSON `null`", worker)
        self.assertIn("`incomplete_required` is not an allowed capability assessment", worker)

    def test_document_tables_are_generated_from_their_authorities(self):
        document = (HERE.parents[1] / "docs/superpowers/specs/2026-09-05-kc-pr-review-capability-protocol-v1.md").read_text()
        for table in protocol.contract_tables():
            self.assertIn(table, document)
            self.assertNotIn(table, document.replace(table.splitlines()[2], "| deliberately wrong |", 1))

    def test_sampled_skill_command_stays_off_and_tokens_are_closed(self):
        skill = (HERE.parent / "skills/kc-pr-review/SKILL.md").read_text()
        profiled = skill.split("### Default-off profiled Lite route", 1)[1].split("Accept PR number", 1)[0]
        for contract in ("--goal-material-file", "ReviewerRequest", "ReviewerJudgment", "--reviewer-judgment-file"):
            self.assertIn(contract, profiled)
        self.assertIn('--pr-archetype "$REVIEW_PR_ARCHETYPE"', profiled)
        self.assertIn("Step 4d", profiled)
        command = skill.split("For the profiled route, call the repository-owned adapter once:", 1)[1]
        command = command.split("```bash\n", 1)[1].split("```", 1)[0]
        with self.launcher(enabled="off") as (root, environment):
            result = subprocess.run(
                ["bash", "-c", command], check=False, cwd=root,
                capture_output=True, text=True, env=environment,
            )
            self.assertEqual(json.loads(result.stdout)["route"], "legacy")
        self.assertRaises(protocol.Invalid, protocol.validate, "abc\n", "Token")

    def test_unsupported_material_is_missing_not_invalid_caller_schema(self):
        for content in (b"value = '\xe9'\n", b"x" * 1048577 + b"\n"):
            with self.subTest(size=len(content)), self.prepared_results() as (prepared, _):
                repo = prepared["repository_path"]
                (pathlib.Path(repo) / "example.py").write_bytes(content)
                protocol.git(repo, "commit", "-qam", "unsupported material")
                identity = {**self.identity, "head_sha": protocol.git(repo, "rev-parse", "HEAD").decode().strip()}
                result = protocol.prepare(
                    repo, identity, pathlib.Path(prepared["directory"]).with_name("unsupported"), "lite",
                )
                binding = next(b for b in result["bundle"]["bindings"] if b["evidence_class"] == "diff_hunks")
                self.assertEqual(binding, {"evidence_class": "diff_hunks", "refs": [], "missing": "unsupported"})
                self.assertEqual(protocol.requests(result), [])
                self.assertEqual(protocol.finish(result, [])["reason"], "receipt_incomplete")

    def cli(self, environment=None, **options):
        arguments = [
            part for key, value in options.items()
            for part in (("--" + key.replace("_", "-"),) if value is True
                         else ("--" + key.replace("_", "-"), str(value)))
        ]
        run = subprocess.run(
            [sys.executable, str(HERE / "review-capability.py"), *arguments],
            env=environment if environment is not None else {**os.environ, "KC_PR_FLOW_REVIEW_TYPED": "on",
                 "KC_PR_FLOW_PROFILED_REVIEW": "on"},
            capture_output=True, text=True, check=False,
        )
        self.assertNotIn("Traceback", run.stderr)
        self.assertTrue(run.stdout, run.stderr)
        return run, json.loads(run.stdout)

    def test_malformed_cli_artifacts_always_return_valid_terminals(self):
        with self.prepared_results() as (prepared, results):
            directory = pathlib.Path(prepared["directory"])
            intake = protocol.store(directory / "invalid-intake.json", {**self.identity, "repository": "x" * 257})
            fallback = protocol.store(directory / "fallback.json", [None])
            cases = [
                (dict(identity_file=intake, repo_worktree=prepared["repository_path"],
                      run_dir=directory / "new", model="unused"), {}, None),
                (dict(finalize_dir=directory), {}, None),
                (dict(finalize_dir=directory, fallbacks_file=fallback),
                 {"prepared": prepared, "results": results}, prepared["identity"]),
            ]
            for arguments, dispatched, expected_identity in cases:
                with self.subTest(arguments=arguments):
                    (directory / "dispatched.json").write_bytes(protocol.canonical(dispatched))
                    run, terminal = self.cli(**arguments)
                    self.assertEqual(run.returncode, 2)
                    protocol.validate(terminal, "RunTerminal")
                    self.assertEqual((terminal["status"], terminal["reason"]), ("REQUEST_INVALID", "schema_failure"))
                    if expected_identity:
                        self.assertEqual(terminal["identity"], expected_identity)

    def test_closed_protocol_fixtures(self):
        fixtures = """\
{"name":"valid evidence absence","definition":"EvidenceClassBinding","valid":true,"value":{"evidence_class":"diff_hunks","refs":[],"missing":"unavailable"}}
{"name":"unknown evidence class","definition":"EvidenceClassBinding","valid":false,"value":{"evidence_class":"model_memory","refs":[],"missing":"unavailable"}}
{"name":"unknown evidence member","definition":"EvidenceClassBinding","valid":false,"value":{"evidence_class":"diff_hunks","refs":[],"missing":"unavailable","waived":true}}
{"name":"invalid boolean attempt","definition":"Positive","valid":false,"value":true}
{"name":"invalid uppercase hash","definition":"Hash","valid":false,"value":"AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"}
{"name":"valid bounded integer","definition":"Positive","valid":true,"value":1}
"""
        for line in fixtures.splitlines():
            fixture = protocol.json.loads(line, object_pairs_hook=protocol.unique_object)
            with self.subTest(fixture=fixture["name"]):
                if fixture["valid"]:
                    protocol.validate(fixture["value"], fixture["definition"])
                else:
                    self.assertRaises(protocol.Invalid, protocol.validate, fixture["value"], fixture["definition"])


    def posting_log(self, prepared, payloads):
        identity = prepared["identity"]
        start = protocol.runtime(
            prepared, "start", "--repo", identity["repository"],
            "--pr", identity["pr_number"], "--base", identity["base_sha"],
            "--head", identity["head_sha"], "--config-hash", identity["config_hash"],
        )
        identity = {**identity, "run_id": start["run_id"]}
        arguments = [identity[k] for k in (
            "run_id", "review_key", "repository", "pr_number",
            "base_sha", "head_sha", "config_hash",
        )]
        events = [protocol.canonical(start).decode()]
        for kind, payload in payloads:
            events.append(subprocess.check_output(
                ["bash", "-c", '. "$1"; shift; review_runtime_build_event "$@"',
                 "fixture", str(HERE / "review-runtime.sh"), *map(str, arguments),
                 str(len(events) + 1), start["occurred_at"], kind,
                 protocol.canonical(payload).decode()], text=True,
            ).strip())
        path = pathlib.Path(prepared["directory"]) / "posting-fixture.jsonl"
        path.write_text("\n".join(events) + "\n")
        return path, start

    def contribution(self, result, **changes):
        answer = result["answers"][0]
        answer.update(assessment="findings", contributions=[{
            "evidence_ref": answer["evidence_refs"][0], "category": "correctness",
            "claim_key": "wrong-value", "severity": "HIGH", "confidence": 9,
            "quote": "value = 2", "summary": "The value violates the contract.",
            **changes,
        }])
        return answer

    def fallback(self, prepared, capability):
        return {"schema": "kc-pr-flow.manual-fallback/v1",
                "bundle_hash": prepared["bundle"]["bundle_hash"], "human_note": "",
                "result": {"schema": "kc-pr-flow.manual-capability-result/v1", "capability": capability,
                           "review_identity": prepared["identity"], "terminal_assessment": "clean",
                           "candidate_ids": [], "evidence": [prepared["bundle"]["pointers"][0]["pointer"]],
                           "recorded_by": "interactive-human", "recorded_at": "2026-09-05T00:00:00Z"}}

    def setUp(self):
        self.identity = {"schema": "kc-pr-flow.intake-identity/v1", "repository": "acme/widgets",
                         "pr_number": 42, "base_sha": "a" * 40, "head_sha": "b" * 40, "intake_id": "intake-test"}
        self.request = {"schema": "kc-pr-flow.planner-input/v1", "identity": self.identity,
                        "protocol_major": 1, "requested": "auto", "full_pass": False,
                        "shape": [{"path": "src/example.py", "added": 4, "deleted": 2, "binary": False}],
                        "test_commands": [], "concerns": []}

    def test_plan_is_deterministic_and_preserves_required_coverage(self):
        plan = protocol.plan(self.request)
        self.assertEqual(plan, protocol.plan(copy.deepcopy(self.request)))
        self.assertEqual(plan["profile"], "lite")
        self.assertEqual(plan["expansion_reserve"], 0)
        self.assertIn("code_correctness", plan["questions"])
        self.assertIn("test_evidence", plan["questions"])
        self.assertEqual(
            protocol.plan({**self.request, "protocol_major": 2})["reason"],
            "unsupported_major",
        )

    def test_plan_preserves_archetype_without_waiving_questions(self):
        baseline = protocol.plan(self.request)
        self.assertEqual(baseline["review_config"]["modes"]["pr_archetype"], "mixed")
        hashes = set()
        for archetype in ("mixed", "bugfix", "feature", "refactor", "docs", "style", "cross_stack"):
            with self.subTest(archetype=archetype):
                planned = protocol.plan({**self.request, "pr_archetype": archetype})
                self.assertEqual(planned["review_config"]["modes"]["pr_archetype"], archetype)
                self.assertEqual(planned["questions"], baseline["questions"])
                self.assertEqual(planned["manifests"], baseline["manifests"])
                runtime_hash = subprocess.check_output([
                    "bash", str(HERE / "review-runtime.sh"), "config-hash", "--pr-archetype", archetype,
                    "--capabilities", ",".join(planned["review_config"]["capabilities"])], text=True).strip()
                self.assertEqual(runtime_hash, protocol.digest(planned["review_config"]))
                hashes.add(planned["plan_hash"])
        self.assertEqual(len(hashes), 7)

    def test_archetype_binds_runtime_requests_and_rejects_drift(self):
        with self.prepared_results(pr_archetype="feature") as (prepared, _):
            config = prepared["plan"]["review_config"]
            self.assertEqual(config["modes"]["pr_archetype"], "feature")
            self.assertEqual(prepared["identity"]["config_hash"], protocol.digest(config))
            self.assertTrue(protocol.requests(prepared))
            changed = copy.deepcopy(prepared)
            changed["plan"]["review_config"]["modes"]["pr_archetype"] = "refactor"
            changed["plan"]["plan_hash"] = protocol.digest({k: v for k, v in changed["plan"].items() if k != "plan_hash"})
            changed["binding"]["plan_hash"] = changed["plan"]["plan_hash"]
            self.assertRaises(protocol.ConfigurationChanged, protocol.requests, changed)

    def test_archetype_contract_remains_closed_and_respects_full_pass(self):
        for value in ("", "fix", "cross-stack", "BUGFIX", None, 0, []):
            with self.subTest(value=value):
                self.assertRaises(protocol.Invalid, protocol.plan, {**self.request, "pr_archetype": value})
        config = protocol.plan({**self.request, "pr_archetype": "refactor"})["review_config"]
        for field in config["modes"]:
            changed = copy.deepcopy(config)
            del changed["modes"][field]
            self.assertRaises(protocol.Invalid, protocol.validate, changed, "ReviewConfig")
        for field, value in (("agent_tier", "standard"), ("full_pass", True), ("probe_required", True),
                             ("cross_model", True), ("noise_filter", True), ("extra", False)):
            changed = copy.deepcopy(config)
            changed["modes"][field] = value
            self.assertRaises(protocol.Invalid, protocol.validate, changed, "ReviewConfig")
        self.assertEqual(protocol.plan({**self.request, "pr_archetype": "refactor", "full_pass": True})["route"], "legacy")
        with tempfile.TemporaryDirectory() as temporary:
            identity = protocol.store(pathlib.Path(temporary) / "intake.json", self.identity)
            run_dir = pathlib.Path(temporary) / "run"
            run, terminal = self.cli(identity_file=identity, repo_worktree=temporary, run_dir=run_dir,
                                     model="fixture", pr_archetype="unknown")
            self.assertEqual(run.returncode, 2)
            self.assertEqual(terminal["reason"], "schema_failure")
            self.assertIn("schema enum mismatch", run.stderr)
            self.assertFalse(run_dir.exists())

    def test_terminal_matrix_and_invalid_intake_echo_are_closed(self):
        review = {key: value for key, value in self.identity.items() if key not in ("schema", "intake_id")}
        review.update(run_id="run-test", config_hash="c" * 64, review_key="d" * 64)
        pairs = {
            "REQUEST_INVALID": ["schema_failure", "unsupported_major", "invalid_identity"],
            "NEEDS_CLARIFICATION": ["missing_intent"],
            "ABORTED_STALE": ["stale_head"],
            "INVALIDATED": ["identity_change", "configuration_change"],
            "ABORTED_INCOMPLETE": ["required_gap", "contradiction", "unsupported_expansion",
                                   "receipt_incomplete", "projection_mismatch"],
        }
        for status, reasons in pairs.items():
            identity = review if status in ("INVALIDATED", "ABORTED_INCOMPLETE") else self.identity
            for reason in reasons:
                with self.subTest(status=status, reason=reason):
                    value = protocol.terminal(identity, status, reason)
                    protocol.validate(value, "RunTerminal")
                    for other_status in pairs.keys() - {status}:
                        self.assertRaises(protocol.Invalid, protocol.validate,
                                          {**value, "status": other_status}, "RunTerminal")
        for reason in ("schema_failure", "invalid_identity", "unsupported_major"):
            with self.subTest(invalid_intake=reason):
                expected = self.assertRaises(protocol.Invalid) if reason == "unsupported_major" else contextlib.nullcontext()
                with expected:
                    value = protocol.terminal({"pr_number": "bad"}, "REQUEST_INVALID", reason)
                    protocol.validate(value, "RunTerminal")

    @contextlib.contextmanager
    def prepared_results(self, commands=(), head_content="value = 2\n", goal_kind="pr_body", **prepare_options):
        with tempfile.TemporaryDirectory() as temporary:
            repo = pathlib.Path(temporary) / "repo"
            repo.mkdir()

            def git(*args):
                return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()

            git("init", "-q")
            git("config", "user.name", "Fixture")
            git("config", "user.email", "fixture@example.invalid")
            git("remote", "add", "origin", "https://github.com/acme/widgets.git")
            (repo / "example.py").write_text("value = 1\n")
            git("add", "example.py")
            git("commit", "-qm", "base")
            self.identity["base_sha"] = git("rev-parse", "HEAD")
            (repo / "example.py").write_text(head_content)
            git("commit", "-qam", "head")
            self.identity["head_sha"] = git("rev-parse", "HEAD")
            goals = [{"identity": dict(self.identity), "evidence_class": goal_kind,
                      "locator": "https://github.com/acme/widgets/pull/42",
                      "material": "Set the example value to 2."}] if goal_kind else []
            prepared = protocol.prepare(
                repo, self.identity, pathlib.Path(temporary) / "run", test_commands=commands,
                **({"goal_material": goals} if goal_kind else {}), **prepare_options,
            )
            self.assertFalse(any("pointer" in p for p in prepared["shape_bundle"]["pointers"]))
            self.assertNotEqual(prepared["bundle"]["identity"]["run_id"], self.identity["intake_id"])
            self.assertEqual(prepared["bundle"]["parent_hash"], prepared["shape_bundle"]["bundle_hash"])
            requests = protocol.requests(prepared)
            results = [clean_reply(request) for request in requests]
            yield prepared, results

    def test_selected_evidence_binds_the_runtime_identity_and_rehydrates(self):
        with self.prepared_results() as (prepared, results):
            requests = protocol.requests(prepared)
            program = ("assert __import__('sys').argv[1] == '--max-budget-usd'; "
                "assert 0 < float(__import__('sys').argv[2]) <= 0.5; "
                "import json,sys\n" + inspect.getsource(clean_reply) + inspect.getsource(provider_reply)
                + "print(json.dumps(provider_reply(clean_reply(json.load(sys.stdin)))))")
            results = protocol.dispatch(prepared, [sys.executable, "-c", program], 6)
            self.assertEqual(len(results), len(requests))
            for event in prepared["audit"][1:]:
                self.assert_provider_report(prepared, event)
            finished = self.finish(prepared, results)
            self.assertEqual(finished["decision"]["coverage"], "complete")
            self.assertTrue(finished["decision"]["approve_eligible"])
            directory = pathlib.Path(prepared["directory"])
            event_file = next((directory / "state").rglob("events.jsonl"))
            identity = prepared["identity"]
            payload_hash = "f" * 64
            idempotency = protocol.raw_hash(f"{identity['review_key']}|{identity['head_sha']}|{payload_hash}".encode())
            posting_binding = {"commit_id": identity["head_sha"], "payload_sha256": payload_hash,
                               "idempotency_key": idempotency}
            payloads = (
                ("head.observed", {"head_sha": identity["head_sha"]}),
                ("authorization.granted", {**posting_binding, "event": "APPROVE"}),
                ("post.intent", posting_binding),
                ("post.result", {"idempotency_key": idempotency, "outcome": "posted_reconciled", "remote_review_id": 42}),
            )
            projected_file, posting_start = self.posting_log(prepared, payloads)
            projected = protocol.posting_projection(prepared, projected_file)
            self.assertEqual(projected["outcome"], "posted_reconciled")
            self.assertEqual(projected["remote_review_id"], 42)
            self.assertEqual(projected["run_id"], posting_start["run_id"])
            self.assertNotEqual(projected["run_id"], prepared["identity"]["run_id"])
            self.assertEqual(event_file.read_text().count("post.result"), 0)
            print("Mechanical runtime timing (ns):", finished["mechanical_timing_ns"], flush=True)

    def test_cross_capability_high_finding_merges_and_forces_request_changes(self):
        with self.prepared_results() as (prepared, results):
            for result, severity in zip(results[:2], ("HIGH", "MEDIUM")):
                self.contribution(result, severity=severity)
            rendered = self.collate(prepared, results)["rendered"]
            self.assertEqual(len(rendered["inline_comments"]), 1)
            inline = rendered["inline_comments"][0]
            self.assertEqual(
                (inline["path"], inline["line"], inline["side"]),
                ("example.py", 1, "RIGHT"),
            )
            self.assertIn("value = 2", inline["body"])
            self.assertIn("example.py:1", rendered["body"])
            finished = self.finish(prepared, results)
            self.assertIn("decision", finished, finished)
            decision = finished["decision"]
            self.assertEqual(decision["effective_event"], "REQUEST_CHANGES")
            self.assertFalse(decision["approve_eligible"])
            self.assertEqual(len(decision["confirmed_blocker_refs"]), 1)
            self.assertEqual(finished["receipt"]["counts"]["findings"], 1)
            self.assertEqual(finished["receipt"]["counts"]["candidates"], 2)

    def test_ambiguous_inline_retains_finding_without_guessing_a_line(self):
        with self.prepared_results(head_content="value = 2\nvalue = 2\n") as (prepared, results):
            self.contribution(results[0])
            rendered = self.collate(prepared, results)["rendered"]
            self.assertEqual(rendered["inline_comments"], [])
            self.assertEqual(rendered["event"], "REQUEST_CHANGES")
            self.assertIn("value = 2", rendered["body"])
            self.assertIn("ambiguous location", rendered["body"])

    def test_transient_adapter_retry_is_bounded_and_timed(self):
        with self.prepared_results() as (prepared, _results):
            command = ["/bin/sh", "-c", "exit 75"]
            returned = protocol.dispatch(prepared, command)
            self.assertEqual(returned, [])
            for attempts in prepared["attempts"].values():
                self.assertEqual([a["result"] for a in attempts], ["transient_failure", "terminal_failure"])
            invocations = [e for e in prepared["audit"] if e["event_type"] == "invoked"]
            self.assertEqual(len(invocations), 2 * len(protocol.requests(prepared)))
            self.assertTrue(all(e["finished_ns"] >= e["started_ns"] > 0 and e["evidence_payload_bytes"] > 0
                                for e in invocations))
            collated = self.collate(prepared, returned)
            self.assertTrue(all(len(o["adapter_attempts"]) == 2 for o in collated["policy"]["obligations"]))
            self.assertEqual(len(collated["observation"]["lanes"]), len(invocations))

    def test_provider_shapes_and_large_monotonic_readings_keep_attempts(self):
        for raw in ('{"structured_output":null}', '{"total_cost_usd":NaN}'):
            with self.subTest(raw=raw), self.prepared_results() as (prepared, _):
                returned = protocol.dispatch(prepared, [sys.executable, "-c", "print(" + repr(raw) + ")"])
                self.assertEqual(returned, [])
                events = [e for e in prepared["audit"] if e["event_type"] == "invoked"]
                self.assertEqual(len(events), len(protocol.requests(prepared)))
                self.assertTrue(all(e["result"] == "terminal_failure" for e in events))
                for path in pathlib.Path(prepared["directory"]).glob("provider-*.raw"):
                    self.assertEqual(path.read_text(), raw + "\n")
                self.assertEqual(len(list(pathlib.Path(prepared["directory"]).glob("provider-*.raw"))), len(events))
        with self.prepared_results() as (prepared, _):
            for ns in (100, 2**53, 2**63):
                protocol.audit(prepared, "accepted", {}, ns, ns + 1)
                self.assertEqual(prepared["audit"][-1]["started_ns"], ns)
            for ns in (True, 0, -1):
                self.assertRaises(protocol.Invalid, protocol.audit, prepared, "accepted", {}, ns, ns)

    def test_configuration_mismatch_is_invalidated_at_collation(self):
        with self.prepared_results() as (prepared, results):
            prepared["binding"]["plan_hash"] = "f" * 64
            terminal = self.collate(prepared, results)
            self.assertEqual((terminal["status"], terminal["reason"]),
                             ("INVALIDATED", "configuration_change"))
            self.assertEqual(terminal["identity"], prepared["identity"])

    def test_terminal_attempt_keeps_identity_without_sealing_the_receipt(self):
        with self.prepared_results() as (prepared, _):
            protocol.dispatch(prepared, [sys.executable, "-c", "print('null')"])
            repo, directory = prepared["repository_path"], pathlib.Path(prepared["directory"])
            event_file = next((directory / "state").rglob("events.jsonl"))
            before = event_file.read_bytes()
            protocol.git(repo, "checkout", "--detach", self.identity["base_sha"])
            terminal = self.collate(prepared, [])
            protocol.git(repo, "checkout", "--detach", self.identity["head_sha"])
            protocol.validate(terminal, "RunTerminal")
            self.assertEqual(terminal["reason"], "identity_change")
            self.assertEqual(terminal["identity"], prepared["identity"])
            self.assertNotIn("decision", terminal)
            self.assertEqual(event_file.read_bytes(), before)

    def test_selected_material_tampering_and_unassigned_answers_refuse(self):
        with self.prepared_results() as (prepared, results):
            self.assertIn("related_source", {p["evidence_class"] for p in prepared["bundle"]["pointers"]})
            changed = copy.deepcopy(prepared)
            changed["bundle"]["pointers"][0]["material"] = "invented evidence"
            rehash_bundle(changed)
            self.assertRaises(protocol.Invalid, protocol.requests, changed)
            results[0]["answers"][0]["question_id"] = "not_assigned"
            self.assertEqual(self.collate(prepared, results)["rendered"]["event"], "COMMENT")
            results[0]["capability"] = "not_selected"
            self.assertEqual(self.collate(prepared, results)["reason"], "schema_failure")

    def test_question_decision_and_confirmation_are_derived_not_model_supplied(self):
        with self.prepared_results() as (prepared, results):
            collated = self.collate(prepared, results)
            decision = collated["protocol_decision"]
            protocol.validate(decision, "ReviewDecision")
            self.assertEqual(
                sorted(t["question_id"] for t in decision["terminals"]),
                prepared["plan"]["questions"],
            )
            for reason in ("required_gap", "contradiction"):
                changed = copy.deepcopy(decision)
                if reason == "required_gap":
                    changed["terminals"].pop()
                else:
                    changed["terminals"][0]["state"] = "contradictory_required"
                self.assertEqual(protocol.check_decision(prepared, changed)["reason"], reason)

    def test_default_off_flags_and_unsupported_profiles_do_not_dispatch(self):
        for typed, profiled in ((None, None), ("on", None), (None, "on"), ("ON", "on"), ("on", "true"), ("on", "on")):
            with self.subTest(typed=typed, profiled=profiled):
                environment = {"KC_PR_FLOW_REVIEW_TYPED": typed, "KC_PR_FLOW_PROFILED_REVIEW": profiled}
                self.assertEqual(protocol.enabled(environment), (typed, profiled) == ("on", "on"))
        for profile in ("standard", "full", "custom"):
            routed = protocol.plan({**self.request, "requested": profile})
            self.assertEqual(
                routed["route"], "unavailable" if profile == "custom" else "legacy"
            )

    def test_manual_fallback_and_failed_capability_rehydrate_real_incomplete_receipt(self):
        started = time.monotonic()
        with self.prepared_results() as (prepared, results):
            print("Mechanical prepare seconds:", time.monotonic() - started, flush=True)
            capability = results[0]["capability"]
            fallback = self.fallback(prepared, results[0]["capability"])
            results[0]["unexpected"] = True
            ordinary = self.collate(prepared, results)
            self.assertEqual(ordinary["rendered"]["event"], "COMMENT")
            collated = self.collate(prepared, results, [fallback])
            obligation = next(o for o in collated["policy"]["obligations"] if o["capability"] == capability)
            self.assertEqual(obligation["terminal_state"], "clean")
            self.assertEqual(obligation["fallback"]["status"], "provided")
            self.assertEqual(obligation["adapter_attempts"][-1]["result"], "terminal_failure")
            for field, value in (("bundle_hash", "f" * 64), ("terminal_assessment", "findings")):
                mutated = copy.deepcopy(fallback)
                (mutated if field == "bundle_hash" else mutated["result"])[field] = value
                refused = self.collate(prepared, results, [mutated])
                self.assertEqual(refused["rendered"]["event"], "COMMENT")
            del results[0]["unexpected"]
            results[0]["unknown"] = True
            missing_capability = results.pop()["capability"]
            directory = pathlib.Path(prepared["directory"])
            protocol.store(directory / "dispatched.json", {"prepared": prepared, "results": results})
            fallback_file = protocol.store(directory / "fallbacks.json", [fallback])
            reviewer_file = protocol.store(directory / "reviewer.json", self.judgment(prepared, results, [fallback]))
            run, refreshed = self.cli(finalize_dir=directory, defer_confirmation=True, fallbacks_file=fallback_file)
            self.assertEqual(run.returncode, 0)
            self.assertEqual(refreshed["reviewer_request"]["fallbacks_hash"], protocol.digest([fallback]))
            run, finished = self.cli(
                environment=os.environ, finalize_dir=directory, fallbacks_file=fallback_file,
                reviewer_judgment_file=reviewer_file,
            )
            self.assertEqual(run.returncode, 0)
            self.assertIn("decision", finished, finished)
            self.assertEqual(finished["decision"]["capability_gap_refs"], [missing_capability])
            self.assertEqual(finished["decision"]["effective_event"], "COMMENT")
            self.assertFalse(finished["confirmation_projection"]["approve_eligible"])
            self.assertEqual(finished["policy"]["obligations"][0]["fallback"]["status"], "provided")
            print("Mechanical runtime timing (ns):", finished["mechanical_timing_ns"], flush=True)

    def test_missing_required_evidence_skips_every_lane_and_refuses_receipt(self):
        with self.prepared_results() as (prepared, _results):
            bundle = prepared["bundle"]
            bundle["pointers"] = [
                p for p in bundle["pointers"] if p["evidence_class"] != "diff_hunks"
            ]
            for binding in bundle["bindings"]:
                if binding["evidence_class"] == "diff_hunks":
                    binding.update(refs=[], missing="unavailable")
            rehash_bundle(prepared)
            self.assertEqual(protocol.requests(prepared), [])
            self.assertEqual(
                protocol.dispatch(prepared, ["/this/command/must/not/run"]), []
            )
            self.assertEqual(prepared["attempts"], {})
            self.assertEqual(
                self.finish(prepared, [])["reason"], "receipt_incomplete"
            )

    def test_failed_and_retried_provider_reports_are_retained(self):
        for recover in (False, True):
            with (
                self.subTest(recover=recover),
                self.prepared_results() as (prepared, results),
            ):
                directory = pathlib.Path(prepared["directory"])
                program = """
import json, pathlib, sys
r = json.load(sys.stdin)
marker = pathlib.Path(sys.argv[1]) / (r['capability'] + '.attempted')
if not marker.exists():
    marker.touch()
    print('null')
    sys.exit(75)
if not RECOVER:
    print('null')
    sys.exit(1)
""".replace("RECOVER", repr(recover)) + inspect.getsource(clean_reply) + inspect.getsource(provider_reply)
                program += "print(json.dumps(provider_reply(clean_reply(r))))"
                returned = protocol.dispatch(
                    prepared, [sys.executable, "-c", program, str(directory)]
                )
                collated = self.collate(prepared, returned)
                requests = protocol.requests(prepared)
                events = [e for e in prepared["audit"] if e["event_type"] == "invoked"]
                self.assertEqual(len(events), 2 * len(requests))
                self.assertEqual(len(returned), len(requests) if recover else 0)
                self.assertEqual(len(collated["observation"]["lanes"]), len(events))
                for request in requests:
                    capability = request["capability"]
                    self.assertEqual(
                        [a["result"] for a in prepared["attempts"][capability]],
                        ["transient_failure", "succeeded" if recover else "terminal_failure"],
                    )
                for event in events:
                    self.assert_provider_report(prepared, event)

    def test_unquoted_critical_is_advisory_not_a_blocker(self):
        with self.prepared_results() as (prepared, results):
            answer = self.contribution(
                results[0], severity="CRITICAL", confidence=1, quote="invented line"
            )
            collated = self.collate(prepared, results)
            self.assertEqual(collated["policy"]["confirmed_blocker_refs"], [])
            self.assertEqual(collated["observation"]["synthesis"]["findings"], [])
            self.assertIn("Advisory", collated["rendered"]["body"])
            for confidence, severity, findings, advisory in (
                (1, "MEDIUM", 0, False),
                (2, "MEDIUM", 0, False),
                (3, "CRITICAL", 0, True),
                (4, "MEDIUM", 0, True),
                (5, "MEDIUM", 1, False),
                (1, "CRITICAL", 1, False),
            ):
                answer["contributions"][0].update(
                    quote="value = 2", confidence=confidence, severity=severity
                )
                checked = self.collate(prepared, results)
                self.assertEqual(
                    len(checked["observation"]["synthesis"]["findings"]), findings
                )
                self.assertEqual("Advisory" in checked["rendered"]["body"], advisory)

    def test_selected_mechanical_commands_run_once_and_record_unavailable(self):
        command = {"id": "missing", "argv": ["/this/command/is/missing"], "cwd": ".", "timeout_seconds": 1}
        with self.prepared_results([command]) as (prepared, _results):
            observations = prepared["bundle"]["test_observations"]
            self.assertEqual(len(observations), 1)
            self.assertEqual(observations[0]["status"], "unavailable")
            rejected_dir = pathlib.Path(prepared["directory"]).with_name("wrong-origin")
            rejected = protocol.prepare(prepared["repository_path"],
                                        {**self.identity, "repository": "other/repository"}, rejected_dir)
            self.assertEqual(rejected["reason"], "invalid_identity")
            self.assertFalse(rejected_dir.exists())
            for manifest in prepared["plan"]["manifests"]:
                self.assertEqual(protocol.canonical(protocol.capability_view(manifest["id"])["manifest"]),
                                 protocol.canonical(manifest))

    def test_mechanical_deadline_is_independent_of_worker_deadline(self):
        program = "import sys; print('test_case failed\\n'+'x'*9000+'\\nTOKEN=fixture-secret\\n-----BEGIN PRIVATE KEY-----\\nprivate-fixture\\n-----END PRIVATE KEY-----\\nFAIL test_case'); sys.stderr.write('AssertionError: expected 2\\n'); raise SystemExit(7)"
        command = {"id": "test", "argv": [sys.executable, "-c", program], "cwd": "."}
        for seconds in (1, 120, 121, 240):
            selected = {**command, "timeout_seconds": seconds}
            frozen = protocol.plan({**self.request, "test_commands": [selected]})
            self.assertEqual(frozen["test_commands"], [selected])
            self.assertEqual(frozen["timeout_seconds"], 120)
        for seconds in (0, 241, True, 1.5):
            self.assertRaises(protocol.Invalid, protocol.validate, {**command, "timeout_seconds": seconds}, "TestCommand")
        communicate, deadlines = subprocess.Popen.communicate, []
        def observed(process, *args, **kwargs):
            if process.args == command["argv"]:
                deadlines.append(kwargs.get("timeout"))
            return communicate(process, *args, **kwargs)
        stalled = {**command, "id": "stalled", "argv": [sys.executable, "-c", "import time; print('waiting', flush=True); time.sleep(5)"], "timeout_seconds": 1}
        passed = {**stalled, "id": "passed", "argv": [sys.executable, "-c", "print('ok')"]}
        with warnings.catch_warnings(record=True) as seen:
            warnings.simplefilter("always", ResourceWarning)
            with patch.object(subprocess.Popen, "communicate", observed), self.prepared_results(
                    [{**command, "timeout_seconds": 240}, stalled, passed]) as (prepared, _):
                observation = prepared["bundle"]["test_observations"][0]
                self.assertEqual((observation["status"], observation["exit_code"]), ("completed", 7))
                diagnostic = observation["diagnostics"]
                self.assertTrue(diagnostic["stdout"].startswith("test_case failed"))
                self.assertTrue(diagnostic["stdout"].endswith("FAIL test_case\n"))
                self.assertEqual(diagnostic["stderr"], "AssertionError: expected 2\n")
                self.assertTrue(diagnostic["truncated"])
                self.assertLessEqual(len(diagnostic["stdout"]), 4096)
                for secret in ("fixture-secret", "private-fixture"):
                    self.assertNotIn(secret, json.dumps(diagnostic))
                bound = next(g for r in protocol.requests(prepared) for g in r["evidence"] if g["evidence_class"] == "mechanical_tests")
                self.assertEqual(bound["test_observations"][0], observation)
                exported = next(e for e in protocol.host_files(prepared, write=True)["request_files"] if e["capability"] == "test_evidence")
                view = next(g for g in protocol.read_json(exported["request_file"])["request"]["evidence"] if g["evidence_class"] == "mechanical_tests")["test_observations"][0]["diagnostics"]
                self.assertEqual({k: "".join(v) for k, v in view.items() if isinstance(v, list) and all(len(c) <= 256 for c in v)},
                                 {k: diagnostic[k] for k in ("stdout", "stderr")})
                changed = copy.deepcopy(prepared)
                changed["bundle"]["test_observations"][0]["diagnostics"]["stdout"] = "invented failure"
                rehash_bundle(changed)
                self.assertRaises(protocol.Invalid, protocol.requests, changed)
                for delta in ({"stdout": "x" * 4097}, {"truncated": 1}, {"extra": "field"}):
                    self.assertRaises(protocol.Invalid, protocol.validate, {**observation, "diagnostics": {**diagnostic, **delta}}, "TestObservation")
                protocol.validate({k: v for k, v in observation.items() if k != "diagnostics"}, "TestObservation")
                self.assertEqual(deadlines, [240])
                self.assertEqual(prepared["bundle"]["test_observations"][1]["status"], "timed_out")
                self.assertEqual(prepared["bundle"]["test_observations"][1]["diagnostics"]["stdout"], "waiting\n")
                self.assertNotIn("diagnostics", prepared["bundle"]["test_observations"][2])
        self.assertEqual([str(w.message) for w in seen if issubclass(w.category, ResourceWarning)], [])

    def test_authority_mutations_refuse_before_approval(self):
        bank = protocol.catalog()
        for field, value in (
            ("activation_signals", []),
            ("required_evidence", ["issue"]),
            ("questions", [bank["capabilities"][1]["questions"][0]]),
        ):
            mutated = copy.deepcopy(bank)
            mutated["capabilities"][0][field] = value
            replacement = patch.object(protocol, "read_json", return_value=mutated)
            with replacement, self.assertRaises(protocol.Invalid):
                protocol.catalog()
        with self.prepared_results() as (prepared, results):
            for field, value in (("revision", 1), ("parent_hash", "f" * 64), ("bindings", [])):
                changed = copy.deepcopy(prepared)
                changed["bundle"][field] = value
                rehash_bundle(changed)
                self.assertRaises(protocol.Invalid, protocol.requests, changed)
            for field, value in (("bundle_revision", 1), ("answers", [])):
                changed = copy.deepcopy(results)
                changed[0][field] = value
                self.assertEqual(self.collate(prepared, changed)["rendered"]["event"], "COMMENT")
            self.assertEqual(self.collate(prepared, results + [results[0]])["rendered"]["event"], "COMMENT")
            self.assertEqual(protocol.collate(prepared, [{"schema": "kc-pr-flow.expansion-request/v1"}])["reason"],
                             "unsupported_expansion")
            protocol.git(prepared["repository_path"], "checkout", "--detach", self.identity["base_sha"])
            self.assertEqual(self.finish(prepared, results)["reason"], "identity_change")

    def test_posting_invalidation_and_absent_outcome_are_read_only(self):
        with self.prepared_results() as (prepared, _results):
            event_file = next((pathlib.Path(prepared["directory"]) / "state").rglob("events.jsonl"))
            original = event_file.read_bytes()
            self.assertIsNone(protocol.posting_projection(prepared, event_file))
            snapshot, event = self.posting_log(prepared, [("run.invalidated", {"reason": "head_moved"})])
            self.assertEqual(protocol.posting_projection(prepared, snapshot)["reason"], "head_moved")
            self.assertEqual(event_file.read_bytes(), original)
            for field in ("review_key", "head_sha", "config_hash", "base_sha", "repository", "run_id"):
                changed = copy.deepcopy(prepared)
                changed["identity"][field] = event["run_id"] if field == "run_id" else "mismatched"
                self.assertRaises(protocol.Invalid, protocol.posting_projection, changed, snapshot)


if __name__ == "__main__":
    unittest.main()
