## Evidence
DISPATCH_TOKEN: dev117-2026-09-06
CANDIDATE_SHA: 3d5f5c2c7ecd4204762618b2e34660c577d706b5
BRANCH: feature/dev-117-b3-kc-ship-flow-sort-the-ship-flow-runtime-prose-into-kernel
BASE_SHA: dc4c8b13c0d86d81e4d79679d8ccb735117a9e52
FILES: docs/ship/runbooks/conductor-cloud.md,kc-ship-flow/references/kernel.md,kc-ship-flow/references/placement.tsv,kc-ship-flow/references/stations/disposition.md,kc-ship-flow/references/stations/e2e-cli.md,kc-ship-flow/references/stations/e2e-gate.md,kc-ship-flow/references/stations/fenced-dispatch.md,kc-ship-flow/references/stations/intent.md,kc-ship-flow/references/stations/notify.md,kc-ship-flow/references/stations/open-pr.md,kc-ship-flow/references/stations/uat-doc.md,kc-ship-flow/references/stations/without-it.md,kc-ship-flow/references/stations/worker-transcript.md,kc-ship-flow/schemas/evidence-block.md,kc-ship-flow/scripts/contract-test.py,kc-ship-flow/scripts/fixtures/runtime-section.2026-09-06.md,kc-ship-flow/scripts/prose-placement-check.py
TESTS: python3 kc-ship-flow/scripts/contract-test.py -> exit 0; python3 scripts/kc-dev-flow-contract-test.py -> exit 0
SURFACE: kc-ship-flow/scripts/prose-placement-check.py -> AC-2 | python3 kc-ship-flow/scripts/prose-placement-check.py | rm -f kc-ship-flow/scripts/prose-placement-check.py
WITHOUT_IT_COMMAND: python3 kc-ship-flow/scripts/prose-placement-check.py >/dev/null 2>&1
WITHOUT_IT_REMOVED_VARIANT: rm -f kc-ship-flow/scripts/prose-placement-check.py
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 2; at BASE_SHA -> exit 2
SELF_CHECK: 2026-09-06T13:58:00Z accept-evidence: ACCEPT
ROBOREV: UNAVAILABLE(reason: no reviewer binary in workspace)
AC-1: kernel.md 28 lines; stations/ 10 files
AC-2: prose-placement-check.py exit 0: 28 segments, 26 placed, 2 residual
AC-3: commit body table lists every segment with destination; residuals reproduced by the script's RESIDUAL lines
BLOCKER: none
