# Independent validation after Captain amendment 2

PASSED at PR #822 head `4a146449de8ad43f1eb67e59599215989c327645`. F1 from validation-1 (ordinal citation refused as a count) is resolved by the explicit Captain ruling and independently reproduced AC-9 behavior. No new Material, Deferred risk, Polish or Needs decision finding was observed. This is a validation recommendation, not gate approval or merge authority.

## Identity and method

Run date: 2026-11-10 UTC. Original base `82c9e67ae892b80647c3f6a8b6929f993e42dbc2`; freshly fetched origin/main `f980a097bf15d8d1382c039949c6b9aefc5439c8`. `identity.json` records the conflict-free merge-tree result `88d466fc004a13d85cd9ed8417ef2a53b8d75068`. Candidate, previous head and merged tree were exported under /tmp; no product worktree was created or removed, no product code or repository configuration changed. `source-integrity.json` verifies exported tracked blobs still match their Git trees after all checks, and pins the assigned clean branch. Only count_tokens.py differs from the rejected candidate; the complete original PR scope remains the authorized files listed there.

Every NAME.json receipt records exact argv, cwd, UTC start/end, producer PID/exit, candidate identity and NAME.log hash. Baseline receipt intentionally executes the `previous` export identified by `identity.previous`; suite-merged executes `identity.merge_tree`. `verification.json` checks accepted receipts and hashes. Reused scripts were read before execution: validation-1 replay/word/negative drivers and implementation-4 historical/mutation drivers; only export paths, pinned candidate and the explicitly documented live-store delta were adapted. No model worker or external mutation was used.

## Criteria and falsifiers

| Criterion | Independently observed | Falsifier run |
| --- | --- | --- |
| AC-1 | acceptance.log exercises actual claim/complete with 18 versus referenced 15; refusal leaves pending token usable, correction completes; legacy reads remain valid. | retained-mutations.log / learn-join.log: remove evaluation's join, refusal test fails without ERROR. |
| AC-4 | replay.py gate-replay.log: 23 of 30 recent summaries across the four pinned state revisions require nonzero disclosure. learn-replay.log: 28 add entries across five stores refuse only 441fe280 and d829872c. | extra-falsifiers.log restores the old comma pattern and recovers `2, round`; mutations.log restores the ordinal refusal. |
| AC-5 | words.log independently recounts base/candidate: startup 5931+48 unchanged, validation 826→848, evaluator 877→896; zero-count question 92→97 and check 84→89 words. | extra-falsifiers.log / budget-mutant.log: one added startup word makes native lint reject the unchanged budget. |
| AC-6 | suite-candidate.log: Ran 1050 tests, OK (skipped=7); suite-merged.log: Ran 1053 tests, OK (skipped=7). Each receipt exit 0. Lint, ADR, design, dispatch and refreshed number checks pass. | budget-mutant.log fails native lint; retained-mutations.log removes the POC writer and both route assertions fail. source-integrity.json confirms scope and unchanged exports. |
| AC-7 | probe.log and acceptance.log exercise actual question writes, wrong/missing/duplicate disclosure, checked 3, unsupported 2, derived ratios, fences, containment, legacy callers and existing holds. | number-in-file.log and writer.log each show required test failure with no ERROR. |
| AC-8 | acceptance.log covers the gh-stub PR body, automatic ask rewrite, idempotence and failure before a merge record on write error. | pr-body.log and writer.log fail their retained tests. |
| AC-9 | probe.log uses the original ed2d3ee1 entry and evidence unchanged; completion exits 0 and stored decision equals the original. Unsupported 2 cells is refused and same-token correction to 3 completes. Each named sequence label/case and adjacent real count is exercised, plus gate disclosure. | baseline.log confirms prior-head refusal; ordinal-exclusion-removed.log restores that failure; plain-count-scan-removed.log permits the unsupported count and therefore fails the probe. |

Both full-suite commands are `SPACEDOCK_BIN=/Users/kent/.local/bin/spacedock python3 -B -m unittest discover -s kc-dev-flow-2/scripts -p 'test_*.py'`, executed in separate candidate/merged exports. No merge-main repair is needed on these exact bytes. Superseded AC-2/AC-3 are not requirements; AC-7/AC-8 and new AC-9 follow the recorded amendments.

## Replay differences and environmental attempts

`replay-differences-current.log` explains every changed gate sentence by removal of a named sequence identifier and verifies that existing learn-record hashes remain unchanged. Recent nonzero gate summaries decrease from validation-1's 24 to this run's 23; the removed learn refusal is ed2d3ee1 only. No comma defect reappears. The live qnow store gained one completed no-change record afdf39d8 since validation-1; replay-store-drift.json proves its decisions are no-change and proposal null, so add-entry counts and refusal results are unaffected. The initial replay-differences.log failure is the old all-records-identical assertion detecting that real addition, not a product failure; the corrected driver checks exactly that allowed addition and still asserts equality for every old record. It does not broadly ignore drift.

The first wrapped GitHub reads failed inside the sandbox; github-pr-refreshed and github-review-comments-refreshed are the authorized successful reruns. Initial numbers.log disclosed a failed state fetch; numbers-refreshed.log has no warning and is the accepted reservation check. Earlier detached replay launch attempts produced no receipts and are not evidence; the tracked replay runs above completed normally. adr.log uses the selected Codex skill package root; adr-dispatch.log additionally runs the exact dispatch-specified Claude package ADR command, both exit 0. package-parity.json confirms those ADR checkers and skill entrypoints are byte-identical.

## Documents, sufficiency and necessity

doc-impact.log returns ADR 0044, 0051, 0062, 0071 and 0072; document-verdicts.json gives a disposition for each after reading their decisions. comments.log measures 3 ADR-link comments among 227 added code lines (1.3%, maximum 5%); each added comment was read and is a governing-document pointer. No workflow, mod, version or CI topology change occurred; CI cost per PR was not measured.

At Pilot depth the accepted goal is sufficient: ordinal source references complete unchanged, unsupported measured numbers stay correctable before completion, and gate disclosures continue to be written. Necessity is supported by the previous-head failure and the targeted removals of sequence exclusion, count scan, learn join, cited-number comparison, automatic writer and PR-body scan. The POC expected-output adjustment preserves the approved forwarding behavior and its holds. No extra policy, parser layer or production obligation was added.

## Limits judged

- A number present in cited material proves presence only, not truth or which command produced it; stale or unrelated numbers may pass. This is an accepted design limit of ADR 0072, not widened by the repair.
- The original outside-adopter issue #811 record is unavailable. The 18/15 CLI case reproduces its reported shape; the historical ed2d3ee1 record and local replay are the declared observed data.
- Derived gate counts remain unchecked without a hold; derived learn numbers must appear in references. These are the accepted distinct behaviors.
- Chat, spelled-out quantities, implicit lists, stage-report text outside summaries and PR readers who never see the ask remain outside scanning. Named sequence labels are excluded by Captain Amendment 2, including their case variants; arbitrary natural-language classification is not claimed.
- Existing completed records remain readable, and historical bytes were not rewritten. Local fixtures/replays do not establish host-wide adoption, native agent writing behavior or unattended reliability.
- The implementation's prior state-publication hold was not assumed resolved from prose: the shared state was clean on entry, and this validation publishes only its own report/evidence. The product remained unchanged.
- github-pr-refreshed.log observes this exact head still OPEN/Draft, test CI successful, docs deploy skipped, and completed Codex review with no major issues; inline review comments are empty. This is read-only provider evidence, not completion of FO's entire delivery workflow. RoboRev, readiness, Captain gate/merge decision and adoption remain FO/Captain-owned and were not performed here.

## Captain acceptance script

Run unchanged in a fresh shell:

```sh
bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/counts-name-the-run-that-produced-them/validation/validation-2/acceptance.sh
```

The four commented steps export the pinned candidate, run the unchanged historical entry plus refusal/correction probes, run retained learning/disclosure/forwarding tests, then check amendment presentation. Expected: `Exported 4a146449de8ad43f1eb67e59599215989c327645`, historical completion_exit 0, unsupported refusal_exit 1 and correction_exit 0, `Ran 10 tests` / `OK`, `design surfaces presentable`, and `Acceptance passed for 4a146449de8ad43f1eb67e59599215989c327645`. acceptance.json/.log record this exact published-path fresh-shell execution with exit 0. Required inputs are Git, tar, Python 3, the pinned repository object, this committed evidence folder, and the explicit installed package/Spacedock paths in the script. It creates a disposable /tmp export. No graphical surface exists; this is observable CLI acceptance. It does not repeat the full suite, corpus, mutations, hosted review or merge, and grants no delivery authority.
