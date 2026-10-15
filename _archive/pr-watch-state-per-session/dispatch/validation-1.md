# validation-1

Dispatched: 656543f41b2f3d11717d418e6b5f6680d97964ff (workflow checkout, kc-dev-flow-2 0.22.1 README); candidate #646 e4fca679
Model: sonnet
Codex round 1 requested at dispatch.

## Checklist

Independent verdict on #646 head e4fca679 against AC-1 to AC-6, re-running each evidence command and at least one falsifier per criterion yourself (the two-session overlap test, the replay of the 2026-10-14 loss, the default-path keying and fallback, the old shared file left unread, tasks output byte-identical in the default case, and AC-6 that a worker and a background command see FO's session id)
A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell from a named checkout, with its observed output
/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/scripts/adr_lint.py docs/adr --since <base> run with its exit code; verdict PASSED or REJECTED naming the head, with findings classified by the workflow's Review-finding disposition

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1

Profile: pilot. Candidate: iamcxa/kc-claude-plugins PR #646, head e4fca679, base origin/main c545b896. Check out the head in a throwaway worktree (`git worktree add --detach /tmp/<name> e4fca679`) and remove it when done. Read and run only: do not push, comment on any PR, request reviews, or edit the candidate or its worktree. A repair goes back through FO. Run every probe under a temporary HOME or with --state in /tmp; never read or write the real ~/.local/state/kc-dev-flow-2 files of other sessions.

Never run `git remote set-url` or any `git config` write in a worktree of this repository. Run each suite and mutation with a time cap, and remove every throwaway worktree you add before reporting. The minimal acceptance script must run unchanged in a fresh shell, name any checkout or install it needs (including which spacedock binary, if any) and write any package script as its full path; FO will run it exactly as written before the gate.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
