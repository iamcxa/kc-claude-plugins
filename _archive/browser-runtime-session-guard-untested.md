---
id: t5sa4zqw245w6ny0eyjmc9ez
title: "The missing-session guard in namespaceForRun has no test that can fail"
status: done
source: "adversarial spot-check of PR #135, 2026-08-02 — captain-ordered evidence backfill"
product: e2e-pipeline
sprint: S1
started: 2026-08-02
completed: 2026-08-02T00:26:50Z
verdict: PASSED
worktree:
issue:
pr: pr-merge:137:artifact-v1:beec1231fd94b9df552a884c11ca94ff5ee53362e84ad7c60eacc05a67274e40
ledger_pr:
pr_artifact_v1: eyJhdWRpdF9saW5rIjoiW3Q1XSgvaWFtY3hhL2tjLWNsYXVkZS1wbHVnaW5zL2Jsb2IvY2RlOTlhNmNhOTcyZGYwNTAzYTNhYzMxYmFiMjNiZjJkZWEwNTI5Zi9icm93c2VyLXJ1bnRpbWUtc2Vzc2lvbi1ndWFyZC11bnRlc3RlZC5tZCkiLCJiYXNlIjoibWFpbiIsImJhc2Vfb2lkIjoiMjVjYjI1OGUwNWEyMzlmMzVkOTk0NDM1NDVkZjNlYmMzNzE0NDNhZSIsImJvZHkiOiIjIyBUaGUgZGVmZWN0XG5cbmBuYW1lc3BhY2VGb3JSdW5gIG9wZW5zIHdpdGggYSBndWFyZCB0aGF0IHJlZnVzZXMgYSBtaXNzaW5nIHNlc3Npb24gbmFtZS4gKipEZWxldGluZyBpdFxubGVmdCB0aGUgc3VpdGUgZnVsbHkgZ3JlZW4qKiDigJQgMTAvMTAgaW4gYGNvbXBpbGVyL3Rlc3QvYnJvd3Nlci1ydW50aW1lLW93bmVyc2hpcC50ZXN0LmpzYCxcbm1lYXN1cmVkIG9uIGFuIGlzb2xhdGVkIGNoZWNrb3V0IG9mIGAyN2JmZjQ4YC5cblxuKipSZWFjaGFiaWxpdHksIHN0YXRlZCBwcmVjaXNlbHkuKiogVGhlIHNvbGUgaW4tcmVwbyBjYWxsIHNpdGUgKGBlMmUtYnJvd3Nlci1ydW50aW1lLmpzOjIzOTFgKVxucnVucyBgYXNzZXJ0UnVuQW5kQXBwYCBhdCAyMzgwIGZpcnN0LCB3aG9zZSByZWdleCByZWplY3RzIGV2ZXJ5IGZhbHN5IGBhcHBgIGJlZm9yZSBpdCBiZWNvbWVzXG5gc2Vzc2lvbk5hbWVgLiBTbyB0aGUgZ3VhcmQgaXMgZGVmZW5zZS1pbi1kZXB0aCBvbiBhbiAqZXhwb3J0ZWQqIHN1cmZhY2Ug4oCUIGBuYW1lc3BhY2VGb3JSdW5gXG5pcyBleHBvcnRlZCBhbmQgZGlyZWN0bHkgY2FsbGFibGUsIGFuZCB0aGUgdGVzdHMgY2FsbCBpdCBkaXJlY3RseSDigJQgcmF0aGVyIHRoYW4gYSBsaXZlXG5yZWFjaGFibGUgcGF0aCB0aHJvdWdoIHRoZSBydW50aW1lIHRvZGF5LiBUaGUgZmFsc2lmaWVyIGlzIHN0aWxsIG93ZWQ7IHRoZSBoYXphcmQgaXMgbmFycm93ZXJcbnRoYW4gYW4gdW5xdWFsaWZpZWQgcmVhZGluZyBzdWdnZXN0cy5cblxuV2l0aG91dCB0aGUgZ3VhcmQgYHNvY2tldEZpbGVgIGJlY29tZXMgdGhlIHN0cmluZyBgXCJ1bmRlZmluZWQuc29ja1wiYCxcbnRoZSAxMDMtYnl0ZSBidWRnZXQgaXMgY29tcHV0ZWQgYWdhaW5zdCB0aGUgd3JvbmcgZmlsZW5hbWUsIGFuZFxuYG5hbWVzcGFjZUZvclJ1bignbXNhaGpidzMtYzVkYjJkZjc3MWY5NzY2Nzg4MzYnLCBzb2NrZXRIb21lLCB1bmRlZmluZWQpYCByZXR1cm5zIHRoZSBmdWxsXG5yZWFkYWJsZSBuYW1lc3BhY2Ug4oCUIHJlaW50cm9kdWNpbmcgZXhhY3RseSB0aGUgdW5kZXItYnVkZ2V0aW5nIGNsYXNzICMxMzUgZml4ZWQsIGFuZCBtb3JlXG5xdWlldGx5LCBiZWNhdXNlIG5vdGhpbmcgcmVmdXNlcy5cblxuVGhlIHN1aXRlIGlzIG5vdCBnZW5lcmFsbHkgZGVhZiBoZXJlLiBUaGUgb3RoZXIgdHdvIGNsYWltLWJyZWFraW5nIGVkaXRzIGZyb20gdGhlIHNhbWVcbnNwb3QtY2hlY2sgYm90aCByZWRkZW5lZCBpdDogcmV2ZXJ0aW5nIGBzb2NrZXRGaWxlYCB0byB0aGUgbGl0ZXJhbCBgZGFlbW9uLnNvY2tgIGZhaWxlZCAzXG50ZXN0cywgbG9vc2VuaW5nIHRoZSBieXRlIGNvbXBhcmlzb24gZnJvbSAxMDMgdG8gMTA0IGZhaWxlZCAyLiBUaGlzIG9uZSBsaW5lIHdhcyB0aGUgb25seVxudW5ndWFyZGVkIHBhcnQgb2YgdGhlIGNoYW5nZS5cblxuYGUyZS1waXBlbGluZWAgaGFzIG5vIENJIGpvYiAoYHJldmlldy1ydW50aW1lLXRlc3RzLnltbGAgaXMgc2NvcGVkIHRvIGBrYy1wci1mbG93LyoqYCksIHNvIGFcbmxvY2FsIHRlc3QgaXMgdGhlIG9ubHkgbmV0IHRoaXMgZ3VhcmQgY2FuIGhhdmUuXG5cbiMjIFJFRCBldmlkZW5jZVxuXG5XaXRoIHRoZSB0aHJlZS1saW5lIGd1YXJkIGRlbGV0ZWQ6XG5cbmBgYFxu4pyWIGEgbWlzc2luZyBzZXNzaW9uIG5hbWUgKHVuZGVmaW5lZCkgaXMgcmVmdXNlZCwgbm90IHNpemVkIGFnYWluc3QgXCJ1bmRlZmluZWRcIlxu4pyWIGEgbWlzc2luZyBzZXNzaW9uIG5hbWUgKFwiXCIpIGlzIHJlZnVzZWQsIG5vdCBzaXplZCBhZ2FpbnN0IFwidW5kZWZpbmVkXCJcbuKcliBhIG1pc3Npbmcgc2Vzc2lvbiBuYW1lIChudWxsKSBpcyByZWZ1c2VkLCBub3Qgc2l6ZWQgYWdhaW5zdCBcInVuZGVmaW5lZFwiXG7ihLkgdGVzdHMgMTMgICDihLkgcGFzcyAxMCAgIOKEuSBmYWlsIDNcbmBgYFxuXG5HdWFyZCByZXN0b3JlZDogMTMvMTMuIFRoZSBvdGhlciB0ZW4gdGVzdHMgc3RheSBncmVlbiBpbiBib3RoIHJ1bnMsIHdoaWNoIGlzIHdoYXRcbmRpc3Rpbmd1aXNoZXMgXCJ0aGUgZ3VhcmQgaXMgbWlzc2luZ1wiIGZyb20gXCJ0aGUgdGVzdCByZWRkZW5zIGZvciBzb21lIG90aGVyIHJlYXNvblwiLlxuXG5UaHJlZSBjYXNlcyByYXRoZXIgdGhhbiBvbmUgbG9vcDogYSBjYXNlIHN0b3BzIGF0IGl0cyBmaXJzdCBmYWlsaW5nIGFzc2VydGlvbiwgc28gYSBsb29wZWRcbnZlcnNpb24gd291bGQgbGVhdmUgYFwiXCJgIGFuZCBgbnVsbGAgdW5leGVjdXRlZCBpbiB0aGUgUkVEIHJ1biBhbmQgdW5wcm92ZW4gYXMgZmFsc2lmaWVycy5cblRoZXkgYWxzbyBidXkgZmFsc2lmaWNhdGlvbiBwb3dlciB0aGUgc2luZ2xlIGNhc2UgZG9lcyBub3Q6IGEgZ3VhcmQgbmFycm93ZWQgdG9cbmBzZXNzaW9uTmFtZSA9PT0gdW5kZWZpbmVkYCBpcyBjYXVnaHQgb25seSBiZWNhdXNlIGBcIlwiYCBhbmQgYG51bGxgIGFyZSBwcmVzZW50LlxuXG5UaGUgUkVEIGhlcmUgaXMgbXV0YXRpb24tZ2VuZXJhdGVkIGJ5IGRlc2lnbiBhbmQgZGVjbGFyZWQgdXAgZnJvbnQgaW4gdGhlIGVudGl0eSBBQywgc28gdGhpc1xuaXMgbm90IGEgcG9zdC1ob2MgdGVzdCB3cml0dGVuIHRvIGNvbmZpcm0gZXhpc3RpbmcgY29kZS5cblxuIyMgU2NvcGVcblxuVGVzdC1vbmx5LCArMjcgbGluZXMsIG9uZSBmaWxlLiAqKk5vIHByb2R1Y3Rpb24gY29kZSBjaGFuZ2VzKiog4oCUIHRoZSBkZWZlY3Qgd2FzIHRoZSBhYnNlbnRcbmZhbHNpZmllciwgbm90IHRoZSBndWFyZC5cblxuIyMgQ2hlY2tzXG5cbi0gYG5wbSB0ZXN0YCDigJQgOTUyIHRlc3RzLCA5NTEgcGFzcywgMCBmYWlsLCAxIHNraXBwZWQuIFJ1biBsb2NhbGx5OyBubyBDSSBqb2IgcnVucyB0aGlzXG4gIHN1aXRlLCB3aGljaCBpcyB0aGUgcG9pbnQgb2YgdGhlIGZpcnN0IHNlY3Rpb24uXG4tIGBucG0gcnVuIGxpbnRgIOKAlCBleGl0IDA7IHRoZSB0b3VjaGVkIGZpbGUgcmVwb3J0cyB6ZXJvIHdhcm5pbmdzIGJvdGggYmVmb3JlIGFuZCBhZnRlci5cbi0gRGlmZiBjb3ZlcmFnZTogKioxMDAlKiog4oCUIGFsbCAyNyBhZGRlZCBsaW5lcyBhcmUgdGVzdC1maWxlIGxpbmVzIGFuZCBlYWNoIGV4ZWN1dGVzIGluIHRoZVxuICAxMy8xMyBydW4uXG4tIFRoZSBkaWZmIHRvdWNoZXMgbm8gdmVyc2lvbiB2YWx1ZSwgbm8gYG1hcmtldHBsYWNlLmpzb25gLCBubyBza2lsbCBmcm9udG1hdHRlciwgbm8gcGx1Z2luXG4gIGRpcmVjdG9yeSBhbmQgbm8gd29ya2Zsb3csIHNvIG5vbmUgb2YgdGhlIHN1cmZhY2Utc3BlY2lmaWMgc2NyaXB0cyBhcmUgZWFybmVkLlxuXG5EZXYtZmxvdyBlbnRpdHk6IGBicm93c2VyLXJ1bnRpbWUtc2Vzc2lvbi1ndWFyZC11bnRlc3RlZGAgKGRlZmVjdCBsYW5lKS5cblxu8J-kliBHZW5lcmF0ZWQgd2l0aCBbQ2xhdWRlIENvZGVdKGh0dHBzOi8vY2xhdWRlLmNvbS9jbGF1ZGUtY29kZSlcblxuXG5bdDVdKC9pYW1jeGEva2MtY2xhdWRlLXBsdWdpbnMvYmxvYi9jZGU5OWE2Y2E5NzJkZjA1MDNhM2FjMzFiYWIyM2JmMmRlYTA1MjlmL2Jyb3dzZXItcnVudGltZS1zZXNzaW9uLWd1YXJkLXVudGVzdGVkLm1kKSIsImJvZHlfc2hhMjU2IjoiNzc1MDBkMGZiNTMxZjZlZjQwOTFlMTdlZWJkMDQzOGViZDRlMjg0MTk2NGNkZmJjMGFmZTg0NzUzY2Q3MGI1YyIsImRpZmZfc2hhMjU2IjoiZjUwYTAzNGU5MTQ4ZTIwMTBmOGU0Yzc5OTlkMmM4NmM0ZmQ3OTFkNjNlMTM4NzViNzE3NjUxOTY5Y2E4ZjY0NCIsImhlYWQiOiJmaXgvc2Vzc2lvbi1ndWFyZC1mYWxzaWZpZXIiLCJoZWFkX29pZCI6ImIzMTE4ZWZhOWFmNThmNTkyMGUzMzdjZTA2N2MwMGEzMDZiMTViZjAiLCJsaXZlX3BhdGgiOiJicm93c2VyLXJ1bnRpbWUtc2Vzc2lvbi1ndWFyZC11bnRlc3RlZC5tZCIsInJlcG8iOiJpYW1jeGEva2MtY2xhdWRlLXBsdWdpbnMiLCJ0aXRsZSI6InRlc3QoZTJlLXBpcGVsaW5lKTogcGluIHRoZSBtaXNzaW5nLXNlc3Npb24gZ3VhcmQgaW4gbmFtZXNwYWNlRm9yUnVuIn0
ledger_artifact_v1:
mod-block:
design: trivial-pass
lane: defect
archived: 2026-08-02T09:08:52Z
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

## Stage Report: implementation

**TL;DR.** One test file, +27 lines, no production change. The guard already existed; the
defect was that nothing could prove it. RED was produced by deleting the guard on an
isolated checkout, and all three new cases failed while the ten pre-existing ones stayed
green. Guard restored, 13/13. Full suite 952/951/0/1-skipped, lint exit 0.

**AC-1 evidence.** Both halves of AC-1 are produced by the two runs below: the deletion run for "removing the guard reddens exactly this test", and the ten-pre-existing-green half for "not for some other reason".

**RED evidence.** With the three-line `!sessionName` branch deleted from `namespaceForRun`:

```
✖ a missing session name (undefined) is refused, not sized against "undefined"
✖ a missing session name ("") is refused, not sized against "undefined"
✖ a missing session name (null) is refused, not sized against "undefined"
ℹ tests 13   ℹ pass 10   ℹ fail 3
```

Restored: 13/13. The ten pre-existing tests are green in both runs — that half is what
separates "the guard is missing" from "the test reddens for another reason".

**Assertion accounting.** Three `test()` registrations generated from a `for` over the input
array, not one test looping internally. A case stops at its first failing assertion, so a
looped version would leave `''` and `null` unexecuted in the RED run and unproven. Every
added assertion appears in the RED output. No arrangement-only assertions were added.

**Surface checks earned.** None. The diff touches no version value or propagation target, no
`marketplace.json`, no `*/skills/*/SKILL.md` frontmatter, no plugin directory, and no
workflow — so `version-parity-check.sh`, `marketplace-verify.sh` and
`skill-frontmatter-lint.sh` are not the checks this diff earns.

**Reachability, corrected at the gate.** The sole in-repo call site (2391) runs
`assertRunAndApp` at 2380 first, and its regex rejects every falsy `app` before it becomes
`sessionName`. The guard is therefore defense-in-depth on an exported, directly-callable
surface rather than a live reachable path through the runtime today. The falsifier is still
owed; the original framing overstated the hazard.

Delivered as PR #137, head `b3118ef`.

## Stage Report: validation

**TL;DR.** AC-1 reproduced by a fresh-context validator on its own isolated worktree, both
halves, plus three mutants. Correctness lens and the cross-model gate both returned zero
findings. EM route `narrow`: three evidence-statement corrections, no branch change, no
correction round.

**AC-1 — PASS, both halves.** Validator's own `--detach` worktree at `b3118ef`: guard
restored 13/13; guard deleted 13 tests / 10 pass / 3 fail with only the three new cases
failing; restored again 13/13 with no residual diff.

**Declared variance.** AC-1 was written anticipating one new case ("the file is 10+1 green")
and three shipped, so the counts read 13 rather than 11. Not scope creep: the narrowed-guard
mutant below is caught *only* because `''` and `null` are present, which is falsification
power AC-1's own falsifier clause asked for. Recorded so a later reader does not re-derive
the mismatch.

### Evidence block

- **Lenses:** test-only diff, one file, touching test assertions and nothing else.
  Correctness fired → `pr-review-toolkit:code-reviewer`, **0 findings**, verified
  empirically rather than by reading. Not fired, with the surfaces the diff does touch
  named: security (no auth/permission/trust boundary, no shell-running hook, no workflow
  with secrets), silent-failure (adds no error handling, fallback or swallowed error — it
  asserts on one), type-design (no new or changed type), concurrency (none),
  resource-lifecycle (no process/handle/memory surface in the diff), manifest/back-compat
  (no `marketplace.json`, `plugin.json`, or skill frontmatter).
- **Diff coverage:** 100% — all 27 added lines are test-file lines, each executed in the
  13/13 run.
- **Adversarial:** three mutants, all caught. Guard deleted → three new cases fail, ten
  pre-existing pass. Guard throwing a different message → caught, because the assertions
  match `/session name is required/` rather than merely "throws". Guard narrowed to
  `sessionName === undefined` → caught by the `''` and `null` cases. Run by the
  fresh-context validator on its own worktree.
- **Cross-model:** codex (gpt-5.6-sol), read-only, on the diff. **No [P1]/[P2].** Noted that
  the tests pin observable refusal rather than the guard's implementation, that only
  `undefined` is strictly necessary for the original regression while `''` and `null` add
  contract coverage, and that the falsy check is sufficient at the call site because
  `assertRunAndApp` runs first — a basis EM then verified in the source.
- **E2E:** N/A — the diff changes no behavior. Zero production lines change and the guard is
  byte-identical at head, so the E2E-first condition at ideation ("changes full-stack or
  user-visible behavior") is not met. The attachment condition is negated, not escaped.

**RED-before-GREEN, stated so it is not re-litigated.** The RED here is mutation-generated
by design and declared up front in AC-1. This is not a post-hoc test written to confirm
existing code; the procedure that produces the RED is the acceptance criterion.

**Correction round budget.** Zero rework rounds. EM returned `narrow` with three corrections
to how the evidence was *stated* — diff coverage over-claimed as `N/A`, the AC count
variance unrecorded, and reachability unqualified — none of which touched the branch. All
three applied. Effort against the 20-minute estimate: roughly 25 minutes including the
validator, both reviewers and the gate, inside the +50% tolerance.

**Exact-head CI:** both required and non-required checks SUCCESS on `b3118ef`;
`MERGEABLE` / `CLEAN`.

### State-holder boundary

This session is a state **non-holder**, so the stage transition and the terminal
transaction cannot be run here — those are binary-owned and the lifecycle hooks refuse from
a non-holder by design. `status` therefore stays `implementation` with the validation gate
recorded above rather than being hand-written to a stage no transaction produced. Everything
the holder needs is on this branch.

`--ac-scan` resolves AC-1 at line 68 and reports `unevidenced=true citations=0`. That is the
tool's normal output here, not a gap: the shipped `e2e-selector-compile-gate` entity returns
the same for all five of its ACs. The contract's requirement is that every AC resolve to the
extractor, which it does.
