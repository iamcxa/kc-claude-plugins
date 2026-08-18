# POC Build

Working perspective: incubation engineer.

## Mission

Build the smallest end-to-end path that can answer the experiment's question.

## Conditional references

```json
{
  "schema": "kc-dev-flow-conditional-references/v1",
  "references": [
    {
      "path": "../../roborev-implementation-exit.md",
      "trigger": "implementation_exit_observation_declared",
      "receipt": null
    },
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
      "path": "../../reverse-recovery-audit.md",
      "trigger": "brownfield_capability_change",
      "receipt": "reverse_recovery"
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

- one runnable integrated artifact;
- focused checks for owned logic and the riskiest assumption;
- no unrelated structure, abstraction, or test surface.

Stop when the journey can be exercised. Do not open a reviewer loop or improve
production qualities outside the selected boundary.

## Implementation exit observation

```json
{
  "schema": "kc-dev-flow-observation/v1",
  "capability": "review_convergence",
  "mode": "observe",
  "provider": "roborev",
  "trigger": "implementation_exit",
  "reasoning": "medium",
  "minimum_severity": "high",
  "panel": "none",
  "live_batch_timeout_seconds": 600,
  "request_cap": 1,
  "repair_confirmation_cap": 0
}
```
