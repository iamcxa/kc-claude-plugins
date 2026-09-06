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

A Milestone's CLI journey lives at `docs/ship-flow/flows/<milestone-slug>.yaml` in e2e-pipeline's `Execute external` step shape, consumed read-only by `scripts/ship-flow/e2e-cli.sh`; the slug is derived from the receipt's milestone name, so the receipt needs no new field. One script takes the batch's accepted candidates in dispatch order, computes the stacked head, and picks the shape: flow file present → run `e2e-cli.sh` at that head and record the stdout log path; journey named but no flow file → record `e2e: not applicable` with the reason; neither → exit non-zero and the batch is not UAT-ready. This item also writes the flow for this batch's own Milestone, `From dispatch to one Slack message`: over a fixture batch record it runs the stations that exist at its base — `accept-evidence.sh` on a recorded block, then this e2e gate — with each step's expected exit declared; later layers append their stations' steps to the same file.

## Non-goals

* No browser e2e in this item; the e2e-flow recording shape is recorded as delegated to e2e-pipeline.
* No change to `e2e-cli.sh` step semantics.
* No Linear write.

## Acceptance criteria

* **AC-1** `docs/ship-flow/flows/from-dispatch-to-one-slack-message.yaml` exists and `e2e-cli.sh <candidate-sha> <that flow>` runs every step and exits 0 at the candidate; the stdout log is recorded.
* **AC-2** With a fixture receipt whose milestone has a flow file, the script runs `e2e-cli.sh` at the stacked head and records the log path; exit 0 recorded.
* **AC-3** With a fixture receipt naming a journey but no flow file, the script records `e2e: not applicable` with the reason text; recorded.
* **AC-4** With no artifact and no reason, the script exits non-zero and the batch is not marked UAT-ready; recorded.
* **AC-5** `python3 scripts/kc-dev-flow-contract-test.py` exits 0 at the candidate.

## Route-back conditions

The accepted outcome or non-goals changed. Stop and return a structured planning delta that names the changed premise, affected acceptance evidence, and recommended change or stop.

Re-verified observation: the three-shape rule exists only in DEV-94's text

Re-verified: `grep -rq 'not applicable' scripts/ship-flow/` exit 1 2026-09-06
