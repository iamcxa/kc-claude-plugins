---
id: g87dzxbq3j3rdwzneqr4g5nt
title: Ask which boards to draw, and default to the user journey alone
status: implementation
source: captain
product: kc-team-ops
planning-window:
planning-outcome:
sprint: journey-map-poc
sprint-readiness: ready
started: 2026-09-10T03:28:44Z
completed:
verdict:
worktree: .worktrees/spacedock-ensign-default-to-the-journey-alone
issue:
pr:
mod-block:
gates:
    version: 1
    records:
        - id: gate:g87dzxbq3j3rdwzneqr4g5nt:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:g87dzxbq3j3rdwzneqr4g5nt-backlog-1
              briefing:
                id: briefing:g87dzxbq3j3rdwzneqr4g5nt:backlog:attempt-1:revision-1
                digest: sha256:ed32b487f4e99d5ea7f2d585335879fade38136431bd574a3fab353dbcb829c9
                room-ref: ./default-to-the-journey-alone/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:g87dzxbq3j3rdwzneqr4g5nt:backlog:1
                briefing: briefing:g87dzxbq3j3rdwzneqr4g5nt:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-10T03:27:59.208817Z"
                decision: approve
                reason: 'Captain: 同意 — approving the two-part split he proposed, of which this is part one: keep the skeleton able to draw all three originally-defined boards, ask through a multi-select, and default to the user journey alone. Integration is explicitly part two and excluded here.'
              application:
                target-stage: ideation
                state: consumed
---

## The problem

The tool decides for the user which boards appear. The story map always renders, and the
function map renders whenever the file happens to carry a command or an event — a hidden
rule nobody asked for and nobody can see. The captain wants the opposite default: one board
unless you say otherwise.

All three projections already exist in the tree. This is a defaults-and-choice task, not a
rebuild: the skeleton keeps its ability to draw the journey board and the function map, and
loses its licence to draw them uninvited.

## Work profile receipt

**Profile:** POC — bounded exploration.

**Next decision:** whether one default board plus an explicit choice is enough, before any
integration work is admitted.

**Cheapest credible falsifier:** render the worked example three ways — default, journey
board added, function map added — and confirm the default carries exactly one board.

**Budget:** one worker dispatch. Browser work only if the host load is under 40.

**Observable stop point:** the three renders and their page lists.

## Accepted outcome

The user is asked which boards to draw, may choose more than one, and gets the user journey
alone when they say nothing.

## Non-goals

- No integration with plan-flow, dev-flow or spacedock. That is the next task and it must
  not leak into this one.
- No `journey:` field on a dev task, and no reading of task state.
- Do not change what any board draws. Only which ones are drawn, and on whose say-so.
- Do not delete a projection. All three stay in the tree.

## Acceptance evidence

**AC-1** Rendering with no selection produces exactly one board, the story map. The
function map does not appear merely because the file carries command or event fields.

**AC-2** A selection may name more than one projection, and each named one is drawn.

**AC-3** The skill asks the question through the host's selection UI rather than guessing,
and the question offers all three with the journey preselected.

**AC-4** All three projections still render correctly when selected. A projection that
regressed while being made optional fails this criterion.

**AC-5** The worked example renders three ways — default, plus journey board, plus function
map — and the page list of each is recorded.

## Route-back conditions

Return `poc_outcome` to planning. The integration skill is a separate item.

## Measurement

The page list of the default render. One board, or the task did not do its job.

## Stage Report: implementation

- DONE: Ask which projections to draw through the host's selection UI, allow more than one, and preselect the user journey.
  `kc-team-ops/skills/kc-journey-map/SKILL.md` § Rendering now specifies an `AskUserQuestion` multi-select (`User journey` preselected, `Journey board`, `Function map`) before rendering; the answer maps 1:1 to `journey-render.mjs --pages`.
- DONE: Render with no selection and prove exactly one board appears — the function map must not arrive uninvited because the file carries a command field.
  `buildAllPages(model)` (no selection arg) on the fixture (which carries `command`/`events`/`state`/`readmodel`) draws `['page:page']` only — test `with no selection, buildAllPages draws the story map alone` in `kc-team-ops/lib/read.test.mjs`; verified again end to end through the real canvas server against the worked example: readback page list `["Story map"]`.
- DONE: Render the worked example three ways and record the page list of each, keeping all three projections working.
  Through the real canvas server (no browser; host load was 38.32/65.10/73.85, so per the browser gate I proved page lists directly): default -> `["Story map"]`; `--pages story-map,journey-board` -> `["Story map","RELEASE 1 — what is missing","RELEASE 2 — what is missing","RELEASE 3 — what is missing"]`; `--pages story-map,function-map` -> `["Story map","Function map"]`. All three selected together reproduces the worked example's existing 5-page `draw-a-journey.tldr` exactly (`scripts/canvas-smoke.sh`, green: 135 shapes across 5 pages).

### Summary

`buildAllPages` in `kc-team-ops/lib/render.mjs` now takes an explicit `selection` from `{story-map, journey-board, function-map}` (`PROJECTIONS`/`PROJECTION_KEYS`/`DEFAULT_PROJECTIONS`), defaulting to `story-map` alone — including when an explicit empty array is passed, which otherwise would have let `renderToRoom`'s reconcile wipe every existing journey shape from a room. `journey-board`, retired from the default render path in a preceding commit (`b997dfdd`) in favour of the generated release contract, is reinstated as opt-in only, reproducing its pre-retirement per-release/whole-journey behavior verbatim (confirmed against `ca8de3da`'s prior `buildAllPages`). `function-map`'s old "draw only if the file models something" gate is dropped per review: selection is now the only gate, per AC-2 and the assignment's own framing of that gate as the defect. Updated `journey-render.mjs` (`--pages` flag, rejects an unknown key with exit 2), `canvas-smoke.sh` (exercises all three projections), and the skill's docs (`SKILL.md`, `canvas.md`, `cell-contract.md`, `example/README.md`) to stop describing the journey board as retired. 42 unit tests pass (`node --test lib/*.test.mjs`); four hand-run mutations (default includes function-map; journey-board loses per-release branching; function-map regains its modelled gate; function-map reuses story-map's shape ids) were each caught by name before being reverted. Residual not fixed: re-rendering a room with a narrower selection removes the other projections' shapes but leaves their now-empty pages behind (pre-existing reconcile behavior, made newly reachable by selection — not part of this task's scope, which is which boards draw, not what reconcile does with a page).
