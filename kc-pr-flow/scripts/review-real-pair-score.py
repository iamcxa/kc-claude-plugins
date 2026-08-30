#!/usr/bin/env python3
"""Validate real-pair scorer inputs without promoting shape fixtures."""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
import sys
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


class InvalidCorpus(ValueError):
    """The corpus is not a closed real-pair shape."""


def closed_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise InvalidCorpus("duplicate member")
        result[key] = value
    return result


def read_corpus(path: Path) -> dict[str, Any]:
    info = os.lstat(path)
    if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_CORPUS_BYTES:
        raise InvalidCorpus("unsafe corpus")
    raw = path.read_bytes()
    if len(raw) != info.st_size or b"\x00" in raw:
        raise InvalidCorpus("unstable corpus")
    value = json.loads(raw.decode("utf-8"), object_pairs_hook=closed_object)
    if not isinstance(value, dict):
        raise InvalidCorpus("corpus is not an object")
    return value


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
    args = parser.parse_args()
    try:
        pair_count = validate_shape(read_corpus(args.corpus))
    except (InvalidCorpus, OSError, UnicodeError, json.JSONDecodeError):
        return initial("invalid_shape")
    if args.command == "score":
        return initial("non_field_evidence")
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
