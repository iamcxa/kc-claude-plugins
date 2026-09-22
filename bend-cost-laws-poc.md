---
title: Prove executable Bend cost laws across the consumer boundary
status: validation
variant: kc-dev-flow-2
profile: poc
merge:
worktree: .worktrees/spacedock-ensign-bend-cost-laws-poc
pr:
gates:
    version: 1
    records:
        - id: gate:bend-cost-laws-poc:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:bend-cost-laws-poc-backlog-1
              briefing:
                id: briefing:bend-cost-laws-poc:backlog:attempt-1:revision-1
                digest: sha256:04e4ca3b19d9f838692a506fb7b4d11411cd3d8f5f9f4168284789711426cea7
                room-ref: ./bend-cost-laws-poc/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:bend-cost-laws-poc:backlog:1
                briefing: briefing:bend-cost-laws-poc:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-22T01:52:10.972891257Z"
                decision: approve
                reason: Kent answered 60 分鐘（建議） after already accepting dev2 POC and the three-law experiment; this accepts the recorded fixed budget and bounded implementation plus independent validation.
              application:
                target-stage: implementation
                state: consumed
started: 2026-09-22T01:53:09Z
---

Decide whether later PR-flow development should adopt a law-checked executable cost-decision component rather than relying only on schema-shaped summaries.

## Scope

Build a disposable integrated path from recorded or synthetic provider terminal JSON through explicit normalization into actual Bend-checked pure cost logic, then into a caller that consumes the resulting decision. Use public Bend source pinned at `a49524265bdfa5753a4bf38e25f0574a705dd868` in an isolated task-owned directory. No retained plugin change, provider/model/JEV call, credentials, product commit/push/PR/merge or invoice-cap claim.

The fixed experiment ceiling is 3,600 seconds. Prior Cloud routing preflight ran from `2026-09-22T01:22:42.726Z` to `2026-09-22T01:31:18.742Z` and consumes 516.016 seconds. User wait is excluded. Work resumed at `2026-09-22T01:45:13Z` with 3,083.984 seconds remaining. The immutable stop deadline is `2026-09-22T02:36:36.984Z`; commission, acquisition, build, implementation and independent validation all count. Stop and clean up owned processes at the deadline.

Input identity, numeric precision, normalization, foreign/IO/compiler and unsafe-dependency assumptions must remain explicit. A Bend-only abstract model disconnected from the caller is insufficient. Preserve failed attempts. Do not switch versions or weaken a law to pass.

## Acceptance criteria

**AC-1**: A uniquely identified valid reported spend remains known and contributes to the decision even when the review result failed.
Verified by: an integrated recorded/synthetic failed-terminal case at the actual caller boundary, plus a retained-cost mutation that the Bend check or caller assertion rejects.

**AC-2**: One receipt identity contributes at most once.
Verified by: duplicate-identity input across the same consumer path, plus a dedup mutation that the Bend check or caller assertion rejects.

**AC-3**: Unknown, ambiguous or invalid cost never becomes a claim of known zero or complete spend.
Verified by: unknown/ambiguous/invalid inputs across the same consumer path, plus an unknown-handling mutation that the Bend check or caller assertion rejects.

**AC-4**: Exit zero from an unsafe/foreign-dependent proof is not accepted as sufficient evidence.
Verified by: a deliberate unsafe or foreign dependency control whose exit status alone cannot satisfy the acceptance gate, with the remaining trust boundary recorded.

**AC-5**: The POC is bounded, reproducible and disposable.
Verified by: exact source/toolchain/artifact hashes, elapsed breakdown, independent fresh-validator verdict, no owned process remaining, and an explicit statement of what is unproved.

## Stage Report: implementation

- DONE: Produce one disposable integrated path where recorded/synthetic terminal JSON is explicitly normalized, actual pinned-Bend checked pure logic runs, and the caller consumes its decision.
  Code commit `edc803201c9417f299a3e7b503f3a6fd05229b17`; `node test.mjs` ran pinned Bend, then the JS caller parsed/asserted 1234 complete for failed review, 800 complete for a duplicate identity, and incomplete known-subtotal for unknown/ambiguous/invalid.
- DONE: Demonstrate all three frozen laws plus retained-cost, dedup, and unknown-handling mutations that the proof/check or consumer assertion rejects; an unsafe exit-zero control must not qualify as proof.
  Bend printed `All terms check.`; semantic mutants were rejected at `failed_review_retains_known`, `duplicate_identity_contributes_once`, and `unknown_is_incomplete`; the exit-zero no-Bend control lacked both required evidence signals. The 2026-09-22T02:05Z full run took real 1.533s.
- DONE: Freeze exact source/toolchain/artifact hashes, timing, failed attempts, trust boundaries and cleanup before the fixed 2026-09-22T02:36:36.984Z deadline.
  Freeze at 02:07:06Z: source `a49524265bdfa5753a4bf38e25f0574a705dd868`; archive `91c0e2640f8d2e3e73fd3dd62ed4d178ce9a6f7ce8f8980b4dc4abf7a6f9ccd4`; binary `d9c0dad1f77be6a13dd8dcc16aef4f59047a956a2744f25d5c220cb8de384693`; Base `e5639663177f2de93ef34867c029698aa4e68a98d46629f0b15452b67b99d798`; artifact commit `edc803201c9417f299a3e7b503f3a6fd05229b17`. Preflight 516.016s plus 1,313s resumed wall = 1,829.016s before freeze; no owned process remained at 02:07:58Z and task-local `.context` is retained only for validation, then removable with the disposable worktree.

### Summary

The provisional POC exercised pinned Bend 2.0.25 across the real generated-input Node consumer boundary without product/plugin edits, provider calls, credentials, delivery, or invoice/savings claims. Failed attempts are preserved: the initially assumed extracted path did not exist, `bend --version` is unsupported, and `/usr/bin/time` was absent; the successful route used the archive layout and shell timing. Fresh validation must decide whether same-ID conflicting valid costs (`8.00` then `99.00`) make the current first-wins `complete:true` decision ambiguous, and must challenge the weak unsafe control with otherwise valid-looking fabricated Bend/consumer evidence; unproved boundaries also include JS/JSON/string identity, the prebuilt compiler and source-to-binary provenance, process/stdout parsing, arbitrary receipt counts, provider truth, currency, and production integration.

## Stage Report: validation

- DONE: Independently verify the frozen commit edc803201c9417f299a3e7b503f3a6fd05229b17 uses pinned Bend source a49524265bdfa5753a4bf38e25f0574a705dd868 across the actual JS caller boundary and assess every AC without producer-context assumptions.
  Independent verdict: REJECTED. Artifact commit/tree/experiment-tree are `edc803201c9417f299a3e7b503f3a6fd05229b17` / `9fa4d9f8af3bdeb8bdb86dbe01d5e02bc8be0cd1` / `f6a019a23296b574278f76f7540776c9e882a921`; source HEAD/tree are `a49524265bdfa5753a4bf38e25f0574a705dd868` / `91f62f2122d3ac4cfb40e2211ce7b80f4c8af665`. AC-1 passes within the declared domain (failed review retained 1234; its mutation fails); AC-2 passes only as at-most-once/first-wins (dedup mutation fails); AC-3 fails the conflicting-same-ID ambiguity case despite ordinary unknown/array-ambiguous/invalid and frozen R4 `0.1367205` correctly becoming `Invalid`, 0, incomplete; AC-4 fails the foreign/no-Bend challenge; AC-5 is bounded and cleaned up but cannot establish source-to-binary provenance or reproducibility from source.
- DONE: Determine from the exact duplicate fixture/normalization whether same-ID conflicting valid costs are incorrectly promoted to complete known spend; distinguish identical duplicate from conflicting ambiguity and exercise the smallest decisive counterexample.
  Fixture SHA-256 `bc2f7183abe31cd3b22af0758e413f63ccbb17959c7019f4d139f0b970507351` contains exact ID `job-002` with canonical `8.00` and `99.00`; both normalize to `Known{800}` / `Known{9900}`, yet the caller exits 0 with `800`, `complete:true`, exactly like the identical `8.00` / `8.00` control. The AC-2 law quantifies all `cents, other: U32` but proves `pair(True, Spend(cents,True), Spend(other,True)) = Spend(cents,True)`, thereby proving first-wins even when values conflict; AC-1 quantifies every U32 known cost under failed review, while the AC-3 laws are three closed Passed-review equations for nullary Unknown/Ambiguous/Invalid and do not cover conflicting identities.
- DONE: Challenge the acceptance gate with unsafe/foreign-dependent computation that supplies otherwise complete valid-looking Bend-check and consumer evidence; compare the clean proof through the identical gate, state the exact quantified properties and caller binding, and finish with hashes, deadline accounting, trust limits and no-owned-process readback.
  The unchanged `test.mjs` gate passed both the real binary in 1.504035748s and a validation-only no-Bend executable in 0.479657760s; the latter fabricated `All terms check.`, every valid-looking `core.Spend` result, and expected mutation diagnostics (control SHA-256 `9a67ad51cb403fa1ed5470b2e6ec0ea20c98f210c9722c9a6b87b2c5f2f65afe`), so output shape/status is not bound to safe execution. JS generates `main.bend`, delegates via overridable `BEND_BIN`, parses stdout, and repeats the same first-wins expectation; hashes are test `5ed5cb42b6c126be68659e79411f36ffcda49f8c693ead8b9aaab80d99b25279`, consumer `5f1dff1cc05f75c9ef5ae1ed68aa75e8b7e8e6b7381b144968e18b37cfee8605`, archive `91c0e2640f8d2e3e73fd3dd62ed4d178ce9a6f7ce8f8980b4dc4abf7a6f9ccd4`, binary `d9c0dad1f77be6a13dd8dcc16aef4f59047a956a2744f25d5c220cb8de384693`, and Base `e5639663177f2de93ef34867c029698aa4e68a98d46629f0b15452b67b99d798`. The source flake names that prebuilt archive, but no evidence proves the binary was built from or implements pinned source; finite checks do not prove arbitrary receipts/runtime/compiler/provider truth. At cleanup `2026-09-22T02:18:41.655Z`, preflight plus resumed wall was 2,524.016s of 3,600s (1,075s remained), validation temp files were zero and process readback found no owned Bend/mutant/control process.

### Summary

The frozen prototype demonstrates the retained-cost behavior and basic unknown-state handling, but it is not acceptable evidence for the stated three-law decision boundary. Conflicting valid costs for one identity are promoted to a complete first-wins total, and the identical gate accepts a no-Bend producer that fabricates every expected signal. No candidate bytes were changed, no second acquisition/provider/model/JEV/delivery action occurred, and the disposable validation controls were removed.
