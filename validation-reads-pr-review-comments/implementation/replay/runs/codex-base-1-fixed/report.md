## Stage Report: validation

- DONE: Independent verdict on PR #812 head 778367ad against every acceptance criterion in the task file, re-running each evidence command and at least one falsifier per criterion yourself, and judging each limit the implementation report states
  REJECTED at 778367adde2e20e0b3e51966ddba2d9f77f9e614; validation-replay/evidence.md maps all eight criteria, fresh checks, falsifiers, limits and same-head review evidence; base 334d91e3165953b2ca7191e3308d80b6c02c4a99.
- DONE: Judge the class repair of validation-2 F1 against review/chief-engineer-1.md (one clean-scope precondition before select_record; its matrix and falsifiers) and every criterion again; the FO rulings in dispatch/implementation-1-message-1.md and -message-2.md still stand. Hosted CI on head 778367adde2e20e0b3e51966ddba2d9f77f9e614 is now green: FO reran the three 504-failed runs at 2026-11-08T11:03Z after three consecutive successful downloads, and run 42468880068 (attempt 3) shows Install pinned Spacedock, and the dispatch-stage, Spacedock dispatch and observer recovery test steps (kc-dev-flow-2/scripts/test_dispatch_stage.py, kc-dev-flow-2/scripts/test_sd_dispatch.py, kc-dev-flow-2/scripts/test_observer_recovery.py) success; PR #812 mergeStateStatus CLEAN, 7 SUCCESS and 1 SKIPPED (gh pr view 812, FO 2026-11-08T11:09:08Z). Report AC-8 from run 42468880068 attempt 3. Keep any download under a new /tmp directory, never in the task state folder.
  Class repair passes: 20 exact-candidate tests, 92 matrix cases/98 unchanged snapshots and nine scope mutants; AC-8 recorded run 42468880068 attempt 3 succeeds on the exact head. The two implementation rulings remain applied.
- DONE: A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0/scripts/adr_lint.py docs/adr --since <base> with its exit code; your verdict naming the head, with findings classified by the workflow's Review-finding disposition
  validation-replay/acceptance.sh ran unchanged in fresh bash: PASS 1–4, FAIL 5, exit 1 on F1. Candidate/package ADR exits 0; installed 0.35.0 exits 1 on the already-ruled ADR 0047 assertion. Full commands and output are retained.
- DONE: AC-1, AC-2, AC-3, AC-4 and AC-6 — records, input identity, refusal and advance.
  Real builder checks pass; removing stamp/model/input text, cleanup, check-before-build, checker exit handling or state commit fails its matching assertion; ac-falsifiers/results.json catches all 13 original controls.
- FAILED: AC-5 — unconditional successful immediate retry.
  Its specified clean fixtures pass, but unrelated staged task work causes exit 1 and no envelope; retry-limit.json proves all versions survive and owner-unstaging restores successful reuse. F2 returns the unaccepted limitation for a ruling.
- DONE: AC-7 — accepted passages, budget and consumer pins.
  Candidate lint reports 5931/5931; real transport passes; 115 record tests pass with one skip. Restoring base passages fails the count. documents.json matches all 13 dispositions; reduced clean-path chatter does not waive F1.
- DONE: AC-8 — exact-head hosted real-binary evidence and local falsifiers.
  Recorded attempt 3 shows Install pinned Spacedock, test_dispatch_stage.py, test_sd_dispatch.py and test_observer_recovery.py success; missing binary fails and deleting the CI step removes that command. This is historical transport evidence, not live-provider refresh.
- FAILED: Preserve the established same-symptom diagnostic reminder on successful dispatch.
  warning-probe.json: second implementation dispatch and both checkers exit 0; direct checks print required questions, wrapper stderr is empty; isolated forwarding control restores them. acceptance.log ends FAIL 5.
- DONE: Required local gates, necessity and candidate preservation.
  Comment ratio 3/776 = 0.4% within 5%; 10 dispatch records complete; design surfaces and diff checks pass. Number guards pass locally with failed-fetch warning. Direct builder produces no record; wrapper commits one. Product tracked bytes remain unchanged.
- DONE: Distinguish supplied package results from candidate results.
  Package wrapper/test already contain a later warning repair: its 22 passing tests are not candidate evidence. Package lint/transport commands fail on missing repository context; explicitly required candidate copies pass. byte-identity.json and logs retain both outcomes.
- SKIPPED: Application suites, broad package replay, diagram rendering, live adoption and delivery.
  No application unit/integration/e2e suites, servers, databases or browsers; prior 28-command run only read. No diagram render, worker/model execution, concurrent-writer proof or remote write. roborev not run: FO owns local review/publication.
- DONE: Judge all implementation limits.
  Exclusive same-task ownership, manual model/roster and follow-ups, separate preflights, direct-builder bypass and unverified adoption remain explicit; the newly documented retry exception is F2. CI cost per PR is not measured; triggers unchanged.

### Findings

- F1 Material: Same-head review comment 4505793059 reproduces: valid repeated-symptom dispatch suppresses the required operator questions (dispatch_stage.py:193–202).
  User/workflow: FO's second same-symptom implementation dispatch; harm: reminder missing despite successful envelope. Boundary: contract[docs/adr/0026-role-calls-are-owed-on-counts-read-from-task-records-and-a-dated-call-clears-them.md#consequences] requires the pre-dispatch questions. Trigger: warning-probe.json and the forwarding control; no supplied FO decline settles it.
- F2 Needs decision: The inherited no-op retry failure conflicts with unchanged AC-5; no Captain amendment in this replay accepts the exception.
  User/workflow: immediate clean-task retry with another task staged; effect: exit 1/no envelope, with state preserved. Boundary: value-ac[AC-5] requires exit 0; trigger: retry-limit.json and the real allowed-route test. FO must route a criterion ruling or repair; no silent scope change.

### Summary

This complete replay validation supersedes earlier validation verdicts for the assigned candidate: REJECTED because F1 violates the existing diagnostic contract, while F2 needs a criterion ruling. The prior data-loss class is closed and historical hosted AC-8 is green; product bytes and task frontmatter are preserved, and FO/Captain retain disposition and delivery authority.
