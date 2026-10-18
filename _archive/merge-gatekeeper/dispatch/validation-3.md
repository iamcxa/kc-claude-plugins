# validation-3

Dispatched: 9b58cd68be01ed360d664642bb3605838cd82c25 (workflow checkout, kc-dev-flow-2 0.24.0 README); batch 2
Candidate: b97068de1d2f91bc8c9c3a9cbc67b59f75b2a048
Model: sonnet

## Checklist

Independent verdict on PR #666 head b97068de against every acceptance criterion in the task file, re-running each evidence command and at least one falsifier per criterion yourself, and judging each limit the implementation report states
recheck after Captain amendment 1 narrowed the PR to holds, points, class, never list and per-ask record (grant, merge-line, recheck, calibrate and fetch code removed, reachable at 3fd84178; ADR 0023 not landed, so adr_lint --require 0023 is not expected to pass; AC-4, AC-5, AC-7, AC-11 superseded with no replacement, AC-13 to AC-15 replace AC-3, AC-8, AC-12); confirm check never prints a merge line and never calls gh pr merge; judge roborev 855 (High: the documented check command omits --workflow-dir) by reproducing it or showing it false on a split-root task and a flat task; re-run the prod validation security review with the Reach brief from origin/main's kc-dev-flow-2/skills/validation/profiles/prod.md as security/validation-3.yaml and write its lines; run lint and package tests on a merge into current origin/main
A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.24.0/scripts/adr_lint.py docs/adr --since <base> with its exit code; your verdict naming the head, with findings classified by the workflow's Review-finding disposition

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.24.0

Profile: prod. Candidate: iamcxa/kc-claude-plugins PR #666, head b97068de1d2f91bc8c9c3a9cbc67b59f75b2a048, base origin/main. Batch-2 task; other batch-2 PRs are in flight and are not your candidate. Check out the head in a throwaway worktree (`git worktree add --detach /tmp/<name> b97068de1d2f91bc8c9c3a9cbc67b59f75b2a048`) and remove it when done. Read and run only: do not push, comment on any PR, request reviews, or edit the candidate or its worktree. A repair goes back through FO. Read adopter state only through read-only commands.

Run kc-dev-flow-2/scripts/lint-skills.py and any package script under test from the candidate checkout, not from the package root. kc-dev-flow-2/scripts/test_sd_dispatch.py needs --sd-plugin-root; name the root and binary you use.

Never run `git remote set-url` or any `git config` write in a worktree of this repository. Run each suite and mutation with a time cap, and remove every throwaway worktree you add before reporting. The minimal acceptance script must run unchanged in a fresh shell, name any checkout or install it needs and write any package script as its full path; FO will run it exactly as written before the gate.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
