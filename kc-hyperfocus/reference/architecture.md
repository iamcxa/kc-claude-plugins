# Hyperfocus Architecture

## Session Lifecycle Data Flow

```
Session Start
    │
    ├── stale-checker.js (SessionStart)
    │     git diff → invalidateStale()
    │     coldEvict(30d, 7d idle)
    │     journal sync → storeInsight(source: 'journal')
    │
    ▼
[Normal work] ←── context-pressure-monitor.js (PostToolUse)
    │                  reads: /tmp/claude-ctx-{session}.json
    │                  emits: WARNING at ≤35%, CRITICAL at ≤25%
    │                  debounce: 5 tool calls between warnings
    │
    ▼
[Context pressure detected]
    │
    ├── session-cleanup-tracker.js (PostToolUse)
    │     reads: /tmp/claude-ctx-{session}.json (CRITICAL at ≤17%)
    │     tracks: journal calls (feelings, project_notes)
    │     tracks: GSD skill calls
    │     writes: /tmp/claude-cleanup-{session}.json
    │
    ▼
[Agent tries to stop]
    │
    ├── session-cleanup-enforcer.js (Stop)
    │     reads: /tmp/claude-cleanup-{session}.json
    │     if CRITICAL + journal incomplete → block stop
    │     max 2 attempts → safety valve release
    │     directs agent to invoke /kc-session-handoff
    │
    ▼
[/kc-session-handoff invoked]
    │
    ├── Gather git state
    ├── Write journal (feelings + project_notes)
    ├── Context Lake capture (safety net)
    │     read touched files + completed explores
    │     cache insights for deeply understood files
    ├── Capture handoff ID from journal path
    ├── Knowledge capture check (MEMORY.md)
    └── Output resume prompt with ID
         │
         ▼
[Next session]
    │
    ├── User pastes: "resume {handoff-id} 繼續 ..."
    │
    ▼
[/kc-session-resume invoked]
    │
    ├── Route: ID present → direct O(1) lookup
    │         no ID → list recent handoffs → user picks
    ├── Read journal entry
    ├── Check MEMORY.md for related context
    ├── CLAUDE.md migration check (3.5)
    ├── Worktree mismatch warning (if applicable)
    └── Present summary → wait for user direction
```

## Context Lake Data Flow

> **v1.6.4 change** — the PreToolUse Read/Explore injector and the PostToolUse
> Explore nudge have been removed. The cache is now consulted on demand via the
> `/kc-cache-insight` skill and the context-lake MCP tools. Reads still record
> their target paths for handoff and trigger silent background auto-extraction.

```
[Agent reads a file]
    │
    ├── PostToolUse:Read — read-tracker.js (silent — no agent-visible output)
    │     append file_path to /tmp/claude-lake-touched-{session}.json
    │     uncached code file → autoExtract → storeInsight(source: "auto")
    │
    ▼
[Agent explicitly consults the cache]
    │
    ├── /kc-cache-insight skill (manual cache + status + metrics)
    ├── MCP context-lake tools (search_insights, store_insight, ...)
    │
    ▼
[Session handoff]
    │
    ├── Read /tmp/claude-lake-touched-{session}.json
    ├── Batch-cache remaining deeply-understood files (source: "handoff")
    └── Cleanup temp file
```

## Context Lake Storage

```
~/.claude/context-lake/
  ├── kc-claude-workspace.db        # one DB per repo
  ├── kc-claude-workspace.db-wal    # WAL journal
  ├── kc-claude-workspace.db-shm    # shared memory
  ├── recce-cloud.db                # another repo
  └── ...
```

Each DB contains:

| Table | Purpose |
|-------|---------|
| `insights` | File-level summaries (UNIQUE on file_path) |
| `insights_fts` | FTS5 virtual table for keyword search (external content mode) |
| `metrics` | Event log: hit, miss, store, explore_allowed |

### Connection Settings

- `PRAGMA journal_mode=WAL` — concurrent reads + writes from hooks and MCP server
- `PRAGMA busy_timeout=5000` — wait up to 5s on write contention instead of failing

### FTS5 External Content Mode

The `insights_fts` table doesn't store data — it indexes `insights.file_path` and `insights.content` via `content=insights, content_rowid=id`. All writes to `insights` must manually sync FTS:

```sql
-- After INSERT/UPDATE:
INSERT INTO insights_fts(rowid, file_path, content) VALUES (?, ?, ?);

-- Before DELETE:
INSERT INTO insights_fts(insights_fts, rowid, file_path, content) VALUES('delete', ?, ?, ?);
```

This is handled internally by `lib/context-lake.ts` — callers never need to manage FTS sync.

### Source Priority

When multiple sources write insights for the same file:

| Source | Priority | Can overwrite |
|--------|----------|---------------|
| `manual` | 3 (highest) | Everything |
| `handoff` | 2 | journal, unknown |
| `journal` | 1 | unknown only |

Higher-priority insights are never overwritten by lower-priority ones.

### Staleness

- Each insight records `git_hash` at write time
- `stale-checker` runs `git diff HEAD~10..HEAD` at session start
- Changed files → `stale = 1`
- Stale insights are still returned (with warning) — structure rarely changes on small edits
- After 30 days without updates AND 7 days without hits → cold eviction

## Session Lifecycle State Files

| File | Written by | Read by | Lifetime |
|------|-----------|---------|----------|
| `/tmp/claude-ctx-{session}.json` | statusline hook (external) | monitor, tracker | Session |
| `/tmp/claude-ctx-{session}-warned.json` | monitor | monitor | Session (debounce) |
| `/tmp/claude-cleanup-{session}.json` | tracker | enforcer | Session (5min stale) |
| `/tmp/claude-lake-touched-{session}.json` | read-tracker | session-handoff | Session |

## Threshold Design

| Component | Threshold | Purpose |
|-----------|-----------|---------|
| Monitor WARNING | ≤35% remaining | Agent wraps up current task |
| Monitor CRITICAL | ≤25% remaining | Agent stops new work, informs user |
| Tracker CRITICAL | ≤17% remaining | Triggers enforcement (journal required before stop) |
| Enforcer safety valve | 2 attempts | Prevents infinite enforcement loop |
| Cold eviction | >30 days + 7 days idle | Remove unused insights |

The gap between Monitor CRITICAL (25%) and Tracker CRITICAL (17%) gives the agent ~8% of context to perform handoff gracefully before enforcement kicks in.

## GSD Integration (Soft)

The plugin adapts behavior when GSD is detected (`.planning/STATE.md` exists):

- **Monitor**: CRITICAL message says "GSD state is already tracked in STATE.md" instead of generic advice
- **Monitor**: WARNING message mentions "defined plan steps"
- **Resume**: Checks for GSD checkpoints and routes to `/gsd:resume-work` if found
- **Handoff**: Recommends `/gsd:pause-work` for active GSD phases

None of these require GSD to be installed. All checks use `fs.existsSync` with graceful fallback.
