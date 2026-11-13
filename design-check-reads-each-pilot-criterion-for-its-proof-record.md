---
title: The design check holds a Pilot design whose criterion lacks its proof record or a stated reason it cannot be run
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:design-check-reads-each-pilot-criterion-for-its-proof-record:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:design-check-reads-each-pilot-criterion-for-its-proof-record-backlog-1
              briefing:
                id: briefing:design-check-reads-each-pilot-criterion-for-its-proof-record:backlog:attempt-1:revision-1
                digest: sha256:415114526c65f8802ea55b310fb612ed5dbd71ccda0fb056baa75c0a2dfc59a7
                room-ref: ./design-check-reads-each-pilot-criterion-for-its-proof-record/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:design-check-reads-each-pilot-criterion-for-its-proof-record:backlog:1
                briefing: briefing:design-check-reads-each-pilot-criterion-for-its-proof-record:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-11-13T09:54:38.596406Z"
                decision: approve
                reason: 'The Captain chose 「兩張都進設計（建議）」 (host question dialog, 2026-11-13), answering 「決定：要不要讓「把 Pilot 試作補完整」的兩張小任務進設計階段？建議要。第一張：設計關卡前的檢查程式逐條檢查 Pilot 的驗收條件，缺「指令、結束代碼、輸出位置」又沒寫明為什麼跑不了的就擋下。第二張：預算寫法可以把設計階段的試作輪數一起算進去，由程式擋下超過的派工，時間工具列出每一輪的起訖和結果。兩張預算都是 1 implementation and 2 validation cycles，各一個套件 PR。同意即接受：兩張的設計階段都先做試作，這次試作的許可我照已合併但未發版的新規則手寫進派工；設計回來各自在設計關卡給你裁定，我不代記；兩張可能都要動流程文件的字數上限，所以實作會排先後、不並行合併；第二張會擴充一份已核准的決策紀錄（預算寫法那份），設計若發現必須取代它而不是擴充，就回來找你。」; accepts outcome, scope and Budget as seeded. Recommendation: followed.'
              application:
                target-stage: ideation
                state: pending
---

## Scope

- Source: the Captain 「先做一：把 Pilot 試作補完整，再做二：邊界合約先行」 (chat, 2026-11-13), answering FO's list of four directions, whose first read 「一、把 Pilot 試作補完整｜這版的兩條規則只靠文字：每條驗收條件要記齊、試作最多兩輪｜驗證時兩個測試 worker 一個漏記；顧問明說只有檢查程式擋得住｜兩張小任務，其中一張已在待辦」.
- Bite (validation of PR 864, 2026-11-13): the merged Pilot text asks an ideation worker to run each criterion's proof once and record command, exit and output path; one history-free test worker recorded them for 2 of its 3 criteria, a second for 4 of 4 after a one-sentence rewording, and the investigation could not decide from one run whether wording was the cause. The chief-engineer's read the same day: the requirement is prose only, the design check reads that criteria are declared and not that each carries the three fields, so completeness rests on the worker.
- Outcome: before the design gate, the existing design check refuses a Pilot design in which a criterion has neither a complete record (command, observed exit, retained output path) nor an entry under `Not provable now` naming that criterion and why.
- What exists: `design_surfaces.py check <task>`, run by FO before every ideation gate; the criterion form (bold `AC-N`, evidence clause, falsifier) and the `Not provable now` heading from ADR 0084.
- Open for the design: how a record is recognised without a new required syntax that old tasks fail; whether tasks approved before the change are exempt by date or by profile; what the check does for a criterion whose proof is a document reading and has no command.
- Non-goals: proving that a recorded command was really run or that its output is true; any change to POC or Prod; the round cap (task budget-form-counts-ideation-rounds-and-times-each-round carries it).

## Budget
1 implementation and 2 validation cycles, in one package PR.

## Stop condition
- A replay of the two test workers' designs from PR 864's validation is refused for the one with a missing record and passes the complete one, and no task approved before the change is refused. Return to the Captain if the check needs a new required line in every criterion.

## FO alignment

Alignment: not needed before ideation: his words admit the direction; the recognition rule is ruled at the design gate.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
