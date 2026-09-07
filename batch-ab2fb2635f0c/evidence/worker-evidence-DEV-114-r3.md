## Evidence
DISPATCH_TOKEN: dev114-2026-09-07-r3
CANDIDATE_SHA: 930214ab5e4edf4fb36d5e46953a56118032d26b
BRANCH: feature/dev-114-ship-flow-merge-station-ready-all-wait-clean-merge-in-order
BASE_SHA: 1d4e95e0f38e53b525a0c7c272d0d55f0b37ddd2
FILES: docs/ship/README.md,kc-ship-flow/references/stations/merge-station.md,kc-ship-flow/scripts/contract-test.py,kc-ship-flow/scripts/fixtures/fake-gh-merge/gh,kc-ship-flow/scripts/merge-station.sh,kc-ship-flow/scripts/merge-station.test.sh
TESTS: bash kc-ship-flow/scripts/merge-station.test.sh -> exit 0; python3 kc-ship-flow/scripts/contract-test.py -> exit 0; python3 scripts/kc-dev-flow-contract-test.py -> exit 0
SURFACE: kc-ship-flow/scripts/merge-station.sh -> AC-1,AC-2 | bash kc-ship-flow/scripts/merge-station.test.sh | sed -i.bak '155s/\\$//;156d' kc-ship-flow/scripts/merge-station.sh
WITHOUT_IT_COMMAND: grep -q 'GH=${GH:-gh}' kc-ship-flow/scripts/merge-station.sh && bash kc-ship-flow/scripts/merge-station.test.sh 2>&1 | grep -q "case d: PASS"
WITHOUT_IT_REMOVED_VARIANT: sed -i.bak '155s/\\$//;156d' kc-ship-flow/scripts/merge-station.sh
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 1; at BASE_SHA -> exit 2
SELF_CHECK: accept-evidence: ACCEPT
ROBOREV: UNAVAILABLE(reason: no reviewer binary in workspace)
AC-1: cases a–g PASS (8 lines), 0 FAIL
AC-2: refused first merge → exit 4 MERGE_FAILED naming #401; no `pr merge 402` in the fake log
AC-3: both contract tests exit 0
BLOCKER: none
