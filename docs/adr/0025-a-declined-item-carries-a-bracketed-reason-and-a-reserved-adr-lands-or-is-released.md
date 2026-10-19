# 0025. A declined item carries a bracketed reason and a reserved ADR lands or is released before merge

Date: 2026-10-19

## Status

Accepted

## Context

Across six batch-2 observer reports, a decline in a gate summary had no reason in 4 of 6 tasks, and one delivery gate was presented while a reserved ADR had no file (merge-gatekeeper #666, ADR 0023). The observer found each days later at archive. Option A was chosen knowing it proves a bracket of two or more words, not that the words are a reason; the observer keeps judging reason quality.

## Decision

**Words:** 「照建議」 — Captain, 2026-10-19, chat, approving the four batch-3 ideation gates presented together, accepting each task's stated decisions. The fo-write-checks gate question named D1 (declined item form: Recommend A, `<class>, <finding> (<reason>)`, enforced as a hold at `delivery_gate.py check`) and D2 (a reserved ADR may not stay unlanded at merge: Recommend no, with K6 holding).

**Options considered:**
- D1 A: each declined item in the merge-ask text carries a bracket of two or more words, and `delivery_gate.py check` holds the ask without one (chosen); B bracket or `because`, C a dash form, D leave it to the observer — not chosen (C fails every legacy summary; D leaves reasons unseen until archive)
- D2 no parked form: a reserved `ADR: NNNN` with no `<adr-path>/NNNN-*.md` at the PR head holds the merge ask, and FO lands the file or deletes the `ADR:` line and notes the successor in the task (chosen); a written `parked` form K6 accepts — not chosen, it adds README words and a form K6 must read

**Recommended:** A and no parked form, as the Captain accepted.

## Consequences

FO rewrites a decline once when the check fires. A reasonless bracket such as `(none yet)` still passes. Deleting an `ADR:` line frees its number for the next `number_guards.py reserve` in this workflow, which cannot see a task in another workflow, so a collision stays possible until that successor lands. Later work that writes decline text or reserves an ADR number must follow these two rules. Reopen if the observer's next batch still finds reasonless declines behind brackets.
