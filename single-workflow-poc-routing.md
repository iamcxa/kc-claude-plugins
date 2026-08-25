---
title: "kc-dev-flow: make POC a bounded decision route in one workflow"
status: validation
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
        - id: gate:ahd8hehpz3g9r7vqmrz82z4x:validation
          stage: validation
          attempts:
            - id: gate-attempt:ahd8hehpz3g9r7vqmrz82z4x-validation-1
              briefing:
                id: briefing:ahd8hehpz3g9r7vqmrz82z4x:validation:attempt-1:revision-1
                digest: sha256:e7acf1724d8cc809da557a1176ebf717a86fd2fada8754061b8675b15dbe616e
                request-digest: sha256:9a1081ef3472496cba1167082e5df54218b9a4ca079918d87adfe2228510ddce
                room-ref: ./single-workflow-poc-routing/review/validation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:ahd8hehpz3g9r7vqmrz82z4x:validation:1
                briefing: briefing:ahd8hehpz3g9r7vqmrz82z4x:validation:attempt-1:revision-1
                by: person:captain
                at: "2026-08-25T08:53:01.957684Z"
                decision: approve
                reason: Captain approved exact candidate 736306b64f54ffbdc28e8432276be2a938a93037 for Draft PR delivery.
              application:
                target-stage: done
                state: superseded
            - id: gate-attempt:ahd8hehpz3g9r7vqmrz82z4x-validation-2
              briefing:
                id: briefing:ahd8hehpz3g9r7vqmrz82z4x:validation:attempt-2:revision-1
                digest: sha256:347151298bc280d9fe38ea776968771db4279bf100c4517650123ffe4a8a7662
                request-digest: sha256:df753d3ec0066d8019e7b9c50b15f7ce2076d4593711845f4813dacb183732a8
                room-ref: ./single-workflow-poc-routing/review/validation/briefing-2
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
- Captain choice: reduce scope, approved 2026-08-25. Remove non-essential
  wrapper structure and test duplication while retaining every accepted close
  behavior; the 650-line stop condition remains unchanged.

## Implementation stop — total delivery diff

- Observed after Task 2 commit `e514078`: 13 changed files and 2,510 changed
  lines against `origin/main` (2,456 additions and 54 deletions).
- Crossing: 1,310 lines above the approved 1,200-line stop condition.
- Detection error: the first observable crossing was 1,446 changed lines after
  Task 1; implementation should have stopped there, before Task 2.
- Cause: the threshold included the already accepted 459-line design and
  647-line implementation plan but left only 94 lines for implementation.
- State: stopped before Task 3. Task 1 and Task 2 commits remain separately
  reviewable; the close-guard limit remains satisfied at 649 lines.
- Captain choice: reshape approved 2026-08-25. Replace the 1,200 changed-line
  stop with 3,300: 2,510 observed, about 500 named remaining lines, and 290
  lines of variance. Keep the 24-file and 650 close-guard limits unchanged.

## Shape correction — delivery file count

- Observed after Task 3 commit `8be5121`: 16 changed files.
- The accepted Task 4 package/adopter parity, three routing skills, migration,
  rationale, and two README surfaces require 15 additional named files.
- Completing the already accepted output therefore requires 31 changed files;
  the 24-file stop cannot hold without omitting a required contract surface.
- State: stopped before Task 4 to avoid a knowingly partial documentation and
  migration cutover.
- Captain choice: reshape approved 2026-08-25. Replace the 24-file stop with
  32 files (31 named files plus one variance); keep 3,300 changed lines and the
  650-line guard pair unchanged.

## Implementation evidence

- Candidate revision: `343eca90af2296efba77100c21fbd950149e6342`.
- Entry contract: packaged and adopted loaders require a v3 POC decision,
  falsifier, budget, and stop condition; active v2 POCs fail with the ordered
  migration message while Pilot and Production retain v2 compatibility.
- Close contract: the packaged and adopted close guards support prepare,
  create, and consume; creation reuses the sole canonical downstream item and
  refuses duplicate source matches or a preselected profile.
- Runtime proof: the pinned Spacedock fixture exercises stop, change, created,
  deferred, declined, failed-write retry, and duplicate-source refusal.
- Documentation and migration: README, rationale, adoption, selection,
  continuation, migration, kernel, POC stage contracts, and bound architecture
  describe the same bounded route and v3 cutover.
- Changed-file mapping: loader and loader tests satisfy entry and migration;
  close guard and real-runtime tests satisfy outcome, idempotency, and recovery;
  profile/kernel copies satisfy loaded behavior; skills and retained docs
  satisfy adopter and operator guidance; contract, ablation, and multi-profile
  scripts satisfy parity, without-it, and unchanged-route obligations.
- Subtraction result: no workflow, model/provider adapter, hosted canary,
  Spacedock graph, automatic scheduling/profile authority, or behavioral-gate
  laboratory file changed.
- Shape stops at the candidate: 27 of 32 files, 1,984 of 3,300 changed lines,
  and 649 of 650 close-guard implementation/test lines.

```yaml
project_context:
  impact: update
  authority: "Root PRODUCT.md, ARCHITECTURE.md, and CLAUDE.md"
  claim_locator: "ARCHITECTURE.md#kc-dev-flow-profile-native-loading"
  surface: "profile receipt schema and POC route boundary"
  stale_claim: "all selected work items use a v2 receipt and POC has no deterministic close boundary"
  approved_change: "v3 POCs bind decision, falsifier, budget, and stop condition, then close as proceed, stop, or change without downstream profile authority"
  landed_change: "ARCHITECTURE.md at candidate 343eca90af2296efba77100c21fbd950149e6342"
  planned_check: "fresh contract and ablation tests plus exact comparison of ARCHITECTURE.md with the v3 loader and close guard"
  validation_evidence: "contract PASS plus exact ARCHITECTURE.md, loader, close-guard, continuation, and retained-document subtraction comparison at 343eca90af2296efba77100c21fbd950149e6342"
```

### Implementation-exit observation

```yaml
review_convergence:
  candidate_revision: 343eca90af2296efba77100c21fbd950149e6342
  capability: "RoboRev v0.62.0 CLI JSON commands, daemon, and Claude Code agent available"
  mode: daemon
  selected_profile: production
  implementation_family: openai
  provider: roborev
  outcome: UNAVAILABLE
  reason: "unavailable: no exact-input job exists and the accepted scope excludes a new model call"
  identity_sha256: a4c72be95e4b3331e865b8a7e510c5db07d7c9cd12f2c8fb6d6cb2464d3e0dd0
  configuration_sha256: 3c2bae48809c3375a68610c9236487dc1ece33e933e343e19fab5e470f1d6a68
  agent: claude-code
  model: sonnet
  reasoning: thorough
  minimum_severity: medium
  panel: none
  job_identity: none
  member_states: "no job; claude-code capability probe passed"
  request_count: 0
  confirmation_count: 0
  cost_coverage: "not applicable; no job launched"
```

The earlier capability-stage list query addressed revision `9d7b4f13`, before
the final architecture sync, and is not reused as evidence for this candidate.
Per the observation contract, `UNAVAILABLE` does not replace fresh validation
and grants no delivery authority.

## Validation evidence — superseded by rework

Exact candidate: `736306b64f54ffbdc28e8432276be2a938a93037`.

- `python3 scripts/kc-dev-flow-contract-test.py`: PASS. This includes loader,
  close-guard, pinned Spacedock route, packaged/adopted parity, and migration
  fixtures.
- `python3 scripts/kc-dev-flow-minimal-stack-ablation.test.py`: PASS. The suite
  rejected disabled POC entry validation and a removed close guard, as well as
  every pre-existing route mutant.
- `python3 scripts/kc-dev-flow-multi-profile-gate.py --json`: PASS. POC, Pilot,
  and Production all reached done; POC remained the lightest route.
- Release metadata: 34/34; skill frontmatter tests: 12/12; all 45 skill
  directories valid; plugin, marketplace, Codex, and Hermes manifests remain
  at matching `kc-dev-flow` version 3.0.0.
- Existing-CI runtime, three runs each: corrected base median 27.23 seconds;
  candidate median 31.65 seconds; comparable delta +4.42 seconds, below the
  20-second stop. The uncorrected base fails early and was not used as a speed
  baseline. No new CI job, PR trigger, or model call was added.
- Exact raw Git scope: 29 changed files, 3,090 changed lines, and 649 close-guard
  implementation/test lines. The earlier 32-file observation came from a
  display-wrapper count; raw `git diff --name-only | wc -l` corrects it.
- Project context: `ARCHITECTURE.md` now describes supported receipts, v3 POC
  entry, its three outcomes, v2 compatibility, and independent downstream
  authority; fresh contract and ablation runs agree with that claim.
- Retained documents: README states the proportional-risk outcome and bounded
  POC role; rationale limits the value claim; migration gives ordered v3-to-v4
  cutover and rollback; no stale v2-only operator instruction remains.
- Delivery state: no open PR uses `iamcxa/dev-flow-explore-router`; local policy
  selects `main` as base. Release Please remains the version/tag owner and the
  breaking commit should make its later release PR propose kc-dev-flow 4.0.0.

Acceptance mapping:

1. The unchanged multi-profile gate proves one graph routes all three profiles.
2. POC base/README own bounded exploration and technical proof.
3. Loader mutation fixtures reject each missing v3 POC entry field.
4. The real Spacedock fixture reaches stop, change, and proceed outcomes.
5. Prove contract and close guard separate supported evidence from handoff.
6. Real routes cover created, deferred, declined, and not-applicable handoffs.
7. Created items stay backlog, reject a preselected profile, and inherit the
   repository's trunk-only delivery-base policy when later developed.
8. No Spacedock graph, route slug, state owner, or terminal mechanism changed.
9. Without-it and real-route tests reject missing outcome, orphan, and duplicate
   handoffs; docs make no engine tamper-resistance claim.
10. No workflow, paid path, secret, protected Environment, or release claim was
    added.
11. No behavioral-gate laboratory file or evidence was imported.

Rollback remains the ordered pair: active v2 POCs finish on pinned 3.x or are
Captain re-recorded; adopters re-vendor loader, close guard, and contracts
together. The profile-effect comparison, hosted release canary, provider CI,
and actual Release Please 4.0.0 proposal remain outside this feature PR's local
claim. RoboRev is `UNAVAILABLE` for this exact candidate because no reusable job
exists and the accepted slice forbids a new model call; request count is zero.

## Rework — absorbed planning artifacts

Captain direction on 2026-08-25 removed the 459-line Superpowers design and
647-line implementation plan from the delivery diff after checking their
contents block by block. The terminal approval for `736306b6` was superseded
through `merge guard --rework`; current candidate is
`343eca90af2296efba77100c21fbd950149e6342`.

- Design decision, outcome, non-goals, empirical boundary, and rejected
  Explore-workflow direction live in this entity and `kc-dev-flow/RATIONALE.md`.
- Entry routing and v3 receipt rules live in the loader, kernel,
  `choose-work-profile`, and their mutation tests.
- POC work, outcome, gate, and handoff rules live in the POC profile contracts,
  `continue-dev-flow`, close guard, and real Spacedock route tests.
- Adoption, compatibility, rollback, and release boundaries live in
  `adopt-dev-flow`, `MIGRATION.md`, README, and this entity.
- File mapping, stop decisions, execution results, acceptance mapping, runtime,
  and exact validation live in this entity, commits, and executable tests.
- The profile-effect POC and hosted canary remain explicitly outside this item;
  they require new entities and Captain choices rather than retained plans in
  this delivery.

The commit-qualified design (`6a68cab0`) and shape (`ca8f9f1`) references above
remain historical provenance. They are not current-path document dependencies.
No contract, runtime, or test references either removed path.

## Validation evidence — absorbed-plan head

Exact candidate: `343eca90af2296efba77100c21fbd950149e6342`.

- Contract test PASS; without-it ablation PASS with every declared mutant
  rejected; POC, Pilot, and Production all reached done on the pinned Spacedock
  runtime.
- Release metadata 34/34; skill-frontmatter fixtures 12/12; all 45 skill
  directories valid; plugin and marketplace versions remain at matching 3.0.0.
- Existing contract-test runtime: corrected-base median 27.23 seconds;
  candidate runs 29.03, 28.13, and 29.22 seconds, median 29.03 seconds;
  comparable delta +1.80 seconds. No new CI job or model call exists.
- Exact raw Git scope is 27 changed files, 1,984 changed lines, and 649
  close-guard implementation/test lines, within every Captain stop.
- Independent retained-document subtraction check found no current contract,
  runtime, or test dependency on either removed path. Every operative block has
  the second home recorded above; commit-qualified provenance remains
  recoverable without shipping an execution plan or historical design record.
- Project context remains aligned: `ARCHITECTURE.md` describes the v3 POC
  boundary and mixed receipt compatibility implemented by the exact loader and
  close guard.

The behavioral profile-effect POC and hosted release canary remain explicitly
unproved and outside this PR. RoboRev remains `UNAVAILABLE` with zero requests
because the accepted slice excludes a new model call.
