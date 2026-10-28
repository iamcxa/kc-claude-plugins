---
title: A Captain ruling recorded from a peer's relayed words is refused by a check FO already runs
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:captain-ruling-sources-checked:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:captain-ruling-sources-checked-backlog-1
              briefing:
                id: briefing:captain-ruling-sources-checked:backlog:attempt-1:revision-1
                digest: sha256:c84dde7cc43e154da060c0b6083fa27ed32494d0046f129f457674091e43c6d4
                room-ref: ./captain-ruling-sources-checked/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:captain-ruling-sources-checked:backlog:1
                briefing: briefing:captain-ruling-sources-checked:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-28T05:38:57.95005Z"
                decision: approve
                reason: The Captain 「准」 (chat, 2026-10-28), answering FO's joint batch-9 backlog presentation of five gates whose ask was 「決定：五張全准進入設計階段；要拿掉或換掉哪張，直接說。」; accepts FO's recommendation to enter ideation on the pilot profile.
              application:
                target-stage: ideation
                state: consumed
---

## Scope

- Source: the Captain 「全准」 (chat, 2026-10-27), accepting FO's recommendation to move the structured Captain-source check out of peers-rules-name-each-host-binding into its own task, designed together with adr-required-statement.
- Bite: peers interview round 1 (fo-interviews-extension/peers-round-1.md): qnow recorded two peer-relayed rulings as the Captain's (agents-md-adr-pointer, product-analytics-posthog); ops-inbox recorded relayed quotes as "relayed" without reading the source.
- Input: the design in peers-rules-name-each-host-binding (section "Structured refusal at the existing check" and its ideation decision 2, at its 2026-10-27 head): a `## Captain sources` section, `design_surfaces.py check` refusing missing, unknown or peer-relay origins, and backfill of active tasks. FO's concern at the gate: every Captain ruling would need a structured entry and active tasks without readable originals would hold, against two bites in one adopter.
- Upstream first: adr-required-statement (another session; designs a `## Captain rulings` section for the same check), `scripts/design_surfaces.py`, `scripts/decision_ledger.py`.

## Non-goals

- Designing adr-required-statement (another session; coordinate only); checking rulings in archived tasks.

## Budget

- One package PR in `scripts/design_surfaces.py`; a backfill of active tasks only if the Captain accepts it at ideation.

## Stop condition

- The two qnow bites replay as refused and current active tasks pass or are listed by name. Return to the Captain if the design needs a structured entry for every Captain ruling (FO's concern at the 2026-10-27 gate).

## FO alignment

Alignment: needed before ideation; the scope of the check and any backfill are the Captain's.
Result: aligned at backlog: the Captain 「准」 (chat, 2026-10-28) to FO's batch-9 backlog sitting, which asked 「決定：五張全准進入設計階段；要拿掉或換掉哪張，直接說。」, approved the outcome and bounds in this file. The scope of the check and any backfill of active tasks stay his: ideation returns them as decisions at the ideation gate.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.


## Stage Report: ideation

- FAILED: A design for refusing, in scripts/design_surfaces.py check, a Captain ruling recorded from a peer's relayed words, reconciled with adr-required-statement's ## Captain rulings design (read its task file as it stands); the two qnow bites in fo-interviews-extension/peers-round-1.md replayed as refused; the scope of any active-task backfill left as a Captain decision
  HOLD before design: FO alignment says "needed before ideation" but records no Result: line; the loaded ideation/principles.md explicitly requires stopping. No design or replay was performed, and no backfill scope was selected.
- SKIPPED: A `### Batch overlap` section naming each file the design would change and each other batch task (reused-worker-dispatch-leaves-a-record, paseo-codex-dispatch-practice, captain-ruling-sources-checked, batch-reaches-each-gate-together, fo-interviews-extension) and live task of other sessions (adoption-asks-which-extensions, adr-required-statement, adr-silent-undo-probe, comment-check-reaches-delivery-gate, journey-canvas-hosted-poc, journey-server-host-pilot, ops-inbox-r1-setup-and-isolation, pr-review-lite-value-pilot (driven by other sessions; read only)) that changes the same file or check, so FO can order implementation
  Deferred with design: sibling task inspection and proposed file ownership were not started after the required alignment hold.
- SKIPPED: The words FO reads at each lifecycle moment, before and after, per root learning.md "Measure the words FO reads at each moment, not one file's size"
  Deferred with design: no before/after wording or word-cost claim was authored.
- SKIPPED: Acceptance criteria with reproducible evidence clauses and falsifiers, and unresolved decisions for the Captain, each with a recommendation and what gets worse under it
  Deferred with design: no criteria were authored; check run below confirms the present task is not gate-ready. FO must record actual alignment, not infer it from dispatch or backlog approval.
- DONE: Run the selected package's design-surface check before reporting.
  `python3 /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.32.1/scripts/design_surfaces.py check <this-task>` exited 1: `captain-ruling-sources-checked.md: missing '## Acceptance criteria' section`; this checks the current missing criteria only and does not mechanically establish the missing-Result hold.

### Summary

Ideation is held, not completed: the pilot route requires a recorded FO alignment result before design, and this task has none. FO should record the actual aligned direction and redispatch; no package design, repository code, branch, sibling task, Captain ruling, gate state or backfill decision was changed. Only this task-body hold report is submitted; current origin/main, GitHub, the upstream/adopter chain, batch overlaps and the two qnow replays remain unexamined because design did not start.
