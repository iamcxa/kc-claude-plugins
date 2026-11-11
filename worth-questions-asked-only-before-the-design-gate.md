---
title: A design that already passed its ideation gate is not refused for lacking Worth questions
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:worth-questions-asked-only-before-the-design-gate:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:worth-questions-asked-only-before-the-design-gate-backlog-1
              briefing:
                id: briefing:worth-questions-asked-only-before-the-design-gate:backlog:attempt-1:revision-1
                digest: sha256:1febe145cd7435b0610d9ca5fcab90f562097141bde4af179b0a986f2782d787
                room-ref: ./worth-questions-asked-only-before-the-design-gate/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:worth-questions-asked-only-before-the-design-gate:backlog:1
                briefing: briefing:worth-questions-asked-only-before-the-design-gate:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-11-11T14:24:06.311538Z"
                decision: approve
                reason: 'The Captain chose 「核准（建議）」 (host question dialog, 2026-11-11), answering 「決定：要不要讓「已經過了設計關卡的舊任務不被『值不值得』檢查擋下」這張修正任務插隊進入設計階段。我建議核准。核准代表接受任務檔寫的範圍（只改檢查在什麼時候要求那一節，不動三個問題的內容、不動預算規則、不補寫任何已核准的設計）、預算（設計、實作、驗證各一輪，一個 PR）與停止條件（我這邊三張被誤擋的任務在新版通過檢查、還在設計階段又沒寫那一節的任務照樣被擋，而且我在請你合併前，先在合併進 main 之後的結果上把整組測試指令全部重跑一次），並派一個設計工人決定「過了設計關卡」要從哪裡讀出來。不代表接受任何修法。」. Recommendation: followed.'
              application:
                target-stage: ideation
                state: consumed
---

## Scope

- Source: the Captain chose 「不擋，開優先修正（建議）」 (host question dialog, 2026-11-11), answering 「已經過了設計關卡的舊任務，要不要被新的「值不值得」檢查擋下？我建議不要：開一張優先修正任務，讓檢查只在任務還沒過設計關卡時要求那一節，發一個修補版（0.39.1）再同步到 kc-claude-plugins 和 qnow。理由是那些設計是你已經核准過的，事後要求補寫等於改動你核准的文字；變差的是這些進行中的任務不會被問到那三個問題，而且要再跑一輪修正和發版，這期間兩個 repo 裡走到驗證關卡的任務會先卡著。」
- Bite (FO reproduced 2026-11-11 with `scripts/design_surfaces.py check`): on kc-dev-flow-2 0.39.0 the check exits 1 with `design needs '### Worth questions'` for `adr-required-statement` and `merge-guard-stops-unasked-merges` (validation) and `archive-waits-for-observer-report` (implementation) in this workflow, whose designs passed their ideation gates before the release; on 0.38.1 the same three print no such line. An adopter's FO reported the same on a task between implementation and validation (peer message, 2026-11-11), which is how it was found.
- How it shipped: PR #841's validation-2 report recorded it as F1 Deferred risk needing a Captain compatibility decision; FO described it to the Captain at the #841 merge ask as affecting only designs not yet through the design gate, and did not run the check on a task past ideation before the release.
- Outcome: `design_surfaces.py check` requires the Worth questions section only for a task that has not yet passed its ideation gate; a task past that gate is not refused for lacking it, at any later stage; a task still in ideation is refused as today.
- Open for the design: what "passed its ideation gate" is read from (the task's stage, its gate records, or its first dispatch record as the Budget exemption does), and what happens when that cannot be read; the design shows the choice by replaying this workflow's and an adopter's in-flight tasks at pinned commits, with counts of tasks released and tasks still refused.
- Non-goals: the two Codex findings and the fifteen sibling findings left unrepaired at the #841 merge ask; any change to what the three questions ask or to the Budget rule; backfilling any approved design.

## Budget
1 cycle per stage, in one package PR to `kc-dev-flow-2/scripts/design_surfaces.py`, its tests and, if the design shows ADR 0077's words exclude the outcome, that ADR.

## Stop condition
- The three tasks named under Bite pass the check at the candidate and a task in ideation with no Worth questions section is still refused; the full kc-dev-flow-2 test commands pass on the result of merging the candidate with main, run by FO before the merge ask. Return to the Captain if the fix needs a change to what a task still in ideation must answer.

## FO alignment

Alignment: not needed: the Captain ruled the direction in the question quoted under Scope; how the gate is read is a design detail he approves at the ideation gate.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
