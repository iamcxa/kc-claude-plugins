---
title: "Make POC decisions ready within 15 minutes"
status: ideation
source: "https://linear.app/duckbase-co/issue/DEV-14/make-poc-decisions-ready-within-15-minutes"
product: kc-dev-flow
planning-window: "Linear Cycle b788c52d-8370-475f-be4f-8fcd88dd03d6 2026-08-27T16:00:00.000Z/2026-09-10T16:00:00.000Z"
planning-outcome: Linear Project 90103fbc-2653-47d8-829a-36cccc6116da POC decisions within 15 minutes sha256:7d790de539c857ef05cea26e21d02850304b70e9eccca931daa463fc1df39a5b
sprint: poc-decisions-within-15-minutes
sprint-readiness: ready
started: 2026-08-30T13:20:03Z
completed:
verdict:
worktree:
issue:
pr:
mod-block:
id: k80xhxhk9b9e26mnnyn2jwsh
gates:
    version: 1
    records:
        - id: gate:k80xhxhk9b9e26mnnyn2jwsh:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:k80xhxhk9b9e26mnnyn2jwsh-backlog-1
              briefing:
                id: briefing:k80xhxhk9b9e26mnnyn2jwsh:backlog:attempt-1:revision-1
                digest: sha256:3508a3f5b697f989c16118348d0e213c997209b88c64cbcb149fc94a35343771
                request-digest: sha256:ec83aaa24f2d201c6dca20ff69b2a5a3d7b64778fd6fb19116eff1b56822839f
                room-ref: ./review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:k80xhxhk9b9e26mnnyn2jwsh:backlog:1
                briefing: briefing:k80xhxhk9b9e26mnnyn2jwsh:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-08-30T13:22:16.295709Z"
                decision: approve
                reason: Captain approved the presented DEV-14 Linear package and Pilot admission; live reconcile must remain clean before ideation dispatch.
              application:
                target-stage: ideation
                state: consumed
---

## The problem

The POC profile claims bounded exploration but does not enforce a wall-clock decision budget. DEV-11 needed 41m43s to write its `poc_outcome` and 1h34m33s to terminalize. Its no-code proof repeated the same live read, reconcile, drift, and mutation evidence across build and prove, ran an unconditional RoboRev observation, and expanded without-it validation beyond the two mechanisms it retained.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: pilot-product-slice
  recommended: pilot-product-slice
  basis: >-
    This bounded repository change repairs the POC profile for limited real use.
    It changes shipped contracts and deterministic coverage without adding
    production operation, provider writes, compatibility migration, an SLO, or
    release ownership.
  route: [shape, build, verify-deliver]
  obligations:
    architecture:
      - Preserve the existing proceed, change, stop, and route-back boundary for POC work.
      - Keep Pilot and Production profile routes and obligations unchanged.
      - Keep the decision budget inside the POC contract without adding a timer or scheduler authority.
    implementation:
      - Add a positive decision-ready minute budget that defaults to 15 unless the approved brief records an override and reason.
      - Separate decision-ready latency from Captain wait and terminal cleanup.
      - Remove unconditional RoboRev and fresh validation for no-code or disposable POCs while retaining independently required repository safety boundaries.
    testing:
      - Prove one real journey, one critical falsifier, and focused without-it checks for only retained mechanisms.
      - Run one fresh measured no-code POC that reaches a durable outcome within 15 minutes with zero post-admission Captain intervention.
      - Reject any Pilot or Production route or obligation drift deterministically.
  scope_boundary: >-
    One repository-local Pilot changes only the POC profile contract, its focused
    enforcement, and one measured no-code dogfood. No daemon, polling, webhook,
    automatic workspace launch, token accounting, planning-provider redesign,
    DEV-11 history rewrite, or universal guarantee for an approved longer external experiment.
  promote_when:
    - Unattended operation, production credentials or data, provider writes, compatibility migration, an SLO, or release ownership enters accepted scope.
  decision:
    authority: Kent Chen (Captain)
    at: 2026-08-30T13:19:00Z
```

## Accepted outcome

Starting from an admitted Captain-approved POC, write a durable proceed, change, or stop outcome within 15 minutes by default and without another Captain intervention, while preserving one real journey, the critical falsifier, focused without-it evidence, cleanup, and an explicit route back to planning.

## Non-goals

- No timer daemon, polling loop, webhook, or automatic workspace launch.
- No token-accounting or model-cost framework.
- No changes to Pilot or Production requirements.
- No planning-provider, Project, Cycle, Initiative, or Milestone redesign.
- No rewriting or reclassifying DEV-11's historical evidence.
- No promise that an explicitly approved longer external experiment finishes within 15 minutes.

## Acceptance criteria

- **AC-1** Every admitted POC carries a positive decision-ready minute budget, defaulting to 15 unless the approved brief records a different limit and reason.
- **AC-2** Decision-ready elapsed time is measured from admitted task creation to the durable `poc_outcome`; Captain wait and post-decision cleanup are separate measurements.
- **AC-3** A no-code or disposable POC does not invoke RoboRev or fresh independent validation unless an independently required repository safety boundary applies.
- **AC-4** POC proof covers one real journey, one critical falsifier, and without-it checks only for its retained mechanisms; unrelated full regression or mutant suites are not selected.
- **AC-5** Budget exhaustion produces `change` with elapsed time, strongest evidence, strongest limit, reversal fact, and cleanup status instead of silent continuation.
- **AC-6** One fresh measured no-code POC reaches a durable outcome within 15 minutes with zero post-admission Captain interventions before decision-ready.
- **AC-7** Existing Pilot and Production routes, obligations, and admission behavior remain byte-equivalent or are rejected by deterministic contract tests.

## Route-back conditions

Return `change` to planning if the time budget cannot fail closed without killing an active tool call or losing evidence, if removing fresh validation or review violates a repository-owned safety boundary, if the POC needs Pilot or Production scope to meet the target, or if a provider prerequisite still needs Captain action after admission.

## Measurement

Record admitted-task creation time, durable `poc_outcome` time, decision-ready elapsed time, Captain interventions before that outcome, Captain wait, terminal cleanup, exact implementation revision, retained mechanisms, focused falsifier results, and cleanup status. The accepted dogfood requires decision-ready elapsed time at or below 15 minutes and zero post-admission Captain interventions before the durable outcome.
