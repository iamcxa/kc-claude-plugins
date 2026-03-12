# Pilot → SOP → Scale 方法論

> 用於系統性驗證和改善 Claude Code plugin 品質的三階段方法。

## 背景

Plugin 由多個 skills 和 agents 組成，各自有 frontmatter（觸發描述）、行為邏輯（phase flow）、和合約對齊（skill↔agent I/O contract）。這些 component 通常由不同 session 逐步建構，缺乏統一的品質基線。

**核心問題**：如何在不了解「好的 plugin component 長什麼樣」的情況下，建立可重複的品質驗證流程？

## 方法選擇

| 方法 | 做法 | 缺點 |
|------|------|------|
| 1. 全面掃描 | 一次驗證所有 component | 沒有 SOP，品質不一致 |
| 2. 寫 SOP 再執行 | 先寫理論 checklist | SOP 脫離實際，缺乏真實案例 |
| **3. Pilot → SOP → Scale** | **先深度驗證一對，從中萃取 SOP，再用 SOP 規模化** | 前期較慢，但 SOP 基於實證 |

選擇方法 3 — SOP 來自實際驗證經驗，不是憑空想像。

## 三階段流程

```
┌─────────────────────────────────────────────────────────┐
│  Pilot（深度驗證 1 對 skill+agent）                       │
│                                                         │
│  Round 1: Frontmatter CSO audit + trigger test          │
│  Round 2: Behavior flow + contract alignment            │
│  Round 3: Edge cases + robustness                       │
│  Agent:   Frontmatter + system prompt + behavior test   │
│                                                         │
│  產出: fixes + VERIFICATION-LOG.md                       │
├─────────────────────────────────────────────────────────┤
│  SOP（從 Pilot 萃取可重複的 checklist）                    │
│                                                         │
│  Skill Verification Checklist (CSO, behavior, edges)    │
│  Agent Verification Checklist (frontmatter, prompt, I/O)│
│  Common Fix Patterns table                              │
│  Gap Analysis template                                  │
│                                                         │
│  產出: VERIFICATION-SOP.md + gap priorities              │
├─────────────────────────────────────────────────────────┤
│  Scale（用 SOP 平行驗證剩餘 components）                   │
│                                                         │
│  Wave N: skill + agent pair → apply SOP → commit        │
│  每個 wave 可平行 dispatch（skill 和 agent 獨立）          │
│                                                         │
│  產出: fixes per wave + append to VERIFICATION-LOG.md    │
└─────────────────────────────────────────────────────────┘
```

## Pilot 階段：怎麼選 Pilot 對象

選擇**最複雜且最常用**的 skill+agent 對：

- 複雜度高 → 能暴露最多問題類型，SOP 覆蓋面更廣
- 使用頻率高 → 修復的 ROI 最大

本次選擇 `e2e-test` (skill) + `e2e-test-runner` (agent) — plugin 中最複雜的 orchestrator+executor 對。

### Pilot 的 3 輪結構

| 輪次 | 焦點 | 驗證工具 |
|------|------|---------|
| Round 1 | **觸發準確性** — 描述是否符合 CSO、keywords 是否充分 | `/writing-skills` CSO rules |
| Round 2 | **行為正確性** — phase flow、contract alignment | 靜態 field table 比對 |
| Round 3 | **邊界情況** — error paths 是否 actionable | 場景清單逐一審計 |

Agent 驗證額外加入：
- Frontmatter audit（`<example>` blocks、tools least privilege）
- System prompt structure（Input Contract、Core Responsibilities）
- **Behavior test**（實際 dispatch agent 觀察行為）

### 為什麼 3 輪而不是 1 輪

每輪聚焦不同層面，避免單次審計的認知過載。Round 1 的 CSO fix 會影響 Round 2 的 trigger test 結果 — 有依賴關係。

## SOP 階段：萃取什麼

從 Pilot 的 findings 萃取兩類 artifact：

### 1. VERIFICATION-SOP.md — 可重複的 checklist

```
Skill checklist:  frontmatter → trigger → behavior → edge cases
Agent checklist:  frontmatter → structure → I/O contract → self-contained → tools
Fix patterns:     pattern → standard fix（查表即可修復）
```

關鍵原則：**SOP 的每個 checklist item 都有 Pilot 中的真實 finding 作為來源**。沒有憑空添加的項目。

### 2. Gap Analysis — 超出驗證範圍的系統性問題

Pilot 會發現個別 fix 無法解決的模式，例如：
- Contract 會持續 drift → 需要自動化 sync check
- Error 在 agent 端才被偵測 → 需要 pre-dispatch validation
- 測試結果是 ephemeral → 需要 trend tracking

這些歸入 priority matrix，留給 Design phase 處理。

## Scale 階段：如何平行化

### Wave 分組

將剩餘 components 分成 waves，每 wave 包含一對 skill+agent（或單獨的 skill）：

| Wave | Components | 為什麼一起 |
|------|-----------|-----------|
| 1 | e2e-map + e2e-mapper | 同一 orchestrator-executor 對 |
| 2 | e2e-walkthrough + e2e-trace-analyzer | walkthrough dispatches trace-analyzer |
| 3 | e2e-dispatch + e2e-skill-ops | 兩個獨立 skill，無 agent |

### 平行 dispatch 規則

- **同一 wave 內**：skill 和 agent 可以平行 dispatch（各自獨立審計）
- **跨 wave**：sequential（Wave 1 的 commit 不影響 Wave 2，但 log 是 append-only）
- **每個 subagent 收到**：SOP checklist + 目標檔案 + 已知問題（from gap analysis）

### Scale 的效率增益

| 指標 | Pilot | Scale (per wave) |
|------|-------|-----------------|
| Tasks | 8 | 2 (平行) |
| Subagent dispatches | 8 | 2 |
| Findings 品質 | 探索式（發現新模式） | 標準化（SOP 驅動） |
| 每 component 耗時 | ~15 min | ~5 min |

## 實證結果（本次執行）

### 數量

- **5 skills + 3 agents** 驗證完成
- **48 issues** 修復
- **14 systemic gaps** 識別並分級

### 高價值發現（只有深度 Pilot 才能找到）

| Finding | 影響 | 怎麼發現的 |
|---------|------|-----------|
| `suite_context` contract 缺失 | 多站測試 session leak | Round 2 field table 逐欄比對 |
| `Write` tool 缺失 (trace-analyzer) | Agent 無法寫入報告 | Scale Wave 2 tools audit |
| `noise_patterns` dispatch gap | Trace 分析忽略 known noise | Scale Wave 2 contract alignment |
| Description workflow summary | Claude 走捷徑跳過讀 SKILL.md | Round 1 CSO audit |

### SOP 的複利效應

Pilot 萃取的 checklist items 在 Scale 中被重複應用：

| SOP Item | Pilot 中發現 | Scale 中再次命中 |
|----------|-------------|----------------|
| "Use when..." CSO | e2e-test | e2e-map, e2e-dispatch |
| Input Contract + STOP guard | e2e-test-runner | e2e-mapper, e2e-trace-analyzer |
| `<example>` blocks | e2e-test-runner | e2e-mapper, e2e-trace-analyzer |
| Tools least privilege | e2e-test-runner (Glob) | e2e-mapper (Glob) |
| Explicit phase transitions | e2e-test | e2e-map, e2e-walkthrough |

每個 SOP item 平均命中 2-3 次 — 不做 Pilot 就不會發現這些模式。

## 適用場景

| 適合 | 不適合 |
|------|--------|
| Plugin 有 3+ components | 單一 skill/agent |
| Components 有共同模式（orchestrator-executor） | 完全異質的 components |
| 需要建立可重複的品質基線 | 一次性快速修復 |
| 有時間做深度 Pilot（~1 hr） | 緊急 hotfix |

## 檔案結構

```
plugin/
├── METHODOLOGY.md          ← 本文件（方法論說明）
├── VERIFICATION-SOP.md     ← Pilot 萃取的 checklist
├── VERIFICATION-LOG.md     ← 所有 findings 的完整記錄
├── skills/                 ← 驗證後的 skills
└── agents/                 ← 驗證後的 agents
```
