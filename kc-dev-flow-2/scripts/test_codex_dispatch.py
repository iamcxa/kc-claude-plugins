import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import codex_dispatch as cd


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
        with self.assertRaises(OSError):
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
        self.assertEqual((code, out, err), (7, "", "stock failed"))

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
