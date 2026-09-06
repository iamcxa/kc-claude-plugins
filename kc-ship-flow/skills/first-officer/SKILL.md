---
name: first-officer
description: Use when running the commissioned docs/ship batch workflow end to end — dispatching a batch, accepting worker evidence, opening and dispositioning review, gating UAT, and closing the batch with a validated close receipt. Triggers on "ship a batch", "run the batch workflow", "docs/ship first officer".
---

# kc-ship-flow first officer

`docs/ship/README.md`'s `## Local Profile` table is this skill's declared input before resolving
or dispatching a batch, not the full README as a policy bundle. `local-profile-check.py` below
verifies the table's required rows; nothing checks what else this skill reads.

## Refuse before dispatch

Run:

```bash
python3 kc-ship-flow/scripts/local-profile-check.py docs/ship/README.md
```

A non-zero exit names the missing row on stderr. Do not dispatch a batch while this refuses —
most commonly the `Runtime` row, which selects local subagent or Conductor cloud dispatch for
the stage that follows.

## Run the station chain

Advance one commissioned `docs/ship` batch entity through its six stages in order, calling each
stage's installed script from `docs/ship/README.md`'s per-stage lines:

1. `dispatched` — `kc-ship-flow/scripts/fenced-dispatch.sh`
2. `accepted` — `kc-ship-flow/scripts/accept-evidence.sh`
3. `reviewed` — `kc-ship-flow/scripts/open-pr.sh`, then `kc-ship-flow/scripts/disposition.py`
4. `uat` (gate) — `kc-ship-flow/scripts/e2e-gate.py`, `kc-ship-flow/scripts/uat-doc.py`,
   `kc-ship-flow/scripts/notify.sh`
5. `merged` — no kc-ship-flow script; observe the GitHub merge through Spacedock's `pr-merge` mod
6. `closed` — `kc-ship-flow/scripts/dev-debrief.py`, then `kc-ship-flow/scripts/ship-debrief.py`

Write and check each stage's pin with `kc-ship-flow/scripts/pin.py write --station <name>` /
`check --station <name>` before advancing past it. Validate the closed stage's close receipt with
`docs/plan-flow/schema/validate-receipt.py <plan-receipt.json> <approval.json> <close-receipt.json>`
before terminalizing the entity.
