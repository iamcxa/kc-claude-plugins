# implementation-4

Dispatched: e2524e93025dd0d5d9217b4d722c2b169d01fda6 (workflow checkout, kc-dev-flow-2 0.21.0 README)
Model: sonnet

Follow-up message to the live implementation worker: FO fix authorization (Review-finding disposition step 3) after its phase-1 reproduction confirmed all four items (item 3 is a refusal of a valid input, not a corrupt draft).

## Checklist

Same checklist as implementation-3.

## Scope notes

Fix all four items:
1. P1 map_footprint.py: a declared state checkout that is missing is a configuration error (non-zero exit naming the missing path), for audit and every other command that resolves the state dir.
2. P2 map_footprint.py: `Map footprints: not needed: <reason>` with one or more valid footprint lines makes `check` exit 1 naming the contradiction.
3. P2 journey-fold.mjs: at a non-newline end of file, insert a newline before the folded lines so the valid input applies; keep the parse-equality guard unchanged.
4. Polish journey-reconcile: a test asserting the CLI exits 1 on a duplicate story id; prefer spawning node with a stub `spacedock` on PATH over exporting `main`.
Each fix gets a test that fails without it, shown by a mutation run. Roborev gate per PR, push #627, merge (not rebase) its branch into the -map branch, push #628, CI on both heads, stage report committed with `spacedock state commit`. Completion message to `main`.
