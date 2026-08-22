---
id: 035jbwvtnjk7betvjck3a1hx
title: The trunk clause tests for a shared file where it means a shared dependency
status: backlog
source: hit while delivering profile-routes-are-graph-differences (8x38b1qryjrmy5w4ffk1egy1) on 2026-08-21; the correct base was reached only because a worker ignored the clause's literal test and reasoned from its intent
product: kc-dev-flow
sprint:
started:
completed:
verdict:
worktree:
issue:
pr:
mod-block:
---

## Problem

`references/delivery-branch-base.md` decides one thing — what branch a delivery
is based on — and its two branches of that decision use different tests. The
stacked clause tests for **dependency**:

> an open artifact whose source branch carries work this candidate builds on,
> depends on, or would otherwise re-deliver

The trunk clause tests for **file identity**:

> Target the trunk only when the candidate is independent of every open artifact
> by the evidence you actually checked — no shared file, no reliance on unmerged
> behavior.

Those disagree whenever two unrelated changes touch one file, which in this
repository is routine: `kernel.md` alone is edited by most in-flight
`kc-dev-flow` work.

Observed on 2026-08-21. `profile-routes-are-graph-differences` shared
`kernel.md` and `choose-work-profile/SKILL.md` with the open stack
`#267 -> #271 -> #272 -> #275`. By the trunk clause's literal test it could not
target trunk. By the stacked clause's test it had no lineage with that stack at
all: the hunks land near the same line of `kernel.md`, but this candidate
rewrites the Production route table and bounds the runtime skip clause, while
the stack inserts a backlog exit bar. Neither builds on, depends on, or
re-delivers the other.

The right base was trunk, and it was reached only because the delivering worker
compared the actual diff hunks and then departed from the clause it was given.
A worker that followed the letter would have stacked an independent one-commit
fix behind four unmerged pull requests, and would have been correct to.

## Why this is worth a task rather than a wording tweak

The clause is a decision procedure that two competent readers resolve opposite
ways on the same evidence. Either test may be the right one — that is the
decision this task owes — but they cannot both be the test, and the cheap-looking
repair (delete "no shared file") may be wrong: a shared file is real evidence of
mechanical conflict risk, which is what the trunk clause was probably reaching
for. The likely shape is that conflict risk should be recorded and disclosed
rather than used to force a stack, but that is a proposal, not a selection.

## Not urgent, and say so

This has produced zero wrong bases so far. Its cost is paid in judgment: each
delivering worker re-derives the resolution, and one of them will eventually
resolve it the other way without recording why.

## Work profile receipt

## Accepted outcome and non-goals

## Acceptance evidence

## Measurement
