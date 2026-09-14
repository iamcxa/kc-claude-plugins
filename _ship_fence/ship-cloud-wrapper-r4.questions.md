# ship-cloud-wrapper-r4 — dispatch log, questions and answers

## 2026-09-15 dispatch
Captain: 「r4 現在開」. Batch of three, all with `bite:` and `consumer:` lines: `admission-asks-who-was-bitten-and-who-will-run-it` (kc-dev-flow), `close-roster-is-the-fence-and-captain-stopped-validates` (kc-ship-flow), `boot-names-delivery-order-and-forbidden-actions` (kc-ship-flow). Three r3-deferred tasks stay deferred in this sprint (no bite). Dispatched with main's dispatch.sh (#445/#451 merged, unreleased): the sql probe degraded cleanly ("degraded: conductor sql probe failed, continuing") — first live use of #451. Follow-up sent to all three: runtime, pilot, gate cadence (prepare and stop; FO records), push-and-open-PR before validation, forbidden actions, no fixture copies, name the consumer in the PR body.
Workspaces: see `ship-cloud-wrapper-r4.json`.
