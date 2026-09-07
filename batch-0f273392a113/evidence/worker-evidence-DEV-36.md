## Evidence
DISPATCH_TOKEN: dev36-repair-2026-09-07-r1
CANDIDATE_SHA: b5d87ed862a92dd1d4187f0773d4f4e9cdcccf52
BRANCH: conductor/dev-36-qnow-esm-runner
BASE_SHA: 3c65da1e99eef40ca7f093128b309a2da9861008
FILES: hosted/acceptance-execution.ts, hosted/acceptance-full-run-dependencies.mjs, hosted/acceptance-full-run.mts, hosted/acceptance-netlify-session.ts, test/acceptance-execution.test.ts, test/acceptance-full-run-dependencies.test.mjs, test/acceptance-full-runner.test.ts, test/acceptance-netlify-session.test.ts, test/identity-bootstrap.test.ts (all under experiments/netlify-refine-poc/qnow-next/)
TESTS: npm run type-check -> exit 0; npm run test:unit -> exit 0 (180 passed); npm run test:netlify-package -> exit 0 (106 passed); npm run acceptance:hosted:full-run:self-check -> exit 0
WITHOUT_IT_COMMAND: cd experiments/netlify-refine-poc/qnow-next && npx vitest run --config vitest.config.ts test/identity-bootstrap.test.ts -t "admits create-users after a 12-minute deploy" 2>&1 | grep -c "Tests  1 passed"
WITHOUT_IT_REMOVED_VARIANT: sed -i '' 's/BOOTSTRAP_WINDOW_MS = 15 \* 60_000/BOOTSTRAP_WINDOW_MS = 10 * 60_000/' experiments/netlify-refine-poc/qnow-next/hosted/acceptance-full-run-dependencies.mjs
WITHOUT_IT_OBSERVED: worker: retained 0; removed 1; base 1. FO: retained 0; removed 1 (variant applied 1 line); type-check 0; test:unit 180; netlify-package 106; self-check 0
SELF_CHECK: accept-evidence: REFUSE: AC-3 extension list (S43/DEV-134)
ROBOREV: UNAVAILABLE(reason: no reviewer binary in workspace)
F1..F8: run id out of paths (random evidence token) + test; bootstrap window 15 min = shared MAX_WINDOW_MS ceiling, 12-minute-deploy test; deployAttempted latched after pre-flight at both layers + tests; error id printed before generic; entrypoint unresolved surfaced non-zero; receipt reader throws UNREADABLE except ENOENT + tests; countedNetlifyApi method-list mutation test; rehearsal fields under browserRehearsal (no post-run census exists)
BLOCKER: station AC-3 extension list (.ts/.mjs)
