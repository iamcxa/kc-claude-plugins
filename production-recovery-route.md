---
title: Make Production recovery proportional
status: validation
source: "Captain-approved kc-dev-flow/S5 design: known Production repairs should retain exact proof without repeating resolved shape work"
product: kc-dev-flow
sprint: S5
sprint-readiness: ready
started: 2026-08-26T06:17:44Z
completed:
verdict:
worktree: .worktrees/spacedock-ensign-production-recovery-route
issue:
pr: 299
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
        - id: gate:za5drqh93q5522c6kstrxrsx:validation
          stage: validation
          attempts:
            - id: gate-attempt:za5drqh93q5522c6kstrxrsx-validation-1
              briefing:
                id: briefing:za5drqh93q5522c6kstrxrsx:validation:attempt-1:revision-1
                digest: sha256:65c8b1f1f39d15b334ab7ac3203585608f7972ae463d4af0dce2280ce7d4c0fa
                request-digest: sha256:9065e228a543900b43d5eb9aa814b63adfd4d2bc1ce6152403afed1d680103a2
                room-ref: ./production-recovery-route/review/validation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:za5drqh93q5522c6kstrxrsx:validation:1
                briefing: briefing:za5drqh93q5522c6kstrxrsx:validation:attempt-1:revision-1
                by: person:captain
                at: "2026-08-26T08:27:03.881908Z"
                decision: approve
                reason: Captain approved delegated exact-candidate E2E UAT and Production validation for b6092e6, retaining RoboRev UNKNOWN(state_unknown) as a visible non-gating residual.
              application:
                target-stage: done
                state: superseded
            - id: gate-attempt:za5drqh93q5522c6kstrxrsx-validation-2
              briefing:
                id: briefing:za5drqh93q5522c6kstrxrsx:validation:attempt-2:revision-1
                digest: sha256:cd8f08b0b3093db0835463ab0d649eaaebbbf7399e59bf52af6f506a83c3e274
                request-digest: sha256:e1346fbe35e2109cfc203b5e3317e0b74eb1d4f45dd719536af361662de40eda
                room-ref: ./production-recovery-route/review/validation/briefing-2
              resolution:
                type: Resolution
                id: resolution:spacedock:za5drqh93q5522c6kstrxrsx:validation:2
                briefing: briefing:za5drqh93q5522c6kstrxrsx:validation:attempt-2:revision-1
                by: person:captain
                at: "2026-08-26T09:25:33.362576Z"
                decision: approve
                reason: Captain approved exact candidate 2b8abff after delegated Terra medium UAT loaded the Production recovery build contract, observed RED to GREEN with one isolated fixture change, performed no shape work, launched no RoboRev request, and left the product candidate clean.
              application:
                target-stage: done
                state: pending
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

## Implementation scope adjustment

Captain approved one replacement threshold after validation exposed stale
route-string assertions in the same repository contract test. Implementation
may now change at most 10 product files while remaining at or below 475 gross
changed lines and 200 gross loader-test lines. The sole added path is
`scripts/kc-dev-flow-contract-test.py`, limited to replacing that exact failure
shape wherever the full gate exposes it, including kernel, chooser,
continuation, package, and self-adopted route claims. Each replacement must
independently require the full Production route and the eligible recovery
clause. No other scope, mechanism, or authority changed.

## Rework scope adjustment

Captain replaced the host-complementary RoboRev mapping with one repository and
package policy: every supported host uses agent `codex`, model
`gpt-5.6-terra`, reasoning `medium`, and panel `none`. The implementation host
family remains recorded provenance but no longer selects the reviewer;
profile-owned minimum severity and request caps remain unchanged.

This rework also closes the two confirmed Terra findings: recovery evidence
scalars must reject YAML structural and block forms, and the loader must emit a
machine-readable implementation-exit observation decision so recovery
`review_risks: [none]` suppresses RoboRev while named risks activate it. The
replacement stop lines are 18 feature files, 650 gross changed lines, and 235
gross loader-test lines. No new workflow, CI job, schema version, release
authority, or reusable review service is authorized.

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

### RoboRev implementation-exit result

```yaml
capability: review_convergence
mode: observe
selected_profile: production
provider: roborev
provider_version: v0.62.0
outcome: UNKNOWN
reason: state_unknown
identity: 2271f2071b6f8de4b6314c1826a31ceb4fed43ae2c81e4a940f9ccc4b76fc83e
configuration_sha256: db38e0744902a028bdea1e69b26a5af28f5a849412284f6699124ec201517bb8
base: d38799af4d980498bfc51380c33e11266cedbafa
tip: a97f157e53f53755d0bfbea1808577fed72a1e07
agent: claude-code
model: sonnet
reasoning: thorough
minimum_severity: medium
panel: none
job_identity: not_observed
member_states: []
request_count: 1
confirmation_count: 0
cost_coverage:
  total_usd: 0
  jobs_with_cost: 0
  jobs_total: 0
  complete: false
diagnostic: >-
  The single explicit request returned "no commits since d38799a" before
  enqueue; the registered repository remained at two prior jobs and exact-tip
  show returned no review. Zero post-request candidates makes launch identity
  indeterminate, so no retry is allowed.
```

## Stage Report: implementation (cycle 2)

- DONE: Resolve the exact candidate a97f157, base d38799a, candidate configuration hash, Production build observation, and complementary Claude Code reviewer; probe required RoboRev capability without installing or updating anything.
  Candidate config is `db38e074…`, identity is `2271f207…`, and RoboRev v0.62.0, daemon health, JSON help, and `claude-code` auth probe succeeded without setup mutation.
- DONE: Follow the registered state-holder single-flight transaction exactly: reuse matching exact-input evidence if present, otherwise claim once through scripts/dev-flow-state-prereq.sh and spacedock state commit before any provider request.
  Exact-tip lookup found no reusable job; the sole claim was committed and pushed as state commit `88fdc3b` after equal-tip and sole-dirty checks.
- DONE: Make at most one initial request with explicit agent claude-code, model sonnet, reasoning thorough, minimum severity medium, panel none, exact base/tip, and 1200-second timeout; never retry an ambiguous launch.
  One explicit exact-range request returned before enqueue with `no commits since d38799a`; post-request population had zero new candidates, so request count stayed one and confirmation count zero.
- DONE: Correlate only canonical JSON evidence. Record PASS, FAIL, UNKNOWN, or UNAVAILABLE with reason, identity/config hashes, job identity if known, request/confirmation counts, and cost coverage in the existing implementation evidence.
  Result is `UNKNOWN(reason: state_unknown)`: no canonical job identity exists; branch-scoped cost JSON is USD 0 with 0/0 jobs and `complete: false`.
- DONE: Do not change product files or the implementation commit. Commit and sync only the resulting state report through supported Spacedock state transaction.
  Product head remains clean at `a97f157`; this cycle changes only the bound state entity and leaves validation and stage advancement untouched.

### Summary

The candidate-bound observation claimed single-flight ownership and spent its one request without producing a correlatable RoboRev job. The honest result is UNKNOWN, carried into fresh validation without retry, product change, or authority effect.

## Stage Report: validation

- DONE: Freshly bind candidate a97f157, implementation base d38799a, current merge target origin/main, accepted spec/ACs, exact nine-file diff, and the carried RoboRev UNKNOWN; make no product edits.
  Candidate `a97f157e53f53755d0bfbea1808577fed72a1e07`, base `d38799af4d980498bfc51380c33e11266cedbafa`, fetched target `f7a3f018e9756c44b354c3a24326594b084b044b`, merge-base `e20d13b5b1fb06921db58b6a0f132401dfc1fe9d`, accepted spec SHA-256 `21a2a9b0…`, and 9 files/419 insertions/21 deletions were observed with a clean product tree; RoboRev remains `UNKNOWN(state_unknown)`.
- FAILED: Run the complete relevant candidate gate from a clean exact-tip worktree: scripts/kc-dev-flow-contract-test.py, loader/kernel package-adopter parity, and git diff --check; require the real Spacedock recovery journey to pass.
  The direct complete loader test, real recovery journey, byte-identical loader/kernel parity, and `git diff --check` passed, but `scripts/kc-dev-flow-contract-test.py` exited 1 because `scripts/roborev-implementation-exit-contract.test.py` still requires the superseded Local Profile phrase `Typed RoboRev observation at every profile's implementation exit`; changing that stale assertion to the accepted risk-triggered contract is the falsifying repair.
- SKIPPED: Run one task-owned full without-it in a temporary isolated copy: execute the complete candidate profile-contract-loader.test.py against the d38799a loader and require a nonzero failure at the recovery capability, not an unrelated setup failure; delete no repository data and add no reusable harness.
  Validation stopped fail-closed when the candidate full gate was non-green; the unexecuted temporary copy was removed, so no without-it result or reusable harness exists.
- DONE: Record exact-candidate E2E UAT evidence for backlog gate -> ideation skip with no ideation artifact -> implementation build -> validation verify, plus compatibility/default-full, rollback readiness, provider-feedback absence before PR, and material residuals.
  Candidate `profile-contract-loader.test.py` passed its real Spacedock skip/no-artifact/build/verify journey and legacy full-route fixtures; rollback is the recorded task reversal plus Captain-controlled full-route re-recording, no PR exists for provider feedback, and the red repository gate, unrun without-it, RoboRev UNKNOWN, divergent target, and missing Captain UAT remain material.
- FAILED: Return PASS only if every AC is falsifiably supported at the exact candidate; append one validation Stage Report and commit/sync only state. Do not create a PR, advance the gate, merge, release, or self-approve Captain UAT.
  Verdict is FAIL because the complete repository gate is red and the required without-it was not run; only this state report is committed, with no PR, gate advance, merge, release, or UAT approval.

### Summary

Exact-candidate recovery behavior and parity passed, but the required repository gate found a stale RoboRev Local Profile assertion and validation therefore fails. The work returns to implementation for one focused contract-test repair before fresh validation; RoboRev UNKNOWN and Captain-owned UAT remain visible and non-authoritative.

## Stage Report: implementation (cycle 3)

- DONE: Repair only the stale Local Profile assertion within the already approved docs/dev/README.md path; keep the exact required phrase while stating that the observation runs only where its trigger is active and Production recovery [none] invokes nothing.
  Commit `456ea29` restores the enforced phrase and immediately limits execution to an active trigger; the same row preserves named-risk activation and `[none]` non-activation for recovery.
- DONE: Run scripts/roborev-implementation-exit-contract.test.py and the complete scripts/kc-dev-flow-contract-test.py, plus diff-check and all prior parity/focused checks.
  Both named contract tests pass, as do the focused loader's real Spacedock journey, loader/kernel byte parity, and `git diff --check d38799a`; removing the phrase or parity makes its owning check fail.
- DONE: Keep the product diff at the same nine files and below 475/200 stop lines; do not change the test contract, schema, engine, CI, UAT, auto-merge, or release behavior.
  The exact slice remains 9 files and 440 gross lines with 199 gross loader-test lines; only one existing README line changed after `a97f157`.
- DONE: Amend or add one bounded repair commit, append the implementation repair Stage Report, and sync only the state report.
  Product repair is isolated in `456ea29`; RoboRev remains the spent-request `UNKNOWN(state_unknown)` and was not retried, and no stage or authority was advanced.

### Summary

The Local Profile again satisfies its enforcement contract while retaining risk-triggered recovery semantics. Fresh validation can now rerun the full gate and the deferred without-it against `456ea29`.

## Stage Report: validation (cycle 2)

- DONE: Freshly bind repaired candidate 456ea29, implementation base d38799a, current origin/main, accepted spec/ACs, exact nine-file diff, prior validation failure, and carried RoboRev UNKNOWN; make no product edits.
  Candidate `456ea299a4bcc1c3a5635a07564e15d6c2be1148`, base `d38799af4d980498bfc51380c33e11266cedbafa`, fetched target `f7a3f018e9756c44b354c3a24326594b084b044b`, merge-base `e20d13b5b1fb06921db58b6a0f132401dfc1fe9d`, spec SHA-256 `21a2a9b0…`, and 9 files/419 insertions/21 deletions were observed in a clean product tree; prior FAIL and RoboRev `UNKNOWN(state_unknown)` remain bound.
- FAILED: Run the complete relevant candidate gate from the clean exact-tip worktree: scripts/kc-dev-flow-contract-test.py, direct loader test, RoboRev contract test, loader/kernel parity, and git diff --check; require the real Spacedock recovery journey to pass.
  Direct loader/E2E, RoboRev contract, loader/kernel parity, and `git diff --check` passed, but `scripts/kc-dev-flow-contract-test.py` exited 1 because its kernel assertion still requires the pre-recovery exact table row; removing the accepted recovery clause makes that stale assertion pass, so the repository gate is not a valid green candidate gate.
- DONE: Run one task-owned full without-it in a temporary isolated copy: execute the complete candidate profile-contract-loader.test.py against the d38799a loader and require a nonzero failure at the missing recovery capability, not an unrelated setup failure; remove the temporary copy and add no harness.
  The candidate test with the `d38799a` loader exited nonzero at `stale route for production: expected ['shape', 'build', 'verify'], got ['build', 'verify']`; this is the missing recovery capability, and the explicit temporary worktree was removed with no harness or product change.
- DONE: Record exact-candidate delegated E2E UAT evidence for backlog gate -> ideation skip with no ideation artifact -> implementation build -> validation verify, plus compatibility/default-full, rollback readiness, current provider-feedback state, and material residuals.
  Candidate `profile-contract-loader.test.py` reported route mechanism PASS after the real Spacedock backlog gate, empty ideation skip/no artifact, build, and verify journey; legacy/default full routes passed, rollback stays Captain-controlled, no PR/provider feedback exists, and the red repository gate, four same-shape stale route assertions, RoboRev UNKNOWN, divergent target, and unapproved Captain UAT remain material.
- FAILED: Return PASS only if every AC is falsifiably supported at 456ea29; append one final validation Stage Report and commit/sync only state. Do not create a PR, prepare/approve the gate, merge, release, or self-approve Captain UAT.
  Verdict is FAIL because the complete repository gate is red at exact candidate `456ea29`; only this state report is committed, with no product edit, PR, gate advance, merge, release, or UAT approval.

### Summary

The repaired candidate's live recovery journey and full without-it both prove the recovery behavior, but the complete repository gate still rejects the accepted route documentation through stale exact-row assertions. Validation therefore fails and returns one bounded test-contract correction to implementation; Captain UAT remains pending and non-delegable.

## Stage Report: implementation (cycle 4)

- DONE: Modify only scripts/kc-dev-flow-contract-test.py as the newly authorized tenth product path.
  Commit `e03fb1b` changes only the contract test; the accepted implementation remains otherwise unchanged from `456ea29`.
- DONE: Replace the four stale exact-route string assertions for kernel, continue-dev-flow, docs/dev/README.md, and kc-dev-flow/README.md with semantic assertions that separately require the unchanged full Production route and the eligible recovery clause.
  One shared row helper now checks the full default and recovery clause independently at those four boundaries; the same approved failure shape also replaced the chooser literal found by the first full-gate rerun.
- DONE: Prove each revised assertion can fail for missing full-route default and missing recovery behavior; do not loosen unrelated contract coverage or change product documents again.
  An in-memory extraction of the committed helper rejected 10/10 mutations across five route rows: one missing-full and one missing-recovery mutation per boundary.
- DONE: Run the complete kc-dev-flow contract gate, direct loader test, RoboRev contract test, parity checks, and diff-check; keep the diff at or below 10 files, 475 gross lines, and 200 gross loader-test lines.
  The full gate reports PASS; direct loader/real Spacedock and RoboRev contracts pass, both package/adopter pairs are byte-identical, diff-check is clean, and the slice is 10 files/467 gross lines with 199 loader-test lines.
- DONE: Commit the bounded repair, append one implementation repair Stage Report, and sync only state; do not retry RoboRev or alter UAT/merge/release authority.
  Product repair is `e03fb1b`; RoboRev remains `UNKNOWN(state_unknown)` with no retry, while fresh validation still owns its rerun and Captain UAT decision.

### Summary

The complete gate now enforces both Production routes instead of preserving stale exact rows. This bounded test-only repair stays below every approved stop line and returns `e03fb1b` to fresh validation.

## Stage Report: validation (cycle 3)

- DONE: Freshly bind candidate e03fb1b, implementation base d38799a, current origin/main, accepted spec plus scope adjustment, exact ten-file diff, prior validation failures, and carried RoboRev UNKNOWN; make no product edits.
  Candidate `e03fb1b23148c5e7a92bbf42105a3146d6366b1f`, base `d38799af4d980498bfc51380c33e11266cedbafa`, fetched target `f7a3f018e9756c44b354c3a24326594b084b044b`, merge-base `e20d13b5b1cf06921db58b6a0f132401dfc1fe9d`, spec SHA-256 `21a2a9b0...`, prior two validation failures, and RoboRev `UNKNOWN(state_unknown)` were bound in a clean product tree; the exact slice is 10 files/467 gross lines with 199 gross loader-test lines.
- DONE: Run the complete candidate gate: scripts/kc-dev-flow-contract-test.py, direct full loader test, RoboRev contract test, loader/kernel parity, and git diff --check; require all five semantic route boundaries and the real Spacedock recovery journey to pass.
  The full gate, direct loader/E2E, RoboRev contract, both byte-parity checks, and diff-check passed; the committed route helper rejected missing-full and missing-recovery mutations at kernel, chooser, continuation, self-adopted workflow, and package README boundaries (10/10 controls), so deleting either route claim makes the owning check fail.
- DONE: Freshly rerun one task-owned full without-it in a temporary isolated copy: execute the complete candidate profile-contract-loader.test.py against the d38799a loader and require the missing recovery capability to fail for the named stale Production route, not setup; remove the temporary copy.
  The candidate test with the `d38799a` loader failed at `stale route for production: expected ['shape', 'build', 'verify'], got ['build', 'verify']`; the registered temporary worktree and its parent directory were then removed, and no reusable harness or product change remains.
- DONE: Record exact-candidate delegated E2E UAT evidence for backlog gate -> ideation empty skip/no artifact -> implementation build -> validation verify, plus legacy/default-full compatibility, rollback readiness, current provider-feedback state, and material residuals.
  Spacedock 0.27.0 live route mechanism PASS exercised the real backlog approval, empty ideation skip with no review artifact, build, and verify loads; legacy/default-full fixtures passed, rollback is one feature revert plus Captain-controlled full-route re-recording, no PR/provider feedback exists, and Captain UAT, RoboRev UNKNOWN, and the 1-behind/7-ahead divergent target remain material residuals.
- DONE: Return PASS only if every AC and replacement threshold is falsifiably supported at e03fb1b; append one final validation Stage Report and commit/sync only state. Do not create a PR, prepare/approve the gate, merge, release, or self-approve Captain UAT.
  Technical verdict is PASS at exact candidate `e03fb1b`: AC-1 through AC-5 and the 10-file/475-line/200-loader-test thresholds are supported by executable positive and negative evidence; this report changes only state and leaves Captain UAT, validation-gate approval, PR, merge, and release untouched.

### Summary

Exact candidate `e03fb1b` passes the complete gate, live recovery journey, five route-boundary mutation controls, and the single task-owned without-it. Technical validation recommends PASS, while Captain UAT remains the final verification decision and the divergent delivery target, absent provider feedback, and carried RoboRev UNKNOWN remain explicit.

## Stage Report: validation (cycle 4)

- DONE: Freshly bind rebased candidate b6092e6, feature base aebe6a0, merge target origin/main f7a3f01, accepted spec/scope adjustment, ten-file feature diff, twelve-file PR diff, and carried RoboRev UNKNOWN; make no product edits.
  Candidate `b6092e69a956a7afac39c52dd1951cef440ac2c8`, feature base `aebe6a08db33cfd809ca4d10004c0c2c8ddcd939`, and fetched target `f7a3f018e9756c44b354c3a24326594b084b044b` bind the accepted spec SHA-256 `21a2a9b0...`; the clean product tree has 10 feature files/467 gross lines/199 loader-test lines and 12 PR files, while RoboRev remains `UNKNOWN(state_unknown)` with no retry.
- DONE: Rerun the complete candidate gate after rebase: kc-dev-flow contract gate, direct loader test, RoboRev contract, loader/kernel parity, diff-check, five route-boundary negative controls, and real Spacedock recovery journey.
  The full gate, direct loader test, RoboRev contract, both byte-parity checks, and diff-check passed; the committed helper rejected missing-full and missing-recovery mutations at all five boundaries (10/10), and Spacedock 0.27.0 reported route mechanism PASS, so deleting either route or breaking the live skip/build/verify journey fails its owner.
- DONE: Freshly rerun the task-owned without-it in a temporary isolated copy using the complete b6092e6 loader test against the aebe6a0 loader; require the expected stale short-Production-route failure and remove the copy.
  The temp copy bound candidate test object `89cf4f1...` to base-loader object `0c82313...` and failed only at `stale route for production: expected ['shape', 'build', 'verify'], got ['build', 'verify']`; the registered copy and parent directory were removed, leaving no harness or product change.
- DONE: Record exact-candidate delegated E2E UAT evidence for backlog gate -> ideation empty skip/no artifact -> implementation build -> validation verify, plus default-full compatibility, rollback readiness, no current PR/provider feedback, and RoboRev UNKNOWN residual.
  The real split-root journey approved backlog, emitted an empty ideation skip without a review artifact, then loaded build and verify; legacy/full-route fixtures passed, rollback is the accepted landing-commit revert plus Captain-controlled full-route re-recording for active recovery items, `gh pr list` returned no PR, and Captain UAT plus RoboRev UNKNOWN remain explicit residuals.
- DONE: Return PASS only if all ACs remain supported after rebase and branch is 0 behind origin/main; append one validation Stage Report and sync only state. Do not create PR, prepare/approve gate, merge, release, or self-approve UAT.
  Technical verdict is PASS at `b6092e6`: AC-1 through AC-5 remain falsifiably supported, the branch is 0 behind/7 ahead `origin/main`, and this report changes only state; Captain UAT/validation approval, PR, merge, and release remain untouched.

### Summary

Rebased candidate `b6092e6` passes the complete deterministic gate, five semantic route boundaries, exact Spacedock recovery journey, and corrected isolated without-it. Technical validation recommends PASS; Captain UAT and validation approval remain the final authority, with no PR/provider feedback and the carried RoboRev UNKNOWN still visible.

## Stage Report: implementation (cycle 5)

- DONE: Replace host-complementary RoboRev selection with one fixed implementation-exit reviewer across package, adopter, local config, adoption/continuation rules, validation guidance, and contracts.
  The repaired candidate fixes agent `codex`, model `gpt-5.6-terra`, reasoning `medium`, and panel `none`; host and implementation family remain provenance only, while profile severity and request/confirmation caps remain profile-owned. The focused RoboRev mapping contract passes.
- DONE: Reject YAML structural and block forms for every required recovery scalar, while preserving byte-identical package/adopter loaders.
  Focused RED accepted a structural value before the repair; GREEN now rejects `[]`, `{}`, and `|` for each required recovery field. The complete loader test passes and the two loader copies are byte-identical.
- DONE: Emit and consume the mechanical `implementation_exit_observation_declared` build decision instead of inferring RoboRev activation from prose.
  Loader tests prove full Production routes and named recovery risks emit `true`, while recovery `[none]` emits `false`; `continue-dev-flow` consumes that field and the full repository contract passes.
- DONE: Stay within the authorized slice and run all required positive, negative, parity, and hygiene gates.
  The exact feature diff from `caba8e3` is 18 files/635 gross lines with 224 gross loader-test lines. RoboRev and kc-dev-flow contracts pass, five route boundaries reject 10/10 missing-route mutations, four package/adopter pairs are byte-identical, and `git diff --check` is clean; no CI, workflow, schema, UAT, auto-merge, release, or other profile build mechanism was added.
- DONE: Commit the repair and sync only this implementation report without pushing product or changing authority.
  Product tip `2b8abff65a5c50df2ef6ae48a77cb79ddbda6e0e` includes repair commit `2b8abff`; RoboRev job 276 remains the spent-request `UNKNOWN(state_unknown)` and was not retried. Fresh validation still owns without-it, exact-candidate UAT evidence, and the Captain's final UAT decision.

### Summary

The fixed Terra reviewer policy, scalar refusals, and loader-owned observation decision now pass the complete authorized contract and mutation gates within all stop lines. The clean candidate returns to fresh validation with RoboRev UNKNOWN and Captain UAT explicitly unresolved.

## Stage Report: validation (cycle 5)

- DONE: Freshly bind exact candidate 2b8abff65a5c50df2ef6ae48a77cb79ddbda6e0e, feature parent 3f5e71baa85687e61299397975cba31123f18228, and merge target origin/main 2e8595f0a1fa4448bc14a56baedd18214824158e; make no product edits.
  A final fetch bound HEAD and merge-base to those objects with `0 behind / 8 ahead` and a clean product tree; the implementation slice from accepted design commit `caba8e3` is 18 files/625 gross lines (not the dispatch's stale 635 description) with 224 loader-test lines, below the 650/235 stop lines.
- DONE: Verify the approved 18-file and 650/235 stop lines, complete kc-dev-flow contract gate, direct loader test, Terra mapping contract, all package/adopter parity checks, diff-check, ten route mutations, and the real Spacedock recovery journey.
  The repository gate, direct loader/E2E, and RoboRev contract all exited 0; four package/adopter pairs are byte-identical, diff-check is clean, and the committed route helper rejected 10/10 missing-full or missing-recovery mutations, so either missing route clause fails its owner.
- DONE: Prove fixed reviewer selection for both Claude-host and GPT-host inputs: agent codex, model gpt-5.6-terra, reasoning medium, panel none; host family remains provenance only. Prove profile minimum severity and request caps did not change.
  The RoboRev contract passed independently with `CLAUDECODE` and `CODEX_THREAD_ID` host inputs while requiring the same repository mapping; profile controls remain POC high/1/0, Pilot medium/1/1, and Production medium/1/1, and the pre-rework Production diff changes only reasoning from thorough to medium.
- DONE: Prove malformed recovery scalars including [], {}, and | fail closed. Prove implementation_exit_observation_declared is true for the full route and named recovery risks, and false for recovery review_risks: [none].
  The direct candidate loader test rejects all three structural forms for each required recovery scalar and asserts full/named-risk `true` plus recovery `[none]` `false`; accepting any form or flipping any decision makes that test fail.
- DONE: Run the single task-owned without-it in an isolated temporary copy: execute the complete candidate loader test against the exact pre-feature loader and require a feature-specific failure, confirm exact objects and absolute paths, then remove the copy.
  Candidate test object `ff9f432...` with exact `3f5e71b` loader object `c9a4913...` exited 1 at `accepted structural-recovery_failure-91`; the registered copy was then removed and the product worktree remained clean.
- DONE: Record exact-candidate delegated E2E UAT evidence for backlog gate -> ideation empty skip/no artifact -> implementation build -> validation verify, plus default-full compatibility, rollback readiness, Draft PR/provider state, and the carried RoboRev job 276 noncanonical UNKNOWN residual.
  Spacedock 0.27.0 exercised that exact recovery journey and legacy full-route fixtures; rollback is the eventual landing-commit revert plus Captain re-recording active short-route items to full. Draft PR #299 remains at stale head `b6092e6` with old-head green checks and no reviews/comments, while job 276's `e20d13b..b6092e6` range is noncanonical and the official observation remains `UNKNOWN(state_unknown)`, not gate PASS.
- DONE: Return PASS only if every acceptance criterion is supported and the branch remains 0 behind origin/main. Append one validation Stage Report and sync only state. Do not edit product, push the product branch, update the Draft PR, prepare/approve a gate, merge, release, or self-approve Captain UAT.
  Technical verdict is PASS at exact candidate `2b8abff`: AC-1 through AC-5 and every replacement threshold have executable positive and negative evidence with the branch 0 behind; this report changes only state, and Captain UAT/validation approval, exact-head Draft update, Ready, merge, and release remain untouched.

### Summary

Exact candidate `2b8abff` passes the complete deterministic gate, fixed Terra mapping under both host families, fail-closed scalar and observation controls, ten route mutations, the real recovery journey, and one fresh without-it. Technical validation recommends PASS; Captain UAT remains the final validation decision, and Draft PR #299 plus RoboRev job 276 remain explicitly noncanonical to this candidate.
