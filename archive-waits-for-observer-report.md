---
title: merge guard does not archive a learn-listed task before its observer report is committed
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:archive-waits-for-observer-report:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:archive-waits-for-observer-report-backlog-1
              briefing:
                id: briefing:archive-waits-for-observer-report:backlog:attempt-1:revision-1
                digest: sha256:64f490b862f1eb401fa474320e8328ae3e48a0724d9ef44da6db83e4cd144e90
                room-ref: ./archive-waits-for-observer-report/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:archive-waits-for-observer-report:backlog:1
                briefing: briefing:archive-waits-for-observer-report:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-27T15:12:52.000973Z"
                decision: approve
                reason: Captain 「全准」 (chat, 2026-10-27) answering 「需要你決定：第 8 批 7 張任務的待辦關卡，要不要一起批准進入設計階段？同時把已經做完的 `peers-paseo-host-binding` 關掉。我建議全部批准，也關掉那張。」; accepts FO's recommendation
              application:
                target-stage: ideation
                state: pending
---

## Scope

- Source: the Captain 「同意開 1 到 5，第 6 項併進「GPT 夥伴」提案」 (chat, 2026-10-27), answering FO's list of package-issue candidates (items 2 to 5 relayed by the relay FO, Paseo 1671c3a9, from its pair-once and room-specs-follow-web-part-select observer reports; item 1 relayed by the kc-ops-inbox FO, Paseo 46c2ebdf).
- Bite: relay pair-once (relay#442): `merge guard --verdict passed` archived the task before observer.md existed; it was committed after archive commit 64ac8c39. Same order here on fo-written-lines-checked-before-dispatch (#724, observer finding 2026-10-26: the sentinel was written before observer.md). `observer_check.py` names the step but nothing refuses the archive.
- Added 2026-10-27: a third bite, relayed by the kc-ops-inbox FO (Paseo 46c2ebdf, data): its task ops-metric-event-protocol (PR #727, merged d7eeeef2) ran the sentinel and archive before the observer report (its observer.md at state commit f25c224f6). Same relay: `spacedock state commit` refuses an archived slug, so an observer report written at archive needs a raw git commit.
- Upstream first: Spacedock `merge guard` (upstream), `scripts/observer_check.py`, `extensions/learn/EXTENSION.md`, the package mod's merge hook.

## FO alignment

Alignment: needed before ideation; where the check runs is a package design choice.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
