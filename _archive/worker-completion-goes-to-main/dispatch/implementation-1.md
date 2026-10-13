# implementation-1

Dispatched: e2524e93025dd0d5d9217b4d722c2b169d01fda6 (workflow checkout, kc-dev-flow-2 0.21.0 README); code base #632 head 0830a3be (stacked)
Model: sonnet

## Checklist

One Draft PR (fix(kc-dev-flow-2): ...) stacked on #632 (branch off spacedock-ensign/observer-before-merge-guard at 0830a3be) with the sentences the design names in references/sd/workflow.md and skills/dev/SKILL.md, the test_sd_dispatch.py entry, and (D2 accepted) dispatch_records.py and its test failing a record whose scope notes lack the main completion line; AC-1 to AC-4 green with each falsifier shown failing by a mutation run
roborev_gate.py evidence= line, CI green on the PR head, lint-skills.py green (raise WORKFLOW_WORD_BUDGET from #632's 5411 only by the words this task adds, saying why), and the CI cost per PR measured or stated as not measured
The existing dispatch records that the D2 check would fail, listed by task and file in the stage report (the design counted 9 of 23 in 3 tasks), so FO can waive them at their gates

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.21.0

Profile: pilot. Approved design: `## Design` and `## Acceptance criteria` in the task file; ideation gate approved 2026-10-13 accepting D2 (dispatch_records.py fails a record without the main line). D1 (a comment on spacedock-dev/spacedock #608) is not part of this task: do not comment on any issue. The design records no ADR; none is reserved. If your stage principles require one, stop and return to FO for a number.

Stacking: fix order is #631 (workflow checkout check), #632 (observer before the sentinel, stacked on #631), then this task. Branch off `origin/spacedock-ensign/observer-before-merge-guard` at 0830a3be and open your PR with that branch as its base. Neither #631 nor #632 is merged; after each squash-merges, FO retargets and merges main back in (never rebase).

Delivery: one pull request in iamcxa/kc-claude-plugins, in your own worktree. Conventional Commit title `fix(kc-dev-flow-2): ...`. Open as Draft. Do not bump versions; release-please owns them. Stage named files only, no empty commits.

Before reporting, commit your changes and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.21.0/extensions/roborev/roborev_gate.py --repo <worktree> --base 0830a3be`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report.

Never run `git remote set-url` or any `git config` write in a worktree of this repository: worktrees share one config, including the Captain's main checkout. Do that only inside a throwaway `git clone`.

Do not request reviews, comment on any PR or issue, mark ready or merge. Stop and return to FO if the change needs a file outside the design's list.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
