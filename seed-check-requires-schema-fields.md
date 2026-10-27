---
title: The seed check refuses a task missing its schema's required fields
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:seed-check-requires-schema-fields:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:seed-check-requires-schema-fields-backlog-1
              briefing:
                id: briefing:seed-check-requires-schema-fields:backlog:attempt-1:revision-1
                digest: sha256:dc63436ce0050258853ef8628ce43caff1e38886de1223d255cb4d35acb051bd
                room-ref: ./seed-check-requires-schema-fields/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:seed-check-requires-schema-fields:backlog:1
                briefing: briefing:seed-check-requires-schema-fields:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-27T15:13:15.991672Z"
                decision: approve
                reason: Captain 「全准」 (chat, 2026-10-27) answering 「需要你決定：第 8 批 7 張任務的待辦關卡，要不要一起批准進入設計階段？同時把已經做完的 `peers-paseo-host-binding` 關掉。我建議全部批准，也關掉那張。」; accepts FO's recommendation
              application:
                target-stage: ideation
                state: consumed
---

## Scope

- Source: the Captain 「同意開 1 到 5，第 6 項併進「GPT 夥伴」提案」 (chat, 2026-10-27), answering FO's list of package-issue candidates (items 2 to 5 relayed by the relay FO, Paseo 1671c3a9, from its pair-once and room-specs-follow-web-part-select observer reports; item 1 relayed by the kc-ops-inbox FO, Paseo 46c2ebdf).
- Bite: relay room-specs-follow-web-part-select had no budget, no stop condition and no `id:`, yet `design_surfaces.py check --seed` passed (relay FO's report).
- Upstream first: `scripts/design_surfaces.py` (`check --seed`), the workflow README schema, Spacedock `new`.

## FO alignment

Alignment: needed before ideation; where the check runs is a package design choice.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
Result: aligned 2026-10-27 on the outcome by the Captain's 「全准」 answering this task's backlog briefing-1 question, which named the seed check refusing a task missing its schema's required fields; which fields are required is put to him at the ideation gate.
