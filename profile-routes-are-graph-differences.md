---
id: 8x38b1qryjrmy5w4ffk1egy1
title: Profile routes are expressed as graph differences, so a POC or Pilot item cannot reach done
status: ideation
source: hit in production 2026-08-20 by declared-receipts-need-a-reader (k69wjs5ttme3z11hph3sy45d), the first Pilot item this workflow has run; the Captain ruled that asking Spacedock to skip stages is the wrong ask
product: kc-dev-flow
sprint:
started:
completed:
verdict:
worktree:
issue:
pr:
mod-block:
gates:
    version: 1
    records:
        - id: gate:8x38b1qryjrmy5w4ffk1egy1:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:8x38b1qryjrmy5w4ffk1egy1-backlog-1
              briefing:
                id: briefing:8x38b1qryjrmy5w4ffk1egy1:backlog:attempt-1:revision-1
                digest: sha256:2a61477e12e737f5b82ec15c384a84b1aab3d3bf5859c30a879f9659d7ddc1d1
                request-digest: sha256:daee347373ac8139866e8c03b4eca2c5e4f0a1a3cf0eabb58e58f4abe3e7f2e1
                room-ref: ./profile-routes-are-graph-differences/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:8x38b1qryjrmy5w4ffk1egy1:backlog:1
                briefing: briefing:8x38b1qryjrmy5w4ffk1egy1:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-08-21T08:46:04.874207Z"
                decision: approve
                reason: 'Captain approved scheduling with the Production work profile, calling this an evident defect. It is an observed failure: the first Pilot item this workflow ran could not reach done and needed a recorded no-op transition to terminalize. Production because any fix touches the ROUTES table or the profile contracts, which external adopters consume at a pinned tag and which carry compatibility obligations. The Captain accepted that the accepted outcome may be a design decision rather than a diff, and had already ruled out asking Spacedock for a skip-stage capability.'
              application:
                target-stage: ideation
                state: consumed
---

## Problem

`kc-dev-flow` gives each work item its own route. The workflow runtime owns one
stage graph. Where the two disagree, nothing reconciles them, and a POC or Pilot
item cannot complete.

Observed, not hypothetical. `declared-receipts-need-a-reader` is a
`pilot-product-slice` item. Its validation gate was approved; `gate consume`
advanced it to `release`; and it is now stranded:

```
status: release
loader: workflow stage 'release' is outside pilot-product-slice;
        expected: ideation, implementation, validation
status --next: dispatchable [] / ready_gates []
```

The loader had already computed the correct answer. For that same item at
`validation` it emits `next_workflow_stage: done`. `gate consume` never asks it;
it advances to the next stage in the declared graph.

`next_workflow_stage` is produced by the loader, asserted by the loader's own
tests, and mentioned in two prose files (`continue-dev-flow/SKILL.md`,
`docs/dev/README.md`). Nothing that executes reads it. That is the same shape as
the defect `#256` reported about `receipt`, one layer up: the right answer is
emitted into a field with no consumer.

`kernel.md` anticipates the need and assigns it to nobody in particular:

> A workflow runtime **may** expose the union of stage names and skip stages
> outside the selected route. Skipping an inactive stage requires no synthetic
> review or receipt.

Permission language, no named implementer, no requirement, and no fallback for a
runtime that cannot skip. Spacedock did not break a promise — it only ever
offered one graph per workflow. The routes are this package's invention, and
this package owns route *validation* (the loader fails closed on an out-of-route
stage, which is what caught this) while owning no part of route *traversal*.

## The two skip points are not equally dangerous

`ROUTES` in `profile-contract-loader.py` against the adopter graph
`backlog -> ideation -> implementation -> validation -> release -> done`:

| Skip | Who | Severity |
|---|---|---|
| `ideation` | POC | Harmless. Non-terminal, so an FO `status --set` moves past it. |
| `release` | POC and Pilot | Blocking. The terminal transition is owned by the merge ceremony and needs a pending approval whose target is `done`; the validation approval gets spent on `release` instead, so that approval never exists. |

Any fix that only addresses `release` still leaves POC items needing a manual
nudge past `ideation`; any fix that only addresses traversal still has to
explain where the terminal approval comes from.

## Ruled out before shaping starts

Asking Spacedock for a skip-stage capability. The Captain ruled this the wrong
ask on 2026-08-20: making traversal depend on data inside an entity body turns a
graph the runtime can reason about into one it cannot, and gates, invariants and
mod-blocks all key off stages. It would also be a large new surface for one
adopter's need.

## Candidate directions, not a decision

1. **Demote `release` from a state to a gate.** `ideation`, `implementation` and
   `validation` are all "work happens here"; `release` for Production is mainly
   an authorization checkpoint, which is the shape of a gate, not a state. Model
   it as a Production-only gate after `validation` and delete the state. All
   three profiles then share one graph, the difference lives in which gates
   fire, and nothing needs to skip. **Cost:** Production loses release authority
   as a separately-rendered decision — "the code is verified" and "this may be
   released" are two rulings, and collapsing the states risks collapsing the
   rulings. The gate design has to carry that weight back.
2. **One workflow per profile.** Three exact linear graphs, zero new mechanism,
   already supported. **Cost:** entities split across three state trees,
   promotion becomes a cross-workflow move, and a single-view status query over
   all work stops working.

Direction 1 is the FO's recommendation; it is recorded here as a starting point
for shape, not as a selection.

## Work profile receipt

## Accepted outcome and non-goals

## Acceptance evidence

## Measurement
