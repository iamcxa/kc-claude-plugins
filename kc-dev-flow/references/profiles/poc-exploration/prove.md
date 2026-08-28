# POC Prove

Working perspective: experiment owner.

## Mission

Exercise the real journey and decide whether the experiment answered its stated
question.

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

Record one `poc_outcome`: direction `proceed`, `stop`, or `change`, exact
evidence, strongest limit, reversal fact, and cleanup. Return it to planning
after terminalization; it grants no downstream creation or profile authority.

- observed journey result and artifact revision;
- result of the critical-risk check;
- cleanup status;
- unproved limits and any promotion trigger.

Pass when the journey and critical assumption are observed. Do not turn
production hardening ideas into POC findings.
