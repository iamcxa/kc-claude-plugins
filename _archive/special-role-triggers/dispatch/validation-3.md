# validation-3

Dispatched: 9b58cd68be01ed360d664642bb3605838cd82c25 (workflow checkout, kc-dev-flow-2 0.24.0 README); batch 2
Candidate: b300d9ba6019a4f2c54d5657b1698338fa71164b
Model: sonnet

## Checklist

Independent verdict on PR #664 head b300d9ba against every acceptance criterion in the task file, re-running each evidence command and at least one falsifier per criterion yourself, and judging each limit the implementation report states
recheck after Cycle 2: Codex round-2 P2 (review:5558381167) fixed by normalizing every heading role_triggers.py matches (Captain amendments, Amendment N, Feedback Cycles, FO alignment, and section ends) for case, leading indent and no-break space, with SPACE copied and pinned to the GO_SPACE constant of kc-dev-flow-2/scripts/design_surfaces.py by test; confirm each matcher's mutation fails only its own test and output over the state task files is unchanged; AC-1 and AC-3 to AC-10 hold
A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.24.0/scripts/adr_lint.py docs/adr --since <base> with its exit code; your verdict naming the head, with findings classified by the workflow's Review-finding disposition

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.24.0

Profile: pilot. Candidate: iamcxa/kc-claude-plugins PR #664, head b300d9ba6019a4f2c54d5657b1698338fa71164b, base origin/main. Batch-2 task; other batch-2 PRs are in flight and are not your candidate. Check out the head in a throwaway worktree (`git worktree add --detach /tmp/<name> b300d9ba6019a4f2c54d5657b1698338fa71164b`) and remove it when done. Read and run only: do not push, comment on any PR, request reviews, or edit the candidate or its worktree. A repair goes back through FO. Read adopter state only through read-only commands.

Run kc-dev-flow-2/scripts/lint-skills.py and any package script under test from the candidate checkout, not from the package root. kc-dev-flow-2/scripts/test_sd_dispatch.py needs --sd-plugin-root; name the root and binary you use.

Never run `git remote set-url` or any `git config` write in a worktree of this repository. Run each suite and mutation with a time cap, and remove every throwaway worktree you add before reporting. The minimal acceptance script must run unchanged in a fresh shell, name any checkout or install it needs and write any package script as its full path; FO will run it exactly as written before the gate.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
