---
title: Every task records its time per stage, its revise count and its interruption count, and a helper reads them out
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:each-task-records-stage-time-revises-and-interruptions:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:each-task-records-stage-time-revises-and-interruptions-backlog-1
              briefing:
                id: briefing:each-task-records-stage-time-revises-and-interruptions:backlog:attempt-1:revision-1
                digest: sha256:34a62b970da873e147a12ba0bb7b6c7b26551529acdc7259ff6e670129ab6f69
                room-ref: ./each-task-records-stage-time-revises-and-interruptions/review/backlog/briefing-1
              withdrawal:
                by: agent:first-officer
                at: "2026-11-12T05:11:35.580927Z"
                reason: The Captain answered the joint question with a change to the experiment instead of a decision (host question dialog, 2026-11-12); FO asks again with the experiment written into the question.
            - id: gate-attempt:each-task-records-stage-time-revises-and-interruptions-backlog-2
              briefing:
                id: briefing:each-task-records-stage-time-revises-and-interruptions:backlog:attempt-2:revision-1
                digest: sha256:762ad300bff30028ba160857706b482da6279dc4723785e20459d456f4b64bd9
                room-ref: ./each-task-records-stage-time-revises-and-interruptions/review/backlog/briefing-2
              resolution:
                type: Resolution
                id: resolution:spacedock:each-task-records-stage-time-revises-and-interruptions:backlog:2
                briefing: briefing:each-task-records-stage-time-revises-and-interruptions:backlog:attempt-2:revision-1
                by: person:captain
                at: "2026-11-12T05:15:39.174528Z"
                decision: approve
                reason: 'The Captain chose 「核准，照這個分組（建議）」 (host question dialog, 2026-11-12), answering 「決定：這五張新任務要不要都進設計階段，並照你說的做成對照實驗。我建議核准。五張是：一、合併前在合併後的結果上跑測試；二、被你擱置或關掉的任務不再像在排隊；三、每張任務記錄階段時間、重做、打斷次數；四、派工結束封存證據、刪掉暫存；五、我問你的問題裡的事實先對過紀錄。實驗分兩組：第三、五、一張的設計階段照你的說法，等於「試作加擴大計畫」，設計工人先在不推送的分支上把東西真的做出一個能跑的試作、拿真實案例跑過，再寫擴大成正式版本還要補什麼，實作工人從那個試作接著做；第二、四張的設計階段只要求把每條驗收條件的證明實際跑一次，不寫試作。對照基準是過去兩週的 67 張。核准代表接受各任務檔寫的範圍、預算（每階段一輪、一個 PR）與停止條件。不代表接受任何設計或修法。哪張進哪一組是我挑的，不是隨機：試作組放的是證據最難產生或最大的三張。五張合起來我沒有把握一天做完，超過時我連同預算回來請你取捨。」. Recommendation: followed. The experiment is his: before this question he answered the first form of it with 「我想要做一個實驗，比較一下，有幾張的構思階段就是包含實作poc，你說構思完全沒有先試驗過測試過，所以我想加過這一段試試看是否就會改善，等於構思等於poc加擴大計畫」 (same dialog), and FO withdrew and re-asked.'
              application:
                target-stage: ideation
                state: consumed
started: 2026-11-12T05:16:44Z
---

## Scope

- Source: the Captain 「prod 應該要縝密沒有問題的，但是不管哪個 profile 都必須明確加入計時機制，要可以追溯每個 stage 的時間，revise 次數，打斷次數，以便改進整個 agentic DX」 (chat with FO session 3, 2026-11-12); earlier 「如果可行，應該要搭配一套 lint + helper 工具記錄時間，判準，取出時間」 and 「而且你沒記錄時間現在看來是一個非常大的問題」 (same chat, 2026-11-11).
- Bite (FO, 2026-11-11 and 2026-11-12): FO could not say how long PR #849 took per stage without reading commit times by hand; a two-week measurement could match agent sessions to tasks for 3 of 10 sampled tasks and could not count interruptions at all, because none is recorded.
- What exists (study of 2026-11-12, FO's local notes, not verified line by line): Spacedock stamps started, completed and archived once per task and each gate decision, not when a gate was opened; kc-dev-flow version 1's POC close guard recorded decision-ready seconds, Captain interventions and Captain wait; a Codex First Officer keeps a per-task time file by hand; state commit times give stage times after the fact.
- Outcome: for any task, one command prints each stage's start and end, agent time against waiting where the source allows, the number of repeat dispatches per stage, and the number of questions put to the Captain outside the task's scheduled gates, from records written at the time.
- Open for the design: the definition of a revise and of an interruption that can be counted; what must be newly recorded and by whom; the time source on Claude and on Codex; whether a check refuses a task with missing records or only reports.
- Non-goals: a time or minutes budget that holds work (ADR 0077 says minutes are not counted); cost in money or tokens; dashboards.

## Budget
1 cycle per stage, in one package PR.

## Stop condition
- The command, run on three tasks finished after the change, prints the same stage times FO kept by hand for them within five minutes each, and the counts match FO's hand tally. Return to the Captain if a reliable time source does not exist on one host.

## FO alignment

Alignment: not needed: the Captain's words under Source name the three quantities and that every profile carries them; definitions are compared in the design and ruled at the ideation gate.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
