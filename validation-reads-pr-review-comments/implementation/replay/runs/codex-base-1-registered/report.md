## Stage Report: validation

- SKIPPED: Independent verdict on PR #812 head 778367ad against every acceptance criterion in the task file, re-running each evidence command and at least one falsifier per criterion yourself, and judging each limit the implementation report states
  Independent verdict REJECTED at 778367adde2e20e0b3e51966ddba2d9f77f9e614, base 334d91e3165953b2ca7191e3308d80b6c02c4a99; validation-replay/evidence.md maps all eight criteria. Full evidence commands/mutations were not rerun under the replay suite restriction; narrow real-CLI probes establish the new Material finding.
- SKIPPED: Judge the class repair of validation-2 F1 against review/chief-engineer-1.md (one clean-scope precondition before select_record; its matrix and falsifiers) and every criterion again; the FO rulings in dispatch/implementation-1-message-1.md and -message-2.md still stand. Hosted CI on head 778367adde2e20e0b3e51966ddba2d9f77f9e614 is now green: FO reran the three 504-failed runs at 2026-11-08T11:03Z after three consecutive successful downloads, and run 42468880068 (attempt 3) shows Install pinned Spacedock, and the dispatch-stage, Spacedock dispatch and observer recovery test steps (kc-dev-flow-2/scripts/test_dispatch_stage.py, kc-dev-flow-2/scripts/test_sd_dispatch.py, kc-dev-flow-2/scripts/test_observer_recovery.py) success; PR #812 mergeStateStatus CLEAN, 7 SUCCESS and 1 SKIPPED (gh pr view 812, FO 2026-11-08T11:09:08Z). Report AC-8 from run 42468880068 attempt 3. Keep any download under a new /tmp directory, never in the task state folder.
  The adopted pre-selection scope guard and two preservation probes agree; the full matrix/nine mutations remain unverified here. Recorded run 42468880068 attempt 3 succeeds on this head including pinned installation and all three named steps; implementation rulings 1 and 2 retained.
- DONE: A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0/scripts/adr_lint.py docs/adr --since <base> with its exit code; your verdict naming the head, with findings classified by the workflow's Review-finding disposition
  validation-replay/acceptance.sh ran unchanged under bash --noprofile --norc: PASS 1–5, FAIL 6, exit 1 for the lost reminder; candidate ADR lint exits 0 (63 records), installed 0.35.0 exits 1 on the previously ruled ADR 0047 false positive.
- FAILED: Preserve required successful-check diagnostic reminders before dispatch.
  validation-replay/warning-probe/result.json and captain-run/result.json: second same-symptom real dispatch exits 0 but loses the direct checker's three questions; review comment 4505793059 is independently reproduced, not cleared by green CI.
- DONE: Inspect the pull request's available review evidence through the required recorded transport.
  Two inline comments, two review receipts and four issue comments read; command-results.json retains responses. The earlier clean receipt names 0d84d5d1b9, not this head; no applicable recorded decline of the new finding found.
- DONE: Exercise staged-only retry and dirty sibling preservation on the unchanged candidate.
  Both probes return 1, name the affected path, emit no envelope, call no builder, and preserve HEAD/index/flags/task/all-file snapshots; retry-before.json, retry-after.json and preservation.json. Omitting the precondition would admit those dirty inputs; that mutation was not run.
- DONE: Confirm approved text, narrow document impact and recorded hosted evidence.
  Three passages match; static arithmetic 5931/5931; all 13 listed document dispositions reviewed. AC-8 is supported by the exact-head attempt-3 recording; unset SPACEDOCK_BIN exits 1 before tests. CI cost per PR not measured; triggers unchanged.
- DONE: Run required available package checks and preserve candidate bytes.
  ADR, dispatch records (10), comment ratio (0.4% <= 5%), design surfaces, document impact and diff check pass; number guard exits 0 with failed-fetch/local-ref freshness limit. Added comments inspected. Product remains detached at the same SHA; unrelated untracked file preserved.
- SKIPPED: Successful full package lint and complete application test/mutation coverage.
  Supplied-package lint exits 1: missing package/scripts/skill-frontmatter-lint.sh. Application unit/integration/e2e suites, full scope matrix and mutation chains NOT RUN per replay instruction; historical green reports are not independent reruns.
- DONE: Judge every implementation limit without extending its authority.
  evidence.md retains manual inputs/follow-ups, separate preflights, bypass/adoption, pending-record recovery, exclusive ownership, inherited no-op retry and unmeasured cost; no worker/adoption/concurrency proof. Supplied package writer contains later stderr forwarding and was not substituted for the candidate probe.
- SKIPPED: RoboRev, external publication, repair, merge and release.
  First Officer owns local review/publication and disposition; no candidate edit, product commit, push, remote write, server, database or browser operation occurred. Only this report/evidence is committed locally.

### Findings

- F1 Material: Successful checker stderr is discarded by the prescribed dispatcher (kc-dev-flow-2/scripts/dispatch_stage.py:191-202).
  User/workflow: First Officer dispatches validation a second time with the same Symptom. Harm: the checker prints required diagnostic questions, but a successful wrapper emits the envelope without them.
  Boundary: contract[docs/adr/0026-role-calls-are-owed-on-counts-read-from-task-records-and-a-dated-call-clears-them.md#consequences] requires the second-round questions before dispatch (2026-11-03 amendment); no explicit waiver found.
  Trigger: warning-probe/result.json and captain-run/result.json; candidate wrapper exit 0 omits "step back:", direct --names --strict exit 0 includes it. Recommend First Officer repair disposition; product untouched.

### Summary

REJECTED: PR #812 at 778367adde2e20e0b3e51966ddba2d9f77f9e614 loses required successful-check reminders despite its green recorded hosted run. Two focused data-preservation checks pass, but complete acceptance remains unverified under the replay restrictions and missing lint helper; this report supersedes the prior validation verdict for this replay, with repair authorization and delivery left to the First Officer/Captain.
