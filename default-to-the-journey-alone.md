---
id: g87dzxbq3j3rdwzneqr4g5nt
title: Ask which boards to draw, and default to the user journey alone
status: backlog
source: captain
product: kc-team-ops
planning-window:
planning-outcome:
sprint: journey-map-poc
sprint-readiness: ready
started:
completed:
verdict:
worktree:
issue:
pr:
mod-block:
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
