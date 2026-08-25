---
title: "kc-dev-flow: make POC a bounded decision route in one workflow"
status: implementation
source: "Captain-approved design 6a68cab0 after Claude PASS, 2026-08-25"
product: kc-dev-flow
sprint: S4
sprint-readiness: ready
started:
completed:
verdict:
worktree:
issue:
pr:
mod-block:
id: ahd8hehpz3g9r7vqmrz82z4x
gates:
    version: 1
    records:
        - id: gate:ahd8hehpz3g9r7vqmrz82z4x:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:ahd8hehpz3g9r7vqmrz82z4x-backlog-1
              briefing:
                id: briefing:ahd8hehpz3g9r7vqmrz82z4x:backlog:attempt-1:revision-1
                digest: sha256:7c89ab7d8e20bb5a8c02e8d500290a3deec8daacc17129496f82f3796de025b5
                request-digest: sha256:1e7a007b69d1aba761c80aa5af0485f20027170c5069dfc5ddd153401f0c0b2f
                room-ref: ./single-workflow-poc-routing/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:ahd8hehpz3g9r7vqmrz82z4x:backlog:1
                briefing: briefing:ahd8hehpz3g9r7vqmrz82z4x:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-08-25T07:30:35.122184Z"
                decision: approve
                reason: Captain selected Production after approving kc-dev-flow/S4.
              application:
                target-stage: ideation
                state: consumed
        - id: gate:ahd8hehpz3g9r7vqmrz82z4x:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:ahd8hehpz3g9r7vqmrz82z4x-ideation-1
              briefing:
                id: briefing:ahd8hehpz3g9r7vqmrz82z4x:ideation:attempt-1:revision-1
                digest: sha256:cc1413a64f7d90333eb2b2232e1216d9365764455654b7450c7b1b440506d782
                request-digest: sha256:9e7d0fcbbcf9e7e60c16dd84fea9d826a751987eeecceb4c985ced8684e5b78b
                room-ref: ./single-workflow-poc-routing/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:ahd8hehpz3g9r7vqmrz82z4x:ideation:1
                briefing: briefing:ahd8hehpz3g9r7vqmrz82z4x:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-08-25T07:48:10.414226Z"
                decision: approve
                reason: Captain approved the Production shape and required KC Dev Flow to remain the governing workflow.
              application:
                target-stage: implementation
                state: consumed
---

## Problem

KC Dev Flow currently describes POC as an experiment that passes when one real
journey and critical assumption are observed, but actual use also asks POC to
decide whether the next commitment should proceed, stop, or change. Without an
explicit decision, falsifier, budget, stop condition, and terminal handoff
boundary, exploratory work can grow into delivery without a new risk decision.

Implement the Captain-approved single-workflow design at commit `6a68cab0`.
Keep the existing Spacedock graph and POC/Pilot/Production route slugs. Add the
smallest deterministic entry and close guards that make the declared kc-dev-flow
path fail closed while preserving Captain task-creation, scheduling, profile,
merge, and release authority.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v2
  selected: production
  recommended: production
  basis: >-
    This delivers an ongoing published workflow contract to existing adopters.
    The Spacedock graph and route slugs stay stable, but consumers must re-vendor
    the loader and contracts, and an active v2 POC must finish on the pinned old
    pair or be Captain re-recorded before the v4 cutover. That consumer action,
    coordinated migration, rollback, release evidence, and exact adopted-copy
    parity require Production rather than Pilot. The separate profile-effect
    comparison remains a later POC and is not part of this delivery item.
  route: [shape, build, verify]
  obligations:
    architecture:
      - Keep one workflow, the existing superset graph, and the existing profile route slugs.
      - Separate the evidence gate, POC outcome, and post-approval handoff without requiring a Spacedock engine change.
      - Define the v2/v3 cutover, recovery order, and Captain authority boundaries before implementation.
    implementation:
      - Add only the v3 receipt fields, deterministic entry checks, and one bounded POC close guard required by the approved design.
      - Update packaged and self-adopted contracts, profile choice, continuation, adoption, migration, and user-facing guidance together.
      - Do not copy the behavioral-gate laboratory branch or add model, provider, sandbox, attestation, or new CI-job machinery.
    testing:
      - Mutation-prove each required POC field and deterministic placeholder refusal without adding POC placeholders to Pilot or Production.
      - Exercise stop, change, created, deferred, declined, failed-write retry, and duplicate-source refusal on the pinned Spacedock runtime.
      - Prove package/adopter parity, v2/v3 migration behavior, unchanged multi-profile routing, rollback readiness, and measured incremental CI runtime.
  scope_boundary: >-
    No Explore workflow or stage, Spacedock engine change, cross-entity
    transaction, automatic downstream task/profile authority, model call, new CI
    job, hosted release canary, or reuse of the 14,568-line laboratory branch.
  promote_when:
    - No higher profile exists; stop for new Captain scope if implementation requires a Spacedock primitive or any excluded provider, model, hosted, or automatic authority surface.
  decision:
    authority: Kent (Captain)
    at: 2026-08-25T07:28:09Z
```

## Accepted outcome and non-goals

Accepted outcome: one adopted workflow routes bounded exploration and technical
proof through POC; a supported POC conclusion closes as `proceed`, `stop`, or
`change`; any downstream delivery is separately created, scheduled, and
profiled.

Non-goals: no Explore workflow or stage, no Spacedock engine change, no
cross-entity transaction, no model call or new CI job in the contract slice, no
automatic downstream profile selection, and no reuse of the 14,568-line
behavioral-gate branch.

## Acceptance evidence

- Exact loader fixtures reject each missing or deterministic placeholder POC
  entry field while leaving Pilot and Production free of POC placeholders.
- A pinned Spacedock local test exercises `stop`, `change`, `created`,
  `deferred`, and `declined` close paths, including succeeded-create / failed-
  handoff-write retry without a duplicate item.
- Package and adopted contract copies remain byte-identical where required.
- Migration proves the declared v2/v3 cutover behavior and names the consumer
  action before release.
- Existing multi-profile routing remains green on the exact supported runtime.

## Measurement

No model call or new CI job belongs to this contract slice. Measure any added
runtime in existing CI jobs before release; do not claim an unmeasured cost.

## Shape outcome

Captain-approved shape: commit `ca8f9f1`,
`docs/superpowers/plans/2026-08-25-kc-dev-flow-single-workflow-poc-routing.md`.
Every journey step is DESIGNED until the implementation tests exercise it on
Spacedock 0.27.0.

- Architecture: retain one graph and three route slugs; add v3 POC entry
  validation plus one close guard that delegates mutations to Spacedock.
- Authority: Superpowers may organize workers only inside `implementation`;
  KC Dev Flow remains the profile, state, gate, and Captain authority.
- Recovery: upgrade and rollback the loader, close guard, and vendored contracts
  as one pair; active v2 POCs finish on 3.x or receive a new Captain v3 receipt.
- Release checks: deterministic contract, ablation, live multi-profile, package
  parity, migration, and measured existing-CI runtime evidence at the exact head.
- Where it touches: 24 named files in the committed plan; no workflow file,
  Spacedock graph, model/provider surface, or behavioral-gate laboratory file.
- Stop numbers: more than 24 changed files, 1,200 changed lines, or 650 combined
  close-guard implementation/test lines stops implementation for Captain review.

## Implementation stop — close guard size

- Observed at implementation head `45f302c` plus the uncommitted Task 2 work:
  `poc-close-guard.py` is 403 lines and `poc-close-guard.test.py` is 288 lines,
  691 combined.
- Crossing: 41 lines above the Captain-approved 650-line stop condition.
- State: stopped before Task 2 commit; the focused guard test is GREEN, but no
  completion or scope claim is made.
- Recommendation: reduce scope by removing non-essential wrapper structure and
  test duplication while preserving the accepted prepare/create/consume,
  idempotency, and refusal behavior. Do not raise the threshold unless that
  smaller route cannot retain the accepted behavior.
- Captain choice: pending.
