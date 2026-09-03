## Evidence
SURFACE: docs/dev/README.md -> AC-2 | scripts/kc-dev-flow-contract-test.py --check docs/dev/README.md | git checkout HEAD~1 -- docs/dev/README.md
SURFACE: scripts/kc-dev-flow-contract-test.py -> AC-3 | python3 scripts/kc-dev-flow-contract-test.py | git checkout HEAD~1 -- scripts/kc-dev-flow-contract-test.py
SURFACE: scripts/ship-flow/e2e-cli.sh -> AC-1 | scripts/ship-flow/e2e-cli.sh --self-test | git rm -f scripts/ship-flow/e2e-cli.sh
SURFACE: scripts/ship-flow/parse-execute-external.py -> AC-1 | scripts/ship-flow/parse-execute-external.py --self-test | git rm -f scripts/ship-flow/parse-execute-external.py
SURFACE: scripts/ship-flow/legacy-runner.sh -> removal | - | -
BLOCKER: none
