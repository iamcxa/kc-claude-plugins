feat(kc-dev-flow-2): sanitize public state writes and add opt-in git guards

Merging stops the home directory being written by the package's dispatch records and newly sealed text evidence. No push is refused until the guard is installed; every class defaults to warn.

Stage and special-role runtime prompts retain real paths. Existing absolute records and new `~/` records both verify, and evidence matching its existing digest is preserved. New or changed UTF-8 evidence, including supplied gzip text, is rewritten before hashing and compression.

The optional installer puts pre-commit and pre-push hooks on one linked state worktree, using an identifier list outside repositories. Hooks scan added text, binary bytes and gzip content; push checks examine each commit, so a later deletion cannot hide a transient identifier. Refusals name the file, class and commit without printing matched text. Missing, stale or partial protection is reported before dispatch. The shared-hook alternative preserves existing hooks and limits the identifier scan to state branches.

Validation: real throwaway dispatch, sealed evidence over 256 KiB, refused commits and pushes, accepted clean pushes, mode changes and product-worktree isolation. Seven historical task folders retain the baseline record-check result; one known historical digest mismatch is unchanged. 222 distinct behavioral checks: 221 passed and one builder fixture skipped because SD_PLUGIN_ROOT was not supplied (the real dispatch was exercised separately); eight product mutations triggered their named test failures, plus an injected synthetic identifier made the artifact scan fail. Candidate: `0c68231ca9147a9833846b47a36e2fc27846cf66`. No live installation, product push or PR creation was performed by the worker. No version bump.

Known residuals:
- Gate summaries are stored verbatim by Spacedock (inferred from stored bytes, not traced in its source).
- Commit-metadata email is unchanged.
- The Captain still decides live installation and initial refusing classes; warn-mode classes can still reach the remote.
- The owner's list covers four adopters' names-only slug lists; the fifth adopter's names and hostnames outside its pattern are absent.
- Rewriting retained patches may prevent verbatim application. Binary evidence is left unchanged for the guard to inspect.

CI cost per PR: not measured; CI configuration is unchanged. FO owns publication, Draft PR, RoboRev and hosted CI review.
