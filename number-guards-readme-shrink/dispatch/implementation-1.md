# implementation-1

Dispatched: c60e89e11ab37441a0dca1c2a0672da4ad223c3c (workflow checkout, kc-dev-flow-2 0.25.0 README); batch 3
Model: sonnet

## Checklist

One Draft PR (feat(kc-dev-flow-2): ...) from a branch off origin/main implementing D1 as recommended: the 55-word cut of the Number guards passage in kc-dev-flow-2/references/sd/workflow.md with the budget step in kc-dev-flow-2/scripts/lint-skills.py lowered by the same count; the pins in kc-dev-flow-2/scripts/test_poc_readme.py and kc-dev-flow-2/scripts/test_number_guards.py replaced and added as the design lists; the Reserve bullet stays byte-identical (the ADR-line check belongs to fo-write-checks); every acceptance criterion in the task file green, each falsifier shown failing by a mutation you run (python3 -B, caches cleared)
No FO-read word added beyond the design; the candidate's own kc-dev-flow-2/scripts/lint-skills.py exits 0; roborev evidence= line; push without force; CI green on the PR head; CI cost measured or stated as not measured

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.25.0

Profile: pilot. Approved design: `## Design` and `## Acceptance criteria` in the task file; ideation gate approved 2026-10-19 in batch 3, accepting each decision as the gate question states. fo-write-checks runs in parallel and changes no README word; captain-question-load later edits the Delivery authority paragraph. Recount the words FO reads at each moment with an independent script and save it under the task folder.

Delivery: one pull request in iamcxa/kc-claude-plugins, in the worktree `dispatch build` made for you; `git fetch origin` first and base the branch on origin/main (the worktree may start at an older workspace HEAD). Push and Draft PR under the Captain's standing grant in his global instructions (~/.claude/CLAUDE.md, Autonomous action boundaries): "No ask on a repo Kent owns: push a branch and open a Draft PR once the work cleared its own bar". Conventional Commit title. Open as Draft. Do not bump versions; release-please owns them. Stage named files only, no empty commits. Other batch-3 tasks are in flight in other worktrees; change only the files your design lists, and stop and return to FO if the change needs another.

Before reporting, commit and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.25.0/extensions/roborev/roborev_gate.py --repo <worktree> --base <base sha>`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report. Run each test suite and mutation with a time cap.

Never run `git remote set-url` or any `git config` write in a worktree of this repository: worktrees share one config, including the Captain's main checkout. Use a throwaway `git clone` for that. Do not request reviews, comment on any PR, mark ready or merge.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
