---
title: A superseded criterion with no later dispatch is still caught
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: validation of fo-written-lines-checked-before-dispatch (PR iamcxa/kc-claude-plugins#724, head b0b2cbf3), finding F4, Deferred risk: an amendment followed by no later dispatch can leave superseded criteria declared without a `design_surfaces.py` error. That PR makes a superseded criterion wait in place until a dispatch checklist names its amendment; if no dispatch follows, nothing names it.
- Observed: not observed in any task (validation, 2026-10-26).
- Bite: none yet; file only so the gap is not lost. Reopen when a task archives with a superseded criterion still declared.

- Added 2026-10-29: the Captain 「那就a吧」 (chat) chose FO's batch-10 theme, whose row listed 「被取代的驗收條件漏抓」. Batch 9 showed no archived task with a superseded criterion still declared; engineering-reviewer found criteria carrying withdrawn content that were never listed under Supersedes (a different gap, under captain-amendment-form-checked).

## Non-goals

- Criteria never listed under Supersedes (captain-amendment-form-checked owns that).

## Budget

- One package PR inside `scripts/design_surfaces.py`; no new script.

## Stop condition

- A replayed task that archives with a superseded criterion still declared and no later dispatch is refused; return to the Captain if no real task shows the gap.
## FO alignment

Alignment: needed before ideation; no bite yet.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
