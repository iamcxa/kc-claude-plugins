# Nightwatch Dashboard — Design Specification

> **Project**: kc-nightwatch/app/
> **Version**: MVP (v1.0)
> **Date**: 2026-03-18
> **Status**: Draft

## Overview

Transform kc-nightwatch from a cron-based nightly job into an interactive autonomous improvement platform with a web dashboard. The system monitors codebases, discovers improvement signals, proposes or fixes issues, self-assesses its work, learns from feedback, and implements accepted proposals — forming a closed-loop flywheel.

**Location**: `kc-claude-plugins/kc-nightwatch/app/`
**Relationship**: Lives alongside the existing nightwatch plugin (skills, agents, config). The app wraps the plugin's capabilities in a persistent server with a web UI.

## Architecture

### Two-Process Model

```
Browser (Preact + HTM)
    │ HTTP + SSE + WebSocket
    ▼
Bun HTTP Server (Hono)          ← API, SSE streaming, MCP server, static files
    │ Unix socket / IPC
    ▼
Worker Process                  ← Scheduler, execution queue, claude -p spawning
    │
    ▼
safehouse → claude -p           ← Sandboxed execution per target
```

**Server process**: Hono HTTP server handling REST API, SSE log streaming, WebSocket chat, MCP endpoint, and static frontend serving. Single entry point starts both processes.

**Worker process**: Manages the scheduler (interval timers), execution queue (max concurrency: 1), and spawns `claude -p` child processes inside agent-safehouse. Communicates with server via Unix socket IPC.

### IPC Protocol

Server → Worker:
- `{ type: 'enqueue', run: Run }` — start a run
- `{ type: 'cancel', run_id: string }` — abort running
- `{ type: 'schedule', config: ScheduleConfig }` — update schedule
- `{ type: 'status' }` — request current state

Worker → Server:
- `{ type: 'run:started', run_id, pid }`
- `{ type: 'run:log', run_id, event }` — parsed stream-json line
- `{ type: 'run:completed', run_id, summary }`
- `{ type: 'run:failed', run_id, error }`
- `{ type: 'state', queue: Run[], current?: Run, schedule }`

## Tech Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| Runtime | Bun | TypeScript, ESM |
| HTTP framework | Hono | Lightweight, Bun-native |
| Frontend | Preact + HTM | ~3KB, component model + hooks, no build step |
| Real-time | SSE (logs) + WebSocket (chat) | SSE for one-way streaming, WS for bidirectional chat |
| Sandbox | agent-safehouse | macOS sandbox-exec, per-target policy |
| Claude CLI | `claude -p --output-format stream-json` | Real-time streaming output |
| Styling | CSS (GitHub dark theme) | No framework |

## Directory Structure

```
kc-nightwatch/
├── .claude-plugin/plugin.json    # existing plugin manifest
├── agents/                       # existing nightwatch agents
├── skills/                       # existing nightwatch skills
├── config/                       # existing safety.yaml, plist, cron
├── CLAUDE.md
│
└── app/                          # NEW: dashboard application
    ├── package.json
    ├── tsconfig.json
    │
    ├── server/
    │   ├── index.ts              # entry point (starts server + worker)
    │   ├── routes/
    │   │   ├── api.ts            # /api/targets, /api/runs, /api/webhook
    │   │   ├── stream.ts         # /api/runs/:id/stream (SSE)
    │   │   ├── config.ts         # /api/config (YAML read/write + validation)
    │   │   ├── chat.ts           # /ws/chat (WebSocket ↔ NW-Claude)
    │   │   └── mcp.ts            # /mcp (MCP server endpoint)
    │   ├── services/
    │   │   ├── yaml-store.ts     # read/write YAML config files
    │   │   ├── run-store.ts      # read run history + artifacts
    │   │   ├── chat-session.ts   # manage NW-Claude process lifecycle
    │   │   └── auth.ts           # optional token auth
    │   └── ipc.ts               # communicate with worker
    │
    ├── worker/
    │   ├── index.ts              # entry point (IPC listener)
    │   ├── scheduler.ts          # interval + webhook trigger management
    │   ├── executor.ts           # spawn safehouse + claude -p
    │   ├── policy.ts             # generate safehouse flags per target
    │   └── log-parser.ts         # parse stream-json → structured events
    │
    ├── frontend/
    │   ├── index.html            # shell
    │   ├── app.tsx               # root component + router
    │   ├── pages/
    │   │   ├── dashboard.tsx     # target cards + chat panel
    │   │   ├── runs.tsx          # run history + detail + live view
    │   │   └── config.tsx        # YAML editor with guards
    │   ├── components/
    │   │   ├── target-card.tsx
    │   │   ├── run-timeline.tsx
    │   │   ├── log-stream.tsx
    │   │   ├── yaml-editor.tsx
    │   │   ├── trigger-dialog.tsx
    │   │   ├── chat-panel.tsx
    │   │   ├── feedback-buttons.tsx
    │   │   └── add-target-wizard.tsx
    │   └── lib/
    │       ├── api.ts            # fetch wrapper
    │       ├── sse.ts            # SSE client hook
    │       └── ws.ts             # WebSocket client hook
    │
    ├── shared/
    │   ├── types.ts              # shared types (Run, Target, etc.)
    │   └── constants.ts
    │
    └── runs/                     # run artifacts (gitignored)
        └── {run-id}/
            ├── log.jsonl         # raw stream-json from claude -p
            ├── summary.yaml      # structured result + assessments
            ├── custom-prompt.txt # if manual run had custom instructions
            └── stdout.txt        # plain text output
```

## Data Model

### Target (revised config schema)

```yaml
targets:
  e2e-pipeline:
    type: plugin                    # plugin | product

    # WHERE to look for signals
    monitors:
      - github-issues              # gh issue list (open bugs, feature requests)
      - journal                    # private journal search
      - episodic-memory            # cross-session patterns
      - memory-md                  # stable unabsorbed lessons
      - git-churn                  # high-change files, staleness

    # WHAT to look for (search terms for journal/memory monitors)
    watch: [e2e, browser test, mapping, selector, flow, agent-browser]

    # HOW to respond
    respond:
      code-fix: true               # error → fix PR (direct)
      proposal: true               # improvement → PROPOSAL.md PR (draft)
      alert: true                  # notify only

    # WHAT success looks like
    north_star: "Browser E2E fully automated, zero manual selector maintenance"
    indicators:
      - id: mapping-freshness
        description: "UI mappings stay in sync"
      - id: pipeline-friction
        description: "Pipeline issues in journal"
        target: "approaching 0"

    # EXECUTION context (all optional)
    auth: default                  # 'default' = current account, or token name
    extra_plugin_dirs: []          # additive to user scope
    extra_mcp_config: []           # additive to project .mcp.json
```

**Field renaming** (from v0.4):

| Old | New | Semantics |
|-----|-----|-----------|
| `sources` | `monitors` | "What channels am I monitoring" |
| `keywords` | `watch` | "What am I watching for" |
| `actions` | `respond` | "How to respond" (map with on/off per type) |
| `proxy_signals` | `indicators` | "Success indicators" |

**Execution context**: Worker sets `cwd` to the target's resolved path before spawning `claude -p`. This causes Claude to automatically load the project's `.mcp.json`, `.claude/settings.json`, and `CLAUDE.md`. The `extra_*` fields are additive — they add nightwatch-specific plugins/MCPs on top of what the project already has.

### Run

```typescript
interface Run {
  id: string                       // uuid
  target: string | '__all__'       // single target or full pipeline
  mode: 'production' | 'dry-run' | 'self-repair'
  trigger: 'manual' | 'interval' | 'webhook' | 'implementation'
  status: 'queued' | 'running' | 'completed' | 'failed' | 'timeout'
  custom_prompt?: string           // optional instructions from manual trigger
  proposal_id?: string             // if trigger is 'implementation'
  started_at?: string
  completed_at?: string
  duration_seconds?: number
  summary?: RunSummary
  pre_assessment?: string          // Round 1: strategy assessment
  post_assessment?: string         // Round 2: reflection assessment
  log_path: string
}
```

### AppConfig

```typescript
interface AppConfig {
  host: string                     // '127.0.0.1' or '0.0.0.0'
  port: number
  auth_token?: string              // required when host != localhost
  schedule: ScheduleConfig
  max_concurrent_runs: 1
  safehouse_path?: string          // path to safehouse binary
  plugins_dir: string              // ~/.claude/plugins/local
}

interface ScheduleConfig {
  enabled: boolean
  interval_hours?: number          // e.g. 2 = every 2 hours
  self_repair_before: boolean      // run self-repair session first
}
```

## Execution Flow

### Run Lifecycle

```
TRIGGER                     WORKER                          BROWSER
(manual/interval/webhook)
        │
        ▼
  POST /api/runs ──IPC──→  enqueue
                            │
                            ├─ resolve target path
                            ├─ build safehouse flags (per-target)
                            ├─ spawn claude -p
                            │    cwd = target path
                            │    --output-format stream-json
                            │    --mcp-config nw-mcp + nw-journal
                            │    --append-system-prompt {custom}
                            │
                  ◄──IPC──  run:log (each event) ──SSE──→ log-stream
                            │
                  ◄──IPC──  run:completed ──SSE──→ dashboard refresh
                            │
                            ├─ write log.jsonl + summary.yaml
                            ├─ append nightwatch-runs.yaml
                            └─ auto-spawn NW-Claude brief session
```

### Safehouse Policy (per-target)

```typescript
function buildSafehouseFlags(target: Target, run: Run): string[] {
  const flags: string[] = []

  // Target dir — read-only for analysis, read-write for production
  if (run.mode === 'dry-run') {
    flags.push('--add-dirs-ro', target.resolved_path)
  } else {
    flags.push('--add-dirs', target.resolved_path)
  }

  // Plugin dirs — read-only
  for (const dir of [...basePluginDirs, ...target.extra_plugin_dirs]) {
    flags.push('--add-dirs-ro', dir)
  }

  // User config dir — read + write
  flags.push('--add-dirs', '~/.claude/kc-plugins-config')

  // NW memory dir — read + write
  flags.push('--add-dirs', `~/.claude/nightwatch/memory/${target.name}`)

  // Run artifacts — write
  flags.push('--add-dirs', `app/runs/${run.id}`)

  return flags
}
```

### Stream-JSON Parsing

`claude -p --output-format stream-json` emits JSON lines. The `log-parser.ts` extracts:
- **Phase progress** — detect "Phase 0", "Phase 1", etc. in assistant messages
- **Tool calls** — Skill invocations, agent dispatches, file edits
- **Errors** — tool failures, MCP unavailable
- **Assessments** — pre-action strategy and post-action reflection
- **Summary** — final assistant message with completion report

## Pipeline Phases (revised)

```
Phase 0:   Resolve        — load config, resolve paths, check skip guards
Phase 1:   Forge Check    — plugin targets only, skip if forge unavailable
Phase 2:   Monitor        — dispatch agents per enabled monitor
Phase 3:   Classify       — confidence filter, cooldown, map to indicators
Phase 3.5: Assess (pre)   — strategy: "what's the best approach to north star?"
Phase 4:   Respond        — code-fix PR / proposal PR / alert
Phase 4.5: Assess (post)  — reflection: "did this move closer to north star?"
Phase 5:   Report         — Slack + dashboard + run artifacts
```

### Two-Phase Self-Assessment

**Phase 3.5 (pre-action)**: After classifying signals, before responding. NW asks itself:
> "Given these N signals mapped to indicators, what's the best strategy to move toward north_star? Prioritize and explain reasoning."

Writes strategy to NW journal (target-specific). Informs Phase 4 action ordering.

**Phase 4.5 (post-action)**: After creating PRs/proposals. NW evaluates each action:
> "Does this {code-fix/proposal} move {target} closer to north_star? Why? Confidence: {high/medium/low}"

Assessment stored in `summary.yaml`, displayed in dashboard run detail and Slack report.

### Proposal → Implementation Pipeline

When a proposal is accepted (dashboard, chat, or MCP):

```
Proposal accepted
    ↓
NW spawns IMPLEMENTATION run:
    claude -p "Implement this proposal: {PROPOSAL.md content}"
      cwd = target_path
      safehouse: read-write on target
    ↓
Creates implementation PR (not draft)
    ↓
Self-assessment + forge validation (if plugin)
    ↓
If forge FAIL or test FAIL → revert, log to NW journal
    ↓
Report + feedback loop continues
```

**Safety**: Only accepted proposals are implemented. Implementation PR is separate from proposal PR — user reviews code changes independently.

## NW Memory Layer

Per-target isolated journal using private-journal MCP:

```
~/.claude/nightwatch/memory/
├── e2e-pipeline/.private-journal/     # NW's memory about e2e-pipeline
├── kc-nightwatch/.private-journal/    # NW's memory about itself
└── carlove/.private-journal/          # NW's memory about carlove
```

Worker injects target-specific journal via `--mcp-config`:

```json
{
  "mcpServers": {
    "nw-journal": {
      "type": "stdio",
      "command": "private-journal",
      "args": ["--dir", "~/.claude/nightwatch/memory/{target}/"]
    }
  }
}
```

**Isolation**: Running e2e-pipeline only loads e2e-pipeline's NW journal. No cross-target memory leakage. User's personal journal/memory is a separate layer loaded from project settings.

**What NW writes to its journal**:
- Pre-action strategy assessments
- Post-action reflections
- Feedback trends ("indicator X reject rate rising, proposals too generic")
- Implementation outcomes
- Lessons from failed actions

## MCP Server

Exposed as HTTP endpoint on the Hono server at `/mcp`. Allows any Claude session to query and command nightwatch.

### Tools

| Tool | Type | Description |
|------|------|-------------|
| `nw_get_targets` | Query | List all targets with latest status |
| `nw_get_latest_run` | Query | Last run for a target — full summary + assessments |
| `nw_get_run` | Query | Specific run by ID — detail, log, assessments |
| `nw_get_proposals` | Query | Pending proposal branches across all repos |
| `nw_get_config_warnings` | Query | Current config issues from self-repair |
| `nw_get_schedule` | Query | Scheduler state (interval, next run) |
| `nw_trigger_run` | Action | Enqueue a run (target, mode, custom_prompt) → run_id |
| `nw_run_targeted` | Action | Run focused on specific issue/signal → run_id |
| `nw_implement_proposal` | Action | Accept proposal + spawn implementation run → run_id |
| `nw_submit_feedback` | Action | Record accept/reject/correct with reason |
| `nw_update_schedule` | Action | Modify interval, enable/disable |

### Usage Pattern

```
User Claude → nw_trigger_run(target, mode, prompt) → {run_id, status: "queued"}
User Claude → nw_get_run(run_id)                   → {status: "running", phase: "Phase 2"}
User Claude → nw_get_run(run_id)                   → {status: "completed", summary, prs}
```

**Auth**: Same token as dashboard. MCP endpoint checks Bearer token when `host != localhost`.

**Lifecycle**: MCP is available only when the app is running. Claude sessions without the app fall back to reading YAML files directly (existing nightwatch behavior).

## Frontend UI

### Pages

| Page | Route | Purpose |
|------|-------|---------|
| Dashboard | `/` | Target cards grid + NW-Claude chat panel (right side) |
| Runs | `/runs`, `/runs/:id` | History list + run detail with log, assessments, feedback |
| Config | `/config` | YAML editor with guards + add target wizard |

### Dashboard

- **Target cards**: Name, type badge, north star excerpt, last run summary, action counts
- **Per-card actions**: ⋮ context menu → Run / Run (dry) / Edit / Chat about this / Remove
- **Global actions**: Run All / Run All (dry-run)
- **Schedule status bar**: interval, next run countdown, last run summary
- **Chat panel**: Right side, persistent NW-Claude conversation

### NW-Claude Chat Panel

- **Auto-brief**: After each run completes, server spawns NW-Claude with run results as system prompt. Generates summary as first message.
- **Bidirectional**: Browser ↔ WebSocket ↔ Server ↔ `claude --input-format stream-json --output-format stream-json`
- **NW-Claude capabilities**: Has NW-MCP (trigger runs, query state, submit feedback), NW journal (target memory), gh CLI (operate on PRs)
- **Per-target focus**: "Chat about this" from target card loads that target's NW journal + latest run
- **Session lifecycle**: Persists until user closes or resets. New run completion prompts "Switch context?" without killing active conversation.

### Run Detail

- **Phase progress bar**: Phase 0 through 5, color-coded (done/active/pending)
- **Log stream**: Monospace, real-time SSE during execution, full log after completion
- **Action cards**: Each action shows type badge, summary, PR link, indicator, self-assessment block
- **Feedback buttons**: 👍/👎 per action card
- **Cancel button**: Available during execution

### Config Editor

**Default state**: Read-only (🔒 locked). Config warnings from self-repair displayed inline.

**Edit flow**:
1. Click 🔓 Enable Editing → editor becomes active (blue border)
2. Edit YAML content
3. Click "Review Changes" → modal opens with 4-step validation:
   - **Step 1**: Static validation (instant) — YAML syntax + schema check
   - **Step 2**: Semantic validation (~30s) — spawn `claude -p --model haiku --max-budget-usd 0.05` to verify Linear teams, resolve paths, check Sentry access. Progress shown per-target in real-time.
   - **Step 3**: Diff preview — show changes with red/green highlighting
   - **Step 4**: Confirm Save
4. Errors block save. Warnings don't block but surface in dashboard.

**Add Target wizard** (4 steps):
1. Type (plugin/product) + Name
2. North star + watch terms + indicators
3. Monitors + respond config (pre-filled by type, user can override)
4. Review + semantic validation → add to targets.yaml

**Edit Target**: Same wizard, pre-filled with current values.

**Remove Target**: Confirm dialog → removes from targets.yaml (no file deletion).

### Trigger Dialog

Modal when manually triggering a run:
- Mode toggle: Production / Dry-run
- Custom instructions textarea (optional, saved to `runs/{id}/custom-prompt.txt`)
- Self-repair toggle: Run self-repair first (default on)
- Start Run button

## Feedback System

### Collection Channels

| Channel | MVP? | Mechanism |
|---------|------|-----------|
| PR status | ✓ MVP | merge = accepted, close = rejected (existing Phase SR.3) |
| Linear issue status | ✓ MVP | done = accepted, wontfix = rejected (existing Phase SR.3) |
| Dashboard 👍/👎 | ✓ MVP | POST /api/feedback per action |
| MCP `nw_submit_feedback` | ✓ MVP | Any Claude session submits verdict + reason |
| NW-Claude chat | ✓ MVP | User directs feedback in conversation |
| Slack reactions | v2 | 👍/👎/🔇 on 晨報 messages (requires Slack MCP read) |
| PR review comments | v2 | Parse "nightwatch: good/bad" in review comments |

### Consumption Flow

```
All channels → nightwatch-feedback.yaml
                    ↓
              Phase 0 of next run:
                Per indicator:
                  reject_rate = rejected / (accepted + rejected)
                  rate > 0.5 → only high confidence
                  rejected signal → 30d cooldown
                  muted → permanent skip until unmuted
                    ↓
              ALSO: Write trend to NW journal
                "indicator X reject rate rising because..."
                    ↓
              Phase 3.5 pre-assessment reads journal
                → naturally adjusts strategy
```

**Dual learning paths**: Reject rate calibration (fast, numeric) + NW journal reflection (slow, semantic).

## Scheduling

### Trigger Types (MVP)

| Type | Mechanism |
|------|-----------|
| **Interval** | Worker sets timer (e.g., every 2 hours). Persisted in AppConfig. |
| **Manual** | Dashboard button or chat command |
| **Webhook** | POST /api/webhook with optional target + mode + auth token |

### Execution Queue

- Max concurrency: 1
- Additional triggers queued (FIFO)
- MCP-triggered runs enter same queue (no priority skip in MVP)
- Queue visible in dashboard status bar

## Security

### Network

- **Default**: Bind to `127.0.0.1` (localhost only)
- **Remote mode**: `0.0.0.0` + `auth_token` required in AppConfig
- All API/MCP/WebSocket endpoints check Bearer token when remote mode active

### Execution Sandbox

- **agent-safehouse** wraps every `claude -p` invocation
- Per-target policy: read-only for analysis, read-write only for production mode
- Plugin dirs always read-only
- User config dir (`~/.claude/kc-plugins-config`) read-write (improvement-log, runs.yaml)
- NW memory dir per-target read-write

### Config Safety

- YAML editor locked by default
- 4-step save: static validation → semantic validation (Claude) → diff → confirm
- Semantic validation budget capped at $0.05 (Haiku model)
- Remove target requires explicit confirmation

## Config File Mapping

### Existing (user-scope, unchanged)

| File | Purpose |
|------|---------|
| `~/.claude/kc-plugins-config/nightwatch-targets.yaml` | Target definitions |
| `~/.claude/kc-plugins-config/nightwatch-runs.yaml` | Run history |
| `~/.claude/kc-plugins-config/nightwatch-improvement-log.md` | Action history + cooldown |
| `~/.claude/kc-plugins-config/nightwatch-feedback.yaml` | Feedback data |
| `~/.claude/kc-plugins-config/nightwatch-self-repair.yaml` | Config health check results |
| `~/.claude/kc-plugins-config/channels.yaml` | Slack channel config |
| `~/.claude/kc-plugins-config/language.yaml` | Language preferences |

### New (app-scope)

| File | Purpose |
|------|---------|
| `app/nightwatch-app.yaml` | AppConfig (host, port, auth, schedule) |
| `app/runs/{id}/` | Run artifacts (log, summary, custom prompt) |
| `~/.claude/nightwatch/memory/{target}/` | Per-target NW journal |
| `kc-nightwatch/config/safety.yaml` | Safety limits (existing, read by app) |

## Out of Scope (future)

- Cron expression scheduling
- File watch triggers (git push detection)
- Multi-user auth / RBAC
- Cross-machine sync / cloud dashboard
- channels.yaml / language.yaml editing in UI
- Custom MCP/plugin marketplace per target
- Per-target auth token management (prepared in schema, not implemented)

## Appendix A: Migration & Compatibility

### Field Renaming Strategy

The app introduces new field names (`monitors`, `watch`, `respond`, `indicators`) but the existing nightwatch skill (SKILL.md) uses old names (`sources`, `keywords`, `actions`, `proxy_signals`). Strategy:

**Phase 1 (MVP)**: App reads/writes both old and new names. Compatibility layer in `yaml-store.ts`:
- Read: accept both `monitors` and `sources`, prefer new name if both present
- Write: always write new names
- Existing SKILL.md phases continue reading old names (no skill changes in MVP)

**Phase 2 (post-MVP)**: Migrate SKILL.md to new names, drop old name support.

### Action Type Mapping

| App (respond) | Skill (actions) | Notes |
|---------------|----------------|-------|
| `code-fix` | `quick-fix` | Same behavior, better name |
| `proposal` | `proposal` | Unchanged |
| `alert` | `alert` | Unchanged |
| — | `linear-issue` | Supported if target has `linear_team` config |
| — | `e2e-flow` | Supported if target has e2e-pipeline plugin |

The `respond` map is the UI-facing config. The worker translates to the skill's `actions` list at dispatch time. `linear-issue` and `e2e-flow` are auto-enabled based on target capabilities, not listed in `respond`.

## Appendix B: Undefined Types

### RunSummary

```typescript
interface RunSummary {
  targets_active: number
  targets_skipped: number
  total_signals: number
  total_actions: number
  errors: number
  per_target: Record<string, {
    monitors: Record<string, { status: string, signals: number }>
    pipeline: {
      found: number
      after_dedup: number
      after_confidence_filter: number
      after_cooldown: number
      classified: Record<string, number>
      executed: Record<string, number>
    }
    actions: Array<{
      type: string
      summary: string
      pr_url?: string
      branch?: string
      indicator: string
      assessment: {
        closer_to_north_star: 'yes' | 'no' | 'uncertain'
        confidence: 'high' | 'medium' | 'low'
        reasoning: string
      }
    }>
  }>
  pre_assessment: string           // Phase 3.5 strategy text
  post_assessment: string          // Phase 4.5 reflection text
}
```

## Appendix C: Worker Process Details

### IPC Transport

Unix domain socket at `${APP_DIR}/nightwatch.sock`. Server creates socket on startup, worker connects.

- Protocol: newline-delimited JSON (one JSON object per line)
- Server is socket server, worker is client
- If worker crashes: server detects disconnect, logs error, marks current run as `failed`, cleans up orphan `claude -p` processes (`kill -TERM` by stored PID)
- If server restarts: creates new socket, worker reconnects (worker has reconnect loop with 1s backoff)

### Worker Implementation

Worker is a separate `bun run worker/index.ts` invocation, spawned by the server entry point (`server/index.ts`):

```typescript
const worker = Bun.spawn(['bun', 'run', 'worker/index.ts'], {
  env: { ...process.env, NW_SOCKET: socketPath },
  stdio: ['ignore', 'pipe', 'pipe']
})
```

### Timeout Enforcement

Worker reads `global.max_runtime_minutes` from `safety.yaml` (default: 30). Each `claude -p` child process is wrapped:

```typescript
const child = Bun.spawn(['safehouse', ...flags, 'claude', '-p', ...])
const timer = setTimeout(() => {
  child.kill('SIGTERM')
  run.status = 'timeout'
}, config.max_runtime_minutes * 60 * 1000)
```

### Graceful Shutdown

On SIGINT/SIGTERM to server:
1. Stop accepting new HTTP connections
2. Send `{ type: 'shutdown' }` to worker via IPC
3. Worker: cancel current run (SIGTERM to claude -p), drain queue, close socket
4. Server: close SSE connections, close WebSocket sessions, remove socket file
5. Exit

## Appendix D: Chat Implementation

### Claude CLI Bidirectional Streaming

The NW-Claude chat uses `--input-format stream-json --output-format stream-json` for bidirectional communication. This is a documented Claude CLI feature (verified from `claude -p --help`).

Server manages the `claude` process:

```typescript
const claude = Bun.spawn(['claude',
  '--input-format', 'stream-json',
  '--output-format', 'stream-json',
  '--mcp-config', nwMcpConfigPath,
  '--mcp-config', nwJournalConfigPath,
  '--system-prompt', runBriefText,
  '--plugin-dir', nightwatchPluginDir,
], { stdin: 'pipe', stdout: 'pipe', cwd: targetPath })
```

User messages from WebSocket are written to `claude.stdin` as stream-json. Claude responses from `claude.stdout` are parsed and forwarded to WebSocket.

**Note**: This is the CLI approach. If `--input-format stream-json` proves unreliable for long-lived sessions, fallback to the Anthropic API directly (using `@anthropic-ai/sdk`) with tool definitions matching the MCP tools. The API approach gives more control but loses Claude Code's built-in tool execution. Decision deferred to implementation.

## Appendix E: Additional Resolutions

### `__all__` Target Runs

When `target: '__all__'`, the worker executes targets sequentially (respecting `max_concurrent_runs: 1`). Each target gets its own `claude -p` process with its own `cwd`, safehouse policy, and NW journal. The run creates sub-entries in `summary.per_target`. This matches the existing cron behavior where one `claude -p` session processes all targets sequentially within the same skill invocation.

### `nw_run_targeted` vs `nw_trigger_run`

`nw_run_targeted` is a convenience wrapper. It creates a run with:
- `target`: specified target
- `custom_prompt`: "Focus on issue {issue_ref}: {issue_title}. Only create {respond_filter} actions."
- `mode`: production (default) or dry-run

Internally it calls the same execution path as `nw_trigger_run`. The MCP tool exists for ergonomics — Claude sessions can say "fix this issue" without composing the custom prompt manually.

### `max_concurrent_runs` Type

Changed from literal `1` to `number` with default 1 in AppConfig:
```typescript
max_concurrent_runs: number  // default: 1
```

### Safehouse Path Resolution

All paths in `buildSafehouseFlags` are resolved to absolute paths using `path.resolve(os.homedir(), ...)` before passing to safehouse. No tilde expansion in string literals.

### Monitor-to-Agent Mapping

| Monitor name | Agent | Notes |
|-------------|-------|-------|
| `github-issues` | signal-harvester (enhanced) | New capability: harvester also searches gh issues |
| `journal` | signal-harvester | Existing |
| `episodic-memory` | signal-harvester | Existing |
| `memory-md` | signal-harvester | Existing |
| `git-churn` | git-scanner | Existing (renamed from `git-stats`) |
| `sentry` | sentry-scanner | Existing (product targets) |
| `e2e-reports` | e2e-scanner | Existing (product targets) |

### Frontend Build

Preact + HTM uses tagged template literals (`html\`<div>...</div>\``), not JSX. Frontend files use `.ts` (not `.tsx`). Bun serves them directly with on-the-fly transpilation in dev mode. Production build uses `Bun.build()` to bundle into a single JS file inlined into `index.html`.

### App Bootstrap

On first start, if `app/nightwatch-app.yaml` doesn't exist, server creates it with defaults:

```yaml
host: "127.0.0.1"
port: 3200
schedule:
  enabled: false
  interval_hours: 2
  self_repair_before: true
max_concurrent_runs: 1
plugins_dir: "~/.claude/plugins/local"
```

`app/runs/` directory created on first run. NW memory directories created per-target on first execution.

### Run Artifact Cleanup

Rolling policy: keep last 50 run directories. On each run completion, worker checks total count and removes oldest directories exceeding the limit. Configurable via `safety.yaml` (future) or hardcoded in MVP.

### Feedback API Route

`POST /api/feedback` is handled in `routes/api.ts`:

```
POST /api/feedback
Body: { signal_id: string, verdict: 'accepted' | 'rejected' | 'corrected', reason?: string }
→ Appends to nightwatch-feedback.yaml
→ Returns { recorded: true }
```

### MCP Transport

The MCP server at `/mcp` uses Streamable HTTP transport (HTTP+SSE). Client configuration:

```json
{
  "mcpServers": {
    "nightwatch": {
      "type": "http",
      "url": "http://localhost:3200/mcp",
      "headers": { "Authorization": "Bearer {token}" }
    }
  }
}
```

Headers only required in remote mode.

### Chat "Switch Context" UX

Inline message in the chat panel (not modal, not toast):

```
[system] New run completed: kc-nightwatch (3 signals, 1 PR).
         [Switch to this run] [Keep current conversation]
```

User clicks inline button or continues typing (keeps current). No auto-switch.
