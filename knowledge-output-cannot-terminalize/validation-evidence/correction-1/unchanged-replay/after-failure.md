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
                digest: sha256:9e835d38ef2201947062c99fe3429a3802c0f62f1a85f24f0796955b6eb8dc37
                room-ref: '@review/validation/briefing-1'
              resolution:
                type: Resolution
                id: resolution:spacedock:task:validation:1
                briefing: briefing:task:validation:attempt-1:revision-1
                by: person:captain
                at: "2026-09-10T18:15:48.487229Z"
                decision: approve
                reason: TEST ONLY
              application:
                target-stage: done
                state: consumed
verdict: PASSED
completed: 2026-09-10T18:15:49Z
mod-block:
archived: 2026-09-10T18:15:49Z
---
Synthetic only.

peer edit before locked finalize
