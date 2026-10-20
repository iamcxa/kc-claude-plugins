---
title: FO runs a batch of tasks in sittings, so the Captain answers each stage's gates for the whole batch at once
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:fo-batch-sittings:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:fo-batch-sittings-backlog-1
              briefing:
                id: briefing:fo-batch-sittings:backlog:attempt-1:revision-1
                digest: sha256:784c5e9786f17002565ff351e677fc6736db43128c3fa2320facf8d4fe332cef
                room-ref: ./fo-batch-sittings/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:fo-batch-sittings:backlog:1
                briefing: briefing:fo-batch-sittings:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-20T04:57:05.128735Z"
                decision: approve
                reason: Captain approved the five batch-4 backlog gates presented together in chat (「按你建議」), answering FO's question put before it (quoted in the gate question); this briefing binds that question and answer after the fact
              application:
                target-stage: ideation
                state: consumed
started: 2026-10-20T04:57:55Z
---

## Scope

- Source: the Captain, 2026-10-17: 「找一下 plugin FO 諮詢怎樣可以批次討論，批次實作，批次檢視的原則，這一段 dev2 還沒實裝，但是我需要你們按共同原則 dogfood 以便提高效率且降低我的負擔」. On 2026-10-20 he asked which task carries this and whether it is scheduled (「我想知道批次處理是哪張票？目前排了嗎」); none existed, so FO filed this one.
- Bite: nothing about batches is in kc-dev-flow-2 (`git grep -n -i batch origin/main -- kc-dev-flow-2/references kc-dev-flow-2/skills` to be rerun at ideation). FOs ran batches 2 and 3 of this workflow by interim rules kept outside the package. captain-question-load measured batch 2 at 22 Captain answers and 63 asks over six tasks; its AC-5 recount of batch 3 at batch close is the second measurement and the baseline for this task.
- Interim rules being dogfooded (FO's record, to be confirmed or dropped by measurement): gates stay per task, but all gates of one stage for the batch are presented in one message and each is recorded with his one answer; FO-side repairs, rechecks and external-review rounds run between sittings; every ideation has a `### Batch overlap` section; numbers are reserved before the batch's first dispatch; one follow-up task per delivered task for declined findings; a repeated finding class calls the chief-engineer.
- Captain's scope addition, 2026-10-20: 「此外這個模式，先列出清單再一題題問應該也要收納到dev2中，再下下版，未來的就是等sd review做到持續性continuity 時要整合進去，可以用webui進行討論」. The sitting pattern FO used for batch 3's leftovers (list every open item first, then ask them one at a time) belongs in this task, targeted two releases out; later, when Spacedock review gains continuity, it integrates there and can be discussed in a web UI.
- Conflict to settle here (Captain agreed 2026-10-20, 「同意」 to FO's item 4): the interim rule "reserve every ADR or migration number before the batch's first dispatch" contradicts the README's Number guards rule "when the implementation dispatch is built and not earlier"; observers flagged it on captain-question-load (7.5 h early) and chat-only-evidence-observer-blind (13 h early).
- Consumer: the Captain, and every adopter FO that runs more than one task at a time (relay, web, qnow).
- Upstream first: Spacedock's own scheduling (`status --next`, `concurrency`, gate presentation) before adding package text; captain-question-load (archived, ADR 0023) and its batch-3 recount.
- Non-goals: to be set at ideation.

## FO alignment

Alignment: needed before ideation. The Captain ruled to wait (「可以等批次 3 的那次計數出來再開始設計。目前多個 FO 都做了這個 dogfood，你可以派觀察者回收一下。」, 2026-10-20, chat, answering FO's 「要不要等批次 3 的那次計數出來再開始設計？我建議等。」): ideation starts after captain-question-load's batch-3 recount, and observers first collect the dogfood record of the FOs that ran batches (kc-claude-plugins, subspace-relay, subspace-web, qnow).
Release review: not needed: workflow maintenance, on no journey map.
Surfaces: none
Visible change: the Captain answers one message per stage per batch instead of one per gate.
