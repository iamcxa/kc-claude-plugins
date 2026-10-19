# validation-1

Dispatched: c60e89e11ab37441a0dca1c2a0672da4ad223c3c (workflow checkout, kc-dev-flow-2 0.25.0 README); batch 3
Candidate: 7e47e8704573e163353a6a5ff80b0e79ea78eebc
Model: sonnet

## Checklist

Independent verdict on PR #670 head 7e47e870 against every acceptance criterion in the task file, re-running each evidence command and at least one falsifier per criterion yourself, and judging each limit the implementation report states
first validation; recount the words FO reads per moment with your own method (the worker's recount_fo_words.py is in the task folder); the --help pin was tightened to the rules list before Limits: (the one deviation from the design); AC-7 is the hand-off of the ADR-line check spec to fo-write-checks, which FO carries; the Reserve bullet must be byte-identical
A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.25.0/scripts/adr_lint.py docs/adr --since <base> with its exit code; your verdict naming the head, with findings classified by the workflow's Review-finding disposition

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.25.0

Profile: pilot. Candidate: iamcxa/kc-claude-plugins PR #670, head 7e47e8704573e163353a6a5ff80b0e79ea78eebc, base origin/main. Batch-3 task; other batch-3 PRs are in flight and are not your candidate. Check out the head in a throwaway worktree (`git worktree add --detach /tmp/<name> 7e47e8704573e163353a6a5ff80b0e79ea78eebc`) and remove it when done. Read and run only: do not push, comment on any PR, request reviews, or edit the candidate or its worktree. A repair goes back through FO. Read adopter state only through read-only commands.

Run kc-dev-flow-2/scripts/lint-skills.py and any package script under test from the candidate checkout, not from the package root. kc-dev-flow-2/scripts/test_sd_dispatch.py needs --sd-plugin-root; name the root and binary you use.

Never run `git remote set-url` or any `git config` write in a worktree of this repository. Run each suite and mutation with a time cap, and remove every throwaway worktree you add before reporting. The minimal acceptance script must run unchanged in a fresh shell, name any checkout or install it needs and write any package script as its full path; FO will run it exactly as written before the gate.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
