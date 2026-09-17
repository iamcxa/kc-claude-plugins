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
RUNTIME = HERE / "review-runtime.sh"
FIXTURE = HERE.parent / "test/fixtures/review-evaluation/real-pair-score-shape.json"


class RealPairScoreShapeTest(unittest.TestCase):
    def run_scorer(
        self,
        command: str,
        payload: dict | None = None,
        published_manifest_sha256: str | None = None,
        published_adjudication_sha256: str | None = None,
        timing_manifest: dict | None = None,
        published_timing_manifest_sha256: str | None = None,
        arm_mapping_manifest: dict | None = None,
        published_arm_mapping_sha256: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
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
                if payload.get("evidence_tier") == "real-pair-field":
                    timing_manifest_value = timing_manifest or self.timing_manifest(payload)
                    timing_manifest_path = Path(directory) / "timing-manifest.json"
                    timing_manifest_path.write_text(
                        json.dumps(timing_manifest_value, sort_keys=True, separators=(",", ":")),
                        encoding="utf-8",
                    )
                    arm_mapping_value = arm_mapping_manifest or self.arm_mapping_manifest(payload)
                    arm_mapping_path = Path(directory) / "arm-mapping.json"
                    arm_mapping_path.write_text(
                        json.dumps(arm_mapping_value, sort_keys=True, separators=(",", ":")),
                        encoding="utf-8",
                    )
                    command_line += [
                        "--published-manifest-sha256",
                        published_manifest_sha256 or self.manifest_sha256(payload),
                        "--published-adjudication-sha256",
                        published_adjudication_sha256 or self.adjudication_sha256(payload),
                        "--timing-manifest",
                        str(timing_manifest_path),
                        "--published-timing-manifest-sha256",
                        published_timing_manifest_sha256
                        or hashlib.sha256(timing_manifest_path.read_bytes()).hexdigest(),
                        "--arm-mapping-manifest",
                        str(arm_mapping_path),
                        "--published-arm-mapping-sha256",
                        published_arm_mapping_sha256
                        or hashlib.sha256(arm_mapping_path.read_bytes()).hexdigest(),
                    ]
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

    @staticmethod
    def canonical_sha256(value: object) -> str:
        canonical = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(canonical).hexdigest()

    def manifest_sha256(self, payload: dict) -> str:
        return self.canonical_sha256([pair["manifest"] for pair in payload["pairs"]])

    def adjudication_sha256(self, payload: dict) -> str:
        adjudication = dict(payload["adjudication"])
        adjudication.pop("content_sha256", None)
        return self.canonical_sha256(adjudication)

    def timing_manifest(self, payload: dict) -> dict:
        return {
            "receipts": [
                {
                    "arm": arm,
                    "pair_id": pair["pair_id"],
                    "timing_sha256": self.canonical_sha256(pair[arm]["timing"]),
                }
                for pair in payload["pairs"]
                for arm in ("control", "treatment")
            ],
            "schema": "kc-pr-flow.timing-receipt-manifest/v1",
        }

    def arm_mapping_manifest(self, payload: dict) -> dict:
        return {
            "candidates": sorted(
                [
                    {"arm": arm, "candidate_id": candidate_id, "pair_id": pair["pair_id"]}
                    for pair in payload["pairs"]
                    for arm in ("control", "treatment")
                    for candidate_id in pair[arm]["candidate_ids"]
                ],
                key=lambda item: item["candidate_id"],
            ),
            "schema": "kc-pr-flow.post-blind-arm-mapping/v1",
        }

    def field_corpus(self) -> dict:
        def identity(pair_index: int, arm: str, mode: str) -> dict:
            repository = "acme/widgets"
            pr_number = 100 + pair_index
            base_sha = f"{pair_index + 1:040x}"
            head_sha = f"{pair_index + 101:040x}"
            config_hash = hashlib.sha256(f"{pair_index}-frozen-config".encode()).hexdigest()
            review_key = hashlib.sha256(
                f"{repository}|{pr_number}|{base_sha}|{head_sha}|{config_hash}".encode()
            ).hexdigest()
            return {
                "base_sha": base_sha,
                "config_hash": config_hash,
                "head_sha": head_sha,
                "mode": mode,
                "pr_number": pr_number,
                "repository": repository,
                "review_key": review_key,
            }

        def timing(review_ms: int, arm_identity: dict, collector_ms: int = 20) -> dict:
            return {
                "attribution_ms": {
                    "agent_critical_path": 50,
                    "collector": collector_ms,
                    "hosted_ci": 0,
                    "human_wait": 0,
                    "unrelated_queue": 0,
                },
                "durations_ms": {
                    "collation_and_draft": 10,
                    "collector": collector_ms,
                    "identity_and_plan": 10,
                    "inventory": 10,
                    "required_lanes_critical_path": 50,
                    "review_to_confirmation_ready": review_ms,
                    "targeted_verification_critical_path": 10,
                    "wall_to_confirmation_ready": review_ms + collector_ms + 20,
                },
                "lane_durations_ms": [
                    {"duration_ms": 40, "lane_id": "correctness", "provider_family": "claude"},
                    {"duration_ms": 50, "lane_id": "security", "provider_family": "claude"},
                ],
                "mode": arm_identity["mode"],
                "review_key": arm_identity["review_key"],
                "schema": "kc-pr-flow.review-timing/v1",
            }

        def arm(review_ms: int, arm_identity: dict, candidate_ids: list[str]) -> dict:
            receipt = timing(review_ms, arm_identity)
            return {
                "candidate_ids": sorted(candidate_ids),
                "timing": receipt,
            }

        pairs = []
        candidates = []
        candidate_to_defect = []
        defects = []
        duplicate_groups = []
        for index in range(5):
            control_identity = identity(index, "control", "initial")
            treatment_identity = identity(index, "treatment", "initial")
            pair_id = f"pair-{index + 1:02d}"
            arm_candidates = {
                arm_name: [
                    hashlib.sha256(f"candidate-{index}-{arm_name}-{ordinal}".encode()).hexdigest()
                    for ordinal in range(2)
                ]
                for arm_name in ("control", "treatment")
            }
            defects.extend(
                [
                    {"defect_id": f"critical-{index}", "pair_id": pair_id, "severity": "Critical"},
                    {"defect_id": f"medium-{index}", "pair_id": pair_id, "severity": "Medium"},
                ]
            )
            mappings = {
                arm_candidates["control"][0]: f"critical-{index}",
                arm_candidates["control"][1]: None,
                arm_candidates["treatment"][0]: f"critical-{index}",
                arm_candidates["treatment"][1]: f"medium-{index}",
            }
            for arm_name, candidate_ids in arm_candidates.items():
                for candidate_id in candidate_ids:
                    candidates.append(
                        {
                            "candidate_id": candidate_id,
                            "evidence_sha256": hashlib.sha256(f"evidence-{candidate_id}".encode()).hexdigest(),
                            "pair_id": pair_id,
                        }
                    )
                    candidate_to_defect.append(
                        {"candidate_id": candidate_id, "defect_id": mappings[candidate_id]}
                    )
                    duplicate_groups.append(
                        {
                            "candidate_ids": [candidate_id],
                            "group_id": "g" + hashlib.sha256(f"group-{candidate_id}".encode()).hexdigest()[:63],
                        }
                    )
            pairs.append(
                {
                    "arms_terminal": True,
                    "config_frozen": True,
                    "control": arm(150, control_identity, arm_candidates["control"]),
                    "fallback_expected": "initial",
                    "fallback_observed": "initial",
                    "no_cross_arm_visibility": True,
                    "no_scheduling_contamination": True,
                    "no_schema_or_tool_drift": True,
                    "pair_id": pair_id,
                    "preregistered": True,
                    "required_lanes_frozen": True,
                    "shas_and_ancestry_frozen": True,
                    "timing_protocol_frozen": True,
                    "manifest": {
                        "control": control_identity,
                        "pair_id": pair_id,
                        "required_lanes": ["correctness", "security"],
                        "schema": "kc-pr-flow.real-pair-manifest/v1",
                        "treatment": treatment_identity,
                    },
                    "treatment": arm(90, treatment_identity, arm_candidates["treatment"]),
                }
            )
        adjudication = self.seal(
            {
                "candidate_to_defect": sorted(candidate_to_defect, key=lambda item: item["candidate_id"]),
                "candidates": sorted(candidates, key=lambda item: item["candidate_id"]),
                "defects": sorted(defects, key=lambda item: (item["pair_id"], item["defect_id"])),
                "duplicate_groups": sorted(duplicate_groups, key=lambda item: item["group_id"]),
                "schema": "kc-pr-flow.blind-adjudication/v1",
            }
        )
        return self.seal(
            {
                "adjudication": adjudication,
                "evidence_tier": "real-pair-field",
                "pairs": pairs,
                "schema": "kc-pr-flow.real-pair-score/v1",
            }
        )

    def producer_timing(self, review_key: str, mode: str) -> dict:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            counter = root / "counter"
            state = root / "state.json"
            lanes = root / "lanes.json"
            attribution = root / "attribution.json"
            receipt = root / "receipt.json"
            counter.write_text("0\n", encoding="utf-8")
            lanes.write_text(
                json.dumps(
                    [
                        {"duration_ms": 17, "lane_id": "correctness", "provider_family": "claude"},
                        {"duration_ms": 23, "lane_id": "security", "provider_family": "claude"},
                    ]
                ),
                encoding="utf-8",
            )
            attribution.write_text(
                json.dumps(
                    {
                        "hosted_ci": 100,
                        "human_wait": 300,
                        "schema": "kc-pr-flow.external-wait-attribution/v1",
                        "unrelated_queue": 200,
                    }
                ),
                encoding="utf-8",
            )
            script = r"""
set -eu
. "$1"
counter="$2"
review_runtime_monotonic_ms() {
  values='9100000000 9100000100 9100000300 9100001300 9100001800 9100002500 9100002800 9100003000'
  index="$(cat "$counter")"
  printf '%s\n' "$values" | awk -v field="$((index + 1))" '{print $field}'
  printf '%s\n' "$((index + 1))" >"$counter"
}
review_runtime_timing_start "$3" "$4" "$5"
for phase in identity_and_plan inventory required_lanes_critical_path collector \
  targeted_verification_critical_path collation_and_draft confirmation_ready; do
  review_runtime_timing_mark "$5" "$phase"
done
review_runtime_timing_finish "$5" "$6" "$8" "$7"
"""
            result = subprocess.run(
                [
                    "bash",
                    "-c",
                    script,
                    "_",
                    str(RUNTIME),
                    str(counter),
                    review_key,
                    mode,
                    str(state),
                    str(lanes),
                    str(attribution),
                    str(receipt),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            return json.loads(result.stdout)

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
        treatment_ids = set(payload["pairs"][0]["treatment"]["candidate_ids"])
        next(
            item
            for item in payload["adjudication"]["candidate_to_defect"]
            if item["candidate_id"] in treatment_ids and item["defect_id"] == "critical-0"
        )["defect_id"] = None
        payload["adjudication"] = self.seal(payload["adjudication"])
        payload = self.seal(payload)
        result = self.run_scorer("score", payload)
        self.assertEqual(result.returncode, 1)
        output = json.loads(result.stdout)
        self.assertEqual(output["verdict"], "do_not_promote")
        self.assertFalse(output["latency_evaluated"])
        self.assertIn("critical_high_recall", output["reason_codes"])

    def test_treatment_false_positives_cannot_exceed_control(self) -> None:
        payload = self.field_corpus()
        treatment_ids = {
            candidate_id for pair in payload["pairs"] for candidate_id in pair["treatment"]["candidate_ids"]
        }
        for item in payload["adjudication"]["candidate_to_defect"]:
            if item["candidate_id"] in treatment_ids:
                item["defect_id"] = None
        payload["adjudication"] = self.seal(payload["adjudication"])
        payload = self.seal(payload)
        result = self.run_scorer("score", payload)
        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)["latency_evaluated"])

    def test_latency_threshold_is_checked_only_after_quality(self) -> None:
        payload = self.field_corpus()
        for pair in payload["pairs"]:
            pair["treatment"]["timing"]["durations_ms"]["review_to_confirmation_ready"] = 105
            pair["treatment"]["timing"]["durations_ms"]["wall_to_confirmation_ready"] = 145
        payload = self.seal(payload)
        result = self.run_scorer("score", payload)
        self.assertEqual(result.returncode, 1)
        output = json.loads(result.stdout)
        self.assertTrue(output["latency_evaluated"])
        self.assertEqual(output["latency"]["median_reduction_bps"], 3000)

    def test_runtime_known_wait_receipt_is_accepted_by_scorer(self) -> None:
        payload = self.field_corpus()
        identity = payload["pairs"][0]["manifest"]["control"]
        payload["pairs"][0]["control"]["timing"] = self.producer_timing(
            identity["review_key"], identity["mode"]
        )
        payload = self.seal(payload)
        result = self.run_scorer("score", payload)
        self.assertEqual(result.returncode, 0, result.stdout or result.stderr)

    def test_unknown_external_wait_invalidates_pair_to_initial(self) -> None:
        for field in ("hosted_ci", "human_wait", "unrelated_queue"):
            with self.subTest(field=field):
                payload = self.field_corpus()
                payload["pairs"][0]["treatment"]["timing"]["attribution_ms"][field] = None
                payload = self.seal(payload)
                result = self.run_scorer("score", payload)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(json.loads(result.stdout)["verdict"], "initial")

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

    def test_real_pair_identity_lane_and_timing_receipts_are_bound(self) -> None:
        original = self.field_corpus()
        published_manifest = self.manifest_sha256(original)
        mutations = {
            "duplicate pair identity": lambda p: p["pairs"].__setitem__(1, dict(p["pairs"][0])),
            "repository mismatch": lambda p: p["pairs"][0]["manifest"]["treatment"].__setitem__(
                "repository", "acme/other"
            ),
            "pr mismatch": lambda p: p["pairs"][0]["manifest"]["treatment"].__setitem__("pr_number", 999),
            "base mismatch": lambda p: p["pairs"][0]["manifest"]["treatment"].__setitem__("base_sha", "f" * 40),
            "head mismatch": lambda p: p["pairs"][0]["manifest"]["treatment"].__setitem__("head_sha", "e" * 40),
            "config/review mismatch": lambda p: p["pairs"][0]["manifest"]["treatment"].__setitem__(
                "config_hash", "d" * 64
            ),
            "wrong control mode": lambda p: p["pairs"][0]["manifest"]["control"].__setitem__("mode", "delta"),
            "wrong treatment mode": lambda p: p["pairs"][0]["manifest"]["treatment"].__setitem__("mode", "delta"),
            "missing required lane": lambda p: p["pairs"][0]["treatment"]["timing"][
                "lane_durations_ms"
            ].pop(),
            "empty required lanes": lambda p: p["pairs"][0]["manifest"].__setitem__("required_lanes", []),
            "forged embedded total": lambda p: p["pairs"][0]["treatment"]["timing"]["durations_ms"].__setitem__(
                "wall_to_confirmation_ready", 999
            ),
        }
        valid = self.run_scorer("score", original, published_manifest)
        self.assertEqual(valid.returncode, 0, valid.stdout)
        for label, mutate in mutations.items():
            with self.subTest(label=label):
                payload = self.field_corpus()
                mutate(payload)
                payload = self.seal(payload)
                result = self.run_scorer("score", payload, published_manifest)
                self.assertEqual(result.returncode, 2, result.stdout)

    def test_cross_arm_and_cross_pair_frozen_identities_are_unique(self) -> None:
        payload = self.field_corpus()
        treatment = payload["pairs"][0]["manifest"]["treatment"]
        treatment["config_hash"] = hashlib.sha256(b"coherent-different-config").hexdigest()
        treatment["review_key"] = hashlib.sha256(
            f'{treatment["repository"]}|{treatment["pr_number"]}|{treatment["base_sha"]}|'
            f'{treatment["head_sha"]}|{treatment["config_hash"]}'.encode()
        ).hexdigest()
        payload["pairs"][0]["treatment"]["timing"]["review_key"] = treatment["review_key"]
        cases = [("coherent cross-arm config mismatch", self.seal(payload))]

        payload = self.field_corpus()
        for arm_name in ("control", "treatment"):
            copied = dict(payload["pairs"][0]["manifest"][arm_name])
            payload["pairs"][1]["manifest"][arm_name] = copied
            payload["pairs"][1][arm_name]["timing"]["review_key"] = copied["review_key"]
        cases.append(("duplicate cross-pair frozen identity", self.seal(payload)))
        for label, mutation in cases:
            with self.subTest(label=label):
                result = self.run_scorer("score", mutation)
                self.assertEqual(result.returncode, 2, result.stdout)

    def test_original_timing_receipts_require_an_external_manifest(self) -> None:
        original = self.field_corpus()
        timing_manifest = self.timing_manifest(original)
        published = self.canonical_sha256(timing_manifest)
        valid = self.run_scorer(
            "score",
            original,
            timing_manifest=timing_manifest,
            published_timing_manifest_sha256=published,
        )
        self.assertEqual(valid.returncode, 0, valid.stdout)
        payload = self.field_corpus()
        timing = payload["pairs"][0]["treatment"]["timing"]["durations_ms"]
        timing["review_to_confirmation_ready"] += 10
        timing["wall_to_confirmation_ready"] += 10
        result = self.run_scorer(
            "score",
            self.seal(payload),
            timing_manifest=timing_manifest,
            published_timing_manifest_sha256=published,
        )
        self.assertEqual(result.returncode, 2, result.stdout)

    def test_blind_artifact_excludes_arm_and_post_blind_mapping_is_bound(self) -> None:
        payload = self.field_corpus()
        adjudication_text = json.dumps(payload["adjudication"], sort_keys=True)
        self.assertNotIn('"arm"', adjudication_text)
        self.assertNotIn("control", adjudication_text)
        self.assertNotIn("treatment", adjudication_text)
        self.assertTrue(
            all(len(item["candidate_id"]) == 64 for item in payload["adjudication"]["candidates"])
        )
        arm_mapping = self.arm_mapping_manifest(payload)
        published = self.canonical_sha256(arm_mapping)
        valid = self.run_scorer(
            "score",
            payload,
            arm_mapping_manifest=arm_mapping,
            published_arm_mapping_sha256=published,
        )
        self.assertEqual(valid.returncode, 0, valid.stdout)
        mutated_mapping = json.loads(json.dumps(arm_mapping))
        mutated_mapping["candidates"][0]["arm"] = (
            "treatment" if mutated_mapping["candidates"][0]["arm"] == "control" else "control"
        )
        result = self.run_scorer(
            "score",
            payload,
            arm_mapping_manifest=mutated_mapping,
            published_arm_mapping_sha256=published,
        )
        self.assertEqual(result.returncode, 2, result.stdout)
        payload = self.field_corpus()
        control = payload["pairs"][0]["control"]["candidate_ids"]
        treatment = payload["pairs"][0]["treatment"]["candidate_ids"]
        control[0], treatment[0] = treatment[0], control[0]
        control.sort()
        treatment.sort()
        result = self.run_scorer(
            "score",
            self.seal(payload),
            arm_mapping_manifest=arm_mapping,
            published_arm_mapping_sha256=published,
        )
        self.assertEqual(result.returncode, 2, result.stdout)

    def test_adjudication_pair_set_must_equal_registered_pairs(self) -> None:
        valid = self.run_scorer("score", self.field_corpus())
        self.assertEqual(valid.returncode, 0, valid.stdout)
        payload = self.field_corpus()
        candidate_id = hashlib.sha256(b"extra-pair-z-candidate").hexdigest()
        payload["adjudication"]["defects"].append(
            {"defect_id": "extra-defect", "pair_id": "pair-z", "severity": "Medium"}
        )
        payload["adjudication"]["candidates"].append(
            {"candidate_id": candidate_id, "evidence_sha256": "f" * 64, "pair_id": "pair-z"}
        )
        payload["adjudication"]["candidate_to_defect"].append(
            {"candidate_id": candidate_id, "defect_id": "extra-defect"}
        )
        payload["adjudication"]["duplicate_groups"].append(
            {"candidate_ids": [candidate_id], "group_id": "g" + "f" * 63}
        )
        for key, order in (
            ("candidates", lambda item: item["candidate_id"]),
            ("candidate_to_defect", lambda item: item["candidate_id"]),
            ("duplicate_groups", lambda item: item["group_id"]),
        ):
            payload["adjudication"][key].sort(key=order)
        payload["adjudication"] = self.seal(payload["adjudication"])
        result = self.run_scorer("score", self.seal(payload))
        self.assertEqual(result.returncode, 2, result.stdout)

    def test_blind_adjudication_digest_binds_denominator_mapping_and_duplicates(self) -> None:
        original = self.field_corpus()
        published_adjudication = self.adjudication_sha256(original)
        mutations = {
            "candidate evidence identity": lambda p: p["adjudication"]["candidates"][0].__setitem__(
                "evidence_sha256", "f" * 64
            ),
            "denominator": lambda p: p["adjudication"]["defects"].pop(),
            "candidate mapping": lambda p: next(
                item for item in p["adjudication"]["candidate_to_defect"] if item["defect_id"] is not None
            ).__setitem__("defect_id", None),
            "duplicate grouping": lambda p: p["adjudication"]["duplicate_groups"][0].__setitem__(
                "group_id", "group-resealed"
            ),
        }
        valid = self.run_scorer(
            "score", original, published_adjudication_sha256=published_adjudication
        )
        self.assertEqual(valid.returncode, 0, valid.stdout)
        for label, mutate in mutations.items():
            with self.subTest(label=label):
                payload = self.field_corpus()
                mutate(payload)
                payload["adjudication"] = self.seal(payload["adjudication"])
                payload = self.seal(payload)
                result = self.run_scorer(
                    "score", payload, published_adjudication_sha256=published_adjudication
                )
                self.assertEqual(result.returncode, 2, result.stdout)


if __name__ == "__main__":
    unittest.main()
