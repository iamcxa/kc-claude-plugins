# implementation-14

Dispatched: 9b58cd68be01ed360d664642bb3605838cd82c25 (workflow checkout, kc-dev-flow-2 0.24.0 README); resumed worker (SendMessage), phase 2 of the Cycle 4 repair: FO fix authorization
Model: sonnet

## Checklist

Apply /tmp/fixproto/fix.patch to kc-dev-flow-2/scripts/delivery_gate.py and its tests: the latest workflow run per workflow on the PR head must be completed and successful, a page overflow exits 2; keep PartialRollupTests
Restore 'and waits for those jobs to finish before asking for merge' in kc-dev-flow-2/references/sd/workflow.md exactly as on origin/main, with the budget step in kc-dev-flow-2/scripts/lint-skills.py recomputed; write recount-3 of the merge-ask moment with an independent script under the task's validation folder
Each new rule's mutation fails its test (python3 -B, caches cleared); kc-dev-flow-2/scripts/test_sd_dispatch.py with --sd-plugin-root passes; all package test files pass; roborev evidence= line; push with an explicit remote and branch, no -u; CI green on the new head; write and commit the stage report

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.24.0

Number guards: ADR: 0023 (not landed by this PR; see the task's Number guards note)

Profile: prod. Task merge-gatekeeper, PR iamcxa/kc-claude-plugins#666, your existing worktree and branch. FO ruling: the workflow-runs hold replaces the base-head check-names idea, which you measured does not work here; the restored README clause is the backstop for a run not yet created. Commit the state report with `spacedock state commit merge-gatekeeper --workflow-dir /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2`. Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not comment on any PR, request reviews or mark ready.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
