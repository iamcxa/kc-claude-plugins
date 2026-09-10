## Evidence
DISPATCH_TOKEN: test-mutant-untracked-path
CANDIDATE_SHA: HEAD
BASE_SHA: HEAD
WITHOUT_IT_COMMAND: test -f kc-ship-flow/scripts/fixtures/accept-evidence-does-not-exist.xyz
WITHOUT_IT_REMOVED_VARIANT: git show HEAD:kc-ship-flow/scripts/accept-evidence.sh > kc-ship-flow/scripts/accept-evidence.sh
WITHOUT_IT_OBSERVED: retained -> exit 1; removed -> exit 1
AC-1: This is a synthetic mutant to test that an untracked-only path is still refused
BLOCKER: none
