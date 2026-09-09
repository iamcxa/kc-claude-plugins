## Evidence
DISPATCH_TOKEN: fixture-token
CANDIDATE_SHA: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
BASE_SHA: bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
BRANCH: feature/fixture-branch
FILES: kc-ship-flow/scripts/open-pr.sh, kc-ship-flow/scripts/contract-test.py, kc-ship-flow/scripts/fixtures/open-pr/{evidence.md,evidence-no-tests.md,batch/README.md,batch/receipt/plan-receipt.json}
TESTS: kc-ship-flow/scripts/contract-test.py -> exit 0; kc-ship-flow/scripts/open-pr.sh --dry-run -> exit 0
WITHOUT_IT_COMMAND: true
WITHOUT_IT_REMOVED_VARIANT: rm -f kc-ship-flow/scripts/open-pr.sh
SELF_CHECK: fixture accept-evidence: ACCEPT
