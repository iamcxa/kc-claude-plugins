# Committed comment removal and local stack propagation

Approval provenance: Kent instructed **“移除冗餘後提交”** after the two pending comment drafts were identified. This authorized those exact local commits and necessary reversible local propagation, not remote publication or a new audit.

`exact-comment-commits.json` records the two ordinary approved commits: planning `c035e3ee792effb2708f646c2761d70ac17d9dbb` (tree `d6a0ff4ac49e6a2fca2ebc070259dd89b5c76c1b`), inspection `77732892d2024abdae7589d576f2e3aabca01275` (tree `7711a3d343cedaae24bc007928c2cc32702d0d57`). Parents/subjects and staged paths matched the exact packets; no hook bypass. `starting-refs.json` retains original refs/trees for recovery.

## Final local stack

| Branch | Original head | Final head | Final tree |
|---|---|---|---|
| `codex/journey-planning` | `0d69be164ccdcd1b3509f3577d6bd03a468f8f36` | `c035e3ee792effb2708f646c2761d70ac17d9dbb` | `d6a0ff4ac49e6a2fca2ebc070259dd89b5c76c1b` |
| `codex/journey-release-inspection` | `818260a8c14b504dae8d3989ba9c710226255b74` | `d339355faf2c2833df91cf9dde42a5ee12098341` | `04c240da4ceee87ea3196273fccde614e22dc6c3` |
| `codex/journey-local-progress` | `a5c08cbdf812826125decb6b55a286c4bcd2f1be` | `36a969a6f890a63c541fad4bfa30071ac7115c64` | `368a83650320d72314ae84b12385a230bdc12a06` |

Ordinary explicit-base rebases replayed the middle's feature and trim onto the new bottom, then the top's progress and CI commits onto the new middle. No product commit was skipped. Middle replay had 15 feature-overlap hunks in 11 files, then two comment-only header conflicts; top replay had two render hunks. Each retained the incoming layer's executable changes and composed only approved comment removals/consolidations. No whole-file ours/theirs selection or behavior decision. Resolution records are retained; all owned worktrees are clean with correct ancestry. Original root, other worktrees and old snapshots/evidence remain unchanged.

`final-equivalence.json` compares each final layer with its starting same-layer head: exact nonblank noncomment lines and existing esbuild output match, licence/shebang/type directives remain, and shell heredoc/data are handled separately with syntax checks. A known in-memory executable mutation still changes compiler output. `no-comment-reintroduction.json` confirms removed explanatory text was not reintroduced. No runtime/browser/test suite, install or reviewer ran. The CI workflow remains byte-identical at SHA-256 `bf12382df016eca71c2757a040167fad7b6855ad4eacb3bda1d69a2470d7f5ba`; no version change.

Same whole-source metric (standalone comments in .mjs/.ts/.tsx/.sh, excluding shebang/three-slash directives): planning 164 → 17; inspection 301 → 31; progress 300 → 32. These include inherited trims and do not claim a new PR417 comment audit. The earlier PR416-only draft remained 148 → 17 incremental lines. Exact counts/paths/generated shares are in `final-comment-metrics.json`, `final-stack.json` and `unit-N-files.json`.

[Full publication packet](push-review.md) and `publication.json` bind live old remote heads, proposed bases/candidates, explicit per-ref leases, unchanged titles and mode-0600 full body files/hashes. Bodies preserve relevant prior proof and label new-head hosted checks pending; previous CI evidence is historical and cost per PR unmeasured. Published PR415/416/417 and native stack418 remain Draft and unchanged. Captain stack push/body-update authority is next.
