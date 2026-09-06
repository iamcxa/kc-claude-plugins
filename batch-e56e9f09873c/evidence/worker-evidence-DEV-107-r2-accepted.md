## Evidence
DISPATCH_TOKEN: dev107r2
CANDIDATE_SHA: ede6eecbf2bbff9b4cdb2d553151d237f18012d9
BRANCH: feature/dev-107-ship-flow-close-the-close-receipt-refuses-an-undispositioned-r2
BASE_SHA: 9282343c43afada5e50ff2a282a7b36102d3cfc8
FILES: docs/plan-flow/schema/validate-receipt.py,docs/plan-flow/schema/kc-ship-close-receipt.v1.schema.json,docs/plan-flow/schema/close-receipt.test.py,scripts/ship-flow/dev-debrief.py,scripts/ship-flow/dev-debrief.test.py,scripts/ship-flow/ship-debrief.py,scripts/ship-flow/ship-debrief.test.py,scripts/kc-dev-flow-contract-test.py
TESTS: python3 scripts/kc-dev-flow-contract-test.py -> exit 0
SHALLOW_CLONE_TEST: exit 0
SURFACE: docs/plan-flow/schema/validate-receipt.py -> #1,#2,#7 | python3 docs/plan-flow/schema/close-receipt.test.py | git checkout 9282343c43afada5e50ff2a282a7b36102d3cfc8 -- docs/plan-flow/schema/validate-receipt.py
SURFACE: scripts/ship-flow/dev-debrief.py -> #3,#4,#5 | python3 scripts/ship-flow/dev-debrief.test.py | git checkout 9282343c43afada5e50ff2a282a7b36102d3cfc8 -- scripts/ship-flow/dev-debrief.py
SURFACE: scripts/ship-flow/ship-debrief.py -> #3,#5 | python3 scripts/ship-flow/ship-debrief.test.py | git checkout 9282343c43afada5e50ff2a282a7b36102d3cfc8 -- scripts/ship-flow/ship-debrief.py
WITHOUT_IT_COMMAND: python3 docs/plan-flow/schema/close-receipt.test.py docs/plan-flow/schema/validate-receipt.py
WITHOUT_IT_REMOVED_VARIANT: git checkout 9282343c43afada5e50ff2a282a7b36102d3cfc8 -- docs/plan-flow/schema/validate-receipt.py docs/plan-flow/schema/kc-ship-close-receipt.v1.schema.json scripts/ship-flow/dev-debrief.py scripts/ship-flow/ship-debrief.py
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 1; at BASE_SHA -> exit 2
SELF_CHECK: accept-evidence: ACCEPT
BLOCKER: none
