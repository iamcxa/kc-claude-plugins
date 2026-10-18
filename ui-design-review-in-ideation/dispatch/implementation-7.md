# implementation-7

Dispatched: 9b58cd68be01ed360d664642bb3605838cd82c25 (workflow checkout, kc-dev-flow-2 0.24.0 README); fresh worker on the existing worktree, phase 1 of the Cycle 3 repair
Model: sonnet

## Checklist

Phase 1 only, no commit or push: reproduce the Cycle 3 regression at #663 head 3656cd74 as a failing test (a task whose real FO alignment quotes a fenced '## FO alignment' / 'Surfaces: none' fixture is refused in check and check --seed), confirm the chief-engineer's two-line change in check_task (FO alignment split from unfenced text, body kept raw for check_db) makes it pass and that reverting it fails it, and run /tmp/ce663/cmpf.sh over the four corpora named in the Cycle 3 entry; report and stop until FO authorizes the fix
## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.24.0

Number guards: ADR: 0022

Profile: pilot. Task ui-design-review-in-ideation, PR iamcxa/kc-claude-plugins#663, worktree `/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-ui-design-review-in-ideation` (head 3656cd74). The ruling is under `### Feedback Cycles` (Cycle 3): fix only the Surfaces read; the Codex round-3 Preview P2 is declined to backlog and is not yours. The chief-engineer's prototype is /tmp/ce663/fence/design_surfaces.py and its corpus scripts are /tmp/ce663/cmp.sh and /tmp/ce663/cmpf.sh. The prior worker of this task is not addressable; run `git status` and `git diff` first. Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not comment on any PR.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).