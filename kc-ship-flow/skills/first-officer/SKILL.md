---
name: first-officer
description: Use when running the commissioned docs/ship batch workflow end to end — dispatching a batch's dev tasks into Conductor cloud, watching them to a prepared validation gate, verifying the integrated head, gating UAT, and closing the batch once every worker's debrief is pushed. Triggers on "ship a batch", "run the batch workflow", "docs/ship first officer".
---

# kc-ship-flow first officer

Ship is a wrapper over kc-dev-flow and Spacedock (design:
`docs/superpowers/specs/2026-09-10-ship-flow-cloud-wrapper-design.md`): anything dev flow or
Spacedock already does per task is not repeated here. `docs/ship/README.md`'s `## Local Profile`
table is this skill's declared input before resolving or dispatching a batch, not the full README
as a policy bundle. `local-profile-check.py` below verifies the table's required rows; nothing
checks what else this skill reads.

## Refuse before dispatch

Run:

```bash
python3 kc-ship-flow/scripts/local-profile-check.py docs/ship/README.md
```

A non-zero exit names the missing row on stderr. Do not dispatch a batch while this refuses —
most commonly the `Runtime` row, which selects local subagent or Conductor cloud dispatch for
the stage that follows.

## Run the stage chain

Advance one commissioned `docs/ship` batch entity through its five stages in order:

1. `dispatched` — `kc-ship-flow/scripts/dispatch.sh <sprint> [--dry-run]` creates one Conductor
   workspace per `docs/dev` task whose `sprint` matches and whose `sprint-readiness` is `ready`,
   each carrying a fixed first-officer boot message, guarded by a claim fence
   (`<state-dir>/_ship_fence/<sprint>.json`) so a re-run skips an already-dispatched slug.
2. `watching` — `kc-ship-flow/scripts/watch.sh <sprint> [--once]` polls the state branch for a
   prepared `validation` gate first, falling back to the transcript tail (`conductor sql`, never
   `session message --after`) only when a task's session is idle, reporting a usage-limit banner
   (`quota`) or a trailing question (`question`). Route a stuck worker's question per the Local
   Profile table before it dispatches next.
3. `verified` — `kc-ship-flow/scripts/e2e-gate.py --root <code checkout> --flows docs/ship/flows
   <plan-receipt.json> <close-receipt.json>` (`--root` and `--flows` are always required; `--flows`
   is the Local Profile table's "E2E flows" row value) at the integrated head.
4. `uat` (gate) — `kc-ship-flow/scripts/uat-doc.py` writes the UAT document from the batch record;
   the Captain records the gate decision per task and merges. Acceptance, review, and merge are
   dev flow's and Spacedock's own — this skill never opens, reviews, or merges a PR itself.
5. `closed` — each cloud worker runs its own `spacedock debrief` after its PR merges and pushes it
   path-scoped under `_debriefs/`; the batch closes once every task shows a merged PR and a pushed
   debrief (or the Captain records `captain_stopped` for the rest).

Write and check each stage's pin with `kc-ship-flow/scripts/pin.py write --station <name>` /
`check --station <name>` before advancing past it. Validate the closed stage's close receipt with
`docs/plan-flow/schema/validate-receipt.py <plan-receipt.json> <approval.json> <close-receipt.json>`
before terminalizing the entity.
