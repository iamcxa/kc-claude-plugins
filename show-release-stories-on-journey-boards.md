---
title: Show release stories on journey boards with shared activity context
status: backlog
source:
product: kc-journey-map
planning-window:
planning-outcome:
sprint: S1
sprint-readiness: ready
started:
completed:
verdict:
worktree:
issue:
pr:
mod-block:
id: wwn8jfrh1f6k6zyj5tfcjb23
gates:
    version: 1
    records:
        - id: gate:wwn8jfrh1f6k6zyj5tfcjb23:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:wwn8jfrh1f6k6zyj5tfcjb23-backlog-1
              briefing:
                id: briefing:wwn8jfrh1f6k6zyj5tfcjb23:backlog:attempt-1:revision-1
                digest: sha256:1f42307ebe5318d7f9f9508d14936bdc5d9c93a37ae01179502ac4c528348d15
                room-ref: ./show-release-stories-on-journey-boards/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:wwn8jfrh1f6k6zyj5tfcjb23:backlog:1
                briefing: briefing:wwn8jfrh1f6k6zyj5tfcjb23:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-10T09:24:50.160423Z"
                decision: approve
                reason: 'Kent approved the presented Pilot admission: release story boards, gap/unverified/exists, deferred host-selection verification, and preparation of the required local execution group.'
              application:
                target-stage: ideation
                state: pending
---

## The problem

The release journey board displays green activity cards, while the story map
uses yellow stories as release scope. A person reviewing a release cannot see
which individual stories the detailed board covers or where each story lacks
evidence. Activity-level system flow must not imply per-story implementation.

This is a product behavior change in kc-journey-map, tracked by docs/dev. It is
separate from the existing standalone extraction task, whose scope excluded
renderer behavior changes. It is not a workflow-maintenance task.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: pilot-product-slice
  recommended: pilot-product-slice
  basis: >-
    Kent will use and retain this local plugin feature to review release
    stories and round-trip edits to valuable journey files. The scope stays
    within local development use, with no production deployment or migration
    required of consumers; legacy activity cards remain readable.
  route: [shape, build, verify-deliver]
  obligations:
    architecture:
      - Keep the journey file authoritative and activity context shared.
      - Preserve legacy canvas readback without requiring consumer migration.
    implementation:
      - Show selected release stories under their activity groups.
      - Use gap, unverified and exists consistently across the model and projections.
      - Apply wording by story identity and refuse ambiguous edits.
    testing:
      - Verify all three statuses and the implemented-story count.
      - Verify render/readback round trips, conflicts and duplicate identities.
      - Inspect each release canvas and exercise a browser edit through the server.
  scope_boundary: >-
    Local journey-board behavior and three story statuses only. Excludes
    plan-flow integration, provider changes, per-story system mapping,
    host-selection execution proof, production rollout and consumer migration.
  promote_when:
    - A consumer must migrate owned records or change configuration to upgrade.
    - Production exposure, unattended operation or long-term support is accepted.
  decision:
    authority: Kent
    at: 2026-09-10T09:02:18Z
```

The Captain selected Pilot in this session. Stage dispatch requires the state
prerequisite, committed receipt readback and admission to be satisfied.
The Planning Receipt is absent; use this standalone Captain-approved brief
without a Linear reader or comparator.

## Accepted outcome

A person can inspect each release's yellow story cards beneath green activity
groups, see each story's status, evidence and open question, and read the shared
system flow and constraints once per activity. Edited story/activity wording
round-trips to the journey file with conflicts and duplicates reported safely.
Release-detail positioning does not change the full journey order, release
membership, or priority. Existing boards remain available for comparison.

The Captain has approved three story statuses:

- `gap`: the story is known to lack implementation.
- `unverified`: the required behavior has not yet been verified; existing
  instructions or code do not settle that question on their own.
- `exists`: implementation evidence supports the story at its relevant execution
  boundary. This is not delivery acceptance or release completion.

The host-selection story is classified as `unverified`, with the actual host
verification deferred. The model, board labels, documentation and worked example
should use these meanings consistently. Missing evidence alone must not be
presented as proof that implementation is absent. Only `exists` contributes to
the implemented-story count.

## Non-goals

- Merge plan-flow into journey-map or change development providers.
- Invent per-story system mappings or turn implementation evidence into release acceptance.
- Implement or execute the deferred host-selection verification; this change records its unverified status only.
- Publish, merge, commit product code, or mark this task done without the corresponding authorization.

## Acceptance criteria

- **AC-1** Each release board displays its selected yellow story cards beneath green activity groups; system flow and constraints appear once per activity and are labeled as shared context.
- **AC-2** The journey model, rendered story/status labels, documented semantics and worked example distinguish `gap` (known missing implementation), `unverified` (behavior not yet verified), and `exists` (supported implementation). Missing evidence alone is not rendered as proof of absence, and only `exists` contributes to the implemented-story count.
- **AC-3** The host-selection story is recorded and displayed as `unverified`; the deferred host exercise is not claimed as passed or required for completion of this bounded renderer change.
- **AC-4** Activity/story wording changes read back from the story map and release boards to the correct model identities. Competing edits and duplicate identities are reported without silently choosing a winner. Existing legacy activity cards remain readable.
- **AC-5** Moving cards or groups on a release detail page does not change global activity order, release membership or story priority. Those gestures retain their documented projection-specific meanings.
- **AC-6** The three release pages are visually inspected in the browser; a story edit persists through the server and is read back into a separate output file. Existing user rooms and unrelated source/state changes are preserved. Local verification does not imply merge, release or journey-level delivery acceptance.

## Existing local observations

Existing local artifacts to inspect in the selected working stage; these are
not retrospective Spacedock stage receipts. These results predate the approved
three-status change and do not verify its implementation:

- Worktree: /Users/kent/conductor/workspaces/kc-claude-plugins/tacoma/.context/worktrees/journey-board-stories
- Branch: codex/journey-board-stories, uncommitted changes based on 1166747c22f0d6c62db098e5f8cad61bf81174bd.
- Scope: lib/render.mjs, lib/read.mjs, lib/read.test.mjs, lib/render.test.mjs,
  skills/kc-journey-map/references/canvas.md under kc-journey-map/.
- Review record: /Users/kent/conductor/workspaces/kc-claude-plugins/tacoma/.context/journey-story-change-review-20260910.md
- Unit tests: /Users/kent/conductor/workspaces/kc-claude-plugins/tacoma/.context/journey-story-tests-20260910.log (59/59 passed).
- Isolated server: /Users/kent/conductor/workspaces/kc-claude-plugins/tacoma/.context/journey-story-smoke-20260910.log (191 shapes across 5 pages; clean readback).
- Browser preview: http://localhost:3737/?room=v4-story-release-boards-20260910
- Three release PNGs, portable tldraw file, and a separate browser-to-YAML
  save-as check are linked from the review record. Preview descriptions were
  refreshed in a local YAML copy; the tracked example remains unchanged.
- Delivery context: PR #394 is a draft for the preceding extraction work.
  This uncommitted change is not in its current head.

## Route-back conditions

Stop and return to the Captain if the accepted outcome changes, per-story
system/rule fields become necessary, the candidate checkout is owned by another
session, or delivery needs a different PR boundary. Do not absorb unrelated
state or source changes.

## Measurement

Observed local implementation exists under the Captain's direct-FO exception.
Review is pending. Task creation must not be presented as proof that the prior
implementation traversed Spacedock stages. All local checks passing means
pending delivery acceptance, not release completion.

## Deferred host-selection verification

The story "Ask which boards to draw, through the host's selection UI" is
included only for status classification in this change. Its skill instructions
exist, while no recorded host run proves the complete selection-to-render
behavior. Record `unverified` in the story and show the same meaning on the board;
it remains excluded from the exists count. The actual host exercise is deferred.

A later check should invoke the skill in the actual host, record the presented
choices and the user's selection, and compare the resulting canvas pages with
that selection. Also check the documented default when the host tool is
unavailable. Code-symbol lookup alone does not prove this host interaction.
Do not claim the complete release journey is accepted before this story's
required evidence is resolved.
