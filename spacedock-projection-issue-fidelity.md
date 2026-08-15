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
worktree: /Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1/.context/worktrees/spacedock-projection-issue-fidelity
issue:
pr: "#240"
mod-block:
design: required
lane: main
---

## Problem

Projector-owned Issues currently replace the Spacedock entity body with visible projection metadata and rely on a mutable hidden body receipt as the only source-to-Issue lookup key. This makes Project views redundant, leaves the actual task unreadable on GitHub, and can lose or duplicate the mapping when a user edits or removes the receipt.

## Proposed approach

Repair the existing projector seam rather than create another synchronizer. Render each projector-owned Issue body from the entity Markdown after frontmatter, prefix its title with the workflow-native short entity ID, keep stage/product/status in Project fields, add one `spacedock:managed` repository label, and add a Project text field named `SD Identity` containing a stable repository/workflow/entity key. Projector-owned Issue title and body are derived bytes: edit the SD entity, not the GitHub projection. A v2 managed Issue requires an agreeing hidden receipt and `SD Identity`; a missing or disagreeing anchor is a conflict that requires operator repair, while the label is only a visible marker and collision guard. Recognize the exact v1 receipt only for the bounded first migration, then emit v2; do not retain body-drift or general self-healing behavior. Linked human Issues remain byte-read-only.

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
Verified by: v2 fixtures require an agreeing receipt and `SD Identity`; a missing or disagreeing anchor, duplicate anchor, or label-only candidate produces `CONFLICT` and cannot plan `CREATE`. One exact v1 receipt may migrate the ten approved dogfood Issues in place and emits v2 plus `SD Identity`; no other repair path exists. Falsified by: deleting a v2 receipt or identity field can plan a second Issue, editing `SD Identity` silently rebinds an Issue, or a non-v1 candidate enters migration.

**AC-4 — Issue ownership determines whether GitHub bytes are writable.**
Verified by: a projector-owned v2 Issue with an intact agreeing identity is restored from SD after a GitHub title/body edit, while a linked human Issue preserves every title/body/state/label byte and receives only managed Project fields. No GitHub edit becomes SD input. Falsified by: projector-owned GitHub prose survives as a second content authority, a linked Issue byte is patched, or any GitHub content is written to the state branch.

**AC-5 — The ten Project #1 dogfood Issues migrate in place and converge.**
Verified by: an exact-state dry-run names only existing Issues #229-#238, stays below the approved mutation cap, and predicts no new Issue or Project item; after authorized apply, live readback preserves all ten numbers/URLs/comments and an identical rerun records zero operations. Falsified by: any duplicate, missing item, foreign-item mutation, or non-empty identical rerun.

## Test plan

- Replace the recovery/drift fixtures with RED fixtures for full-population short IDs, entity-body rendering, text-field schema/apply, managed-label preservation, exact v1-to-v2 migration, v2 anchor refusal, projector-owned overwrite, and linked-Issue byte preservation.
- Run the scoped projector suite, then `scripts/kc-dev-flow-contract-test.py` and repository-required lint/parity checks earned by the diff.
- Generate an exact `origin/main` plus `spacedock-state/dev` Project #1 dry-run before requesting external apply.

## Measurement

One user-visible journey and one projector lifecycle surface. Success is ten preserved Issue identities, readable bodies, deterministic short-ID titles, zero ambiguous matches, no steady-state repair lifecycle, and a zero-operation rerun.

## Doc diff

Update the setup skill's mapping contract and runtime receipt/refusal guidance. Record this S3 repair before the status-update item in ROADMAP. No PRODUCT or ARCHITECTURE change is required because SD remains authoritative and the existing one-way topology is unchanged.

## Out of scope

- GitHub-to-SD content or lifecycle writeback.
- Editing linked/human Issue title, body, state, or labels.
- Per-stage/product repository labels, organization Issue fields, or a second mapping ledger.
- Sprint-to-Milestone enablement, status-update publication, Relay/CarLove rollout, or LLM-authored projection content.

## Captain-approved route revision — 2026-08-15

After PR #240 reached provider approval, the captain challenged whether the 1,628-line gross diff was necessary and approved the smaller route proposed in the same discussion. The pre-change surface set was readable rendering plus three-signal auto-recovery, body-drift preservation, and general legacy-summary migration. The accepted replacement keeps readable rendering, structured identity, collision refusal, and one exact v1-to-v2 dogfood migration, while removing steady-state auto-repair and the `BODY_DRIFT` lifecycle. Projector-owned Issues are explicitly derived and overwritable; human prose belongs in SD or in a linked Issue.

The route is reversible before merge and external apply. Implementation must return to this authority if the exact ten-Issue migration cannot complete without general recovery, if missing v2 anchors can reach `CREATE`, or if linked Issue bytes require mutation. Product commit, push, Ready/merge, and Project apply remain separately gated.

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
