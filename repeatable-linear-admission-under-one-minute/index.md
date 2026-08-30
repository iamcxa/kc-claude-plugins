---
title: "Add a workspace-bound Linear reader and admission guard"
status: backlog
source: "https://linear.app/duckbase-co/issue/DEV-12/add-a-workspace-bound-linear-reader-and-admission-guard"
product: kc-dev-flow
planning-window: "Linear Cycle b788c52d-8370-475f-be4f-8fcd88dd03d6 2026-08-27T16:00:00.000Z/2026-09-10T16:00:00.000Z"
planning-outcome: "Linear Project 535b8bd1-2d97-4d57-9161-1051574af0d5 Repeatable Linear admission under 1 minute sha256:74d2f2065da858dfe47fe3c04f6b32f0cddb9418d477de18b766dc5089254854"
sprint: repeatable-linear-admission-under-one-minute
sprint-readiness: ready
started:
completed:
verdict:
worktree:
issue:
pr:
mod-block:
id: np4b5ef99wf5tns6r7aqs10p
gates:
    version: 1
    records:
        - id: gate:np4b5ef99wf5tns6r7aqs10p:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:np4b5ef99wf5tns6r7aqs10p-backlog-1
              briefing:
                id: briefing:np4b5ef99wf5tns6r7aqs10p:backlog:attempt-1:revision-1
                digest: sha256:d957aa962460d82265eb1b209882c1fb94a5f9f730bad3285ea9790107fd1fa0
                request-digest: sha256:d389c270362b520d29fb75b44a2009188fee723770ce1223a38ebd69df97677c
                room-ref: ./review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:np4b5ef99wf5tns6r7aqs10p:backlog:1
                briefing: briefing:np4b5ef99wf5tns6r7aqs10p:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-08-30T10:09:33.703034Z"
                decision: approve
                reason: Captain approved the DEV-12 Pilot and the one-time manual workspace Linear MCP bootstrap for initial admission only; validation must use the durable reader and retain no exception.
              application:
                target-stage: ideation
                state: pending
---

## The problem

DEV-11 proved that Linear planning can enter the existing provider-neutral kc-dev-flow contract, but the path still depends on manual MCP reads and hand-built normalization. There is no persistent workspace-bound reader, and the loader does not enforce the Development Brief plus complete-or-absent Planning Receipt for Pilot or Production admission. The measured admission-to-verdict interval was 41m43s.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: pilot-product-slice
  recommended: pilot-product-slice
  basis: >-
    One maintainer will repeatedly use a persistent repository-local admission
    path that reads the current workspace's Linear account and creates durable
    execution state only after a clean reconcile. This is limited real use with
    likely iteration, but it accepts no production data, unattended operation,
    compatibility migration, automatic launch, SLO, or release duty.
  route: [shape, build, verify-deliver]
  obligations:
    architecture:
      - Preserve the existing five-field provider-neutral Planning Receipt; Linear remains the planning authority and Spacedock remains the execution authority.
      - Bind authentication to the current workspace and fail closed before execution-state mutation.
    implementation:
      - Retain only a workspace-bound Linear reader, loader admission guard, exact snapshot binding, comparator stop, and dispatch-envelope path required by the accepted journey.
      - Create no mirror, synchronization, polling, webhook, automatic launch, paid Linear Agent delegation, or second planning authority.
    testing:
      - Measure no more than 60 seconds from successful Todo-plus-Cycle update readback to a valid dispatch envelope, excluding prior human review and later worker startup.
      - Prove authentication refusal, invalid Development Brief refusal, partial Planning Receipt refusal, clean status progress, classified planning drift, and without-it failure for each retained component.
  scope_boundary: >-
    One repository, one workspace-bound Linear account, one Project, one Cycle,
    one issue, one Spacedock task, and one execution worktree. No multi-issue
    package, Initiative, Milestone, automatic launch, migration of prior work,
    POC-profile redesign, production operation, or broader provider framework.
  promote_when:
    - Unattended operation, production credentials or data, cross-repository reuse, compatibility migration, automatic launch, or an SLO becomes accepted scope.
  decision:
    authority: Kent Chen (Captain)
    at: 2026-08-30T09:59:53Z
```

## Accepted outcome

Starting from successful readback of one Captain-approved Todo-plus-Cycle update, emit a valid kc-dev-flow dispatch envelope within 60 seconds and with no further Captain intervention, using the workspace's Linear connection, the existing five-field snapshot, read-only reconcile, and fail-closed loader validation.

## Non-goals

- No GitHub mirror, bidirectional synchronization, polling, or webhook.
- No automatic workspace launch.
- No paid Linear Agent coding delegation.
- No multi-issue package, Initiative, or Milestone.
- No POC-profile redesign.
- No migration of previously admitted work.

## Acceptance evidence

- One live workspace-bound Linear read resolves DEV-12, its Project, Cycle 1, and the complete admitted set into the existing five-field snapshot.
- Missing or invalid authentication stops before task creation, state mutation, or dispatch without altering the real credential.
- Pilot and Production admission rejects a missing or invalid Development Brief and a partial Planning Receipt before task creation or dispatch.
- Todo to In Progress remains clean; a changed Cycle, Project package, goal, non-goal, or admitted membership stops with a classified delta.
- A fresh exact-revision measurement emits a valid dispatch envelope within 60 seconds of Todo-plus-Cycle update readback with no additional Captain intervention.
- Removing any retained reader, loader guard, snapshot binding, comparator behavior, or dispatch stop breaks a named accepted property.

## Route-back conditions

Return to Linear Planning with `change` or `stop` if the 60-second target requires synchronization or automatic launch, workspace-bound authentication cannot fail closed, the five-field provider-neutral contract cannot express the planning object, or any accepted goal or non-goal changes.

## Measurement

Measure wall-clock time from successful Todo-plus-Cycle update readback to dispatch-envelope emission. Record the exact candidate revision, elapsed time, Captain interventions after admission, clean and drift results, retained components, the acceptance evidence broken by removing each component, and cleanup status.
