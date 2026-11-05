---
title: A gate summary that declines findings names each finding and its reason
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:gate-summary-names-each-decline:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:gate-summary-names-each-decline-backlog-1
              briefing:
                id: briefing:gate-summary-names-each-decline:backlog:attempt-1:revision-1
                digest: sha256:b0f8f869872b9d9b67cd9095d8bcdf6810f9ba532c02fbbb0bdd335e24bfc205
                room-ref: ./gate-summary-names-each-decline/review/backlog/briefing-1
---

## Scope

- Source: the Captain 「同意開 1 到 5，第 6 項併進「GPT 夥伴」提案」 (chat, 2026-10-27), answering FO's list of package-issue candidates (items 2 to 5 relayed by the relay FO, Paseo 1671c3a9, from its pair-once and room-specs-follow-web-part-select observer reports; item 1 relayed by the kc-ops-inbox FO, Paseo 46c2ebdf).
- Bite: relay pair-once validation-1: the gate summary said 'security 2 LOW declined' without naming the findings or a reason; `gate prepare` accepted it, and `delivery_gate.py` checks only text starting with 'Declined:' (relay FO's reading).
- Upstream first: `scripts/delivery_gate.py` decline parsing, `scripts/design_surfaces.py`, the README's FO steps: review findings step 2.
- Added 2026-11-05 (FO read of origin/main `delivery_gate.py`): partly covered since 22534441e (2026-10-19): the merge check holds a `Declined...:` or `FO declines...:` item with no bracketed reason, and fewer declined items than the newest validation report's `Deferred risk:` / `Polish:` bullets. Not covered: a decline written without that label (the relay bite above), findings from a reviewer that writes no such bullets, and a decline that names no receiving backlog task (README FO steps: review findings, step 5; observer: 3 violations in batches 12 and 13, 9 across all archives, grep 2026-11-05). FO proposes all three as this task's scope at the batch 14 backlog gate.
- Non-goals: judging whether a bracketed reason is a good one; the check proves only that a reason is written.
- Batch 14: the Captain 「可以」 (chat, 2026-11-05), answering 「這 5 張當下一批，可以嗎？」, which named this task.

## Budget
- One package PR. Workflow word budget unchanged unless the design names a raise for the Captain.

## Stop condition
- A replay of the relay 'security 2 LOW declined' summary and of the batch 12 and 13 declines that name no receiving task is held; a decline that names the finding, a bracketed reason and its receiving task passes.

## FO alignment

Alignment: needed before ideation; where the check runs is a package design choice.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
