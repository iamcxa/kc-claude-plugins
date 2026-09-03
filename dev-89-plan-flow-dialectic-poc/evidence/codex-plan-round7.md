結論：三層責任切分 sound；目前的 WHY 實作、Seam 1 與 Project語意 unsound。DEV-89 已出現反證：Captain選「四個 who bleeds」，但 office-hours要求一個實際人。

## [P0]

1. **Station 2 允許沒有特定使用者仍繼續**

   - **判定：unsound**
   - `Design STATIONS 2`：options先於free text；Captain選了全部四個persona。
   - `office-hours Q3`：要求「actual name, actual title, actual consequence」。
   - 後果：Ask UI把診斷變成多選確認，寬泛persona仍可進入Pilot。
   - 修正：選多個或只選category必須拒絕Seam 1；輸出一個discovery assignment，不建立Issues。

2. **Seam 1 丟掉WHY真正需要傳遞的內容**

   - **判定：unsound**
   - `Design THREE LAYERS`：Seam 1只有「one-line user value + profile」。
   - `office-hours Q1-Q4`需要demand behavior、status quo、特定人、wedge；Phase 3還要求已同意premises。
   - 修正：Seam 1至少包含`demand evidence / status quo / target human / wedge / premises / go|discover|stop`。一句user value不夠。

3. **Q4不能直接映射kc-dev-flow profile**

   - **判定：unsound**
   - `Design STATIONS 2`：narrowest wedge maps to POC/Pilot/Production。
   - wedge回答「做多小」；profile回答proof depth、credentials、資料、不可逆性與營運承諾。兩者不是同一軸。
   - 修正：Q4只決定scope。之後依kc-dev-flow邊界產生profile recommendation，由Captain另行選擇。

## [P1]

4. **這不是faithful office-hours，只是Q1-Q4摘錄**

   - **判定：unsound，若仍稱完整office-hours**
   - `office-hours Operating Principles`要求watch、premise challenge、alternatives及assignment。
   - 刪除Q5：失去實際觀察與surprise。
   - 刪除Q6：失去future-fit；可明確標成optional omission。
   - 刪除Phase 3：未驗證do-nothing、既有解法、distribution及premises。
   - 刪除Phase 4：直接違反`Alternatives Generation (MANDATORY)`。
   - 修正：恢復Q5、Phase 3、Phase 4與assignment；或誠實命名為`office-hours Q1-Q4 subset`，不得聲稱faithful。

5. **Station 1在需求證據前寫完整persona與感受**

   - **判定：needs a falsifier**
   - `Design STATIONS 1`先產出persona／because／feels；Station 2才問需求證據。
   - `office-hours`要求不invent pain、user words beat founder pitch。
   - 風險：先寫出的同理敘事會錨定後續答案。
   - 修正：Station 1只能產生標為unverified的hypothesis；Station 2後必須重寫。若沒有證據，不得保留`feels`推測。

6. **Project name、hypothesis與user value被混成一句**

   - **判定：unsound**
   - `Design LINEAR OBJECT SHAPES`與L9要求description if/then byte-equals`## User value`。
   - Press-release headline是benefit；if/then是solution bet；user value是使用者結果。三者不同。
   - 修正：
     - Project name：短benefit。
     - User value：`[persona] obtains [observable outcome]`。
     - Hypothesis：`If we [action]… then [outcome]`。
     - Description由User value機械投影；不要讓兩個可編輯欄位byte-equal。
   - `## Goal`也應是observable outcome，不是solution action。

7. **三層本身成立，但PLAN組合不是pm-skills原生pipeline**

   - **判定：sound，附帶命名限制**
   - `pm-skills excerpts`提供components，沒有規定problem → hypothesis → splitting的完整pipeline。
   - plan-flow可以自行組合，但必須標明順序與seams由plan-flow擁有，不能說是pm-skills流程。
   - fallback也必須產生相同schema與拒絕條件，否則是否安裝skill會改變planning authority。

8. **Milestone作recordable journey仍未定義**

   - **判定：needs a falsifier**
   - `Design STATIONS 4`：`Milestone = one recordable journey`。
   - 缺少journey起點、終點、persona、可觀察結果與Issue coverage規則。
   - 修正：Milestone只作planning grouping，不決定PR topology；lint驗證每個journey step至少被一個Issue/AC覆蓋。L7保持warning是sound。

## Receipt

9. **receipt缺少Captain approval與成本授權**

   - **判定：unsound**
   - `Design PLAN RECEIPT`只有內容hash，沒有approval record。
   - ship-flow需要知道哪個exact hash已獲核准，以及核准多少workspace、concurrency與repair rounds。
   - 修正：另建approval receipt：`receipt_sha256 / approver / approved_at / max_workspaces / concurrency / retry budget`。

10. **receipt缺少ship所需的交付位置與Project outcome文字**

   - **判定：unsound**
   - `Design PLAN RECEIPT`只有Linear project ID與`outcome_hash`。
   - ship在always-on host需要code repository、base branch及完整Project user value/outcome/exit，才能建立workspace與batch UAT。hash不能供人或agent判讀。
   - 修正：加入`code_repo / base_branch / user_value / outcome / exit`；Conductor project ID可執行時解析，不必固化。

11. **Issue `description`命名不清**

   - **判定：needs a falsifier**
   - `issues{... body_sha256, description ...}`。
   - 若description就是完整Development Brief，應明名`body`並驗證hash；若只是摘要，ship缺少worker dispatch內容。
   - 修正：receipt必須包含完整canonical Issue body或不可變content-addressed reference。

12. **receipt hash未定義canonicalization**

   - **判定：unsound**
   - `receipt_sha256`包含在receipt自身schema內，未說明是否排除自己，也未定義JSON key/order/Unicode/null normalization。
   - 修正：定義canonical JSON；hash輸入排除`receipt_sha256`欄位。

13. **verbatim Captain answers不應放在ship receipt**

   - **判定：unsound**
   - `Design PLAN RECEIPT provenance`；ship明確不讀它。
   - 它增加隱私、prompt-injection、授權與hash churn；也不是最小dispatch資料。
   - 修正：移到獨立plan rationale。receipt只保留structured premise IDs、未決問題與rationale artifact hash。需要比較時由下一輪plan-flow讀rationale，不讓ship攜帶原文。

14. **dispatch_order與edges可以保留**

   - **判定：sound**
   - edges保存依賴事實；dispatch_order固定同一DAG的機械排序。
   - lint必須驗證DAG無cycle、order涵蓋每個Issue一次，且每條edge均滿足先後順序。

## Q1

三層責任是sound；借用方式不faithful。

- WHY缺Q5、Phase 3、Phase 4與assignment後，會把「未驗證想法」直接轉成build plan。
- Q6可以省略，但要記錄future-fit未評估。
- pm-skills可作components；pipeline順序必須歸plan-flow所有。
- 若無需求證據，正確輸出應是discovery assignment，不是Linear Project。

## Q2

Unsound。三句應分開：

- Headline：可重述的customer benefit。
- User value：誰得到什麼observable result。
- Hypothesis：我們押注哪個action會造成該result。

L9應改成「description由單一User value來源生成」，而不是把hypothesis與value強制byte-equal。

## Q3

缺少：

- approved receipt hash與Captain attestation。
- spend、concurrency、retry上限。
- code repo與base branch。
- Project user value、outcome、exit全文。
- canonical body或immutable body reference。
- canonical JSON/hash規則。
- Project outcome/exit到Issue AC的coverage mapping。
- generation／canonical claim key。

應移出：

- q1–q4 verbatim answers。
- rewritten sentences明細。
- 完整lint輸出；只需lint schema/version、pass結果與digest。

## Q4

DEV-89應帶一個「polished but evidence-free」falsifier：

> 輸入一個寫得完整的平台構想，只有waitlist／「很有興趣」，沒有付費行為、現行workflow、實際姓名或觀察紀錄；Ask UI提供四個看似合理的persona，Captain選全部。

唯一正確結果：

- 拒絕Seam 1。
- 不選profile。
- 不建立Project、Issues或plan receipt。
- 明確指出demand、specific human與observation缺口。
- 產生一個可在本週執行的discovery assignment。

若它再次接受「all four」、選Pilot並開始story splitting，plan-flow不應commission。

```text
剩餘: WHY停止條件、Seam 1、三種Project語句與receipt最小schema仍需修正
下一步: 用evidence-free requirement跑DEV-89單一拒絕falsifier（你）
可收線: 否
```

tokens used: 877766
