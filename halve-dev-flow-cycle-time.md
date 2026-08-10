---
title: Halve accepted-work to first-integrated-slice cycle time
source: Captain 2x development-speed target, 2026-08-10
product: kc-dev-flow
sprint: S1
id: f32cg5cbw6b633s09e2zxbr5
status: validation
lane: main
started: 2026-08-10T22:03:08Z
design: required
worktree: /Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1/.worktrees/kc-dev-flow-release-batch
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

## End value

Judgment remains independent at the two stages that decide route and acceptance,
while implementation no longer waits for a reviewer when no premise changed.

## Smallest route and reverse-recovery audit

The existing lifecycle, EM skill, and contract suite are all `WORKING`; the
broken seam is the review schedule. Reuse those surfaces and change only their
stage binding. Do not add a reviewer queue, timing service, model registry, or
new stage.

The fixed comparable scenario is one accepted task with two implementation-time
high-reasoning review waits before its first integrated slice. The new route has
zero mandatory waits in that interval, a 100% reduction; ideation and validation
each retain one fresh EM verdict.

## Design determination

`required` — this changes who reviews at each stage and when the captain is
offered an additional model pass.

## Acceptance criteria

**AC-1 — Judgment is required only at ideation and validation.**

Verified by: `kc-dev-flow/skills/continue-dev-flow/SKILL.md:193-197` and
`scripts/kc-dev-flow-contract-test.py:251-259`. Falsified by: adding a mandatory
implementation reviewer or removing either gate's fresh EM verdict.

**AC-2 — Reviewer capability has a bounded fallback.**

Verified by: `kc-dev-flow/skills/science-officer-em/SKILL.md:46-49` and
`scripts/kc-dev-flow-contract-test.py:527-529`. Falsified by: hard-coding a
provider/model or leaving a top-tier worker with no fresh-context route.

**AC-3 — Multi-model review is optional and decision-triggered.**

Verified by: `kc-dev-flow/skills/science-officer-em/SKILL.md:93-97` and
`docs/dev/README.md:244-255`. Falsified by: launching it without captain approval,
treating silence as approval, or skipping the one EM verdict.

**AC-4 — Pre-integration reviewer waits fall by at least half.**

Verified by: the task's fixed before/after route count, recorded in
`docs/dev/history/workflow-cost-record.md:14-17`. Falsified by: any ordinary
implementation path still requiring one of the two baseline review waits.

## Test plan

Run contract mutations for missing stage verdicts, implementation review loops,
fallback absence, and universal multi-model wording; then run the full contract,
frontmatter, parity, marketplace, and link checks and obtain one fresh EM review.

## Appetite and pre-mortem

One worker, one review-schedule seam. Stop if the route needs a new stage or
review orchestration service. If this ships and speed does not improve, the
dominant delay is post-implementation CI/release work, which this task measures
separately and does not hide by weakening validation.

## Out of scope

Reducing test depth, changing merge authority, optimizing release PR #198's CI,
provider-specific model policy, and creating or merging a PR.

## Stage Report: ideation

- DONE: The captain selected one EM at ideation and validation, a higher-tier
  preference with top-tier fallback, and optional multi-model review.
- DONE: Reverse recovery kept the lifecycle, EM skill, and contract suite; only
  their review-stage binding changes.
- DONE: AC-1 keeps exactly one fresh EM verdict at ideation and validation and
  opens no implementation reviewer loop.
- DONE: AC-2 prefers the next capability tier and gives a top-tier worker a
  fresh high-reasoning fallback.
- DONE: AC-3 offers an additional model only for a contested, irreversible,
  low-confidence, or unresolved call and requires captain approval.
- DONE: AC-4 removes 2/2 blocking implementation review waits while retaining
  both judgment gates and every delivery predicate.
- DONE: Fresh high-reasoning EM returned `narrow / high`: remove repeated
  implementation review, keep one EM at each judgment stage, and do not make
  multi-model review universal.

### Summary

Proceed with the existing two judgment gates and zero implementation review
loops unless a premise changes and returns to its owning stage.

## Stage Report: implementation

- DONE: Commit `c48a9e97f1614d80d8220ac4c80b4df993db09fb` updates the
  continuation skill, EM compatibility skill, local workflow binding, and their
  existing contract test; it adds no stage, queue, provider registry, or model
  identifier.
- DONE: Contract fixtures first failed on the prior judgment-heavy and universal
  cross-model wording, then pass on one EM at ideation/validation, no
  implementation review loop, the top-tier fallback, and optional multi-model
  semantics.
- DONE: The before/after route removes both implementation-time waits before the
  first integrated slice; validation still requires fresh exact-revision EM and
  delivery evidence.
- DONE: Fresh stage-exit checks pass: kc-dev-flow contract, 40 skill
  frontmatters, version parity at 2.1.0, marketplace L0/L1/L2,
  state-prerequisite contract, Python compilation, and `git diff --check`.

### Summary

Implementation changes one scheduling seam: deep judgment stays at ideation and
validation; implementation proceeds without a reviewer loop unless a premise
returns to its owning stage.
