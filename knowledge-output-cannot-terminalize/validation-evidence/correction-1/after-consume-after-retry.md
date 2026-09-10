---
id: task
title: Synthetic knowledge
status: done
gates:
    version: 1
    records:
        - id: gate:task:validation
          stage: validation
          attempts:
            - id: gate-attempt:task-validation-1
              briefing:
                id: briefing:task:validation:attempt-1:revision-1
                digest: sha256:b68ac14979facc0ab7e067415bbf3e640e7763cc9a282296212540bb206f6a75
                room-ref: '@review/validation/briefing-1'
              resolution:
                type: Resolution
                id: resolution:spacedock:task:validation:1
                briefing: briefing:task:validation:attempt-1:revision-1
                by: person:captain
                at: "2026-09-10T18:16:46.405901Z"
                decision: approve
                reason: TEST ONLY
              application:
                target-stage: done
                state: consumed
verdict: PASSED
completed: 2026-09-10T18:16:46Z
mod-block:
archived: 2026-09-10T18:16:48Z
---
Synthetic only.

peer edit across finalization
