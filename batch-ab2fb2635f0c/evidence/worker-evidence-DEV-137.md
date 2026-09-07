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
