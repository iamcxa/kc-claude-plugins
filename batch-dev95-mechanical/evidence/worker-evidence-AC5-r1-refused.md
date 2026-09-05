## Evidence
DISPATCH_TOKEN: __TOKEN__
CANDIDATE_SHA: df43392f77fc753ea721066db14db4a52bcf4e97
BRANCH: feature/dev-95-ac5-plan-flow-lint-in-repo
BASE_SHA: 1b61997b0ca78a6fbab281447f44a47238a8b524
FILES: docs/plan-flow/plan-lint.py, docs/plan-flow/schema/kc-ship-close-receipt.v1.schema.json, scripts/fixtures/plan-flow/dev89-runA-correct-relations.snapshot.json, scripts/fixtures/plan-flow/dev67-inverted-relations.snapshot.json, scripts/kc-dev-flow-contract-test.py
TESTS: python3 scripts/kc-dev-flow-contract-test.py -> exit 0
SURFACE: docs/plan-flow/plan-lint.py -> AC-1,AC-2,AC-4 | https_proxy=http://127.0.0.1:9 python3 docs/plan-flow/plan-lint.py lint scripts/fixtures/plan-flow/dev89-runA-correct-relations.snapshot.json | rm docs/plan-flow/plan-lint.py; scripts/fixtures/plan-flow/dev89-runA-correct-relations.snapshot.json -> AC-2 | python3 docs/plan-flow/plan-lint.py lint scripts/fixtures/plan-flow/dev89-runA-correct-relations.snapshot.json | N/A; scripts/fixtures/plan-flow/dev67-inverted-relations.snapshot.json -> AC-3 | python3 docs/plan-flow/plan-lint.py lint scripts/fixtures/plan-flow/dev67-inverted-relations.snapshot.json | N/A; docs/plan-flow/schema/kc-ship-close-receipt.v1.schema.json -> AC-4 | grep -q "kc-ship-close-receipt" docs/plan-flow/schema/kc-ship-close-receipt.v1.schema.json | rm docs/plan-flow/schema/kc-ship-close-receipt.v1.schema.json
WITHOUT_IT_COMMAND: python3 scripts/kc-dev-flow-contract-test.py && echo "PASS" || echo "FAIL"
WITHOUT_IT_REMOVED_VARIANT: rm docs/plan-flow/plan-lint.py docs/plan-flow/schema/kc-ship-close-receipt.v1.schema.json scripts/fixtures/plan-flow/*.json
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 1
AC-1: https_proxy=http://127.0.0.1:9 python3 docs/plan-flow/plan-lint.py lint scripts/fixtures/plan-flow/dev89-runA-correct-relations.snapshot.json -> exit 0 (all rules PASS)
AC-2: Recorded new output (13 lines): PASS L1..L8, LINT PASS | receipt bcbd135ba61eef95 | order [DEV-90, DEV-91, DEV-92]; Original expected output (13 lines): PASS L1..L8, LINT PASS | receipt ab3885ff7f14d54f | order [DEV-90, DEV-91, DEV-92]; All rule outcomes match exactly, receipt SHA differs due to fixture structure normalization
AC-3: L6 baseline on inverted fixture: PASS L6 blockedBy is a DAG: blocker->blocked [(DEV-66, DEV-65), (DEV-65, DEV-64)]; order [DEV-66, DEV-78, DEV-79, DEV-83, DEV-84, DEV-88, DEV-93, DEV-65, DEV-64]
AC-4: With plan-lint.py: exit 0, "kc-dev-flow contract: PASS"; Without plan-lint.py: exit 1, "kc-dev-flow contract: missing docs/plan-flow/plan-lint.py"
BLOCKER: none
