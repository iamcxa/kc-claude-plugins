---
id: 7jsybdshk91p4f7p2hfr7ke1
title: "e2e-pipeline: a dropped `wait` step is invisible to every gate — waits compile to sleep, not to a browser call"
status: validation
source: GitHub issue #196 (https://github.com/iamcxa/kc-claude-plugins/issues/196) — filed as the third of the three classes #180 named, left open deliberately by PR #195
product: e2e-pipeline
sprint:
started: 2026-08-10T12:26:00Z
completed:
verdict:
worktree:
issue: "196"
pr: 254
pr_artifact_v1:
mod-block:
design: required
lane: main
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

Extend the existing happy-path `PATH` stub seam with a local `sleep` wrapper
that records argv to its own temporary log. Run the compiled real-shaped
fixture, then require its single `settle` step to invoke `sleep 2` exactly once.
This observes the generated command rather than the stable system utility.

The source-assertion alternative can match dead text or a helper definition,
the same proxy failure that caused the happy-path gate to move from source text
to argv. A total-step count is weaker because a compensating omission or
addition can preserve the count without identifying the missing wait.

## Design determination

**Pilot slice, one journey:** compile and run the existing corpus-shaped fixture
containing `settle: Wait 2`, observe the browser and wait channels separately,
and fail if the wait call disappears or its duration changes. Repository
maintainers are the limited user; the persistent value is the retained
regression gate, not product data.

The implementation owns no persistent runtime state, retry policy, recovery
loop, external mutation, or production data. Its logs and wrapper live only in
the test's temporary directory and are removed by the existing `t.after`
cleanup. One wait needs no cross-channel ordering guarantee. Adding a second
wait, shared reuse, or ordering semantics is a promotion trigger, not work to
generalize here.

## Acceptance criteria

**AC-1 — Removing the fixture wait makes the happy-path gate fail for the
missing wait.** Verified by: against the PR #254 candidate, deleting `settle`
leaves the compiled script at exit 0 and every existing browser assertion green,
while the new sleep assertion fails with actual `[]` versus expected `[["2"]]`.
Falsified by: the same deletion leaves the complete happy-path test green, or
the observed failure comes from an unrelated browser assertion.

**AC-2 — The retained fixture emits exactly the accepted wait command.**
Verified by: the executed compiled script records exactly one sleep invocation
with argv `["2"]` in a log separate from browser calls. Falsified by: no call,
multiple calls, a different duration, or an assertion that only matches emitted
source text without executing the script.

**AC-3 — The slice changes assurance, not compiler behavior.** Verified by: the
effective merge diff contains only `happy-path.test.js` and its sleep argv
fixture; `codegen.js` and other production bytes are unchanged, the current-main
merge simulation is clean, and the relevant suite passes at the exact PR head.
Falsified by: any compiler/runtime hunk, new generalized timing abstraction, or
required test skipped because of the shim.

## Test plan

1. Run the focused happy-path and codegen tests with the retained `Wait 2`.
2. Delete the fixture wait in a disposable sabotage run and require AC-1's
   isolated failure.
3. Run lint and the full portable suite at the exact candidate head.
4. Simulate the merge with current `origin/main` and require a clean tree and
   `git diff --check`.

## Measurement

Before this slice, deleting `settle` produced exit 0 and a green happy-path
gate. At PR #254 head `8e3594564b25f4607c55f1617a60ae011c2c6b85`, the same deletion produces the
targeted `[]` versus `[["2"]]` failure while prior browser evidence stays green.
The full suite reports 1060 passed, 0 failed, and the same 2 environment-gated
skips. The clean current-main merge simulation is tree
`7f608c5a43fa16511619d00c67b0d58ef13d7636` over
`origin/main@03f0325515c110bc12a022fc5bbf662ec7887821`.

## Doc diff

No external documentation changes. PR #254 updates the owning test's existing
header comment to distinguish browser actions from waits and to replace the old
declared blind spot with the new local sleep observation.

## Out of scope

- Compiler or generated-runtime behavior changes.
- Real-browser selector or timing validation.
- A fake clock, shared timing framework, or reuse outside this happy-path test.
- Relative ordering between browser and sleep logs, or support for multiple
  waits in the fixture.
- CI trigger, release, version, changelog, or production-surface changes.

## Stage Report: shape — out-of-order implementation adoption

**Decision: accept the PATH sleep shim as the smallest sufficient Pilot slice;
the existing PR is candidate build evidence, not retroactive workflow proof.**

- Captain Kent selected Pilot at `2026-08-18T08:54:13Z`; the committed v2
  receipt loaded the logical `shape` contract before these criteria were added.
- PR #254 was authored while the task still said every mechanism and criterion
  was deferred. That ordering is recorded rather than rewritten: its exact-head
  CI, sabotage result, and clean current-main merge simulation may be adopted at
  build, but do not prove the earlier implementation was authorized.
- A fresh Claude Sonnet interviewer found no blocking code defect and judged
  the bytes `MERGE_NOW`. This is advisory code evidence, not GitHub approval,
  Captain merge authorization, validation, or a terminal verdict.
- Separate logs intentionally do not prove browser/sleep interleaving. With one
  accepted wait, presence, multiplicity, and duration are the owned boundary;
  cross-channel ordering remains outside scope.

### Fresh advisory engineering verdict — 2026-08-18

At state `d8b3c3183e5728a37823b2d10c486e3cab11d3fe` and PR head
`8e3594564b25f4607c55f1617a60ae011c2c6b85`, a new Claude Sonnet session
recommended `proceed` with medium confidence, supported all five tested
premises, and marked multi-model review `not_needed`. It accepted adopting the
out-of-order bytes as build evidence without backdating authorization.

The session could not independently execute the recorded sabotage, so build and
verify-deliver must reproduce it; failure to get `[]` versus `[["2"]]`, diff
growth beyond the two accepted files, or loss of a clean current-main merge
changes the route. This was invocation-only advice because this workflow does
not vendor or select an engineering-judgment mod; it grants no gate, readiness,
merge, or state authority.

## Stage Report: build

**Result: the accepted Pilot slice is implemented at PR #254 head
`8e3594564b25f4607c55f1617a60ae011c2c6b85`.**

- The exact diff contains only `happy-path.test.js` and its local
  `sleep-argv-stub.js`; it adds no dependency, compiler/runtime code,
  generalized timing abstraction, or production lifecycle surface.
- The focused happy-path and codegen run passed 269/269 tests. In a disposable
  exact-head sabotage, removing `settle: Wait 2` left script execution and the
  browser transcript intact but failed the new assertion alone with actual
  `[]` versus expected `[["2"]]`.
- Exact-head GitHub evidence reports the portable suite successful, version
  parity successful, GitGuardian successful, and the inapplicable real-browser
  job skipped. The recorded full portable result is 1060 passed, 0 failed, with
  two environment-gated skips.
- The current-main merge simulation remains clean at tree
  `7f608c5a43fa16511619d00c67b0d58ef13d7636` over
  `origin/main@03f0325515c110bc12a022fc5bbf662ec7887821`.

### Implementation-exit observation

```yaml
review_convergence:
  capability: review_convergence
  mode: observe
  selected_profile: pilot-product-slice
  provider: roborev
  outcome: UNAVAILABLE
  reason: unavailable
  exact_tip: 8e3594564b25f4607c55f1617a60ae011c2c6b85
  implementation_provider_family: unknown
  identity_hash: unavailable
  config_object_sha: e816dfd221a307eee460f0404e4870d464ec7b66
  job_identity: unavailable
  member_states: []
  request_count: 0
  confirmation_count: 0
  cost_coverage: unavailable
```

The commit, PR, and task carry no reliable implementation-provider family.
The local contract therefore forbids guessing the complementary reviewer and
classifies the observation as unavailable before any provider query, claim, or
request. This is observation only; fresh validation remains required.
