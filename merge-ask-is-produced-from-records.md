---
title: The merge ask's summary is produced from records that already exist, and FO writes only the question
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:merge-ask-is-produced-from-records:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:merge-ask-is-produced-from-records-backlog-1
              briefing:
                id: briefing:merge-ask-is-produced-from-records:backlog:attempt-1:revision-1
                digest: sha256:4fc17bafe54536ccf49044c7b1d56e9218ed069be1e6f0e69edd13a6ede24a7e
                room-ref: ./merge-ask-is-produced-from-records/review/backlog/briefing-1
              withdrawal:
                by: agent:first-officer
                at: "2026-11-13T13:41:47.915088Z"
                reason: The Captain answered the first question with a question about model and effort instead of a decision (chat, 2026-11-13); FO asked again with the build strength in the question, and that second question is the one he answered.
            - id: gate-attempt:merge-ask-is-produced-from-records-backlog-2
              briefing:
                id: briefing:merge-ask-is-produced-from-records:backlog:attempt-2:revision-1
                digest: sha256:110960e6a9d63888a6308a54fccc52e8bc0bf08274303d8586e8c75044a8c7fe
                room-ref: ./merge-ask-is-produced-from-records/review/backlog/briefing-2
---

## Scope

- Source: the Captain 「3. 要」 (chat, 2026-11-13), answering FO's item 3: 「下一輪顧問試跑要不要現在開始準備，以及是否把「合併前這一段」的三個摩擦點各開一張任務。」 Evidence: the route trial of 2026-11-13, FO's hand-kept log and result (worker stages took 15 to 30 minutes; validated to merge ask took 85 to 120 minutes on three tasks).
- Bite: FO typed each delivery summary by hand on 2026-11-12 and 2026-11-13 (seven PRs, 15 to 20 minutes each by FO's log), copying the head, the validation verdict, the check counts, the review evidence ids and the merge-result run from records already in the task folder; hand-typed lines were refused by the checker four times and one observer found the external round count wrong.
- Upstream first, open for the design: what the delivery check, the validation skill text and the listed extensions already do for this, and whether a smaller change to one of them is enough.
- Non-goals: to be set at ideation.

## Budget
1 implementation and 2 validation cycles, in one package PR.

## Stop condition
- For the seven recorded deliveries, a generated summary passes the delivery check with no hand edit, and the Captain's question stays FO-written.

## FO alignment

Alignment: not needed before ideation: an observed friction with counts; the mechanism is compared in the design.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
