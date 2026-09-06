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
    - name: accepted
    - name: reviewed
    - name: uat
      gate: true
    - name: merged
    - name: closed
      terminal: true
---

# kc-ship-flow batch workflow

This workflow replaces the hand-built batch records under `docs/dev/.spacedock-state/batch-*/`
(the station chain that ran in the First Officer's head for batch `e56e9f09`) with one commissioned
Spacedock entity per batch, moving through `dispatched -> accepted -> reviewed -> uat -> merged ->
closed`.

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

### `dispatched` — kick off the batch

Script: `kc-ship-flow/scripts/fenced-dispatch.sh`
(station: `kc-ship-flow/references/stations/fenced-dispatch.md`)

### `accepted` — accept a worker's Evidence block

Script: `kc-ship-flow/scripts/accept-evidence.sh`
(station: `kc-ship-flow/references/stations/accept-evidence.md`)

### `reviewed` — Draft PR and disposition

Scripts: `kc-ship-flow/scripts/open-pr.sh` (opens the Draft PR before the `kc-pr-review` session;
station: `kc-ship-flow/references/stations/open-pr.md`),
`kc-ship-flow/scripts/disposition.py` (dispositions that session's findings after it;
station: `kc-ship-flow/references/stations/disposition.md`)

### `uat` — e2e gate and UAT handoff

Scripts: `kc-ship-flow/scripts/e2e-gate.py` (runs `kc-ship-flow/scripts/e2e-cli.sh` at the resolved
head; stations: `kc-ship-flow/references/stations/e2e-gate.md`,
`kc-ship-flow/references/stations/e2e-cli.md`), `kc-ship-flow/scripts/uat-doc.py` (writes the UAT
document; station: `kc-ship-flow/references/stations/uat-doc.md`), `kc-ship-flow/scripts/notify.sh`
(sends the UAT-ready message; station: `kc-ship-flow/references/stations/notify.md`)

### `merged` — GitHub merge observed

No kc-ship-flow script is dispatched here; the reconciled GitHub merge is observed through
Spacedock's own `pr-merge` mod.

### `closed` — debrief and close receipt

Scripts: `kc-ship-flow/scripts/dev-debrief.py`
(station: `kc-ship-flow/references/stations/dev-debrief.md`), `kc-ship-flow/scripts/ship-debrief.py`
(station: `kc-ship-flow/references/stations/ship-debrief.md`)
