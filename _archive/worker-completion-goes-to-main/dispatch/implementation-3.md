# implementation-3

Dispatched: e2524e93025dd0d5d9217b4d722c2b169d01fda6 (workflow checkout, kc-dev-flow-2 0.21.0 README); candidate #633 a7fa7f1b
Model: sonnet
FO fix lane for the Codex round-2 P2 plus a merge of #632's new head 7679ab7a; phase 1 investigation only.

## Checklist

Investigation first, with no candidate change: reproduce the Codex round-2 P2 on #633 head a7fa7f1b (`replay_dispatch.py build` without `--scope` writes a scope.txt that lacks the completion-recipient line, so a candidate replay cannot exercise the fix), reconcile it with the implementation's roborev:612 decline (AC-4's control arm builds without the line), send FO the result and a proposed fix, then wait for FO's fix authorization message
After FO's fix authorization only: merge (never rebase) #632's new head 7679ab7a into #633's branch, apply the authorized fix with a test that fails without it (mutation run), keep this PR's own hunks otherwise equal to the validated ones; push (never force); CI green on the new head
Stage report: new head, the merge result, the fix and its mutation, roborev_gate.py evidence= line, anything left for FO

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.21.0

Profile: pilot. Repair under the workflow's Review-finding disposition step 3; the task stays in validation and you work as the implementation stage in the existing worktree. Approved design and D2 unchanged.

Worktree and PR: /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-worker-completion-goes-to-main, branch spacedock-ensign/worker-completion-goes-to-main, PR iamcxa/kc-claude-plugins#633, head a7fa7f1b, base #632's branch. #632 moved to 7679ab7a (a merge of origin/main after #631 squash-merged; #631's text is now on main). Fast-forward the local worktree to origin's head first. Do not create a new worktree.

The finding (Codex round 2, review:5501183844, under the task's `### Feedback Cycles`, Cycle 1): P2 `references/sd/workflow.md` around line 100: `replay_dispatch.py build` without `--scope` builds `scope.txt` with only the package root and harness text, so a candidate replay lacks the new completion-recipient line. Add the line to the helper's generated scope, keeping a way for AC-4's control arm to build without it. `scripts/replay_dispatch.py` and its test are outside this PR's current files; FO authorizes them for this finding if your fix needs them.

Phase 1 (now): read-only investigation; do not edit, commit or push the worktree. Never run `git remote set-url` or any `git config` write in a worktree of this repository (shared config, including the Captain's main checkout); use a throwaway `git clone`. Send FO one message (to `main`) with the reproduction and proposed fix, then wait. FO's reply naming the fix is the only authorization to change the candidate.

Phase 2 (after FO's message): commit `fix(kc-dev-flow-2): ...`, stage named files only. Before pushing, commit and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.21.0/extensions/roborev/roborev_gate.py --repo <worktree> --base 7679ab7a`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest. Put the `evidence=` or `incomplete:` line in the stage report. Push (never force), wait for CI (`gh pr checks 633 --repo iamcxa/kc-claude-plugins`).

Do not comment on the PR, request reviews, mark ready or merge.

Send your phase-1 report and your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
