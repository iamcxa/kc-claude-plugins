---
title: The task budget counts ideation rounds, and the timeline helper reports each round's times and result
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:budget-form-counts-ideation-rounds-and-times-each-round:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:budget-form-counts-ideation-rounds-and-times-each-round-backlog-1
              briefing:
                id: briefing:budget-form-counts-ideation-rounds-and-times-each-round:backlog:attempt-1:revision-1
                digest: sha256:893c9d8282f18ba657f64cc67475bfeb01734f139a62768ce677a31ec40ce2d2
                room-ref: ./budget-form-counts-ideation-rounds-and-times-each-round/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:budget-form-counts-ideation-rounds-and-times-each-round:backlog:1
                briefing: briefing:budget-form-counts-ideation-rounds-and-times-each-round:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-11-13T09:54:45.159744Z"
                decision: approve
                reason: 'The Captain chose 「兩張都進設計（建議）」 (host question dialog, 2026-11-13), answering 「決定：要不要讓「把 Pilot 試作補完整」的兩張小任務進設計階段？建議要。第一張：設計關卡前的檢查程式逐條檢查 Pilot 的驗收條件，缺「指令、結束代碼、輸出位置」又沒寫明為什麼跑不了的就擋下。第二張：預算寫法可以把設計階段的試作輪數一起算進去，由程式擋下超過的派工，時間工具列出每一輪的起訖和結果。兩張預算都是 1 implementation and 2 validation cycles，各一個套件 PR。同意即接受：兩張的設計階段都先做試作，這次試作的許可我照已合併但未發版的新規則手寫進派工；設計回來各自在設計關卡給你裁定，我不代記；兩張可能都要動流程文件的字數上限，所以實作會排先後、不並行合併；第二張會擴充一份已核准的決策紀錄（預算寫法那份），設計若發現必須取代它而不是擴充，就回來找你。」; accepts outcome, scope and Budget as seeded. Recommendation: followed.'
              application:
                target-stage: ideation
                state: consumed
---

## Scope

- Source: the Captain 「分兩步（建議）」 (host question dialog, 2026-11-13), answering 「Pilot 試作的設計回來了，核准前要先定一件會改變範圍的事：試作輪數的預算要怎麼管？我建議分兩步。設計查到：現有的預算寫法（N implementation and M validation cycles）只會算實作和驗證，不會算設計階段的輪數；時間工具會算設計階段派了幾次、整個階段多久，但不會列出每一輪各自的起訖和結果。」; the chosen option read 「這張先用一句規則：試作一輪就是一次設計派工，第三次派工前我要停下來問你。另開一張小任務把預算寫法擴成「N ideation, N implementation and M validation cycles」由程式檢查，並讓時間工具列出每一輪。」 His earlier words (chat, 2026-11-13): 「可以，要同時加入預算與計時機制，我看目前你 X implementiation + Y valdiation cycle 方式還不錯」.
- What exists: the budget reader accepts three forms and counts implementation and validation records only; the timeline helper counts ideation dispatches and times a stage as a whole (ADR 0080); ADR 0077 names its own reopen condition for a bound the fixed forms cannot express. The design of pilot-ideation-runs-a-probe-before-the-design (decision D4) states the gap and holds the round cap in prose until this task lands.
- Outcome: a budget may bound ideation rounds in the same sentence as implementation and validation cycles, the script FO runs at each boundary holds the dispatch that would exceed it, and the timeline helper prints each round's start, end and result.
- Non-goals: counting minutes against a budget; changing the default when a budget is spent.

## Budget
1 implementation and 2 validation cycles, in one package PR.

## Stop condition
- A replayed task with three ideation dispatches is held at the third under a budget naming two, and the helper prints three rounds with their times. Return to the Captain if ADR 0077 or ADR 0080 must be superseded rather than extended.

## FO alignment

Alignment: not needed before ideation: his words choose the form; the grammar is ruled at the design gate.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
