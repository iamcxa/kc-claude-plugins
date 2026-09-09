---
id: rzqf2brz01krek0pdmz8cbnt
title: Collapse to one board, and generate the per-release contract that replaces the other
status: implementation
source: captain
product: kc-team-ops
planning-window:
planning-outcome:
sprint: journey-map-poc
sprint-readiness: ready
started: 2026-09-09T07:39:54Z
completed:
verdict:
worktree: .worktrees/spacedock-ensign-collapse-to-one-board
issue:
pr:
mod-block:
gates:
    version: 1
    records:
        - id: gate:rzqf2brz01krek0pdmz8cbnt:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:rzqf2brz01krek0pdmz8cbnt-backlog-1
              briefing:
                id: briefing:rzqf2brz01krek0pdmz8cbnt:backlog:attempt-1:revision-1
                digest: sha256:f4f5cc0cc7d58414dffc892090b3406d7778c6ba1d439fef67fb367a3a5d6ae1
                room-ref: ./collapse-to-one-board/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:rzqf2brz01krek0pdmz8cbnt:backlog:1
                briefing: briefing:rzqf2brz01krek0pdmz8cbnt:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-09T07:39:23.210261Z"
                decision: approve
                reason: 'Captain: 開票，我想盡快看到新版結果 — approving the absorb-and-collapse seed and asking for the new format quickly. Scope constraints recorded from his prior rulings: cross-repository evidence is a separate task, the function map leaves the flow but not the tree, and the skill''s own journey must survive the migration.'
              application:
                target-stage: ideation
                state: consumed
---

## The problem

Three boards were built. Two of them have never been used by anyone but their author, and
the captain's attention has stayed on the story map throughout — that is the users' vote.
An independently drawn board of the same system, made by another engineer in one canvas,
carried four things ours cannot and needed only one page to do it.

The journey board's unique content is a citation and a constraint list. Neither is spatial,
so neither needs a board; the grid's value was never the picture, it was the schema. A
schema survives as a generated document, and a required field left empty can be checked by a
program, which is stronger than a person noticing a gap in a grid.

## Work profile receipt

**Profile:** POC — bounded exploration.

**Next decision:** whether one board plus a generated contract carries everything three
boards carried, judged on this skill's own journey.

**Cheapest credible falsifier:** regenerate this repository's own journey in the new format
and run the three lints against it. If a lint cannot be made to fire on a real defect, the
contract is decoration.

**Budget:** one worker dispatch. No browser work — the host is saturated and the visual
check waits.

**Observable stop point:** the skill's own journey file in the new format, one generated
release contract, and the three lints demonstrated firing and passing.

## Accepted outcome

One board carries the method. The journey board becomes a generated per-release contract,
and the function map stays in the repository but leaves the critical path.

## Non-goals

- No cross-repository evidence. `evidence` stays a bare symbol in this task; `repo:symbol`
  and its grep path are a separate task, because this repository cannot exercise them.
- Do not delete the function map's code. It leaves the flow; it does not leave the tree.
- No browser, no render, no export. The host is saturated and the visual check is a later
  step.

## Acceptance evidence

**AC-1** A story carries `status` (`exists` or `gap`), an optional `question`, and an
optional `evidence` symbol. The story map draws a question in violet and a gap visibly, at
story level rather than step level.

**AC-2** The model carries `one_journey`: one sentence naming what is true when the whole
loop works. It renders above the backbone.

**AC-3** A release's label carries how many of its stories exist, computed from the model —
never typed by hand.

**AC-4** A generated per-release contract exists, carrying each story's status, evidence
symbol and applicable rule ids. It is generated from the journey file, not authored.

**AC-5** Three lints, each demonstrated failing on a real defect and passing when fixed:
a story marked `exists` with no evidence; an evidence symbol that no longer greps; a story
with no status at all.

**AC-6** This repository's own journey file is migrated to the new format and every lint
passes against it. This is the value criterion the others serve — a format that cannot
describe the tool that made it describes nothing.

## Route-back conditions

Return `poc_outcome` to planning. The cross-repository evidence path is a separate item and
this task creates no delivery work for it.

## Measurement

Whether every lint can be made to fire on a real defect, and whether the skill's own journey
survives the migration without a field the new format cannot express.

## Stage Report: implementation

- DONE: Add story-level status, question and evidence to the model, and draw a gap and an open question on the story map at story level rather than step level.
  `lib/model.mjs` (`normalizeStory`), `lib/storymap.mjs` draws `story-status` (gap, red) and `story-question` (violet) per story; step-level `badge` rendering removed. `lib/storymap.test.mjs` asserts both kinds are present.
- DONE: The model carries `one_journey`, rendered above the backbone; a release label's exists-count is computed, never typed.
  `lib/storymap.mjs` `one-journey` shape + `existsCount = band.stories.filter(s => s.status === 'exists').length`; the dead `→ what is missing` canvas link to the retired board was dropped with it.
- DONE: Generate a per-release contract from the journey file, and make three lints each fire on a real defect and pass when it is fixed.
  `lib/release-contract.mjs` (`buildReleaseContract`) + CLI `lib/journey-contract.mjs`. Lints in `lib/lint.mjs` (`lintNoStatus`, `lintExistsWithoutEvidence`, `lintEvidenceNotFound` — the last via `git grep`, excluding the journey file itself) + CLI `lib/journey-lint.mjs`. All three demonstrated firing on an injected defect and passing clean via the CLI against `journey.example.yaml` (commit message / session transcript carries the four runs); `lib/lint.test.mjs` covers the same three cases plus the "evidence only in the journey file itself" trap and a combined clean pass.
- DONE: Migrate this repository's own journey file to the new format and show every lint passing against it.
  `skills/kc-journey-map/references/journey.example.yaml` — every story carries `status`; every `exists` story carries an `evidence` symbol verified (`git grep -w -F`) against this repository's real code; the story-less `handoff` step gained one story to carry its retired `NOT_RULED` badge as a `question`; a new `contract` step documents this session's own feature. `lib/journey-example.test.mjs` loads the real file and asserts `lintJourney` returns zero violations, and generates a contract for every declared release.
- DONE: Collapse to one board — the per-release canvas (`buildJourneyBoard`) no longer renders through the default pipeline.
  `lib/render.mjs` `buildAllPages` drops the `boards` spread; `buildJourneyBoard`/`boardPageId` stay exported and under direct test (`storymap.test.mjs`'s shape-id-disjointness test), same position as `funcmap.mjs` — leaves the critical path, not the tree, per the dispatch's own DO-NOT. Five `read.test.mjs` tests that asserted board pages exist through `buildAllPages` were deleted (they guarded a retired feature) and replaced with one test asserting `buildAllPages` emits no `page:jm-board-*` page.
- SKIPPED: Cross-repository evidence (`repo:symbol`).
  Explicit non-goal; `evidence` stays a bare symbol, matching this repository being the only repository journey.example.yaml can exercise.
- SKIPPED: Deleting `lib/funcmap.mjs` or its tests.
  Explicit DO-NOT; untouched (`git diff --stat -- lib/funcmap.mjs lib/funcmap.test.mjs` is empty).
- SKIPPED: Round-tripping story `status`/`evidence`/`question` from a canvas edit back into the file.
  Out of scope for this stage (`read.mjs`'s reader covers wording/order/release/priority only, unchanged); disclosed as a residual in `journey.example.yaml`'s own `status.unproven` and in `canvas.md`.

### Tests and what would break them

- `lib/lint.test.mjs`: `lintNoStatus` — a lint defaulting missing status to `gap` before checking would never fire this test but would still pass the exists-lint test, so the assertion is on `story === 's-0'`, not just non-empty. `lintExistsWithoutEvidence` — a lint checking only `status === 'exists'` (dropping `!evidence`) fires on the evidenced story too; asserted exact `story` id. `lintEvidenceNotFound` (two cases) — a lint that never greps (checks only truthiness) passes both a real and a renamed-away symbol; a lint that does not exclude the journey file's own text lets a symbol cited only there pass.
- `lib/release-contract.test.mjs`: filtering by step membership instead of `story.release` would pull a same-step, other-release story into the contract — asserted by absence (`Not in this release`) and by exact row-id order.
- `lib/journey-example.test.mjs`: the AC-6 value criterion — a story left unmigrated (no `status`) or an evidence symbol that does not actually grep in this repository fails `lintJourney`, not a mock.
- Pre-existing suite: 40/40 pass (`node --test lib/*.test.mjs`), up from 32 (5 deleted, 13 added net).

### Summary

Merged `iamcxa/journey-map-skill-merge` (the branch the tool lives on) into this stage's
branch first, since the worktree started on `main` and had none of `kc-team-ops/lib`. All
four absorbed items, the generated per-release contract, the three lints, and the migrated
worked example are implemented, tested (40/40, `node --test lib/*.test.mjs`), and verified
against real repository content rather than a mock — the lints were also run as CLIs against
four hand-injected defects (one per lint, plus a control) with output pasted into this
report's parent stage's evidence trail. Docs (`SKILL.md`, `canvas.md`, `cell-contract.md`,
`map-from-conversation.md`) were updated to stop describing the retired per-release canvas
board as current. No browser, no canvas server, no export were used, per the dispatch.
