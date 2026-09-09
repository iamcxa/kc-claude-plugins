## Evidence
DISPATCH_TOKEN: dev153-2026-09-09
CANDIDATE_SHA: 2d54370c3d3832880a1195fd9d26d86c5994fa19
BRANCH: feature/dev-153-kc-ship-flow-e2e-gatepy-root-resolves-from-the-plugin-file
BASE_SHA: 39cb179be8af4bd71063d51ce7a58e646368e45d
FILES: kc-ship-flow/scripts/e2e-gate.py, contract-test.py, fixtures/e2e-gate/repo/docs/ship/flows/synthetic-gate-journey.yaml, references/stations/e2e-gate.md, skills/first-officer/SKILL.md, docs/ship-flow/flows/*.yaml (see diff)
TESTS: AC-1 e2e-gate.py --root fixture --flows docs/ship/flows "Synthetic gate journey" -> exit 0; AC-2 --flows docs/missing -> exit 2; AC-3 contract-test -> exit 0
WITHOUT_IT_COMMAND: python3 kc-ship-flow/scripts/e2e-gate.py --root kc-ship-flow/scripts/fixtures/e2e-gate/repo --flows docs/ship/flows "Synthetic gate journey"
WITHOUT_IT_REMOVED_VARIANT: git show 39cb179be8af4bd71063d51ce7a58e646368e45d:kc-ship-flow/scripts/e2e-gate.py > kc-ship-flow/scripts/e2e-gate.py
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 2; at BASE_SHA -> exit 2
SELF_CHECK: accept-evidence: ACCEPT
BLOCKER: none
