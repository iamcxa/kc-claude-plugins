# Planning canvas comment trim — exact uncommitted draft

Approval provenance: Kent said “#415 註解好像太多了”, then approved with **好** the standard of removing method tutorials, old-version narratives and adjacent-code explanations while retaining terse data-safety/library facts and licence attribution. This authorizes the draft only: no product commit/push/restack, CI patch commit or PR mutation.

## Measured scope

Same declared metric: standalone `//` or `#` comment lines (including separators, excluding shebangs and `///` directives) in `.mjs`, `.ts`, `.tsx`, `.sh` under `kc-journey-map/lib`, `server`, `scripts`; includes JavaScript comments inside the shell NODE heredoc. CSS/HTML are excluded.

**Before: 164 comment lines / 1,428 total lines. After: 17 / 1,281.** Exactly 17 files, +12/-159 lines. This measures the final draft, not a quota. `measurement.json` gives per-file counts; `manifest.json` gives exact paths/file hashes; `candidate.patch` is the full delta.

| Example | Disposition and reason |
|---|---|
| Story-map 12-line method/history header | Removed: narrative method and former implementation do not explain a current code constraint. |
| Repeated CLI usage and ordinary drag/order/test narration | Removed: executable errors, code or test assertions already express it. |
| Font-size and fractional-index incident narratives | Replaced with short local warnings: zero yields invisible note text; index keys encode length. |
| Room deletion, destructive import, manual canvas content and YAML wrapping | Retained tersely at relevant operations because they define data-safety boundaries. |
| Three tldraw MIT adaptation lines | Preserved byte-for-byte as licence attribution. |

## Exact equivalence

All 17 changed files preserve every noncomment line, including whitespace and executable/string data. Existing esbuild compiled output is identical for JavaScript/TypeScript/TSX; whitespace-only compiler normalization removes comments, without syntax or identifier minification. The shell NODE heredoc is compared as JavaScript separately; remaining shell/data lines are identical and Bash syntax passes. Shebangs, reference directives and licence lines are preserved. An in-memory `fontSizeAdjustment: 1` → `0` falsifier produces different compiled output, confirming the instrument detects executable changes. No product mutation was written for that falsifier. `executable-equivalence.json` records hashes/options/results. No install, runtime suite, browser, source regeneration or reviewer ran; prior behavior evidence carries through unchanged executable content, not a new runtime PASS.

## Candidate and sibling boundary

Base `0d69be164ccdcd1b3509f3577d6bd03a468f8f36`; candidate tree `d6a0ff4ac49e6a2fca2ebc070259dd89b5c76c1b`. Proposed subject: `refactor(kc-journey-map): trim planning canvas comments`. The real index remains unstaged. The exact [local-commit packet](local-commit-review.md) is pending Captain decision.

Read-only overlap: 14 touched paths also change in PR416; 3 also change in PR417. `manifest.json` lists them. Later authorized propagation/restacking must preserve this trim and each layer's changes; overlap alone is not a conflict verdict. Siblings were not edited or restacked. Published commits/PR415/416/417/stack418, original root, old evidence, Markdown/reference/example files, executable code and services remain unchanged.

The separate pending [CI prerequisite packet](../ci-reader-bootstrap-evidence/local-commit-review.md) is not absorbed. Its workflow SHA-256 remains `bf12382df016eca71c2757a040167fad7b6855ad4eacb3bda1d69a2470d7f5ba`. Product commits/push/PR edits and CI publication remain pending separate authority.
