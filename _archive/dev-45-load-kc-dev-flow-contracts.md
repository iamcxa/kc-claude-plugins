---
title: Load kc-dev-flow contracts from the installed plugin
status: done
source: https://linear.app/duckbase-co/issue/DEV-45/load-kc-dev-flow-contracts-from-the-installed-plugin
product: kc-dev-flow
planning-window: Linear Cycle b788c52d-8370-475f-be4f-8fcd88dd03d6 2026-08-27T16:00:00.000Z/2026-09-10T16:00:00.000Z
planning-outcome: Linear Project e780d04f-cf7d-4ebb-bf9a-90fec8466923 Plugin-owned kc-dev-flow contracts sha256:4106b2e493e8bd75052c1fb3b775eaf434ef8b087a7717611d5d81f2a3a81990
sprint: S7
sprint-readiness: ready
design: required
started: 2026-09-01T16:31:49Z
completed: 2026-09-02T04:54:01Z
verdict: PASSED
worktree: .worktrees/spacedock-ensign-dev-45-load-kc-dev-flow-contracts
issue:
pr: pr-merge:326
mod-block:
id: 3fkmdwdvsfha8ektb2s5jz7d
gates:
    version: 1
    records:
        - id: gate:3fkmdwdvsfha8ektb2s5jz7d:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:3fkmdwdvsfha8ektb2s5jz7d-backlog-1
              briefing:
                id: briefing:3fkmdwdvsfha8ektb2s5jz7d:backlog:attempt-1:revision-1
                digest: sha256:ae267311c31a0901273945546368887a7d6c2cd9bfe84748a06a52dc5dbdf822
                request-digest: sha256:a18c3d220d0cbce5f1048e194bf5745aeecdc945a63c166cc1766b7bc5ddda4b
                room-ref: ./dev-45-load-kc-dev-flow-contracts/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:3fkmdwdvsfha8ektb2s5jz7d:backlog:1
                briefing: briefing:3fkmdwdvsfha8ektb2s5jz7d:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-01T16:29:53.994804Z"
                decision: approve
                reason: Captain approved the bound Production ideation direction.
              application:
                target-stage: ideation
                state: consumed
        - id: gate:3fkmdwdvsfha8ektb2s5jz7d:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:3fkmdwdvsfha8ektb2s5jz7d-ideation-1
              briefing:
                id: briefing:3fkmdwdvsfha8ektb2s5jz7d:ideation:attempt-1:revision-1
                digest: sha256:316d0049499202ef0cee28d3ea037f8ab3ad5847ec235249f2fcfa6168f3b2db
                request-digest: sha256:16b49076565a628748444eb81e392ce0d54bf48c34d4391a608818f2df24586c
                room-ref: ./dev-45-load-kc-dev-flow-contracts/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:3fkmdwdvsfha8ektb2s5jz7d:ideation:1
                briefing: briefing:3fkmdwdvsfha8ektb2s5jz7d:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-09-01T23:14:22.958866Z"
                decision: approve
                reason: Captain approved the resource-anchor manifest and bounded Production implementation.
              application:
                target-stage: implementation
                state: consumed
        - id: gate:3fkmdwdvsfha8ektb2s5jz7d:validation
          stage: validation
          attempts:
            - id: gate-attempt:3fkmdwdvsfha8ektb2s5jz7d-validation-1
              briefing:
                id: briefing:3fkmdwdvsfha8ektb2s5jz7d:validation:attempt-1:revision-1
                digest: sha256:67cfae00b03c4d75ae08dce198a354a43b5dcd1229b850ea81e77601e2e8c09c
                request-digest: sha256:ea77823e1d8648c65a254d91ae769b83feaf60b4e16b331849d7a6c6209e509b
                room-ref: ./dev-45-load-kc-dev-flow-contracts/review/validation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:3fkmdwdvsfha8ektb2s5jz7d:validation:1
                briefing: briefing:3fkmdwdvsfha8ektb2s5jz7d:validation:attempt-1:revision-1
                by: person:captain
                at: "2026-09-02T01:19:52.677671Z"
                decision: approve
                reason: Captain approved exact candidate 61ce308d as locally validated and authorized one Draft PR with Fixes DEV-45.
              application:
                target-stage: done
                state: superseded
            - id: gate-attempt:3fkmdwdvsfha8ektb2s5jz7d-validation-2
              briefing:
                id: briefing:3fkmdwdvsfha8ektb2s5jz7d:validation:attempt-2:revision-1
                digest: sha256:f3deab388349267e8a65308a452315b11fc25588464c29e9ccbd9c5304210466
                request-digest: sha256:63a5fa9ecc1f2596e7e47ab61eb4c14ef7d32d4253308ec6c81c87488e9d0546
                room-ref: ./dev-45-load-kc-dev-flow-contracts/review/validation/briefing-2
              resolution:
                type: Resolution
                id: resolution:spacedock:3fkmdwdvsfha8ektb2s5jz7d:validation:2
                briefing: briefing:3fkmdwdvsfha8ektb2s5jz7d:validation:attempt-2:revision-1
                by: person:captain
                at: "2026-09-02T03:55:05.599987Z"
                decision: approve
                reason: Captain approved exact validated candidate 111d47126df43c15c02d8db4bb0fb4621df25aa1 for native-stack delivery.
              application:
                target-stage: done
                state: consumed
archived: 2026-09-02T04:54:01Z
---

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: production
  recommended: production
  basis: Existing and new adopters keep persistent repository policy and state; removing vendored runtime contracts changes migration, compatibility, and rollback commitments.
  route: [shape, build, verify]
  obligations:
    architecture: [Define host-neutral installed-resource discovery, bind one plugin version and contract digest per stage, distinguish compatible from incompatible stage-boundary upgrades, preserve provider-neutral GitHub and Linear adapters]
    implementation: [Keep README, local mods, and Spacedock state repository-owned, resolve canonical runtime contracts from the installed plugin, remove obsolete vendored files and parity machinery only after replacement behavior is proven]
    testing: [Exercise fresh adoption across supported hosts and profiles, prove active-stage pinning and next-stage upgrade, prove incompatible upgrades stop before dispatch, measure the smaller retained surface, reject every required-mechanism removal]
  scope_boundary: No automatic plugin installation, marketplace release automation, provider writes, executor scheduling, or Hermes and Nightwatch portfolio work.
  decision:
    authority: person:captain
    at: 2026-09-01T16:13:19Z
```

## The problem

Repository adoption currently copies canonical kc-dev-flow kernels, profiles, references, loaders, and guards into each repository. Installation and upgrades therefore duplicate plugin-owned behavior, create merge and parity work, and can leave a repository on mixed contract bytes.

## Accepted outcome

An installed kc-dev-flow plugin is the canonical runtime source. An adopter repository keeps only its local workflow README, local mods, and Spacedock state. Adoption and upgrades inspect and refit those local files without copying canonical contracts. A stage pins the plugin version and contract digest it starts with; a compatible upgrade becomes effective at the next stage boundary, while an incompatible boundary stops before dispatch until local policy is refit.

## Non-goals

- Do not change planning semantics beyond the approved forward-only Linear cutover for new docs/dev admissions.
- Do not mutate active Spacedock state during plugin upgrades.
- Do not bind the design to Conductor, Claude Code, Codex, Hermes, GitHub Projects, or Linear internals.
- Do not retain vendored canonical files merely for offline parity.
- Do not build automatic plugin installation, marketplace release automation, executor scheduling, or the proposed Hermes/Nightwatch portfolio direction.

## Acceptance criteria

- **AC-1** A fresh adopter executes every supported profile and stage from installed plugin resources without repository copies of canonical kernel, profile, reference, loader, or guard files.
- **AC-2** An active stage stays bound to its starting plugin version and contract digest; the next stage uses a compatible installed upgrade.
- **AC-3** An incompatible upgrade fails before next-stage dispatch and identifies the README or local mod refit required.
- **AC-4** Adoption and upgrade preserve repository-owned README policy, local mods, and Spacedock state.
- **AC-5** Migration removes obsolete vendored files and parity machinery without weakening profile routing, close guards, or kernel authority.
- **AC-6** Runtime resolution remains host-neutral and works from Spacedock tracks in repository worktrees.
- **AC-7** Goal-sufficiency and without-it evidence prove every retained mechanism is necessary and the adoption surface is smaller.

## Route-back conditions

The accepted outcome, non-goals, Linear Project, or Cycle changes; runtime discovery cannot bind a plugin version and digest at a stage boundary; or the minimum retained repository surface cannot preserve local policy without weakening kernel authority.

## Admission snapshot

Linear `DEV-45` was read live on 2026-09-02. Its Goal and complete five-item Non-goals match the existing `## Accepted outcome` and `## Non-goals` sections above exactly, so those sections are the admission snapshot and there is no planning delta or second goal authority.

## Ideation decision

Use a **resource-anchor manifest** — a manifest beside the activated skill. The activated `adopt-dev-flow` or `continue-dev-flow` skill supplies its sibling installed loader for that invocation; the loader resolves its own package root, validates one package manifest, and emits only the selected route. No installation path is stored in the adopter.

| Host-neutral design | Decision | Decisive tradeoff |
|---|---|---|
| Skill-relative loader plus installed manifest | Select | Reuses the host's existing skill activation, needs no host-name branch or global install, and keeps canonical bytes in the plugin. |
| Skill embeds the canonical bundle in every dispatch | Reject | Host-neutral, but persists duplicate contract bytes in briefing/state and makes restart provenance larger. |
| Stable executable on `PATH` | Reject | Host-neutral at call time, but creates an installation and global-name surface excluded by this item. |

`kc-dev-flow/contract-manifest.json` declares the contract interface, local-profile interface, and exact plugin-owned runtime resources. `profile-contract-loader.py` reads plugin version from package metadata and hashes the manifest plus declared bytes; it never searches Claude, Codex, Hermes, Conductor, or cache directories.

### Accepted journey and observable semantics

`OBSERVED` means exercised now; `DESIGNED` means awaiting implementation.

1. **OBSERVED:** the packaged loader selected Production `shape` from the exact committed item and emitted kernel/base/stage hashes; its focused behavior suite passed. The present repository-vendored path is therefore working, not a missing capability.
2. **DESIGNED:** an activated installed skill passes its sibling loader path; a fresh adopter containing only its workflow README, declared local mods/adapters, and Spacedock state loads every profile-stage combination from plugin resources.
3. **DESIGNED:** before dispatch, the First Officer records one **stage pin** — version and digest fixed for one attempt — containing stage/attempt identity, plugin version, contract digest, work-item hash, and local-profile interface. It re-reads the committed pin, then dispatches the emitted contract.
4. **DESIGNED:** re-entry to the same active stage accepts only the exact version and digest. Missing bytes, changed bytes under the same version, timeout, or another installed version returns `ACTIVE_STAGE_PIN_MISMATCH`, exit 2, empty stdout, and no state mutation.
5. **DESIGNED:** at the next stage boundary, the current installed plugin may supply a new digest when its declared local-profile interface is compatible. An incompatible interface returns `LOCAL_PROFILE_REFIT_REQUIRED` before pin write or dispatch and names `docs/dev/README.md` fields and any declared local-mod path requiring review.
6. **DESIGNED:** adoption removes only byte-identical canonical copies after the installed route passes. README policy, provider adapters, local `pr-merge`, and the Spacedock state tree remain repository-owned; no vendored fallback is consulted.

The observable changes are the loader CLI (installed/self-locating, no `--contracts-root`), the JSON contract envelope and stage-pin schemas, the Local Profile machine binding, and the repository file set. Planning, profile, gate, merge, and release authority do not change.

### Lifecycle, preservation, and recovery

- Plugin package owns the manifest, canonical contracts, loader, comparator, POC close guard, and their integrity tests. The repository owns README policy, local mods, Linear/GitHub adapters, and Spacedock state; the First Officer owns pin recording; the Captain retains incompatible-refit and release decisions.
- A compatible plugin upgrade is read-only during an active stage. The old pin remains authoritative; the next stage creates a new pin only after interface validation. An unavailable pinned install stops and asks for that exact version; it never falls back to repository copies.
- Initial migration is an explicit incompatible refit from the vendored interface. Rollback before a new-stage pin restores the old plugin and the atomic README/canonical-file deletion commit. After a new stage is pinned, downgrade waits for the following boundary; no mid-stage rewrite is allowed.
- Retained-document Rules 4, 5, and 8 apply. For every deleted canonical section, the package path is its exact byte-identical second home; README, package rationale, and migration guidance are repaired in place. Historical state is not rewritten.
- Preservation proof snapshots the Local Profile block, `docs/dev/_mods/pr-merge.md` bytes/mode, and state HEAD/tree/status. Only named installed-binding rows may change; all other README policy lines and all local-mod bytes must compare equal, and an upgrade invocation must leave state HEAD/tree/status equal.
- Security and privacy remain unchanged: installed-resource resolution reads package files only, while the repository Linear adapter remains the only credential-bearing boundary.

```yaml
project_context:
  impact: update
  authority: root PRODUCT.md, ARCHITECTURE.md, and CLAUDE.md
  claim_locator: ARCHITECTURE.md:17 kc-dev-flow profile-native loading
  surface: loader ownership, stage resource resolution, and conditional-reference activation
  stale_claim: a deterministic repository-local loader and vendored references supply the active policy
  approved_change: the installed plugin manifest and loader supply canonical policy while the repository retains Local Profile policy, local mods, adapters, and state
  landed_change: pending
  planned_check: python3 scripts/kc-dev-flow-contract-test.py must exercise a no-vendor fresh adopter and reject the prior repository-local-loader architecture claim
  validation_evidence: pending
```

### Reverse recovery

```yaml
reverse_recovery:
  trigger: replace working vendored runtime loading and remove canonical repository copies
  boundary: current kc-dev-flow package, self-adopter README/mods/adapters, and active Spacedock route; excludes history, external adopter trees, host caches, installation, and provider writes
  layers:
    - surface: activated-skill resource anchor
      location: kc-dev-flow/skills/continue-dev-flow/SKILL.md:132
      completeness: STUB
      need: REQUIRED
      evidence: package-relative resources exist, but current continuation expressly refuses installed fallback
      disproof_hook: install the package under an arbitrary temporary root with host environment variables absent and run every route
    - surface: canonical profile loader and package contracts
      location: kc-dev-flow/scripts/profile-contract-loader.py:395
      completeness: WORKING
      need: REQUIRED
      evidence: direct Production shape load succeeded and profile-contract-loader.test.py passed
      disproof_hook: mutate any manifest-declared resource and require the bundle digest or loader result to change
    - surface: repository canonical copies and parity checks
      location: docs/dev/_mods and scripts/kc-dev-flow-contract-test.py:449
      completeness: WORKING
      need: REQUIRED
      evidence: static path search found current consumers; byte inventory found 20 copied references plus loader, close guard, and comparator
      disproof_hook: remove the installed-resource handoff and require the no-vendor fresh-adopter journey to fail before classifying these as removal candidates
    - surface: README policy, local pr-merge, provider adapter, and state
      location: docs/dev/README.md:47; docs/dev/_mods/pr-merge.md:1; scripts/kc-dev-flow/linear-admission.py:239; docs/dev/.spacedock-state
      completeness: WORKING
      need: REQUIRED
      evidence: static consumer search plus byte/dynamic route inspection found all four on the accepted journey
      disproof_hook: mutate each protected surface in a migration fixture and require preservation or compatibility proof to fail
  decision: recover
```

The recovery keeps the proven loader, route tables, close guard, comparator, and conditional-reference rules, but moves root resolution and canonical ownership back to their installed package. Two searches bounded removal: static consumer/path search, and byte inventory plus direct loader/focused-test execution. External adopters remain unknown, so the interface bump fails closed and requires their explicit refit.

### Where it touches

Counts are verified in the current tree; `after` values are estimates. Delivery-base stop counts use refreshed `origin/main`, currently `3aafd3d22e749257f3551079475cc41183525d7c`; implementation must create Linear's exact branch `feature/dev-45-load-kc-dev-flow-contracts-from-the-installed-plugin` from the then-current trunk.

| Path or exact set | Lines now | Lines after |
|---|---:|---:|
| `kc-dev-flow/contract-manifest.json` | 0 | ~45 |
| `kc-dev-flow/scripts/profile-contract-loader.py` and `.test.py` | 2,220 | ~2,500 |
| `kc-dev-flow/skills/{adopt-dev-flow,continue-dev-flow}/SKILL.md` | 476 | ~440 |
| `kc-dev-flow/{README.md,RATIONALE.md,MIGRATION.md}` and the retained/project-context/RoboRev references | 1,134 | ~1,150 |
| `scripts/kc-dev-flow/linear-admission.py` | 456 | ~460 |
| contract, ablation, and multi-profile release tests under `scripts/` | 3,192 | ~3,150 |
| `ARCHITECTURE.md` | 259 | ~260 |
| `docs/dev/README.md` | 437 | ~410 |
| 20 canonical `docs/dev/_mods` references, copied loader/guard, and copied comparator | 2,645 | 0 |
| local `docs/dev/_mods/pr-merge.md` | 519 | 519, byte-identical |
| `docs/dev/.spacedock-state` outside normal task/pin receipts | unchanged | unchanged |

Expected scope is about 40 files and 4,250 diff lines, including 2,645 lines of exact-copy deletion. Stop and return to shape above 44 changed files, above 4,800 changed lines, or at the first host-specific discovery adapter or Spacedock-core edit; cross-host discovery is the named runaway area. `multi_slice_required` is false: loader/manifest, caller wiring, and self-adopter deletion cannot independently deliver a safe mixed state, but should be three reviewable commits in that order.

### Falsifiable acceptance and without-it checks

- **AC-1/AC-6:** a temporary adopter with README, one local mod, one provider adapter, and state—but no canonical files—runs all POC, Pilot, and Production stages from three arbitrary install roots with Claude/Codex/Hermes variables absent. Moving the package or worktree must not change resolution.
- **AC-2:** pin version/digest A, replace the installed root with compatible B, and prove same-stage re-entry refuses A/B while next-stage entry accepts B and records digest B.
- **AC-3:** change only the installed local-profile interface; next-stage load must exit 2 with no stdout, name the README or local-mod refit, and leave the state tree unchanged. A mutation that deletes this check must make the test red.
- **AC-4:** migration fixtures carry sentinel README policy, a local-mod byte hash/mode, and a state commit/tree. Adoption and compatible upgrade must preserve all sentinels; mutations that overwrite each protected surface must be detected.
- **AC-5:** existing route, conditional-reference, POC close, planning reconciliation, and kernel-authority tests pass through the installed package before the 23 copied files are removed; reintroducing any canonical adopter copy fails the reduced-surface assertion.
- **AC-7 goal sufficiency:** one fresh-adopter journey loads, advances, upgrades at a boundary, refuses an incompatible boundary, and completes with exact revision evidence. The focused current loader suite is green; the broad repository contract currently fails only because this shared worktree contains an empty retired `setup-github-project-projection` directory, so validation must rerun it in the fresh implementation worktree.
- **AC-7 minimal necessity:** remove, one at a time, the skill anchor, manifest inventory, digest, active-stage equality check, compatibility check, preservation check, and remaining local binding; each removal must break its named journey check. Any retained mechanism whose removal breaks none is deleted.

Explicit exclusions are automatic plugin installation, a PATH launcher, host cache discovery, embedded contract copies, provider writes, executor scheduling, Spacedock-core changes, marketplace/release automation, planning-model changes, offline parity fallback, and Hermes/Nightwatch portfolio work.

## Stage Report: ideation

- DONE: Copy the Linear accepted outcome and non-goals into the admission snapshot, then compare at least two host-neutral installed-resource designs and select one.
  Live `DEV-45` matched the existing snapshot exactly; three designs were compared and the skill-relative installed manifest was selected.
- DONE: Specify falsifiable stage pinning, compatible next-stage upgrade, incompatible-upgrade refusal, and preservation proof for README policy, local mods, and Spacedock state.
  The stage-pin schema, exact refusal outputs, interface boundary, preservation sentinels, mutations, and rollback are specified above.
- DONE: Use goal-sufficiency, reverse recovery, and without-it reasoning to bound the smallest file and line scope, hard stop numbers, rollback, and explicit exclusions before implementation.
  The receipt recovers the working loader, bounds one integrated slice to about 40 files/4,250 diff lines, and stops above 44 files, 4,800 lines, or any host-specific resolver/Spacedock-core edit.
- DONE: Classify the bound project-context impact.
  `ARCHITECTURE.md:17` requires an in-slice update from repository-local loading and vendoring to installed manifest loading and stage pinning; validation evidence remains pending for the fresh validator.

### Summary

Ideation selects a self-locating installed-resource manifest with a durable per-stage version/digest pin and a fail-closed local-profile compatibility boundary. The design removes 2,645 lines of canonical repository copies only after installed-route, preservation, upgrade, and without-it proofs pass; implementation remains one atomic delivery slice with no host adapter or Spacedock-core expansion.

## Implementation evidence

```yaml
review_convergence_claim:
  schema: kc-dev-flow-roborev-claim/v1
  identity: 7141d793868da4f0f12f69a24997e546f37f733e428d96dfeb6ef1100ff35e60
  claimant: spacedock-ensign-3fkmdwdvsf-implementation
  state_revision: ae448413ed83897e158413f2640fc73946830c75
  state: claimed
  candidate: 2c5149dc33fdbe6cf4aeaf75c7c683a4681ab404
```

```yaml
review_convergence_observation:
  schema: kc-dev-flow-roborev-observation/v1
  candidate: 2c5149dc33fdbe6cf4aeaf75c7c683a4681ab404
  base: 3aafd3d22e749257f3551079475cc41183525d7c
  capability: review_convergence
  mode: observe
  profile: production
  provider: roborev
  outcome: UNKNOWN
  reason: stale
  identity: 7141d793868da4f0f12f69a24997e546f37f733e428d96dfeb6ef1100ff35e60
  config_sha256: ae3555f0b3fcf5b626c39c614e3b2058bd2e31fb5840ce864edfaeded34f07f1
  job_id: 292
  job_uuid: 15ae54d7-0137-4a69-8ddc-f9ba6ebc48a7
  provider_verdict: SEVERITY_THRESHOLD_MET
  missing_identity_fields: [panel_identity, stable_member_population]
  request_count: 1
  confirmation_count: 0
  cost:
    job_usd: 0.0372104
    aggregate_usd: 1.9240536
    jobs_with_cost: 7
    jobs_total: 10
    complete: false
```

## Stage Report: implementation

- DONE: Before product edits, base the implementation worktree on current origin/main and use Linear's exact branch feature/dev-45-load-kc-dev-flow-contracts-from-the-installed-plugin.
  The clean worktree rebased to `origin/main@3aafd3d22e749257f3551079475cc41183525d7c` and remained on the exact branch through candidate `2c5149dc33fdbe6cf4aeaf75c7c683a4681ab404`.
- SKIPPED: The delivery PR must contain Fixes DEV-45.
  Implementation created no PR; validation/delivery must append `Fixes DEV-45` before authorized Draft creation.
- DONE: Implement the selected installed manifest and self-locating loader.
  Commit `a91da87379c77ab4d4b7837f2dec664d5eb20136` validates one package manifest, hashes every declared byte, and resolves only its own installed package root.
- DONE: Implement the per-stage version/digest pin, compatible next-stage upgrade, and fail-closed incompatible-refit boundary.
  Commit `12ded46ac9ef31169932fcd6e545596dcef8af0a` binds attempt/version/digest/work-item/interface; the focused suite fails same-stage drift and requires explicit accepted refit before an incompatible boundary opens.
- DONE: Preserve README policy, local mods, provider adapters, and Spacedock state.
  Sentinel README bytes, local-mod bytes/mode, and unrelated state survive adoption/upgrade; Linear remains the repository adapter and `docs/dev/_mods/pr-merge.md` remains byte-identical.
- DONE: Delete vendored canonical copies and parity machinery only after fresh-adopter, all-profile/stage, preservation, migration, and without-it proofs pass.
  Commit `2c5149dc33fdbe6cf4aeaf75c7c683a4681ab404` removes 22 canonical copies after the loader, repository contract, and 57-mutant ablation suite pass; reintroducing a copy now fails the repository contract.
- DONE: Stop above 44 changed files, 4,800 diff lines, or any host-specific resolver or Spacedock-core edit.
  Final scope is 37 files and 3,868 changed lines (`+1000/-2868`), with no host-specific discovery adapter or Spacedock-core edit.
- DONE: Record exact counts plus RoboRev observation.
  RoboRev job `292` returned `SEVERITY_THRESHOLD_MET`; strict JSON correlation records `UNKNOWN(reason: stale)` because panel identity and complete member population are absent, with one request, zero confirmations, and incomplete cost coverage.
- DONE: Exercise the required implementation proof.
  `profile-contract-loader.test.py` fails on install-root, digest, active-pin, refit, or preservation regressions; `kc-dev-flow-contract-test.py` fails on route/package/adopter drift; `kc-dev-flow-minimal-stack-ablation.test.py` rejects every named mechanism removal.
- DONE: Run the relevant repository exit gates.
  Version parity, marketplace schema/installability, skill frontmatter, multi-profile static budget, package/repository contract, and minimal-stack ablation all pass; no CI workflow changed, so per-PR CI cost is unchanged and was not remeasured.

### Summary

The candidate now loads canonical KC Dev Flow contracts from one installed, self-locating manifest and pins exact version/digest bytes per active attempt. Compatible upgrades begin only at stage boundaries, incompatible interfaces stop for explicit refit, and the self-adopter retains only local policy, adapters, mods, and state.

## Stage Report: implementation (cycle 2)

- DONE: Cite fresh-adopter installed-resource execution.
  AC-1 evidence: candidate `2c5149dc33fdbe6cf4aeaf75c7c683a4681ab404` (manifest commit `a91da87379c77ab4d4b7837f2dec664d5eb20136`, binding commit `12ded46ac9ef31169932fcd6e545596dcef8af0a`, deletion commit `2c5149dc33fdbe6cf4aeaf75c7c683a4681ab404`) passed `python3 kc-dev-flow/scripts/profile-contract-loader.test.py` and `python3 scripts/kc-dev-flow-contract-test.py`; either check fails if any supported profile-stage cannot load from an arbitrary installed root, needs a repository canonical copy, or a canonical copy is reintroduced.
- DONE: Cite active-stage pinning and compatible boundary upgrade.
  AC-2 evidence: commit `12ded46ac9ef31169932fcd6e545596dcef8af0a` in candidate `2c5149dc33fdbe6cf4aeaf75c7c683a4681ab404` passed `python3 kc-dev-flow/scripts/profile-contract-loader.test.py`; the check fails if a same-stage A pin accepts version/digest B or if the next compatible stage does not write digest B.
- DONE: Cite incompatible-upgrade refusal.
  AC-3 evidence: commit `12ded46ac9ef31169932fcd6e545596dcef8af0a` in candidate `2c5149dc33fdbe6cf4aeaf75c7c683a4681ab404` passed `python3 kc-dev-flow/scripts/profile-contract-loader.test.py` and `python3 scripts/kc-dev-flow-minimal-stack-ablation.test.py`; the checks fail if an incompatible interface emits dispatch stdout, writes a pin, omits the README/local-mod refit target, or a mutation deleting the compatibility guard survives.
- DONE: Cite preservation of repository-owned surfaces.
  AC-4 evidence: candidate `2c5149dc33fdbe6cf4aeaf75c7c683a4681ab404` passed `python3 kc-dev-flow/scripts/profile-contract-loader.test.py`; the check fails if adoption or upgrade changes sentinel README policy, local-mod bytes or mode, or unrelated Spacedock state commit/tree/status.
- DONE: Cite safe vendored-copy and parity removal.
  AC-5 evidence: deletion commit `2c5149dc33fdbe6cf4aeaf75c7c683a4681ab404` passed `python3 scripts/kc-dev-flow-contract-test.py` and `python3 scripts/kc-dev-flow-minimal-stack-ablation.test.py`; the checks fail if an obsolete canonical adopter copy returns or if a route, conditional-reference, POC close-guard, or kernel-authority mutation survives.
- DONE: Cite host-neutral resolution from worktrees.
  AC-6 evidence: self-locating commit `a91da87379c77ab4d4b7837f2dec664d5eb20136` in candidate `2c5149dc33fdbe6cf4aeaf75c7c683a4681ab404` passed `python3 kc-dev-flow/scripts/profile-contract-loader.test.py` from the exact implementation worktree; the check fails if three arbitrary install roots require Claude, Codex, Hermes, or Conductor environment discovery, or if moving the package/worktree changes resolution.
- DONE: Cite goal-sufficiency, necessity, and reduced surface.
  AC-7 evidence: candidate `2c5149dc33fdbe6cf4aeaf75c7c683a4681ab404` passed `python3 scripts/kc-dev-flow-minimal-stack-ablation.test.py` with all 57 named mutants rejected, while `git diff --shortstat 3aafd3d22e749257f3551079475cc41183525d7c..2c5149dc33fdbe6cf4aeaf75c7c683a4681ab404` reports 37 files and 3,868 changed lines; evidence fails if any named mechanism-removal mutant survives or scope exceeds 44 files/4,800 lines.
- DONE: Inspect RoboRev job 292's stored finding output and record the non-action disposition.
  `roborev show --job 292 --json` stores exact output `SEVERITY_THRESHOLD_MET` with `min_severity: medium`, so it exposes no Medium, High, or Critical finding to repair; no product commit or changed-tip confirmation was made. The strict observation remains `UNKNOWN(reason: stale)` because panel identity and stable member population are still absent; this provider result is observation only, not validation authority.
- SKIPPED: Create or link the delivery PR.
  No PR exists for this branch. Delivery must create the authorized PR and include exactly one `Fixes DEV-45` linkage before completion.

### Summary

Candidate `2c5149dc33fdbe6cf4aeaf75c7c683a4681ab404` now has one durable implementation citation for every AC-1 through AC-7, each tied to the exact commit/check and its falsifying regression. These are implementation proofs for the next gate; they do not claim validation authority.

## Stage Report: validation

- DONE: Independently verify exact candidate 2c5149dc33fdbe6cf4aeaf75c7c683a4681ab404 on the Linear branch against current origin/main: rerun the fresh-adopter installed-root matrix, all supported profile-stage routes, relevant repository gates, and confirm no canonical adopter copy remains.
  Exact branch `feature/dev-45-load-kc-dev-flow-contracts-from-the-installed-plugin` stayed at `2c5149dc33fdbe6cf4aeaf75c7c683a4681ab404` over `origin/main@3aafd3d22e749257f3551079475cc41183525d7c`; the installed-loader suite fails if any of eight routes across three arbitrary roots needs host discovery, the live three-profile gate fails on route or terminal drift, repository gates passed, and `docs/dev/_mods/pr-merge.md` is the only retained mod file.
- DONE: Adversarially falsify active-stage pinning, compatible next-stage upgrade, incompatible-refit refusal, repository-owned surface preservation, and every retained-mechanism without-it claim; map concrete evidence or failure to AC-1 through AC-7 and re-anchor the mechanism set to the smaller adoption surface.
  AC-1/AC-6 passed the arbitrary-root all-route matrix; AC-2 rejected same-stage A/B drift and accepted compatible B only at the next boundary; AC-3 exited 2 with empty stdout, named README/local-mod refit, and preserved the pin; AC-4 preserved README, mod bytes/mode, and unrelated state; AC-5 passed route, close-guard, kernel, and no-copy checks; AC-7 rejected all 57 named mutants and confirmed 37 files/3,868 changed lines.
- FAILED: Verify architecture, migration, rollback or forward-recovery, exact stop counts, and delivery readiness; observe live provider feedback only if a PR exists, and do not create or merge a PR without Captain authorization.
  Migration and boundary rollback are documented and 37 files/3,868 lines stay below the 44/4,800 stops, but `ARCHITECTURE.md:48` and `:55` both declare Mermaid node `M`, conflating the installed package manifest with the `pr-merge` runtime mod; implementation owns renaming one node and exact-revision revalidation. No PR exists, so provider feedback was not queried; release authorization, operational owner, and monitoring handoff are not yet recorded, and delivery is not ready.

### Summary

Exact candidate behavior passes the fresh-adopter, lifecycle, preservation, repository-gate, and 57-mutant necessity evidence. Validation returns to implementation because the changed architecture diagram merges two distinct authorities under one Mermaid node ID; after that correction, validation must rerun at the new exact revision before any Captain-authorized Draft PR.

## Implementation evidence (cycle 3)

```yaml
review_convergence_claim:
  schema: kc-dev-flow-roborev-claim/v1
  identity: aeae44bc0a2eca0a277c745ecdaed8e8374d9a592f0a182686f907dba32e3699
  claimant: spacedock-ensign-3fkmdwdvsf-implementation
  state_revision: 1e657ec8b9f36c2b153b4e70d6b57d1fb4ea3d9f
  state: claimed
  candidate: 61ce308dfeaae40f05b997092eb3a3a359a61ff6
  confirmation_of_candidate: 2c5149dc33fdbe6cf4aeaf75c7c683a4681ab404
```

```yaml
review_convergence_observation:
  schema: kc-dev-flow-roborev-observation/v1
  candidate: 61ce308dfeaae40f05b997092eb3a3a359a61ff6
  expected_base: 3aafd3d22e749257f3551079475cc41183525d7c
  observed_base: 9d4e499ac5ac66d668131d378be41d487f89d446
  capability: review_convergence
  mode: observe
  profile: production
  provider: roborev
  outcome: UNKNOWN
  reason: state_unknown
  identity: aeae44bc0a2eca0a277c745ecdaed8e8374d9a592f0a182686f907dba32e3699
  config_sha256: ae3555f0b3fcf5b626c39c614e3b2058bd2e31fb5840ce864edfaeded34f07f1
  job_id: 293
  job_uuid: 25c6f5b8-2754-4c50-98d6-3cf2061a1e4a
  provider_verdict: FAIL
  launch_correlation: mismatched_range
  missing_identity_fields: [panel_identity, stable_member_population]
  request_count: 1
  confirmation_count: 1
  diagnostic_disposition: carry KC_DEV_FLOW_LOADER binding finding to fresh validation; no retry or implementation expansion
  cost:
    job_usd: 0.0548216
    aggregate_usd: 1.9788752
    jobs_with_cost: 8
    jobs_total: 11
    complete: false
```

## Stage Report: implementation (cycle 3)

- DONE: Fix only the duplicate Mermaid node ID in ARCHITECTURE.md so the installed manifest and repository-owned pr-merge mod remain distinct nodes with correct edges.
  Commit `61ce308dfeaae40f05b997092eb3a3a359a61ff6` changes only the delivery-mod declaration from node `M` to `RM`; the installed manifest remains `M -> L` and delivery remains `D -.-> RM`, so reverting that line recreates the duplicate-ID conflation.
- DONE: Commit the bounded correction on the exact Linear branch, rerun the earned architecture and repository checks.
  Exact branch `feature/dev-45-load-kc-dev-flow-contracts-from-the-installed-plugin` is clean at `61ce308dfeaae40f05b997092eb3a3a359a61ff6`; the focused `awk` duplicate-node/exact-edge check, `python3 scripts/kc-dev-flow-contract-test.py`, `python3 scripts/kc-dev-flow-multi-profile-gate.py --json`, and `git diff --check 3aafd3d22e749257f3551079475cc41183525d7c..61ce308dfeaae40f05b997092eb3a3a359a61ff6` pass and fail on duplicate/incorrect graph edges, KC Dev Flow contract drift, route/budget drift, or whitespace errors respectively.
- DONE: Report the new exact candidate and diff counts, and preserve every unaffected implementation claim.
  Candidate `61ce308dfeaae40f05b997092eb3a3a359a61ff6` over `3aafd3d22e749257f3551079475cc41183525d7c` is 37 files and 3,870 changed lines (`+1001/-2869`), below the 44-file/4,800-line stops; commit `61ce308dfeaae40f05b997092eb3a3a359a61ff6` is exactly one diagram-line replacement, so no non-diagram candidate byte changed.
- DONE: Preserve durable evidence for every acceptance criterion on the corrected candidate.
  AC-1 evidence: candidate `61ce308dfeaae40f05b997092eb3a3a359a61ff6` retains commits `a91da87379c77ab4d4b7837f2dec664d5eb20136`, `12ded46ac9ef31169932fcd6e545596dcef8af0a`, and `2c5149dc33fdbe6cf4aeaf75c7c683a4681ab404`; `python3 scripts/kc-dev-flow-contract-test.py` fails if any supported profile-stage needs a repository canonical copy or a copy is reintroduced.
  AC-2 evidence: pinning commit `12ded46ac9ef31169932fcd6e545596dcef8af0a` remains in candidate `61ce308dfeaae40f05b997092eb3a3a359a61ff6`; the previously earned `python3 kc-dev-flow/scripts/profile-contract-loader.test.py` fails if a same-stage A pin accepts version/digest B or the next compatible stage does not write digest B.
  AC-3 evidence: compatibility commit `12ded46ac9ef31169932fcd6e545596dcef8af0a` remains in candidate `61ce308dfeaae40f05b997092eb3a3a359a61ff6`; `python3 kc-dev-flow/scripts/profile-contract-loader.test.py` and `python3 scripts/kc-dev-flow-minimal-stack-ablation.test.py` fail if an incompatible interface dispatches, writes a pin, omits the refit target, or a compatibility-guard removal survives.
  AC-4 evidence: candidate `61ce308dfeaae40f05b997092eb3a3a359a61ff6` changes only `ARCHITECTURE.md` after validated candidate `2c5149dc33fdbe6cf4aeaf75c7c683a4681ab404`; `python3 kc-dev-flow/scripts/profile-contract-loader.test.py` fails if README policy, local-mod bytes/mode, or unrelated state commit/tree/status changes.
  AC-5 evidence: deletion commit `2c5149dc33fdbe6cf4aeaf75c7c683a4681ab404` plus diagram repair `61ce308dfeaae40f05b997092eb3a3a359a61ff6` passed `python3 scripts/kc-dev-flow-contract-test.py` and the focused `awk` duplicate-node/exact-edge check; they fail if a canonical copy returns, a route/guard/kernel mutation survives, or installed manifest node `M` and repository mod node `RM` conflate.
  AC-6 evidence: self-locating commit `a91da87379c77ab4d4b7837f2dec664d5eb20136` remains in candidate `61ce308dfeaae40f05b997092eb3a3a359a61ff6`; `python3 kc-dev-flow/scripts/profile-contract-loader.test.py` fails if three install roots require host-specific discovery or moving the package/worktree changes resolution.
  AC-7 evidence: candidate `61ce308dfeaae40f05b997092eb3a3a359a61ff6` retains the 57-mutant `python3 scripts/kc-dev-flow-minimal-stack-ablation.test.py` result and `git diff --shortstat 3aafd3d22e749257f3551079475cc41183525d7c..61ce308dfeaae40f05b997092eb3a3a359a61ff6` reports 37 files/3,870 lines; evidence fails if a named mechanism-removal mutant survives or scope exceeds 44 files/4,800 lines.
- DONE: Record the one allowed changed-tip RoboRev observation and its strict disposition.
  The one allowed confirmation produced job `293` for `9d4e499ac5ac66d668131d378be41d487f89d446..61ce308dfeaae40f05b997092eb3a3a359a61ff6`, not required `3aafd3d22e749257f3551079475cc41183525d7c..61ce308dfeaae40f05b997092eb3a3a359a61ff6`; strict launch correlation remains non-authoritative `UNKNOWN(reason: state_unknown)`, no retry is allowed, and its loader-binding diagnostic remains carried to fresh validation.
- SKIPPED: Create or link the delivery PR.
  No PR exists for this branch. Delivery must create the authorized PR and include exactly one `Fixes DEV-45` linkage after fresh validation of `61ce308dfeaae40f05b997092eb3a3a359a61ff6`.

### Summary

The duplicate Mermaid node is repaired in one diagram-only commit, with plugin manifest and repository delivery-mod authority now distinct and all earned checks green at exact candidate `61ce308dfeaae40f05b997092eb3a3a359a61ff6`. The single changed-tip observation could not correlate its range and remains non-authoritative; fresh validation owns the corrected candidate and the carried diagnostic before any Draft PR.

## Stage Report: validation (cycle 2)

- DONE: Reverify candidate 61ce308dfeaae40f05b997092eb3a3a359a61ff6 against required base 3aafd3d22e749257f3551079475cc41183525d7c, prove the duplicate Mermaid node is closed with correct distinct edges, and confirm the correction changed no other candidate byte.
  `61ce308dfeaae40f05b997092eb3a3a359a61ff6` has parent `2c5149dc33fdbe6cf4aeaf75c7c683a4681ab404`; their diff is exactly one `ARCHITECTURE.md` line (`+1/-1`), with manifest `M -> L`, delivery `D -.-> RM`, and the focused duplicate-node/exact-edge probe passing.
- DONE: Independently adjudicate whether KC_DEV_FLOW_LOADER has a concrete host-neutral resolution/export before every documented README and Linear command; reproduce the accepted journey or reject with exact evidence and a bounded assignment.
  The carried diagnostic is rejected: `continue-dev-flow` resolves exact sibling `../../scripts/profile-contract-loader.py`, `docs/dev/README.md:168-170` binds that resolved path as invocation-local `KC_DEV_FLOW_LOADER`, skill-relative `realpath` plus the README loader command passed without host discovery, and the contract suite passed Linear admission with `--profile-loader` deriving the sibling comparator; no global export is promised or required.
- DONE: Rerun the earned exact-candidate AC-1 through AC-7, stop-count, migration, rollback, and delivery-readiness checks; record one final PASSED or REJECTED verdict and do not create or merge a PR.
  Final verdict: PASSED for local exact-candidate validation. Loader, repository-contract, live three-profile, 57-mutant ablation, release metadata/parity, frontmatter, plugin-release, state-prerequisite, comparator, close-guard, route, and RoboRev-contract checks passed; migration and boundary rollback remain explicit, 37 files/3,870 lines stay below 44/4,800, and no canonical adopter copy remains. No PR exists, so provider feedback was not queried; the candidate is ready only for Captain-authorized Draft creation with exactly one `Fixes DEV-45`, not merge or release.
  AC-1 evidence: exact candidate `61ce308dfeaae40f05b997092eb3a3a359a61ff6` passed `profile-contract-loader.test.py` and `kc-dev-flow-contract-test.py`; they fail if any supported profile-stage cannot load from arbitrary installed roots, needs an adopter canonical copy, or such a copy returns.
  AC-2 evidence: exact candidate `61ce308dfeaae40f05b997092eb3a3a359a61ff6` passed `profile-contract-loader.test.py`; it fails if same-stage version/digest drift is accepted or a compatible upgrade cannot bind only at the next stage boundary.
  AC-3 evidence: exact candidate `61ce308dfeaae40f05b997092eb3a3a359a61ff6` passed `profile-contract-loader.test.py` and `kc-dev-flow-minimal-stack-ablation.test.py`; they fail if an incompatible interface emits dispatch output, mutates the pin, omits the README/local-mod refit target, or the compatibility guard is removed.
  AC-4 evidence: exact candidate `61ce308dfeaae40f05b997092eb3a3a359a61ff6` passed `profile-contract-loader.test.py`; it fails if adoption or upgrade changes README policy, local-mod bytes or mode, or unrelated Spacedock state.
  AC-5 evidence: exact candidate `61ce308dfeaae40f05b997092eb3a3a359a61ff6` passed `kc-dev-flow-contract-test.py`, the live route gate, and the 57-mutant ablation; they fail if a canonical copy returns or route, close-guard, conditional-reference, or kernel authority weakens.
  AC-6 evidence: exact candidate `61ce308dfeaae40f05b997092eb3a3a359a61ff6` passed the three-arbitrary-root loader matrix plus the invocation-local `KC_DEV_FLOW_LOADER` handoff; they fail if resolution needs host discovery or moving the package or worktree changes the selected contracts.
  AC-7 evidence: exact candidate `61ce308dfeaae40f05b997092eb3a3a359a61ff6` rejected all 57 named without-it mutants, retains only `docs/dev/_mods/pr-merge.md`, and measures 37 files/3,870 changed lines below the 44-file/4,800-line stops.

Native stack exception: REJECTED — PR #323 already separates dependent green layers: `a91da873` adds the manifest/loader, `12ded46a` refits callers while old copies remain inert, and `2c5149dc` removes those copies; the first two boundaries pass focused loader/contract checks and the final deletion is verified at `61ce308d`, so local `pr-merge` requires bottom-to-top Draft PRs.

### Summary

The one-line Mermaid repair is exact, closes the prior architecture failure, and leaves all AC-1 through AC-7 evidence green at corrected candidate `61ce308dfeaae40f05b997092eb3a3a359a61ff6`. The wrong-range RoboRev loader-path diagnostic does not reproduce when the activated skill's required invocation-local binding is honored; local validation passes, while PR creation and release authority remain pending with the Captain.

PR feedback: {"dispositions":[],"fingerprint":"sha256:11374cc6b7bfd28902fd621a1603f5669788aaab44d804bc6364a83597a5b18f","head":"61ce308dfeaae40f05b997092eb3a3a359a61ff6","layer":"single","pr_number":323,"repository":"iamcxa/kc-claude-plugins","scheme":"github-pr-feedback/v1"}

## Stage Report: validation (cycle 5)

- DONE: Re-read exact heads, bodies, bases, stack identity/order, and required checks for corrected GitHub-native stack #328.
  Active order is bottom Draft PR #324 `main..399a010cfd8a3d1c2688798472b927f4c9a74f9d` then top Draft PR #326 `feature/dev-45-add-installed-contract-loader..314045f475d077d8dbb0e87ec536c906a04505e7`; both bodies bind those exact candidates, only top carries one `Fixes DEV-45`, and PR #325 is MERGED at `2026-09-02T04:26:48Z` and excluded from active stack #328.
- DONE: Perform the complete GitHub-native feedback observation for both active layers.
  Start and repeat repository-explicit views matched both exact heads; every GraphQL thread page ended with `hasNextPage=false` and zero nodes, every REST review pagination returned one complete empty page, and the two canonical records below therefore have empty evidence-bearing disposition populations.
- DONE: Validate bottom-layer required checks against the corrected exact base.
  Required runs `33590837218` and `33590837209` both passed after checking out merge `a0bd048babbaf042f91ac582f30285278f8d9db2`, exactly candidate `399a010cfd8a3d1c2688798472b927f4c9a74f9d` into `main@3aafd3d22e749257f3551079475cc41183525d7c`.
- FAILED: Adjudicate PR #326 as having valid base-bound CI evidence after the base/topology correction.
  Required runs `33589599589` and `33589599609` passed only on old merge `2e70da1af3822b6bf860fd4425cdc91841a00364`, whose immutable checkout log says top `314045f475d077d8dbb0e87ec536c906a04505e7` into old base `75ef10766a6e9d1fd315a295b388b75b1987a336`; current merge ref `f6e01e9979361220aae4abfbb1387b590973de3e` instead composes the top over corrected bottom merge `a0bd048babbaf042f91ac582f30285278f8d9db2`, so current Actions association metadata cannot substitute for an exact corrected-topology run.
- DONE: Append and commit only the durable validation observation without mutating product code, PRs, readiness, stack links, or gate state.
  Product worktree remains clean at `111d47126df43c15c02d8db4bb0fb4621df25aa1`, whose tree equals top candidate `314045f475d077d8dbb0e87ec536c906a04505e7`; all provider operations were read-only.

### Summary

Corrected stack #328 has stable two-layer identities, exact bodies, complete empty GitHub-native feedback, and valid bottom-layer checks. Validation is REJECTED only because PR #326 has no required CI run against the corrected base composition; it must remain Draft and not Ready until that exact base-bound evidence exists.

PR feedback: {"dispositions":[],"fingerprint":"sha256:5b1677c63be19e9086e36ae77589a8c06ed3031f02f87375e5e108eb93abae32","head":"399a010cfd8a3d1c2688798472b927f4c9a74f9d","layer":"bottom","pr_number":324,"repository":"iamcxa/kc-claude-plugins","scheme":"github-pr-feedback/v1"}
PR feedback: {"dispositions":[],"fingerprint":"sha256:654eac8235793e0b9029a37b8e03c04841111498725943edf2143d8a7b8e306e","head":"314045f475d077d8dbb0e87ec536c906a04505e7","layer":"top","pr_number":326,"repository":"iamcxa/kc-claude-plugins","scheme":"github-pr-feedback/v1"}

## Stage Report: validation (cycle 4)

- DONE: Observe complete GitHub-native feedback for PRs 324, 325, and 326 at their exact approved heads, with stable bottom/middle/top layer identities.
  Start and repeat repository-explicit PR views matched bottom `#324@a91da87379c77ab4d4b7837f2dec664d5eb20136`, middle `#325@75ef10766a6e9d1fd315a295b388b75b1987a336`, and top `#326@314045f475d077d8dbb0e87ec536c906a04505e7`; every GraphQL thread page ended with `hasNextPage=false` and zero nodes, and every REST review pagination returned one complete empty page.
- DONE: Record one canonical github-pr-feedback/v1 line per layer with complete pagination, exact-head repeat readback, fingerprint, and evidence-bearing dispositions.
  The three records below hash canonical UTF-8 objects containing `pr_number`, stable layer, exact head, and `items:[]`; their empty dispositions are clean only because both native feedback populations completed without retained external items.
- DONE: Commit and push only the durable validation observation; do not modify product code, PR content, branches, Draft status, stack linkage, readiness, or merge state.
  Product worktree remains clean at `111d47126df43c15c02d8db4bb0fb4621df25aa1`, whose tree equals top candidate `314045f475d077d8dbb0e87ec536c906a04505e7`; no product or provider mutation was made.
- FAILED: Classify the current three-PR stack as Ready.
  Required runs `33589546743` for PR #324 and `33589563504` for PR #325 fail `kc-dev-flow-contract-test.py` with `self-adopted profile loader differs from package source`; PR #326 has both required checks passing, so independent-layer delivery readiness is not satisfied.

### Summary

GitHub-native feedback is complete and empty at all three exact heads, with stable bottom, middle, and top identities. The current stack is not Ready because the bottom and middle required portable-contract checks fail independently; this report records the observation without changing product or provider state.

PR feedback: {"dispositions":[],"fingerprint":"sha256:8169a60f11878b081fcdc13b57501aeabc2e4392bfd98369557fc9c55054b7ba","head":"a91da87379c77ab4d4b7837f2dec664d5eb20136","layer":"bottom","pr_number":324,"repository":"iamcxa/kc-claude-plugins","scheme":"github-pr-feedback/v1"}
PR feedback: {"dispositions":[],"fingerprint":"sha256:9e3074d3870cdf70fd08e4861a33b0f2182041b9ffeccb26eceabd251cfae60b","head":"75ef10766a6e9d1fd315a295b388b75b1987a336","layer":"middle","pr_number":325,"repository":"iamcxa/kc-claude-plugins","scheme":"github-pr-feedback/v1"}
PR feedback: {"dispositions":[],"fingerprint":"sha256:654eac8235793e0b9029a37b8e03c04841111498725943edf2143d8a7b8e306e","head":"314045f475d077d8dbb0e87ec536c906a04505e7","layer":"top","pr_number":326,"repository":"iamcxa/kc-claude-plugins","scheme":"github-pr-feedback/v1"}

## Stage Report: implementation (cycle 4)

- DONE: Keep PR #323 Draft; do not ready, merge, close, push, create, or link PRs.
  Live readback shows PR #323 OPEN and Draft at unchanged remote head `61ce308dfeaae40f05b997092eb3a3a359a61ff6`; candidate `111d47126df43c15c02d8db4bb0fb4621df25aa1` remains local.
- DONE: Make the smallest local contract correction that supports provider-backed native stacks.
  Commit `111d47126df43c15c02d8db4bb0fb4621df25aa1` reserves exact `delivery.branch` and `delivery.close_line` for the top layer while lower layers bind reviewed unique branch/base pairs with no close line.
- DONE: Update the Local Profile delivery-base row so it matches the executable sibling-base behavior already required by pr-merge.
  The Local Profile now selects trunk for independent units and the immediately lower reviewed sibling branch/candidate for dependent green layers.
- DONE: Add focused behavior-level coverage in the existing contract suite; do not add a new standing checker or dependency.
  `python3 scripts/pr-merge-portable-delivery.test.py` passes and rejects lower-layer provider-branch reuse, lower-layer close lines, lost top provider binding, restored trunk-only policy, and removed sibling-base policy.
- DONE: Preserve all unrelated candidate bytes and prior acceptance evidence.
  The correction changes only `docs/dev/README.md`, `docs/dev/_mods/pr-merge.md`, and `scripts/pr-merge-portable-delivery.test.py`; prior commits and AC-1 through AC-7 behavior remain intact.
- DONE: Stop and report instead of widening if this requires a provider schema change, more than five files, or more than 300 changed lines.
  No provider schema changed; the correction is 3 files and 121 changed lines (`+100/-21`) over rejected candidate `61ce308dfeaae40f05b997092eb3a3a359a61ff6`.
- DONE: Report the new exact candidate plus focused falsification evidence.
  Exact candidate `111d47126df43c15c02d8db4bb0fb4621df25aa1` passes the focused portable-delivery suite, repository contract, all-profile route gate, installed-loader suite, and exact-base diff check; total scope is 39 files/3,991 changed lines below 44/4,800.

### Summary

Provider-backed native-stack delivery now gives every lower layer an explicitly reviewed unique branch/base and no provider close line, while the top alone carries Linear's exact branch and `Fixes DEV-45`. The bounded three-file correction preserves the installed-contract outcome and leaves Draft PR #323 untouched for fresh validation.

## Stage Report: validation (cycle 3)

- DONE: Validate exact candidate 111d47126df43c15c02d8db4bb0fb4621df25aa1 against all prior AC-1 through AC-7 evidence and required repository gates.
  Exact candidate `111d47126df43c15c02d8db4bb0fb4621df25aa1` over required base `3aafd3d22e749257f3551079475cc41183525d7c` passes local validation at 39 files/3,991 changed lines (`+1101/-2890`), below the 44-file/4,800-line stops; the assigned worktree is clean on Linear's exact branch.
  AC-1 evidence: exact candidate `111d47126df43c15c02d8db4bb0fb4621df25aa1` passed `profile-contract-loader.test.py` and `kc-dev-flow-contract-test.py`; they fail if any supported profile-stage cannot load from arbitrary installed roots, needs an adopter canonical copy, or such a copy returns.
  AC-2 evidence: exact candidate `111d47126df43c15c02d8db4bb0fb4621df25aa1` passed `profile-contract-loader.test.py`; it fails if same-stage version/digest drift is accepted or a compatible upgrade cannot bind only at the next stage boundary.
  AC-3 evidence: exact candidate `111d47126df43c15c02d8db4bb0fb4621df25aa1` passed `profile-contract-loader.test.py` and `kc-dev-flow-minimal-stack-ablation.test.py`; they fail if an incompatible interface dispatches, mutates the pin, omits the refit target, or the compatibility guard is removed.
  AC-4 evidence: exact candidate `111d47126df43c15c02d8db4bb0fb4621df25aa1` passed `profile-contract-loader.test.py`; it fails if adoption or upgrade changes README policy, local-mod bytes or mode, or unrelated Spacedock state.
  AC-5 evidence: exact candidate `111d47126df43c15c02d8db4bb0fb4621df25aa1` passed `kc-dev-flow-contract-test.py`, the live three-profile route gate, and the 57-mutant ablation; they fail if a canonical copy returns or route, close-guard, conditional-reference, or kernel authority weakens.
  AC-6 evidence: exact candidate `111d47126df43c15c02d8db4bb0fb4621df25aa1` passed the three-arbitrary-root loader matrix and invocation-local loader handoff; they fail if resolution needs host discovery or moving the package or worktree changes the selected contracts.
  AC-7 evidence: exact candidate `111d47126df43c15c02d8db4bb0fb4621df25aa1` rejected all 57 named without-it mutants, retains only repository-owned `docs/dev/_mods/pr-merge.md`, and remains within both scope stops.
  Release metadata (34 checks), version parity, skill frontmatter (12 fixture checks plus 44 live skills), plugin release (11 checks plus packaged contract), work-context (23 checks), state prerequisite, RoboRev contract, and whitespace gates all passed.
- DONE: Adversarially verify provider-backed native-stack semantics: only the top layer owns the exact Linear branch and Fixes DEV-45; lower layers retain unique reviewed branches, sibling bases, and no close line.
  `pr-merge-portable-delivery.test.py` passed and rejected all 12 delivery mutants, including lower-layer reuse of the provider branch, a lower close line, loss of the top provider binding, restored trunk-only policy, and removal of the sibling-base rule; the contract binds only the top to `feature/dev-45-load-kc-dev-flow-contracts-from-the-installed-plugin` and exactly one `Fixes DEV-45`.
- DONE: Re-adjudicate the required PR topology and report exact green layer boundaries without mutating, pushing, closing, readying, linking, or merging PR #323.
  Native stack exception: REJECTED. The numeric trigger is met and three dependent green scopes remain required: bottom `3aafd3d2..a91da873` is the 3-file manifest/loader layer; middle is `a91da873..12ded46a` plus the one-line `61ce308d` Mermaid repair; top is the `12ded46a..2c5149dc` vendored-copy deletion plus `61ce308d..111d4712` provider-stack correction.
  The stack must be recut because historical `12ded46a` alone still has the duplicate Mermaid node: the middle layer needs a new exact candidate containing that repair, and the top needs a new exact candidate preserving the final `111d4712` tree. Bottom and middle use distinct reviewed branches, the immediately lower sibling branch/SHA, and no close line; only the top uses Linear's exact branch and one `Fixes DEV-45`.
  PR #323 remains OPEN and Draft at `61ce308dfeaae40f05b997092eb3a3a359a61ff6` over `3aafd3d22e749257f3551079475cc41183525d7c`, with its single-PR exception body and both required checks passing; it is not the local candidate or a native stack, and no provider mutation was made.
  Review disposition is deterministic-only: the change is a declarative delivery contract exercised by mutation tests, with no new credential, privacy, data, or runtime surface. Rollback and stage-boundary recovery remain unchanged; the First Officer owns stack construction and per-layer feedback/check monitoring, while exact-candidate Captain authorization is still absent because the prior one-Draft authorization covered only `61ce308d` and is superseded.

### Summary

Exact candidate `111d47126df43c15c02d8db4bb0fb4621df25aa1` passes every AC and repository gate, including provider-backed stack falsification. Local validation is PASSED, but delivery remains blocked until the three scopes are recut into independently green Draft layers and the Captain reviews their exact branches, bases, bodies, and candidates; PR #323 was only observed.

PR feedback: {"dispositions":[],"fingerprint":"sha256:11374cc6b7bfd28902fd621a1603f5669788aaab44d804bc6364a83597a5b18f","head":"61ce308dfeaae40f05b997092eb3a3a359a61ff6","layer":"single","pr_number":323,"repository":"iamcxa/kc-claude-plugins","scheme":"github-pr-feedback/v1"}
