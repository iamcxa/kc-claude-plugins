---
id: t5sa4zqw245w6ny0eyjmc9ez
title: "The missing-session guard in namespaceForRun has no test that can fail"
status: implementation
source: "adversarial spot-check of PR #135, 2026-08-02 — captain-ordered evidence backfill"
product: e2e-pipeline
sprint: S1
started: 2026-08-02
completed:
verdict:
worktree:
issue:
pr:
ledger_pr:
pr_artifact_v1:
ledger_artifact_v1:
mod-block:
design: trivial-pass
lane: defect
---

## Problem

`namespaceForRun` in `e2e-pipeline/bin/e2e-browser-runtime.js` opens with:

```js
if (!sessionName) {
  throw new Error('a session name is required to size a socket-safe e2e namespace');
}
```

Deleting those three lines leaves the suite **fully green** — 10/10 in
`compiler/test/browser-runtime-ownership.test.js`. Measured on an isolated checkout of
`27bff48`, 2026-08-02.

The guard is load-bearing. Without it, a missing session name makes `socketFile` the string
`"undefined.sock"`, so the budget is computed against 14 bytes of the wrong filename and
`namespaceForRun('msahjbw3-c5db2df771f976678836', socketHome, undefined)` returns the full
readable namespace — reintroducing exactly the under-budgeting class PR #135 fixed, and
more quietly, because nothing refuses.

The suite is not generally deaf here: the other two claim-breaking edits from the same
spot-check both reddened it — reverting `socketFile` to the literal `daemon.sock` failed 3
tests, and loosening the byte comparison from 103 to 104 failed 2. This one line is the
only unguarded part of the change.

There is no CI job for this plugin's suite ([[e2e-pipeline-suite-has-no-ci-job]]), so a
local test is the only net this guard can have.

## Defect-lane classification

All four conditions hold:

1. **Root cause cited.** `bin/e2e-browser-runtime.js`, `namespaceForRun`, the `!sessionName`
   branch — no test exercises it.
2. **Acceptance is mechanical.** A test that fails before the fix and passes after: with the
   guard removed the new test must go red, with the guard present it must go green.
3. **Single seam.** One function, one test file. No cross-layer ripple, no schema change.
4. **No open design decision.** The guard already exists and its behavior is already
   chosen. This adds the falsifier for it, nothing else.

`design: trivial-pass` — the change decides nothing about any surface; it makes an existing
refusal provable. Per the Defect-lane clause the value-AC requirement does not apply: this
restores provability rather than delivering new value.

## Acceptance criteria

**AC-1 — removing the guard reddens exactly this test.**
Verified by: on an isolated checkout, delete the three-line `!sessionName` branch from
`namespaceForRun` and run `node --test compiler/test/browser-runtime-ownership.test.js`;
the new test fails and the pre-existing tests stay green. Restore the branch; the file is
10+1 green. Falsified by: an implementation that passes with the guard deleted, or a test
that reddens for a reason other than the missing guard (which the pre-existing-tests-green
half detects).

## Appetite

**Estimate: 20 minutes.** One test case against an existing function; the RED evidence was
already produced by the spot-check that found this.
**Tolerance: +50% (30 minutes).** Past that, the work is not what it looks like — stop and
re-cut rather than continue.

## Implementation dispatch sizing

One dispatch. A single behavior, one complete RED→GREEN loop, well under the ~90 minute
split threshold.

## Measurement

## Doc diff

none — no described behavior changes; the guard's behavior is unchanged, only its proof.

## Out of scope

The namespace-drift finding from the same spot-check
([[browser-runtime-namespace-drift-across-upgrade]]) — that one has an open design decision
and is not in this lane.
