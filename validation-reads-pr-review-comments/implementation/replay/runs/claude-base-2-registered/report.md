## Stage Report: validation

- DONE: Independent verdict on PR #812 head 778367ad against every acceptance criterion in the task file, re-running each evidence command and at least one falsifier per criterion yourself, and judging each limit the implementation report states
  REJECTED at 778367adde2e20e0b3e51966ddba2d9f77f9e614 (base 334d91e3165953b2ca7191e3308d80b6c02c4a99) on F1; AC-1–AC-8 each pass with own falsifiers in validation-3/evidence.md. Package suites not run here (replay harness); the hosted run executed them.
- DONE: Judge the class repair of validation-2 F1 against review/chief-engineer-1.md (one clean-scope precondition before select_record; its matrix and falsifiers) and every criterion again; the FO rulings in dispatch/implementation-1-message-1.md and -message-2.md still stand. Hosted CI on head 778367adde2e20e0b3e51966ddba2d9f77f9e614 is now green: FO reran the three 504-failed runs at 2026-11-08T11:03Z after three consecutive successful downloads, and run 42468880068 (attempt 3) shows Install pinned Spacedock, and the dispatch-stage, Spacedock dispatch and observer recovery test steps (kc-dev-flow-2/scripts/test_dispatch_stage.py, kc-dev-flow-2/scripts/test_sd_dispatch.py, kc-dev-flow-2/scripts/test_observer_recovery.py) success; PR #812 mergeStateStatus CLEAN, 7 SUCCESS and 1 SKIPPED (gh pr view 812, FO 2026-11-08T11:09:08Z). Report AC-8 from run 42468880068 attempt 3. Keep any download under a new /tmp directory, never in the task state folder.
  Class closed: check_task_scope runs before select_record on all routes; staged record retry and staged task-file edit both refuse with blob kept, and removing the guard loses both blobs at exit 0 (validation-3/probe.json). AC-8 from run 42468880068 attempt 3: steps 29–32 success; downloads in /tmp/pr812-v3.732K.
- DONE: A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0/scripts/adr_lint.py docs/adr --since <base> with its exit code; your verdict naming the head, with findings classified by the workflow's Review-finding disposition
  validation-3/acceptance.sh, five steps, `env -i … bash --noprofile --norc`: PASS 1,2,3,5, FAIL 4 on F1, exit 1 (acceptance.log). Installed 0.35.0 ADR lint exit 1 (ruled pre-#806 ADR 0047 false positive); package and candidate copies exit 0.
- DONE: AC-1, AC-2 — stamped record committed and carrying the received inputs.
  Probe `fresh` subject `dispatch: probe-task entering ideation`; acceptance record lines all present in record and dispatch file; dropping `Model:` fails it.
- DONE: AC-3, AC-4 — incomplete record and missing candidate hold before build.
  Exit 1, prefix and checker text, no record, spy not run; skipped cleanup and ignored checker mutants fail.
- DONE: AC-5, AC-6 — failed build leaves no record; advance commits its record.
  Spacedock's `dispatch build --stamp:` line and exit 1 pass through; advance commits `state: update`; removing cleanup or the state commit leaves a file.
- DONE: AC-7, AC-8 — README passages verbatim at 5931/5931 words; CI step runs the real binary.
  Restoring base passages: lint exit 1 at 5933; SPACEDOCK_BIN unset exits 1 naming it.
- FAILED: ADR 0026 step-back questions reach FO before a repeated-symptom dispatch.
  Second same-Symptom implementation dispatch exits 0 with no step-back line while the checker alone prints it; forwarding successful checks' stderr fixes all seven probe scenarios.
- DONE: Required gates, limits and necessity.
  comment_ratio 3/776 = 0.4%; dispatch records 10 complete; number guards PASS at --base 334d91e3 (default base fails R5 only because this replay's origin/main holds #812's squash); doc impact 13 dispositions; exclusive-writer and no-op retry limits judged in evidence.md.
- SKIPPED: RoboRev, PR replies, push and live adoption proof.
  roborev not run: FO owns local review and publication; no state push per replay harness.

### Findings

- F1 Material: dispatch_stage.py `main` discards successful `dispatch_records.py` stderr, so the round-two step-back questions are never shown before dispatch. Boundary contract[docs/adr/0026-role-calls-are-owed-on-counts-read-from-task-records-and-a-dated-call-clears-them.md#consequences] (amended 2026-11-03); trigger acceptance step 4, probe.json, Codex review comment 4505793059 on this head. Needs decision instead only if FO reads the design's "prints nothing of theirs" as a ruling over ADR 0026.
- F2 Polish: dispatch/validation-3.md checklist item 2 predates the received dispatch text (green rerun, run 42468880068); no record holds what this worker received. Workflow state only; checker exits 0.

### Summary

REJECTED at 778367adde2e20e0b3e51966ddba2d9f77f9e614: the clean-scope precondition closes the validation-2 F1 class, and AC-1–AC-8 hold with hosted run 42468880068 attempt 3 green. One new Material finding remains — the wrapper hides ADR 0026's step-back reminder, also raised by the unanswered Codex P2 on this head — and its repair is small and within the task. Gate, merge and release stay with FO and the Captain.
