# Independent evidence scope

Candidate: d79053d0836c558a9269f9cf1ba222933935b820; base: 8ce0eb6050c889b21baccf50fec35231bc888d66. Code was read/run from git archive exports. The read-only diff has exactly the approved four paths. No product byte was edited or pushed.

## Historical reproduction and falsifiers

The replay uses public state commit b3e749c251b876ebdbe47864fe91befb9d4b5bb7 and the stored briefing, with recorded PR facts stubbed to their ask-time state. It reconstructs the real task inputs, not live GitHub at an earlier time. The actual merge tree equals the landed squash tree 3ba409485bafe8619557e955a8b6393736988da6. A fresh red run has 226 run, 221 passed, 1 failure, 4 skipped; head-only and earlier-trunk green each have 224 run, 220 passed, 4 skipped (runtime-summary.json). The passing replay uses the approved earlier trunk; it does not claim the real ask's red tree passes.

AC-1 through AC-6 match the expected exits in runtime-tests.json. AC-6 output is byte-for-byte equal to the base and has 187 words. AC-1 has only one new hold reason, but not a literal two-line-only output diff (findings.json). The nine independently rerun source mutations each produce assertion failures and zero test errors (mutations.json); the extra green-record exit mutation also holds. Removing merged-tree execution or scratch removal breaks the two-commit fixture's observations. The actual cleanup script passes unchanged with the real Git binary placed first on PATH.

## Environment and preservation

The first merge-tree attempts failed before tests with sandbox exit 128 because the repository object directory is outside writable roots. Retained in sandbox-cost-command.log and sandbox-runtime-red.log. Re-running against an owned bare object database, without any git worktree, succeeded. The first cleanup procedure returned 1 because Apple's /usr/bin/git wrapper left xcrun_db; cleanup-isolated.json identifies that sole residue. Selecting /Applications/Xcode.app/Contents/Developer/usr/bin/git on PATH reran the same procedure with its unchanged zero-entry expectation and passed (tree-and-cleanup-real-git.log). No product workaround or expectation filtering was applied.

Private repositories inspected: 0. The pinned Spacedock source repository was confirmed PUBLIC. The three integration checks used Spacedock binary 0.27.2 and source archive 4d158a484ec73e184861067f8ed1e20087fdc26a; they exercised disposable repositories only.

## Design limits judged

- Main moving between check and merge: still a real limit; this design binds the trunk observed at check time, and adds no merge-time recheck.
- Disclosure only from supplied gate text, not PR body: confirmed by the data path and not-run tests; question-only placement is exercised behaviorally.
- merge-test key placement: the adopted workflow has its one approved command line; no automatic adopter migration was added. Each adopter still needs its own configured command or explicit disclosure.
- Original replay hardcodes this machine: retained proof-of-concept script remains historical; validation's adapter takes MERGE_REPLAY_CODE and the four-step acceptance script declares exact inputs.
- Record tree and exit trusted: confirmed; check does not recompute or authenticate the record. The exit mutation proves the saved value controls the hold, not that an authenticated test ran.
- Live post-release merge ask: still not provable in this dispatch; public PR 853 remains Draft/open, and this is an unreleased candidate.
- Full delivery-gate unit suite and README/question behavior: executed on the exact exported candidate; the command exited 0: 1345 run, 1334 passed, 11 skipped across 24 unit scripts plus lint (cost-suite-summary.json).
- Three pinned-Spacedock tests: now proven locally (test-dispatch-stage.log, test-sd-dispatch.log, test-observer-recovery.log); not a claim of native agent dispatch or a remote merge.

## Goal sufficiency and necessity

The existing check now holds the historical missed ask, rejects stale/failed runs, permits a matching passing run, and carries explicit non-execution into the question. The added command is necessary to produce the record and run the merged tree; the README parser adjustment preserves trailing shell quotes needed by that configured command; the single configuration line fixes the command source; the question check closes summary-only disclosure. Tests and ADR cover those approved surfaces. No CI definition or repository setting changed. Local replay and fixture checks do not replace release/adopter proof.

## Captain acceptance

Run `bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/merge-ask-tests-the-merge-result/validation/acceptance.sh` unchanged. Four steps and expected observations are in the script; acceptance.log is its fresh-shell output. It requires this public repository's pinned objects, task evidence, git, python3 and bash. It does not run the full package suite or prove a live post-release ask. Its own scratch directory is removed by its EXIT trap.
