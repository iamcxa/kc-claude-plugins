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
                digest: sha256:37086f62086213838868c0d90bcb240e14375e510035a8ad16ccaf365d4155b9
                room-ref: '@review/validation/briefing-1'
              resolution:
                type: Resolution
                id: resolution:spacedock:task:validation:1
                briefing: briefing:task:validation:attempt-1:revision-1
                by: person:captain
                at: "2026-09-10T17:51:13.672674Z"
                decision: approve
                reason: TEST ONLY
              application:
                target-stage: done
                state: consumed
verdict: PASSED
completed: 2026-09-10T17:51:14Z
mod-block:
archived: 2026-09-10T17:51:14Z
---
Synthetic only.

peer edit before locked finalize
