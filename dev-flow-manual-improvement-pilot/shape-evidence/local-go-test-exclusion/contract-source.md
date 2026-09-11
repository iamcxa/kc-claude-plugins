# Pilot Build

Working perspective: product engineer.

## Mission

Implement the accepted journey through its real seams with enough diagnostics
and recovery for bounded use.

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

- runnable integrated slice;
- focused tests for owned logic and seam behavior;
- diagnostics and bounded retry/recovery required by the shape contract.

Stop here on crossing a stop number the shape contract declared. Run scoped
tests while iterating and the relevant integrated checks at exit. Do not add
production lifecycle surfaces or a standing review loop.

At implementation exit, run `kc-dev-flow/scripts/surface-map-check.py` against
the candidate diff and the Evidence block, checking every non-test changed
file.

## Implementation exit observation

```json
{
  "schema": "kc-dev-flow-observation/v1",
  "capability": "review_convergence",
  "mode": "observe",
  "provider": "roborev",
  "trigger": "implementation_exit",
  "reasoning": "medium",
  "minimum_severity": "medium",
  "panel": "none",
  "live_batch_timeout_seconds": 900,
  "request_cap": 1,
  "repair_confirmation_cap": 1
}
```
