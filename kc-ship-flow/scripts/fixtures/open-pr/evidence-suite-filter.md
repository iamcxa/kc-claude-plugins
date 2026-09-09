## Evidence
DISPATCH_TOKEN: fixture-token
CANDIDATE_SHA: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
BASE_SHA: bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
BRANCH: feature/fixture-branch
TESTS: evidence.md exit 0; contract-test.py exit 0
WITHOUT_IT_COMMAND: true
WITHOUT_IT_REMOVED_VARIANT: rm -f kc-ship-flow/scripts/open-pr.sh
SELF_CHECK: fixture accept-evidence: ACCEPT
