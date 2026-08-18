# Production Shape

Working perspective: staff engineer and delivery lead.

## Mission

Define the production outcome, architecture and lifecycle ownership, failure
policy, rollout, and release boundary.

## Conditional shape references

```json
{
  "schema": "kc-dev-flow-conditional-references/v1",
  "references": [
    {
      "path": "../../reverse-recovery-audit.md",
      "trigger": "brownfield_capability_change",
      "receipt": "reverse_recovery"
    },
    {
      "path": "../../journey-slicing.md",
      "trigger": "multi_slice_required",
      "receipt": "journey_slices"
    },
    {
      "path": "../../retained-document-policy.md",
      "trigger": "retained_document_change",
      "receipt": null
    },
    {
      "path": "../../project-context-maintenance.md",
      "trigger": "project_context_claim_may_change",
      "receipt": "project_context"
    }
  ]
}
```

## Required output

- accepted journey, constraints, non-goals, and exact owners;
- applicable lifecycle and specialist-risk obligations;
- rollback or forward-recovery policy;
- falsifiable acceptance and release checks.

Stop when the smallest operable route is decision-ready. Escalate scope,
irreversibility, and accepted residual risk to the Captain.
