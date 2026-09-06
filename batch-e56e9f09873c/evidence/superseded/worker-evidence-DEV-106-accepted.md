## Evidence
DISPATCH_TOKEN: __TOKEN__
CANDIDATE_SHA: dea62ed6965132607120821860bae9fbb897bc7e
BRANCH: feature/dev-106-ship-flow-handoff-one-uat-document-and-one-slack-message
BASE_SHA: 4300eee610a19079664e5d5ee8c609719d313673
FILES: docs/ship-flow/README.md, scripts/ship-flow/notify.sh, scripts/ship-flow/uat-doc.py, scripts/fixtures/ship-flow/uat-doc/batch-1016352e0223/evidence/uat.md.reference, scripts/fixtures/ship-flow/uat-doc/batch-1016352e0223/evidence/worker-evidence-DEV-90.md, scripts/fixtures/ship-flow/uat-doc/batch-1016352e0223/evidence/worker-evidence-DEV-91.md, scripts/fixtures/ship-flow/uat-doc/batch-1016352e0223/evidence/worker-evidence-DEV-92.md, scripts/fixtures/ship-flow/uat-doc/batch-1016352e0223/receipt/close-receipt.DRAFT.json, scripts/fixtures/ship-flow/uat-doc/batch-1016352e0223/receipt/plan-approval.json, scripts/fixtures/ship-flow/uat-doc/batch-1016352e0223/receipt/plan-receipt.json, scripts/fixtures/ship-flow/uat-doc/batch-e56e9f09873c/README.md, scripts/fixtures/ship-flow/uat-doc/batch-e56e9f09873c/evidence/worker-evidence-DEV-104.md, scripts/fixtures/ship-flow/uat-doc/batch-e56e9f09873c/evidence/worker-evidence-DEV-105.md, scripts/fixtures/ship-flow/uat-doc/batch-e56e9f09873c/receipt/plan-approval.json, scripts/fixtures/ship-flow/uat-doc/batch-e56e9f09873c/receipt/plan-receipt.json
TESTS: python3 scripts/kc-dev-flow-contract-test.py -> exit 0
SURFACE: scripts/ship-flow/uat-doc.py -> AC-1 | grep -q '(5 defaults decisions listed above.)' <(python3 scripts/ship-flow/uat-doc.py scripts/fixtures/ship-flow/uat-doc/batch-e56e9f09873c) | git rm -f scripts/ship-flow/uat-doc.py
SURFACE: scripts/ship-flow/notify.sh -> AC-3 | bash scripts/ship-flow/notify.sh t b1 docs/ship-flow/README.md --dry-run --state-dir scripts/fixtures/ship-flow/uat-doc/.notify-surface-check >/dev/null && grep -q "already sent" <(bash scripts/ship-flow/notify.sh t b1 docs/ship-flow/README.md --dry-run --state-dir scripts/fixtures/ship-flow/uat-doc/.notify-surface-check) | git rm -f scripts/ship-flow/notify.sh
SURFACE: docs/ship-flow/README.md -> AC-1 | grep -q "uat-doc.py <batch-dir>" docs/ship-flow/README.md | git checkout 4300eee610a19079664e5d5ee8c609719d313673 -- docs/ship-flow/README.md
WITHOUT_IT_COMMAND: grep -q '(5 defaults decisions listed above.)' <(python3 scripts/ship-flow/uat-doc.py scripts/fixtures/ship-flow/uat-doc/batch-e56e9f09873c) && bash scripts/ship-flow/notify.sh t b2 docs/ship-flow/README.md --dry-run --state-dir scripts/fixtures/ship-flow/uat-doc/.notify-wi-check >/dev/null && grep -q "already sent" <(bash scripts/ship-flow/notify.sh t b2 docs/ship-flow/README.md --dry-run --state-dir scripts/fixtures/ship-flow/uat-doc/.notify-wi-check)
WITHOUT_IT_REMOVED_VARIANT: git rm -f scripts/ship-flow/uat-doc.py && git rm -f scripts/ship-flow/notify.sh
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 1; at BASE_SHA -> exit 1
SELF_CHECK: 2026-09-06T02:38:15Z accept-evidence: ACCEPT
ROBOREV: UNAVAILABLE(reason: no reviewer binary in workspace)
AC-1: uat-doc.py on batch-1016352e0223 reproduces the hand-written uat.md's 5 section headers in order; every shared fact agrees; 53-line diff is phrasing plus the #366 stack annotation the record does not carry.
AC-2: uat-doc.py on batch-e56e9f09873c lists all 5 defaults decisions; awk count 5 matches the trailer.
AC-3: notify.sh twice for the same batch and state-dir: first DRY-RUN sent msg-a47a71a92bf6; second DRY-RUN skip (already sent), same id, one file.
AC-4: python3 scripts/kc-dev-flow-contract-test.py exits 0 at the candidate.
BLOCKER: none
