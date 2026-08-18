# Production Build

Working perspective: senior software engineer.

## Mission

Build the smallest operable slice and its accepted lifecycle behavior.

## Conditional references

```json
{
  "schema": "kc-dev-flow-conditional-references/v1",
  "references": [
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

- integrated production path;
- focused tests for owned logic, real seams, failure and recovery behavior;
- observability, compatibility, migration, integrity, and rollback work selected
  during shape;
- changed-file-to-obligation mapping.

Use scoped iteration checks and one relevant exit suite. Return changed premises
to their owner; do not start an unbounded reviewer loop.

## Implementation exit observation

```json
{
  "schema": "kc-dev-flow-observation/v1",
  "capability": "review_convergence",
  "mode": "observe",
  "provider": "roborev",
  "trigger": "implementation_exit",
  "reasoning": "thorough",
  "minimum_severity": "medium",
  "panel": "none",
  "live_batch_timeout_seconds": 1200,
  "request_cap": 1,
  "repair_confirmation_cap": 1
}
```
