---
title: Halve accepted-work to first-integrated-slice cycle time
source: Captain 2x development-speed target, 2026-08-10
product: kc-dev-flow
sprint: S1
id: f32cg5cbw6b633s09e2zxbr5
status: ideation
lane: main
started: 2026-08-10T22:03:08Z
---

## Problem

KC Dev Flow has no bounded measure of the time from an accepted outcome to its first integrated runnable slice, so added reading, review, and self-improvement work can slow delivery without appearing as a failed gate. Establish a comparable baseline and find the smallest change that cuts median cycle time to at most half while validation rejection and escaped-defect signals do not worsen; verification depth is not the speed lever.

## Observations

- The 2.1.0 delivery repeated Claude Opus high during implementation because of a
  session-level instruction, not a stage requirement. Two bounded attempts consumed
  three minutes each without a verdict. Cross-model review belongs only at the
  `ideation` and `validation` gates; a changed premise returns to its owning stage
  instead of opening an implementation review loop.
- Release PR #198's repo-wide typed review job took 11m42s. The once-only posting
  tests alone took 4m58s, although the release diff changed only kc-dev-flow version
  metadata and its changelog. Measure first-integrated-slice latency separately from
  post-merge release latency before choosing which path to optimize.
