## Evidence
DISPATCH_TOKEN: test-mutant-negation
CANDIDATE_SHA: d0712eeb9c1054a5e1710dbdcb62f04f80e8b2a6
BRANCH: feature/test-mutant-negation
BASE_SHA: 1283046b605285f259da0a2a728cfa37bf1cf3dd
FILES: docs/dev/README.md
TESTS: python3 scripts/kc-dev-flow-contract-test.py -> exit 0
SURFACE: docs/dev/README.md -> AC-1 | grep -q "test content" docs/dev/README.md | git show 1283046b605285f259da0a2a728cfa37bf1cf3dd:docs/dev/README.md > docs/dev/README.md
WITHOUT_IT_COMMAND: grep -q "test content" docs/dev/README.md
WITHOUT_IT_REMOVED_VARIANT: ! grep -q "test content" docs/dev/README.md
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 1
AC-1: Variant that negates the command (! <cmd>) should be refused as it alters no changed read paths.
BLOCKER: none
