## Evidence
DISPATCH_TOKEN: 4ca7217057de0726
CANDIDATE_SHA: 00c4c05be6ea19a810e40606e6d0f3baad3f9af1
BRANCH: feature/dev-91-pin-the-three-contract-sentences-to-the-contract-test
BASE_SHA: 00d2dbf5d2a2778da500a6580849dc89c2e782ba
FILES: scripts/kc-dev-flow-contract-test.py
TESTS: python3 scripts/kc-dev-flow-contract-test.py -> exit 0
SURFACE: scripts/kc-dev-flow-contract-test.py -> AC-1 | grep -q "Dispatch a higher layer only after the lower layer is fully verified." scripts/kc-dev-flow-contract-test.py && grep -q "A worker.*s without-it command runs in an isolated environment" scripts/kc-dev-flow-contract-test.py && grep -q "Security, data-loss, and compatibility findings outside the Brief" scripts/kc-dev-flow-contract-test.py | git show 00d2dbf5d2a2778da500a6580849dc89c2e782ba:scripts/kc-dev-flow-contract-test.py > scripts/kc-dev-flow-contract-test.py
WITHOUT_IT_COMMAND: grep -q "Dispatch a higher layer only after the lower layer is fully verified." scripts/kc-dev-flow-contract-test.py && grep -q "A worker.*s without-it command runs in an isolated environment" scripts/kc-dev-flow-contract-test.py && grep -q "Security, data-loss, and compatibility findings outside the Brief" scripts/kc-dev-flow-contract-test.py
WITHOUT_IT_REMOVED_VARIANT: git show 00d2dbf5d2a2778da500a6580849dc89c2e782ba:scripts/kc-dev-flow-contract-test.py > scripts/kc-dev-flow-contract-test.py
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 2
AC-1: Three mutation runs executed: (1) removed "Dispatch a higher layer only after the lower layer is fully verified." -> exit 1 naming guarantee; (2) removed "A worker's without-it command runs in an isolated environment" -> exit 1 naming guarantee; (3) removed "Security, data-loss, and compatibility findings outside the Brief" -> exit 1 naming guarantee. All restored and verified passing.
AC-2: Contract test passes at candidate 00c4c05be6ea19a810e40606e6d0f3baad3f9af1 with all three sentences present in docs/ship-flow/README.md.
BLOCKER: none
