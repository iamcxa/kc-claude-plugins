# kc-journey-map product planning

[draw-a-journey.yaml](draw-a-journey.yaml) is the canonical ongoing product plan.
[draw-a-journey.tldr](draw-a-journey.tldr) is its native editable snapshot: Story map,
three release boards and Function map. Keep planning decisions in the YAML; the
snapshot is a deliberate backup/share artifact, not a required export after every update.
The packaged fictional teaching fixture is separate from this plan.

Historical `lib/...`, `canvas.md` and symbol references in the source refer to the
`kc-journey-map/` plugin and its skill references. Observation dates below describe
those runs, not a new verification of every story or current repository-wide merge state.

## Open, read back or regenerate

A native snapshot can be opened in tldraw without this plugin. For source readback,
use the plugin canvas and a fresh room; importing replaces the target document.
Follow [canvas setup and lifecycle guidance](../../../kc-journey-map/skills/kc-journey-map/references/canvas.md)
to reuse a suitable service or start one when needed. These commands run from the
marketplace repository root; replace the room name with an unused one:

```bash
node kc-journey-map/lib/journey-tldr.mjs import docs/journey/kc-journey-map/draw-a-journey.tldr product-plan-fresh
open "http://localhost:3737/?room=product-plan-fresh"
node kc-journey-map/lib/journey-read.mjs docs/journey/kc-journey-map/draw-a-journey.yaml product-plan-fresh
```

To deliberately refresh the paired snapshot, read back unread edits first, then:

```bash
node kc-journey-map/lib/journey-render.mjs docs/journey/kc-journey-map/draw-a-journey.yaml product-plan-fresh --pages story-map,journey-board,function-map
node kc-journey-map/lib/journey-tldr.mjs export product-plan-fresh docs/journey/kc-journey-map/draw-a-journey.tldr
```

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
other source observations retain their historical dates. The five-page snapshot here
is the ongoing planning board, separate from that four-page verification capture.

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
