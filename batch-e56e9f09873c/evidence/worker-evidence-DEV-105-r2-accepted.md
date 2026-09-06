## Evidence
DISPATCH_TOKEN: __TOKEN__
CANDIDATE_SHA: ba96da4ecd8b1b4b26f7f7302fd2c00c02dba681
BRANCH: feature/dev-105-ship-flow-e2e-station-a-passing-cli-journey-at-the-stacked-r2
BASE_SHA: 470b3e412632652e7c758102ceb2c9cecb169a90
FILES: scripts/ship-flow/e2e-gate.py,scripts/ship-flow/e2e-cli.sh,scripts/kc-dev-flow-contract-test.py,docs/ship-flow/README.md,docs/ship-flow/flows/contract-test-journey.yaml,scripts/fixtures/ship-flow/e2e-gate/close-receipt.ac2.json,scripts/fixtures/ship-flow/e2e-gate/plan-receipt.ac2.json
TESTS: python3 scripts/kc-dev-flow-contract-test.py -> exit 0
SURFACE: scripts/ship-flow/e2e-gate.py -> findings 2,3,4,6 | grep -q "resolve_commit" scripts/ship-flow/e2e-gate.py | git checkout 470b3e412632652e7c758102ceb2c9cecb169a90 -- scripts/ship-flow/e2e-gate.py
SURFACE: scripts/ship-flow/e2e-cli.sh -> finding 1 | grep -q "run_stripped" scripts/ship-flow/e2e-cli.sh | git checkout 470b3e412632652e7c758102ceb2c9cecb169a90 -- scripts/ship-flow/e2e-cli.sh
SURFACE: docs/ship-flow/flows/contract-test-journey.yaml -> shallow-safe ac2 | grep -q "contract-test-journey" docs/ship-flow/flows/contract-test-journey.yaml | git rm -f docs/ship-flow/flows/contract-test-journey.yaml
WITHOUT_IT_COMMAND: python3 -c "import importlib.util,sys; spec=importlib.util.spec_from_file_location(\"e2e_gate\",\"scripts/ship-flow/e2e-gate.py\"); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); sys.exit(0 if m.slugify(\"从派工到一条 Slack 消息\")==\"从派工到一条-slack-消息\" else 1)"
WITHOUT_IT_REMOVED_VARIANT: git checkout 470b3e412632652e7c758102ceb2c9cecb169a90 -- scripts/ship-flow/e2e-gate.py
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 1; at BASE_SHA -> exit 1
SHALLOW_CLONE_TEST: exit 0
SELF_CHECK: 2026-09-06T03:28:36Z accept-evidence: ACCEPT
BLOCKER: none
