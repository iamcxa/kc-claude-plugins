# implementation-2

Dispatched: e2524e93025dd0d5d9217b4d722c2b169d01fda6 (workflow checkout, kc-dev-flow-2 0.21.0 README); candidate #631 085e28aa
Model: sonnet
Fresh worker (context-budget probe unavailable; prior implementation and validation workers sent shutdown_request). FO fix lane, Review-finding disposition step 3; phase 1 investigation only.

## Checklist

Investigation first, with no candidate change: reproduce both Codex round-1 P2 on #631 head 085e28aa (a clean filter such as `*.md text eol=lf` makes a CRLF README hash equal to the LF trunk blob; an unquoted checkout path with whitespace makes the printed remedy not runnable), send FO the result (confirmed or not, command and output) and your proposed fix, then wait for FO's fix authorization message
After FO's fix authorization only: fix each with a test that fails without the fix (shown failing by a mutation run); push to #631's branch; CI green on the new head
Stage report: new head, the roborev_gate.py evidence= line, test and mutation results, and anything left for FO

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.21.0

Profile: pilot. Repair under the workflow's Review-finding disposition step 3 (FO fix authorization); the task stays in validation and you work as the implementation stage in the existing worktree. Approved design, D1-D3 and ADR 0014 are unchanged.

Worktree and PR: /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-workflow-checkout-must-match-trunk-readme, branch spacedock-ensign/workflow-checkout-must-match-trunk-readme, PR iamcxa/kc-claude-plugins#631, head 085e28aa, base main. Do not create a new worktree. Task observer-before-merge-guard is being implemented on a branch stacked on 085e28aa; do not touch it, FO merges your new head into it afterwards.

The findings (Codex round 1, review:5500393427, recorded under the task's `### Feedback Cycles`, Cycle 1):
1. P2 `scripts/workflow_checkout.py` around line 74: `git hash-object` applies clean filters, so a CRLF README can hash equal to the LF trunk blob. Use `--no-filters`.
2. P2 `scripts/workflow_checkout.py` around line 49: the printed remedy does not shell-quote the checkout path. Quote it.

Phase 1 (now): read-only investigation in a throwaway copy or repository; do not edit, commit or push the worktree. Never run `git remote set-url` or any `git config` write in a worktree of this repository: worktrees share one config, including the Captain's main checkout; do that only inside a throwaway `git clone`. Send FO one message (to `main`) with the reproduction and a proposed fix, then wait. FO's reply naming the fix is the only authorization to change the candidate.

Phase 2 (after FO's message): commit with a `fix(kc-dev-flow-2): ...` subject, stage named files only. Before pushing, commit and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.21.0/extensions/roborev/roborev_gate.py --repo <worktree> --base 085e28aa`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest as findings for FO. Put the printed `evidence=` line, or the `incomplete:` line on exit 3, in the stage report. Push (never force), wait for CI (`gh pr checks 631 --repo iamcxa/kc-claude-plugins`).

Do not comment on the PR, request reviews, mark ready or merge. If the fix needs a file the PR does not already change, stop and return it to FO as a scope change.

Send your phase-1 report and your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
