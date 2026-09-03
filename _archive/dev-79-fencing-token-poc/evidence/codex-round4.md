結論：falsifier 成功推翻 C7+C8。fencing 只阻止舊 holder 持久化，沒有阻止它造成外部效果；AC-2 已實際產生兩個 workspace。

## P0

1. **C7 不成立：check-act-check 不是 exactly-once**

   - 情境：A 通過第一次 check；B handover；A 的 create 在 Conductor 生效；A 第二次 check 才被 fenced。
   - 錯誤：外部效果已發生，第二次 check 無法撤回。
   - 最小修正：外部動作前先持久化 `pending intent`。新 holder 看見 pending 時只能查回／接管，不能自動重做。

2. **仍有殘留窗口：舊 create 在新 reconcile 後才出現**

   時序可以是：

   1. A check 通過並送出 create。
   2. B handover。
   3. B reconcile；W1 尚未可見。
   4. B 建立 W2。
   5. A 的 in-flight create 完成，W1 才出現。
   6. A 被 fenced，不持久化 W1。

   此時 W1 是未知 workspace，且可能已開始工作。C7+C8 無法保證「只有一個 worker doing work」。

3. **C8 的處置方向錯誤**

   - 情境：B 找到帶同一 dispatch token 的 W1，但先建 W2，再 archive W1。
   - 錯誤：它主動製造第二個 workspace；archive 也不能撤銷 W1 已做的工作與成本。
   - 最小修正：若找到唯一、內容相符的 W1，接管並持久化 W1；只有確認是額外 duplicate 後才隔離其他 workspace。

4. **AC-2 沒有測到所寫的 C8**

   - 情境：C8 說 handover 後第一步 reconcile；實際 B 先 create W2，之後才 list/archive。
   - 錯誤：結果不能支持 C8。
   - 最小修正：重跑「handover → reconcile → adopt-or-block → 禁止 create」路徑。

## 合約判定

| 結論 | 判定 | 原因 |
|---|---|---|
| C7 check-act-check | 不成立 | 只能保護 receipt，不能保護外部 effect |
| C8 name reconcile/archive | 不成立 | reconcile可能早於舊 create 可見；archive也可能殺錯 workspace |
| C9 human handover | 需要 falsifier | human command不代表舊 holder已停止或沒有 in-flight action |
| C10 writer mismatch exit 1 | 不成立 | 還須核對 holder ID；fetch、parse、non-FF與真正 fenced應可區分，且全部 fail-closed |

## Q1

不充分。剩餘窗口是：

> A 第一次 check 通過後，到 Conductor create 最終生效並可被查詢之前。

沒有 provider idempotency或 provider-side fencing，就不能保證 exactly-once effect。可誠實保證的較弱版本是：

> 最多一個自動啟動的 worker；不確定 create 必須阻塞並人工對帳。

前提是 workspace 在確認採用前不會開始工作；若 create 立即啟動 agent，連這個較弱保證也做不到。

## Q2

`git fetch` 加 fast-forward merge 只提供 state branch ref 的一致快照：

- 若 B 的 push 在 A 的 fetch 讀取遠端 ref 前完成，A 應看到新 writer並被 fenced。
- 若 A 的 fetch 先完成，A 可合法通過；B 隨後立即 handover也阻止不了 A 的 action。
- 同時發生時，遠端只會呈現舊 tip或新 tip，不會呈現半個 commit。
- fast-forward只保證 ancestry；不把後續外部 action鎖進同一交易。

fetch失敗、non-fast-forward、malformed holder或遠端不明都必須停止。這仍是典型 check/action race。

## Q3

依賴 `-v1` 不成立。它只是 Conductor 的命名副作用，不是 identity：

- 命名規則可能改變。
- 舊 generation或人工 workspace也可能撞名。
- suffix可能是 `-v2` 或受 truncation影響。
- prefix lookup可能匹配錯 claim。

名稱應包含短 dispatch token；完整 token、receipt hash與generation還要出現在不可混淆的 workspace metadata或首則 transcript。Reconcile按 token匹配，不按 suffix推理。

## Q4

阻擋 commission：

- 宣稱 exactly-once effect。
- external action前沒有 durable pending intent。
- 新 holder遇到 pending create仍可建立第二個 workspace。
- reconcile依賴名稱 suffix。
- planned handover沒有 drain：停止舊 action、等待 in-flight結束、再轉移。
- crash handover沒有 adopt-or-block規則。

可列為限制：

- manual handover，沒有 unattended failover。
- 每次 check增加1–2秒。
- ambiguous create可能需要 Captain處理。
- 可能留下已付費但未啟動的 duplicate workspace。

建議把 contract 改成：`intent commit → check → create once → token read-back → check → adopt/persist`。新 holder看見 unresolved intent時只 reconcile；永不自動 create第二次。

```text
剩餘: exactly-once宣稱、pending intent、token reconcile與handover drain仍未成立
下一步: 接受「不確定即阻塞」的較弱保證，或要求Conductor提供idempotent create（你）
可收線: 否
```

tokens used: 521425
