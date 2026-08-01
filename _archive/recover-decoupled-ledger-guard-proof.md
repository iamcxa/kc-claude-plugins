---
title: Recover the decoupled-ledger local guard proof
status: done
source: captain approval plus high-confidence Claude Science Officer EM narrow judgment on 2026-08-01; supersedes parked entity id 7rgdvsjypgmzk8wh03h3vst9 without altering it
product: repo-platform
sprint:
started: 2026-07-31T16:30:42Z
completed: 2026-08-01T03:20:36Z
verdict: PASSED
worktree:
issue:
pr: pr-merge:120:artifact-v1:f3d75a206cc9052f4e21e24f599a4d6c83ef633dfc218f5ce1bb478360e09ad2
ledger_pr:
pr_artifact_v1: eyJhdWRpdF9saW5rIjoiWzFhXSgvaWFtY3hhL2tjLWNsYXVkZS1wbHVnaW5zL2Jsb2IvMjljZmEzNzQ2ZjcyZWMwZjQ3NjdiOGQwNjg5OWY3YWZhNzM2ZmZiZS9yZWNvdmVyLWRlY291cGxlZC1sZWRnZXItZ3VhcmQtcHJvb2YubWQpIiwiYmFzZSI6Im1haW4iLCJiYXNlX29pZCI6IjcxMDg0OTU0YTU1ZTJiNTczNzE0ODYzNjdmZjUxZDAwNTA4YjE5NzMiLCJib2R5IjoiTGV0IGF1dGhlbnRpY2F0ZWQgcHJvZHVjdCBkZWxpdmVyeSBjb21wbGV0ZSB0YXNrcyBpbW1lZGlhdGVseSB3aGlsZSBsZWRnZXIgbWFpbnRlbmFuY2UgcmVtYWlucyBvcHRpb25hbCwgYmFja3dhcmQtY29tcGF0aWJsZSBvYnNlcnZhdGlvbi5cblxuIyMgV2hhdCBjaGFuZ2VkXG5cbi0gVGVybWluYWxpemUgYW5kIGFyY2hpdmUgdGFza3MgZnJvbSBhdXRoZW50aWNhdGVkIHByb2R1Y3QgbWVyZ2VzLlxuLSBQcmVzZXJ2ZSBsZWdhY3kgbGVkZ2VyIHJvd3MgYW5kIHJlZmVyZW5jZXMgYXMgb2JzZXJ2YXRpb25hbCBldmlkZW5jZS5cbi0gQWRkIGNvbnRyYWN0IGNvdmVyYWdlIGZvciB0ZXJtaW5hbCwgY29tcGF0aWJpbGl0eSwgYXJjaGl2ZSwgYW5kIHNjb3BlIHBhdGhzLlxuLSBFeGVyY2lzZSBmaXZlIGxvY2FsIHByb2R1Y3QtYXV0aGVudGljYXRpb24gcmVmdXNhbCBjb25kaXRpb25zIGluZGVwZW5kZW50bHkuXG5cbiMjIEV2aWRlbmNlXG5cbi0gNC80IGNvbnRyYWN0IHBoYXNlcyBwYXNzZWQ7IGZ1bGwgYGFsbGAgcGFzc2VkLlxuLSA2LzYgYWR2ZXJzYXJpYWwgbXV0YXRpb25zIHJlamVjdGVkOyA1MjUvNTk4IGV4ZWN1dGFibGUgc3RhdGVtZW50cyBjb3ZlcmVkICg4Ny43OSUpLlxuXG4jIyBSZXZpZXcgZ3VpZGFuY2VcblxuLSBgYXV0aGVudGljYXRlX3Rlcm1pbmFsX3JvdXRlYCBhbmQgYGR1cmFibGVfYXJjaGl2ZWAgYXJlIGZpeHR1cmUtYXV0aG9yZWQsIG5vdCBpbmRlcGVuZGVudCB1cHN0cmVhbSBwcm9vZi5cbi0gUmVmdXNhbCBiZWhhdmlvci9zdGF0ZSBpcyBwaW5uZWQsIGJ1dCBleGFjdCByZXR1cm4gY2xhc3NlcyBhbmQgZGlhZ25vc3RpYyBzdHJpbmdzIHJlbWFpbiB1bnBpbm5lZC5cblxuLS0tXG5bMWFdKC9pYW1jeGEva2MtY2xhdWRlLXBsdWdpbnMvYmxvYi8yOWNmYTM3NDZmNzJlYzBmNDc2N2I4ZDA2ODk5ZjdhZmE3MzZmZmJlL3JlY292ZXItZGVjb3VwbGVkLWxlZGdlci1ndWFyZC1wcm9vZi5tZClcbiIsImJvZHlfc2hhMjU2IjoiNjExMThiOWU0NDMwYjY1ZjRjMGI1MDBiZWJmZGJiODZjOWJiNzQzM2Q1MjE4NGFmMzE4YjAyZmExMjY1MTY1OCIsImRpZmZfc2hhMjU2IjoiMjNiNTFlNTI3NDRjZGM4ZmU1ZjE3NDY4MzhkYjBjNDJlYWY2MmM3Mjk0MWRjNjc3Njc5MTA2NmFjMTc5MmY1YyIsImhlYWQiOiJzcGFjZWRvY2stZW5zaWduL3JlY292ZXItZGVjb3VwbGVkLWxlZGdlci1ndWFyZC1wcm9vZiIsImhlYWRfb2lkIjoiNzRjNjZiMDIwNGMxNGNlM2E1YWRjMGVjMTlkMzkyODdjNTI0NWEzYSIsImxpdmVfcGF0aCI6InJlY292ZXItZGVjb3VwbGVkLWxlZGdlci1ndWFyZC1wcm9vZi5tZCIsInJlcG8iOiJpYW1jeGEva2MtY2xhdWRlLXBsdWdpbnMiLCJ0aXRsZSI6ImRvY3MoZGV2KTogZGVjb3VwbGUgbGVkZ2VyIGZyb20gdGVybWluYWxpemF0aW9uIn0
ledger_artifact_v1:
mod-block:
design: trivial-pass
lane: defect
id: 1a1c5f9k2m3cjmmhzf7162dv
archived: 2026-08-01T03:36:54Z
---

The parked decoupled-ledger change makes a broader local-authentication claim than its focused fixture proves. Recover only the five local guards of terminalize_authenticated_product with mechanical mutation evidence, while preserving the inherited whole-diff behavior and leaving the parked entity untouched.

This task explicitly supersedes parked entity `7rgdvsjypgmzk8wh03h3vst9`; it does
not reopen, advance, or alter that entity or its exhausted correction loop.

## Defect-lane classification

All four bounded-defect conditions hold:

1. Root cause is identified at `docs/dev/_mods/pr-merge.md:394`: the sentence
   claims the focused fixture falsifies every local guard, while the fixture
   exercises only `PRODUCT_AUTHENTICATED`.
2. Acceptance is mechanical: deleting any one of the five local conditions
   must make its targeted mutation run red, and each refusal must leave the
   live entity at `status: validation`.
3. This is one test/docs seam: the extracted terminal function, its focused
   Bash fixture, and the one sentence describing that fixture's evidence.
4. No design choice is open: retain the five existing guards and bound the
   prose to exactly the evidence added for them.

Design: `trivial-pass` — restore proof for the already-defined local guard
contract without changing terminalization, archive, or authentication design.

Appetite: one implementation dispatch, estimated 30 minutes. Tolerance: 15
additional minutes. If the repair needs a new route, file, mechanism, or claim,
stop and return it rather than widening this defect.

Implementation dispatch sizing: one worker in one isolated worktree rooted at
parked product head `57ddb26b32e03a3e5f4136f603d2319cad3881a5`.
Validation allowance: exactly one fresh independent whole-diff pass.

## Acceptance criteria

**AC-1 — The bounded local-guard claim and executable evidence agree.**
The focused fixture independently refuses `PRODUCT_AUTHENTICATED`,
`PRODUCT_HOST_STATE`, `PRODUCT_MERGED_AT`, exact `PRODUCT_REF`, and non-empty
`PRODUCT_ARTIFACT_B64URL`; every refusal preserves `status: validation`. The
enumerated prose claim names exactly those five local conditions. The inherited
AC-1 through AC-4 suite remains green and full-denominator added-executable
coverage remains at least 85% against freshly verified `origin/main`.
Verified by: the table-driven targeted phase, five guard-deletion adversarial
mutations, focused `all`, and independent out-of-tree Bash/Python-heredoc
coverage. Falsified by: any guard deletion staying green, any refusal changing
status, the prose naming broader evidence, full `all` failing, or coverage below
85%.

## Test plan

1. Before the fix, delete `PRODUCT_HOST_STATE` and `PRODUCT_REF` guards in
   scratch contract copies and record that `terminal-without-ledger` stays green.
2. Add the smallest one-setup table-driven five-negative matrix and observe RED
   before recutting the prose.
3. Recut only the broad sentence to enumerate the five locally tested inputs.
4. Prove each of five guard-deletion mutations makes the targeted phase red.
5. Run targeted/full fixture, independent complete coverage, Bash syntax,
   ShellCheck, `git diff --check`, and exact changed-path checks.

## Pre-mortem

The likely failure is a fixture-authored route making a stronger claim than the
extracted production/doc marker actually supports. Mutation proof therefore
edits only the extracted marker and must redden the targeted fixture.

## Measurement

- D1 launched 2026-07-31T16:30:42Z | tokens: n/a (Codex runtime does not expose per-worker usage)

## Approved doc diff

- Before: the focused fixture "falsifies every guard consumed by this function."
- After: the focused fixture tests only the five named local inputs; upstream
  artifact/host reconciliation remains explicitly assigned to existing fixtures.

## Out of scope

README changes beyond the inherited commits; ROADMAP, ledger, CI, daemon,
persistence, task creation, analytics, archive/authentication routes, Carlove,
push, PR creation, merge, and handoff.

## Stage Report: implementation

- DONE: AC-1 — The bounded local-guard claim and executable evidence agree.
  Verified by: the five named mutation failures, the refusal-path status-drift
  failure, focused `all`, and independent `392/447=87.70%` coverage below.
  Falsified by: any named mutation staying green, refusal changing state, a
  broader prose claim, a failing inherited phase, or coverage below 85%.

### Summary

On 2026-08-01, implemented the bounded proof recovery in code commit
`2bd5a2386fa4c803e62d6adb32556c43c5bd93cd`. One fixture setup now drives
five independent local refusal cases and preserves `status: validation`; the
adjacent prose names exactly those five conditions and no archive or upstream
authentication guarantee. The inherited whole-diff proof remains green with
87.70% complete executable-surface coverage.

### Identity and scope

- Task id/path: `1a1c5f9k2m3cjmmhzf7162dv` at
  `docs/dev/.spacedock-state/recover-decoupled-ledger-guard-proof.md`.
- Branch: `spacedock-ensign/recover-decoupled-ledger-guard-proof`.
- Worktree: `.worktrees/spacedock-ensign-recover-decoupled-ledger-guard-proof`.
- Verified base: parked head `57ddb26b32e03a3e5f4136f603d2319cad3881a5`;
  fresh `origin/main@1d6d0d02d4b0d6c84eac0813e6962c6774e652b7` is its ancestor,
  so replay was a no-op. Final head: `2bd5a2386fa4c803e62d6adb32556c43c5bd93cd`.
- This task changes only `docs/dev/_mods/pr-merge.md` and
  `docs/dev/artifacts/decoupled-ledger-contract-test.sh`. The inherited full
  diff still has exactly those paths plus unchanged `docs/dev/README.md`.

### RED and adversarial evidence

- Before the matrix, scratch deletions of `PRODUCT_HOST_STATE` and
  `PRODUCT_REF` both left `terminal-without-ledger` green at exit 0, reproducing
  the blind spot. The same copies red immediately after adding the matrix.
- Five syntax-checked final marker mutations each exited 1 at its named case:
  `PRODUCT_AUTHENTICATED`, `PRODUCT_HOST_STATE`, `PRODUCT_MERGED_AT`,
  `PRODUCT_REF`, and `PRODUCT_ARTIFACT_B64URL` each reported
  `guard accepted invalid local evidence`.
- A separate refusal-path state-drift mutation exited 1 with
  `PRODUCT_AUTHENTICATED refusal changed task state`, proving the shared status
  assertion can fail rather than merely decorating the matrix.

### GREEN and exit evidence

- `bash docs/dev/artifacts/decoupled-ledger-contract-test.sh terminal-without-ledger`
  exited 0 after emitting the five expected refusal diagnostics.
- `bash docs/dev/artifacts/decoupled-ledger-contract-test.sh all` exited 0:
  terminal-without-ledger, compatibility, archive-derive, and exact scope pass.
- Independent out-of-tree coverage at
  `/tmp/decoupled-ledger-coverage.23hKSF/measure.py` counted Bash `309/355`
  plus Python heredocs `83/92`, total `392/447=87.70%`; no tracked exclusion or
  waiver participates in the denominator.
- `bash -n` on the fixture and extracted terminal marker, `shellcheck` on the
  fixture, `git diff --check`, and Markdown fence parity all exited 0.
- The focused fixture is manual and no CI file changed, so this recut adds no
  CI-enlisted runtime or job-margin claim.

### Effort and residual

Elapsed implementation effort was about 7 minutes against the 30-minute
estimate plus 15-minute tolerance, with one dispatch. No implementation
residual is known. Exactly one fresh independent whole-diff validation pass
remains; no product/state push, PR, merge, parked-entity mutation, Carlove
handoff, or worktree cleanup was performed.

## Stage Report: validation

- DONE: Re-anchored the clean product worktree at exact head
  `2bd5a2386fa4c803e62d6adb32556c43c5bd93cd` against freshly fetched
  `origin/main@1d6d0d02d4b0d6c84eac0813e6962c6774e652b7`; the base is a strict
  ancestor.
- DONE: Audited all 61 hunks across the three-path whole diff and reproduced
  inherited AC-1 through AC-4 with real `spacedock 0.26.0 (contract 3)`.
- DONE: Independently falsified each of the five local guards and the shared
  refusal-path status-preservation assertion.
- DONE: Re-measured every added executable Bash/Python statement with an
  independent tracer and no executable exclusions or waivers.
- DONE: Audited the absolute claims, state scope, exact changed paths, and
  parked-entity byte identity.

### Independent evidence

- Product/base: clean exact head
  `2bd5a2386fa4c803e62d6adb32556c43c5bd93cd`; fresh base
  `1d6d0d02d4b0d6c84eac0813e6962c6774e652b7`; strict ancestry passed.
- Whole diff: only `docs/dev/README.md`, `docs/dev/_mods/pr-merge.md`, and
  `docs/dev/artifacts/decoupled-ledger-contract-test.sh`; 61 hunks; exact
  scope hash
  `23b51e52744cdc8fe5f1746838db0c42eaf62c72941dc6776791066ac1792f5c`.
- Inherited behavior: `terminal-without-ledger`, `compatibility`,
  `archive-derive`, and `scope` each exited 0 independently; a final fresh
  `all` run also exited 0. The compatibility phase exercised all six ledger
  forms plus reachable/unreachable direct-mode behavior.
- Guard falsification: five scratch-only, syntax-checked marker mutations each
  exited 1 at its named `guard accepted invalid local evidence` assertion for
  `PRODUCT_AUTHENTICATED`, `PRODUCT_HOST_STATE`, `PRODUCT_MERGED_AT`,
  `PRODUCT_REF`, and `PRODUCT_ARTIFACT_B64URL`.
- State falsification: a separate direct refusal-path byte mutation exited 1
  with `PRODUCT_AUTHENTICATED refusal changed task state`, proving the shared
  status assertion detects drift.
- Independent full-denominator coverage: Bash `388/433=89.61%`; all eight
  Python heredocs `123/137=89.78%`; combined `511/570=89.65%`. The denominator
  includes every added executable statement; no executable exclusion, waiver,
  or implementation coverage helper was used.
- Static checks: fixture, extracted terminal marker, and extracted archive
  marker passed `bash -n`; fixture passed ShellCheck 0.11.0; `git diff --check`
  and Markdown fence parity passed.
- Absolute-claim audit: each new five-guard and status-preservation claim has
  the red mutation above. Inherited non-authority, compatibility, byte-exact
  archive, and exact-scope claims were exercised by the full fixture and whole
  61-hunk audit. A fourth changed path or any task, daemon, CI, metric, or
  product-authority hunk would falsify the scope claim; none exists.
- Review lenses: correctness PASS/0 Material; security PASS/0 Material;
  silent-failure PASS/0 Material; manifest/backward-compatibility PASS/0
  Material. No type, concurrency, resource-lifecycle, CI, or runtime surface
  changed in the bounded recovery commit.
- E2E: the split-root, bare-origin fixture ran through real Spacedock 0.26.0
  and all phases passed. Cross-model judgment remains pending for the separate
  Claude Science Officer EM gate authorized after this evidence pass.
- State isolation before this report: state head
  `c9d3b732623ca6ed6ac5c171b260d1b8cecd3757`, remote state head
  `e994be184b7f31ef9193959831112185b26f9f45`, and parked-entity blob
  `0f88ef000d87862412232de3fedad18cbfca80c2`; only this new entity differed
  from the remote/seed state.

No Material finding was found in this bounded pass. The evidence is PASS-ready
for the separate Claude Science Officer EM gate; this report does not set a
verdict. Residual: the local matrix proves only the five enumerated local
inputs. `authenticate_terminal_route` and `durable_archive` remain
fixture-authored inherited routes, so this pass does not claim that the local
matrix independently proves upstream authentication or durable archiving.

## Stage Report: validation (replacement validation after base refresh)

- DONE: Re-establish the exact product/base identity after the authorized base refresh.
  Fresh fetches retained `origin/main@71084954a55e2b57371486367ff51d00508b1973`,
  strict ancestor of clean local head `74c66b0204c14ce3a5adc0ec19d39287c5245a3a`.
- DONE: Prove the rebased four-commit series is patch-equivalent and audit the whole diff.
  Four `git range-diff` entries were `=`, all stable patch IDs matched, and old/new binary
  diffs were byte-identical at SHA-256 `23b51e52744cdc8fe5f1746838db0c42eaf62c72941dc6776791066ac1792f5c`.
- DONE: Re-run inherited AC-1 through AC-4 plus the final `all` fixture on the refreshed base.
  Every phase exited 0 with real `spacedock 0.26.0 (contract 3)` from the exact product worktree.
- DONE: Re-run all five guard deletions and the refusal-state-drift mutation out of tree.
  Every scratch mutation exited 1 at its intended named assertion; product HEAD stayed clean.
- DONE: Re-measure the complete added executable surface without exclusions or waivers.
  Independent Bash plus Python statement/branch tracing measured `525/598=87.79%`.

### Replacement evidence

- Captain authorization (2026-08-01): local rebase, later force-with-lease, and exactly one
  replacement validation because `origin/main` advanced after the prior EM gate. This pass made
  no product edit, rebase, push, force-push, PR mutation, cleanup, or parked-entity mutation.
- Old series: base `1d6d0d02d4b0d6c84eac0813e6962c6774e652b7`, head
  `2bd5a2386fa4c803e62d6adb32556c43c5bd93cd`. New series: base
  `71084954a55e2b57371486367ff51d00508b1973`, head
  `74c66b0204c14ce3a5adc0ec19d39287c5245a3a`. Patch IDs matched for all four commits.
- Whole diff: only `docs/dev/README.md`, `docs/dev/_mods/pr-merge.md`, and
  `docs/dev/artifacts/decoupled-ledger-contract-test.sh`; 61 hunks (`26/34/1`),
  1,068 insertions and 592 deletions. Every added hunk was audited; no task/entity creator,
  daemon, scheduler, CI trigger, runtime file, automatic process mutation, or metric gate entered.
- Base advance `7108495` added ledger row `rd55vfpddtyvsbfqxqecj6cx`; `archive-derive` passed
  against that refreshed file while still reproducing the exemplar row byte-for-byte.
- Fresh commands `terminal-without-ledger`, `compatibility`, `archive-derive`, `scope`, and
  `all` each exited 0. Compatibility exercised empty/draft/pending/numbered/merged/malformed
  ledger refs, rejected unreachable direct commit, and archived the reachable direct route.
- Five syntax-checked guard deletions each exited 1 with its named `guard accepted invalid local
  evidence` assertion. The separate drift mutation exited 1 at
  `PRODUCT_AUTHENTICATED refusal changed task state`.
- Coverage: Bash physical/logical execution `390/433=90.07%`; all eight Python heredocs under
  statement-and-branch tracing `135/165=81.82%`; combined `525/598=87.79%`. This is a fresh,
  more conservative denominator, not the inherited `511/570`; no tracked helper, exclusion,
  pragma, or waiver changed the denominator.
- Static exits: fixture plus both extracted markers passed `bash -n` and ShellCheck 0.11.0;
  `git diff --check` passed; README fences stayed `30/30`, pr-merge fences `24/26`, and both
  marker pairs were exactly `1/1`.
- Absolute-claim scan reviewed all 93 added hit lines. Local-guard/state claims have the six red
  mutations; path/hunk/hash and historical-byte claims have scope/compatibility/derivation proof;
  the remaining lifecycle absolutes are bounded to the reviewed product-only transaction.

### Findings and residuals

No Material finding was found. Correctness, security/trust-boundary, silent-failure,
manifest/back-compatibility, state isolation, and exact-scope lenses pass; no type, concurrency,
resource-lifecycle, CI, or product-runtime surface changed in this replacement diff.

Two bounded residuals remain explicit: `authenticate_terminal_route` and `durable_archive` are
fixture-authored routes, not independent upstream authentication/archive proof; and the five-case
matrix pins refusal plus unchanged `status: validation`, but not the exact refusal return class or
diagnostic strings. Neither residual broadens the five local-guard claim.

The remote product branch was still deliberately old at
`2bd5a2386fa4c803e62d6adb32556c43c5bd93cd` during this gate. This evidence is PASS-ready for a
separate fresh Claude Science Officer EM gate; this report leaves `status: validation`,
`completed:`, and `verdict:` unchanged.

### Summary

The captain-authorized base refresh preserved the exact four-patch product change, and fresh
behavioral, mutation, static, scope, coverage, and absolute-claim evidence found no Material drift.
Only this replacement validation report was added to state; product content stayed unchanged.
