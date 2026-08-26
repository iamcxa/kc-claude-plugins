#!/usr/bin/env python3
"""Contract coverage for the review-only kc-pr-review minimum-stack POC."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "kc-pr-flow/skills/kc-pr-review/SKILL.md"
README = ROOT / "kc-pr-flow/README.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"minimum-stack review contract: {message}")


def section(text: str, start: str, end: str) -> str:
    begin = text.find(start)
    finish = text.find(end, begin + len(start))
    require(begin >= 0 and finish >= 0, "missing bounded minimum-stack pass")
    return text[begin : finish + len(end)]


def main() -> int:
    skill = SKILL.read_text(encoding="utf-8")
    bounded = section(
        skill,
        "<!-- minimum-stack-review-pass:start -->",
        "<!-- minimum-stack-review-pass:end -->",
    )
    for phrase in (
        "review-only",
        "CURRENT_BASE_SHA",
        "CURRENT_HEAD_SHA",
        "exact diff",
        "largest added responsibility",
        "served AC",
        "without-it",
        "proven",
        "unknown",
        "unnecessary",
        "not approval",
        "stale or malformed",
        "normal review",
        "cannot post",
        "Ready",
        "merge",
        "workflow state",
    ):
        require(phrase in bounded, f"pass omits {phrase!r}")
    require(
        "test," in bounded and "CI check, mutation, or runtime evidence" in bounded,
        "proven status lacks a falsifiable-evidence boundary",
    )
    require(
        "never turn `unknown` into approval" in bounded,
        "unknown can be mistaken for approval",
    )
    require(
        "#289" in bounded and "Issue #149" in bounded and "read-only" in bounded,
        "the #289 / Issue #149 dogfood route is not explicitly read-only",
    )
    for phrase in (
        "authoritative work-item content",
        "when accessible",
        "content or anchor mapping is absent",
        "Status: unknown",
        "cannot approve",
        "never `UNCERTAIN`",
        "Exact diff is authoritative for change shape",
        "`changed_files` is context, not a complete diff claim",
        "valid v2 handoff",
        "ac-1",
    ):
        require(phrase in bounded, f"exact handoff contract omits {phrase!r}")
    require("minimum-stack" in README.read_text(encoding="utf-8"), "README omits the POC trigger")
    print("minimum-stack review contract: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
