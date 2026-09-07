## Evidence
DISPATCH_TOKEN: dev136-2026-09-07
CANDIDATE_SHA: 7a969ed119d55955845fa40020c6c3af94f918c3
BRANCH: feature/dev-136-land-the-hosted-runners-supporting-files-on-main-netlify
BASE_SHA: 820f6fb5e155c352a75181c0662e3f866e581dc2
FILES: experiments/netlify-refine-poc/qnow-next/{netlify/database/migrations (8), netlify.toml, identity/*.ts, api/app.ts, db/acceptance-controller.ts, schema/migration-runner.ts, local/*.ts, test/* (13), package.json, package-lock.json}, scripts/qnow-next-hosted-preflight.mjs; schema/0000_claim_slice.migration removed (superseded by native migration 0001)
TESTS: npm run type-check -> exit 0; npm run test:unit -> exit 0 (142); npm run test:native-migrations -> exit 0 (6); npm run test:hosted-gates -> exit 0 (7, scoped); npm run test:netlify-package -> exit 1 (3/4; the 4th needs hosted/build-artifacts.mjs → DEV-137); npm run test:secret -> exit 0; acceptance-postgres integration -> exit 0
SURFACE: experiments/netlify-refine-poc/qnow-next/local/postgres-docker.ts -> AC-2 | npm run test:secret | git checkout 820f6fb5e155c352a75181c0662e3f866e581dc2 -- experiments/netlify-refine-poc/qnow-next/local/postgres-docker.ts
WITHOUT_IT_COMMAND: node --test experiments/netlify-refine-poc/qnow-next/test/hosted-preflight.test.mjs
WITHOUT_IT_REMOVED_VARIANT: sed -i.bak "s#'../../scripts/qnow-next-hosted-preflight.mjs'#'../../scripts/qnow-next-hosted-preflight-WRONG.mjs'#" experiments/netlify-refine-poc/qnow-next/test/hosted-preflight.test.mjs
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 1; at BASE_SHA -> exit 1
SELF_CHECK: accept-evidence: REFUSE: AC-3 extension list (S43/DEV-134)
ROBOREV: UNAVAILABLE(reason: no reviewer binary in workspace)
AC-1: not this PR (hosted/ is PR 2) AC-2: all except netlify-package 4th sub-test (hosted/-dependent) AC-3: closes with DEV-137
BLOCKER: station S43; residuals: `acceptance:hosted:full-run:self-check` does not exist on the branch (only `acceptance:hosted:self-check`, hosted/-dependent) — ticket naming slip; AC-1/AC-3 describe the post-DEV-137 state

## Evidence (repair round 2, final)
DISPATCH_TOKEN: dev136-2026-09-07-r2
CANDIDATE_SHA: 0a513602fe8e764bfb48835d8a170b3f94fcf1cd
BRANCH: feature/dev-136-land-the-hosted-runners-supporting-files-on-main-netlify
BASE_SHA: 820f6fb5e155c352a75181c0662e3f866e581dc2
COMMITS: 7a969ed1 (round 1) + 15480a46 (A: carried main-test edits, netlify-package skip) + 0a513602 (B: DEV-25 block ported to native migrations, 0008 revoke)
TESTS (worker): type-check 0; test:unit 0 (142); test:native-migrations 0 (6, incl. 0008); test:hosted-gates 0 (7, scoped); test:secret 0; packages/db test 0 (10); single-file tenancy-isolation 0 (13/13); single-file work-control-postgres 0 on retry (27/27; first attempt Docker cold-start hook timeout, not permission-denied); single-file postgres.integration 0 (14/14)
TESTS (FO-verified at 0a513602, fresh npm ci): test:netlify-package -> exit 0, 1 skipped with visible DEV-137 reason (the worker's block said exit 1; that value was stale)
WITHOUT_IT: unchanged (retained 0 / removed 1 / base 1, FO-verified at 7a969ed1; test file untouched by A/B)
SELF_CHECK: REFUSE AC-3 (S43/DEV-134, .mjs path extraction) — FO override stands
PRE_PUSH_GATE: skipped (SKIP_PRE_PUSH=1) — whole-monorepo vitest pool mirrors CI's pr-test; CI runs once the PR leaves Draft (pr.yaml gates classify/pr-test on draft == false)
AC-1/AC-3: post-DEV-137 state by design of the split; AC-2: all named suites pass except the hosted-dependent sub-test (skipped, DEV-137)
