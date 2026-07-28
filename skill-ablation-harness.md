---
title: Cutting prose from a skill has no failure signal — build one before cutting
status: ideation
source: precondition for the Sprint 4 slimming track, filed 2026-07-27 on captain direction
design:
id: 5b5gp68f2aq0bdrcf3q28jgg
started: 2026-07-28T08:10:24Z
---

The kit is going to be cut down before it is extended. The problem with that order is that
**prose has no test**. Delete a paragraph of instruction from `SKILL.md` and every one of the 935
assertions still passes, because they exercise the shell scripts, not the skill's wording. The one
exception proves the rule: `review-shadow.test.sh:56` extracts the block between
`# typed-interactive-recipe:start/end` and sources it, so that 415-line region is genuinely
protected — and nothing else is.

This was demonstrated the expensive way. A slimming proposal in this workflow targeted "544 lines
of example output" in Step 6; 415 of those lines were that executable adapter. The proposal read
as a clean subtraction and would have broken 213 assertions.

So: before any line is cut, there has to be a way to answer "did that change what the review
produces?" other than by reading the diff and feeling confident.

## What this is

The minimum A/B capability: run the same PR through two versions of the skill and diff the
outcome — findings emitted, their severities and file:line anchors, tokens, wall-clock.

## What this is not

It is not `review-effectiveness-benchmark` (62). That entity measures **how good the kit is** in
absolute terms, against pre-registered known defects, and needs ground truth. This one measures
**whether a change moved anything**, and needs no ground truth at all — the previous version is
the reference. It is the cheaper half and it is what unblocks cutting.

## The difficulty that has to be solved first

**A review is not deterministic.** The same PR through the same skill twice will not produce a
byte-identical finding set, so a naive diff reports every run as a regression. Ideation must
decide how to separate signal from noise, and the honest options each cost something:

- **Repeat and compare distributions** rather than single runs — more expensive, and it needs a
  stated threshold for "materially different" that is chosen before the first cut, not after.
- **Compare on stable projections only** — e.g. the set of `file:line` anchors touched, or the
  count per severity, discarding wording. Cheaper, and blind to a change that alters what a
  finding *says* without moving where it points.
- **Freeze what can be frozen** — a fixed PR corpus, pinned model, temperature/seed where the
  harness allows it. Reduces variance without eliminating it.

Whichever is chosen, the threshold is pre-registered. Choosing it after seeing a cut's result is
how a slimming pass talks itself into "that difference doesn't matter".

## Scope

Two skill versions, one frozen PR corpus, one comparison report. Reuses the corpus `62` will need,
so the corpus work is shared rather than duplicated — but this entity does not wait on `62`'s
ground-truth decision, which is the expensive part.

**AC-1 — Running the unmodified skill against itself reports "no material difference".**
Verified by: an A/A run on the frozen corpus under the pre-registered threshold, reporting no material change. Falsified by: an A/A run that reports a difference — that means the threshold is measuring noise and no cut can be judged with it.

**AC-2 — A deliberate removal of a load-bearing instruction is reported as a difference.**
Verified by: cutting one instruction known to change behaviour (e.g. the pre-emit quote gate at `SKILL.md:973`) and confirming the harness flags it, with the flagged dimension named. Falsified by: the harness reporting no material difference for that cut — it would then be unable to catch the cuts this sprint intends to make.
