# validation-4

Dispatched: e2524e93025dd0d5d9217b4d722c2b169d01fda6 (workflow checkout, kc-dev-flow-2 0.21.0 README); candidate #639 4072363b
Model: sonnet
Fresh validation recheck after the round-3 P1 repair (implementation-6/7). Codex round 4 requested at dispatch.

## Checklist

Independent recheck of the cycle-3 repair on #639 head 4072363b: the Codex round-3 P1 (a restarted session that recreates a missing watch entry for an already-ready PR waits forever for a draft True -> False line) and its class (any wait whose exit is a pr_watch change line, including a re-add erasing a missed flip and step 2 hanging on an already-green Draft) reproduced fixed against 24029378, the new tests shown failing under mutations you run yourself, the ready-time read the text names run read-only against real GitHub on an already-ready PR (for example iamcxa/kc-claude-plugins#637) with its observed output, the round-1 and round-2 fixes still holding, and AC-1 to AC-6 re-run at the new head with any change from validation cycle 3 named
The minimal acceptance script updated to the new head, run by you exactly as written in a fresh shell, with its observed output
adr_lint.py docs/adr --since <base> run at the new head with its exit code; verdict PASSED or REJECTED naming the head, with findings classified by the workflow's Review-finding disposition

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.21.0

Profile: pilot. Candidate: iamcxa/kc-claude-plugins PR #639, head 4072363b (repair of 24029378 for the Codex round-3 P1 recorded under `### Feedback Cycles`, Cycle 3), base origin/main. Check out the head in a throwaway worktree (`git worktree add --detach /tmp/<name> 4072363b`) and remove it when done. Read and run only: do not push, comment on the PR, request reviews, or edit the candidate or its worktree. A repair goes back through FO. Do not touch the real learning store under the repository's git common directory; run every learning.py command against a temp repository.

Never run `git remote set-url` or any `git config` write in a worktree of this repository: worktrees share one config, including the Captain's main checkout. Use a throwaway `git clone` for that.

The minimal acceptance script must run unchanged in a fresh shell and name any checkout or install it needs; FO will run it exactly as written before the gate. Write any package script you name as its full path.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
