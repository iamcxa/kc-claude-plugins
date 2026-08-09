#!/usr/bin/env python3
"""Contract tests for source-side kc-dev-flow improvement intake."""

from __future__ import annotations

import ast
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("improvement-intake.py")


def snapshot(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def handoff(**overrides: object) -> dict[str, object]:
    value: dict[str, object] = {
        "schema": "kc-dev-flow-improvement-handoff/v1",
        "source_policy_revision": "kc-dev-flow-v1.3.0",
        "failure_shape": "behavioral-gate-closed-from-text",
        "finding_kind_hint": "enforcement-gap",
        "landing_target_hint": "plugin-enforcement",
        "existing_rule": "kernel.md#behavioral-validity",
        "summary": "Behavioral gate accepted text-only evidence.",
        "expected_value": "Reject closure evidence that never observed behavior.",
        "cost": "Add one source-side admissibility control and focused tests.",
        "disproof_hook": "A text-only closure attempt is refused before done.",
        "duplicate_search": [
            "kernel.md behavioral validity",
            "work-control-profile.md review convergence",
        ],
        "observations": [
            {
                "id": "src-a1b2c3d4e5f6-1111111111111111",
                "evidence": "A behavioral issue closed from instruction assertions.",
                "impact": "The reported behavior remained unobserved at closure.",
            }
        ],
    }
    value.update(overrides)
    return value


class ImprovementIntakeTest(unittest.TestCase):
    def run_intake(
        self, values: list[dict[str, object]]
    ) -> tuple[subprocess.CompletedProcess[str], Path, dict[str, str]]:
        temporary = tempfile.TemporaryDirectory(prefix="kc-dev-flow-intake-")
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        paths: list[Path] = []
        for index, value in enumerate(values, start=1):
            path = root / f"handoff-{index}.json"
            path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
            paths.append(path)
        before = snapshot(root)
        command = [sys.executable, str(SCRIPT)]
        for path in paths:
            command.extend(["--handoff", str(path)])
        result = subprocess.run(
            command,
            cwd=root,
            capture_output=True,
            text=True,
            env={**os.environ, "GH_TOKEN": "must-not-be-used"},
            check=False,
        )
        return result, root, before

    def parse_success(
        self, values: list[dict[str, object]]
    ) -> tuple[dict[str, object], Path, dict[str, str]]:
        result, root, before = self.run_intake(values)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout), root, before

    def test_renders_proposal_and_counts_distinct_observations_without_writes(self) -> None:
        second = handoff(
            summary="Text assertions were accepted as behavioral closure evidence.",
            observations=[
                {
                    "id": "src-0f1e2d3c4b5a-2222222222222222",
                    "evidence": "A second adopter accepted instruction assertions.",
                    "impact": "The same failure shape reached a second closure.",
                },
            ],
        )

        proposal, root, before = self.parse_success([handoff(), second, handoff()])

        self.assertEqual(proposal["schema"], "kc-dev-flow-improvement-proposal/v1")
        self.assertRegex(str(proposal["fingerprint"]), r"^[a-f0-9]{64}$")
        self.assertEqual(proposal["recurrence"], 2)
        self.assertEqual(proposal["distinct_sources"], 2)
        self.assertEqual(
            proposal["observation_ids"],
            [
                "src-0f1e2d3c4b5a-2222222222222222",
                "src-a1b2c3d4e5f6-1111111111111111",
            ],
        )
        self.assertEqual(len(proposal["observations"]), 2)
        self.assertEqual(
            proposal["observations"][0]["evidence"],
            "A second adopter accepted instruction assertions.",
        )
        self.assertEqual(
            proposal["duplicate_search"],
            [
                "kernel.md behavioral validity",
                "work-control-profile.md review convergence",
            ],
        )
        self.assertEqual(
            proposal["summaries"],
            [
                "Behavioral gate accepted text-only evidence.",
                "Text assertions were accepted as behavioral closure evidence.",
            ],
        )
        self.assertEqual(
            proposal["expected_values"],
            ["Reject closure evidence that never observed behavior."],
        )
        self.assertEqual(
            proposal["costs"],
            ["Add one source-side admissibility control and focused tests."],
        )
        self.assertEqual(
            proposal["disproof_hooks"],
            ["A text-only closure attempt is refused before done."],
        )
        self.assertEqual(proposal["finding_kind_hint"], "enforcement-gap")
        self.assertEqual(proposal["landing_target_hint"], "plugin-enforcement")
        self.assertEqual(proposal["authorized_action"], "captain-review-only")
        self.assertIn("2 distinct field observations", proposal["body"])
        self.assertIn("A second adopter accepted instruction assertions", proposal["body"])
        self.assertIn("## Duplicate search", proposal["body"])
        self.assertIn("adopter-reported transport counts", proposal["body"].lower())
        self.assertIn("not source-verified", proposal["body"])
        self.assertIn("<!-- kc-dev-flow-improvement:v1:", proposal["body"])
        self.assertEqual(snapshot(root), before)

    def test_fingerprint_is_stable_across_wording_and_classification_changes(self) -> None:
        first, _, _ = self.parse_success([handoff()])
        changed, _, _ = self.parse_success(
            [
                handoff(
                    finding_kind_hint="rule-gap",
                    landing_target_hint="kernel",
                    summary="Closure evidence described text but not behavior.",
                    expected_value="Keep behavior unclosed until it is observed.",
                    cost="Change one portable clause after source review.",
                )
            ]
        )
        self.assertEqual(first["fingerprint"], changed["fingerprint"])
        self.assertEqual(
            first["fingerprint"],
            "24074cc6ff867f32d32f79db4d975405be4f0bd487850801d2d7291103ee93e3",
        )

        cross_release, _, _ = self.parse_success(
            [
                handoff(
                    source_policy_revision="a" * 40,
                    observations=[
                        {
                            "id": "src-0f1e2d3c4b5a-3333333333333333",
                            "evidence": "A different occurrence showed the same failure shape.",
                            "impact": "Recurrence must survive a policy release boundary.",
                        }
                    ],
                )
            ]
        )
        self.assertEqual(first["fingerprint"], cross_release["fingerprint"])

        different, _, _ = self.parse_success(
            [handoff(failure_shape="consumer-runtime-not-reobserved")]
        )
        self.assertNotEqual(first["fingerprint"], different["fingerprint"])

    def test_output_is_independent_of_handoff_argument_order(self) -> None:
        first = handoff()
        second = handoff(
            summary="Text assertions were accepted as behavioral closure evidence.",
            expected_value="Behavior remains open until a valid instrument observes it.",
            cost="Add one bounded source control.",
            disproof_hook="A valid behavioral observation closes the same gate.",
            observations=[
                {
                    "id": "src-0f1e2d3c4b5a-2222222222222222",
                    "evidence": "A second adopter accepted instruction assertions.",
                    "impact": "The same failure shape reached a second closure.",
                }
            ],
        )
        forward, _, _ = self.parse_success([first, second])
        reverse, _, _ = self.parse_success([second, first])
        self.assertEqual(forward, reverse)

    def test_conflicting_hints_are_reported_for_source_judgment(self) -> None:
        proposal, _, _ = self.parse_success(
            [
                handoff(),
                handoff(
                    finding_kind_hint="rule-gap",
                    landing_target_hint="kernel",
                    observations=[
                        {
                            "id": "src-0f1e2d3c4b5a-2222222222222222",
                            "evidence": "A second source classified the same failure differently.",
                            "impact": "Placement needs source-maintainer judgment.",
                        }
                    ],
                ),
            ]
        )
        self.assertEqual(proposal["finding_kind_hint"], "requires-source-judgment")
        self.assertEqual(proposal["landing_target_hint"], "requires-source-judgment")
        self.assertEqual(
            proposal["finding_kind_hints"], ["enforcement-gap", "rule-gap"]
        )
        self.assertEqual(
            proposal["landing_target_hints"], ["kernel", "plugin-enforcement"]
        )

    def test_rejects_unsafe_or_unstructured_handoffs(self) -> None:
        unsafe_values = [
            "Observed at /Users/operator/private-project",
            "Contact ops@acme-internal.example about this failure",
            "Observed at gitlab.acme.internal/platform/api",
            "Observed under /opt/customer/runtime/state",
            "Observed under D:\\customer\\runtime\\state",
            "Observed under \\\\corp-fileserver\\builds\\out",
            "Observed at 10.20.30.40:8080 during the gate run",
            "Observed at [fd00::42]:5432 during the gate run",
            "Observed at acme.ai/platform during the gate run",
            "Observed under $HOME/private-project during the gate run",
            "Observed api_key=private-value during the run",
            "The run logged ghp_abcdefghijklmnopqrstuvwxyz123456",
        ]
        for unsafe_value in unsafe_values:
            for field in [
                "existing_rule",
                "summary",
                "expected_value",
                "cost",
                "disproof_hook",
            ]:
                with self.subTest(field=field, unsafe_value=unsafe_value):
                    result, _, _ = self.run_intake(
                        [handoff(**{field: unsafe_value})]
                    )
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("unsafe or adopter-specific text", result.stderr)

            result, _, _ = self.run_intake(
                [handoff(duplicate_search=[unsafe_value])]
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("unsafe or adopter-specific text", result.stderr)

            for observation_field in ["evidence", "impact"]:
                observation = {
                    "id": "src-a1b2c3d4e5f6-1111111111111111",
                    "evidence": "A behavioral issue closed from instruction assertions.",
                    "impact": "The reported behavior remained unobserved at closure.",
                }
                observation[observation_field] = unsafe_value
                result, _, _ = self.run_intake(
                    [handoff(observations=[observation])]
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("unsafe or adopter-specific text", result.stderr)

        incomplete = handoff()
        incomplete.pop("disproof_hook")
        result, _, _ = self.run_intake([incomplete])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("fields must match", result.stderr)

    def test_rejects_mixed_failure_shapes_and_conflicting_observation_ids(self) -> None:
        result, _, _ = self.run_intake(
            [handoff(), handoff(failure_shape="consumer-runtime-not-reobserved")]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("one failure shape", result.stderr)

        conflicting = handoff(
            observations=[
                {
                    "id": "src-a1b2c3d4e5f6-1111111111111111",
                    "evidence": "Different evidence under the same observation identifier.",
                    "impact": "The collision must fail closed.",
                }
            ]
        )
        result, _, _ = self.run_intake([handoff(), conflicting])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("observation id collision", result.stderr)

    def test_rejects_malformed_enum_revision_shape_and_observation_id(self) -> None:
        cases = [
            ("finding_kind_hint", "kernel-required", "finding_kind_hint"),
            ("landing_target_hint", "source", "landing_target_hint"),
            ("source_policy_revision", "main", "source_policy_revision"),
            ("failure_shape", "Maybe this happened", "failure_shape"),
        ]
        for field, value, message in cases:
            result, _, _ = self.run_intake([handoff(**{field: value})])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(message, result.stderr)

        for field in ["finding_kind_hint", "landing_target_hint"]:
            result, _, _ = self.run_intake([handoff(**{field: []})])
            self.assertEqual(result.returncode, 2)
            self.assertIn(field, result.stderr)
            self.assertNotIn("Traceback", result.stderr)

        malformed_observation = handoff(
            observations=[
                {
                    "id": "observation-one",
                    "evidence": "A behavioral issue closed from instruction assertions.",
                    "impact": "The reported behavior remained unobserved at closure.",
                }
            ]
        )
        result, _, _ = self.run_intake([malformed_observation])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("observation id", result.stderr)

        malformed_digest = handoff(
            observations=[
                {
                    "id": "src-a1b2c3d4e5f6-abcdef012345678",
                    "evidence": "A behavioral issue closed from instruction assertions.",
                    "impact": "The reported behavior remained unobserved at closure.",
                }
            ]
        )
        result, _, _ = self.run_intake([malformed_digest])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("observation id", result.stderr)

        mixed_namespaces = handoff(
            observations=[
                {
                    "id": "src-a1b2c3d4e5f6-1111111111111111",
                    "evidence": "A behavioral issue closed from instruction assertions.",
                    "impact": "The reported behavior remained unobserved at closure.",
                },
                {
                    "id": "src-0f1e2d3c4b5a-2222222222222222",
                    "evidence": "A second namespace appeared in one adopter handoff.",
                    "impact": "The handoff could inflate distinct source recurrence.",
                }
            ]
        )
        result, _, _ = self.run_intake([mixed_namespaces])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("one source namespace", result.stderr)

    def test_intake_source_has_no_network_process_or_write_primitives(self) -> None:
        tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
        forbidden_modules = {
            "asyncio",
            "ctypes",
            "ftplib",
            "http",
            "importlib",
            "multiprocessing",
            "os",
            "requests",
            "shutil",
            "smtplib",
            "socket",
            "subprocess",
            "urllib",
        }
        forbidden_calls = {
            "chmod",
            "check_call",
            "check_output",
            "connect",
            "copy",
            "eval",
            "exec",
            "hardlink_to",
            "import_module",
            "mkdir",
            "makedirs",
            "open",
            "popen",
            "Popen",
            "remove",
            "rename",
            "replace",
            "rmtree",
            "rmdir",
            "run",
            "symlink_to",
            "system",
            "touch",
            "truncate",
            "unlink",
            "urlopen",
            "write_bytes",
            "write_text",
            "__import__",
        }
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots = {alias.name.split(".", 1)[0] for alias in node.names}
                self.assertTrue(roots.isdisjoint(forbidden_modules), roots)
            elif isinstance(node, ast.ImportFrom) and node.module:
                root = node.module.split(".", 1)[0]
                self.assertNotIn(root, forbidden_modules)
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    self.assertNotIn(node.func.id, forbidden_calls)
                elif isinstance(node.func, ast.Attribute):
                    self.assertNotIn(node.func.attr, forbidden_calls)

    def test_non_utf8_handoff_fails_with_a_controlled_error(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="kc-dev-flow-intake-utf8-")
        self.addCleanup(temporary.cleanup)
        path = Path(temporary.name) / "handoff.json"
        path.write_bytes("not utf eight".encode("utf-16"))
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--handoff", str(path)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("improvement intake:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
