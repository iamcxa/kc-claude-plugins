---
title: Prove one journey-board to development handoff
status: backlog
product: kc-journey-map
sprint: journey-planning-proof
sprint-readiness: ready
started:
completed:
verdict:
worktree:
pr:
mod-block:
id: ndmwj51qjzktmqsxtzv3etr7
gates:
    version: 1
    records:
        - id: gate:ndmwj51qjzktmqsxtzv3etr7:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:ndmwj51qjzktmqsxtzv3etr7-backlog-1
              briefing:
                id: briefing:ndmwj51qjzktmqsxtzv3etr7:backlog:attempt-1:revision-1
                digest: sha256:f687c5ddd99ae51a6ebd3539a8752fc2e0403c4cdaa560f96de925f30e3d4b4a
                room-ref: ./review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:ndmwj51qjzktmqsxtzv3etr7:backlog:1
                briefing: briefing:ndmwj51qjzktmqsxtzv3etr7:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-11T04:45:17.378668Z"
                decision: approve
                reason: 'Captain explicitly selected this complete-flow POC in current chat: 就先做這個完整流程的 poc. Scope is the preceding agreed planning-to-dev handoff; this is execution admission, not terminal acceptance.'
              application:
                target-stage: ideation
                state: pending
---

## Exploration Brief

Prove the proposed planning-to-development plugin interaction before committing to its implementation. Use the Captain-approved intent in the sibling plan-release-from-journey-board task as the real release input, explicitly deriving a disposable board from that intent. Existing journey.example.yaml is historical example material, not live planning authority. Preserve all existing delivery tasks and PRs.

One real journey: existing decisions -> selected release board -> relevant uncertainty triage -> Development Brief -> clean-context development consumer. Reuse the Captain's already recorded decisions; do not fabricate a new answer. An unanswered decision that changes scope must stop the dependent path. A bounded control removes one necessary decision and must surface exactly that question rather than inventing work.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: poc-exploration
  recommended: poc-exploration
  basis: A local disposable workflow experiment for the Captain, with no product or provider mutation and no downstream delivery commitment.
  route: [build, prove]
  obligations:
    architecture: [Reuse existing board and brief contracts]
    implementation: [Exercise a real producer-to-consumer handoff]
    testing: [Run one happy path and one missing-decision control]
  scope_boundary: Disposable experiment and evidence only; no retained product changes, new framework, CI, provider writes, task auto-admission, or automatic Pilot selection.
  poc_decision: Decide whether to implement adaptive journey planning and a single development handoff, and whether evidence justifies adding a decomposition principle to profile selection and kernel.
  poc_falsifier: A clean-context dev consumer needs to repeat settled value questions, mistakes unknown evidence for missing implementation, or cannot shape necessary work from the brief without reconstructing the conversation.
  poc_budget: At most 15 minutes from admission to decision-ready, two workers total with zero tolerance, one happy-path handoff and one missing-decision control, no paid external provider or new review loop.
  poc_stop_when: Record proceed or change after the handoff and control, or stop product proof on budget exhaustion, required Captain intervention, or a contract blocker.
  poc_artifact: disposable
  poc_safety_boundary: none
  poc_decision_ready_minutes: 15
  promote_when: [The Captain independently accepts a Development Brief for retained plugin behavior]
  decision:
    authority: captain Kent; current chat explicitly selected this complete-flow POC
    at: 2026-09-11T04:44:38.803060+00:00
```

## Evidence and boundaries

Record timestamps for setup, producer, handoff and consumer; count repeated questions, necessary new decisions and rework. Report speed as unproven without a comparable baseline. Do not confuse an expected human choice in the planned product with a fabricated experiment answer; the current POC contract counts any pre-decision Captain intervention as change.

The producer's disposable board and brief must cite the accepted source and stable release/story references, preserve unverified versus gap, and keep shared integration tasks honest. The consumer receives only the brief and cited factual sources, not this conversation or the producer's expected answer. Its output is an actual technical shaping proposal, not a self-review or authorization to execute tasks. Use existing local admission validation where applicable without selecting a delivery profile on the Captain's behalf.

Compare the existing choose-work-profile and kernel wording against the result. Recommend the smallest nonduplicative principle only if earned: decompose independent uncertainties when this lowers proof cost, and prove one integrated journey before retaining implementation; never mandate multiple POCs followed by Pilot. Product wording remains a separately reviewable follow-up unless this experiment supplies sufficient evidence and a selected retained-work profile.

## Authorization

Captain: "如果這樣會更快，也應該納入 profile chosen skill / kernel 作為原則之一。就先做這個完整流程的 poc". This authorizes the bounded experiment, not terminal acceptance or automatic Pilot promotion.
