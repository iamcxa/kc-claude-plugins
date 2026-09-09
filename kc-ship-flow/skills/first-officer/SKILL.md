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
3. `reviewed` — `kc-ship-flow/scripts/open-pr.sh`, then `kc-ship-flow/scripts/disposition.py`. When the
   diff touches a dependency manifest or lockfile, dispatch the supply-chain lane
   (`kc-pr-flow:tob-supply-chain-checker` or the profile's equivalent) and write its findings before
   calling `disposition.py` — passed a bundle directory, it refuses (exit 2,
   `supply-chain findings required`) when that path is absent.
4. `uat` (gate) — `kc-ship-flow/scripts/e2e-gate.py --root <code checkout> --flows docs/ship/flows
   <plan-receipt.json> <close-receipt.json>` (`--root` and `--flows` are always required; `--flows`
   is the Local Profile table's "E2E flows" row value), `kc-ship-flow/scripts/uat-doc.py`,
   `kc-ship-flow/scripts/notify.sh`
5. `merged` — no kc-ship-flow script; observe the GitHub merge through Spacedock's `pr-merge` mod
6. `closed` — `kc-ship-flow/scripts/dev-debrief.py`, then `kc-ship-flow/scripts/ship-debrief.py`;
   embed each script's stdout as the close receipt's own `dev_debrief` / `ship_debrief` field (the
   schema requires both there)

Write and check each stage's pin with `kc-ship-flow/scripts/pin.py write --station <name>` /
`check --station <name>` before advancing past it. Validate the closed stage's close receipt with
`docs/plan-flow/schema/validate-receipt.py <plan-receipt.json> <approval.json> <close-receipt.json>`
before terminalizing the entity.

## Merge verdict

Before a stage-5 merge verdict names a CI check as the gate for a monorepo package, run:

```bash
kc-ship-flow/scripts/ci-covers.sh <repo-root> <package-path> <check-name>
```

Exit 0 records the check's output as the gate. On exit 1 the check named it but never entered the
package (or never named it at all) — the verdict cannot cite that CI check as the gate; it names the
FO's own local run of the package's tests as the gate instead, and says so. See
`references/stations/ci-covers.md`.
