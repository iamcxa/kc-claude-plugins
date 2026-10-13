# validation-1

Dispatched: e2524e93025dd0d5d9217b4d722c2b169d01fda6 (workflow checkout, kc-dev-flow-2 0.21.0 README); candidate #632 0830a3be
Model: sonnet
Fresh validation; Codex round 1 requested at dispatch.

## Checklist

Independent verdict on #632 head 0830a3be against AC-1 to AC-9, re-running each evidence command and at least one falsifier per criterion yourself rather than citing the implementation report, including AC-1 against the real dev2 state branch, AC-8's learn acceptance of the extra archived file, and AC-9's behavioural half (an observer dispatched on the AC-8 fixture reports a Coverage window over both path pairs)
A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh shell from a named checkout, with its observed output
adr_lint.py docs/adr --since <base> run with its exit code; an independent check of the implementation's unreproduced roborev:609 High finding (a state checkout that is a subdirectory of its repository); verdict PASSED or REJECTED with findings classified by the workflow's Review-finding disposition

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.21.0

Profile: pilot. Candidate: iamcxa/kc-claude-plugins PR #632, branch spacedock-ensign/observer-before-merge-guard, head 0830a3be (the implementation commit 2ec59fc8 plus a GitHub merge of #631's repaired head 70da29c7; `git diff 70da29c7...0830a3be` equals `git diff 085e28aa 2ec59fc8`). Base is #631's branch, stacked; #631 is not merged. Check out the head in a throwaway worktree (`git worktree add --detach /tmp/<name> 0830a3be`) and remove it when done. Read and run only: do not push, comment on the PR, request reviews, or edit the candidate or its worktree. A repair goes back through FO.

The real dev2 state checkout for AC-1 is /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state; read it only, never commit there. Dispatching an observer for AC-9 is allowed only on a scratch fixture or read-only on the real archived task; save nothing into the real state.

Never run `git remote set-url` or any `git config` write in a worktree of this repository: worktrees share one config, including the Captain's main checkout. Do that only inside a throwaway `git clone`.

The minimal acceptance script must run unchanged in a fresh shell and name any checkout or install it needs; FO will run it exactly as written before the gate.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
