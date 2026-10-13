---
title: learn delivery follow-through round-3 Polish items
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

Declined under the round-3 rule from validation cycle 3 of iamcxa/kc-claude-plugins PR #639 (head 24029378), 2026-10-13, task `learn-delivery-follow-through`. All three are Polish; none is P1 or Material, so none started a repair cycle there. The same round's Codex P1 is being repaired in that task, not here.

## Scope

- Polish 1: in `scripts/test_learning.py`, the guard that pins "pass the head check" in the settle paragraph no longer fails when the phrase is removed from that sentence, because the test's settle slice now includes the restart bullet, which also says "head check". Decline reason: no behaviour is lost; the restart arm still inherits the check through step 6.
- Polish 2: `kc-dev-flow-2/README.md` (outside #639's four files) calls `notices --all` explicit inspection or recovery, while the `dev` and `learn` texts now run it on every invocation. Decline reason: stale wording that contradicts nothing.
- Polish 3: the test's step-order check is case-sensitive (carried from validation cycle 1). Decline reason: the current text passes and a case change has not happened.
- Non-goals: to be set at ideation.

## Acceptance criteria

To be written at ideation.

## FO alignment

Alignment: not needed before ideation; the findings and decline reasons above are the scope.
Release review: not needed: workflow maintenance, on no journey map.
Surfaces: none
Visible change: none
