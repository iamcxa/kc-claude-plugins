# Pilot Verify and Deliver

Working perspective: integration and delivery owner.

## Mission

Exercise the accepted journey through real seams, confirm bounded recovery and
data safety, and deliver it through the repository's declared authority.

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

- exact-revision journey evidence;
- retry/recovery, duplicate, diagnostic, and data-safety results that apply;
- provider feedback disposition when a delivery artifact exists;
- remaining production obligations and promotion triggers.

Use one bounded repair loop for material failures. Do not require production
release or operational evidence that the Pilot did not accept.
