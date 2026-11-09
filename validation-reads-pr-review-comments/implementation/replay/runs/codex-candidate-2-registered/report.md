## Stage Report: validation

- SKIPPED: Independent verdict on PR #812 head 778367ad against every acceptance criterion in the task file, re-running each evidence command and at least one falsifier per criterion yourself, and judging each limit the implementation report states
  Independent verdict is REJECTED at 778367adde2e20e0b3e51966ddba2d9f77f9e614; complete per-criterion suite/mutation reruns are explicitly prohibited by this replay dispatch. validation-replay-candidate-2/evidence.md distinguishes each AC's inspected evidence, bounded executions and unrun obligations.
- DONE: Judge the class repair of validation-2 F1 against review/chief-engineer-1.md (one clean-scope precondition before select_record; its matrix and falsifiers) and every criterion again; the FO rulings in dispatch/implementation-1-message-1.md and -message-2.md still stand. Hosted CI on head 778367adde2e20e0b3e51966ddba2d9f77f9e614 is now green: FO reran the three 504-failed runs at 2026-11-08T11:03Z after three consecutive successful downloads, and run 42468880068 (attempt 3) shows Install pinned Spacedock, and the dispatch-stage, Spacedock dispatch and observer recovery test steps (kc-dev-flow-2/scripts/test_dispatch_stage.py, kc-dev-flow-2/scripts/test_sd_dispatch.py, kc-dev-flow-2/scripts/test_observer_recovery.py) success; PR #812 mergeStateStatus CLEAN, 7 SUCCESS and 1 SKIPPED (gh pr view 812, FO 2026-11-08T11:09:08Z). Report AC-8 from run 42468880068 attempt 3. Keep any download under a new /tmp directory, never in the task state folder.
  Class guard is before select_record; exact-head staged-only retry preserves all snapshots, while disabling the guard loses the staged blob (scope-probe.json). Full 92-row/nine-mutant author evidence was read, not rerun. Recorded run 42468880068 attempt 3 at the exact head confirms AC-8's install and three named steps success (ci-run.json).
- DONE: A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0/scripts/adr_lint.py docs/adr --since <base> with its exit code; your verdict naming the head, with findings classified by the workflow's Review-finding disposition
  Four-step acceptance.sh ran unchanged in bash --noprofile --norc: two dispatches/direct checker exit 0, candidate ADR 63 records/exit 0, final missing-reminder assertion exit 1 (acceptance.log). Installed 0.35.0 ADR command exits 1 on ADR 0047, the already-ruled false positive; both exact commands and outputs are in gates.json.
- DONE: Read the open pull request's reviews, conversation and inline comments against the exact candidate.
  Historical shim: OPEN draft, exact head/base, CLEAN, seven SUCCESS/one SKIPPED; both inline comments read. Comment 4505536959 is the older repaired loss case; same-head comment 4505793059 is the newly reproduced Material finding, not a clean review (review-comments.json).
- FAILED: Successful dispatch preserves the binding second-symptom step-back reminder.
  Exact candidate wrapper twice exits 0 but drops the required questions; its direct --names --strict checker exits 0 and prints them. Newer declared-package bytes emit the warning but are not this candidate. warning-result.json and acceptance.log preserve the comparison.
- DONE: Required local gates, affected documents and added comments.
  Candidate/package ADR, number guards, dispatch records (10), design surfaces, lint (5931/5931), comment ratio (3/776 = 0.4%, limit 5%), doc impact (13 dispositions) and diff check exit 0. Number-guard fetch failed, so remote reservations remain unrefreshed; Scope scan intentionally not run at validation.
- DONE: Judge every reported implementation limit and the retained change's necessity.
  evidence.md retains manual model/roster/follow-ups, separate preflights, direct-builder bypass, exclusive-writer requirement and upstream no-op retry limitation. Adoption/concurrency/delivery remain unverified; CI cost per PR unmeasured, triggers unchanged. The guard is necessary but reminder loss prevents goal sufficiency.
- SKIPPED: Application unit, integration and e2e suites, original acceptance/mutation collections and full class-repair matrix.
  Explicit replay prohibition; no server, database or browser started. Author logs are evidence read, never independent pass claims. Only bounded disposable CLI reproductions and prescribed package checks ran.
- SKIPPED: RoboRev, GitHub writes, remote commits/pushes, merge and release.
  FO owns review/publication and this replay forbids writes to remotes. Candidate tracked bytes and existing untracked shell log are preserved; code/state checkouts are detached, so no product branch commit was attempted.

- FAILED: Commit the validation report and supporting evidence locally before completion.
  The prescribed path-scoped git add exited 128: cannot create /Users/kent/Project/kc-claude-workspace/kc-claude-plugins/.git/worktrees/-spacedock-state7/index.lock (Operation not permitted). Git metadata is outside this replay sandbox; no commit, remote write, alternate index or bypass was attempted. FO must commit the retained files.

### Findings

- F1 Material: Candidate drops successful record checks' required step-back questions (kc-dev-flow-2/scripts/dispatch_stage.py:193-202; PR inline comment 4505793059).
  Released user/workflow: FO sends a second implementation dispatch naming the same Symptom through the prescribed wrapper. Harm: successful dispatch omits the three required pre-dispatch questions.
  Boundary: contract[docs/adr/0026-role-calls-are-owed-on-counts-read-from-task-records-and-a-dated-call-clears-them.md#consequences] requires the second-round stderr reminder; ADR 0027 places it at the write. ADR 0070 does not supersede or explicitly waive that duty.
  Trigger: real Spacedock 0.27.2 and exact-head candidate reproduce success without the reminder; direct checker emits it. No recorded FO decline for this finding was found. The design's silent-success sentence does not establish an explicit waiver of the binding reminder; route repair or that decision through FO.

### Summary

REJECTED: PR #812 head 778367adde2e20e0b3e51966ddba2d9f77f9e614 has green recorded hosted checks and a bounded independently confirmed data-preservation repair, but the same-head review finding is reproduced and violates the binding reminder contract. This replay report supersedes the earlier validation verdict for this candidate only within its stated execution limits; FO must disposition F1 and retain the unrun proof obligations before presenting delivery, and no product bytes were repaired.
