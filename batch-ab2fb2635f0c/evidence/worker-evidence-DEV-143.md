## Evidence (from PR #1183 body; worker's final reply omitted the block)
DISPATCH_TOKEN: dev143-2026-09-08
CANDIDATE_SHA: fba04c0f
BRANCH: feature/dev-143-rollback-admission-by-own-count → PR #1183 (Draft, base main)
FILES: hosted/runtime-receipt-diagnostic.mjs (expectedMigrations parameter, no default; CLI keeps CLI_EXPECTED_MIGRATIONS=10), hosted/acceptance-full-run-dependencies.mjs (forwards input.expectedMigrations; gates nativeMigrationCount), hosted/acceptance-netlify-session.ts (ROLLBACK_MIGRATIONS=8 at bindBaseline; 10 at candidate), hosted/acceptance-environment.mjs (four baseline ids → failureReason, phase provider_baseline_admission); 5 test files
TESTS (worker): type-check 0; test:unit 204; test:hosted-gates 19; test:netlify-package 110; both self-checks providerCalls 0; full npm test exit 1 on a Docker hook timeout in work-control-postgres (unrelated file), 27/27 standalone
FO: full npm test + self-check + without-it mutation (ROLLBACK_MIGRATIONS 8→10 must fail the session test) running at fba04c0f; delta review dispatched
