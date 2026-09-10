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
                digest: sha256:e89eb222e1bd5e3945ee2e9c74237f55050b9f1e30856e69ab8f90eae4d8d626
                room-ref: '@review/validation/briefing-1'
              resolution:
                type: Resolution
                id: resolution:spacedock:task:validation:1
                briefing: briefing:task:validation:attempt-1:revision-1
                by: person:captain
                at: "2026-09-10T18:16:42.993071Z"
                decision: approve
                reason: TEST ONLY
              application:
                target-stage: done
                state: consumed
verdict: PASSED
completed: 2026-09-10T18:16:43Z
mod-block:
archived: 2026-09-10T18:16:45Z
---
Synthetic only.

peer edit across finalization
