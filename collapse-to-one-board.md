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
worktree:
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
