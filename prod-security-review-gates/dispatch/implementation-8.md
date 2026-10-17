# implementation-8

Dispatched: 1383c9119eb5328543e2c4df5e562be22b74e355 (workflow checkout, kc-dev-flow-2 0.23.0 README); fresh worker on the existing worktree; FO fix authorization for Cycle 2 after the chief-engineer ruling
Model: sonnet

## Checklist

Lock `report_severities` and the existence test in `check_security` (kc-dev-flow-2/scripts/design_surfaces.py) to the reviewer's documented report shape with three refuse-on-mismatch rules: exactly one `tob_security_review:` line at column 0; exactly one `findings:` line in the whole file, a direct child of the root key; the item parser's severity count equals a plain count of `severity:` lines; each rule a named error, one failing-first test per rule including Codex round 2's nested case (review:5555839646), one mutation per rule; rerun all saved reports under prod-security-review-gates/security/ (0 false holds expected); commit with named files only; run /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.23.0/extensions/roborev/roborev_gate.py until clean or twice; push without force; CI green; commit the stage report

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.23.0

Profile: pilot. Task prod-security-review-gates, PR iamcxa/kc-claude-plugins#656, worktree `/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-prod-security-review-gates`, branch spacedock-ensign/prod-security-review-gates-v2 (head 1e4cd1e8). The ruling and its reasons are under `### Feedback Cycles` (Cycle 2). Do not teach the parser any new shape; refuse instead. The prior worker of this task is not addressable; run `git status` and `git diff` first. Commit the state report with `spacedock state commit prod-security-review-gates --workflow-dir /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2`. Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not comment on any PR, request reviews or mark ready.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
