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
RESIDUALS_HEADING = "## Residuals"
WITHOUT_IT_HEADING = "## without-it unanswered"
RESIDUALS_CAP_ROW = "| `## Residuals` | at most three |"


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
        "residuals heading": RESIDUALS_HEADING,
        "without-it unanswered heading": WITHOUT_IT_HEADING,
        "residuals cap": RESIDUALS_CAP_ROW,
        "residuals not-tested exclusion": '"Not tested" is never a residual.',
        "residuals source": "Validation stage report's residual items",
        "without-it source": "Implementation stage report's `without-it unanswered` items",
        "optional sections placement": "placed after `## Evidence` and before the `---` separator",
        "word target exclusion": "60-120 word target excludes both sections",
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
    "residuals-cap-loosened": (
        EXTENSION.replace(RESIDUALS_CAP_ROW, "| `## Residuals` | at most five |", 1),
        "missing residuals cap",
    ),
    "residuals-not-tested-allowed": (
        EXTENSION.replace('"Not tested" is never a residual.', "", 1),
        "missing residuals not-tested exclusion",
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


RESIDUALS_CAP_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}


def parse_residuals_cap(text: str) -> int:
    """Read the cap from the extension text itself so the AC-4 oracle below
    reflects the shipped doc rather than a value hardcoded independently of it."""
    match = re.search(r"\| `## Residuals` \| at most (\w+) \|", text)
    if match is None or match.group(1) not in RESIDUALS_CAP_WORDS:
        raise SystemExit("portable-delivery:FAIL cannot parse the Residuals cap from the extension text")
    return RESIDUALS_CAP_WORDS[match.group(1)]


def render_optional_sections(residuals: list[str], without_it: list[str], cap: int) -> str:
    """AC-4 test oracle: no shipped code renders a PR body (an FO paraphrases
    the mod's prose), so this mirrors the documented placement/extraction rule
    for exercise against fixtures."""
    kept_residuals = [item for item in residuals if item.strip().lower() != "not tested"][:cap]
    body = ["## Evidence", "- 4/4 passed", ""]
    if kept_residuals:
        body += [RESIDUALS_HEADING, *(f"- {item}" for item in kept_residuals), ""]
    if without_it:
        body += [WITHOUT_IT_HEADING, *(f"- {item}" for item in without_it), ""]
    body += ["---", "[abc123d](/owner/repo/blob/deadbeef/docs/dev/.spacedock-state/fixture.md)"]
    return "\n".join(body)


def section_line_index(rendered: str, heading: str) -> int:
    return next((i for i, line in enumerate(rendered.splitlines()) if line == heading), -1)


def bullets_under(rendered: str, heading: str) -> list[str]:
    lines = rendered.splitlines()
    start = section_line_index(rendered, heading)
    if start < 0:
        return []
    items = []
    for line in lines[start + 1:]:
        if not line.startswith("- "):
            break
        items.append(line[2:])
    return items


both_fixture = render_optional_sections(
    residuals=["known limit A", "known limit B", "known limit C", "known limit D", "not tested"],
    without_it=["kc-dev-flow/scripts/example.py:helper", "docs/dev/README.md"],
    cap=parse_residuals_cap(EXTENSION),
)
fixture_lines = both_fixture.splitlines()
evidence_at = section_line_index(both_fixture, "## Evidence")
residuals_at = section_line_index(both_fixture, RESIDUALS_HEADING)
without_it_at = section_line_index(both_fixture, WITHOUT_IT_HEADING)
separator_at = next((i for i, line in enumerate(fixture_lines) if line == "---"), -1)
if not (evidence_at < residuals_at < without_it_at < separator_at):
    raise SystemExit(f"portable-delivery:FAIL fixture-with-items: sections out of order: {both_fixture}")
residual_bullets = bullets_under(both_fixture, RESIDUALS_HEADING)
if len(residual_bullets) != 3 or "not tested" in residual_bullets:
    raise SystemExit(
        f"portable-delivery:FAIL fixture-with-items: Residuals cap or not-tested exclusion violated: {residual_bullets}"
    )
without_it_bullets = bullets_under(both_fixture, WITHOUT_IT_HEADING)
if without_it_bullets != ["kc-dev-flow/scripts/example.py:helper", "docs/dev/README.md"]:
    raise SystemExit(f"portable-delivery:FAIL fixture-with-items: without-it unanswered lines dropped: {without_it_bullets}")
print("portable-delivery:fixture-with-items:PASS")

neither_fixture = render_optional_sections(residuals=[], without_it=[], cap=parse_residuals_cap(EXTENSION))
if RESIDUALS_HEADING in neither_fixture or WITHOUT_IT_HEADING in neither_fixture:
    raise SystemExit(f"portable-delivery:FAIL fixture-without-items: heading rendered with no source items: {neither_fixture}")
print("portable-delivery:fixture-without-items:PASS")

print("portable-delivery:PASS")
