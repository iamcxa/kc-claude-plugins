---
title: "Inventory kc-dev-flow surfaces for removal candidates (POC)"
status: backlog
source: https://linear.app/duckbase-co/issue/DEV-52/inventory-kc-dev-flow-surfaces-for-removal-candidates-poc
product: kc-dev-flow
planning-window: Linear Cycle d1c96803-02fa-4323-b3a8-2fc44cc43699 2026-09-10T16:00:00.000Z/2026-09-24T16:00:00.000Z
planning-outcome: Linear Project 4746021d-2930-4589-80a0-b7b3d1d70eeb kc-dev-flow slimming dogfood sha256:0599c390742642a1edf03e07a50c28635ff41d3ef77188e076cb2f02e6d85372
sprint: S8
sprint-readiness: ready
started:
completed:
verdict:
worktree:
issue:
pr:
mod-block:
id: mbm3d94fcn4ks8vgf30rk2kh
gates:
    version: 1
    records:
        - id: gate:mbm3d94fcn4ks8vgf30rk2kh:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:mbm3d94fcn4ks8vgf30rk2kh-backlog-1
              briefing:
                id: briefing:mbm3d94fcn4ks8vgf30rk2kh:backlog:attempt-1:revision-1
                digest: sha256:af1786749b9f43b2294ed5edf930d882fc1ccf12bf05ec39309180b9d90258eb
                room-ref: ./dev-52-inventory-kc-dev-flow-removal-candidates/review/backlog/briefing-1
---

## The problem

kc-dev-flow has been slimmed twice (`7e8fa5e8` 2026-08-11, `4b3eaf73` 2026-08-31) by reading and judgement, without an inventory that classifies each surface on completeness and need with evidence. A slimming project needs its candidate list produced by `reverse-recovery-audit.md`'s two-axis procedure, so that each candidate carries two search strategies, a named boundary, and a disproof hook before the Captain sees it. Kernel plus profile contracts measure 31,782 bytes on 2026-09-02; references, skills, scripts, tests, and README sections are the surfaces.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: poc-exploration
  recommended: poc-exploration
  basis: A search-tier inventory whose output is a record, not code; the result decides whether the slimming project opens removal items this cycle, and a stop is a valid outcome.
  route: [build, prove]
  obligations:
    architecture: [Apply reverse-recovery-audit.md's two-axis classification to every kc-dev-flow surface with the search boundary named]
    implementation: [Record the reverse_recovery receipt in this work item only; edit no contract, skill, script, or test]
    testing: [Every NO_OBSERVED_CONSUMER entry carries two search strategies, the boundary where they stopped, and a runnable disproof_hook; DEV-51's duplicate-rule signal and its 23 wording-only rules are checked as candidates]
  scope_boundary: No removal, no edit to any contract or script, no aggregate size target, no change to the audit mod, no creation of removal items.
  poc_decision: Whether the slimming project opens bounded removal items this cycle or records stop.
  poc_falsifier: Fewer than five surfaces classify NO_OBSERVED_CONSUMER with two-strategy evidence, or the search boundary cannot be named for the majority of surfaces.
  poc_budget: One dispatch on sonnet, one reverse-recovery pass, no provider requests, no code edits.
  poc_stop_when: The reverse_recovery receipt lists every audited surface or names the stop boundary, and poc_outcome is recorded with the candidate count against the threshold of five.
  poc_artifact: no-code
  poc_safety_boundary: none
  poc_decision_ready_minutes: 15
  decision:
    authority: person:captain
    at: 2026-09-03T00:54:55Z
```

## Accepted outcome

One reverse-recovery audit over kc-dev-flow's surfaces (`kc-dev-flow/references/`, profile contracts, `skills/*/SKILL.md`, `scripts/`, tests, and the workflow README sections that describe them), every surface classified on completeness × need, every `NO_OBSERVED_CONSUMER` backed by two search strategies and the boundary where they stopped, every non-runtime claim carrying one `disproof_hook`, and a `decision: removal_candidate` list returned to the Captain. Decision-ready inside the recorded POC limit.

Falsifier and stop: if fewer than five surfaces classify `NO_OBSERVED_CONSUMER` with complete evidence, or the search boundary cannot be named for the majority of surfaces, record `poc_outcome: stop`; the slimming project does not proceed this cycle. Otherwise `proceed` with the candidate list.

## Non-goals

- Do not remove, rewrite, or edit any contract, skill, script, or test.
- Do not set or imply an aggregate size target.
- Do not change `reverse-recovery-audit.md` or its receipt shape.
- Do not preselect or create the removal items; `poc_outcome` returns to planning and the Captain admits each group.

## Acceptance criteria

- **AC-1** The `reverse_recovery` receipt lists every audited surface, or names the boundary at which the audit stopped and why.
- **AC-2** Every `NO_OBSERVED_CONSUMER` entry carries two named search strategies, the boundary where they stopped, and a `disproof_hook` a reader can run.
- **AC-3** `poc_outcome` is recorded as `proceed`, `stop`, or `change` with the candidate count against the threshold of five, the exact revision audited, and cleanup status.
- **AC-4** The exact diff at close touches only the work item; no other file changed.

## Route-back conditions

The accepted outcome or non-goals changed. Stop and return a structured planning delta that names the changed premise, affected acceptance evidence, and recommended change or stop.

## Measurement

Not yet measured. Build records the surface count, the NO_OBSERVED_CONSUMER count against the threshold of five, and decision-ready time against 15 minutes.
