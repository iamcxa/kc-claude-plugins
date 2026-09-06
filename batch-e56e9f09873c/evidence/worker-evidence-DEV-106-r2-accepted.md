## Evidence
DISPATCH_TOKEN: __TOKEN__
CANDIDATE_SHA: b6d503470d3736bad8761e148dea159d9040ca78
BRANCH: feature/dev-106-ship-flow-handoff-one-uat-document-and-one-slack-message-r2
BASE_SHA: dea62ed6965132607120821860bae9fbb897bc7e
FILES: scripts/ship-flow/uat-doc.py, scripts/ship-flow/notify.sh, scripts/ship-flow/uat-doc.test.py, scripts/ship-flow/notify.test.sh, scripts/kc-dev-flow-contract-test.py
TESTS: python3 scripts/kc-dev-flow-contract-test.py -> exit 0
SURFACE: scripts/ship-flow/uat-doc.py -> #1-#8,#10 | python3 scripts/ship-flow/uat-doc.test.py | git checkout dea62ed6965132607120821860bae9fbb897bc7e -- scripts/ship-flow/uat-doc.py
SURFACE: scripts/ship-flow/notify.sh -> #9 | bash scripts/ship-flow/notify.test.sh | git checkout dea62ed6965132607120821860bae9fbb897bc7e -- scripts/ship-flow/notify.sh
WITHOUT_IT_COMMAND: python3 scripts/ship-flow/uat-doc.py scripts/fixtures/ship-flow/uat-doc/batch-1016352e0223 | grep -q "^## Unaccounted$"
WITHOUT_IT_REMOVED_VARIANT: git checkout dea62ed6965132607120821860bae9fbb897bc7e -- scripts/ship-flow/uat-doc.py
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 1; at BASE_SHA -> exit 1
SHALLOW_CLONE_TEST: exit 0
SELF_CHECK: 2026-09-06T03:14:14Z accept-evidence: ACCEPT
BLOCKER: none
