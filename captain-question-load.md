---
title: The Captain answers fewer FO questions per delivered task, without losing a decision that is his
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:captain-question-load:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:captain-question-load-backlog-1
              briefing:
                id: briefing:captain-question-load:backlog:attempt-1:revision-1
                digest: sha256:f5df5bbb224d836196b8fe7f7d580cb661bba02b1564603d5073b4fef3eb9bdc
                room-ref: ./captain-question-load/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:captain-question-load:backlog:1
                briefing: briefing:captain-question-load:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-18T16:56:58.283398Z"
                decision: approve
                reason: Captain approved in chat (「批准這些作為第三批」) the five batch-3 backlog gates presented together, accepting the recommended profiles and the stated grouping and order
              application:
                target-stage: ideation
                state: pending
---

Filed for batch 3 on the Captain's 「先走批次三規劃」 (chat, 2026-10-19), after FO reported that most of his turns in batch 2 were answering FO's questions rather than reviewing PRs. His goal for batching (chat, 2026-10-16): 「這樣我才可以從一直在追每個 FO 過程中解放出來」.

## Scope

- Measure first, from the batch-2 decision ledger rows and the gate briefings of this workflow (2026-10-17 to 10-19): every Captain decision per task, split into stage gates, Needs decisions, amendments, merge asks, and procedural asks (a push the permission check refused, a throwaway repository, a PR-body edit, a waiver), and how many he answered with a plain approval of FO's recommendation.
- Then find which kinds a written standing rule could settle without him (for example a delivery gate that carries the merge grant by default, or a repair inside an approved design), and which must stay his (ADR 0011: authority, approval, merge, outward-facing actions, irreversible changes and money).
- Existing pieces: batch sittings (memory note fo-batch-sittings-interim), pre-authorized merges at delivery gates, the qnow R11 batching numbers the qnow FO owes.
- Non-goals: to be set at ideation.

## FO alignment

Alignment: not needed before ideation; the Captain approved planning batch 3.
Release review: not needed: workflow maintenance, on no journey map.
Surfaces: none
Visible change: none
