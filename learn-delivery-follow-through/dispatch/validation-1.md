# validation-1

Dispatched: e2524e93025dd0d5d9217b4d722c2b169d01fda6 (workflow checkout, kc-dev-flow-2 0.21.0 README); candidate #639 f1689849
Model: sonnet
Codex round 1 requested at dispatch.

## Checklist

Independent verdict on #639 head f1689849 against AC-1 to AC-6, re-running each evidence command and at least one falsifier per criterion yourself, including AC-2's control arm stalling on origin/main text and the new arm settling; AC-7 named as an unverified live obligation
A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh shell from a named checkout, with its observed output
adr_lint.py docs/adr --since <base> run with its exit code; verdict PASSED or REJECTED naming the head, with findings classified by the workflow's Review-finding disposition

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.21.0

Profile: pilot. Candidate: iamcxa/kc-claude-plugins PR #639, head f1689849, base origin/main. Check out the head in a throwaway worktree (`git worktree add --detach /tmp/<name> f1689849`) and remove it when done. Read and run only: do not push, comment on the PR, request reviews, or edit the candidate or its worktree. A repair goes back through FO. Do not touch the real learning store under the repository's git common directory; run every learning.py command against a temp repository.

Never run `git remote set-url` or any `git config` write in a worktree of this repository: worktrees share one config, including the Captain's main checkout. Use a throwaway `git clone` for that.

The minimal acceptance script must run unchanged in a fresh shell and name any checkout or install it needs; FO will run it exactly as written before the gate. Write any package script you name as its full path.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
