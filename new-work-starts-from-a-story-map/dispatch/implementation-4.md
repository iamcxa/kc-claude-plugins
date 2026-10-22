# implementation-4

Dispatched: c27e76590c1d2dc910e7fa2d332242a7534df0b0 (workflow checkout, kc-dev-flow-2 0.27.0 README); resumed worker (SendMessage), phase 2 of the Cycle 2 repair: FO fix authorization
Model: sonnet

## Checklist

On feat/story-map-kc-journey-map (#704) in kc-journey-map/lib/journey-review.mjs: refuse a source.date that is not an ISO YYYY-MM-DD date and a source.words that is not a non-empty string; read a Tasks table whose separator row is missing without skipping its first data row (or refuse the table with a reason); refuse an ADR owed entry whose question already holds doc: instead of answer:; one failing-then-passing test per fix in kc-journey-map/lib/journey-review.test.mjs
Run the full kc-journey-map lib/*.test.mjs suite and show each new test failing on the matching mutant; leave #705 unchanged
All package test files pass; push with an explicit remote and branch, no -u; CI green on the new head; commit the stage report

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.27.0

Number guards: ADR: 0029

Profile: pilot. Task new-work-starts-from-a-story-map, PR iamcxa/kc-claude-plugins#704, your existing worktree `/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-new-work-starts-from-a-story-map` and branch. Commit the state report with `spacedock state commit new-work-starts-from-a-story-map --workflow-dir /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2`.

Before reporting, commit and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.27.0/extensions/roborev/roborev_gate.py --repo <worktree> --base <base sha>`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report.

Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not comment on any PR, request reviews or mark ready. If a push or gh call is refused by the permission check, stop and report it.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
