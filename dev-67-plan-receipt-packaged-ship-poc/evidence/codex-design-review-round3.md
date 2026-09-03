結論：plan POC 可進下一輪；ship POC 不可 commission。它實際證明了兩個結構問題：相依 PR 並未形成 native stack，而且 holder 移轉沒有防雙主機制。

## P0

1. **三個相依 PR 全部 base main**

   - 情境：上層包含下層 commit，三個 Draft PR 卻都對 main。
   - 錯誤：PR diff 重疊；它們不是 native stack，也不能證明原子落地。`merge-tree` 對 main tip 更沒有驗證實際下層 base。
   - 最小修正：blockedBy 只決定 dispatch 順序。多 Issue 各自從 main 交付；若程式碼真的必須堆疊，改成一個 Issue 的多 layer delivery。

2. **C3 layer freeze 自相矛盾**

   - 情境：上層已基於下層 SHA-A；下層 review 要求改成 SHA-B。
   - 錯誤：「freeze」說不能改；「重派所有上層」又允許改，而且會新增 workspace、claims、branches及成本。
   - 最小修正：最簡單規則是下層完全 verify 並封存後才 dispatch 上層。若保留推測式平行工作，必須作廢整個上層 generation，再經 Captain 核准重新花費。

3. **C4 執行 worker 提供的 verbatim command 不安全**

   - 情境：`WITHOUT_IT` 讀取 `$HOME`、credential files、SSH agent或直接連網；它不需要環境變數中的 secrets。
   - 錯誤：只 unset credential variables 不構成 sandbox，也不能防自證式 command。
   - 最小修正：使用臨時 HOME、無 credentials、無 agent、無網路的隔離環境；移除 patch 與 command 必須是核准 receipt 的資料，不可只信任 PR body。

4. **C6 holder 移轉會產生雙主**

   - 情境：laptop 睡眠後 always-on host 接管；laptop 醒來繼續舊 bash loop。
   - 錯誤：兩邊都可能先做外部動作、之後才由 Git push conflict 發現衝突。Git branch 不是 writer lock。
   - 最小修正：使用隔離代號（每次移交遞增的 writer 編號）；每個外部動作前驗證代號。舊 holder 永久失去該代號。

5. **S1 的 grace 是時間猜測**

   - 情境：workspace 顯示 ready、session 顯示 idle，但訊息接收端仍未完成。
   - 錯誤：延長 grace 只降低機率，不能建立交付保證。
   - 最小修正：訊息帶 dispatch token；必須在完整 transcript 中讀回相同 token，才算送達。無 acknowledgment 就停止，不能猜。

6. **carrier branch 是未列入合約的交付通道**

   - 情境：task text 被 commit、push 到 repository，再由 worker `git show`。
   - 錯誤：內容永久留在 Git objects；可能洩漏 Brief，還增加 branch mutation、清理及權限問題。
   - 最小修正：優先使用可確認讀回的 Conductor message。若保留 carrier，Captain approval 必須綁定 repo、ref、content hash與資料公開風險；不得稱為可真正刪除。

## P1

7. **C2 claim 還需證明原子性**

   - 情境：同機兩個程序同時建立 claim，或 create 成功但回應遺失。
   - 錯誤：普通 file write 不保證 exclusive create；name lookup 也可能受延遲影響。
   - 最小修正：原子 exclusive create、共享唯一索引、dispatch token lookup；不確定時永久凍結 generation。

8. **S5 不能推導出「LLM review 永久 load-bearing」**

   - 情境：下次 reviewer 漏掉同類 secrets、parser或pin問題。
   - 錯誤：一次成功找錯，只證明這次 review 有價值，不證明它是可靠 gate。
   - 最小修正：保留 review，但把已重現的四類問題轉成 deterministic checks；review處理尚未機械化的風險。

9. **S6 的 blanket scope-out 規則錯誤**

   - 情境：review 發現 Brief 外的 credential leak或資料破壞風險。
   - 錯誤：只列給 Captain仍允許不安全候選繼續。
   - 最小修正：Brief 外一般改善可 scope out；security、data loss、compatibility break與候選造成的回歸必須 block。

10. **S8/S13 字串定位仍可誤中**

   - 情境：相同兩行出現在 fenced example、blockquote或第二個 Evidence section。
   - 錯誤：substring search仍可選錯 evidence。
   - 最小修正：解析 Markdown；要求唯一、頂層 `## Evidence`，其直接內容恰有一個合法 SHA。加入 duplicate/fence/quote falsifiers。

11. **S12「改用 Python」不是完整保證**

   - 情境：Python producer仍把 `\\n` 解碼成 newline，或重新編碼內容。
   - 錯誤：換語言不等於 byte preservation。
   - 最小修正：寫入後重讀並比對 byte hash；用包含 `\\n`、backticks、`$()`與Unicode的 fixture。

12. **時間結果否定原始成本假設**

   - 情境：POC 1 為 41/15 分鐘；POC 2 為 104/60 分鐘。
   - 錯誤：原 commission 容量與 repair budget不可信。
   - 最小修正：先縮小 ship scope或正式重設上限；不能把兩次超時當 incidental noise。

## C1–C6 判定

| 結論 | 判定 | 原因 |
|---|---|---|
| C1 lint與receipt | 需要 falsifier | 只刻意擊中4條；其餘規則未見失敗。receipt還需 schema version、canonicalization及完整 title hash |
| C2 claim-first recovery | 需要 falsifier | 順序正確，但 exclusive claim、eventual lookup及雙程序尚未證明 |
| C3 layer freeze | 不成立 | 已觀察到下層修復破壞上層 base；「重派全部」缺 generation與新支出授權 |
| C4 verify contract | 不成立 | verbatim command不安全；dependent candidate卻只對 main preflight |
| C5 ship不寫 Linear | 成立 | 權責清楚；close結果只應成為 plan-flow輸入 |
| C6 always-on holder | 不成立 | clone state branch不等於移交唯一 writer authority，也未處理舊 laptop醒來 |

## Q1：C6 與 holder 移轉

C6 如寫法不成立。正常移交至少要：

1. laptop 停止 FO、hooks及排程。
2. 完成並 push所有 state transaction。
3. 明確釋放 holder lease。
4. always-on host取得新的隔離代號並重跑 prerequisite。
5. laptop移除寫入權或保留為 read-only；醒來不可自動 resume。
6. always-on host重建本機 worktree；不能沿用 laptop 的絕對路徑。

若 laptop 已睡、無法合作釋放，只能等 lease expiry後接管。舊 laptop醒來時必須因隔離代號過期而在任何外部動作前停止。

## Q2：laptop sleep

不需要可靠的「sleep event」；突然睡眠前通常沒有機會寫它。輪詢可重入並在醒來後先做完整 reconciliation就夠。

實際行為：

- macOS sleep 時 bash與 CLI程序被暫停，不會繼續 polling。
- 現有 TCP connection可能斷線、逾時，或 server已完成請求但client沒收到回應。
- `sleep` 通常在醒來後很快返回，bash接著執行。
- blocking HTTP call可能立即失敗，也可能等底層 timeout；不可依賴單一結果。

可記錄 wall-clock gap 作觀察，但醒來後必須先 read-back，再做任何 mutation。對 read-only poll，重讀足夠；對 create/send/push，必須按 token查回結果。

## Q3：反轉項目與單一 falsifier

我會反轉：

- S1：移除 grace，改 transcript acknowledgment。
- S3：移除「只 unset variables 就是 sandbox」。
- S5：review保留，但已知 failure shapes轉成機械 checks。
- S6：安全與候選回歸不得 scope out。
- S10/C3：下層 verify完成前不派上層。
- C4：不執行未隔離的 worker command。
- C6：禁止單靠 clone state branch完成 holder移轉。

commission POC 的單一 falsifier應是：

> laptop 在 workspace create 已到 server、但 ID 尚未持久化時睡眠；always-on host接管；laptop再醒來。測試必須證明只有一個 workspace、一個 claim、一組訊息，且舊 holder 在任何外部動作前被拒絕。

這一次同時打中 C2、C6、sleep recovery與最昂貴的重複派工風險。

```text
剩餘: 修正 delivery topology、command sandbox與 holder fencing
下一步: 你決定取消推測式上層 dispatch，或為整個 suffix設計重建 generation（你）
可收線: 否
```

tokens used: 432500
