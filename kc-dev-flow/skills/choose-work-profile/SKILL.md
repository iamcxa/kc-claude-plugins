---
name: choose-work-profile
description: Recommend and ask the Captain to choose POC, Pilot, or Production before a work item enters its first working stage, or when an observed promotion trigger makes the committed profile stale.
---

# Choose Work Profile

Select the lifecycle before loading its working contract. The Captain chooses;
this skill has recommendation and question authority only.

## Resolve the choice

Read the exact work item and its `## Work profile receipt`. A Pilot or
Production receipt records `semantics_unchanged` at every working stage from
`ideation` onward, not only at `ideation`, making the shape's existing
observable-semantics declaration machine-readable; the loader refuses any of
those stages without it and refuses `validation` without an
`equivalence_instrument` when it was declared `true`. Reuse an unchanged
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

Before the choice, explain the **next commitment**, **unresolved assumption**,
**observable result**, and **included work** in task terms. Future ambition is not
the accepted scope. Repository scaffolding means files exist; it does not prove
the first user journey or define a fourth profile. Distinguish existing
valuable state and consumers from disposable state an experiment may create.
Repository age selects no profile.

If credible negative evidence could change that commitment, consider a disposable
integrated experiment. When the first journey is unproved and you recommend
Production, offer the smallest lower-commitment alternative and name the evidence
or accepted operational duty it cannot cover. Change the recommendation when that
alternative suffices; explicit production-data or recovery duties can still
require Production. Do not require a POC-to-Pilot-to-Production sequence.

| Choice | Route | Use when |
|---|---|---|
| `POC / Exploration` (`poc-exploration`) | `build -> prove` | A disposable experiment must prove one real journey and its riskiest assumption. |
| `Pilot / Product slice` (`pilot-product-slice`) | `shape -> build -> verify-deliver` | Limited real use creates persistent value and likely iteration. |
| `Production` (`production`) | `shape -> build -> verify` by default; eligible recovery uses `build -> verify` | An operated release accepts production boundaries or long-term operational duties. |

After selecting Production, ask one coupled route question only when an exact
known failure has a concrete falsifier and rollback. The Captain may keep the
full route or record recovery with `recovery_failure`, `recovery_falsifier`,
`recovery_rollback`, and `review_risks`; uncertainty keeps the full route.

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

Check the shared core's brief admission bar in the same read. Pilot and
Production require a Development Brief with the problem, accepted outcome,
complete non-goal list, route-back conditions, and one canonical
`## Acceptance criteria` section. Its concrete bullets use unique ascending
`AC-N` identifiers; an evidence-only or dual-section new admission is refused.
Existing admitted prose is not migrated or rewritten. POC
requires the four concrete v3 Exploration Brief fields. A Planning Receipt is
optional: all of `source`, `planning-window`, and `planning-outcome` selects the
provider-backed path; none selects standalone Captain authority; a partial tuple
keeps the item in `backlog`. A local runtime may separately require `sprint` and
`sprint-readiness: ready`, but those fields do not invent or prove provider
scheduling.

Feature and bug labels do not select the route. A clear urgent bug may use a
standalone Development Brief, an uncertain bug may use POC, and a scheduled
feature or bug may carry a Planning Receipt. Choose from uncertainty and the
accepted commitment, not the ticket label.

Ask one clarifying question when a missing fact could change the choice or leave
the item unready for `backlog` exit. Explain the task-specific architecture,
implementation, testing, stages, and delivery. Use the host's structured
Ask UI; plain chat is the fallback. Misunderstanding, no answer, cancellation,
or timeout leaves scope unresolved: do not create a selected receipt or claim
success. A non-interactive worker returns `NEEDS_PROFILE_DECISION` with the missing
fact, without selecting or filling it in.

## Return the candidate receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: poc-exploration | pilot-product-slice | production
  recommended: poc-exploration | pilot-product-slice | production
  basis: <accepted commitment, assumption, result, audience, lifespan, and state>
  route: [<ordered logical working stages>]
  obligations:
    architecture: [<task-specific obligations>]
    implementation: [<task-specific obligations>]
    testing: [<task-specific obligations>]
  scope_boundary: <what this profile excludes>
  # Pilot and Production, every working stage from ideation onward.
  semantics_unchanged: true | false
  # POC only; omit these fields for Pilot and Production.
  poc_decision: <the next commitment this evidence decides>
  poc_falsifier: <the cheapest credible negative evidence>
  poc_budget: <explicit time, model, provider, or review ceiling>
  poc_stop_when: <observable point at which work stops>
  poc_artifact: no-code | disposable | retained
  poc_safety_boundary: none | <named repository safety check>
  poc_decision_ready_minutes: 15
  poc_decision_ready_reason: <required only for a non-15 override>
  # Eligible Production recovery only; omit on the full route.
  recovery_failure: <exact bounded failure>
  recovery_falsifier: <repository-owned command or observable scenario>
  recovery_rollback: <task-specific reversal action>
  review_risks: [none | named closed risks]
  promote_when: [<observable task-specific triggers>]
  decision:
    authority: <captain identity or bound authority>
    at: <RFC3339 timestamp>
```

After the Captain accepts, carry the commitment, assumption, and result into
`basis`, included work into `obligations`, exclusions into `scope_boundary`, and
escalation conditions into `promote_when`; add no receipt key. Preserve an existing
receipt while scope is unresolved. The locally authorized actor re-reads the
entity, records the accepted receipt there, syncs it through the existing safe
transaction, and re-reads the committed result. Do not write a sidecar or start a working stage before
that re-read. Returning a recovery item to the full route requires a new Captain
decision unless its recorded rollback explicitly grants that exact rewrite.

## Promotion

Promote POC to Pilot for accepted real users, persistent valuable state, reused
shortcuts, beyond-session operation, or retry/recovery duty. Promote either
lower profile to Production for any production trigger above. Outside profile
selection, stop at the boundary and return `PROFILE_PROMOTION_REQUIRED`; do not
rewrite the receipt or stage.

The profile never grants secrets, permission, spend, destructive action,
irreversibility, red-residual acceptance, merge, release, or closeout authority.
