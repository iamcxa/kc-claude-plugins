## Stage Report: validation

- DONE: Independent verdict on PR #812 head bd9d4abc against every acceptance criterion in the task file, re-running each evidence command and at least one falsifier per criterion yourself, and judging each limit the implementation report states
  PASSED at bd9d4abce4e0c61a69079d4e822b6ded45cfdc20, base 334d91e3165953b2ca7191e3308d80b6c02c4a99; validation-4/evidence.md records all active criteria, independent commands, counterexamples and each limit.
- DONE: Judge the repair of the second Codex P2 (review comment 4505793059: successful record checks' step-back warnings now reach the wrapper's stderr) and every active criterion again at this head, including Captain amendment 1's AC-9; validation-3 at 778367adde2e20e0b3e51966ddba2d9f77f9e614 is the prior verdict, and the FO rulings in dispatch/implementation-1-message-1.md and -message-2.md still stand. Read every inline review comment on PR #812 and say whether any is unaddressed at this head. Report AC-8 from the hosted run on this exact head. Keep any download under a new /tmp directory, never in the task state folder.
  Both review comments are technically fixed; GitHub threads remain unresolved administratively. Two real-binary warning tests and four targeted mutations prove before-build, once-only and distinct-warning behavior; hosted run 42476440927 attempt 1 passes for this head.
- DONE: A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0/scripts/adr_lint.py docs/adr --since <base> with its exit code; your verdict naming the head, with findings classified by the workflow's Review-finding disposition
  validation-4/acceptance.sh ran from its final path in fresh bash, exit 0, captain-final.log PASS 1–6. Installed ADR lint exit 1 is the settled pre-#806 false positive; authorized candidate lint exits 0 for 63 ADRs.
- DONE: AC-1 and AC-2 — committed complete records contain the worker's exact inputs.
  Real stamped subject, both checkers and envelope pass; no-stamp/no-Model/dropped-scope mutations fail their expected assertions.
- DONE: AC-3 and AC-4 — incomplete records and absent/malformed candidates hold before build.
  State and task stay unchanged, no envelope or builder call; removal omission, build-before-check and ignored-checker controls fail.
- DONE: AC-6 and amended AC-9 — advance persistence, retry numbering and accepted outside-staging limit.
  Real failures withhold envelope and preserve data in both layouts; no-removal/no-reuse/bytes-only-reuse/no-state-commit plus outside-staging mutations fail.
- DONE: AC-7 — approved passages, reduced budget, observer coupling and existing consumers.
  5931/5931 words; 47 lint and 115 record tests plus pinned real transport pass; restored base passages and observer entry fail.
- DONE: AC-8 — exact-head hosted real-binary seam evidence.
  hosted-run.json binds bd9d4abce4e0c61a69079d4e822b6ded45cfdc20; job 128718733545 passes installation, 22 seam tests, transport and recovery on this head's PR merge ref. Unset binary exits 1 and deleted-step wiring control holds.
- DONE: Full regression, preservation class and falsifier sensitivity.
  Unchanged implementation acceptance exits 0; all 28 CI Python commands exit 0 (1225 reported tests, 11 optional skips); 98 unchanged snapshots/92 matrix cases, 13 original controls, nine scope and four warning mutations, plus two additional controls.
- DONE: Required guards, document dispositions, goal sufficiency and minimal necessity.
  Number guards, dispatch records, design surfaces, doc impact and diff checks pass; comments 3/822=0.4% below 5%; all 13 document dispositions verified, direct-builder bypass exercised, exported bytes and clean candidate preserved.
- DONE: Judge all stated limits without promoting validation to delivery.
  Model/roster/manual follow-ups/separate preflights remain accepted exclusions; exclusive same-task ownership, accepted AC-9 limit and pending-record recovery remain explicit; actual adoption/model execution/concurrency/RoboRev/gate/merge/release are not claimed. CI cost per PR unmeasured; triggers unchanged.

### Findings and disposition

Both previously Material Codex comments (4505536959 and 4505793059) are fixed at this head; no technical review comment remains unaddressed. Captain amendment 1 settles the former AC-5 finding, and AC-9 passes. No open Material, Deferred risk, Polish or Needs decision finding; FO owns the still-unresolved GitHub threads and delivery actions.

### Summary

PASSED: PR #812 at bd9d4abce4e0c61a69079d4e822b6ded45cfdc20 meets the amended Pilot criteria, including hosted AC-8 and the successful-check warning repair. This complete report supersedes earlier validation verdicts; evidence is under validation-4/, and FO/Captain retain gate, merge and release authority.
