---
title: A kc-journey-map canvas room runs on a hosted service, survives this machine being off, and can be shared by link with edit access limited to people the Captain allows
status: backlog
variant: kc-dev-flow-2
profile: pilot
merge: pr
---

kc-journey-map's canvas is a tldraw 5.4 room synced over WebSocket by a local Node service (server/canvas-server.ts, @tldraw/sync 5.4.0); boards live on this machine and disappear from view when it is off. subspace-relay is hosted on Netlify, whose functions do not hold long-lived WebSocket connections, so relay's hosting does not carry over as is.

## Scope

Captain 2026-10-10: 「第二是畫布不是 host 在一個第三方，萬一關了就沒了，如果可以跟 relay 一樣 host 在某個服務會更好，也更容易分享」; then 「同意」 to the FO's proposal to open a proof-of-concept task first: stand a hosted sync server up (the FO named tldraw's Cloudflare sync template as the likely fit, not yet tried), and confirm sharing by link, persistence, and edit access limited to people the Captain allows, before deciding to move.
Non-goals: migrating existing rooms; changing the journey YAML format.
Budget and stop condition: to be set at ideation; the outcome is a decision with evidence, not a production move.

## Acceptance criteria

To be written at ideation.

## FO alignment

Release: none (package tooling).
Release review: not needed: no release.
Needed at ideation: the hosting options checked against the canvas's actual sync stack, the access-control question, and what a POC must prove.
Surfaces: none
Visible change: none
