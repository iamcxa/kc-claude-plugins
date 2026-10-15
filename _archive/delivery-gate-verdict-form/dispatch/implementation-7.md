# implementation-7

Dispatched: 656543f41b2f3d11717d418e6b5f6680d97964ff (workflow checkout, kc-dev-flow-2 0.22.1 README); candidate #647 0a26ca37; worker spacedock-ensign-delivery-gate-verdict-form-implementation-c7, a fresh worker on the existing worktree
Model: sonnet

## Checklist

First commit on the #647 branch restores kc-dev-flow-2/scripts/delivery_gate.py, kc-dev-flow-2/scripts/test_delivery_gate.py, kc-dev-flow-2/skills/validation/principles.md and kc-dev-flow-2/scripts/test_sd_dispatch.py to origin/main c545b896; then the amendment 2 design on top: kc-dev-flow-2/scripts/delivery_gate.py reads the `Candidate:` lines of the highest-numbered validation dispatch record, kc-dev-flow-2/references/sd/workflow.md names the line, test pins follow the new wording
AC-9 to AC-14 green, each falsifier shown failing by a mutation you run (python3 -B, caches cleared), with the observer-before-merge-guard replay re-run on a scratch copy
/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/scripts/lint-skills.py exit 0 with WORKFLOW_WORD_BUDGET unchanged, paid by the design's 26-word sentence removal; that sentence listed in the PR body under `without-it unanswered`
PR body rewritten for the new design (Changes, Evidence, Known limits, without-it unanswered); roborev evidence= line; push without force; CI green on the PR head; CI cost measured or stated as not measured

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1

Profile: pilot. Approved design: `## Design` and `## Acceptance criteria` (AC-9 to AC-14) in the task file; ideation gate approved 2026-10-15 under Captain amendment 2. The gate question stated, and the Captain's 「准」 accepted: D1 as recommended (a bare `Candidate: <40-hex head>` line, one per head validated); continuing on the #647 branch with a first commit that restores the four verdict-parsing files to origin/main; and "is the grant for the implementation worker to push to the #647 branch". AC-1 to AC-8 are superseded; do not work to them.

Worktree: /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-delivery-gate-verdict-form (branch spacedock-ensign/delivery-gate-verdict-form, head 0a26ca37, clean, merge base origin/main c545b896). Earlier implementation workers of this task are not addressable; this is a fresh dispatch on their worktree. PR #647 stays Draft. Conventional Commit subjects `fix(kc-dev-flow-2): ...`. Stage named files only, no empty commits, no force push, no version edits.

Before reporting, commit and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/extensions/roborev/roborev_gate.py --repo /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-delivery-gate-verdict-form --base c545b8960b291176f668628dc0886b384db78b86`. On exit 1 fix findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report. Run each test suite and mutation with a time cap.

Never run `git remote set-url` or any `git config` write in a worktree of this repository: worktrees share one config, including the Captain's main checkout. Do not request reviews, comment on any PR, mark ready or merge. Stop and return to FO if the change needs a file outside the design's list.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
