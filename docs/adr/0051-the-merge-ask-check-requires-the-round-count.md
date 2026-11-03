# 0051. The merge-ask check requires the round count

Date: 2026-11-02

## Status

Accepted

## Context

Four batch 11 validation briefings omitted the external review round count.
The merge-ask check accepted their supplied question and summary, although
the separate-summary question check refused them. The task
validation-gate-requires-the-question-check records the seven-briefing replay
at state commit 99e8bb36 and the absence of a package hook at gate binding.
In six attempts the check ran 3 to 24 seconds before binding, the nearest
observed moment available to this package.

## Decision

**Words:** 「可以」 — Captain, chat, 2026-11-02, ideation revise;
「照建議」 — Captain, chat, 2026-11-02, revised ideation approval.

**Asked:** The revise answered
「決定：多開「完成通知」和「挑剔使用者可用 Gemini」兩張票，先前五件事照建議，可以嗎？」
and accepted D1: the text check at `check` is enough for now. The approval
answered 「決定：五張設計進實作、Gemini 這張停在這裡，四個決定都照建議嗎？要改哪件直接說。」
The task's ideation gate records retain both answers and their context.

**Options considered:**
- Require the round-count line in the text supplied to `check` (chosen).
- Hold this change for a host-hook trial at binding (deferred; unproven here).
- Check at idle or on state push (too late for the observed binding sequence).
- Record a receipt that `question` ran (proves execution, not the bound text).

**Recommended:** Require the round-count line at `check` now, with a separate
host-hook trial for binding, as D1 accepted.

**Protects:**
- `kc-dev-flow-2/scripts/delivery_gate.py` — round-count check before emitting problems in check

`check` applies the existing `summary_round_problems` rule to the supplied gate
text outside fences. It holds the ask without saving a merge record when the
text lacks exactly one top-level `External rounds: N` line in the existing
nonnegative count form. Zero and the count-with-detail forms remain valid.
This amends ADR 0044's statement that merge checks stay as before; its
optional summary input and legacy `question` behavior remain unchanged.

## Consequences

FO must add the count to previously accepted merge-ask text without it.
Presence and form do not establish truthful counts or actual review activity.
The check reads supplied text, not the bound briefing, and forces neither its
own execution nor its order: skipping it or binding first is not refused.
If the Captain already answered in chat, a later hold corrects the text to
bind, not what he read. Approval and merge authority remain unchanged.
The workflow and its word budget gain no words; a missing-count hold adds
the problem and one next-step line. Reopen when a binding hook is proven or
this nearest-moment check no longer covers the observed sequence.
