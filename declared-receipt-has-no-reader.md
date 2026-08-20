---
id: q0z8h3xny0qxv0r5srter8tj
title: Conditional-reference receipt and trigger declarations are read by nothing
status: backlog
source: adopter field report on kc-dev-flow 3.0.0, filed as issue #256 (2026-08-19); confirmed on origin/main and the current branch before filing
product: kc-dev-flow
sprint:
started:
completed:
verdict:
worktree:
issue: 256
pr:
mod-block:
gates:
    version: 1
    records:
        - id: gate:q0z8h3xny0qxv0r5srter8tj:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:q0z8h3xny0qxv0r5srter8tj-backlog-1
              briefing:
                id: briefing:q0z8h3xny0qxv0r5srter8tj:backlog:attempt-1:revision-1
                digest: sha256:b29f07c33f960893825b1e55a02b9f11e3527102175446986dc91ef5e313029b
                request-digest: sha256:916b5961b8f51a1d9210c5dc0be4c24ac424c1f737c87da4d03dab1bc98a2c99
                room-ref: ./declared-receipt-has-no-reader/review/backlog/briefing-1
---

## Problem

Every stage contract in `kc-dev-flow/references/profiles/**` declares a
`kc-dev-flow-conditional-references/v1` block whose entries carry `path`,
`trigger`, and `receipt`. `scripts/profile-contract-loader.py`
(`check_conditional_references`) reads only `path`, and fails closed when the
named file is not vendored. `trigger` and `receipt` are consumed by nothing —
not the loader, not a skill, not a script. A stage can therefore complete having
produced no `reverse_recovery`, `journey_slices`, or `project_context` receipt
and the route still reports success. The asymmetry is the defect: the same block
enforces one field rigorously and ignores the other two, so a field that names an
obligation reads as a guarantee while providing none.

Confirmed present at `kc-dev-flow-v3.0.0`, on `origin/main`, and on the current
branch: 9 contracts declare receipts; the loader's only entry read is
`entry["path"]`.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v2
  selected: production
  recommended: production
  basis: "A marketplace-published plugin contract consumed by external repositories at a pinned release tag. The change alters the loader's output shape and the conditional-reference reference text, so every adopter reads it at their next pin; it carries compatibility and release obligations and no operational runtime."
  route: [shape, build, verify, release]
  obligations:
    architecture:
      - "Keep the declaration block's schema stable; add a reader for the already-declared `receipt` field rather than a new field or a second declaration surface."
      - "Do not make `trigger` evaluable and do not add a stage-exit enforcement check; that is a separate, larger decision the Captain declined at this gate."
    implementation:
      - "Emit the selected stage's declared receipt names in the loader's JSON output so a caller can read them without re-parsing contracts."
      - "State in the conditional-reference reference exactly what the loader guarantees and what it does not, so the field stops reading as an enforced obligation."
    testing:
      - "A loader test that fails when the declared receipt names are absent from the JSON output, and one that fails when they do not match the selected stage's declarations."
      - "The existing `path` fail-closed behavior stays proven by its current tests."
  scope_boundary: "Excludes evaluable triggers, stage-exit receipt verification, any standing enforcement gate, and any change to which references each contract declares."
  promote_when:
    - "The Captain accepts that a missing receipt must block a stage, not merely be observable."
    - "An adopter needs the receipt names before the loader runs, which would move the declaration out of the contract body."
  decision:
    authority: person:captain
    at: 2026-08-20T13:50:38Z
```

## Accepted outcome and non-goals

## Acceptance evidence

## Measurement
