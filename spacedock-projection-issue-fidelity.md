---
id: q0ndnhere7c5pgkft8n3kcp5
title: Make projected Issues readable and identity-safe
status: ideation
source: Captain review of the Project #1 Issue #232 projection screenshot on 2026-08-14
product: kc-dev-flow
sprint: S3
started: 2026-08-14
completed:
verdict:
worktree:
issue:
pr:
mod-block:
design: required
lane: main
---

## Problem

Projector-owned Issues currently replace the Spacedock entity body with visible projection metadata and rely on a mutable hidden body receipt as the only source-to-Issue lookup key. This makes Project views redundant, leaves the actual task unreadable on GitHub, and can lose or duplicate the mapping when a user edits or removes the receipt.

## Proposed approach

Repair the existing projector seam rather than create another synchronizer. Render each projector-owned Issue body from the entity Markdown after frontmatter, prefix its title with the workflow-native short entity ID, keep stage/product/status in Project fields, add one `spacedock:managed` repository label, and add a Project text field named `SD Identity` containing a stable repository/workflow/entity key. Match by the Project field and hidden receipt as independent anchors; repair one missing anchor, reject disagreement, and report body drift without overwriting user bytes. Recognize the current receipt/summary form only as an in-place migration source.

## Design determination

`design: required`. The captain approved one projection-contract repair after reviewing the live Project #1 Issue #232 screenshot on 2026-08-14. The protected value is immediate FO-to-human recognition plus readable task content without allowing a mutable title or body to become identity authority. Appetite is one small S3 follow-up before status-update work; tolerance is no new Issue, no Issue-number change, no GitHub-to-SD writeback, and no replacement state store.

Reverse recovery at `origin/main@c00de6c2`: the installed projector, receipt parser, Project field adapter, mutation journal, and no-op planner are `EXISTS_BROKEN / REQUIRED`. `_projector_summary()` at the projector asset's lines 350-365 renders metadata instead of entity content; `_target_by_identity()` at lines 386-404 indexes only body receipts; `_same_managed_state()` at lines 912-929 compares receipt core but not rendered body drift. The simplest sufficient route extends those seams. A separate mapping file, state-branch writeback, unique per-entity labels, and another workflow are unnecessary.

The thinnest journey is one existing v1 projector-owned Issue: dry-run resolves it, proposes the same Issue number with `[short-id]` title, entity Markdown body, `SD Identity`, existing lifecycle fields, and managed label; apply updates it in place; an identical rerun is empty. The pre-mortem is that either REST text-field handling or v1 migration ambiguity causes a duplicate or silent overwrite; the plan therefore makes those cases fail mechanically before any external write.

## Acceptance criteria

**AC-1 — A projected Issue presents the same task humans discuss in Spacedock.**
Verified by: a fixture and Project #1 dry-run show `[{short-id}] {title}` where the short ID matches the whole active-plus-archived workflow population, and the rendered body is the entity Markdown after frontmatter with no visible projection-summary block. Falsified by: a title prefix differs from `spacedock status --short-id`, frontmatter or worktree data leaks, or the Issue body omits entity content.

**AC-2 — Structured projection metadata lives on structured GitHub surfaces.**
Verified by: projector-owned Issues retain `Status`, `SD Stage`, and optional `SD Product`, gain text field `SD Identity` plus `spacedock:managed`, and preserve unrelated Project fields and repository labels. Falsified by: lifecycle metadata remains duplicated in visible body, a human field/label is replaced, or an absent optional SD field suppresses projection.

**AC-3 — Mutable Issue content is not the sole mapping key.**
Verified by: fixtures cover field-plus-receipt agreement, either anchor missing, disagreement, duplicate anchors, and a managed item with neither anchor; one valid anchor repairs the other while ambiguity produces `CONFLICT` and zero external writes. Falsified by: deleting the hidden receipt can plan a second Issue or editing `SD Identity` silently rebinds an Issue.

**AC-4 — User body edits fail closed without becoming SD input.**
Verified by: a post-projection body mutation produces typed `BODY_DRIFT`, preserves the GitHub body, emits no mutation or refreshed receipt, and leaves comments outside the managed comparison. Falsified by: a drifted body is silently overwritten, accepted as current, or written back to the state branch.

**AC-5 — The ten Project #1 dogfood Issues migrate in place and converge.**
Verified by: an exact-state dry-run names only existing Issues #229-#238, stays below the approved mutation cap, and predicts no new Issue or Project item; after authorized apply, live readback preserves all ten numbers/URLs/comments and an identical rerun records zero operations. Falsified by: any duplicate, missing item, foreign-item mutation, or non-empty identical rerun.

## Test plan

- Add RED fixtures for full-population short IDs, entity-body rendering, text-field schema/apply, managed-label preservation, v1 migration, anchor repair/conflict, and body drift.
- Run the scoped projector suite, then `scripts/kc-dev-flow-contract-test.py` and repository-required lint/parity checks earned by the diff.
- Generate an exact `origin/main` plus `spacedock-state/dev` Project #1 dry-run before requesting external apply.

## Measurement

One user-visible journey and one projector lifecycle surface. Success is ten preserved Issue identities, readable bodies, deterministic short-ID titles, zero ambiguous matches, and a zero-operation rerun.

## Doc diff

Update the setup skill's mapping contract and runtime receipt/refusal guidance. Record this S3 repair before the status-update item in ROADMAP. No PRODUCT or ARCHITECTURE change is required because SD remains authoritative and the existing one-way topology is unchanged.

## Out of scope

- GitHub-to-SD content or lifecycle writeback.
- Editing linked/human Issue title, body, state, or labels.
- Per-stage/product repository labels, organization Issue fields, or a second mapping ledger.
- Sprint-to-Milestone enablement, status-update publication, Relay/CarLove rollout, or LLM-authored projection content.
