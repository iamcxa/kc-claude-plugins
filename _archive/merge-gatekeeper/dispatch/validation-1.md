# validation-1

Dispatched: 9b58cd68be01ed360d664642bb3605838cd82c25 (workflow checkout, kc-dev-flow-2 0.24.0 README); batch 2
Candidate: 1beabd975bac782a14e8c9e98fa42bd80b333eaf
Model: sonnet

## Checklist

Independent verdict on PR #666 head 1beabd97 against every acceptance criterion in the task file, re-running each evidence command and at least one falsifier per criterion yourself, and judging each limit the implementation report states
first validation of a Production task. Run the prod validation security review as origin/main now defines it (#659 merged after the installed 0.24.0): dispatch kc-pr-flow:tob-security-reviewer once with model sonnet and the Reach brief from origin/main's kc-dev-flow-2/skills/validation/profiles/prod.md, save the report under the task folder as security/validation-1.yaml, and write the Security review (validation) and Security finding lines that profile requires; judge each finding. Also: AC-5 transcripts are under merge-gatekeeper/validation/ (ac5-run-2 is the final line form; the throwaway repository is left for the Captain to delete; do not touch it); AC-9 does not apply (no model arm, D1 b); the PR base is 2dad59ca and main is now 18e161d9, so also run kc-dev-flow-2/scripts/lint-skills.py and the package tests on a merge of the head into current origin/main; judge the implementer's listed deviations from the design; the ADR is ADR: 0023 and ADR 0011 gains one Status line
A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.24.0/scripts/adr_lint.py docs/adr --since <base> with its exit code; your verdict naming the head, with findings classified by the workflow's Review-finding disposition

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.24.0

Profile: pilot. Candidate: iamcxa/kc-claude-plugins PR #666, head 1beabd975bac782a14e8c9e98fa42bd80b333eaf, base origin/main. Batch-2 task; other batch-2 PRs are in flight and are not your candidate. Check out the head in a throwaway worktree (`git worktree add --detach /tmp/<name> 1beabd975bac782a14e8c9e98fa42bd80b333eaf`) and remove it when done. Read and run only: do not push, comment on any PR, request reviews, or edit the candidate or its worktree. A repair goes back through FO. Read adopter state only through read-only commands.

Run kc-dev-flow-2/scripts/lint-skills.py and any package script under test from the candidate checkout, not from the package root. kc-dev-flow-2/scripts/test_sd_dispatch.py needs --sd-plugin-root; name the root and binary you use.

Never run `git remote set-url` or any `git config` write in a worktree of this repository. Run each suite and mutation with a time cap, and remove every throwaway worktree you add before reporting. The minimal acceptance script must run unchanged in a fresh shell, name any checkout or install it needs and write any package script as its full path; FO will run it exactly as written before the gate.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
