# implementation-5

Dispatched: 1383c9119eb5328543e2c4df5e562be22b74e355 (workflow checkout, kc-dev-flow-2 0.23.0 README); follow-up message to the live cycle-2 phase-1 worker; FO fix authorization for Cycle 2
Model: sonnet

## Checklist

Phase 2: replace the lookahead in `instruction_error` of kc-dev-flow-2/scripts/dispatch_records.py with the allowlist, allowing a run of one to three of the listed punctuation characters before whitespace or end; add the stacked cases (backtick then paren, period then paren, period then comma) as allowed subtests; show the old exclusion lookahead failing the new test; rerun the suite and the AC-7 corpus (no passing record may flip); commit with named files only; run /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.23.0/extensions/roborev/roborev_gate.py again; push without force; CI green on the new head; write and commit the stage report

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.23.0

FO fix authorization for #652 (Codex round 2, one P2, Cycle 2): the allowlist as proposed, with stacked punctuation allowed, because records quote a path inside backticks and parentheses in prose and refusing that would fail a record that does carry the instruction. Keep the branch stacked on #649. Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not comment on any PR, request reviews or mark ready.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
