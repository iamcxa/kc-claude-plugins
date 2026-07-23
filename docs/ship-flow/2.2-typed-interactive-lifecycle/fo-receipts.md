# FO Receipts

## fo-20260723T062111Z-verify-proceed-auto-advance

```yaml receipt
receipt_id: fo-20260723T062111Z-verify-proceed-auto-advance
created_at: "2026-07-23T06:21:11Z"
actor: "first-officer"
transition:
  from: verify
  to: verify
  trigger: verify-proceed-auto-advance
decision: self-approved
verdict: PROCEED
rule_source: plugins/ship-flow/skills/ship-verify/SKILL.md
evidence:
  verify_artifact: verify.md
  claim_records: "required VERIFIED=5 NOT VERIFIED=0 INCONCLUSIVE=0"
  cross_review_verdict: PROCEED
preconditions:
  - name: verify.md exists and has status passed
    status: pass
  - name: required claims verified
    status: pass
  - name: independent adversarial probes permit advance
    status: pass
blocker_scan:
  missing_verify_md: none
  missing_hand_off_to_review: none
  required_not_verified: none
  invalid_required_inconclusive: none
  veto: none
  prompt_captain_required: false
open_decisions: []
next_action: "dispatch review stage"

```

## fo-20260723T064233Z-verify-proceed-auto-advance

```yaml receipt
receipt_id: fo-20260723T064233Z-verify-proceed-auto-advance
created_at: "2026-07-23T06:42:33Z"
actor: "first-officer"
transition:
  from: verify
  to: verify
  trigger: verify-proceed-auto-advance
decision: self-approved
verdict: PROCEED
rule_source: plugins/ship-flow/skills/ship-verify/SKILL.md
evidence:
  verify_artifact: verify.md
  claim_records: "required VERIFIED=6 NOT VERIFIED=0 INCONCLUSIVE=0"
  cross_review_verdict: PROCEED
preconditions:
  - name: round-four verify.md has status passed
    status: pass
  - name: confirmed blocker precedence is independently verified
    status: pass
  - name: required claims verified
    status: pass
blocker_scan:
  missing_verify_md: none
  missing_hand_off_to_review: none
  required_not_verified: none
  invalid_required_inconclusive: none
  veto: none
  prompt_captain_required: false
open_decisions: []
next_action: "dispatch final review rerun"

```
