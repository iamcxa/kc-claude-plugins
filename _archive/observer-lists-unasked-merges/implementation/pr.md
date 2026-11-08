feat(kc-dev-flow-2): audit merges against saved task asks

List PRs merged during an observer window against saved merge asks across this repository's local and fetched spacedock-state branches. A matching PR and head is carried; a different recorded head is a violation; a missing record is explicitly inconclusive because approval may exist in chat or outside the readable state.

Recognize release-please, workflow sync and learning PRs separately, collapse findings quoted in earlier committed observer reports, and teach the observer to report the result without blocking archives.

Validation:
- Live historical replay: 54 of 82 carried, with the exact eight expected gaps including #785.
- 17 behavioral tests and five reverse mutations; #727 also replayed as carried and as a head mismatch.
- Native candidate observer report includes merge evidence; the base 0.35.0 observer control includes none.
- Independent recount over the approved 54-window fixture: median +60, max +320 words with chronological verbatim-report collapse.
- Package checks and local suite evidence are in the task's implementation artifacts.

The existing CI path filters and job remain unchanged; one step runs the new tests. Cost per PR was not measured.

roborev not run: FO owns the local review, publication, Draft PR and CI checks under the Paseo worker handoff. No product branch was pushed and no PR was opened by this worker.
