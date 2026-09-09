## Evidence
DISPATCH_TOKEN: dev155-2026-09-09-r3
CANDIDATE_SHA: 7d0ac8cc813b82b7cf06e23a2347db788c89079d
BRANCH: feature/dev-155-accept-station-a-without-it-pair-that-lives-in-a-test-file
BASE_SHA: 39cb179be8af4bd71063d51ce7a58e646368e45d
FILES: kc-ship-flow/scripts/accept-evidence.sh, contract-test.py, fixtures/{dev-155-new-test.sh,new-test-file-pair.md,mutant-absent-both-sides.md}, references/stations/accept-evidence.md, schemas/evidence-block.md
TESTS: AC-1 accept-evidence.sh new-test-file-pair.md -> exit 0 ACCEPT (records absent (added by candidate)); AC-2 mutant-absent-both-sides.md -> exit 1 REFUSE naming the path; AC-3 contract-test -> exit 0
WITHOUT_IT_COMMAND: bash kc-ship-flow/scripts/accept-evidence.sh kc-ship-flow/scripts/fixtures/new-test-file-pair.md
WITHOUT_IT_REMOVED_VARIANT: git show 39cb179be8af4bd71063d51ce7a58e646368e45d:kc-ship-flow/scripts/accept-evidence.sh > kc-ship-flow/scripts/accept-evidence.sh
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 1; at BASE_SHA -> exit 2
SELF_CHECK: accept-evidence: ACCEPT (AC-3 WARN: fixture not restored by the variant)
BLOCKER: none

## FO verification at fdc4d6ff (worker block restatement pending)
Candidate station: new-test-file-pair.md → ACCEPT with `AC-1: at BASE_SHA: absent (added by candidate): …dev-155-new-test.sh`; mutant-absent-both-sides.md → REFUSE naming the path (127); contract-test 0. Base station on the new-test-file fixture → REFUSE 127 (the defect). FO mutation: forcing the `added_by_candidate` guard false makes the candidate station refuse the fixture and contract-test fail; restored passes. 4 comment lines in accept-evidence.sh. The worker's first pair (delete the command's own file → 127) was degenerate; restatement requested (base station as the removed variant).

## Round 2 (7d0ac8cc): true-add set via `git diff --name-only --diff-filter=A -M`; only the executed path (after a leading interpreter) may qualify; contract cases for a renamed script (REFUSE) and an unrelated-127 script with a new fixture argument (REFUSE). FO mutations: `--no-renames` fails the rename case (a plain `-M` removal is a no-op under git's default diff.renames=true); making the executed path the last token fails the unrelated-127 case. 9 comment lines in accept-evidence.sh.
