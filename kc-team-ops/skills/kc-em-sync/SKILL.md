---
name: kc-em-sync
description: Use when syncing team context (initiatives, projects, members, cycles, customers, estimate scale) from Linear to local YAML cache. Triggers on '/kc-em-sync', 'sync team context', 'refresh team data', '同步團隊資料', 'team sync'.
---

# EM Team Context Sync

Fetch team strategic context from Linear and cache as YAML for use by EM triage.

## Arguments

| Invocation | Behavior |
|------------|----------|
| `/kc-em-sync` | Interactive: list teams via `list_teams`, user picks one |
| `/kc-em-sync <team-name>` | Direct sync for named team |
| `/kc-em-sync --all` | Sync all previously synced teams (read existing YAML files in `~/.claude/kc-team-ops/`) |

## Process

### 1. Resolve Team

- If team name provided → `list_teams` → find matching team → get `team_id`
- If no argument → `list_teams` → present list → user picks
- If `--all` → read `~/.claude/kc-team-ops/*.yaml` → extract team names → sync each

### 2. Parallel Fetch

Fetch all data sources concurrently:

| Source | Linear MCP Call | Filter |
|--------|----------------|--------|
| Initiatives | `list_initiatives` | `status: active` only |
| Projects | `list_projects` per initiative | All statuses (show planned too) |
| Members | `list_users(teamId)` | Active members |
| Cycles | `list_cycles(teamId)` | Current + next (type `current`, `next`) |
| Recent issues | `list_issues(teamId, limit: 10)` | For estimate scale inference |
| Customers | `list_customers(includeNeeds: true)` | All customers with needs |

### 3. Infer Estimate Scale

Follow `${CLAUDE_PLUGIN_ROOT}/reference/estimate-inference.md` logic:
- Read recent issues' `estimate.name` values
- Determine scale (T-shirt / Fibonacci / Linear / Exponential / Unknown)
- If Unknown → note in YAML, will prompt user during triage

### 4. Assemble & Write YAML

Write to `~/.claude/kc-team-ops/<team-name>-context.yaml`:

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

next_cycle:
  id: "<id>"
  name: "<name>"
  starts: "<date>"
  ends: "<date>"

estimate_scale: "<tshirt|fibonacci|linear|exponential|unknown>"
estimate_values: ["<value1>", "<value2>", ...]
```

### 5. Confirm

Display summary:
```
✅ Synced <team-name> context
   Initiatives: N active (M projects)
   Customers: N (M needs)
   Members: N
   Cycle: <current cycle name> (ends <date>)
   Estimate scale: <scale>
   Cache: ~/.claude/kc-team-ops/<team-name>-context.yaml
```

## Error Handling

| Error | Action |
|-------|--------|
| **Linear MCP unavailable** | Stop immediately. Display `❌ Linear MCP not available — cannot sync. Check MCP server configuration.` Do NOT retry or fall back. |
| **Team not found** | Display `❌ No team matching "<input>" found. Available teams: [list from list_teams]`. Use case-insensitive matching when comparing user input against team names. |
| **`--all` with no existing cache** | Display `⚠️ No existing cache files in ~/.claude/kc-team-ops/. Use /kc-em-sync <team-name> to sync a specific team first.` |
| **Write permission failure** | Display error and suggest manual directory creation: `mkdir -p ~/.claude/kc-team-ops/` |
| **Partial fetch failure** | Write what succeeded, mark failed sections as `null` in YAML, display which sources failed. A partial cache is better than no cache. |

## Rules

- **Never create directory without checking** — `mkdir -p ~/.claude/kc-team-ops/` before write
- **Parallel fetch** — all 6 sources concurrently, don't serialize
- **Preserve manual edits** — if YAML has fields not in the schema (e.g., user-added annotations), preserve them
- **UTF-8 YAML** — team/member names may be non-ASCII
- **Idempotent** — running sync twice produces the same file (modulo `synced_at` timestamp)
- **Case-insensitive team matching** — compare user input against `list_teams` results case-insensitively
