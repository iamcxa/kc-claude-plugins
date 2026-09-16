# ideation gate — canvas-document-popup

FO recommendation: **approve, with the one open question answered.**

## FO verification

Checked rather than accepted on report:

- The preview answers on `http://localhost:3799/?room=captain-demo` (HTTP 200).
- The Captain's own canvas on port 3742 is still answering (HTTP 200) and was not
  disturbed.
- The real worktree is clean: no preview artifact leaked into it.
- The design is committed at `5635f8fc` on the state branch, 255 lines.
- The tldraw symbol the Escape finding names,
  `tldraw/dist-esm/lib/ui/hooks/useKeyboardShortcuts.mjs`, exists.

## Design summary

Built on the Captain's settled D1 (server reads the checkout) and D2 (`git show
<ref>:<path>`). One new server route plus one Vite proxy entry, following the existing
`/connect` pattern. `marked`, `dompurify` and `mermaid` are already transitive
dependencies; only `github-slugger` is new. `@tldraw/mermaid`'s `createMermaidDiagram`
was rejected because it mutates the store.

One substantive discovery: tldraw's own keyboard handling swallows the browser's
native dialog-close on Escape, so the popup needs a capture-phase listener on the
dialog. Found by running the preview, not by reading.

## Open question for the Captain

**Repo → local-checkout mapping.** The link carries `owner/repo`; the server needs a
path. The preview uses an operator env map,
`JOURNEY_DOC_REPOS=owner/repo=/abs/path,...`, verified for lookup, ref-not-found and
path-not-found.

- **Option 1 — env map only.** Smallest. This repository reviewing its own documents
  still needs an env entry.
- **Option 2 — env map plus one zero-config default**: when the server checkout's
  `git remote get-url origin` matches the link's `owner/repo`, use that checkout. This
  repository reviewing itself then needs no configuration at all.

The worker recommends option 2. Either answer stays inside Pilot; it changes the
implementation task list, not the profile.

## Obligations the worker left to the Captain rather than absorbing

Live `git fetch` from the server; a configuration UI for the map; cross-request
document caching; and updating `human-led-review.md` lines 114-122 from deferred
language to describing an implemented capability. None is taken into scope here.
FO agrees none should be: the first would break the credential-free guarantee D1
rests on, and the last is a retained-document edit with its own practice.

## Limit

The preview is disposable and proves the interaction loop, not the candidate. No
product code exists yet.
