---
title: "DEV-106: ship-flow handoff: one UAT document and one Slack message, generated from the batch record"
status: implementation
source: https://linear.app/duckbase-co/issue/DEV-106/ship-flow-handoff-one-uat-document-and-one-slack-message-generated
product: kc-dev-flow
planning-window: Linear Cycle b788c52d-8370-475f-be4f-8fcd88dd03d6
planning-outcome: Linear Project 6072d592-8704-448b-bb8d-66471b0557f9 Ship-flow hands the Captain one UAT message instead of a chat to read
sprint: S10
sprint-readiness: ready
started:
completed:
verdict:
worktree:
issue: DEV-106
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

The UAT document for batch 1016352e0223 was written by hand; `uat-doc.py` survives only in DEV-67's evidence directory on the state branch. No Slack message has ever been sent by ship-flow; the Captain learned a batch was ready by reading the chat. The Captain's stated day shape ends with 'one UAT document and one Slack ping'.

## Accepted outcome

`scripts/ship-flow/uat-doc.py` moves into the repository and reads the batch record (accepted blocks, PR numbers and SHAs, review dispositions, e2e artifact, every decision the `defaults` made) into one markdown document; `scripts/ship-flow/notify.sh` sends exactly one Slack message carrying the document link, idempotent on the batch id so a re-run sends nothing.

## Non-goals

* No Slack for anything other than UAT-ready.
* No change to the UAT document's meaning: it lists, it does not decide.
* No Linear write.

## Acceptance criteria

* **AC-1** Run on batch 1016352e0223's recorded evidence the generator reproduces the hand-written `uat.md` section for section; diff recorded.
* **AC-2** The generated document lists every `defaults` decision from the batch record; count recorded against the record.
* **AC-3** `notify.sh` run twice for the same batch id sends one message; both runs and the message id recorded.
* **AC-4** `python3 scripts/kc-dev-flow-contract-test.py` exits 0 at the candidate.

## Route-back conditions

The accepted outcome or non-goals changed. Stop and return a structured planning delta that names the changed premise, affected acceptance evidence, and recommended change or stop.

Re-verified observation: the generator is not in the repository; grep -rqi slack scripts/ship-flow/ also exits 1

Re-verified: `test -f scripts/ship-flow/uat-doc.py` exit 1 2026-09-06
