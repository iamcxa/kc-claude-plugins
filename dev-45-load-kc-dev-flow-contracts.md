---
title: Load kc-dev-flow contracts from the installed plugin
status: ideation
source: https://linear.app/duckbase-co/issue/DEV-45/load-kc-dev-flow-contracts-from-the-installed-plugin
product: kc-dev-flow
planning-window: Linear Cycle b788c52d-8370-475f-be4f-8fcd88dd03d6 2026-08-27T16:00:00.000Z/2026-09-10T16:00:00.000Z
planning-outcome: Linear Project e780d04f-cf7d-4ebb-bf9a-90fec8466923 Plugin-owned kc-dev-flow contracts sha256:4106b2e493e8bd75052c1fb3b775eaf434ef8b087a7717611d5d81f2a3a81990
sprint: S7
sprint-readiness: ready
design: required
started: 2026-09-01T16:31:49Z
completed:
verdict:
worktree:
issue:
pr:
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
                state: pending
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
