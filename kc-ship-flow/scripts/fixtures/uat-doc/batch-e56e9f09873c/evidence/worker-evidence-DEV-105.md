## Evidence
DISPATCH_TOKEN: __TOKEN__
CANDIDATE_SHA: 470b3e412632652e7c758102ceb2c9cecb169a90
BRANCH: feature/dev-105-ship-flow-e2e-station-a-passing-cli-journey-at-the-stacked
BASE_SHA: 4300eee610a19079664e5d5ee8c609719d313673
FILES: docs/ship-flow/README.md,docs/ship-flow/flows/from-dispatch-to-one-slack-message.yaml,scripts/ship-flow/e2e-gate.py,scripts/fixtures/ship-flow/e2e-gate/plan-receipt.ac2.json,scripts/fixtures/ship-flow/e2e-gate/close-receipt.ac2.json,scripts/fixtures/ship-flow/e2e-gate/plan-receipt.ac3.json,scripts/fixtures/ship-flow/e2e-gate/close-receipt.ac3.json,scripts/fixtures/ship-flow/e2e-gate/plan-receipt.ac4.json,scripts/fixtures/ship-flow/e2e-gate/close-receipt.ac4.json,scripts/fixtures/ship-flow/e2e-gate/recorded-evidence-block.txt
TESTS: python3 scripts/kc-dev-flow-contract-test.py -> exit 0
SURFACE: docs/ship-flow/README.md -> AC-1 | grep -q "scripts/ship-flow/e2e-gate.py <plan-receipt.json> <close-receipt.json>" docs/ship-flow/README.md | git show 4300eee610a19079664e5d5ee8c609719d313673:docs/ship-flow/README.md > docs/ship-flow/README.md
SURFACE: docs/ship-flow/flows/from-dispatch-to-one-slack-message.yaml -> AC-1 | grep -q "Execute external" docs/ship-flow/flows/from-dispatch-to-one-slack-message.yaml && grep -q "e2e-gate.py" docs/ship-flow/flows/from-dispatch-to-one-slack-message.yaml | git rm -f docs/ship-flow/flows/from-dispatch-to-one-slack-message.yaml
SURFACE: scripts/ship-flow/e2e-gate.py -> AC-2 | grep -q "def milestone_name" scripts/ship-flow/e2e-gate.py && grep -q "def stacked_head" scripts/ship-flow/e2e-gate.py | git rm -f scripts/ship-flow/e2e-gate.py
WITHOUT_IT_COMMAND: bash scripts/ship-flow/e2e-cli.sh $(git rev-parse HEAD) docs/ship-flow/flows/from-dispatch-to-one-slack-message.yaml
WITHOUT_IT_REMOVED_VARIANT: rm -f docs/ship-flow/flows/from-dispatch-to-one-slack-message.yaml
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 2; at BASE_SHA -> exit 2
SELF_CHECK: 2026-09-06T02:21:12Z accept-evidence: ACCEPT
ROBOREV: UNAVAILABLE(reason: no reviewer binary in workspace)
AC-1: flow exists with two Execute external steps; e2e-cli.sh at the candidate ran both and exited 0
AC-2: e2e-gate.py with a milestone naming an existing flow ran e2e-cli.sh at the stacked head, recorded the log path, exit 0
AC-3: e2e-gate.py with a journey but no flow file printed e2e: not applicable (reason ...) and exited 0
AC-4: e2e-gate.py with no milestone named exited 1
BLOCKER: none
