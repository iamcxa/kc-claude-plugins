## Evidence
DISPATCH_TOKEN: __TOKEN__
CANDIDATE_SHA: 3a733578afbdc3a3e784c9484861e9b9dc5eb83b
BRANCH: feature/dev-104-ship-flow-review-station-open-the-draft-pr-and-run-kc-pr
BASE_SHA: 4300eee610a19079664e5d5ee8c609719d313673
FILES: docs/ship-flow/README.md, scripts/fixtures/ship-flow/fake-gh/gh, scripts/fixtures/ship-flow/findings-empty.json, scripts/fixtures/ship-flow/findings-security.json, scripts/fixtures/ship-flow/findings-style.json, scripts/fixtures/ship-flow/open-pr-evidence.md, scripts/ship-flow/disposition.py, scripts/ship-flow/open-pr.sh
TESTS: python3 scripts/kc-dev-flow-contract-test.py -> exit 0
SURFACE: scripts/ship-flow/open-pr.sh -> AC-1 | test "$(PATH="$PWD/scripts/fixtures/ship-flow/fake-gh:$PATH" bash scripts/ship-flow/open-pr.sh scripts/fixtures/ship-flow/open-pr-evidence.md 2>/dev/null)" = "777" | git rm -f scripts/ship-flow/open-pr.sh
SURFACE: scripts/ship-flow/disposition.py -> AC-3 | grep -q '"disposition": "reviewer-absent"' <(python3 scripts/ship-flow/disposition.py scripts/fixtures/ship-flow/findings-empty.json) | git rm -f scripts/ship-flow/disposition.py
SURFACE: docs/ship-flow/README.md -> AC-1 | grep -qF 'the review station is two scripts either side of that session' docs/ship-flow/README.md | git checkout 4300eee610a19079664e5d5ee8c609719d313673 -- docs/ship-flow/README.md
WITHOUT_IT_COMMAND: python3 scripts/ship-flow/disposition.py scripts/fixtures/ship-flow/findings-empty.json | grep -q '"disposition": "reviewer-absent"'
WITHOUT_IT_REMOVED_VARIANT: git rm -f scripts/ship-flow/disposition.py
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 1; at BASE_SHA -> exit 1
SELF_CHECK: 2026-09-06T02:20:47Z accept-evidence: ACCEPT
ROBOREV: UNAVAILABLE(reason: no reviewer binary in workspace)
AC-1: open-pr.sh opened a Draft PR (stub gh) with title equal to the commit subject and body carrying BASE_SHA, CANDIDATE_SHA, the without-it pair, and SELF_CHECK; printed PR number 777 on stdout.
AC-2: disposition.py on findings-security.json (one security finding) -> disposition block; on findings-style.json (one style finding) -> disposition listed. Both runs recorded.
AC-3: disposition.py on findings-empty.json and on a missing path both -> disposition reviewer-absent, marker fallback_to_fo_diff_read, never no-findings.
AC-4: python3 scripts/kc-dev-flow-contract-test.py exits 0 at the candidate.
BLOCKER: none
