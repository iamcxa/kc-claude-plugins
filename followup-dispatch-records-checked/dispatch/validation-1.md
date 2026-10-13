# validation-1

Dispatched: 656543f41b2f3d11717d418e6b5f6680d97964ff (workflow checkout, kc-dev-flow-2 0.22.1 README); candidate #642 12670427
Model: sonnet
Codex round 1 requested at dispatch.

## Checklist

Independent verdict on #642 head 12670427 against AC-1 to AC-7, re-running each evidence command and at least one falsifier per criterion yourself (replays against the archived and active records with the counts re-measured, the default folder mode otherwise unchanged, the lint budget and the README clause), and judging the implementation's one change to the design's file list (the FIXES["resumed-dispatch"] regex in kc-dev-flow-2/scripts/test_sd_dispatch.py of the candidate, authorized by FO after CI failed)
A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh shell from a named checkout, with its observed output
/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/scripts/adr_lint.py docs/adr --since <base> run with its exit code; verdict PASSED or REJECTED naming the head, with findings classified by the workflow's Review-finding disposition

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1

Profile: pilot. Candidate: iamcxa/kc-claude-plugins PR #642, branch spacedock-ensign/followup-dispatch-records-checked, head 12670427, base origin/main 656543f4. Check out the head in a throwaway worktree (`git worktree add --detach /tmp/<name> 12670427`) and remove it when done. Read and run only: do not push, comment on any PR, request reviews, or edit the candidate or its worktree. A repair goes back through FO.

Records for the replays (read only): /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/ (active task folders and _archive/).

Never run `git remote set-url` or any `git config` write in a worktree of this repository: worktrees share one config, including the Captain's main checkout. Use a throwaway `git clone` for that.

The minimal acceptance script must run unchanged in a fresh shell and name any checkout or install it needs; FO will run it exactly as written before the gate. Write any package script you name as its full path.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
