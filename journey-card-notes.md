---
title: A journey card carries a short note that a person or an agent can add on the canvas, round-tripped through the map YAML
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the Captain, 2026-10-22: 「我覺得故事地圖可能有必須新增備注，就是人跟 agent 點一個卡片可以幫它輸入備注，輸出的 yml 也要支援此功能以便雙向轉移， yml to 畫布或反過來。這個功能可以用來加入描述性的內容，但不要讓卡片過長，同意嗎？」
- Shape asked for: clicking a card on the canvas lets a person or an agent enter a note; the journey YAML holds it; YAML to canvas and canvas to YAML both carry it; the note holds descriptive content without making the card itself long (for example shown collapsed or in a side panel, with a length bound).
- First ideation step: read kc-journey-map's own schema (`lib/schemas.mjs`), canvas and fold code for an existing description or note field, and name the bound and where the full note shows.
- Upstream first: kc-journey-map map, draw and canvas modes; the canvas tasks of other sessions (journey-canvas-hosted-poc, journey-server-host-pilot) read only; kc-adr's five-question routing rule (PR #691), so a note never carries a ruling that belongs in an ADR or a question's answer.
- Non-goals: rulings in notes; rich text beyond what the canvas renders.

## FO alignment

Alignment: needed at ideation; the length bound and where the full note shows are the Captain's to accept.
Surfaces: ui
Visible change: a card on the journey canvas gains a note a person or agent can add, shown without lengthening the card
Release review: not needed: workflow maintenance, on no journey map.
