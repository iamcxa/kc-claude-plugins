---
id: bzjf3m574p8c3yt7s7y71x99
title: Make delivery topology review sticky and provider-neutral
status: backlog
source: Captain review of PR #240 threshold compression and duplicated reviewer gate on 2026-08-16
product: kc-dev-flow
sprint:
started:
completed:
verdict:
worktree:
issue:
pr:
mod-block:
design:
lane:
---

## Problem

The current large-change topology trigger can be escaped by semantics-preserving line compression, while `Native stack exception` requires a GitHub non-author acknowledgement even when an exact-candidate fresh EM or RoboRev has already independently adjudicated separability. This duplicates judgment, incentivizes threshold gaming, and obscures that topology review is a safety signal rather than permission.

## Proposed approach

Evaluate a sticky topology-review trigger, rename the exception as a delivery-topology rationale, and accept one provider-neutral candidate-bound independent judgment without weakening ordinary exact-head CI, feedback, readiness, or merge authority.

## Acceptance criteria

To be defined in ideation after the item is scheduled.

## Out of scope

- Changing PR #240's governing contract mid-delivery.
- Weakening exact-head CI, review-feedback, readiness, or merge gates.
