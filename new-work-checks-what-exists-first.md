---
title: Before any new work, the worker finds what already exists, states what it checked and found, and designs the new part as an addition to it
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:new-work-checks-what-exists-first:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:new-work-checks-what-exists-first-backlog-1
              briefing:
                id: briefing:new-work-checks-what-exists-first:backlog:attempt-1:revision-1
                digest: sha256:2e8a099d1f558a47191b650c77499eb8616e1f95913e5dc1583173f0a7da57a9
                room-ref: ./new-work-checks-what-exists-first/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:new-work-checks-what-exists-first:backlog:1
                briefing: briefing:new-work-checks-what-exists-first:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-11-12T17:01:28.675944Z"
                decision: approve
                reason: The Captain chose 「五張都准，授權代記設計關卡（建議）」 (host question dialog, 2026-11-13), answering 「獨立審查說原本的合約不能直接跑，我已照它修正（設計關卡保留、Prod 不動、每張最多 3 輪實作）。要不要用下面五張小任務開始試跑，並授權我在第一輪沒踩到停止條件時，代你記錄設計關卡通過？五張：①做新東西前先查既有的（你的首要方向，預期第一輪後會停下來問你）②設計檢查腳本遇到同名資料夾會當掉 ③合併檢查不該要求已刪除的暫存路徑 ④沒啟用學習擴充的專案不該被叫去跑學習 ⑤PR 監看不該對別台機器的任務提示。預算每張：1 implementation and 2 validation cycles。」; accepts outcome, scope and Budget as seeded and the trial route rules.
              application:
                target-stage: ideation
                state: consumed
started: 2026-11-12T17:03:29Z
---

## Scope

- Source: the Captain 「照上面這個理解，開「先查上游」這張任務」 (chat, 2026-10-23), after his correction 「這裡的問題是，做新需求時應該要先查上游，不管幹嘛都要先確認已有的東西才去評估怎樣加入新的東西。說明一下你的理解是怎樣」 and FO's restatement: before building anything new, find what already exists, say where it looked and what it found, then judge how the new part joins it; the places to look are what this project actually depends on and sits beside (its own repository, the packages or frameworks it uses, sibling projects, the third-party tools it will use, read from their own docs or source, not from a neighbour's usage); what was found decides whether the new part extends, changes or replaces it.
- Port: his global instructions "Upstream first" (check the chain, say what you checked and found) and "A sibling's usage is not a tool's contract", stated for any adopter's own chain rather than his fleet's.
- What exists: kc-dev-flow-2 implementation principles "Existing-code capability check" (this repository only, and only when existing code adds, replaces or removes a capability); FO's own dispatch text has carried a chain-check line, which adopters' FOs do not get. A grep of the kc-dev-flow-2 0.28.0 markdown and of kc-dev-flow on origin/main for an upstream-first clause found none (2026-10-23).
- Bite: none recorded in dev2, because FO's dispatch line supplied it; his global instructions record the class costing two days in his fleet.
- Rulings are existing state: the Captain 「都准」 (chat, 2026-10-23, kc-adr FO's Paseo session) to the kc-adr FO's 「准不准我在 dev2 那張任務的範圍裡加上「ADR 也算既有狀態」這一句」, whose proposed sentence was 「生效中的 ADR 也算既有狀態，worker 必須列出管到這次要動的檔案或行為的 ADR，沒有就寫「無」。」, after his 「讓 agent 務必先查既有狀態的機制，ADR也是一種既有狀態」. Related: dev2 task `adr-protected-path-guard` adds an optional ADR field listing the files it protects, which this check can read. (Bullet written by the kc-adr FO, Paseo agent 1bcf070c; the quotes are relayed from its session, not a ruling in this one; FO confirms them at this task's backlog gate.)
- Non-goals: naming any particular project's upstream in the package.
- Trial (2026-11-13): admitted by the Captain's 「五張都准，授權代記設計關卡（建議）」 (host question dialog, 2026-11-13) as one of five tasks run by hand under the trial route rules: one worker builds a working probe during ideation and continues into implementation, a different worker validates, at most 3 build rounds counted by hand; stop for the Captain on an overturned premise, spent budget, two rounds without progress or a second validation rejection, a change of scope or criterion, or a component boundary or Prod trigger.

## Budget
1 implementation and 2 validation cycles, in one package PR.

## Stop condition
- Return to the Captain after the first round with where the check sits; the alignment line makes that his to accept. Done when a worker dispatched with the candidate text states what it checked and found before designing, shown on one replayed dispatch.

## FO alignment

Alignment: needed at ideation; where the check sits (ideation principles, the seed, the gate content) is his to accept.
Result: the Captain admitted this task into the route trial with 「五張都准，授權代記設計關卡（建議）」 (host question dialog, 2026-11-13); he has not yet ruled where the check sits, so FO does not record this task's ideation gate under the grant: the probe's result and the options go to him at that gate.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
