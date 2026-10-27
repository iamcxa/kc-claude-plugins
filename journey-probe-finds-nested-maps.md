---
title: The journey-extension install probe finds maps in nested product folders
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:journey-probe-finds-nested-maps:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:journey-probe-finds-nested-maps-backlog-1
              briefing:
                id: briefing:journey-probe-finds-nested-maps:backlog:attempt-1:revision-1
                digest: sha256:f3a012ccc0de1f03a67e45fc1124106055aa0816db1921076d713a47d5666f60
                room-ref: ./journey-probe-finds-nested-maps/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:journey-probe-finds-nested-maps:backlog:1
                briefing: briefing:journey-probe-finds-nested-maps:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-27T15:13:21.741603Z"
                decision: approve
                reason: Captain 「全准」 (chat, 2026-10-27) answering 「需要你決定：第 8 批 7 張任務的待辦關卡，要不要一起批准進入設計階段？同時把已經做完的 `peers-paseo-host-binding` 關掉。我建議全部批准，也關掉那張。」; accepts FO's recommendation
              application:
                target-stage: ideation
                state: pending
---

## Scope

- Source: the Captain 「開」 (chat, 2026-10-26), answering FO's ask to file this and the Codex-reader task.
- Bite: Codex P2 on iamcxa/kc-claude-plugins#716 (head 8340c3ba, 2026-10-25T04:30:35Z), unaddressed at merge: `kc-dev-flow-2/references/sd/adoption.md` probes `docs/journey/*.yaml`, but kc-journey-map's README documents `docs/journey/<product>/<journey>.yaml` for multi-product adopters, so the probe rejects valid maps and leaves both journey extensions off. Still on origin/main c70f1b22 (`git show origin/main:kc-dev-flow-2/references/sd/adoption.md`, 2026-10-26).
- Upstream first: kc-journey-map README (map locations) and its own map-finding code, before writing a new glob.

## FO alignment

Alignment: not needed: a recorded review finding against the documented map layout.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
