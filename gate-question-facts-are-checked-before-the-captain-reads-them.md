---
title: A factual claim in a question FO puts to the Captain has been checked against the record before he reads it
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:gate-question-facts-are-checked-before-the-captain-reads-them:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:gate-question-facts-are-checked-before-the-captain-reads-them-backlog-1
              briefing:
                id: briefing:gate-question-facts-are-checked-before-the-captain-reads-them:backlog:attempt-1:revision-1
                digest: sha256:ab7abf3920dd5c06228fc87eabeee3a493b7bb32aea8b905da77f71bffdcd594
                room-ref: ./gate-question-facts-are-checked-before-the-captain-reads-them/review/backlog/briefing-1
              withdrawal:
                by: agent:first-officer
                at: "2026-11-12T05:11:42.508362Z"
                reason: The Captain answered the joint question with a change to the experiment instead of a decision (host question dialog, 2026-11-12); FO asks again with the experiment written into the question.
            - id: gate-attempt:gate-question-facts-are-checked-before-the-captain-reads-them-backlog-2
              briefing:
                id: briefing:gate-question-facts-are-checked-before-the-captain-reads-them:backlog:attempt-2:revision-1
                digest: sha256:e7c2ec3f8a86e3421463c2cdb688b335db038471b38756669febb492c3efccb8
                room-ref: ./gate-question-facts-are-checked-before-the-captain-reads-them/review/backlog/briefing-2
              resolution:
                type: Resolution
                id: resolution:spacedock:gate-question-facts-are-checked-before-the-captain-reads-them:backlog:2
                briefing: briefing:gate-question-facts-are-checked-before-the-captain-reads-them:backlog:attempt-2:revision-1
                by: person:captain
                at: "2026-11-12T05:15:55.668181Z"
                decision: approve
                reason: 'The Captain chose 「核准，照這個分組（建議）」 (host question dialog, 2026-11-12), answering 「決定：這五張新任務要不要都進設計階段，並照你說的做成對照實驗。我建議核准。五張是：一、合併前在合併後的結果上跑測試；二、被你擱置或關掉的任務不再像在排隊；三、每張任務記錄階段時間、重做、打斷次數；四、派工結束封存證據、刪掉暫存；五、我問你的問題裡的事實先對過紀錄。實驗分兩組：第三、五、一張的設計階段照你的說法，等於「試作加擴大計畫」，設計工人先在不推送的分支上把東西真的做出一個能跑的試作、拿真實案例跑過，再寫擴大成正式版本還要補什麼，實作工人從那個試作接著做；第二、四張的設計階段只要求把每條驗收條件的證明實際跑一次，不寫試作。對照基準是過去兩週的 67 張。核准代表接受各任務檔寫的範圍、預算（每階段一輪、一個 PR）與停止條件。不代表接受任何設計或修法。哪張進哪一組是我挑的，不是隨機：試作組放的是證據最難產生或最大的三張。五張合起來我沒有把握一天做完，超過時我連同預算回來請你取捨。」. Recommendation: followed. The experiment is his: before this question he answered the first form of it with 「我想要做一個實驗，比較一下，有幾張的構思階段就是包含實作poc，你說構思完全沒有先試驗過測試過，所以我想加過這一段試試看是否就會改善，等於構思等於poc加擴大計畫」 (same dialog), and FO withdrew and re-asked.'
              application:
                target-stage: ideation
                state: pending
---

## Scope

- Source: FO's own misses, filed by FO with no Captain ruling yet; the backlog gate confirms it.
- Bite, three times in two days, each found after the Captain had answered: the #843 merge ask said already-filed tasks would not be asked to add a Story line, while the approved design has the idle look name them (observer report, 2026-11-11); the #841 merge ask said only designs not yet through the design gate would be refused, while release 0.39.0 refused approved ones and an adopter found it after release (2026-11-11); a question of 2026-11-12 described five tasks as waiting in design when the Captain had held or closed all five.
- What exists: the delivery check counts unchecked numbers in gate text and the workflow says each claim names the command and date that produced it; none of the three claims was a number, and the check passed each time.
- Outcome: a sentence in a gate or decision question that says what a change does or what state a task is in either names the record or run that shows it, or is marked as unverified where the Captain reads it.
- Open for the design: whether this can be checked at all by a script, or is a step with a record; what the cheapest version is that would have caught the three cases; what it costs FO per question in words and minutes.
- Non-goals: checking the Captain's own words; a second reviewer for every question; rewriting the question form.

## Budget
1 cycle per stage, in one package PR.

## Stop condition
- Replaying the three questions named under Bite at their recorded state, the candidate flags each false sentence, and three questions that were true are not flagged. Return to the Captain if the design finds no mechanism cheaper than a second agent reading every question.

## FO alignment

Alignment: not needed: one observed defect with one outcome; whether and how it can be checked is compared in the design and ruled at the ideation gate.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
