---
title: "DEV-105: ship-flow e2e station: a passing CLI journey at the stacked head is the condition for UAT-ready"
status: implementation
source: https://linear.app/duckbase-co/issue/DEV-105/ship-flow-e2e-station-a-passing-cli-journey-at-the-stacked-head-is-the
product: kc-dev-flow
planning-window: Linear Cycle b788c52d-8370-475f-be4f-8fcd88dd03d6
planning-outcome: Linear Project 6072d592-8704-448b-bb8d-66471b0557f9 Ship-flow hands the Captain one UAT message instead of a chat to read
sprint: S10
sprint-readiness: ready
started:
completed:
verdict:
worktree:
issue: DEV-105
pr:
mod-block:
---

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: pilot-product-slice
  recommended: pilot-product-slice
  route: [shape, build, verify-deliver]
  basis: A product slice the First Officer runs on every batch from now on; consumer is the ship-flow FO; the Brief carries its own acceptance commands.
  semantics_unchanged: false
```

## The problem

DEV-94 AC-4 was relaxed on 2026-09-04 to three shapes: an e2e-flow recording where the Milestone names a journey, otherwise the `e2e-cli.sh` stdout log at the stacked head, otherwise `e2e: not applicable` with a reason. `scripts/ship-flow/e2e-cli.sh` exists and runs `Execute external` steps at a pinned SHA, but nothing selects the shape, runs it at the stacked head, or refuses to call a batch UAT-ready without one of the three.

## Accepted outcome

One script takes the batch's accepted candidates in dispatch order, computes the stacked head, picks the shape from the receipt (journey named or not, CLI flow present or not), runs `e2e-cli.sh` at that head when the CLI shape applies, and writes the artifact path or the `not applicable` reason into the batch record. UAT-ready is refused when none of the three is present.

## Non-goals

* No browser e2e in this item; the e2e-flow recording shape is recorded as delegated to e2e-pipeline.
* No change to `e2e-cli.sh` step semantics.
* No Linear write.

## Acceptance criteria

* **AC-1** With a fixture receipt naming a CLI flow, the script runs `e2e-cli.sh` at the stacked head and the stdout log path is recorded; exit 0 recorded.
* **AC-2** With a fixture receipt naming no journey and no CLI flow, the script records `e2e: not applicable` with the reason text; recorded.
* **AC-3** With no artifact and no reason, the script exits non-zero and the batch is not marked UAT-ready; recorded.
* **AC-4** `python3 scripts/kc-dev-flow-contract-test.py` exits 0 at the candidate.

## Route-back conditions

The accepted outcome or non-goals changed. Stop and return a structured planning delta that names the changed premise, affected acceptance evidence, and recommended change or stop.

Re-verified observation: the three-shape rule exists only in DEV-94's text

Re-verified: `grep -rq 'not applicable' scripts/ship-flow/` exit 1 2026-09-06
