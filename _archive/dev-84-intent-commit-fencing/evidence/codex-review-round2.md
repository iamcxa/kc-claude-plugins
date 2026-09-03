結論：前兩個 P1 已關閉；第三個仍開放，並有一個新的 P1。行號為套用 diff 後。

- **已關閉**：trap 太晚安裝。`scripts/ship-flow/intent.sh:32`，早於 `mkdir`（line 36）。
- **已關閉**：`kill -0` 不支援跨主機。`scripts/ship-flow/intent.sh:42-47`，現只看目錄年齡。
- **仍開放**：刪除非自己建立的 lock。`scripts/ship-flow/intent.sh:22-27` 只比 PID，沒有比完整 `hostname:pid:epoch`；無 marker 時也直接刪除目前路徑，該路徑可能已被 takeover 後的另一持有者重建。

**NEW [P1]**（confidence: 10/10）`scripts/ship-flow/intent.sh:47-52`：檢查與使用之間競態（TOCTOU）。讀到舊 lock 已過期後，另一程序可先搬走舊 lock 並建立新 lock；本程序接著會把這個新 lock 搬走，再成功 `mkdir`。兩個程序會同時認為自己持鎖。`mv` 本身原子化，並不保證搬走的仍是剛才檢查的目錄。

```text
剩餘: 2 個 P1：release 必須比對完整 owner token；takeover 必須避免搬走檢查後才建立的新 lock
下一步: worker 修正後再複核（你）
可收線: 否
```
