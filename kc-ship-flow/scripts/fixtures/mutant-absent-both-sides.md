## Evidence
DISPATCH_TOKEN: test-mutant-absent-both-sides
CANDIDATE_SHA: HEAD
BASE_SHA: HEAD
WITHOUT_IT_COMMAND: bash kc-ship-flow/scripts/fixtures/dev-155-absent-both-sides.sh kc-ship-flow/scripts/without-it.sh
WITHOUT_IT_REMOVED_VARIANT: rm -f kc-ship-flow/scripts/fixtures/dev-155-absent-both-sides.sh
WITHOUT_IT_OBSERVED: retained -> exit 127; removed -> exit 127
AC-2: a without-it pair naming a path absent at both BASE_SHA and CANDIDATE_SHA is still refused
BLOCKER: none
