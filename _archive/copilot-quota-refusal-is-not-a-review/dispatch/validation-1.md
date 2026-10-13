# validation-1

Dispatched: e2524e93025dd0d5d9217b4d722c2b169d01fda6 (workflow checkout, kc-dev-flow-2 0.21.0 README); candidate #630 218645da
Model: sonnet

## Checklist

Independent verdict on #630 head 218645da against AC-1 to AC-7, re-running each evidence command and at least one falsifier per criterion yourself rather than citing the implementation report; AC-6's behaviour half named as an unverified obligation
A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh shell from a named checkout, with its observed output
adr_lint.py docs/adr --since <base> run with its exit code; verdict PASSED or REJECTED with findings classified by the workflow's Review-finding disposition

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.21.0

Profile: pilot. Candidate: iamcxa/kc-claude-plugins PR #630, branch spacedock-ensign/copilot-quota-refusal-is-not-a-review, head 218645da, base origin/main 9e68eb87. Check out the head in a throwaway worktree (`git worktree add --detach /tmp/<name> 218645da`) and remove it when done. Read and run only: do not push, comment on the PR, request reviews, or edit the candidate or its worktree. A repair goes back through FO.

Live reads of Copilot reviews with `gh api` are allowed (read only). Do not request Copilot.

The minimal acceptance script must run unchanged in a fresh shell and name any checkout or install it needs; FO will run it exactly as written before the gate.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
