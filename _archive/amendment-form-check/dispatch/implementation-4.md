# implementation-4

Dispatched: 1383c9119eb5328543e2c4df5e562be22b74e355 (workflow checkout, kc-dev-flow-2 0.23.0 README); follow-up message to the live phase-1 worker; FO fix authorization for Cycle 1
Model: sonnet

## Checklist

Phase 2: apply the proposed declaration-line allowlist in kc-dev-flow-2/scripts/design_surfaces.py (`named` from the Supersedes value before the waiver, marker only on declaration lines, held ids from declaration lines only), keep the four new tests, rewrite the four broken mutation tests and add one mutation each for the anchor and the waiver cut, rerun the suite and the corpus, commit with named files only, run /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.23.0/extensions/roborev/roborev_gate.py again, push without force, CI green on the new head, and update the PR body's Known limits

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.23.0

FO fix authorization for #650 (Codex round 1, three P2, Cycle 1): apply the fix exactly as proposed in phase 1 (/tmp/af-phase1/proposal.diff), with "marker anywhere on a declaration line" (the stricter shape refused 7 correctly marked corpus tasks). Known limits for the PR body: evidence on the same line as a declaration can still carry the marker; a marker written only on a `Replaced by:` line (as in vehicle-based-pricing) is refused, which matches the README's "a criterion says it"; `check_criteria` still reads a bold id anywhere in an acceptance-criteria line, a separate change not made here. Do not change `check_criteria`. Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not comment on any PR, request reviews or mark ready.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
