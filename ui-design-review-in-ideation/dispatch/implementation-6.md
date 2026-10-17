# implementation-6

Dispatched: 9b58cd68be01ed360d664642bb3605838cd82c25 (workflow checkout, kc-dev-flow-2 0.24.0 README); resumed worker (SendMessage), phase 2 of the Cycle 2 repair: FO fix authorization
Model: sonnet

## Checklist

Apply /tmp/uidr-p1-0AR9S8/phase1.patch to kc-dev-flow-2/scripts/design_surfaces.py and kc-dev-flow-2/scripts/test_design_surfaces.py: exactly one Design review: line (Codex P2, review:5558204896), exactly one Security review: line, no repeated Security finding N: number, and exactly one Surfaces: line in FO alignment, each with its refusal test and per-call-site mutation
Run kc-dev-flow-2/scripts/lint-skills.py, every package test file, kc-dev-flow-2/scripts/comment_ratio.py and kc-dev-flow-2/scripts/number_guards.py check; the validation acceptance script still matches; roborev evidence= line; push without force; CI green on the new head; commit the stage report

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.24.0

Number guards: ADR: 0022

Profile: pilot. Task ui-design-review-in-ideation, PR iamcxa/kc-claude-plugins#663, your existing worktree and branch. FO authorizes the Surfaces: rule too (it closes a bypass where a second Surfaces line hides ui; it applies in seed mode to every task, so state that in the stage report). No ADR or brief text change. Commit the state report with `spacedock state commit ui-design-review-in-ideation --workflow-dir /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2`. Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not comment on any PR, request reviews or mark ready.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
