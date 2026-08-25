---
name: choose-work-profile
description: Recommend and ask the Captain to choose POC, Pilot, or Production before a work item enters its first working stage, or when an observed promotion trigger makes the committed profile stale.
---

# Choose Work Profile

Select the lifecycle before loading its working contract. The Captain chooses;
this skill has recommendation and question authority only.

## Resolve the choice

Ask first: **Could credible negative evidence cancel or materially change the
next commitment this item asks the Captain to accept?** Yes recommends POC. No
compares Pilot and Production using the existing delivery-risk boundaries.

Read the exact work item and its `## Work profile receipt`. Reuse an unchanged
supported receipt. A v2 Pilot or Production receipt remains supported; an active
v2 POC must finish on its pinned 3.x pair or be Captain re-recorded as v3. Treat
any receipt as stale when audience, lifespan, valuable state, mutation boundary,
authority need, or operational commitment changes.

An unchanged v1 Pilot or Production receipt already records the Captain's
profile choice. Return a mechanical v3 candidate with the same `selected`,
current route, basis, and task-specific obligations. A v1 POC preserves its
profile choice but cannot supply the new experiment contract mechanically: ask
the Captain to complete the v3 POC fields without reopening the profile choice.
Ask for a new selection only when its basis is stale or the selected profile no
longer contains the accepted scope.

| Choice | Route | Use when |
|---|---|---|
| `POC / Exploration` (`poc-exploration`) | `build -> prove` | A disposable experiment must prove one real journey and its riskiest assumption. |
| `Pilot / Product slice` (`pilot-product-slice`) | `shape -> build -> verify-deliver` | Limited real use creates persistent value and likely iteration. |
| `Production` (`production`) | `shape -> build -> verify` | The scope accepts a production boundary or long-term operational commitment. |

A POC label cannot downscope production credentials or data, destructive
external mutation, irreversible migration, a compatibility break that makes a
consumer act, unattended operation, broad exposure, SLO/support duty, or
release/rollback ownership.

The compatibility trigger asks whether a consumer must do something, not whether
the change is published. Recommend Production when an existing consumer cannot
upgrade by taking the new version — it has to run a migration, edit its own
configuration, or rewrite records it owns. If you cannot state that consumers
upgrade without acting, recommend Production; the error that costs more is the
one that sends a migration out on a shorter route.

Check the shared core's `backlog` exit bar in the same read. The work item must
already state what it is, why it is worth doing, and when it is scheduled — an
accepted `sprint` and `sprint-readiness: ready` — in the form that core requires
for the profile under consideration. A missing part is a missing fact: carry it
into the question below rather than supplying it. Scheduling is the iteration
owner's answer, not yours; an item with no accepted iteration is not ready to
leave `backlog` however clear its problem statement is.

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
  schema: kc-dev-flow-work-profile/v3
  selected: poc-exploration | pilot-product-slice | production
  recommended: poc-exploration | pilot-product-slice | production
  basis: <audience, lifespan, state, mutation boundary, and commitment>
  route: [<ordered logical working stages>]
  obligations:
    architecture: [<task-specific obligations>]
    implementation: [<task-specific obligations>]
    testing: [<task-specific obligations>]
  scope_boundary: <what this profile excludes>
  # POC only; omit these fields for Pilot and Production.
  poc_decision: <the next commitment this evidence decides>
  poc_falsifier: <the cheapest credible negative evidence>
  poc_budget: <explicit time, model, provider, or review ceiling>
  poc_stop_when: <observable point at which work stops>
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
