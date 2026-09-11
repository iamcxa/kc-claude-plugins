---
title: Prove one journey-board to development handoff
status: validation
product: kc-journey-map
sprint: journey-planning-proof
sprint-readiness: ready
started: 2026-09-11T04:57:31Z
completed:
verdict:
worktree: .worktrees/spacedock-ensign-prove-journey-release-handoff
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
                state: consumed
        - id: gate:ndmwj51qjzktmqsxtzv3etr7:validation
          stage: validation
          attempts:
            - id: gate-attempt:ndmwj51qjzktmqsxtzv3etr7-validation-1
              briefing:
                id: briefing:ndmwj51qjzktmqsxtzv3etr7:validation:attempt-1:revision-1
                digest: sha256:c1a958e761bf433619ea0b53d1d738eb05dc4a9d98e951e8c0f39d51022935c7
                room-ref: ./review/validation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:ndmwj51qjzktmqsxtzv3etr7:validation:1
                briefing: briefing:ndmwj51qjzktmqsxtzv3etr7:validation:attempt-1:revision-1
                by: person:captain
                at: "2026-09-11T05:11:03.067959Z"
                decision: approve
                reason: 'Captain approved the presented change outcome and scoped disposable experiment cleanup in current chat: 核准，所以下一步是什麼？ Bound review c1a958e761bf. No Pilot admission or product release is included.'
              application:
                target-stage: done
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

### Feedback Cycles

#### Admission routing blocker — First Officer

The Captain-authorized backlog gate was recorded and consumed durably. Native Spacedock selected `target-stage=ideation`, while the selected v3 POC route and repository Local Profile require backlog directly to implementation. The current installed 4.3.0 profile loader refused before creating a stage pin or dispatch envelope:

```text
profile contract: workflow stage 'ideation' is outside poc-exploration; expected: implementation, validation
```

No worker was dispatched; no integrated product journey, timing comparison or handoff proof occurred. Do not report this as a completed or failed product experiment. Existing backlog approval is consumed; do not replay it. The recorded state is ideation and is held from dispatch because it has no POC working contract.

Smallest proposed recovery: Captain explicitly authorizes a one-task status correction to implementation in accordance with the already selected POC route, then the First Officer writes and commits the installed 4.3.0 implementation pin and performs normal stamped dispatch. This leaves the shared workflow graph and product contracts unchanged. Generic FO gate rules forbid silently using a status setter to advance a gate, so the exception must be explicit. No permanent route fix or chooser/kernel principle is claimed proven.


## POC outcome

```yaml
poc_outcome:
  direction: change
  admitted_at: 2026-09-11T04:57:31Z
  decision_ready_at: 2026-09-11T05:04:40Z
  decision_ready_elapsed_seconds: 429
  captain_interventions_before_decision_ready: 1
  evidence: evidence/consumer-result.json, evidence/control-observation.json, evidence/board-result.json; actual clean-context shaping, missing-decision refusal, and local board generation observed.
  strongest_limit: Source already contained a complete brief; board-to-brief value elicitation and comparative speed remain unproved; original admission-to-decision was 1163 seconds with one extra Captain intervention.
  reversal_fact: A bounded run from accepted board decisions without a prewritten complete brief produces the handoff and independent necessary-work shaping within measured budget, with any real missing decision left to Captain.
  cleanup_status_at_decision: pending
```

## POC close measurement

```yaml
poc_close_measurement:
  captain_wait_seconds: pending
  terminal_cleanup_seconds: pending
  cleanup_status: pending
```

## Execution measurement and boundaries

Original admission remains 2026-09-11T04:45:17Z; working started remains 2026-09-11T04:57:31Z. The installed close guard requires `admitted_at` to equal frontmatter `started`, so its 429-second measurement is the working interval; the separately preserved total is 1163 seconds, including 734 seconds of routing/setup overhead. One extra Captain intervention authorized the one-task routing correction and resumed functional experiment; it is not zero-overhead success.

Two workers total performed one control and one happy handoff. The actual consumer needed zero repeated value questions; the control surfaced one missing endpoint decision and supplied no answer. Model token/dollar cost is unmeasured; no paid external provider call, product PR, CI run or retained product edit occurred. CI cost per PR is unmeasured. Full costs and timestamps: [measurements](evidence/measurements.json).

Disposable artifacts are at `/Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1/.worktrees/spacedock-ensign-prove-journey-release-handoff/.context/journey-handoff-poc`; `node <that-directory>/render-board.mjs` reproduces the 45 records with the declared local dependencies. Remove that directory after outcome approval and durable evidence acceptance; approval wait and cleanup remain pending. No source, version, CI, provider or PR changes were retained.

## Stage Report: implementation

- DONE: Exercise the selected release planning handoff using a disposable board and Development Brief grounded in accepted source decisions.
  [Source revision](evidence/source-revision.json), [brief](evidence/development-brief.md), [board result](evidence/board-result.json): local generator emitted 45 records and six-of-six activity coverage. No live host selection/rendering was exercised.
- DONE: Demonstrate a clean-context dev consumer and one missing-decision control without invented tasks or repeated settled questions.
  [Actual consumer](evidence/consumer-result.json) consumed brief SHA-256 c502adc10ec7f502f6ab54ab0f87a24c42ed847f3ede5f60339697fe00576eaa and shaped necessary work with zero extra value questions; [control](evidence/control-observation.json) asked only the absent release endpoint and withheld dependent implementation. Removing that endpoint caused the observed refusal; restoring it allowed shaping.
- DONE: Record measured costs, limitations, a truthful POC outcome, and a minimal chooser/kernel recommendation without retained product edits.
  [Measurements](evidence/measurements.json), [limitations](evidence/limitations.md), [policy comparison](evidence/policy-comparison.md): direction change, one extra Captain intervention, 1163-second full interval, no comparative speed evidence, no chooser/kernel edit recommended.

Read-only installed `poc-close-guard.py review` passed: direct implementation proof, three evidenced obligations, direction change, and pending close measurements. No gate prepare or terminal mutation was performed.

### Summary

The local source/brief-to-consumer seam and missing-decision control worked; an actual consumer proposed one dependency sequence and one shared integration task with multiple textual story origins, preserving unknown facts and all admission/profile authority. The accepted source was already a complete brief and the board was generated alongside it, so the full board-to-brief value-elicitation claim remains unproved; next proof should begin with accepted board decisions that have no prewritten brief. This direct disposable POC returns change for outcome approval, with cleanup pending and no automatic delivery commitment.
