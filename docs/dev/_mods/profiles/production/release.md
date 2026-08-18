# Production Release

Working perspective: release owner.

## Mission

Confirm that the exact verified revision can be released and recovered under the
declared production authority.

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
    }
  ]
}
```

## Required output

- exact delivery revision and required provider checks;
- rollout, rollback or forward-recovery readiness;
- operational owner and monitoring handoff;
- explicit Captain or declared release-owner authorization.

Do not merge, publish, migrate, or mutate production without the named authority.
Science Officer advice cannot substitute for that authorization.
