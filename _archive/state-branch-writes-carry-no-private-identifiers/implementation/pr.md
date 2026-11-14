feat(kc-dev-flow-2): sanitize public state writes and add opt-in git guards

Merging stops the home directory being written by the package's dispatch records and newly sealed text evidence. No push is refused until the guard is installed; every class defaults to warn.

Stage and special-role runtime prompts retain real paths. Existing absolute records and new `~/` records both verify, and evidence matching its existing digest is preserved. New or changed UTF-8 evidence, including supplied gzip text, is rewritten before hashing and compression.

The optional installer puts pre-commit and pre-push hooks on one linked state worktree, using an identifier list outside repositories. Hooks scan path names, added text, binary bytes and gzip content; push checks examine each commit, so a later deletion cannot hide a transient identifier. Refusals name the file, class and commit without printing matched text. A changed blob with no Git text hunks is scanned whole. Same-blob renames have their paths checked without rescanning inherited content. Missing, stale or partial protection is reported before dispatch. The shared-hook alternative preserves existing hooks and limits the identifier scan to state branches.

Validation at `d2d5bec640f0a61d3e044877b8443cdfdc03faa7`: all 13 guard tests pass, with no skips; AC-3 and AC-5 were replayed through real installed hooks and local remotes. Two new regression methods fail on the exact old guard at `0c68231ca` (14 commit/push cases), and four mutations remove the new protections or break archive-rename compatibility and are caught. Path refusals assert that diagnostics contain the class and a sanitized path, with no matched literal. The repair changes only the guard and its test. Original dispatch, seal and seven-folder compatibility evidence is retained at the prior candidate; its one historical digest mismatch remains unchanged. No live installation, product push or PR creation was performed by the worker. No version bump.

Known residuals:
- Gate summaries are stored verbatim by Spacedock (inferred from stored bytes, not traced in its source).
- Commit-metadata email is unchanged.
- The Captain still decides live installation and initial refusing classes; warn-mode classes can still reach the remote.
- The owner's list covers four adopters' names-only slug lists; the fifth adopter's names and hostnames outside its pattern are absent.
- Rewriting retained patches may prevent verbatim application. Binary evidence is left unchanged for the guard to inspect.

CI cost per PR: not measured; CI configuration is unchanged. FO owns publication, Draft PR, RoboRev and hosted CI review.
