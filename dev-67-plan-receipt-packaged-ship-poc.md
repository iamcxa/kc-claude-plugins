---
title: "POC: plan receipt in, packaged ship out — one Project, three dependent Issues, one UAT document"
status: implementation
source:
product: kc-dev-flow
planning-window:
planning-outcome:
sprint: S9
sprint-readiness: ready
started: 2026-09-02T16:30:00Z
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
                state: consumed
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

Plan side: lint plus receipt plus a deliberately broken fixture, 2.1 min. Ship side, three layers: DEV-66 dispatch to accepted 43.6 min (two rounds), DEV-65 19.8 min from evidence to accepted (two rounds; a 7-hour FO idle gap sits between dispatch and first evidence and is excluded), DEV-64 15 min evidence to accepted (one round). Active ship time about 104 min against a 60-minute limit. Worker cost not summed (transcripts read through SQL, which carries no cost field).

## POC outcome

```yaml
poc_outcome:
  direction: change
  admitted_at: 2026-09-02T16:30:00Z
  decision_ready_at: 2026-09-03T01:36:30Z
  decision_ready_elapsed_seconds: 32790
  captain_interventions_before_decision_ready: 0
  plan_direction: proceed
  ship_direction: change
  evidence: >-
    Plan: eight lint rules ran on the live Project, emitted one receipt
    (evidence/plan-receipt.json, sha256 08c6798b), and the same lint refused a
    deliberately broken Project on four rules (multi-line User value, no cycle,
    empty Non-goals, vague AC); ship-flow dispatched all three Issues from the
    receipt alone without reading Linear. Ship: three cloud workers dispatched
    in receipt order, each layer on the previous layer's candidate; each
    candidate pinned (remote head == CANDIDATE_SHA), the worker's without-it
    line run verbatim with credentials stripped (retained 0, removed 1), the
    contract test green, merge-tree preflight clean against main 56e3095d; one
    package UAT document produced (evidence/uat.md); Codex review of each diff
    found P1s the mechanical checks could not, two fix rounds closed them
    within the cap of 2. No station needed a new mechanism.
  strongest_limit: >-
    Ship direction is change because thirteen glue defects were recorded
    (evidence/ship-defects.txt); the load-bearing ones are S10 (a fix round on
    layer N after layer N+1 was dispatched breaks the stack base: DEV-64 sits
    on DEV-65's round-0 candidate, not its accepted one), S4 (three contract
    runs in one call exceed the tool budget), S1 (a task sent before the
    workspace is ready is silently dropped), and S8/S13 (evidence block
    location must anchor on CANDIDATE_SHA, not on fences or headings). The
    60-minute limit was exceeded; most of the overrun is fix rounds and reader
    bugs, not worker time.
  reversal_fact: >-
    A repeat where a lint rule cannot be made to fail, the receipt lacks a
    field dispatch needs, a candidate head moves during verification, or the
    stack base rule cannot be enforced by freezing lower layers.
  cleanup_status_at_decision: pending
```

## POC close measurement

```yaml
poc_close_measurement:
  captain_wait_seconds: 0
  terminal_cleanup_seconds: 0
  cleanup_status: not-applicable
```

## Change returned to planning

1. Freeze a layer's candidate once a higher layer is dispatched on it; a lower-layer fix re-dispatches every higher layer (S10). Until then, stacks of depth greater than two must not run fix rounds on lower layers.
2. Verify steps run as separate invocations with their own timeouts; receipts are written after each step (S4).
3. Send the task only after workspace status is ready and session status is idle, then wait a grace period (S1).
4. Locate the Evidence block by `CANDIDATE_SHA: <40hex>` following `## Evidence`, never by fences or the heading alone (S8, S13); write evidence files from python, never shell heredocs (S12).
5. Pin on the receipt's exact Linear branchName; Linear truncates generated names (S11).
6. A no-secrets sandbox strips credential variables and keeps HOME (S3).
7. Code review (Codex or kc-pr-review) is load-bearing for script-producing Issues; findings outside the Brief's ACs are dispositioned as scope-outside-brief and listed for the Captain, not looped (S5, S6).
8. Conductor MCP has run_sql but no wait primitive and dropped mid-session; the CLI sql path is the contract (S7).
9. Plan-flow lint set: keep the eight rules; the relation direction must be read from inverseRelations (blocker -> blocked); L7 stays a warning.
