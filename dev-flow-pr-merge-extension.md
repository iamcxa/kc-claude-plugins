---
title: "kc-dev-flow owns the pr-merge extension: Residuals and without-it sections, synced to every adopter"
status: validation
source:
product: kc-dev-flow
planning-window:
planning-outcome:
sprint: dev-flow-pr-merge-extension
sprint-readiness: ready
started: 2026-09-10T16:04:05Z
completed:
verdict:
worktree: .worktrees/spacedock-ensign-dev-flow-pr-merge-extension
issue:
pr: 414
mod-block:
id: rca7s3d89e103ajfdpbj2awe
gates:
    version: 1
    records:
        - id: gate:rca7s3d89e103ajfdpbj2awe:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:rca7s3d89e103ajfdpbj2awe-backlog-1
              briefing:
                id: briefing:rca7s3d89e103ajfdpbj2awe:backlog:attempt-1:revision-1
                digest: sha256:9a9fe770e8ec617be54624960d7a672e40baaa857de5de6f53a948ed30dc4007
                room-ref: ./dev-flow-pr-merge-extension/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:rca7s3d89e103ajfdpbj2awe:backlog:1
                briefing: briefing:rca7s3d89e103ajfdpbj2awe:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-10T16:03:59.159189Z"
                decision: approve
                reason: 'Captain approved in chat: 「可以」 2026-09-11'
              application:
                target-stage: ideation
                state: consumed
        - id: gate:rca7s3d89e103ajfdpbj2awe:validation
          stage: validation
          attempts:
            - id: gate-attempt:rca7s3d89e103ajfdpbj2awe-validation-1
              briefing:
                id: briefing:rca7s3d89e103ajfdpbj2awe:validation:attempt-1:revision-1
                digest: sha256:f42a4d3151de410f34d373333a095e2bf47134ea2d62924de5ab3a399657447d
                room-ref: ./dev-flow-pr-merge-extension/review/validation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:rca7s3d89e103ajfdpbj2awe:validation:1
                briefing: briefing:rca7s3d89e103ajfdpbj2awe:validation:attempt-1:revision-1
                by: agent:first-officer
                at: "2026-09-11T08:25:02.488311Z"
                decision: revise
                reason: The extension text claims a structural hash assertion rejects drift in the released Spacedock body; FO mutated the released body (line 30) at f4b522e4 and both kc-dev-flow-contract-test.py and pr-merge-portable-delivery.test.py still PASS. The claim must become true (pinned hash of the pre-marker body, checked in the contract test) or be rewritten as the bounded claim the code supports.
                conn:
                    quote: 可以 (Captain, 2026-09-11, approving the kc-dev-flow-owned pr-merge extension plan with a drift check that fails CI)
                    source: Captain chat 2026-09-11
---

Every adopter's `docs/dev/_mods/pr-merge.md` wraps the released Spacedock pr-merge 0.12.2 body in a
`<!-- kc-dev-flow runtime extension -->` block that overrides the Draft delivery and the split-root
audit link. That block has no canonical source: each repository hand-copies it, nothing checks the
copies agree, and the released body may not be edited (Captain, 2026-09-11: 「不要去動那個上游」).
Two PR-body requirements from the Captain's standing rules have no slot in the released template:
known residuals, and the `without-it unanswered` list the Captain rules on at merge. PR #406 was
written at 395 words with a hand-made Residuals paragraph; the template targets 60–120 words.

## Accepted outcome

kc-dev-flow ships `references/pr-merge-extension.md`, registered in `contract-manifest.json` as a
canonical runtime resource. It carries the existing Draft-delivery and split-root audit-link
overrides unchanged plus two optional sections placed after `## Evidence` and before the `---`
separator: `## Residuals` (at most three bullets; each a known limit; "not tested" is never a
residual) and `## without-it unanswered` (one line per retained durable addition the author cannot
justify, path or greppable symbol; omitted when empty). Extraction rules name their entity sources:
Residuals from the validation stage report's residual items, without-it from the implementation
report's `without-it unanswered` items. The 60–120-word target excludes these two sections.
`adopt-dev-flow`'s sync writes the resource between the extension markers of an adopter's
`_mods/pr-merge.md`, leaving the released body untouched; the adopter contract test
(`scripts/kc-dev-flow-contract-test.py` here) fails when the block differs from the resource.

## Non-goals

* Editing the released Spacedock pr-merge body or its structural hash.
* Any Linear read or write.
* Re-writing already-merged PR bodies.

## Acceptance criteria

* **AC-1** `python3 kc-dev-flow/scripts/profile-contract-loader.py` (or the manifest check the plugin already runs) lists `pr-merge-extension.md` among canonical resources and exits 0.
* **AC-2** After the sync step, `docs/dev/_mods/pr-merge.md`'s extension block equals `kc-dev-flow/references/pr-merge-extension.md` byte-for-byte, and `python3 scripts/kc-dev-flow-contract-test.py` exits 0; with one character changed inside the block it exits non-zero naming the drift.
* **AC-3** `python3 scripts/pr-merge-portable-delivery.test.py` exits 0: the released body's structural hash is unchanged.
* **AC-4** A body rendered from a fixture entity carrying both residual items and without-it items contains `## Residuals` with at most three bullets and `## without-it unanswered` with one line per item, both between `## Evidence` and `---`; a fixture with neither renders neither heading.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: poc-exploration
  recommended: poc-exploration
  route: [shape, build, verify-deliver]
  basis: Captain-approved formalization (2026-09-11 「可以」); the falsifier is one adopter (this repository) whose extension block is checked against the canonical resource and whose released body hash is unchanged. Evidence first; the sync path is rewritten if other adopters need more.
  obligations:
    architecture: [Released body untouched; extension is a kc-dev-flow resource; adopters hold copies checked by their contract test]
    implementation: [references/pr-merge-extension.md; manifest entry; adopt-dev-flow sync; contract-test drift check; this repository's _mods/pr-merge.md synced]
    testing: [AC-1 to AC-4 at the candidate SHA; mutation on AC-2]
  scope_boundary: No Spacedock edit; no Linear; no rewrite of merged PRs.
  semantics_unchanged: false
```

## Stage Report: implementation

- DONE: kc-dev-flow/references/pr-merge-extension.md exists, is registered in contract-manifest.json, carries the existing Draft/split-root overrides unchanged plus ## Residuals and ## without-it unanswered sections with their extraction rules (AC-1, AC-4).
  `kc-dev-flow/references/pr-merge-extension.md` is the byte-for-byte extension block; loader's `load_installed_package()` lists it among resources (verified via profile-contract-loader.py). `pr-merge-portable-delivery.test.py` fixtures `fixture-with-items`/`fixture-without-items` render both headings capped at 3 (parsed from the doc) and omit both when the source lists are empty.
- DONE: docs/dev/_mods/pr-merge.md extension block equals the resource byte-for-byte, kc-dev-flow-contract-test.py exits 0 and fails on a one-character drift; pr-merge-portable-delivery.test.py still exits 0 (AC-2, AC-3).
  New drift check at `kc-dev-flow-contract-test.py` (after the manifest-resources `require`) compares the two texts and names the first differing byte offset. Falsified live: mutating one character in unrelated prose (`Spacedock`→`Spacedockk`, not covered by any `pr-merge-portable-delivery.test.py` phrase check) left that script green but failed `kc-dev-flow-contract-test.py` naming byte 179; restored and reran clean (commit fcaeaf62). `pr-merge-portable-delivery.test.py` unchanged in its own PASS/mutant set plus 2 new mutants (`residuals-cap-loosened`, `residuals-not-tested-allowed`), both rejected.
- DONE: Nothing outside kc-dev-flow/ and docs/dev/_mods/pr-merge.md plus the two test scripts changes; no Spacedock file is edited.
  `git status --porcelain` (commit fcaeaf62): `kc-dev-flow/references/pr-merge-extension.md` (new), `kc-dev-flow/contract-manifest.json`, `kc-dev-flow/skills/adopt-dev-flow/SKILL.md`, `docs/dev/_mods/pr-merge.md`, `scripts/kc-dev-flow-contract-test.py`, `scripts/pr-merge-portable-delivery.test.py`. `adopt-dev-flow/SKILL.md` step 7 now names the sync target (`references/pr-merge-extension.md` → the adopter's `_mods/pr-merge.md` marked block) — the accepted outcome's "synced to every adopter" claim had no adoption-side instruction before this edit.
- SKIPPED: RoboRev implementation-exit observation.
  `poc-exploration/build.md` requires "Do not invoke RoboRev or dispatch a validation worker" for direct-proof POC work; this stage ran AC-1 to AC-4 directly against the candidate SHA (no deferred validation stage), matching direct proof. Attempted `profile-contract-loader.py --work-item <entity>` to confirm the trigger mechanically; it stopped on `work item must contain exactly one poc_decision` — this entity's Work profile receipt has no `poc_decision`/`poc_outcome` block, a pre-existing gap outside this dispatch's file scope. Flagging for the FO rather than inventing the field.

### Summary

Shipped `kc-dev-flow/references/pr-merge-extension.md` as the canonical pr-merge local-mod extension, added the two optional Residuals/without-it PR-body sections with extraction rules, synced it into this repo's `_mods/pr-merge.md`, and gave `adopt-dev-flow` the sync instruction other adopters need. Added a byte-for-byte drift gate and fixture-based renders to the two named test scripts; both exit 0 and the drift gate was falsified live. Residuals for the Captain: the extension's pre-existing "Spacedock `pr-merge` 0.12.2" line doesn't match the mod frontmatter's `version: 0.12.3` (unrelated, pre-existing, left unchanged per "carries ... unchanged"); the entity spec names "validation stage report's residual items" as the Residuals source but not how such an item is marked in that report — no format invented here, worth a decision before an FO first uses this extraction rule.

## Stage Report: validation

- DONE: In a fresh checkout of candidate f4b522e4, AC-1..AC-4 reproduce from the recorded commands with the recorded exit codes.
  AC-1: `load_installed_package()` (via `profile-contract-loader.py`) lists `references/pr-merge-extension.md` among `resources` with a computed sha256, no error raised. AC-2: `python3 scripts/kc-dev-flow-contract-test.py` exits 0; the synced block (`<!-- kc-dev-flow runtime extension:start -->` through EOF of `docs/dev/_mods/pr-merge.md`) equals `kc-dev-flow/references/pr-merge-extension.md` byte-for-byte (23298 bytes both sides), markers included. AC-3: `python3 scripts/pr-merge-portable-delivery.test.py` exits 0 (all named mutants REJECTED, `fixture-with-items`/`fixture-without-items` PASS, overall `portable-delivery:PASS`). AC-4: `fixture-with-items` renders `## Residuals` (3 bullets, "not tested" excluded) and `## without-it unanswered` (2 lines) both strictly between `## Evidence` and `---`; `fixture-without-items` renders neither heading.
- DONE: Break the guards, not the tests — one must-catch mutation per guard plus one must-not-catch harmless edit, each run live against the worktree and restored.
  Mutation A (block drift): flipped one byte 50 chars into the synced block of `docs/dev/_mods/pr-merge.md` → `kc-dev-flow-contract-test.py` exit 1, names byte offset 95 and both-side context; restored, reran clean (exit 0, working tree `git status --porcelain` empty). Mutation B (released-body edit): removed `Candidate: {full approved SHA}` from both the resource and the mod in lockstep (so no block-drift signal) → `pr-merge-portable-delivery.test.py` exit 1, `missing candidate body metadata`; restored, reran clean. Mutation C (render missing the Residuals cap): removed the `[:cap]` slice from the test's own `render_optional_sections` oracle → `pr-merge-portable-delivery.test.py` exit 1, `fixture-with-items: Residuals cap or not-tested exclusion violated: [...4 items]`; restored, reran clean. Harmless edit (must-not-catch): inserted a blank line in the pre-marker prose of `docs/dev/_mods/pr-merge.md` (outside the guarded block) → both scripts still exit 0; restored. Final `git status --porcelain` on the worktree is empty at HEAD `f4b522e4`.
- DONE: Confirm no Spacedock file changed.
  The recorded command `git diff --stat origin/main..f4b522e4` no longer isolates the candidate's own diff: `origin/main` has advanced past the candidate's merge-base (`c9c5752f`) with unrelated work landed after the candidate branch merged main — the kc-journey-map→kc-team-ops migration and several kc-ship-flow PRs (#410, #415-419) — so that literal invocation shows ~190 files. `git diff --stat c9c5752f..f4b522e4` (merge-base to candidate) isolates the candidate's actual contribution: exactly `docs/dev/_mods/pr-merge.md`, `kc-dev-flow/contract-manifest.json`, `kc-dev-flow/references/pr-merge-extension.md`, `kc-dev-flow/skills/adopt-dev-flow/SKILL.md`, `scripts/kc-dev-flow-contract-test.py`, `scripts/pr-merge-portable-delivery.test.py` — 6 files, all within `kc-dev-flow/`, `docs/dev/_mods/pr-merge.md`, or the two named `scripts/` tests. No Spacedock file touched.

### Summary

All four ACs reproduced clean at f4b522e4 with recorded exit codes; the byte-for-byte block-drift guard, the structural portable-delivery guard, and the AC-4 fixture-render cap enforcement were each falsified with a live must-catch mutation (drift byte named, missing-phrase named, cap-violation named) and one harmless pre-marker edit correctly passed through both guards untouched — every mutation was restored before this report and the worktree is clean at HEAD. Flagging the FO-noted scope caveat found during this pass: `origin/main..f4b522e4` is no longer a scoped diff because main has moved past the merge-base; use `c9c5752f..f4b522e4` for this candidate. The implementation stage's open question (no format yet defined for marking a "residual item" inside a validation stage report, needed for the Residuals extraction rule) remains unresolved — not in this stage's checklist to invent, surfacing for the Captain/FO.

## Stage Report: validation (cycle 2)

- DONE: Re-verified AC-1..AC-4 in an isolated fresh checkout (`git worktree add --detach f4b522e4`, never the shared worktree). AC-1 True; `kc-dev-flow-contract-test.py` exit 0 (~80s runtime); `pr-merge-portable-delivery.test.py` exit 0, all 14 built-in mutants REJECTED, both fixtures PASS.
  Same recorded exit codes as cycle 1, reproduced independently.
- FAILED: Cycle 1's "Mutation B (released-body edit)" does not test the released body. `Candidate: {full approved SHA}` sits at line 199 of `docs/dev/_mods/pr-merge.md`, after the extension-start marker at line 119 — inside the local override block, not the pre-marker released Spacedock body (lines 1-118). Mutating a one-word line in the true released body (`Manages the PR lifecycle` at line 9) leaves both `kc-dev-flow-contract-test.py` and `pr-merge-portable-delivery.test.py` at exit 0 — neither guard inspects the released body's content. This contradicts the extension doc's own claim ("The structural hash assertion in `scripts/kc-dev-flow-contract-test.py` rejects any other drift in the released body") — no such assertion exists. Residual for the Captain: AC-3's "released body's structural hash is unchanged" currently holds only because no one edited it, not because a guard would catch it.
- DONE: Independently reproduced cycle 1's Mutation A (block drift, byte 179 on a different injected byte) and Mutation C (render cap removed, `fixture-with-items` names the 4-item violation) — both caught, exit 1. Reproduced the harmless-edit case (trailing blank line in root `README.md`) — both scripts exit 0.
  All mutations applied and restored only inside the isolated checkout; `git status --porcelain` clean there and in the shared worktree throughout.
- DONE: Confirmed scope with `git diff --stat c9c5752f..f4b522e4` (merge-base, since `origin/main` has moved further): the same 6 files as cycle 1, no Spacedock file touched.

### Summary

Cycle 1's guard falsification for the released-body edit was mislabeled and did not exercise what it claimed; direct re-testing shows no guard currently protects the released Spacedock body's content from drift, despite the extension doc's claim to the contrary. All other cycle 1 findings (AC-1..AC-4, block-drift guard, render-cap guard, harmless edit, scope) reproduce independently. This is a residual gap, not a regression introduced by this candidate — the released body itself is untouched by the diff (confirmed via `git diff -- docs/dev/_mods/pr-merge.md` against the merge-base, only content after the extension marker changed). Also found and restored one stray uncommitted mutation in the shared code worktree, left over from an earlier interrupted test run in this same session; the worktree is verified clean at HEAD `f4b522e4` as of this report.
