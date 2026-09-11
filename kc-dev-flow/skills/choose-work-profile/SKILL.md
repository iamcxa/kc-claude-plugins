---
name: choose-work-profile
description: Recommend and ask the Captain to choose POC, Pilot, or Production before a work item enters its first working stage, or when an observed promotion trigger makes the committed profile stale.
---

# Choose Work Profile

Select the lifecycle before loading its working contract. The Captain chooses;
this skill has recommendation and question authority only.

## Resolve the choice

Read the exact work item and its `## Work profile receipt`. A receipt is stale
when audience, lifespan, valuable state, mutation boundary, authority need, or
operational commitment changes. Use the first applicable path:

1. **Recorded unchanged choice:** With no change requested, reuse the supported
   receipt and stop selection. v2 Pilot/Production is supported; active v2 POC
   finishes on its pinned 3.x pair or is Captain re-recorded as v3. For unchanged v1
   Pilot/Production, return a mechanical v3 candidate preserving `selected`,
   current route, basis and obligations. For v1 POC, keep the choice and ask
   only for missing v3 experiment fields.
2. **Supplied acceptance:** Without a reusable receipt, keep a valid
   supplied profile/route. Explain below, return the candidate from that answer,
   not a reconstructed conversation.
3. **Unaccepted recommendation:** Explain below as a proposal, then ask for the
   choice. This includes a stale basis or profile that no longer contains the
   scope, without valid acceptance.

## Explain and resolve

Explain the **next commitment**, **unresolved assumption**,
**observable result**, and **included work** from task facts and stated evidence
gaps; do not invent assumptions. Label unaccepted
commitments as proposals; future ambition is not accepted scope. Scaffolding
means files, not a proved journey or fourth profile. Distinguish existing
valuable state and consumers from disposable state an experiment may create.
Repository age selects no profile.

For an unproved journey, explain both, including after acceptance:

- **Smallest experiment:** concrete actions through the same end-to-end journey
  on disposable inputs, and observable result.
- **Coverage limit:** the evidence or accepted duty that experiment cannot cover.

The comparison explains scope, without replacing supplied acceptance.
Before acceptance, recommend the experiment if credible negative evidence could
change the commitment. No profile sequence is required.

| Choice | Route | Use when |
|---|---|---|
| `POC / Exploration` (`poc-exploration`) | `build -> prove` | A disposable experiment must prove one real journey and its riskiest assumption. |
| `Pilot / Product slice` (`pilot-product-slice`) | `shape -> build -> verify-deliver` | Limited real use creates persistent value and likely iteration. |
| `Production` (`production`) | `shape -> build -> verify` by default; eligible recovery uses `build -> verify` | An operated release accepts production boundaries or long-term operational duties. |

A POC label cannot downscope production credentials or data, destructive
external mutation, irreversible migration, a compatibility break that makes a
consumer act, unattended operation, broad exposure, SLO/support duty, or
release/rollback ownership.

Compatibility means a consumer must migrate, edit configuration, or rewrite
owned records to upgrade; publication alone is not that trigger. Unless you can
state that consumers upgrade by taking the version without acting, recommend Production.

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

Feature/bug labels do not select routes: a clear urgent bug may use a standalone
Development Brief, an uncertain bug POC, and a scheduled item a Planning Receipt.

Only the unaccepted path requests a profile choice. Ask one clarifying question
if a missing fact could change the choice or block
`backlog` exit. Explain task-specific architecture, implementation, testing,
stages, and delivery. Use the host's structured Ask UI, or plain chat if
unavailable. Misunderstanding, no answer, cancellation, or timeout leaves scope
unresolved: do not create a selected receipt or claim success. Non-interactive
workers return `NEEDS_PROFILE_DECISION` with the missing fact, without filling it in.

For Production with no supplied route, ask one coupled route question only when
an exact known failure has a concrete falsifier and rollback. The Captain may
keep the full route or record recovery with `recovery_failure`,
`recovery_falsifier`, `recovery_rollback`, and `review_risks`; uncertainty keeps
the full route.

## Return the candidate receipt

Use the actual Captain answer. A candidate with
unknown facts is not ready to record. Pilot/Production receipts copy shape's
observable-semantics declaration into `semantics_unchanged` from `ideation`.
The loader refuses a missing value and `validation` without an
`equivalence_instrument` when true.

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
  scope_boundary: <accepted limits, or positive accepted scope if none>
  # Pilot/Production: required from ideation.
  semantics_unchanged: <work's declared true | false; omit if unknown>
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
    at: <supplied or clock-read RFC3339 time; omit if unknown> # label capture here
```

After the Captain accepts, put commitment, assumption, and result into `basis`,
included work into `obligations`, scope into `scope_boundary`, and escalation
conditions into `promote_when`; add no receipt key. Without accepted exclusions,
describe accepted work; proposed restrictions stay outside the receipt.
Preserve an existing receipt while scope is unresolved. Before a working stage,
the locally authorized actor re-reads the entity, records the accepted receipt
via the existing safe transaction and re-reads the committed result. No sidecar.
Return recovery to the full route only with a new Captain decision or its
recorded rollback's exact rewrite grant.

## Promotion

Promote POC to Pilot for accepted real users, persistent valuable state, reused
shortcuts, beyond-session operation, or retry/recovery duty. Promote either
lower profile to Production for any production trigger above. Outside profile
selection, stop at the boundary and return `PROFILE_PROMOTION_REQUIRED`; do not
rewrite the receipt or stage.

The profile never grants secrets, permission, spend, destructive action,
irreversibility, red-residual acceptance, merge, release, or closeout authority.
