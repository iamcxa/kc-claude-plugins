## Evidence
DISPATCH_TOKEN: dev118-2026-09-06-r2
CANDIDATE_SHA: 94c2696e277a10b213de04796aa2f7598c8a2a02
BRANCH: feature/dev-118-b4-poc-kc-ship-flow-a-batch-×-station-pin-loader-with-its
BASE_SHA: 2c7f71927f6721401bf8d0a28e67f95dc747aec5
FILES: kc-ship-flow/scripts/pin.py, kc-ship-flow/scripts/pin.test.py, kc-ship-flow/schemas/resources.json, kc-ship-flow/references/poc-batch-station-pin.md
TESTS: python3 kc-ship-flow/scripts/pin.test.py -> exit 0; python3 scripts/kc-dev-flow-contract-test.py -> exit 0; python3 kc-ship-flow/scripts/contract-test.py -> exit 0
SURFACE: kc-ship-flow/scripts/pin.py -> AC-1,AC-2,AC-3 | python3 kc-ship-flow/scripts/pin.py write --batch b1 --station accepted | rm kc-ship-flow/scripts/pin.py
WITHOUT_IT_COMMAND: python3 kc-ship-flow/scripts/pin.py write --batch acc --station accepted | grep -q "\"contract_digest\": \"[0-9a-f]\{64\}\""
WITHOUT_IT_REMOVED_VARIANT: rm kc-ship-flow/scripts/pin.py
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 1; at BASE_SHA -> exit 1
SELF_CHECK: 2026-09-06T13:09:35Z accept-evidence: ACCEPT
ROBOREV: UNAVAILABLE(reason: no reviewer binary in workspace)
AC-1: write printed a kc-ship-flow-batch-pin/v1 record with a 64-hex contract_digest, exit 0
AC-2: check exits 1 naming CONTRACT_DIGEST_MISMATCH (changed resource) and PREVIOUS_STATION_MISMATCH; both mutations in pin.test.py
AC-3: grep -c 'import.*profile_contract_loader' pin.py prints 0
BLOCKER: none
