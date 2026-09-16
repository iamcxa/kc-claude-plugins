# backlog gate — canvas-document-popup

FO admission record for [issue #465](https://github.com/iamcxa/kc-claude-plugins/issues/465).
This boundary has no worker report by workflow design.

## Variant and profile

- `variant: kc-dev-flow-2`
- `profile:` unset, pending the Captain's selection. Recommended: **prod**.

The issue asks to "preserve running user canvases" and "do not merge or replace a
live service as part of this handoff", and its acceptance list requires the exported
board to keep working in a tldraw host that does not have this viewer. Those are
compatibility and live-operation boundaries, not a bounded first use.

Both `prod` and `pilot` run on this workflow's existing five-stage graph, so the
selection changes which profile references the stage skills load — not the route.

## Verified inputs

- The review chain this viewer serves landed in `#463`, merged to `main` as
  `6570fca9`.
- The canvas client and server named in the issue exist on `main`:
  `kc-journey-map/server/client/App.tsx` and `kc-journey-map/server/canvas-server.ts`.
- A canvas dev server is answering on `http://localhost:3742` (HTTP 200, Vite dev
  server serving the React client). This is the Captain's running instance and the
  implementation stage must not disturb it.

## Proposed outcome

A reviewer following the Action → Question → answer → evidence chain can read a
technical-document chapter without leaving the card or losing the canvas viewport,
and the board stays portable to a tldraw host that has no viewer.

## Scope, exclusions, budget and stop condition

As recorded on the task. The exclusions are the issue's own list, plus preserving
every human-authored record, wording, colour, layout, arrow and binding, and not
translating canvas content. The stop condition covers the case where private-repo
retrieval would require exposing a server credential to the browser or standing up
authentication work — both are the issue's explicit non-goals.

## Acceptance criteria translation

The issue carries seven checkbox items. Items 6 (browser verification covering the
shared board origin as well as local development) and 7 (tests plus separate
reporting of local, browser and shared-origin results) are evidence obligations
rather than properties of the finished thing. They are therefore folded into the
verification clauses of AC-1 through AC-5 instead of becoming criteria of their own.
No requirement was dropped; if the Captain wants them as standalone criteria, say so
and they move back out.

## Evidence needed before ideation starts

1. The Captain's selected profile recorded on the task.
2. The approved outcome, scope, exclusions and stop condition above.
3. FO-led design alignment on the popup's placement, states and heading-navigation
   behaviour against the running canvas, before any ideation worker is dispatched.
   This stage's own contract puts that alignment on FO; on the previous task FO
   skipped it and dispatched immediately, and nothing in the workflow caught it.

## Known route risk

Stage `concurrency` is 1 per stage, counted on the destination stage. This task and
`release-please-exclude-paths` can hold different stages simultaneously, but not the
same one. `release-please-exclude-paths` currently holds `implementation`.
