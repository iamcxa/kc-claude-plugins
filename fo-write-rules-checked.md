---
title: The four FO-write rules observers keep finding broken are checked when FO writes, not only stated in the README
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:fo-write-rules-checked:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:fo-write-rules-checked-backlog-1
              briefing:
                id: briefing:fo-write-rules-checked:backlog:attempt-1:revision-1
                digest: sha256:4279d2f5be06967ca9000823beac267a910ff56e06f6429b249cef9c387dd3e8
                room-ref: ./fo-write-rules-checked/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:fo-write-rules-checked:backlog:1
                briefing: briefing:fo-write-rules-checked:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-20T04:56:55.823864Z"
                decision: approve
                reason: Captain approved the five batch-4 backlog gates presented together in chat (「按你建議」), answering FO's question put before it (quoted in the gate question); this briefing binds that question and answer after the fact
              application:
                target-stage: ideation
                state: pending
---

## Scope

- Source: issue iamcxa/kc-claude-plugins#684 (filed 2026-10-20 at the Captain's 「同意」 from the batch-3 observer reports); batch 4 approved 2026-10-20 (「按你建議」).
- Bite, the four rules and where batch 3 broke them (observer reports in the archived tasks): a Captain ruling written before its question was put (delivery-gate-settles-skipped-checks); a two-part finding declined with one part's reason (chat-only-evidence-observer-blind, special-role-calls-fire-when-needed); a Captain scope change after a closed gate kept outside `## Captain amendments` (special-role-calls-fire-when-needed); a merge made on a gate whose recorded question did not name it (Release PR #672 on the #682 approval).
- Consumer: the Captain, whose authority these rules protect, and the observer.
- Upstream first: the FO-write checks from #671 (`dispatch_records.py`, `delivery_gate.py`, laws L2) and the special-role triggers from #682; extend them before adding any script.
- Batch overlap: comment-check-reaches-delivery-gate also edits `delivery_gate.py`; implement after it merges.
- Non-goals: to be set at ideation.

## FO alignment

Alignment: not needed before ideation; the Captain approved batch 4.
Release review: not needed: workflow maintenance, on no journey map.
Surfaces: none
Visible change: none
