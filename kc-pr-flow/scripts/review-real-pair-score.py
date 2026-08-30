#!/usr/bin/env python3
"""Validate real-pair scorer inputs without promoting shape fixtures."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
from statistics import median
from pathlib import Path
from typing import Any


MAX_CORPUS_BYTES = 1_048_576
PAIR_ID = re.compile(r"^pair-[a-z0-9][a-z0-9._-]{0,58}$")
TOP_KEYS = {"adjudication", "evidence_tier", "pairs", "schema"}
ADJUDICATION_KEYS = {
    "arm_labels_revealed_after_freeze",
    "blind_candidate_ids",
    "defect_classes_frozen",
}
PAIR_KEYS = {
    "arms_terminal",
    "config_frozen",
    "fallback_expected",
    "fallback_observed",
    "no_cross_arm_visibility",
    "no_scheduling_contamination",
    "no_schema_or_tool_drift",
    "pair_id",
    "preregistered",
    "required_lanes_frozen",
    "shas_and_ancestry_frozen",
    "timing_protocol_frozen",
}
BOOLEAN_PAIR_KEYS = PAIR_KEYS - {"fallback_expected", "fallback_observed", "pair_id"}
FALLBACKS = {"initial", "delta", "resolve"}
FIELD_TOP_KEYS = {"adjudication", "content_sha256", "evidence_tier", "pairs", "schema"}
FIELD_PAIR_KEYS = PAIR_KEYS | {"adjudicated_defects", "control", "treatment"}
DEFECT_KEYS = {"defect_id", "severity"}
ARM_KEYS = {"finding_ids", "timing"}
TIMING_KEYS = {"attribution_ms", "durations_ms", "lane_durations_ms", "mode", "review_key", "schema"}
DURATION_KEYS = {
    "collation_and_draft",
    "collector",
    "identity_and_plan",
    "inventory",
    "required_lanes_critical_path",
    "review_to_confirmation_ready",
    "targeted_verification_critical_path",
    "wall_to_confirmation_ready",
}
ATTRIBUTION_KEYS = {"agent_critical_path", "collector", "hosted_ci", "human_wait", "unrelated_queue"}
LANE_KEYS = {"duration_ms", "lane_id", "provider_family"}
TOKEN = re.compile(r"^[a-z][a-z0-9._-]{0,63}$")
DEFECT_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
HASH64 = re.compile(r"^[0-9a-f]{64}$")
SEVERITIES = {"Critical", "High", "Medium", "Low"}


class InvalidCorpus(ValueError):
    """The corpus is not a closed real-pair shape."""


def closed_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise InvalidCorpus("duplicate member")
        result[key] = value
    return result


def read_corpus(path: Path) -> tuple[dict[str, Any], str]:
    info = os.lstat(path)
    if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_CORPUS_BYTES:
        raise InvalidCorpus("unsafe corpus")
    raw = path.read_bytes()
    if len(raw) != info.st_size or b"\x00" in raw:
        raise InvalidCorpus("unstable corpus")
    value = json.loads(raw.decode("utf-8"), object_pairs_hook=closed_object)
    if not isinstance(value, dict):
        raise InvalidCorpus("corpus is not an object")
    return value, hashlib.sha256(raw).hexdigest()


def validate_shape(corpus: dict[str, Any]) -> int:
    if set(corpus) != TOP_KEYS:
        raise InvalidCorpus("top-level shape")
    if corpus["schema"] != "kc-pr-flow.real-pair-score-shape/v1":
        raise InvalidCorpus("schema")
    if corpus["evidence_tier"] != "real-pair-shape-only":
        raise InvalidCorpus("evidence tier")
    adjudication = corpus["adjudication"]
    if not isinstance(adjudication, dict) or set(adjudication) != ADJUDICATION_KEYS:
        raise InvalidCorpus("adjudication shape")
    if any(adjudication[key] is not True for key in ADJUDICATION_KEYS):
        raise InvalidCorpus("unfrozen adjudication")
    pairs = corpus["pairs"]
    if not isinstance(pairs, list) or len(pairs) < 5:
        raise InvalidCorpus("insufficient pairs")
    pair_ids: list[str] = []
    for pair in pairs:
        if not isinstance(pair, dict) or set(pair) != PAIR_KEYS:
            raise InvalidCorpus("pair shape")
        if any(pair[key] is not True for key in BOOLEAN_PAIR_KEYS):
            raise InvalidCorpus("invalid pair")
        pair_id = pair["pair_id"]
        if not isinstance(pair_id, str) or PAIR_ID.fullmatch(pair_id) is None:
            raise InvalidCorpus("pair id")
        if pair["fallback_expected"] not in FALLBACKS:
            raise InvalidCorpus("expected fallback")
        if pair["fallback_observed"] != pair["fallback_expected"]:
            raise InvalidCorpus("fallback mismatch")
        pair_ids.append(pair_id)
    if pair_ids != sorted(set(pair_ids)):
        raise InvalidCorpus("pair order")
    return len(pairs)


def nonnegative_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and 0 <= value <= 9_007_199_254_740_991


def validate_timing(value: Any) -> int:
    if not isinstance(value, dict) or set(value) != TIMING_KEYS:
        raise InvalidCorpus("timing shape")
    if value["schema"] != "kc-pr-flow.review-timing/v1" or value["mode"] not in FALLBACKS:
        raise InvalidCorpus("timing identity")
    if not isinstance(value["review_key"], str) or HASH64.fullmatch(value["review_key"]) is None:
        raise InvalidCorpus("timing review key")
    durations = value["durations_ms"]
    if not isinstance(durations, dict) or set(durations) != DURATION_KEYS:
        raise InvalidCorpus("duration shape")
    if not all(nonnegative_integer(item) for item in durations.values()):
        raise InvalidCorpus("duration value")
    attribution = value["attribution_ms"]
    if not isinstance(attribution, dict) or set(attribution) != ATTRIBUTION_KEYS:
        raise InvalidCorpus("attribution shape")
    if not nonnegative_integer(attribution["agent_critical_path"]) or not nonnegative_integer(attribution["collector"]):
        raise InvalidCorpus("attribution value")
    if any(attribution[key] is not None for key in ("hosted_ci", "human_wait", "unrelated_queue")):
        raise InvalidCorpus("external attribution")
    if attribution["collector"] != durations["collector"]:
        raise InvalidCorpus("collector attribution")
    if attribution["agent_critical_path"] != durations["required_lanes_critical_path"]:
        raise InvalidCorpus("critical path attribution")
    if durations["review_to_confirmation_ready"] + durations["collector"] > durations["wall_to_confirmation_ready"]:
        raise InvalidCorpus("collector exclusion")
    lanes = value["lane_durations_ms"]
    if not isinstance(lanes, list):
        raise InvalidCorpus("lane durations")
    lane_ids: list[str] = []
    for lane in lanes:
        if not isinstance(lane, dict) or set(lane) != LANE_KEYS:
            raise InvalidCorpus("lane shape")
        if not nonnegative_integer(lane["duration_ms"]):
            raise InvalidCorpus("lane duration")
        if not isinstance(lane["lane_id"], str) or TOKEN.fullmatch(lane["lane_id"]) is None:
            raise InvalidCorpus("lane id")
        if not isinstance(lane["provider_family"], str) or TOKEN.fullmatch(lane["provider_family"]) is None:
            raise InvalidCorpus("provider family")
        lane_ids.append(lane["lane_id"])
    if lane_ids != sorted(set(lane_ids)):
        raise InvalidCorpus("lane order")
    return durations["review_to_confirmation_ready"]


def validate_arm(value: Any) -> tuple[set[str], int]:
    if not isinstance(value, dict) or set(value) != ARM_KEYS:
        raise InvalidCorpus("arm shape")
    finding_ids = value["finding_ids"]
    if not isinstance(finding_ids, list) or any(
        not isinstance(item, str) or DEFECT_ID.fullmatch(item) is None for item in finding_ids
    ):
        raise InvalidCorpus("finding ids")
    if finding_ids != sorted(set(finding_ids)):
        raise InvalidCorpus("finding order")
    return set(finding_ids), validate_timing(value["timing"])


def validate_field(corpus: dict[str, Any]) -> list[dict[str, Any]]:
    if set(corpus) != FIELD_TOP_KEYS or corpus["schema"] != "kc-pr-flow.real-pair-score/v1":
        raise InvalidCorpus("field shape")
    if corpus["evidence_tier"] != "real-pair-field":
        raise InvalidCorpus("field evidence tier")
    expected_hash = corpus["content_sha256"]
    if not isinstance(expected_hash, str) or HASH64.fullmatch(expected_hash) is None:
        raise InvalidCorpus("field hash")
    unsealed = dict(corpus)
    del unsealed["content_sha256"]
    canonical = json.dumps(unsealed, sort_keys=True, separators=(",", ":")).encode()
    if hashlib.sha256(canonical).hexdigest() != expected_hash:
        raise InvalidCorpus("field hash mismatch")
    adjudication = corpus["adjudication"]
    if not isinstance(adjudication, dict) or set(adjudication) != ADJUDICATION_KEYS:
        raise InvalidCorpus("adjudication shape")
    if any(adjudication[key] is not True for key in ADJUDICATION_KEYS):
        raise InvalidCorpus("unfrozen adjudication")
    pairs = corpus["pairs"]
    if not isinstance(pairs, list) or len(pairs) < 5:
        raise InvalidCorpus("insufficient pairs")
    pair_ids: list[str] = []
    validated: list[dict[str, Any]] = []
    for pair in pairs:
        if not isinstance(pair, dict) or set(pair) != FIELD_PAIR_KEYS:
            raise InvalidCorpus("field pair shape")
        if any(pair[key] is not True for key in BOOLEAN_PAIR_KEYS):
            raise InvalidCorpus("invalid pair")
        pair_id = pair["pair_id"]
        if not isinstance(pair_id, str) or PAIR_ID.fullmatch(pair_id) is None:
            raise InvalidCorpus("pair id")
        if pair["fallback_expected"] not in FALLBACKS or pair["fallback_observed"] != pair["fallback_expected"]:
            raise InvalidCorpus("fallback mismatch")
        defects = pair["adjudicated_defects"]
        if not isinstance(defects, list) or not defects:
            raise InvalidCorpus("adjudicated defects")
        defect_ids: list[str] = []
        high_ids: set[str] = set()
        for defect in defects:
            if not isinstance(defect, dict) or set(defect) != DEFECT_KEYS:
                raise InvalidCorpus("defect shape")
            defect_id = defect["defect_id"]
            if not isinstance(defect_id, str) or DEFECT_ID.fullmatch(defect_id) is None:
                raise InvalidCorpus("defect id")
            if defect["severity"] not in SEVERITIES:
                raise InvalidCorpus("defect severity")
            defect_ids.append(defect_id)
            if defect["severity"] in {"Critical", "High"}:
                high_ids.add(defect_id)
        if defect_ids != sorted(set(defect_ids)):
            raise InvalidCorpus("defect order")
        control_findings, control_ms = validate_arm(pair["control"])
        treatment_findings, treatment_ms = validate_arm(pair["treatment"])
        defect_set = set(defect_ids)
        pair_ids.append(pair_id)
        validated.append(
            {
                "defect_ids": defect_set,
                "high_ids": high_ids,
                "control_findings": control_findings,
                "control_fp": len(control_findings - defect_set),
                "control_ms": control_ms,
                "treatment_findings": treatment_findings,
                "treatment_fp": len(treatment_findings - defect_set),
                "treatment_ms": treatment_ms,
            }
        )
    if pair_ids != sorted(set(pair_ids)):
        raise InvalidCorpus("pair order")
    return validated


def score_field(pairs: list[dict[str, Any]]) -> int:
    defects = sum(len(pair["defect_ids"]) for pair in pairs)
    recalled = sum(len(pair["defect_ids"] & pair["treatment_findings"]) for pair in pairs)
    high_total = sum(len(pair["high_ids"]) for pair in pairs)
    high_recalled = sum(len(pair["high_ids"] & pair["treatment_findings"]) for pair in pairs)
    control_fp = sum(pair["control_fp"] for pair in pairs)
    treatment_fp = sum(pair["treatment_fp"] for pair in pairs)
    overall_bps = recalled * 10_000 // defects
    high_bps = 10_000 if high_total == 0 else high_recalled * 10_000 // high_total
    quality = {
        "critical_high_recall_bps": high_bps,
        "overall_recall_bps": overall_bps,
        "control_false_positives": control_fp,
        "treatment_false_positives": treatment_fp,
    }
    reasons: list[str] = []
    if overall_bps < 9_000:
        reasons.append("overall_recall")
    if high_bps != 10_000:
        reasons.append("critical_high_recall")
    if treatment_fp > control_fp:
        reasons.append("false_positive_regression")
    if reasons:
        emit(
            {
                "latency_evaluated": False,
                "quality": quality,
                "reason_codes": reasons,
                "schema": "kc-pr-flow.real-pair-score-result/v1",
                "status": "quality_failed",
                "verdict": "do_not_promote",
            }
        )
        return 1
    reductions = []
    for pair in pairs:
        if pair["control_ms"] <= 0:
            raise InvalidCorpus("zero control duration")
        reductions.append((pair["control_ms"] - pair["treatment_ms"]) * 10_000 // pair["control_ms"])
    median_reduction = int(median(reductions))
    latency = {"median_reduction_bps": median_reduction, "pair_reduction_bps": reductions}
    eligible = median_reduction >= 3_333
    emit(
        {
            "latency": latency,
            "latency_evaluated": True,
            "quality": quality,
            "reason_codes": [] if eligible else ["median_latency_reduction"],
            "schema": "kc-pr-flow.real-pair-score-result/v1",
            "status": "eligible" if eligible else "latency_failed",
            "verdict": "promote_candidate" if eligible else "do_not_promote",
        }
    )
    return 0 if eligible else 1


def emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))


def initial(reason: str) -> int:
    emit(
        {
            "reason_codes": [reason],
            "schema": "kc-pr-flow.real-pair-score-result/v1",
            "status": "invalid",
            "verdict": "initial",
        }
    )
    return 2


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("validate-shape", "score"))
    parser.add_argument("--corpus", required=True, type=Path)
    parser.add_argument("--published-sha256")
    args = parser.parse_args()
    try:
        corpus, corpus_sha256 = read_corpus(args.corpus)
        if args.command == "score":
            if args.published_sha256 is None or args.published_sha256 != corpus_sha256:
                return initial("unbound_publication")
            if corpus.get("evidence_tier") == "real-pair-shape-only":
                return initial("non_field_evidence")
            return score_field(validate_field(corpus))
        pair_count = validate_shape(corpus)
    except (InvalidCorpus, OSError, UnicodeError, json.JSONDecodeError):
        return initial("invalid_field" if args.command == "score" else "invalid_shape")
    emit(
        {
            "pair_count": pair_count,
            "schema": "kc-pr-flow.real-pair-score-result/v1",
            "status": "valid_shape",
            "verdict": "do_not_promote",
        }
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
