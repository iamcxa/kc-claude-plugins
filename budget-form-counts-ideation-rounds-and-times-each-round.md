---
title: The task budget counts ideation rounds, and the timeline helper reports each round's times and result
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
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
