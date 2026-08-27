#!/usr/bin/env python3
"""Validate that review CI selects only the contracts affected by a change."""

from __future__ import annotations

import fnmatch
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = {
    "plan": ROOT / ".github/workflows/review-plan-tests.yml",
    "runtime": ROOT / ".github/workflows/review-runtime-tests.yml",
    "shadow": ROOT / ".github/workflows/review-shadow-tests.yml",
    "post": ROOT / ".github/workflows/review-post-tests.yml",
    "evaluation": ROOT / ".github/workflows/review-evaluation-tests.yml",
    "cross_model": ROOT / ".github/workflows/cross-model-tests.yml",
}
STATIC_CONTRACT_WORKFLOW = ROOT / ".github/workflows/review-ci-contracts.yml"


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


PHASE1_PATH_OWNERS = {
    "kc-pr-flow/scripts/review-plan.sh": {"plan"},
    "kc-pr-flow/scripts/review-plan.test.sh": {"plan"},
    "kc-pr-flow/test/fixtures/review-plan/pr1693-replay.json": {"plan"},
    "kc-pr-flow/scripts/review-latency-benchmark.sh": {"evaluation"},
    "kc-pr-flow/scripts/review-latency-benchmark.test.sh": {"evaluation"},
    "kc-pr-flow/test/fixtures/review-plan/phase1-promotion.jsonl": {"evaluation"},
}

# These runtime files are deliberately shared by existing behavioral owners;
# Phase 1 adds only the plan owner for its read-only dependency.
PHASE1_SHARED_DEPENDENCY_ALLOWLIST = {
    "kc-pr-flow/scripts/review-runtime.sh": {"plan", "runtime", "shadow", "post", "evaluation"},
    "kc-pr-flow/scripts/review-runtime-safe-io.py": {"plan", "runtime", "shadow", "post", "evaluation"},
}


def phase1_path_class(path: str) -> str | None:
    if fnmatch.fnmatchcase(path, "kc-pr-flow/scripts/review-plan*.sh"):
        return "review-plan script"
    if fnmatch.fnmatchcase(path, "kc-pr-flow/scripts/review-latency-benchmark*.sh"):
        return "review-latency script"
    if path.startswith("kc-pr-flow/test/fixtures/review-plan/"):
        return "review-plan fixture"
    return None


def phase1_expected_owners(path: str) -> set[str]:
    path_class = phase1_path_class(path)
    require(path_class is not None, f"{path}: not a governed Phase 1 path")
    try:
        return PHASE1_PATH_OWNERS[path]
    except KeyError as error:
        raise AssertionError(f"{path}: unclassified {path_class}") from error


def assert_phase1_path_rejected(path: str) -> None:
    require(phase1_path_class(path) is not None, f"{path}: mutation escaped governed class")
    try:
        phase1_expected_owners(path)
    except AssertionError:
        return
    raise AssertionError(f"{path}: unknown Phase 1 path was accepted")


def validate_phase1_inventory(routes: dict[str, list[str]]) -> None:
    discovered: set[str] = set()
    for pattern in (
        "kc-pr-flow/scripts/review-plan*.sh",
        "kc-pr-flow/scripts/review-latency-benchmark*.sh",
    ):
        discovered.update(path.relative_to(ROOT).as_posix() for path in ROOT.glob(pattern))
    fixture_root = ROOT / "kc-pr-flow/test/fixtures/review-plan"
    discovered.update(
        path.relative_to(ROOT).as_posix() for path in fixture_root.rglob("*") if path.is_file()
    )

    for path in PHASE1_PATH_OWNERS:
        require((ROOT / path).is_file(), f"{path}: missing governed Phase 1 file")
    for path in sorted(discovered):
        expected = phase1_expected_owners(path)
        actual = selected_workflows(path, routes)
        require(actual == expected, f"{path}: expected {sorted(expected)}, got {sorted(actual)}")


def validate_phase1_static_ownership() -> None:
    text = STATIC_CONTRACT_WORKFLOW.read_text(encoding="utf-8")
    pull_paths = event_paths(text, "pull_request")
    push_paths = event_paths(text, "push")
    require(pull_paths == push_paths, "static contracts: pull and push routing differ")
    require(
        "kc-pr-flow/test/fixtures/review-plan/*" in pull_paths,
        "static contracts: review-plan fixtures are not routed",
    )
    for path in PHASE1_PATH_OWNERS:
        require(
            any(fnmatch.fnmatchcase(path, pattern) for pattern in pull_paths),
            f"{path}: missing static-contract owner",
        )


texts = {name: path.read_text(encoding="utf-8") for name, path in WORKFLOWS.items()}
routes: dict[str, list[str]] = {}

for name, text in texts.items():
    pull_paths = event_paths(text, "pull_request")
    push_paths = event_paths(text, "push")
    require(pull_paths == push_paths, f"{name}: pull and push routing differ")
    require(len(pull_paths) == len(set(pull_paths)), f"{name}: duplicate path filters")
    routes[name] = pull_paths

expected_routes = {
    **PHASE1_PATH_OWNERS,
    ".github/workflows/review-plan-tests.yml": {"plan"},
    **PHASE1_SHARED_DEPENDENCY_ALLOWLIST,
    "kc-pr-flow/scripts/review-runtime.test.sh": {"runtime"},
    "kc-pr-flow/test/fixtures/review-runtime/valid-events.jsonl": {"runtime"},
    "kc-pr-flow/scripts/review-shadow.test.sh": {"shadow"},
    "kc-pr-flow/scripts/review-post.sh": {"post"},
    "kc-pr-flow/test/fixtures/review-post/reviews.json": {"post"},
    "kc-pr-flow/scripts/review-runtime-benchmark.sh": {"evaluation"},
    "kc-pr-flow/scripts/review-ablation-core.py": {"evaluation"},
    "kc-pr-flow/test/fixtures/review-runtime/paired-runs.jsonl": {"evaluation"},
    "kc-pr-flow/skills/kc-pr-review/SKILL.md": {"plan", "shadow", "evaluation", "cross_model"},
    "kc-pr-flow/reference/review-triage.md": {"plan", "evaluation"},
    "kc-pr-flow/reference/review-runtime.md": {"plan", "runtime"},
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

validate_phase1_inventory(routes)
validate_phase1_static_ownership()

for unknown_phase1_path in (
    "kc-pr-flow/scripts/review-plan-helper.sh",
    "kc-pr-flow/test/fixtures/review-plan/unclassified-case.json",
):
    assert_phase1_path_rejected(unknown_phase1_path)

expected_commands = {
    "plan": ["bash kc-pr-flow/scripts/review-plan.test.sh"],
    "runtime": ["bash kc-pr-flow/scripts/review-runtime.test.sh"],
    "shadow": ["bash kc-pr-flow/scripts/review-shadow.test.sh"],
    "post": ["bash kc-pr-flow/scripts/review-post.test.sh"],
    "evaluation": [
        "bash kc-pr-flow/scripts/review-runtime-benchmark.test.sh",
        "bash kc-pr-flow/scripts/review-ablation.test.sh",
        "bash kc-pr-flow/scripts/review-latency-benchmark.test.sh",
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
