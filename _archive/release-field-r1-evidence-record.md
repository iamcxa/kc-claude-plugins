---
id: yz3we5ez1ad507vg956cwg0s
title: "Evidence record: release r1 carried end to end into a work item's release field"
status: backlog
archived: 2026-09-15
source:
product: kc-dev-flow
planning-window:
planning-outcome:
release: r1
release-readiness: defer
started:
completed:
verdict:
worktree:
issue:
pr:
mod-block:
---

## The problem

`sprint-to-release-contract-migration` (AC-4, AC-5) needs one real committed work
item, not a fixture, that carries a real journey release identifier in its
`release` field and is findable by `spacedock status --where release=<id>`. No
r1 story in `docs/journey/kc-journey-map/draw-a-journey.yaml` is itself open
work right now (every r1-tagged story there already carries `status: exists`),
so this record exists to carry the evidence rather than to name new work.

## Accepted outcome

This entity's `release` field holds `r1`, copied byte-for-byte from
`docs/journey/kc-journey-map/draw-a-journey.yaml`'s `releases:` list, and
`spacedock status --workflow-dir docs/dev --where release=r1` returns exactly
this entity.

## Non-goals

- Naming new kc-journey-map work. r1 is fully shipped; nothing here proposes
  more of it.
- Retiring `sprint` or migrating any other entity's frontmatter.

## Acceptance criteria

- **AC-5-evidence** `release: r1` on this entity's frontmatter is byte-equal to
  the `id: r1` value in `docs/journey/kc-journey-map/draw-a-journey.yaml`, and
  `spacedock status --workflow-dir docs/dev --where release=r1` returns exactly
  this entity's slug.

## Route-back conditions

Retire this record once `sprint-to-release-contract-migration` closes and a
real migrated adopter item supersedes it as AC-5 evidence; without-it
disposition is Kent's call, flagged in `sprint-to-release-contract-migration`'s
stage report.

## Withdrawal

Withdrawn on the Captain's ruling of 2026-09-15. Two reviewers judged this an evidence artifact rather
than a deliverable this workflow tracks: its own body says it exists to carry evidence rather than to
name work, and the evidence itself — the byte equality and the `--where release=r1` result — is
recorded verbatim in `sprint-to-release-contract-migration`'s stage reports. It also carried a bare
`release: r1`, which the qualified-release rule in PR #454 refuses.
