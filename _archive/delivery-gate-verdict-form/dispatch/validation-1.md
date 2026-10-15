# validation-1

Dispatched: 656543f41b2f3d11717d418e6b5f6680d97964ff (workflow checkout, kc-dev-flow-2 0.22.1 README); candidate #647 57d58532
Model: sonnet
Codex round 1 requested at dispatch.

## Checklist

Independent verdict on #647 head 57d58532 against AC-1 to AC-6, re-running each evidence command and at least one falsifier per criterion yourself (the relay report that held, each accepted Verdict spelling, forms outside the family, a REJECTED or verdictless report quoting an earlier PASSED, the word budget, the pinned sentence), and judging the implementation's two choices: the [ \t] separator, and AC-4's conflict, where the latest section that names a candidate wins, so a later REJECTED section that names none falls through to an older PASSED one; say whether a REJECTED recheck on the same head as an older PASSED can reach exit 0, with a probe
AC-7: one fresh validator run on the package text of the candidate, writing a validation report for a small fixture, with its verdict line checked against the stated form, and one control run on the base text
A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/scripts/adr_lint.py docs/adr --since <base> with its exit code; verdict PASSED or REJECTED naming the head, with findings classified by the workflow's Review-finding disposition

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1

Profile: pilot. Candidate: iamcxa/kc-claude-plugins PR #647, head 57d58532, base origin/main c545b896. Check out the head in a throwaway worktree (`git worktree add --detach /tmp/<name> 57d58532`) and remove it when done. Read and run only: do not push, comment on any PR, request reviews, or edit the candidate or its worktree. A repair goes back through FO. Read relay and other adopter reports only through read-only commands. For AC-7 use a headless run on a scratch fixture, never a real workflow, and record the launch command and the tokens read from the stream.

Never run `git remote set-url` or any `git config` write in a worktree of this repository. Run each suite and mutation with a time cap, and remove every throwaway worktree you add before reporting. The minimal acceptance script must run unchanged in a fresh shell, name any checkout or install it needs (including which spacedock binary, if any) and write any package script as its full path; FO will run it exactly as written before the gate.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
