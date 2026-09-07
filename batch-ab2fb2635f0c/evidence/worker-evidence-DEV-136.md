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
