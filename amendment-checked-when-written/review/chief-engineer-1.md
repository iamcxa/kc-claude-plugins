# Chief Engineer advice — amendment-checked-when-written

2026-11-10。建議：保留已核准的七次歷史事件與逐次推送檢查；由 FO（流程執行負責人）正式處置 F2（不可讀檔案吞掉其他診斷）為 Deferred risk（尚無實際觸發的風險），只對 F3（程式範例冒充有效標記）進行有界修復。兩項都可用人工輸入重現，兩項都沒有在本次查閱的真實任務歷史中找到同形案例；這不使它們自動同級：F2 的例外路徑仍明確失敗，F3 則讓可解析的任務在違反既有標記規則時通過。

這是 `kc-dev-flow-2:chief-engineer` 的路線建議，不是新的驗證裁決、風險接受、修復授權或關卡決定。既有兩份 REJECTED 報告完整保留；Captain（決策負責人）裁定範圍與風險，FO 處置及派工。沒有理由僅因驗證退回兩次就刪除已有真實事故支持的規則，也沒有理由把每個可構造反例都升格成必修事故。

```yaml
chief_engineer_advice:
  outcome: 在狀態推送時指出已寫入的驗收條件編號重用或缺少修訂標記，保留七次真實歷史事件覆蓋
  next_step: FO 分別處置 F2 與 F3 後，只派一次 F3 的 L4 輸入過濾修復，保留既有標記判定與歷史事件規則
  material_risk: 若修復擴及共用 unfenced 或既有 design check 語意，會越過已承諾的相容性邊界
  decision_needed: FO 決定證據分類並另行授權修復；只有縮減驗收、接受 F3 漏報或擴大相容性變更才需 Captain 裁定
  defer:
    - F2 的不可讀檔案部分診斷保留與恢復機制，直到有實際觸發或 Captain 要求
    - 通用 Markdown 解析器整理與其他呼叫點修改
    - 已核准延後的發版、採用版本更新與 hosted 執行證據；完成前任務仍不能關閉
  recommendation: adjust
```

## 證據與權限範圍

- 候選版本：`d7502656c765e36ce3d24be8602862ccc2551254`，產品分支 `spacedock-ensign/amendment-checked-when-written`，基準 `6a495cb8c4055f9a6eba8a05419c2d2fad1a90f1`。本次開始及寫報告前均確認產品工作樹乾淨，HEAD 與派工相同。
- 工作根目錄：`/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree`。產品位於其 `.worktrees/spacedock-ensign-amendment-checked-when-written`；狀態庫是 `docs/dev2/.spacedock-state`，分支 `spacedock-state/dev2`，讀取時 HEAD 為 `bfffd196014d24af9e7f693db053d345fb1f8dfe`。上層工作樹既有 `.gitignore` 修改未碰觸。
- 以下 `task` 指 `docs/dev2/.spacedock-state/amendment-checked-when-written.md`；`v1`、`v2` 分別指同名任務資料夾內 `validation/cycle-1/`、`validation/cycle-2/`。AC 是驗收條件；L4 是本次新增的第四條狀態規則；ADR 是已接受的架構決策紀錄。
- 已讀 task 的 Scope、Design、兩次 Captain amendments、Feedback Cycles、兩份驗證與修復報告；workflow README 的 Review-finding disposition；ADR 0005、0016、0017、0026、0027、0057、0064，以及候選產品來源。
- 本次只讀 Git 與候選程式，以 `python3 -B` 執行無檔案寫入的歷史檢視及記憶體探針；只寫本報告。未執行會建立暫存 Git 庫或輸出檔的 `v2/acceptance.sh`、`review-probes.py`，未重跑整套驗證。其完整命令列結果是既有驗證者收據，不冒稱本次重新驗證。未查遠端新狀態、發訊息、改 PR、提交或推送。

## 三個退一步問題

### 1. 現在解的仍是最初要求的結果嗎？

**核心仍相同；兩項新發現是原規則的邊界情境，不是新的使用者成果。** task Scope 的原始事故是：

> “FO rewrote AC-1, AC-2 and AC-4 in place under reused ids (state a113aa3e9); design_surfaces.py caught it only when the implementation worker ran it.”

Stop condition 要求：

> “Committing a task whose amendment reuses an id or lacks the 'Amended by Captain, amendment N' marker is refused or flagged at that commit, with a falsifier.”

核准設計已選擇「推送後逐提交標出」，不是攔下本機提交；其限制也已在 ideation 關卡問句明說。因此缺少提交前拒絕不是本次要追加的新工作。L4 僅在 `Superseded text:` 已出現時判定，無搬移的原地重寫仍是已接受的限制，不可把現有修復說成攔住所有改寫。

原始事故確實已被目前候選抓到：本次直接在真實 `b91e7434adde..a113aa3e9` 範圍呼叫候選 `walk()` 與 `l4_amendment_moves_use_fresh_ids()`，取得一個事件，分別列出重用 `AC-1, AC-2, AC-4` 與缺標記，提交為 `a113aa3e9a3d`。這是 L4 局部讀取，不是整個命令列或 hosted 推送證明。

兩次修訂也不是任意擴張：第一次因設計中的整檔跳過而改成五次，第二次發現漏掉的兩次沒有被其他規則接住，Captain 明說：

> 「這張就做到 7 次」

因此目前的交付基準是七次真實事件，不是只要原始一次通過就可收。`v2/README.md`、`corpus-comparison.json` 與 task 最新驗證記錄指出七次保留、F1（部分修復重報舊編號）已修好；本次未重跑全套七事件驗證。

### 2. F2、F3 現在能對真實已發生案例測試，還是只能對人工輸入？

**兩項的直接失敗收據都是人工輸入；目前沒有同形的真實任務案例。** 我以 `v2/corpus-inputs.json` 的三段固定歷史，讀取非合併提交修改過的任務檔新舊 blob，依候選 `amendment_slug()` 篩選、排除 README，以 blob 去重。命令是唯讀 `git log --no-merges --format=%H --raw --no-abbrev --no-renames <before>..<after> -- '*.md'` 加 `git cat-file --batch`，對內容嚴格 UTF-8 解碼並搜尋行首波浪號圍欄。沒有建立或修改任何歷史。

| 歷史 | 固定範圍 | 不重複任務 blob | 含搬移文字 | 非 UTF-8 | 波浪號圍欄 |
| --- | --- | ---: | ---: | ---: | ---: |
| dev2 | `166c16d968305ad711481276809433a15fcf8a5e..2a42fbb15e0f0509b4084370850f730e6334a983` | 3855 | 654 | 0 | 0 |
| qnow | `4a37fda441f2eb71ff8b3c2b9886983cb46c3e5f..c36650727548d893324aad22723fd530bc900570` | 2873 | 261 | 0 | 0 |
| relay | `22a3ef1cad0677b8cc2ef3890ead67ff26cfd071..fd1481da62952ed6706bb3c1db4620ee1b04b144` | 2539 | 270 | 0 | 0 |

這些是不同任務內容版本的計數，不是事件數或使用者數；也不是全世界或目前遠端都不會發生的證明。它覆蓋驗證所用的固定歷史，不能用零次推算未來機率。

- F2：`v2/review-probes.py` 明確把無關 `z.md` 寫成 `b'\xff'`。`review-probes.json` 顯示單獨有效任務移動有診斷、同次推送混入該檔後 exit 2 且 L4 只印 cannot-judge、下一次修正該檔仍因父版本不可讀而 exit 2，之後無關修改 exit 0。失去的是該次輸出的具體診斷，不是第一次就假綠；Git 內的原始提交仍在，並非再也無法檢視或以原範圍調查。
- F3：同一探針建立無標記的有效替代條件，再在驗收區放一段 `~~~md` 範例，其中的假 `AC-9` 帶標記。收據顯示 exit 0；只換成反引號圍欄就 exit 1。本次另以相同內容在記憶體直接呼叫候選函式，`move_defects` 對反引號回傳 `[("unmarked", 1)]`、對波浪號回傳 `[]`；兩者 `parse_amendments` 都沒有結構問題。這證明可解析輸入的判定不一致，仍不冒稱有實際使用者已踩到。

### 3. 刪掉或縮窄各發現所依據的條件，或刪掉整條逐推送規則，會壞什麼？

- **F2 所依據的 AC-3：** 保留「新事件只報一次」的規則，但明說無法讀取時整條規則可能只給 cannot-judge，現有反例仍紅燈；代價是操作者要自行調查原推送，不能依靠同一輸出取得所有已知違規。不要為拒修 F2 而刪掉 AC-3：那會容許已修好的 F1 重現，也會動到 ADR 0017「only the events the commits of the push add … reported once」。若要新增「即使不可讀也保留其他任務診斷」的強保證，需明確承擔該額外恢復行為，而不是假定已由七次歷史事故證明需要。
- **F3 所依據的 AC-2／L4 Rule：** 刪除缺標記判定會直接失去原始事故的一條診斷，也放掉 ADR 0016 已有真實案例支持的標記要求。只縮成「不支援波浪號範例」雖保留既有七次，但必須把可解析範例當成有效條件或另拒絕該格式；目前沒有這項使用限制。`laws.md` 說的是 “a live criterion or another entry's moved declaration”，並非「任何看起來像標記的範例」。接受目前假綠需 Captain 裁定風險，不宜由 FO 以沒在歷史看過就自行縮窄承諾。
- **整條 L4：** 原始事故又回到等工作者／關卡執行 `design_surfaces.py check` 才看到，違反本任務「寫入時被標出」的成果。task 設計既有七事件調查記錄「Only 1 of the 7 commits added a dispatch record」；改成只在派工檢查也不能宣稱等價。既有 ADR 0017 的一次性推送語意已承認錯過失敗通知就沒有後續提醒；這是接受過的限制，不是本次重做歷史監控的理由。

## 逐項四欄評估：建議而非處置裁決

### F2 — 建議 Deferred risk；不建議目前另開修復輪

1. **使用者與正常流程：** 採用套件的 FO 推送多個文字任務並處理失敗通知是正常流程；但探針要求把單一不可解碼位元組提交成任務檔，尚無真實流程／產生工具案例。已承諾的不可讀行為是 cannot-judge，不是成功繼續判完整批次。
2. **可見損害：** 人工重現的損害成立：先算出的可讀任務違規被丟掉；修不可讀檔後的預設新範圍不補報。兩個相關推送仍 exit 2，不應將其描述成沒有任何警告或可直接接受的成功結果。
3. **受保護邊界：** `value-ac[AC-3]` 要求新事件歸屬正確；但 `contract[kc-dev-flow-2/references/sd/laws.md#l4-amendment-moves-use-fresh-ids]` 明定 “Unreadable blobs or ambiguous path matches yield cannot-judge (exit 2).” ADR 0017 也不保證無法判定時全面成功。已知診斷保留值得改善，但現有證據不足以證成「不可讀批次仍完整報出其他事件」是當前必交保障。Captain amendment 2 要求的是可讀檔案內逐筆跳過結構壞掉的修訂，不等於要求還原不可讀 bytes。
4. **觸發證據：** `v2/review-probes.py` 與 `review-unreadable-{solo,combined,repair,later}.log`；固定三歷史未見非 UTF-8 任務。若真實推送出現同形遺失、既有寫入工具會產生該輸入、或 Captain 要求不可讀批次也保留可判定診斷，重新評估為 Material（當前承諾受到實質損害）。

與驗證者不同之處在正常觸發／承諾範圍，**不是否認程式會丟掉已收集診斷**。FO 如採此建議，應綁定候選 `d7502656...`、`laws_check.py` 的 L4 函式／`amendment_blob` 與上述收據，依 README 記錄 decline（有理由的不修決定）；不得改寫驗證者報告、標成已修或自動增加待辦。若 FO 無法接受此分類，先交 Captain 決定，不先修。

### F3 — 建議 Material、由本任務承擔；不要擴成通用解析器工程

1. **使用者與正常流程：** 工作者在 Markdown 任務中保留範例與搬移條件。這次組合尚未在三歷史出現，但候選自己的修訂解析器明確識別兩種圍欄，並且此輸入通過該解析器；它沒有落入已宣告的不可讀／結構壞掉例外。可解析範例不應成為正式替代條件。
2. **可見損害：** 真正替代條件沒有標記，卻因範例中的標記而讓引入違規的推送 exit 0。這是可重現的假綠，保護的是實際標記規則，並非單純格式美化。
3. **受保護邊界：** `value-ac[AC-2]` 的無標記移動必須報違規；`contract[kc-dev-flow-2/references/sd/laws.md#l4-amendment-moves-use-fresh-ids]` 要求有效條件宣告或另一筆搬移宣告帶標記；ADR 0016 保留同一語意。人工反例與既有來源的語法支持一起建立邊界違反；沒有歷史發生率，不代表需等真實漏報後才能修。這裡不推論所有 Markdown 變體都必須新增支援。
4. **觸發證據：** `v2/review-example-{backtick,tilde}.log`、`review-probes.json`；本次記憶體對照同樣證明兩個合法解析結果的判定差異。來源是 `design_surfaces.py:419` 的 `section(unfenced(lines), AC_HEADING)`，而 `unfenced` 只辨識反引號；`parse_amendments` 的 `AMENDMENT_FENCE` 同時辨識反引號與波浪號。

最小修復邊界是 **L4 的有效宣告輸入**，共用 `unmarked` 判定仍只有一份，既有 `check_amendments` 行為不動。不應直接改共用 `unfenced`，因它有其他呼叫者，會擴大 AC-6（保留既有檢查相容性）的影響。由工作者先調查並提出窄修，FO 再獨立授權；如果做不到這個邊界，停止並把相容性選擇交 Captain，而非悄悄變更設計。

這兩項並非同一個小函式的反覆失敗：F2 是整條規則的例外回傳捨棄結果，F3 是宣告來源過濾不一致。不要以共同出現在 L4 就推導必須整體重寫。

## Captain 可選的路線與代價

| 路線 | 得到什麼 | 變差之處／決定者 |
| --- | --- | --- |
| **拒修 F2、只修 F3（建議）** | 保留七次、一次性事件與既有標記承諾；只補可解析輸入的假綠 | 不可讀批次仍可能只給不能判定訊息，須調查原推送。FO 可在既有邊界內分類與授權；若把這視為新增風險接受，交 Captain，不可自行變更 AC |
| 兩項現在都修 | 額外保留不可讀批次中已知診斷，也排除範例冒充 | 增加尚無實際觸發的例外處理及測試範圍，延後採用；七次事故並沒有證明 F2 恢復機制必需。需分開授權，不能以修 F3 偷帶 F2 |
| 兩項都拒修，或只拒修 F3 | 最快保留目前候選交付路線 | 接受可解析任務因範例標記而假綠；這牴觸現有語意，需 Captain 明確接受並留下原因，不能靠 Deferred risk 名稱繞過 |
| 縮窄成只處理第 17 批原始事故 | 驗收最窄、該事故已可抓到 | 撤回「這張就做到 7 次」及一般缺標記／事件規則的部分承諾；只證明單一樣本。必須由 Captain 修訂驗收，FO 不可自行改成一個歷史案例就算完成 |
| 擱置整張 | 不再投入修復，保留目前候選與報告 | 原寫入時檢查缺口繼續存在，L4 未啟用；已花的工作不能轉成日常保護。Captain 決定停止／排程，不可稱已交付 |

若 Captain 要親自裁定，一次只問路線：**保留七次與標記承諾，先不修 F2、只修 F3，是否接受？** 不同時綁採用版本更新或合併批准。這份報告本身不向 Captain 發問，也不建立新關卡。

## 最小後續與完成界線

FO 先在既有流程記錄兩項各自的理由與候選；之後一次有界 F3 修復應以波浪號／反引號對照拒絕假標記，保留有效標記、豁免與未搬移記錄的合法結果，並維持已修 F1 及七次歷史事件。獨立驗證針對新候選與受影響證據，不因本建議重新跑無關調查或改寫過去的失敗。

`AC-7` 仍明文要求發版後更新採用 pin（固定套件版本），並看見一次 hosted 狀態推送的 L4 輸出。現在的本機證據、F2 處置或 F3 修好都不代替該步；也不授權合併、發版或採用。CI（自動檢查）每 PR／每狀態推送成本未量測，本報告未改 job、trigger 或 pin，不聲稱節省成本。

本次唯一產物為本報告；產品、任務條件、先前報告與裁決均保持原樣。
