# validation-3

Dispatched: 1383c9119eb5328543e2c4df5e562be22b74e355 (workflow checkout, kc-dev-flow-2 0.23.0 README); batch 1
Candidate: d64cf1995ba24a2fd2efcc2fa9a4dee7031f4d5a
Model: sonnet

## Checklist

Independent verdict on PR #651 head d64cf199 against every acceptance criterion in the task file, re-running each evidence command and at least one falsifier per criterion yourself, and judging each limit the implementation report states
Recheck after the Cycle 1, roborev and Cycle 2 repairs: confirm validation F1 and F2, the delete-and-re-add High and the deleted-task P1 (under ### Feedback Cycles) are fixed at this head, each test failing under a mutation you run, and try one more way later history could change a law's result that the property test does not cover; re-run AC-4 and AC-6 on real history and state the counts the Captain is asked to amend to; AC-8's failed-run notice reaching the Captain is his to state
A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.23.0/scripts/adr_lint.py docs/adr --since <base> with its exit code; your verdict naming the head, with findings classified by the workflow's Review-finding disposition

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.23.0

Profile: pilot. Candidate: iamcxa/kc-claude-plugins PR #651, head d64cf1995ba24a2fd2efcc2fa9a4dee7031f4d5a, base origin/main. Batch-1 task; other batch-1 PRs are in flight and are not your candidate. Check out the head in a throwaway worktree (`git worktree add --detach /tmp/<name> d64cf1995ba24a2fd2efcc2fa9a4dee7031f4d5a`) and remove it when done. Read and run only: do not push, comment on any PR, request reviews, or edit the candidate or its worktree. A repair goes back through FO. Read adopter state only through read-only commands.

Run kc-dev-flow-2/scripts/lint-skills.py and any package script under test from the candidate checkout, not from the package root. kc-dev-flow-2/scripts/test_sd_dispatch.py needs --sd-plugin-root; name the root and binary you use.

Never run `git remote set-url` or any `git config` write in a worktree of this repository. Run each suite and mutation with a time cap, and remove every throwaway worktree you add before reporting. The minimal acceptance script must run unchanged in a fresh shell, name any checkout or install it needs and write any package script as its full path; FO will run it exactly as written before the gate.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
