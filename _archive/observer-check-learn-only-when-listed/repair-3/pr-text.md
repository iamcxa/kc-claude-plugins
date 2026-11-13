fix(kc-dev-flow-2): honor learn selection after task archive

Archived observer checks appended learning instructions even when the workflow did not list `learn`. Honor the workflow README selection, preserve enabled output and the observer verdict, and pass the known README through both callers and the generated post-archive command so detached state checkouts work.

The pre-validation repair also makes the history-law checker and PR watcher use the same existing extension reader as the observer. The reported quoted/commented block-list case previously enabled observer learning steps while silently skipping L1; the repaired head reports the missing-observer violation. Comment words no longer enable an extension in the watcher. The two new regressions fail on the previous head and pass after repair; PR 858's absent-worktree fact behavior is retained.

Candidate: 97fe3d6ff9f9afe220b463c71ac428e380fc4dc5; integration base: c8d6dd40cf12ff6d9047e42e4d1041afa3bcf694; repair parent: 17eccdda05fde54e6dff66f4989787864219ef43.

Validation:
- Repository merge-test command: 25 scripts, 1377 tests total; 1366 passed and 11 skipped, exit 0. The command excludes three pinned-Spacedock integration scripts.
- Focused reruns: 245 total; 244 passed and 1 optional replay skipped. Native observer archive/recovery/publish/validate passed separately.
- All 24 archive matrix cases passed; 11 reverse/fault mutations detected with bytecode disabled and caches cleared, including restoring each legacy extension parser.
- Enabled adopter corpora: 237 identical output/verdict pairs. Historical unlisted configuration: 82 intended changes, zero unexpected. Public artifacts contain counts only; the exact original historical task is unavailable.
- Repository lint, ADR lint, number guards, comment ratio, design and diff checks pass. Added-comment ratio 0.0% against the 5% maximum. learning.md remains applicable.

Only the six approved scripts/tests differ from the integration base; four changed in the repair. No version, dependency or CI-trigger change; CI cost per PR was not measured. RoboRev job 1809's finding was independently reproduced and repaired, but no fresh clean RoboRev or hosted CI result is claimed here: the First Officer pushes and reruns review/validation.

Evidence: spacedock-state/dev2, observer-check-learn-only-when-listed/repair-3/.
