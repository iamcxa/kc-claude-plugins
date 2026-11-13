---
title: A question to the Captain outside a gate is one record in the task's state folder, open until his answer is recorded
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:captain-question-outside-a-gate-is-an-open-record:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:captain-question-outside-a-gate-is-an-open-record-backlog-1
              briefing:
                id: briefing:captain-question-outside-a-gate-is-an-open-record:backlog:attempt-1:revision-1
                digest: sha256:1583608f505a10767ffa143043566d134b15b2fe009e1dc6cf84abe55fb7bcd9
                room-ref: ./captain-question-outside-a-gate-is-an-open-record/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:captain-question-outside-a-gate-is-an-open-record:backlog:1
                briefing: briefing:captain-question-outside-a-gate-is-an-open-record:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-11-13T16:37:09.424075Z"
                decision: approve
                reason: 'The Captain answered 「改革試驗：兩張都進設計階段」 (chat, 2026-11-14), answering 「決定：要不要讓兩張任務進設計階段，當作改革試驗（十分鐘內先回報、分鐘預算加喚醒、同一階段派第二次重來就停）的其中兩張？建議要。第一張：關卡以外問你的每一題做成一筆紀錄，答案記錄前都算待決定，先寫格式合約再實作，Bridge 那邊當只看文件的讀者。第二張：專案的架構文件有固定的版面，每個事實、裁定和想法只有一個家（這張是 11/11 另一個工作階段照你的意思建的，背後的試驗我沒有重跑過）。兩張預算都是 1 implementation and 2 validation cycles，各一個套件 PR。同意即接受：兩張都不是小修正，設計裡會有要你選的選項，所以不適用常設授權，設計關卡都由你裁定；我照試驗的三條做法回報；第二張的預算原本寫「一輪設計、一輪實作、一輪驗證」，現在的檢查不接受那個寫法，我改成上面這個；試驗另外三張是已經准入的「驗證者留下的東西能直接用」、已在設計階段等重派的「設計階段先查 RFC」，第五張之後再補。」; admits the task with outcome, scope and Budget as seeded. Recommendation: followed.'
              application:
                target-stage: ideation
                state: pending
---

## Scope

- Source: the Captain 「開「待決定事項紀錄」任務，照這個範圍」 (chat, 2026-11-13), answering FO's question 「要不要開「待決定事項紀錄」這張任務？」 whose stated scope was 「兩個專案的 FO 今天都轉述你要改善「等你決定的事」的呈現方式。開任務等於接受：我把它放進待辦，寫成「關卡以外問你的每一題是一筆紀錄，答案記錄前都算待決定」；因為寫的是 dev2、讀的是 Bridge 和 Review，會先定格式合約再實作；Spacedock 本身和任何畫面都不在範圍內。」
- Relayed, not his words to this session (two adopter First Officers, 2026-11-13): he wants what waits on him collected in one place used together with Spacedock Review and tied to Spacedock's task state and gates; and a question unanswered after two more turns should be published once as a stand-alone briefing, later turns carrying only its link. The design confirms both with him before building on them.
- What exists: since 0.40.0 (ADR 0080) FO appends one line to `<task>/asks.jsonl` when it asks him outside a scheduled gate, through the timeline helper's ask command, to count interruptions; it holds no options, recommendation, waiting party or resolution, and nothing lists open ones across tasks. Captain amendments hold his words and the bound question for a ruling that changes an approved design, written by hand afterwards. Spacedock gates hold question, summary, references and resolution, at stage boundaries only.
- Bite (FO count, 2026-11-13): FO put 18 questions to him through the host dialog in one day; only the gate-bound ones were in state as open before he answered. A reader of another repository reports, in two four-hour read-only runs on 2026-11-08, that inferring waiting items from labels and reply text counted 4 of 12 question items that were the First Officer's own step, re-admitted 5 day-old items as new in one batch of 7, and had no trustworthy waiting time for 9 to 10 of about 20 items per poll (its report, not re-read by FO).
- Contract first: the record format is a boundary between a writer (a dev2 First Officer) and readers outside this package. The design writes the format as a contract before any code, and that reader's First Officer has agreed to build a reader from the document alone and return every question it had to ask. Fields that reader says it reads or lacks: kind, a stable key and version, the bound question, who waits, since when (unknown representable), open or closed, options, FO's recommendation and grounds, whose step it is, and blocked or continuing.
- Open for the design: extend `asks.jsonl` or add a file; how an answer given in chat, in the host dialog or on Spacedock Review becomes the resolution; whether gate questions are listed by the same command from Spacedock's own gate records; the two-turn briefing rule; what the change removes or shortens.
- Non-goals: any change to Spacedock itself; any screen; deciding for the Captain; the Bridge's or Review's own reader.

## Budget
1 implementation and 2 validation cycles, in one package PR.

## Stop condition
- A blind reader built from the format document alone lists the open questions of a replayed day of this workflow with the right owner and waiting time, and every question that reader had to ask is disposed. Return to the Captain if the format needs a Spacedock change or a second file other sessions must also write.

## FO alignment

Alignment: needed at ideation; the relayed wishes above are confirmed with the Captain before the design builds on them.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
