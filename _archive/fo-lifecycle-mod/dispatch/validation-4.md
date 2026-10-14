# validation-4

Dispatched: 656543f41b2f3d11717d418e6b5f6680d97964ff (workflow checkout, kc-dev-flow-2 0.22.1 README); candidate #643 5eb6bf05
Model: sonnet
Fresh validation recheck after the Codex round-3 repair; no replays (Captain amendment 5). Codex round 4 on this PR requested at dispatch.

## Checklist

Independent recheck of the cycle-3 repair on #643 head 5eb6bf05: the Codex round-3 P1 (merge-ask line printed while a listed reviewer is unsettled) and the missing-worktree risk (tasks exits 2 and skips the watch) reproduced fixed against 5b280387, the empty-pr absent-worktree record line present, each new test shown failing under a mutation you run yourself, AC-8 to AC-12, AC-14 to AC-18 re-run at the new head with any change from validation cycle 3 named, AC-12's recount at or under the design column at every moment, and whether AC-11(g) as written still holds or needs the qualifier "when no listed reviewer is unsettled"
The acceptance script of validation cycle 3 updated to the new head, run by you exactly as written in a fresh bash shell, with its observed output
/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/scripts/adr_lint.py docs/adr --since <base> and /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/scripts/number_guards.py check run at the new head with their exit codes; verdict PASSED or REJECTED naming the head, with findings classified by the workflow's Review-finding disposition; run no replay (Captain amendment 5)

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1

Profile: pilot. Candidate: iamcxa/kc-claude-plugins PR #643, branch spacedock-ensign/fo-lifecycle-mod, head 5eb6bf05 (repair of 5b280387 for the Codex round-3 P1 and the missing-worktree risk recorded under `### Feedback Cycles`, Cycle 3), base origin/main 0cdb40a7. Check out the head in a throwaway worktree (`git worktree add --detach /tmp/<name> 5eb6bf05`) and remove it when done. Read and run only: do not push, comment on any PR, request reviews, or edit the candidate or its worktree. A repair goes back through FO.

Captain amendments 1 to 5 are in the task file; ADR 0015 is in the PR. Run no replay. Keep the harness and fixtures outside the repository (a scratch directory under /tmp), never against a real workflow or the real learning store, with a stub gh first on PATH; record what the launch command was. If the launcher or a flag the design names does not exist (check with --help), say so and use the design's stated fallback, or stop and report.

Never run `git remote set-url` or any `git config` write in a worktree of this repository: worktrees share one config, including the Captain's main checkout. Use a throwaway `git clone` for that.

The minimal acceptance script must run unchanged in a fresh shell and name any checkout or install it needs; FO will run it exactly as written before the gate. Write any package script you name as its full path.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).

### Dispatch Retries

- 2026-10-14: the validator stopped at its first step with an API error (weekly usage limit for claude-sonnet-5-5, resets 2026-10-16 16:00 Asia/Taipei); no report was written. FO removed its two throwaway worktrees (/tmp/v643c4/new, /tmp/v643c4/old). Not retried pending the Captain.
