# validation-1

Dispatched: 656543f41b2f3d11717d418e6b5f6680d97964ff (workflow checkout, kc-dev-flow-2 0.22.1 README); candidate #643 33295355
Model: sonnet
Codex round 1 requested at dispatch; PR added to pr_watch.

## Checklist

Independent verdict on #643 head 33295355 against AC-1 to AC-3, AC-6 (met by the merge hook's deletion under Captain amendment 1) and AC-7, re-running each evidence command and at least one falsifier per criterion yourself, and judging the two roborev High findings (roborev:653, a failed observer check cannot stop pr-merge's own sentinel scan in the same pass; roborev:654, the mods are not yet copied into the adopter workflows) against the design's Limits and the post-release sync
The D3 go/no-go replay as the approved design's Replay method describes it, limited to the S2 pair under the Captain's verbatim cue (one control run without the mod files, one mod run, same fixture, model claude-opus-5-5): the M5 to M8 record per run, the first twenty tool calls, and the token usage read from the stream (not total_cost_usd); stop after this pair and report, running no other replay
A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh shell from a named checkout, with its observed output
/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/scripts/adr_lint.py docs/adr --since <base> and /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/scripts/number_guards.py check run with their exit codes; verdict PASSED or REJECTED naming the head, with findings classified by the workflow's Review-finding disposition

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1

Profile: pilot. Candidate: iamcxa/kc-claude-plugins PR #643, branch spacedock-ensign/fo-lifecycle-mod, head 33295355, base origin/main 656543f4. Check out the head in a throwaway worktree (`git worktree add --detach /tmp/<name> 33295355`) and remove it when done. Read and run only: do not push, comment on any PR, request reviews, or edit the candidate or its worktree. A repair goes back through FO.

Captain amendment 1 (task file) removed the merge hook; ADR 0015 is reserved and drafted in the PR. The replay is the Captain-approved spend under D3 with FO's change: one pair only. Keep the harness and fixtures outside the repository (a scratch directory under /tmp), never against a real workflow or the real learning store, with a stub gh first on PATH; record what the launch command was. If the launcher or a flag the design names does not exist (check with --help), say so and use the design's stated fallback, or stop and report.

Never run `git remote set-url` or any `git config` write in a worktree of this repository: worktrees share one config, including the Captain's main checkout. Use a throwaway `git clone` for that.

The minimal acceptance script must run unchanged in a fresh shell and name any checkout or install it needs; FO will run it exactly as written before the gate. Write any package script you name as its full path.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
