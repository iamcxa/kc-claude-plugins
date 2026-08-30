#!/usr/bin/env python3
"""Focused shape tests for the real-pair scorer."""

from __future__ import annotations

import json
import hashlib
import subprocess
import tempfile
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SCORER = HERE / "review-real-pair-score.py"
FIXTURE = HERE.parent / "test/fixtures/review-evaluation/real-pair-score-shape.json"


class RealPairScoreShapeTest(unittest.TestCase):
    def run_scorer(self, command: str, payload: dict | None = None) -> subprocess.CompletedProcess[str]:
        if payload is None:
            corpus = FIXTURE
            command_line = ["python3", str(SCORER), command, "--corpus", str(corpus)]
            if command == "score":
                command_line += ["--published-sha256", hashlib.sha256(corpus.read_bytes()).hexdigest()]
            return subprocess.run(
                command_line,
                text=True,
                capture_output=True,
                check=False,
            )
        with tempfile.TemporaryDirectory() as directory:
            corpus = Path(directory) / "corpus.json"
            corpus.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":")), encoding="utf-8")
            command_line = ["python3", str(SCORER), command, "--corpus", str(corpus)]
            if command == "score":
                command_line += ["--published-sha256", hashlib.sha256(corpus.read_bytes()).hexdigest()]
            return subprocess.run(
                command_line,
                text=True,
                capture_output=True,
                check=False,
            )

    def fixture(self) -> dict:
        return json.loads(FIXTURE.read_text(encoding="utf-8"))

    @staticmethod
    def seal(payload: dict) -> dict:
        value = dict(payload)
        value.pop("content_sha256", None)
        canonical = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
        value["content_sha256"] = hashlib.sha256(canonical).hexdigest()
        return value

    def field_corpus(self) -> dict:
        def timing(review_ms: int, collector_ms: int = 20) -> dict:
            return {
                "attribution_ms": {
                    "agent_critical_path": review_ms,
                    "collector": collector_ms,
                    "hosted_ci": None,
                    "human_wait": None,
                    "unrelated_queue": None,
                },
                "durations_ms": {
                    "collation_and_draft": 10,
                    "collector": collector_ms,
                    "identity_and_plan": 10,
                    "inventory": 10,
                    "required_lanes_critical_path": review_ms,
                    "review_to_confirmation_ready": review_ms,
                    "targeted_verification_critical_path": 10,
                    "wall_to_confirmation_ready": review_ms + collector_ms + 20,
                },
                "lane_durations_ms": [],
                "mode": "initial",
                "review_key": "a" * 64,
                "schema": "kc-pr-flow.review-timing/v1",
            }

        pairs = []
        for index in range(5):
            pairs.append(
                {
                    "adjudicated_defects": [
                        {"defect_id": f"critical-{index}", "severity": "Critical"},
                        {"defect_id": f"medium-{index}", "severity": "Medium"},
                    ],
                    "arms_terminal": True,
                    "config_frozen": True,
                    "control": {
                        "finding_ids": [f"control-fp-{index}", f"critical-{index}"],
                        "timing": timing(150),
                    },
                    "fallback_expected": "initial",
                    "fallback_observed": "initial",
                    "no_cross_arm_visibility": True,
                    "no_scheduling_contamination": True,
                    "no_schema_or_tool_drift": True,
                    "pair_id": f"pair-{index + 1:02d}",
                    "preregistered": True,
                    "required_lanes_frozen": True,
                    "shas_and_ancestry_frozen": True,
                    "timing_protocol_frozen": True,
                    "treatment": {
                        "finding_ids": [f"critical-{index}", f"medium-{index}"],
                        "timing": timing(90),
                    },
                }
            )
        return self.seal(
            {
                "adjudication": {
                    "arm_labels_revealed_after_freeze": True,
                    "blind_candidate_ids": True,
                    "defect_classes_frozen": True,
                },
                "evidence_tier": "real-pair-field",
                "pairs": pairs,
                "schema": "kc-pr-flow.real-pair-score/v1",
            }
        )

    def test_closed_shape_is_valid_but_never_promotes(self) -> None:
        result = self.run_scorer("validate-shape")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            json.loads(result.stdout),
            {
                "pair_count": 5,
                "schema": "kc-pr-flow.real-pair-score-result/v1",
                "status": "valid_shape",
                "verdict": "do_not_promote",
            },
        )

    def test_shape_fixture_cannot_enter_real_scoring(self) -> None:
        result = self.run_scorer("score")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["reason_codes"], ["non_field_evidence"])

    def test_field_scoring_requires_the_published_file_hash(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            corpus = Path(directory) / "corpus.json"
            corpus.write_text(json.dumps(self.field_corpus(), sort_keys=True, separators=(",", ":")))
            result = subprocess.run(
                ["python3", str(SCORER), "score", "--corpus", str(corpus)],
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["reason_codes"], ["unbound_publication"])

    def test_synthetic_tier_is_rejected(self) -> None:
        payload = self.fixture()
        payload["evidence_tier"] = "synthetic-structural"
        result = self.run_scorer("validate-shape", payload)
        self.assertEqual(result.returncode, 2)

    def test_fewer_than_five_pairs_is_rejected(self) -> None:
        payload = self.fixture()
        payload["pairs"] = payload["pairs"][:4]
        result = self.run_scorer("validate-shape", payload)
        self.assertEqual(result.returncode, 2)

    def test_unblinded_adjudication_is_rejected(self) -> None:
        payload = self.fixture()
        payload["adjudication"]["blind_candidate_ids"] = False
        result = self.run_scorer("validate-shape", payload)
        self.assertEqual(result.returncode, 2)

    def test_quality_passes_before_latency_and_reports_candidate(self) -> None:
        result = self.run_scorer("score", self.field_corpus())
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output["verdict"], "promote_candidate")
        self.assertEqual(output["quality"]["overall_recall_bps"], 10000)
        self.assertEqual(output["quality"]["critical_high_recall_bps"], 10000)
        self.assertEqual(output["latency"]["median_reduction_bps"], 4000)

    def test_quality_failure_does_not_evaluate_latency(self) -> None:
        payload = self.field_corpus()
        payload["pairs"][0]["treatment"]["finding_ids"] = ["medium-0"]
        payload = self.seal(payload)
        result = self.run_scorer("score", payload)
        self.assertEqual(result.returncode, 1)
        output = json.loads(result.stdout)
        self.assertEqual(output["verdict"], "do_not_promote")
        self.assertFalse(output["latency_evaluated"])
        self.assertIn("critical_high_recall", output["reason_codes"])

    def test_treatment_false_positives_cannot_exceed_control(self) -> None:
        payload = self.field_corpus()
        for pair in payload["pairs"]:
            pair["treatment"]["finding_ids"] += ["treatment-fp-a", "treatment-fp-b"]
            pair["treatment"]["finding_ids"].sort()
        payload = self.seal(payload)
        result = self.run_scorer("score", payload)
        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)["latency_evaluated"])

    def test_latency_threshold_is_checked_only_after_quality(self) -> None:
        payload = self.field_corpus()
        for pair in payload["pairs"]:
            pair["treatment"]["timing"]["durations_ms"]["review_to_confirmation_ready"] = 105
        payload = self.seal(payload)
        result = self.run_scorer("score", payload)
        self.assertEqual(result.returncode, 1)
        output = json.loads(result.stdout)
        self.assertTrue(output["latency_evaluated"])
        self.assertEqual(output["latency"]["median_reduction_bps"], 3000)

    def test_invalid_pair_returns_initial_before_scoring(self) -> None:
        payload = self.field_corpus()
        payload["pairs"][0]["fallback_observed"] = "delta"
        payload = self.seal(payload)
        result = self.run_scorer("score", payload)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["verdict"], "initial")

    def test_self_resealed_extra_member_is_rejected(self) -> None:
        payload = self.field_corpus()
        payload["pairs"][0]["control"]["extra"] = True
        payload = self.seal(payload)
        result = self.run_scorer("score", payload)
        self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
