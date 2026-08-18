# Production Verify

Working perspective: risk-selected verification owner.

## Mission

Prove the accepted production obligations at the exact revision using the
cheapest instruments that can fail.

## Conditional references

```json
{
  "schema": "kc-dev-flow-conditional-references/v1",
  "references": [
    {
      "path": "../../delivery-branch-base.md",
      "trigger": "delivery_artifact_review",
      "receipt": null
    },
    {
      "path": "../../pr-delivery.md",
      "trigger": "pr_delivery_selected",
      "receipt": null
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

- exact-revision journey and lifecycle evidence;
- required deterministic gate results;
- findings from only the applicable security, privacy, reliability, data, or
  compatibility specialists;
- provider feedback disposition and any material residual risk.

One repair owner may close all findings before one final re-verification. Invoke
Science Officer only for a material contested or high-risk judgment.
