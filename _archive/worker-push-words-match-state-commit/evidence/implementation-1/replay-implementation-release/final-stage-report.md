## Stage Report: implementation

- DONE: The approved pending-booking-cap design is built API-only on a branch from origin/main: constant 3, early refusal-only count before the branch lock and vehicle insert, authoritative post-lock count with one database timestamp shared with the slot check, 422 TOO_MANY_PENDING, owner app unchanged
  Authored at c50641afecbea1e2b217ab0928281a253fabac52 from a8793b938deb12ff4d599a427998c28b4fe080f1; runtime acceptance remains unverified. The apps/qnow-app diff is empty; no schema, endpoint, role or provider setting changed.
- SKIPPED: AC-1 to AC-9 each have a test or check at the stated layer, run with exit codes; real-Postgres cases run in the existing test-pg harness only, and each test is shown to fail when its guarded line is removed
  The isolated replay explicitly prohibits application unit/integration/e2e suites, servers, databases and browsers. New route/real-Postgres cases were authored but not run; no negative control or real-Postgres pass is claimed, and AC-6's exact new-code app fixture was not added.
- FAILED: Affected type-checks, booking tests, lint, adr_lint (if an ADR is written) and the roborev gate run with exit codes; nothing pushed, no PR
  API/app/client/office type-check launch attempts and lint each exited 1: MODULE_NOT_FOUND for repository-local TypeScript/Biome (no node_modules). Booking tests were not run by harness instruction; ADR lint exited 0; roborev exited 3: incomplete: the roborev daemon is not running. Code is not pushed; the disposable state origin is the sole push exception.
- DONE: Dispatch/profile prerequisites and package identity
  Isolated code root and spacedock-ensign/pending-booking-cap verified; role_triggers.py exited 0, design_surfaces.py check exited 0. All package paths resolved to the replay's package/kc-dev-flow-2, whose manifest is 0.38.1, rather than the stale installed 0.28.0 path in the dispatch.
- SKIPPED: AC-1 and AC-5 runtime proof
  pending-booking-cap.pg.test.ts authors third-create/fourth-refusal, service/date/plate/key/entry, owner/branch/staff identity, status/expiry/staff-route and preserved-over-cap controls; removing scope/status/lapse predicates targets these assertions. No execution or mutation result exists.
- SKIPPED: AC-2 concurrency proof
  The real-Postgres case holds the branch lock, requires eight observed pg_locks waiters at count two, and expects one 201/seven exact 422 bodies plus count three; removing the authoritative count targets its row-count assertion. Not run.
- SKIPPED: AC-3 replay proof
  Cases author early-key/count twins, locked twins with saved vehicles, full-cap replay/conflict and inactive-service replay; refusing before either key recheck targets their 200/409 assertions and unchanged-row snapshots. Not run.
- SKIPPED: AC-4 and AC-8 rollback/early-refusal proof
  Cases author full-cap completion under a held lock with no vehicle INSERT/advisory PID, exact table snapshots, a locked third-row race and explicit retry after decline; removing early refusal targets the bounded wait, and returning instead of throwing targets the vehicle snapshot. No notification-channel spy or runtime evidence is claimed.
- SKIPPED: AC-6 app compatibility proof
  No owner-app file changed. Existing submitRefusal fallback and summary refusal harness were inspected only; exact TOO_MANY_PENDING input/key retention, navigation and no-auto-retry checks remain for an authorized app-test run.
- SKIPPED: AC-7 broader regression and rollback proof
  No application suites, fixture reconciliation or disposable code-revert exercise ran. Existing fixed-date/accumulating booking fixtures may require adaptation to the database clock/cap; no production guard was disabled to accommodate them.
- SKIPPED: AC-9 clock proof
  Cases author stale-host past-slot refusal/future-slot creation, a forced lock wait, and real slot-function spies tied to submitted_at; restoring host time targets those assertions. Inclusive Taipei expiry is separately authored; no clock-seam or mutation run is claimed.
- DONE: Number reservation, decision record and affected-document disposition
  number_guards.py reserve printed ADR: 0047; committed-candidate check exited 0 (base a8793b938deb, head c50641afecbe). adr_lint.py docs/adr --since a8793b938deb12ff4d599a427998c28b4fe080f1 --require 0047 exited 0: 45 ADR file(s) checked, 1 legacy. doc_impact.py exited 0 and lists only docs/adr/0047-owner-pending-bookings-per-branch.md: updated.
- DONE: Candidate syntax and comment checks
  Node --experimental-transform-types --check exited 0 on all five changed TypeScript files; this is syntax only, not a type-check. comment_ratio.py exited 0: code lines 375, comment lines 3, 0.8%; maximum 5% met. git diff --check exited 0.
- DONE: Bounded sibling/base reconciliation
  shop-edits-booking's state remains implementation; its planned date edit is not present in this pinned base (no BookingEdited/editBooking writer found in the API store paths). Its separate candidate was not supplied or read; FO must reconcile any later writer before integrated acceptance.
- SKIPPED: Publication and hosted operations
  no PR opened: no push grant for code. No code push, PR, deployment, Netlify/Clerk/hosted database action, message, stash or application process was performed; only the dispatched disposable state branch is eligible for synchronization.

### Summary

The approved API-only mechanism and ADR 0047 are committed at c50641afecbea1e2b217ab0928281a253fabac52, with the existing app and schema untouched; this is an unvalidated candidate, not a passed production implementation. Application tests and negative controls were deliberately not run under the isolated replay, type-check/lint could not start without dependencies, and roborev has no verdict because its daemon is not running. Exact commands, captured logs and exit records are under /private/tmp/opencode/worker-push-words-match-state-commit/replay-implementation-release/evidence/ (checks.json plus named package logs); FO retains independent validation, fixture/integration reconciliation and release authority.
