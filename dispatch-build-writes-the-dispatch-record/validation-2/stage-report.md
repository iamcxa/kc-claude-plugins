## Stage Report: validation

- DONE: Independent verdict on PR #812 head 0d84d5d1 against every acceptance criterion in the task file, re-running each evidence command and at least one falsifier per criterion yourself, and judging each limit the implementation report states
  REJECTED at 0d84d5d1b96fd674dba3a442d69c2e7898cceccd; validation-2/evidence.md maps every criterion, counterexample and limit; base/merge-base 334d91e3165953b2ca7191e3308d80b6c02c4a99.
- DONE: Judge the repair of the Codex P2 finding (review comment 4505536959) at this head as well as every criterion again; the FO rulings in dispatch/implementation-1-message-1.md and -message-2.md still stand, so run the candidate's own kc-dev-flow-2/scripts/adr_lint.py for the required ADR check and record the installed copy's result too. Keep any download under a new /tmp directory, never in the task state folder.
  The three reported new-path preservation cases pass and reject the old writer; F1 exposes the remaining committed-retry index loss. Candidate ADR exit 0; installed exit 1 remains the ruled pre-#806 false positive; fresh pinned-source download stayed under /tmp/pr812-validation2.gfsHcD.
- DONE: A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0/scripts/adr_lint.py docs/adr --since <base> with its exit code; your verdict naming the head, with findings classified by the workflow's Review-finding disposition
  validation-2/acceptance.sh: six steps, run unchanged using bash --noprofile --norc; acceptance.log has PASS 1–5, FAIL 6, exit 1 on F1. Full commands, expected observations, declared dependencies and ADR exits are in evidence.md and gate-results.json.
- DONE: AC-1 and AC-2 — committed complete record and matching worker inputs.
  validation-2/implementation-rerun/dispatch-stage.json: record/checkers/stamp subject/envelope and each input line pass; no-stamp/no-model/dropped-line mutants fail the corresponding assertions.
- DONE: AC-3 and AC-4 — malformed dispatches hold before building.
  Incomplete notes and missing/malformed candidates preserve task/HEAD and leave no record or spy call; no-removal/build-before-check/ignored-checker mutants are rejected.
- DONE: AC-5 and AC-6 — the specified failed-build, retry, new-round and advance cases.
  Failure cleanup, changed input/intervening commit, advance commit/envelope suppression and explicit recovery of a pending record pass; no-removal/no-reuse/bytes-only-reuse/no-state-commit mutants fail. F1 is an additional unsafe retry state.
- DONE: AC-7 — approved passages, reduced word budget and existing consumers.
  Three passages match; lint 5931/5931; 47 lint tests, 115 record tests and real integration pass; restoring base passages fails at 5933/5931. Reverting only the authorized observer entry independently fails its chat-only contract.
- FAILED: AC-8 — passing exact-head hosted real-binary seam evidence.
  Run 42464643158 fails at Install pinned Spacedock: HTTP 504, curl exit 22; seam/integration/recovery steps skipped (validation-2/ci-job.log, ci-jobs.json). Local missing-binary and CI-step deletion controls pass; no hosted mutation or rerun requested.
- FAILED: Existing record staging remains intact on every supported identical retry.
  validation-2/retry-index-probe.json and captain-run/retry-index.json reproduce F1: exit 0, MM becomes clean, staged blob replaced, HEAD unchanged; throwaway refusal control preserves all state and returns 1.
- DONE: Full package replay and original regression falsifiers.
  All 28 CI-listed Python commands exit 0 (1215 tests reported, 11 optional skips); original acceptance runner exits 0; 13 original falsifiers and three preservation falsifiers catch intended defects. validation-2/package-tests/results.json and implementation-rerun/falsifiers/results.json retain evidence.
- DONE: Required local gates, document dispositions, necessity and candidate preservation.
  Number guards, design surfaces, dispatch records, doc impact and diff checks exit 0; comment ratio 3/379 = 0.8% within 5%; 13 document dispositions checked. Direct real builder creates no record; wrapper commits one. Product worktree and exported tracked bytes remain unchanged.
- DONE: Reassess every implementation limit at this head.
  validation-2/evidence.md retains accepted manual model/roster, separate preflights, direct-builder bypass, manual follow-ups and unverified post-release adoption; pending-record recovery now explicitly needs a state commit. CI cost per PR not measured; triggers unchanged.
- SKIPPED: Installed 0.35.0 ADR lint success and live adoption/delivery proof.
  Installed ADR command with --since 334d91e3165953b2ca7191e3308d80b6c02c4a99 --require 0070 exits 1 on ADR 0047; authorized candidate copy exits 0, 63 records. Local fixtures do not prove worker/model execution, adoption, merge or release.
- SKIPPED: Local RoboRev and external review disposition.
  roborev not run: FO owns review/publication. Refreshed Codex summary reports completed/no findings on this head; it does not override the reproduced F1.

### Findings

- F1 Material: Immediate retry discards a staged-only edit to the committed dispatch record (kc-dev-flow-2/scripts/dispatch_stage.py, lines 44–46).
  User/workflow: FO retries a stamped dispatch while that record has different staged bytes but unchanged working bytes. Harm: the real stamp replaces the staged blob silently and returns success.
  Boundary: contract[kc-dev-flow-2/references/profiles/pilot.md#pilot-bounded-real-use] requires data safety at the exposed retry seam; implementation follow-up 3 also requires existing staging be preserved. Trigger: validation-2/retry-index-probe.json and captain-run/retry-index.json; the throwaway index-refusal control preserves it.
  Recommend checking index identity before reuse and covering this retry case; product bytes remain untouched for FO disposition. No other Material, Deferred risk, Polish or Needs decision finding.

### Summary

REJECTED: PR #812 at 0d84d5d1b96fd674dba3a442d69c2e7898cceccd fixes the three reported new-path data-loss cases but still loses staged content on committed-record retry (F1); AC-8 also lacks passing hosted evidence because the pinned download returned 504. This complete cycle-2 validation supersedes the earlier validation report; F1 returns to FO for disposition and repair, while gate, merge and release remain FO/Captain-owned.

