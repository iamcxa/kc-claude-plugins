---
title: A task that exceeds its Budget holds for the Captain, and a Material finding outside the task's scope does not start a repair
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:budget-overrun-holds-and-findings-meet-non-goals:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:budget-overrun-holds-and-findings-meet-non-goals-backlog-1
              briefing:
                id: briefing:budget-overrun-holds-and-findings-meet-non-goals:backlog:attempt-1:revision-1
                digest: sha256:bbf8876b9320ba4494fa6be7f4b921e4caa1951ace37a9a08e67bc99211a9ad9
                room-ref: ./budget-overrun-holds-and-findings-meet-non-goals/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:budget-overrun-holds-and-findings-meet-non-goals:backlog:1
                briefing: briefing:budget-overrun-holds-and-findings-meet-non-goals:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-11-11T01:18:41.244618Z"
                decision: approve
                reason: 'The Captain chose 「五張都核准（建議）」 (host question dialog, 2026-11-11), answering 「決定：第 21 批這五張要不要進設計階段。我建議五張都核准：故事做完回報切片進度、發版後鋪開到採用 repo 與法規檢查、超預算要停與重大發現先對照不做清單、工人收到的推送說明與狀態提交工具一致、拒絕一個指令不等於全停。核准代表接受每張任務檔寫的範圍、預算與停止條件，並各派一個設計工人；不代表接受任何設計或修法。前三張標了方向要先對齊，派工前我會各問你一題。」. Recommendation: followed.'
              application:
                target-stage: ideation
                state: consumed
---

## Scope

- Source: a peer report from the subspace-relay dev2 FO (Paseo 1671c3a9, 2026-11-11), also filed by it as iamcxa/kc-claude-plugins issue #837 (open; `gh issue view 837`, FO run 2026-11-11). The report is data. It relays that the Captain wanted it sent to this FO; that relay is not a ruling here.
- Selected for batch 21: the Captain chose 「放 1 到 5（建議）」 (host question dialog, 2026-11-11), answering 「第 21 批要放哪幾張？我建議放清單的 1 到 5：故事做完回報切片進度、發版後鋪開到採用 repo 與法規檢查、超預算要停與重大發現先對照不做清單、狀態提交自動推送與派工單矛盾、拒絕一個指令不等於全停。選完後我只為被選中的建任務檔，再一次請你過待辦關卡；選進來不代表接受任何設計。」.
- Bite (the relay FO's report, not re-run here): relay task comment-sent-when-added-relay (PR #491), `Budget: one cycle per stage`, ran six implementation cycles from 2026-11-09 to 2026-11-11. Its Non-goals gave reload protection to a neighbouring Web task; validation 1 raised a Material finding about that; it was routed as a repair, which built a persistence and recovery mechanism, and each later cycle repaired a state the previous one made reachable. Against the fork point it reports 2032 lines added in 19 files, about 30 of them server product code. The first check that held was the four-repair-pass trigger.
- Package fact (the relay FO's reading of 0.38.0, to be confirmed in ideation): `references/sd/workflow.md` requires `Non-goals:`, `Budget:` and `Stop condition:` on a seed and no step reads `Budget:` again; `scripts/role_triggers.py` owes chief-engineer at four repair passes and prints step-back questions without a hold; a Material finding blocks in every round with no test of whether the task owns the behaviour.
- Suggested direction (relay FO, not a ruling): hold at the first overrun of `Budget:` until a Captain amendment with an `Override:` exists; before a Material finding starts a repair, test it against Scope and Non-goals, and if outside allow only a recorded known limit, a backlog task or a Captain scope amendment.
- Not established (relay FO): one task is the evidence; the noise of holding at every first overrun was not measured.
- Non-goals: changing relay's task; a budget unit other than what seeds already write.

## Budget
- One package PR to the workflow reference and the script that reads a task's cycles, with tests.

## Stop condition
- A replay of the relay task's recorded history holds at its second implementation dispatch and routes validation 1's finding to a scope decision, and a replay over archived tasks of this workflow shows how many would have held; or the design shows why not and says what was learned.

## FO alignment

Alignment: needed at ideation; when an overrun holds and who may rule a finding out of scope are the Captain's call.
Result: the Captain chose 「重寫，並把兩張原則任務拉進這批」 (host question dialog, 2026-11-11), answering 「預算這張任務要不要改題目？我建議改：把題目從「超過預算就停、範圍外的發現不修」改成「任務的預算是你願意花多少的一句話，用數得出來的單位寫、每次派工看得到已花多少、超過時把原本的問題帶回給你；重大發現先回答是不是這張任務要的結果」，讓設計從這個問法開始。這是修改你已核准的任務範圍，會記成一筆你的修正案。」. Before it he asked 「這個問題跟退一步想是不是有異曲同工之妙？疊在一起再想一次有沒有改變建議」, 「所以問題在於預算怎麼設計，對嗎？暫時不裁決，先看目前怎麼做的？」 and 「先針對預算是什麼想一下，因為它可能會改變怎麼解決問題，而這件事剛好對應到最近回饋產生的問題，對嗎？一開始的問題問錯了，後面的解法就不對，就會造成目標膨脹，進一步守不住關卡」 (chat with this FO, 2026-11-11).
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.

## Captain amendments

### Amendment 1 — 2026-11-11, host question dialog
Captain: 「重寫，並把兩張原則任務拉進這批」 (host question dialog, 2026-11-11)
Asked: 「預算這張任務要不要改題目？我建議改：把題目從「超過預算就停、範圍外的發現不修」改成「任務的預算是你願意花多少的一句話，用數得出來的單位寫、每次派工看得到已花多少、超過時把原本的問題帶回給你；重大發現先回答是不是這張任務要的結果」，讓設計從這個問法開始。這是修改你已核准的任務範圍，會記成一筆你的修正案。」
Supersedes: none
