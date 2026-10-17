# implementation-3

Dispatched: 1383c9119eb5328543e2c4df5e562be22b74e355 (workflow checkout, kc-dev-flow-2 0.23.0 README); under Captain amendment 1
Model: sonnet

## Checklist

Captain amendment 1 applied: AC-3 moved under it as `Superseded text:`, its replacement written as a new criterion that says 'Amended by Captain, amendment 1' (the ideation-gate review names prompt injection; the validation-gate review names unbounded comment or session writes), and kc-dev-flow-2/scripts/design_surfaces.py check exits 0
Before any push: one replay of the validation-gate review with the r2 brief on relay PR spacedock-dev/subspace-relay#347's diff (read only), recording whether it names unbounded writes, its tokens and duration; if it does not, stop and report without pushing
Then one Draft PR (feat(kc-dev-flow-2): ...) from the local branch spacedock-ensign/prod-security-review-gates (r2 brief, db8e04bc) rebased or merged onto origin/main as needed without force on any shared branch, every other acceptance criterion still green, the candidate's own kc-dev-flow-2/scripts/lint-skills.py exit 0, roborev evidence= line, CI green, CI cost measured or stated as not measured

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.23.0

Profile: pilot. Captain amendment 1 is in the task file. Worktree `/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-prod-security-review-gates`; the prior worker is not addressable, run `git status` and `git log` first. ADR: 0018 (reserved). Push and Draft PR under the Captain's 「准」 (chat, 2026-10-16) to a gate question that says approval "is the grant for the implementation worker to push a branch and open a Draft PR". Read relay only through read-only commands; do not edit any relay file. Before reporting, run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.23.0/extensions/roborev/roborev_gate.py --repo <worktree> --base <base sha>` and put its evidence= line in the report.

Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not comment on any PR, request reviews or mark ready.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
