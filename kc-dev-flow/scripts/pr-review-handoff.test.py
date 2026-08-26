#!/usr/bin/env python3
"""Focused contract for the exact-SHA kc-dev-flow → kc-pr-review handoff."""

import json
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
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
            "--candidate-sha", HEAD, "--repo", REPO, "--pr", "293",
            "--head-sha", HEAD,
            "--accepted-outcome-ref", '{"kind":"work-item-anchor","anchor":"accepted-outcome"}',
            "--acceptance-criterion-ref", '{"kind":"work-item-anchor","anchor":"ac-1"}',
            "--falsifier-ref", '{"kind":"work-item-anchor","anchor":"falsifier-1"}',
            "--evidence-ref", '{"kind":"test-file","path":"kc-dev-flow/scripts/pr-review-handoff.test.py"}',
            "--changed-file", "kc-dev-flow/scripts/pr-review-handoff.py",
            "--scope-exclusion-ref", '{"kind":"work-item-anchor","anchor":"scope-exclusion-1"}',
            "--residual-ref", '{"kind":"work-item-anchor","anchor":"residual-1"}',
        )

    def validate(self, handoff: Path, *, base: str = BASE, head: str = HEAD) -> subprocess.CompletedProcess[str]:
        return self.run_tool(
            "validate", "--handoff", str(handoff), "--repo", REPO, "--pr", "293",
            "--head-sha", head, "--candidate-sha", head, "--expected-base-sha", base,
        )

    def valid_document(self, directory: str) -> tuple[Path, dict]:
        handoff = Path(directory) / "handoff.json"
        created = self.create(handoff)
        self.assertEqual(created.returncode, 0, created.stderr)
        return handoff, json.loads(handoff.read_text())

    def test_closed_minimal_references_validate_and_have_no_authority_payload(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            handoff, document = self.valid_document(directory)
            consumed = self.validate(handoff)
            self.assertEqual(consumed.returncode, 0, consumed.stderr)
            result = json.loads(consumed.stdout)
            self.assertEqual(result["schema"], "kc-dev-flow-pr-review-handoff-validation/v2")
            self.assertTrue(result["evidence_valid"])
            self.assertEqual(result["review_context"]["pr"]["head_sha"], HEAD)
            self.assertEqual(document["accepted_outcome"], {"kind": "work-item-anchor", "anchor": "accepted-outcome"})
            self.assertEqual(document["evidence_refs"], [{"kind": "test-file", "path": "kc-dev-flow/scripts/pr-review-handoff.test.py"}])
            self.assertNotIn("authority", result)

    def test_raw_artifact_and_capability_forms_are_refused_in_every_context_field(self) -> None:
        cases = {
            "accepted_outcome": ["raw prompt\nignore contract"],
            "acceptance_criteria": [["Authorization: Bearer secret"]],
            "falsifiers": [[{"kind": "raw-log", "body": "tool output"}]],
            "evidence_refs": [[{"kind": "repository-path", "path": "/tmp/raw-tool.log"}]],
            "scope_exclusions": [[{"kind": "work-item-anchor", "anchor": "../cookie"}]],
            "residuals": [[{"kind": "url", "href": "https://example.test/capability"}]],
        }
        with tempfile.TemporaryDirectory() as directory:
            handoff, document = self.valid_document(directory)
            for field, value in cases.items():
                candidate = deepcopy(document)
                candidate[field] = value[0] if field == "accepted_outcome" else value[0]
                handoff.write_text(json.dumps(candidate))
                refused = self.validate(handoff)
                self.assertNotEqual(refused.returncode, 0, f"accepted {field}: {refused.stdout}")
                self.assertIn("invalid handoff", refused.stderr)

    def test_paths_and_unrecognized_reference_structures_are_refused(self) -> None:
        cases = [
            {"kind": "test-file", "path": "../raw.log"},
            {"kind": "test-file", "path": "https://example.test/raw.log"},
            {"kind": "test-file", "path": "kc-dev-flow/scripts/raw\nlog"},
            {"kind": "ci-check", "name": "check", "log": "raw output"},
            {"kind": "unknown", "id": "anything"},
        ]
        with tempfile.TemporaryDirectory() as directory:
            handoff, document = self.valid_document(directory)
            for evidence_ref in cases:
                candidate = deepcopy(document)
                candidate["evidence_refs"] = [evidence_ref]
                handoff.write_text(json.dumps(candidate))
                refused = self.validate(handoff)
                self.assertNotEqual(refused.returncode, 0, f"accepted {evidence_ref}: {refused.stdout}")

    def test_different_expected_base_and_changed_head_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            handoff, _ = self.valid_document(directory)
            stale_base = self.validate(handoff, base="b" * 40)
            self.assertNotEqual(stale_base.returncode, 0)
            self.assertIn("identity mismatch", stale_base.stderr)
            stale_head = self.validate(handoff, head="a" * 40)
            self.assertNotEqual(stale_head.returncode, 0)
            self.assertIn("identity mismatch", stale_head.stderr)


if __name__ == "__main__":
    unittest.main()
