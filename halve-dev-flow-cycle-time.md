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
pr: pr-merge:199
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

Verified by: the fixed before/after route above and the contract mutation that
rejects an implementation reviewer loop. Falsified by: any ordinary
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

## Captain scope revision — 2026-08-11

The captain approved removing the non-authoritative workflow cost history. AC-4
keeps the same accepted two-to-zero fixed-route comparison; its durable evidence
is this task plus the executable contract, so deleting the duplicate observation
file changes no review schedule or acceptance threshold.

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

## Stage Report: validation

### TL;DR

Fresh Claude Opus high session `d4daa8b0-ea12-4c8f-9ccc-a086ae9a8edd`
reviewed exact head `c48a9e97f1614d80d8220ac4c80b4df993db09fb` over
`a024b254e236f521d8438d567ade36d779a52d11` and returned
`proceed / high / multi_model:not_needed`, with AC-1..AC-4 PASS and zero
Material findings. This validates the accepted fixed-route wait reduction; it
does not claim a post-release median that has not yet been observed.

### Per-AC verdicts

- **AC-1 PASS** — every ideation and validation gate gets one fresh EM verdict,
  the defect lane retains validation EM, and implementation opens no review loop.
- **AC-2 PASS** — reviewer choice prefers the next capability tier and gives a
  top-tier worker a fresh highest-tier/high-reasoning fallback without provider
  or model identifiers.
- **AC-3 PASS** — the EM recommends an optional model only for the four named
  decision conditions; the captain must approve it and silence is not approval.
- **AC-4 PASS** — the approved comparison falls from two mandatory
  implementation-time waits to zero, a 100% reduction, while both judgment gates
  and delivery predicates remain.

### Evidence block

`Lenses:` Docs/policy, authority, back-compat, and workflow correctness fired;
all PASS with zero Material findings. Security, concurrency, and resource
lifecycle did not fire because the change adds no executable provider, state,
auth, process, or handle surface. Would fail on a third mandatory review point,
a removed gate verdict, or a provider-specific fallback.

`Diff coverage:` N/A — the task's production surface is Markdown workflow/skill
policy. Its executable contract assertions ran in the full kc-dev-flow suite and
are validation instruments, not shipped runtime behavior.

`Adversarial:` PASS — pre-change contract assertions reddened on the old
judgment-heavy/universal-cross-model wording; the exact-head suite rejects a
missing stage verdict, implementation review loop, absent top-tier fallback, or
universal multi-model requirement. Would fail if any mutation passed.

`Cross-model:` not_needed — the exact-head EM found no contested, irreversible,
low-confidence, or unresolved call. No optional second model was requested.

`E2E:` N/A — ideation approved a workflow-policy scheduling change, not a
user-visible or full-stack product behavior. Exact-head contract and fresh EM
are its declared validation instruments.

`Origin re-observation:` N/A — the accepted ACs concern repository stage policy
and a captain-approved fixed route; no AC claims a consumer or external runtime
median. Historical waits remain observation evidence, not the pass predicate.

### Engineering judgment

- `question:` Does exact head satisfy the two-stage EM route, bounded fallback,
  optional multi-model rule, and at-least-half fixed-route wait reduction?
- `revision:` `c48a9e97f1614d80d8220ac4c80b4df993db09fb` over
  `a024b254e236f521d8438d567ade36d779a52d11`.
- `adjudications:` AC-1..AC-4 supported; no task-level non-pass, Material
  finding, removable complete file, or removable review mechanism.
- `risk_tradeoff:` retain independent judgment where route and acceptance are
  decided while removing all ordinary implementation waits; keep an extra model
  available only for the four decision-risk conditions.
- `recommendation/route/confidence:` proceed / proceed / high.
- `dissent:` bounded future performance remains an operational measurement;
  this verdict proves the accepted route-count reduction, not an unobserved median.
- `multi_model:` not_needed.
- `disproof_condition:` change route if implementation regains a mandatory wait,
  either EM gate disappears, the fallback becomes provider-specific, or optional
  multi-model work runs without its condition and captain approval.
- `authority_boundary:` advisory only; Captain retains scope/irreversibility,
  Spacedock retains state, and GitHub/release-please retain delivery and release.

### Exact-head PR rebind

Fresh PR-level Claude Opus high session
`53ca4a4a-e114-4a4b-9412-ae0fbb0c0e0a` rebound AC-1, AC-2, AC-3, and AC-4 to
`454507f7ba56ce79ca0414f1964af4e59126eea5`. The delta changes neither skill,
contract-test, nor workflow-cost-record instruments. Its ideation and validation
surface challenges execute inside the two existing EM seats: no implementation
reviewer, third seat, route, or blocking wait was added. Multi-model remains
optional at current README line 264. Hosted CI is green at the exact head.
Verdict remains `proceed / high`, with zero Material findings.

## Implementation correction — remove duplicate observation surface

Commit `76614da671eaf29e9bed2147aae4e4f9f390af84` deletes the
non-authoritative workflow cost history and its file-specific contract wording.
The accepted two-to-zero fixed-route comparison remains in this work item and
the semantic contract still rejects an implementation reviewer loop. No skill,
stage binding, EM seat, multi-model condition, or delivery predicate changed.

Fresh implementation checks pass at that commit: kc-dev-flow contract, 40 skill
frontmatters, version parity, marketplace L0/L1/L2 installation, state
prerequisite contract, Python compilation, diff check, and local Markdown links.
Re-enter validation because the exact head changed; prior verdicts are evidence,
not authority for the new revision.

## Exact-head validation — `76614da671eaf29e9bed2147aae4e4f9f390af84`

Fresh Claude Opus high session `317c8a98-df85-4baa-8a48-c780d51e55b9`
returned `proceed / high`, AC 4/4, zero Material findings, and
`multi_model: not_needed`. The same session corrected its output envelope
without changing evidence or verdict.

- `Lenses:` review scheduling, authority, fallback, and delivery all pass.
- `Diff coverage:` the 13-path PR map binds every changed path; the deletion of
  history changes no skill, stage seat, fallback, or delivery predicate.
- `Adversarial:` the contract rejects an implementation review loop, a missing
  ideation/validation EM, absent top-tier fallback, and universal multi-model.
- `Cross-model:` not_needed — no contested, irreversible, low-confidence, or
  unresolved call remains.
- `E2E:` N/A — this accepted value is repository stage policy; hosted exact-head
  CI and all local contract/install checks are green.
- `Origin re-observation:` N/A — the accepted comparison is the recorded fixed
  route, not an external consumer-runtime claim.

The two mandatory pre-integration waits remain zero; both judgment gates and
all delivery predicates remain present. Delivery state remains open until PR
#199 merges.
