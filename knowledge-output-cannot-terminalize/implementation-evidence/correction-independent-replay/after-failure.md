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
                digest: sha256:cb774b7b44a4729c7cbd9757ac942caf01a632255e8571737c1cee6a8f126d35
                room-ref: '@review/validation/briefing-1'
              resolution:
                type: Resolution
                id: resolution:spacedock:task:validation:1
                briefing: briefing:task:validation:attempt-1:revision-1
                by: person:captain
                at: "2026-09-10T17:48:17.223912Z"
                decision: approve
                reason: TEST ONLY
              application:
                target-stage: done
                state: pending
---
Synthetic only.

peer edit before locked finalize
