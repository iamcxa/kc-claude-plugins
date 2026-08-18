#!/usr/bin/env python3
"""Validate that review CI selects only the contracts affected by a change."""

from __future__ import annotations

import fnmatch
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = {
    "runtime": ROOT / ".github/workflows/review-runtime-tests.yml",
    "shadow": ROOT / ".github/workflows/review-shadow-tests.yml",
    "post": ROOT / ".github/workflows/review-post-tests.yml",
    "evaluation": ROOT / ".github/workflows/review-evaluation-tests.yml",
    "cross_model": ROOT / ".github/workflows/cross-model-tests.yml",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def event_paths(text: str, event: str) -> list[str]:
    lines = text.splitlines()
    event_marker = f"  {event}:"
    try:
        start = lines.index(event_marker) + 1
    except ValueError as error:
        raise AssertionError(f"missing {event} trigger") from error

    paths: list[str] = []
    in_paths = False
    for line in lines[start:]:
        if line.startswith("  ") and not line.startswith("    "):
            break
        if line == "    paths:":
            in_paths = True
            continue
        if in_paths:
            if line.startswith("      - "):
                paths.append(line.removeprefix("      - ").strip('"'))
            elif line.strip() and not line.startswith("      "):
                break
    require(paths, f"{event} has no paths")
    return paths


def selected_workflows(path: str, routes: dict[str, list[str]]) -> set[str]:
    return {
        name
        for name, patterns in routes.items()
        if any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns)
    }


texts = {name: path.read_text(encoding="utf-8") for name, path in WORKFLOWS.items()}
routes: dict[str, list[str]] = {}

for name, text in texts.items():
    pull_paths = event_paths(text, "pull_request")
    push_paths = event_paths(text, "push")
    require(pull_paths == push_paths, f"{name}: pull and push routing differ")
    require(len(pull_paths) == len(set(pull_paths)), f"{name}: duplicate path filters")
    routes[name] = pull_paths

expected_routes = {
    "kc-pr-flow/scripts/review-runtime.sh": {"runtime", "shadow", "post", "evaluation"},
    "kc-pr-flow/scripts/review-runtime-safe-io.py": {"runtime", "shadow", "post", "evaluation"},
    "kc-pr-flow/scripts/review-runtime.test.sh": {"runtime"},
    "kc-pr-flow/test/fixtures/review-runtime/valid-events.jsonl": {"runtime"},
    "kc-pr-flow/scripts/review-shadow.test.sh": {"shadow"},
    "kc-pr-flow/scripts/review-post.sh": {"post"},
    "kc-pr-flow/test/fixtures/review-post/reviews.json": {"post"},
    "kc-pr-flow/scripts/review-runtime-benchmark.sh": {"evaluation"},
    "kc-pr-flow/scripts/review-ablation-core.py": {"evaluation"},
    "kc-pr-flow/test/fixtures/review-runtime/paired-runs.jsonl": {"evaluation"},
    "kc-pr-flow/skills/kc-pr-review/SKILL.md": {"shadow", "evaluation", "cross_model"},
    "kc-pr-flow/reference/review-triage.md": {"evaluation"},
    "kc-pr-flow/reference/learned-patterns.md": {"evaluation"},
    "kc-pr-flow/reference/gh-api-patterns.md": set(),
    "PRODUCT.md": set(),
    "ARCHITECTURE.md": set(),
    "kc-pr-flow/README.md": set(),
    "kc-pr-flow/docs/review-runtime.md": set(),
    "kc-pr-flow/.claude-plugin/plugin.json": set(),
    ".claude-plugin/marketplace.json": set(),
    "kc-pr-flow/scripts/cross-model.sh": {"cross_model"},
    "kc-pr-flow/scripts/cross-model.test.sh": {"cross_model"},
    ".github/workflows/cross-model-tests.yml": {"cross_model"},
    "kc-pr-flow/scripts/review-architecture-diagrams-validate.sh": set(),
    "docs/ship-flow/tools/validate-tdd-ledger.py": set(),
}

for path, expected in expected_routes.items():
    actual = selected_workflows(path, routes)
    require(actual == expected, f"{path}: expected {sorted(expected)}, got {sorted(actual)}")

expected_commands = {
    "runtime": ["bash kc-pr-flow/scripts/review-runtime.test.sh"],
    "shadow": ["bash kc-pr-flow/scripts/review-shadow.test.sh"],
    "post": ["bash kc-pr-flow/scripts/review-post.test.sh"],
    "evaluation": [
        "bash kc-pr-flow/scripts/review-runtime-benchmark.test.sh",
        "bash kc-pr-flow/scripts/review-ablation.test.sh",
    ],
    "cross_model": ["bash kc-pr-flow/scripts/cross-model.test.sh"],
}
all_commands = [command for commands in expected_commands.values() for command in commands]

for name, text in texts.items():
    for command in all_commands:
        require(
            (command in text) == (command in expected_commands[name]),
            f"{name}: wrong behavioral suite ownership for {command}",
        )
    for retired in (
        "validate-tdd-ledger.py",
        "review-tdd-evidence",
        "grep -Fq",
        "review-architecture-diagrams.test.sh",
    ):
        require(retired not in text, f"{name}: retained non-owned check {retired}")

print("review CI routing contract: PASS")
