#!/usr/bin/env python3
"""Exact portable-delivery contract and known-mutant checks."""

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
MOD = (ROOT / "docs/dev/_mods/pr-merge.md").read_text(encoding="utf-8")
README = (ROOT / "docs/dev/README.md").read_text(encoding="utf-8")
START = "<!-- kc-dev-flow runtime extension:start -->\n"
if MOD.count(START) != 1:
    raise SystemExit("portable-delivery: runtime extension marker is not unique")
EXTENSION = START + MOD.split(START, 1)[1]


def markdown_row(line: str) -> tuple[str, ...]:
    return tuple(cell.strip() for cell in line.strip().strip("|").split("|"))


def table(text: str, heading: str) -> list[tuple[str, ...]]:
    marker = f"#### {heading}\n"
    if text.count(marker) != 1:
        return []
    section = text.split(marker, 1)[1]
    section = re.split(r"\n#{3,4} ", section, maxsplit=1)[0]
    return [markdown_row(line) for line in section.splitlines() if line.startswith("|")]


UNIT_ROWS = [
    ("Field", "Exact binding"),
    ("---", "---"),
    ("Worktree", "`UNIT_WORKTREE` from `{worktree}`"),
    ("Code repository", "`UNIT_CODE_REPO` from the worktree origin"),
    ("Branch", "`UNIT_BRANCH` from `{branch}`"),
    ("Base branch", "caller-supplied `UNIT_BASE_BRANCH`"),
    ("Base SHA", "approved `UNIT_BASE_SHA`"),
    ("Candidate SHA", "full approved `UNIT_CANDIDATE_SHA`"),
    ("Title", "reviewed `UNIT_TITLE`"),
    ("Body file", "mode-0600 reviewed `UNIT_BODY_FILE`"),
]

STACK_ROWS = [
    ("Layer", "`UNIT_BRANCH`", "`UNIT_BASE_BRANCH`", "`UNIT_BASE_SHA`", "Provider close line"),
    ("---", "---", "---", "---", "---"),
    (
        "bottom",
        "explicitly reviewed layer-unique delivery-unit branch",
        "trunk `$BASE`",
        "approved trunk `$BASE_SHA`",
        "omit",
    ),
    (
        "each middle",
        "explicitly reviewed layer-unique delivery-unit branch",
        "branch immediately below",
        "approved `UNIT_CANDIDATE_SHA` immediately below",
        "omit",
    ),
    (
        "top",
        "exact `delivery.branch`",
        "branch immediately below",
        "approved `UNIT_CANDIDATE_SHA` immediately below",
        "append exact `delivery.close_line` once",
    ),
]

COMPLETION_ROWS = [
    ("Evidence", "Required result", "Otherwise"),
    ("---", "---", "---"),
    ("PR repository", "explicit `PR_REPO`", "stop"),
    ("Approved candidate", "exactly one full `Candidate:` SHA in approved body", "stop"),
    ("GitHub PR", "`headRefOid` equals Candidate and `mergedAt` is non-empty", "stop"),
    ("PR feedback", "current exact-head fingerprint and evidenced dispositions", "stop"),
    ("Required checks", "explicit-repository required checks succeed", "stop"),
    ("Sentinel commit", "set and state commit both succeed", "only then guard"),
]

CREATE = 'gh pr create --draft --repo "$UNIT_CODE_REPO" --base "$UNIT_BASE_BRANCH" --head "$UNIT_BRANCH" --title "$UNIT_TITLE" --body-file "$UNIT_BODY_FILE" --assignee "@me"'
PREFLIGHT = 'git -C "$UNIT_WORKTREE" merge-tree --write-tree "$UNIT_BASE_SHA" "$UNIT_CANDIDATE_SHA"'
PUSH = 'git -C "$UNIT_WORKTREE" push origin "${UNIT_CANDIDATE_SHA}:refs/heads/${UNIT_BRANCH}"'
VIEW = 'gh pr view "$PR_NUMBER" --repo "$PR_REPO" --json body,headRefOid,mergedAt'
CHECKS = 'gh pr checks "$PR_NUMBER" --repo "$PR_REPO" --required'
SET_SENTINEL = "spacedock status --workflow-dir {dir} --set {slug} pr=pr-merge:{N}"
COMMIT_SENTINEL = "spacedock state commit {slug} --workflow-dir {dir}"
GUARD = "spacedock merge guard {slug} --workflow-dir {dir} --verdict passed"
PROVIDER_BRANCH = "bind `UNIT_BRANCH` byte-for-byte to `delivery.branch`"
PROVIDER_CLOSE = "append `delivery.close_line` exactly once to the reviewed PR body"
PROVIDER_ISSUE_OVERRIDE = "supersedes the released `Closes {issue}` rule above"
PROVIDER_STACK_TOP = "reserve both provider values for the top layer"
PROVIDER_STACK_LOWER = "Every lower layer uses its own explicitly reviewed delivery-unit branch and base, carries no provider close line"
README_BASE_POLICY = "**Local base policy: dependency-aware.**"
README_STACK_BASE = "Dependent green layers use the reviewed sibling branch immediately below and its exact candidate SHA"


def validate(text: str, readme: str = README) -> list[str]:
    errors: list[str] = []
    if table(text, "Canonical Draft delivery unit") != UNIT_ROWS:
        errors.append("canonical delivery-unit table drifted")
    if table(text, "Native stack delivery-unit composition") != STACK_ROWS:
        errors.append("provider stack delivery-unit table drifted")
    if table(text, "Single-PR completion decision") != COMPLETION_ROWS:
        errors.append("single-PR completion table drifted")
    required = {
        "canonical Draft create": CREATE,
        "released create disabled": "This is the only active PR-create command; do not execute the released inline-body command above.",
        "exact base/candidate preflight": PREFLIGHT,
        "exact candidate refspec": PUSH,
        "provider delivery branch": PROVIDER_BRANCH,
        "provider close line": PROVIDER_CLOSE,
        "provider legacy issue override": PROVIDER_ISSUE_OVERRIDE,
        "provider stack top binding": PROVIDER_STACK_TOP,
        "provider stack lower binding": PROVIDER_STACK_LOWER,
        "candidate body metadata": "Candidate: {full approved SHA}",
        "mode-0600 body": '`PR_BODY_FILE=$(mktemp)` and `chmod 600 "$PR_BODY_FILE"`',
        "one unit per PR": "A single PR binds exactly one approved delivery unit",
        "explicit PR proof": VIEW,
        "required checks": CHECKS,
        "failed commit stop": "If state commit fails, stop; do not invoke the guard.",
        "no local terminal fallback": "Do not fall back to local merge.",
    }
    for label, phrase in required.items():
        if phrase not in text:
            errors.append(f"missing {label}")
    if text.count("gh pr create") != 1:
        errors.append("local extension must contain exactly one canonical PR-create command")
    positions = [text.find(item) for item in [VIEW, CHECKS, SET_SENTINEL, COMMIT_SENTINEL, GUARD]]
    if any(position < 0 for position in positions) or positions != sorted(positions):
        errors.append("completion transcript is incomplete or out of order")
    for command in re.findall(r"`(gh pr view[^`\n]+)`", text):
        if " --repo " not in command:
            errors.append("ambient gh pr view is forbidden")
    if "Automatically fall back to local merge" in text or "automatic local-merge terminal success" in text:
        errors.append("automatic local-merge terminal success is forbidden")
    if (
        "When a PR is the selected delivery artifact, authenticated product PR"
        not in readme
        or "`mergedAt` supplies the completion time" not in readme
    ):
        errors.append("README selected-PR terminal requirement drifted")
    if README_BASE_POLICY not in readme or README_STACK_BASE not in readme:
        errors.append("README sibling-base policy drifted")
    return errors


baseline_errors = validate(EXTENSION)
if baseline_errors:
    raise SystemExit("portable-delivery:FAIL\n" + "\n".join(baseline_errors))

mutants = {
    "missing-self-assignment": (
        EXTENSION.replace(' --assignee "@me"', "", 1),
        "missing canonical Draft create",
    ),
    "ambient-view": (
        EXTENSION.replace(VIEW, VIEW.replace(' --repo "$PR_REPO"', ''), 1),
        "ambient gh pr view is forbidden",
    ),
    "continue-after-state-commit-failure": (
        EXTENSION.replace(
            "If state commit fails, stop; do not invoke the guard.",
            "If state commit fails, continue and invoke the guard.",
            1,
        ),
        "missing failed commit stop",
    ),
    "automatic-local-merge": (
        EXTENSION.replace(
            "Do not fall back to local merge.",
            "Automatically fall back to local merge and mark terminal success.",
            1,
        ),
        "automatic local-merge terminal success is forbidden",
    ),
    "provider-branch-ignored": (
        EXTENSION.replace(PROVIDER_BRANCH, "Ignore `delivery.branch`.", 1),
        "missing provider delivery branch",
    ),
    "provider-close-line-ignored": (
        EXTENSION.replace(PROVIDER_CLOSE, "Omit `delivery.close_line`.", 1),
        "missing provider close line",
    ),
    "provider-legacy-issue-restored": (
        EXTENSION.replace(PROVIDER_ISSUE_OVERRIDE, "retains the released `Closes {issue}` rule above", 1),
        "missing provider legacy issue override",
    ),
    "provider-stack-lower-reuses-top-branch": (
        EXTENSION.replace(
            "explicitly reviewed layer-unique delivery-unit branch",
            "exact `delivery.branch`",
            1,
        ),
        "provider stack delivery-unit table drifted",
    ),
    "provider-stack-lower-carries-close-line": (
        EXTENSION.replace(
            "| bottom | explicitly reviewed layer-unique delivery-unit branch | trunk `$BASE` | approved trunk `$BASE_SHA` | omit |",
            "| bottom | explicitly reviewed layer-unique delivery-unit branch | trunk `$BASE` | approved trunk `$BASE_SHA` | append exact `delivery.close_line` once |",
            1,
        ),
        "provider stack delivery-unit table drifted",
    ),
    "provider-stack-top-loses-provider-binding": (
        EXTENSION.replace(
            "| top | exact `delivery.branch` | branch immediately below | approved `UNIT_CANDIDATE_SHA` immediately below | append exact `delivery.close_line` once |",
            "| top | explicitly reviewed layer-unique delivery-unit branch | branch immediately below | approved `UNIT_CANDIDATE_SHA` immediately below | omit |",
            1,
        ),
        "provider stack delivery-unit table drifted",
    ),
}

for name, (mutant, expected) in mutants.items():
    failures = validate(mutant)
    if expected not in failures:
        raise SystemExit(f"portable-delivery:{name}: mutant survived: {failures}")
    print(f"portable-delivery:{name}:REJECTED")

readme_mutants = {
    "readme-trunk-only-restored": README.replace(
        README_BASE_POLICY,
        "**Local base policy: trunk-only, pending a refit.**",
        1,
    ),
    "readme-sibling-base-removed": README.replace(
        README_STACK_BASE,
        "Dependent green layers target trunk",
        1,
    ),
}
for name, mutant in readme_mutants.items():
    failures = validate(EXTENSION, mutant)
    if "README sibling-base policy drifted" not in failures:
        raise SystemExit(f"portable-delivery:{name}: mutant survived: {failures}")
    print(f"portable-delivery:{name}:REJECTED")

print("portable-delivery:PASS")
