# Observe-and-Continue Design — Walkthrough 降噪 + Enhanced Trace Correlation

**日期**: 2026-03-15
**狀態**: Draft

## 問題

e2e-walkthrough 是三個 e2e skill 中最難遵守的，根因是三個因素疊加：

1. **指令量最大**：812 行（SKILL.md 314 + reference.md 498），遠超 e2e-test（318）和 e2e-map（196）
2. **Context 汙染**：唯一在 main context 執行 browser 操作的 skill。7 步 walkthrough 產生 ~1,050 行 browser 輸出，佔 context ~45%
3. **Phase 4 複雜度**：12 mandatory items 在 context 最滿的時候執行，遵守率最低

e2e-test 和 e2e-map 不受影響，因為 browser 操作隔離在 subagent 裡。

## 設計目標

1. Phase 3 browser 噪音從 ~1,050 行降至 ~50 行（**-95%**）
2. 保留即時告知能力（errors detected → 通知人類）但不中斷流程
3. 新增「視覺異常觀察」能力（agent 主動發現 UI 問題）
4. 透過 enhanced trace analysis 提升 debug 品質（步驟關聯 + anomaly 交叉比對）
5. 偵測 silent failure（UI 顯示成功但 API 失敗）

## 核心概念：Observe-and-Continue

```
Phase 3 (執行):
  每步: action → observe → 記錄異常 → 通知（不停）→ 繼續
  → 產出: step-log.json (步驟時間軸 + 異常記錄)

Phase 4 (分析):
  step-log.json + trace.zip → enhanced trace-analyzer (subagent)
  → 產出: step-correlated trace-analysis.md (步驟關聯 + anomaly × trace 交叉比對)
  → main context: 可展開異常清單讓人類 review
```

---

## 1. step-log.json 格式

Phase 3 期間由 walkthrough 持續寫入，Phase 4 傳給 trace-analyzer。

```json
{
  "walkthrough_start": "2026-03-15T14:32:10+08:00",
  "steps": [
    {
      "id": "step-1",
      "action": "Navigate to /dashboard",
      "ts": "14:32:10",
      "result": "pass",
      "anomalies": []
    },
    {
      "id": "step-3",
      "action": "Click submit_button on add-dialog",
      "ts": "14:32:18",
      "result": "pass",
      "anomalies": [
        {
          "type": "js_error",
          "detail": "TypeError: Cannot read property 'id' of undefined",
          "source": "errors --json"
        },
        {
          "type": "visual",
          "detail": "Success toast appeared but form fields still populated",
          "source": "post-action snapshot"
        }
      ]
    },
    {
      "id": "step-6",
      "action": "Verify data_table on list-page",
      "ts": "14:32:35",
      "result": "pass",
      "anomalies": [
        {
          "type": "visual",
          "detail": "Table shows 0 rows, expected new entry from step-3",
          "source": "post-action snapshot"
        }
      ]
    }
  ]
}
```

### 欄位定義

| Field | 說明 |
|-------|------|
| `id` | 步驟 ID，與 flow YAML 的 step id 對應 |
| `action` | 步驟動作描述 |
| `ts` | 步驟執行時間（HH:MM:SS，用於 trace timestamp 比對） |
| `result` | `pass` / `fail` / `skip` — 步驟本身是否成功（元素找到、action 執行完） |
| `anomalies` | 該步驟觀察到的異常（可為空陣列） |
| `anomaly.type` | `js_error`（errors --json）、`visual`（agent 觀察）、`network_hint`（a11y tree 出現 fetch error） |
| `anomaly.detail` | 異常描述（≤ 200 字） |
| `anomaly.source` | 資料來源，供 trace analyzer 知道用什麼去 cross-reference |

### 設計決策

- `result` 只記步驟成功與否，anomaly 是附加觀察（不影響 result）
- anomaly 不中斷流程——記錄 + 通知，繼續下一步
- step-log.json 在 Phase 3 結束後寫入 `$REPORT_DIR/step-log.json`

---

## 2. Phase 3 Per-Step Loop 變更

### 現行

```
每步:
  1. snapshot            → 完整 a11y tree（50-200 行）
  2. action              → click/fill
  3. wait networkidle
  4. screenshot          → 截圖
  5. console --json      → 完整 console dump（10-50 行）
  6. errors --json       → 完整 error dump（10-50 行）
  7. 報告給人類           → 完整 health summary（10-20 行）
  → 每步 context 成本: ~80-320 行
```

### 修改後

```
每步:
  1. snapshot -i          → interactive-only a11y tree（更精簡）
  2. action               → click/fill
  3. wait networkidle
  4. screenshot           → 截圖
  5. errors --json        → 快速檢查（通常空 = 0 行）
     → 有錯: 記錄到 anomaly log + 通知人類（不停）
     → 沒錯: 不輸出
  6. 觀察異常              → agent 對照 snapshot 結果主動觀察
     → 有異常: 記錄到 anomaly log + 通知人類（不停）
     → 沒異常: 不輸出
  7. 一行報告              → "Step N ✓" 或 "Step N ✓  ⚠ <anomaly summary>"
  → 每步 context 成本: ~1-5 行
```

### 異常觀察規則

agent 在每步的 post-action snapshot 和 screenshot 之間，主動檢查：

| 觀察對象 | 怎麼發現 | 例子 |
|---------|---------|------|
| 意外的 UI 元素 | snapshot 出現 error toast, alert banner, empty state | "Error toast: 'Something went wrong'" |
| 預期元素消失 | action 後 snapshot 缺少 expect 中提到的元素 | "Submit 後 form 仍在，沒有跳轉" |
| Loading 狀態卡住 | networkidle 後仍有 spinner/skeleton | "Loading spinner still visible" |
| 資料不一致 | 表格/列表行數和前一步操作預期不符 | "Table shows 0 rows, expected new entry" |
| 版面異常 | 元素重疊、意外 collapse、空白區塊 | "Sidebar collapsed unexpectedly" |

### 通知格式（不中斷流程）

```
Step 1 ✓
Step 2 ✓
Step 3 ✓  ⚠ JS error: TypeError: Cannot read 'id' | Visual: success toast + form still visible
Step 4 ✓  ⚠ Visual: loading spinner still visible after networkidle
Step 5 ✓
Step 6 ✓  ⚠ Visual: table shows 0 rows, expected data from step 3
Step 7 ✓

7/7 steps passed, 4 anomalies recorded → analyzing with trace...
```

### console --json 移除理由

- trace.zip 的 `trace.trace` 包含完整 console 記錄（覆蓋率更高）
- per-step `console --json` 只抓到 check 當下的 buffer，背景 log 可能已被清除
- `errors --json` 已涵蓋 error-level console messages
- 移除後每步減少 10-50 行 raw JSON

### 不同模式的行為

| Mode | Per-step error check | 異常觀察 | 通知風格 |
|------|---------------------|---------|---------|
| Guided | `errors --json` → 有錯記錄通知 | 主動觀察 | 一行 summary |
| Step | `errors --json` → 有錯記錄通知 | 主動觀察 | 一行 summary（wait "go" 時可問） |
| Auto | `errors --json` → 有錯記錄 | 主動觀察 | 結束後統一報告 |
| Smoke | 無 per-step check（現狀） | 有（selector 驗證已涵蓋） | 結束後統一報告 |

---

## 3. Enhanced Trace Analyzer

### 新增 Input

| Field | Required | 說明 |
|-------|----------|------|
| `step_log_path` | Optional | `$REPORT_DIR/step-log.json`。如未提供，行為與現行相同 |

### Cross-Reference 邏輯

當 `step_log_path` 存在時，trace-analyzer 執行額外分析：

```python
for step in step_log.steps:
    window_start = step.ts - 2s
    window_end = next_step.ts  # 或 walkthrough_end

    # 從 trace.network 找這個時間窗內的 HTTP errors
    network_errors = [e for e in trace_network if e.ts in window and e.status >= 400]

    # 從 trace.trace 找這個時間窗內的 console errors
    console_errors = [e for e in trace_trace if e.ts in window and e.type == 'error']

    # 與 step 的 anomalies 交叉比對
    for anomaly in step.anomalies:
        if anomaly.type == "js_error":
            # 用 message similarity 比對 console_errors
            # 往前看 network_errors 是否是 root cause
        elif anomaly.type == "visual":
            # 看 network_errors 是否能解釋視覺異常
            # 看 console_errors 是否能解釋
            # 都沒有 → "Unmatched anomaly"
```

### 新增 Output Sections

在現有 `trace-analysis.md` 基礎上新增兩個 section：

```markdown
# Trace Analysis

## API Failures
<!-- 現有 -->

## Console Errors
<!-- 現有 -->

## Step-Correlated Issues                          ← NEW

| Step | Action | Network | Console | Timing |
|------|--------|---------|---------|--------|
| step-3 | Click submit | POST /api/items 500 | TypeError: 'id' | 14:32:18 |
| step-5 | Click save | POST /api/settings timeout | — | 14:32:28 |

## Anomaly × Trace Cross-Reference                 ← NEW

| # | Step | Agent 觀察 | Trace 佐證 | 判定 |
|---|------|-----------|-----------|------|
| 1 | step-3 | JS error: TypeError | POST /api/items 500 (1s before) | ⚠ API failure → client error |
| 2 | step-3 | Success toast + form visible | API 500 but UI showed success | ⚠ Silent failure |
| 3 | step-6 | Table 0 rows | No new POST after step-3 | ⚠ Cascading from step-3 |

## Anomalies Without Trace Evidence                 ← NEW

| # | Step | Agent 觀察 | Possible Cause |
|---|------|-----------|----------------|
| 4 | step-4 | Spinner after networkidle | Client-side state (no network issue) |

## Summary
- API failures: 2 (steps 3, 5)
- Console errors: 1 (step 3)
- Agent-observed anomalies: 4 (3 trace-correlated, 1 unmatched)
- Silent failures detected: 1 (step 3)                ← NEW field
- Clean: false
```

### Backward Compatibility

- `step_log_path` 是 optional——不提供時行為完全不變
- 新增的 sections 只在 step_log 存在時才出現
- Summary 的 `agent-observed anomalies` 和 `silent failures` 只在有值時才出現
- e2e-test skill 的 Phase 1.75 dispatch 不受影響（目前 test-runner 不產生 step-log）

---

## 4. Phase 4 呈現變更

### Anomaly Review 清單

walkthrough 收到 trace-analyzer 回傳後，呈現可展開的異常清單：

```
Walkthrough complete: 7/7 steps passed

⚠ 4 anomalies detected, cross-referenced with trace:

Correlated (3):
  1. step-3: API failure → client error → silent failure
  2. step-3: Success toast despite API 500
  3. step-6: Empty table — cascading from step-3

Unmatched (1):
  4. step-4: Spinner after networkidle (likely client state)

→ Full analysis: e2e-reports/<ts>/trace-analysis.md

What's next?
1. Review anomaly details (expand with trace evidence)
2. Fix from #1 (highest severity)
3. Re-walk affected steps after fix
4. Continue to report generation
```

### 選擇 "Review anomaly details"

從 trace-analysis.md 讀取對應 section，展示完整的 cross-reference 表格。人類可以逐項確認或跳過。

### 與現有 Phase 4 Checklist 的整合

在現有 12-item checklist 的 step 3 (trace analysis) 之後插入：

```
[ ] 1. record stop
[ ] 2. trace stop
[ ] 3. trace-analyzer dispatched
[ ] 3.5 anomaly review presented               ← NEW
[ ] 4. report.md written
...
```

---

## 5. 修改範圍

| 檔案 | 變更類型 | 說明 |
|------|---------|------|
| `skills/e2e-walkthrough/SKILL.md` | Modify | Phase 3 per-step loop 改為 observe-and-continue；Phase 4 checklist 加入 anomaly review |
| `skills/e2e-walkthrough/reference.md` | Modify | Phase 3 execution details 重寫；新增 step-log.json spec；新增 anomaly observation rules |
| `agents/e2e-trace-analyzer.md` | Modify | 新增 `step_log_path` input；新增 cross-reference 邏輯和 output sections |
| `skills/e2e-test/SKILL.md` | No change | test-runner 不產生 step-log，Phase 1.75 dispatch 不變 |
| `references/common-patterns.md` | Optional | 可加入 anomaly observation patterns，但非必要 |

### Impact Matrix Check

| File | 影響 |
|------|------|
| e2e-test SKILL.md | 無——test 走 subagent 路線，不受 walkthrough 改動影響 |
| e2e-map SKILL.md | 無——map 走 subagent 路線 |
| e2e-test-runner agent | 無——不使用 step-log |
| e2e-mapper agent | 無 |
| e2e-trace-analyzer agent | **有**——新增 step_log_path + cross-reference |
| common-patterns.md | Optional |
| commands.md | 無 |

---

## 6. Context 成本比較

| 項目 | 現行 | 修改後 |
|------|------|--------|
| Phase 3 per-step output | ~150 行 × 7 = ~1,050 行 | ~2 行 × 7 + anomalies = ~20-50 行 |
| Health data dump | 包含在上方 | 0（trace-analyzer 處理） |
| Phase 4 trace result | ~20 行 | ~30 行（多 cross-reference summary） |
| **Total browser noise** | **~1,050 行** | **~50-80 行** |
| **Debug 覆蓋率** | ~60% | ~95%（含 silent failure） |
| **降幅** | — | **~93%** |

---

## 7. 實作順序（由下而上）

1. **Enhanced trace-analyzer** — 新增 step_log_path input + cross-reference output
2. **step-log.json writer** — walkthrough reference.md 新增 step-log 寫入邏輯
3. **Phase 3 per-step loop** — SKILL.md 改為 observe-and-continue
4. **Phase 4 anomaly review** — SKILL.md + reference.md 新增異常清單呈現
5. **Verification** — 用一個真實 walkthrough 驗證完整流程

---

## 8. 驗收標準

| # | 標準 | 驗證方法 |
|---|------|---------|
| 1 | Phase 3 每步 context output ≤ 5 行（正常步驟） | 觀察 walkthrough 執行 |
| 2 | errors --json 有 error 時記錄到 step-log 且通知人類（不停） | 模擬 API error 場景 |
| 3 | 視覺異常被記錄（至少含 toast/spinner/empty state） | 觀察 anomaly log |
| 4 | step-log.json 正確寫入 $REPORT_DIR | 檢查檔案 |
| 5 | trace-analyzer 接受 step_log_path 並產出 cross-reference | dispatch 驗證 |
| 6 | 無 step_log 時 trace-analyzer 行為不變 | 從 e2e-test dispatch 驗證 |
| 7 | Silent failure 被偵測（UI success + API error） | 模擬場景 |
| 8 | Phase 4 anomaly review 清單正確呈現 | 觀察 walkthrough 完整流程 |
| 9 | 總 context 降幅 ≥ 80% | 比較前後 |
