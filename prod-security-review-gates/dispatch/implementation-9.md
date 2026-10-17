# implementation-9

Dispatched: 1383c9119eb5328543e2c4df5e562be22b74e355 (workflow checkout, kc-dev-flow-2 0.23.0 README); fresh worker on the existing worktree; FO fix authorization for Cycle 3
Model: sonnet

## Checklist

Fix the folder-form report path in `check_security` (kc-dev-flow-2/scripts/design_surfaces.py): for a task file named `index.md` the task folder is `path.parent`; for a flat task file it stays the sibling `path.parent / path.stem`. Add a failing-first folder-form test (same report bytes pass as `<slug>.md` and as `<slug>/index.md`, Codex round 3 review:5555969981), a mutation that reverts the branch and fails that test with its reason, and check whether any other path in `check_security` or its callers repeats the `path.stem` form for a task folder; rerun all saved reports under prod-security-review-gates/security/ (0 false holds expected); commit with named files only; run /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.23.0/extensions/roborev/roborev_gate.py until clean or twice; push without force; CI green; commit the stage report

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.23.0

Profile: pilot. Task prod-security-review-gates, PR iamcxa/kc-claude-plugins#656, worktree `/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-prod-security-review-gates`, branch spacedock-ensign/prod-security-review-gates-v2 (head a741e357). The finding is under `### Feedback Cycles` (Cycle 3) and in validation-3 F1. Do not change the report parser or its shape rules. The prior worker of this task is not addressable; run `git status` and `git diff` first. Commit the state report with `spacedock state commit prod-security-review-gates --workflow-dir /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2`. Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not comment on any PR, request reviews or mark ready.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
