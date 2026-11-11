## Stage Report: validation

- DONE: Independent PASSED or REJECTED verdict on candidate 32901fe5f34fb17ae9a5741cff88471d55e81288 (base 706b01fdb04b5d0b17b213562296dc95eaa60368) against AC-1 to AC-12 of owner-cancels-booking.md: one row per criterion with real evidence or an explicit unverified reason; re-check rather than trust evidence/implementation-1/
  REJECTED for missing independent runtime evidence; AC-1 to AC-12 below are individually UNVERIFIED, not product failures or reused implementation passes.
- FAILED: Close what the implementation report left open: the lost-reply recovery at the final candidate with a real pointer click (AC-9); office focus refetch and the read-only drawer at the final candidate (AC-5); staff complete or cancel forced interleavings against an owner cancel in real PostgreSQL 18 (AC-7); a competing second-owner confirmation for the released slot (AC-2)
  AC-9 pointer recovery, AC-5 focus/drawer, AC-7 PostgreSQL interleavings and AC-2 competing confirmation were not run: replay harness prohibits browsers/databases/servers.
- SKIPPED: Every PASS has a positive control that fails at the base or with the relevant hunk reverted in a scratch copy; say which
  No acceptance criterion is PASS; no base/hunk positive control was executed. Package checks alone do not prove product behavior.
- FAILED: Run migration 0027 on a disposable database seeded with all six statuses and an old-code staff write after it, and confirm the narrow owner writer is the only path that can set cancel_source owner (no general UPDATE grant)
  Migration 0027 was not applied and old-code/owner permission probes were not run: disposable databases are prohibited in this replay.
- FAILED: Pictures at 390, 834 and 1440 of the states you verify, phone text masked immediately before each capture after any viewport change, absolute paths in the report
  No current screenshots were captured at any requested width: browser execution is prohibited; no prior picture is promoted to candidate validation evidence.
- SKIPPED: Judge, under Review-finding disposition with the four evidence fields, the repeated sentence on the withdrawn and cancelled result cards (「您已撤回這筆預約，店家不會再確認。」 then 「已撤回預約，店家不會再確認。」) and the test-only /__fixture routes (confirm they exist only in apps/qnow-api/test-pg/support and are not reachable from any production entry)
  Source-only dispositions are in evidence/validation-1/findings.md (F4 Polish and F5 Deferred risk); deployed fixture nonreachability and built-screen rendering remain unverified.
- SKIPPED: Run the affected unit suites, the real PostgreSQL suites, type-checks and lint at the candidate
  Application unit/integration/e2e and real PostgreSQL suites were not run by harness instruction; type-check/lint dependencies are absent, no install attempted. Package checks are recorded separately.

### Summary

Verdict: REJECTED — independent product acceptance is incomplete in this isolated replay; no product runtime defect is asserted.
Candidate: 32901fe5f34fb17ae9a5741cff88471d55e81288; base: 706b01fdb04b5d0b17b213562296dc95eaa60368; profile: pilot (bounded real-use journey); package: isolated kc-dev-flow-2 0.38.1.
Package commands and exits: evidence/validation-1/checks.json and role-triggers.log; ADR lint (--since base --require 0061), number guards, comment ratio, dispatch records and doc impact exit 0. Design surfaces exits 1: built-screen review missing; see design-surfaces.log. No application suite, build, server, database, browser, screenshot or secret was used.
Evidence read is not evidence rerun: prior implementation claims stay historical. Retained-document disposition coverage and added comments were inspected; detailed limits, four-field finding dispositions and the minimal acceptance command are in evidence/validation-1/findings.md. The Captain script checks only replay identity/package behavior and expects the unresolved design gate; it cannot authorize delivery.

### Per-criterion evidence

| Criterion | Verdict | Independent evidence or unverified reason |
| --- | --- | --- |
| AC-1 | UNVERIFIED | No owner browser action, API refusal or SQL event/confirmation readback; harness prohibits runtime. |
| AC-2 | UNVERIFIED | No capacity-one cancellation, transaction visibility or competing second-owner confirmation. |
| AC-3 | UNVERIFIED | No branch-contact/device navigation or held-lock cutoff probe; dependency-present contract not exercised. |
| AC-4 | UNVERIFIED | No reason normalization/Unicode/strict-body runtime probes or SQL readback. |
| AC-5 | UNVERIFIED | No final-candidate focus refetch, pointer/keyboard drawer, staff/window/isolation probe. |
| AC-6 | UNVERIFIED | No real caller/API/SQL permission probes; fixture source isolation is not a production reachability test. |
| AC-7 | UNVERIFIED | No real PostgreSQL staff-complete/cancel interleaving, replay, rollback or lock-removal control. |
| AC-8 | UNVERIFIED | No browser/mobile keyboard, screen reader, held-request sampling or current viewport captures. |
| AC-9 | UNVERIFIED | No actual-pointer lost reply/readback retry, stale-auth/navigation matrix or final-state DOM/SQL readback. |
| AC-10 | UNVERIFIED | No event/delivery counts or forced sender/cancel interleaving; no notification sent. |
| AC-11 | UNVERIFIED | No six-status migration replay, old-code staff write or narrow owner-writer exercise. |
| AC-12 | UNVERIFIED | ADR lint passed; no new built-screen review, Mermaid rendering, served-asset proof or dependent first-send rebooking. |

### Findings and handoff

- F1 Needs decision: runtime acceptance blocked by replay scope; FO must route the remaining normal validation without lowering the criteria.
- F2 Needs decision: design-surfaces rejects missing built-screen review; dispatch leaves the director review with FO.
- F3 Needs decision: Migration 0027 has no Applied at:/Not applied:/Applied: none record; number-guard PASS does not fill this FO-owned omission.
- F4 Polish: withdrawn/cancelled explanation and success notice repeat the outcome in source; no runtime loss demonstrated, no repair or director decline claimed.
- F5 Deferred risk: /__fixture definitions/consumers found only in test-pg/support and separate from inspected production entries; bundle/live nonreachability unverified.
All four evidence fields per finding: evidence/validation-1/findings.md. Product bytes/branch, YAML frontmatter and all prior entity text are preserved. No code/PR/hosted publication, agents or peer messages; only this report and its evidence are committed/synced to the disposable state origin. FO retains validation gate and all delivery decisions.
