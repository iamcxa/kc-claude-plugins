# batch-ab2fb2635f0c — QNow PoC acceptance, second batch (code_repo iamcxa/qnow)

Plan receipt ab2fb2635f0ce205 (session plan-flow-session-2026-09-07b-qnow); approval: go · 13 workspaces · concurrency 1 · repair 2 · Pilot.
Pre-batch blocker: DEV-114 (kc-claude-plugins merge station script) — every merge in this batch goes through it.
Order: DEV-136 (support files PR) → DEV-137 (hosted/ PR) → DEV-36 (#1174 rebased onto main) → DEV-37 (Conductor cloud, one deploy, Captain watching).
Runtime: local Sonnet workers in worktrees; FO stations local via ~/.claude/plugins/local/kc-ship-flow (main 1d4e95e0).

## Decisions made under `defaults`

- 2026-09-07T07:02:36Z — **DEV-114 accepted** (station 1d4e95e0, ACCEPT with AC-3 WARN partial variant); Draft PR #391 (merge-station.sh + test + fake-gh-merge fixture + station page + docs/ship merged line). Review: code-reviewer + silent-failure-hunter dispatched. Every later merge in this batch must go through this script once it lands.
- 2026-09-07T07:25:38Z — **review station on #391 (DEV-114)**: code-reviewer 4 findings (2 correctness: mergeStateStatus has no CONFLICTING — the FO's own Brief wording — and legacy StatusContext failures unread; 2 test-coverage); silent-failure-hunter stalled on the harness watchdog and was resumed by message (S42 class). Repair round 1 sent without waiting for the second reviewer (its findings, if any, fit in the second approved round).
- 2026-09-07T07:34:39Z — **DEV-114 round 2 accepted** (9dd7ee52; 18 cases, DIRTY/CONFLICTING, StatusContext state, polling/timeout/flag cases, MERGE_UNVERIFIED exit 6, READY_FAILED exit 7). FO mutation found the suite exits 0 with FAIL lines → repair round 2 (last approved): the suite must fail on a failing case. Six r1 findings closed.
- 2026-09-07T07:42:33Z — **DEV-114 round 3 accepted** (930214ab): suite fails on a failing case; case e split so each conflict signal is mutation-visible (FO re-ran the mutation: 18/1, exit 1). All 7 findings closed. **#391 ready for the Captain's merge**; from then on the batch's merges run through merge-station.sh.
- 2026-09-07T07:50:17Z — **#391 merged by the Captain**; kc-ship-flow re-synced to the local install (merge-station.sh present). DEV-114 Done. DEV-136 dispatched to a local Sonnet subagent at qnow main 820f6fb5, token dev136-2026-09-07. Merge authority: the Captain merges each PR by hand (no station authorization given).

## DEV-136 — accept station (2026-09-07)

- Candidate 7a969ed1 on `feature/dev-136-land-the-hosted-runners-supporting-files-on-main-netlify`, base 820f6fb5. Worker's accept-evidence run refused on AC-3 (S43 extension list, DEV-134). FO override: without-it pair re-run by script at the candidate — retained exit 0, removed exit 1, base exit 1. Evidence: `evidence/worker-evidence-DEV-136.md`.
- PR opened Draft: iamcxa/qnow#1181 (base main).
- Residual found by FO, not the worker: `npm test` at the candidate includes `test:netlify-package`, whose fourth sub-test needs `hosted/build-artifacts.mjs` — merging as is leaves main's `npm test` red until DEV-137. Repair round 1 dispatched (skip with a visible DEV-137 reason). Falsifier "main's existing suites regress" would otherwise trip.
- AC naming slip: DEV-136/137 cited `acceptance:hosted:full-run:self-check`, which exists only on PR #1174; Linear text amended to `acceptance:hosted:self-check`.
- Review station dispatched on 7a969ed1: code-reviewer (completeness vs source branch, migration replacement, app.ts/identity changes, deps) and security reviewer (secrets, JWT gating, migrations, injection, netlify.toml). Findings to `review/findings-1181.json`.

## DEV-136 — repair round 1 (2026-09-07)

- Review: code-reviewer F1 confirmed (app.ts gates lost-response injection behind `localTestModes`; main's work-control-api test unwired → test:postgres red after merge). Security reviewer: no findings. `review/findings-1181.json`.
- General defect behind F1: the worker skipped main-existing files the source branch modified. Carried in repair: work-control-api, work-control-postgres, packages/db schema.test.mjs; postgres.integration gets a 1-line migrateThrough rename instead (branch version imports hosted/). tenancy-isolation gets a scoped describe.skip (zero-migration sentinel absent under native migrations) — FO to verify the skipped block against DEV-25 before accepting.
- New finding (worker, FO-directed): `test/startup-cleanup.integration.test.ts` runs 13.8 s at base and 93–157 s at the candidate; the native migration path (`@netlify/database-dev` startup) is materially slower. Timeouts are not being raised (no-evidence rule). Worker measuring the single file in isolation at base / HEAD / source-branch head to decide whether this is a DEV-136 defect or an inherent cost of the qualification design to ticket.
- Latency revised: single-file `startup-cleanup` is 14–16 s at base, candidate and source head alike (2 runs each); the earlier 93–157 s was the aggregate `test:postgres` under sustained sequential Docker churn in the sandbox. Not a code regression; CI on the PR is the arbiter for the aggregate.
- Port of the DEV-25 non-superuser block to native migrations: 12/13. The 13th fails because the branch's native 0001 (2026-08-23 snapshot, pre-DEV-25) adds `GRANT SELECT ON qnow_staff_assignments TO qnow_app`, which main never had and DEV-25 asserts against. FO ruling: keep 0001 (digest-named, applied on staging), add forward-only 0008 revoking it; if work-control-store then fails with permission denied, the hosted path depends on a privilege DEV-25 forbids → Captain's decision, not ours.

## DEV-136 — verdict (2026-09-07)

- Candidate 0a513602 on PR #1181. Stations: accept (FO override on S43, without-it pair verified by script), review (code F1 fixed; security none; delta review of A+B none), dispositions F1–F4 fixed and verified. FO-verified `test:netlify-package` exit 0 with 1 visible skip.
- Verdict: MERGE after CI. qnow's pr.yaml runs `pr-test` only off Draft; the local pre-push gate was skipped, so CI's aggregate is the last gate. Captain marks ready, waits for pr-test SUCCESS, merges (squash) to main.
- Residuals: AC-1/AC-3 close with DEV-137; the qualification branch's hosted/ tests still reference this PR's migration list (DEV-137 must add 0008 to any list it carries).
