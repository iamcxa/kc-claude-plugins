---
title: workflow budget ratchet follow-ups declined at validation of #658 (ledger delta edits, unpinned message tails, stale learning.md symbol)
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

Declined by FO at validation-1 of workflow-budget-ratchet (PR #658, head 57673bfd, 2026-10-17); reasons below, also in that task's gate summary.

- Deferred risk: `kc-dev-flow-2/scripts/lint-skills.py` checks the budget ledger against itself, not against base, so editing an existing step's `delta` raises the budget with no ruling (validator reproduced: +50 words and `-79` changed to `-29` prints `5482 of 5482 words`, exit 0). ADR 0020 names only the START edit. Decline reason: the edit is visible in the PR diff, like a START edit; closing it needs the lint to read base, a design change outside #658's file list.
- Polish: the tail of the fourth amendment message (`'no replacement'`) and the `with the same check` clause of the `resumed-dispatch` pin in `kc-dev-flow-2/scripts/test_sd_dispatch.py` are unpinned; the two comment lines added to `lint-skills.py` restate the code; the AC-4 and AC-7 literal greps are blind to README line wrapping.
- Stale symbol: root `learning.md` names `WORKFLOW_WORD_BUDGET` as an example; after #658 the names are `WORKFLOW_BUDGET_START` and `WORKFLOW_BUDGET_STEPS`. A learning.md edit goes through the learn loop or its own PR.
