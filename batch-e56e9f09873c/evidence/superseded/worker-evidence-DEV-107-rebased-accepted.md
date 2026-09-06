## Evidence
DISPATCH_TOKEN: __TOKEN__
CANDIDATE_SHA: 9282343c43afada5e50ff2a282a7b36102d3cfc8
BRANCH: feature/dev-107-ship-flow-close-the-close-receipt-refuses-an-undispositioned
BASE_SHA: 8983967357fb457751fa0fbdbcd7965e41fede25
FILES: docs/plan-flow/schema/kc-ship-close-receipt.v1.schema.json,docs/plan-flow/schema/validate-receipt.py,docs/ship-flow/flows/from-dispatch-to-one-slack-message.yaml,scripts/ship-flow/dev-debrief.py,scripts/ship-flow/ship-debrief.py,scripts/fixtures/ship-flow/close-receipt/plan-receipt.json,scripts/fixtures/ship-flow/close-receipt/plan-approval.json,scripts/fixtures/ship-flow/close-receipt/close-receipt.DRAFT.json,scripts/fixtures/ship-flow/close-receipt/close-receipt.dispositioned.json,scripts/fixtures/ship-flow/close-receipt/close-receipt.missing-dev-debrief.json,scripts/fixtures/ship-flow/close-receipt/close-receipt.missing-rounds.json
TESTS: python3 scripts/kc-dev-flow-contract-test.py -> exit 0
SHALLOW_CLONE_TEST: exit 0
SURFACE: docs/plan-flow/schema/kc-ship-close-receipt.v1.schema.json -> AC-1 | grep -q "\"accepted_residual\"" docs/plan-flow/schema/kc-ship-close-receipt.v1.schema.json | git show 8983967357fb457751fa0fbdbcd7965e41fede25:docs/plan-flow/schema/kc-ship-close-receipt.v1.schema.json > docs/plan-flow/schema/kc-ship-close-receipt.v1.schema.json
SURFACE: docs/plan-flow/schema/validate-receipt.py -> AC-1 | grep -q "defects_returned missing fix_ticket or accepted_residual" docs/plan-flow/schema/validate-receipt.py | git show 8983967357fb457751fa0fbdbcd7965e41fede25:docs/plan-flow/schema/validate-receipt.py > docs/plan-flow/schema/validate-receipt.py
SURFACE: docs/ship-flow/flows/from-dispatch-to-one-slack-message.yaml -> AC-5 | grep -q close-receipt-accepts-dispositioned-with-debriefs docs/ship-flow/flows/from-dispatch-to-one-slack-message.yaml | git show 8983967357fb457751fa0fbdbcd7965e41fede25:docs/ship-flow/flows/from-dispatch-to-one-slack-message.yaml > docs/ship-flow/flows/from-dispatch-to-one-slack-message.yaml
SURFACE: scripts/ship-flow/dev-debrief.py -> AC-4 | grep -q candidate_correction scripts/ship-flow/dev-debrief.py | git rm -f scripts/ship-flow/dev-debrief.py
SURFACE: scripts/ship-flow/ship-debrief.py -> AC-4 | grep -q minutes_per_station scripts/ship-flow/ship-debrief.py | git rm -f scripts/ship-flow/ship-debrief.py
WITHOUT_IT_COMMAND: grep -q "defects_returned missing fix_ticket or accepted_residual" docs/plan-flow/schema/validate-receipt.py
WITHOUT_IT_REMOVED_VARIANT: git checkout 8983967357fb457751fa0fbdbcd7965e41fede25 -- docs/plan-flow/schema/validate-receipt.py
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 1; at BASE_SHA -> exit 1
SELF_CHECK: 2026-09-06T02:59:11Z accept-evidence: ACCEPT
BLOCKER: none
