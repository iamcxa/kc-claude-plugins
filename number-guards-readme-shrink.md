---
title: The Number guards passage of the workflow README shrinks to what number_guards.py cannot tell its reader
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

Filed under D4 of workflow-budget-ratchet, approved by the Captain on 2026-10-17 (「那就照建議」 to the batch-2 ideation gates, whose question said approving accepts D4: "Number guards becomes a follow-up task").

## Scope

- Measured by workflow-budget-ratchet's ideation on 0.24.0: the Number guards passage of `kc-dev-flow-2/references/sd/workflow.md` is 745 words, 13.6% of the README, the largest single candidate for the ratchet's shrink rule; its script messages were not read there.
- Apply the ratchet's rule: read each `kc-dev-flow-2/scripts/number_guards.py` failure message first; a rule the script enforces and whose message tells the reader what to do shrinks to one pointer sentence; the budget falls by the words removed in the same change.
- Bite to confirm at ideation: the observer's count of number-guard violations (an ADR number reserved after the first implementation dispatch happened twice, on prod-security-review-gates 2026-10-16/17).
