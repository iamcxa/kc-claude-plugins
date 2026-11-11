observed | rule: "FO runs `python3 <package>/scripts/design_surfaces.py check --seed <task>`" (backlog) | evidence: "Budget must start with 'N cycles per stage'"；exit 1，屬目前格式與歷史種子不相容 (34ee229ba)。

violation | rule: "FO runs `python3 <package>/scripts/design_surfaces.py check <task>`" (ideation) | evidence: "budget-overrun-holds-and-findings-meet-non-goals.md: design needs '### Worth questions': Captain words served, what breaks without each part, and the premise's cheap test"；兩次目前重播均 exit 1，非當時違規判定 (f7aca998c、459e753db)。

ok | rule: "A Captain ruling is his reply to the question it settles" (FO steps: review findings) | evidence: "五張都核准（建議）"；question 起首「決定：第 21 批」、reason 起首「answering 「決定：第 21 批」，完整問題比對一致 (1e734670f)。

ok | rule: "A Captain ruling is his reply to the question it settles" (FO steps: review findings) | evidence: "照建議核准（建議）"；question 起首「決定：要不要核准」、reason 起首「answering 「決定：要不要核准」，完整問題比對一致 (4cbe6f81b)。

ok | rule: "A Captain ruling is his reply to the question it settles" (FO steps: review findings) | evidence: "合併，時間另開任務（建議）"；question 起首「決定：合併 #841」、reason 起首「answering 「決定：合併 #841」，完整問題比對一致 (d7ab5a9ba)。

ok | rule: "plain approval accepts that recommendation only when the gate question says so" (FO steps: review findings) | evidence: "核准即接受這三項"、"同意即接受四件沒修的事"、"Recommendation: followed." (d7ab5a9ba)。

ok | rule: "FO appends one entry per amendment" (Captain amendments) | evidence: "### Amendment 1" 至 "### Amendment 6" 均有 Captain、Asked、Supersedes；"Supersedes: AC-7" 對應保留原文與新 "AC-10" (d7ab5a9ba)。

observed | rule: "Reviewer: <agent> <model> <date> — <question>" (Stages) | evidence: "Reviewer: kc-dev-flow-2:chief-engineer gpt-6-astra 2026-11-11 — what is the smallest next step, given the findings so far?" (19409ef0a)。

ok | rule: "FO runs `python3 <package>/scripts/delivery_gate.py check` before the merge ask" (Delivery authority) | evidence: "reference:budget-overrun-holds-and-findings-meet-non-goals:validation:attempt-1:revision-1:item-2"、"2026-11-11T08:52:08Z"、"6da9a765ee04e1e2c7836517ba01f75b0ea91d73"；雜湊、head、兩項條款均一致 (b3e749c25、ca1513f83)。

ok | rule: "FO confirms both goal sufficiency and minimal necessity" (validation) | evidence: "sufficiency": "a task's Budget is read as a countable bound"；"necessity": "the fourteen files gh pr view 841 lists change against origin/main" (b3e749c25)。

ok | rule: "FO counts rounds and records the count in the committed gate summary" (FO steps: review findings) | evidence: "External rounds: 1."、"FO declines the two Codex findings and the validation finding"；三項均附理由並列入批准問題 (ca1513f83)。

can't tell | rule: "merging the full head" (Delivery authority) | evidence: "error connecting to api.github.com"；實際 PR 合併資料在 state 外，merge_audit.py exit 2 (8aaa6a083..d7ab5a9ba)。

Coverage: 完整讀取指定 README、任務歷史、FO 紀錄差異、四份 briefing、裁決 ledger、派工與合併紀錄；工人報告及大量測試附件僅取樣，未評判產品。歷史 README e8664a72 與 RULES 相同，未要求固定預算格式或 Worth questions 小節，因此重播失敗不證成歷史違規。role_triggers.py exit 0，無 next。未發現代理裁決或適用的 Precedent；Captain 引文未以同儕意見替代。批次其他成員、實際對話、發布權限、提交指令與 PR 審查實情未能核實。合併稽核未接管線，立即保存 exit 2；state fetch 失敗，僅讀本機 refs，未產生 carried 結果。缺失紀錄可能在聊天或其他 repository。觀察期間 HEAD 已前進，報告仍固定於 d7ab5a9ba。
