# validation-6

Dispatched: 656543f41b2f3d11717d418e6b5f6680d97964ff (workflow checkout, kc-dev-flow-2 0.22.1 README); candidate #643 eb643a18
Model: sonnet
Fresh recheck covering the repairs since validation cycle 3; no replays (Captain amendment 5). roborev:676 and :678 (no adopter mod copies) are the post-release sync. Codex round 6 on this PR requested at dispatch.

## Checklist

Independent recheck of the repairs on #643 head eb643a18 since validation cycle 3 (5b280387): Codex round 3 P1 (merge-ask line while a listed reviewer is unsettled), the missing-worktree risk, Codex round 4 P1 (no check runs) and Codex round 5 P1 (findings counted as settled once a wait reported them; the merge-ask line now prints only when every listed reviewer passes, Copilot answered is always the review-step line), each reproduced fixed against the head before its repair, each new test shown failing under a mutation you run yourself, AC-8 to AC-12 and AC-14 to AC-18 re-run at the new head with any change from validation cycle 3 named, AC-12's recount at or under the design column at every moment, and whether AC-11(g) as written still holds or needs the qualifier "when every listed reviewer passes"
The acceptance script of validation cycle 3 updated to the new head, run by you exactly as written in a fresh bash shell, with its observed output
/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/scripts/adr_lint.py docs/adr --since <base> and /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/scripts/number_guards.py check run at the new head with their exit codes; verdict PASSED or REJECTED naming the head, with findings classified by the workflow's Review-finding disposition; run no replay (Captain amendment 5)

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1

Profile: pilot. Candidate: iamcxa/kc-claude-plugins PR #643, branch spacedock-ensign/fo-lifecycle-mod, head eb643a18 (repairs of 5b280387 for the Codex round-3, round-4 and round-5 P1 findings and the missing-worktree risk recorded under `### Feedback Cycles`, Cycles 3 to 5), base origin/main 0cdb40a7. Check out the head in a throwaway worktree (`git worktree add --detach /tmp/<name> eb643a18`) and remove it when done. Read and run only: do not push, comment on any PR, request reviews, or edit the candidate or its worktree. A repair goes back through FO.

Captain amendments 1 to 5 are in the task file; ADR 0015 is in the PR. Run no replay. Keep the harness and fixtures outside the repository (a scratch directory under /tmp), never against a real workflow or the real learning store, with a stub gh first on PATH; record what the launch command was. If the launcher or a flag the design names does not exist (check with --help), say so and use the design's stated fallback, or stop and report.

Never run `git remote set-url` or any `git config` write in a worktree of this repository: worktrees share one config, including the Captain's main checkout. Use a throwaway `git clone` for that.

The minimal acceptance script must run unchanged in a fresh shell and name any checkout or install it needs; FO will run it exactly as written before the gate. Write any package script you name as its full path.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).

Run each test suite and mutation with a time cap, and remove every throwaway worktree you add before reporting.
