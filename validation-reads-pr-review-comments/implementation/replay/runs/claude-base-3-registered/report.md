## Stage Report: validation

- DONE: Independent verdict on PR #812 head 778367ad against every acceptance criterion in the task file, re-running each evidence command and at least one falsifier per criterion yourself, and judging each limit the implementation report states
  REJECTED at 778367adde2e20e0b3e51966ddba2d9f77f9e614 (base 334d91e3165953b2ca7191e3308d80b6c02c4a99): AC-1 to AC-8 pass, F1 below is Material. Evidence in validation-3/; candidate run from a git-archive export under /tmp/pr812-validation3.l3Qh.
- DONE: Judge the class repair of validation-2 F1 against review/chief-engineer-1.md (one clean-scope precondition before select_record; its matrix and falsifiers) and every criterion again; the FO rulings in dispatch/implementation-1-message-1.md and -message-2.md still stand. Hosted CI on head 778367adde2e20e0b3e51966ddba2d9f77f9e614 is now green: FO reran the three 504-failed runs at 2026-11-08T11:03Z after three consecutive successful downloads, and run 42468880068 (attempt 3) shows Install pinned Spacedock, and the dispatch-stage, Spacedock dispatch and observer recovery test steps (kc-dev-flow-2/scripts/test_dispatch_stage.py, kc-dev-flow-2/scripts/test_sd_dispatch.py, kc-dev-flow-2/scripts/test_observer_recovery.py) success; PR #812 mergeStateStatus CLEAN, 7 SUCCESS and 1 SKIPPED (gh pr view 812, FO 2026-11-08T11:09:08Z). Report AC-8 from run 42468880068 attempt 3. Keep any download under a new /tmp directory, never in the task state folder.
  Class repair holds: check_task_scope runs once in main before select_record; validation-2 F1 (staged-only retry) now refuses and preserves state. Guard removed, reuse-only bypass, scope narrowed to dispatch/, index-vs-HEAD omitted and untracked omitted each fail a preservation snapshot (mutants/). Guard-after-creation and advance-bypass were not rerun; the implementation's exact-scope-falsifiers/ covers them. Observer entry and candidate ADR linter rulings applied. No new download; sd-plugin-root reused from /tmp/pr812-validation2.gfsHcD.
- DONE: A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0/scripts/adr_lint.py docs/adr --since <base> with its exit code; your verdict naming the head, with findings classified by the workflow's Review-finding disposition
  validation-3/acceptance.sh, four steps, run under `env -i … bash --noprofile --norc`: PASS 1–3, FAIL 4 (F1), exit 1 (acceptance.log). Installed 0.35.0 adr_lint `--since <base>` exits 1 (ADR 0047 pointer, the ruled pre-#806 false positive), as does `--require 0070`; the candidate linter exits 0, 63 ADRs. Verdict REJECTED at 778367ad.
- DONE: AC-1 and AC-2: the stamp commits a complete record carrying exactly what the worker received.
  test_dispatch_stage.py: 20 tests OK against Spacedock 0.27.2 (dispatch-stage.log). Caught: dropping `--stamp` fails the commit-subject assertion; dropping `Model:` fails the checker; dropping the last scope-notes line fails line preservation.
- DONE: AC-3 and AC-4: an incomplete record, or a validation dispatch without a candidate, holds before build.
  Caught: skipping cleanup leaves `ideation-1.md`; ignoring the checker's exit lets the build run.
- DONE: AC-5 and AC-6: a failed build cleans up, a retry reuses, a later round mints a new record, and advance commits.
  Caught: no reuse adds `ideation-2.md`; reuse on bytes alone fails the post-commit rerun; skipping `state commit` leaves the advance record uncommitted.
- DONE: AC-7: README passages, word budget and consumers.
  All three passages are verbatim; lint reports 5931/5931; test_dispatch_records 115 OK (1 skipped); test_sd_dispatch exit 0. Caught: restoring the base passages makes lint exit 1 at 5933 words.
- DONE: AC-8: hosted CI runs the real-binary seam test.
  Run 42468880068 attempt 3: headSha 778367ad, completed success; Install pinned Spacedock, test_dispatch_stage, test_sd_dispatch and test_observer_recovery all success. PR is CLEAN with 7 SUCCESS and 1 SKIPPED (ci/, read through the replay gh shim). With SPACEDOCK_BIN unset, the test exits nonzero and names it; the base workflow lacks the step. CI cost per PR was not measured.
- FAILED: A second same-symptom dispatch through the prescribed wrapper shows the ADR 0026 step-back questions.
  stepback-probe.json: the wrapper exits 0, builds, and prints only the build's own stderr. The same record checked directly (folder mode and `--names --strict`) prints `step back: 2 implementation dispatches …`. This is F1.
- DONE: Required gates, comments, document dispositions and candidate preservation.
  Passed: comment_ratio exit 0 (3 lines, 0.4%), dispatch_records on the task (10 complete), design_surfaces presentable, doc_impact exit 0 with all 13 dispositions present, test_observer_recovery. number_guards exits 1 (R5) at the default base: this replay's origin/main e7c9381f already holds squash 5757476fc (#812), an environment fact. Pinned at base 334d91e3 and head 778367ad it exits 0. Read every added comment: only the ADR 0070 pointer, kept. Product bytes untouched.
- DONE: Implementation limits judged.
  Accepted, not findings: exclusive same-task writer, no concurrency claim (prepared-pr.md says so); FO-typed model and roster; separate preflights; a direct `dispatch build` bypasses the record; follow-ups are written by hand; post-release adoption is unproven. Also accepted: an upstream no-op retry fails on unrelated staged work without loss (allowed-recovery logs).
- SKIPPED: RoboRev, application suites, push.
  roborev not run: FO owns review and publication. Application unit, integration and e2e suites were not run, per the harness. The state commit is local, not pushed, per the harness instruction.

### Findings

- F1 Material: The wrapper swallows dispatch_records.py's step-back questions on a successful check.
  On success, `main` in kc-dev-flow-2/scripts/dispatch_stage.py captures both checker runs and discards their stderr, which carries the `check_symptoms` reminder.
  User and workflow: FO sends a second implementation or validation dispatch with the same `Symptom:` through `dispatch_stage.py`, as the README now prescribes. Harm: the dispatch builds with no step-back questions shown at the write.
  Boundary: captain-ruling[2026-11-03], the ADR 0026 amendment: "At round two, dispatch_records.py prints the three step-back questions on stderr before each dispatch". Trigger: validation-3/stepback-probe.json and acceptance step 4; Codex review comment 4505793059 on this head reports the same.
  Not settled: no FO decline or gate summary names it. The design sentence "on success it prints nothing of theirs" and its 4→0 words row cover a clean dispatch. ADR 0026 counts 0 added words for a clean dispatch and 48 at round two, and the design's past-rulings list omits ADR 0026. So forwarding this line fits the design; FO decides whether an amendment is owed.
  Recommend: forward the checkers' stderr on success, print the line once even though both checks emit it, and add a seam test for it. No other Material, Deferred risk, Polish or Needs decision finding.

### Summary

REJECTED: PR #812 at 778367adde2e20e0b3e51966ddba2d9f77f9e614 passes AC-1 to AC-8, including hosted run 42468880068 attempt 3, and its clean-scope guard closes validation-2 F1. Every falsifier run was caught. F1 (Material) blocks: the prescribed dispatch path hides the ADR 0026 round-two step-back questions that FO previously saw by running the checker directly. The repair is small: forward the checkers' stderr on success and print the step-back line once. Gate, merge and release stay with FO and the Captain.
