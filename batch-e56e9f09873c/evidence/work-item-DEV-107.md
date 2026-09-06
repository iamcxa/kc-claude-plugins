---
title: "DEV-107: ship-flow close: the close receipt refuses an undispositioned defect and carries the dev and ship debriefs"
status: implementation
source: https://linear.app/duckbase-co/issue/DEV-107/ship-flow-close-the-close-receipt-refuses-an-undispositioned-defect
product: kc-dev-flow
planning-window: Linear Cycle b788c52d-8370-475f-be4f-8fcd88dd03d6
planning-outcome: Linear Project 6072d592-8704-448b-bb8d-66471b0557f9 Ship-flow hands the Captain one UAT message instead of a chat to read
sprint: S10
sprint-readiness: ready
started:
completed:
verdict:
worktree:
issue: DEV-107
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

`validate-receipt.py` already binds a close receipt to its plan receipt and approval and checks the issue set (2026-09-06, lines 65-77), but it never reads `defects_returned`: S24, S25, S26 sat with `fix_ticket: null` for two days and nothing complained. DEV-94 AC-6 and AC-7 ask for two things the validator does not know about: an entry must carry a `fix_ticket` or an `accepted_residual`, and the close receipt carries a dev debrief (written at UAT-ready from the Evidence blocks and refusals) and a ship debrief (written after merge from the Captain's overturns).

## Accepted outcome

The close-receipt schema gains `accepted_residual` as the alternative to `fix_ticket`, and two debrief fields with fixed minimum shapes. The dev debrief is written at UAT-ready and addressed to dev-flow: per Issue, rounds, Evidence refusals with their shape, code refusals, and one candidate correction to the build contract. The ship debrief is written after the Captain merges and addressed to ship-flow: every `defaults` decision and whether the Captain overturned it, defects returned with disposition, minutes per station, and one candidate correction to ship-flow. `validate-receipt.py` refuses a `defects_returned` entry with neither disposition, names it, and refuses a close receipt missing either debrief or any of a debrief's minimum fields. Two small writers draft each debrief from the batch record into that shape; the FO edits, never writes from scratch. This item also appends the `uat-doc` and close-receipt validation steps to `docs/ship-flow/flows/from-dispatch-to-one-slack-message.yaml`, which DEV-105 created.

## Non-goals

* No change to the plan receipt or approval schemas.
* No automatic Linear ticket creation for a defect; `fix_ticket` is filled by plan-flow.
* No Linear write.

## Acceptance criteria

* **AC-1** The recorded `close-receipt.DRAFT.json` from batch 1016352e0223 is refused naming S24, S25, S26; exit and message recorded.
* **AC-2** The same receipt with `accepted_residual` filled on those three and both debriefs present is accepted; recorded.
* **AC-3** A close receipt with no dev debrief, and one whose dev debrief lacks the per-Issue rounds field, are each refused naming the field; recorded.
* **AC-4** The two writers, run on batch 1016352e0223's record, produce drafts carrying every minimum field; recorded.
* **AC-5** The flow file carries the appended steps and `e2e-cli.sh` at the candidate exits 0 over the whole flow; recorded.
* **AC-6** `python3 scripts/kc-dev-flow-contract-test.py` exits 0 at the candidate.

## Route-back conditions

The accepted outcome or non-goals changed. Stop and return a structured planning delta that names the changed premise, affected acceptance evidence, and recommended change or stop.

Re-verified observation: printed 0 matches: the validator does not read defects_returned

Re-verified: `grep -c 'defects_returned\|fix_ticket' docs/plan-flow/schema/validate-receipt.py` exit 0 2026-09-06
