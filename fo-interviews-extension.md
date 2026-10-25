---
title: The dev2 maintainer interviews every FO each few batches about each extension and rule, alongside the observer
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the Captain (chat, 2026-10-26): 「紀錄一件事，等這批清完，請你訪問所有fo，跟他們了解peer ext的使用狀況，做為改進用途，任何把這個流程紀錄成一個新的ext，等於你每幾輪/批，要去訪談其他fo對於每個ext，每條規則的心得，這樣就會有兩個面向的改善資料，一個是觀察者抓犯規，一個是操作者心得。可能還可以補一個，是哪裡他們覺得現在做的很好，用來評估特殊的『核心能力』，用來改寫dev2 本身的repo readme.md。合理嗎？有沒有哪裡想補充？」
- First step he named: after batch 6 clears, interview every FO about how they use the peers extension, by hand.
- Outcome he named: an extension that has the dev2 maintainer FO, every few rounds or batches, interview the other FOs on each extension and each rule; three kinds of data: observer violations (exists), operator experience (new), and what works well, used to name dev2's core capabilities and rewrite kc-dev-flow-2/README.md.
- FO additions proposed in chat the same day (not ruled): ask about recorded events (task, date) rather than general opinions, and cross-check answers with observer reports and the decision ledger; ask which rule each FO skips or works around and why (an unenforced rule is an enforcement gap); keep a fixed short question set per extension so rounds compare; answers are data, not rulings; write one interview record per round in the state checkout and file findings as backlog tasks; run the first round by hand before building the extension.
- Upstream first: dev2 `peers` extension (how FO asks another session), `observer` agent and `learn` extension (the violation side), `decision_ledger.py`; backlog worker-knows-the-team-and-asks-early and learn-names-agents-md-candidates (related operator-side data).
- Non-goals: FOs changing each other's work; treating an interview answer as a Captain ruling.
- Ruled 2026-10-26, the Captain (chat): 「由你直接問。我問說co是因為它就是一個這樣一對多的特殊角色。但是現在先由你來問比較適合，先走幾輪看看再說。」, answering 「需要你決定：訪談由誰來問？我建議先由我直接問，用固定題目、引用具體事件來降低偏差；跑過一輪後，如果你覺得回饋太客氣，再改成由 CO 來問。」 FO's recommended shape in the same message (not ruled beyond the interviewer): name it 操作者回饋 / `fo-feedback`, not retro; a general extension like learn, used for dev2 first; one interviewer (the package maintainer) asks every FO.

## FO alignment

Alignment: needed before ideation: cadence, question set and the README rewrite are the Captain's.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
