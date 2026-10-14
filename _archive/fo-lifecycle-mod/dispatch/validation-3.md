# validation-3

Dispatched: 656543f41b2f3d11717d418e6b5f6680d97964ff (workflow checkout, kc-dev-flow-2 0.22.1 README); candidate #643 5b280387
Model: sonnet
Validation of the redone cycle-3 design with the four D2 replay runs. Codex round 3 on this PR requested at dispatch.

## Checklist

Independent verdict on #643 head 5b280387 (the redone cycle-3 design) against AC-8 to AC-17, re-running each evidence command and at least one falsifier per criterion yourself, including AC-12's recount of the words FO reads at each moment from the shipped text and script output, and judging the one file outside the design's list (kc-dev-flow-2/scripts/test_observer_recovery.py, commit ca3d1427) and the roborev:669 High against the post-release sync
The four replay runs of D2 as the design's Replay plan states them (stub gh, model claude-opus-5-5, Agent and SendMessage disallowed, harness copied from /tmp/replay-c2): S1 at the merge ask under the cue 「用 /kc-dev-flow-2:dev 然後 resume」, one control run first and then two design runs, stopping if the control already does the right thing; S2 at the merged PR under the cue 「合併了，你應該主動追蹤 362 是否合併」, one design run; per run the M measurements the design names, the first twenty tool calls and the token usage read from the stream; run no other replay
A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell from a named checkout, with its observed output
/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/scripts/adr_lint.py docs/adr --since <base> and /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/scripts/number_guards.py check run with their exit codes; verdict PASSED or REJECTED naming the head, with findings classified by the workflow's Review-finding disposition

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1

Profile: pilot. Candidate: iamcxa/kc-claude-plugins PR #643, branch spacedock-ensign/fo-lifecycle-mod, head 5b280387 (the redone cycle-3 design, built on d6a427aa), base origin/main 0cdb40a7. Check out the head in a throwaway worktree (`git worktree add --detach /tmp/<name> 5b280387`) and remove it when done. Read and run only: do not push, comment on any PR, request reviews, or edit the candidate or its worktree. A repair goes back through FO.

Captain amendments 1 to 4 are in the task file; ADR 0015 is in the PR. The replays are the four runs D2 approved, no more. Keep the harness and fixtures outside the repository (a scratch directory under /tmp), never against a real workflow or the real learning store, with a stub gh first on PATH; record what the launch command was. If the launcher or a flag the design names does not exist (check with --help), say so and use the design's stated fallback, or stop and report.

Never run `git remote set-url` or any `git config` write in a worktree of this repository: worktrees share one config, including the Captain's main checkout. Use a throwaway `git clone` for that.

The minimal acceptance script must run unchanged in a fresh shell and name any checkout or install it needs; FO will run it exactly as written before the gate. Write any package script you name as its full path.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
