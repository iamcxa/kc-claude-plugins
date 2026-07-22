#!/usr/bin/env python3
"""Fail-closed JSON and file-ingestion primitives for review-runtime.sh."""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, List, Tuple


class DuplicateMember(ValueError):
    """Raised when any JSON object repeats a member name."""


def unique_object(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateMember
        result[key] = value
    return result


def reject_nonstandard_constant(_: str) -> None:
    raise ValueError


def unique_json() -> int:
    try:
        payload = sys.stdin.buffer.read().decode("utf-8")
        json.loads(
            payload,
            object_pairs_hook=unique_object,
            parse_constant=reject_nonstandard_constant,
        )
    except DuplicateMember:
        return 1
    except (UnicodeDecodeError, ValueError, json.JSONDecodeError):
        return 2
    return 0


def main(argv: List[str]) -> int:
    if argv == ["unique-json"]:
        return unique_json()
    print("usage: review-runtime-safe-io.py unique-json", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
