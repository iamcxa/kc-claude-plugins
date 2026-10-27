# implementation-5

Dispatched: 8bf4f3582411e8e4238f19fbadda8ddeca6767be (workflow checkout, kc-dev-flow-2 0.32.0 README); batch 8, resumed worker; the Captain's 「全准」 (chat, 2026-10-28) to FO's batch-8 sitting item 「**四、#738 必要欄位：從 #737 拆開**」
Model: gpt-6.1-sol (Codex via Paseo, thinking high; the Captain's interim dispatch directive, chat 2026-10-26: 「接下來派工結束後新的派工盡量用 sol / astra，推理等級可以比 claude 高一級」)

## Checklist

Decouple from #737: `git fetch origin`, create branch spacedock-ensign/seed-check-requires-schema-fields-main from origin/main (now including #734, #735 and #736), cherry-pick only this task's own commits (those on spacedock-ensign/seed-check-requires-schema-fields after 207c0a7e, ending at e31e3022), resolving any conflict without changing behaviour; leave the old branch untouched
Run every kc-dev-flow-2 test file and kc-dev-flow-2/scripts/lint-skills.py, /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.32.0/scripts/adr_lint.py docs/adr --since <origin/main> --require 0041 and /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.32.0/scripts/number_guards.py check on the new branch; push it with an explicit remote and branch name, no force, no -u; write the PR title and body (same as #738's, saying it replaces #738 and is no longer stacked) to /tmp/impl-seed-check-requires-schema-fields-main-pr.md; append a complete new `## Stage Report: implementation` ending in a superseding `### Summary` naming the new head, committed with `spacedock state commit seed-check-requires-schema-fields --workflow-dir /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2`

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.32.0

Number guards: ADR: 0041

Profile: pilot. Task seed-check-requires-schema-fields. FO opens the new Draft PR, closes #738 with the Captain's approval, runs RoboRev, reads CI and routes a revalidation. No change beyond the cherry-pick and conflict resolution. Your sandbox reaches neither the GitHub API nor the RoboRev daemon; do not run gh. Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not comment on any PR.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
