# implementation-1

Dispatched: 656543f41b2f3d11717d418e6b5f6680d97964ff (workflow checkout, kc-dev-flow-2 0.22.1 README)
Model: sonnet

## Checklist

One Draft PR (fix(kc-dev-flow-2): ...) from a branch off origin/main with the two new rules in kc-dev-flow-2/scripts/dispatch_records.py (an absolute Package root: line inside ## Scope notes; a checklist in which not every line names a sibling record), their tests in test_dispatch_records.py, the one references/sd/workflow.md clause from D1 and the lint-skills.py WORKFLOW_WORD_BUDGET raise by the words it adds (reason stated); AC-1 to AC-7 green with each falsifier shown failing by a mutation run, and the replays against the archived records reproducing the design's results (the three named records fail, the nine others in that folder pass, the counts in AC-5 re-measured at the state HEAD you read)
roborev_gate.py evidence= line, CI green on the PR head, lint-skills.py green, and the CI cost per PR measured or stated as not measured

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1

Profile: pilot. Approved design: `## Design` and `## Acceptance criteria` in the task file; ideation gate approved 2026-10-14 accepting D1 and D2 as recommended (see the gate resolution in the task frontmatter). The design records no ADR; none is reserved. If your stage principles require one, stop and return to FO for a number.

Delivery: one pull request in iamcxa/kc-claude-plugins from a branch off origin/main (fetch first; main carries 0.22.1, and workflow.md's budget is 5561), in your own worktree. Conventional Commit title `fix(kc-dev-flow-2): ...`. Open as Draft. Do not bump versions; release-please owns them. Stage named files only, no empty commits.

Archived records for the replays (read only): /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/_archive/ and the active task folders beside it.

Before reporting, commit your changes and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/extensions/roborev/roborev_gate.py --repo <worktree> --base <base sha>`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report.

Never run `git remote set-url` or any `git config` write in a worktree of this repository: worktrees share one config, including the Captain's main checkout. Use a throwaway `git clone` for that. Do not request reviews, comment on any PR, mark ready or merge. Stop and return to FO if the change needs a file outside the design's list.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
