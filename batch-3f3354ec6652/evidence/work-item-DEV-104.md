---
title: "DEV-104: ship-flow review station: open the Draft PR and run kc-pr-review, treating empty reviewer output as absence"
status: implementation
source: https://linear.app/duckbase-co/issue/DEV-104/ship-flow-review-station-open-the-draft-pr-and-run-kc-pr-review
product: kc-dev-flow
planning-window: Linear Cycle b788c52d-8370-475f-be4f-8fcd88dd03d6
planning-outcome: Linear Project 6072d592-8704-448b-bb8d-66471b0557f9 Ship-flow hands the Captain one UAT message instead of a chat to read
sprint: S10
sprint-readiness: ready
started:
completed:
verdict:
worktree:
issue: DEV-104
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

Five PRs were opened by the First Officer on 2026-09-05/06 and none was reviewed by `kc-pr-review`; the FO read each diff by hand. S25 recorded a cross-model reviewer returning empty output that was nearly recorded as 'no findings'. The approval `defaults` now name the rule (`empty_reviewer: fallback_to_fo_diff_read`) but nothing executes the station.

## Accepted outcome

One script opens the Draft PR from an accepted Evidence block (title from the commit subject, body from a template fed by the block), runs the `kc-pr-review` skill on it, and dispositions findings by the approval `defaults`: security, data-loss, and compatibility findings block; others are listed for the UAT document. Empty reviewer output is recorded as reviewer-absent and falls back to the FO diff read, never as 'no findings'.

## Non-goals

* No change to kc-pr-review itself.
* No auto-merge, no marking ready.
* No Linear write.

## Acceptance criteria

* **AC-1** Run on a real accepted block the script opens a Draft PR whose title equals the commit subject and whose body carries the block's SHAs; the run log is recorded.
* **AC-2** A fixture review output with one `security` finding produces disposition `block`; one with only a `style` finding produces `listed`; both runs recorded.
* **AC-3** An empty reviewer output produces `reviewer-absent` and the fallback marker, not `no findings`; recorded.
* **AC-4** `python3 scripts/kc-dev-flow-contract-test.py` exits 0 at the candidate.

## Route-back conditions

The accepted outcome or non-goals changed. Stop and return a structured planning delta that names the changed premise, affected acceptance evidence, and recommended change or stop.

Re-verified observation: no ship-flow script or runtime doc invokes the review skill

Re-verified: `grep -rq 'kc-pr-review' scripts/ship-flow/ docs/ship-flow/README.md` exit 1 2026-09-06
