## Evidence
DISPATCH_TOKEN: test-mutant-extra-path
CANDIDATE_SHA: d0712eeb9c1054a5e1710dbdcb62f04f80e8b2a6
BRANCH: feature/test-mutant-extra-path
BASE_SHA: 1283046b605285f259da0a2a728cfa37bf1cf3dd
FILES: docs/dev/README.md,docs/ship-flow/README.md,kc-dev-flow/README.md
TESTS: python3 scripts/kc-dev-flow-contract-test.py -> exit 0
SURFACE: docs/dev/README.md -> AC-1 | grep -q "test content" docs/dev/README.md | git show 1283046b605285f259da0a2a728cfa37bf1cf3dd:docs/dev/README.md > docs/dev/README.md
SURFACE: docs/ship-flow/README.md -> AC-1 | grep -q "test content" docs/ship-flow/README.md | git show 1283046b605285f259da0a2a728cfa37bf1cf3dd:docs/ship-flow/README.md > docs/ship-flow/README.md
SURFACE: kc-dev-flow/README.md -> AC-1 | grep -q "test content" kc-dev-flow/README.md | git show 1283046b605285f259da0a2a728cfa37bf1cf3dd:kc-dev-flow/README.md > kc-dev-flow/README.md
WITHOUT_IT_COMMAND: grep -q "test content" docs/dev/README.md && grep -q "test content" docs/ship-flow/README.md
WITHOUT_IT_REMOVED_VARIANT: git show 1283046b605285f259da0a2a728cfa37bf1cf3dd:docs/dev/README.md > docs/dev/README.md && git show 1283046b605285f259da0a2a728cfa37bf1cf3dd:docs/ship-flow/README.md > docs/ship-flow/README.md && git show 1283046b605285f259da0a2a728cfa37bf1cf3dd:kc-dev-flow/README.md > kc-dev-flow/README.md
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 1
AC-1: This is a synthetic mutant to test that extra paths in the variant are accepted.
BLOCKER: none
