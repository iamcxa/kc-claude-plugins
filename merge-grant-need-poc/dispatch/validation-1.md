# validation-1

Dispatched: c60e89e11ab37441a0dca1c2a0672da4ad223c3c (POC workflow checkout, kc-dev-flow-2 0.25.0 README)
Candidate: none (POC result on the state branch; no code candidate)
Model: sonnet

## Checklist

Confirm from state history that the pre-registration and the Captain's bar ruling were committed before the measurement ran, and that the bar text is unchanged
Re-derive M1 independently on a sample: for each repository, list the merged PRs in the window with read-only gh, re-class at least 15 PRs per repository with kc-dev-flow-2/scripts/delivery_gate.py classify at origin/main, and compare with the committed table; confirm the largest docs-only or script-with-test count
Re-check M2's recognizer on the 10 hand-checked PRs and on 5 more of your choosing; state whether the 'unrecognizable' rate and the hand-check disagreement hold
Verdict against the Captain's bar as registered (PASSED meaning the code returns, or REJECTED meaning retire, or inconclusive), and what the POC does not show
## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.25.0

Profile: poc. Task merge-grant-need-poc; the pre-registration, the Captain's bar ruling and the phase-2 results are in the task file. Read only; run no model; change no package or adopter file; open no PR. Commit your stage report with `spacedock state commit merge-grant-need-poc --workflow-dir /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-poc-route/docs/dev2-poc`. Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not comment on any PR or issue.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).