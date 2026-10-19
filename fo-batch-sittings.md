---
title: FO runs a batch of tasks in sittings, so the Captain answers each stage's gates for the whole batch at once
variant: kc-dev-flow-2
merge: pr
status: backlog
---

## Scope

- Source: the Captain, 2026-10-17: 「找一下 plugin FO 諮詢怎樣可以批次討論，批次實作，批次檢視的原則，這一段 dev2 還沒實裝，但是我需要你們按共同原則 dogfood 以便提高效率且降低我的負擔」. On 2026-10-20 he asked which task carries this and whether it is scheduled (「我想知道批次處理是哪張票？目前排了嗎」); none existed, so FO filed this one.
- Bite: nothing about batches is in kc-dev-flow-2 (`git grep -n -i batch origin/main -- kc-dev-flow-2/references kc-dev-flow-2/skills` to be rerun at ideation). FOs ran batches 2 and 3 of this workflow by interim rules kept outside the package. captain-question-load measured batch 2 at 22 Captain answers and 63 asks over six tasks; its AC-5 recount of batch 3 at batch close is the second measurement and the baseline for this task.
- Interim rules being dogfooded (FO's record, to be confirmed or dropped by measurement): gates stay per task, but all gates of one stage for the batch are presented in one message and each is recorded with his one answer; FO-side repairs, rechecks and external-review rounds run between sittings; every ideation has a `### Batch overlap` section; numbers are reserved before the batch's first dispatch; one follow-up task per delivered task for declined findings; a repeated finding class calls the chief-engineer.
- Consumer: the Captain, and every adopter FO that runs more than one task at a time (relay, web, qnow).
- Upstream first: Spacedock's own scheduling (`status --next`, `concurrency`, gate presentation) before adding package text; captain-question-load (archived, ADR 0023) and its batch-3 recount.
- Non-goals: to be set at ideation.

## FO alignment

Alignment: needed before ideation: whether to wait for captain-question-load's batch-3 recount (AC-5) before designing is the Captain's.
Release review: not needed: workflow maintenance, on no journey map.
Surfaces: none
Visible change: the Captain answers one message per stage per batch instead of one per gate.
