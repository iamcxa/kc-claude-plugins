---
title: dev2's principles make a stage ask the first-principles questions
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:first-principles-check-in-dev2-principles:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:first-principles-check-in-dev2-principles-backlog-1
              briefing:
                id: briefing:first-principles-check-in-dev2-principles:backlog:attempt-1:revision-1
                digest: sha256:41a7e4e0e039a9909cc26c4af95d7ebfa9165a4dd3a4e2793941a93985328029
                room-ref: ./first-principles-check-in-dev2-principles/review/backlog/briefing-1
---

## Scope

- Source: the Captain 「第一性原理審查在 dev2 沒有一樣的規範嗎？有就用，沒有就找 dev2 fo 討論是否做一個原則」 and then 「我覺得應該把第一性原理確實加入到 dev2 心態原則中，讓它更全面更完整，就像你說的，沒有任何階段會強制問」 (chat with the session that owns kc-ops-inbox, 2026-11-10), relayed by Paseo 0a411d01 (relayed, not a ruling here; the backlog gate confirms it).
- The three questions as that session described them: trace each part of the scope to a stated need in the Captain's words; say what breaks if a part is deleted; name the one assumption that would make the task unnecessary and a cheap test for it.
- Bite (that session's report, which it marks as not yet checked; not re-run here): task ops-inbox-r1-setup-and-isolation in this workflow passed backlog, two ideation gates, three implementation cycles and an independent architecture review before a first-principles pass run by hand on 2026-11-10 reported that the dispatched agent may add nothing the Captain cannot decide from the bare numbers, and that one repair requirement traces to no request.
- Package fact (FO read 2026-11-10, kc-dev-flow-2 0.37.0): `skills/ideation/principles.md` holds "Prefer the smallest working mechanism for the accepted goal", which constrains the mechanism once the goal is accepted; the other claims in the relay about the chief-engineer and engineering-reviewer skills are that session's reading, not re-read here.
- Open for the design, his to gate: which file holds it (stage principles, FO's backlog alignment lines, or both), the wording, where it is forced and not only stated, its cost per task, whether it would have caught the inbox case with what was known on 2026-10-19 to 2026-10-23, and what it removes or replaces so the flow does not only grow.
- Related: the without-it test in the Captain's global instructions; the journey-map release-review interrogation; backlog task ideation-checks-external-prior-art.
- Asked by the relaying session: one short message with the outcome, since the inbox task is the test case.
- Non-goals: repairing ops-inbox-r1-setup-and-isolation; installing a global agent.

## Budget
- One package PR to the principles text and its tests; workflow word budget unchanged unless the design names a raise for the Captain.

## Stop condition
- A named stage is made to answer the three questions, shown by a replay on the inbox case's backlog or ideation dispatch and a control task where it stays short, and the design names what it removes or replaces.

## FO alignment

Alignment: needed at ideation; where it is forced and what it costs each task are the Captain's call.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
