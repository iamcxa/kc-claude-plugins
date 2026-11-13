fix(kc-dev-flow-2): honor learn selection after task archive

Archived observer checks appended learning instructions even when the workflow did not list `learn`. Read the supplied workflow README (or discover its nearest workflow ancestor) before adding those instructions, while preserving the observer verdict and the existing output for enabled workflows. Unknown archived selection exits 2 with a cause.

Pass the known README through the PR watcher, its generated post-archive command, and the history-law caller so detached state checkouts work. The absent-worktree fact behavior from #858 is retained.

Validation on base c8d6dd40cf12ff6d9047e42e4d1041afa3bcf694, candidate 17eccdda05fde54e6dff66f4989787864219ef43:
- Observer 23 tests, PR watcher 136 tests, and history laws 84 tests: 242 passed, 1 optional source replay skipped.
- Native Spacedock archive/recovery/publish/validate fixture passed; 24 archive matrix cases passed.
- Three enabled adopter corpora: 237 identical output/verdict pairs; historical unlisted configuration: 82 intended two-line deletions and no unexpected change. Public evidence contains counts only; the exact original incident is unavailable.
- Nine falsifier mutations detected with bytecode disabled and caches cleared; the unchanged integration base fails the no-learn goal check.
- Repository lint, ADR lint, number guards, comment ratio and design check pass. Added-comment ratio is 0.0% against the 5% maximum; the affected learning.md entry remains applicable.

Only the six approved scripts/tests change; no dependency, version or CI-trigger change. CI cost per PR was not measured. This local handoff does not claim hosted CI or RoboRev: the First Officer owns publication, those checks and independent validation.

Evidence: spacedock-state/dev2, observer-check-learn-only-when-listed/implementation/.
