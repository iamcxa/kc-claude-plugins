---
title: "Fixture: POC work item with a retained surface absent from the diff"
status: implementation
issue: FIXTURE-POC-NOT-IN-DIFF
sprint: S9
sprint-readiness: ready
---

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: poc-exploration
  route: [build, prove]
  poc_decision: proceed
  poc_falsifier: n/a
  poc_budget: n/a
  poc_stop_when: n/a
```

## POC outcome

```yaml
poc_outcome:
  direction: proceed
  evidence: n/a
  strongest_limit: n/a
  reversal_fact: n/a
  cleanup: n/a
  retained_surfaces: [scripts/ship-flow/does-not-exist-in-diff.py]
```
