---
title: "fixture: gate prepared at validation, pr: absent"
status: validation
sprint: ship-cloud-wrapper
sprint-readiness: ready
id: fixgatenoprep0000000000
gates:
    version: 1
    records:
        - id: gate:fixgatenoprep0000000000:validation
          stage: validation
          attempts:
            - id: gate-attempt:fixgatenoprep0000000000-validation-1
              briefing:
                id: briefing:fixgatenoprep0000000000:validation:attempt-1:revision-1
                digest: sha256:1111111111111111111111111111111111111111111111111111111111111111
                room-ref: ./task-gate-prepared-no-pr/review/validation/briefing-1
---

Fixture entity: gate prepared, `pr:` field absent (AC-3 -- reports question, not gate-prepared).
