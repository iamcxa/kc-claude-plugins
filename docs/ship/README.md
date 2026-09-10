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

kc-ship-flow is a thin wrapper over kc-dev-flow: it bundles the `docs/dev` tasks sharing one
`sprint` value, sends each to its own Conductor cloud first officer, watches the set to a prepared
`validation` gate, verifies at the integrated head, and hands the Captain one UAT. Anything a task
already does per-task belongs to dev flow or Spacedock, not here; see
`docs/superpowers/specs/2026-09-10-ship-flow-cloud-wrapper-design.md` for the full design and the
ruling it implements. The batch moves through `dispatched -> watching -> verified -> uat -> closed`.

<!-- kc-ship-flow-static-local-profile:start -->
## Local Profile

This table is the first-officer skill's declared input before dispatching a batch, not the full README as a policy bundle. `kc-ship-flow/scripts/local-profile-check.py` verifies the table's required rows; nothing checks what else the skill reads.

| Role | Bound local authority |
|---|---|
| Holder | State-holder identity written to `.spacedock-state`'s `_holder.json` by `spacedock state commit` |
| Runtime | Conductor cloud (the design's premise: if Conductor cloud cannot run, ship cannot be used) |
| Planning provider | Linear `duckbase-co` via `kc-plan-receipt/v1` |
| UAT delivery | Subspace `/r` |
| Approval defaults | `receipt/plan-approval.json` in the batch dir |
| E2E flows | `docs/ship/flows/` |
| Pin | `kc-ship-flow/pins/conductor-cli.txt` (the Conductor CLI this plugin was written against) |
| Installed contract interface | `kc-ship-flow-batch-pin/v1` |
| Integrated head | `trunk` — the adopter's row deciding whether `verified` runs before or after the Captain's merge (`preview`, `trunk`, or `staging`) |
<!-- kc-ship-flow-static-local-profile:end -->

## Stages

### `dispatched` — one workspace per ready task

Script: `kc-ship-flow/scripts/dispatch.sh <sprint> [--dry-run]`. One `conductor workspace create`
per `docs/dev` task whose `sprint` matches and whose `sprint-readiness` is `ready`, each carrying a
fixed first-officer boot message (not a per-stage ensign dispatch). Records a claim fence
(`<state-dir>/_ship_fence/<sprint>.json`) before each create so a re-run skips an
already-dispatched slug. Refuses (exit 2, `conductor unavailable`) when `conductor auth whoami`
fails or the workspace project id cannot be resolved from the repo remote.

### `watching` — poll to a prepared gate or an exit condition

Script: `kc-ship-flow/scripts/watch.sh <sprint> [--once]`. Reads the docs/dev state branch for a
prepared `validation` gate first; only when a task's session is idle does it fall back to reading
the transcript tail (`conductor sql`, never `session message --after` — see
`docs/ship/runbooks/conductor-cloud.md`) for a usage-limit banner (`quota`) or a trailing question
(`question`). Every question a worker asked and the answer sent is recorded on the batch.

### `verified` — e2e at the integrated head

Script: `kc-ship-flow/scripts/e2e-gate.py` (runs `kc-ship-flow/scripts/e2e-cli.sh`; stations:
`kc-ship-flow/references/stations/e2e-gate.md`, `kc-ship-flow/references/stations/e2e-cli.md`). The
head it verifies is the Local Profile's `Integrated head` row, not a choice this stage makes.

### `uat` — UAT handoff, then the Captain merges

Script: `kc-ship-flow/scripts/uat-doc.py` writes one document (tasks, PR links, gate status, e2e
result, open questions and answers; station: `kc-ship-flow/references/stations/uat-doc.md`). The
Captain approves each task's gate and merges; the ship first officer never merges.

### `closed` — worker debriefs, close receipt

After the Captain's merges are observed on the tasks (`pr: pr-merge:N`), each cloud worker runs its
own `spacedock debrief` and pushes it (a cloud session cannot collect its own transcript any other
way). The close receipt writer for this stage is a residual of the POC (owned by the
`ship-verify-uat-close` task); it is not yet implemented here.
