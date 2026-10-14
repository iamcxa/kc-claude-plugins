# validation-8

Dispatched: 656543f41b2f3d11717d418e6b5f6680d97964ff (workflow checkout, kc-dev-flow-2 0.22.1 README); candidate #643 3a3cfc30
Model: sonnet
Recheck after the Codex round-7 repair; no replays. Codex round 8 on this PR requested at dispatch.

## Checklist

Independent recheck of #643 head 3a3cfc30 against validation cycle 7 at 5e10c355: the Codex round-7 P1 (a <slug>/index.md task is never seen by tasks) reproduced fixed against 5e10c355, the entities() rule matching Spacedock 0.27.0's discover rule (folder wins, sidecar folder without index.md and _archive, _mods and dot entries skipped), each new test shown failing under a mutation you run yourself, the diff from 5e10c355 confined to the files the report names, the kept steps and AC-8 to AC-12 and AC-14 to AC-18 unchanged, and AC-12's recount with the corrected script fo-lifecycle-mod/validation/recount-643-5e10c355.py from the state checkout (not implementation/recount.py, which under-counts the merge ask)
The acceptance script of validation cycle 7 updated to the new head, run by you exactly as written in a fresh bash shell, with its observed output
/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/scripts/adr_lint.py docs/adr --since <base> and /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/scripts/number_guards.py check run with their exit codes; verdict PASSED or REJECTED naming the head, with findings classified by the workflow's Review-finding disposition, including roborev:682 against the design's Limits; run no replay

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1

Profile: pilot. Candidate: iamcxa/kc-claude-plugins PR #643, branch spacedock-ensign/fo-lifecycle-mod, head 3a3cfc30 (the Codex round-7 repair on 5e10c355; Feedback Cycle 7 in the task file), base origin/main 0cdb40a7. Check out the head in a throwaway worktree (`git worktree add --detach /tmp/<name> 3a3cfc30`) and remove it when done. Read and run only: do not push, comment on any PR, request reviews, or edit the candidate or its worktree. A repair goes back through FO.

Captain amendments 1 to 5 are in the task file; ADR 0015 is in the PR. Run no replay. Keep the harness and fixtures outside the repository (a scratch directory under /tmp), never against a real workflow or the real learning store, with a stub gh first on PATH; record what the launch command was. If the launcher or a flag the design names does not exist (check with --help), say so and use the design's stated fallback, or stop and report.

Never run `git remote set-url` or any `git config` write in a worktree of this repository: worktrees share one config, including the Captain's main checkout. Use a throwaway `git clone` for that.

The minimal acceptance script must run unchanged in a fresh shell and name any checkout or install it needs; FO will run it exactly as written before the gate. Write any package script you name as its full path.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).

Run each test suite and mutation with a time cap, and remove every throwaway worktree you add before reporting.
