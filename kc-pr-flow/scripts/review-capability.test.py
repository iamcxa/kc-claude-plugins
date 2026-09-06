#!/usr/bin/env python3
"""Behavioral checks for the default-off profiled review journey."""

import contextlib
import copy
import importlib.util
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

HERE = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "capability", HERE / "review-capability.py"
)
protocol = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(protocol)


class PlannerTests(unittest.TestCase):
    def test_actual_rehydrate_projection_mismatch_is_terminal(self):
        with self.prepared_results() as (prepared, results):
            private = pathlib.Path(prepared["directory"]) / "boundary-probe"
            (private / "scripts").mkdir(parents=True)
            shutil.copytree(HERE.parent / "schemas", private / "schemas")
            shutil.copy(
                HERE / "review-capability.py", private / "scripts/review-capability.py"
            )
            wrapper = private / "scripts/review-runtime.sh"
            wrapper.write_text(
                '#!/usr/bin/env bash\nset -o pipefail\nif [ "$1" = rehydrate-interactive ]; then\n'
                + "bash "
                + str(HERE / "review-runtime.sh")
                + " \"$@\" | jq ' .approve_eligible = (.approve_eligible | not) '\n"
                + "else\nbash "
                + str(HERE / "review-runtime.sh")
                + ' "$@"\nfi\n'
            )
            spec = importlib.util.spec_from_file_location(
                "boundary_probe", private / "scripts/review-capability.py"
            )
            probe = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(probe)
            result = probe.finish(prepared, results)
            self.assertEqual(result["reason"], "projection_mismatch")
            protocol.validate(result, "RunTerminal")

    def test_document_tables_are_generated_from_their_authorities(self):
        document = (
            HERE.parents[1]
            / "docs/superpowers/specs/2026-09-05-kc-pr-review-capability-protocol-v1.md"
        ).read_text()
        for table in protocol.contract_tables():
            self.assertIn(table, document)
            self.assertNotIn(
                table,
                document.replace(table.splitlines()[2], "| deliberately wrong |", 1),
            )

    def test_sampled_skill_command_stays_off_and_tokens_are_closed(self):
        skill = (HERE.parent / "skills/kc-pr-review/SKILL.md").read_text()
        command = (
            skill.split(
                "For the profiled route, call the repository-owned adapter once:", 1
            )[1]
            .split("```bash\n", 1)[1]
            .split("```", 1)[0]
        )
        with tempfile.TemporaryDirectory() as root:
            root = pathlib.Path(root)
            stub = root / "claude"
            stub.write_text('#!/bin/sh\ntouch "' + str(root / "called") + '"\nexit 1\n')
            stub.chmod(0o755)
            result = subprocess.run(
                ["bash", "-c", command],
                check=False,
                cwd=root,
                capture_output=True,
                text=True,
                env={
                    **os.environ,
                    "PATH": str(root) + os.pathsep + os.environ["PATH"],
                    "CLAUDE_PLUGIN_ROOT": str(HERE.parent),
                    "KC_PR_FLOW_REVIEW_TYPED": "off",
                    "KC_PR_FLOW_PROFILED_REVIEW": "off",
                    "REVIEW_WORKTREE": str(root),
                    "REVIEW_RUN_DIR": str(root / "run"),
                    "REVIEW_MODEL": "fixture",
                },
            )
            self.assertEqual(json.loads(result.stdout)["route"], "legacy")
            self.assertFalse((root / "called").exists())
        with self.assertRaises(protocol.Invalid):
            protocol.validate("abc\n", "Token")

    def test_unsupported_material_is_missing_not_invalid_caller_schema(self):
        for content in (b"value = '\xe9'\n", b"x" * 1048577 + b"\n"):
            with (
                self.subTest(size=len(content)),
                self.prepared_results() as (prepared, _),
            ):
                repo = prepared["repository_path"]
                (pathlib.Path(repo) / "example.py").write_bytes(content)
                protocol.git(repo, "commit", "-qam", "unsupported material")
                identity = {
                    **self.identity,
                    "head_sha": protocol.git(repo, "rev-parse", "HEAD")
                    .decode()
                    .strip(),
                }
                result = protocol.prepare(
                    repo,
                    identity,
                    pathlib.Path(prepared["directory"]).with_name("unsupported"),
                    "lite",
                )
                binding = next(
                    b
                    for b in result["bundle"]["bindings"]
                    if b["evidence_class"] == "diff_hunks"
                )
                self.assertEqual(
                    binding,
                    {
                        "evidence_class": "diff_hunks",
                        "refs": [],
                        "missing": "unsupported",
                    },
                )
                self.assertEqual(protocol.requests(result), [])
                self.assertEqual(
                    protocol.finish(result, [])["reason"], "receipt_incomplete"
                )

    def test_malformed_cli_artifacts_always_return_valid_terminals(self):
        with self.prepared_results() as (prepared, results):
            directory = pathlib.Path(prepared["directory"])
            intake = directory / "invalid-intake.json"
            intake.write_text(
                protocol.canonical({**self.identity, "repository": "x" * 257}).decode()
            )
            fallback = directory / "fallback.json"
            fallback.write_text("[null]")
            pending = directory / "dispatched.json"
            cases = [
                (
                    [
                        "--identity-file",
                        str(intake),
                        "--repo-worktree",
                        prepared["repository_path"],
                        "--run-dir",
                        str(directory / "new"),
                        "--model",
                        "unused",
                    ],
                    {},
                ),
                (["--finalize-dir", str(directory)], {}),
                (
                    [
                        "--finalize-dir",
                        str(directory),
                        "--fallbacks-file",
                        str(fallback),
                    ],
                    {"prepared": prepared, "results": results},
                ),
            ]
            for arguments, dispatched in cases:
                with self.subTest(arguments=arguments):
                    pending.write_text(protocol.canonical(dispatched).decode())
                    run = subprocess.run(
                        [
                            sys.executable,
                            str(HERE / "review-capability.py"),
                            *arguments,
                        ],
                        check=False,
                        env={
                            **os.environ,
                            "KC_PR_FLOW_REVIEW_TYPED": "on",
                            "KC_PR_FLOW_PROFILED_REVIEW": "on",
                        },
                        capture_output=True,
                        text=True,
                    )
                    self.assertEqual(run.returncode, 2, run.stderr)
                    terminal = protocol.json.loads(run.stdout)
                    protocol.validate(terminal, "RunTerminal")
                    self.assertEqual(terminal["reason"], "schema_failure")
                    self.assertNotIn("Traceback", run.stderr)

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
            fixture = protocol.json.loads(
                line, object_pairs_hook=protocol.unique_object
            )
            with self.subTest(fixture=fixture["name"]):
                if fixture["valid"]:
                    protocol.validate(fixture["value"], fixture["definition"])
                else:
                    with self.assertRaises(protocol.Invalid):
                        protocol.validate(fixture["value"], fixture["definition"])

    def setUp(self):
        self.identity = {
            "schema": "kc-pr-flow.intake-identity/v1",
            "repository": "acme/widgets",
            "pr_number": 42,
            "base_sha": "a" * 40,
            "head_sha": "b" * 40,
            "intake_id": "intake-test",
        }
        self.request = {
            "schema": "kc-pr-flow.planner-input/v1",
            "identity": self.identity,
            "protocol_major": 1,
            "requested": "auto",
            "full_pass": False,
            "shape": [
                {"path": "src/example.py", "added": 4, "deleted": 2, "binary": False}
            ],
            "test_commands": [],
            "concerns": [],
        }

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

    def test_terminal_matrix_and_invalid_intake_echo_are_closed(self):
        review = {
            key: value
            for key, value in self.identity.items()
            if key not in ("schema", "intake_id")
        }
        review.update(run_id="run-test", config_hash="c" * 64, review_key="d" * 64)
        pairs = {
            "REQUEST_INVALID": [
                "schema_failure",
                "unsupported_major",
                "invalid_identity",
            ],
            "NEEDS_CLARIFICATION": ["missing_intent"],
            "ABORTED_STALE": ["stale_head"],
            "INVALIDATED": ["identity_change", "configuration_change"],
            "ABORTED_INCOMPLETE": [
                "required_gap",
                "contradiction",
                "unsupported_expansion",
                "receipt_incomplete",
                "projection_mismatch",
            ],
        }
        for status, reasons in pairs.items():
            identity = (
                review
                if status in ("INVALIDATED", "ABORTED_INCOMPLETE")
                else self.identity
            )
            for reason in reasons:
                with self.subTest(status=status, reason=reason):
                    value = protocol.terminal(identity, status, reason)
                    protocol.validate(value, "RunTerminal")
                    for other_status in pairs.keys() - {status}:
                        with self.assertRaises(protocol.Invalid):
                            protocol.validate(
                                {**value, "status": other_status}, "RunTerminal"
                            )
        for reason in ("schema_failure", "invalid_identity"):
            protocol.validate(
                protocol.terminal({"pr_number": "bad"}, "REQUEST_INVALID", reason),
                "RunTerminal",
            )
        with self.assertRaises(protocol.Invalid):
            protocol.validate(
                protocol.terminal(
                    {"pr_number": "bad"}, "REQUEST_INVALID", "unsupported_major"
                ),
                "RunTerminal",
            )

    @contextlib.contextmanager
    def prepared_results(self, commands=()):
        with tempfile.TemporaryDirectory() as temporary:
            repo = pathlib.Path(temporary) / "repo"
            repo.mkdir()

            def git(*args):
                return subprocess.check_output(
                    ["git", "-C", str(repo), *args], text=True
                ).strip()

            git("init", "-q")
            git("config", "user.name", "Fixture")
            git("config", "user.email", "fixture@example.invalid")
            git("remote", "add", "origin", "https://github.com/acme/widgets.git")
            (repo / "example.py").write_text("value = 1\n")
            git("add", "example.py")
            git("commit", "-qm", "base")
            self.identity["base_sha"] = git("rev-parse", "HEAD")
            (repo / "example.py").write_text("value = 2\n")
            git("commit", "-qam", "head")
            self.identity["head_sha"] = git("rev-parse", "HEAD")
            prepared = protocol.prepare(
                repo,
                self.identity,
                pathlib.Path(temporary) / "run",
                test_commands=commands,
            )
            self.assertEqual(prepared["shape_bundle"]["pointers"], [])
            self.assertNotEqual(
                prepared["bundle"]["identity"]["run_id"], self.identity["intake_id"]
            )
            self.assertEqual(
                prepared["bundle"]["parent_hash"],
                prepared["shape_bundle"]["bundle_hash"],
            )
            requests = protocol.requests(prepared)
            results = [
                {
                    **{
                        key: request[key]
                        for key in (
                            "identity",
                            "plan_rev",
                            "plan_hash",
                            "bundle_revision",
                            "bundle_hash",
                            "capability",
                        )
                    },
                    "schema": "kc-pr-flow.capability-result/v1",
                    "answers": [
                        {
                            "question_id": request["question_ids"][0],
                            "assessment": "clean",
                            "evidence_refs": [
                                request["evidence"][0]["material"][0]["id"]
                            ],
                            "contributions": [],
                        }
                    ],
                    "status": "succeeded",
                    "usage": {
                        "input_tokens": None,
                        "output_tokens": None,
                        "total_tokens": None,
                    },
                }
                for request in requests
            ]
            yield prepared, results

    def test_selected_evidence_binds_the_runtime_identity_and_rehydrates(self):
        with self.prepared_results() as (prepared, results):
            requests = protocol.requests(prepared)
            program = (
                "import json,sys; r=json.load(sys.stdin); results="
                + repr(results)
                + "; print(json.dumps({'structured_output':next(x for x in results if x['capability']==r['capability']), 'modelUsage':{'fixture':{}}, 'total_cost_usd':0.01, 'usage':{'input_tokens':10,'output_tokens':2,'cache_creation_input_tokens':0,'cache_read_input_tokens':0}}))"
            )
            results = protocol.dispatch(prepared, [sys.executable, "-c", program])
            finished = protocol.finish(prepared, results)
            self.assertEqual(finished["decision"]["coverage"], "complete")
            self.assertTrue(finished["decision"]["approve_eligible"])
            directory = pathlib.Path(prepared["directory"])
            protocol.store(directory / "prepared.json", prepared)
            protocol.store(directory / "audit.json", prepared["audit"])
            spec = importlib.util.spec_from_file_location(
                "ablation", HERE / "review-ablation-core.py"
            )
            core = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(core)
            metrics = core.pilot_telemetry(directory, "fixture")
            self.assertAlmostEqual(metrics["capability_cost_usd"], len(requests) * 0.01)
            self.assertEqual(metrics["capability_tokens"], len(requests) * 12)
            with self.assertRaises(SystemExit):
                core.pilot_telemetry(directory, "different-model")
            provider = next(directory.glob("provider-*.json"))
            envelope = provider.read_bytes()
            provider.write_text("null")
            with self.assertRaises(SystemExit):
                core.pilot_telemetry(directory, "fixture")
            provider.write_bytes(envelope)
            event_file = next((directory / "state").rglob("events.jsonl"))
            identity = prepared["identity"]
            posting_start = protocol.runtime(
                prepared,
                "start",
                "--repo",
                identity["repository"],
                "--pr",
                identity["pr_number"],
                "--base",
                identity["base_sha"],
                "--head",
                identity["head_sha"],
                "--config-hash",
                identity["config_hash"],
            )
            identity = {**identity, "run_id": posting_start["run_id"]}
            payload_hash = "f" * 64
            idempotency = protocol.raw_hash(
                f"{identity['review_key']}|{identity['head_sha']}|{payload_hash}".encode()
            )
            events = [protocol.canonical(posting_start).decode()]
            for kind, payload in (
                ("head.observed", {"head_sha": identity["head_sha"]}),
                (
                    "authorization.granted",
                    {
                        "commit_id": identity["head_sha"],
                        "event": "APPROVE",
                        "payload_sha256": payload_hash,
                        "idempotency_key": idempotency,
                    },
                ),
                (
                    "post.intent",
                    {
                        "commit_id": identity["head_sha"],
                        "payload_sha256": payload_hash,
                        "idempotency_key": idempotency,
                    },
                ),
                (
                    "post.result",
                    {
                        "idempotency_key": idempotency,
                        "outcome": "posted_reconciled",
                        "remote_review_id": 42,
                    },
                ),
            ):
                arguments = [
                    identity[k]
                    for k in (
                        "run_id",
                        "review_key",
                        "repository",
                        "pr_number",
                        "base_sha",
                        "head_sha",
                        "config_hash",
                    )
                ]
                events.append(
                    subprocess.check_output(
                        [
                            "bash",
                            "-c",
                            '. "$1"; shift; review_runtime_build_event "$@"',
                            "fixture",
                            str(HERE / "review-runtime.sh"),
                            *map(str, arguments),
                            str(len(events) + 1),
                            "2026-09-06T00:00:00Z",
                            kind,
                            protocol.canonical(payload).decode(),
                        ],
                        text=True,
                    ).strip()
                )
            projected_file = directory / "posted-fixture.jsonl"
            projected_file.write_text("\n".join(events) + "\n")
            projected = protocol.posting_projection(prepared, projected_file)
            self.assertEqual(projected["outcome"], "posted_reconciled")
            self.assertEqual(projected["remote_review_id"], 42)
            self.assertEqual(projected["run_id"], posting_start["run_id"])
            self.assertNotEqual(projected["run_id"], prepared["identity"]["run_id"])
            self.assertEqual(event_file.read_text().count("post.result"), 0)
            print(
                "Mechanical runtime timing (ns):",
                finished["mechanical_timing_ns"],
                flush=True,
            )

    def test_cross_capability_high_finding_merges_and_forces_request_changes(self):
        with self.prepared_results() as (prepared, results):
            for result, severity in zip(results[:2], ("HIGH", "MEDIUM")):
                answer = result["answers"][0]
                answer["assessment"] = "findings"
                answer["contributions"] = [
                    {
                        "evidence_ref": answer["evidence_refs"][0],
                        "category": "correctness",
                        "claim_key": "wrong-value",
                        "severity": severity,
                        "confidence": 9,
                        "quote": "value = 2",
                        "summary": "The value violates the accepted contract.",
                    }
                ]
            rendered = protocol.collate(prepared, results)["rendered"]
            self.assertEqual(len(rendered["inline_comments"]), 1)
            inline = rendered["inline_comments"][0]
            self.assertEqual(
                (inline["path"], inline["line"], inline["side"]),
                ("example.py", 1, "RIGHT"),
            )
            self.assertIn("value = 2", inline["body"])
            self.assertIn("example.py:1", rendered["body"])
            finished = protocol.finish(prepared, results)
            self.assertIn("decision", finished, finished)
            decision = finished["decision"]
            self.assertEqual(decision["effective_event"], "REQUEST_CHANGES")
            self.assertFalse(decision["approve_eligible"])
            self.assertEqual(len(decision["confirmed_blocker_refs"]), 1)
            self.assertEqual(finished["receipt"]["counts"]["findings"], 1)
            self.assertEqual(finished["receipt"]["counts"]["candidates"], 2)

    def test_transient_adapter_retry_is_bounded_and_timed(self):
        with self.prepared_results() as (prepared, _results):
            command = ["/bin/sh", "-c", "exit 75"]
            returned = protocol.dispatch(prepared, command)
            self.assertEqual(returned, [])
            for attempts in prepared["attempts"].values():
                self.assertEqual(
                    [a["result"] for a in attempts],
                    ["transient_failure", "terminal_failure"],
                )
            invocations = [e for e in prepared["audit"] if e["event_type"] == "invoked"]
            self.assertEqual(len(invocations), 2 * len(protocol.requests(prepared)))
            self.assertTrue(
                all(
                    e["finished_ns"] >= e["started_ns"] > 0
                    and e["evidence_payload_bytes"] > 0
                    for e in invocations
                )
            )
            collated = protocol.collate(prepared, returned)
            self.assertTrue(
                all(
                    len(o["adapter_attempts"]) == 2
                    for o in collated["policy"]["obligations"]
                )
            )
            self.assertEqual(len(collated["observation"]["lanes"]), len(invocations))

    def test_selected_material_tampering_and_unassigned_answers_refuse(self):
        with self.prepared_results() as (prepared, results):
            self.assertIn(
                "related_source",
                {p["evidence_class"] for p in prepared["bundle"]["pointers"]},
            )
            changed = copy.deepcopy(prepared)
            changed["bundle"]["pointers"][0]["material"] = "invented evidence"
            changed["bundle"]["bundle_hash"] = protocol.digest(
                {k: v for k, v in changed["bundle"].items() if k != "bundle_hash"}
            )
            with self.assertRaises(protocol.Invalid):
                protocol.requests(changed)
            results[0]["answers"][0]["question_id"] = "not_assigned"
            self.assertEqual(
                protocol.collate(prepared, results)["rendered"]["event"], "COMMENT"
            )
            results[0]["capability"] = "not_selected"
            self.assertEqual(
                protocol.collate(prepared, results)["reason"], "schema_failure"
            )

    def test_question_decision_and_confirmation_are_derived_not_model_supplied(self):
        with self.prepared_results() as (prepared, results):
            collated = protocol.collate(prepared, results)
            decision = collated["protocol_decision"]
            protocol.validate(decision, "ReviewDecision")
            self.assertEqual(
                sorted(t["question_id"] for t in decision["terminals"]),
                prepared["plan"]["questions"],
            )
            changed = copy.deepcopy(decision)
            changed["terminals"].pop()
            self.assertEqual(
                protocol.check_decision(prepared, changed)["reason"], "required_gap"
            )
            changed = copy.deepcopy(decision)
            changed["terminals"][0]["state"] = "contradictory_required"
            self.assertEqual(
                protocol.check_decision(prepared, changed)["reason"], "contradiction"
            )

    def test_default_off_flags_and_unsupported_profiles_do_not_dispatch(self):
        for typed, profiled in (
            (None, None),
            ("on", None),
            (None, "on"),
            ("ON", "on"),
            ("on", "true"),
        ):
            self.assertFalse(
                protocol.enabled(
                    {
                        "KC_PR_FLOW_REVIEW_TYPED": typed,
                        "KC_PR_FLOW_PROFILED_REVIEW": profiled,
                    }
                )
            )
        self.assertTrue(
            protocol.enabled(
                {"KC_PR_FLOW_REVIEW_TYPED": "on", "KC_PR_FLOW_PROFILED_REVIEW": "on"}
            )
        )
        for profile in ("standard", "full", "custom"):
            routed = protocol.plan({**self.request, "requested": profile})
            self.assertEqual(
                routed["route"], "unavailable" if profile == "custom" else "legacy"
            )

    def test_failed_final_attempt_accepts_only_bound_clean_manual_fallback(self):
        with self.prepared_results() as (prepared, results):
            capability = results[0]["capability"]
            fallback = {
                "schema": "kc-pr-flow.manual-fallback/v1",
                "bundle_hash": prepared["bundle"]["bundle_hash"],
                "human_note": "",
                "result": {
                    "schema": "kc-pr-flow.manual-capability-result/v1",
                    "capability": capability,
                    "review_identity": prepared["identity"],
                    "terminal_assessment": "clean",
                    "candidate_ids": [],
                    "evidence": [prepared["bundle"]["pointers"][0]["pointer"]],
                    "recorded_by": "interactive-human",
                    "recorded_at": "2026-09-05T00:00:00Z",
                },
            }
            results[0]["unexpected"] = True
            ordinary = protocol.collate(prepared, results)
            self.assertEqual(ordinary["rendered"]["event"], "COMMENT")
            collated = protocol.collate(prepared, results, [fallback])
            obligation = next(
                o
                for o in collated["policy"]["obligations"]
                if o["capability"] == capability
            )
            self.assertEqual(obligation["terminal_state"], "clean")
            self.assertEqual(obligation["fallback"]["status"], "provided")
            self.assertEqual(
                obligation["adapter_attempts"][-1]["result"], "terminal_failure"
            )
            for field, value in (
                ("bundle_hash", "f" * 64),
                ("terminal_assessment", "findings"),
            ):
                mutated = copy.deepcopy(fallback)
                (mutated if field == "bundle_hash" else mutated["result"])[field] = (
                    value
                )
                refused = protocol.collate(prepared, results, [mutated])
                self.assertEqual(refused["rendered"]["event"], "COMMENT")

    def test_manual_fallback_and_failed_capability_rehydrate_real_incomplete_receipt(
        self,
    ):
        started = time.monotonic()
        with self.prepared_results() as (prepared, results):
            print("Mechanical prepare seconds:", time.monotonic() - started, flush=True)
            fallback = {
                "schema": "kc-pr-flow.manual-fallback/v1",
                "bundle_hash": prepared["bundle"]["bundle_hash"],
                "human_note": "",
                "result": {
                    "schema": "kc-pr-flow.manual-capability-result/v1",
                    "capability": results[0]["capability"],
                    "review_identity": prepared["identity"],
                    "terminal_assessment": "clean",
                    "candidate_ids": [],
                    "evidence": [prepared["bundle"]["pointers"][0]["pointer"]],
                    "recorded_by": "interactive-human",
                    "recorded_at": "2026-09-05T00:00:00Z",
                },
            }
            results[0]["unknown"] = True
            missing_capability = results.pop()["capability"]
            directory = pathlib.Path(prepared["directory"])
            protocol.store(
                directory / "dispatched.json",
                {"prepared": prepared, "results": results},
            )
            fallback_file = protocol.store(directory / "fallbacks.json", [fallback])
            output = subprocess.check_output(
                [
                    sys.executable,
                    str(HERE / "review-capability.py"),
                    "--finalize-dir",
                    str(directory),
                    "--fallbacks-file",
                    fallback_file,
                ]
            )
            finished = protocol.json.loads(output)
            self.assertIn("decision", finished, finished)
            self.assertEqual(
                finished["decision"]["capability_gap_refs"], [missing_capability]
            )
            self.assertEqual(finished["decision"]["effective_event"], "COMMENT")
            self.assertFalse(finished["confirmation_projection"]["approve_eligible"])
            self.assertEqual(
                finished["policy"]["obligations"][0]["fallback"]["status"], "provided"
            )
            print(
                "Mechanical runtime timing (ns):",
                finished["mechanical_timing_ns"],
                flush=True,
            )

    def test_missing_required_evidence_skips_every_lane_and_refuses_receipt(self):
        with self.prepared_results() as (prepared, _results):
            bundle = prepared["bundle"]
            bundle["pointers"] = [
                p for p in bundle["pointers"] if p["evidence_class"] != "diff_hunks"
            ]
            for binding in bundle["bindings"]:
                if binding["evidence_class"] == "diff_hunks":
                    binding.update(refs=[], missing="unavailable")
            bundle["bundle_hash"] = protocol.digest(
                {k: v for k, v in bundle.items() if k != "bundle_hash"}
            )
            self.assertEqual(protocol.requests(prepared), [])
            self.assertEqual(
                protocol.dispatch(prepared, ["/this/command/must/not/run"]), []
            )
            self.assertEqual(prepared["attempts"], {})
            self.assertEqual(
                protocol.finish(prepared, [])["reason"], "receipt_incomplete"
            )

    def test_provider_attempt_budget_and_raw_usage_bind_audit(self):
        with self.prepared_results() as (prepared, _results):
            program = """
import json, sys
request = json.load(sys.stdin)
assert sys.argv[1] == '--max-budget-usd'
assert 0 < float(sys.argv[2]) <= 0.5
answer = {'question_id': request['question_ids'][0], 'assessment': 'clean',
          'evidence_refs': [request['evidence'][0]['material'][0]['id']], 'contributions': []}
result = {k: request[k] for k in ('identity','plan_rev','plan_hash','bundle_revision','bundle_hash','capability')}
result.update(schema='kc-pr-flow.capability-result/v1', answers=[answer], status='succeeded',
              usage={'input_tokens':None,'output_tokens':None,'total_tokens':None})
print(json.dumps({'structured_output':result, 'modelUsage':{'fixture':{}}, 'total_cost_usd':0.01,
                  'usage':{'input_tokens':10,'output_tokens':2,'cache_creation_input_tokens':0,'cache_read_input_tokens':0}}))
"""
            returned = protocol.dispatch(prepared, [sys.executable, "-c", program], 6)
            self.assertEqual(len(returned), len(protocol.requests(prepared)))
            for event in prepared["audit"][1:]:
                envelope = protocol.read_json(
                    pathlib.Path(prepared["directory"])
                    / f"provider-{event['capability']}-1.json"
                )
                request = next(
                    r
                    for r in protocol.requests(prepared)
                    if r["capability"] == event["capability"]
                )
                self.assertEqual(
                    event["payload_sha256"],
                    protocol.digest(
                        {"request": request, "provider_envelope": envelope}
                    ),
                )

    def test_failed_and_retried_provider_usage_is_never_skipped(self):
        spec = importlib.util.spec_from_file_location(
            "ablation", HERE / "review-ablation-core.py"
        )
        core = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(core)
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
answer = next(x for x in RESULTS if x['capability'] == r['capability'])
print(json.dumps({'structured_output':answer, 'modelUsage':{'fixture':{}}, 'total_cost_usd':0.01,
                  'usage':{'input_tokens':10,'output_tokens':2,'cache_creation_input_tokens':0,'cache_read_input_tokens':0}}))
""".replace("RECOVER", repr(recover)).replace("RESULTS", repr(results))
                returned = protocol.dispatch(
                    prepared, [sys.executable, "-c", program, str(directory)]
                )
                collated = protocol.collate(prepared, returned)
                protocol.audit(prepared, "collated", collated)
                for name, value in (
                    ("prepared", prepared),
                    ("audit", prepared["audit"]),
                    ("policy", collated["policy"]),
                ):
                    protocol.store(directory / (name + ".json"), value)
                metrics = core.pilot_telemetry(directory, "fixture")
                count = len(protocol.requests(prepared))
                self.assertEqual(metrics["capability_cost_status"], "incomplete")
                self.assertEqual(
                    metrics["capability_unknown_attempts"],
                    count if recover else 2 * count,
                )
                self.assertAlmostEqual(
                    metrics["capability_cost_usd"], count * 0.01 if recover else 0
                )
                self.assertEqual(metrics["retry_count"], count)

    def test_unquoted_critical_is_advisory_not_a_blocker(self):
        with self.prepared_results() as (prepared, results):
            answer = results[0]["answers"][0]
            answer.update(
                assessment="findings",
                contributions=[
                    {
                        "evidence_ref": answer["evidence_refs"][0],
                        "category": "correctness",
                        "claim_key": "bad-value",
                        "severity": "CRITICAL",
                        "confidence": 1,
                        "quote": "invented line",
                        "summary": "Unverified critical claim",
                    }
                ],
            )
            collated = protocol.collate(prepared, results)
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
                checked = protocol.collate(prepared, results)
                self.assertEqual(
                    len(checked["observation"]["synthesis"]["findings"]), findings
                )
                self.assertEqual("Advisory" in checked["rendered"]["body"], advisory)

    def test_selected_mechanical_commands_run_once_and_record_unavailable(self):
        command = {
            "id": "missing",
            "argv": ["/this/command/is/missing"],
            "cwd": ".",
            "timeout_seconds": 1,
        }
        with self.prepared_results([command]) as (prepared, _results):
            observations = prepared["bundle"]["test_observations"]
            self.assertEqual(len(observations), 1)
            self.assertEqual(observations[0]["status"], "unavailable")
            rejected_dir = pathlib.Path(prepared["directory"]).with_name("wrong-origin")
            rejected = protocol.prepare(
                prepared["repository_path"],
                {**self.identity, "repository": "other/repository"},
                rejected_dir,
            )
            self.assertEqual(rejected["reason"], "invalid_identity")
            self.assertFalse(rejected_dir.exists())
            for manifest in prepared["plan"]["manifests"]:
                self.assertEqual(
                    protocol.canonical(
                        protocol.capability_view(manifest["id"])["manifest"]
                    ),
                    protocol.canonical(manifest),
                )

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
            for field, value in (
                ("revision", 1),
                ("parent_hash", "f" * 64),
                ("bindings", []),
            ):
                changed = copy.deepcopy(prepared)
                changed["bundle"][field] = value
                changed["bundle"]["bundle_hash"] = protocol.digest(
                    {k: v for k, v in changed["bundle"].items() if k != "bundle_hash"}
                )
                with self.assertRaises(protocol.Invalid):
                    protocol.requests(changed)
            for field, value in (("bundle_revision", 1), ("answers", [])):
                changed = copy.deepcopy(results)
                changed[0][field] = value
                self.assertEqual(
                    protocol.collate(prepared, changed)["rendered"]["event"], "COMMENT"
                )
            self.assertEqual(
                protocol.collate(prepared, results + [results[0]])["rendered"]["event"],
                "COMMENT",
            )
            self.assertEqual(
                protocol.collate(
                    prepared, [{"schema": "kc-pr-flow.expansion-request/v1"}]
                )["reason"],
                "unsupported_expansion",
            )
            protocol.git(
                prepared["repository_path"],
                "checkout",
                "--detach",
                self.identity["base_sha"],
            )
            self.assertEqual(
                protocol.finish(prepared, results)["reason"], "identity_change"
            )

    def test_posting_invalidation_and_absent_outcome_are_read_only(self):
        with self.prepared_results() as (prepared, _results):
            event_file = next(
                (pathlib.Path(prepared["directory"]) / "state").rglob("events.jsonl")
            )
            original = event_file.read_bytes()
            self.assertIsNone(protocol.posting_projection(prepared, event_file))
            identity = prepared["identity"]
            event = protocol.runtime(
                prepared,
                "start",
                "--repo",
                identity["repository"],
                "--pr",
                identity["pr_number"],
                "--base",
                identity["base_sha"],
                "--head",
                identity["head_sha"],
                "--config-hash",
                identity["config_hash"],
            )
            identity = {**identity, "run_id": event["run_id"]}
            arguments = [
                identity[k]
                for k in (
                    "run_id",
                    "review_key",
                    "repository",
                    "pr_number",
                    "base_sha",
                    "head_sha",
                    "config_hash",
                )
            ]
            invalidated = subprocess.check_output(
                [
                    "bash",
                    "-c",
                    '. "$1"; shift; review_runtime_build_event "$@"',
                    "fixture",
                    str(HERE / "review-runtime.sh"),
                    *map(str, arguments),
                    "2",
                    event["occurred_at"],
                    "run.invalidated",
                    '{"reason":"head_moved"}',
                ]
            )
            snapshot = pathlib.Path(prepared["directory"]) / "invalidated.jsonl"
            snapshot.write_bytes(protocol.canonical(event) + b"\n" + invalidated)
            self.assertEqual(
                protocol.posting_projection(prepared, snapshot)["reason"], "head_moved"
            )
            self.assertEqual(event_file.read_bytes(), original)
            for field in (
                "review_key",
                "head_sha",
                "config_hash",
                "base_sha",
                "repository",
                "run_id",
            ):
                changed = copy.deepcopy(prepared)
                changed["identity"][field] = (
                    event["run_id"] if field == "run_id" else "mismatched"
                )
                with self.assertRaises(protocol.Invalid):
                    protocol.posting_projection(changed, snapshot)


if __name__ == "__main__":
    unittest.main()
