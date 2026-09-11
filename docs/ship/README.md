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
`docs/dev/.spacedock-state/ship-cloud-dispatch-and-watch/design/2026-09-10-ship-flow-cloud-wrapper-design.md`
on branch `spacedock-state/dev` for the full design and the ruling it
implements. The batch moves through `dispatched -> watching -> verified -> uat -> closed`.

<!-- kc-ship-flow-static-local-profile:start -->
## Local Profile

This table is the `run-batch` skill's declared input before dispatching a batch, not the full README as a policy bundle. `kc-ship-flow/scripts/local-profile-check.py` verifies the table's required rows; nothing checks what else the skill reads.

| Role | Bound local authority |
|---|---|
| Holder | State-holder identity written to `.spacedock-state`'s `_holder.json` by `spacedock state commit` |
| Runtime | Conductor cloud (the design's premise: if Conductor cloud cannot run, ship cannot be used) |
| Planning provider | Linear `duckbase-co` via `kc-plan-receipt/v1` |
| UAT delivery | Subspace `/r` |
| Approval defaults | `receipt/plan-approval.json` in the batch dir |
| E2E flows | `docs/ship/flows/` |
| Pin | `kc-ship-flow/pins/conductor-cli.contract` (the argv shapes `dispatch.sh`/`watch.sh` call; checked against live `conductor --help`, not version-gated) |
| Installed contract interface | `kc-ship-flow-batch-pin/v1` |
| Integrated head | `trunk` (placeholder, not yet a Captain ruling — one of `preview`, `trunk`, or `staging`; decides whether `verified` runs before or after the Captain's merge) |
<!-- kc-ship-flow-static-local-profile:end -->

## Stages

### `dispatched` — one workspace per ready task

Script: `kc-ship-flow/scripts/dispatch.sh <sprint> [--dry-run] --conn-quote QUOTE --conn-source
SOURCE`. One `conductor workspace create` per `docs/dev` task whose `sprint` matches and whose
`sprint-readiness` is `ready`, each carrying a fixed first-officer boot message (not a per-stage
ensign dispatch). The boot message names the sender (`workspace_creator_id` from `conductor auth
whoami`), a per-dispatch 12-hex token every worker report must echo, the Captain's verbatim batch
approval (`--conn-quote`/`--conn-source`), and "sync state by merge, never rebase" — round 1 showed
a worker treat an unnamed sender's answer as an injection and another refuse `git push` with no
conn to point to. `--conn-quote` (and its `--conn-source`) are required; missing either refuses
(exit 2, `conn required`) before any conductor call. Records a claim fence
(`<state-dir>/_ship_fence/<sprint>.json`) before each create so a re-run skips an
already-dispatched slug. Refuses (exit 2, `conductor unavailable`) when `conductor auth whoami`
fails; refuses (exit 6) when the workspace project id cannot be resolved from the repo remote;
refuses (exit 5) when a used argv shape in `kc-ship-flow/pins/conductor-cli.contract` is missing
from the installed `conductor --help`.

### `watching` — poll to a prepared gate or an exit condition

Script: `kc-ship-flow/scripts/watch.sh <sprint> [--once]`. Reads the docs/dev state branch for a
prepared `validation` gate first (flat `<slug>.md` or folder `<slug>/index.md`), then
`conductor workspace status` (an `initializing`-like workspace reads as `pending`); only when a
task's session is idle does it fall back to reading the transcript tail (`conductor sql`, never
`session message --after` — see `docs/ship/runbooks/conductor-cloud.md`) for a usage-limit banner
(`quota`) or a question (a trailing `?`, or a line opening `Q:`/`Question:`/`Decision:`/
`Could you`). A `stopped` verdict is only reported after two consecutive idle polls, since the
outer session can read idle while the FO's own subagent is still running. Recording each question
and its answer on the batch record is a residual: this stage only reports the `question` exit
today, it does not yet write that record.

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
