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
