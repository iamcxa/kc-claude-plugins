# implementation-3

Dispatched: 9b58cd68be01ed360d664642bb3605838cd82c25 (workflow checkout, kc-dev-flow-2 0.24.0 README); resumed worker (SendMessage), phase 2 of the Cycle 1 repair: FO fix authorization
Model: sonnet

## Checklist

Apply the phase-1 fix in kc-dev-flow-2/scripts/role_triggers.py: a call dated no earlier than the amendment entry clears it (AC-10, Captain amendment 1), and only lines under ## FO alignment (with its ### subheadings) can clear an event or carry a waiver; drop the superseded 10-17 case from the old test in kc-dev-flow-2/scripts/test_role_triggers.py and keep the two new tests
Each rule's test fails under its own mutation (python3 -B, caches cleared); the output over the state task files is unchanged except where the new rules apply, with the count stated; kc-dev-flow-2/scripts/lint-skills.py exits 0 at 5447 of 5447; all package test files pass; roborev evidence= line; push without force; CI green on the new head; commit the stage report

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.24.0

Profile: pilot. Task special-role-triggers, PR iamcxa/kc-claude-plugins#664, your existing worktree and branch. FO's ruling on finding 2: the approved design states that the Reviewer: line stays under ## FO alignment (Design, and the README's Stages sentence), so restricting clearing to that section implements the approved design and needs no new criterion. Commit the state report with `spacedock state commit special-role-triggers --workflow-dir /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2`. Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not comment on any PR, request reviews or mark ready.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
