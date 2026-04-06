# kc-hyperfocus

Session lifecycle and context efficiency plugin for Claude Code. Manages context pressure, session handoff/resume, **Context Lake** intelligent cache, and statusline with Anthropic usage quota.

## Measured Impact

Data from 9 repos over 4 days of real usage (2026-04-02 to 2026-04-06):

| Metric | Value |
|--------|-------|
| Cache hits | 626 |
| Lines of code NOT re-read | 96,929 |
| Estimated tokens saved | ~145K |
| Best repo hit rate | 41% (spacedock, 105 insights) |
| Avg lines saved per hit | 256 |

Each cache hit means the agent already knows what a file does before reading it. At 41% hit rate, nearly half of all file reads come with pre-loaded understanding.

## Features

### Context Pressure Management

Monitors context window usage in real-time. Warns the agent when running low and enforces journal writing before session ends.

| Level | Remaining | Action |
|-------|-----------|--------|
| WARNING | <=35% | Agent wraps up current task |
| CRITICAL | <=25% | Agent stops new work, informs user |
| Enforcer | <=17% | Blocks exit until journal complete (max 2 attempts) |

### Session Handoff & Resume

Seamless cross-session continuity. Agent writes a journal entry at handoff; next session resumes with full context via a single handoff ID.

```
/kc-session-handoff  →  journal + Context Lake cache + resume prompt
/kc-session-resume {id}  →  O(1) lookup → present context → wait for direction
```

At session start, the `stale-checker` hook automatically detects pending handoff entries from the last 3 days and surfaces them as a reminder.

### Context Lake

**The problem:** Agents repeatedly explore the same codebase areas, wasting tokens and time. A single Explore dispatch can cost 10-50 tool calls and tens of thousands of tokens.

**The solution:** Context Lake caches file-level insights (3-8 sentence summaries of what a file does, how it's used, and what the gotchas are) in a local SQLite database with FTS5 full-text search. Next time the agent encounters the same files, it already knows.

### Statusline with Usage Quota

Standalone statusline showing model, git branch, context usage bar, and **Anthropic 5h/7d rolling quota utilization**. Also writes the bridge file that context pressure hooks depend on.

```
Opus 4.6 (1M context) | app main ███░░░░░░░ 34% | 5h:43% 7d:70%
```

Run `/kc-statusline-setup` to install. The wizard detects existing statuslines (e.g., GSD) and skips if usage display is already present.

---

## Context Lake Details

### How It Works

```
Session N:
  Agent reads files → hooks track what was read
  Agent calls store_insight() → insight saved to SQLite (FTS5)
  Session handoff → batch-cache remaining insights

Session N+1:
  SessionStart → stale-checker invalidates changed files + detects pending handoffs
  Agent about to Read a file → hook injects cached insight as prior context
  Agent about to Explore → hook suggests cached insights (never blocks)
```

### Hook Trigger Points

#### 1. PreToolUse:Read — `explore-interceptor.js`

When the agent is about to read a file, looks up the file in the cache. If found, injects the cached insight as `additionalContext` so the agent already knows what the file does before reading it.

- **Fresh hit** → inject insight (agent reads with prior understanding)
- **Stale hit** → inject with warning (file changed since last cache)
- **Miss** → no injection, agent reads normally

The Read always proceeds. Cache just adds context.

#### 2. PreToolUse:Agent(Explore) — `explore-interceptor.js`

When the agent is about to dispatch an Explore subagent, searches the cache using keywords from the Explore prompt. If fresh insights exist, provides them alongside the Explore dispatch.

**Behavior:** Always `allow` — Explore runs with cached hints injected. The cache supplements exploration, never blocks it. (Changed in v1.2.1 from deny to allow-and-suggest after FTS5 false positives caused premature denials.)

#### 3. PostToolUse:Read — `read-tracker.js`

After the agent finishes reading a file, silently records the file path. Tracks uncached reads and nudges the agent with specific file paths at thresholds (15/30 uncached reads) to cache insights.

#### 4. PostToolUse:Agent(Explore) — `post-explore-nudge.js`

After an Explore subagent completes, reminds the agent to cache the insights it just gained.

#### 5. SessionStart — `stale-checker.js`

At session start:
1. `git diff HEAD~10..HEAD` → marks cached insights for changed files as stale
2. Evicts ancient insights (>30 days, no hits in 7 days)
3. Syncs technical insights from journal entries (last 3 days)
4. Detects pending session handoffs → surfaces as resume prompt

### Insight Quality

| Source | Quality | When |
|--------|---------|------|
| `manual` (via `/kc-cache-insight`) | Highest | User explicitly caches with confirmation |
| `handoff` (via session handoff) | High | Agent summarizes at session end, has full context |
| `journal` (via journal sync) | Medium-High | Extracted from reflected technical insights |

Higher-quality sources can't be overwritten by lower ones.

### MCP Tools

Context Lake exposes 5 tools via MCP:

| Tool | Purpose |
|------|---------|
| `store_insight` | Cache a 3-5 sentence file summary |
| `search_insights` | Search by file path or keywords (FTS5) |
| `invalidate_stale` | Mark insights as stale for changed files |
| `get_metrics` | Query hit/miss/store/explore metrics |
| `lake_status` | Show DB stats: total, stale, hit rate, top files |

### Skills

| Skill | Usage |
|-------|-------|
| `/kc-cache-insight` | Cache insight for a file (or most recently discussed) |
| `/kc-cache-insight --status` | Show lake stats (total, stale, hit rate) |
| `/kc-cache-insight --metrics` | Show cache effectiveness metrics |
| `/kc-cache-insight --search <query>` | Search cached insights |
| `/kc-cache-insight --dashboard` | Cross-repo overview |
| `/kc-session-handoff` | Write journal + cache insights + produce resume prompt |
| `/kc-session-resume {id}` | Restore context from handoff entry |
| `/kc-statusline-setup` | Install statusline with usage quota display |

---

## Installation

### From Marketplace (recommended)

```bash
/plugin install kc-hyperfocus@kc-claude-plugins
```

### Prerequisites

- Claude Code CLI
- Bun runtime (hooks and MCP server use Bun)

### Post-Install

Install dependencies for the MCP server:

```bash
cd ~/.claude/plugins/cache/kc-claude-plugins/kc-hyperfocus/*/
bun install
```

### Verify

```
/mcp                        → Should show "context-lake: Connected"
/kc-cache-insight --status  → Should show lake stats
```

---

## Configuration

### Context Lake Storage

DB files at `~/.claude/context-lake/{repo-slug}.db`. One DB per repo (auto-detected from `git rev-parse --show-toplevel`).

### Cold Eviction Policy

Default: insights older than 30 days with no hits in the last 7 days are evicted at session start. Configured in `stale-checker.js`.

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
| 1.3.0 | 2026-04-06 | Statusline setup skill, SessionStart handoff detection, context lake protocol reference, handoff/resume metrics, forge TDD (14 edits across 3 skills), published to public marketplace |
| 1.2.1 | 2026-04-05 | Explore: deny→allow+suggest, read-based nudge, worktree path normalization, fileLines savings tracking |
| 1.2.0 | 2026-04-02 | Context Lake: SQLite cache, 4 hooks, MCP server, /kc-cache-insight skill |
| 1.1.0 | 2026-03-17 | MCP summarizer agent, context firewall |
| 1.0.0 | 2026-03-15 | Initial: context pressure, handoff/resume, cleanup enforcement |
