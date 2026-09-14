---
title: "The Mermaid sequence companion has no repeatable in-repo check, so the journey map cannot rely on Mermaid"
status: done
source:
product: kc-journey-map
planning-window:
planning-outcome:
sprint: journey-map-mermaid-companion
sprint-readiness: ready
started: 2026-09-14T08:57:36Z
completed: 2026-09-14T09:13:22Z
verdict: PASSED
worktree: .worktrees/spacedock-ensign-mermaid-sequence-companion-has-no-repeatable-check
issue:
pr: local-merge:1ea1a2ae
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
        - id: gate:n2wd7aavte2k7p7nfj3aa2r5:validation
          stage: validation
          attempts:
            - id: gate-attempt:n2wd7aavte2k7p7nfj3aa2r5-validation-1
              briefing:
                id: briefing:n2wd7aavte2k7p7nfj3aa2r5:validation:attempt-1:revision-1
                digest: sha256:a7ab82eaae46bc0ea1ce34b27bd31e073ead05c836fa428b38b93e6fcefdf56c
                room-ref: ./mermaid-sequence-companion-has-no-repeatable-check/review/validation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:n2wd7aavte2k7p7nfj3aa2r5:validation:1
                briefing: briefing:n2wd7aavte2k7p7nfj3aa2r5:validation:attempt-1:revision-1
                by: person:captain
                at: "2026-09-14T09:12:56.795946Z"
                decision: approve
                reason: 'POC outcome accepted. The Captain ruled in chat 2026-09-14 「不用再跑，codex 單獨跑過可以用」: no second fresh validation worker, and the Mermaid sequence companion is accepted as working at cfb804d. AC-2/3/4 hold on the implementation receipt; AC-1''s failure is a pre-existing declaration-file gap the FO re-derived on origin/main and is not this PR''s defect; AC-5 stays an open ask against PR #440. The Captain also ruled 「型別檢查修復」, which the FO carries forward as a separate item. This POC produced no candidate; PR #440 remains Draft and unruled.'
              application:
                target-stage: done
                state: consumed
archived: 2026-09-14T09:13:22Z
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

## Stage Report: implementation

- DONE: Reset this worktree to PR #440's pinned head cfb804d64f1e0ef35862505ee68c26c51c176076 and record `git rev-parse HEAD` in the receipt before running anything.
  Confirmed `HEAD is now at cfb804d6`; recorded in receipt.md.
- DONE: AC-1 — run `npm ci && npx tsc` in kc-journey-map; record exit code. Then apply a throwaway type-breaking edit to server/client/sequence.ts, re-run `npx tsc`, record that it exits nonzero and name the error, and revert the edit.
  `npx tsc` exits 2 even before the mutation (pre-existing `lib/records.mjs` TS7016, unrelated to this PR) — AC-1 fails as written; the mutation itself does add the expected `sequence.ts` TS2322 and was cleanly reverted (`git diff --stat` empty).
- DONE: AC-2 — build a production client bundle with `npx vite build`; record the command, exit code, the emitted chunk list, and the measured byte size of the Mermaid chunk and of the total bundle. Confirm the dynamic `@tldraw/mermaid` import resolves in the output. Then remove `@tldraw/mermaid` from package.json dependencies, re-run the build, record that it fails, and revert.
  Build exit 0, total dist 5,391,377 bytes, deterministic on rebuild; dynamic import resolves to `dist-esm-DTH9OtbL.js` exporting `createMermaidDiagram`; Mermaid weight reported as 1,924,564–3,398,433 bytes (method disclosed, no clean diff obtainable since the mutation build fails outright rather than producing a leaner bundle); mutation build exits 1 (rolldown fails to resolve `@tldraw/mermaid`); package.json and package-lock.json both restored, `npm ci` reinstalled the dependency, rebuild matched the original byte-for-byte.
- DONE: AC-3 — start an isolated frontend and API pair for the test with a dedicated JOURNEY_API_PORT, a temporary JOURNEY_ROOMS_DIR, and a matching VITE_JOURNEY_API_URL; run `node scripts/sequence-smoke.mjs <origin>`; record both ports, the rooms dir, the room id, the script's JSON output, and the pass/fail of each of its seven assertions. If `agent-browser` is unavailable, say so plainly and mark AC-3 unmet — do not substitute a different check.
  `agent-browser` 0.32.0 present and used; API on port 58234 with JOURNEY_ROOMS_DIR=/tmp/journey-rooms-smoke-mermaid-poc, frontend on port 58235 with matching VITE_JOURNEY_API_URL; script exit 0, all 13 assert() call sites passed (the script has 13, not 7 — noted and itemized in the receipt), full JSON output recorded.
- DONE: AC-4 — confirm `editor.getTextOptions()`, `editor.options.maxPages`, and `createMermaidDiagram`'s `blueprintRender` option each exist in the installed tldraw@5.4.0 and @tldraw/mermaid@5.4.0 type declarations; cite each by greppable symbol and the declaration file it was read from.
  All three confirmed in `@tldraw/editor/dist-cjs/index.d.ts` and `@tldraw/mermaid/dist-cjs/index.d.ts`, cited by symbol.
- DONE: AC-5 — diff the kc-journey-map SKILL.md description between origin/main and cfb804d; confirm whether 產出 journey 圖 and 現況跟 journey 對不對 are dropped and sequence companion added; report the exact before/after trigger lists. Do not edit SKILL.md.
  Both triggers confirmed dropped, `sequence companion` confirmed added; `gh pr view 440 --json body` read in full and contains no mention of the drop — AC-5 fails as written (neither restore nor disposition happened).
- DONE: Write the receipt with every command verbatim, its exit code, and its output excerpt. State plainly which ACs hold, which fail, and which could not be run. Never report an AC as met from the PR body's claims.
  Receipt written to `.spacedock-state/mermaid-sequence-companion-has-no-repeatable-check/implementation/receipt.md`; every command and exit code re-derived independently, none taken from the PR body.

### Summary

At PR #440's pinned head, AC-2, AC-3, and AC-4 hold with independently re-derived evidence; AC-1 and
AC-5 fail. AC-1 fails for a reason unrelated to this PR (a pre-existing `lib/records.mjs` declaration
gap already breaks `tsc` before any mutation is applied) but the AC's falsifier mechanism does still
work once tested. AC-5 fails because the PR drops two SKILL.md triggers without dispositioning the
drop in its body. No product code, CI, or npm scripts were changed; all throwaway mutations were
reverted and the worktree is clean at `cfb804d64f1e0ef35862505ee68c26c51c176076`.
