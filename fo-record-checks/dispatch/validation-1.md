# validation-1

Dispatched: e2524e93025dd0d5d9217b4d722c2b169d01fda6 (workflow checkout, kc-dev-flow-2 0.21.0 README); candidate #640 63dfff51
Model: sonnet
Codex round 1 requested at dispatch.

## Checklist

Independent verdict on #640 head 63dfff51 against AC-1 to AC-8, re-running each evidence command and at least one falsifier per criterion yourself (replays against the archived records, the default folder mode unchanged, delivery_gate.py on the named task and head pairs, lint budget, CI step, and one live gh run on an open PR read only), and judging the implementation's two changes to the design (a fifth workflow.md sentence; prefix-of-equal-length SHA comparison kept despite roborev:625/626)
A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh shell from a named checkout, with its observed output
adr_lint.py docs/adr --since <base> run with its exit code; verdict PASSED or REJECTED naming the head, with findings classified by the workflow's Review-finding disposition

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.21.0

Profile: pilot. Candidate: iamcxa/kc-claude-plugins PR #640, branch spacedock-ensign/fo-record-checks, head 63dfff51, base origin/main 38c55fcf. Check out the head in a throwaway worktree (`git worktree add --detach /tmp/<name> 63dfff51`) and remove it when done. Read and run only: do not push, comment on any PR, request reviews, or edit the candidate or its worktree. A repair goes back through FO.

Archived records for the replays (read only): /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/_archive/. For the live gh run use #639 or #640 read only.

Never run `git remote set-url` or any `git config` write in a worktree of this repository: worktrees share one config, including the Captain's main checkout. Use a throwaway `git clone` for that.

The minimal acceptance script must run unchanged in a fresh shell and name any checkout or install it needs; FO will run it exactly as written before the gate. Write any package script you name as its full path.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
