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

## DEV-136 — supply-chain check (2026-09-07, after the Captain asked whether 20k lines is mergeable)

- Size: +17465/−2501 is package-lock.json (netlify-cli 27.3.0 + @netlify/dev pull 1057 packages, 5 new install-script packages, all dev-tree); runtime code +1668/−137; tests + migrations ≈ +2700.
- Findings: fflate 0.8.2 in CVE-2026-45820 range (test-only call site) → repair round 3 bumps to 0.8.3. @netlify/dev 5.0.1→5.0.5 available, @netlify/identity type-only but in dependencies, netlify-cli transitive highs unfixable → follow-up ticket blocked by DEV-137 (toolchain pins are contract-tested as a set). Identity code: no insecure defaults.
- FO omission recorded: the review station did not trigger the supply-chain lane on a deps change; kc-pr-review's triage rule does. Add to DEV-134/135 class of station fixes.
- Round 3: 4d13d179 bumps fflate to 0.8.3 (single lock entry, dev tree); worker: test:netlify-package 0 (1 skip), test:native-migrations 0. FO verified the package.json/lock pins at the pushed SHA. Final verdict unchanged: MERGE after CI pr-test at 4d13d179.

## DEV-136 — merged (2026-09-07)

- Captain: "幫我合併，然後繼續". Marked ready; CI pr-test (node-tests, test-summary) + ci-gate passed, 8/8, MERGEABLE/CLEAN, base main verified; squash-merged → main 4122d2be. DEV-136 → Done in Linear.
- DEV-137 dispatched next with BASE 4122d2be, token dev137-2026-09-07 (brief: evidence/dispatch-DEV-137-subagent.md, amended).

## DEV-137 — accept station and PR (2026-09-07)

- Round 1 (1901bc94): hosted/ byte-identical but 8-migration and open-api 2.57.0 assumptions fail against main → FO rulings recorded in evidence/worker-evidence-DEV-137.md. Round 2 (269b90e0): six 8→9 literals, lock restored to the branch's + fflate, scripts block; FO-verified without-it pair, lock diff fflate-only, netlify-package 69 ok. Round 3 (087b36e4): preflight script 8→9 with a refusing test case (test:hosted-gates 19/19, self-check providerCalls 0).
- Accept: S43 refusal overridden by FO script verification. Draft PR iamcxa/qnow#1182 opened (56 files, +10262/−520). Reviews (code, security) dispatched on 269b90e0; the 087b36e4 delta is two files, FO-read.

## Correction (2026-09-07): CI never ran qnow-next's tests

- The DEV-137 code review found, and FO verified by grep, that nothing in `.github/` references qnow-next; CI's pr-test filters the pnpm packages only. My verdicts for #1181 and #1182 said "CI's pr-test is the aggregate gate" — false. #1181's green CI exercised none of qnow-next. Ticket filed (see Linear, QNow project). For #1182 the FO runs the full `npm test` locally at the final candidate as the substitute, and reports it as such.

## DEV-137 — full npm test at 5b1faa18 FAILED (2026-09-07), decision for the Captain

- test:postgres 3 failed / 68 passed: acceptance-postgres.integration ×2 and the branch's postgres.integration ×1, all `42501 permission denied` on `SELECT … FROM qnow_staff_assignments WHERE subject_id = $1 AND active` while running as `qnow_app` (the hosted runtime pool does `SET ROLE qnow_app`). Everything else green (secret 2, unit 169, native-migrations, netlify-package, hosted-gates).
- Root cause: the hosted runtime reads staff assignments as qnow_app through db/work-control-store.ts; DEV-25 (main) asserts qnow_app has no privilege on that table, and my DEV-136 migration 0008 revoked the branch's grant. My F4 "store tests pass under the revoke" was measured on main's test, which runs as the owner — the evidence did not cover the hosted role. Correction recorded.
- Options: (A) re-grant SELECT (branch's original; qnow_app can then read every tenant's subject→tenant mapping, the table has no RLS — weakens DEV-25); (B) keep DEV-25, add migration 0009 with a SECURITY DEFINER function `qnow_active_assignments(subject uuid)` granted to qnow_app and point the store at it (small, tested, preserves the invariant). FO recommends B. Captain rules.
