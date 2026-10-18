# implementation-5

Dispatched: 9b58cd68be01ed360d664642bb3605838cd82c25 (workflow checkout, kc-dev-flow-2 0.24.0 README); resumed worker (SendMessage), phase 2 of the Cycle 2 repair: FO fix authorization
Model: sonnet

## Checklist

Apply /tmp/rt-fix-scratch/fix.patch to kc-dev-flow-2/scripts/role_triggers.py and keep HeadingFormsTest in kc-dev-flow-2/scripts/test_role_triggers.py: all four headings (Captain amendments, Amendment N, Feedback Cycles, FO alignment) and section ends accept case, leading indent and no-break space
Copy the SPACE class and add a test that pins it equal to the GO_SPACE constant in kc-dev-flow-2/scripts/design_surfaces.py (no import at run time); each matcher's mutation fails only its own test (python3 -B, caches cleared); output over the state task files unchanged, with the count stated
kc-dev-flow-2/scripts/lint-skills.py exits 0 at 5447 of 5447; all package test files pass; roborev evidence= line; push without force; CI green on the new head; commit the stage report

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.24.0

Profile: pilot. Task special-role-triggers, PR iamcxa/kc-claude-plugins#664, your existing worktree and branch. FO rulings: (1) normalize all four headings, including the two kc-dev-flow-2/scripts/design_surfaces.py reads strictly, since a stricter task already fails that check; (2) copy SPACE and pin it by test rather than import it, so the script keeps running under python3 -I and a failed import cannot read as calls owed. Commit the state report with `spacedock state commit special-role-triggers --workflow-dir /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2`. Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not comment on any PR, request reviews or mark ready.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
