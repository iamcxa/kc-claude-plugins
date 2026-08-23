---
name: project-context-maintenance
description: "Portable stage obligations that keep authoritative product and architecture context aligned with approved delivered behavior"
version: 0.1.0
---

# Project Context Maintenance

## Why this exists

Project context is the stable explanation of what a product is, how it is shaped,
and which constraints must survive individual tasks. Work-item state explains what
is being changed now. Both can be correct in isolation while drifting apart: code
lands a new public contract, the task closes, and the next worker still plans from an
obsolete product or architecture description.

The kernel should require coherent authority without knowing a repository's document
names. The workflow README should bind local authority without re-implementing a
portable update procedure. Launchers should load policy, not contain product-specific
documentation logic. This mod owns the small stage obligation between those layers.

## Rule

**Every approved task classifies its effect on the bound project context. When the
task changes a described product behavior, architecture boundary, public contract,
scope decision, or durable constraint, the approved context change lands in the same
delivery slice and fresh validation checks the changed claim against the delivered
behavior.**

Use one of two classifications:

- `none` — the task changes no claim made by the bound project context. Name the
  relevant described surface or explain why none is involved.
- `update` — name the bound authority, the routed claim locator that becomes stale,
  and the replacement claim already authorized by the task.

The classification is not permission to change product direction. Scope and
irreversible decisions remain with their existing authority.

## Inputs

- The repository's single bound `project_context` locator.
- The affected claim locator, when the bound authority explicitly routes to a deeper
  document.
- The approved work item, including its affected behavior and contract boundary.
- Any product or architecture ruling the work item already cites.

If the repository has not bound a project-context authority, this mod is not ready to
run. Binding the existing authority comes first; creating a new context document is
not the fallback.

## Stage obligations

| Stage | Obligation |
|---|---|
| `backlog` | None. A cheap seed does not perform context analysis. |
| `shape` / runtime `ideation` | Record `none` or `update`. Name the described surface or routed claim, the approved replacement when applicable, and the check that will validate the classification. |
| `build` / runtime `implementation` | Apply the approved context change with the behavior. A selected route without `shape` performs the same classification before its first edit and may document only the already-approved change. If the stale claim extends beyond that scope, record it and return the slice to the task's approving authority for reclassification instead of inventing a replacement. |
| `prove`, `verify-deliver`, or `verify` / runtime `validation` | Execute the recorded `planned_check` against fresh behavior or runtime evidence. For `update`, check the landed context claim against the delivered behavior. For `none`, confirm that the delivered behavior changes no claim in the bound authority, starting from the named surface and not limited to it. Presence of changed prose is not proof. Record the evidence or return the slice when the authority remains stale or contradicts delivery. |
| `done` | No new analysis. For every classification, the existing receipt must contain fresh `validation_evidence`; for `update`, it must also point to the landed context change. |

Repositories may store the receipt in the work item or stage report. This mod does not
prescribe a filename, provider, or extra state store.

## Receipt

```yaml
project_context:
  impact: none | update
  authority: <single bound locator>
  claim_locator: <routed claim locator or none>
  surface: <described surface or none>
  stale_claim: <claim or none>
  approved_change: <replacement claim or none>
  landed_change: <pending | landed change reference | none>
  planned_check: <check able to falsify none or update>
  validation_evidence: <pending | fresh validation reference>
```

For `none`, `stale_claim`, `approved_change`, and `landed_change` are `none`;
`surface` names what must remain unchanged or is `none` when the planned check proves
that no described surface is involved. For `update`, implementation replaces the
pending `landed_change` with a reference inside the bound authority. For both
classifications, validation executes `planned_check` and replaces pending
`validation_evidence` with evidence that can fail.

## Ownership

- Product and architecture owners authorize changed claims.
- The implementation worker updates only claims already changed by approved scope.
- A fresh validator checks correspondence; it does not finish missing product work or
  invent the intended documentation.
- The project-context authority remains the source of truth. This receipt records the
  maintenance result and never becomes a competing context document.

## Non-goals

- No automatic rewriting, generated prose, watcher, lifecycle hook, or background
  job. The responsible stage worker or validator writes each field.
- No mandatory filename, document format, tracker, or documentation site.
- No second product-context document, decision ledger, or mirrored task state.
- No general documentation refresh unrelated to the approved behavior change.
- No authority to create a task, schedule work, expand scope, or pause delivery beyond
  the workflow's existing validation verdict and stage-return mechanism.

Automation may be proposed later only after repeated measured drift shows that the
stage obligation is insufficient. Adoption of this v1 mod does not authorize it.

## Adoption

1. Confirm the repository has bound `project_context` under the
   `kernel.md` Authority model.
2. Vendor this file under the workflow's `_mods/` directory.
3. Add its local path to each profile's applicable shape, build, and verification
   stage as a typed conditional reference. Bind
   `project_context_claim_may_change`; do not load the file when that trigger is
   false.
4. Exercise one `none` task and one `update` task before proposing automation.
