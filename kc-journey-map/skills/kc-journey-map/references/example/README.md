# The worked example, as a board

`draw-a-journey.tldr` is the example journey rendered onto all five of its pages, in
tldraw's own file format. It is here so the boards can be looked at without running
anything, and opened without this plugin at all.

Two ways in.

**Without the canvas** — drag the file onto [tldraw.com](https://tldraw.com), or open it in
the tldraw desktop app. Everything renders; nothing round-trips, because the journey file
is what round-trips and it is not in here.

**With the canvas** — import it into a room, then read it back against the file it came
from:

```bash
npm ci && npm run canvas          # from the plugin directory
node lib/journey-tldr.mjs import skills/kc-journey-map/references/example/draw-a-journey.tldr demo
open "http://localhost:3737/?room=demo"
node lib/journey-read.mjs skills/kc-journey-map/references/journey.example.yaml demo
```

The read reports no drift, because the board was rendered from that file. Move a card and
run it again to see what it catches.

**Import replaces the whole target document.** Use a room name nothing else is using.

## What is in it

| Page | Shows |
|---|---|
| Story map | the backbone, its stories, and three release bands |
| RELEASE 1/2/3 — stories, flow & constraints | selected yellow stories with status borders beneath green activity groups; shared flow and constraints once per activity |
| Function map | Command, Event, State and Read model over the same columns |

See [canvas portability](../canvas.md) for saved border geometry and the native
height/scale synchronization boundary.

## Observed host selection

On 2026-09-11, Conductor Codex in Plan mode returned Kent's answer through
`request_user_input`: “故事地圖＋Release 詳細頁 (Recommended)”. After Kent switched
to Default mode and authorized rendering, the CLI applied
`--pages story-map,journey-board`. Expected and observed: four pages, Story map
and Release 1/2/3, with 76/62/32/44 shapes; no Function map. Native exports of all
four were viewed, reload preserved the pages/counts, and readback found no drift.
The tested plugin files matched merged main `0ec3380f590cbaf5b01ee1c325eb222da99a3c5a`.

`buildAllPages` supports the rendering leg; the host answer above establishes
this specific interaction. Native multi-select, Default-mode async question UI
and other hosts remain unverified. A temporary browser WebSocket redirect to the
isolated test server was instrumentation, not application code or proof of
alternate-port setup. This run verifies one story, not all Release 1 acceptance;
other source observations retain their historical dates. The five-page file here
is a regenerated example, separate from that four-page verification capture.

## Accepted Release 3 direction and feedback observation

Release 3 covers authoring a function model, iterating on the board and handing one
Development Brief to development planning. Existing authoring/handoff support is
separate from full journey acceptance, so those stories remain `unverified`. Direct
function-model canvas writeback is deferred; edit the source and redraw. The default
review artifact is the usable live board; PNG output follows Process step 5 in the
journey skill, including requests and context that justify an image.

A local experiment on 2026-09-11 alternated three trials per route with the same source
text change and selected story map plus three release pages. These are milliseconds
from immediately before the source edit; each visible check required exact changed
text in both projections and on the live story-map DOM, font readiness and two frames.

| Trial | Export-first: visible / review-ready | Live-link-first: visible / review-ready |
|---|---:|---:|
| 1 | 579.7 / 31373.0 | 699.0 / 699.0 |
| 2 | 700.9 / 31481.0 | 729.1 / 729.1 |
| 3 | 691.5 / 31108.7 | 706.6 / 706.6 |

The reconstructed export-first route used the shipped native scale-2 exporter for all
four pages, then reload and readback. Its median review-ready time was 31.37 seconds
versus 0.71 seconds for the verified live link; both became visible in 0.58–0.73 seconds.
This supports earlier live review when PNGs are unnecessary, not faster rendering.
Exports and reload were timed together; prior manual scale-1 previews were not replayed.
Timings exclude service/room setup, the common pre-edit safety readback, LLM deliberation
and human interaction. Full request-to-link timing, reliability and automatic server
version/lifecycle enforcement remain unverified.

A separate supported story-card edit survived readback, `applyDiff`, another source
change and redraw. The negative control skipped readback/application and lost an unread
edit on redraw: protection is procedural. Existing services were left running; this
observes preservation, not an automatic compatibility guarantee or full R3 acceptance.

## Regenerate the example

Regenerate it after changing the example — all five pages need every projection selected:

```bash
node lib/journey-render.mjs skills/kc-journey-map/references/journey.example.yaml example-release-stories-fresh --pages story-map,journey-board,function-map
node lib/journey-tldr.mjs export example-release-stories-fresh skills/kc-journey-map/references/example/draw-a-journey.tldr
```
