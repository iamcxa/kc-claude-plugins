---
title: "POC 4: ship-flow as a thin wrapper (dispatch, accept by evidence, kc-pr-review, e2e as UAT admission, zero questions per batch)"
status: backlog
source:
product: kc-dev-flow
planning-window:
planning-outcome:
sprint: S9
sprint-readiness: blocked
started:
completed:
verdict:
worktree:
issue: DEV-94
pr:
mod-block:
id: xhjz5zq7mk9jbhh54ag2x8qq
---

## The problem

The first receipt-driven ship batch (batch-1016352e0223, DEV-90/91/92, 2026-09-03) proved the seam but not the shape the Captain wants. The First Officer re-ran every dev-flow build check (without-it, contract test, own falsifiers) instead of reading the worker's evidence, never ran kc-pr-review or e2e, and interrupted the Captain four times inside one batch (DEV-91 disposition, PR creation, a rebase choice, a commission question). The Captain's stated day shape is: plan and POC in the morning, dispatch at noon, close the laptop, verify in the afternoon, one UAT, merge. ship-flow must therefore be one thin wrapper: dispatch, accept by reading evidence, review through kc-pr-review, e2e as the UAT admission test, one UAT document, one Slack ping, zero questions in between.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: poc-exploration
  recommended: poc-exploration
  route: [shape, build, verify-deliver]
  basis: Fourth ship-flow POC; the shape (four stations, defaults, zero questions) is unproven and the batch of six Issues is the falsifier run. Outcome is a keep/change/discard on the shape, not a product change.
  obligations:
    architecture: [Four stations only; the accept station reads the Evidence block and never re-runs a build check]
    implementation: [Worker: approval defaults block plus validator refusal (AC-1) and the static accept script (AC-2). FO: the six-Issue batch (AC-3 to AC-6) as ship-flow operator]
    testing: [AC-2 refuses DEV-91's recorded pair and accepts DEV-90's; AC-3 batch log shows zero Captain questions]
  scope_boundary: No re-verification in ship-flow; no cloud ship-FO; no receipt schema change beyond approval defaults; no Linear write.
  semantics_unchanged: false
```

## Shape

- **Deviation, recorded:** before admission the FO drafted the `defaults` block into `/tmp/poc5/schema/kc-plan-approval.v1.schema.json` and ran the validator once. That edit is a draft handed to the worker, not AC-1 evidence; the worker owns AC-1 and AC-2 and reports them in its Evidence block.
- **Blocked on the Captain:** AC-3 to AC-6 need six Issues from one Milestone whose receipt names a journey (`milestones[].journey` in kc-plan-receipt/v1). Which six is the Captain's choice; the entity stays in backlog until named.
- The second falsifier tests whether DEV-91's pair (command reads two files, removed variant restores one) is catchable by a static check; that is unproven until AC-2 runs.

## Accepted outcome

ship-flow is four stations on top of a plan receipt plus an approval that carries a `defaults` block. dispatch: one cloud worker per Issue in receipt order at the approved concurrency; the worker runs kc-dev-flow shape and build and returns an Evidence block. accept: the First Officer reads the Evidence block and checks it for internal consistency only, without re-running anything: CANDIDATE_SHA equals the remote head; every changed non-test file has a SURFACE line (surface-map-check); the without-it pair is statically consistent, meaning the removed variant touches every path the command reads (DEV-91's pair, which read two files and restored one, must be refused here); the contract-test exit the worker reported is trusted. review: open the Draft PR and run the kc-pr-review skill on it; its findings are dispositioned by the defaults. e2e: when the receipt's Milestone names a journey, run e2e-flow on the stacked candidates and record the recording; a passing e2e is the condition for "ready for UAT"; a docs-only batch records `e2e: not applicable` and is ready on review alone. Then one UAT document listing every PR, its evidence, how to verify, and every decision the First Officer made under the defaults, and one Slack message. The Captain merges. The approval `defaults` block fixes: security, data-loss, and compatibility findings block; other findings outside the Brief are listed; a minimal-necessity fail records `accepted_no_pr`; a moved base is rebased and re-accepted; a worker BLOCKER skips that Issue and continues; an empty reviewer output falls back to the FO reading the diff and is recorded. The batch runs six real Issues from one Milestone with a journey, so the e2e station is exercised.

Falsifier and stop: the First Officer asks the Captain anything between dispatch and the UAT message; or the static without-it check accepts DEV-91's pair; or kc-pr-review or e2e is skipped on an Issue where the defaults say it applies.

## Non-goals

* No re-running of dev-flow build checks in ship-flow; a worker whose evidence is inconsistent is refused, not re-verified.
* No ship-FO in the cloud; the First Officer runs on the Captain's machine after the laptop reopens.
* No change to the plan receipt schema beyond the approval `defaults` block.
* No Linear write.

## Acceptance evidence

* **AC-1 **`kc-plan-approval/v1` gains a `defaults` block with the six rules above; `validate-receipt.py` refuses an approval without it; recorded.
* **AC-2** The accept station is one script that reads an Evidence block and a candidate SHA and exits 0 or names the inconsistency; it refuses DEV-91's recorded pair (removed variant narrower than the command) and accepts DEV-90's; both runs recorded.
* **AC-3** Six Issues from one Milestone with a journey are dispatched under one approval; the batch log shows zero Captain questions between the first dispatch and the UAT message; recorded.
* **AC-4** Every accepted Issue has a Draft PR, a kc-pr-review run, and (where the Milestone names a journey) an e2e-flow recording; the UAT document lists them with the decisions the defaults produced; recorded.
* **AC-5** One Slack message carries the UAT document link; sent once; recorded.
* **AC-6** Close receipt validated against the plan receipt and approval; defects returned listed.

## Route-back conditions

The accepted outcome or non-goals changed. Stop and return a structured planning delta that names the changed premise, affected acceptance evidence, and recommended change or stop.

## Measurement

Not yet measured.
