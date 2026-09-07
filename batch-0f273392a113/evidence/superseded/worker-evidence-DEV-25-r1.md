## Evidence
DISPATCH_TOKEN: dev25-repair-2026-09-07-r1
CANDIDATE_SHA: 2c79489203b3cb2476cd9817ac231a41dbb35f27
BRANCH: conductor/dev-25-netlify-tenancy-and-otp-validation
BASE_SHA: eeb7d4f83e5e31312051bb2d99ee40794fc3f6e3
FILES: experiments/netlify-refine-poc/qnow-next/identity/phone-identity-port.ts, experiments/netlify-refine-poc/qnow-next/identity/reference-phone-identity.ts, experiments/netlify-refine-poc/qnow-next/test/phone-identity-conformance.test.ts, experiments/netlify-refine-poc/qnow-next/test/phone-identity-conformance.ts, experiments/netlify-refine-poc/qnow-next/test/tenancy-isolation.integration.test.ts
TESTS: npm run type-check -> exit 0; npx vitest run --config vitest.config.ts test/phone-identity-conformance.test.ts -> exit 0 (22 passed); npx vitest run --config vitest.config.ts test/tenancy-isolation.integration.test.ts -> exit 0 (13 passed); npm test -> exit 0
SURFACE: identity/reference-phone-identity.ts -> finding 1 | npx vitest run --config vitest.config.ts test/phone-identity-conformance.test.ts | sed -i.bak '159d' identity/reference-phone-identity.ts
WITHOUT_IT_COMMAND: npx vitest run --config vitest.config.ts test/phone-identity-conformance.test.ts 2>&1 | grep -q "22 passed"
WITHOUT_IT_REMOVED_VARIANT: sed -i.bak '159d' experiments/netlify-refine-poc/qnow-next/identity/reference-phone-identity.ts
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 1; at BASE_SHA -> exit 1
SELF_CHECK: 2026-09-07T02:25:58Z accept-evidence: REFUSE: AC-3: cannot extract paths from WITHOUT_IT_COMMAND - command may be unparseable
ROBOREV: UNAVAILABLE(reason: no reviewer binary in workspace)
F1: verify attempts bounded (maxVerifyAttempts 5), burst conformance case; F2: refusal collapse stated, message pinned across 7 refusals; F3: import-boundary test added; F4: sentCount unchanged across refresh; F5: ROLLBACK residue case added (neither-variant not expressible with pg-pool; stated in commit body)
BLOCKER: accept-evidence.sh AC-3 path extractor recognizes only .py/.md/.sh/.json/.yaml/.yml/.txt; this diff is .ts
