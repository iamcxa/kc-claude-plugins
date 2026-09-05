## Evidence
DISPATCH_TOKEN: test-s29-prose-after-semicolon
CANDIDATE_SHA: d0712eeb9c1054a5e1710dbdcb62f04f80e8b2a6
BRANCH: feature/test-s29-prose-after-semicolon
BASE_SHA: 1b61997b0ca78a6fbab281447f44a47238a8b524
FILES: docs/ship-flow/README.md
TESTS: python3 scripts/kc-dev-flow-contract-test.py -> exit 0
SURFACE: docs/ship-flow/README.md -> AC-1 | grep -q "test content" docs/ship-flow/README.md | git show 1b61997b0ca78a6fbab281447f44a47238a8b524:docs/ship-flow/README.md > docs/ship-flow/README.md
WITHOUT_IT_COMMAND: test -f ~/.claude/plugins/test && echo clean || echo derivative; on candidate exits 0, on removed variant exits 1
WITHOUT_IT_REMOVED_VARIANT: git show 1b61997b0ca78a6fbab281447f44a47238a8b524:docs/ship-flow/README.md > docs/ship-flow/README.md
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 1
AC-1: This is the S29 block with prose after semicolon and out-of-tree path
BLOCKER: none
