# batch-0a557023cc36 — ship-flow batch 2: dispatch dev entities; adopter portability

Plan receipt 0a557023cc36cc41 (session plan-flow-session-2026-09-09b-shipflow-batch2); approval go · 15 workspaces · concurrency 1 · repair 2 · Pilot (Captain 「approve」 2026-09-09).
Order: DEV-156 → DEV-151 → DEV-152 (#399, pre-built, enters at accepted) → DEV-153 → DEV-154 → DEV-155. Repo iamcxa/kc-claude-plugins, base main. Workers push branches; the FO opens PRs (open-pr.sh, body per pr-merge until DEV-151 lands). Captain merges by hand.

## Decision log

- 2026-09-09T14:05:31Z — batch opened.
- 2026-09-09 — DEV-156 accepted by the installed station at 04b896da; PR #401 opened by open-pr.sh, body per pr-merge template. Review dispatched. Premise gap recorded: dispatch build flag mode needs --checklist-file; the station writes a one-line procedural checklist.
- 2026-09-09 — DEV-152: the Captain merged #399 directly (main 39cb179b) before its accept/review stations ran here; recorded as merged with stations skipped (Captain's prerogative). DEV-152 Done.
