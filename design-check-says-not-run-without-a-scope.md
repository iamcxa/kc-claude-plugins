---
title: design_surfaces.py says not run when the bound artifact has no Scope instead of holding against an empty baseline
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:design-check-says-not-run-without-a-scope:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:design-check-says-not-run-without-a-scope-backlog-1
              briefing:
                id: briefing:design-check-says-not-run-without-a-scope:backlog:attempt-1:revision-1
                digest: sha256:eecbe2296eb4a6340ec7f93ddc0a8b35976aef0ad6529afc57fb7a78c7cbb4f1
                room-ref: ./design-check-says-not-run-without-a-scope/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:design-check-says-not-run-without-a-scope:backlog:1
                briefing: briefing:design-check-says-not-run-without-a-scope:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-11-07T08:09:30.330332Z"
                decision: approve
                reason: 'The Captain chose 「核准（建議）」 (host question dialog, 2026-11-07), answering 「決定：第 17 批這五張（Paseo 瀏覽器當工人驗收的預設、決策紀錄檢查分清驗證取代與指向依據、派工時自動寫派工紀錄、沒給範圍時設計檢查說沒跑、觀察者列出沒有合併提問紀錄的合併）都用 Pilot，照各自寫下的範圍、預算與停止條件進入構想嗎？建議核准。要改哪張直接說。」. Recommendation: followed.'
              application:
                target-stage: ideation
                state: consumed
---

When the artifact bound at a gate has no Scope section, `design_surfaces.py check` prints a not-run line naming the artifact instead of reporting "Scope changed" against an empty baseline, and `gate prepare` warns when the artifact is not the task file.

## Scope

- Source: the Captain 「開」 (chat, 2026-11-06), answering 「要開這 4 張嗎？」 after fo-feedback round 005 (.notes/fo-feedback/round-005.md, closed 2026-11-06).
- Bite: relay llms-teaches-versions (2026-11-06): FO bound the Chinese presentation file as the backlog artifact, and the design check later held "Scope changed" though a diff showed Scope identical (round 005, operator report; the FO disclosed it under "Presentability hold").
- Upstream first: kc-dev-flow-2 scripts/design_surfaces.py check; Spacedock gate prepare (upstream; a warning there is an upstream issue).
- Non-goals: allowing a non-task artifact at a gate.

## Budget
- One package PR; the workflow word budget does not rise unless the design names a raise for the Captain.

## Stop condition
- A replay with a non-task artifact prints the not-run line, and a real Scope change is still held.

## FO alignment

Alignment: needed at ideation; the design choice is his to accept.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
