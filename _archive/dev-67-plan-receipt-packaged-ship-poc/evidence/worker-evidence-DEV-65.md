## Evidence
CANDIDATE_SHA: 09f1f72c70be703b6a8cc826a17d9137caadf3ec
BRANCH: feature/dev-65-without_it_command-is-one-verbatim-shell-line-the-fo-runs
BASE_SHA: b5adfba85b346f6605d507764c67ee19d412a95d
FILES: docs/dev/README.md, scripts/kc-dev-flow-contract-test.py, scripts/ship-flow/without-it.sh
TESTS: python3 scripts/kc-dev-flow-contract-test.py -> exit 0
WITHOUT_IT_COMMAND: python3 scripts/kc-dev-flow-contract-test.py
WITHOUT_IT_REMOVED_VARIANT: git checkout b5adfba85b346f6605d507764c67ee19d412a95d -- docs/dev/README.md
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 1
ROBOREV: UNAVAILABLE(reason: no reviewer binary in workspace)
AC-1: scripts/ship-flow/without-it.sh 0144264343775f4c74f517ccea488a8ef91c44bc "grep -q '^## Goal$' docs/dev/README.md" "git checkout f47fd8ca34f54ada90e6292bcffcdb55a96ea44c -- docs/dev/README.md" -> retained=0 removed=1, script exit 0 (PASS); same sha/removed-variant with "true" as command -> retained=0 removed=0, script exit 1 (FAIL, as required)
AC-2: docs/dev/README.md "## Ship-flow runtime" defines CANDIDATE_SHA, BRANCH, BASE_SHA, WITHOUT_IT_COMMAND, WITHOUT_IT_REMOVED_VARIANT and states the one-line/no-external-file/run-verbatim rule; contract test asserts these phrases and passes: exit 0
AC-3: removed the one-line-rule sentence from docs/dev/README.md -> python3 scripts/kc-dev-flow-contract-test.py exited 1 with "Ship-flow runtime omits the WITHOUT_IT_COMMAND one-line rule: ..."; restored the sentence -> exit 0 (PASS)
DEFECT-1 (secrets): GH_TOKEN="dummy-caller-token" scripts/ship-flow/without-it.sh 0144264343775f4c74f517ccea488a8ef91c44bc 'test -z "$GH_TOKEN"' "true" -> retained exited 0, removed exited 0 (GH_TOKEN unset inside both variants despite being set in the caller's shell)
DEFECT-2 (isolation): scripts/ship-flow/without-it.sh 0144264343775f4c74f517ccea488a8ef91c44bc 'if [ -f .without-it-marker ] && grep -q present .without-it-marker; then echo MARKER_FOUND_ISOLATION_FAILED; exit 1; else echo present > .without-it-marker; exit 0; fi' "true" -> retained exited 0 (wrote marker), removed exited 0 (marker absent, took the write branch again, MARKER_FOUND_ISOLATION_FAILED never printed) -- worktree reset before the removed run confirmed
BLOCKER: none
