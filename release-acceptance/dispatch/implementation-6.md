# implementation-6

Dispatched: c27e76590c1d2dc910e7fa2d332242a7534df0b0 (workflow checkout, kc-dev-flow-2 0.27.0 README); resumed worker (SendMessage), phase 2 of the Cycle 1 repair: FO fix authorization
Model: sonnet

## Checklist

In kc-journey-map/skills/kc-journey-map/SKILL.md, edit only the frontmatter description: after "prepare a selected release for development," insert "accept a built release by walking it end to end once every story's tasks are done (pending delivery acceptance),"; after the trigger "review the release", insert "accept this release", "release acceptance", "walk the release", "驗收這個 release",; add no test (FO decision: a substring test on metadata proves no routing)
Run scripts/skill-frontmatter-lint.sh on the worktree and confirm the new description stays under 1024 characters
All package test files pass; push with an explicit remote and branch, no -u; CI green on the new head; commit the stage report

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0

Number guards: ADR: 0031

Profile: pilot. Task release-acceptance, PR iamcxa/kc-claude-plugins#709, your existing worktree `/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-release-acceptance` and branch. Commit the state report with `spacedock state commit release-acceptance --workflow-dir /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2`.

Before reporting, commit and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0/extensions/roborev/roborev_gate.py --repo <worktree> --base <base sha>`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report.

Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not comment on any PR, request reviews or mark ready. If a push or gh call is refused by the permission check, stop and report it.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
