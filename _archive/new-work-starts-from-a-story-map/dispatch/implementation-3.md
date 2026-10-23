# implementation-3

Dispatched: c27e76590c1d2dc910e7fa2d332242a7534df0b0 (workflow checkout, kc-dev-flow-2 0.27.0 README); resumed worker (SendMessage), phase 2 of the Cycle 1 repair: FO fix authorization
Model: sonnet

## Checklist

Move AC-2 under `Superseded text:` in Captain Amendment 2 and write its replacement criterion marked (Amended by Captain, amendment 2; replaces AC-2), carrying the date rule Amendment 2 states, per ADR 0005
On feat/story-map-kc-journey-map (#704): apply the phase-1 fix in kc-journey-map/lib/journey-review.mjs with its tests: the Amendment 2 date rule for moved stories; require the Reviewed line and the Map edit, Walk, Holes, Slice and Tasks headings in order; refuse a source.kind outside gate, amendment or release; require at least one lens arm; update the one existing test whose message changed
On feat/story-map-kc-dev-flow-2 (#705): in kc-dev-flow-2/skills/dev/SKILL.md replace "Record his answer on each resulting task as its `Release review:` line" with "Record the result on each task as the workflow's `Release review:` line" (AC-7 stays 56 words); in ADR 0029 replace "the order is kept by `journey-review.mjs check`" with "`journey-review.mjs check` refuses a record with no `Interrogation:` line or with a question still open", and delete the parenthetical "(the task's release-preparation intake, 2026-10-21)"
State in the stage report that #705's two Codex P1s (comment:4345825352, comment:4345825366) read kc-journey-map on main and are resolved by #704, with the file lines; the full kc-journey-map lib/*.test.mjs suite, kc-dev-flow-2/scripts/test_pr_watch.py and kc-dev-flow-2/scripts/lint-skills.py (repository copy) pass
All package test files pass; push with an explicit remote and branch, no -u; CI green on the new head; commit the stage report

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.27.0

Number guards: ADR: 0029

Profile: pilot. Task new-work-starts-from-a-story-map, PR iamcxa/kc-claude-plugins#704, your existing worktree `/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-new-work-starts-from-a-story-map` and branch. Commit the state report with `spacedock state commit new-work-starts-from-a-story-map --workflow-dir /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2`.

Before reporting, commit and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.27.0/extensions/roborev/roborev_gate.py --repo <worktree> --base <base sha>`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report.

Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not comment on any PR, request reviews or mark ready. If a push or gh call is refused by the permission check, stop and report it.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
