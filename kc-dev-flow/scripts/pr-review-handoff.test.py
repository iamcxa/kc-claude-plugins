#!/usr/bin/env python3
"""Focused contract for the exact-SHA kc-dev-flow → kc-pr-review handoff."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("pr-review-handoff.py")
REPO = "iamcxa/kc-claude-plugins"
BASE = "99b6747b4521b878cb2b0cb3f34d1c5049a0cd67"
HEAD = "722efe6508627bd4abac7f27a4260cd883b5ebec"


class PrReviewHandoffTest(unittest.TestCase):
    def run_tool(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args], text=True, capture_output=True
        )

    def create(self, output: Path) -> subprocess.CompletedProcess[str]:
        return self.run_tool(
            "create", "--output", str(output), "--work-item-ref", "issue-292@eb057c7",
            "--profile", "poc-exploration", "--base-sha", BASE,
            "--candidate-sha", HEAD, "--repo", REPO, "--pr", "289",
            "--head-sha", HEAD, "--accepted-outcome", "Require declared profile liveness.",
            "--acceptance-criterion", "A declared profile must be live before verification.",
            "--falsifier", "A stale head invalidates this index.",
            "--evidence-ref", "e2e-pipeline/compiler/test/browser-runtime-lifecycle.test.js",
            "--changed-file", "e2e-pipeline/bin/e2e-browser-runtime.js",
            "--scope-exclusion", "No merge or posting authority.",
            "--residual", "Host journey still required before delivery.",
        )

    def test_exact_head_index_validates_and_has_no_authority_payload(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            handoff = Path(directory) / "handoff.json"
            created = self.create(handoff)
            self.assertEqual(created.returncode, 0, created.stderr)
            consumed = self.run_tool(
                "validate", "--handoff", str(handoff), "--repo", REPO, "--pr", "289",
                "--head-sha", HEAD, "--candidate-sha", HEAD, "--expected-base-sha", BASE,
            )
            self.assertEqual(consumed.returncode, 0, consumed.stderr)
            result = json.loads(consumed.stdout)
            self.assertEqual(result["schema"], "kc-dev-flow-pr-review-handoff-validation/v1")
            self.assertTrue(result["evidence_valid"])
            self.assertEqual(result["review_context"]["pr"]["head_sha"], HEAD)
            self.assertNotIn("authority", result)
            self.assertNotIn("credentials", handoff.read_text())
            self.assertNotIn("prompt", handoff.read_text())

    def test_different_expected_base_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            handoff = Path(directory) / "handoff.json"
            self.assertEqual(self.create(handoff).returncode, 0)
            stale_base = self.run_tool(
                "validate", "--handoff", str(handoff), "--repo", REPO, "--pr", "289",
                "--head-sha", HEAD, "--candidate-sha", HEAD,
                "--expected-base-sha", "b" * 40,
            )
            self.assertNotEqual(stale_base.returncode, 0)
            self.assertIn("identity mismatch", stale_base.stderr)

    def test_changed_head_and_malformed_index_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            handoff = Path(directory) / "handoff.json"
            self.assertEqual(self.create(handoff).returncode, 0)
            stale = self.run_tool(
                "validate", "--handoff", str(handoff), "--repo", REPO, "--pr", "289",
                "--head-sha", "a" * 40, "--candidate-sha", HEAD, "--expected-base-sha", BASE,
            )
            self.assertNotEqual(stale.returncode, 0)
            self.assertIn("identity mismatch", stale.stderr)
            handoff.write_text('{"schema":"kc-dev-flow-pr-review-handoff/v1","credentials":"no"}')
            malformed = self.run_tool(
                "validate", "--handoff", str(handoff), "--repo", REPO, "--pr", "289",
                "--head-sha", HEAD, "--candidate-sha", HEAD, "--expected-base-sha", BASE,
            )
            self.assertNotEqual(malformed.returncode, 0)
            self.assertIn("invalid handoff", malformed.stderr)


if __name__ == "__main__":
    unittest.main()
