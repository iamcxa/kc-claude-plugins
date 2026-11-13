# Validation cycle 2 — PR 870

Verdict: PASSED at 0b620345b538b67f4c6522d8b97028038f1ec17d; base 1c3e714ff6752b8c84a490064639baf0d0ef3c9c. This is an independent validation recommendation, not gate approval, merge, release, or adoption.

## Scope and provenance

Repair from 3d65ebd7a456bcb05fd94ce754a79735bdcbcf39 changes exactly three existing files, within the original eight-file candidate. provenance.json records the assigned branch, clean product worktree, unchanged contract/design checker/workflow/linter/ADR blobs, fixed candidate, reader hash and acceptance hash. Product execution used git-archive exports under the assigned validation-2 scratch; no repository worktree was created or removed. Unit-test fixtures create and clean their own throwaway repositories inside scratch.

The prior independent reader is reused byte-for-byte, as requested by the second-cycle instruction to rerun the blind comparison. No fresh blind-agent or cross-family read is claimed. It originally received only the shipped contract and fixtures; ../validation-1/blind-output/report.md records that boundary and ../validation-1/blind-dispositions.md disposes all seven questions.

## Original findings, rechecked at their triggers

- F1 Material, resolved: acceptance-observed.log runs the same four-step acceptance script with only candidate/stage paths updated. Step 4 now exits 0 and prints demo#2, Acceptance FO, acceptance, Next question?. The 28-case timeline suite also exercises plain/JSON question rows and mixed native gate rows. Removing the two-line mapping reproduces KeyError: question (F1-falsifier.log).
- F2 Material, resolved: design-full-missing-binary.log reruns the original entire unittest file with SPACEDOCK_BIN=/nonexistent/spacedock: 239 tests, 6 existing optional skips, exit 0. design-missing-binary.log separately shows all five new question-record tests run without skips. Removing the self-contained Worth questions fixture recreates four failures (F2-falsifier.log). Hosted unit run 43483914184, job 132087213353 is success; test_design_surfaces.py still executes before Spacedock installation (hosted-job.json). No CI definition or trigger changed. Cost per PR: not measured.
- F3 Material, resolved: reconciliation.log re-derives the same fourteen question/answer records from public state history. source-audit.json independently matches every candidate tuple, full source record, primary blob hash and commit author date. Replay-5 is 2026-11-13T14:42:40+08:00 at 3bf964c4746c0b2022d8ffb36da051722bac61e9; restoring November 5 fails the cohort assertion (F3-falsifier.log). Source comparison also rejects the prior truncated question string. Exact question text and recorded-answer times are not synthetic; asking offsets, replay keys and owner are synthetic as declared.

No new Material, Polish or Needs decision finding. Deferred risk remains live-day capture and a released remote consumer; these become Material if an observed supported released workflow misses a question or misreads a shared record.

## Acceptance criteria and falsifiers

- AC-1 PASS: timeline.log, CI unittest spelling, 28 tests exit 0; all six event lifecycle/refusal cases remain covered. Six named refusal deletions each fail in mutation-results.json. No pytest installation or pytest command was used.
- AC-2 PASS: reconciled-replay.log, reconciled-product-replay.json and reconciled-comparison.json show fourteen questions, 56 clocks, 28 open rows, zero membership/key/owner/since/holds/interruption/state/text differences. waiting_since is exact; only displayed waiting_min uses the previously dispositioned 0.051-minute rounding tolerance. timeline.log covers null asked_at with lower-bound wait. Omitting an open row and retaining an answered row both fail (mutation-results.json and reader-output/counterexamples.json). Historical one-day fidelity is now corroborated by source-audit.json.
- AC-3 PASS: the original mixed legacy/ask/reask/answer regression test reran within timeline.log; count is three showings, not four lines. every-line mutation fails. The original base crash/count-four outputs remain ../validation-1/h3-results.json and its cited logs; those baseline controls were read, not rerun.
- AC-4 PASS: original missing-binary reproduction and five focused tests pass, including own/shared/archive records, missing and partial question text, and real adoption history. Removing lookup and always refusing both fail (mutation-results.json). Product checker bytes are unchanged from validation-1. task-check.log exits 0 but explicitly skips the omission rule because the adopted workflow lacks the new sentence: it is not live enforcement proof. The deleted ideation probe and full committed-task corpus were not rerun in this three-file repair; no all-adopter claim is made.
- AC-5 PASS, bounded repair recheck: timeline.log reruns the native gate/archive-move case and mixed-row entrance. add-time mutation again loses the required open row (mutation-add-time.log); its IndexError is the expected test row access, not setup/import failure. The gate algorithm is unchanged. The earlier independent 34-attempt historical replay remains ../validation-1/gate-replay.json; it was read, not claimed as a new full replay.
- AC-6 SUPERSEDED by Captain amendment 1; AC-9 applies.
- AC-7 PASS: installed 0.41.0 adr_lint.py docs/adr --since 1c3e714ff6752b8c84a490064639baf0d0ef3c9c --require 0086 exits 0: 79 records (adr.log). Removing reserved 0086 fails (adr-falsifier.log). Protects still names both scripts. The earlier bare-file command checked zero records, so it is not used as evidence.
- AC-8 PASS, second-cycle replay: unchanged saved blind reader on reconciled-input produces 56 clocks / 28 open rows with no semantic differences (reader-output/output.json and reconciled-comparison.json). Its two intentionally incorrect lists are detected. The original seven interpretation questions retain dispositions; point 7's truncated-prose limitation is now resolved by full source reconciliation. Presentation rounding, local enumeration and same-family scope remain as previously disclosed.
- AC-9 PASS: wording.json/log proves the approved candidate plus --by "<session>" matches exactly, 41 words; workflow 6097 to 6113, delta +16. lint.log exits 0; removing the added startup budget step fails (mutation-budget.log). The quoted ruling matches the task's Captain amendment and approved ideation words. The actual plain listing entrance now passes F1.

## Implementation claims and remaining limits

All repair claims have targeted independent support above. The implementation's full 29-command local run, 1,480-case total, 16 mutation total and release-environment control were read as implementation evidence, not relabeled independent runs. Its disclosed imposed-SPACEDOCK_BIN release-acceptance failure was dispositioned by FO; the actual hosted release-acceptance step and whole unit job now succeed. No reason was found to reopen that environment disposition.

All five candidate PR workflows returned success (hosted-runs.json). No full CI list was rerun locally. PR remains open Draft at the exact validated head (hosted-pr.json); its body still cites the earlier review head, so no exact-head RoboRev claim is made here. FO owns that review/publication metadata and delivery checks.

Role precheck passes (role.log); eight dispatch records are complete (dispatch.log), and all implementation/follow-up requirements were read against approved scope. Number guard exits 0 after correcting the task filename (numbers-corrected.log), but warns state fetch failed: fresh remote reservations remain unverified. Initial argument diagnostic is retained (numbers.log). Added comments were read: two ADR pointers and the declared synthetic fixture comment; comments.log reports 3/704 lines, 0.4%, under 5%. diff-check.log exits 0.

Goal sufficiency: the accepted local Pilot record/lifecycle/open-list journey now works at the tested seams. Minimal necessity: all eight retained paths map to record writing/listing, omission refusal, tests of those behaviors, contract, ruling or approved startup words; each repair removes a reproduced failure without a new product path or contract revision.

Unverified obligations remain: released-day asking-time capture; another repository's released remote reader; actual adopter enforcement after README adoption; sibling PR 869 integration/recount and moved-base delivery checks; merge/release. Native gate waits remain lower bounds. No UI was changed and no screenshot/browser proof is claimed.

## Captain acceptance

Run in a fresh shell, unchanged:

    bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/captain-question-outside-a-gate-is-an-open-record/evidence/validation-2/acceptance.sh

The four steps export the exact head, ask/list one question, answer it and reject reask, then ask a second question and display the plain list. Expected observations are written in the script; acceptance-observed.log records exit 0. It requires Python 3, git, tar, the explicitly named clone and installed 0.41.0 scratch helper; it removes only its own temporary subdirectory. This is local CLI lifecycle/entry proof, not CI, omission adoption, gate-history, live-day or remote proof.

Public visibility was checked live (public-source.json). Retained evidence contains public repository facts and synthetic probes only. setup-notes.md records corrected validator path mistakes without changing product expectations.

