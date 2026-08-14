---
id: q0ndnhere7c5pgkft8n3kcp5
title: Make projected Issues readable and identity-safe
status: implementation
source: Captain review of the Project #1 Issue #232 projection screenshot on 2026-08-14
product: kc-dev-flow
sprint: S3
started: 2026-08-14
completed:
verdict:
worktree: /Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1/.context/worktrees/spacedock-projection-issue-fidelity
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
Verified by: fixtures cover field-plus-receipt agreement, either anchor missing, disagreement, duplicate anchors, and a managed item with neither anchor; discovery uses the union of `spacedock:managed`, `SD Identity`, and hidden receipt, so one valid anchor repairs the other while label-only or ambiguous candidates produce `CONFLICT` and cannot plan `CREATE`. Falsified by: deleting any single signal can hide a managed candidate, deleting the hidden receipt can plan a second Issue, or editing `SD Identity` silently rebinds an Issue.

**AC-4 — User body edits fail closed without becoming SD input.**
Verified by: a post-projection body mutation produces per-item typed `BODY_DRIFT`, preserves the GitHub body, emits no mutation or refreshed receipt, and leaves comments outside the managed comparison without blocking unrelated safe entities. The digest covers body-minus-receipt after pinned CRLF/CR-to-LF normalization and one terminal newline; an unmodified normalized round-trip is `NO_CHANGE`. Falsified by: an unmodified body drifts, one drifted item blocks unrelated safe updates, or a drifted body is overwritten, accepted as current, or written back to the state branch.

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

## Stage Report: ideation — cycle 1

**Decision: propose one in-place projector repair; external Project #1 mutation remains blocked until exact-state dry-run, fresh validation, delivery, and the existing expiring approval envelope all pass.**

- `Lenses:` the value surface is one readable and recoverable projected Issue journey. Short-ID title, entity body, structured fields, managed ownership marker, dual identity anchors, and drift refusal are dependent parts of that journey rather than independently releasable products.
- `AC normalization:` AC-1 is user value; AC-2 preserves the captain's structured-metadata constraint; AC-3 and AC-4 are governing safety constraints earned by the observed receipt-only failure; AC-5 is the dogfood runtime falsifier. No inherited mechanism was retained without a named failure.
- `Reverse recovery:` existing receipt parsing, item observation, field adapter, mutation journal, approval digest, and no-op planner remain the one supported surface. The broken seams are visible summary rendering, receipt-only indexing, and equality that ignores managed body bytes. No second workflow, ledger, or state writeback is proposed.
- `Simpler route rejected:` title prefix plus entity body alone leaves receipt deletion able to orphan identity; receipt plus `SD Identity` without drift comparison silently accepts human body edits. One repository label scopes recovery outside Project views; stage/product labels are rejected because the existing Project fields already supply their view and chart value.
- `Risk spike:` official GitHub Project fields support text metadata and the live adapter already observes raw text field values; implementation still begins RED on text-field create/update and v1 migration before any live schema mutation. The fail condition is any plan that can create a second Issue after either anchor is removed.
- `Journey/demo:` migrate one v1 fixture in place, then render the ten Project #1 changes as a no-write plan. The first visible demo is #232 with `[g5]` title, its full `## Problem` content, existing lifecycle fields, `SD Identity`, and the same Issue number.
- `Pre-mortem:` a user removes both anchors or edits the body during migration and the projector guesses; managed-orphan and `BODY_DRIFT` classifications therefore stop the entire apply before its first write.
- `Sizing:` one worker, one projector/test/doc seam, expected under 90 minutes; external apply is a later delivery procedure, not inner-loop implementation evidence.
- `Cross-model:` PASS — fresh Claude Opus 5 High, tool-less safe mode, returned `proceed / medium`; it required the discovery-union AC-3 row and normalized round-trip AC-4 row now recorded above, recommended no second model, and left schema/external apply with the captain.
- `Disproof hooks:` a field/receipt disagreement that does not conflict, a removed receipt that plans CREATE, replacement of a foreign label/field, body drift that is overwritten, short IDs computed from only the selected subset, or a non-empty identical rerun rejects the route.

```yaml
science_officer_em_upward_report:
  em_judgment: "Proceed with the in-place repair. The existing field adapter, receipt parser, journal, approval digest, cap, no-op planner, and live ten-Issue installation make body construction and identity indexing localized repair seams rather than a replacement."
  evidence_synthesis: "Live Issue #232 omits entity Markdown; the current summary producer emits metadata, receipt-only indexing loses identity when the comment is removed, and current equality ignores managed body bytes. Pre-apply evidence does not yet prove REST text-field normalization or live preservation."
  risk_tradeoff_call: "The benefit is one readable and recognizable projected-task journey. Additive field and label risk is reversible and ambiguity remains fail-closed; the durable cost is the anchor matrix, v1 migration, and normalized body digest. A mapping ledger or state writeback costs more authority."
  recommendation: "Proceed after extending AC-3 with union discovery and AC-4 with normalized unmodified round-trip proof. Keep BODY_DRIFT per-item and non-blocking; document manual body revert and add no repair command in this slice."
  route: proceed
  confidence: medium
  multi_model: not_needed
  fo_boundary: "FO may render, preview, and report typed outcomes; FO may not mutate schema, apply externally, write SD, or resolve drift/conflict by editing GitHub."
  engineering_judgment:
    question: "Should one S3 follow-up proceed as an in-place repair of the existing one-way Spacedock-to-GitHub projector?"
    revision: "Product c00de6c2140db268eb1fe693abfa347b13a9e0b4; state 3dfa01064d514484c6f03f31729dbf2bed921854; task sha256 12f7bc5fe3d8e11a8490e50062fe1ca5dcd64fd1032ea4cfcece93552875caa9; roadmap sha256 755181bcdfc66b9aa62efe9dfa2dfda21531a3c8e122d62823ae96c3fd830029."
    evidence_synthesis: "Live Issue #232 omits entity Markdown; the current summary producer emits metadata, receipt-only indexing loses identity when the comment is removed, and current equality ignores managed body bytes. Pre-apply evidence does not yet prove REST text-field normalization or live preservation."
    adjudications:
      - finding: "In-place repair is the smallest sufficient route and one value surface."
        disposition: supported
        basis: "The accepted journey extends existing projection lifecycle components and rejected alternatives add authority or leave the duplicate hole open."
      - finding: "Project text identity plus receipt bounds mutable-body matching risk."
        disposition: supported
        basis: "Two additive anchors permit one missing signal to repair while disagreement stops before writes."
      - finding: "Managed candidate discovery is underspecified unless label, field, and receipt form a union."
        disposition: unresolved
        basis: "Label-only discovery could hide an intact field/receipt after label deletion; AC-3 now requires the union fixture."
      - finding: "Body digest normalization is underspecified until an unmodified GitHub-style round-trip is no-op."
        disposition: unresolved
        basis: "Line-ending normalization can otherwise produce fleet-wide false BODY_DRIFT; AC-4 now pins normalization and its RED/GREEN row."
    risk_tradeoff: "The benefit is one readable and recognizable projected-task journey. Additive field and label risk is reversible and ambiguity remains fail-closed; the durable cost is the anchor matrix, v1 migration, and normalized body digest. A mapping ledger or state writeback costs more authority."
    recommendation: "Proceed after extending AC-3 with union discovery and AC-4 with normalized unmodified round-trip proof. Keep BODY_DRIFT per-item and non-blocking; document manual body revert and add no repair command in this slice."
    route: proceed
    confidence: medium
    dissent: "The under-90-minute appetite is optimistic; preserve conflict and migration fixtures before optional projection metadata if scope pressure appears."
    disproof_condition: "Return if a single-signal deletion can reach CREATE, normalized unmodified body reports drift, exact preview names a new/out-of-scope Issue, or the captain declines either additive anchor."
    authority_boundary: "Captain retains schema, scope, merge, and external apply; work-item authority retains task state; EM is advisory and FO owns mechanics only."
```
