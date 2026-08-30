---
id: direct-poc-cycle-2
title: Direct POC proof dogfood cycle 2
status: implementation
sprint: dogfood/decision-ready
sprint-readiness: ready
started: 2026-08-30T14:59:15Z
---

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: poc-exploration
  recommended: poc-exploration
  route: [build, prove]
  basis: Exercise the exact no-code direct path on the unchanged candidate revision.
  poc_decision: Does direct POC proof produce a durable decision without extra ceremony?
  poc_falsifier: The budget, observation, proof path, guard, or higher-profile contract differs from the approved direct path.
  poc_budget: One loader read and one exact read-only Git probe
  poc_stop_when: Stop after the first durable outcome
  poc_artifact: no-code
  poc_safety_boundary: none
```

## The problem

The direct path needs one measured shared-state-backed use on exact candidate
`2f3391855653889ede9ac205eaa4b7a88befff43`.

## POC outcome

```yaml
poc_outcome:
  direction: proceed
  admitted_at: 2026-08-30T14:59:15Z
  decision_ready_at: 2026-08-30T15:00:31Z
  decision_ready_elapsed_seconds: 76
  captain_interventions_before_decision_ready: 0
  evidence: Admission ba5124277d55801c0b5efb5d9c79ea0e339a1611 loaded budget 15, direct proof, and no implementation-exit observation at candidate 2f3391855653889ede9ac205eaa4b7a88befff43; exact tree a3de404c2b8fb21c9201e2e3d4312438c52e018d had no Pilot or Production profile-contract diff from base.
  strongest_limit: The dogfood exercises shared repository state and read-only probes, not a provider-backed planning admission.
  reversal_fact: A repeat emits fresh proof, a review request, a validation dispatch, elapsed time above 900 seconds, or a Pilot or Production contract diff.
  cleanup_status_at_decision: not-applicable
```

## No-RoboRev-request receipt

```yaml
no_roborev_request:
  requested: false
  request_count: 0
  candidate: 2f3391855653889ede9ac205eaa4b7a88befff43
  branch: spacedock-ensign/make-poc-decisions-ready-within-15-minutes
  before_admission_list_json: null
  after_probe_list_json: null
  after_probe_observed_at: 2026-08-30T15:00:31Z
  query: roborev list --json with the exact candidate repository and branch
  loader_observation_declared: false
```

## No-validation-dispatch receipt

```yaml
no_validation_dispatch:
  requested: false
  dispatch_count: 0
  selected_proof_path: direct
  loader_next_workflow_stage: validation
  validation_worker_dispatched: false
  state_evidence_path_count: 1
  state_evidence_paths: make-poc-decisions-ready-within-15-minutes/evidence/direct-poc-cycle-2.md
  query: git ls-tree on the admission commit under the durable evidence directory
```

## POC close measurement

```yaml
poc_close_measurement:
  captain_wait_seconds: 0
  terminal_cleanup_seconds: 0
  cleanup_status: not-applicable
```
