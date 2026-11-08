# Preservation repair evidence

Authorized scope: `dispatch/implementation-1-message-3.md`, the material review
finding on PR #812, comment 4505536959 at
`afa4523468a2e86e6c6e0467591df00bf8e51d35`.

The next numbered record is now refused if Git's index already contains it.
Otherwise the writer uses exclusive creation, so an existing worktree path also
refuses without overwriting. The refusal names the path and returns before the
record checker or builder. Cleanup's existing `wrote` flag now denotes a file
this invocation created; committed retry reuse still sets it false.

`regressions-before.log` shows all three new preservation cases fail against the
old implementation: existing untracked/staged files disappear and an index-only
entry is removed. `dispatch-stage.log` records the repaired seam suite. The
staged case deliberately gives the index and worktree different bytes, and checks
both independently. The index-only case deletes the worktree copy before running.
All cases check task bytes, state HEAD, file state and index entries remain intact.

`preservation-falsifiers.py` restores the reviewed old writer in disposable,
bytecode-free copies and runs each new case separately. Its JSON results and raw
logs are under `preservation-falsifiers/`; passing means the mutant was caught.
The same counterexamples were rerun after the local commit, with the decisive
results under `preservation-falsifiers-committed/`.

A failed advance commit leaves a pending record. A subsequent build now refuses
it instead of overwriting it. The adjusted advance test commits that preserved
record with the real `spacedock state commit`, then verifies identical committed
retry reuse succeeds. This follows the explicit refusal rule in follow-up 3.

`run-package-tests.py` reads the existing CI workflow and replays its Python
commands locally, using the declared real binary and pinned source dependency.
It leaves the optional `SD_PLUGIN_ROOT` variable unset inside child tests, as in
CI; the direct integration command receives the pinned root explicitly. Per-command
results, test/skip counts and logs are under `package-tests/`.

The original `../acceptance.sh` runner is rerun against the final local commit,
with a new output directory, preserving the first candidate's evidence. Its
stronger record-test invocation supplies `SD_PLUGIN_ROOT`, exercising the optional
real-builder case that the CI-shaped package replay skips.

No PR response, review request or product push is performed by this worker.
FO owns publication, the review reply, new-head CI and independent revalidation.
No CI configuration changed; CI cost per PR remains unmeasured.
