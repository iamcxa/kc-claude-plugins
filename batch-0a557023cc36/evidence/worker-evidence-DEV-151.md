## Evidence
DISPATCH_TOKEN: dev151-2026-09-09
CANDIDATE_SHA: 6f914ac73bd30a3b3c61567377b3511cd8806b58
BRANCH: feature/dev-151-kc-ship-flow-open-prsh-write-the-pr-body-per-the-pr-merge
BASE_SHA: 39cb179be8af4bd71063d51ce7a58e646368e45d
FILES: kc-ship-flow/scripts/open-pr.sh, contract-test.py, fixtures/open-pr/{evidence.md,evidence-no-tests.md,batch/README.md,batch/receipt/plan-receipt.json}, references/stations/open-pr.md, schemas/evidence-block.md, skills/first-officer/SKILL.md
TESTS: AC-1 open-pr.sh evidence.md batch --dry-run -> exit 0 (lead ≤25 words, sections in order); AC-2 evidence-no-tests.md -> exit 0, no Evidence section; AC-3 contract-test -> exit 0
WITHOUT_IT_COMMAND: bash kc-ship-flow/scripts/open-pr.sh kc-ship-flow/scripts/fixtures/open-pr/evidence.md kc-ship-flow/scripts/fixtures/open-pr/batch --dry-run | grep -q '^## What changed$'
WITHOUT_IT_REMOVED_VARIANT: git show 39cb179be8af4bd71063d51ce7a58e646368e45d:kc-ship-flow/scripts/open-pr.sh > kc-ship-flow/scripts/open-pr.sh
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 1; at BASE_SHA -> exit 1
SELF_CHECK: accept-evidence: ACCEPT (AC-3 WARN: candidate-only fixture paths)
BLOCKER: none

## FO verification at 6f914ac7 (round 1)
Installed station ACCEPT. AC-1 dry run: 46 words, lead 25 words, sections in order; AC-2: no Evidence heading; contract-test 0. Falsifier run on this PR's own evidence + batch: 34 words, lead = the Captain's quote, What changed = five `Update <file>` bullets, Evidence = `3/3 passed` (AC count) — mechanics pass, content fails the template's intent. Repair round 1: derive the body from the dev entity per pr-merge.md's extraction table (lead from the entity paragraph, What changed from `[x]` DONE items, Evidence from validation N/N), with a `--what-changed-file` fallback and refusal when neither exists.
