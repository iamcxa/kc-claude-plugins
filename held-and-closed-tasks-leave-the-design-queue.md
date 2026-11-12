---
title: A task the Captain held or closed at a gate no longer looks like work waiting in that stage
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:held-and-closed-tasks-leave-the-design-queue:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:held-and-closed-tasks-leave-the-design-queue-backlog-1
              briefing:
                id: briefing:held-and-closed-tasks-leave-the-design-queue:backlog:attempt-1:revision-1
                digest: sha256:cff2229580a5f7be6070bdcd4e21387458f05516df089eae064cacbff26a131d
                room-ref: ./held-and-closed-tasks-leave-the-design-queue/review/backlog/briefing-1
---

## Scope

- Source: FO's own miss, filed by FO with no Captain ruling yet; the backlog gate confirms it.
- Bite (FO read 2026-11-12 from gate records in this workflow's state): of 12 tasks with `status: ideation`, 10 carry a Captain `hold` or close ruling dated 2026-10-20 to 2026-11-05 and are not waiting for anything. FO offered five of them to the Captain as tasks waiting in design and he approved redispatching them before FO read the rulings; no dispatch was made. The two-week measurement of 2026-11-12 counted them as open tasks.
- Outcome: a held or closed task is told apart from a waiting one by a reader of `spacedock status` and by FO before it proposes work, and a held task states what would reopen it.
- Open for the design: whether Spacedock's own verdicts, archive or an existing field already express this (read its README and source first); whether closed tasks are archived as rejected, as two were; what happens to the 10 tasks named above.
- Non-goals: reopening or rebuilding any held task; changing what a hold ruling means.

## Budget
1 cycle per stage, in one package PR or none if the design finds an existing mechanism and only state changes are owed.

## Stop condition
- The 10 tasks are no longer listed as waiting in ideation by the command FO uses to choose work, each with its Captain ruling intact. Return to the Captain if any of the 10 needs a new ruling.

## FO alignment

Alignment: not needed: one observed defect with one outcome; the mechanism is compared in the design and ruled at the ideation gate.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
