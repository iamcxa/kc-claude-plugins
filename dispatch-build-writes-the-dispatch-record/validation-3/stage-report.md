## Stage Report: validation

- DONE: Independent verdict on PR #812 head 778367ad against every acceptance criterion in the task file, re-running each evidence command and at least one falsifier per criterion yourself, and judging each limit the implementation report states
  Candidate 778367adde2e20e0b3e51966ddba2d9f77f9e614: amended local criteria pass; overall REJECTED solely because AC-8 has no hosted pass. validation-3/evidence.md separates exercised evidence, accepted limits and unverified delivery.
- DONE: Judge the class repair of validation-2 F1 against review/chief-engineer-1.md (one clean-scope precondition before select_record; its matrix and falsifiers) and every criterion again; the FO rulings in dispatch/implementation-1-message-1.md and -message-2.md still stand.
  One whole-scope precondition runs before select_record on all routes; 92 matrix cases and 98 complete snapshots remain unchanged, and nine matching mutations fail the preservation assertion (validation-3/scope-summary.json, scope-falsifiers/).
- DONE: A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; required ADR command with its exit code; verdict naming the head with classified findings
  Six-step validation-3/acceptance.sh runs unchanged in fresh bash: captain-run-amended.log PASS 1–6, exit 0. evidence.md gives its exact command; pre-amendment AC-5 failure is retained separately, not relabelled.
- DONE: Apply validation-3-message-1 and judge AC-9 instead of superseded AC-5.
  Captain amendment 1 accepts the outside-staged retry limit; AC-9 is present and design-surfaces-amended.log exits 0. F2 is settled by that amendment; the candidate remains 778367adde2e20e0b3e51966ddba2d9f77f9e614.
- DONE: AC-1 and AC-2 — stamp commits an accepted record containing the worker's actual inputs.
  Real binary 0.27.2 passes subject, both checkers, JSON envelope and received-input assertions; removing stamp/Model or a scope line fails (acceptance/dispatch-stage.json, acceptance/falsifiers/).
- DONE: AC-3 and AC-4 — incomplete scope or candidate holds before building.
  Missing Package root/candidate leaves no record, task/HEAD change or builder call; invalid SHA exits 2. No-removal, build-before-check and ignored-checker mutations fail their corresponding assertions.
- DONE: AC-6 — advance commits before returning its envelope and preserves failed-commit recovery.
  Real advance subject passes; failed commit has no envelope and retains the pending record until intentional owner commit; removing state commit fails.
- DONE: AC-7 — approved passages, reduced budget and retained consumers.
  Three passages match; 5931/5931 words, 47 lint and 115 record tests plus real transport pass; base passages fail at 5933/5931 and the independently reverted observer entry fails its chat-only contract.
- DONE: AC-9 — failed builds, immediate retry, later-commit/changed-input numbering and the accepted outside-staging limit.
  Both layouts: first build exits 0; outside-staged retry exits 1 with no envelope and identical files/index/HEAD; clean retry recovers. Original retry mutations and an extra whole-index staging mutation fail (outside-staged-retry.json, outside-staged-falsifier.json).
- FAILED: AC-8 — the PR's exact-head real-binary seam test passes on hosted CI.
  Run 42468880068 fails installing pinned Spacedock: HTTP 504, curl exit 22; seam/transport/recovery skipped (ci-run.json, ci-failed.log). Runs 42468880154 and 42468880263 also remain failed. External outage, not a product defect; FO owns reruns.
- DONE: Local AC-8 wiring and missing-binary controls.
  CI step is after pinned install; deleting it removes the command, and unset SPACEDOCK_BIN exits 1 naming the variable. These local controls do not replace hosted evidence.
- DONE: Full package replay, original acceptance chain and candidate preservation.
  Original acceptance exits 0; all 28 CI-listed Python commands exit 0, 1223 tests reported with 11 optional skips; 13 original plus nine class and one AC-9 controls catch their mutations. Two exports each retain all 1582 tracked file bytes.
- DONE: Required gates, document dispositions, necessity and implementation limits.
  Number guards, record check, design surfaces and diff checks pass; comment ratio 3/776 = 0.4%, maximum 5%; all 13 document dispositions checked. Direct builder makes no record, wrapper commits one; evidence.md judges every stated limit.
- SKIPPED: Installed 0.35.0 ADR lint success.
  python3 -B /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0/scripts/adr_lint.py docs/adr --since 334d91e3165953b2ca7191e3308d80b6c02c4a99 --require 0070 exits 1 on the known ADR 0047 assertion; follow-up 2 authorizes candidate linter, exit 0 with 63 records.
- SKIPPED: Concurrent-writer safety, model execution, post-release adoption and delivery proof.
  Exclusive same-task ownership remains required; no transaction-lock claim. Model/roster, separate preflights, manual follow-ups and direct-builder bypass retain accepted limits. CI cost per PR unmeasured; triggers unchanged.
- SKIPPED: Local RoboRev and external review disposition.
  roborev not run: FO owns review/publication. This validator made no product or PR writes and grants no merge/release authority.

### Findings and disposition

Validation-2 F1 is fixed by the complete-scope precondition. The newly reproduced F2 was Material under old AC-5 and is now settled by Captain amendment 1 and passing AC-9; it is not reopened. No open Material, Deferred risk, Polish or Needs decision finding remains within the amended product scope; AC-8 is a missing external proof obligation.

### Summary

REJECTED for missing hosted evidence only: PR #812 at 778367adde2e20e0b3e51966ddba2d9f77f9e614 passes the amended local criteria and the class-preservation proof, while AC-8 remains blocked by the pinned download's HTTP 504. This complete cycle-3 report supersedes the prior validation reports; evidence is under validation-3/, and FO/Captain retain hosted rerun, gate, merge and release authority.
