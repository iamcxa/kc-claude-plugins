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
FIELD_PAIR_KEYS = PAIR_KEYS | {"control", "manifest", "treatment"}
FIELD_ADJUDICATION_KEYS = {
    "candidate_to_defect",
    "candidates",
    "content_sha256",
    "defects",
    "duplicate_groups",
    "schema",
}
DEFECT_KEYS = {"defect_id", "pair_id", "severity"}
CANDIDATE_KEYS = {"candidate_id", "evidence_sha256", "pair_id"}
MAPPING_KEYS = {"candidate_id", "defect_id"}
DUPLICATE_KEYS = {"candidate_ids", "group_id"}
ARM_KEYS = {"candidate_ids", "timing"}
TIMING_MANIFEST_KEYS = {"receipts", "schema"}
TIMING_RECEIPT_KEYS = {"arm", "pair_id", "timing_sha256"}
ARM_MAPPING_KEYS = {"candidates", "schema"}
ARM_MAPPING_ENTRY_KEYS = {"arm", "candidate_id", "pair_id"}
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
MANIFEST_KEYS = {"control", "pair_id", "required_lanes", "schema", "treatment"}
IDENTITY_KEYS = {"base_sha", "config_hash", "head_sha", "mode", "pr_number", "repository", "review_key"}
TOKEN = re.compile(r"^[a-z][a-z0-9._-]{0,63}$")
DEFECT_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
HASH64 = re.compile(r"^[0-9a-f]{64}$")
HASH40 = re.compile(r"^[0-9a-f]{40}$")
REPOSITORY = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
SEVERITIES = {"Critical", "High", "Medium", "Low"}
ARMS = {"control", "treatment"}


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


def canonical_sha256(value: Any) -> str:
    canonical = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(canonical).hexdigest()


def validate_timing_manifest(value: Any, file_sha256: str, published_sha256: str | None) -> dict[tuple[str, str], str]:
    if not isinstance(value, dict) or set(value) != TIMING_MANIFEST_KEYS or value["schema"] != "kc-pr-flow.timing-receipt-manifest/v1":
        raise InvalidCorpus("timing manifest shape")
    if published_sha256 != file_sha256:
        raise InvalidCorpus("unbound timing manifest")
    result: dict[tuple[str, str], str] = {}
    order: list[tuple[str, str]] = []
    if not isinstance(value["receipts"], list):
        raise InvalidCorpus("timing manifest receipts")
    for receipt in value["receipts"]:
        if not isinstance(receipt, dict) or set(receipt) != TIMING_RECEIPT_KEYS:
            raise InvalidCorpus("timing manifest receipt")
        identity = (receipt["pair_id"], receipt["arm"])
        if (
            not isinstance(identity[0], str)
            or PAIR_ID.fullmatch(identity[0]) is None
            or identity[1] not in ARMS
            or not isinstance(receipt["timing_sha256"], str)
            or HASH64.fullmatch(receipt["timing_sha256"]) is None
            or identity in result
        ):
            raise InvalidCorpus("timing manifest identity")
        result[identity] = receipt["timing_sha256"]
        order.append(identity)
    if order != sorted(order):
        raise InvalidCorpus("timing manifest order")
    return result


def validate_arm_mapping(value: Any, file_sha256: str, published_sha256: str | None) -> dict[str, tuple[str, str]]:
    if not isinstance(value, dict) or set(value) != ARM_MAPPING_KEYS or value["schema"] != "kc-pr-flow.post-blind-arm-mapping/v1":
        raise InvalidCorpus("arm mapping shape")
    if published_sha256 != file_sha256:
        raise InvalidCorpus("unbound arm mapping")
    result: dict[str, tuple[str, str]] = {}
    if not isinstance(value["candidates"], list):
        raise InvalidCorpus("arm mappings")
    for entry in value["candidates"]:
        if not isinstance(entry, dict) or set(entry) != ARM_MAPPING_ENTRY_KEYS:
            raise InvalidCorpus("arm mapping entry")
        candidate_id = entry["candidate_id"]
        if (
            not isinstance(candidate_id, str)
            or HASH64.fullmatch(candidate_id) is None
            or not isinstance(entry["pair_id"], str)
            or PAIR_ID.fullmatch(entry["pair_id"]) is None
            or entry["arm"] not in ARMS
            or candidate_id in result
        ):
            raise InvalidCorpus("arm mapping identity")
        result[candidate_id] = (entry["pair_id"], entry["arm"])
    if list(result) != sorted(result):
        raise InvalidCorpus("arm mapping order")
    return result


def validate_identity(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != IDENTITY_KEYS:
        raise InvalidCorpus("identity shape")
    if not isinstance(value["repository"], str) or REPOSITORY.fullmatch(value["repository"]) is None:
        raise InvalidCorpus("repository identity")
    if not isinstance(value["pr_number"], int) or isinstance(value["pr_number"], bool) or value["pr_number"] <= 0:
        raise InvalidCorpus("pr identity")
    if any(not isinstance(value[key], str) or HASH40.fullmatch(value[key]) is None for key in ("base_sha", "head_sha")):
        raise InvalidCorpus("revision identity")
    if not isinstance(value["config_hash"], str) or HASH64.fullmatch(value["config_hash"]) is None:
        raise InvalidCorpus("config identity")
    if value["mode"] not in FALLBACKS:
        raise InvalidCorpus("mode identity")
    expected_key = hashlib.sha256(
        f'{value["repository"]}|{value["pr_number"]}|{value["base_sha"]}|{value["head_sha"]}|{value["config_hash"]}'.encode()
    ).hexdigest()
    if value["review_key"] != expected_key:
        raise InvalidCorpus("review identity")
    return value


def validate_manifest(value: Any, pair_id: str, fallback: str) -> tuple[dict[str, Any], dict[str, Any], list[str]]:
    if not isinstance(value, dict) or set(value) != MANIFEST_KEYS:
        raise InvalidCorpus("manifest shape")
    if value["schema"] != "kc-pr-flow.real-pair-manifest/v1" or value["pair_id"] != pair_id:
        raise InvalidCorpus("manifest identity")
    lanes = value["required_lanes"]
    if not isinstance(lanes, list) or not lanes or lanes != sorted(set(lanes)) or any(
        not isinstance(lane, str) or TOKEN.fullmatch(lane) is None for lane in lanes
    ):
        raise InvalidCorpus("required lanes")
    control = validate_identity(value["control"])
    treatment = validate_identity(value["treatment"])
    for key in ("repository", "pr_number", "base_sha", "head_sha", "config_hash", "review_key"):
        if control[key] != treatment[key]:
            raise InvalidCorpus("cross-arm identity")
    if control["mode"] != "initial" or treatment["mode"] != fallback:
        raise InvalidCorpus("arm mode")
    return control, treatment, lanes


def validate_timing(value: Any, identity: dict[str, Any], required_lanes: list[str]) -> int:
    if not isinstance(value, dict) or set(value) != TIMING_KEYS:
        raise InvalidCorpus("timing shape")
    if value["schema"] != "kc-pr-flow.review-timing/v1" or value["mode"] not in FALLBACKS:
        raise InvalidCorpus("timing identity")
    if not isinstance(value["review_key"], str) or HASH64.fullmatch(value["review_key"]) is None:
        raise InvalidCorpus("timing review key")
    if value["mode"] != identity["mode"] or value["review_key"] != identity["review_key"]:
        raise InvalidCorpus("timing manifest mismatch")
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
    external = [attribution[key] for key in ("hosted_ci", "human_wait", "unrelated_queue")]
    if not all(nonnegative_integer(item) for item in external):
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
    if lane_ids != required_lanes:
        raise InvalidCorpus("lane coverage")
    if max(lane["duration_ms"] for lane in lanes) > durations["required_lanes_critical_path"]:
        raise InvalidCorpus("lane critical path")
    if (
        durations["required_lanes_critical_path"]
        + durations["targeted_verification_critical_path"]
        + durations["collation_and_draft"]
        > durations["review_to_confirmation_ready"] + sum(external)
    ):
        raise InvalidCorpus("review component equation")
    if (
        durations["review_to_confirmation_ready"]
        + durations["identity_and_plan"]
        + durations["inventory"]
        + durations["collector"]
        + sum(external)
        != durations["wall_to_confirmation_ready"]
    ):
        raise InvalidCorpus("wall equation")
    return durations["review_to_confirmation_ready"]


def validate_arm(
    value: Any, identity: dict[str, Any], required_lanes: list[str], timing_sha256: str | None
) -> tuple[set[str], int]:
    if not isinstance(value, dict) or set(value) != ARM_KEYS:
        raise InvalidCorpus("arm shape")
    candidate_ids = value["candidate_ids"]
    if not isinstance(candidate_ids, list) or any(
        not isinstance(item, str) or HASH64.fullmatch(item) is None for item in candidate_ids
    ):
        raise InvalidCorpus("candidate ids")
    if candidate_ids != sorted(set(candidate_ids)):
        raise InvalidCorpus("candidate order")
    if timing_sha256 is None or timing_sha256 != canonical_sha256(value["timing"]):
        raise InvalidCorpus("external timing hash")
    timing_ms = validate_timing(value["timing"], identity, required_lanes)
    return set(candidate_ids), timing_ms


def validate_adjudication(value: Any, published_sha256: str | None) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != FIELD_ADJUDICATION_KEYS:
        raise InvalidCorpus("adjudication shape")
    if value["schema"] != "kc-pr-flow.blind-adjudication/v1":
        raise InvalidCorpus("adjudication schema")
    embedded_sha256 = value["content_sha256"]
    if not isinstance(embedded_sha256, str) or HASH64.fullmatch(embedded_sha256) is None:
        raise InvalidCorpus("adjudication hash")
    unsealed = dict(value)
    del unsealed["content_sha256"]
    actual_sha256 = canonical_sha256(unsealed)
    if embedded_sha256 != actual_sha256 or published_sha256 != actual_sha256:
        raise InvalidCorpus("unbound adjudication")

    candidates = value["candidates"]
    if not isinstance(candidates, list) or not candidates:
        raise InvalidCorpus("candidates")
    candidate_by_id: dict[str, dict[str, Any]] = {}
    for candidate in candidates:
        if not isinstance(candidate, dict) or set(candidate) != CANDIDATE_KEYS:
            raise InvalidCorpus("candidate shape")
        candidate_id = candidate["candidate_id"]
        if not isinstance(candidate_id, str) or HASH64.fullmatch(candidate_id) is None:
            raise InvalidCorpus("candidate id")
        if not isinstance(candidate["pair_id"], str) or PAIR_ID.fullmatch(candidate["pair_id"]) is None:
            raise InvalidCorpus("candidate identity")
        if not isinstance(candidate["evidence_sha256"], str) or HASH64.fullmatch(candidate["evidence_sha256"]) is None:
            raise InvalidCorpus("candidate evidence")
        if candidate_id in candidate_by_id:
            raise InvalidCorpus("duplicate candidate")
        candidate_by_id[candidate_id] = candidate
    if list(candidate_by_id) != sorted(candidate_by_id):
        raise InvalidCorpus("candidate order")

    defects = value["defects"]
    if not isinstance(defects, list) or not defects:
        raise InvalidCorpus("defects")
    defect_by_pair: dict[str, dict[str, str]] = {}
    defect_order: list[tuple[str, str]] = []
    for defect in defects:
        if not isinstance(defect, dict) or set(defect) != DEFECT_KEYS:
            raise InvalidCorpus("defect shape")
        pair_id, defect_id = defect["pair_id"], defect["defect_id"]
        if not isinstance(pair_id, str) or PAIR_ID.fullmatch(pair_id) is None:
            raise InvalidCorpus("defect pair")
        if not isinstance(defect_id, str) or DEFECT_ID.fullmatch(defect_id) is None or defect["severity"] not in SEVERITIES:
            raise InvalidCorpus("defect identity")
        if defect_id in defect_by_pair.setdefault(pair_id, {}):
            raise InvalidCorpus("duplicate defect")
        defect_by_pair[pair_id][defect_id] = defect["severity"]
        defect_order.append((pair_id, defect_id))
    if defect_order != sorted(defect_order):
        raise InvalidCorpus("defect order")

    mappings = value["candidate_to_defect"]
    if not isinstance(mappings, list):
        raise InvalidCorpus("candidate mapping")
    mapped: dict[str, str | None] = {}
    for mapping in mappings:
        if not isinstance(mapping, dict) or set(mapping) != MAPPING_KEYS:
            raise InvalidCorpus("mapping shape")
        candidate_id, defect_id = mapping["candidate_id"], mapping["defect_id"]
        if candidate_id not in candidate_by_id or candidate_id in mapped:
            raise InvalidCorpus("mapping candidate")
        pair_id = candidate_by_id[candidate_id]["pair_id"]
        if defect_id is not None and defect_id not in defect_by_pair.get(pair_id, {}):
            raise InvalidCorpus("mapping defect")
        mapped[candidate_id] = defect_id
    if list(mapped) != list(candidate_by_id):
        raise InvalidCorpus("mapping coverage")

    groups = value["duplicate_groups"]
    if not isinstance(groups, list) or not groups:
        raise InvalidCorpus("duplicate groups")
    grouped: list[str] = []
    group_order: list[str] = []
    group_by_candidate: dict[str, str] = {}
    for group in groups:
        if not isinstance(group, dict) or set(group) != DUPLICATE_KEYS:
            raise InvalidCorpus("duplicate group shape")
        group_id, candidate_ids = group["group_id"], group["candidate_ids"]
        if not isinstance(group_id, str) or TOKEN.fullmatch(group_id) is None:
            raise InvalidCorpus("duplicate group id")
        if not isinstance(candidate_ids, list) or not candidate_ids or candidate_ids != sorted(set(candidate_ids)):
            raise InvalidCorpus("duplicate group candidates")
        if any(candidate_id not in candidate_by_id for candidate_id in candidate_ids):
            raise InvalidCorpus("unknown duplicate candidate")
        identities = {candidate_by_id[item]["pair_id"] for item in candidate_ids}
        mapped_defects = {mapped[item] for item in candidate_ids}
        if len(identities) != 1 or len(mapped_defects) != 1:
            raise InvalidCorpus("duplicate group semantics")
        for candidate_id in candidate_ids:
            group_by_candidate[candidate_id] = group_id
        grouped.extend(candidate_ids)
        group_order.append(group_id)
    if group_order != sorted(set(group_order)) or sorted(grouped) != sorted(candidate_by_id) or len(grouped) != len(set(grouped)):
        raise InvalidCorpus("duplicate group coverage")

    return {
        "candidate_pairs": {candidate_id: candidate["pair_id"] for candidate_id, candidate in candidate_by_id.items()},
        "defects": defect_by_pair,
        "groups": group_by_candidate,
        "mapped": mapped,
    }


def validate_field(
    corpus: dict[str, Any],
    published_manifest_sha256: str | None,
    published_adjudication_sha256: str | None,
    timing_manifest: dict[tuple[str, str], str],
    arm_mapping: dict[str, tuple[str, str]],
) -> list[dict[str, Any]]:
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
    adjudication = validate_adjudication(corpus["adjudication"], published_adjudication_sha256)
    if set(arm_mapping) != set(adjudication["candidate_pairs"]) or any(
        pair_id != adjudication["candidate_pairs"][candidate_id]
        for candidate_id, (pair_id, _arm) in arm_mapping.items()
    ):
        raise InvalidCorpus("arm mapping candidate binding")
    candidates_by_arm: dict[tuple[str, str], set[str]] = {}
    for candidate_id, identity in arm_mapping.items():
        candidates_by_arm.setdefault(identity, set()).add(candidate_id)
    pairs = corpus["pairs"]
    if not isinstance(pairs, list) or len(pairs) < 5:
        raise InvalidCorpus("insufficient pairs")
    if published_manifest_sha256 is None or not HASH64.fullmatch(published_manifest_sha256):
        raise InvalidCorpus("unbound manifest")
    manifests = [pair.get("manifest") if isinstance(pair, dict) else None for pair in pairs]
    if canonical_sha256(manifests) != published_manifest_sha256:
        raise InvalidCorpus("manifest hash mismatch")
    pair_ids: list[str] = []
    frozen_identities: set[tuple[Any, ...]] = set()
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
        control_identity, treatment_identity, required_lanes = validate_manifest(
            pair["manifest"], pair_id, pair["fallback_observed"]
        )
        frozen_identity = tuple(
            control_identity[key]
            for key in ("repository", "pr_number", "base_sha", "head_sha", "config_hash", "review_key")
        )
        if frozen_identity in frozen_identities:
            raise InvalidCorpus("duplicate frozen identity")
        frozen_identities.add(frozen_identity)
        defects = adjudication["defects"].get(pair_id, {})
        if not defects:
            raise InvalidCorpus("adjudicated defects")
        defect_set = set(defects)
        high_ids = {defect_id for defect_id, severity in defects.items() if severity in {"Critical", "High"}}
        control_candidates, control_ms = validate_arm(
            pair["control"], control_identity, required_lanes, timing_manifest.get((pair_id, "control"))
        )
        treatment_candidates, treatment_ms = validate_arm(
            pair["treatment"],
            treatment_identity,
            required_lanes,
            timing_manifest.get((pair_id, "treatment")),
        )
        if control_candidates != candidates_by_arm.get((pair_id, "control"), set()) or treatment_candidates != candidates_by_arm.get(
            (pair_id, "treatment"), set()
        ):
            raise InvalidCorpus("arm candidate binding")
        control_findings = {adjudication["mapped"][item] for item in control_candidates if adjudication["mapped"][item] is not None}
        treatment_findings = {
            adjudication["mapped"][item] for item in treatment_candidates if adjudication["mapped"][item] is not None
        }
        control_fp = len(
            {adjudication["groups"][item] for item in control_candidates if adjudication["mapped"][item] is None}
        )
        treatment_fp = len(
            {adjudication["groups"][item] for item in treatment_candidates if adjudication["mapped"][item] is None}
        )
        pair_ids.append(pair_id)
        validated.append(
            {
                "defect_ids": defect_set,
                "high_ids": high_ids,
                "control_findings": control_findings,
                "control_fp": control_fp,
                "control_ms": control_ms,
                "treatment_findings": treatment_findings,
                "treatment_fp": treatment_fp,
                "treatment_ms": treatment_ms,
            }
        )
    if pair_ids != sorted(set(pair_ids)):
        raise InvalidCorpus("pair order")
    registered = set(pair_ids)
    if (
        set(adjudication["defects"]) != registered
        or set(adjudication["candidate_pairs"].values()) != registered
        or {pair_id for pair_id, _arm in arm_mapping.values()} != registered
        or set(timing_manifest) != {(pair_id, arm) for pair_id in registered for arm in ARMS}
    ):
        raise InvalidCorpus("registered pair coverage")
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
    parser.add_argument("--published-manifest-sha256")
    parser.add_argument("--published-adjudication-sha256")
    parser.add_argument("--timing-manifest", type=Path)
    parser.add_argument("--published-timing-manifest-sha256")
    parser.add_argument("--arm-mapping-manifest", type=Path)
    parser.add_argument("--published-arm-mapping-sha256")
    args = parser.parse_args()
    try:
        corpus, corpus_sha256 = read_corpus(args.corpus)
        if args.command == "score":
            if args.published_sha256 is None or args.published_sha256 != corpus_sha256:
                return initial("unbound_publication")
            if corpus.get("evidence_tier") == "real-pair-shape-only":
                return initial("non_field_evidence")
            if args.timing_manifest is None or args.arm_mapping_manifest is None:
                raise InvalidCorpus("missing external manifest")
            timing_value, timing_file_sha256 = read_corpus(args.timing_manifest)
            arm_mapping_value, arm_mapping_file_sha256 = read_corpus(args.arm_mapping_manifest)
            timing_manifest = validate_timing_manifest(
                timing_value, timing_file_sha256, args.published_timing_manifest_sha256
            )
            arm_mapping = validate_arm_mapping(
                arm_mapping_value, arm_mapping_file_sha256, args.published_arm_mapping_sha256
            )
            return score_field(
                validate_field(
                    corpus,
                    args.published_manifest_sha256,
                    args.published_adjudication_sha256,
                    timing_manifest,
                    arm_mapping,
                )
            )
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
