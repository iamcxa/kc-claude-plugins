# implementation-1

Dispatched: e2524e93025dd0d5d9217b4d722c2b169d01fda6 (workflow checkout, kc-dev-flow-2 0.21.0 README); code base origin/main 9e68eb87ec184ffca1b6cd210c576d83b9a01e07
Model: sonnet

## Checklist

One Draft PR (fix(kc-dev-flow-2): ...) from a branch off origin/main changing only copilot_review.py, test_copilot_review.py, extensions/copilot/EXTENSION.md, scripts/pr_watch.py, test_pr_watch.py and ADR 0013; AC-1 to AC-7 green with each falsifier shown failing by a mutation run (AC-6's behaviour half named as a limit)
ADR 0013 records D1 (fail closed on any heading-less, comment-less answer) and D2 (no re-request after a refusal until the Captain says the quota is back), with the Captain's words; adr_lint.py docs/adr --require 0013 passes
roborev_gate.py evidence= line, CI green on the PR head, and the CI cost per PR measured or stated as not measured

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.21.0

Profile: pilot. Approved design: `## Design` and `## Acceptance criteria` in the task file; ideation gate approved 2026-10-13 accepting D1 and D2 as recommended (see the gate resolution in the task frontmatter).

ADR: 0013 (reserved; write docs/adr/0013-<short-title>.md, one ADR covering D1 and D2).

Delivery: one pull request in iamcxa/kc-claude-plugins from a branch off origin/main (currently 9e68eb87), in your own worktree. Conventional Commit title scoped `fix(kc-dev-flow-2): ...`. Open as Draft. Do not bump versions; release-please owns them. Stage named files only, no empty commits.

Before reporting, commit your changes and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.21.0/extensions/roborev/roborev_gate.py --repo <worktree> --base <base sha>`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report.

For EXTENSION.md Limits, an FO measurement from 2026-10-13: `gh api /copilot_internal/user` (an undocumented editor endpoint, no gh subcommand exists; gh 2.92.0) showed account iamcxa with premium_interactions 318 of 1500 remaining and token_based_billing true at about the time both reviews were refused for quota, so that endpoint does not predict a review refusal. Use it only if it belongs in Limits; do not add a quota probe (the design reads the answer, not the quota).

Do not request Copilot or Codex reviews, comment on any PR, mark ready or merge. Stop and return to FO if the change needs a file outside the list in the checklist, or a second ADR.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
