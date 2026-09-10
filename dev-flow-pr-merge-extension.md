---
title: "kc-dev-flow owns the pr-merge extension: Residuals and without-it sections, synced to every adopter"
status: backlog
source:
product: kc-dev-flow
planning-window:
planning-outcome:
sprint: dev-flow-pr-merge-extension
sprint-readiness: ready
started:
completed:
verdict:
worktree:
issue:
pr:
mod-block:
id: rca7s3d89e103ajfdpbj2awe
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
