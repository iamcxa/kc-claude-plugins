# implementation-2

Dispatched: ad44f0cbf42274ff65802cabc52ebe919f159fd5 (workflow checkout, kc-dev-flow-2 0.26.0 README); fresh worker on the existing worktree, Cycle 1 repair: FO fix authorization
Model: sonnet

## Checklist

In docs/adr/0027-fo-write-rules-are-checked-by-the-script-fo-runs-at-the-write.md, Consequences, replace "No script reads the approved question, so" with "No script checks that an approved question named the merge, so", and change nothing else
kc-dev-flow-2/scripts/adr_lint.py docs/adr --since ad44f0cbf42274ff65802cabc52ebe919f159fd5 --require 27 exits 0 and kc-dev-flow-2/scripts/lint-skills.py exits 0 on the new head
All package test files pass; push with an explicit remote and branch, no -u; CI green on the new head; commit the stage report

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.26.0

Number guards: ADR: 0027

Profile: pilot. Task fo-write-rules-checked, PR iamcxa/kc-claude-plugins#687, existing worktree `/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-fo-write-rules-checked` on branch spacedock-ensign/fo-write-rules-checked at d0c2e25b. The finding is under `### Feedback Cycles` in the task file. The prior worker is not addressable; run `git status` and `git diff` first. Commit the state report with `spacedock state commit fo-write-rules-checked --workflow-dir /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2`.

Before reporting, commit and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.26.0/extensions/roborev/roborev_gate.py --repo <worktree> --base <base sha>`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report.

Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not comment on any PR, request reviews or mark ready. If a push or gh call is refused by the permission check, stop and report it.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
