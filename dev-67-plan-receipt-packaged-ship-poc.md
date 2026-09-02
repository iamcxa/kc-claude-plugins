---
title: "POC: plan receipt in, packaged ship out — one Project, three dependent Issues, one UAT document"
status: backlog
source:
product: kc-dev-flow
planning-window:
planning-outcome:
sprint: S9
sprint-readiness: ready
started:
completed:
verdict:
worktree:
issue: DEV-67
pr:
mod-block:
id: t5nxcbfq1ynpff13kh3sdnga
gates:
    version: 1
    records:
        - id: gate:t5nxcbfq1ynpff13kh3sdnga:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:t5nxcbfq1ynpff13kh3sdnga-backlog-1
              briefing:
                id: briefing:t5nxcbfq1ynpff13kh3sdnga:backlog:attempt-1:revision-1
                digest: sha256:faa74ff5ea2a9d60326880ac55f147251b405fd8a7993666480d429f86457d25
                room-ref: ./dev-67-plan-receipt-packaged-ship-poc/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:t5nxcbfq1ynpff13kh3sdnga:backlog:1
                briefing: briefing:t5nxcbfq1ynpff13kh3sdnga:backlog:attempt-1:revision-1
                by: agent:first-officer
                at: "2026-09-02T16:34:33.791896Z"
                decision: approve
                reason: Captain admitted DEV-67 as a standalone poc-exploration item in sprint S9; POC route build -> prove; 60-minute limit carries its reason.
                conn:
                    quote: 如果沒其他問題要討論可以先做 PoC
                    source: Captain chat, this conversation, 2026-09-03, after confirming the two-question POC scope and plan-flow backlog
              application:
                target-stage: ideation
                state: pending
---

## The problem

DEV-62 proved the ship-flow glue for one Issue but not for a package: nothing has yet taken one Project through plan-side lint to a plan receipt, then dispatched two or more dependent Issues in dependency order to cloud workers, verified each at a pinned SHA, and handed the Captain one UAT document for the whole package. Both halves are designed (2026-09-02, two Codex reviews) and neither has run.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: poc-exploration
  recommended: poc-exploration
  route: [build, prove]
  basis: One disposable run on a real three-Issue Project proves whether the plan receipt and the packaged ship line connect with existing components; no production state, provider write beyond the fixture, compatibility promise, or continuing operation.
  poc_decision: Plan side — does one plan receipt carry everything ship-flow needs to dispatch without re-reading Linear? Ship side — do dependency-ordered dispatch, per-layer pinned verification, per-Issue Captain-approved delivery units, and one package UAT document connect as glue?
  poc_falsifier: Plan — the receipt lacks a field ship needs, or a lint rule cannot be made to fail on a deliberately broken Project. Ship — any station needs a new mechanism rather than glue. Each side records stop independently.
  poc_budget: Three cloud workspaces, three Issues (DEV-64, DEV-65, DEV-66), four First Officer hours, no merge
  poc_stop_when: Either falsifier hits, or all three delivery units are Captain-approved and the package UAT document exists, whichever first
  poc_artifact: disposable
  poc_safety_boundary: none
  poc_decision_ready_minutes: 60
  poc_decision_ready_reason: Three sequential cloud dispatches of roughly 15 minutes each, measured on DEV-62, cannot fit one 15-minute window; the limit is the sum, not a relaxation.
```

## Accepted outcome


Two questions, one run, on the real Project "Ship-flow glue closes its four POC defects" (DEV-64 -> DEV-65 -> DEV-66, Cycle 2). Plan side: the eight lint rules (one-line User value, one Cycle, milestone membership, per-Issue admission through the guard's own parsers, Initiative when more than one Project, blockedBy is a DAG, split advisory, e2e-able AC) run against the live Project and emit one plan receipt whose contents let ship-flow dispatch every Issue without reading Linear again. Ship side: reading only that receipt, the First Officer dispatches the three Issues in receipt order with each layer waiting for the previous layer's CANDIDATE_SHA, verifies each candidate with the DEV-62 acceptance steps, presents one delivery unit per Issue for Captain approval, and produces one UAT document for the package. Two directions are recorded separately.

Falsifier and stop, plan side: the receipt lacks a field ship-flow needs and the First Officer has to read Linear to dispatch, or a lint rule cannot be stated as a check that fails on a deliberately broken Project. Ship side: any station (dependency-ordered dispatch, parallel-safe claims, per-layer pin, package UAT document) needs a new mechanism rather than glue over existing components. Either falsifier records stop for that side only.

## Non-goals

* No dialectic stage: the delivery was hand-written; office-hours, PM skills, and the Linear-method reasoning are the next plan-flow POC.
* No workflow commission, no new plugin, no kernel change; every rule stays a script or a README sentence.
* No Linear write by the First Officer during the run beyond this Brief and the fixture already created; the worker has no Linear access.
* No merge; each Draft PR stays draft for Captain UAT.
* No Milestones on the fixture Project; the implicit single-milestone path is the one under test.

## Acceptance evidence


* **AC-1 **`poc_outcome` records two directions, `plan` and `ship`, each `proceed`, `change`, or `stop`, with the station reached and minutes per station.
* **AC-2** The plan receipt is recorded with its sha256, the eight lint results, and one deliberately broken variant of the Project (a non-DAG relation or a missing Non-goals bullet) that the lint refused; the refusal is recorded.
* **AC-3** For each of the three Issues: the worker Evidence block, CANDIDATE_SHA equal to the verified remote head, the without-it command run twice, and the base SHA the layer was dispatched on; layer N+1's base equals layer N's candidate.
* **AC-4** One UAT document for the package listing each Draft PR, its evidence, and how the Captain verifies it, plus the list of stuck or drifted Issues if any.
* **AC-5** Cleanup recorded: workspaces archived, carrier branches deleted, Draft PRs and candidate branches kept for Captain UAT.

## Route-back conditions

The accepted outcome or non-goals changed. Stop and return a structured planning delta that names the changed premise, affected acceptance evidence, and recommended change or stop.
## Measurement

Not yet measured. Build records per-station minutes for plan and ship separately, and the falsifier station if any.
