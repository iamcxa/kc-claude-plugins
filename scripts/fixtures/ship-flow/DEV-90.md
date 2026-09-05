## Evidence
DISPATCH_TOKEN: ffce2d8ff9ce7af1
CANDIDATE_SHA: 00d2dbf5d2a2778da500a6580849dc89c2e782ba
BRANCH: feature/dev-90-write-the-three-ship-flow-contract-sentences-into-the
BASE_SHA: d98f40b5e2080cb884facf1734fc66052eff9982
FILES: docs/dev/README.md,docs/ship-flow/README.md,scripts/kc-dev-flow-contract-test.py
TESTS: python3 scripts/kc-dev-flow-contract-test.py -> exit 0
SURFACE: docs/dev/README.md -> AC-1 | grep -q "Ship-flow's runtime record lives in" docs/dev/README.md | git show d98f40b5e2080cb884facf1734fc66052eff9982:docs/dev/README.md > docs/dev/README.md
SURFACE: docs/ship-flow/README.md -> AC-1 | grep -q "(DEV-67)" docs/ship-flow/README.md | git show d98f40b5e2080cb884facf1734fc66052eff9982:docs/ship-flow/README.md > docs/ship-flow/README.md
SURFACE: scripts/kc-dev-flow-contract-test.py -> AC-1 | grep -q "normalized_ship_readme" scripts/kc-dev-flow-contract-test.py | git show d98f40b5e2080cb884facf1734fc66052eff9982:scripts/kc-dev-flow-contract-test.py > scripts/kc-dev-flow-contract-test.py
WITHOUT_IT_COMMAND: grep -q "(DEV-67)" docs/ship-flow/README.md && test "$(grep '(DEV-67)' docs/ship-flow/README.md | wc -l)" -eq 3 && grep -q "Ship-flow's runtime record lives in docs/ship-flow/README.md" docs/dev/README.md
WITHOUT_IT_REMOVED_VARIANT: git show d98f40b5e2080cb884facf1734fc66052eff9982:docs/ship-flow/README.md > docs/ship-flow/README.md && git show d98f40b5e2080cb884facf1734fc66052eff9982:docs/dev/README.md > docs/dev/README.md
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 1
ROBOREV: UNAVAILABLE(reason: no reviewer binary in workspace)
AC-1: "Dispatch a higher layer only after the lower layer is fully verified. (DEV-67)" present in docs/ship-flow/README.md; "A worker's without-it command runs in an isolated environment (temporary HOME, no agent, no network). (DEV-67)" present; "Security, data-loss, and compatibility findings outside the Brief block the candidate while general improvements are scoped out. (DEV-67)" present
AC-2: git diff d98f40b5e2080cb884facf1734fc66052eff9982...HEAD --stat shows docs/dev/README.md | 67 +-, docs/ship-flow/README.md | 73 +++, scripts/kc-dev-flow-contract-test.py | 27 ++; python3 scripts/kc-dev-flow-contract-test.py passes with repointed pins
BLOCKER: none
