## Evidence
DISPATCH_TOKEN: __TOKEN__
CANDIDATE_SHA: 0fd7ad471e6657007aeb011c96a0e8a597fb7ea5
BRANCH: feature/dev-104-ship-flow-review-station-open-the-draft-pr-and-run-kc-pr-r2
BASE_SHA: 3a733578afbdc3a3e784c9484861e9b9dc5eb83b
FILES: docs/ship-flow/README.md,scripts/kc-dev-flow-contract-test.py,scripts/ship-flow/disposition.py,scripts/ship-flow/open-pr.sh,scripts/fixtures/ship-flow/findings-malformed-entry.json,scripts/fixtures/ship-flow/findings-security-cased.json,scripts/fixtures/ship-flow/findings-unrecognized-category.json,scripts/fixtures/ship-flow/open-pr-evidence-double-block.md,scripts/fixtures/ship-flow/open-pr-evidence-fork-branch.md
TESTS: python3 scripts/kc-dev-flow-contract-test.py -> exit 0
SURFACE: scripts/ship-flow/open-pr.sh -> finding #1 | bash scripts/ship-flow/open-pr.sh scripts/fixtures/ship-flow/open-pr-evidence-fork-branch.md 2>&1 | grep -q "fork syntax refused" | git show 3a733578afbdc3a3e784c9484861e9b9dc5eb83b:scripts/ship-flow/open-pr.sh > scripts/ship-flow/open-pr.sh
SURFACE: scripts/ship-flow/disposition.py -> finding #2 | python3 scripts/ship-flow/disposition.py scripts/fixtures/ship-flow/findings-security-cased.json | grep -q '"disposition": "block"' | git show 3a733578afbdc3a3e784c9484861e9b9dc5eb83b:scripts/ship-flow/disposition.py > scripts/ship-flow/disposition.py
SURFACE: docs/ship-flow/README.md -> finding #6-doc | grep -q "runs it headless for its ablation" docs/ship-flow/README.md | git show 3a733578afbdc3a3e784c9484861e9b9dc5eb83b:docs/ship-flow/README.md > docs/ship-flow/README.md
SURFACE: scripts/kc-dev-flow-contract-test.py -> finding #8 | grep -q "open-pr-evidence-fork-branch.md" scripts/kc-dev-flow-contract-test.py | git show 3a733578afbdc3a3e784c9484861e9b9dc5eb83b:scripts/kc-dev-flow-contract-test.py > scripts/kc-dev-flow-contract-test.py
WITHOUT_IT_COMMAND: bash scripts/ship-flow/open-pr.sh scripts/fixtures/ship-flow/open-pr-evidence-fork-branch.md 2>&1 | grep -q "fork syntax refused"
WITHOUT_IT_REMOVED_VARIANT: git show 3a733578afbdc3a3e784c9484861e9b9dc5eb83b:scripts/ship-flow/open-pr.sh > scripts/ship-flow/open-pr.sh
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 1; at BASE_SHA -> exit 1
SELF_CHECK: 2026-09-06T02:48:18Z accept-evidence: ACCEPT
BLOCKER: none
