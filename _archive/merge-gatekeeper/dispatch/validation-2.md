# validation-2

Dispatched: 9b58cd68be01ed360d664642bb3605838cd82c25 (workflow checkout, kc-dev-flow-2 0.24.0 README); batch 2
Candidate: 3fd841789db9c76d863ae4f723184c790471a7da
Model: sonnet

## Checklist

Independent verdict on PR #666 head 3fd84178 against every acceptance criterion in the task file, re-running each evidence command and at least one falsifier per criterion yourself, and judging each limit the implementation report states
recheck after Cycles 1 and 2: the three Codex P1 (review:5561577977) fixed (quoted prod read by the shared reader, instruction directories at any depth, trunk fetched inside check with fail-closed); the Captain's Cycle 2 ruling applied (a grant needs its Accepted ADR to contain the whole merge-grants entry; never list gains .githooks, .roborev.toml, repo-root scripts/, hooks/ and bin/ at any depth; docs-only only .md); confirm each new rule's test fails under its mutation; re-run the prod validation security review with the Reach brief from origin/main's kc-dev-flow-2/skills/validation/profiles/prod.md as security/validation-2.yaml and write its lines; AC-1 to AC-12 hold; run lint and package tests on a merge into current origin/main
A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.24.0/scripts/adr_lint.py docs/adr --since <base> with its exit code; your verdict naming the head, with findings classified by the workflow's Review-finding disposition

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.24.0

Profile: prod. Candidate: iamcxa/kc-claude-plugins PR #666, head 3fd841789db9c76d863ae4f723184c790471a7da, base origin/main. Batch-2 task; other batch-2 PRs are in flight and are not your candidate. Check out the head in a throwaway worktree (`git worktree add --detach /tmp/<name> 3fd841789db9c76d863ae4f723184c790471a7da`) and remove it when done. Read and run only: do not push, comment on any PR, request reviews, or edit the candidate or its worktree. A repair goes back through FO. Read adopter state only through read-only commands.

Run kc-dev-flow-2/scripts/lint-skills.py and any package script under test from the candidate checkout, not from the package root. kc-dev-flow-2/scripts/test_sd_dispatch.py needs --sd-plugin-root; name the root and binary you use.

Never run `git remote set-url` or any `git config` write in a worktree of this repository. Run each suite and mutation with a time cap, and remove every throwaway worktree you add before reporting. The minimal acceptance script must run unchanged in a fresh shell, name any checkout or install it needs and write any package script as its full path; FO will run it exactly as written before the gate.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
