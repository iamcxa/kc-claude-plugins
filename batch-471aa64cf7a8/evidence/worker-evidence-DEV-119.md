## Evidence
DISPATCH_TOKEN: dev119-2026-09-06-r2
CANDIDATE_SHA: 043eb7e65b1c98f52f1f65f00498f553f908f285
BRANCH: feature/dev-119-b5-kc-ship-flow-commission-docsship-as-a-spacedock-workflow
BASE_SHA: 4095e5fcae1d3181abd6cf65379ccd3a21c998be
FILES: kc-ship-flow/references/stations/accept-evidence.md, kc-ship-flow/references/stations/dev-debrief.md, kc-ship-flow/references/stations/ship-debrief.md, docs/ship/README.md, kc-ship-flow/scripts/contract-test.py, kc-ship-flow/scripts/local-profile-check.py, kc-ship-flow/skills/first-officer/SKILL.md
TESTS: python3 scripts/kc-dev-flow-contract-test.py -> exit 0; python3 kc-ship-flow/scripts/contract-test.py -> exit 0
SURFACE: docs/ship/README.md -> AC-1 | spacedock status --workflow-dir docs/ship | rm -f docs/ship/README.md
SURFACE: kc-ship-flow/scripts/local-profile-check.py -> AC-3 | python3 kc-ship-flow/scripts/local-profile-check.py docs/ship/README.md | rm -f kc-ship-flow/scripts/local-profile-check.py
WITHOUT_IT_COMMAND: python3 kc-ship-flow/scripts/local-profile-check.py docs/ship/README.md
WITHOUT_IT_REMOVED_VARIANT: rm -f kc-ship-flow/scripts/local-profile-check.py
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 2; at BASE_SHA -> exit 2
SELF_CHECK: 2026-09-06T15:00:42Z accept-evidence: ACCEPT
ROBOREV: UNAVAILABLE(reason: no reviewer binary in workspace)
AC-1: spacedock status --workflow-dir docs/ship exit 0, six stages resolvable
AC-2: not run by the worker (Brief: FO runs a real batch after merge)
AC-3: deleting the Runtime row → local-profile-check.py exit 1 LOCAL_PROFILE_MISSING_ROW: Runtime
BLOCKER: none
