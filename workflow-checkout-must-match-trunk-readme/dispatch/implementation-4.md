# implementation-4

Dispatched: e2524e93025dd0d5d9217b4d722c2b169d01fda6 (workflow checkout, kc-dev-flow-2 0.21.0 README); candidate #631 70da29c7
Model: sonnet
Fresh worker (prior implementation and validation workers sent shutdown_request). FO fix lane for the Codex round-2 P1; phase 1 investigation only.

## Checklist

Investigation first, with no candidate change: reproduce the Codex round-2 P1 on #631 head 70da29c7 (the dev skill's instruction runs workflow_checkout.py directly while the file is mode 100644, so the shell exits 126), check every other place in the PR that names a script FO is told to run for the same defect, send FO the result and your proposed fix, then wait for FO's fix authorization message
After FO's fix authorization only: fix it with a check that fails without the fix (shown failing by a mutation run); push to #631's branch; CI green on the new head
Stage report: new head, the roborev_gate.py evidence= line, test and mutation results, and anything left for FO

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.21.0

Profile: pilot. Repair under the workflow's Review-finding disposition step 3; the task stays in validation and you work as the implementation stage in the existing worktree. Approved design, D1-D3 and ADR 0014 unchanged.

Worktree and PR: /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-workflow-checkout-must-match-trunk-readme, branch spacedock-ensign/workflow-checkout-must-match-trunk-readme, PR iamcxa/kc-claude-plugins#631, head 70da29c7, base main. Do not create a new worktree. PRs #632 and #633 are stacked on this branch; do not touch them, FO merges your new head into them afterwards.

The finding (Codex round 2, review:5500564188, under the task's `### Feedback Cycles`, Cycle 2): P1 `skills/dev/SKILL.md` around line 65: the instruction runs `workflow_checkout.py` directly, but the file is mode 100644, so the shell exits 126 "Permission denied". Invoke it through `python3` as `references/sd/workflow.md` does, or make it executable. Close the class within this PR: every instruction the PR adds that names a script to run.

Phase 1 (now): read-only investigation; do not edit, commit or push the worktree. Never run `git remote set-url` or any `git config` write in a worktree of this repository (shared config, including the Captain's main checkout); use a throwaway `git clone` for that. Send FO one message (to `main`) with the reproduction and proposed fix, then wait. FO's reply naming the fix is the only authorization to change the candidate.

Phase 2 (after FO's message): commit `fix(kc-dev-flow-2): ...`, stage named files only. Before pushing, commit and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.21.0/extensions/roborev/roborev_gate.py --repo <worktree> --base 70da29c7`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest. Put the `evidence=` or `incomplete:` line in the stage report. Push (never force), wait for CI (`gh pr checks 631 --repo iamcxa/kc-claude-plugins`).

Do not comment on the PR, request reviews, mark ready or merge. A file the PR does not already change is a scope change: stop and return it to FO.

Send your phase-1 report and your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
