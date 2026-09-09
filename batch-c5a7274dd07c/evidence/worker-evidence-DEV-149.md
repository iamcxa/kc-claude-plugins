## Evidence
DISPATCH_TOKEN: dev149-2026-09-09
CANDIDATE_SHA: 62dbffea58cff3db1ee089a6b2e977ab0dd5635d
BRANCH: feature/dev-149-kc-ship-flow-merge-verdict-verify-the-named-ci-check
BASE_SHA: 68447554384ae047a41bcd5b8e5a483b52698408
FILES: kc-ship-flow/scripts/ci-covers.sh, ci-covers.test.sh, contract-test.py, fixtures/monorepo-uncovered/**, fixtures/monorepo-covered/**, skills/first-officer/SKILL.md, references/stations/merge-station.md, references/stations/ci-covers.md
TESTS: contract-test 0; ci-covers.test.sh 0 (8 passed); AC-1 uncovered -> exit 1 "experiments/island not run by pr-test (b …)"; AC-2 covered -> exit 0
WITHOUT_IT_COMMAND: bash kc-ship-flow/scripts/ci-covers.sh kc-ship-flow/scripts/fixtures/monorepo-uncovered experiments/island pr-test; test $? -eq 1
WITHOUT_IT_REMOVED_VARIANT: sed -i.bak 's/matched=1/matched=0/' kc-ship-flow/scripts/ci-covers.sh
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 1; at BASE_SHA -> exit 1
SELF_CHECK: accept-evidence: ACCEPT
BLOCKER: none

## FO verification at 62dbffea58cff3db1ee089a6b2e977ab0dd5635d
AC-1 exit 1 with the (b) reason; AC-2 exit 0; ci-covers.test 8/8; contract-test 0. Pair re-run by script: retained 0; with the variant (initial state flipped to matched) the uncovered fixture passes, so the test exits 1 — the pair proves the check exists. 19 comment lines in ci-covers.sh (usage/limit block the Brief asked for; reviewer to judge). 10 files +377.
