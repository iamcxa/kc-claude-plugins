# implementation-6

Dispatched: e2524e93025dd0d5d9217b4d722c2b169d01fda6 (workflow checkout, kc-dev-flow-2 0.21.0 README)
Model: sonnet

Follow-up message to the live implementation worker: FO fix authorization (Review-finding disposition step 3) after its phase-1 reproduction confirmed all four Codex round-2 items and widened item 1 to journey-reconcile and item 4 to duplicate story ids.

## Checklist

Same checklist as implementation-5.

## Scope notes

Fix all four items, with both widenings:
1. P1: `audit` (map_footprint.py) and `journey-reconcile.mjs` require the supplied workflow dir to be a directory containing README.md, else a non-zero path error naming the path. A missing `_archive` under a valid workflow is a legitimate zero, printed as `archive none: <path> does not exist`. Tests, smoke and acceptance steps that pass a README-less temp workflow dir (AC-6 runs included) get a README; each such change named in the report.
2. P2: each amendment match bounded to its own section; an amendment with no `Captain:` line is not a source.
3. P1: `already` only when stored answer equals the footprint's answer, status is `answered` and the ref matches; otherwise `conflict`, nothing written for that question; reconcile counts it in `unfolded`. Limit line: an intentionally reworded answer stays a conflict until a new ruling replaces it.
4. P2: fold requires exactly one matching story and one matching question, else refuse naming both, exit 1, no draft.
Tests that fail without each fix (mutation runs), roborev gate per PR (bases c811de1f, f320d6d3), push #627, merge into -map, push #628, CI green, stage report committed, completion to `main`.
