# Independent findings — PR 870

Candidate: 3d65ebd7a456bcb05fd94ce754a79735bdcbcf39. Base: 1c3e714ff6752b8c84a490064639baf0d0ef3c9c. Verdict: REJECTED. Findings are recommendations for FO disposition, not repair authorization.

## F1 Material — README's plain open-question list crashes

- Released user and normal workflow: an adopting FO follows the approved workflow sentence, records a question with the documented ask command, then runs task_timeline.py STATE --open.
- Observable harm: exit 1 with KeyError: question instead of the waiting list. JSON rows carry asked but not the question field promised by contract section 8. Native gate rows do carry question, so a mixed list also crashes when it reaches a question row.
- Protected boundary: contract[kc-dev-flow-2/references/captain-question-records.md#8-commands-and-gate-rows] — the shipped list command and derived question field must work; value-ac[AC-9] — the approved entry sentence must reach the accepted open-question outcome.
- Trigger evidence: acceptance-observed.log, open-text.log, question-field.json and question-field-check.log. Candidate task_timeline.py:535 dereferences r["question"]; open_rows at line 464 returns the folded asked field without that mapping. The exact four-step acceptance script reproduces it after also proving ask, answer, and refusal to reask after closing.
- Repair direction: make the returned row shape agree with the shipped contract and exercise the actual plain --open entrance. Product bytes were not changed.

## F2 Material — new tests fail before the workflow installs Spacedock

- Released user and normal workflow: a contributor opens a package PR and the existing kc-dev-flow-2 tests workflow runs test_design_surfaces.py before its pinned Spacedock installation.
- Observable harm: four new QuestionRecordTests fail because their subprocess invokes spacedock; subsequent test steps are skipped. This is a candidate regression, not merely a local sandbox outage.
- Protected boundary: contract[.github/workflows/kc-dev-flow-2-tests.yml#jobs] — the contributor's configured test lane must run at its declared dependency stage; value-ac[AC-4] — the new positive/skip evidence must be executable in the CI evidence route.
- Trigger evidence: hosted-ci.json and hosted-ci.log, run 43475968096 / job 132059736398; ci-reproduction.log reproduces the same four failures with SPACEDOCK_BIN=/nonexistent/spacedock. ci-base-control.log passes the unchanged base design suite with that same setting. Local installed-Spacedock design.log passes, explaining why the implementation's local result did not expose it.
- Repair direction: make the tests' dependency setup agree with the existing CI order; do not enlarge CI triggers without measured need. CI cost per PR was not measured; this validation changes no CI.

## F3 Material — the claimed one-day replay includes an answer from November 5

- Released user and normal workflow: the Captain/FO uses the AC-2 replay evidence to judge whether the accepted fourteen questions from 2026-11-13 are represented.
- Observable harm: the supplied fixture cannot substantiate that exact historical cohort. replay-5 uses 2026-11-05T17:40:56+08:00; four declared snapshots consequently occur on November 5. Several question strings are truncated, inherited from the ideation extraction, so the blind reader cannot restore the source question from its input.
- Protected boundary: value-ac[AC-2] — a fixture of the fourteen outside-gate questions on 2026-11-13, with recorded answer times; only asking times were declared synthetic.
- Trigger evidence: shipped test_task_timeline.py REPLAY_2026_11_13, blind-input/replay-5/asks.jsonl, blind-input/clocks.json, and the reader's report point 7. The independently executed listing comparison passes the supplied data; it does not repair their provenance.
- Repair direction: reconcile the cohort and complete question text against the public source records, then rerun the same list/blind comparison. Changing the accepted cohort instead would need an FO/Captain scope disposition; validation did neither.

## Deferred risk — post-release capture and remote consumer

No released-day asking-time capture or another repository's remote-branch reader was exercised. The implementation explicitly excludes both; no new supported-workflow harm was observed. These become material if released-day observation misses records or a released consumer cannot interpret pushed records.
