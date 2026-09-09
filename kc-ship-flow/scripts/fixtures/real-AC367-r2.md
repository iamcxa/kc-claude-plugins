## Evidence
DISPATCH_TOKEN: __TOKEN__
CANDIDATE_SHA: 7e495afd50b43ea6d0b31028d8b56d9158d7b858
BRANCH: feature/dev-95-ac367-three-lint-rules-r2
BASE_SHA: df43392f77fc753ea721066db14db4a52bcf4e97
FILES: docs/plan-flow/plan-lint.py,scripts/fixtures/plan-flow/dev89-runA-reverified.snapshot.json,scripts/kc-dev-flow-contract-test.py
TESTS: python3 scripts/kc-dev-flow-contract-test.py -> exit 0
SURFACE: docs/plan-flow/plan-lint.py -> AC-1 | python3 docs/plan-flow/plan-lint.py lint scripts/fixtures/plan-flow/dev67-inverted-relations.snapshot.json 2>&1 | grep -q 'FAIL L6 blockedBy direction' | git show df43392f77fc753ea721066db14db4a52bcf4e97:docs/plan-flow/plan-lint.py > docs/plan-flow/plan-lint.py
SURFACE: docs/plan-flow/plan-lint.py -> AC-2 | python3 docs/plan-flow/plan-lint.py lint scripts/fixtures/plan-flow/dev89-runA-correct-relations.snapshot.json 2>&1 | grep -q 'DEV-91.*already claimed by DEV-90' | git show df43392f77fc753ea721066db14db4a52bcf4e97:docs/plan-flow/plan-lint.py > docs/plan-flow/plan-lint.py
SURFACE: docs/plan-flow/plan-lint.py -> AC-3 | python3 docs/plan-flow/plan-lint.py lint scripts/fixtures/plan-flow/dev89-runA-reverified.snapshot.json 2>&1 | grep -q 'PASS L10 re-verified presence and age' | git show df43392f77fc753ea721066db14db4a52bcf4e97:docs/plan-flow/plan-lint.py > docs/plan-flow/plan-lint.py
WITHOUT_IT_COMMAND: python3 docs/plan-flow/plan-lint.py lint scripts/fixtures/plan-flow/dev67-inverted-relations.snapshot.json 2>&1 | grep -q 'FAIL L6 blockedBy direction'
WITHOUT_IT_REMOVED_VARIANT: git show df43392f77fc753ea721066db14db4a52bcf4e97:docs/plan-flow/plan-lint.py > docs/plan-flow/plan-lint.py
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 1; at BASE_SHA -> exit 1
AC-1: inverted FAIL: intent order ['DEV-64', 'DEV-65', 'DEV-66', 'DEV-78', 'DEV-79', 'DEV-83', 'DEV-84', 'DEV-88', 'DEV-93']; violations (DEV-66, DEV-65), (DEV-65, DEV-64) | correct PASS: intent order ['DEV-90', 'DEV-91', 'DEV-92']; violations none
AC-2: FAIL L9 by-product Issue check: issues with no unique surface: DEV-91: only surface scripts/kc-dev-flow-contract-test.py already claimed by DEV-90
AC-3: inverted FAIL L10 re-verified presence and age: 14-day bound; violations: DEV-93: no Re-verified line, DEV-88: no Re-verified line, DEV-84: no Re-verified line, DEV-83: no Re-verified line, DEV-79: no Re-verified line, DEV-78: no Re-verified line, DEV-66: no Re-verified line, DEV-65: no Re-verified line, DEV-64: no Re-verified line | correct FAIL L10 re-verified presence and age: 14-day bound; violations: DEV-92: no Re-verified line, DEV-91: no Re-verified line, DEV-90: no Re-verified line | reverified PASS L10 re-verified presence and age: 14-day bound; violations: none
AC-4: differences
AC-5: l6_ok = not l6_violations; exit 0 at candidate, exit 1 when removed
AC-6: exit 0; pin runs dev89-runA-reverified.snapshot.json
BLOCKER: none