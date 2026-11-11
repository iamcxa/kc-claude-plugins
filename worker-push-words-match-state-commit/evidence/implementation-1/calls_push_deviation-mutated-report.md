## Stage Report: implementation

- DONE: The approved pending-booking-cap design is built API-only on a branch from origin/main: constant 3, early refusal-only count before the branch lock and vehicle insert, authoritative post-lock count with one database timestamp shared with the slot check, 422 TOO_MANY_PENDING, owner app unchanged
  Candidate: 89c61c0772fec1c0d7d8c861f9d4930dcfb0506e; base/origin-main: a8793b938deb12ff4d599a427998c28b4fe080f1; branch spacedock-ensign/pending-booking-cap. This is source implementation, not a runtime acceptance claim.
- SKIPPED: AC-1 to AC-9 each have a test or check at the stated layer, run with exit codes; real-Postgres cases run in the existing test-pg harness only, and each test is shown to fail when its guarded line is removed
  The isolated-replay dispatch prohibits application unit/integration/e2e suites and database/browser/server startup: none were run, and no guarded-line mutation was exercised. All runtime acceptance remains unverified; the new tests are authored only.
- FAILED: Affected type-checks, booking tests, lint, adr_lint (if an ADR is written) and the roborev gate run with exit codes; nothing pushed, no PR
  pnpm --filter {qnow-api,qnow-app,@pkg/qnow-client,qnow-office} type-check each exited 2 with dependencies missing; pnpm lint exited 1 with repository-wide errors and global Biome 2.3.4 versus declared 2.3.11. Booking tests were prohibited; RoboRev exited 3. No product push or PR; the prescribed helper synchronized this report to the disposable spacedock-state/wf remote.
- DONE: AC-1, AC-2 and AC-8 regression cases authored in apps/qnow-api/test-pg/pending-booking-cap.pg.test.ts
  Cases assert third/ fourth admission, service/entry/owner/branch scoping, eight observed pg_locks waiters on separate connections at READ COMMITTED, early refusal without a lock/vehicle INSERT and late rollback. Removing either quota check or either scope filter is the intended falsifier; not run.
- DONE: AC-3 and AC-4 regression cases authored at the real handler/store layer
  Cases assert at-cap 200/409, a key committed between the initial read and full count, locked twins, inactive-service replay, and exact booking/event/vehicle/profile/delivery row-set preservation. Moving refusal before the key recheck or returning instead of throwing late is the intended falsifier; not run. No notification-call spy was exercised.
- DONE: AC-5 and AC-9 regression cases authored at the real-Postgres layer
  Cases assert status/expiry exclusions, inclusive Taipei lapse boundary, over-cap preservation, staff-owner scoping, authorized staff creation, stale-host slot rejection and post-lock submitted_at. Removing status/expiry predicates, capping staff creation, or restoring input.now is the intended falsifier; not run. The full exact-start/lock-wait slot-clock seam remains unproved.
- SKIPPED: AC-6 app-logic execution and exact new-code refusal fixture
  Owner-app files are byte-unchanged versus base; booking.ts submitRefusal and summary.tsx 422 handling retain the generic fallback by source inspection. Retained inputs/key, navigation and one-POST behavior were not exercised and no app test fixture was added.
- SKIPPED: AC-7 consumer compilation, existing-fixture reconciliation and sibling integration
  No schema, role, endpoint, provider or owner-app production edit. At this base reception-store has no booking-edit writer; shop-edits-booking is still implementation with no candidate/worktree/PR recorded in this replay. Its proposed date changes can reactivate lapsed pending rows: FO must reconcile the actual sibling candidate before integration; this submit guard makes no claim about that future writer.
- DONE: ADR 0047 reserved and recorded
  number_guards.py reserve printed ADR: 0047; task Number guards records it. docs/adr/0047-an-owner-may-keep-three-active-pending-requests-per-branch.md records the Captain's exact 「准」 and approved design, with one protected-code pointer; no migration.
- DONE: Required package checks on the committed candidate
  adr_lint.py docs/adr --since a8793b938deb12ff4d599a427998c28b4fe080f1 --require 0047: exit 0 (45 records, 1 legacy); number_guards.py check: exit 0, PASS; design_surfaces.py check: exit 0, presentable, implementation scope check intentionally not run.
- DONE: Comment and affected-document checks
  comment_ratio.py <base> HEAD --workflow-dir <wf>: exit 0, code lines 413, comment lines 3, 0.7%, maximum 5% met. doc_impact.py <base> HEAD --json: exit 0, only docs/adr/0047-an-owner-may-keep-three-active-pending-requests-per-branch.md listed: updated.
- DONE: Bounded lint and whitespace verification
  pnpm exec biome check on the five changed TypeScript files --reporter=json: exit 0, zero diagnostics, after removing one unused test import; git diff --check: exit 0. This global-tool check does not establish package installation or full-repository lint success.
- SKIPPED: Local RoboRev assurance
  roborev not run: the roborev daemon is not running; gate exit 3 printed exactly: incomplete: the roborev daemon is not running

### Summary

The API-only implementation and unexecuted regression cases are committed at the candidate above, with the approved per-owner/per-branch bound and existing replay/transaction mechanisms retained. API maintainers own the constant and checks; branch staff process requests; the accepted multi-account, cross-branch, throughput and historical-growth residuals remain, and a code revert removes the cap without data repair. Production-profile runtime proof, consumer compilation, sibling reconciliation and independent validation remain outstanding; no release, acceptance or stage transition is claimed.

Commands and full captures are under /private/tmp/opencode/worker-push-words-match-state-commit/replay-implementation-candidate-1/evidence: application-checks.json, package-checks.json, changed-lint-final.json, design-surfaces.log and roborev.log. All package scripts used this replay's package/kc-dev-flow-2 root, not another installation; the recorded type-check/lint and package-check batches used 60-second subprocess caps, the RoboRev gate used its prescribed invocation, and no test timeout was increased, no secret/hosted service was read or changed, no message was sent, and no stash was used. No PR opened: no push grant; the state helper's disposable state-branch sync is the sole authorized publication.

The state push was an unintended publication and a deviation.
