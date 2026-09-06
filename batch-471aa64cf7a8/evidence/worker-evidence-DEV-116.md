## Evidence
DISPATCH_TOKEN: dev116-2026-09-06
CANDIDATE_SHA: 1645da96c44c5cf9b4e8b5aa1d377031b2cee660
BRANCH: feature/dev-116-b2-kc-ship-flow-move-the-fourteen-station-scripts-and-their
BASE_SHA: 2c7f71927f6721401bf8d0a28e67f95dc747aec5
FILES: .gitignore,docs/plan-flow/schema/close-receipt.test.py,docs/plan-flow/schema/validate-receipt.py,docs/ship-flow/README.md,docs/ship-flow/flows/contract-test-journey.yaml,docs/ship-flow/flows/from-dispatch-to-one-slack-message.yaml,kc-ship-flow/schemas/kc-ship-close-receipt.v1.schema.json,kc-ship-flow/scripts/accept-evidence.sh,kc-ship-flow/scripts/contract-test.py,kc-ship-flow/scripts/dev-debrief.py,kc-ship-flow/scripts/dev-debrief.test.py,kc-ship-flow/scripts/disposition.py,kc-ship-flow/scripts/e2e-cli.sh,kc-ship-flow/scripts/e2e-gate.py,kc-ship-flow/scripts/fenced-dispatch.sh,kc-ship-flow/scripts/fixtures/(moved tree),kc-ship-flow/scripts/holder.sh,kc-ship-flow/scripts/intent.sh,kc-ship-flow/scripts/notify.sh,kc-ship-flow/scripts/notify.test.sh,kc-ship-flow/scripts/open-pr.sh,kc-ship-flow/scripts/parse-execute-external.py,kc-ship-flow/scripts/ship-debrief.py,kc-ship-flow/scripts/ship-debrief.test.py,kc-ship-flow/scripts/uat-doc.py,kc-ship-flow/scripts/uat-doc.test.py,kc-ship-flow/scripts/without-it.sh,kc-ship-flow/scripts/worker-transcript.sh,scripts/kc-dev-flow-contract-test.py
TESTS: python3 kc-ship-flow/scripts/contract-test.py -> exit 0; python3 scripts/kc-dev-flow-contract-test.py -> exit 0
SURFACE: kc-ship-flow/scripts/contract-test.py -> AC-1 | python3 kc-ship-flow/scripts/contract-test.py | git show 2c7f71927f6721401bf8d0a28e67f95dc747aec5:kc-ship-flow/scripts/contract-test.py > kc-ship-flow/scripts/contract-test.py
SURFACE: scripts/ship-flow -> AC-2 | test ! -e scripts/ship-flow | git show 2c7f71927f6721401bf8d0a28e67f95dc747aec5:scripts/ship-flow/accept-evidence.sh > scripts/ship-flow/accept-evidence.sh
SURFACE: kc-ship-flow/scripts/uat-doc.py -> AC-3 | python3 kc-ship-flow/scripts/contract-test.py | git rm -f kc-ship-flow/scripts/uat-doc.py
WITHOUT_IT_COMMAND: python3 kc-ship-flow/scripts/uat-doc.test.py
WITHOUT_IT_REMOVED_VARIANT: sed -i.bak 's#"fixtures"#"nonexistent-fixtures"#' kc-ship-flow/scripts/uat-doc.test.py
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 1; at BASE_SHA -> exit 2
SELF_CHECK: 2026-09-06T13:09:45Z accept-evidence: ACCEPT
ROBOREV: UNAVAILABLE(reason: no reviewer binary in workspace)
AC-1: kc-ship-flow contract-test exits 0 on the candidate, printing "station present" for all 15 moved scripts then PASS
AC-2: test -e scripts/ship-flow exits 1
AC-3: each of the 15 scripts removed in turn → contract-test exits 1 (restored after each)
BLOCKER: none
