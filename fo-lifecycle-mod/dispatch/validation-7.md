# validation-7

Dispatched: 656543f41b2f3d11717d418e6b5f6680d97964ff (workflow checkout, kc-dev-flow-2 0.22.1 README); candidate #643 5e10c355
Model: sonnet
Validation after Captain amendment 6; no replays. roborev:679 (no adopter mod copies) is the post-release sync. Codex round 7 on this PR requested at dispatch.

## Checklist

Independent verdict on #643 head 5e10c355 after Captain amendment 6 (the script reports facts and keeps the validated steps; the merge-ask decision returns to the README with /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/scripts/delivery_gate.py): confirm no merge-ask or hold line remains in kc-dev-flow-2/scripts/pr_watch.py output, the kept steps (record a PR or remind to record it, keep one wait, observer before the sentinel, learn after the archive, mark ready on a green or settled-unchecked draft, the no-CI settle with its BLOCKED guard) each work with a falsifier you run yourself, the restored README rule, AC-8 to AC-12 and AC-14 to AC-18 as amended, AC-12's recount from the shipped text (every moment at or under today's count), and whether the Codex round-6 P1 (reviewer applicability) is moot under amendment 6
A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output
/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/scripts/adr_lint.py docs/adr --since <base> and /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1/scripts/number_guards.py check run with their exit codes; verdict PASSED or REJECTED naming the head, with findings classified by the workflow's Review-finding disposition; run no replay

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.22.1

Profile: pilot. Candidate: iamcxa/kc-claude-plugins PR #643, branch spacedock-ensign/fo-lifecycle-mod, head 5e10c355 (Captain amendment 6 applied on eb643a18; Feedback Cycles 3 to 6 in the task file), base origin/main 0cdb40a7. Check out the head in a throwaway worktree (`git worktree add --detach /tmp/<name> 5e10c355`) and remove it when done. Read and run only: do not push, comment on any PR, request reviews, or edit the candidate or its worktree. A repair goes back through FO.

Captain amendments 1 to 5 are in the task file; ADR 0015 is in the PR. Run no replay. Keep the harness and fixtures outside the repository (a scratch directory under /tmp), never against a real workflow or the real learning store, with a stub gh first on PATH; record what the launch command was. If the launcher or a flag the design names does not exist (check with --help), say so and use the design's stated fallback, or stop and report.

Never run `git remote set-url` or any `git config` write in a worktree of this repository: worktrees share one config, including the Captain's main checkout. Use a throwaway `git clone` for that.

The minimal acceptance script must run unchanged in a fresh shell and name any checkout or install it needs; FO will run it exactly as written before the gate. Write any package script you name as its full path.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).

Run each test suite and mutation with a time cap, and remove every throwaway worktree you add before reporting.
