---
title: A worker whose command is denied keeps working on everything the denial did not cover
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:denied-command-denies-only-that-command:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:denied-command-denies-only-that-command-backlog-1
              briefing:
                id: briefing:denied-command-denies-only-that-command:backlog:attempt-1:revision-1
                digest: sha256:5e90859c0bda53830c6e3722375635673ab295ffa15f3f1e2e989ee026e9e6d3
                room-ref: ./denied-command-denies-only-that-command/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:denied-command-denies-only-that-command:backlog:1
                briefing: briefing:denied-command-denies-only-that-command:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-11-11T01:18:55.268444Z"
                decision: approve
                reason: 'The Captain chose 「五張都核准（建議）」 (host question dialog, 2026-11-11), answering 「決定：第 21 批這五張要不要進設計階段。我建議五張都核准：故事做完回報切片進度、發版後鋪開到採用 repo 與法規檢查、超預算要停與重大發現先對照不做清單、工人收到的推送說明與狀態提交工具一致、拒絕一個指令不等於全停。核准代表接受每張任務檔寫的範圍、預算與停止條件，並各派一個設計工人；不代表接受任何設計或修法。前三張標了方向要先對齊，派工前我會各問你一題。」. Recommendation: followed.'
              application:
                target-stage: ideation
                state: pending
---

## Scope

- Source: item 3 of a peer report from the qnow dev2 FO (Paseo 519ab4c8, 2026-11-10), which states its Captain approved handing it over (「要」, relayed, not a ruling here).
- Selected for batch 21: the Captain chose 「放 1 到 5（建議）」 (host question dialog, 2026-11-11), answering 「第 21 批要放哪幾張？我建議放清單的 1 到 5：故事做完回報切片進度、發版後鋪開到採用 repo 與法規檢查、超預算要停與重大發現先對照不做清單、狀態提交自動推送與派工單矛盾、拒絕一個指令不等於全停。選完後我只為被選中的建任務檔，再一次請你過待辦關卡；選進來不代表接受任何設計。」.
- Bite (qnow FO's report, not re-run here): Codex workers on gpt-6.1-sol and gpt-6-astra read an FO permission denial as a stop of the whole task, announced the commit was refused and began cleanup after a denial that removed one flag; five times across two qnow tasks on 2026-11-10, each needing an explicit steer to keep going.
- Related in this workflow (FO observed, 2026-11-11): the subspace-web sync worker, refused a push by Codex auto-review, stopped and asked the Captain for authorization with a button instead of returning the commit to FO; a later dispatch that said to report the commit to FO did not repeat it.
- Package fact to confirm in ideation: kc-dev-flow-2 0.38.1 extensions/paseo/EXTENSION.md "Worker permission requests" tells FO how to answer a request; FO found no worker-facing sentence on what a denial covers (read 2026-11-11).
- Non-goals: changing which requests FO allows or holds; Codex auto-review's own rules.

## Budget
- One package PR adding the worker-facing words where a dispatched worker reads them, within the workflow word budget or with a named raise for the Captain.

## Stop condition
- A Behaviour replay of a dispatch in which one command is denied shows the worker at the candidate continuing the rest and reporting the denied step, where the worker at the released tag stops; or the design shows why not and says what was learned.

## FO alignment

Alignment: not needed before ideation; the Captain approved filing it and the outcome is one worker-facing rule.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
