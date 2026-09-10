---
commissioned-by: spacedock@0.25.0
entity-type: batch
entity-label: batch
entity-label-plural: batches
id-style: sd-b32
state: .spacedock-state
trunk: main
stages:
  defaults:
    worktree: false
    concurrency: 2
  states:
    - name: dispatched
      initial: true
    - name: watching
    - name: verified
    - name: uat
      gate: true
    - name: closed
      terminal: true
---

# kc-ship-flow batch workflow

Ship is a wrapper over kc-dev-flow and Spacedock: it bundles the batch's dev tasks, dispatches one
Conductor cloud workspace + First Officer per task, watches them to a prepared `validation` gate,
verifies the integrated head, hands the Captain a UAT, and closes once every worker's debrief is
pushed. Anything kc-dev-flow or Spacedock already does per task (acceptance, PR review, merge,
debrief) is not repeated here — see
`docs/superpowers/specs/2026-09-10-ship-flow-cloud-wrapper-design.md` for the discriminator and the
full removal rationale (DEV-157, `ship-remove-duplicated-stations`). This workflow replaces the
hand-built batch records under `docs/dev/.spacedock-state/batch-*/` (the station chain that ran in
the First Officer's head for batch `e56e9f09`) with one commissioned Spacedock entity per batch,
moving through `dispatched -> watching -> verified -> uat -> closed`.

<!-- kc-ship-flow-static-local-profile:start -->
## Local Profile

This table is the first-officer skill's declared input before dispatching a batch, not the full README as a policy bundle. `kc-ship-flow/scripts/local-profile-check.py` verifies the table's required rows; nothing checks what else the skill reads.

| Role | Bound local authority |
|---|---|
| Holder | State-holder identity written to `.spacedock-state`'s `_holder.json` by `spacedock state commit` |
| Runtime | Local subagent or Conductor cloud |
| Planning provider | Linear `duckbase-co` via `kc-plan-receipt/v1` |
| UAT delivery | Subspace `/r` |
| Approval defaults | `receipt/plan-approval.json` in the batch dir |
| E2E flows | `docs/ship/flows/` |
| Pin | `kc-ship-flow/scripts/pin.py` record per batch |
| Installed contract interface | `kc-ship-flow-batch-pin/v1` |
<!-- kc-ship-flow-static-local-profile:end -->

## Stages

Each stage's Spacedock pin (`kc-ship-flow/scripts/pin.py write --station <name>`) records the
plugin version and contract digest reached at that stage; the lines below name the station's own
enforcing script.

### `dispatched` — one workspace + FO per task

Script: `kc-ship-flow/scripts/fenced-dispatch.sh` dispatches a dev entity's stage into its
Conductor cloud workspace (station: `kc-ship-flow/references/stations/fenced-dispatch.md`); the
claim fence (`intent.sh`/`holder.sh`) guards the workspace-create call it makes.

### `watching` — poll until every task is at `validation` with a gate prepared

Primary signal is the state branch (`spacedock status --workflow-dir docs/dev --where
sprint=<value>`), not the transcript; secondary signal is `conductor --json session status <id>`.
A dedicated `dispatch-and-watch` script pair lands this stage's own enforcing script; until then
the First Officer runs this poll by hand per the design's exit-condition table.

### `verified` — e2e at the integrated head

Script: `kc-ship-flow/scripts/e2e-gate.py` (runs `kc-ship-flow/scripts/e2e-cli.sh` at the resolved
head; stations: `kc-ship-flow/references/stations/e2e-gate.md`,
`kc-ship-flow/references/stations/e2e-cli.md`)

### `uat` (gate) — UAT doc handed to the Captain

Script: `kc-ship-flow/scripts/uat-doc.py` (station: `kc-ship-flow/references/stations/uat-doc.md`)
reads the batch record and the dev entities and writes one document; the Captain records the gate
decision per task and merges. Acceptance is dev flow's own validation gate; review is `kc-pr-review`
inside the cloud FO's own validation stage; merge is the Captain's, recorded by Spacedock's
`pr-merge` mod — none of those are kc-ship-flow's own script anymore.

### `closed` — debriefs pushed, close receipt written

Each cloud worker runs its own `spacedock debrief` after its PR merges and pushes it path-scoped
under `_debriefs/` on the state branch; a close-receipt writer records the batch's close receipt
once every task shows a merged PR and a pushed debrief. That writer is a separate task's
deliverable (`ship-verify-uat-close`); until it lands the First Officer assembles the close receipt
by hand from the close-receipt schema (`kc-ship-flow/schemas/kc-ship-close-receipt.v1.schema.json`).
