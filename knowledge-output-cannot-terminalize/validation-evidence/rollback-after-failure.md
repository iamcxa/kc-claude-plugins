---
id: task
title: Synthetic knowledge
status: validation
gates:
    version: 1
    records:
        - id: gate:task:validation
          stage: validation
          attempts:
            - id: gate-attempt:task-validation-1
              briefing:
                id: briefing:task:validation:attempt-1:revision-1
                digest: sha256:171693a264731e396e8b48a685c781284489a883bce1fa67378d49cb95c77bd9
                room-ref: '@review/validation/briefing-1'
              resolution:
                type: Resolution
                id: resolution:spacedock:task:validation:1
                briefing: briefing:task:validation:attempt-1:revision-1
                by: person:captain
                at: "2026-09-10T17:37:58.531202Z"
                decision: approve
                reason: TEST ONLY
              application:
                target-stage: done
                state: pending
---
Synthetic only.
