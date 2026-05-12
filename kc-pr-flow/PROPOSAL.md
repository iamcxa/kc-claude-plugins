# Proposals: kc-pr-flow improvements (run 2)

## 1. Advisory items must ALL appear as inline comments

### Signal
- ID: sig-20260313-001
- Source: journal
- Date: 2026-03-13
- Confidence: high
- Related proxy signal: review-friction

### Current State
Review agents classify findings as "advisory" but the skill does not explicitly instruct that advisory items must be posted as inline comments. Agents omit them or group them in the review body, reducing review granularity.

### Suggested Change
Add explicit instruction to kc-pr-review that ALL findings — including advisory-category items — must be posted as inline comments on the specific line, not summarized in the review body.

### Impact Scope
- Files likely affected: `skills/kc-pr-review/SKILL.md`
- Cross-plugin dependencies: none

### North Star Alignment
All review findings are actionable and located at the exact code line.

---

## 2. GitHub API silently rejects inline comments outside diff hunks

### Signal
- ID: sig-20260313-002
- Source: journal
- Date: 2026-03-13
- Confidence: high
- Related proxy signal: review-friction

### Current State
The GitHub PR Review API requires the `line` parameter to fall within a diff hunk. Comments targeting unchanged code between hunks silently fail (API returns 422). The skill does not guide agents to handle this constraint.

### Suggested Change
Add a fallback strategy to the review reference: when inline comment fails (422 or line not in diff), fall back to file-level comment or include the finding in the review body with the file:line reference.

### Impact Scope
- Files likely affected: `reference/review-triage.md`, `skills/kc-pr-review/SKILL.md`
- Cross-plugin dependencies: none

### North Star Alignment
Zero silently dropped review comments — every finding reaches the PR author.
