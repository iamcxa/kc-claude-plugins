# implementation-4

Dispatched: e2524e93025dd0d5d9217b4d722c2b169d01fda6 (workflow checkout, kc-dev-flow-2 0.21.0 README); candidate #639 8d15a0c0
Model: sonnet
Fresh worker; FO fix lane for the Codex round-2 findings; phase 1 investigation only.

## Checklist

Investigation first, with no candidate change: reproduce the two Codex round-2 findings on #639 head 8d15a0c0 (a restarted session cannot resume an open learning PR recorded before ready; an acknowledged open delivery is invisible to plain notices), send FO the result per finding and your proposed fix, then wait for FO's fix authorization message
After FO's fix authorization only: fix them with tests that fail without the fix (shown failing by a mutation run); push to #639's branch; CI green on the new head
Stage report: new head, the roborev_gate.py evidence= line, test and mutation results, and anything left for FO

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.21.0

Profile: pilot. Repair under the workflow's Review-finding disposition step 3; the task stays in validation and you work as the implementation stage in the existing worktree (`git worktree list` in /Users/kent/conductor/workspaces/kc-claude-plugins/colombo shows the branch of PR iamcxa/kc-claude-plugins#639; fast-forward it to origin's head first). Approved design and D1-D3 unchanged; keep the change inside the four files the PR already changes.

The findings (Codex round 2, review:5502957038) are recorded under the task's `### Feedback Cycles`, Cycle 2: (1) P1 a restarted session that finds the delivery still open (recorded before ready) recovers it with an honest stopped-owner attestation and continues the lifecycle (ready, merge ask, record); (2) P2 find acknowledged open deliveries with `notices --all` while presenting only unread results. Keep the round-1 fixes (head check, no applicable checks with the mergeStateStatus BLOCKED hold, settle by actor) intact.

Phase 1 (now): read-only investigation; do not edit, commit or push. Never run `git remote set-url` or any `git config` write in a worktree of this repository; use a throwaway `git clone`. Never touch the real learning store under the repository's git common directory; use temp stores. Send FO one message (to `main`) with the reproduction and proposed fix, then wait. FO's reply naming the fix is the only authorization to change the candidate.

Phase 2 (after FO's message): commit `fix(kc-dev-flow-2): ...`, stage named files only. Before pushing, commit and run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.21.0/extensions/roborev/roborev_gate.py --repo <worktree> --base 8d15a0c0`. On exit 1 fix the findings inside your scope, commit and run it again, at most twice, and report the rest. Put the `evidence=` or `incomplete:` line in the stage report. Push (never force), wait for CI (`gh pr checks 639 --repo iamcxa/kc-claude-plugins`).

Do not comment on the PR, request reviews, mark ready or merge.

Send your phase-1 report and your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
