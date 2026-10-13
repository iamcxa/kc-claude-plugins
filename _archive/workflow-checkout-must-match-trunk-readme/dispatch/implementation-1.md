# implementation-1

Dispatched: e2524e93025dd0d5d9217b4d722c2b169d01fda6 (workflow checkout, kc-dev-flow-2 0.21.0 README); code base origin/main 9e68eb87ec184ffca1b6cd210c576d83b9a01e07
Model: sonnet

## Checklist

One Draft PR (fix(kc-dev-flow-2): ...) from a branch off origin/main adding scripts/workflow_checkout.py and its test, the sentences in skills/dev/SKILL.md and references/sd/workflow.md, the tests-workflow step, and ADR 0014; AC-1 to AC-6 green with each falsifier shown failing by a mutation run
ADR 0014 records the accepted D1 (fetch inside the check; unreachable remote holds), D2 (strict equality) and D3 (FO shows the remedy and waits) with the Captain's words; adr_lint.py docs/adr --require 0014 passes
roborev_gate.py evidence= line, CI green on the PR head, lint-skills.py green (raise WORKFLOW_WORD_BUDGET only by the words this task adds, saying why), and the CI cost per PR measured or stated as not measured

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.21.0

Profile: pilot. Approved design: `## Design` and `## Acceptance criteria` in the task file; ideation gate approved 2026-10-13 accepting D1, D2 and D3 as recommended (see the gate resolution in the task frontmatter).

ADR: 0014 (reserved; write docs/adr/0014-<short-title>.md, one ADR for D1-D3).

Fix order ruled by the Captain: this task first, then observer-before-merge-guard, then worker-completion-goes-to-main. Those two are approved but not yet dispatched; they will build on this PR's wording in references/sd/workflow.md, skills/dev/SKILL.md and lint-skills.py, so keep your edits to the places the design names.

Delivery: one pull request in iamcxa/kc-claude-plugins from a branch off origin/main (fetch first), in your own worktree. Conventional Commit title `fix(kc-dev-flow-2): ...`. Open as Draft. Do not bump versions; release-please owns them. Stage named files only, no empty commits.

Before reporting, commit your changes and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.21.0/extensions/roborev/roborev_gate.py --repo <worktree> --base <base sha>`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report.

Do not request reviews, comment on any PR, mark ready or merge. Stop and return to FO if the change needs a file outside the design's list, or a second ADR.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
