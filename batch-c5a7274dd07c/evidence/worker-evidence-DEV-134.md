## Evidence
DISPATCH_TOKEN: dev134-2026-09-09
CANDIDATE_SHA: 686f86fb595b390538f883df13fd113bd015a302
BRANCH: feature/dev-134-accept-station-ac-3-path-extraction-must-accept-any-tracked
BASE_SHA: de64053ceb5d508d91ca2441f88502d6aa2ef10c
PR: iamcxa/kc-claude-plugins#395
FILES: kc-ship-flow/scripts/accept-evidence.sh, kc-ship-flow/scripts/contract-test.py, kc-ship-flow/scripts/fixtures/ts-read-path.md, kc-ship-flow/scripts/fixtures/mutant-untracked-path.md, kc-ship-flow/scripts/fixtures/accept-evidence-ts-read-target.ts, kc-ship-flow/scripts/fixtures/accept-evidence-ts-read-target.mts
TESTS: AC-1 accept-evidence.sh ts-read-path.md -> exit 0 ACCEPT; AC-2 mutant-untracked-path.md -> exit 1 REFUSE naming the path; AC-3 contract-test.py -> exit 0
WITHOUT_IT_COMMAND: bash kc-ship-flow/scripts/accept-evidence.sh kc-ship-flow/scripts/fixtures/ts-read-path.md
WITHOUT_IT_REMOVED_VARIANT: git show de64053c:kc-ship-flow/scripts/accept-evidence.sh > kc-ship-flow/scripts/accept-evidence.sh
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 2; at BASE_SHA -> exit 2
SELF_CHECK: accept-evidence: ACCEPT exit 0
BLOCKER: none. Residual: kc-ship-flow/README.md named in the Brief does not exist (FO Brief error; references/stations/accept-evidence.md is the doc).

## Round 2 (c1bd1c03)
is_tracked_path takes CANDIDATE_SHA and tests `git cat-file -e "$CANDIDATE_SHA:$path"`; new contract case: throwaway repo, checkout at base, candidate-only.ts exists only at CANDIDATE_SHA → ACCEPT. Worker proof and FO's independent mutation both flip the case. AC-1 0 / AC-2 1 / contract-test 0.
