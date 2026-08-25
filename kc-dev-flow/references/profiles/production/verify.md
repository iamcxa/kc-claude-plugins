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
- review disposition: deterministic-only with reason, applicable named
  specialist, or one bounded Science Officer question; model identity alone
  neither triggers nor satisfies review;
- findings from only the applicable security, privacy, reliability, data, or
  compatibility specialists;
- provider feedback disposition and any material residual risk;
- rollout, rollback, or forward-recovery readiness for the exact delivery
  revision;
- operational owner and monitoring handoff;
- explicit Captain-or-declared-release-owner authorization for the exact
  delivery revision.

One repair owner may close all findings before one final re-verification. Invoke
Science Officer only for a material contested or high-risk judgment; Science
Officer advice cannot substitute for release authorization.

This gate's approval targets the terminal `done` stage: `gate record --consume`
leaves it pending (`route=approved-awaiting-merge`) rather than landing
anywhere, and `spacedock merge guard <slug> --verdict passed|rejected` is the
sole terminal consumer — it refuses to finalize without that pending approval.
Do not merge, publish, migrate, or mutate production without the named
authority recorded in this gate's resolution before that approval exists.
