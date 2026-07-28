---
title: Replace the review's presentation examples with a renderer
status: backlog
source: Anthropic context-engineering guidance + the kit cost map, 2026-07-27
design:
id: fa1depkrg2wegwe32dpaappa
---

Roughly 104 lines of `SKILL.md` are fenced examples showing what the review tables and the
confirmation menu look like. Anthropic's guidance for this model generation is to stop documenting
with examples and instead make the interface expressive: *"think more about the design of your
tools, scripts and files — what parameters does Claude have and how can they be more expressive?"*

A deterministic renderer with closed inputs satisfies that better than relocating the examples: it
removes the lines from context **and** makes the output shape enforceable rather than imitated.
That is the same move `2t` and `1c` make for pre-scans, applied to presentation.

**Careful about scope.** This is 104 lines, not the 544 an earlier draft claimed — 415 of that
region is the executable adapter `review-shadow.test.sh:56` extracts and sources, and it stays.
The confirmation menu at `SKILL.md:1723` is an authorization boundary, not decoration; if it is
rendered, the rendering is part of the contract and needs its own test.

**AC-1 — The review tables and menu are produced by a renderer with a closed input schema.**
Verified by: the renderer invoked on a fixture producing the documented shape, plus an ablation run showing no material difference in what a review emits. Falsified by: a review path that still hand-formats, or an output shape the schema does not pin.
