# PR416 incremental comment trim — uncommitted

Approval provenance: Kent said **“416 也有一樣的問題”** after approving the PR415 comment-trim standard. This applies that standard only to descriptive comments introduced or materially changed by published PR416. No product commit/push/restack or PR edit is authorized.

## Consistent measurement

Published incremental range: `0d69be164ccdcd1b3509f3577d6bd03a468f8f36` → `818260a8c14b504dae8d3989ba9c710226255b74`. The unified-zero diff identifies **148 added/changed standalone comment lines**. The corrected incremental diff contains **17**, independently recounted against the same published base. Whole-source comments are **301 → 170**; the **153 inherited comment lines remain unchanged**. Whole-source lines: 2,681 → 2,550. Exactly 20 edited files, +13/-144.

The metric matches the earlier trim: `.mjs`, `.ts`, `.tsx`, `.sh` under `kc-journey-map/lib`, `server`, `scripts`; standalone `//`/`#` lines including separators, excluding shebangs and `///` directives. JavaScript heredoc comments are included; CSS/HTML are excluded. `measurement.json` separates incremental and whole-source counts; `incremental-comment-lines.json` records original eligible line numbers.

| Cut or keep | Reason |
|---|---|
| Function-map tactical-method header; fixture/migration history | Removed method teaching and obsolete narrative. |
| Repeated CLI usage; ordinary lint mutation-test explanations | Removed facts already explicit in usage errors, assertions or code. |
| tldraw note height, deep-link camera normalization and child-border coordinates | Kept terse non-obvious library constraints near their consumers. |
| Unsafe constraint inverse, cross-page ambiguity, partial-board order and empty-selection deletion | Kept concise readback/data-safety boundaries. |
| Tracked git-grep paths and self-citation exclusions | Consolidated evidence limitations beside the implementing lint. |

Two new lines embedded in otherwise inherited blocks (`storymap.mjs` header and `App.tsx` upload note) remain untouched so this draft cannot orphan or rewrite inherited PR415 prose. Their whole blocks are already covered by the separate bottom trim. All licence attribution, shebangs and type references remain unchanged.

## Proof and propagation

`executable-equivalence.json` reuses the existing esbuild comparison: all 20 changed files preserve exact noncomment lines and compiled output; shell/heredoc content is handled separately and Bash syntax passes. The prior in-memory font-size mutation still changes compiled output. Every inherited comment line is retained in order. No install, runtime/browser/test suite, source generation, standing harness or reviewer ran; prior behavior evidence carries through unchanged executable content, not a new runtime PASS.

Base `818260a8c14b504dae8d3989ba9c710226255b74`; candidate tree `7711a3d343cedaae24bc007928c2cc32702d0d57`. Exact files/hashes, overlaps and full patch are in `manifest.json` and `candidate.patch`. [Local-commit packet](local-commit-review.md) remains pending.

PR417 changes three touched paths: `records.mjs`, `render.mjs`, `storymap.mjs`. Later approved propagation must compose both comment drafts with those product changes; no restack/conflict resolution was attempted. Exact pending-patch byte comparisons confirm the PR415 trim and PR417 +15-line CI repair remain unchanged. The [bottom trim](../planning-comment-trim-evidence/local-commit-review.md) and [CI packet](../ci-reader-bootstrap-evidence/local-commit-review.md) stay separate. Published heads/PRs/stack, original root, other worktrees and immutable evidence are preserved.
