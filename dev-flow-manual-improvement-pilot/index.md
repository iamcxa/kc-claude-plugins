---
title: "Pilot: one evidence-complete manual dev-flow improvement cycle"
status: implementation
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
                state: consumed
        - id: gate:3w83fmy975y617nrfhcy1mqq:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:3w83fmy975y617nrfhcy1mqq-ideation-1
              briefing:
                id: briefing:3w83fmy975y617nrfhcy1mqq:ideation:attempt-1:revision-1
                digest: sha256:ef2a004507cdb9033f64aca96dd1e608cd93ff4212c29a3333963722d547dede
                room-ref: ./review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:3w83fmy975y617nrfhcy1mqq:ideation:1
                briefing: briefing:3w83fmy975y617nrfhcy1mqq:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-09-10T16:23:46.069557Z"
                decision: approve
                reason: Kent explicitly approved the presented ef2a0045 Pilot design and upstream knowledge-only closure scope with 批准. Implement the existing defect owner first, preserving native approval/evidence and product delivery refusal. Original POC close approval remains valid; no product commit, cloud launch, external post, merge or release authorization is inferred.
              application:
                target-stage: implementation
                state: consumed
started: 2026-09-10T16:11:49Z
worktree: .worktrees/spacedock-ensign-dev-flow-manual-improvement-pilot
---

# One manually triggered local dev-flow improvement cycle

Kent confirmed the controlled local-only route with 「確認」 after directing 「不要去動 ＳD 上游」. Select one existing kc-dev-flow case, retain raw before/after and negative-control evidence, obtain fresh independent review, record per-actor usage with unknowns preserved, and report the result. This standalone Development Brief remains Pilot; S8 is execution grouping only, with no provider planning receipt or recurring activation.

## Problem

The initial event-query experiment produced a repair, but raw case evidence and whole-cycle actor usage were incomplete. One controlled local case can test whether the improvement process produces reproducible repair evidence and an honest report. Original/native knowledge closure remains incomplete and is not a prerequisite for this local replay; the stopped upstream repair is not part of the current plan.

## Accepted outcome

One manually triggered execution selects an eligible PR feedback item first, otherwise an eligible issue/finding, reproduces it locally, makes the smallest selected repair, and retains same-case before/after results plus a meaningful negative control and fresh independent review. Report the observed outcome and each actor's available usage without claiming complete cost when measurements are missing. The original experiment's native terminalization/archive, cleanup and final check remain explicitly incomplete and separately owned; this Pilot does not fabricate or require their completion before local replay.

## Non-goals

No Spacedock upstream work or consumer migration dependency. Do not read or write the stopped upstream/product repair worktrees. No recurring or unattended activation, new workflow engine, whole-profile coverage, production data, paid runtime launch, cloud execution, separate provider/model call, product push/PR creation, external review publication, merge, installation, live original cleanup or forced terminalization. Existing-session host workers perform the controlled local execution; unavailable usage stays unknown and forbids complete-cost claims. Product commits require Kent's confirmation of the exact selected files. State-tracking commits remain authorized.

## Acceptance criteria

- **AC-1** One manual execution selects one eligible PR feedback item first, otherwise one eligible issue/finding, with stable deduplication identity and explicit stop/retry limits; duplicate input does not start duplicate work.
- **AC-2** Retain raw stdout, stderr, exit status and exact code/runtime provenance for the selected case; same-case before/after retest and a meaningful negative control distinguish repair from a misleading success summary.
- **AC-3** Record every participating actor's usage boundary for input, cached input, output and reasoning where available. Missing fields remain unknown; do not double-count subsets or claim complete cost. Quality outcomes accompany any measured comparison. Existing-session host workers only; no paid new runtime launch or separate provider call.
- **AC-4** A fresh independent reviewer evaluates the exact selected candidate and retained evidence; a known failing control cannot be reported ready. Product commit requires exact-file confirmation; push, PR/review publication, merge and installation remain outside this authorization.
- **AC-5** Retain a factual local report and raw evidence stating the observed result and limitations. Explicitly record that original/native knowledge terminalization, archive, cleanup and final check remain incomplete. Do not manufacture completion, consume an old approval, force state or invent a merge sentinel.

## Route-back conditions

Stop and return a concrete scope delta if the selected repair needs more than two product files or 150 added-plus-deleted lines, another case, stopped upstream/product-root access, consumer migration, a new paid runtime, separate provider/cloud execution, broader permissions or recurring operation. Preserve pending original approvals and existing evidence. Missing usage or native closure evidence is a reported limitation, never a zero, pass or reason to reopen stopped upstream work.

## Current local plan and limits

The First Officer checks the existing input queue: eligible PR feedback first, otherwise one eligible issue/finding, with no duplicate owner. Select one existing kc-dev-flow case and bind its product root, exact baseline, failure, negative control, participating existing-session workers, usage fields and stop/retry limits before local execution. The selected repair is limited to two product files and 150 gross added-plus-deleted lines; tests count. No product commit until Kent confirms exact files. No upstream repair, consumer migration, installation or original archive prerequisite is part of this plan.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: pilot-product-slice
  recommended: pilot-product-slice
  basis: One Captain-confirmed local case with raw repair evidence and honest actor usage, using existing-session workers only.
  route: [shape, build, verify-deliver]
  obligations:
    architecture: [Keep native state and approval authority, reuse one existing finding owner and queue, leave original native closure explicitly incomplete]
    implementation: [Bound one manual local case to two product files and 150 gross lines, preserve raw evidence and actor usage unknowns, exclude stopped upstream and product repair worktrees]
    testing: [Exercise same-case before and after plus a meaningful negative control, obtain fresh independent review, retain a factual report without claiming native closure or complete cost]
  scope_boundary: One manual local case using existing-session host workers; no paid new runtime, separate provider or cloud call, recurring operation, product commit without exact-file confirmation, external delivery, installation or original cleanup.
  semantics_unchanged: false
  promote_when: [Unattended recurring operation, new paid runtime, expanded production or delivery obligations]
  decision:
    authority: Kent, current conversation confirmation of the local-only Pilot proposal
    at: 2026-09-11T07:39:22.469305+00:00
```

## Captain scope amendment — current local-only route

After Kent instructed 「不要去動 ＳD 上游」, the First Officer proposed a controlled local improvement loop: one existing kc-dev-flow case, raw before/after and a negative control, independent review, per-actor usage preserving unknowns, then a factual report; original/native knowledge closure stays explicitly incomplete and no recurring activation follows. Kent replied exactly 「確認」. This records that existing Captain authority; it is not a request for another approval.

The prior active scope required an upstream knowledge-close repair and original archive before replay. It is superseded by the local-only scope above. [Complete pre-amendment task bytes](scope-history/2026-09-11-before-local-only-amendment.md) preserve the original brief, receipt, frontmatter and historical reports. Existing Stage Reports below, stage pins, gates, frozen Briefing and approval history remain unchanged. Their old dependency and closure claims are historical, not the current plan. This amendment does not advance task state, rewrite a pin, consume the old pending approval or claim implementation completed.

## Stage Report: ideation

- DONE: 1. Determine the legitimate knowledge-only terminalization dependency from live upstream evidence and a bounded local falsifier; preserve existing approval.
   AC-5: dispatch-pinned upstream check plus `shape-evidence/native-probe.py` / `native-probe.json` prove blocked accepted knowledge; rejected syntax succeeds only by changing meaning. Positive path DESIGNED, original approval untouched.
- DONE: 2. Shape one manual improvement journey with raw case evidence, per-actor usage, duplicate handling and independent same-case/negative-control verification.
   AC-1, AC-2, AC-3, AC-4: `shape-evidence/shape.md` journey steps 2–7 and acceptance table bind each consumer, artifact, failure and recovery path; implementation acceptance remains pending.
- DONE: 3. Provide the smallest file-level implementation plan, limits, execution budget and exact Captain decision needed; cite AC-1 through AC-5 without claiming designed behavior already passes.
   `shape-evidence/shape.md` contains file counts, delivery bases, diff stop numbers, bounded local-only execution proposal and upstream scope delta; no launch/product mutation performed.
- SKIPPED: 4. Implement the selected repair, run live replay, publish review, or terminalize either real task.
   Shape-only authorization; AC-1–AC-4 positive execution and AC-5 legitimate closure/cleanup/final-check are not yet accepted.

### Summary

Completed the bounded Pilot shape and retained a runnable native refusal probe with raw results. The recommended route reuses local tools and existing state ownership; upstream knowledge-delivery authority is the blocking dependency, and the next decision is its explicit scope delta. No positive implementation, independent cloud result, complete cost comparison, or terminal completion is claimed.


## Stage Report: ideation (cycle 2)

- DONE: Select one eligible local case after PR-feedback-first queue disposition, within the current Captain-confirmed Pilot scope.
  AC-1: selected Go `_test.go` default-exclusion defect with one stable finding identity. FO reports three PRs without actionable review feedback and four issue dispositions; raw PR JSON is unavailable, so this is attributed evidence. [Current shape](shape-evidence/local-go-test-exclusion/current-shape.md).
- DONE: Retain exact checker/contract provenance, observed raw baseline and the smallest falsifiable local repair plan.
  AC-2: fresh real-Git default check returned 1 instead of expected 0; `--no-exclude` returned intended 1. [Raw baseline](shape-evidence/local-go-test-exclusion/baseline.json). Exact main object 0ec3380f590cbaf5b01ee1c325eb222da99a3c5a; proposed files measured at 278 and 2,405 lines. Design estimate 67–119 gross, hard limit two files/150. Before/after, normal-Go enforcement, strict mode, explicit-map and defective-producer controls are designed; candidate proof is pending.
- DONE: Bound existing-session execution, actor usage, independent review and honest reporting without upstream/native closure dependencies.
  AC-3: usage windows unknown; FO's supplied cumulative observation is preserved without claiming Pilot totals or complete cost. AC-4: fresh exact-candidate reviewer planned. AC-5: original/native terminal/archive/cleanup/final check remain explicitly incomplete. FO reports old ideation approval was consumed natively after amendment; this worker changed no gates/frontmatter/pins, and a fresh implementation pin remains FO-owned.
- SKIPPED: Implement the selected repair, run candidate/negative-control verification, publish review, commit product files or terminalize a task.
  This assignment completes current ideation/report preparation only. No stopped upstream/product repair worktree, paid runtime, provider, cloud or product mutation was used.

### Summary

One bounded local case is ready for implementation dispatch under the confirmed local-only scope. Its real baseline defect and strict-mode refusal are observed; the two-file correction, same-case after-results, negative control and independent review remain pending. Historical shape/report/approval bytes are preserved, and no original closure or complete-cost claim is made.
