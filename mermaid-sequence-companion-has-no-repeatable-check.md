---
title: "The Mermaid sequence companion has no repeatable in-repo check, so the journey map cannot rely on Mermaid"
status: implementation
source:
product: kc-journey-map
planning-window:
planning-outcome:
sprint: journey-map-mermaid-companion
sprint-readiness: ready
started:
completed:
verdict:
worktree:
issue:
pr: 440
mod-block:
id: n2wd7aavte2k7p7nfj3aa2r5
gates:
    version: 1
    records:
        - id: gate:n2wd7aavte2k7p7nfj3aa2r5:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:n2wd7aavte2k7p7nfj3aa2r5-backlog-1
              briefing:
                id: briefing:n2wd7aavte2k7p7nfj3aa2r5:backlog:attempt-1:revision-1
                digest: sha256:2d069b2db454bc8c7f6aa33b3e2577251b43b5a1bb81bec8668108c36e6578ba
                room-ref: ./mermaid-sequence-companion-has-no-repeatable-check/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:n2wd7aavte2k7p7nfj3aa2r5:backlog:1
                briefing: briefing:n2wd7aavte2k7p7nfj3aa2r5:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-14T08:55:58.777138Z"
                decision: approve
                reason: 'Captain approved in chat 2026-09-14 with 「ok poc」 after the FO presented the #440 review, the coverage gap, the task, and the coupled scope question. Selecting POC ruled the scope question the same way: the CI wiring in AC-1/AC-2 of the first draft was removed and carried as a residual, because a POC runs the check once rather than building the gate. Sprint uses the task-scoped slug journey-map-mermaid-companion, which needs no ROADMAP registration on this workflow''s existing convention.'
              application:
                target-stage: ideation
                state: consumed
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
operator starts by hand. Every validation line in the PR body is an author-run observation that
nothing in the repository can re-reach.

## Accepted outcome

One independent run at PR #440's pinned head establishes whether the Mermaid sequence companion
works, so the journey map can use Mermaid on the Captain's own machine. Evidence is a receipt
naming the commands, the isolated ports and room, and each assertion — not a restatement of the
author's observations.

## Non-goals

* Wiring any of these checks into CI, adding npm scripts, or editing the workflow's `paths` filter.
* Changing the converter pin, the Mermaid dialect, or `addSequencePage`'s semantics.
* Reverse synchronization from canvas to `.mmd`, or a lossless exporter.
* Marking PR #440 ready, merging it, or any version bump.

## Acceptance criteria

* **AC-1** At `cfb804d`, `npm ci && npx tsc` in `kc-journey-map` exits 0; a mutation that breaks
  `server/client/sequence.ts` types makes the same command exit nonzero.
* **AC-2** At `cfb804d`, a production client bundle builds (`npx vite build`) and the dynamic
  `@tldraw/mermaid` import resolves in the output; the Mermaid chunk's added weight is reported as a
  measured number. A mutation removing the dependency makes the build fail.
* **AC-3** At `cfb804d`, `node scripts/sequence-smoke.mjs <origin>` passes against a frontend and
  API pair started for the test, with the receipt naming both ports, the `JOURNEY_ROOMS_DIR`, the
  room id, and each of its seven assertions.
* **AC-4** `editor.getTextOptions()`, `editor.options.maxPages`, and `createMermaidDiagram`'s
  `blueprintRender` option are each confirmed present in the installed `tldraw@5.4.0` and
  `@tldraw/mermaid@5.4.0` type declarations, cited by symbol.
* **AC-5** The SKILL.md `description` trigger delta is dispositioned: PR #440 drops
  `產出 journey 圖` and `現況跟 journey 對不對` while adding `sequence companion`. Either both dropped
  triggers are restored, or the PR body records the decision to drop them.

## Residual carried to the Captain

Wiring the typecheck and the bundle build into `kc-journey-map-tests.yml`, and adding
`scripts/sequence-smoke.mjs` to its `paths` filter, were in this task's first draft and were
removed when the Captain selected POC on 2026-09-14: a POC runs the check once, it does not build
the gate. Nothing has bitten yet, so no CI step is justified on evidence today. `server/client/**`
needs no filter entry — the existing `server/**` pattern already covers it.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: poc-exploration
  recommended: poc-exploration
  route: [build, prove]
  basis: The candidate already exists as PR #440; the only open question is whether it works at a commit someone else can re-reach.
  obligations:
    architecture: []
    implementation: [No product change; mutations exist only to prove AC-1 and AC-2 can fail]
    testing: [AC-1..AC-5]
  scope_boundary: No CI edit, no npm script, no change to kc-journey-map product code beyond throwaway mutations.
  semantics_unchanged: true
  poc_decision: whether the Mermaid sequence companion works at cfb804d, so the journey map can use Mermaid
  poc_falsifier: a check fails at the pinned head, or a claimed tldraw/@tldraw/mermaid symbol does not exist
  poc_budget: one worker, no PR of its own
  poc_stop_when: AC-1..AC-5 each hold or fail at cfb804d with a receipt
  poc_artifact: retained
  poc_safety_boundary: a throwaway worktree at cfb804d; no push to codex/journey-mermaid, no GitHub write
  poc_decision_ready_minutes: 30
```
