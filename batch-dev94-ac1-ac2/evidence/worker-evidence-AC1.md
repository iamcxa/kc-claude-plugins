## Evidence
DISPATCH_TOKEN: __TOKEN__
CANDIDATE_SHA: 14932d5a57701addac5f49bc5768092b1076614a
BRANCH: feature/dev-94-ac1-approval-defaults-block
BASE_SHA: 13c31d1
FILES: docs/plan-flow/schema/kc-plan-approval.v1.schema.json, docs/plan-flow/schema/kc-plan-receipt.v1.schema.json, docs/plan-flow/schema/validate-receipt.py
TESTS: python3 scripts/kc-dev-flow-contract-test.py -> exit 0

SURFACE: 
- docs/plan-flow/schema/kc-plan-approval.v1.schema.json -> AC-1 | grep '"required":.*"defaults"' docs/plan-flow/schema/kc-plan-approval.v1.schema.json | grep "additionalProperties.*false" | proof the schema enforces defaults block with exactly six named fields, no additional properties
- docs/plan-flow/schema/validate-receipt.py -> AC-2 | grep -A3 'if "defaults" not in a:' docs/plan-flow/schema/validate-receipt.py | proof validator names specific missing field for each mutant
- validate-receipt.py structural checks path (lines 53-59) | remove these lines and all 7 mutants would exit 0 incorrectly

WITHOUT_IT_COMMAND: python3 docs/plan-flow/schema/validate-receipt.py /tmp/plan-receipt.json /tmp/mutant_no_defaults_block.json

WITHOUT_IT_REMOVED_VARIANT: delete lines 46-59 from validate-receipt.py (the entire approval validation block in the no-jsonschema path), remove "defaults" from line 8 of kc-plan-approval.v1.schema.json required array, and remove lines 20-39 (the entire defaults property definition)

WITHOUT_IT_OBSERVED: retained -> exit 1 (INVALID: defaults block is required); removed -> exit 0 (would incorrectly accept approval without defaults)

MUTANTS:
1. no_defaults_block | exit: 1 | message: INVALID: defaults block is required
2. missing_findings_outside_brief | exit: 1 | message: INVALID: defaults block missing required field: findings_outside_brief
3. missing_minimal_necessity_fail | exit: 1 | message: INVALID: defaults block missing required field: minimal_necessity_fail
4. missing_moved_base | exit: 1 | message: INVALID: defaults block missing required field: moved_base
5. missing_worker_blocker | exit: 1 | message: INVALID: defaults block missing required field: worker_blocker
6. missing_empty_reviewer | exit: 1 | message: INVALID: defaults block missing required field: empty_reviewer
7. missing_pr_creation | exit: 1 | message: INVALID: defaults block missing required field: pr_creation

JSONSCHEMA: absent (validator runs structural-checks path; both jsonschema and non-jsonschema paths validated)

AC-3: note: jsonschema not installed; structural checks only
OK 1016352e02231945 3 issues 3 edges
(exit 0 — batch 1016352e0223 approval amended with conforming defaults validates against receipt)

BLOCKER: none
```