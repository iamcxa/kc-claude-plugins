---
title: A journey-map re-render keeps hand-drawn annotations on the cards they marked
status: ideation
variant: kc-dev-flow-2
profile: pilot
merge: pr
gates:
    version: 1
    records:
        - id: gate:journey-render-keeps-annotations:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:journey-render-keeps-annotations-backlog-1
              briefing:
                id: briefing:journey-render-keeps-annotations:backlog:attempt-1:revision-1
                digest: sha256:53739e52c6aba71edfb2c323921f36fe3949cc2b8f87e64f1964b2afe0fda63e
                room-ref: ./journey-render-keeps-annotations/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:journey-render-keeps-annotations:backlog:1
                briefing: briefing:journey-render-keeps-annotations:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-07T13:55:08.870201Z"
                decision: approve
                reason: 'Captain 2026-10-07: 「核准這張任務以 Pilot 進入設計」 — confirms the request relayed by dhaka-32'
              application:
                target-stage: ideation
                state: consumed
---

`renderToRoom` in `kc-journey-map/lib/render.mjs` recomputes generated card positions from the journey YAML and refuses only when a generated shape was hand-edited (`handEditedIds`); shapes without `meta.journey` — hand frames, sticky notes, and the `discuss-merged-*` / `discuss-halo-*` frames — keep their absolute position. When a release row gains stories, the cards below move and those annotations are left beside empty space, silently.

## Scope

Relayed by the peer session dhaka-32 on 2026-10-07 (not yet confirmed by the Captain in this session): the Captain asked for an upstream fix of this defect through this workflow, profile Pilot. Evidence it reported: team canvas room relay-spacedock-review-draft, 2026-10-06/07, kc-journey-map 1.5.0; two stories added to one release moved the cards below by +500 and another row by +2910; 7 annotations were stranded and repaired by hand (shift each by the delta of the card it overlapped before the render). Room snapshots (raw room records of relay-spacedock-review-draft, copied by dhaka-32 to a durable path): /Users/kent/conductor/workspaces/subspace-relay/dhaka/.context/journey-render-annotations/draft-room.json (before the stranding render, 2026-10-06 14:09), /Users/kent/conductor/workspaces/subspace-relay/dhaka/.context/journey-render-annotations/draft-before-frame-fix.json (stranded state, 2026-10-07), /Users/kent/conductor/workspaces/subspace-relay/dhaka/.context/journey-render-annotations/draft-after-fix.json (after the hand repair).
Wanted behaviour (relayed): on re-render, an annotation that overlapped a generated card moves with that card, or the render at least reports which annotations would be stranded instead of doing it silently; a test fails on today's renderer.
Non-goals: moving annotations that overlapped no generated card; changing the YAML-is-authority rule.

## Acceptance criteria

To be written at ideation.

## FO alignment

Release review: not needed: plugin defect, not on a product journey release.
Needed at ideation: no Captain alignment before ideation; ideation chooses move-with-card versus report-only from the two snapshots, and returns the choice if it changes what a human-drawn canvas guarantees.
Surfaces: ui
Visible change: A re-render keeps a hand-drawn frame or sticky note on the card it marked instead of leaving it behind.
