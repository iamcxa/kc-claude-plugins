---
title: "Admit one Linear-planned release into kc-dev-flow"
status: implementation
source: "https://linear.app/duckbase-co/issue/DEV-11/admit-one-linear-planned-release-into-kc-dev-flow"
product: kc-dev-flow
planning-window: "Linear Cycle b788c52d-8370-475f-be4f-8fcd88dd03d6 2026-08-27T16:00:00.000Z/2026-09-10T16:00:00.000Z"
planning-outcome: "Linear Project 10ae38f6-2d58-45a6-8ce5-388b35086e97 Linear-backed kc-dev-flow admission sha256:c29c728e43bbc88a12f7794bf1d687eeec3b3005baa96b93c51bede6f53f51e1"
sprint: linear-backed-kc-dev-flow-admission
sprint-readiness: ready
started: 2026-08-30T07:47:10Z
completed:
verdict:
worktree: .worktrees/spacedock-ensign-linear-backed-kc-dev-flow-admission
issue:
pr:
mod-block:
id: k0h7t34tjp7em4ns8rae22qv
gates:
    version: 1
    records:
        - id: gate:k0h7t34tjp7em4ns8rae22qv:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:k0h7t34tjp7em4ns8rae22qv-backlog-1
              briefing:
                id: briefing:k0h7t34tjp7em4ns8rae22qv:backlog:attempt-1:revision-1
                digest: sha256:d61e388310926a6c75f01000aa683e2a26c21a31fdc7d558ef101d7b2b71984c
                request-digest: sha256:158d74ff29a2ad0e8398fa21b9603960877b3f59d258be893de7b126bcf5c2ec
                room-ref: ./review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:k0h7t34tjp7em4ns8rae22qv:backlog:1
                briefing: briefing:k0h7t34tjp7em4ns8rae22qv:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-08-30T07:42:31.282085Z"
                decision: approve
                reason: Captain approved the presented POC profile and backlog admission with ok after the exact Linear snapshot, clean reconcile, drift stop, scope boundary, and without-it proof target were shown.
              application:
                target-stage: ideation
                state: consumed
---

## The problem

kc-dev-flow claims that its planning provider is replaceable, but this repository has only exercised GitHub Issues plus GitHub Projects. There is no real evidence that a Linear-planned release can enter execution without duplicate planning authority or additional steering.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: poc-exploration
  recommended: poc-exploration
  basis: >-
    One maintainer is testing one Linear issue in one Cycle as a bounded decision
    experiment. Credible negative evidence can cancel or materially change the
    next commitment to build a persistent Linear reader. No production data,
    credentials, compatibility migration, unattended operation, or release duty
    is accepted.
  route: [build, prove]
  obligations:
    architecture:
      - Use the existing provider-neutral Planning Receipt and comparator without adding a second planning authority.
      - Bind one Linear Project, one Cycle, one issue, one Spacedock task, and one worktree.
    implementation:
      - Exercise the smallest real MCP read, deterministic normalization, snapshot, and read-only reconcile path.
      - Do not retain a reusable adapter, webhook, mirror, polling loop, or automatic workspace launcher in this POC.
    testing:
      - Prove an unchanged planning object returns clean.
      - Prove a changed Cycle, Project package, goal, non-goal, or admitted membership stops before dispatch.
      - Apply the without-it test to every retained mechanism.
  scope_boundary: >-
    No durable Linear integration, reusable skill, GitHub mirror, bidirectional
    synchronization, automatic launch, Relay adoption, multi-issue package, or
    production release commitment.
  poc_decision: >-
    Decide whether evidence justifies admitting a separate Pilot commitment for
    a durable Linear reader and repository binding.
  poc_falsifier: >-
    Stop or change direction if the live Linear planning object cannot be
    normalized into the existing receipt and fail-closed comparator without a
    duplicate authority, core schema expansion, or manual scope reconstruction.
  poc_budget: >-
    One SD task, one worktree, one live MCP read, one clean reconcile, one
    intentional drift probe, existing comparator tests, and no additional issue
    or reusable adapter.
  poc_stop_when: >-
    Stop after both clean and intentional-drift paths are evidenced, or at the
    first proof that the accepted mapping requires excluded scope.
  promote_when:
    - Captain accepts persistent reuse, lifecycle, or operational responsibility after the POC returns to planning.
  decision:
    authority: Kent Chen (Captain)
    at: 2026-08-30T07:37:52Z
```

## Accepted outcome

Produce the smallest real Linear-to-kc-dev-flow admission: one approved issue in dev Cycle 1 within this Project becomes one Spacedock task and one execution workspace.

## Non-goals

- No GitHub Project projection or mirrored issue.
- No bidirectional synchronization, polling, or webhook.
- No automatic workspace launch.
- No reusable Linear Agent skill until the one-off planning prompt proves reusable.
- No Relay migration or multi-issue release package.

## Acceptance evidence

- One live Linear MCP read resolves DEV-11, its Project, Cycle 1, and the admitted issue set.
- One exact Spacedock admission snapshot records source, planning window, planning outcome, accepted goal, and non-goals.
- Existing comparator contract tests pass on the exact implementation revision.
- One unchanged live normalization returns clean and permits dispatch.
- One intentional read-only planning delta is classified and stops before dispatch.
- Removing any retained component makes at least one accepted property fail.

## Route-back conditions

Stop and return to Linear Planning when the Cycle, Project package, accepted outcome, non-goals, or admitted membership changes; when normalization requires duplicate authority or core schema expansion; or after the POC records PROCEED, CHANGE, or STOP. This POC creates no downstream item and preselects no later profile.

## Measurement

Record elapsed time from admitted task creation to POC verdict, the number of Captain interventions after this admission, retained implementation components, and the acceptance criterion broken by removing each retained component.

### RoboRev observation claim

- identity: `sha256:afa6016daeaa64aada1402f442639d684891fe80519a70b6c741a4109e32d154`
- claimant: `codex:spacedock-ensign-k0h7t34tjp-implementation`
- observed state revision: `7e70d2fa9811700bc1bcef74fff66362989f5eb0`
- state: `claimed`
- exact input: repository `https://github.com/iamcxa/kc-claude-plugins.git`; base `d8092fa93eec70a0d5c64d663e6c156983a785cf`; tip `7256e02dbbc5340e4328bfeeb016448e4033fde5`; RoboRev `0.62.0`; configuration object `225a29d4fa1eef963a7effaab7e60afa5f488e8f`; profile `poc-exploration`; reviewer `codex` / `gpt-5.6-terra` / `medium`; severity `high`; panel `none` with one member; timeout 600 seconds; request cap 1; confirmation cap 0.
