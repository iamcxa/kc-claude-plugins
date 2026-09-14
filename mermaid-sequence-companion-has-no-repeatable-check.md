---
title: "The Mermaid sequence companion has no repeatable in-repo check, so the journey map cannot rely on Mermaid"
status: backlog
source:
product: kc-journey-map
planning-window:
planning-outcome:
sprint:
sprint-readiness: defer
started:
completed:
verdict:
worktree:
issue:
pr: 440
mod-block:
id: n2wd7aavte2k7p7nfj3aa2r5
---

PR #440 (`codex/journey-mermaid`, head `cfb804d64f1e0ef35862505ee68c26c51c176076`) adds a Mermaid
sequence companion to the journey canvas: `@tldraw/mermaid` pinned to 5.4.0, a new browser
entrypoint `addSequencePage` in `kc-journey-map/server/client/sequence.ts`, `window.addSequencePage`
wiring in `App.tsx`, `scripts/sequence-smoke.mjs`, and the `references/sequence.md` reference.

No check in this repository exercises any of it. `.github/workflows/kc-journey-map-tests.yml` runs
`node --test lib/*.test.mjs` and `scripts/canvas-smoke.sh`; both are server- and model-side, and
`canvas-smoke.sh` never loads the client bundle. `kc-journey-map/tsconfig.json` sets `strict` and
`noEmit` over `server`, but no npm script and no CI step invokes `tsc`, and `package.json` has no
`build` or `typecheck` script, so the PR body's "production build" claim has no in-repo command
behind it. `scripts/sequence-smoke.mjs` needs `agent-browser` plus a frontend and API pair the
operator starts by hand, and its path is not in the workflow's filter, so it never runs
unattended. Every validation line in the PR body is an author-run observation at a SHA no
automated check can re-reach.

## Accepted outcome

The Mermaid sequence companion is verified at a pinned SHA by a check this repository can re-run,
and the journey map can use Mermaid without that evidence depending on one operator's machine. The
client typecheck and the production bundle become in-repo commands wired into
`kc-journey-map-tests.yml`, and the browser smoke is reachable by a documented invocation whose
path appears in the workflow's trigger filter even if the browser leg stays operator-run.

## Non-goals

* Changing the converter pin, the Mermaid dialect, or `addSequencePage`'s semantics.
* Reverse synchronization from canvas to `.mmd`, or a lossless exporter.
* Marking PR #440 ready, merging it, or any version bump.
* Adding a browser-driving job to CI if its measured per-PR cost is not stated.

## Acceptance criteria

* **AC-1** `npm ci && npx tsc` in `kc-journey-map` exits 0 at PR #440's head, and a named npm
  script plus a CI step in `kc-journey-map-tests.yml` runs it. A mutation that breaks
  `server/client/sequence.ts` types makes that step fail.
* **AC-2** A production client bundle is produced by a named npm script, runs in CI, and the
  dynamic `@tldraw/mermaid` import resolves; a mutation removing the dependency makes it fail.
  The added bundle weight of the Mermaid chunk is reported as a measured number.
* **AC-3** `node scripts/sequence-smoke.mjs <origin>` passes against an isolated frontend and API
  pair at PR #440's head, with the receipt naming the ports, the `JOURNEY_ROOMS_DIR`, the room id,
  and each of its seven assertions. `kc-journey-map/scripts/sequence-smoke.mjs` and
  `server/client/**` are in the workflow's `paths` filter.
* **AC-4** `editor.getTextOptions()`, `editor.options.maxPages`, and `createMermaidDiagram`'s
  `blueprintRender` option are confirmed to exist in the installed `tldraw@5.4.0` and
  `@tldraw/mermaid@5.4.0` type declarations, cited by symbol.
* **AC-5** The `kc-journey-map` SKILL.md `description` trigger delta is dispositioned: PR #440
  drops `產出 journey 圖` and `現況跟 journey 對不對` from the trigger list while adding
  `sequence companion`. Either both dropped triggers are restored, or the PR body records the
  Captain's decision to drop them.
