---
title: A worker that corrects its stage report writes a complete new report under the exact stage heading
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:stage-report-correction-path:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:stage-report-correction-path-backlog-1
              briefing:
                id: briefing:stage-report-correction-path:backlog:attempt-1:revision-1
                digest: sha256:9d10466c445af6d14dd837ba071b4ed964dcb1629dad24a57fa3c24fba221969
                room-ref: ./stage-report-correction-path/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:stage-report-correction-path:backlog:1
                briefing: briefing:stage-report-correction-path:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-25T14:15:43.013909Z"
                decision: approve
                reason: Captain 「全准」 (chat, 2026-10-25) answering the batch-6 backlog sitting, which listed this task's backlog briefing-1 question
              application:
                target-stage: ideation
                state: consumed
---

## Scope

- Source: batch 6 (2026-10-25): the Captain 「可以」 (chat), answering 「需要你決定：這份第 6 批的清單可以嗎？」 about FO's batch-6 list, item 5 「報告寫錯時的正確更正方式（新票）」.
- Bite (FO, 2026-10-25): on extension-defaults-and-install-choice the implementation report carried one `FAILED` item; `spacedock status --set ... status=validation` refused ("cannot change status away from entered stage implementation until a durable, complete ## Stage Report: implementation is committed"). A correction appended as `## Stage Report: implementation (correction)` was not read; only a second, complete report under the exact heading `## Stage Report: implementation` with every item DONE and a `### Summary` let it pass. Two worker rounds.
- Fact: Spacedock 0.27.3 `internal/status/entered_stage.go` `hasCompleteCommittedStageReport` reads only the latest report whose heading token is exactly the stage name; its checklist must hold no FAILED or blank item, every item needs an evidence line, and it must end with a non-empty Summary.
- Outcome: the dev2 worker skills (and FO's correction message) say how a report is corrected: a complete new report under the exact heading that supersedes the earlier ones.
- Upstream first: Spacedock ensign skill (report protocol) and the check above; dev2 `skills/implementation`, `skills/validation`.
- Non-goals: changing Spacedock's check.

## FO alignment

Alignment: not needed: documents an observed Spacedock behaviour.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
