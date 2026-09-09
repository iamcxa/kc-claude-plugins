## Evidence
DISPATCH_TOKEN: dev147-2026-09-09-r2
CANDIDATE_SHA: b3235989f3037b7c1b45036de040a4b892b03686
BRANCH: feature/dev-147-ship-flow-close-receipt-schema-forbids-the-debrief-writers
BASE_SHA: 668510376e157d1ff9f8fc7781c417c0f6b0d719
PR: iamcxa/kc-claude-plugins#397
FILES: docs/plan-flow/schema/validate-receipt.py, docs/plan-flow/schema/close-receipt.test.py, kc-ship-flow/scripts/{dev-debrief,ship-debrief}.py + .test.py, contract-test.py, references/stations/{dev,ship}-debrief.md, skills/first-officer/SKILL.md, fixtures (batch-carried-issue, debrief-writer/batch-carried-probe, close-receipt/*)
TESTS: DEV-147 AC-1 exit 2 "jsonschema required"; AC-2 exit 0 evidence_refusals []; AC-3 contract-test exit 0; DEV-135 AC-1 exit 0 note "not dispatched"; AC-2 mutated outcome exit 2; falsifiers: ab2fb2635f0c-shape CLOSE OK, embedded dev_debrief refused; kc-dev-flow-contract-test exit 0; CI version parity SUCCESS on #397
WITHOUT_IT_COMMAND: python3 -S docs/plan-flow/schema/validate-receipt.py kc-ship-flow/scripts/fixtures/close-receipt/ab2fb2635f0c-shape/plan-receipt.json kc-ship-flow/scripts/fixtures/close-receipt/ab2fb2635f0c-shape/plan-approval.json kc-ship-flow/scripts/fixtures/close-receipt/ab2fb2635f0c-shape/close-receipt.json; test $? -eq 2
WITHOUT_IT_REMOVED_VARIANT: git show 668510376e157d1ff9f8fc7781c417c0f6b0d719:docs/plan-flow/schema/validate-receipt.py > docs/plan-flow/schema/validate-receipt.py
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 1; at BASE_SHA -> exit 1
SELF_CHECK: worker notes — DEV-135's Linear ACs supersede the Brief paraphrase (fixture path, outcome set {carried, captain_stopped, drift}, note field); close-receipt.test.py edited outside the Brief's file list because CI runs it; writer stdout carries a note field the receipt schema forbids (inert: writers no longer embed)
BLOCKER: none

## FO verification at b3235989 (fresh worktree; the first run had no worktree and was discarded)
AC-1 `python3 -S validate-receipt.py <ab2fb2635f0c-shape trio>` exit 2 "jsonschema required"; same trio with jsonschema: CLOSE OK 6f2c2660; AC-2 dev-debrief on batch-carried-issue exit 0 (evidence_refusals present); embedded dev_debrief receipt refused exit 1 (by the validator's own per_issue check, which runs before jsonschema — the schema refusal is second in line); close-receipt.test 0; validator reverted to base → close-receipt.test exit 1; dev-debrief.test 0; ship-debrief.test 0. Comment lines added in python: 5 (one block explaining check ordering; 0.6% of +806).
