## Evidence
DISPATCH_TOKEN: test-unparseable
CANDIDATE_SHA: d0712eeb9c1054a5e1710dbdcb62f04f80e8b2a6
BRANCH: feature/test-unparseable
BASE_SHA: 1b61997b0ca78a6fbab281447f44a47238a8b524
FILES: docs/ship-flow/README.md
TESTS: python3 scripts/kc-dev-flow-contract-test.py -> exit 0
SURFACE: docs/ship-flow/README.md -> AC-1 | grep -q "test content" docs/ship-flow/README.md | git show 1b61997b0ca78a6fbab281447f44a47238a8b524:docs/ship-flow/README.md > docs/ship-flow/README.md
WITHOUT_IT_COMMAND: some random prose that cannot be parsed as a command
WITHOUT_IT_REMOVED_VARIANT: git show 1b61997b0ca78a6fbab281447f44a47238a8b524:docs/ship-flow/README.md > docs/ship-flow/README.md
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 1
AC-1: Unparseable command should be refused
BLOCKER: none
