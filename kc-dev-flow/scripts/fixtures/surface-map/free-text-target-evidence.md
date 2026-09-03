## Evidence
CANDIDATE_SHA: 4ce46967651c25234f1ed01b18e95d1fdfad2ff5
BRANCH: feature/dev-66-dispatch-carrier-and-e2e-evidence-rules-for-cloud-workers
BASE_SHA: bda45e6bb2716d9276d0542b7c11edd2014ab1be
SURFACE: docs/dev/README.md -> AC-2 | scripts/kc-dev-flow-contract-test.py --check docs/dev/README.md | git checkout HEAD~1 -- docs/dev/README.md
SURFACE: scripts/kc-dev-flow-contract-test.py -> AC-3 | python3 scripts/kc-dev-flow-contract-test.py | git checkout HEAD~1 -- scripts/kc-dev-flow-contract-test.py
SURFACE: scripts/ship-flow/e2e-cli.sh -> AC-1 | scripts/ship-flow/e2e-cli.sh --self-test | git rm -f scripts/ship-flow/e2e-cli.sh
SURFACE: scripts/ship-flow/parse-execute-external.py -> handles the fixture path | scripts/ship-flow/parse-execute-external.py --self-test | git rm -f scripts/ship-flow/parse-execute-external.py
BLOCKER: none
