#!/usr/bin/env python3
"""Validate and aggregate sanitized kc-dev-flow improvement handoffs."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


SCHEMA = "kc-dev-flow-improvement-handoff/v1"
PROPOSAL_SCHEMA = "kc-dev-flow-improvement-proposal/v1"
FINGERPRINT_SCHEMA = "kc-dev-flow-improvement-fingerprint/v1"
FIELDS = {
    "schema",
    "source_policy_revision",
    "failure_shape",
    "finding_kind_hint",
    "landing_target_hint",
    "existing_rule",
    "summary",
    "expected_value",
    "cost",
    "disproof_hook",
    "duplicate_search",
    "observations",
}
OBSERVATION_FIELDS = {"id", "evidence", "impact"}
FINDING_KINDS = {
    "rule-gap",
    "enforcement-gap",
    "local-instance",
    "duplicate/no-change",
    "unknown",
}
LANDING_TARGETS = {
    "kernel",
    "plugin-enforcement",
    "adopter-local",
    "no-change",
    "unknown",
}
SAFE_TEXT_RE = re.compile(
    r"[<>]|https?://|~/|"
    r"(?<![A-Za-z0-9._-])/(?:[A-Za-z0-9._-]+/)*[A-Za-z0-9._-]+|"
    r"[A-Za-z]:[\\/][^\s]+|"
    r"\\\\[^\s\\]+\\[^\s]+|"
    r"[$%][A-Za-z_][A-Za-z0-9_]*[\\/]|"
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}|"
    r"(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?::\d{1,5})?(?![\w.])|"
    r"\[(?:[0-9a-f]{0,4}:){2,7}[0-9a-f]{0,4}\](?::\d{1,5})?|"
    r"(?<![\w:])(?:[0-9a-f]{0,4}:){2,7}[0-9a-f]{0,4}(?![\w:])|"
    r"(?<![\w@])(?:[a-z0-9-]+\.)+[a-z]{2,24}(?=/[^\s]*|:\d{1,5})|"
    r"(?<![\w@])(?:(?:[a-z0-9-]+\.){2,}[a-z]{2,}|"
    r"(?:[a-z0-9-]+\.)+(?:com|net|org|io|dev|app|cloud|internal|local|corp|example))"
    r"(?::\d+|/[^\s]*)?|"
    r"(?:api[_-]?key|access[_-]?key|token|password|secret|authorization|cookie)"
    r"\s*[:=]|"
    r"(?:sk-|ghp_|gho_|github_pat_|AKIA|xox[baprs]-|eyJ)[A-Za-z0-9_.-]{16,}",
    re.IGNORECASE,
)
IDENTIFIER_RE = re.compile(r"^[a-z0-9][a-z0-9-]{2,127}$")
OBSERVATION_ID_RE = re.compile(
    r"^src-[a-f0-9]{12}-[a-f0-9]{16}$"
)
REVISION_RE = re.compile(r"^(?:kc-dev-flow-v\d+\.\d+\.\d+|[a-f0-9]{40,64})$")


class IntakeError(ValueError):
    """A controlled contract error."""


def require_text(value: Any, field: str, minimum: int, maximum: int) -> str:
    if not isinstance(value, str):
        raise IntakeError(f"{field} must be text")
    if not minimum <= len(value) <= maximum:
        raise IntakeError(f"{field} must contain {minimum} to {maximum} characters")
    if (
        any(ord(character) < 32 or ord(character) == 127 for character in value)
        or SAFE_TEXT_RE.search(value)
    ):
        raise IntakeError(f"{field} contains unsafe or adopter-specific text")
    return value


def validate_handoff(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != FIELDS:
        raise IntakeError("handoff fields must match the version 1 contract")
    if value["schema"] != SCHEMA:
        raise IntakeError(f"handoff schema must be {SCHEMA}")
    if not isinstance(value["source_policy_revision"], str) or not REVISION_RE.fullmatch(
        value["source_policy_revision"]
    ):
        raise IntakeError(
            "source_policy_revision must be kc-dev-flow-vX.Y.Z or a 40-64 hex Git revision"
        )
    if not isinstance(value["failure_shape"], str) or not IDENTIFIER_RE.fullmatch(
        value["failure_shape"]
    ):
        raise IntakeError("failure_shape must be a stable lowercase identifier")
    if (
        not isinstance(value["finding_kind_hint"], str)
        or value["finding_kind_hint"] not in FINDING_KINDS
    ):
        raise IntakeError("finding_kind_hint is not recognized")
    if (
        not isinstance(value["landing_target_hint"], str)
        or value["landing_target_hint"] not in LANDING_TARGETS
    ):
        raise IntakeError("landing_target_hint is not recognized")

    normalized: dict[str, Any] = {
        "schema": value["schema"],
        "source_policy_revision": value["source_policy_revision"],
        "failure_shape": value["failure_shape"],
        "finding_kind_hint": value["finding_kind_hint"],
        "landing_target_hint": value["landing_target_hint"],
        "existing_rule": require_text(value["existing_rule"], "existing_rule", 4, 160),
        "summary": require_text(value["summary"], "summary", 12, 200),
        "expected_value": require_text(
            value["expected_value"], "expected_value", 12, 300
        ),
        "cost": require_text(value["cost"], "cost", 8, 240),
        "disproof_hook": require_text(
            value["disproof_hook"], "disproof_hook", 12, 300
        ),
    }

    duplicate_search = value["duplicate_search"]
    if not isinstance(duplicate_search, list) or not 1 <= len(duplicate_search) <= 20:
        raise IntakeError("duplicate_search must contain 1 to 20 bounded queries")
    normalized["duplicate_search"] = [
        require_text(item, "duplicate_search item", 3, 160)
        for item in duplicate_search
    ]

    observations = value["observations"]
    if not isinstance(observations, list) or not 1 <= len(observations) <= 50:
        raise IntakeError("observations must contain 1 to 50 records")
    normalized_observations = []
    for observation in observations:
        if not isinstance(observation, dict) or set(observation) != OBSERVATION_FIELDS:
            raise IntakeError("observation fields must match the version 1 contract")
        if not isinstance(observation["id"], str) or not OBSERVATION_ID_RE.fullmatch(
            observation["id"]
        ):
            raise IntakeError(
                "observation id must use src-<12 hex>-<16 hex>"
            )
        normalized_observations.append(
            {
                "id": observation["id"],
                "evidence": require_text(
                    observation["evidence"], "observation evidence", 12, 300
                ),
                "impact": require_text(
                    observation["impact"], "observation impact", 12, 300
                ),
            }
        )
    namespaces = {item["id"].split("-", 2)[1] for item in normalized_observations}
    if len(namespaces) != 1:
        raise IntakeError("one handoff must contain one source namespace")
    normalized["observations"] = normalized_observations
    return normalized


def fingerprint(failure_shape: str) -> str:
    payload = json.dumps([FINGERPRINT_SCHEMA, failure_shape], separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def one_or_judgment(values: list[str]) -> str:
    return values[0] if len(values) == 1 else "requires-source-judgment"


def aggregate(handoffs: list[dict[str, Any]]) -> dict[str, Any]:
    failure_shapes = sorted({item["failure_shape"] for item in handoffs})
    if len(failure_shapes) != 1:
        raise IntakeError("one intake invocation must contain one failure shape")

    observations: dict[str, dict[str, str]] = {}
    for handoff in handoffs:
        for observation in handoff["observations"]:
            existing = observations.get(observation["id"])
            if existing is not None and existing != observation:
                raise IntakeError(
                    f"observation id collision for {observation['id']}"
                )
            observations[observation["id"]] = observation

    failure_shape = failure_shapes[0]
    digest = fingerprint(failure_shape)
    finding_kinds = sorted({item["finding_kind_hint"] for item in handoffs})
    landing_targets = sorted({item["landing_target_hint"] for item in handoffs})
    existing_rules = sorted({item["existing_rule"] for item in handoffs})
    source_revisions = sorted({item["source_policy_revision"] for item in handoffs})
    summaries = sorted({item["summary"] for item in handoffs})
    expected_values = sorted({item["expected_value"] for item in handoffs})
    costs = sorted({item["cost"] for item in handoffs})
    disproof_hooks = sorted({item["disproof_hook"] for item in handoffs})
    duplicate_search = sorted(
        {query for item in handoffs for query in item["duplicate_search"]}
    )
    observation_ids = sorted(observations)
    source_namespaces = sorted({item.split("-", 2)[1] for item in observation_ids})
    sorted_observations = [observations[item] for item in observation_ids]
    observation_label = "observation" if len(observation_ids) == 1 else "observations"
    source_label = "namespace" if len(source_namespaces) == 1 else "namespaces"
    marker = f"<!-- kc-dev-flow-improvement:v1:{digest} -->"
    body = "\n".join(
        [
            marker,
            "",
            "## Field evidence",
            "",
            *(f"- {item}" for item in summaries),
            "",
            f"- Failure shape: `{failure_shape}`",
            f"- Adopter-reported transport counts: {len(observation_ids)} distinct "
            f"field {observation_label} across {len(source_namespaces)} source "
            f"{source_label}; these counts are not source-verified.",
            f"- Source policy revisions: {', '.join(f'`{item}`' for item in source_revisions)}",
            f"- Finding hints: {', '.join(f'`{item}`' for item in finding_kinds)}",
            f"- Landing hints: {', '.join(f'`{item}`' for item in landing_targets)}",
            f"- Existing-rule hints: {', '.join(f'`{item}`' for item in existing_rules)}",
            "",
            "## Observations",
            "",
            *(
                f"- `{item['id']}`: {item['evidence']} Impact: {item['impact']}"
                for item in sorted_observations
            ),
            "",
            "## Duplicate search",
            "",
            *(f"- {item}" for item in duplicate_search),
            "",
            "## Proposal inputs",
            "",
            *(f"- Expected value: {item}" for item in expected_values),
            *(f"- Cost: {item}" for item in costs),
            *(f"- Disproof hook: {item}" for item in disproof_hooks),
            "",
            "## Authority",
            "",
            "This is a captain-review-only proposal. It creates no task, schedule, edit, post, or merge authority.",
            "",
        ]
    )
    return {
        "schema": PROPOSAL_SCHEMA,
        "fingerprint": digest,
        "failure_shape": failure_shape,
        "recurrence": len(observation_ids),
        "distinct_sources": len(source_namespaces),
        "observation_ids": observation_ids,
        "observations": sorted_observations,
        "duplicate_search": duplicate_search,
        "summaries": summaries,
        "expected_values": expected_values,
        "costs": costs,
        "disproof_hooks": disproof_hooks,
        "finding_kind_hint": one_or_judgment(finding_kinds),
        "finding_kind_hints": finding_kinds,
        "landing_target_hint": one_or_judgment(landing_targets),
        "landing_target_hints": landing_targets,
        "existing_rules": existing_rules,
        "source_policy_revisions": source_revisions,
        "authorized_action": "captain-review-only",
        "title": f"kc-dev-flow: {summaries[0].rstrip('.!?')}",
        "body": body,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate sanitized adopter handoffs and render a source proposal."
    )
    parser.add_argument(
        "--handoff",
        action="append",
        required=True,
        type=Path,
        help="Path to one sanitized kc-dev-flow improvement handoff; repeat as needed.",
    )
    return parser.parse_args()


def main() -> int:
    try:
        args = parse_args()
        handoffs = [
            validate_handoff(json.loads(path.read_text(encoding="utf-8")))
            for path in args.handoff
        ]
        print(json.dumps(aggregate(handoffs), indent=2, sort_keys=True))
        return 0
    except (
        IntakeError,
        OSError,
        TypeError,
        RecursionError,
        UnicodeDecodeError,
        json.JSONDecodeError,
    ) as error:
        print(f"improvement intake: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
