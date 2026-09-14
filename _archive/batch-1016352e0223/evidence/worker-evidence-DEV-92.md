## Evidence
DISPATCH_TOKEN: 7374515cd5918361
CANDIDATE_SHA: 9c05eaf86e74b608d5bef929e5772c931d6791b4
BRANCH: feature/dev-92-observe-three-ship-flow-uats-for-re-derivation-of-the-three
BASE_SHA: 00d2dbf5d2a2778da500a6580849dc89c2e782ba
FILES: docs/ship-flow/evidence/uat-observations/README.md
TESTS: python3 scripts/kc-dev-flow-contract-test.py -> exit 0
SURFACE: docs/ship-flow/evidence/uat-observations/README.md -> AC-1 | test -f docs/ship-flow/evidence/uat-observations/README.md | git rm -f docs/ship-flow/evidence/uat-observations/README.md
WITHOUT_IT_COMMAND: test -f docs/ship-flow/evidence/uat-observations/README.md
WITHOUT_IT_REMOVED_VARIANT: git rm -f docs/ship-flow/evidence/uat-observations/README.md
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 1
ROBOREV: UNAVAILABLE(reason: no reviewer binary in workspace)
AC-1: Template created at docs/ship-flow/evidence/uat-observations/README.md with format specification for one file per PR with fields pr, date, rederived, which. FO will create three observation records (one per UAT PR) post-UAT. Template provides structure for evidence collection.
AC-2: Template includes verdict rule (three files, all rederived: no = valid; any rederived: yes = invalidated). FO will apply this rule and record explicit verdict line after collecting all three observations.
BLOCKER: none
