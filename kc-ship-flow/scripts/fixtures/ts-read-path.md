## Evidence
DISPATCH_TOKEN: test-ts-read-path
CANDIDATE_SHA: HEAD
BASE_SHA: HEAD
WITHOUT_IT_COMMAND: grep -q "accept-evidence-fixture-marker-absent" kc-ship-flow/scripts/fixtures/accept-evidence-ts-read-target.ts && grep -q "accept-evidence-fixture-marker-absent" kc-ship-flow/scripts/fixtures/accept-evidence-ts-read-target.mts
WITHOUT_IT_REMOVED_VARIANT: git show HEAD:kc-ship-flow/scripts/accept-evidence.sh > kc-ship-flow/scripts/accept-evidence.sh
WITHOUT_IT_OBSERVED: retained -> exit 1; removed -> exit 1
AC-1: Path extraction should accept tracked .ts and .mts paths regardless of extension
BLOCKER: none
