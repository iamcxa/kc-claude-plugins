---
title: Derive release story progress from local development tasks
status: ideation
product: kc-journey-map
source:
planning-window:
planning-outcome:
sprint: S1
sprint-readiness: ready
started: 2026-09-10T16:09:10Z
completed:
verdict:
worktree:
issue:
pr:
mod-block:
id: 91n5fvm5qtpf6gxd4bwhxxkg
gates:
    version: 1
    records:
        - id: gate:91n5fvm5qtpf6gxd4bwhxxkg:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:91n5fvm5qtpf6gxd4bwhxxkg-backlog-1
              briefing:
                id: briefing:91n5fvm5qtpf6gxd4bwhxxkg:backlog:attempt-1:revision-1
                digest: sha256:0a602c42d8b37ea7b1b47e1afb24c4de0ead2a31e0dfa988f4bb23b04d441834
                room-ref: ./review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:91n5fvm5qtpf6gxd4bwhxxkg:backlog:1
                briefing: briefing:91n5fvm5qtpf6gxd4bwhxxkg:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-10T16:07:48.101427Z"
                decision: approve
                reason: Kent approved the concrete two-skill task scope with 那就按這樣繼續 and answered 可以 to adopting Pilot and the shape/build/verify route for this task. Admit this standalone brief to ideation only; the prior border commit and later implementation/delivery gates retain their authority.
              application:
                target-stage: ideation
                state: consumed
---

## The problem

Journey-map currently counts authored story status values. Its executable-symbol
lint checks citations but does not derive development progress. Kent approved a
separate optional skill that reads local Spacedock tasks, maps them to release
stories, and supplies progress to the independently usable drawing skill.

This is a kc-journey-map product deliverable under the existing docs/dev workflow,
not workflow maintenance or a replacement planning provider.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: pilot-product-slice
  recommended: pilot-product-slice
  basis: >-
    Kent selected Pilot for this retained local plugin feature. Task access is
    read-only; drawing-only consumers keep working without a migration. There
    is no unattended operation or production commitment.
  route: [shape, build, verify-deliver]
  obligations:
    architecture:
      - Keep task reading outside the independently usable drawing core.
      - Keep journey intent authoritative and derived progress out of readback writes.
    implementation:
      - Add one optional progress skill with explicit local refresh and optional drawing.
      - Resolve complete required mappings by journey, release, and story identity.
      - Separate development completion from delivery acceptance using the three existing colors.
    testing:
      - Exercise the actual local task reader and projection seam.
      - Falsify missing mappings, identity collisions, reopened tasks, and vacuous completion.
      - Prove source preservation and all-done pending-delivery-acceptance behavior.
  scope_boundary: >-
    Local read-only task progress and optional drawing integration within
    kc-journey-map. Excludes plan-flow consolidation, provider changes, global
    sprint migration, background operation, consumer migration, and delivery authority.
  semantics_unchanged: false
  promote_when:
    - Existing drawing-only consumers must migrate records or configuration.
    - Production exposure, unattended operation, or long-term support is accepted.
  decision:
    authority: Kent
    at: 2026-09-10T16:06:47.619756Z
```

Kent answered "可以" to the explicit Pilot selection question for this new task.
The standalone Development Brief supplies planning authority; no Planning Receipt
or planning-provider invocation is needed. Use the existing local kc-journey-map
S1 execution group for this continuation of release-story inspection; this legacy
scheduler field is not a journey release mapping or a time-cycle commitment.

## Accepted outcome

Kent can explicitly refresh a journey's release progress from local Spacedock
tasks and draw the result in one operation, while drawing remains independently
usable without Spacedock. Both skills live in kc-journey-map; this does not add a
third top-level planning/development flow.

Task records point to stable journey, release, and story identities. One story
may require multiple tasks. Count a story as development-complete only when its
required task mapping is complete and every required task is done. Calculate
release progress from stories rather than substituting a release-wide task ratio.
A release whose required stories are all development-complete is pending
delivery acceptance, not accepted, released, or proven usable by its target user.

Use the existing three colors. Task-derived green means development-complete,
with provenance that distinguishes it from journey acceptance. Missing or
uncertain mappings must not invent completion or turn existing untracked
functionality into a confirmed gap. Drawing-only use retains its existing
authored status/evidence route. Progress is a derived input, not a second
editable source of truth in the journey file.

## Non-goals

- Merge kc-plan-flow into journey-map or change its admission/backlog gates.
- Migrate the repository-wide sprint vocabulary or rewrite active tasks'
  execution grouping. Use release terminology in the new product interface;
  any narrowly required legacy adapter must be explicit and must not equate
  a time grouping with a user-value release by inference.
- Change planning-provider defaults, integrate or project to Linear, or write
  external issues. This item reads local development state only.
- Add a daemon, background synchronization, generic provider framework, another
  top-level workflow, new standing gates, or new CI lanes.
- Treat task status as journey acceptance, introduce a fourth border state, or
  strengthen source-symbol lint into a separate implementation-proof system.
- Modify the frozen border candidate, its approval record, existing task states,
  user rooms, or valuable journey source files during validation.
- Prove the deferred live host-selection story or redo unrelated border work.
- Commit product changes without exact-file approval; push, create PRs, merge,
  release, or accept delivery without the corresponding authority.
- Bump plugin versions or require existing drawing-only consumers to migrate.

## Acceptance criteria

- **AC-1**: Drawing works without Spacedock installed or configured; an optional
  progress skill in the same plugin can refresh and draw in one invocation.
- **AC-2**: Progress is resolved by journey/release/story identity and all required
  tasks per story. A mixed multi-task example demonstrates that task and story
  completion ratios differ; cross-release or cross-journey collisions do not
  contribute to the selected story.
- **AC-3**: Empty, missing, ambiguous, incomplete, or unreadable task mappings do
  not become complete. Reopening a required task removes the story from the
  completed count on the next refresh; archived done tasks remain discoverable
  through the declared local reader when they belong to the mapping.
- **AC-4**: All required stories complete yields pending delivery acceptance.
  The board's existing three colors and progress labels expose the distinction
  between development completion and journey acceptance without claiming either
  source-symbol presence or a task status proves user usability.
- **AC-5**: Explicit refresh supplies derived progress to rendering without
  changing authoritative journey intent, persisting derived statuses through
  canvas readback, or mutating task states. A before/after source comparison and
  a real local reader-to-board exercise provide evidence.

## Route-back conditions

Return to Kent if the smallest implementation requires consumer migration,
unattended operation, provider writes, a new standing policy, materially broader
files/dependencies, a different completion meaning, or changing the approved
standalone drawing behavior. If task metadata cannot establish complete required
mapping, keep that result unverified and present the missing mapping contract
during shape rather than inventing an accepted scope.

## Delivery and preservation

The existing product home is kc-journey-map. The default dependency base is the
reviewed journey-map work, not an unrelated trunk snapshot. Draft PR #394
(iamcxa/journey-map-skill-merge -> main) is open; current border work is frozen in
/Users/kent/conductor/workspaces/kc-claude-plugins/tacoma/.context/worktrees/journey-board-stories
at HEAD 697525fe1e647dcea67663bc19b5519b70dfa5b3 plus its exact validated 12-file
uncommitted delta. That delta is still awaiting separate local-commit approval.
Do not absorb or alter it. Resolve an isolated dependent candidate at the
implementation boundary after checking live ownership and delivery state.

## Captain direction

Kent approved the preceding two-skill division with "那就按這樣繼續".
This authorizes preparing and continuing this integration task. Kent subsequently selected Pilot for this item. It does not approve the earlier
border commit.
The Planning Receipt is absent: use this standalone Captain-approved brief and
invoke no planning-provider reader or comparator.
