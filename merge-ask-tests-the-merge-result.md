---
title: A merge ask for a PR whose base moved since validation carries a test run on the merge result
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:merge-ask-tests-the-merge-result:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:merge-ask-tests-the-merge-result-backlog-1
              briefing:
                id: briefing:merge-ask-tests-the-merge-result:backlog:attempt-1:revision-1
                digest: sha256:49ebaa98701d209a51e97e09e90aa390888350e8d02aef377224de98ebe6270a
                room-ref: ./merge-ask-tests-the-merge-result/review/backlog/briefing-1
              withdrawal:
                by: agent:first-officer
                at: "2026-11-12T05:11:28.449691Z"
                reason: The Captain answered the joint question with a change to the experiment instead of a decision (host question dialog, 2026-11-12); FO asks again with the experiment written into the question.
            - id: gate-attempt:merge-ask-tests-the-merge-result-backlog-2
              briefing:
                id: briefing:merge-ask-tests-the-merge-result:backlog:attempt-2:revision-1
                digest: sha256:09fe9a54d587cdd31282078fed3541c7e4e93362d7126e11df246e7af3164c35
                room-ref: ./merge-ask-tests-the-merge-result/review/backlog/briefing-2
              resolution:
                type: Resolution
                id: resolution:spacedock:merge-ask-tests-the-merge-result:backlog:2
                briefing: briefing:merge-ask-tests-the-merge-result:backlog:attempt-2:revision-1
                by: person:captain
                at: "2026-11-12T05:15:22.509496Z"
                decision: approve
                reason: 'The Captain chose 「核准，照這個分組（建議）」 (host question dialog, 2026-11-12), answering 「決定：這五張新任務要不要都進設計階段，並照你說的做成對照實驗。我建議核准。五張是：一、合併前在合併後的結果上跑測試；二、被你擱置或關掉的任務不再像在排隊；三、每張任務記錄階段時間、重做、打斷次數；四、派工結束封存證據、刪掉暫存；五、我問你的問題裡的事實先對過紀錄。實驗分兩組：第三、五、一張的設計階段照你的說法，等於「試作加擴大計畫」，設計工人先在不推送的分支上把東西真的做出一個能跑的試作、拿真實案例跑過，再寫擴大成正式版本還要補什麼，實作工人從那個試作接著做；第二、四張的設計階段只要求把每條驗收條件的證明實際跑一次，不寫試作。對照基準是過去兩週的 67 張。核准代表接受各任務檔寫的範圍、預算（每階段一輪、一個 PR）與停止條件。不代表接受任何設計或修法。哪張進哪一組是我挑的，不是隨機：試作組放的是證據最難產生或最大的三張。五張合起來我沒有把握一天做完，超過時我連同預算回來請你取捨。」. Recommendation: followed. The experiment is his: before this question he answered the first form of it with 「我想要做一個實驗，比較一下，有幾張的構思階段就是包含實作poc，你說構思完全沒有先試驗過測試過，所以我想加過這一段試試看是否就會改善，等於構思等於poc加擴大計畫」 (same dialog), and FO withdrew and re-asked.'
              application:
                target-stage: ideation
                state: pending
---

## Scope

- Source: FO's own miss, filed by FO with no Captain ruling yet; the backlog gate confirms it.
- Bite (FO read 2026-11-11, `gh run view 42991036147 --repo iamcxa/kc-claude-plugins --log-failed`): PRs #843 and #841 each passed their own checks and validation; after both merged, main failed one of 226 tests in `kc-dev-flow-2/scripts/test_design_surfaces.py`, Release PR #840 could not pass, and a fix task ran 80 minutes from filing to archive. The #841 merge ask said the acceptance was not rerun on the merged result; nothing held the ask.
- Outcome: when main has moved since the validated head was dispatched, FO's merge ask is held until a test run on the result of merging that head with current main is recorded, or the Captain is told in the question that none was run.
- Open for the design: which commands count as the run and who runs them; whether the existing delivery check can carry it or GitHub's own merge queue or required up-to-date branch setting already does; what it costs per PR in minutes.
- Non-goals: changing CI definitions; rerunning validation; any rule for PRs whose base did not move.

## Budget
1 cycle per stage, in one package PR.

## Stop condition
- A replay of PR #841's merge ask at its recorded state is held by the candidate and the same ask with a recorded merge-result run passes. Return to the Captain if the design needs a CI or repository-setting change.

## FO alignment

Alignment: not needed: one observed defect with one outcome; how it is checked is compared in the design and ruled at the ideation gate.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
