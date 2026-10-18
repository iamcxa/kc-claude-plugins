import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path
import tempfile
import sys
import unittest
from unittest.mock import patch

import codex_dispatch as cd
import check_codex_dispatch_evidence as evidence


class CodexDispatchTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.policy = Path(__file__).resolve().parents[1] / "references/codex-model-policy-v1.json"
        self.caps = self.root / "caps.json"
        self.caps.write_text(json.dumps({"arguments": ["task_name", "message", "fork_turns", "model", "reasoning_effort"],
                                        "supported_models": {"gpt-6.1-sol": ["medium", "high"],
                                                             "gpt-6-astra": ["xhigh"], "gpt-6-luna": ["medium"]}}))
        self.workflow = self.root / "README.md"
        self.workflow.write_text("---\nstages:\n  defaults:\n    model: sonnet\n  states:\n    - name: implementation\n      context-sections: [Facts]\n    - name: validation\n      fresh: true\n---\n")
        self.helper = {"name": "Stock-Worker", "prompt": "unaltered\n  λ\\prompt\n", "model": None}

    def binding(self, stage="implementation", model="sonnet", effort=None):
        return cd.resolve(self.policy, self.caps, stage, model, effort)

    def test_real_policy_mapping_and_explicit_reasoning(self):
        for model, effort, expected in (("haiku", "medium", "gpt-6-luna"),
                                        ("sonnet", None, "gpt-6.1-sol"),
                                        ("opus", "xhigh", "gpt-6-astra")):
            self.assertEqual(self.binding(model=model, effort=effort)["model"], expected)
        self.assertEqual(self.binding()["reasoning_effort"], "medium")
        self.assertEqual(self.binding(stage="validation")["reasoning_effort"], "high")
        self.assertEqual(self.binding(effort="high")["reasoning_effort"], "high")

    def test_workflow_and_agents_use_resolver_and_preserve_bytes(self):
        self.assertEqual(cd.declaration(self.root, None, "implementation"), ("sonnet", None))
        agent = self.root / "agent.md"
        agent.write_text("---\nmodel: opus\nreasoning: xhigh\n---\nOriginal Claude wording\n")
        binding = cd.resolve(self.policy, self.caps, "reviewer", *cd.declaration(None, agent, "reviewer"))
        result = cd.convert(self.helper, binding)
        self.assertEqual(result["spawn_args"]["message"], self.helper["prompt"])
        self.assertEqual(result["helper_name"], self.helper["name"])
        self.assertEqual(result["spawn_args"]["fork_turns"], "none")
        self.assertEqual(result["spawn_args"]["model"], "gpt-6-astra")

    def test_reuse_compares_both_settings_policy_and_freshness(self):
        binding = self.binding()
        self.assertTrue(cd.convert(self.helper, binding, binding)["reuse"])
        for field in ("model", "reasoning_effort", "policy_id", "policy_sha256"):
            previous = dict(binding, **{field: "different"})
            self.assertFalse(cd.convert(self.helper, binding, previous)["reuse"])
        self.assertFalse(cd.convert(self.helper, binding, binding, fresh=True)["reuse"])

    def test_negative_mappings_and_missing_capabilities(self):
        for stage, model, effort in (("implementation", "unknown", None),
                                     ("implementation", "opus", "high"),
                                     ("implementation", "sonnet", "unknown"),
                                     ("missing", "sonnet", None)):
            with self.assertRaises(ValueError):
                self.binding(stage, model, effort)
        self.caps.write_text("{}")
        with self.assertRaises(ValueError):
            self.binding()
        with self.assertRaises(ValueError):
            cd.resolve(self.root / "missing", self.caps, "implementation", "sonnet", None)

    def invoke(self, args, text=""):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), patch("sys.stdin", io.StringIO(text)):
            code = cd.main(args)
        return code, out.getvalue(), err.getvalue()

    def test_refuse_before_stamped_build_and_no_fallback(self):
        args = ["build", "--policy", str(self.root / "missing"), "--capabilities", str(self.caps), "--",
                "--workflow-dir", str(self.root), "--stage", "implementation", "--stamp"]
        with patch("codex_dispatch.subprocess.run") as stock:
            code, out, err = self.invoke(args)
            self.assertEqual(code, 1)
            self.assertEqual(out, "")
            self.assertTrue(err)
            stock.assert_not_called()

    def test_stock_failure_preserves_exit_and_emits_no_spawn(self):
        args = ["build", "--policy", str(self.policy), "--capabilities", str(self.caps), "--",
                "--workflow-dir", str(self.root), "--stage", "implementation"]
        with patch("codex_dispatch.subprocess.run", return_value=cd.subprocess.CompletedProcess([], 7, "bad", "stock failed")):
            code, out, err = self.invoke(args)
        self.assertEqual((code, out), (7, ""))
        self.assertTrue(err.startswith("stock failed"))
        self.assertIn("partial state", err)
        self.assertIn("Do not resend automatically", err)

    def test_selected_success_and_no_policy_passthrough(self):
        args = ["build", "--policy", str(self.policy), "--capabilities", str(self.caps), "--",
                "--workflow-dir", str(self.root), "--stage", "implementation"]
        done = cd.subprocess.CompletedProcess([], 0, json.dumps(self.helper), "stock note")
        with patch("codex_dispatch.subprocess.run", return_value=done) as stock:
            code, out, _ = self.invoke(args)
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(out)["stock_helper"], self.helper)
            self.assertEqual(json.loads(out)["spawn_args"]["message"], self.helper["prompt"])
            self.assertIn("codex", stock.call_args.args[0])
            self.assertNotIn("input", stock.call_args.kwargs)
        for host in ("claude", "pi", "codex"):
            with patch("codex_dispatch.subprocess.run", return_value=cd.subprocess.CompletedProcess([], 9)) as stock:
                self.assertEqual(self.invoke(["build", "--", "--host", host])[0], 9)
                stock.assert_called_once_with(["spacedock", "dispatch", "build", "--host", host])

    def test_convert_rejects_empty_envelope_and_unsupported_declarations(self):
        for helper in ({}, {"name": "x", "prompt": 1}):
            with self.assertRaises(ValueError):
                cd.convert(helper, self.binding())
        self.workflow.write_text("---\nstages: {states: []}\n---\n")
        with self.assertRaises(ValueError):
            cd.declaration(self.root, None, "implementation")

    def test_advance_preserves_pointer_and_refuses_changed_binding_before_build(self):
        binding = self.binding()
        helper = {"prompt": "Advancing to next stage:\nRead original pointer", "model": None}
        result = cd.convert(helper, binding, binding, target="existing-worker")
        self.assertEqual(result["followup_args"], {"target": "existing-worker", "message": helper["prompt"]})
        self.assertNotIn("spawn_args", result)
        for previous, fresh in ((None, False), (self.binding(effort="high"), False), (binding, True)):
            with self.assertRaises(ValueError):
                cd.convert(helper, binding, previous, fresh, "existing-worker")
        previous_path = self.root / "previous.json"
        previous_path.write_text(json.dumps(self.binding(effort="high")))
        args = ["build", "--policy", str(self.policy), "--capabilities", str(self.caps),
                "--previous-binding", str(previous_path), "--target", "existing-worker", "--",
                "--workflow-dir", str(self.root), "--stage", "implementation", "--advance"]
        with patch("codex_dispatch.subprocess.run") as stock:
            code, out, _ = self.invoke(args)
            self.assertEqual((code, out), (1, ""))
            stock.assert_not_called()

    def test_advance_refusal_categories_and_recovery_before_stock(self):
        binding = self.binding()
        prior = self.root / "prior.json"
        base = ["build", "--policy", str(self.policy), "--capabilities", str(self.caps)]
        stock_args = ["--", "--workflow-dir", str(self.root), "--stage", "implementation", "--advance", "--stamp"]
        variants = [(["--previous-binding", str(prior)], binding),
                    (["--previous-binding", str(prior), "--target", "worker", "--fresh"], binding)]
        for field in ("model", "reasoning_effort", "policy_id", "policy_sha256"):
            variants.append((["--previous-binding", str(prior), "--target", "worker"], dict(binding, **{field: "changed"})))
        for options, previous in variants:
            prior.write_text(json.dumps(previous))
            with self.subTest(options=options, previous=previous), patch("codex_dispatch.subprocess.run") as stock:
                code, out, err = self.invoke(base + options + stock_args)
                self.assertEqual((code, out), (1, ""))
                self.assertIn("without --advance and without --target", err)
                stock.assert_not_called()

    def test_input_diagnostics_name_file_and_refuse_before_stock(self):
        prior = self.root / "prior.json"
        prior.write_text("[]")
        for category, path in (("policy", self.policy), ("capabilities", self.caps), ("previous binding", prior)):
            options = ["build", "--policy", str(self.policy), "--capabilities", str(self.caps)]
            if category == "policy":
                bad = self.root / "bad-policy.json"
                bad.write_text("{")
                options[2] = str(bad)
                path = bad
            elif category == "capabilities":
                self.caps.write_text("[]")
            else:
                self.caps.write_text(json.dumps({"arguments": ["task_name", "message", "fork_turns", "model", "reasoning_effort"],
                                                 "supported_models": {"gpt-6.1-sol": ["medium"]}}))
                options += ["--previous-binding", str(prior)]
            with patch("codex_dispatch.subprocess.run") as stock:
                code, out, err = self.invoke(options + ["--", "--workflow-dir", str(self.root), "--stage", "implementation"])
                self.assertEqual((code, out), (1, ""))
                self.assertIn(category, err)
                self.assertIn(str(path), err)
                stock.assert_not_called()

    def test_invalid_stock_output_is_retained_without_dispatch_args(self):
        evidence = self.root / "stock-output.json"
        args = ["build", "--policy", str(self.policy), "--capabilities", str(self.caps),
                "--stock-output", str(evidence), "--", "--workflow-dir", str(self.root), "--stage", "implementation"]
        for raw in ("not-json", "[]", json.dumps({"name": "worker", "prompt": ""})):
            with patch("codex_dispatch.subprocess.run", return_value=cd.subprocess.CompletedProcess([], 0, raw, "")):
                code, out, err = self.invoke(args)
            self.assertEqual((code, out), (1, ""))
            self.assertEqual(evidence.read_text(), raw)
            self.assertIn("stock conversion", err)
            self.assertIn("partial state", err)

    def test_no_policy_real_process_preserves_stdin_args_output_and_exit(self):
        stock = self.root / "stock"
        stock.write_text("#!/usr/bin/env python3\nimport json, sys\nprint(json.dumps(sys.argv[1:]))\nsys.stdout.flush()\nsys.stdout.buffer.write(sys.stdin.buffer.read())\nsys.stderr.write('stock-stderr')\nsys.exit(9)\n")
        stock.chmod(0o755)
        wrapper = Path(cd.__file__)
        for host in ("claude", "pi", "codex"):
            result = cd.subprocess.run([sys.executable, str(wrapper), "build", "--spacedock", str(stock), "--", "--host", host, "--scope-notes", "a b"],
                                       input=b"\x00stdin\n", capture_output=True)
            line, payload = result.stdout.split(b"\n", 1)
            self.assertEqual(json.loads(line), ["dispatch", "build", "--host", host, "--scope-notes", "a b"])
            self.assertEqual((result.returncode, payload, result.stderr), (9, b"\x00stdin\n", b"stock-stderr"))

    def test_operator_high_override_does_not_change_packaged_defaults(self):
        policy = json.loads(self.policy.read_text())
        policy["id"] = "operator-local-sol-high"
        policy["reasoning_defaults"]["implementation"] = "high"
        local = self.root / "policy-high.json"
        local.write_text(json.dumps(policy))
        result = cd.resolve(local, self.caps, "implementation", "sonnet", None)
        self.assertEqual((result["model"], result["reasoning_effort"]), ("gpt-6.1-sol", "high"))
        self.assertEqual(self.binding()["reasoning_effort"], "medium")

    def test_evidence_rejects_altered_native_record_or_arguments(self):
        raw = self.root / "host.jsonl"
        call = {"type": "response_item", "payload": {"type": "function_call", "namespace": "collaboration", "name": "followup_task", "call_id": "call-1", "arguments": json.dumps({"target": "producer", "message": "fixture pointer"})}}
        result = {"type": "response_item", "payload": {"type": "function_call_output", "call_id": "call-1", "output": ""}}
        raw.write_text(json.dumps(call) + "\n" + json.dumps(result) + "\n")
        ledger = self.root / "calls.json"
        ledger.write_text(json.dumps({"source_session": str(raw), "calls": [call]}))
        with self.assertRaisesRegex(ValueError, "arguments mismatch"):
            evidence.native_call(ledger, "followup_task", {"target": "wrong-owner", "message": "fixture pointer"})
        call["payload"]["arguments"] = json.dumps({"target": "wrong-owner", "message": "fixture pointer"})
        ledger.write_text(json.dumps({"source_session": str(raw), "calls": [call]}))
        with self.assertRaisesRegex(ValueError, "absent/altered"):
            evidence.native_call(ledger, "followup_task", {"target": "wrong-owner"})
        raw.unlink()
        with self.assertRaises(OSError):
            evidence.native_call(ledger, "followup_task", {"target": "producer"})


class EvidenceRouteTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / ".worktrees/pilot"
        self.repo.mkdir(parents=True)
        self.git("init", "-b", "pilot")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "user.name", "Disposable fixture")
        wrapper = self.repo / "kc-dev-flow-2/scripts/codex_dispatch.py"
        wrapper.parent.mkdir(parents=True)
        wrapper.write_text("disposable wrapper bytes\n")
        self.git("add", "kc-dev-flow-2/scripts/codex_dispatch.py")
        self.git("commit", "-m", "fixture base")
        base = self.git("rev-parse", "HEAD")
        (self.repo / "kc-dev-flow-2/fixture.txt").write_text("disposable candidate\n")
        self.git("add", "kc-dev-flow-2/fixture.txt")
        self.git("commit", "-m", "fixture candidate")
        candidate = self.git("rev-parse", "HEAD")
        self.producer, marker = "/root/disposable_producer", "DISPOSABLE-ACK"
        binding = {"policy_id": "fixture-policy", "policy_sha256": "", "requested_model": "sonnet",
                   "requested_reasoning": None, "model": "gpt-6.1-sol", "reasoning_effort": "high"}
        policy = {"version": 1, "id": "fixture-policy", "models": {"sonnet": "gpt-6.1-sol"}, "reasoning_defaults": {"implementation": "high"}}
        self.write("policy", policy)
        binding["policy_sha256"] = hashlib.sha256((self.root / "policy.json").read_bytes()).hexdigest()
        self.write("capabilities", {"arguments": ["task_name", "message", "fork_turns", "model", "reasoning_effort"], "supported_models": {"gpt-6.1-sol": ["high"]}})
        self.requests = {"spawn_agent": {"task_name": "disposable_producer", "message": "original spawn pointer", "fork_turns": "none", "model": "gpt-6.1-sol", "reasoning_effort": "high"},
                         "followup_task": {"target": self.producer, "message": "original followup pointer"}}
        self.write("initial-wrapper", {"spawn_args": self.requests["spawn_agent"], "helper_name": "fixture-helper", "stock_helper": {"name": "fixture-helper", "prompt": "original spawn pointer"}, "binding": binding})
        self.write("host-receipt", {"returned_handle": self.producer, "binding": binding, "requested_spawn_args": self.requests["spawn_agent"]})
        self.write("followup-wrapper", {"followup_args": self.requests["followup_task"], "stock_helper": {"prompt": "original followup pointer"}, "binding": binding, "reuse": True})
        entity = self.root / "entity.md"
        entity.write_text("---\nstatus: implementation\nworktree: .worktrees/pilot\n---\n")
        owner = {"entity_file": str(entity), "stage": "implementation", "code_worktree": str(self.repo), "branch": "pilot", "handle": self.producer,
                 "frontmatter_sha256": hashlib.sha256(entity.read_text().split("---", 2)[1].encode()).hexdigest()}
        self.write("followup-receipt", dict(owner, candidate=candidate, wrapper_sha256=hashlib.sha256(wrapper.read_bytes()).hexdigest(), binding=binding,
                                           marker=marker, completion_turn_id="followup-turn", before=owner, after=owner,
                                           before_entity_snapshot=str(entity), after_entity_snapshot=str(entity)))
        self.write("baseline", {"base": base, "protected_base_git_objects": {}, "stock_files": []})
        child = self.root / "child.jsonl"
        self.jsonl(child, [{"type": "session_meta", "payload": {"id": "fixture-session", "source": {"subagent": {"thread_spawn": {"agent_path": self.producer, "parent_thread_id": "fixture-parent"}}}}},
                           *[{"type": "turn_context", "timestamp": at, "payload": {"turn_id": t, "model": "gpt-6.1-sol", "effort": "high"}} for t, at in (("initial-turn", "2000-01-01T00:00:00.050Z"), ("followup-turn", "2000-01-01T00:00:02.050Z"))],
                           {"type": "response_item", "payload": {"type": "message", "role": "assistant", "internal_chat_message_metadata_passthrough": {"turn_id": "followup-turn"}, "content": [{"type": "output_text", "text": marker}]}}])
        self.write("observed", [{"handle": self.producer, "session_id": "fixture-session", "session_path": str(child), "turns": [{"turn_id": "initial-turn", "model": "gpt-6.1-sol", "reasoning_effort": "high"}]}])
        self.native("spawn_agent", outputs=[json.dumps({"task_name": self.producer})])
        self.native("followup_task", outputs=[""])
        self.args = ["--repo", str(self.repo), "--base", base, "--candidate", candidate, "--entity", str(entity), "--marker", marker]
        for name in ("baseline", "initial-wrapper", "host-receipt", "observed", "native-calls", "followup-wrapper", "followup-receipt", "followup-native-calls", "policy", "capabilities"):
            self.args += ["--" + name, str(self.root / (name + ".json"))]

    def git(self, *args):
        return cd.subprocess.run(["git", "-C", str(self.repo), "-c", "core.hooksPath=/dev/null", *args], capture_output=True, text=True, check=True).stdout.strip()

    def write(self, name, data):
        (self.root / (name + ".json")).write_text(json.dumps(data))

    def jsonl(self, path, rows):
        path.write_text("".join(json.dumps(row) + "\n" for row in rows))

    def native(self, name, arguments=None, outputs=()):
        at = "2000-01-01T00:00:00.000Z" if name == "spawn_agent" else "2000-01-01T00:00:02.000Z"
        done_at = "2000-01-01T00:00:00.200Z" if name == "spawn_agent" else "2000-01-01T00:00:02.200Z"
        call = {"type": "response_item", "timestamp": at, "payload": {"type": "function_call", "namespace": "collaboration", "name": name, "call_id": name + "-call",
                                                     "arguments": json.dumps(self.requests[name] if arguments is None else arguments)}}
        raw = self.root / (name + ".jsonl")
        self.jsonl(raw, [{"type": "session_meta", "payload": {"id": "fixture-parent"}}, call,
                         *[{"type": "response_item", "timestamp": done_at, "payload": {"type": "function_call_output", "call_id": name + "-call", "output": output}} for output in outputs]])
        self.write("native-calls" if name == "spawn_agent" else "followup-native-calls", {"source_session": str(raw), "calls": [call]})

    def invoke(self):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = evidence.main(self.args)
        return code, out.getvalue(), err.getvalue()

    def test_plaintext_matching_requests_and_successful_results_pass_fixture_control(self):
        self.assertEqual(self.invoke()[0], 0)

    def test_async_completion_in_post_followup_observation_still_passes(self):
        observed = evidence.read(self.root / "observed.json")
        observed[0]["turns"].append({"turn_id": "followup-turn", "model": "gpt-6.1-sol", "reasoning_effort": "high"})
        self.write("observed", observed)
        self.assertEqual(self.invoke()[0], 0)

    def test_completion_starting_after_tool_result_also_passes(self):
        child = self.root / "child.jsonl"
        rows = list(evidence.records(child))
        rows[2]["timestamp"] = "2000-01-01T00:00:02.300Z"
        self.jsonl(child, rows)
        self.assertEqual(self.invoke()[0], 0)

    def test_noninitial_pre_request_turn_cannot_certify_followup(self):
        child = self.root / "child.jsonl"
        rows = list(evidence.records(child))
        earlier, ack = copy.deepcopy(rows[2]), copy.deepcopy(rows[3])
        earlier["payload"]["turn_id"], earlier["timestamp"] = "earlier-turn", "2000-01-01T00:00:01.000Z"
        ack["payload"]["internal_chat_message_metadata_passthrough"]["turn_id"] = "earlier-turn"
        rows[3]["payload"]["content"][0]["text"] = "Current followup contains no acknowledgement."
        self.jsonl(child, [rows[0], rows[1], earlier, ack, rows[2], rows[3]])
        receipt = evidence.read(self.root / "followup-receipt.json")
        receipt["completion_turn_id"] = "earlier-turn"
        self.write("followup-receipt", receipt)
        observed = evidence.read(self.root / "observed.json")
        observed[0]["turns"].append({"turn_id": "earlier-turn", "model": "gpt-6.1-sol", "reasoning_effort": "high"})
        self.write("observed", observed)
        self.assertEqual(self.invoke()[0], 1)

    def test_repeated_old_context_cannot_make_an_existing_turn_new(self):
        child = self.root / "child.jsonl"
        rows = list(evidence.records(child))
        old = copy.deepcopy(rows[2])
        old["timestamp"] = "2000-01-01T00:00:01.000Z"
        self.jsonl(child, [rows[0], rows[1], old, rows[2], rows[3]])
        self.assertEqual(self.invoke()[0], 1)

    def test_blank_markers_hold(self):
        for marker in ("", " ", "\t"):
            with self.subTest(marker=repr(marker)):
                self.args[self.args.index("--marker") + 1] = marker
                receipt = evidence.read(self.root / "followup-receipt.json")
                receipt["marker"] = marker
                self.write("followup-receipt", receipt)
                child = self.root / "child.jsonl"
                rows = list(evidence.records(child))
                rows[3]["payload"]["content"][0]["text"] = "Ordinary prose with spaces\tand a tab."
                self.jsonl(child, rows)
                self.assertEqual(self.invoke()[0], 1)

    def test_nonblank_marker_bytes_are_not_trimmed(self):
        marker = " DISPOSABLE-ACK "
        self.args[self.args.index("--marker") + 1] = marker
        receipt = evidence.read(self.root / "followup-receipt.json")
        receipt["marker"] = marker
        self.write("followup-receipt", receipt)
        child = self.root / "child.jsonl"
        rows = list(evidence.records(child))
        rows[3]["payload"]["content"][0]["text"] = marker
        self.jsonl(child, rows)
        self.assertEqual(self.invoke()[0], 0)
        rows[3]["payload"]["content"][0]["text"] = marker.strip()
        self.jsonl(child, rows)
        self.assertEqual(self.invoke()[0], 1)

    def test_missing_invalid_or_naive_request_time_holds(self):
        for at in (None, "not-a-time", "2000-01-01T00:00:02"):
            with self.subTest(at=at):
                self.native("followup_task", outputs=[""])
                ledger = evidence.read(self.root / "followup-native-calls.json")
                raw = Path(ledger["source_session"])
                rows = list(evidence.records(raw))
                rows[1]["timestamp"] = at
                self.jsonl(raw, rows)
                self.assertEqual(self.invoke()[0], 1)

    def test_missing_invalid_naive_or_tied_completion_time_holds(self):
        child = self.root / "child.jsonl"
        base = list(evidence.records(child))
        for at in (None, "not-a-time", "2000-01-01T00:00:02.050", "2000-01-01T00:00:02.000Z"):
            with self.subTest(at=at):
                rows = copy.deepcopy(base)
                rows[2]["timestamp"] = at
                self.jsonl(child, rows)
                self.assertEqual(self.invoke()[0], 1)

    def test_reversed_repeated_context_times_hold(self):
        child = self.root / "child.jsonl"
        rows = list(evidence.records(child))
        reverse = copy.deepcopy(rows[2])
        reverse["timestamp"] = "2000-01-01T00:00:02.010Z"
        self.jsonl(child, [*rows[:3], reverse, rows[3]])
        self.assertEqual(self.invoke()[0], 1)

    def test_changed_spawn_assignment_is_not_certified(self):
        self.native("spawn_agent", dict(self.requests["spawn_agent"], message="different assignment"), [json.dumps({"task_name": self.producer})])
        self.assertEqual(self.invoke()[0], 1)

    def test_changed_followup_assignment_is_not_certified(self):
        self.native("followup_task", dict(self.requests["followup_task"], message="different assignment"), [""])
        self.assertEqual(self.invoke()[0], 1)

    def test_initial_turn_marker_cannot_certify_followup(self):
        child = self.root / "child.jsonl"
        rows = list(evidence.records(child))
        rows[3]["payload"]["internal_chat_message_metadata_passthrough"]["turn_id"] = "initial-turn"
        self.jsonl(child, [rows[0], rows[1], rows[3], rows[2]])
        self.assertEqual(self.invoke()[0], 1)

    def test_later_turn_marker_cannot_certify_followup(self):
        child = self.root / "child.jsonl"
        rows = list(evidence.records(child))
        rows[3]["payload"]["internal_chat_message_metadata_passthrough"]["turn_id"] = "later-turn"
        later = {"type": "turn_context", "payload": {"turn_id": "later-turn", "model": "gpt-6.1-sol", "effort": "high"}}
        self.jsonl(child, [*rows[:3], later, rows[3]])
        self.assertEqual(self.invoke()[0], 1)

    def test_marker_without_turn_metadata_holds(self):
        child = self.root / "child.jsonl"
        rows = list(evidence.records(child))
        rows[3]["payload"].pop("internal_chat_message_metadata_passthrough")
        self.jsonl(child, rows)
        self.assertEqual(self.invoke()[0], 1)

    def test_returned_handle_cannot_select_a_child_from_another_parent(self):
        child = self.root / "child.jsonl"
        rows = list(evidence.records(child))
        rows[0]["payload"]["source"]["subagent"]["thread_spawn"]["parent_thread_id"] = "unrelated-parent"
        self.jsonl(child, rows)
        self.assertEqual(self.invoke()[0], 1)

    def test_encrypted_spawn_assignment_holds_with_explanation(self):
        self.native("spawn_agent", dict(self.requests["spawn_agent"], message="gAAAA_DISPOSABLE_OPAQUE_CONTENT"), [json.dumps({"task_name": self.producer})])
        code, out, err = self.invoke()
        self.assertEqual((code, out), (1, ""))
        self.assertIn("encrypted", err)
        self.assertIn("call_id", err)

    def test_missing_error_duplicate_and_wrong_spawn_results_are_not_certified(self):
        for outputs in ([], ['{"error":"fixture failure"}'], ['{"task_name":"/root/other_fixture_worker"}'],
                        [json.dumps({"task_name": self.producer})] * 2):
            with self.subTest(outputs=outputs):
                self.native("spawn_agent", outputs=outputs)
                self.assertEqual(self.invoke()[0], 1)

    def test_missing_error_and_duplicate_followup_results_are_not_certified(self):
        for outputs in ([], ["Error: fixture failure"], ['{"error":"fixture failure"}'], ["", ""]):
            with self.subTest(outputs=outputs):
                self.native("followup_task", outputs=outputs)
                self.assertEqual(self.invoke()[0], 1)


if __name__ == "__main__":
    unittest.main()
