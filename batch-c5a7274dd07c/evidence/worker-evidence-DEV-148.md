## Evidence
DISPATCH_TOKEN: dev148-2026-09-09-r3
CANDIDATE_SHA: 1b1cefe155cd503a3b67b3e91b15a539ee88a02b
BRANCH: feature/dev-148-kc-ship-flow-review-station-a-diff-that-touches-a-dependency
BASE_SHA: 68447554384ae047a41bcd5b8e5a483b52698408
FILES: kc-ship-flow/scripts/disposition.py, kc-ship-flow/scripts/contract-test.py, kc-ship-flow/references/stations/disposition.md, kc-ship-flow/skills/first-officer/SKILL.md, fixtures deps-diff-no-supply/{changed-files.txt,findings.json}, deps-diff-with-supply/{changed-files.txt,findings.json,review/findings-7-supply.json}
TESTS: AC-1 disposition.py deps-diff-no-supply -> exit 2 "supply-chain findings required"; AC-2 deps-diff-with-supply -> exit 0; AC-3 contract-test -> exit 0; SKILL.md supply-chain mentions 3
WITHOUT_IT_COMMAND: python3 kc-ship-flow/scripts/disposition.py kc-ship-flow/scripts/fixtures/deps-diff-no-supply; test $? -eq 2
WITHOUT_IT_REMOVED_VARIANT: git show 68447554384ae047a41bcd5b8e5a483b52698408:kc-ship-flow/scripts/disposition.py > kc-ship-flow/scripts/disposition.py
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 1; at BASE_SHA -> exit 1
SELF_CHECK: accept-evidence: ACCEPT
BLOCKER: none

## FO verification at 70581f0a (round 1)
AC-1 exit 2; AC-2 exit 0; contract-test 0; FO mutation of the refusal condition makes AC-1 exit 0 and contract-test fail (first attempt matched nothing, discarded). r2 delta 70581f0a..deb94d0b0c42e44e637cc91141b1346966ce4c98: fixture ids made synthetic (findings-7-supply.json, example pr).

## Round 3 (1b1cefe1): bundle without changed-files.txt → exit 2 'changed-files.txt required'; fixture deps-diff-no-changed-files + contract case. FO mutation (guard → if False) makes contract-test fail at that case; restored passes.
