# implementation-8

Dispatched: 9b58cd68be01ed360d664642bb3605838cd82c25 (workflow checkout, kc-dev-flow-2 0.24.0 README); resumed worker (SendMessage), phase 2 of the Cycle 3 repair: FO fix authorization
Model: sonnet

## Checklist

Apply the chief-engineer's two-line change in check_task of kc-dev-flow-2/scripts/design_surfaces.py (FO alignment split from unfenced text, body kept raw) and keep FencedFoAlignmentTests in kc-dev-flow-2/scripts/test_design_surfaces.py; the Surfaces exactly-one rule stays as ruled
All package test files pass; kc-dev-flow-2/scripts/lint-skills.py exits 0; roborev evidence= line; push with an explicit remote and branch, no force, no -u; CI green on the new head; commit the stage report with the four-corpus comparison you ran

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.24.0

Number guards: ADR: 0022

Profile: pilot. Task ui-design-review-in-ideation, PR iamcxa/kc-claude-plugins#663, your existing worktree and branch. FO ruling on the relay cases: both were already in the chief-engineer's measured report; relay's _archive/multi-document-room-picker.md has two real unfenced Surfaces: ui lines, a correct hit on an archived task that nothing in the package re-checks, and review-ui-room-asks-through-shell.md is the new design-review rule working as intended (the relay FO is told at sync). The rule is not loosened. Commit the state report with `spacedock state commit ui-design-review-in-ideation --workflow-dir /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2`. Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not comment on any PR, request reviews or mark ready.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
