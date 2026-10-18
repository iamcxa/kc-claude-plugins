# validation-4

Dispatched: 9b58cd68be01ed360d664642bb3605838cd82c25 (workflow checkout, kc-dev-flow-2 0.24.0 README); batch 2
Candidate: ab8b675169a8a76f0a3dd97f11a651de3cdcf9f5
Model: sonnet

## Checklist

Independent verdict on PR #663 head ab8b6751 against every acceptance criterion in the task file, re-running each evidence command and at least one falsifier per criterion yourself, and judging each limit the implementation report states
recheck after Cycle 3: the FO alignment lines and the design-review Preview: candidates are read from unfenced text in check_task (chief-engineer ruling, then roborev 830 High); check_ui and check_db unchanged; confirm each new test fails under its mutation; rerun the main-vs-candidate comparison over the four corpora (this state, subspace-web, subspace-relay, qnow; scripts under /tmp/ce663/) and confirm the only changes are relay's _archive/multi-document-room-picker.md (two real Surfaces lines) and review-ui-room-asks-through-shell.md (no Design review: line), both already ruled; AC-1 to AC-8 hold; the ADR is ADR: 0022
A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.24.0/scripts/adr_lint.py docs/adr --since <base> with its exit code; your verdict naming the head, with findings classified by the workflow's Review-finding disposition

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.24.0

Profile: pilot. Candidate: iamcxa/kc-claude-plugins PR #663, head ab8b675169a8a76f0a3dd97f11a651de3cdcf9f5, base origin/main. Batch-2 task; other batch-2 PRs are in flight and are not your candidate. Check out the head in a throwaway worktree (`git worktree add --detach /tmp/<name> ab8b675169a8a76f0a3dd97f11a651de3cdcf9f5`) and remove it when done. Read and run only: do not push, comment on any PR, request reviews, or edit the candidate or its worktree. A repair goes back through FO. Read adopter state only through read-only commands.

Run kc-dev-flow-2/scripts/lint-skills.py and any package script under test from the candidate checkout, not from the package root. kc-dev-flow-2/scripts/test_sd_dispatch.py needs --sd-plugin-root; name the root and binary you use.

Never run `git remote set-url` or any `git config` write in a worktree of this repository. Run each suite and mutation with a time cap, and remove every throwaway worktree you add before reporting. The minimal acceptance script must run unchanged in a fresh shell, name any checkout or install it needs and write any package script as its full path; FO will run it exactly as written before the gate.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
