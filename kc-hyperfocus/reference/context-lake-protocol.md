# Context Lake Protocol

> How to effectively use the context lake for cross-session knowledge transfer.
> Derived from spacedock build pipeline (41%+ hit rate, 138k+ tokens saved).

## Why This Matters

The context lake caches file-level insights (purpose, patterns, gotchas) in a per-repo SQLite DB. Insights are consulted on demand via the `/kc-cache-insight` skill and the context-lake MCP tools (`search_insights`, `store_insight`, …).

> **v1.6.4 change** — the PreToolUse Read/Explore injector and the PostToolUse
> Explore nudge have been removed to stop unsolicited interference with agent
> context. The cache no longer auto-injects on Read or pre-Explore. Treat the
> protocol below as a workflow you opt into when you genuinely need cached
> understanding, not as a hook-driven prompt.

**Without protocol**: cache never gets consulted → re-analyze the same files every session.
**With protocol**: search before deep analysis, store after deep understanding → cache grows → hits compound over sessions.

## Core Principles

| # | Principle | Why |
|---|-----------|-----|
| 1 | **Search before work** | Check if prior insight exists before reading a file deeply. Saves re-analysis. |
| 2 | **Store after learning** | Cache insights for files you deeply understood. Future sessions benefit. |
| 3 | **Exact path, not keywords** | `file_path` exact lookup has near-100% precision. FTS keyword search is for discovery only. |
| 4 | **English only** | All insights in English for FTS5 consistency, regardless of conversation language. |

## When to Search

Before deeply analyzing a file, check for existing insight:

```
search_insights(file_path: "src/domain/order.saga.ts", freshness_days: 30)
```

- **Fresh hit**: Read the insight. Skip deep analysis unless new questions arise.
- **Stale hit**: Re-read the file. Update the insight after.
- **Miss**: Read the file. Store insight after understanding it.

## When to Store

Store after you've built deep understanding of a file — not after a glance.

**Good candidates for storing:**
- Files you analyzed, explained, modified, or debugged
- Files with non-obvious patterns or gotchas
- Files that are frequently read across sessions (high miss count)

**Not worth storing:**
- Files you only glanced at (< 30 seconds of analysis)
- Config files, lock files, generated code
- Files that change too frequently (will go stale immediately)

## Content Format

3-8 sentences in English. Use tags for scanability:

```
[purpose] Work-order saga — pure function mapping WorkOrderEvents to cross-domain commands.
[pattern] ReceptionCompleted dispatches CreateWorkOrderTask per pipeline workspace entry.
[gotcha] Template IDs from pipeline_snapshot are frozen at WO creation. Empty IDs trigger fallback returning ALL templates.
```

### Tag Vocabulary

| Tag | Meaning | When to use |
|-----|---------|-------------|
| `[purpose]` | What this file does (one sentence) | Always |
| `[pattern]` | Key patterns and abstractions | When non-obvious architecture |
| `[gotcha]` | Non-obvious traps, silent failures | When you discovered something surprising |
| `[correction]` | Corrected assumption: thought A, actually B | After debugging or research |
| `[decision]` | Implementation choice and rationale | After making a design decision |

Tags are optional — plain prose works fine. Tags help with FTS discovery (`search_insights(query: "gotcha")`).

## Source Types

| Context | Source | Priority | Behavior |
|---------|--------|----------|----------|
| Manual cache (`/kc-cache-insight`) | `manual` | 3 (highest) | Overwrites everything |
| Session handoff | `handoff` | 2 | Overwrites journal only |
| Journal sync (SessionStart) | `journal` | 1 | Never overwrites higher sources |
| Automated read (pipeline) | `read` | 0 (lowest) | Initial scan, overwritten by any later stage |

## Integration Patterns

### For workflow/pipeline plugins (like spacedock)

Add to each stage's checklist:

```markdown
## Explore Stage Checklist
- [ ] Search context lake for each discovered file (freshness_days: 30)
- [ ] Store insight for each key file with [purpose] + [pattern] + [gotcha]
```

This makes store_insight a **mandatory step**, not a suggestion.

### For general sessions (carlove, recce, etc.)

No hook will prompt you to cache. Build the habit yourself:

1. **Search before deep analysis** — `search_insights(file_path: "...")` for files you're about to study in depth.
2. **Store after deep understanding** — `store_insight(...)` for files you analyzed, modified, or debugged. Skip glances.
3. **Use `/kc-cache-insight` for batch caching** — at natural pauses, cache the 3-5 files you understood best this session.

If you never store, the same files keep missing — costing comprehension overhead every session. The discipline lives in the workflow, not in a hook.

### For CLAUDE.md integration

Add to project CLAUDE.md for stronger enforcement:

```markdown
## Context Lake

After reading 15+ code files in a session, cache insights for the most-read files.
Call `store_insight` (context-lake MCP) with source "manual" for files you understand well.
This is not optional — uncached files cost comprehension overhead every session.
```

## Invalidation

| Trigger | Action |
|---------|--------|
| File modified (git diff) | `stale-checker.js` marks insight as stale at session start |
| 30 days without update + 7 days without hits | Cold eviction (automatic) |
| Manual | `invalidate_stale(changed_files: [...])` |

Stale insights are still served (with warning) — file structure rarely changes on small edits.

## Metrics

Check lake health via `/kc-cache-insight --dashboard` or `--metrics`:

| Metric | Healthy | Concern |
|--------|---------|---------|
| Hit rate | >20% | <5% = cache too small or wrong paths |
| Nudge→Store conversion | >30% | 0% = nudge being ignored |
| Insights per repo | 20+ for active repos | <5 = not storing enough |
| Saved tokens | Growing over time | Flat = no new hits with fileLines |

## Quick Reference

```
# Search before reading deeply
search_insights(file_path: "src/foo.ts", freshness_days: 30)

# Store after understanding
store_insight(
  file_path: "src/foo.ts",
  content: "[purpose] ... [pattern] ... [gotcha] ...",
  source: "manual",
  git_hash: "abc123"
)

# Check health
/kc-cache-insight --dashboard
/kc-cache-insight --metrics
```
