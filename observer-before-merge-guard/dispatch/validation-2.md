# validation-2

Dispatched: e2524e93025dd0d5d9217b4d722c2b169d01fda6 (workflow checkout, kc-dev-flow-2 0.21.0 README); candidate #632 d127ec71
Model: sonnet
Fresh validation recheck after the round-1 P1 repair (implementation-2/3). Codex round 2 requested at dispatch.

## Checklist

Independent recheck of the cycle-1 repair on #632 head d127ec71: the Codex round-1 P1 (the documented late-report repair could not commit an untracked observer.md) reproduced fixed against 0830a3be by following EXTENSION.md's text literally on a scratch fixture, the new test shown failing under a mutation you run yourself, and AC-1 to AC-9 re-run at the new head with any change from validation cycle 1 named
The minimal acceptance script updated to the new head, run by you exactly as written in a fresh shell from a named checkout, with its observed output
adr_lint.py docs/adr --since <base> run at the new head with its exit code; verdict PASSED or REJECTED with findings classified by the workflow's Review-finding disposition

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.21.0

Profile: pilot. Candidate: iamcxa/kc-claude-plugins PR #632, branch spacedock-ensign/observer-before-merge-guard, head d127ec71 (the repair commit d8f329ee for the Codex round-1 P1 recorded under `### Feedback Cycles`, Cycle 1, plus a GitHub merge of #631's new head 20c9ec53; this PR's own hunks equal `git diff 70da29c7 d8f329ee`). Base is #631's branch, stacked; #631 is not merged. Check out the head in a throwaway worktree (`git worktree add --detach /tmp/<name> d127ec71`) and remove it when done. Read and run only: do not push, comment on the PR, request reviews, or edit the candidate or its worktree. A repair goes back through FO.

The real dev2 state checkout for AC-1 is /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state; read it only, never commit there. Dispatching an observer for AC-9 is allowed only on a scratch fixture or read-only on the real archived task; save nothing into the real state.

Never run `git remote set-url` or any `git config` write in a worktree of this repository: worktrees share one config, including the Captain's main checkout. Do that only inside a throwaway `git clone`.

The minimal acceptance script must run unchanged in a fresh shell and name any checkout or install it needs; FO will run it exactly as written before the gate.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
