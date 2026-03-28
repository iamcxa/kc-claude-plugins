# e2e-debug — Reference Schemas & Procedures

Loaded on demand from SKILL.md. Contains all schemas, templates, and cleanup procedures.

---

## 1. Manifest Schema

Written to `.claude/e2e/debug/manifest.yaml` at start of Phase 1.

```yaml
session_id: "dbg-20260323-001"         # dbg-YYYYMMDD-NNN
created_at: "2026-03-23T10:00:00Z"
mode: "standalone"                      # standalone | experiment
round: 1                                # increments on --continue
bug_description: "workspace list is empty after selecting customer"
hypothesis: "data shape mismatch — usePipelineWorkspaces wraps in extra .data layer"
target_url: "http://localhost:5173/operations/service-schedule"
auth_profile: "~/.agent-browser/carlove/"   # omit if no auth required
reproduction_steps:
  - "Navigate to /operations/service-schedule"
  - "Click 建立服務單"
  - "Select customer 王大明"
  - "Click 快速洗車"
  - "Observe step 3 workspace section"
network_filters:
  - "pipeline-preview"
  - "api/rest"
injections:
  - file: "apps/carlove/src/hooks/usePipelineWorkspaces.ts"
    line: 42
    tag: "usePipelineWorkspaces:allData"
    code: "console.log('[E2E-DBG:usePipelineWorkspaces:allData]', JSON.stringify(d1));"
    original_line: "const workspaces = d1.data.workspaces;"
  - file: "apps/carlove/src/hooks/usePipelineWorkspaces.ts"
    line: 43
    tag: "usePipelineWorkspaces:wsList"
    code: "console.log('[E2E-DBG:usePipelineWorkspaces:wsList]', JSON.stringify(workspaces));"
    original_line: "return workspaces;"
cleanup_grep: "\\[E2E-DBG\\]"
cleanup_scope: "apps/ src/ lib/"
```

---

## 2. Report Template

Written to `.claude/e2e/debug/report.md` by the `e2e-debug-observe` agent.

```markdown
# E2E Debug Report

**Session:** dbg-20260323-001  
**Round:** 1  
**Date:** 2026-03-23T10:05:00Z  
**Target:** http://localhost:5173/operations/service-schedule

## Execution Summary

| Step | Action | Result | Screenshot |
|------|--------|--------|-----------|
| 1 | Navigate to /operations/service-schedule | ✅ OK | step-01.png |
| 2 | Click 建立服務單 | ✅ OK | step-02.png |
| 3 | Select customer 王大明 | ✅ OK | step-03.png |
| 4 | Click 快速洗車 | ✅ OK | step-04.png |
| 5 | Observe step 3 workspace section | ✅ OK | step-05.png |

## [E2E-DBG] Console Output

| Tag | Value | Step |
|-----|-------|------|
| `usePipelineWorkspaces:allData` | `{"data":{"data":{"workspaces":[...]}}}` | 4 |
| `usePipelineWorkspaces:wsList` | `undefined` | 4 |

## JS Errors

| Error | Step |
|-------|------|
| (none) | — |

## Network Requests

| URL | Method | Status | Step |
|-----|--------|--------|------|
| /api/rest/pipeline-preview | GET | 200 | 4 |

## Step Screenshots

step-01.png, step-02.png, step-03.png, step-04.png, step-05.png

<details>
<summary>Raw Console Output</summary>

```
[E2E-DBG:usePipelineWorkspaces:allData] {"data":{"data":{"workspaces":[...]}}}
[E2E-DBG:usePipelineWorkspaces:wsList] undefined
```

</details>
```

---

## 3. History File Schema

Written to `.claude/e2e/debug/history/<session_id>-r<N>.yaml` at end of each round.

```yaml
session_id: "dbg-20260323-001"
round: 1
hypothesis: "data shape mismatch — usePipelineWorkspaces wraps in extra .data layer"
injections_summary:
  - "usePipelineWorkspaces:allData @ line 42"
  - "usePipelineWorkspaces:wsList @ line 43"
observations:
  - "allData shows double-wrapped: d1.data.data.workspaces"
  - "wsList is undefined because code accesses d1.data.workspaces"
verdict: "confirmed"       # confirmed | unconfirmed | inconclusive
next_investigation: ""     # populated when verdict is unconfirmed/inconclusive
```

---

## 4. Injection Format Rules

| Rule | Correct | Wrong |
|------|---------|-------|
| Tag format | `[E2E-DBG:<module>:<variable>]` | `[DBG]`, `[debug]` |
| Object logging | `JSON.stringify(value)` | `value` (renders `[object Object]`) |
| Log level | `console.log` | `console.error` (conflicts with agent-browser errors) |
| Insertion position | **BEFORE** the observed line | after |
| Granularity | One log per data point | Multiple values in one log |

**Template:**
```typescript
console.log('[E2E-DBG:<module>:<variable>]', JSON.stringify(<value>));
```

---

## 5. Cleanup Procedure (Three-Layer Fallback)

### Layer 1 — Manifest-driven (preferred)

Read `manifest.yaml` → iterate `injections[]` in **REVERSE** order (LIFO):

1. Read the file at `injections[i].file`
2. Verify `injections[i].original_line` is still present near expected location
3. Use Edit tool to remove `injections[i].code` (exact string match)
4. If Edit fails → fall through to Layer 2

### Layer 2 — Grep fallback

```bash
grep -rn '\[E2E-DBG\]' <cleanup_scope>
```

For each match: use Edit tool to remove the entire matching line.

### Layer 3 — Verification

```bash
grep -rn '\[E2E-DBG\]' apps/ src/ lib/
```

- **0 matches** → cleanup complete ✅
- **>0 matches** → alert user with exact file paths + line numbers. Suggest:
  ```bash
  git checkout -- <file>
  ```

---

## 6. Experiment Result Schema

Returned to caller (e.g., `systematic-debugging`) when `--experiment` flag is set.

```yaml
experiment_result:
  hypothesis: "data shape mismatch — extra .data wrapper"
  observations:
    - tag: "usePipelineWorkspaces:allData"
      value: '{"data":{"data":{"workspaces":[...]}}}'
      step: 4
    - tag: "usePipelineWorkspaces:wsList"
      value: "undefined"
      step: 4
  errors: []
  network:
    - url: "/api/rest/pipeline-preview"
      status: 200
  verdict: "confirmed"    # confirmed | unconfirmed | inconclusive
```

---

## 7. Teams Communication Schema

> Shared protocol (startup, lifecycle, shutdown): `references/agent-teams.md`
> This section covers **e2e-debug-specific** command and response formats only.

### Verify command (lead → observer)

```
VERIFY
steps:
- Navigate to /operations/service-schedule
- Click 建立服務單
- Select customer 王大明
- Click 快速洗車
- Observe step 3 workspace section
log_tags: [E2E-DBG]
network_filters: [pipeline-preview, api/rest]
report_dir: /absolute/path/.claude/e2e/debug
```

### Observation result (observer → lead)

```
OBSERVATION COMPLETE
steps_executed: 5/5
dbg_logs_captured: 2
errors_captured: 0
network_captured: 1
report_path: /absolute/path/.claude/e2e/debug/report.md

[E2E-DBG] Console:
| Tag | Value | Step |
|-----|-------|------|
| usePipelineWorkspaces:allData | {"data":{"data":{"workspaces":[...]}}} | 4 |
| usePipelineWorkspaces:wsList | undefined | 4 |

JS Errors:
(none)

Network:
| URL | Method | Status | Step |
|-----|--------|--------|------|
| /api/rest/pipeline-preview | GET | 200 | 4 |
```

### Lifecycle and teardown

See `references/agent-teams.md` § 2 (lifecycle detection + teardown sequence).
```

### Round-trip timing (empirical from PoC)

| Operation | Subagent mode | Teams mode (first round) | Teams mode (reuse) |
|-----------|--------------|--------------------------|---------------------|
| Context spawn | ~5-10s | ~5-10s | 0 |
| Browser open + networkidle | ~8-15s | ~8-15s | 0 (navigate only ~3s) |
| Steps + collection | ~10-20s | ~10-20s | ~10-20s |
| Report + close | ~5s | ~2s (message) | ~2s (message) |
| **Total per round** | **~30-50s** | **~25-45s** | **~12-25s** |
