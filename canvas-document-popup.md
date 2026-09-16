---
id:
title: read a Markdown and Mermaid document in a journey-canvas popup
status: backlog
variant: kc-dev-flow-2
profile:
merge: pr
worktree:
pr:
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
