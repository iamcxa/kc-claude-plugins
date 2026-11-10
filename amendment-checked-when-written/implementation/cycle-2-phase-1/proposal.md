# Cycle 2 phase 1: F3 investigation and unapplied repair proposal

Candidate: `d7502656c765e36ce3d24be8602862ccc2551254`. The product checkout is unchanged and clean. F3 still violates AC-2; this is an investigation report, not a repaired candidate or a validation verdict.

## Independent reproduction

`candidate-tests.log` has five methods: one expected assertion failure and four passing controls, with no errors. The failing method exercises the real candidate laws CLI against a temporary state Git repository. A valid amendment receives an actual unmarked replacement and a `~~~md` example whose fake AC-9 carries the marker. The parser reports no structural issue and L3 remains clean, but L4 exits 0 with no diagnostic. Changing only the example fence to backticks exposes the unmarked event. Real marked replacements, no-replacement waivers and record-only amendments remain green for both delimiters.

The reproducer does not create an unreadable task or exercise F2. It uses `python3 -B`, isolated fixture repositories and temporary package copies without bytecode; it verifies the product HEAD/status at exit.

## Smallest proposed product change

In `design_surfaces.move_defects` only, replace the live-section call to the shared backtick-only `unfenced` with an inline visible-line filter using the already defined `AMENDMENT_FENCE`. Ignore opening/inside/closing lines, and close only on the same delimiter character, sufficient delimiter length and no trailing content. Feed the resulting visible lines to the existing `section` and `declarations` calls. This confines the change to the input of the L4-only move predicate and follows the fence grammar already recognized by amendment parsing.

`proposed-input.diff` is concrete but unapplied. The proposed product scope is `kc-dev-flow-2/scripts/design_surfaces.py` and a focused backtick/tilde regression in `kc-dev-flow-2/scripts/test_laws_check.py`. No change is needed to the laws walker, event delta, exception accumulation, registry, documentation, workflow or versions. Existing `unmarked`, `parse_amendments`, structural-entry filtering and grouped output stay as written. Changing the global `unfenced` would affect other entry points and exceed the compatibility boundary, so it is not this proposal.

## Compatibility and bounded execution proof

The package AST call search finds `move_defects` called only twice, both inside L4. `proposal.py` asserts that the module AST outside this one function is identical, including `unfenced`, `unmarked`, `check_amendments`, `check_task`, `check_seed_fields` and `main`. Thus the public check/seed code paths do not acquire the new filter. `gate-comparison.json` additionally records 32 matching candidate/proposal check-or-seed result pairs across eight distinct synthetic inputs, including the reproduced input. The inherited gate behavior on the example remains unchanged; it is not silently repaired here. This is source isolation plus focused CLI comparison, not a rerun of the entire historical check/seed corpus.

In a disposable package copy only, `proposal-tests.log` passes the same five methods, and `proposal-existing-l4.log` passes all 14 existing L4 regressions, including the Cycle 1 partial/growth/mixed cases and heading/sibling controls. These are analysis probes of the unapplied proposal, not fixed-candidate validation.

## Historical impact

`corpus-helper-comparison.json` independently compares original/proposed `move_defects` results on every old/new task blob modified by a non-merge commit in the three fixed validation ranges, deduplicated within each history: dev2 3,855, qnow 2,873, relay 2,539. The batched Git read found no undecodable or tilde-fenced task blob and no changed defect result across these 9,267 per-history content versions. Counts describe content versions, not events or users.

`seven-events.json` separately exercises the real first-parent L4 function for each of the seven named introducing commits, then repeats with only its imported move predicate replaced in memory by the proposal. All seven event counts, headlines and grouped diagnostics match exactly. The unchanged walk/delta plus the all-blob predicate comparison support no event change within the fixed ranges. No full historical CLI run with a patched product candidate, fresh remote-tip scan or hosted run is claimed.

## Stop boundary

F2 is outside this repair and no exception-handling path is changed or probed. Shared fence handling and public check/seed verdicts are preserved by the proposed isolation; only the new L4 input behavior changes for fenced examples. FO authorization is still required before applying the product patch, promoting the regression, making a product commit or repeating candidate validation. Product publication, PR writes, RoboRev, release/adoption and AC-7 hosted proof remain outside this phase.
