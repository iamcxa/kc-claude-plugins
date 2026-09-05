## Evidence
DISPATCH_TOKEN: __TOKEN__
CANDIDATE_SHA: 030a0bb763463bed8c97ff1f1af9c00c2565cd5f
BRANCH: feature/dev-94-ac2-r3-accept-station-fail-closed
BASE_SHA: 1b61997b0ca78a6fbab281447f44a47238a8b524
FILES: scripts/ship-flow/accept-evidence.sh,scripts/fixtures/ship-flow/mutant-prose-after-semicolon.md,scripts/fixtures/ship-flow/mutant-command-not-found.md,scripts/fixtures/ship-flow/mutant-out-of-tree.md,scripts/fixtures/ship-flow/mutant-unparseable.md,scripts/fixtures/ship-flow/control-double-assert.md
TESTS: python3 scripts/kc-dev-flow-contract-test.py -> exit 0
SURFACE: scripts/ship-flow/accept-evidence.sh -> AC-1,AC-2,AC-3,AC-4 | grep -q "check_masked_exit\|check_command_for_out_of_tree" scripts/ship-flow/accept-evidence.sh | git show 1b61997b0ca78a6fbab281447f44a47238a8b524:scripts/ship-flow/accept-evidence.sh > scripts/ship-flow/accept-evidence.sh; scripts/fixtures/ship-flow/mutant-*.md, control-*.md -> AC-1..AC-6 | each fixture refuses or accepts as expected | git rm -f scripts/fixtures/ship-flow/mutant-*.md scripts/fixtures/ship-flow/control-*.md
WITHOUT_IT_COMMAND: grep -q "check_masked_exit\|check_command_for_out_of_tree" scripts/ship-flow/accept-evidence.sh
WITHOUT_IT_REMOVED_VARIANT: git show 1b61997b0ca78a6fbab281447f44a47238a8b524:scripts/ship-flow/accept-evidence.sh > scripts/ship-flow/accept-evidence.sh
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 1; at BASE_SHA -> exit 1
AC-1: S29 block (mutant-prose-after-semicolon.md) refused with "WITHOUT_IT_COMMAND reads out-of-tree path: ~/.claude/plugins/test" - detects out-of-tree path first
AC-2: Command not found (mutant-command-not-found.md) refused with "WITHOUT_IT_COMMAND did not run at BASE_SHA (exit 127 - command not found)" - detects exit code 127
AC-3: Out-of-tree path read (mutant-out-of-tree.md) refused with "WITHOUT_IT_COMMAND reads out-of-tree path: ~/.claude/anything" - detects out-of-tree paths
AC-4: Unparseable command (mutant-unparseable.md) refused with "AC-3: cannot extract paths from WITHOUT_IT_COMMAND - command may be unparseable" - SKIP becomes REFUSE on parse failure
AC-5_TABLE: DEV-90: BASE=ACCEPT,CANDIDATE=ACCEPT; DEV-91: BASE=REFUSE,CANDIDATE=REFUSE; DEV-92: BASE=ACCEPT,CANDIDATE=ACCEPT; mutant-drop-path: BASE=REFUSE,CANDIDATE=REFUSE; mutant-extra-path: BASE=ACCEPT,CANDIDATE=ACCEPT; mutant-sha-mismatch: BASE=REFUSE,CANDIDATE=REFUSE
AC-6: Control fixture (control-double-assert.md) with two assertions joined by && and no trailing || is accepted at CANDIDATE_SHA
AC-7: Contract test passes with exit 0
BLOCKER: none