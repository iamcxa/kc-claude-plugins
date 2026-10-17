# validation-1

Dispatched: 19fe3b5b3d34d54908d288860909d10db1ae9226 (workflow checkout, kc-dev-flow-2 0.24.0 README); batch 2
Candidate: fce79ed7bd8a1ed8b8684ba2a1be25e0aefc671c
Model: sonnet

## Checklist

Independent verdict on PR #659 head fce79ed7 against every acceptance criterion in the task file, re-running each evidence command and at least one falsifier per criterion yourself, and judging each limit the implementation report states
first validation; confirm the three automated security-review items (frontmatter fail-closed, duplicate Security finding lines refused, review bound to the candidate equal to the PR head) each have a failing-first test and a mutation; AC-2 re-run of the shipped wording on relay #347 within the stop rule; the added CI step and its per-PR cost; do not run Opus or Fable
A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.24.0/scripts/adr_lint.py docs/adr --since <base> with its exit code; your verdict naming the head, with findings classified by the workflow's Review-finding disposition

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.24.0

Profile: pilot. Candidate: iamcxa/kc-claude-plugins PR #659, head fce79ed7bd8a1ed8b8684ba2a1be25e0aefc671c, base origin/main. Batch-2 task; other batch-2 PRs are in flight and are not your candidate. Check out the head in a throwaway worktree (`git worktree add --detach /tmp/<name> fce79ed7bd8a1ed8b8684ba2a1be25e0aefc671c`) and remove it when done. Read and run only: do not push, comment on any PR, request reviews, or edit the candidate or its worktree. A repair goes back through FO. Read adopter state only through read-only commands.

Run kc-dev-flow-2/scripts/lint-skills.py and any package script under test from the candidate checkout, not from the package root. kc-dev-flow-2/scripts/test_sd_dispatch.py needs --sd-plugin-root; name the root and binary you use.

Never run `git remote set-url` or any `git config` write in a worktree of this repository. Run each suite and mutation with a time cap, and remove every throwaway worktree you add before reporting. The minimal acceptance script must run unchanged in a fresh shell, name any checkout or install it needs and write any package script as its full path; FO will run it exactly as written before the gate.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
