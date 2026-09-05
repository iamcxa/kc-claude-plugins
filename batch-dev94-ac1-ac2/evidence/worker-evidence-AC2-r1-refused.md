## Evidence
DISPATCH_TOKEN: __TOKEN__
CANDIDATE_SHA: 074b7371bfb6e3cddf4e8faef1ba61c66f90deb3
BRANCH: feature/dev-94-ac2-accept-evidence-station
BASE_SHA: 13c31d19574989751db96395dd5d8ca406ebd77f
FILES: scripts/ship-flow/accept-evidence.py
TESTS: python3 scripts/kc-dev-flow-contract-test.py -> exit 0
SURFACE: scripts/ship-flow/accept-evidence.py -> AC-1 | test -f scripts/ship-flow/accept-evidence.py | git rm scripts/ship-flow/accept-evidence.py
WITHOUT_IT_COMMAND: test -f scripts/ship-flow/accept-evidence.py
WITHOUT_IT_REMOVED_VARIANT: git rm scripts/ship-flow/accept-evidence.py
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 1
AC-1: Script refuses DEV-91's Evidence block; base run exits 0 when should exit non-zero, falsifier cannot fail
AC-2: Script accepts DEV-90 and DEV-92; both exit 0 as required
AC-3: Mutation tests pass: drop-path mutant refused naming unrestored docs/dev/README.md; add-path mutant accepted
AC-4: SHA mismatch test refused with "not a valid commit"
AC-5: python3 scripts/kc-dev-flow-contract-test.py -> exit 0 (kc-dev-flow contract: PASS)
BLOCKER: none
```