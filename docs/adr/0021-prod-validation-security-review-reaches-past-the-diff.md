# 0021. A prod task's validation runs one security review that reaches past the diff and the merge-ask check enforces

Date: 2026-10-17

## Status

Accepted

## Context

Relay PR #347 exposed existing comment and session write paths that had no total cap, and that code was outside the PR's diff. On that PR at its reviewed head, `kc-pr-flow:tob-security-reviewer` at `security_tier: full` under its own contract named the prompt injection and never the unbounded writes, on Sonnet 5.5, Opus 5.5 and Fable 5.1 alike (0 of 6 runs). The same agent with one added paragraph (the Reach brief, now in `skills/validation/profiles/prod.md`) named them in 4 of 4 runs (Sonnet twice, Opus once, Fable once) and returned `findings: []` on a Python check script with no public surface. No run of 14 was a refusal. Cost per review on Sonnet, relay size: 0.86 to 0.91 USD assumed (4.07 to 4.33 ceiling); Opus about 2.2 and Fable about 12.3 for the same paragraph. "Assumed" prices cache writes at 1.25x and reads at 0.1x the input price, and output tokens are estimated; neither is verified. ADR 0019 left the validation-gate review and the default model to this task.

## Decision

**Words:** 「那就照建議」 — Captain, 2026-10-17, chat, approving the six batch-2 ideation gates, each of which stated its recommendations (this task's D1 to D4)

**Options considered:**
- D1 model and effort: `model: sonnet` for validation and ideation, one agent definition (chosen); Opus or Fable by public surface, or a second definition by complexity — not chosen: the model was not the lever in 14 runs and effort was never varied
- D2 refusal: hold, no rerun and no model switch (chosen); rerun on Opus — not chosen: never exercised, and the worker would swap the model that refused
- D3 enforcement: `delivery_gate.py check` at the merge ask plus the command in the worker's acceptance script, no FO word changed (chosen); an FO step in `### validation` — not chosen: about 25 words in a file 16 words under budget
- D4 rerun: a new review for every new candidate head (chosen); a rule keyed to "touches a public surface" — not chosen: it asks the worker to judge exposure, the step that failed on #347

**Recommended:** the first option of each of D1 to D4, as the Captain accepted.

A prod task's validation worker dispatches the reviewer once with the Reach brief, saves the report as `security/validation-<N>.yaml`, writes `Security review (validation): <path> at <head>` and one `Security finding (validation <N>) <n>:` line per finding (`Material`, `declined` on MEDIUM or LOW only, or `Needs decision`). `validation_security.py`, called from `delivery_gate.py check`, refuses a prod task with no review, a `not run` review, a review at any head but the dispatched one the PR head equals, a profile line it cannot read as poc, pilot or prod, a repeated finding line, a report that is not a `tob_security_review` report, a finding with no line, a declined HIGH or CRITICAL, or an open Material finding. A reply with no report is saved, recorded as `not run: reviewer returned no report (<model>)`, and holds the stage, at ideation and at validation.

## Consequences

FO reads 10 more words at the merge ask of a prod task and none elsewhere; each prod review costs the amounts above, again for each new candidate head. The check proves a report with this shape exists at a dispatched head and every finding has a disposition; it cannot tell a real zero-finding report from a fabricated one, or which brief produced it. A worker that skips the review meets the hold at the merge ask, not at the validation gate. The Reach brief is fitted to one miss on one PR from one repository; Opus and Fable are n=1 each. An adopter without kc-pr-flow, or a Codex-hosted worker that cannot dispatch the Claude agent, holds every prod validation. Reopen if a refusal occurs, if a stronger model finds a class Sonnet misses under the same brief, or if the brief misses a write class on another repository.
