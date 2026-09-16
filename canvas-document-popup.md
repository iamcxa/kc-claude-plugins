---
id:
title: read a Markdown and Mermaid document in a journey-canvas popup
status: ideation
variant: kc-dev-flow-2
profile: pilot
merge: pr
worktree:
pr:
gates:
    version: 1
    records:
        - id: gate:canvas-document-popup:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:canvas-document-popup-backlog-1
              briefing:
                id: briefing:canvas-document-popup:backlog:attempt-1:revision-1
                digest: sha256:25de7ada15242d51c6400cb3aa5a9c36d5bab3aac42cddd75afc65f838471fc9
                room-ref: ./canvas-document-popup/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:canvas-document-popup:backlog:1
                briefing: briefing:canvas-document-popup:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-16T07:21:13.098661Z"
                decision: approve
                reason: Captain selected profile pilot and approved the admission record's outcome, scope, exclusions and stop condition.
              application:
                target-stage: ideation
                state: consumed
        - id: gate:canvas-document-popup:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:canvas-document-popup-ideation-1
              briefing:
                id: briefing:canvas-document-popup:ideation:attempt-1:revision-1
                digest: sha256:d4ad0aa41a3e5f4655539b2c4b5ce81278e5e5a34ba2859e898bf1d8872749a7
                room-ref: ./canvas-document-popup/review/ideation/briefing-1
              withdrawal:
                by: agent:first-officer
                at: "2026-09-16T14:44:43.608229Z"
                reason: 'Captain reported the popup cannot be closed. FO reproduced: the Close button is visible but not hittable. The stage''s evidence claim is contradicted, so the binding is withdrawn before any correction.'
started: 2026-09-16T14:10:56Z
---

Human-led architecture review follows a chain on the journey canvas: green Action →
Question → short answer carrying a technical-document chapter → implementation
evidence. Opening that chapter in another browser tab breaks the chain — the reviewer
loses the card they were on and the canvas viewport they had arranged. The review
skill that defines this chain landed in #463; this task is the viewer half.

Source: [issue #465](https://github.com/iamcxa/kc-claude-plugins/issues/465). The
issue's own acceptance list is the Captain's wording; items 6 and 7 of that list are
evidence obligations rather than end-state properties, so they appear below inside the
verification clauses of AC-1 through AC-5 rather than as separate criteria.

## Scope

In scope: an optional popup inside the existing journey canvas that opens a supported
GitHub Markdown document or chapter from an answer card, renders Markdown and Mermaid,
navigates to the linked heading, and closes back to the originating card with the
canvas viewport and selection intact. The canonical GitHub URL stays in the native
shape or bookmark; the popup is a way to read the document, not a document store.

Non-goals, taken from the issue's own exclusion list: document editing;
authentication or account product work; a new document repository; full
multi-document navigation history; redesigning the journey canvas. Also excluded:
changing any human-authored record, wording, colour, layout, arrow or binding on an
existing board, and translating canvas content.

Budget: one reviewable PR against `main`, implemented in an isolated worktree, with
the Captain's running canvas on port 3742 left undisturbed.

Stop condition: the motivating documents may live in private repositories. If the
smallest supported retrieval approach for those documents would require exposing a
server credential to the browser, or standing up authentication product work, stop
and report the constraint — both are explicit non-goals. Retaining the source link
and an unavailable-document state is an acceptable outcome for that case.

## Acceptance criteria

**AC-1**: An answer card on a real canvas opens its linked document at the linked
heading inside the current canvas, with no new browser tab created.
Verified by: a browser run against the running canvas that records the popup open,
the resolved heading position, and the unchanged tab count, captured on both local
development and the shared board origin. An HTTP status or parser result alone does
not satisfy this.

**AC-2**: A document containing Markdown and a Mermaid sequence diagram renders as
content, with the numbering the Mermaid source expresses still visible, and without
executing any script embedded in the document.
Verified by: a browser run on a fixture document whose Mermaid source carries
`autonumber`, showing rendered numbering, plus a case containing an embedded script
that demonstrably does not execute.

**AC-3**: Closing the popup — by the Close control and by Escape — restores focus to
the originating card and leaves the canvas selection, viewport and the diagram itself
unchanged.
Verified by: a browser run comparing focus, selection, viewport and diagram state
before open and after close, plus an automated test exercising focus restoration.

**AC-4**: Loading, unavailable-document, inaccessible-or-private-document and
missing-heading states each render a useful state, and Open on GitHub stays available
in every one of them.
Verified by: a browser run covering all four states including a genuinely
inaccessible document, showing the Open on GitHub control present in each.

**AC-5**: The canonical chapter URL survives native copy, export and import, and the
exported diagram remains understandable with a working source link in a tldraw host
that does not have this viewer.
Verified by: an export/import round trip whose output is opened in a tldraw host
without the viewer, with the source link followed successfully.

## Captain's design decisions (FO-led alignment, 2026-09-16)

These are settled. Ideation reflects them; it does not re-open them.

**D1 — where the server gets the document: from the repository checkout on the
machine running the canvas server.** The browser never talks to GitHub, so no
credential reaches it and private repositories work without one. Accepted limit: a
reviewer on the shared board origin can only read documents that the server's machine
has checked out; anything else degrades to the unavailable-document state with Open on
GitHub retained, which AC-4 already requires.

**D2 — which revision the popup shows: the ref carried in the canonical link, read
with `git show <ref>:<path>`.** Not the current working tree. This is what makes the
issue's rule implementable — the review branch while a document is under review, the
verified chapter on `main` after merge — and it makes the popup show exactly what the
link points at rather than whatever happens to be checked out.

### Architecture facts these rest on

Verified by FO against `main` before the decision:

- The document API is Fastify on `JOURNEY_API_PORT` (default 5858), bound to
  `127.0.0.1` only.
- The client is served by Vite on port 3737 by default; the Captain's instance runs on
  3742.
- Vite proxies exactly one path, `/connect` (websocket), to the loopback API.
- The shared board origin works through Vite's `allowedHosts`, extended by
  `JOURNEY_ALLOWED_HOSTS`.
- Nothing in the package fetches anything over the network: no HTTP client, no GitHub
  integration.

So the shape is one new route on the Fastify server plus one new Vite proxy entry,
following the existing `/connect` pattern. `human-led-review.md` lines 114-122 already
constrain the viewer and prescribe no renderer architecture.

## Smallest useful end-to-end slice

A reviewer working the human-led architecture review chain (`human-led-review.md`)
selects a chapter link on an answer card. The popup opens inline, renders the chapter,
lets them navigate to the linked heading, and returns them to exactly the card and
canvas state they left — no new tab, no lost selection or viewport. That single
click-open-read-close loop is the whole slice; everything else (multi-doc history,
editing, auth) is excluded per Scope.

Real seams crossed: the canvas client's shape-hyperlink UI (tldraw has no override
slot for it — see "Existing-code capability check"), the existing Vite proxy (one new
`/repo-doc` entry beside `/connect`), the existing loopback-only Fastify server (one
new `GET` route), and the machine's local git checkout(s) via `git show`. No new
network egress, no new port, no schema change to the tldraw document itself — the
chapter link lives in a shape's ordinary `url` prop.

## Existing-code capability check

`@tldraw/mermaid`'s `createMermaidDiagram` (already a dependency, used by
`server/client/sequence.ts`'s `addSequencePage`) converts Mermaid source into native
tldraw shapes on a **new page**, then calls `zoomToFit`. Verified by reading
`sequence.ts`: it mutates the store (creates a page, adds shapes, changes the current
page and camera). That is the opposite of what AC-3 requires — the popup must leave
the canvas' current page, selection, and viewport untouched. Conclusion: not reused.
The popup renders Mermaid to an SVG string via the `mermaid` package directly
(confirmed present in `package-lock.json` as a transitive dependency of
`@tldraw/mermaid`, `mermaid@11.16.1`, alongside `marked@16.4.2` and
`dompurify@3.4.15` — also transitive, also unused elsewhere) inside a DOM overlay
that never touches the editor's store. No existing capability answers "read-only
chapter render without mutating the canvas"; this is genuinely new, not a
duplicate of `addSequencePage`.

tldraw's shape hyperlink UI (`HyperlinkButton`, shared by note/geo/bookmark/image/
video shape utils — confirmed by reading `BookmarkShapeUtil.mjs`, which imports the
same component) always renders `<a class="tl-hyperlink-button" target="_blank">` and
has no entry in `TLComponents`/`TLEditorComponents` (checked
`@tldraw/editor/dist-esm/index.d.mts`). There is no supported override point. The only
available seam is a capture-phase `click` listener on `editor.getContainer()` matching
the canonical chapter-URL shape and calling `preventDefault()` before the browser's
native new-tab navigation — verified working in the preview (see evidence below).

## PRFAQ

**Proposition.** A reviewer working a human-led architecture review canvas can open a
linked technical-document chapter — Markdown and Mermaid, rendered, numbered, script-
free — without leaving the card they were reading, and return to exactly where they
were by pressing Escape or Close.

**FAQ**

*Why does the popup read from a local checkout instead of fetching GitHub?* Per D1,
so no GitHub credential ever reaches the browser and private repositories work
without one. The cost: a reviewer on the shared board origin can only read documents
the server's own machine has checked out.

*Why the ref in the link, not the working tree?* Per D2, so the popup shows exactly
what the link promises — the review branch while under review, `main` after merge —
via `git show <ref>:<path>`, never whatever happens to be checked out.

*What happens when the document truly isn't available?* Ref not found, path not
found at that ref, and "no checkout configured for this repository" (the D1 private/
inaccessible case) all render the same **unavailable** state with the reason and
Open on GitHub retained (AC-4). The server cannot distinguish "private" from
"nonexistent" without a credential it deliberately doesn't have; that collapse is
accepted, not a gap.

*What if the link's heading has moved or was mistyped?* The chapter renders at the
top with a visible "heading not found" banner; Open on GitHub stays available.

**Acceptance evidence plan.** Each AC below is proven by a real browser run
(Playwright or equivalent) exercising the actual interaction — click, render, close —
not by an HTTP response or a markdown-parser unit result alone, per the stage's own
distinction and the ACs' explicit verification clauses.

## Sequence

```mermaid
sequenceDiagram
    participant Reviewer
    participant Client as Canvas client (popup)
    participant Proxy as Vite proxy
    participant Server as Fastify /repo-doc
    participant Checkout as Local git checkout

    Reviewer->>Client: click a shape's link
    alt URL does not match the canonical blob-chapter pattern
        Client-->>Reviewer: native <a target=_blank> opens (popup not involved) [STOP]
    else canonical chapter link (blob/<ref>/<path>#<chapter>)
        Client->>Client: preventDefault + stopPropagation, open popup (loading)
        Client->>Proxy: GET /repo-doc?owner&repo&ref&path
        Proxy->>Server: forward over loopback
        Server->>Server: look up owner/repo in configured checkout map
        alt no checkout configured (includes D1's private/inaccessible case)
            Server-->>Client: unavailable, reason
            Client-->>Reviewer: unavailable state, Open on GitHub retained [STOP]
        else checkout configured
            Server->>Checkout: git rev-parse --verify <ref>
            alt ref not found
                Checkout-->>Server: not found
                Server-->>Client: unavailable, reason
                Client-->>Reviewer: unavailable state, Open on GitHub retained [STOP]
            else ref resolves to a commit
                Server->>Checkout: git show <ref>:<path>
                alt path not found at that ref
                    Checkout-->>Server: not found
                    Server-->>Client: unavailable, reason
                    Client-->>Reviewer: unavailable state, Open on GitHub retained [STOP]
                else content found
                    Checkout-->>Server: file content pinned at the resolved SHA
                    Server-->>Client: content, sha
                    Client->>Client: marked to HTML, DOMPurify sanitize, mermaid.render (strict)
                    alt chapter heading present
                        Client-->>Reviewer: rendered chapter, scrolled to heading
                    else heading not found
                        Client-->>Reviewer: rendered chapter, top of doc, missing-heading banner
                    end
                    Reviewer->>Client: Close control OR Escape
                    Client->>Client: dialog closes; focus, selection, viewport, diagram unchanged
                    Client-->>Reviewer: back on the originating card [STOP]
                end
            end
        end
    end
```

No runtime approvals occur in this flow — the only approvals are the Captain's D1/D2
rulings and this gate itself, both outside the sequence above.

## Acceptance evidence

| AC | Preview evidence (this stage, not candidate evidence) | Still needed at implementation |
|---|---|---|
| AC-1 (open in place, no new tab) | Playwright run against the live preview: `context.pages().length` unchanged (1→1) before/after click, popup opens inline. Verified on localhost only. | Same run against the shared-board-origin path (`JOURNEY_ALLOWED_HOSTS`) — not yet verified. |
| AC-2 (Markdown+Mermaid render, autonumber, no script execution) | Playwright run: rendered SVG contains `class="sequenceNumber"` text nodes `1`–`4` (dumped and inspected directly, not string-matched); `window.__popup_xss_fired` from an embedded `<script>` in the fixture stayed `false` after popup open. | Same fixture pattern ported into the candidate's own test fixtures. |
| AC-3 (Close/Escape restores focus, selection, viewport, diagram) | (Cycle 2) Playwright run with a **real pointer click** on the rendered Close button (`locator.click()`, not `.evaluate()` or a key press): dialog removed from DOM, focus returns to the exact trigger `<a>`, `editor.getSelectedShapeIds()` and `editor.getCamera()` identical before open and after close. `document.elementFromPoint` at the Close button's own bounding-box centre resolves to the button itself. Escape re-verified independently afterward (same assertions), confirming the portal fix preserved it. `verify-real-clicks.mjs` is the automated test; `verify.mjs` (cycle 1, Escape-only) kept for the Mermaid/no-new-tab regression it still proves. | Port `verify-real-clicks.mjs`'s real-click assertions into the candidate's test suite. |
| AC-4 (loading/unavailable/inaccessible/missing-heading, Open on GitHub always present) | Playwright run against 4 seeded links: bad ref → unavailable; bad path → unavailable; unmapped repo (D1 case) → unavailable; bad heading → missing-heading banner + chapter body. (Cycle 2) The bad-ref/unavailable state re-checked with the same real-click-and-hit-test method used for AC-3 — Close is hit-testable and click-closable there too, not only in the `ready` render. "Open on GitHub": `document.elementFromPoint` at its own bounding-box centre resolves to the link itself, and a real click opens a new tab targeting `target.sourceUrl` (`context.waitForEvent('page')`), confirming the control's actual effect, not just its presence in the DOM. | A genuinely private GitHub repo (the preview used an unmapped local repo as D1's analog, not a real private-repo denial). |
| AC-5 (export/import round trip readable in a viewer-less tldraw host) | Not exercised. Reasoning only: the chapter link lives in the shape's native `url` prop (`T.linkUrl`, confirmed in `TLNoteShape.mjs`), not custom metadata, so ordinary tldraw export/import and the stock `HyperlinkButton` render it identically with no popup present. | An actual export → import → open-in-bare-tldraw round trip. Not yet verified. |

## A seam worth recording precisely

tldraw's `useKeyboardShortcuts` hook binds a `keydown` listener on `document.body`
(bubble phase, confirmed in `useKeyboardShortcuts.mjs`) and calls `preventDefault()`
for its own shortcut handling, including Escape. Because a native `<dialog>`'s
"Escape closes the topmost modal" behavior is only triggered if the keydown event's
`defaultPrevented` is still `false` once the whole dispatch finishes, tldraw's handler
running anywhere in the bubble chain silently suppresses the browser's own dialog-
close — no `cancel` event ever fires. A React `onKeyDown` handler on the `<dialog>`
calling `stopPropagation()` does **not** fix this: React's delegated listener sits at
the root container, which is still a descendant of `body`, so by the time it runs the
event has already reached `body` in native bubble order. The fix verified in the
preview is a plain native `addEventListener('keydown', ..., { capture: true })`
attached directly to the dialog element in a `useEffect` — capture phase runs before
any bubble-phase listener anywhere, including tldraw's. This is exactly the contested
mechanism the preview exists to settle, and it would not have surfaced from reading
the code alone.

A second, smaller seam: `repo-doc.ts`'s ref resolution tries the raw ref and
`origin/<ref>` only. A branch containing `/` (e.g. `feature/foo`) is not yet handled —
the parser's single split between ref and path can pick the wrong boundary. Flagged
as an implementation obligation (progressive `rev-parse` over ref prefixes), not
solved here.

A third seam, the one this correction round exists to record: tldraw's
`InFrontOfTheCanvas` slot renders inside `.tl-canvas__in-front`
(`position: absolute; pointer-events: none`), itself inside `.tl-canvas`
(`contain: strict; overflow: clip`) — CSS confirmed by reading `tldraw.css`.
`pointer-events` is inherited down the DOM tree regardless of `showModal()`'s
top-layer paint promotion, so nothing rendered in that slot is ever hit-testable
unless it (or an ancestor inside the slot) explicitly sets `pointer-events: auto`.
Measured live with a script computing `getComputedStyle(el).pointerEvents` up the
Close button's ancestor chain: `button` → `.doc-popup-chrome` → `dialog.doc-popup`
→ `.tl-canvas__in-front` all read `none`, and `document.elementFromPoint` at the
button's own bounding-box centre returned `<html>` — the whole dialog, backdrop
included, was invisible to hit-testing, not just the Close button. This
contradicts the cycle-1 stage report's claim that "every ancestor computes
`pointer-events: auto`"; that claim did not reproduce against the unmodified
cycle-1 code and is superseded by this measurement.

## Unresolved decision for the Captain

**Repo → local-checkout mapping.** The canonical link carries `owner/repo`; the
server needs a local filesystem path for it. The preview uses an operator-supplied
env map, `JOURNEY_DOC_REPOS=owner/repo=/abs/path,owner2/repo2=/abs/path2`, verified
working for lookup, ref-not-found, and path-not-found. Recommendation: keep that as
the general mechanism, and add one zero-config default for the common case — when the
server's own checkout's `git remote get-url origin` matches the link's `owner/repo`,
use that checkout without requiring an env entry (this repo reviewing itself needs no
configuration at all). Open question for the Captain: is the env-map-only mechanism
acceptable for Pilot, or does "this repo reviews itself with zero config" need to be
in scope now rather than deferred? Either answer stays within Pilot; it changes the
implementation task list, not the profile.

## Obligations that would push this past Pilot — left to the Captain

- Any live `git fetch`/network access from the server (D1 assumes the checkout
  already holds the ref; keeping it that way is what keeps the credential-free
  guarantee load-bearing).
- A configuration UI for the repo→checkout map (env var is adequate for Pilot).
- Caching document content across requests (each `/repo-doc` call currently shells
  out to `git show` fresh; fine at review-session volume, not addressed here).
- Updating `human-led-review.md` lines 114-122 from deferred/"future" language to
  describe an implemented capability — a retained-document edit
  (`kc-dev-flow-2/references/retained-documents.md` practice applies), not performed
  in this stage.

## Preview the Captain can click

Built in a throwaway copy at `/tmp/cdp-preview-20260916` (not a git branch, not the
`kc-journey-map` worktree — confirmed `git -C <worktree> status --porcelain` empty
throughout). A disposable-preview banner renders at the top of the page and inside
every popup.

- Canvas: `http://localhost:3799/?room=captain-demo` — 5 labeled cards, each a note
  shape with a chapter link and a plain-text label naming what it demonstrates
  (AC-1/AC-2 happy path on `main`; D2's ref-pinning via the same doc on a `review`
  branch with a branch-only section; AC-4's bad-ref, bad-heading and unmapped-repo/
  D1 states). Click a card's link icon to open the popup; Escape or Close to return.
- Ports: API `5959` (not 3742, not the API default 5858), Vite `3799` (not 3742, not
  the default 3737) — confirmed free before use (`lsof`), confirmed distinct from the
  Captain's running instance on 3742 throughout.
- Processes: server `22739`→`22770` (`nohup npx tsx server/canvas-server.ts`, log at
  `/tmp/cdp-preview-20260916-server.log`), Vite `23407`→`23433` (log at
  `/tmp/cdp-preview-20260916-vite.log`). Stop with
  `kill 22739 22770 23407 23433`. The server runs under plain `tsx`, not `tsx watch` —
  a server-side edit needs a restart; client edits hot-reload via Vite.
- Env used: `JOURNEY_API_PORT=5959 JOURNEY_VITE_PORT=3799
  JOURNEY_ROOMS_DIR=/tmp/cdp-preview-20260916/.rooms
  JOURNEY_DOC_REPOS=demo-owner/demo-repo=/tmp/cdp-preview-20260916`.
- Reproducible checks: `/tmp/cdp-preview-20260916/verify.mjs` (cycle 1, AC-1/AC-2/
  no-new-tab/Mermaid Playwright assertions, still passing), `verify-real-clicks.mjs`
  (cycle 2, the real-pointer-click Close/Escape/Open-on-GitHub evidence — see
  "Correction" section below), and `/tmp/cdp-preview-20260916.patch` (regenerated
  against the current corrected state; diff against the real `kc-journey-map`
  package, for review without touching the worktree).
- The fixture document lives in a throwaway git repo initialized inside the preview
  copy itself (`git init` in `/tmp/cdp-preview-20260916`, unrelated to
  `kc-claude-plugins`), with a `main` and a `review` branch, demonstrating D1 (server
  reads its own local checkout) and D2 (ref pinning) without touching any real repo
  content.

## Stage Report: ideation

- DONE: Smallest useful end-to-end slice defined: who reads a document this way, and the real seams it crosses
  "Smallest useful end-to-end slice" section; seams named: shape-hyperlink UI, Vite proxy, Fastify route, local git checkout.
- DONE: The Captain's recorded D1 and D2 decisions are reflected as settled, not re-argued or re-opened
  D1/D2 cited and built on throughout (PRFAQ FAQ, sequence, preview env `JOURNEY_DOC_REPOS`, fixture's `main`/`review` branches); no alternative to D1/D2 proposed.
- DONE: PRFAQ and Mermaid present with matching actors, order, branches, approvals and stops
  "PRFAQ" and "Sequence" sections; actors (Reviewer, Client, Proxy, Server, Checkout) and branches (non-chapter URL, no-checkout/D1, ref-not-found, path-not-found, heading-not-found) match the AC table and the preview's verified states; stops marked `[STOP]`; no runtime approvals exist, stated explicitly.
- DONE: Acceptance criteria evidence named per AC, distinguishing what a browser run proves from what an HTTP or parser result proves
  "Acceptance evidence" table, one row per AC-1..AC-5, each naming the exact Playwright assertion or an explicit not-yet-verified statement — no AC range used.
- DONE: A preview the Captain can click: built in a throwaway checkout, served on a port that is neither 3742 nor the default 3737, and explicitly labelled disposable rather than the candidate
  `http://localhost:3799/?room=captain-demo`, ports 5959/3799 confirmed free and distinct from 3742/3737/5858 via `lsof` before use; disposable banner in page header and popup chrome; `git -C <worktree> status --porcelain` empty after all work.
- DONE: Any obligation that would push this past Pilot identified and left to the Captain, not absorbed
  "Obligations that would push this past Pilot" section: server-side git fetch, repo-map config UI, content caching, the `human-led-review.md` retained-document update.
- DONE: Unresolved decisions identified for the Captain rather than decided by the worker
  "Unresolved decision for the Captain" section: repo→checkout mapping mechanism (env-map-only vs. adding a self-checkout zero-config default), with a recommendation and the concrete question.

### Summary

Ideation for issue #465 (canvas-document-popup): PRFAQ, Mermaid sequence, and a
per-AC evidence table built on the Captain's settled D1/D2. The existing-code check
found `@tldraw/mermaid`'s `createMermaidDiagram` unsuitable (mutates the store) and
confirmed `marked`/`dompurify`/`mermaid` are already transitive dependencies, so the
popup needs no new heavy dependency beyond `github-slugger` for heading anchors. A
disposable preview at `/tmp/cdp-preview-20260916` (ports 5959/3799, a `captain-demo`
room with five labeled cards) demonstrates the full open→render→Escape-close loop
with real Playwright evidence: no new tab, Mermaid autonumber renders, an embedded
script does not execute, focus/selection are restored, and all four AC-4 states
render with Open on GitHub retained. The one genuine bug the preview caught —
tldraw's own Escape handler silently suppressing the browser's native dialog-close —
is recorded as a seam with its fix and the greppable symbol that explains it. AC-1's
shared-board-origin path and AC-5's export/import round trip are named as not yet
verified, for implementation to close.

## Material finding — the Close control does not work

Reported by the Captain on the disposable preview: the popup could not be closed.
FO reproduced it against the same preview on port 3799.

**Observed.** With the popup open, the Close button is present, visible, and has a
sane bounding box (`x 1036.9, y 151.5, w 50.1, h 21` at a 1440x900 viewport).
`playwright` clicking it times out and the dialog stays open. The decisive
measurement: `document.elementFromPoint` at that button's own bounding-box centre
returns `<html>`. Every ancestor in the chain computes `pointer-events: auto`, so this
is not a pointer-events problem — nothing inside the dialog is hit-testable where the
dialog is painted.

**Mechanism.** The popup calls `showModal()`, which promotes the dialog into the top
layer, while being rendered inside tldraw's `InFrontOfTheCanvas` slot, inside
`.tl-container`. The painted position and the hit-test geometry disagree, so pointer
events never reach the dialog's contents.

**Why the stage's own evidence missed it.** The stage reported "verified via real
Playwright runs … focus/selection restored, all four AC-4 states correct". Those runs
exercised Escape, which is delivered to the focused element and does not go through
hit-testing. Escape closing the dialog is reproducible; the Close button was never
actually clicked. A keyboard path passing is not evidence a pointer path works.

**Classification: Material.** Released user and normal workflow: the Captain, reading
a document on the canvas. Observable harm: the popup cannot be dismissed by the
control the design says to provide. Affected value acceptance criterion: `value-ac[AC-3]`
("Closing the popup — by the Close control and by Escape") and `value-ac[AC-4]`
("Open on GitHub stays available in every one of them" — the same controls row).
Trigger evidence: the reproduction above.

Scope and profile are unchanged; the design's D1 and D2 are untouched by this. The
correction is where the dialog lives in the component tree, not what it fetches.

## Correction — the dialog now mounts outside tldraw's canvas subtree

**Root cause, measured fresh (see the third seam above).** The cycle-1 "every
ancestor computes `pointer-events: auto`" claim did not reproduce. A live
`getComputedStyle` walk of the Close button's ancestor chain, against the
unmodified cycle-1 code, showed `pointer-events: none` inherited from
`.tl-canvas__in-front` (tldraw's `InFrontOfTheCanvas` wrapper, deliberately
click-through by default so canvas-space overlays don't block the canvas
underneath them) down through `.doc-popup`, `.doc-popup-chrome`, and the Close
button itself — none of it overridden. `document.elementFromPoint` at the
button's centre landed on `<html>` because nothing in the dialog's subtree was
hit-testable at all, not because of a top-layer/containing-block geometry
mismatch.

**Mechanism chosen: `createPortal(<DocPopup .../>, document.body)`, rendered as
a sibling of `.tl-container` instead of inside `InFrontOfTheCanvas`.** `DocPopup`
itself is unchanged — same `<dialog>`, same `showModal()`, same capture-phase
Escape fix from the seam above. Only its React mount target moved
(`server/client/App.tsx`): the `Tldraw` component's `components.InFrontOfTheCanvas`
slot is removed; the popup's open/closed `useState` still lives in `RoomCanvas`,
and the portal is rendered as a sibling of `<Tldraw>`.

**Why a portal instead of a local `pointer-events: auto` override.** A CSS
override on `.doc-popup` alone would have closed this specific measured gap, but
would have left the dialog nested inside `.tl-canvas__in-front`, which also wires
`onPointerDown`/`onPointerUp` to `editor.markEventAsHandled` — a coupling meant
for canvas-space annotations, not a viewport-level modal that has no
relationship to the canvas's pan/zoom or tool state. `InFrontOfTheCanvas` exists
for content that overlays the canvas and may need editor context; `DocPopup`
needs neither — it never reads `editor` and never needs to move with the camera.
Portaling to `document.body` removes the slot's entire opt-out-by-default
contract (pointer-events, the handled-event coupling, and any future tldraw
z-index layer it could collide with) in one change, rather than defeating one
symptom of being in the wrong place.

**Re-verification method fix.** `verify-real-clicks.mjs` (new,
`/tmp/cdp-preview-20260916/verify-real-clicks.mjs`) replaces "press Escape and
call that verification" with real `locator.click()` calls on the rendered Close
button and the "Open on GitHub" link — the same input path a person uses — and
asserts the control's effect: the dialog element is gone from the DOM, focus is
on the original trigger, canvas selection and camera are byte-identical, and (per
this round's specific ask) `document.elementFromPoint` at each control's own
bounding-box centre resolves to that control or a descendant of it, for both the
Close button and the Open-on-GitHub link. Escape is re-verified independently in
the same run rather than assumed to still work post-fix. All 9 assertions pass;
full output is in the cycle-2 stage report below. The AC-4 unavailable-state
render was spot-checked with the same real-click method (Close is hit-testable
and click-closable there too, not only in the `ready` state).

**What did not change.** `DocPopup.tsx`'s data fetching, Markdown/Mermaid
rendering, sanitization, and heading-scroll logic; the Escape capture-phase fix;
D1/D2; scope; acceptance criteria; ports (server `5959`, Vite `3799`, both
already confirmed free and distinct from `3742`/`3737`/`5858` in cycle 1, and
still the only listeners on those ports — `lsof` re-checked before this round's
runs). The Vite dev server picked up `App.tsx` via HMR; no restart was needed
(confirmed via the dev server's own log timestamps advancing past the edit).
`git -C <the real kc-journey-map worktree> status --porcelain` is empty — only
the disposable copy at `/tmp/cdp-preview-20260916` was touched.

**Not verified in this round, unchanged from cycle 1.** AC-1's shared-board-origin
path and AC-5's export/import round trip — neither is affected by where the
dialog mounts, and neither was in scope for this correction.

## Stage Report: ideation (cycle 2)

This cycle is a correction round; the checklist below is the standing ideation
checklist, not a rewrite of it — items untouched by the Close-control defect are
marked DONE with a pointer back to the unaffected cycle-1 evidence, since D1/D2,
scope and profile were explicitly out of bounds for this round.

- DONE: Smallest useful end-to-end slice defined: who reads a document this way, and the real seams it crosses
  Unaffected by this round; cycle-1 "Smallest useful end-to-end slice" section still holds. Portaling the dialog to `document.body` changes a DOM mount point, not a seam the slice crosses.
- DONE: The Captain's recorded D1 and D2 decisions are reflected as settled, not re-argued or re-opened
  Untouched, per the dispatch's explicit instruction. No edits to D1/D2 or their supporting "Architecture facts" section this round.
- DONE: PRFAQ and Mermaid present with matching actors, order, branches, approvals and stops
  Untouched; the Close/Escape branch in the "Sequence" diagram already reads "Close control OR Escape" and needs no change — the fix is where the dialog mounts, not the interaction contract.
- DONE: Acceptance evidence named per AC, distinguishing what a browser run proves from what an HTTP or parser result proves
  AC-3 and AC-4 rows in "Acceptance evidence" rewritten this round: real `locator.click()` on Close and on Open-on-GitHub (not Escape, not `.evaluate()`), asserting dialog removal / restored focus+selection+camera / a real new-tab open, plus the `elementFromPoint`-at-centre check this round specifically requires. `verify-real-clicks.mjs` → `ALL 9 CHECKS PASSED`; `verify.mjs` (cycle 1) re-run clean as a regression check (no new tab, Mermaid renders, script doesn't fire).
- DONE: A preview the Captain can click: built in a throwaway checkout, served on a port that is neither 3742 nor the default 3737, and explicitly labelled disposable rather than the candidate
  Same disposable checkout and ports reused (server 5959, Vite 3799; `lsof` re-confirmed only those listeners on 5959/3799, 3742 untouched), per the dispatch's instruction to keep the preview disposable on its existing non-conflicting ports. `server/client/App.tsx` edited to portal `DocPopup` to `document.body`; picked up via Vite HMR, no restart. `git -C <real kc-journey-map worktree> status --porcelain` empty.
- DONE: Any obligation that would push this past Pilot identified and left to the Captain, not absorbed
  Untouched; "Obligations that would push this past Pilot" section unaffected by a DOM-mount-point fix.
- DONE: Unresolved decisions identified for the Captain rather than decided by the worker
  Untouched; the repo→checkout mapping question in "Unresolved decision for the Captain" is unaffected by this round.

### Summary

Root cause was not the top-layer/containing-block geometry the cycle-1 report guessed — a fresh `getComputedStyle` measurement showed `pointer-events: none` inherited unbroken from tldraw's `.tl-canvas__in-front` wrapper down to the Close button, making the entire dialog non-hit-testable; the cycle-1 "every ancestor computes auto" claim did not reproduce and is superseded. Fix: portal `DocPopup` to `document.body`, fully outside tldraw's DOM subtree, rather than patching `pointer-events` locally, because the slot's opt-out-by-default contract (pointer-events plus an `editor.markEventAsHandled` coupling) doesn't fit a canvas-independent modal. Re-verification replaced Escape-only checks with real pointer clicks on both interactive controls, plus the specific `elementFromPoint`-at-centre assertion this round asked for; all pass, including a spot-check that Close remains clickable in the AC-4 unavailable-state render. Real kc-journey-map worktree untouched; only the disposable preview was edited.
