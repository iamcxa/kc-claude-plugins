結論：核心 recovery 順序已通過 falsifier，但目前實作的 at-most-one 保證仍不成立。AC-1～AC-4 證明 intent protocol 有效；程式內仍有 fail-open、正式 bypass與未實作的 token read-back。

## [P1]

1. **state sync 失敗後繼續使用舊資料**

   - `scripts/ship-flow/holder.sh:11`
   - `scripts/ship-flow/intent.sh:11`
   - `fetch` 或 fast-forward merge 失敗被 `|| true` 吃掉；舊 holder 可讀本機 `_holder.json` 並通過 check。
   - 修正：fetch、merge、dirty tree、non-FF任何失敗都立即停止。不可 fallback到本機狀態。

2. **正式入口保留完整安全 bypass**

   - `scripts/ship-flow/fenced-dispatch.sh:5-6,13,17-20,32`
   - `--no-intent` 與 `--no-fence` 可直接關閉全部保證；AC-4 已證明會建立兩個 workspace。
   - 修正：從 production entrypoint移除。without-it測試使用獨立 fixture或測試專用 wrapper。

3. **create失敗會被持久化成 `CREATE_FAILED`**

   - `scripts/ship-flow/fenced-dispatch.sh:25-32`
   - 腳本沒有 `set -e`；JSON錯誤、timeout或模糊回應後仍可能 adopt字串 `CREATE_FAILED`，留下孤兒 workspace並把 intent錯誤標成 resolved。
   - 修正：只接受格式與ID均合法的回應；其他結果保持 unresolved，交 reconcile查回。

4. **README 宣稱的 token read-back 沒有實作**

   - `docs/dev/README.md:496-505`
   - `scripts/ship-flow/fenced-dispatch.sh:25-31`
   - create後沒有查 workspace或transcript確認 token，只相信create回傳的ID。
   - 修正：按ID重新讀取 workspace，確認完整 token、project、claim與首則訊息；不符就保持 unresolved。

5. **adopt沒有 holder fence或 compare-and-swap**

   - `scripts/ship-flow/intent.sh:20-24`
   - reconcile只在開始check一次；下一次 handover可發生在check與adopt之間。舊 holder仍可在新 writer之上提交adoption，並可覆寫已有workspace ID。
   - 修正：`adopt` 必須接收 holder、writer、token；同步後重驗 holder，要求 workspace目前為null或同一ID，再以remote tip作條件push。

6. **claim可作路徑穿越，也沒有 canonical identity**

   - `scripts/ship-flow/intent.sh:15-16`
   - `claim="../../_holder"` 可寫出 `_intents`；`DEV-79`、`dev-79`或新generation也可能代表同一邏輯工作卻取得不同intent。
   - 修正：只接受固定schema，例如 `receiptHash.issueId.generation`，並限制為安全字元與固定長度。

7. **workspace路由仍是POC硬編碼**

   - `scripts/ship-flow/fenced-dispatch.sh:22-27`
   - 從前100個project選第一個remote suffix匹配，branch固定main，訊息固定`Reply only: ok`。這不能承載approved dispatch envelope。
   - 修正：project ID、base、workspace name與message-file全部來自已核准receipt並逐項綁定。

## [P2]

8. **token matching不是精確identity**

   - `scripts/ship-flow/intent.sh:34`
   - 只有48-bit token，reconcile使用名稱substring，且只查20筆；可能碰撞、截斷或匹配錯workspace。
   - 修正：至少128-bit token；使用固定完整名稱或immutable metadata，再核對transcript token。

9. **共用可預測 `/tmp` 檔案會互相覆寫**

   - `scripts/ship-flow/fenced-dispatch.sh:15,23`
   - 並行dispatch共用`hello.txt`與holder log；另一程序可在create讀取前改掉message。
   - 修正：每次使用權限0700的獨立臨時目錄，message寫完後hash並read-back。

10. **intent沒有完成、停止或新generation模型**

   - `scripts/ship-flow/intent.sh:15-18`
   - claim一旦存在便永久拒絕；Captain-stopped、失敗重派、profile change沒有合法後續。
   - 修正：intent不可刪改歷史；新工作使用新generation，並記錄舊generation的terminal outcome。

11. **contract test只固定句子，不證明行為**

   - `scripts/kc-dev-flow-contract-test.py:1886-1890`
   - 腳本壞掉、read-back缺失、sync fail-open時測試仍通過。
   - 修正：AC-5 mutation必須使測試轉紅；另加入fetch failure、malformed create、stale adopt與bypass absence測試。

12. **「every external action」宣稱過廣**

   - `docs/dev/README.md:498-505`
   - 實作只處理workspace dispatch；push、Slack、PR、archive等沒有相同intent/reconcile協定。
   - 修正：把文字限縮為「workspace create」，或逐類外部動作定義自己的read-back與重試規則。

## 判定

目前只能支持：

> 每個精確、已canonicalize的claim，成功提交intent後，正常入口最多發出一次create呼叫。

尚不能支持：

> 最多一個自動啟動的worker。

後者還依賴：

- Conductor單次CLI呼叫不會內部重試出兩個workspace。
- exact token read-back成功。
- production無bypass。
- state sync完全fail-closed。
- claim identity不可別名或穿越。

阻擋 commission 的項目：

1. `sync_in` fail-open。
2. production的`--no-intent`／`--no-fence`。
3. `CREATE_FAILED`可被adopt。
4. token read-back尚未實作，但README已宣稱。
5. unfenced、可覆寫的adopt。
6. POC硬編碼的project、branch與message。
7. AC-5 mutation尚未完成。

其餘可列為已知限制：human-only handover、unresolved intent需要人工處理、每次remote check的延遲。

```text
剩餘: 七項commission blocker，核心intent protocol本身已通過
下一步: 先修fail-closed sync、token read-back與fenced adopt，再跑AC-5及網路失敗falsifier（你）
可收線: 否
```

tokens used: 627523
