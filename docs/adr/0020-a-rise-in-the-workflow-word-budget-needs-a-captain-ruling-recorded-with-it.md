# 0020. A rise in the workflow word budget needs a Captain ruling recorded with it

Date: 2026-10-17

## Status

Accepted

## Context

`kc-dev-flow-2/scripts/lint-skills.py` refused the workflow README only above its budget, so a cut left slack for the next addition. Measured 2026-10-17: 24 commits changed the budget between 2026-10-09 and 2026-10-15 (21 raises, 2 cuts; 4420 to 5511 words), and the README stood at 5495 words against 5511. The README is read whole at startup and resume.

## Decision

**Words:** 「文件不應該一直變長，除非可以證明文件內容不是一次性載入，這裡的意義是文件如果一次載入太長，那 llm 的注意力八成會失焦」 — Captain, 2026-10-17, chat; he approved the recommendations of this task's ideation gate with 「那就照建議」 (2026-10-17, gate)

**Options considered:**
- the budget is a start value plus recorded steps and the README count must equal it; a raise step carries the Captain's quoted words and the one moment FO reads the added text, checked for presence only (chosen)
- keep the at-most comparison and ask reviewers to lower the number after a cut — not chosen: it banked 79 words of slack within one review
- a budget per section — not chosen: no measured section limit was proposed

**Recommended:** the first option, as the Captain accepted.

`lint-skills.py` refuses a README whose word count differs from `WORKFLOW_BUDGET_START` plus the `delta` of every entry of `WORKFLOW_BUDGET_STEPS`, in either direction, and names the step to add. A step with a positive `delta` needs a `captain` value holding a 「…」 quote and a `loaded` value naming the moment FO reads the added text; every step needs a `why`.

## Consequences

A cut lowers the budget in the same change, and a raise cannot merge without a quoted ruling. The script checks form and arithmetic: it cannot tell that a quote is the Captain's or that `loaded` is true, and an author who edits `WORKFLOW_BUDGET_START` evades it, so validation compares each quote with the gate record. Two pull requests that both edit the README conflict on the steps and the later one recounts. Reopen if a raise lands whose quote is not the Captain's.
