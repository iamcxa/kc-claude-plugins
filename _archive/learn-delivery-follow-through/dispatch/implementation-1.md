# implementation-1

Dispatched: e2524e93025dd0d5d9217b4d722c2b169d01fda6 (workflow checkout, kc-dev-flow-2 0.21.0 README); code base origin/main 70b88d75
Model: sonnet

## Checklist

One Draft PR (fix(kc-dev-flow-2): ...) from a branch off origin/main changing only skills/learn/SKILL.md, skills/dev/SKILL.md, extensions/learn/EXTENSION.md and scripts/test_learning.py; AC-1 to AC-6 green with each falsifier shown failing by a mutation run, AC-2's control arm shown stalling on today's text; AC-7 named as live-only
roborev_gate.py evidence= line, CI green on the PR head, lint-skills.py green, and the CI cost per PR measured or stated as not measured

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.21.0

Profile: pilot. Approved design: `## Design` and `## Acceptance criteria` in the task file; ideation gate approved 2026-10-13 accepting D1, D2 and D3 as recommended (see the gate resolution in the task frontmatter). The design records no ADR; none is reserved. If your stage principles require one, stop and return to FO for a number.

Delivery: one pull request in iamcxa/kc-claude-plugins from a branch off origin/main (fetch first), in your own worktree. Conventional Commit title `fix(kc-dev-flow-2): ...`. Open as Draft. Do not bump versions; release-please owns them. Stage named files only, no empty commits. Task fo-record-checks is being designed in parallel and may later edit the same `Cannot run` bullet of extensions/learn/EXTENSION.md; keep your edit there small.

Before reporting, commit your changes and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.21.0/extensions/roborev/roborev_gate.py --repo <worktree> --base <base sha>`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report.

Never run `git remote set-url` or any `git config` write in a worktree of this repository: worktrees share one config, including the Captain's main checkout. Use a throwaway `git clone` for that. Do not request reviews, comment on any PR, mark ready or merge. Stop and return to FO if the change needs a file outside the four named.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
