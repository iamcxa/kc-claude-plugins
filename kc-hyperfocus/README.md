# kc-hyperfocus

Session lifecycle and context efficiency plugin for Claude Code. Manages context pressure, session handoff/resume, and **Context Lake** — an intelligent cache that remembers what your agent learned across sessions.

## Features

### Context Pressure Management

Monitors context window usage in real-time. Warns the agent when running low and enforces journal writing before session ends.

### Session Handoff & Resume

Seamless cross-session continuity. Agent writes a journal entry at handoff; next session resumes with full context via a single handoff ID.

### Context Lake (v1.2.0)

**The problem:** Agents repeatedly explore the same codebase areas, wasting tokens and time. A single Explore dispatch can cost 10-50 tool calls and tens of thousands of tokens.

**The solution:** Context Lake caches file-level insights (3-8 sentence summaries of what a file does, how it's used, and what the gotchas are) in a local SQLite database. Next time the agent encounters the same files, it already knows.

---

## Context Lake

### How It Works

```
Session N:
  Agent explores files → hooks track what was read
  Agent calls store_insight() → insight saved to SQLite (FTS5)
  Session handoff → batch-cache remaining insights

Session N+1:
  SessionStart → stale-checker invalidates changed files
  Agent about to Read a file → hook injects cached insight as prior context
  Agent about to Explore a module → hook denies if cache has enough coverage
                                    (agent uses cached data instead)
```

### Architecture

```
                    ┌─────────────────────────┐
                    │     Context Lake DB      │
                    │  ~/.claude/context-lake/ │
                    │    {repo-slug}.db        │
                    │                          │
                    │  Tables:                 │
                    │   insights (FTS5)        │
                    │   metrics                │
                    └──────────┬──────────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                 │
     ┌────────▼────────┐  ┌───▼──────┐  ┌──────▼───────┐
     │   Hook Layer     │  │ MCP      │  │  Skills      │
     │                  │  │ Server   │  │              │
     │ explore-         │  │          │  │ /kc-cache-   │
     │  interceptor     │  │ 5 tools: │  │  insight     │
     │ read-tracker     │  │ store    │  │              │
     │ post-explore-    │  │ search   │  │ /kc-session- │
     │  nudge           │  │ invalidate│ │  handoff     │
     │ stale-checker    │  │ metrics  │  │  (modified)  │
     └─────────────────┘  │ status   │  └──────────────┘
                           └──────────┘
```

### Hook Trigger Points

Every tool call in Claude Code can trigger hooks. Context Lake uses 4 hook events:

#### 1. PreToolUse:Read — `explore-interceptor.js`

**When:** Every time the agent is about to read a file.

**What it does:** Looks up the file in the cache. If found, injects the cached insight into the agent's context so it already knows what the file does before reading it.

```
Agent: "I'll read src/mcp/impact.ts"
  │
  ▼
Hook: Is src/mcp/impact.ts in cache?
  │
  ├── Yes (fresh) → Inject insight as additionalContext
  │   "MCP tool for impact analysis. Key functions: analyzeImpact()..."
  │   Agent reads the file WITH prior understanding
  │
  ├── Yes (stale) → Inject with warning
  │   "⚠️ stale — file changed since last cache"
  │   Agent reads with caution
  │
  └── No → Miss, no injection. Agent reads normally.
```

**Behavior:** `allow` — the Read always proceeds. Cache just adds context.

#### 2. PreToolUse:Agent(Explore) — `explore-interceptor.js`

**When:** The agent is about to dispatch an Explore subagent.

**What it does:** Searches the cache using keywords from the Explore prompt. If enough fresh insights exist (>= 3), **denies** the Explore entirely and provides the cached insights instead.

```
Agent: "I need to explore the impact analysis module"
  │
  ▼
Hook: FTS5 search for "impact analysis module"
  │
  ├── >= 3 fresh hits → DENY Explore + provide cached insights
  │   "Found 3 cached insights covering your query:
  │    1. src/mcp/impact.ts — MCP tool for impact analysis...
  │    2. src/mcp/lineage.ts — Dependency graph builder...
  │    3. src/routes/impact.ts — HTTP route handler..."
  │   Agent uses cached data. Explore never runs.
  │   >>> This is where the main token savings come from <<<
  │
  ├── < 3 fresh hits → ALLOW + partial context
  │   Explore runs, but agent has some prior knowledge
  │
  └── No hits → Miss. Explore runs normally.
```

**Behavior:** `deny` when cache is sufficient (saves entire Explore cost), `allow` otherwise.

#### 3. PostToolUse:Read — `read-tracker.js`

**When:** After the agent finishes reading a file.

**What it does:** Silently records the file path to a temp file. This list is used during session handoff to know which files the agent explored.

```
Agent reads src/foo.ts
  │
  ▼
Hook: Append "src/foo.ts" to /tmp/claude-lake-touched-{session}.json
      (silent — no output, no delay)
```

**Behavior:** Silent tracking. No visible effect.

#### 4. PostToolUse:Agent(Explore) — `post-explore-nudge.js`

**When:** After an Explore subagent completes and returns results.

**What it does:** Reminds the agent to cache the insights it just gained. Also records the Explore completion for the handoff safety net.

```
Explore agent returns results
  │
  ▼
Hook: Inject nudge into agent context:
      "You just completed an exploration. Consider calling
       store_insight for key files you now understand."
  │
  ▼
Agent may immediately cache insights (instant)
  OR
Agent caches them later during session handoff (safety net)
```

**Behavior:** Nudge — the agent decides what's worth caching.

#### 5. SessionStart — `stale-checker.js`

**When:** Every time a new Claude Code session starts.

**What it does:**
1. Runs `git diff` to find recently changed files → marks their cached insights as stale
2. Evicts ancient insights (>30 days old with no recent hits)
3. Syncs insights from journal entries

```
New session starts
  │
  ▼
Hook: git diff HEAD~10..HEAD → ["src/foo.ts", "src/bar.ts"]
      Mark insights for those files as stale
      Evict insights older than 30 days
      Sync technical_insights from recent journal entries
```

### Insight Quality

Not all data sources produce equal quality insights:

| Source | Quality | When |
|--------|---------|------|
| `manual` (via `/kc-cache-insight`) | Highest | User explicitly caches with confirmation |
| `handoff` (via session handoff) | High | Agent summarizes at session end, has full context |
| `journal` (via journal sync) | Medium-High | Extracted from reflected technical insights |

**Source priority guard:** Higher-quality sources can't be overwritten by lower ones. A `manual` insight will never be replaced by a `handoff` or `journal` insight.

### Freshness & Staleness

- Each insight records the `git_hash` at write time
- At session start, `stale-checker` compares against recent git history
- **Fresh** insights are injected normally
- **Stale** insights are still injected but with a warning — the file's purpose and architecture usually survive small changes
- After 30 days without use, insights are automatically evicted

### MCP Tools

Context Lake exposes 5 tools via MCP (auto-prefixed as `mcp__plugin_kc-hyperfocus_context-lake__<tool>`):

| Tool | Purpose |
|------|---------|
| `store_insight` | Cache a 3-5 sentence file summary |
| `search_insights` | Search by file path or keywords (FTS5) |
| `invalidate_stale` | Mark insights as stale for changed files |
| `get_metrics` | Query hit/miss/store/explore_allowed metrics |
| `lake_status` | Show DB stats: total, stale, hit rate, top files |

### Skills

#### `/kc-cache-insight [file_path | --status | --metrics]`

Manual control over the cache:

```
/kc-cache-insight                → Cache insight for most recently discussed file
/kc-cache-insight src/foo.ts     → Cache insight for specific file
/kc-cache-insight --status       → Show lake stats (total, stale, hit rate)
/kc-cache-insight --metrics      → Show cache effectiveness metrics (last 7 days)
```

#### `/kc-session-handoff`

At session end, automatically:
1. Writes journal entry
2. **Caches insights** for files explored during the session (safety net for anything not cached by the nudge hook)
3. Produces resume prompt

### Metrics & Demo

Track cache effectiveness:

```sql
-- Hit rate
SELECT hit_rate_pct FROM lake_status;

-- Explore denials (primary ROI metric — each denial = entire Explore saved)
SELECT COUNT(*) FROM metrics WHERE event = 'explore_allowed';

-- Top cached files
SELECT file_path, COUNT(*) as hits FROM metrics
WHERE event = 'hit' GROUP BY file_path ORDER BY hits DESC;
```

Access via `/kc-cache-insight --metrics` or the `get_metrics` MCP tool.

---

## Context Pressure Management

### How It Works

```
[Normal work] → context-pressure-monitor checks remaining context
  │
  ├── ≤35% → WARNING: "Wrap up current task"
  ├── ≤25% → CRITICAL: "Stop new work, prepare handoff"
  ├── ≤17% → Enforcer activates: blocks session stop until journal is written
  │
  ▼
Agent runs /kc-session-handoff → journal + context lake cache + resume prompt
```

### Thresholds

| Level | Remaining | Action |
|-------|-----------|--------|
| WARNING | ≤35% | Agent wraps up current task |
| CRITICAL | ≤25% | Agent stops new work, informs user |
| Enforcer | ≤17% | Blocks exit until journal complete (max 2 attempts) |

---

## Session Handoff & Resume

### Handoff

```
/kc-session-handoff
  │
  ├── Gather git state (branch, status, recent commits)
  ├── Write journal (feelings + project notes)
  ├── Cache insights to Context Lake (safety net)
  ├── Capture handoff ID
  └── Output: "resume {handoff-id} 繼續 ..."
```

### Resume

```
/kc-session-resume {handoff-id}
  │
  ├── Direct O(1) lookup by handoff ID
  ├── Read journal entry
  ├── Check MEMORY.md for related context
  └── Present summary → wait for direction
```

---

## Installation

### Prerequisites

- Claude Code CLI
- Bun runtime (hooks and MCP server use Bun)

### Setup

1. Clone or symlink the plugin:
   ```bash
   ln -s /path/to/kc-hyperfocus ~/.claude/plugins/local/kc-hyperfocus
   ```

2. Register in local marketplace:
   ```json
   // ~/.claude/plugins/local/.claude-plugin/marketplace.json
   { "plugins": [..., "kc-hyperfocus"] }
   ```

3. Enable in settings:
   ```json
   // ~/.claude/settings.json
   { "enabledPlugins": { "kc-hyperfocus@local": true } }
   ```

4. Install dependencies (for MCP server):
   ```bash
   cd /path/to/kc-hyperfocus && bun install
   ```

5. Restart Claude Code.

### Verify Installation

```
/mcp                        → Should show "context-lake: Connected"
/kc-cache-insight --status  → Should show lake stats
```

---

## Configuration

### Context Lake Storage

DB files at `~/.claude/context-lake/{repo-slug}.db`. One DB per repo (auto-detected from `git rev-parse --show-toplevel`).

### Explore Deny Threshold

The default threshold for denying Explore dispatches is **3 fresh insights**. This is hardcoded in `explore-interceptor.js` as `EXPLORE_DENY_THRESHOLD`. Adjust if the deny rate is too aggressive or too passive.

### Cold Eviction Policy

Default: insights older than **30 days** with no hits in the last **7 days** are evicted at session start. Configured in `stale-checker.js`.

---

## Tech Stack

- **Runtime:** Bun (hooks + MCP server)
- **Database:** SQLite via `bun:sqlite` (WAL mode, FTS5 full-text search)
- **MCP:** `@modelcontextprotocol/sdk` (stdio transport)
- **Dependencies:** Zero npm deps for hooks; SDK + Zod for MCP server

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.2.0 | 2026-04-02 | Context Lake: SQLite cache, 4 hooks, MCP server, /kc-cache-insight skill |
| 1.1.0 | 2026-03-17 | MCP summarizer agent, context firewall |
| 1.0.0 | 2026-03-15 | Initial: context pressure, handoff/resume, cleanup enforcement |
