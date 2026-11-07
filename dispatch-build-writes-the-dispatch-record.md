---
title: spacedock dispatch build --stamp writes the task's dispatch record itself
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:dispatch-build-writes-the-dispatch-record:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:dispatch-build-writes-the-dispatch-record-backlog-1
              briefing:
                id: briefing:dispatch-build-writes-the-dispatch-record:backlog:attempt-1:revision-1
                digest: sha256:98146d1a1c26e89ee031d45b1a6b1fc6b907c8f287a194c73f8743ac402975ce
                room-ref: ./dispatch-build-writes-the-dispatch-record/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:dispatch-build-writes-the-dispatch-record:backlog:1
                briefing: briefing:dispatch-build-writes-the-dispatch-record:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-11-07T08:09:24.850248Z"
                decision: approve
                reason: 'The Captain chose 「核准（建議）」 (host question dialog, 2026-11-07), answering 「決定：第 17 批這五張（Paseo 瀏覽器當工人驗收的預設、決策紀錄檢查分清驗證取代與指向依據、派工時自動寫派工紀錄、沒給範圍時設計檢查說沒跑、觀察者列出沒有合併提問紀錄的合併）都用 Pilot，照各自寫下的範圍、預算與停止條件進入構想嗎？建議核准。要改哪張直接說。」. Recommendation: followed.'
              application:
                target-stage: ideation
                state: pending
---

A dispatch built with `dispatch build --stamp` leaves <task>/dispatch/<stage>-<cycle>.md written from the same checklist, scope notes, model and SHA it sends, so the record no longer depends on FO remembering it.

## Scope

- Source: the Captain 「開」 (chat, 2026-11-06), answering 「要開這 4 張嗎？」 after fo-feedback round 005 (.notes/fo-feedback/round-005.md, closed 2026-11-06).
- Bite: kc-paseo-plugins reconstructed every dispatch record of batch r1b-polish-1 after the fact (_archive/project-env-rate-limit-cause/dispatch/ideation-1.md: "Reconstructed by FO on 2026-11-06, after the dispatch"; FO read 2026-11-06); qnow sent a follow-up addendum with no record (observer); the kc-plugin FO wrote one message record late and omitted required lines in batches 14 and 15 (observer reports).
- Upstream first: Spacedock dispatch build --stamp (Spacedock is not the Captain's repository: a change there is an upstream issue, so the dev2 side may be a package wrapper); kc-dev-flow-2 dispatch_records.py, which checks the record.
- Non-goals: follow-up messages to a running worker (a separate record kind).

## Budget
- One package PR; the workflow word budget does not rise unless the design names a raise for the Captain.

## Stop condition
- A stamped dispatch leaves a record that dispatch_records.py accepts without FO writing it, or the design names why Spacedock cannot and what the package does instead.

## FO alignment

Alignment: needed at ideation; the design choice is his to accept.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
