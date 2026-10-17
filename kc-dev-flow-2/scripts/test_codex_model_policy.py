import json
import pathlib
import unittest


class CodexModelPolicyTest(unittest.TestCase):
    def test_policy_and_unchanged_role_declarations_agree(self):
        root = pathlib.Path(__file__).resolve().parents[1]
        policy = json.loads((root / "references/codex-model-policy-v1.json").read_text())
        self.assertEqual(policy["version"], 1)
        self.assertEqual(policy["models"], {
            "haiku": "gpt-6-luna", "sonnet": "gpt-6.1-sol", "opus": "gpt-6-astra"
        })
        self.assertEqual(policy["reasoning_defaults"]["implementation"], "medium")
        for stage in ("ideation", "validation", "observer", "evaluate-learning"):
            self.assertEqual(policy["reasoning_defaults"][stage], "high")
        for name, model, effort in (("observer", "sonnet", "high"),
                                    ("engineering-reviewer", "opus", "xhigh"),
                                    ("chief-engineer", "opus", "xhigh")):
            fields = dict(line.split(": ", 1) for line in
                          (root / f"agents/{name}.md").read_text().split("---", 2)[1].splitlines()
                          if ": " in line)
            self.assertEqual(fields["model"], model)
            self.assertEqual(fields["reasoning"], effort)


if __name__ == "__main__":
    unittest.main()
