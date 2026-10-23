# implementation-2

Dispatched: c27e76590c1d2dc910e7fa2d332242a7534df0b0 (workflow checkout, kc-dev-flow-2 0.27.0 README); resumed worker (SendMessage), phase 2 of the Cycle 0 repair: FO fix authorization
Model: sonnet

## Checklist

Move AC-7 and AC-3 under `Superseded text:` in Captain Amendment 2 and write their replacements marked (Amended by Captain, amendment 2; replaces AC-7) and (Amended by Captain, amendment 2; replaces AC-3), carrying exactly what Amendment 2 states and nothing more, per ADR 0005; change no code
Update the PR #708 body's acceptance and known-limit lines to match the amended criteria, and commit the stage report
All package test files pass; push with an explicit remote and branch, no -u; CI green on the new head; commit the stage report

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.27.0

Number guards: ADR: 0030

Profile: pilot. Task design-director-runs-ui-design-review, PR iamcxa/kc-claude-plugins#708, your existing worktree `/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-design-director-runs-ui-design-review` and branch. Commit the state report with `spacedock state commit design-director-runs-ui-design-review --workflow-dir /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2`.

Before reporting, commit and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.27.0/extensions/roborev/roborev_gate.py --repo <worktree> --base <base sha>`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report.

Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not comment on any PR, request reviews or mark ready. If a push or gh call is refused by the permission check, stop and report it.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
