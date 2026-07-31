---
title: Recover the decoupled-ledger local guard proof
status: validation
source: captain approval plus high-confidence Claude Science Officer EM narrow judgment on 2026-08-01; supersedes parked entity id 7rgdvsjypgmzk8wh03h3vst9 without altering it
product: repo-platform
sprint:
started: 2026-07-31T16:30:42Z
completed:
verdict:
worktree: .worktrees/spacedock-ensign-recover-decoupled-ledger-guard-proof
issue:
pr:
ledger_pr:
pr_artifact_v1:
ledger_artifact_v1:
mod-block:
design: trivial-pass
lane: defect
id: 1a1c5f9k2m3cjmmhzf7162dv
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
