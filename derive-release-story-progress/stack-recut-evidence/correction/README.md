# Stable story identity correction

Producer closure: the same-wording second-story edit now changes the requested ID
in layers 2 and 3. Distinct-wording controls pass; source hashes remain unchanged.
The initial defect is preserved in both red runtime proofs and the independent
reviewer's original evidence. Focused independent re-review is still pending.

The promoted patch replaces text-based selection with the existing layer-4 ID
selection and stale-wording refusal. It is +5/-1 in `read.mjs`, with no new final
product code or tests. `../equivalence.json` proves corrected layers 2/3 differ
from their initial trees only by this exact existing block; layer 3's old exact
extraction-tree condition is qualified by `promoted-layer-3.patch`. Final layer-4/5
trees are unchanged, and `../patch-proof.json` proves all five adjacent patches.

The real-server probe runs a same-wording case that failed at both original trees,
then a distinct-wording control. Against corrected trees both cases return CLI exit
0, preserve the source hash, and edit only the expected `a-2` story. The stale-wording
probe exercises the promoted guard: no story is changed if its source wording no
longer matches the canvas edit's previous wording. Replacing the promoted selector
with text search reproduces the recorded red outcome.

Run the temporary regression probe with the task's declared Node/runtime dependencies:

```bash
RECUT_SNAPSHOT_ROOT=<code-worktree>/.context RECUT_LAYER=2 RECUT_PROOF_DIR=<scratch>/layer-2 node same-wording-probe.mjs
RECUT_SNAPSHOT_ROOT=<code-worktree>/.context RECUT_LAYER=3 RECUT_PROOF_DIR=<scratch>/layer-3 node same-wording-probe.mjs
RECUT_SNAPSHOT_ROOT=<code-worktree>/.context RECUT_PROOF_DIR=<scratch>/stale node stale-wording-probe.mjs
```

`RECUT_PROOF_DIR` must be a new owned scratch directory; the probe creates fixture
YAML, room databases and JSON output there. Each real-server run stops its owned
process. Original source snapshots remain in the code worktree's
`.context/rejected-layer-2` and `.context/rejected-layer-3`; raw original patches,
indexes and review packet remain in the task artifact root's `initial-rejected/`.

Scoped follow-up checks passed: 10 layer-2 read tests and 16 layer-3 read tests,
plus one-page and five-page server smoke/readback. No install, export/persistence,
full unaffected layer-4/5 suite, provider review, or CI run was repeated. CI cost
remains unmeasured, RoboRev requests remain zero, and existing runtime/icon limits
are unchanged. No product commits, pushes, PRs, task state/gates or approvals changed.

## Immutable correction binding

This correction record is frozen for the focused independent re-review.
`closure-proof.json` SHA-256: `670cc5e35da28cd56a938ebae35f4b3c1f4fe2353f6b78bc2d47437e448d3367`.
It binds both rejected and corrected trees, exact promoted patch hashes, observed
red/green outcomes, distinct-wording controls, source preservation, and scoped checks.
Any later correction must use a new record, not rewrite this proof.
