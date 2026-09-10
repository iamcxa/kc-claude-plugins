## The problem

Captain, 2026-09-09: 「should follow the pr-merge template」. The open-pr station wrote five audit
lines instead of the pr-merge mod's motivation lead, What changed, and Evidence sections, and a
naive extraction let a quoted Captain remark become the lead instead of the real change.

## Accepted outcome

Synthetic outcome text, not read by open-pr.sh.

## Stage Report: implementation

- [x] Match BRANCH to one plan-receipt issue
- [x] Build the pr-merge body from the batch entity
- [x] Refuse when neither an entity nor a changed-file is given

## Stage Report: validation

contract-test.py 12/12 passed
