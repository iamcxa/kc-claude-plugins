# implementation-12

Dispatched: 9b58cd68be01ed360d664642bb3605838cd82c25 (workflow checkout, kc-dev-flow-2 0.24.0 README); fresh worker on the existing worktree, applying Captain amendment 1
Model: sonnet

## Checklist

Apply Captain amendment 1 (## Captain amendments): move each superseded criterion (AC-3, AC-4, AC-5, AC-7, AC-8, AC-11, AC-12) verbatim under the entry's 'Superseded text:' and write replacements with fresh ids that say 'Amended by Captain, amendment 1' and keep only what the narrowed PR delivers (the class and never list as stored in each record and points, the replay of holds and points, the injection guard on check's output); FO adds no words of its own there
Narrow PR #666 to the holds, points, class, never list and per-ask record: remove from kc-dev-flow-2/scripts/delivery_gate.py and its tests the grant, merge-line, recheck, calibrate, label and fetch code, remove ADR 0023 and ADR 0011's added Status line, and remove the workflow.md words that name a grant or a merge line, recomputing the budget step in kc-dev-flow-2/scripts/lint-skills.py; the removed code stays reachable at 3fd84178 (named in POC task merge-grant-need-poc), so delete rather than comment out
All remaining tests pass and each kept rule still fails under its mutation (python3 -B, caches cleared); kc-dev-flow-2/scripts/lint-skills.py exits 0; all package test files pass; roborev evidence= line; push with an explicit remote and branch, no -u; CI green on the new head; update the PR title and body to the narrowed scope in a file and name it in the stage report; commit the stage report
## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.24.0

Profile: prod. Task merge-gatekeeper, PR iamcxa/kc-claude-plugins#666, worktree `/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-merge-gatekeeper` (head 3fd84178). The Captain approved narrowing on 2026-10-18 (amendment 1); the chief-engineer's measured split of which code, tests and words belong to each part is in its report, recorded in the task under the Cycle 2 Reviewer line and FO's summary. Keep classify, NEVER_PATH and the never list: they feed the point and the record. ADR 0023 stays reserved for the POC; this PR lands no ADR. Do not run gh pr edit; FO updates the PR title and body. The prior worker of this task is not addressable; run `git status` and `git diff` first. Commit the state report with `spacedock state commit merge-gatekeeper --workflow-dir /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2`. Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not comment on any PR, request reviews or mark ready.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).