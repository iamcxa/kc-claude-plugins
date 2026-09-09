## Evidence
DISPATCH_TOKEN: dev156-2026-09-09
CANDIDATE_SHA: 04b896dab9701ea40dd9a4ff26f71806f9c41402
BRANCH: feature/dev-156-kc-ship-flow-dispatch-station-dispatch-dev-entities-via
BASE_SHA: 39cb179be8af4bd71063d51ce7a58e646368e45d
FILES: kc-ship-flow/scripts/fenced-dispatch.sh, fenced-dispatch.test.sh, contract-test.py, fixtures/dispatch/{task-with-model,task-without-model,task-build-fails}(.md + README.md), references/stations/fenced-dispatch.md, skills/first-officer/SKILL.md
TESTS: contract-test 0; fenced-dispatch.test.sh 0 (3 passed); dry-run on task-with-model prints --model sonnet and message_sha256; FO re-ran the dry run and both suites at 04b896dab9701ea40dd9a4ff26f71806f9c41402
WITHOUT_IT_COMMAND: bash kc-ship-flow/scripts/fenced-dispatch.sh witi-state h1 1 dev-1.g1 00000000-0000-0000-0000-000000000000 main --entity-path kc-ship-flow/scripts/fixtures/dispatch/task-with-model.md --stage implementation --dry-run
WITHOUT_IT_REMOVED_VARIANT: git show 39cb179be8af4bd71063d51ce7a58e646368e45d:kc-ship-flow/scripts/fenced-dispatch.sh > kc-ship-flow/scripts/fenced-dispatch.sh
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 2; at BASE_SHA -> exit 2
SELF_CHECK: accept-evidence: ACCEPT
BLOCKER: none. Premise gap: spacedock dispatch build flag mode requires --checklist-file; the station writes a one-line procedural checklist (documented).
