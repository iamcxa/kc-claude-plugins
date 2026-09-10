---
title: "Pilot: one evidence-complete manual dev-flow improvement cycle"
status: backlog
product: kc-dev-flow
sprint: S8
sprint-readiness: ready
id: 3w83fmy975y617nrfhcy1mqq
gates:
    version: 1
    records:
        - id: gate:3w83fmy975y617nrfhcy1mqq:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:3w83fmy975y617nrfhcy1mqq-backlog-1
              briefing:
                id: briefing:3w83fmy975y617nrfhcy1mqq:backlog:attempt-1:revision-1
                digest: sha256:f4e4d284e5d60d57ff73cc00fdeaadeeb300eacee90a058825a018485ff7f528
                room-ref: ./review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:3w83fmy975y617nrfhcy1mqq:backlog:1
                briefing: briefing:3w83fmy975y617nrfhcy1mqq:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-10T16:10:48.218365Z"
                decision: approve
                reason: Kent approved the proposed bounded manual Pilot with 同意 and resumed it with 繼續，額度回來了. Admit shaping of the recorded scope; no recurring activation, new cloud execution, product commit, merge or release authority is inferred.
              application:
                target-stage: ideation
                state: pending
---

# One manually triggered dev-flow improvement cycle

Kent accepted the proposed Pilot with “同意” after the 2026-09-10 experiment debrief: repair the knowledge-only close gap, complete the original archive, then run one manually triggered improvement cycle with complete test evidence and token accounting. This standalone Development Brief records that scope and profile; S8 is execution grouping only, with no provider planning receipt. Automatic scheduling remains a later decision.

## Problem

The initial event-query cloud experiment produced one merged repair (#412), but individual raw test results and whole-cycle actor usage were incomplete. Actual knowledge-only terminalization remains blocked: the mod documents a reason sentinel while Spacedock 0.27.2 accepts a real local-merge hash. The existing `knowledge-output-cannot-terminalize` task owns that defect; do not file a duplicate. A recurring loop would currently repeat these evidence and completion gaps.

## Accepted outcome

A bounded, manually triggered improvement cycle can select one eligible finding, preserve reproducible failure evidence, produce and independently verify a focused repair, and reach an honest close with complete evidence and measured usage. The original experiment's already-approved archive is a prerequisite to live replay. The shape stage first proves or names the exact knowledge-only closure dependency, checks existing fixes, and proposes the smallest reviewable implementation and execution budget.

## Non-goals

No recurring or unattended Routine activation, automatic merge or release, whole-profile coverage claim, new paid provider arrangement, automatic external issue/review posting, production data, destructive cleanup, replacement workflow engine, fabricated usage or delivery proof, or duplicated knowledge-terminalization repair task. This admission authorizes shaping and local proof preparation; a new cloud/model execution waits for its concrete budget and launch configuration. Product commits require Kent's confirmation of exact files. Existing state-tracking commits and original archive approval remain authorized.

## Acceptance criteria

- **AC-1** One manually triggered execution selects one eligible PR feedback item first, otherwise one eligible issue/finding, with a stable deduplication identity and explicit stop/retry limits; duplicate input does not start duplicate work.
- **AC-2** The selected case has retained raw stdout, stderr, exit status and exact code/runtime provenance; a same-case before/after retest and a negative control distinguish an actual repair from a misleading success summary.
- **AC-3** Every participating actor has an explicit usage boundary covering input, cached input, output and reasoning where available; missing fields remain unknown, subsets are not double-counted, and quality outcomes accompany any cost comparison.
- **AC-4** A fresh reviewer evaluates the exact candidate and retained evidence; a known failing control cannot be reported ready. External review publication and merge remain human-authorized.
- **AC-5** The original experiment and the Pilot's selected delivery route reach a legitimate native terminal/archive path, with consumed approval, evidence retained, actual cleanup measurement and successful final check; no forced state or invented merge sentinel is accepted.

## Route-back conditions

Return a concrete scope delta if closure requires changing upstream Spacedock authority, consumer migration, replacing the state engine, paid execution beyond an approved budget, unattended operation, expanded permissions, or a new production commitment. Preserve pending original approval and existing evidence. Unavailable usage or provider evidence is a limitation, not a zero or pass.

## Dependency and next proof

`knowledge-output-cannot-terminalize` is the existing defect owner. Establish live upstream status before implementing a second local workaround. The first shape output must explain the true terminal consumer and demonstrate its riskiest path in a disposable local fixture or explicitly report it blocked. Do not run another cloud baseline merely to rediscover the close defect.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: pilot-product-slice
  recommended: pilot-product-slice
  basis: Retained tooling and evidence for Kent's limited manual improvement runs, with human-owned external mutations and no unattended service commitment.
  route: [shape, build, verify-deliver]
  obligations:
    architecture: [Keep native state and approval authority, reuse the existing finding owner and queue]
    implementation: [Bound one manual cycle and preserve raw evidence and actor usage]
    testing: [Exercise same-case failure and repair plus negative controls and real terminalization]
  scope_boundary: One manual improvement cycle; recurring operation, release, production use and broad profile coverage excluded.
  semantics_unchanged: false
  promote_when: [Unattended recurring operation, consumer migration, production support or rollback duty]
  decision:
    authority: Kent, current conversation approval of the proposed Pilot
    at: 2026-09-10T16:04:06.089743+00:00
```
