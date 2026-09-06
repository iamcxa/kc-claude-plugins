## Evidence
DISPATCH_TOKEN: __TOKEN__
CANDIDATE_SHA: e9b04927c24411a57617522ce4d55c32a74ab2f5
BRANCH: feature/dev-94-ac2-r4-static-check-weakest-sufficient-r5
BASE_SHA: 030a0bb763463bed8c97ff1f1af9c00c2565cd5f
FILES: scripts/fixtures/ship-flow/mutant-negation-variant.md,scripts/fixtures/ship-flow/real-AC367-r2.md,scripts/fixtures/ship-flow/real-AC4-r3-s29.md,scripts/fixtures/ship-flow/real-AC5-r2.md,scripts/ship-flow/accept-evidence.sh
TESTS: python3 scripts/kc-dev-flow-contract-test.py -> exit 0
SURFACE: scripts/ship-flow/accept-evidence.sh -> AC-1 AC-3 | bash scripts/ship-flow/accept-evidence.sh scripts/fixtures/ship-flow/mutant-drop-path.md 2>&1 | grep -q 'WARN' | git show 030a0bb763463bed8c97ff1f1af9c00c2565cd5f:scripts/ship-flow/accept-evidence.sh > scripts/ship-flow/accept-evidence.sh
WITHOUT_IT_COMMAND: bash scripts/ship-flow/accept-evidence.sh scripts/fixtures/ship-flow/mutant-drop-path.md 2>&1 | grep -q 'WARN'
WITHOUT_IT_REMOVED_VARIANT: git show 030a0bb763463bed8c97ff1f1af9c00c2565cd5f:scripts/ship-flow/accept-evidence.sh > scripts/ship-flow/accept-evidence.sh
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 1; at BASE_SHA -> exit 1
AC-1: Base station refuses mutant-drop-path with no WARN (command reads two changed files but variant restores only one)
AC-2: Station extracts variant alterations from git show, git checkout, git rm, rm, sed, >, >>, mv patterns
AC-3: Station computes changed_read_paths as intersection of command reads and git diff BASE..CANDIDATE
AC-4: CANDIDATE_SHA e9b04927c24411a57617522ce4d55c32a74ab2f5 is reachable and valid
AC-5: WARN is issued when variant restores some but not all changed read paths
AC-6: ACCEPT is issued when variant restores at least one changed read path (mutant-drop-path: variant restores docs/dev/README.md)
AC-7: Contract test passes (repository-wide regression check: exit 0)
BLOCKER: none
