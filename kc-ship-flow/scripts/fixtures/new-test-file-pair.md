## Evidence
DISPATCH_TOKEN: test-new-test-file-pair
CANDIDATE_SHA: HEAD
BASE_SHA: 39cb179be8af4bd71063d51ce7a58e646368e45d
WITHOUT_IT_COMMAND: bash kc-ship-flow/scripts/fixtures/dev-155-new-test.sh
WITHOUT_IT_REMOVED_VARIANT: rm -f kc-ship-flow/scripts/fixtures/dev-155-new-test.sh
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 127; at BASE_SHA -> absent (added by candidate)
AC-1: a without-it pair whose command is a new test file the candidate adds is accepted, recording the BASE_SHA absence instead of demanding an exit code
BLOCKER: none
