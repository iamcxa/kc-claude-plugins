# ideation-2

Dispatched: c27e76590c1d2dc910e7fa2d332242a7534df0b0 (workflow checkout, kc-dev-flow-2 0.27.0 README); batch 5 addition
Model: sonnet

## Checklist

Cycle 2 redesign per the Captain ruling 「重做檢查」 under FO alignment and the chief-engineer advice (Reviewer line, 2026-10-23): the check reads the dispatched task's own record in kc-dev-flow-2/scripts/pr_watch.py tasks beside seeds(): a signal 1 or 2 mark in its ## FO alignment with no later documented Release review line holds the first implementation dispatch; the primary fixture is the R4 record shape (qnow commit 51a251347: journey only, prose Release line, Signal 1, no review line, expected hold); remove the map-diff stale mode, review_stale.py, the journey-map PR and their criteria; choose between a regex over the five mark forms found in qnow and a pinned format in workflow.md (with its word cost under ADR 0020), as a decision for the Captain with a recommendation and what gets worse; keep the workflow.md Release review bullet and the FIXES regexes of kc-dev-flow-2/scripts/test_sd_dispatch.py consistent; count the live adopter tasks the hold would stop and name any false hold
A `### Batch overlap` section naming each file the design would change and each other batch task (new-work-starts-from-a-story-map, codex-reader-reads-receipt-marker, merge-ask-holds-missing-clauses, fo-write-checks-parse-top-level, idle-names-failing-seeds, agent-reads-governing-adr) and live task of other sessions (kc-decision-log-p1, kc-decision-log-cli, kc-decision-log-handoff-trial, pr-review-lite-value-pilot, release-acceptance, journey-canvas-hosted-poc, journey-server-host-pilot (driven by other sessions; read only)) that changes the same file or check, so FO can order implementation
The words FO reads at each lifecycle moment, before and after, per root learning.md "Measure the words FO reads at each moment, not one file's size"
Acceptance criteria with reproducible evidence clauses and falsifiers, and unresolved decisions for the Captain, each with a recommendation and what gets worse under it

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0

Profile: pilot. The Captain's words and the evidence are in the task file. This task is one of batch 5 addition; read the other task files only as they stand, and do not edit them. Design against the current package source: kc-dev-flow-2/ in iamcxa/kc-claude-plugins at origin/main, released as 0.28.0 (read with `git -C /Users/kent/conductor/workspaces/kc-claude-plugins/colombo show origin/main:<path>` after `git fetch origin`). Check the chain first (Spacedock, then kc-dev-flow-2, then sibling adopters) and say what you found; for a third-party mechanism read its own docs or source, not an adopter's workaround.

Ideation writes no repository file, branch or commit; the design and criteria go in the task file. Do not comment on any PR or issue, and do not message any other session. Never run `git remote set-url` or any `git config` write in a worktree of this repository. Read adopter state (relay, web, qnow) only through read-only commands.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
