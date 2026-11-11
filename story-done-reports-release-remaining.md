---
title: When a story's task is archived, FO tells the Captain how much of the release remains, and the story shows the pull requests that finished it
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:story-done-reports-release-remaining:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:story-done-reports-release-remaining-backlog-1
              briefing:
                id: briefing:story-done-reports-release-remaining:backlog:attempt-1:revision-1
                digest: sha256:bc068bffc4730bd93d2deb7690dcb9ecf6c545c3f8ed5c5f68a3b3849b8252ab
                room-ref: ./story-done-reports-release-remaining/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:story-done-reports-release-remaining:backlog:1
                briefing: briefing:story-done-reports-release-remaining:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-11-11T01:18:27.351416Z"
                decision: approve
                reason: 'The Captain chose 「五張都核准（建議）」 (host question dialog, 2026-11-11), answering 「決定：第 21 批這五張要不要進設計階段。我建議五張都核准：故事做完回報切片進度、發版後鋪開到採用 repo 與法規檢查、超預算要停與重大發現先對照不做清單、工人收到的推送說明與狀態提交工具一致、拒絕一個指令不等於全停。核准代表接受每張任務檔寫的範圍、預算與停止條件，並各派一個設計工人；不代表接受任何設計或修法。前三張標了方向要先對齊，派工前我會各問你一題。」. Recommendation: followed.'
              application:
                target-stage: ideation
                state: consumed
started: 2026-11-11T01:22:31Z
---

## Scope

- Source: the Captain 「我有個需求/想法，我覺得每張票作完之後，如果有同時有跑地圖ext，那應該要每張故事票做完就告訴我這個切片還剩下多少，這樣我才能知道離終點多遠。因為像是relay那邊一次要做兩個切片，已經做了大概兩天，但我如果沒有主動問就沒辦法知道做到哪裡了。這裡也要評估是否每個故事做完就同步更新畫布與地圖，更快反應狀況。以及，是否地圖應該記錄某個故事是因為哪些pr完成才完成的？等於切片地圖可以連結到完成它的pr？適合嗎？」 (chat with this FO, 2026-11-11).
- Selected for batch 21: the Captain chose 「放 1 到 5（建議）」 (host question dialog, 2026-11-11), answering 「第 21 批要放哪幾張？我建議放清單的 1 到 5：故事做完回報切片進度、發版後鋪開到採用 repo 與法規檢查、超預算要停與重大發現先對照不做清單、狀態提交自動推送與派工單矛盾、拒絕一個指令不等於全停。選完後我只為被選中的建任務檔，再一次請你過待辦關卡；選進來不代表接受任何設計。」.
- Package fact (FO read 2026-11-11): kc-journey-map skill kc-journey-progress runs `lib/journey-progress.mjs <journey.yaml> --workflow-dir <dir> [--draw <room>]` only "when explicitly refreshing"; kc-dev-flow-2 0.38.1 extensions/journey-map/EXTENSION.md joins FO at three points (a ruling answering a map question, before merge guard, after archive) and none runs the progress reader or reports to the Captain. `grep -n "pr\\b\\|pull" kc-journey-map/lib/progress.mjs` printed nothing (FO run 2026-11-11), so the observation carries no pull request.
- Known dependency (the backlog task journey-map-progress-and-provenance, its relay evidence of 2026-10-14, not re-read on relay today): no relay story carried `journey-required-tasks`, so the reader reports every story unverified there. The design says how a task joins its story's declaration when it is approved into the story, or names another way the count becomes real, and says what it takes from that task and what it leaves.
- FO's assessment given to the Captain in chat (not a ruling): report after each archive and redraw the canvas; keep progress derived from task state instead of writing it into the map file; derive story-to-PR links from each task's `pr:` value instead of storing them in the map.
- Surface note: this seed records no surface. If the design adds or changes anything a person sees on the canvas (a link, a mark), ideation records the `ui` surface and what it owes before its gate.
- Non-goals: the evidence ladder, ADR references and drawing provenance of journey-map-progress-and-provenance; one journey spanning several workflows; a background refresh.

## Budget
- One PR to kc-journey-map (reader output and canvas) and one to kc-dev-flow-2 (the journey-map extension step), or one PR if the design shows they cannot be split.

## Stop condition
- On a real adopter map with at least one declared story, archiving that story's last task makes FO report done and remaining stories for the release with each finished story's pull requests; or the design shows why not and says what was learned.

## FO alignment

Alignment: needed at ideation; what FO reports, whether the map file stores anything, and how much of journey-map-progress-and-provenance this takes are the Captain's call.
Result: the Captain chose 「交給設計比較」 (host question dialog, 2026-11-11), answering 「「故事做完回報切片進度」這張任務的設計方向要怎麼定？我建議：每張故事票歸檔後 First Officer 主動回報切片完成與剩餘並重畫畫布；進度和 PR 連結都從任務狀態現算、不寫回地圖檔；並把「任務獲准進入故事時自動記進故事的宣告」包進來，讓 relay 算得出數字。這是設計的方向，細節與證明仍在設計關卡由你核准。」. FO's recommendation was not taken: the design compares the choices and he picks at the ideation gate.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
