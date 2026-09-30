---
title: A release can opt out of its journey-board page, and a re-render removes board pages that no longer belong
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

kc-journey-map renders a board page for every release and re-renders recreate or keep pages the map no longer wants; issue #541.

## Scope

Captain 2026-09-30: 「做board: false 可以」, choosing a per-release `board: false` field over a semantic `shipped: true`, after asking (via the relay journey session) 「那 r1, r1.5 是否就是已經在 main 上…我這為這兩片似乎不需要有 release board」 and 「選 1，轉給 colombo-ae 做」. This task covers issue #541.
Evidence (origin/main d3c79ba5, 2026-09-30): `journeyBoardPages` in `kc-journey-map/lib/render.mjs` maps every release to `buildJourneyBoard`, and nothing in `lib/` reads a board opt-out; on an adopter journey two shipped releases (6 of 7 stories `exists`) keep boards that repeat the story map; a board page deleted by hand is recreated by the next `--pages journey-board` render, and a page for a release removed from the YAML survives re-renders.
Non-goals: a semantic `shipped` field; deriving the opt-out from story statuses (one shipped release keeps an `unverified` story the evidence lint cannot count); the release version field (#531).

## Acceptance criteria

To be written at ideation.

## FO alignment

Needed at ideation: where `board: false` is read and validated (a non-boolean value), that the release keeps its story-map row, how a re-render removes an existing board page for a release that opts out or no longer exists without touching human-drawn content, and what the canvas read-back does with a removed page.
Result: the FO delegates these questions to ideation, which decides each with its source and returns any ruling that needs the Captain.
Surfaces: none
Visible change: none
