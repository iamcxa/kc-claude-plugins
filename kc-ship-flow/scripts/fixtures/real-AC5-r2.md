## Evidence
DISPATCH_TOKEN: __TOKEN__
CANDIDATE_SHA: df43392f77fc753ea721066db14db4a52bcf4e97
BRANCH: feature/dev-95-ac5-plan-flow-lint-in-repo-r2
BASE_SHA: 1b61997b0ca78a6fbab281447f44a47238a8b524
FILES: docs/plan-flow/plan-lint.py, docs/plan-flow/schema/kc-ship-close-receipt.v1.schema.json, scripts/fixtures/plan-flow/dev67-inverted-relations.snapshot.json, scripts/fixtures/plan-flow/dev89-runA-correct-relations.snapshot.json, scripts/kc-dev-flow-contract-test.py
TESTS: python3 scripts/kc-dev-flow-contract-test.py -> exit 0
SURFACE: docs/plan-flow/plan-lint.py -> AC-1 | python3 docs/plan-flow/plan-lint.py lint scripts/fixtures/plan-flow/dev89-runA-correct-relations.snapshot.json | rm -f docs/plan-flow/plan-lint.py; docs/plan-flow/schema/kc-ship-close-receipt.v1.schema.json -> AC-4 | test -f docs/plan-flow/schema/kc-ship-close-receipt.v1.schema.json | rm -f docs/plan-flow/schema/kc-ship-close-receipt.v1.schema.json; scripts/fixtures/plan-flow/dev*.snapshot.json -> AC-5 | ls scripts/fixtures/plan-flow/dev*.snapshot.json | rm -f scripts/fixtures/plan-flow/dev*.snapshot.json; scripts/kc-dev-flow-contract-test.py -> AC-2 | python3 scripts/kc-dev-flow-contract-test.py | git checkout scripts/kc-dev-flow-contract-test.py
WITHOUT_IT_COMMAND: python3 docs/plan-flow/plan-lint.py lint scripts/fixtures/plan-flow/dev89-runA-correct-relations.snapshot.json
WITHOUT_IT_REMOVED_VARIANT: rm -f docs/plan-flow/plan-lint.py
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 2; at BASE_SHA -> exit 2
AC-1: Eight rule() calls (L1-L8) are present in plan-lint.py - PASS
AC-2: Contract test fails closed when plan-lint.py is deleted (contract requires all plan-flow files) - PASS
AC-3: Lint mode runs offline without requiring LINEAR_API_KEY environment variable - PASS
AC-4: Schema file kc-ship-close-receipt.v1.schema.json is present and included in contract test - PASS
AC-5: Fixture files (dev67-inverted-relations.snapshot.json, dev89-runA-correct-relations.snapshot.json) are present and included in contract test - PASS
BLOCKER: none
