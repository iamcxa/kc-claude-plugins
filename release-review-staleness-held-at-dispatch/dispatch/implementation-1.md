# implementation-1

Dispatched: c27e76590c1d2dc910e7fa2d332242a7534df0b0 (workflow checkout, kc-dev-flow-2 0.27.0 README); batch 5 addition
Model: sonnet

## Checklist

One Draft PR (feat(kc-dev-flow-2): ...) from a branch off origin/main (a476b5ff69c27627220e96af27ee898641c6f100) implementing the approved cycle-2 design: kc-dev-flow-2/scripts/pr_watch.py holds() beside seeds() printing the hold next: line, kc-dev-flow-2/scripts/test_pr_watch.py, the workflow.md Release review bullet with the 5-word cut (5374 to 5369) and the kc-dev-flow-2/scripts/lint-skills.py cut step carrying the Captain's quoted words, ADR 0032; only the files the design's delivery line names
Every acceptance criterion green with the evidence each names, including the R4 record shape (journey only, prose Signal 1, no review line) holding and the documented review-line tails clearing; each falsifier shown failing by a mutation you run (python3 -B, caches cleared); kc-dev-flow-2/scripts/test_sd_dispatch.py FIXES still match
/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0/scripts/lint-skills.py, /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0/scripts/adr_lint.py docs/adr --since <base> --require 0032 exit 0; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0/scripts/comment_ratio.py within its maximum; roborev evidence= line; push without force and without -u; CI green on the PR head; CI cost measured or stated as not measured

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0

Number guards: ADR: 0032

Profile: pilot. Approved design: ## Design and ## Acceptance criteria in the task file, cycle 2; ideation gate approved 2026-10-23 (Captain 「可以」, accepting the three Captain decisions as recommended: regex mark recognition with no new workflow.md words, the 5-word cut of "no script checks that line", and accepting the known false holds). The cut step's captain value is that 「可以」 to the gate question that named the cut. If #708 (which raises the workflow.md budget to 5389) merges first, rebase and re-measure. If a change needs a file the design does not list, stop and return to FO.

Delivery: one pull request in iamcxa/kc-claude-plugins, in the worktree `dispatch build` made for you; `git fetch origin` first and base the branch on origin/main. Push and Draft PR under the Captain's standing grant in his global instructions (~/.claude/CLAUDE.md, Autonomous action boundaries): "No ask on a repo Kent owns: push a branch and open a Draft PR once the work cleared its own bar". Conventional Commit title. Open as Draft. Do not bump versions. Stage named files only, no empty commits. If a push or gh call is refused by the permission check, stop and report it; do not work around it.

Before reporting, commit and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0/extensions/roborev/roborev_gate.py --repo <worktree> --base <base sha>`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report.

Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not request reviews, comment on any PR, mark ready or merge.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
