import contextlib
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
        call = {"type": "response_item", "payload": {"name": "followup_task", "call_id": "call-1", "arguments": json.dumps({"target": "producer"})}}
        raw.write_text(json.dumps(call) + "\n")
        ledger = self.root / "calls.json"
        ledger.write_text(json.dumps({"source_session": str(raw), "calls": [call]}))
        with self.assertRaisesRegex(ValueError, "arguments mismatch"):
            evidence.native_call(ledger, "followup_task", {"target": "wrong-owner"})
        call["payload"]["arguments"] = json.dumps({"target": "wrong-owner"})
        ledger.write_text(json.dumps({"source_session": str(raw), "calls": [call]}))
        with self.assertRaisesRegex(ValueError, "absent/altered"):
            evidence.native_call(ledger, "followup_task", {"target": "wrong-owner"})
        raw.unlink()
        with self.assertRaises(OSError):
            evidence.native_call(ledger, "followup_task", {"target": "producer"})


if __name__ == "__main__":
    unittest.main()
