import contextlib
import io
import json
import pathlib
import tempfile
import unittest

import codex_model_policy

ROOT = pathlib.Path(__file__).resolve().parents[1]
POLICY = ROOT / "references/codex-model-policy-v1.json"
README = """---
stages:
  defaults:
    model: sonnet
  states:
    - name: implementation
    - name: ideation
      model: opus
    - name: validation
      reasoning: xhigh
    - name: odd
      model: gpt-x
---
"""


def run(*argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = codex_model_policy.main(list(argv))
    return code, out.getvalue(), err.getvalue()


class CodexModelPolicyTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.wf = pathlib.Path(tmp.name)
        (self.wf / "README.md").write_text(README)

    def stage(self, name, *extra, policy=POLICY):
        return run("--policy", str(policy), "--workflow-dir", str(self.wf), "--stage", name, *extra)

    def test_stage_default_and_declared_model(self):
        code, out, _ = self.stage("implementation")
        self.assertEqual((code, json.loads(out)), (0, {"model": "gpt-6.1-sol", "reasoning_effort": "medium"}))
        self.assertEqual(json.loads(self.stage("ideation")[1]),
                         {"model": "gpt-6-astra", "reasoning_effort": "high"})

    def test_declared_reasoning_beats_policy_default(self):
        self.assertEqual(json.loads(self.stage("validation")[1])["reasoning_effort"], "xhigh")

    def test_flags_form(self):
        self.assertEqual(self.stage("implementation", "--flags")[1],
                         "--model gpt-6.1-sol --reasoning-effort medium\n")

    def test_agent_file(self):
        code, out, _ = run("--policy", str(POLICY), "--agent-file", str(ROOT / "agents/chief-engineer.md"))
        self.assertEqual((code, json.loads(out)), (0, {"model": "gpt-6-astra", "reasoning_effort": "xhigh"}))

    def test_unmapped_model_is_an_error_naming_it(self):
        code, out, err = self.stage("odd")
        self.assertEqual((code, out), (1, ""))
        self.assertIn("gpt-x", err)

    def test_missing_effort_is_an_error(self):
        policy = self.wf / "policy.json"
        policy.write_text(json.dumps({"models": {"sonnet": "m"}, "reasoning_defaults": {}}))
        code, out, err = self.stage("implementation", policy=policy)
        self.assertEqual((code, out), (1, ""))
        self.assertIn("implementation", err)

    def refused(self, readme, stage, needle):
        (self.wf / "README.md").write_text(readme)
        code, out, err = self.stage(stage)
        self.assertEqual((code, out), (1, ""))
        self.assertIn(needle, err)

    def test_duplicate_stage_is_refused(self):
        self.refused(README.replace("    - name: odd", "    - name: validation\n    - name: odd"),
                     "validation", "duplicate stage 'validation'")

    def test_duplicate_field_is_refused(self):
        self.refused(README.replace("      reasoning: xhigh", "      reasoning: xhigh\n      reasoning: low"),
                     "validation", "duplicate reasoning")
        self.refused(README.replace("    model: sonnet", "    model: sonnet\n    model: opus"),
                     "implementation", "duplicate model")


if __name__ == "__main__":
    unittest.main()
