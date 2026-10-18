# implementation-9

Dispatched: 9b58cd68be01ed360d664642bb3605838cd82c25 (workflow checkout, kc-dev-flow-2 0.24.0 README); resumed worker (SendMessage), FO ruling on the roborev High at e6eb277f (roborev:830)
Model: sonnet

## Checklist

Fix the roborev High: build the design-review Preview: candidates in check_task of kc-dev-flow-2/scripts/design_surfaces.py from unfenced text, as the FO alignment read now is; leave check_ui's existing Preview read unchanged; a failing-first test (a fenced 'Preview: fake.html' beside the real Preview line cannot bind a report) and a mutation that reverts it
Run the roborev gate again until clean or twice; rerun /tmp/ce663/cmpf.sh-style comparison over the four corpora and state the counts; all package test files pass; push with an explicit remote and branch, no -u; CI green on the new head; commit the stage report

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.24.0

Number guards: ADR: 0022

Profile: pilot. Task ui-design-review-in-ideation, PR iamcxa/kc-claude-plugins#663, your existing worktree and branch. A roborev High counts as P1 in this workflow, so it blocks; Cycle 3 had declined the same issue as a non-P1 Codex P2, and FO now takes it into this cycle because the fix is one read. FO updates backlog task ui-design-review-round3-followups. Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not comment on any PR, request reviews or mark ready.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
