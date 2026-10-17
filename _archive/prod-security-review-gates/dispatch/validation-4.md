# validation-4

Dispatched: 1383c9119eb5328543e2c4df5e562be22b74e355 (workflow checkout, kc-dev-flow-2 0.23.0 README); batch 1
Candidate: 44f77c1b357f01deb965f983329e0f894be887ba
Model: sonnet

## Checklist

Independent verdict on PR #656 head 44f77c1b against every acceptance criterion in the task file, re-running each evidence command and at least one falsifier per criterion yourself, and judging each limit the implementation report states
recheck after Cycle 3: Codex round-3 P1 (review:5555969981, validation-3 F1) fixed in check_security by resolving the task folder as path.parent for index.md and path.parent/path.stem for a flat task; rerun validation-3 acceptance step 4 for the folder form; confirm the new folder-form test fails under its mutation; shape-lock rules and Cycle 1 P1 still fixed; AC-8 to AC-14 under amendment 2; F2 to F4 are declined to backlog task prod-security-check-round3-followups and need no recheck
A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.23.0/scripts/adr_lint.py docs/adr --since <base> with its exit code; your verdict naming the head, with findings classified by the workflow's Review-finding disposition

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.23.0

Profile: pilot. Candidate: iamcxa/kc-claude-plugins PR #656, head 44f77c1b357f01deb965f983329e0f894be887ba, base origin/main. Batch-1 task; other batch-1 PRs are in flight and are not your candidate. Check out the head in a throwaway worktree (`git worktree add --detach /tmp/<name> 44f77c1b357f01deb965f983329e0f894be887ba`) and remove it when done. Read and run only: do not push, comment on any PR, request reviews, or edit the candidate or its worktree. A repair goes back through FO. Read adopter state only through read-only commands.

Run kc-dev-flow-2/scripts/lint-skills.py and any package script under test from the candidate checkout, not from the package root. kc-dev-flow-2/scripts/test_sd_dispatch.py needs --sd-plugin-root; name the root and binary you use.

Never run `git remote set-url` or any `git config` write in a worktree of this repository. Run each suite and mutation with a time cap, and remove every throwaway worktree you add before reporting. The minimal acceptance script must run unchanged in a fresh shell, name any checkout or install it needs and write any package script as its full path; FO will run it exactly as written before the gate.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
