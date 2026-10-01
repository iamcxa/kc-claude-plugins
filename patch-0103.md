---
title: A revise at the validation gate goes back to implementation, not to the validation worker
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:patch-0103:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:patch-0103-backlog-1
              briefing:
                id: briefing:patch-0103:backlog:attempt-1:revision-1
                digest: sha256:2ae64f6340df422fc95a80ae1b1256978bc0253f8580b650090b8f3103e641d1
                room-ref: ./patch-0103/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:patch-0103:backlog:1
                briefing: briefing:patch-0103:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-01T03:05:30.733944Z"
                decision: approve
                reason: 'Captain 2026-10-01: 「修完再合併」 — fix the round-3 P1 before qnow #1248 merges'
              application:
                target-stage: ideation
                state: consumed
---

One wording defect in kc-dev-flow-2 0.10.2 `references/sd/workflow.md` `## Captain amendments`, found as a P1 in round 3 of an external review of an adopter's workflow sync (qnow PR #1248, commit 39bf550, 2026-10-01); patch release 0.10.3.

## Scope

Captain 2026-10-01: 「修完再合併」 — fix the round-3 P1 before #1248 merges; under the review-round rule the round-3 P2s become follow-ups (task `review-followups-0102`).
Finding: the paragraph says that when the Captain calls `revise` while a gate is open, "at a stage that dispatches a worker, that stage's worker reworks it". At the validation gate that names the validation worker, but the validation contract forbids that worker from taking over implementation and routes changes through feedback; the revise must go to the `feedback-to` target (implementation), the validation worker then re-reviews.
Non-goals: the round-3 P2s; any Spacedock change; other sections.

## Acceptance criteria

To be written at ideation.

## FO alignment

Needed at ideation: replacement wording that sends a revise at a feedback stage's gate to its `feedback-to` stage and keeps a revise at ideation with the ideation worker and at backlog with FO or the author; the asserted phrase and a falsifier holding the 0.10.2 text in `test_sd_dispatch.py`; whether ADR 0005 needs an amendment line.
Result: the FO delegates these questions to ideation, which decides each with its source and returns any ruling that needs the Captain.
Surfaces: none
Visible change: none
