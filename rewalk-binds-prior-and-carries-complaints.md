---
title: A re-walk binds its prior report and carries every unresolved complaint forward
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: FO, 2026-10-24, declining Codex round 3 on iamcxa/kc-claude-plugins#714 (review:5636428225, head 0535aa2c) under the workflow's round rule (from round 3, decline unless Material or P1). Both findings are P2, in `kc-dev-flow-2/extensions/release-acceptance/release_acceptance.py`:
  - a third walk recognizes only complaints new in the second walk, so an original complaint carried as `partly-fixed` can be omitted and the third walk passes with `clean: yes`;
  - a prior report from another journey or release with the same reviewer rows is accepted (the digest proves the file unchanged, not that it is the right predecessor); validate its schema, journey and release against the current walk.
- Also carried from #714 validation: F8 (an item merging a filed prior complaint with a new one passes with the new one unfiled) and the residual that a reviewer's `will-not-fix` or `deferred` mark is not checked against a director or Captain ruling.
- Bite so far: none observed; the re-walk mode has run on fixtures only. Reopen when a real re-walk is planned or one of these is seen.
- Non-goals: the first walk, director pass 3.

## FO alignment

Alignment: not needed: review findings deferred by the round rule, no direction change.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
