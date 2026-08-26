---
title: Make Production recovery proportional
status: backlog
source: "Captain-approved kc-dev-flow/S5 design: known Production repairs should retain exact proof without repeating resolved shape work"
product: kc-dev-flow
sprint: S5
sprint-readiness: ready
started:
completed:
verdict:
worktree:
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
