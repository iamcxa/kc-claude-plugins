## Evidence (round 1)
DISPATCH_TOKEN: dev137-2026-09-07
CANDIDATE_SHA: 1901bc94a020ad46ae39483aeff298bc97f4cbd2
BRANCH: feature/dev-137-land-experimentsnetlify-refine-pocqnow-nexthosted-on-main-pr
BASE_SHA: 4122d2be3c61a6b4fe69de133d069978f62af12d
FILES: hosted/ 26 files byte-identical to the branch; 23 hosted-owning tests; netlify-package/postgres.integration/netlify-local tests carried with 0008 appended; package.json gains build:hosted and acceptance:hosted:self-check
TESTS: type-check 0; test:hosted-gates 0 (7/7); test:netlify-package 1 (HOSTED_NATIVE_MIGRATION_NOT_CONTENT_BOUND — hosted/build-artifacts.mjs expects 8 migrations, main has 9); acceptance:hosted:self-check 1 (ACCEPTANCE_NETLIFY_ENVIRONMENT_API_CONTRACT_NOT_ADMITTED — hosted expects @netlify/open-api 2.57.0, lock resolves 2.57.1)
WITHOUT_IT: node --test test/hosted-artifact.test.mjs; hosted/artifact-gate.mjs moved → retained 0 / removed 1 / base 1 (test absent at base)
SELF_CHECK: REFUSE AC-3 (.mjs, DEV-134)
AC-1 PASS (26) · AC-2 FAIL (2/4) · AC-3 PASS (0-diff)
BLOCKER (worker): AC-2 vs AC-3 unsatisfiable as scoped.

## FO rulings (2026-09-07)
- AC-3 amended: byte-identical except lines forced by main's merged state, each named. The 8→9 migration count follows the 0008 ruling.
- open-api 2.57.1 is lockfile drift: DEV-136 round 1 regenerated the lock (7a969ed1/0a513602 already 2.57.1; the branch's lock has 2.57.0). Fix = restore the branch's lock + fflate 0.8.3 only, not the hosted constant. Staging was verified on 2.57.0.
- Carry the branch's scripts block (its test:unit excludes the Docker tests; main's would pick up netlify-local.integration). without-it unanswered: the four diagnose:* scripts.
- hosted/acceptance-full-run.mts named in the brief's Surface does not exist on the branch tip; brief error, not worker's.

## Evidence (repair round 1, candidate 269b90e0)
DISPATCH_TOKEN: dev137-2026-09-07-r2
CANDIDATE_SHA: 269b90e0aadc950acb0efaabbf08e49a07be82be
FILES: hosted/ 5 files, 6 lines, all 8→9 native-migration-count literals (build-artifacts.mjs, runtime-receipt-diagnostic.mjs ×2, build-receipt.ts, acceptance-execution.ts, acceptance-netlify-session.ts); 8 test files' mocks 8→9 in lockstep; package-lock.json restored to the branch's + fflate 0.8.3 only (@netlify/open-api 2.57.0); package.json scripts = branch block + main-only entries + tenancy-isolation kept in excludes; qnow-next/.gitignore `dist-hosted/` (branch has it)
TESTS (worker): type-check 0; test:hosted-gates 0 (18/18); test:netlify-package 0 (69/69, hosted-artifact sub-test ✔); acceptance:hosted:self-check 0 ({"status":"admitted","providerCalls":0,"netlifyOpenApiVersion":"2.57.0",...,"valuesExposed":false}); test:unit 0 (168); test:native-migrations 0 (6); test:hosted-runtime 0 (5)
TESTS (FO-verified at 269b90e0, fresh npm ci): without-it retained 0 / removed 1 (artifact-gate.mjs moved); test:netlify-package 0 (69 ok); lock diff vs branch = fflate block only; open-api 2.57.0; hosted/ diff vs branch = 5 files/6 lines
AC-1 PASS (26) · AC-2 PASS · AC-3 amended PASS
Residual → repair round 2: scripts/qnow-next-hosted-preflight.mjs:137 still `!== 8` (gates the DEV-37 deploy; its test mock is self-contained). Brief error: hosted/acceptance-full-run.mts does not exist on the branch tip.
