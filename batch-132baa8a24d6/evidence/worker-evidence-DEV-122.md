## Evidence
DISPATCH_TOKEN: dev122-2026-09-06
CANDIDATE_SHA: 91d0227806ba4906746c37e9b530ae8a25ad976e
BRANCH: feature/dev-122-plan-lint-l9-and-l2-must-ignore-done-issues-and-report-un
BASE_SHA: d75b92dade55ac6911d5bff8282497488a05a514
FILES: docs/plan-flow/plan-lint.py, scripts/kc-dev-flow-contract-test.py, scripts/fixtures/plan-flow/dev122-done-pair-unadmitted.snapshot.json, scripts/fixtures/plan-flow/dev122-started-pair.snapshot.json
TESTS: python3 scripts/kc-dev-flow-contract-test.py -> exit 0
SURFACE: docs/plan-flow/plan-lint.py -> AC-1,AC-2 | python3 docs/plan-flow/plan-lint.py lint scripts/fixtures/plan-flow/dev122-done-pair-unadmitted.snapshot.json | sed -i.bak '/unadmitted/d' docs/plan-flow/plan-lint.py
WITHOUT_IT_COMMAND: python3 docs/plan-flow/plan-lint.py lint scripts/fixtures/plan-flow/dev122-done-pair-unadmitted.snapshot.json | grep -q 'unadmitted: 1'
WITHOUT_IT_REMOVED_VARIANT: sed -i.bak '/unadmitted/d' docs/plan-flow/plan-lint.py
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 1; at BASE_SHA -> exit 1
SELF_CHECK: 2026-09-06T08:54:16Z accept-evidence: ACCEPT
ROBOREV: UNAVAILABLE(reason: no reviewer binary in workspace)
AC-1: lint on dev122-done-pair-unadmitted exits 0; output has PASS L9 and "PASS L2 one cycle: {'cycle-1'}; unadmitted: 1"
AC-2: lint on dev122-started-pair exits 1; output names DEV-902's shared surface
AC-3: contract test exits 0; the pre-existing dev89 fixture assertion was changed from FAIL L9 to PASS L9 (all its issues are Done)
BLOCKER: none
