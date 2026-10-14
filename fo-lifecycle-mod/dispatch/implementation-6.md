# implementation-6

Dispatched: 656543f41b2f3d11717d418e6b5f6680d97964ff (workflow checkout, kc-dev-flow-2 0.22.1 README); candidate #643 branch
Model: sonnet
Implementation of the redone cycle-3 design after the redo ideation gate.

## Checklist

The approved cycle-3 design built on PR #643's branch with new commits (no rebase, no force): the one mod kc-dev-flow-2/references/sd/mods/kc-dev-flow-2.md (and the two cycle-2 mod files removed), the tasks subcommand and the next: lines in /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/scripts/pr_watch.py, /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/scripts/observer_check.py and /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/scripts/delivery_gate.py as kc-dev-flow-2/scripts/ changes, the counted README, learn extension, dev skill, codex and copilot text changes, the worker principles sentence of D1, the adoption step, ADR 0015 updated to the redone design, WORKFLOW_WORD_BUDGET set to the new count with its reason line; the PR title and body updated to the redone change
AC-8 to AC-17 that implementation owns green with each falsifier shown failing by a mutation run, including AC-12's recount of the words FO reads at each moment from the shipped script output and text, every moment at or under the design's column
roborev evidence= line, CI green on the PR head, kc-dev-flow-2/scripts/lint-skills.py green, and the CI cost per PR measured or stated as not measured

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1

Profile: pilot. Approved design: `## Design` and `## Acceptance criteria` (AC-8 to AC-17) in the task file; the redo ideation gate approved 2026-10-14 accepting D1 to D3. Captain's push grant, quoted from that gate question as D1 requires: "this approval is that grant for this task: the implementation worker may push the task branch and open a Draft PR in iamcxa/kc-claude-plugins" (Captain: 「准」). The Draft PR already exists as #643; push new commits to its branch and keep it Draft. ADR 0015 is reserved under `## Number guards`.

Work in the existing worktree (`git worktree list` in /Users/kent/conductor/workspaces/kc-claude-plugins/colombo shows the branch of #643; fetch and bring it to origin's head first, and merge origin/main if it moved). Stage named files only, no empty commits, no version bumps. The replays (AC-13, AC-14) are validation's: launch none. Do not copy the mod into any adopter workflow. Spacedock and _mods/pr-merge.md are not changed. Stop and return to FO if the change needs a file outside the design's list or a word count above the design's column.

Before reporting, commit and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/extensions/roborev/roborev_gate.py --repo <worktree> --base $(git merge-base HEAD origin/main)`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest. Put the `evidence=` or `incomplete:` line in the stage report.

Never run `git remote set-url` or any `git config` write in a worktree of this repository: worktrees share one config, including the Captain's main checkout. Do not request reviews, comment on any PR, mark ready or merge.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
