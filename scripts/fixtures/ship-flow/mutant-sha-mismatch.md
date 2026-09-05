## Evidence
DISPATCH_TOKEN: test-mutant-sha-mismatch
CANDIDATE_SHA: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
BRANCH: feature/test-mutant-sha-mismatch
BASE_SHA: 1283046b605285f259da0a2a728cfa37bf1cf3dd
FILES: docs/dev/README.md
TESTS: python3 scripts/kc-dev-flow-contract-test.py -> exit 0
SURFACE: docs/dev/README.md -> AC-1 | grep -q "test" docs/dev/README.md | git show 1283046b605285f259da0a2a728cfa37bf1cf3dd:docs/dev/README.md > docs/dev/README.md
WITHOUT_IT_COMMAND: grep -q "test" docs/dev/README.md
WITHOUT_IT_REMOVED_VARIANT: git show 1283046b605285f259da0a2a728cfa37bf1cf3dd:docs/dev/README.md > docs/dev/README.md
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 1
AC-1: This is a synthetic mutant to test SHA mismatch detection.
BLOCKER: none
