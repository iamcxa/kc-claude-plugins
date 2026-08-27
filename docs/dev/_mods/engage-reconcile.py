#!/usr/bin/env python3
"""Compare two normalized planning snapshots without writing either side."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import cast


MOVEMENT_FIELDS = ("planning-window", "planning-outcome")
CONTENT_FIELDS = ("accepted-goal", "non-goals")
REQUIRED_FIELDS = ("source", *MOVEMENT_FIELDS, *CONTENT_FIELDS)
TEXT_SENTINELS = {
    "null", "none", "unknown", "tbd", "todo", "~", "true", "false",
    "[]", "{}", "|", ">", "&", "*", "!", "<>",
}
PLACEHOLDER_PATTERN = re.compile(r"<[^<>]+>")


class ReconcileError(RuntimeError):
    """A fail-closed normalized-input error."""


def valid_text(value: object) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    stripped = value.strip()
    return (
        stripped.casefold() not in TEXT_SENTINELS
        and PLACEHOLDER_PATTERN.fullmatch(stripped) is None
    )


def reject_duplicate_fields(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ReconcileError(f"duplicate field: {key}")
        result[key] = value
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Compare ephemeral normalized admission and current Ready sets. "
            "Exit 0 is clean, 1 is a classified delta, and 2 is invalid input."
        )
    )
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--current", type=Path, required=True)
    parser.add_argument("--expected-source", required=True)
    parser.add_argument("--expected-window", required=True)
    parser.add_argument("--expected-outcome", required=True)
    return parser.parse_args()


def read_items(path: Path, label: str) -> object:
    try:
        return json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=reject_duplicate_fields,
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ReconcileError(f"cannot read {label}: {exc}") from exc


def by_source(items: object, label: str) -> dict[str, dict[str, object]]:
    if not isinstance(items, list):
        raise ReconcileError(f"{label} must be a JSON list")
    indexed: dict[str, dict[str, object]] = {}
    for position, item in enumerate(items):
        if not isinstance(item, dict):
            raise ReconcileError(f"{label} item {position} must be a JSON object")
        for field in REQUIRED_FIELDS:
            if field not in item:
                raise ReconcileError(
                    f"{label} item {position} is missing required field: {field}"
                )
        for field in ("source", *MOVEMENT_FIELDS, "accepted-goal"):
            value = item[field]
            if not valid_text(value):
                raise ReconcileError(f"{label} item {position} has invalid {field}")
        non_goals = item["non-goals"]
        if (
            not isinstance(non_goals, list)
            or any(not valid_text(value) for value in non_goals)
            or len(non_goals) != len(set(non_goals))
        ):
            raise ReconcileError(f"{label} item {position} has invalid non-goals")
        source = item["source"]
        if source in indexed:
            raise ReconcileError(f"{label} contains duplicate source: {source}")
        indexed[source] = item
    return indexed


def comparable(item: dict[str, object], field: str) -> object:
    value = item[field]
    if field == "non-goals":
        return sorted(cast(list[str], value))
    return value


def main() -> int:
    args = parse_args()
    try:
        snapshot_items = read_items(args.snapshot, "snapshot")
        current_items = read_items(args.current, "current")
        if args.snapshot.samefile(args.current):
            raise ReconcileError("snapshot and current must be different files")
        snapshot = by_source(snapshot_items, "snapshot")
        current = by_source(current_items, "current")
        if not snapshot:
            raise ReconcileError("snapshot must contain the engaged source")
        if args.expected_source not in snapshot:
            raise ReconcileError(
                f"snapshot does not contain expected source: {args.expected_source}"
            )
        if not valid_text(args.expected_window) or not valid_text(args.expected_outcome):
            raise ReconcileError("expected planning scope is invalid")
        expected_scope = (args.expected_window, args.expected_outcome)
        engaged_scope = tuple(
            cast(str, snapshot[args.expected_source][field])
            for field in MOVEMENT_FIELDS
        )
        if engaged_scope != expected_scope:
            raise ReconcileError(
                "snapshot engaged source does not match expected planning scope"
            )
        for source, item in snapshot.items():
            item_scope = tuple(cast(str, item[field]) for field in MOVEMENT_FIELDS)
            if item_scope != expected_scope:
                raise ReconcileError(
                    f"snapshot source is outside expected planning scope: {source}"
                )
        added = sorted(current.keys() - snapshot.keys())
        removed = sorted(snapshot.keys() - current.keys())
        shared = snapshot.keys() & current.keys()
        moved = sorted(
            source
            for source in shared
            if any(
                comparable(snapshot[source], field)
                != comparable(current[source], field)
                for field in MOVEMENT_FIELDS
            )
        )
        changed = sorted(
            source
            for source in shared
            if any(
                comparable(snapshot[source], field)
                != comparable(current[source], field)
                for field in CONTENT_FIELDS
            )
        )
        result = {
            "added": added,
            "changed": changed,
            "moved": moved,
            "removed": removed,
            "status": "delta" if added or removed or changed or moved else "clean",
        }
        sys.stdout.write(json.dumps(result, sort_keys=True) + "\n")
    except ReconcileError as exc:
        print(f"engage reconcile: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"engage reconcile: unexpected comparison failure: {exc}", file=sys.stderr)
        return 2
    return 1 if result["status"] == "delta" else 0


if __name__ == "__main__":
    raise SystemExit(main())
