---
name: choose-work-profile
description: Recommend and ask the Captain to choose POC, Pilot, or Production before a work item enters its first working stage, or when an observed promotion trigger makes the committed profile stale.
---

# Choose Work Profile

Select the lifecycle before loading its working contract. The Captain chooses;
this skill has recommendation and question authority only.

## Resolve the choice

Read the exact work item and its `## Work profile receipt`. Reuse an unchanged
`kc-dev-flow-work-profile/v2` receipt. Treat it as stale when audience, lifespan,
valuable state, mutation boundary, authority need, or operational commitment
changes.

An unchanged v1 receipt already records the Captain's profile choice. Return a
mechanical v2 candidate with the same `selected`, current route, basis, and
task-specific obligations; do not ask the Captain to repeat the decision. Ask
again only when its basis is stale or the selected profile no longer contains
the accepted scope.

| Choice | Route | Use when |
|---|---|---|
| `POC / Exploration` (`poc-exploration`) | `build -> prove` | A disposable experiment must prove one real journey and its riskiest assumption. |
| `Pilot / Product slice` (`pilot-product-slice`) | `shape -> build -> verify-deliver` | Limited real use creates persistent value and likely iteration. |
| `Production` (`production`) | `shape -> build -> verify -> release` | The scope accepts a production boundary or long-term operational commitment. |

A POC label cannot downscope production credentials or data, destructive
external mutation, irreversible migration, public compatibility, unattended
operation, broad exposure, SLO/support duty, or release/rollback ownership.

Check the shared core's `backlog` exit bar in the same read. The work item must
already state what it is and why it is worth doing, in the form that core
requires for the profile under consideration. A missing part is a missing fact:
carry it into the question below rather than supplying it.

Derive a recommendation from the task. Ask one clarifying question only when one
missing fact — an incomplete exit bar included — could change the choice or
leave the item unready to leave `backlog`. State the task-specific difference in architecture,
implementation, testing, stages, and delivery. Use the host's best structured
Ask UI when available; plain chat is the fallback. In a non-interactive worker,
return `NEEDS_PROFILE_DECISION` and name the missing fact; never select
automatically and never supply the missing part.

## Return the candidate receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v2
  selected: poc-exploration | pilot-product-slice | production
  recommended: poc-exploration | pilot-product-slice | production
  basis: <audience, lifespan, state, mutation boundary, and commitment>
  route: [<ordered logical working stages>]
  obligations:
    architecture: [<task-specific obligations>]
    implementation: [<task-specific obligations>]
    testing: [<task-specific obligations>]
  scope_boundary: <what this profile excludes>
  promote_when: [<observable task-specific triggers>]
  decision:
    authority: <captain identity or bound authority>
    at: <RFC3339 timestamp>
```

The locally authorized actor re-reads the entity, records the receipt in the
existing work item, syncs it through the existing safe transaction, and re-reads
the committed result. Do not write a sidecar or start a working stage before
that re-read.

## Promotion

Promote POC to Pilot for accepted real users, persistent valuable state, reused
shortcuts, beyond-session operation, or retry/recovery duty. Promote either
lower profile to Production for any production trigger above. Outside profile
selection, stop at the boundary and return `PROFILE_PROMOTION_REQUIRED`; do not
rewrite the receipt or stage.

The profile never grants secrets, permission, spend, destructive action,
irreversibility, red-residual acceptance, merge, release, or closeout authority.
