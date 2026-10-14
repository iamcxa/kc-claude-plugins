# implementation-1

Dispatched: 656543f41b2f3d11717d418e6b5f6680d97964ff (workflow checkout, kc-dev-flow-2 0.22.1 README)
Model: sonnet

## Checklist

One Draft PR (feat(kc-dev-flow-2): ...) from a branch off origin/main with the two mod files under kc-dev-flow-2/references/sd/mods/ (observe-merged.md and watch-and-learn.md, as the approved design gives them), the references/sd/workflow.md edits R1 to R3 and the ### done deletion, WORKFLOW_WORD_BUDGET in kc-dev-flow-2/scripts/lint-skills.py lowered to the new count with its reason line, the adoption.md copy-and-cmp step, the package README row, and the test changes the design names (kc-dev-flow-2/scripts/test_sd_dispatch.py pins re-pointed, the mod order and arm-target assertion of AC-1, kc-dev-flow-2/scripts/test_observer_check.py if it reads the moved text); AC-1 to AC-3 and AC-7 green with each falsifier shown failing by a mutation run
Before writing the merge-hook line: how Spacedock's pr-merge merge hook behaves when the task's pr field is already set (in this workflow the implementation worker opens the PR), read from Spacedock's own source and its pr-merge.md text, with the probe or citation; if it does not match the design's flow, stop and return to FO before changing the mod
roborev evidence= line, CI green on the PR head, kc-dev-flow-2/scripts/lint-skills.py green, and the CI cost per PR measured or stated as not measured

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1

Profile: pilot. Approved design: `## Design` and `## Acceptance criteria` in the task file; ideation gate approved 2026-10-14 accepting D1 (two files), D2 (no drift-check script) and D3 with FO's change (the replay starts with the S2 chat-cue pair, one control and one mod, as a go/no-go). The replays (AC-4 to AC-6) are validation's, not yours: do not launch any headless FO session. The design records no ADR; none is reserved. If your stage principles require one, stop and return to FO for a number.

Delivery: one pull request in iamcxa/kc-claude-plugins from a branch off origin/main (fetch first), in your own worktree. Conventional Commit title `feat(kc-dev-flow-2): ...`. Open as Draft. Do not bump versions; release-please owns them. Stage named files only, no empty commits. PR #642 (followup-dispatch-records-checked) is open and also edits references/sd/workflow.md (one clause in the Stages follow-up sentence) and the budget line in kc-dev-flow-2/scripts/lint-skills.py (5561 to 5581); do not touch that sentence, and state in the PR body that whichever merges second recomputes the budget.

Spacedock is not changed and `_mods/pr-merge.md` stays an unchanged copy. Read Spacedock's mod convention in /Users/kent/.claude/plugins/cache/spacedock/spacedock/0.27.0/skills/first-officer/references/first-officer-shared-core.md and its source, not an adopter's usage.

Before reporting, commit your changes and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/extensions/roborev/roborev_gate.py --repo <worktree> --base <base sha>`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report.

Never run `git remote set-url` or any `git config` write in a worktree of this repository: worktrees share one config, including the Captain's main checkout. Use a throwaway `git clone` for that. Do not request reviews, comment on any PR, mark ready or merge. Do not copy the mod files into any adopter workflow (`docs/dev2/_mods/` here included); that is the post-release sync. Stop and return to FO if the change needs a file outside the design's list.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
