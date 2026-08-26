---
title: Make Production recovery proportional
status: implementation
source: "Captain-approved kc-dev-flow/S5 design: known Production repairs should retain exact proof without repeating resolved shape work"
product: kc-dev-flow
sprint: S5
sprint-readiness: ready
started: 2026-08-26T06:17:44Z
completed:
verdict:
worktree: .worktrees/spacedock-ensign-production-recovery-route
issue:
pr:
mod-block:
design: required
lane: main
id: za5drqh93q5522c6kstrxrsx
gates:
    version: 1
    records:
        - id: gate:za5drqh93q5522c6kstrxrsx:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:za5drqh93q5522c6kstrxrsx-backlog-1
              briefing:
                id: briefing:za5drqh93q5522c6kstrxrsx:backlog:attempt-1:revision-1
                digest: sha256:961bbed0d4b713fb3fa268a47854856cecba773ba5e41db22e3c5655cafafde7
                request-digest: sha256:541807e04fb832e47616caf1195f4ba2f71eafc14b5e4b3c1d37dd39bf92e0dc
                room-ref: ./production-recovery-route/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:za5drqh93q5522c6kstrxrsx:backlog:1
                briefing: briefing:za5drqh93q5522c6kstrxrsx:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-08-26T06:16:11.487243Z"
                decision: approve
                reason: Captain approved the S5 Production recovery direction to enter ideation and produce the formal design spec.
              application:
                target-stage: ideation
                state: consumed
        - id: gate:za5drqh93q5522c6kstrxrsx:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:za5drqh93q5522c6kstrxrsx-ideation-1
              briefing:
                id: briefing:za5drqh93q5522c6kstrxrsx:ideation:attempt-1:revision-1
                digest: sha256:158618a1d9e6faacdea3cd8e455446d2f80caeda56f6806099b7682f1976e88f
                request-digest: sha256:a34c17f877575cf77f6e85ad597d9c449a93e9989506b1878a06083a129a108f
                room-ref: ./production-recovery-route/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:za5drqh93q5522c6kstrxrsx:ideation:1
                briefing: briefing:za5drqh93q5522c6kstrxrsx:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-08-26T06:40:49.712967Z"
                decision: revise
                reason: Reduce the recovery receipt to route plus failure, falsifier, rollback, and review risks; remove duplicated shape/scope hashes and generic reverse-delta machinery; shrink the first slice materially below 16 files and 901 lines.
            - id: gate-attempt:za5drqh93q5522c6kstrxrsx-ideation-2
              briefing:
                id: briefing:za5drqh93q5522c6kstrxrsx:ideation:attempt-2:revision-1
                digest: sha256:2ba7e63286438a3413aaeb2463477c3170d49d80d653227aae5b01d6f8937668
                request-digest: sha256:2d8e50e0c212537f869998e4c5440f14eabdcf91461ea66cad267cfd88795e30
                room-ref: ./production-recovery-route/review/ideation/briefing-2
              resolution:
                type: Resolution
                id: resolution:spacedock:za5drqh93q5522c6kstrxrsx:ideation:2
                briefing: briefing:za5drqh93q5522c6kstrxrsx:ideation:attempt-2:revision-1
                by: person:captain
                at: "2026-08-26T07:02:33.085169Z"
                decision: approve
                reason: Captain approved the revised minimal Production recovery design at commit d38799a after independent re-review passed.
              application:
                target-stage: implementation
                state: consumed
---

Add a fail-closed Production recovery route for exact, bounded, reversible failures while preserving the existing full route as the default.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: production
  recommended: production
  basis: >-
    This changes the public route and evidence contract used by adopters at a
    production delivery boundary. Existing receipts must remain compatible and
    an ineligible shortcut could weaken release evidence.
  route: [shape, build, verify]
  obligations:
    architecture:
      - Keep one workflow and the existing POC, Pilot, and Production profiles.
      - Define additive recovery eligibility, invalidation, and default-full behavior.
      - Preserve the accepted S5 seams for Captain UAT and per-item auto-merge follow-ups.
    implementation:
      - Let an explicitly eligible Production receipt select build then verify without an ideation dispatch.
      - Make optional implementation-exit review depend on accepted risk rather than the Production label alone.
    testing:
      - Prove legacy receipts still select shape, build, verify.
      - Prove eligible recovery receipts select build, verify and malformed or drifting receipts fail closed.
      - Prove implementation uses focused red-green and fresh validation owns the single full without-it.
  scope_boundary: >-
    This item implements only the Production recovery route and its evidence
    triggers. Captain UAT and automatic merge execution remain the next two S5
    items; no new profile, workflow, stage, CI job, or release authority.
  promote_when:
    - Stop for Captain scope if compatibility requires a receipt schema bump or a Spacedock engine change.
  decision:
    authority: Kent (Captain)
    at: 2026-08-26T06:13:25Z
```

## Intended outcome

An exact known Production failure can skip redundant shape work while retaining one fresh full falsifier at validation and failing closed on uncertainty or scope drift.

## Acceptance criteria

**AC-1 — Full Production remains the default.** Existing supported receipts still load `shape -> build -> verify` without migration.

**AC-2 — Recovery is explicit and fail closed.** Only a Captain-recorded eligible recovery receipt loads `build -> verify`; missing evidence, uncertainty, or changed scope refuses or returns to shape.

**AC-3 — Evidence is proportional.** Implementation runs focused red-green checks, while fresh validation runs the one full without-it required by the accepted guard claim.

**AC-4 — Review follows risk.** Deterministic recovery does not invoke RoboRev solely because the profile is Production; an accepted specialist risk still can.

**AC-5 — The S5 boundary stays intact.** No new profile, workflow state, CI job, auto-merge action, UAT self-approval, or release authorization enters this slice.

## Delivery boundary

Deliver through one Captain-reviewed PR to `main`. This authority-changing item keeps manual merge; release remains separately authorized.

## Stage Report: ideation

- DONE: Write and commit one formal S5 design spec covering Production recovery, Captain-owned UAT for all profiles, and per-item auto-merge, with exact authority and invalidation boundaries.
  Commit `dc7a1c8` adds `docs/superpowers/specs/2026-08-26-kc-dev-flow-proportional-production-delivery-design.md`; changed head/base, scope, evidence, and authority cases each have a named non-green outcome.
- DONE: Define the first implementation slice only: additive v3 recovery routing, legacy full-route compatibility, risk-triggered review, one fresh full without-it, file touch points, and stop numbers.
  The spec limits implementation to recovery, maps 16 expected files from base `5707a6f`, stops at 17 files/901 changed lines/281 loader-test lines, and would fail on a schema bump, engine change, new CI job, or later-interface edit.
- DONE: Record the brownfield reverse-recovery receipt and retained-document checks; self-review the spec for placeholders, contradictions, ambiguous defaults, and duplicated live claims.
  The spec records the four-layer `reverse_recovery` receipt, two-strategy per-section overlap check, intentional typed metavariables, and explicit defaults of full route, risk-triggered review, Captain UAT, manual merge, and manual release.

### Summary

The design preserves one workflow, three profiles, the superset graph, v3 compatibility, and existing Captain and release authority while making eligible Production recovery `build -> verify`. Only the recovery interface enters the first implementation boundary; UAT and auto-merge retain separate ownership and no implementation began in ideation.

## Stage Report: ideation (cycle 2)

- DONE: Replace the ten-field recovery block with route plus failure, falsifier, rollback, and review risks; reuse the existing work-item hash, scope boundary, decision authority, and exact-diff checks.
  Commit `0b5bfd6` keeps only `recovery_failure`, `recovery_falsifier`, `recovery_rollback`, and `review_risks`, with existing `scope_boundary`, `decision`, loader hash, and stage diff ownership.
- DONE: Remove the generic reverse-delta harness design; make one task-owned full without-it a validation obligation and keep implementation focused red-green only.
  The corrected spec adds no executable, receipt command, patch algorithm, or ablation harness; validation records the task-owned full without-it and build owns focused red-green.
- DONE: Recut the first slice materially below 16 files and 901 lines, preserve all S5 authority boundaries, update the Stage Report, and commit only the corrected spec.
  The slice now maps 8 files and stops at 9 files/451 changed lines/201 loader-test lines; Captain UAT, per-item auto-merge, manual release authority, v3 compatibility, and fail-closed routing remain intact.

### Summary

The revised design removes duplicated recovery identity and generic negative-control machinery while preserving the accepted `build -> verify` behavior and risk-triggered review. Only the corrected retained spec changed; implementation remains unstarted.

## Stage Report: ideation (cycle 3)

- DONE: Add docs/dev/README.md to the first-slice touch table because the self-adopted route and RoboRev activation claims must change with the package contract.
  Commit `d38799a` adds the 320-line self-adopted workflow README with an estimated 332 lines and binds both its route and recovery-specific RoboRev claims.
- DONE: Reword rollback so an active recovery item stops before the old loader and waits for Captain-authorized re-recording of the full route; do not grant mechanical fallback authority.
  Rollback now stops before old-loader use and requires Captain authorization unless the existing `recovery_rollback` explicitly grants that exact rewrite and state transition.
- DONE: Recalculate the file and changed-line stop conditions, preserve all other cycle-2 minimality decisions, update the Stage Report, and commit only the corrected spec.
  The nine-file slice stops above 9 files, 475 changed lines, or 200 loader-test lines; the four fields, task-owned without-it, review trigger, and later S5 boundaries are unchanged.

### Summary

The corrected spec now covers both package and self-adopted live claims without expanding the recovery mechanism. Rollback retains Captain authority, and implementation remains unstarted.

## Stage Report: implementation

- DONE: Implement the additive v3 Production recovery receipt with only recovery_failure, recovery_falsifier, recovery_rollback, and review_risks; preserve legacy v2/v3 full-route behavior and byte-identical adopter loader/kernel copies.
  Commit `a97f157` adds only the four recovery fields; legacy route fixtures stay green, while either vendored copy drifting makes the two `cmp -s` checks fail.
- DONE: Make a valid recovery at ideation emit a fail-closed skip to implementation, then load build and verify normally; reject malformed, non-Production, unsupported-stage, or changed-premise recovery.
  `profile-contract-loader.test.py` rejects the refusal matrix, changes the bound hash on premise edits, and would fail if the real Spacedock fixture loaded shape or created an ideation review artifact.
- DONE: Update choose-work-profile, continue-dev-flow, package README/kernel, and self-adopted docs/dev/README.md so recovery selection, exact-diff rechecks, Captain fallback authority, and risk-triggered RoboRev agree.
  `scripts/kc-dev-flow-contract-test.py` passes against the package/adopter contracts; removing parity or a supported profile-stage mapping makes it fail.
- DONE: Add focused tests for legacy routes, eligible recovery, refusal cases, real Spacedock transition/no ideation artifact, and review_risks none versus named risk; do not run or add the validation-owned full without-it here.
  The focused loader test reports route mechanism PASS and overall PASS; changing the short route, risk grammar, skip output, or build/verify loads breaks a named assertion.
- DONE: Run scoped implementation checks, enforce the design stop conditions, commit only the approved nine-file product slice, and append one implementation Stage Report with exact evidence and residuals.
  Exact diff is 9 files and 440 gross lines, with 199 gross loader-test lines; `git diff --check d38799a`, parity, contract, and focused checks pass with no schema, engine, CI, UAT, or auto-merge change.

### Summary

Production keeps the full route by default and now accepts an explicit fail-closed recovery skip whose risks control optional review. Fresh validation still owes the task-owned full without-it; implementation intentionally did not run or add it.

### RoboRev implementation-exit claim

```yaml
identity: 2271f2071b6f8de4b6314c1826a31ceb4fed43ae2c81e4a940f9ccc4b76fc83e
configuration_sha256: db38e0744902a028bdea1e69b26a5af28f5a849412284f6699124ec201517bb8
base: d38799af4d980498bfc51380c33e11266cedbafa
tip: a97f157e53f53755d0bfbea1808577fed72a1e07
claimant: codex:01a03ce1-7c69-76e2-b818-49f4098fddd2
observed_state_revision: 35d5268353b1b0f6744e9cc5d024c168952b04b7
state: claimed
```
