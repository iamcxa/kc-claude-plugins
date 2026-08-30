#!/usr/bin/env python3
"""Focused shape tests for the real-pair scorer."""

from __future__ import annotations

import json
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
            return subprocess.run(
                ["python3", str(SCORER), command, "--corpus", str(corpus)],
                text=True,
                capture_output=True,
                check=False,
            )
        with tempfile.TemporaryDirectory() as directory:
            corpus = Path(directory) / "corpus.json"
            corpus.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":")), encoding="utf-8")
            return subprocess.run(
                ["python3", str(SCORER), command, "--corpus", str(corpus)],
                text=True,
                capture_output=True,
                check=False,
            )

    def fixture(self) -> dict:
        return json.loads(FIXTURE.read_text(encoding="utf-8"))

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


if __name__ == "__main__":
    unittest.main()
