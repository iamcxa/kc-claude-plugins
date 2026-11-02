
## Stage Report: validation

- DONE: Independent verdict on PR #765 head c2643dae against every acceptance criterion in the task file, re-running each evidence command and at least one falsifier per criterion yourself, and judging each limit the implementation report states
  PASSED at c2643dae831f9685166b7cd564d8d885e88a3f21 against fetched origin/main e891e83582ac10936ffd67fb083b530b009ad847; validation-3/evidence.md maps all eleven criteria, commands, falsifiers and limits. AC-10 is explicitly post-release.
- DONE: This rerun's ruling is Captain amendment 2 in the task file. Re-judge F1, F2 and F5 of validation-2 and the shared list reader. FO's final AC-6 run on this exact head is native-runs/final/README.md and receipts.json; judge it as FO's record and name any gap. Do not start agents yourself
  F1/F2 resolved: the FO run, linked primary transcripts and matched inbound events establish distinct Opus high/low, Codex model/xhigh, and later completion for all four children; no send or second route. F5 remains installed-copy drift; no validator agent started.
- DONE: A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/adr_lint.py docs/adr --since <base> with its exit code; your verdict naming the head, with findings classified by the workflow's Review-finding disposition
  validation-3/acceptance.sh ran unchanged with bash --noprofile --norc, exit 0, all five steps PASS; acceptance.md includes full commands/output. Assigned ADR lint --since e891e83582ac10936ffd67fb083b530b009ad847 exits 0: 49 records, 0 legacy; required 0050 also passes.
- DONE: Re-run package CI commands, criterion mutations and the shared-reader compatibility comparison.
  All 26 commands exit 0, 1009 unittest cases including 7 unchanged skips; 16 criterion mutations fail, and all 3 shared-reader mutations fail in both callers while empty/no-key controls pass. All 190 committed-task verdicts match main.
- DONE: Verify AC-1 through AC-5 and AC-7 through AC-9 with bounded behavioral evidence.
  Both callers preserve manifests; all provider/model/effort and family cases pass; live CLI yields ask and fresh Paseo options match. Mutating prerequisites, pairings, defaults, mapping, family, absence, ADR status or workflow words fails the relevant check.
- DONE: Verify AC-6 and AC-11 at their declared seam.
  FO's committed fixture resolves at this head; process/transcript fields and exact later receipt IDs agree. Equal-control/missing-receipt record falsifiers fail. Provider-host builds emit opus/null/null; omitting --host on Claude emits sonnet. No child was spawned by this validator.
- DONE: Check required guards, affected documents, scope and hosted candidate.
  Number/design guards and parity pass; workflow diff is empty at 5781 words; comments 1/268 (0.4%). All seven affected documents are dispositioned in evidence.md. PR #765 remains OPEN at this exact head with five successful hosted checks.
- SKIPPED: Seven existing environment-conditional suite cases.
  Four amendment/history corpus cases, one Node/yaml bridge, one optional dispatch-builder case and one external-obligation corpus case; no new skip or CI trigger.
- SKIPPED: A clean exact-head RoboRev result and product delivery.
  Local review gate exits 3: incomplete: the roborev daemon is not running. FO retains review and delivery; no product push, PR write, ready transition, merge or release performed.
- SKIPPED: AC-10 — released-package update of consumer PR #762 and Captain merge request.
  Owed by FO after release; #762 is still OPEN/Draft. No predicted version, unreleased-script substitution or pre-release falsifier accepted.
- DONE: Assess goal sufficiency, minimal necessity and implementation limits.
  The bounded Pilot journey passes; base rejects Opus and each retained behavior has a failing counterexample. Nine scoped files, one shared stdlib reader, no dependency/workflow/CI change; cost per PR and model spend not measured.
- DONE: Preserve the candidate and remove owned validation checkouts.
  cleanup.json records the detached checkout and owned fixture copies removed; assigned branch remains clean at c2643dae831f9685166b7cd564d8d885e88a3f21. Other state work is untouched.
- F5 Polish: The assigned Claude 0.34.0 cache rejects six saved final-reply lines, while the loaded Codex 0.34.0 cache and candidate accept all eight records; historical records remain unchanged and no candidate harm is demonstrated. Digests and four disposition fields: validation-3/evidence.md.

### Summary

This report supersedes the earlier validation reports and recommends PASSED for c2643dae831f9685166b7cd564d8d885e88a3f21. The shared-reader repair, current package checks and independently corroborated FO native run meet all currently due criteria; FO retains local review, the delivery decision and AC-10 after release.
