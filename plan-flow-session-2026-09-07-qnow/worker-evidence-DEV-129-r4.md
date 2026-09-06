## Evidence
DISPATCH_TOKEN: dev129-2026-09-07-r4
CANDIDATE_SHA: 2c7363d75e67c3cda2053dbc7d5a827c105f951a
BRANCH: feature/dev-129-plan-lint-admitted-only-l4-l8-l10-l6-advisory
BASE_SHA: ac60ebe462a9177dbfcaa61f29db98444f4a384d
FILES: docs/plan-flow/plan-lint.py, scripts/kc-dev-flow-contract-test.py, scripts/fixtures/plan-flow/admitted-only-rough-backlog.snapshot.json
TESTS: python3 scripts/kc-dev-flow-contract-test.py -> exit 0
SURFACE: docs/plan-flow/plan-lint.py -> AC-1,AC-2 | python3 docs/plan-flow/plan-lint.py lint scripts/fixtures/plan-flow/admitted-only-rough-backlog.snapshot.json | sed -i.bak '/id-order/d' docs/plan-flow/plan-lint.py
WITHOUT_IT_COMMAND: python3 docs/plan-flow/plan-lint.py lint scripts/fixtures/plan-flow/admitted-only-rough-backlog.snapshot.json | grep -q 'WARN L6 id-order advisory'
WITHOUT_IT_REMOVED_VARIANT: sed -i.bak '/id-order/d' docs/plan-flow/plan-lint.py
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 1; at BASE_SHA -> exit 1
SELF_CHECK: accept-evidence: ACCEPT
ROBOREV: UNAVAILABLE(reason: no reviewer binary in workspace)
AC-1: fixture lints PASS L4/L8/L10 for the admitted issue, WARN L6 id-order advisory printed
AC-2: Non-goals removed → exit 1, FAIL L4 names DEV-913
AC-3: contract test exit 0 (~43 s); dev89 L8 assertion changed to "not judged" since all its issues are Done
BLOCKER: none
