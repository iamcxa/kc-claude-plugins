---
id: q0ndnhere7c5pgkft8n3kcp5
title: Project SD tasks without repository Issue noise
status: implementation
source: Captain review of the Project #1 Issue #232 projection screenshot on 2026-08-14
product: kc-dev-flow
sprint: S3
started: 2026-08-14
completed:
verdict:
worktree: /Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1/.context/worktrees/spacedock-project-draft-items
issue:
pr: 242
mod-block:
design: required
lane: main
---

## Problem

Projecting every SD task as a repository Issue inflates the repository tracker and
mixes derived execution state with user and agent feedback Issues. Project #4
needs the task content and lifecycle fields, but an SD task is not inherently a
GitHub Issue and should not consume repository Issue identity by default.

## Proposed approach

Repair the existing projector seam. Project an SD task to a Project Draft item by
default, with `[{short-id}] {title}`, the entity Markdown body plus a hidden
receipt, and managed `Status`, `SD Stage`, optional `SD Product`, and
`SD Identity` fields. A reviewed `linked_issue` binding reuses that exact
repository Issue and manages only its Project membership and fields; repository
Issue title, body, state, and labels remain human-owned.

Keep Project observation, fields, membership removal, approval, mutation cap,
journal, and retry on the existing REST adapter. Add only the GitHub GraphQL
Draft create/update mutations required to preserve Draft content and identity.
For the ten bot-created dogfood Issues, create and converge replacement Drafts
while treating the old Issue items as typed migration residue. After live
readback and a residue-present zero-write rerun, record the exact Issue-to-SD
mapping, remove the old Project memberships, permanently delete only #229-#238
after the approved ownership/comment recheck, and require a final zero-write
reconcile. Scheduled automation never performs repository Issue deletion.

## Design determination

`design: required`. The protected value is useful SD visualization without
polluting the feedback tracker. Appetite remains one S3 follow-up before status
updates; tolerance is one existing projector, one existing workflow, no second
state store, no inferred Issue binding, and no unattended destructive cleanup.

Reverse recovery at `origin/main@54594f18`: approval validation, REST Project
observation and field writes, linked-Issue byte preservation, mutation cap,
journal, retry, and canonical-to-installed parity are `WORKING / REQUIRED`.
Draft items are `EXISTS_BROKEN / REQUIRED`: `target_items_from_rest()` discards
`DraftIssue`, while `_desired_issue()` and `apply_github_plan()` default to
repository Issue create/PATCH. The manual Project #4 Draft preview proves only
platform capability. Official REST exposes Draft creation and Project field/item
writes but not Draft title/body update; `addProjectV2DraftIssue` and
`updateProjectV2DraftIssue` are therefore the smallest additional API seam.

The thinnest journey is one selected SD entity creating one Draft, receiving its
managed fields, and producing an empty identical rerun. The pre-mortem is a
partial Draft-create/field-write sequence or coexistence with the old Issue
causing duplicate identity or perpetual writes; dual anchors, typed residue, and
two zero-write gates make those failures stop before deletion.

## Acceptance criteria

**AC-1 — Default projection creates a readable Project Draft, not a repository Issue.**
Verified by: `kc-dev-flow/scripts/project-spacedock-state.test.py` and a selected-scope Project #4 readback show `[{short-id}] {title}`, normalized entity Markdown plus only the hidden receipt, and zero `CREATE_ISSUE`, Issue PATCH, or label writes. Falsified by: a default entity consumes an Issue number, leaks frontmatter/worktree metadata, or omits the SD body.

**AC-2 — Draft lifecycle and identity metadata remain structured and optional-safe.**
Verified by: `kc-dev-flow/scripts/project-spacedock-state.test.py` shows every Draft receiving `Status`, exact `SD Stage`, and `SD Identity`, receiving `SD Product` only when supplied, and preserving unrelated Project fields; an absent optional field reports `PARTIAL` without suppressing the item. Falsified by: metadata is duplicated visibly, a human field is replaced, or an absent optional source field drops the projection.

**AC-3 — Draft identity converges without guessing or duplicate repair.**
Verified by: `kc-dev-flow/scripts/project-spacedock-state.test.py` requires agreeing `SD Identity` and deterministic hidden receipt bytes, permits only one unique trusted receipt-to-missing-field transaction-prefix resume, rejects disagreement/duplicate/field-only/unknown candidates, and makes an identical Draft rerun empty. Falsified by: anchor damage can plan a second Draft, a field reconstructs a receipt, or unchanged receipt-bearing body bytes replan an update.

**AC-4 — Explicit Issue binding remains human-owned while old projector Issues become bounded residue.**
Verified by: linked-Issue fixtures preserve title, body, state, labels, number, and comments while managing only membership/fields; the exact #229-#238 migration plan creates one Draft per SD identity, types the existing Issue items as non-target residue, plans no repository Issue mutation, and the residue-present identical rerun performs zero writes. Falsified by: any linked Issue byte is PATCHed, a residue wins target selection, two Drafts bind one identity, or the scheduled workflow removes/deletes an Issue.

**AC-5 — The attended dogfood cleanup removes noise only after recoverable convergence.**
Verified by: the q0n migration journal records all ten `Issue number → slug → SD Identity` rows; immediate pre-delete readback proves `github-actions[bot]` ownership and zero comments for exactly #229-#238; Draft identity/title/body/fields and a residue-present zero-write rerun pass before Project membership removal and deletion; a final reconcile is also zero-write. Falsified by: a row/audit differs, #229/#238 cross-reference mapping is absent, any deletion occurs before both pre-delete gates, any target falls outside #229-#238, or the final reconcile plans a write.

## Test plan

- Record RED against current Issue-only normalization and `CREATE_ISSUE` behavior, then GREEN for Draft normalization, GraphQL create/update, managed fields, dual-anchor resume/refusal, linked-Issue preservation, typed migration residue, and both no-op states.
- Run the scoped projector suite, then `scripts/kc-dev-flow-contract-test.py` and repository-required lint/parity checks earned by the diff.
- Generate an exact `origin/main` plus `spacedock-state/dev` selected-scope Project #4 dry-run before requesting external apply; exercise cleanup only after its separately recorded gates.

## Measurement

One user-visible journey and one projector lifecycle surface. Success is ten
readable Drafts, zero new repository Issues, zero ambiguous identities, an empty
residue-present rerun, deletion of only the ten synthetic Issues, and an empty
post-cleanup rerun.

## Doc diff

Update the setup skill, mapping contract, projector/test assets, and dogfood
installed projector/config as earned by the diff. Update the existing S3 roadmap
wording. No root PRODUCT or ARCHITECTURE duplication is required because the
plugin mapping contract owns this provider-specific projection topology.

## Out of scope

- GitHub-to-SD content or lifecycle writeback.
- Creating repository Issues for unlinked SD tasks or editing linked/human Issue bytes.
- Unattended Project membership removal or repository Issue deletion.
- A durable migration database, per-stage/product repository labels, or a second mapping ledger.
- Sprint-to-Milestone enablement, status-update publication, Relay/CarLove rollout, or LLM-authored projection content.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v1
  selected: production
  recommended: production
  basis: Public installable skill plus unattended GitHub Actions cron projects authoritative SD tasks into persistent GitHub Project #4 Draft items, may reuse explicitly linked human Issues without editing repository bytes, and performs one irreversible cleanup of projector-created Issues #229-#238 only after verified migration convergence.
  obligations:
    architecture:
      - Keep one-way SD authority, one workflow to one Project, and Project items as derived visualization rather than lifecycle authority.
      - Project an SD task to a Project Draft item by default; reuse an explicitly linked repository Issue only when SD declares that delivery binding, while preserving all repository Issue bytes.
      - Keep stable matching in Project-owned structured identity, with no repository Issue creation, reverse sync, mapping ledger, hosted service, or second task universe.
    implementation:
      - Extend the existing deterministic projector and GitHub adapter rather than add another workflow, service, language, or state store.
      - Preserve preflight validation, mutation cap, append-only operation journal, bounded retry, credential expiry checks, and canonical-to-installed byte parity.
      - Sequence migration as create or reconcile Draft items, verify live identity and an identical zero-write rerun, remove old Project memberships, then delete only projector-created Issues #229-#238.
    testing:
      - Record RED and GREEN for Draft create, update, stable identity, collision refusal, linked-Issue byte preservation, migration ordering, and identical no-op rerun.
      - Run the scoped projector suite, package contract, installer parity, repository checks earned by the diff, and an exact kc-plugins Project #4 dry-run.
      - Require live readback and zero-operation rerun before Project-item removal, and require a complete zero-comment and ownership audit before the separately authorized permanent deletion.
  invariant_sources:
    - docs/dev/README.md
    - docs/dev/_mods/kernel.md
    - docs/dev/_mods/engineering-judgment.md
    - docs/dev/_mods/work-control-profile.md
    - kc-dev-flow/skills/setup-github-project-projection/references/mapping-contract.md
  scope_boundary: One selected docs/dev workflow, user kc-plugins Project #4, migration of the ten existing dogfood projections, and deletion of only bot-created Issues #229-#238 after convergence; excludes Relay, CarLove, reverse sync, status-update publication, broader rollout, and automatic prose generation.
  promote_when:
    - Relay or CarLove rollout enters scope.
    - GitHub-to-SD writeback, automatic linking inferred from Issue prose, a hosted service, automatic status publication, or organization-wide compatibility enters scope.
    - The current PAT, cron, or one-Project ownership boundary changes.
  decision:
    authority: iamcxa as captain
    at: 2026-08-16T06:04:11Z
```

## Promotion trigger — Project Draft migration

The live Project #4 dogfood showed that one repository Issue per SD task inflates
the repository's Issue tracker and mixes derived execution state with user and
agent feedback. The captain approved returning this item from validation to
ideation, selected the replacement Production profile above, and authorized
permanent deletion of bot-created Issues #229-#238 only after their replacement
Draft items pass live identity readback and an identical zero-write rerun. This
record changes no acceptance criterion yet; ideation must normalize the route
after the committed receipt is re-read.

## Stage Report: ideation — cycle 3

**Decision: proceed with Draft-first projection and an attended, proof-gated retirement of the ten synthetic Issues; return the product to implementation.**

- `Profile:` the replacement Production receipt was committed at state
  `6b8e27ec2386fa852226041fb0e8fdfad5ef5c84` and re-read before AC-1 through
  AC-5 were replaced.
- `AC normalization:` readable SD content and chartable lifecycle fields remain
  value; repository Issue identity preservation is superseded by the higher
  value of keeping derived tasks out of the feedback tracker. One-way SD
  authority, explicit linked-Issue byte ownership, irreversible cleanup
  authority, and no reverse sync remain governing constraints.
- `Reverse recovery:` the existing projector, approval envelope, REST adapter,
  field schema, journal, cap, retry, linked binding, and installer parity remain
  `WORKING / REQUIRED`. Draft normalization and Draft content convergence are
  the two `EXISTS_BROKEN / REQUIRED` seams. No second workflow, service, state
  store, language, or repository is proposed.
- `Surface mapping:` before: projector plus default repository Issue lifecycle,
  managed label lifecycle, and one-time cleanup debt. After: the same projector
  plus Draft content mutations and attended cleanup. Linked Issues remain the
  same explicit path. Default Issue create/PATCH and managed repository labels
  are removed, so the steady-state surface set is smaller.
- `Simpler routes:` filtering Issues keeps the unwanted lifecycle; a tracking
  repository adds one; REST delete/recreate churns Draft identity; one identity
  field alone can orphan a partial write; scheduled deletion turns a one-time
  irreversible obligation into permanent authority.
- `Risk spike:` official GitHub REST 2026-03-10 supports Draft creation and
  Project field/item writes but not Draft title/body updates. Official GraphQL
  supplies `addProjectV2DraftIssue` and `updateProjectV2DraftIssue`; those are
  the only new API operations. A manual Project #4 Draft proves platform
  acceptance but not projector behavior.
- `Journey/demo:` one selected SD entity creates one Draft, reads back the exact
  title/body/identity fields, and reruns with zero writes. The ten-entity demo
  then proves residue-present convergence before any cleanup.
- `Pre-mortem:` receipt bytes thrash, a partial create loses its identity field,
  or an old Issue wins target selection. Deterministic receipt comparison,
  one asymmetric receipt-to-field resume, typed residue, and two zero-write
  gates make those failures stop before deletion.
- `Sizing:` one worker and one existing projector/test/doc seam; cleanup is an
  attended delivery procedure, not a second product slice.
- `Cross-model:` PASS — fresh Claude Opus 5 High in tool-less safe mode returned
  `proceed / high`, recommended no additional model, and required the durable
  Issue-to-SD migration journal now included in AC-5.
- `AC scan:` the required scan resolved AC-1 through AC-5 but reported
  `citations=0` despite each criterion naming its test or live artifact. This is
  the ROADMAP's carried-forward scanner defect, recorded rather than treated as
  a finding about the criteria.
- `Disproof hooks:` any default Issue write, linked-Issue PATCH, duplicate Draft,
  non-empty residue-present rerun, failed ownership/comment recheck, cleanup in
  GHA, or non-empty final rerun returns or blocks the route as specified below.

```yaml
science_officer_em_upward_report:
  em_judgment: "Proceed. The route removes the default repository Issue create/PATCH responsibility and replaces it with narrowly scoped Draft mutations plus one attended migration. The irreversible deletion is Captain-authorized and remains behind live readback and two zero-write gates."
  evidence_synthesis: "At product 54594f1871a1a693528f8bdbbe132010ea4fb6db and state 6b8e27ec2386fa852226041fb0e8fdfad5ef5c84, the existing seam already owns REST Project observation and fields, approval expiry, mutation cap, journaling, bounded retry, linked-Issue preservation, and byte-identical vendoring. Current normalization discards DraftIssue and current apply defaults to repository Issue mutation. REST cannot update Draft title/body, while GraphQL supplies the two required Draft mutations. The live manual Draft is capability evidence only. Issues #229-#238 are bot-authored with zero comments; #229 and #238 are cross-referenced by merged PR #240."
  risk_tradeoff_call: "The material irreversible risk is loss of the #229/#238 cross-reference trail. The accepted benefit is a clean feedback tracker; the durable cost is two bounded GraphQL mutations and a one-time attended cleanup. Record Issue number to slug and SD Identity before deletion, and require deterministic receipt bytes so both zero-write gates can fail honestly."
  recommendation: "Proceed with GraphQL confined to addProjectV2DraftIssue and updateProjectV2DraftIssue; keep observation, fields, membership removal, and cleanup preflight on existing REST. Require deterministic receipt comparison, a durable ten-row migration journal, a new reviewed projector digest and mutation cap, residue-present zero-write proof, attended cleanup, and a final zero-write proof."
  route: proceed
  confidence: high
  multi_model: not_needed
  fo_boundary: "FO may implement, test, dry-run, and prepare bounded migration evidence. Captain retains external apply and irreversible deletion authority; scheduled automation receives no cleanup authority."
  engineering_judgment:
    question: "Should the one-way projector default to Project Draft items while retaining explicit linked Issues and use the bounded migration for #229-#238?"
    revision: "Product 54594f1871a1a693528f8bdbbe132010ea4fb6db; state 6b8e27ec2386fa852226041fb0e8fdfad5ef5c84; Project #4 PVT_kwHOABc8eM4BgcAp."
    evidence_synthesis: "At product 54594f1871a1a693528f8bdbbe132010ea4fb6db and state 6b8e27ec2386fa852226041fb0e8fdfad5ef5c84, the existing seam already owns REST Project observation and fields, approval expiry, mutation cap, journaling, bounded retry, linked-Issue preservation, and byte-identical vendoring. Current normalization discards DraftIssue and current apply defaults to repository Issue mutation. REST cannot update Draft title/body, while GraphQL supplies the two required Draft mutations. The live manual Draft is capability evidence only. Issues #229-#238 are bot-authored with zero comments; #229 and #238 are cross-referenced by merged PR #240."
    adjudications:
      - finding: "The proposed route is the fewest maintained lifecycle responsibilities sufficient for the accepted value."
        disposition: supported
        basis: "It removes the default Issue and managed-label lifecycles, adds only two Draft-content mutations inside the existing client, and keeps cleanup non-recurring and attended. Every rejected alternative retains or adds a larger lifecycle."
      - finding: "Dual-anchor Draft identity with one receipt-to-missing-field resume avoids duplicates without general repair."
        disposition: supported
        basis: "Receipt and SD Identity must agree; only a unique trusted same-scope receipt may complete the known create-then-field interruption. Disagreement, duplicate, field-only, and unknown candidates fail closed."
      - finding: "The create, readback, zero-write, membership removal, exact deletion, final zero-write ordering is safe and falsifiable."
        disposition: supported
        basis: "The destructive step is last, each preceding predicate is binary, old Issues are typed residue during proof, and any nonzero write or ownership/comment mismatch stops before deletion."
      - finding: "GraphQL should be confined to Draft creation and title/body update."
        disposition: supported
        basis: "REST item update exposes fields only; delete/recreate would churn identity and increase writes. Existing REST remains sufficient for every other Project operation."
    risk_tradeoff: "The material irreversible risk is loss of the #229/#238 cross-reference trail. The accepted benefit is a clean feedback tracker; the durable cost is two bounded GraphQL mutations and a one-time attended cleanup. Record Issue number to slug and SD Identity before deletion, and require deterministic receipt bytes so both zero-write gates can fail honestly."
    recommendation: "Proceed with GraphQL confined to addProjectV2DraftIssue and updateProjectV2DraftIssue; keep observation, fields, membership removal, and cleanup preflight on existing REST. Require deterministic receipt comparison, a durable ten-row migration journal, a new reviewed projector digest and mutation cap, residue-present zero-write proof, attended cleanup, and a final zero-write proof."
    route: proceed
    confidence: high
    dissent: "Deleting #229 and #238 severs PR #240 cross-reference context; closing those two would be narrower. The Captain accepted full deletion, so the durable mapping journal is the required mitigation."
    disproof_condition: "Return on any nonzero residue-present or final rerun, Draft readback divergence, duplicate or disagreeing identity, linked-Issue PATCH, or deletion candidate failing the bot/zero-comment recheck. Block if cleanup enters the scheduled workflow or external apply lacks a new digest and reviewed cap."
    authority_boundary: "Captain retains scope, external apply, deletion, Ready, and merge. Work-item and validation authorities retain stage verdicts; delivery and provider owners retain remote mutation evidence. This advisory grants none of those actions."
```

## Migration journal — Project #4 pre-apply baseline

Exact live read-only reconcile at product
`54594f1871a1a693528f8bdbbe132010ea4fb6db`, state
`c56aaad847e623e4583014e2cb310e972fad4c6b`, and reviewed projector digest
`a30e8a4e3588b81ca76bf8cce9b4258dc3128b3e634ad68ffb3032505617897a`
classified all ten selected entities as replacement Draft creates, reported no
orphans, and identified these exact legacy residues:

| Issue | Slug | SD Identity |
| --- | --- | --- |
| #229 | `ci-integration-consumer-count-backport` | `iamcxa/kc-claude-plugins:docs/dev:ci-integration-consumer-count-backport` |
| #230 | `e2e-prose-load` | `iamcxa/kc-claude-plugins:docs/dev:e2e-prose-load` |
| #231 | `e2e-schema-contract` | `iamcxa/kc-claude-plugins:docs/dev:e2e-schema-contract` |
| #232 | `e2e-typed-operands` | `iamcxa/kc-claude-plugins:docs/dev:e2e-typed-operands` |
| #233 | `executable-diff-coverage-ratchet` | `iamcxa/kc-claude-plugins:docs/dev:executable-diff-coverage-ratchet` |
| #234 | `github-project-projection-dogfood` | `iamcxa/kc-claude-plugins:docs/dev:github-project-projection-dogfood` |
| #235 | `roborev-implementation-exit` | `iamcxa/kc-claude-plugins:docs/dev:roborev-implementation-exit` |
| #236 | `ship-flow-pr-merge-audit-link-parity` | `iamcxa/kc-claude-plugins:docs/dev:ship-flow-pr-merge-audit-link-parity` |
| #237 | `spacedock-project-status-updates` | `iamcxa/kc-claude-plugins:docs/dev:spacedock-project-status-updates` |
| #238 | `spacedock-projector-automation-sunset-review` | `iamcxa/kc-claude-plugins:docs/dev:spacedock-projector-automation-sunset-review` |

This journal preserves the #229 and #238 mappings referenced by merged PR #240.
It is not deletion evidence: bot ownership, zero comments, Draft readback, and
residue-present zero-write convergence must still be rechecked immediately
before the approved attended cleanup.

## Stage Report: implementation — exact candidate delivery

- Product candidate `8359bc3226d2ccf06cfa45fc785421916fee9425`
  contains the approved nine-file Draft-first slice and is the exact head of
  Draft PR #242 against `main@54594f1871a1a693528f8bdbbe132010ea4fb6db`.
- The scoped projector suite passed 50/50, the aggregate kc-dev-flow contract
  passed, installer audit was clean, canonical and installed projector bytes
  were identical, and `git diff --check` passed at the candidate.
- Exact-state Project #4 read-only reconcile found ten Draft creates, ten typed
  legacy residues, zero conflicts, and zero orphans. No Draft or Issue mutation
  occurred during this implementation gate.
- PR #242 remains Draft. CI, feedback observation, Ready, merge, live Project
  apply, attended Issue deletion, and terminalization retain their later
  authorities.

## Captain-approved route revision — 2026-08-15

After PR #240 reached provider approval, the captain challenged whether the 1,628-line gross diff was necessary and approved the smaller route proposed in the same discussion. The pre-change surface set was readable rendering plus three-signal auto-recovery, body-drift preservation, and general legacy-summary migration. The accepted replacement keeps readable rendering, structured identity, collision refusal, and one exact v1-to-v2 dogfood migration, while removing steady-state auto-repair and the `BODY_DRIFT` lifecycle. Projector-owned Issues are explicitly derived and overwritable; human prose belongs in SD or in a linked Issue.

The route is reversible before merge and external apply. Fresh EM review required one production resume exception: a unique trusted projector-owned v2 receipt may restore only a missing `SD Identity` field after a partial cross-API write. This does not authorize field-to-receipt repair or any ambiguous recovery. Implementation must return to this authority if the exact ten-Issue migration cannot complete without broader recovery, if missing v2 receipt can reach `CREATE`, or if linked Issue bytes require mutation. Product commit, push, Ready/merge, and Project apply remain separately gated.

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

## Stage Report: implementation — cycle 1

**Decision: implementation complete at the uncommitted exact worktree revision; advance to fresh validation without external apply.**

- `RED/GREEN:` the first valid projector run failed at all six new contract surfaces (five failures plus one missing-schema error): short-ID title, entity body, text identity field, anchor repair/conflict, body drift, and structured label ownership. The final scoped suite passes 42/42, including v1 summary migration, unknown legacy-body preservation, duplicate/disagreeing anchors, label-only duplicate prevention, additive label preservation, selected-scope short-ID stability, and zero-operation convergence.
- `Implementation:` the existing projector now derives workflow-native short IDs across active plus archived entities, renders normalized entity Markdown, records a body digest, indexes receipt plus `SD Identity`, recognizes label-only managed candidates, writes typed Project fields, and adds `spacedock:managed` without replacing human labels. Linked Issue bytes and labels remain outside Issue PATCH paths.
- `Dogfood installation:` the packaged installer synchronized the canonical projector to `.github/scripts/project-spacedock-state.py` byte-for-byte and updated only the approval projector digest to `sha256:928b74ab29cb3343000d3e31894d629cb4f4579d58a0ec836a8e67ba908dae8f`; the workflow file remained unchanged and no GitHub mutation occurred.
- `Live read-only probe:` Project #1 resolves all selected entities to existing Issues #229-#238. The plan contains no `CREATE`, `BODY_DRIFT`, `CONFLICT`, or orphan; it requests one new text field, `SD Identity`. Issue #232 previews as `[g5] Kill the parse-and-discard class in flow step operands` with `## Problem` as its first visible body heading.
- `Package evidence:` `python3 scripts/kc-dev-flow-contract-test.py` PASS; `python3 kc-dev-flow/scripts/project-spacedock-state.test.py` 42/42 PASS; `git diff --check` PASS. The installer audit proves canonical/vendored byte parity.
- `Line measurement:` the one canonical runtime adds 383 and removes 79 lines (net +304, about 19% of its prior 1,568 lines); tests add 338 and remove 12 (net +326). The second +304 runtime copy is generated dogfood vendoring, not a second implementation. This is the upper edge of a small change but proportionate to five lifecycle seams—body normalization/drift, short IDs, dual-anchor recovery, typed text fields, and additive labels—without a dependency, workflow, config schema, mapping ledger, or state writeback.
- `Blocked evidence:` a fresh Claude Opus High implementation review attempted at 19:08 CST but the host session limit resets at 19:30; it produced no verdict. The earlier ideation Opus verdict remains `proceed / medium`. Fresh cross-model review and post-delivery live apply/readback remain validation work, not implementation claims.

## Stage Report: validation — cycle 1

**Decision: local and live read-only evidence passes; validation remains open for the reset-time Claude review and captain-owned delivery.**

- `Fresh-context finding:` manual validation found stable Issue repository/ID checks occurring after potential label/schema writes. The checks now run before any request or mutation; a new regression proves a foreign Issue identity produces zero client calls.
- `Subtraction:` removed the dead legacy-summary producer so runtime can recognize old summaries for migration but cannot generate the rejected visible-summary UX. The expected test dependency failed once, then a fixed legacy fixture restored GREEN.
- `Exact evidence:` canonical and vendored projector bytes are identical at `sha256:eb3f783ad531d5adb4c323bc5822c9354596063f381a2478f06f30feee261d8f`; projector tests pass 43/43, the full kc-dev-flow package contract passes, installer audit is clean, and `git diff --check` passes.
- `Exact live dry-run:` Project #1 plans only existing Issues #229-#238; `CREATE=0`, new Project items `=0`, `BODY_DRIFT=0`, `CONFLICT=0`, and orphans `=0`. Planned writes are 32/80: one `SD Identity` text field, one repository label, ten Issue migrations, ten additive label writes, and ten Project field writes.
- `Visible sample:` Issue #232 remains #232 and previews title `[g5] Kill the parse-and-discard class in flow step operands`; its body begins `## Problem`, fields are `Status=Todo`, `SD Stage=backlog`, and qualified `SD Identity`, and its only projector label addition is `spacedock:managed`.
- `Final line measurement:` the canonical runtime is 1,879 lines versus 1,572 at `origin/main`, net +307 (19.5%); contract tests are net +405. The equal vendored runtime delta is generated installation parity. The size is acceptable but at the upper bound: every retained block maps to a required lifecycle seam, while the implementation adds no dependency, workflow, config schema, mapping ledger, or reverse sync.
- `Pending:` Claude Opus High produced no implementation verdict before the host reset. No code commit, push, PR, Project schema write, Issue update, or external apply has been performed.

## Stage Report: validation — cycle 2

**Decision: PASS for local implementation and exact live dry-run; retain post-delivery zero-write readback as the final AC-5 falsifier.**

- `Fresh Claude Opus High:` initial verdict `FAIL` found one High normalization defect: `_body_with_receipt()` and `_body_without_receipt()` stripped all trailing whitespace while the entity digest preserved Markdown hard-break spaces, causing a self-created permanent `BODY_DRIFT` on rerun.
- `Repair evidence:` a Markdown hard-break fixture first failed with `BODY_DRIFT`, then passed after both receipt insertion and extraction were restricted to trimming CR/LF only. The scoped suite remains 43/43 and checks `NO_CHANGE` plus empty mutations on the real rerun path.
- `Adjudication:` the review's linked-Issue concern is unreachable because any valid quoted or unquoted `issue` parses to a positive integer, forces linked ownership, requires a reviewed binding, and conflicts before mutation when missing. Existing `issue=404` evidence proves zero mutations. Live Project item observation was separately inspected and contains the `labels` key.
- `Focused re-review:` `VERDICT: PASS`; findings 1 and 3 closed. The only retained item is the already-declared post-apply dry-run: any replanned `ADD_LABEL` or other write reopens validation rather than permitting completion.
- `Exact revision evidence:` canonical/vendored projector digest `sha256:b0327065f19c4c11808ab7403293954fbafa36360231d2c5e5037c79967ca33a`; canonical runtime 1,880 lines versus 1,572 at `origin/main`, net +308. Package contract PASS, projector 43/43 PASS, and `git diff --check` PASS.

## Stage Report: validation — cycle 3

**Decision: PROCEED to a fresh captain push-approval decision for recut candidate `8af38c437201abf2f47fbbc3966af028c80daa2e`; keep Draft readiness, merge, and Project apply closed.**

- `Recut identity:` candidate parent is exact `origin/main@387be484ae353ebe4603720cc7cc3f8c633d25a1`; the stable patch ID remains `be9809758663aa415a179856241cf92a70c1e662`, matching approved candidate `736ce6710533cc18d9c5bf37c3d1deb9bf00ac54`. The only upstream path overlap was `docs/dev/ROADMAP.md`, and rebase completed without conflict.
- `Exact evidence:` package contract PASS; projector 43/43 PASS; `git diff origin/main...HEAD --check` PASS; version parity, skill frontmatter, marketplace schema/install, and bound-field validation PASS. Canonical and vendored projector bytes remain identical at `sha256:b0327065f19c4c11808ab7403293954fbafa36360231d2c5e5037c79967ca33a`; the worktree is clean and exact-base merge-tree preflight succeeds.
- `Lenses:` delivery/exact-head and docs-policy fired; no changed implementation behavior or route was introduced by the recut. The gross 1,628-line diff remains one projector lifecycle, including a 544-line vendored runtime copy and 453 test lines.
- `Diff coverage:` unchanged from cycle 2 because the stable patch and projector bytes are identical; the exact candidate reruns every owned projector behavior row.
- `Adversarial:` patch-ID comparison, canonical/vendored byte comparison, current-main parent proof, and explicit old-remote-head readback would fail on logical, packaging, base, or provider drift.
- `Cross-model:` `not_needed` — fresh GPT-5.6 High EM returned `proceed / high`; the call is reversible and uncontested after exact evidence.
- `E2E:` the prior exact live Project #1 dry-run remains behavior-continuity evidence for the unchanged projector bytes, but it does not authorize apply or close AC-5.
- `Origin re-observation:` pending delivery — Issue #232 still shows the old projection because PR #240 and the default-branch workflow remain at old candidate `736ce671`; candidate-bound CI, complete `github-pr-feedback/v1`, authorized apply, and the post-apply zero-write rerun must follow their own gates.
- `EM disproof condition:` return if the base/candidate/body cannot be bound exactly, remote head moves before push, candidate-bound CI or feedback is non-pass, a fresh dry-run plans create/conflict/body drift/orphan, or apply fails zero-write convergence.

## Delivery checkpoint

Captain approved the canonical recut delivery packet binding `main@387be484ae353ebe4603720cc7cc3f8c633d25a1`, candidate `8af38c437201abf2f47fbbc3966af028c80daa2e`, branch `iamcxa/spacedock-projection-issue-fidelity`, and Draft PR #240. Exact `force-with-lease` replaced remote candidate `736ce6710533cc18d9c5bf37c3d1deb9bf00ac54`; remote branch and PR now read back at the approved candidate. The reviewed PR body is byte-identical to its mode-0600 body file, contains exactly one full-SHA `Candidate:` line, the split-root `q0n` audit link, and the required `## Native stack exception`. Candidate-bound GitHub checks pass; the PR remains Draft.

`PR feedback: {"scheme":"github-pr-feedback/v1","repository":"iamcxa/kc-claude-plugins","pr_number":240,"layer":"single","head":"8af38c437201abf2f47fbbc3966af028c80daa2e","fingerprint":"sha256:6318c612cab0d6278740cf062d06f62c5d8718e0f7961db539b8873497efe831","items":[],"dispositions":[]}`

Ready still requires a fresh matching feedback observation plus explicit non-author reviewer acknowledgement of the native-stack exception and captain authorization. Merge, Project #1 apply, and the post-apply zero-write rerun remain pending and captain-owned.

## Stage Report: ideation — cycle 2

**Decision: NARROW to the captain-approved smaller route with one trusted receipt-to-field partial-apply resume; return the product to implementation.**

- `Profile:` the captain selected Production because the public skill installs an unattended cron using a separate PAT against persistent Issues and Project #1.
- `Surface subtraction:` remove `BODY_DRIFT`, body-digest ownership, general legacy-summary recognition, field-to-receipt repair, and symmetric anchor recovery. Retain readable rendering, exact v1 migration, strict v2 identity, collision refusal, projector-owned overwrite, linked-byte preservation, and one transaction-prefix resume.
- `Route proof:` fresh GPT-5.6 High EM returned `narrow / high`; the smaller route remains sufficient and strictly smaller. Production requires resumable partial writes but not human-body preservation on projector-owned Issues.
- `Disproof hooks:` return if the receipt-only resume can bind a duplicate or foreign Issue, any non-v1 candidate migrates, missing receipt reaches `CREATE`, interrupted apply cannot resume, linked bytes mutate, or the identical rerun is non-empty.

```yaml
science_officer_em_upward_report:
  em_judgment: "Narrow the current candidate to the captain-approved smaller route, but retain one asymmetric partial-apply resume rule: a unique trusted projector-owned v2 receipt may restore a missing SD Identity field; field-only, missing-receipt, mismatched, duplicate, or label-only states remain conflicts. This remains cumulatively sufficient and strictly smaller. Production does not require BODY_DRIFT, human-body preservation, general legacy-summary migration, or symmetric anchor repair."
  evidence_synthesis: "At state 1dbfae54b9330d395d1be3540340a9b1c93c0551, the accepted outcome makes projector-owned title and body derived from SD, preserves linked Issue bytes, bounds migration to exact v1-to-v2, and explicitly removes BODY_DRIFT and general repair. Candidate 8af38c437201abf2f47fbbc3966af028c80daa2e still emits receipt v1, repairs either missing anchor, recognizes general legacy-summary shape, computes body digests, and returns BODY_DRIFT. Its apply path writes the Issue receipt before the Project field, while the governing runtime contract requires successful partial sequences to be resumable. Current origin/main 004444c5501fc1ef32c9fe61ea616e8fdc3bc426 differs from the candidate parent only in release metadata, so it introduces no contrary projector behavior but still requires a fresh recut and exact-revision validation."
  risk_tradeoff_call: "The smaller route removes an independently violated and reconciled BODY_DRIFT lifecycle and collapses projector-owned prose into normal one-way convergence; it also replaces symmetric steady-state anchor repair and general legacy migration with one bounded migration plus one transaction-prefix resume. The remaining risk is that a trusted receipt-only state can also restore a deliberately deleted projector-owned field; bind it to a unique schema-valid v2 projector receipt, trusted automation authorship, repository/workflow scope, and absence of disagreement or duplication. Manual repair for every missing field violates the accepted resumable production runtime, while a durable recovery ledger or two-phase protocol adds a larger lifecycle surface."
  recommendation: "Emit and require v2 agreement at steady state; permit only trusted v2 receipt-to-missing-SD-Identity completion; keep exact v1 migration; remove BODY_DRIFT, body-digest ownership, general summary recognition, and field-to-receipt repair; overwrite projector-owned title/body from SD; preserve linked Issue bytes. Recut onto 004444c5501fc1ef32c9fe61ea616e8fdc3bc426 and re-run exact migration, interrupted-apply resume, refusal, linked-byte, and zero-operation evidence before readiness, merge, or Project apply."
  route: narrow
  confidence: high
  multi_model: not_needed
  fo_boundary: "FO may implement, test, recut, and produce read-only evidence after the captain-owned route clarification is recorded; FO may not approve the route delta, mark Ready, merge, apply to Project #1, or advance task state."
  engineering_judgment:
    question: "Does the captain-approved smaller route remain sufficient and strictly smaller, and does the production profile require any removed lifecycle?"
    revision: "State 1dbfae54b9330d395d1be3540340a9b1c93c0551; candidate 8af38c437201abf2f47fbbc3966af028c80daa2e; comparison base origin/main 004444c5501fc1ef32c9fe61ea616e8fdc3bc426."
    evidence_synthesis: "At state 1dbfae54b9330d395d1be3540340a9b1c93c0551, the accepted outcome makes projector-owned title and body derived from SD, preserves linked Issue bytes, bounds migration to exact v1-to-v2, and explicitly removes BODY_DRIFT and general repair. Candidate 8af38c437201abf2f47fbbc3966af028c80daa2e still emits receipt v1, repairs either missing anchor, recognizes general legacy-summary shape, computes body digests, and returns BODY_DRIFT. Its apply path writes the Issue receipt before the Project field, while the governing runtime contract requires successful partial sequences to be resumable. Current origin/main 004444c5501fc1ef32c9fe61ea616e8fdc3bc426 differs from the candidate parent only in release metadata, so it introduces no contrary projector behavior but still requires a fresh recut and exact-revision validation."
    adjudications:
      - finding: "F-1: The revised route is cumulatively sufficient and strictly smaller than candidate 8af38c437201abf2f47fbbc3966af028c80daa2e."
        disposition: supported
        basis: "It retains readable projection and structured identity, narrows migration to the approved v1 population, retains only transaction-prefix recovery, and removes the independently violable BODY_DRIFT lifecycle."
      - finding: "F-2: Production requires BODY_DRIFT or preservation of human edits to projector-owned title/body."
        disposition: unsupported
        basis: "The Production receipt defines projector-owned bytes as derived, forbids a body-drift lifecycle, and assigns human prose to SD or linked Issues."
      - finding: "F-3: Production requires general symmetric repair whenever either v2 identity anchor is missing."
        disposition: unsupported
        basis: "Missing receipt, disagreement, duplicates, and label-only candidates can conflict; field-to-receipt repair would let mutable Project state reconstruct Issue identity."
      - finding: "F-4: Every missing v2 anchor can require manual repair without affecting production obligations."
        disposition: unsupported
        basis: "Issue receipt writes precede Project field writes, so an ordinary interruption would otherwise become permanently non-resumable."
      - finding: "F-5: A unique trusted v2 receipt may restore only a missing SD Identity field without recreating general repair."
        disposition: supported
        basis: "This is the minimum recovery for the actual write order when bounded to schema-valid projector ownership, trusted automation authorship, repository/workflow scope, uniqueness, and no contradiction."
      - finding: "F-6: Overwriting projector-owned title/body while preserving linked Issue bytes maintains the accepted ownership boundary."
        disposition: supported
        basis: "SD owns projector bytes and GitHub owns linked Issue bytes; the existing linked path excludes Issue and label PATCH operations."
      - finding: "F-7: Candidate 8af38c437201abf2f47fbbc3966af028c80daa2e already implements the smaller route."
        disposition: unsupported
        basis: "It still emits v1, repairs either anchor, recognizes general legacy summaries, records body_digest, and returns BODY_DRIFT."
    risk_tradeoff: "The smaller route removes BODY_DRIFT and symmetric recovery while retaining one bounded migration and one transaction-prefix resume. The trusted receipt-only resume may also restore a deliberately deleted field, but full manual repair or a durable two-phase ledger costs more and defeats unattended recovery."
    recommendation: "Implement the narrow route, recut to current main, and validate exact migration, interrupted resume, refusal, linked-byte preservation, and zero-operation convergence before any external apply."
    route: narrow
    confidence: high
    dissent: "The earlier phrase requiring conflict on every missing v2 anchor is too broad for the accepted production runtime; a trusted receipt-only transaction prefix must remain resumable."
    disproof_condition: "Return if an interrupted run cannot resume without CREATE or guessing, a trusted receipt-only candidate can bind a duplicate or out-of-scope Issue, any non-exact v1 candidate migrates, projector-owned overwrite fails a zero-operation rerun, or linked Issue bytes mutate."
    authority_boundary: "The captain retains route delta, schema transition, readiness, merge, and external apply; work-item authority owns scope; validation owns exact-revision evidence; delivery and provider owners retain push, PR, and Project mutation authority."
```

## Stage Report: implementation — cycle 2

**Decision: the smaller route is locally green; retarget dogfood from deleted Project #1 to its observed kc-plugins successor Project #4 before fresh validation.**

- `Target drift:` live GraphQL lists Projects #2, #3, and #4; Project #1 no longer resolves. Project #4 (`kc-plugins`, node `PVT_kwHOABc8eM4BgcAp`) contains Issues #229-#233 and #236-#238 plus PR #240. The installed config's deleted #1 target explains the cron's repeated 404 with `operations=[]`.
- `Exact read-only dry-run:` product worktree `bdb2768525f001b05161f74590cd73b0606fd7e7` with uncommitted candidate bytes and state `30e05526e5b75aa632395fc78611d6d6c7a85102` plans ten in-place Issue updates for #229-#238, `CREATE=0`, conflicts `=0`, and orphans `=0`. It attaches existing Issues #234 and #235 as the only two missing Project items.
- `Visible sample:` Issue #232 remains #232 and previews `[g5] Kill the parse-and-discard class in flow step operands`, body heading `## Problem`, qualified `SD Identity`, and receipt schema v2.
- `Schema/apply preview:` create `SD Identity` text, `SD Product` single-select, and `SD Stage` single-select; create/add `spacedock:managed`; update ten derived Issue surfaces and ten Project field sets. The exact plan remains below the approved 80-write cap. No external apply occurred.
- `Local evidence:` 44 behavior cases across 43 test methods pass, package contract PASS, installer audit clean, version parity PASS, skill frontmatter PASS, marketplace schema/install PASS, canonical and dogfood projector bytes identical, and `git diff --check` PASS.
- `Subtraction:` current diff is 1,489 gross lines (1,210 additions, 279 deletions), including two byte-identical projector deltas for canonical distribution and dogfood vendoring. This is below the 1,500-line topology re-review trigger and removes BODY_DRIFT, body-digest ownership, general legacy-summary recognition, and symmetric anchor recovery.
- `Historical title:` #234 comes from an archived completed entity whose `Project #1` title records the original dogfood target. Preserve that archive byte in this slice; the live config and current acceptance target Project #4 independently.
- `Candidate:` captain-confirmed local commit `b7d9a5534dd833a0aa69d44cf97709f3d6ff86f4`; push, Ready, merge, and Project #4 apply remain closed.

## RoboRev implementation-exit claim

```yaml
roborev_claim:
  schema: roborev-implementation-exit-claim/v1
  identity_sha256: 89a1b88f6063d7973493019dc17e9f804635e28702f183c324fb606d1e7aba68
  claimant: codex-montpellier-v1-b7d9a553
  observed_state_revision: 7d9f7d1e25f7a7cfc2217193cdec895f4223ca31
  repository: iamcxa/kc-claude-plugins
  base_sha: 004444c5501fc1ef32c9fe61ea616e8fdc3bc426
  tip_sha: b7d9a5534dd833a0aa69d44cf97709f3d6ff86f4
  provider: roborev
  provider_version: 0.62.0
  config_object_sha: cd46a0b2fc23a91036ab0a8f8885be0dfc9e7380
  config_sha256: 63b6d59a39c07c8a28db161da4d79af412d4b01d46b5bdcf1c7cc4eec58e64dd
  agent: codex
  model: gpt-5.6-terra
  reasoning: thorough
  minimum_severity: medium
  panel: none
  member_count: 1
  state: claimed
  request_count: 0
```

## RoboRev implementation-exit receipt — b7d9a553

```yaml
roborev_observation:
  schema: roborev-implementation-exit-observation/v1
  identity_sha256: 89a1b88f6063d7973493019dc17e9f804635e28702f183c324fb606d1e7aba68
  config_sha256: 63b6d59a39c07c8a28db161da4d79af412d4b01d46b5bdcf1c7cc4eec58e64dd
  provider: roborev
  provider_version: 0.62.0
  mode: observe
  outcome: FAIL
  reason: findings
  job_id: 171
  job_uuid: d0d374f7-1467-4f0d-a8de-34e84059c279
  review_uuid: 9cc26390-4239-40b8-be53-ead383603f5f
  base_sha: 004444c5501fc1ef32c9fe61ea616e8fdc3bc426
  tip_sha: b7d9a5534dd833a0aa69d44cf97709f3d6ff86f4
  status: done
  verdict: F
  member_states:
    - identity: codex:gpt-5.6-terra:thorough:medium
      state: done
      findings: 1
  finding:
    severity: medium
    location: .github/scripts/project-spacedock-state.py:1468
    summary: A receipt-only Project item outside the selected workflow scope is ignored when its managed label is absent, contrary to union discovery.
  request_count: 1
  confirmation_count: 0
  cost_coverage:
    approximate_total: unknown
    jobs_with_cost: 0
    jobs_total: 2
    complete: false
```

## RoboRev changed-tip confirmation claim

```yaml
roborev_confirmation_claim:
  schema: roborev-implementation-exit-claim/v1
  identity_sha256: 608c26d72a99d8d356fb85034b732ee1b7a43b0686c9b650c53105dd03efca11
  parent_identity_sha256: 89a1b88f6063d7973493019dc17e9f804635e28702f183c324fb606d1e7aba68
  claimant: codex-montpellier-v1-bdd4dee5
  observed_state_revision: a4acefb7dbbb36aeeca1d4fa5a6de7373377efe1
  repository: iamcxa/kc-claude-plugins
  base_sha: 004444c5501fc1ef32c9fe61ea616e8fdc3bc426
  tip_sha: bdd4dee58e373711a793bfe397bfdff71af08c13
  provider: roborev
  provider_version: 0.62.0
  config_object_sha: cd46a0b2fc23a91036ab0a8f8885be0dfc9e7380
  config_sha256: 63b6d59a39c07c8a28db161da4d79af412d4b01d46b5bdcf1c7cc4eec58e64dd
  agent: codex
  model: gpt-5.6-terra
  reasoning: thorough
  minimum_severity: medium
  panel: none
  member_count: 1
  state: claimed
  request_count: 1
  confirmation_count: 0
```

## RoboRev changed-tip confirmation receipt — bdd4dee5

```yaml
roborev_observation:
  schema: roborev-implementation-exit-observation/v1
  identity_sha256: 608c26d72a99d8d356fb85034b732ee1b7a43b0686c9b650c53105dd03efca11
  parent_identity_sha256: 89a1b88f6063d7973493019dc17e9f804635e28702f183c324fb606d1e7aba68
  config_sha256: 63b6d59a39c07c8a28db161da4d79af412d4b01d46b5bdcf1c7cc4eec58e64dd
  provider: roborev
  provider_version: 0.62.0
  mode: observe
  outcome: PASS
  reason: passed
  job_id: 172
  job_uuid: 0984dc79-4f2c-45cd-a923-4e7fbc8b8dfc
  review_uuid: f7623779-e618-482e-af75-afb8b07f89ce
  base_sha: 004444c5501fc1ef32c9fe61ea616e8fdc3bc426
  tip_sha: bdd4dee58e373711a793bfe397bfdff71af08c13
  status: done
  verdict: P
  member_states:
    - identity: codex:gpt-5.6-terra:thorough:medium
      state: done
      findings: 0
  summary: The change correctly detects same-repository receipt-only projections outside the selected workflow scope.
  request_count: 1
  confirmation_count: 1
  cost_coverage:
    approximate_total: unknown
    jobs_with_cost: 0
    jobs_total: 3
    complete: false
```

## Stage Report: validation — cycle 4

**Decision: PROCEED to a captain-owned exact push decision for `bdd4dee58e373711a793bfe397bfdff71af08c13`; validation is not complete, and Ready, merge, Project #4 apply, and completion remain closed.**

- `Lenses:` behavior PASS; contract/schema PASS; state/concurrency PASS; security/privacy PASS; runtime/platform PASS; docs/policy PASS; delivery PENDING. Inputs were exact base `004444c5501fc1ef32c9fe61ea616e8fdc3bc426`, candidate `bdd4dee58e373711a793bfe397bfdff71af08c13`, all seven AC-mapped files, 43 projector tests, package/installer/parity/lint evidence, RoboRev jobs 171/172, live Project #4 read-only state, and current PR #240 provider state. Delivery remains pending because the PR is Ready at stale head `8af38c437201abf2f47fbbc3966af028c80daa2e`.
- `Diff coverage:` PASS — coverage.py observed 159/181 added executable canonical-projector statements, 87.8%; the installed projector is byte-identical at `sha256:ed5bf547518c8624a155c3316acca0606d8cdab8a4242ee0aa39064a3b060f3e`. The cumulative diff is 1,216 additions plus 283 deletions, 1,499 gross; 1,030 gross lines are the two byte-identical projector copies and 367 are focused tests.
- `Adversarial:` PASS — the label-less same-repository out-of-scope v2 receipt fixture reproduced RoboRev job 171's unsafe `CREATE` before the repair, then conflicts at the exact tip; receipt-only resume, missing-receipt, field-only, mismatched, duplicate, label-only, non-exact-v1, linked-byte, Markdown-hard-break, CRLF, and identical-rerun rows pass. Changed-tip RoboRev job 172 reports PASS with zero findings.
- `Cross-model:` PASS — one fresh isolated GPT-5.6 High EM returned `proceed / high`, found no reason for another implementation return, and restricted the recommendation to an exact captain push decision. `multi_model: not_needed`.
- `E2E:` PARTIAL — the live Project #4 read-only plan names only existing Issues #229-#238, plans ten updates, zero Issue creates, conflicts, or orphans, and attaches only existing Issues #234 and #235. External apply, live identity/byte readback, and the identical zero-write rerun remain separately authorized delivery evidence.
- `Origin re-observation:` PASS for the pre-apply claim — Reported scenario: the deleted Project #1 target has a kc-plugins successor whose current membership requires only two existing-Issue attachments | Originating runtime kind: live GitHub user Project and repository Issues | Re-observation artifact/revision: Project #4 `PVT_kwHOABc8eM4BgcAp`, source-state observation `a4acefb7dbbb36aeeca1d4fa5a6de7373377efe1`, candidate `bdd4dee58e373711a793bfe397bfdff71af08c13` | Equivalent-runtime rationale: same user Project, repository, Issues, projector adapter, and target config as delivery, with writes disabled | Falsifier kind: existence-disproof and mutation | Result: Issues #229-#233 and #236-#238 already exist in Project #4; #234/#235 are the only selected missing memberships; the plan creates no Issue and reports no conflict or orphan. The visible applied outcome remains pending delivery.
- `PR feedback:` the only provider review is `quinn-code-agent` approval `4943821972`, body digest `sha256:22d63650ebb6bec279429feaba806ae584f99e2d3b012faa7e279a46dd79c041`, bound to stale head `8af38c437201abf2f47fbbc3966af028c80daa2e`; disposition `rejected-with-reason` for candidate validation because it cannot cover `bdd4dee58e373711a793bfe397bfdff71af08c13`. Current old-head checks are likewise not candidate evidence.
- `Disproof hooks:` return if base or candidate changes; any local receipt becomes non-pass; candidate-bound CI or complete GitHub feedback is non-pass; a fresh Project #4 plan creates an Issue, reports a conflict/orphan, targets outside #229-#238, or attaches beyond #234/#235. Block completion if apply changes Issue identity or linked-Issue bytes, or the identical rerun plans any write.

```yaml
science_officer_em_upward_report:
  em_judgment: "Proceed with exact candidate bdd4dee58e373711a793bfe397bfdff71af08c13 to a captain-owned push decision. The accepted one-way projection route is cumulatively sufficient, the RoboRev defect is closed at the exact tip, and no evidence justifies another implementation return. This is not validation completion: candidate-bound PR evidence and post-apply convergence remain closed."
  evidence_synthesis: "Candidate bdd4dee58e373711a793bfe397bfdff71af08c13 is clean, descends directly from exact base 004444c5501fc1ef32c9fe61ea616e8fdc3bc426 through three scoped commits, passes merge-tree and diff checks, and changes seven AC-mapped files by 1,216 additions and 283 deletions, 1,499 gross. The two 515-line projector diffs are byte-identical packaging copies with digest ed5bf547518c8624a155c3316acca0606d8cdab8a4242ee0aa39064a3b060f3e; the remaining weight is focused tests, contract documentation, roadmap, and target configuration. Projector tests pass 43/43, package contract, installer audit, parity, frontmatter, marketplace, and canonical-vendored equality pass. RoboRev job 171 found the label-less same-repository out-of-scope receipt gap at b7d9a553; RED reproduced CREATE, the exact tip changed candidate discovery to inspect receipt or SD Identity before requiring the managed label, and changed-tip job 172 passed with no findings. The Project #4 read-only plan at state a4acefb7 names only Issues #229-#238, plans ten updates, zero Issue creates, conflicts, or orphans, and only attaches existing Issues #234 and #235. The material limits are delivery-bound: PR #240 is currently Ready at old head and Candidate binding 8af38c437201abf2f47fbbc3966af028c80daa2e, so its green check and prior feedback do not cover bdd4dee5; no external apply or post-apply zero-write rerun has occurred."
  risk_tradeoff_call: "The benefit is the accepted readable, identity-safe, one-way SD projection while preserving all ten Issue identities and linked-Issue bytes. The durable cost is the necessary short-ID rendering, structured identity and managed-label discovery, exact v1 migration, and one bounded receipt-to-field interruption resume; the 1,499 gross count is delivery-topology evidence, not a minimality failure, and much of it is distribution duplication plus tests. The immediate risks are pushing a new exact head into a currently Ready stale PR and applying against mutable Project state. A further scope cut would remove a mechanism with a named AC falsifier, while keeping the old candidate preserves the receipt-only gap; the lower-risk alternative is captain-approved exact push with Draft restoration and fresh provider and apply-time evidence."
  recommendation: "Approve only an exact delivery packet for base 004444c5501fc1ef32c9fe61ea616e8fdc3bc426 and candidate bdd4dee58e373711a793bfe397bfdff71af08c13. If approved, restore PR #240 to Draft before exposing the new head, rebind its body and topology to the exact candidate, push with the exact lease, then require candidate-bound CI and a complete github-pr-feedback/v1 observation before Ready or merge. Repeat the Project #4 read-only plan before separately authorized apply, and require live identity readback plus an identical zero-write rerun before task completion. Do not apply, advance state, or claim PASSED now."
  route: proceed
  confidence: high
  multi_model: not_needed
  fo_boundary: "FO may relay this advisory record and prepare the exact captain-reviewed delivery packet; FO may not push, change PR Draft or Ready state, merge, apply Project #4, or advance task state without the retained authority and required exact-revision evidence."
  engineering_judgment:
    question: "Should exact candidate bdd4dee58e373711a793bfe397bfdff71af08c13 proceed to a captain-owned push decision despite the repaired RoboRev finding, 1,499-line gross diff, Project #4 target drift, stale PR evidence, and pending external convergence?"
    revision: "Candidate bdd4dee58e373711a793bfe397bfdff71af08c13; base 004444c5501fc1ef32c9fe61ea616e8fdc3bc426; authoritative task state 5dbc9019cb5159868588d87109e55adcdc4c3385."
    evidence_synthesis: "Candidate bdd4dee58e373711a793bfe397bfdff71af08c13 is clean, descends directly from exact base 004444c5501fc1ef32c9fe61ea616e8fdc3bc426 through three scoped commits, passes merge-tree and diff checks, and changes seven AC-mapped files by 1,216 additions and 283 deletions, 1,499 gross. The two 515-line projector diffs are byte-identical packaging copies with digest ed5bf547518c8624a155c3316acca0606d8cdab8a4242ee0aa39064a3b060f3e; the remaining weight is focused tests, contract documentation, roadmap, and target configuration. Projector tests pass 43/43, package contract, installer audit, parity, frontmatter, marketplace, and canonical-vendored equality pass. RoboRev job 171 found the label-less same-repository out-of-scope receipt gap at b7d9a553; RED reproduced CREATE, the exact tip changed candidate discovery to inspect receipt or SD Identity before requiring the managed label, and changed-tip job 172 passed with no findings. The Project #4 read-only plan at state a4acefb7 names only Issues #229-#238, plans ten updates, zero Issue creates, conflicts, or orphans, and only attaches existing Issues #234 and #235. The material limits are delivery-bound: PR #240 is currently Ready at old head and Candidate binding 8af38c437201abf2f47fbbc3966af028c80daa2e, so its green check and prior feedback do not cover bdd4dee5; no external apply or post-apply zero-write rerun has occurred."
    adjudications:
      - finding: "F-1: The RoboRev label-less out-of-scope receipt finding is closed at exact candidate bdd4dee58e373711a793bfe397bfdff71af08c13."
        disposition: supported
        basis: "The previous label-first filter allowed CREATE; the exact-tip code now admits any same-repository receipt or SD Identity anchor into union discovery before applying the managed-label fallback. The focused fixture removes the label from an out-of-scope receipt candidate, RED reproduced the defect, and changed-tip RoboRev job 172 reports PASS with zero findings."
      - finding: "F-2: The 1,499-line cumulative diff is sufficient and does not justify another narrowing cycle."
        disposition: supported
        basis: "Kernel minimality is lifecycle-based rather than LOC-based, while the pr-merge numeric predicate is strictly greater than 1,500 and controls topology only. Every changed file maps to AC-1 through AC-5; 1,030 gross lines are byte-identical canonical and vendored runtime copies, 367 are focused tests, and each retained identity, ownership, migration, or rendering mechanism has a named accepted falsifier. No strictly smaller compatible route is evidenced."
      - finding: "F-3: Retargeting the dogfood to Project #4 and attaching existing Issues #234 and #235 requires implementation return."
        disposition: unsupported
        basis: "Authoritative state 5dbc9019 explicitly binds AC-1 and AC-5, the Production receipt, roadmap, and configuration to Project #4 after Project #1 deletion. The exact read-only plan preserves Issues #229-#238, creates no Issue, and identifies #234 and #235 as the only missing Project memberships. Mutable target state still requires a fresh apply-time observation, but it does not invalidate the candidate."
      - finding: "F-4: Missing candidate-bound PR feedback and CI prevent an advisory local proceed-to-push judgment."
        disposition: unsupported
        basis: "The exact local artifact, tests, adversarial finding closure, and live no-write plan support the reversible captain push decision. Because PR #240 still binds old head 8af38c43, its provider evidence cannot cover bdd4dee5 and therefore blocks provider-complete validation, Ready, and merge—not the request for authority to publish the candidate so those exact-head checks can run."
      - finding: "F-5: External apply and the post-apply zero-write rerun may remain pending while the candidate proceeds to delivery evidence."
        disposition: supported
        basis: "AC-5 and the Production receipt explicitly place live readback and identical zero-operation convergence after separately authorized apply. Their absence is an unmet completion obligation and blocks PASSED or done, but the read-only zero-create plan is sufficient for the preceding captain-owned push decision."
    risk_tradeoff: "The benefit is the accepted readable, identity-safe, one-way SD projection while preserving all ten Issue identities and linked-Issue bytes. The durable cost is the necessary short-ID rendering, structured identity and managed-label discovery, exact v1 migration, and one bounded receipt-to-field interruption resume; the 1,499 gross count is delivery-topology evidence, not a minimality failure, and much of it is distribution duplication plus tests. The immediate risks are pushing a new exact head into a currently Ready stale PR and applying against mutable Project state. A further scope cut would remove a mechanism with a named AC falsifier, while keeping the old candidate preserves the receipt-only gap; the lower-risk alternative is captain-approved exact push with Draft restoration and fresh provider and apply-time evidence."
    recommendation: "Approve only an exact delivery packet for base 004444c5501fc1ef32c9fe61ea616e8fdc3bc426 and candidate bdd4dee58e373711a793bfe397bfdff71af08c13. If approved, restore PR #240 to Draft before exposing the new head, rebind its body and topology to the exact candidate, push with the exact lease, then require candidate-bound CI and a complete github-pr-feedback/v1 observation before Ready or merge. Repeat the Project #4 read-only plan before separately authorized apply, and require live identity readback plus an identical zero-write rerun before task completion. Do not apply, advance state, or claim PASSED now."
    route: proceed
    confidence: high
    dissent: "Proceed is limited to the captain push decision. The current Ready PR state, stale Candidate binding, absent bdd4dee5 CI and GitHub feedback, and unperformed external convergence prevent any broader validation-complete or delivery-complete claim."
    disproof_condition: "Return if the approved base or candidate changes, the union-discovery RED no longer fails on the prior tip, any exact-candidate local receipt becomes non-pass, candidate-bound CI or complete GitHub feedback is non-pass, or a fresh Project #4 plan creates an Issue, reports a conflict or orphan, targets an Issue outside #229-#238, or attaches anything beyond #234 and #235. Block completion if authorized apply changes Issue identity or linked-Issue bytes, or if the identical post-apply rerun plans any write."
    authority_boundary: "The captain retains exact push, PR-body and topology approval, Draft or Ready transition, merge, Project #4 target acceptance, and external apply authority. Validation and work-item authorities retain verdict and stage transitions; delivery and provider owners retain GitHub mutations and evidence. This EM record is advisory and grants none of those actions."
```

## Delivery checkpoint — candidate bdd4dee5

Captain approved the corrected canonical delivery unit after the body disclosed that the current 1,499-gross-line diff had an equivalent 1,505-line uncompressed repair form. The unit keeps `## Native stack exception`, targets kc-plugins Project #4, and records candidate `bdd4dee58e373711a793bfe397bfdff71af08c13` exactly once. The reviewed mode-0600 body and GitHub readback are byte-equal at `sha256:5dab42cc68300bf29528d7cec74408e1afcf2ec9142ec28d28ebf127ebc270da`.

PR #240 was restored to Draft before the exact lease replaced old head `8af38c437201abf2f47fbbc3966af028c80daa2e`; local candidate, remote branch, and PR `headRefOid` now equal `bdd4dee58e373711a793bfe397bfdff71af08c13`. Candidate-bound version parity, portable E2E, real-browser decision/proof, and GitGuardian checks pass. Quinn's old approval remains bound only to `8af38c43`; a fresh `quinn-code-agent` review is requested for `bdd4dee5`. Ready, merge, Project #4 apply, and task completion remain closed.

The separately approved workflow-rule follow-up is captured unscheduled as backlog task `delivery-topology-review-deduplication` (`bzj`). It does not change PR #240's governing contract or delivery gates.

## Post-merge reconciliation — 2026-08-16

PR #240 was already provider-merged before the requested merge command could run. GitHub reports `mergedBy=iamcxa`, `mergedAt=2026-08-15T18:13:56Z`, head `bdd4dee58e373711a793bfe397bfdff71af08c13`, base `004444c5501fc1ef32c9fe61ea616e8fdc3bc426`, and squash merge `54594f1871a1a693528f8bdbbe132010ea4fb6db`. The merge commit has that exact base as its parent, its tree is byte-equal to the candidate tree, and the explicit required version-parity check passes.

`PR feedback: {"scheme":"github-pr-feedback/v1","repository":"iamcxa/kc-claude-plugins","pr_number":240,"layer":"single","head":"bdd4dee58e373711a793bfe397bfdff71af08c13","fingerprint":"sha256:5d2fb209f03b109e8989b6084373c839854c65a2cb03d877cdef9b9cc3a08efc","items":[{"kind":"review","id":"4943821972"}],"dispositions":[{"kind":"review","id":"4943821972","disposition":"rejected-with-reason","reason":"Approval is bound to superseded head 8af38c437201abf2f47fbbc3966af028c80daa2e and cannot satisfy candidate-bound feedback or the Native stack acknowledgement for bdd4dee5."}]}`

The merge occurred while `quinn-code-agent` remained requested and no non-author review acknowledged the Native stack exception at `bdd4dee5`. This is missing completion evidence, so no sentinel, merge guard, `PASSED`, `done`, or archive mutation is authorized. Project #4 apply, live identity/byte readback, and the identical zero-write rerun also remain pending separate authority.

## Project #4 apply checkpoint — 2026-08-16

Captain authorized Project #4 apply after an exact merged-main dry-run. Manual Actions run `31901066280` executed at merge commit `54594f1871a1a693528f8bdbbe132010ea4fb6db` against state commit `2ce631e2ee55b0d2021cfb6017d9f421877f8aae` and Project #4 node `PVT_kwHOABc8eM4BgcAp`; it completed successfully with 36 operations and zero conflicts. The operations matched the approved plan exactly: one managed-label creation, three Project field creations, ten in-place Issue updates, ten managed-label additions, ten field updates, and existing-Issue attachments only for #234 and #235. No Issue was created and every selected Issue number remained #229-#238.

Live readback confirms all ten Issues now have workflow-native short-ID title prefixes, SD entity content as their visible body, the `spacedock:managed` label, and a v2 receipt bound to the exact trunk and state commits. Project #4 contains all ten items with populated `SD Identity` and `SD Stage`; optional `SD Product` is populated only where SD supplies it. Status is `Backlog` for eight entities and `Done` for archived #234 and #235.

The already-queued scheduled run `31901116656` followed the manual apply at the same exact trunk and state commits. It completed successfully with `operations=[]` and `conflict_count=0`, proving identical-run convergence without requiring another dispatch. AC-5's external apply, live readback, identity preservation, bounded attachment, and zero-write rerun are satisfied.

Task terminalization remains blocked only by the pre-existing delivery-contract defect: PR #240 merged without a non-author exact-candidate acknowledgement of the Native stack exception. The only Quinn approval remains bound to superseded head `8af38c437201abf2f47fbbc3966af028c80daa2e`; `quinn-code-agent` is still requested on merged head `bdd4dee58e373711a793bfe397bfdff71af08c13`. No projection failure or further Project write is pending.
