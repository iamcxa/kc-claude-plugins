---
name: choose-work-profile
description: Use when an ideation-stage work item has no valid work-profile receipt or its audience, lifespan, mutation boundary, authority need, or operational commitment has changed.
---

# Choose Work Profile

## Overview

Recommend a proportional proof burden before acceptance criteria expand. The
Captain chooses; this skill has recommendation and question authority only.

## Inputs and activation

Use the already-bound project context and exact work-item body. Do not discover
or create another tracker. Re-read the exact work item and its
`## Work profile receipt`.

- If the receipt is valid and its basis is unchanged, return it to the ideation
  actor without another question or full re-selection.
- Treat it as stale when the audience, lifespan, mutation boundary, authority
  need, or operational commitment changed.
- Do not retroactively apply this gate after ideation. Tasks already beyond
  ideation are not reopened without an observed promotion trigger.
- Do not add this gate to the bounded mechanical-defect route that validly skips
  ideation.

## Profiles

Profiles select burden of proof, not implementation language. Shell, CLI,
off-the-shelf tools, libraries, and existing repository mechanisms remain valid
when they satisfy the selected obligations.

| Label | Receipt value | Choose when | Proof floor |
|---|---|---|---|
| `POC / Exploration` | `poc-exploration` | A disposable experiment must prove one real journey and its riskiest assumption. | Test owned logic and the critical risk, exercise one real end-to-end journey, name cleanup, and record what remains unproved. |
| `Pilot / Product slice` | `pilot-product-slice` | Limited real use creates persistent value and likely iteration. | Add diagnostics, retry/recovery, data safety, real seam tests, and the accepted end-to-end journey without hypothetical scale. |
| `Production` | `production` | The scope accepts long-term operational commitment or a production boundary. | Retain applicable lifecycle, compatibility, migration/recovery, observability, integrity, rollback, release, and ownership proof. |

A task labeled POC does not downscope a production credential, production data,
destructive external mutation, irreversible migration, compatibility promise,
unattended recurring operation, broad exposure, SLO/support duty, or
release/rollback obligation. Recommend `production` until an explicit safe
non-production scope boundary removes the trigger.

## Recommend and ask

1. Derive a recommendation from the bound audience, lifespan, state ownership,
   mutation boundary, authority need, and operational commitment. Ask one
   clarifying question first only when one missing fact could change it.
2. State the recommendation and the exact architecture, implementation, testing,
   scope, and proof delta among the three profiles. Ask one focused question; do
   not run a generic questionnaire.
3. Use the host's best structured question capability when available. Prefer a
   host-specific structured surface, then another native structured surface. Do
   not couple the contract to a tool name.
4. When no structured surface is available, ask the same three-choice decision
   as one concise plain-chat question and wait.
5. In a non-interactive worker, return the recommendation, exact delta, and
   `NEEDS_PROFILE_DECISION` to the user-facing parent. Do not auto-select.

The question event carries the exact prompt plus these three ordered choices.
Each choice includes its label, closed receipt value, and task-specific
consequence: `POC / Exploration` / `poc-exploration`, `Pilot / Product slice` /
`pilot-product-slice`, and `Production` / `production`. The host or user-facing
parent records the actual structured surface or plain-chat payload and its
evidence reference before forwarding the Captain's answer. A later summary that
only says a question was asked is not interaction evidence.

## Return the candidate receipt

Return this payload to the actor already authorized by the Local Profile and
current dispatch to mutate the work-item body. Instantiate task-specific
obligations; do not paste a global checklist.

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v1
  selected: poc-exploration | pilot-product-slice | production
  recommended: poc-exploration | pilot-product-slice | production
  basis: <audience, lifespan, state, mutation boundary, and operational commitment>
  obligations:
    architecture: [<selected task-specific obligations>]
    implementation: [<selected task-specific obligations>]
    testing: [<selected task-specific obligations>]
  invariant_sources: [<governing local safety, authority, evidence, and cleanup locators>]
  scope_boundary: <what the selected profile excludes>
  promote_when: [<observable task-specific triggers>]
  decision:
    authority: <captain identity or bound authority>
    at: <RFC3339 timestamp>
```

The authorized actor stores it under `## Work profile receipt` in the existing
work-item body. Before writing, that actor re-reads the exact entity and compares
its identity, scope basis, and prior receipt with the decision input. On mismatch,
discard the answer and restart selection. Commit through the repository's safe,
path-scoped work-item transaction, sync it, and re-read the committed receipt.
If work-item authority supplies no safe mutation path, return `UNKNOWN`.
Do not write a sidecar.

The actor returns authoritative transaction facts to the ideation caller: exact
work-item identity and path, authority source, actor identity, pre-write
revision, the path-scoped committed revision and changed-path set, sync result,
committed and re-read work-item digests, the re-read receipt, and an evidence
reference. The caller verifies that the committed and re-read revisions,
digests, and receipt match before deriving. Model-authored fields that merely
claim `recorded` or `re-read` are not evidence. If the runtime cannot expose any
required fact, return `UNKNOWN` and do not derive acceptance criteria.

Only after the committed receipt is re-read may inherited criteria be normalized
or acceptance criteria be expanded.

## Invariants and promotion

The selected profile cannot authorize secrets, permissions, spend, destructive
actions, production data, external mutations, irreversibility, red residual
acceptance, merge, or closeout. Preserve the governing safety, authority,
evidence honesty, cleanup, exact-revision delivery, and four-state receipt
requirements in every profile.

Default promotion triggers are:

- `poc-exploration` to `pilot-product-slice`: a limited real user, persistent
  valuable state, beyond-session operation, retry/recovery duty, or a reused
  shortcut enters accepted scope.
- Either lower profile to `production`: production credentials/data, external
  production mutation, irreversible migration, public compatibility, unattended
  recurring operation, broad exposure, SLO/support, or release/rollback enters
  accepted scope.

Outside ideation, do not rewrite the receipt or stage. Return
`PROFILE_PROMOTION_REQUIRED` with the stale basis and observed trigger to the
bound execution-state owner. That owner performs the existing transition to
ideation and dispatches the authorized mutation actor; this skill gains no stage
transition authority. The handoff evidence names the detecting worker,
execution-state owner, authorized mutation actor, stale receipt revision,
ideation transition, replacement committed receipt revision, and the ordering
from detection through committed re-read. Replacement acceptance criteria are
derived only after that sequence completes.

## Example

For a one-session script that converts a local fixture and deletes its temporary
output, recommend `POC / Exploration`: keep the script and input fixture as the
implementation surface; test owned parsing and the risky conversion; run the
real CLI journey; name cleanup and unproved scale. Present Pilot's persistence,
diagnostics, and retry delta and Production's lifecycle/release delta, then ask
the Captain to choose among the same three labels.

## Quick reference

| Situation | Result |
|---|---|
| Valid unchanged receipt | Return it; do not ask again. |
| Missing or stale receipt in ideation | Recommend, ask, return a candidate receipt. |
| No interactive surface | Return `NEEDS_PROFILE_DECISION`. |
| Unsafe or ambiguous write path | Return `UNKNOWN`; create no sidecar. |
| Promotion trigger outside ideation | Return `PROFILE_PROMOTION_REQUIRED`. |

## Common mistakes

- Treating a POC label as authority to cross a production boundary.
- Copying the full profile checklist instead of instantiating task-specific
  obligations and exclusions.
- Writing ACs before the authorized actor re-reads the committed receipt.
- Choosing automatically because the recommendation is high confidence.
- Creating a profile tracker, stage, daemon, or execution-state record.
