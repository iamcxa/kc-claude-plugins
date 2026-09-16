# ideation gate — canvas-document-popup (after one correction round)

FO recommendation: **approve, with the one open question answered.**

## The defect the Captain found, and its fix

The Captain could not close the popup. Root cause: tldraw's own stylesheet sets
`.tl-canvas__in-front { pointer-events: none }` — the `InFrontOfTheCanvas` slot is
click-through by design, for canvas-space overlays — and that inherited unbroken down
to the Close button, so nothing in the dialog was hit-testable. Fix: `DocPopup` now
mounts through `createPortal(..., document.body)`, outside tldraw's subtree entirely,
rather than patching `pointer-events` locally. The popup never reads `editor` and has
no relationship to canvas pan or zoom, so it does not belong in that slot.

FO's own first root-cause explanation was wrong and is withdrawn on the task; the
mechanism above is the measured one, confirmed in tldraw's CSS.

## FO independent re-verification

Not accepted on report. FO re-ran its own reproduction — the same script that failed
before the fix:

- The Close button click now lands and the dialog closes (`dialog[open]` count 0
  after the click). Before the fix the identical click timed out with the dialog still
  open.
- `createPortal` is genuinely wired at the render site, not an unused import.
- `.tl-canvas__in-front { pointer-events: none }` is present in
  `node_modules/tldraw/tldraw.css`, so the mechanism is tldraw's documented behaviour
  rather than an artifact of the preview.
- The Captain's canvas on port 3742 still answers and was not touched. The real
  `kc-journey-map` worktree is clean.

The worker also replaced its Escape-only verification with real pointer clicks on both
interactive controls plus the `elementFromPoint`-at-centre assertion, and re-verified
Escape separately. FO's confirmation covers the Close control specifically, which is
what actually failed.

## What this round did not change

D1, D2, scope, acceptance criteria and profile are untouched, as the correction
dispatch required. The design is otherwise cycle-1's: one server route plus one Vite
proxy entry following `/connect`; `marked`, `dompurify` and `mermaid` already present
as transitive dependencies; only `github-slugger` new.

## Open question for the Captain

**Repo → local-checkout mapping.** The link carries `owner/repo`; the server needs a
path.

- **Option 1 — operator env map only** (`JOURNEY_DOC_REPOS=owner/repo=/abs/path,...`),
  verified in the preview for lookup, ref-not-found and path-not-found. This
  repository reviewing its own documents still needs an env entry.
- **Option 2 — the same map plus one zero-config default:** when the server
  checkout's `git remote get-url origin` matches the link's `owner/repo`, use that
  checkout. This repository reviewing itself then needs no configuration.

Worker and FO both recommend option 2. Either answer stays inside Pilot; it changes
the implementation task list, not the profile.

## Obligations left to the Captain, not absorbed

Live `git fetch` from the server; a configuration UI for the map; cross-request
caching; and updating `human-led-review.md` lines 114-122 from deferred language to an
implemented capability. FO agrees none should enter scope: the first would break the
credential-free guarantee D1 rests on, and the last is a retained-document edit with
its own practice.

## Limit

The preview is disposable and proves the interaction loop. No product code exists yet,
and nothing here has been exercised on the shared board origin — AC-1's verification
clause requires that, and it belongs to validation.
