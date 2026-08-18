---
id: 7jsybdshk91p4f7p2hfr7ke1
title: "e2e-pipeline: a dropped `wait` step is invisible to every gate — waits compile to sleep, not to a browser call"
status: backlog
source: GitHub issue #196 (https://github.com/iamcxa/kc-claude-plugins/issues/196) — filed as the third of the three classes #180 named, left open deliberately by PR #195
product: e2e-pipeline
sprint:
started: 2026-08-10T12:26:00Z
completed:
verdict:
worktree:
issue: "196"
pr:
pr_artifact_v1:
mod-block:
design:
lane:
---

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v2
  selected: pilot-product-slice
  recommended: pilot-product-slice
  basis: >-
    This is a durable, limited-use regression gate for one compiler journey. It
    creates persistent repository value but changes no compiler behavior,
    credential, production data, external mutation, unattended operation, or
    public compatibility boundary.
  route: [shape, build, verify-deliver]
  obligations:
    architecture:
      - Choose the smallest observable seam that makes a dropped generated wait falsifiable.
      - Reuse the existing happy-path PATH-stub boundary without creating a second test framework.
    implementation:
      - Keep the candidate test-only and leave compiler and generated-runtime behavior unchanged.
      - Observe sleep argv independently from browser argv for the single accepted wait boundary.
    testing:
      - Prove deletion of the fixture wait fails only the newly owned observation.
      - Run focused and full portable suites at the exact candidate revision.
      - Prove the candidate merges cleanly with current main before delivery.
  scope_boundary: >-
    No compiler code change, general fake-clock abstraction, cross-channel
    ordering guarantee, real-browser claim, CI trigger change, release surface,
    or additional harness beyond the PR #254 candidate.
  promote_when:
    - The sleep observer becomes a shared compatibility surface outside this happy-path test.
    - Accepted scope requires relative ordering across browser and sleep channels.
    - A production runtime, CI trigger, or operational commitment enters scope.
  decision:
    authority: Captain Kent
    at: 2026-08-18T08:54:13Z
```

## Problem

`happy-path.test.js` now executes the compiled script against a stubbed
`agent-browser` and asserts the argv it receives (PR #195, merged
2026-08-10). That instrument cannot see a dropped `wait`: `codegen.js`
compiles a `wait` step to `sleep N`, not to an `agent-browser` call, so
nothing reaches the stub to be counted. Deleting a `wait` step from the
fixture flow leaves every assertion in the happy-path gate satisfied and the
compiled script exiting 0. The class matters more than its size suggests —
a dropped wait does not fail deterministically in a real browser either; it
fails intermittently, under load, on someone else's machine, which is the
#122 shape that cost a full investigation. Issue #196 names three candidate
mechanisms (pin `sleep N` in the source assertions; assert a total step
count; add a PATH `sleep` shim that logs argv the way `agent-browser`
already is) and explicitly declines to pick one, because the third is a new
mechanism and `kernel.md:116` requires a new mechanism to name the concrete
defect it prevents before it is built. The issue records that the class is
real but no instance of a silently dropped wait has ever been observed.

### Triage verification (FO, against `origin/main` @ 334764d)

The seed's premise was confirmed before filing; no option was chosen.

| Claim | Evidence | Verdict |
|---|---|---|
| A `wait` compiles to `sleep`, not a browser call | `e2e-pipeline/compiler/codegen.js:1891-1898` — `case 'wait':` pushes `sleep <seconds>` | CONFIRMED |
| The argv gate cannot see it | `e2e-pipeline/compiler/test/happy-path.test.js:84-85` states the gap in its own header comment | CONFIRMED (self-documented) |
| A PATH stub seam already exists to extend | `happy-path.test.js:240-255` — a `binDir` on `PATH` holding only `agent-browser`, plus a compiled-in shell function shim | CONFIRMED |
| The step already records a name and a duration | `codegen.js:1893-1897` — `_record_step_name`, `_STEP_RESULTS`, `_STEP_TIMES` are emitted for `wait` | CONFIRMED — relevant to the step-count option |
| PR #195 is merged and #180 is closed | `gh pr view 195` → MERGED 2026-08-10T12:21:55Z; `gh issue view 180` → CLOSED | CONFIRMED |

## Proposed approach

Deferred — ideation owns this. The issue leaves an open choice between three
defensible mechanisms, so this task is not in the defect lane (condition 4
fails).

## Design determination

Deferred — ideation owns this. Not pre-judged at seed capture.

## Acceptance criteria

Deferred — ideation owns this.

## Test plan

Deferred — ideation owns this.

## Measurement

## Doc diff

Deferred — ideation owns this.

## Out of scope

Deferred — ideation owns this.
