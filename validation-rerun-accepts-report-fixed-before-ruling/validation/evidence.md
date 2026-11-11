# Independent validation of PR #834

Verdict: **PASSED** at `7d75d65ef317fc5c426eb7b0975d93a72d50acaa`, base `8c714a370867eccb0d26a589c5149ad3e0c911b4`.
The accepted profile is pilot. Product bytes were exported with `git archive` from the assigned worktree and checked against all three implementation hashes; no candidate repair, product push, PR comment, review request or merge was performed.

## Primary evidence and falsifiers

| Criterion | Independent observation | Falsifier exercised |
| --- | --- | --- |
| AC-1 | `replay-original.log` and `replay-raw.json`: actual qnow history gives tag exit 2 / candidate exit 0 and empty candidate stdout. Before Amendment 1, candidate gives exit 1 naming F1,F4. | `replay-mutant.log`: restoring blanket rewrite refusal makes recorded qnow candidate exit 2. `AC-1-any-rewrite.log` fails its success assertion. |
| AC-2 | Actual after-ruling rewrite gives exit 2 at both revisions; candidate names rewritten-report-after-ruling. Package tests exercise new validation/ideation/FO resolutions, withdrawal, and a same-commit amendment. | `AC-2-identities.log` and `AC-2-same-commit.log`: removing each comparison fails the corresponding assertion. Unsupported manually constructed duplicate-entry history is dispositioned below. |
| AC-3 | Raw replay verifies rewritten-report-verdict-changed; focused cases cover flipping, adding/reordering tokens, and no verdict token. | `AC-3-verdict-list.log`, `AC-3-unreadable.log`: removing ordered-word or empty-word protection fails assertions. |
| AC-4 | Corrected report then later ruling clears; without ruling the final-text SHA is named; old text returning and a ruling between corrections refuse. | `AC-4-final-clock.log`, `AC-4-old-text-return.log`: wrong clock and missing ancestry rejection fail assertions. |
| AC-5 | `corpus.log`: four recorded revisions, 26 selected tasks, ten changes only from tag rewritten-report (eight clear, one needs-ruling, one verdict-unreadable). Both callers were read: dispatch_stage propagates status/output; laws_check uses non-git snapshots and skips this predicate. | `AC-5-recovery.log` rejects the old recovery text. `corpus-mutant.log` detects previously-cleared tasks when supported clearing is disabled. |
| AC-6 | `adr-source-check.log` checks both complete Captain questions/replies. `adr-lint.log`: 67 ADRs checked, zero legacy, exit 0. Diff adds only the amendment to existing ADR 0045. | `adr-mutant.log`: removing the paragraph fails the source-binding assertion (exit 1). |

`mutations.json` records eight independently rerun mutants, all killed by assertion failures rather than test errors. `sources.json` pins the four corpus revisions; these are frozen evidence, not a claim about every later adopter commit.

## Tests and required checks

- `records-tests.log`: 125 tests, one optional native-builder skip; `real-builder-retry.log` runs that one case with the explicit real binary and plugin root and passes.
- `dispatch-stage-retry.log`: 40 tests pass. `laws-check.log`: 84 tests, one optional external-record source skip (`DEV2_OBLIGATION_SOURCES` not provided). The latter does not weaken the live predicate proof: actual qnow replay and the four-state corpus ran separately.
- `checks.json` contains exact argv and exit 0 for installed 0.38.0 ADR lint, number guards, comment ratio, document impact, design surfaces, dispatch records, source binding, and the repository's skill lint.
- The required ADR invocation ran in the archive with read-only `GIT_DIR` / `GIT_WORK_TREE` metadata: `python3 -B /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.38.0/scripts/adr_lint.py docs/adr --since 8c714a370867eccb0d26a589c5149ad3e0c911b4 --require 0045`.
- No added inline comments; `comment-ratio.log`: 136 code lines, zero comment lines, 0.0% against maximum 5%. The changed module docstring describes current behavior.
- `doc-impact.json` agrees with implementation: ADR 0045 updated; ADR 0048 unaffected (completion/publication ownership unchanged); learning.md unaffected (the cited output-consumer and evidence rules remain applicable). `word-counts.json` independently confirms ADR 489 to 612 words, boot +0.
- Initial helper invocation errors were corrected, not counted as product failures: dispatch-stage first lacked its explicit binary, and the first native-builder selector named a nonexistent test class. The successful retry logs above supersede those invocations.

## Finding disposition

- **F1 Deferred risk — a hand-authored resolution plus withdrawal on one gate attempt collapses to one identity.** Released user / normal workflow: no supported trigger established; native Spacedock refuses withdrawal after a resolution. Observable harm in the artificial history: tag exits 2, candidate exits 0 after a late report correction and later amendment. Protected boundary: `value-ac[AC-2]` requires after-entry corrections to refuse. Trigger evidence: `withdrawal-probe.py` / `withdrawal-probe.log` construct the artificial history; `native-withdrawal.py` / `native-withdrawal.json` exercise real prepare, record-hold, withdraw and receive exit 1, `frozen closed`. No live repair is justified. It becomes Material if a supported native operation or actual supported historical record produces both entry kinds on an already-known attempt.
- The preliminary synthetic suspicion was independently checked against the real entrance and downgraded before this report. `acceptance-exploratory.log` is an exploratory failing assertion against that unsupported combination, not a failed accepted workflow or the final acceptance script.

## Limits assessed

The implementation correctly limits its proof to ordered whole-word PASSED/REJECTED tokens and reports with open F-numbered Needs decision findings. Removing all such findings, expressing a semantic verdict change without those words, or proving a ruling's authenticity/coverage is outside the accepted check; the approved design explicitly retained those limits. The three product-file changes are sufficient and necessary for the approved correction, failure messages, regression coverage, and recorded decision; no workflow wording, CI trigger, version, migration or production obligation is added.

`pr.json` is a fresh read of OPEN PR #834 at the exact candidate. Hosted checks are recorded there (including a skipped docs deploy), not treated as merge authorization. RoboRev was not rerun: the assignment reserves it to FO. CI cost per PR is not measured and no CI configuration changes. The worker's implementation-time publication limits were accurate then; current publication is separately observed here.

## Captain acceptance — four steps

Prerequisites: bash, Git, Python 3, the named product and qnow repositories with recorded commits, this committed task folder, and the installed 0.38.0 package. The task has no GUI surface. Run this exact command in a fresh shell:

```sh
/usr/bin/env -u BASH_ENV -u ENV -u GIT_DIR -u GIT_WORK_TREE bash --noprofile --norc '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/validation-rerun-accepts-report-fixed-before-ruling/validation/acceptance.sh'
```

1. Export the pinned candidate. Expected: `Step 1 candidate=7d75d65ef317fc5c426eb7b0975d93a72d50acaa`.
2. Replay qnow and check unfiltered refusal tokens. Expected: tag/candidate exits 2/0, 2/2, 2/2 and `Step 2 PASS`.
3. Run nine focused regressions and installed ADR lint. Expected: nine tests OK, 67 ADRs checked, `Step 3 PASS`.
4. Exercise real native gate closure in a disposable repository. Expected: attempted withdrawal is frozen closed, `Step 4 PASS`; overall exit 0.

I ran the final script exactly as above in a fresh bash shell: `acceptance.log` and `acceptance.exit` record all four steps and exit 0. It completes within the five-minute budget. It does not replace the full corpus/unit evidence or prove remote review, merge, release, installed adoption, or actual human approval. Synthetic gate records in temporary repositories grant no authority.

## Cleanup and handoff

All sessions started by this validator have completed. Product worktree remains clean at the pinned candidate; unrelated FO workspace changes are preserved. Temporary exports and reproductions are retained under `/tmp/validation-pr834-7d75d65e` as supporting evidence; no long-running process, live model worker, service, browser, or production data was created. Only this task's validation evidence and appended report are published by the prescribed path-scoped state commit. Gate disposition and delivery remain with FO and the Captain.

