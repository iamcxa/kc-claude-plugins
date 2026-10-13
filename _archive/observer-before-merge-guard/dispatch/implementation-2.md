# implementation-2

Dispatched: e2524e93025dd0d5d9217b4d722c2b169d01fda6 (workflow checkout, kc-dev-flow-2 0.21.0 README); candidate #632 0830a3be
Model: sonnet
Fresh worker (prior implementation and validation workers sent shutdown_request). FO fix lane for the Codex round-1 P1; phase 1 investigation only.

## Checklist

Investigation first, with no candidate change: reproduce the Codex round-1 P1 on #632 head 0830a3be (the documented late-report repair cannot commit an untracked `_archive/<slug>/observer.md` with a pathspec-only `git commit`), following EXTENSION.md's text literally on a scratch fixture, send FO the result and your proposed fix, then wait for FO's fix authorization message
After FO's fix authorization only: fix it so the documented steps work as written, with a check that fails without the fix (shown failing by a mutation run, e.g. the recovery test following the documented commands rather than its own `git add`); push to #632's branch; CI green on the new head
Stage report: new head, the roborev_gate.py evidence= line, test and mutation results, and anything left for FO

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.21.0

Profile: pilot. Repair under the workflow's Review-finding disposition step 3; the task stays in validation and you work as the implementation stage in the existing worktree. Approved design, D2 and D3 unchanged.

Worktree and PR: /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-observer-before-merge-guard, branch spacedock-ensign/observer-before-merge-guard, PR iamcxa/kc-claude-plugins#632, head 0830a3be, base #631's branch (stacked). Do not create a new worktree. #631 is being repaired in parallel by another worker (dev skill invocation of workflow_checkout.py): do not edit that sentence; FO merges #631's new head into this branch afterwards. #633 is stacked on this branch; do not touch it.

The finding (Codex round 1, review:5500580111, under the task's `### Feedback Cycles`, Cycle 1): P1 `extensions/learn/EXTENSION.md` around line 22: the late-report repair commits an untracked `_archive/<slug>/observer.md` with a pathspec-only `git commit`, which Git refuses for an untracked file; `test_observer_recovery.py` passes only because it runs `git add` first. Put the staging step in the documented repair, and make the test follow the documented commands so it cannot pass on steps the text does not give.

Phase 1 (now): read-only investigation on a scratch fixture; do not edit, commit or push the worktree, and never commit into the real dev2 state checkout. Never run `git remote set-url` or any `git config` write in a worktree of this repository; use a throwaway `git clone`. Send FO one message (to `main`) with the reproduction and proposed fix, then wait. FO's reply naming the fix is the only authorization to change the candidate.

Phase 2 (after FO's message): commit `fix(kc-dev-flow-2): ...`, stage named files only. Before pushing, commit and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.21.0/extensions/roborev/roborev_gate.py --repo <worktree> --base 0830a3be`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest. Put the `evidence=` or `incomplete:` line in the stage report. Push (never force), wait for CI (`gh pr checks 632 --repo iamcxa/kc-claude-plugins`).

Do not comment on the PR, request reviews, mark ready or merge. A file the PR does not already change is a scope change: stop and return it to FO.

Send your phase-1 report and your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
