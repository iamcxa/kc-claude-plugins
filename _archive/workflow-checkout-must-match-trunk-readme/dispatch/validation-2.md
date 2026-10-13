# validation-2

Dispatched: e2524e93025dd0d5d9217b4d722c2b169d01fda6 (workflow checkout, kc-dev-flow-2 0.21.0 README); candidate #631 70da29c7
Model: sonnet
Fresh validation recheck after the FO-authorized repair (implementation-2/3). Codex round 2 requested at dispatch.

## Checklist

Independent recheck of the cycle-1 repair on #631 head 70da29c7: both Codex round-1 P2 (clean filters hide a CRLF README; the printed remedy does not quote the checkout path) reproduced fixed against 085e28aa, their new tests shown failing under a mutation you run yourself, and AC-1 to AC-6 re-run at the new head with any change from the cycle-1 validation named
The minimal acceptance script updated to the new head, run by you exactly as written in a fresh shell from a named checkout, with its observed output
adr_lint.py docs/adr --since <base> run at the new head with its exit code; verdict PASSED or REJECTED with findings classified by the workflow's Review-finding disposition

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.21.0

Profile: pilot. Candidate: iamcxa/kc-claude-plugins PR #631, branch spacedock-ensign/workflow-checkout-must-match-trunk-readme, head 70da29c7 (repair of 085e28aa for the two Codex round-1 P2 recorded under `### Feedback Cycles`, Cycle 1), base origin/main 9e68eb87. Check out the head in a throwaway worktree (`git worktree add --detach /tmp/<name> 70da29c7`) and remove it when done. Read and run only: do not push, comment on the PR, request reviews, or edit the candidate or its worktree. A repair goes back through FO.

The minimal acceptance script must run unchanged in a fresh shell and name any checkout or install it needs; FO will run it exactly as written before the gate.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).

Never run `git remote set-url` or any `git config` write in a worktree of this repository: worktrees share one config, including the Captain's main checkout. Do that only inside a throwaway `git clone`. The cycle-1 validator did it once on 2026-10-13 and rewrote the shared origin URL.
