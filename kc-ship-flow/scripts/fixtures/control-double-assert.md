## Evidence
DISPATCH_TOKEN: test-control-double-assert
CANDIDATE_SHA: d0712eeb9c1054a5e1710dbdcb62f04f80e8b2a6
BRANCH: feature/test-control-double-assert
BASE_SHA: 1b61997b0ca78a6fbab281447f44a47238a8b524
FILES: docs/ship-flow/README.md
TESTS: python3 scripts/kc-dev-flow-contract-test.py -> exit 0
SURFACE: docs/ship-flow/README.md -> AC-1 | grep -q "test content" docs/ship-flow/README.md | git show 1b61997b0ca78a6fbab281447f44a47238a8b524:docs/ship-flow/README.md > docs/ship-flow/README.md
WITHOUT_IT_COMMAND: test -f docs/ship-flow/README.md && grep -q "test content" docs/ship-flow/README.md
WITHOUT_IT_REMOVED_VARIANT: git show 1b61997b0ca78a6fbab281447f44a47238a8b524:docs/ship-flow/README.md > docs/ship-flow/README.md
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 1
AC-1: Two real assertions joined by && without trailing || should be accepted
BLOCKER: none
