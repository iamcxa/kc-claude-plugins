# implementation-4

Dispatched: 9b58cd68be01ed360d664642bb3605838cd82c25 (workflow checkout, kc-dev-flow-2 0.24.0 README); resumed worker (SendMessage), phase 2 of the Cycle 1 repair: FO fix authorization
Model: sonnet

## Checklist

Apply /tmp/p2fix-ensign-QJtK8i/proposed-fix.diff to kc-dev-flow-2/scripts/design_surfaces.py and kc-dev-flow-2/scripts/test_design_surfaces.py: duplicate 'Design finding N:' lines refused (Codex P2 2), exactly one 'preview:' directly under 'design_review:' (P2 3), and a report naming any of the task's Preview: lines accepted (validation-1 Deferred risk 2)
Codex P2 1 (findings: [] beside a limitation naming an unshown state) by option A: keep the check, keep the test that pins today's pass, and add one sentence to the Consequences of docs/adr/0022-ui-ideation-design-review-binds-design.md that the check does not read limitations and the worker's step 3 turns such a limitation into a finding; design-review.md stays within 850 words
Each new rule's test fails under its mutation (python3 -B, caches cleared); the validation acceptance script still matches; kc-dev-flow-2/scripts/lint-skills.py exits 0; roborev evidence= line; push without force; CI green on the new head; commit the stage report

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.24.0

Number guards: ADR: 0022

Profile: pilot. Task ui-design-review-in-ideation, PR iamcxa/kc-claude-plugins#663, your existing worktree and branch. FO's ruling on P2 1: option A stays inside the approved design, whose Limits section already says the check counts findings only, the same limit the Captain approved for the prod security review; FO declines the remaining bypass as a Deferred risk in the gate summary. Commit the state report with `spacedock state commit ui-design-review-in-ideation --workflow-dir /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2`. Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not comment on any PR, request reviews or mark ready.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
