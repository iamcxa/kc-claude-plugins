# 0007. A release opts out of its journey-board page with an explicit `board: false`

Date: 2026-09-30

## Status

Accepted

## Context

`kc-journey-map` drew a journey-board page for every release, and a re-render removed
nothing at page level. On one adopter's journey (origin/main d3c79ba5, 2026-09-30) two
releases whose stories were nearly all `exists` kept boards that repeated the story map,
and a board page for a release deleted from the file survived every re-render (the
render replied `removed: 0`; reproduced in a throwaway canvas room). A release mixing an
`unverified` story with `exists` ones cannot be told apart from a finished release by
status, so the opt-out cannot be derived from statuses.

## Decision

**Words:** 「做board: false 可以」 — Captain, backlog gate of this task, 2026-09-30.
On what happens to a stale page that holds hand-drawn shapes: 「同意，手畫的不刪除」 —
Captain, ideation gate of this task, 2026-09-30.

**Options considered:**
- an explicit per-release `board: false`, read as `release.board !== false` (chosen)
- a semantic `shipped: true` field — rejected by the Captain's choice of `board: false`
- derive the opt-out from story statuses — rejected: a shipped release can keep an
  `unverified` story the evidence lint cannot count
- when a stale board page holds hand-drawn shapes: keep the page and those shapes, remove
  only generated shapes (chosen); refuse the whole render until they are moved, or delete
  everything under `--force` — rejected: the first blocks unrelated pages, the second
  loses hand-drawn work

A release may carry `board: false`; the renderer draws no journey-board page for it and
the story map still shows its band. A `board` value that is present and not a boolean is
the lint violation `invalid-board`; the renderer does not lint and still draws the board.
When every release opts out no board is drawn; the whole-journey board is only for a
journey with no `releases:` key. Changing `board` on a release is not a change to its
requirements, so `journey-handoff.mjs` ignores it.

A render that selects `journey-board` removes every page whose id starts `page:jm-board-`
that the render did not produce, with its generated shapes (those carrying `meta.journey`)
and bindings. A stale board page holding any shape without `meta.journey` is kept with
those shapes, with or without `--force`, and the render reports it. The render never
removes the last page in the room. A page without the `page:jm-board-` prefix is never
removed, and a render that does not select `journey-board` removes no board page. Later
work, including any release-version field, must keep the field's meaning and this
ownership rule.

## Consequences

An opted-out release can leave a near-empty tab until a person deletes the note or the
page; the render reports it on every run. An older plugin version ignores `board` and
still draws the board. A duplicate a person makes of a generated card carries the same
`meta.journey`, so a duplicated card on a stale page is removed with it. A person-made
page is safe only because the canvas names it differently from `page:jm-board-*`; that
was not exercised in a browser. What a sync room does with zero pages, and a browser tab
open on a removed page, were not tested. Reopen if an adopter needs the opt-out derived
from status, or if a kept page with a stale note proves a nuisance.
