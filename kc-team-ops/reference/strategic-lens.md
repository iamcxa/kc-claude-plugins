# Strategic Lens Reference

## Estimate Semantic Buckets

Depth routing uses semantic size buckets (SMALL/MEDIUM/LARGE), mapped from all Linear estimate scales:

| Semantic | T-shirt | Fibonacci | Linear | Exponential |
|----------|---------|-----------|--------|-------------|
| SMALL    | XS, S   | 1, 2      | 1, 2   | 1, 2        |
| MEDIUM   | M       | 3         | 3      | 4           |
| LARGE    | L, XL   | 5, 8, 13+ | 4, 5   | 8, 16, 32   |

When estimate is missing or scale is unknown, treat as MEDIUM (default to Standard depth).

## Depth Recommendation Logic

Evaluate in order — first match wins:

### 🟢 Quick
- NOT aligned with any active initiative AND estimate SMALL AND symptom signal low
- OR label is clearly bug-fix / typo / chore type (exact label match, not inference)

### 🟡 Standard
- Aligned with an active initiative
- OR estimate MEDIUM or above
- OR symptom signal present but not strong

### 🔴 Deep
- Aligned with a **priority** initiative AND estimate LARGE
- OR symptom signal strong (vague description + cross-system language + no repro steps)
- OR content credibility LOW (file paths/endpoints in description don't exist in codebase)
- OR user override

**Default**: if no rule matches clearly, default to 🟡 Standard.

## Symptom Signal Heuristic

Evaluate issue description structure (not content meaning):

| Signal | Indicator |
|--------|-----------|
| **Low** | Has repro steps, identifies specific trigger, names concrete error |
| **Present** | Describes phenomenon without trigger ("X is slow", "Y sometimes fails") |
| **Strong** | Vague + cross-system language ("everything", "the whole feature") + no repro + no error message |

## EM Lens Entry Card Format

### Single Issue
```
── EM Lens ──────────────────────────────
🎯 對齊: [initiative name] > [project name]
🤝 Customer Need: [customer] — "[need title]" ([priority])
👤 Reporter: [name] ([role], [team])
📄 信心度: [HIGH/MEDIUM/LOW] — [reason]
🔍 Symptom 疑慮: [低/有/強] — [reason if 有 or 強]
💡 建議深度: [🟢 快速過 / 🟡 標準 triage / 🔴 深度分析] ([reasoning])
─────────────────────────────────────────
```

Rules:
- `🤝 Customer Need` line: omit entirely if no linked customer need
- `🎯 對齊`: show `⚪ 未對齊任何當季倡議` if no match
- `📄 信心度`: Grep up to 5 file paths/endpoints/function names mentioned in description

### Multiple Issues (Overview)
```
| # | Issue | Alignment | Customer | Credibility | Symptom | Depth |
```

### 🔴 Deep Interaction
When depth is 🔴, append opt-in source selection:
```
   附加 source: [x] Sentry  [ ] Slack
   要加上 Slack search 嗎？(y/n)
```

## EM Lens Exit Dimensions

### Assignment Candidates (🟡 Standard + 🔴 Deep)
```
git log --format="%an" -- <paths from code-explorer>
→ count per author → top 2
→ cross-reference with team context cache members
```
Output: `👥 歷史貢獻者: [name] ([N] commits), [name] ([N] commits)`
If no team member in git history: `⚠️ 無團隊內歷史貢獻者`

### Skill/Pattern Awareness (🟡 Standard + 🔴 Deep)
Extract keywords from issue + exploration results → match against:
1. Installed skill list (from session context)
2. Team context cache project names and initiative themes

- 🟡: show matching skills and related project references only
- 🔴: also show pattern observations from memory/journal (only if backed by data, never guessed)

Output: `🔧 相關 skill: [skill1], [skill2]`
Pattern (🔴 only, if data exists): `💡 Pattern 觀察: [observation]`

### Cost of Inaction (🔴 Deep only)
Synthesize from Deep sources (memory, journal, git log, Sentry, Slack):
```
── Cost of Inaction 素材 ────────────────
📜 過去經驗: [finding from memory/journal]
📊 Sentry: [error trend or "無相關 signal"]
🔧 近期變動: [relevant recent commits]
💬 Slack: [discussion context or omit if not opted in]
💡 以上供你判斷此票的急迫性與是否為 symptom
─────────────────────────────────────────
```

### Exit Card Format
```
── EM Lens (exit) ───────────────────────
👥 歷史貢獻者: [candidates]
🔧 相關 skill: [skills]
📋 相關規範: [references]
💡 Pattern 觀察: [if data exists, 🔴 only]
📊 Cost of Inaction: [🔴 only, see above]
─────────────────────────────────────────
以上納入 draft，或調整後再 draft？
```

## Team Context Cache

### Location
`~/.claude/kc-team-ops/<team>-context.yaml`

### Freshness
- Default: `freshness_hours: 3`
- Fresh (< 3h): use silently
- Stale (≥ 3h): warn, don't block
- Missing: skill fetches on-demand before dispatching agent

### Structure

```yaml
team: <team-name>
team_id: "<id>"
synced_at: "<ISO 8601 timestamp>"
freshness_hours: 3

initiatives:
  - id: "<id>"
    name: "<name>"
    status: active
    projects:
      - id: "<id>"
        name: "<name>"
        status: "<status>"
        lead: "<assignee name>"
        target: "<target date or null>"

customers:
  - id: "<id>"
    name: "<name>"
    needs:
      - id: "<id>"
        title: "<title>"
        priority: "<urgency value>"
        linked_issues: ["<issue identifier>", ...]
        linked_project: "<project id or null>"

members:
  - id: "<id>"
    name: "<display name>"
    role: "<role or 'member'>"

active_cycle:
  id: "<id>"
  name: "<name>"
  starts: "<date>"
  ends: "<date>"

estimate_scale: "<tshirt|fibonacci|linear|exponential|unknown>"
estimate_values: ["<value1>", "<value2>", ...]
```
