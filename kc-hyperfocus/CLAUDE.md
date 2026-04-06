# kc-hyperfocus

Session lifecycle & context efficiency plugin: context pressure detection → cleanup enforcement → cross-session handoff/resume → MCP context firewall → context lake cache → statusline with usage quota.

## Architecture

```
[statusline hook]  →  /tmp/claude-ctx-{session}.json  (bridge file)
        │
        ├── context-pressure-monitor.js  (PostToolUse)
        │   reads bridge → injects WARNING/CRITICAL into agent context
        │
        ├── session-cleanup-tracker.js   (PostToolUse)
        │   reads bridge → detects CRITICAL → tracks journal/GSD calls
        │   writes /tmp/claude-cleanup-{session}.json
        │
        └── session-cleanup-enforcer.js  (Stop)
            reads cleanup state → blocks stop if journal incomplete
            max 2 attempts (safety valve)

Skills:
  /kc-session-handoff    →  gather state → write journal → capture ID → output resume prompt
  /kc-session-resume     →  direct lookup (O(1) with ID) or list search → present context → wait for direction
  /kc-cache-insight      →  manual cache + status + metrics view
  /kc-statusline-setup   →  detect existing statusline → install hyperfocus-statusline.js if needed

Context Lake:
  context-lake.ts      →  shared SQLite module (schema, CRUD, FTS5, metrics)
  context-lake-mcp.ts  →  MCP server: 5 tools (insight store/search/metrics)

  [Read/Explore] → explore-interceptor.js (PreToolUse)
                    inject cached insights on Read; suggest cached insights before Explore (never deny)
  [Read]         → read-tracker.js (PostToolUse)
                    record touched files + track uncached reads → nudge at threshold
  [SessionStart] → stale-checker.js
                    invalidate stale insights, cold eviction, journal sync
```

## Components

| Type | Name | Event | Purpose |
|------|------|-------|---------|
| Skill | kc-session-handoff | — | Write journal + produce resume prompt with handoff ID |
| Skill | kc-session-resume | — | Restore context from journal handoff entry |
| Hook | context-pressure-monitor.js | PostToolUse | Inject WARNING/CRITICAL when context ≤35%/≤25% |
| Hook | session-cleanup-tracker.js | PostToolUse | Track journal/GSD calls during CRITICAL sessions |
| Hook | session-cleanup-enforcer.js | Stop | Block exit if CRITICAL triggered but journal incomplete |
| Agent | mcp-summarizer | — | Context firewall: summarize MCP/file data to prevent context bloat |
| Lib | context-lake.ts | — | Shared SQLite module: DB schema, CRUD, FTS5, metrics |
| MCP | context-lake-mcp.ts | — | MCP server: 5 tools for insight store/search/metrics |
| Hook | explore-interceptor.js | PreToolUse | Inject cached insights on Read; suggest (never deny) cached insights before Explore |
| Hook | read-tracker.js | PostToolUse | Record touched files + track uncached reads → nudge Claude to cache insights |
| Hook | post-explore-nudge.js | PostToolUse | Nudge Claude to cache insights after Explore completes |
| Hook | stale-checker.js | SessionStart | Invalidate stale insights, cold eviction, journal sync |
| Skill | kc-cache-insight | — | Manual cache + status + metrics view |
| Skill | kc-statusline-setup | — | Install statusline with model, branch, context bar, Anthropic 5h/7d usage quota |
| Script | hyperfocus-statusline.js | statusLine | Standalone statusline: model │ dir branch ██░░ used% │ 5h:N% 7d:N%. Writes context bridge file. |

## External Dependencies

- **Statusline bridge file** (`/tmp/claude-ctx-{session_id}.json`): Written by `hyperfocus-statusline.js` or a compatible statusline (e.g., GSD statusline). If absent, hooks degrade gracefully (no warnings, no enforcement).
- **Journal**: Built-in (v1.4.0+). Journal tools (`process_thoughts`, `list_recent_entries`, `read_journal_entry`, `search_journal`) are integrated into the context-lake MCP server. Data stored in `.private-journal/` directories (project-level + user-level).
- **GSD** (soft): Context monitor customizes messages when `.planning/STATE.md` exists. Resume skill checks for GSD checkpoints. Neither is required — the plugin works without GSD.

## Migration Guide

This plugin replaces user-level skills and hooks. Migration steps:

### Phase 1: Test (parallel operation)

1. Plugin is created but NOT in `enabledPlugins`
2. Test skills: `cd kc-hyperfocus && ccp` then try `/kc-session-handoff`
3. User-level skills (`~/.claude/skills/kc-session-handoff/`, `~/.claude/skills/kc-session-resume/`) continue to work

### Phase 2: Switch

1. Register in local marketplace:
   ```json
   // ~/.claude/plugins/local/.claude-plugin/marketplace.json
   { "plugins": [..., "kc-hyperfocus"] }
   ```
   And symlink:
   ```bash
   ln -s ~/Project/kc-claude-workspace/kc-claude-plugins/kc-hyperfocus ~/.claude/plugins/local/kc-hyperfocus
   ```

2. Enable in settings:
   ```json
   // ~/.claude/settings.json → enabledPlugins
   "kc-hyperfocus@local": true
   ```

3. Remove user-level hooks from `~/.claude/settings.json`:
   - PostToolUse: `gsd-context-monitor.js` entry
   - PostToolUse: `session-cleanup-tracker.js` entry
   - Stop: `session-cleanup-enforcer.js` entry

4. Remove (or rename) user-level skills:
   ```bash
   mv ~/.claude/skills/kc-session-handoff ~/.claude/skills-backup/kc-session-handoff
   mv ~/.claude/skills/kc-session-resume ~/.claude/skills-backup/kc-session-resume
   ```

5. Remove (or rename) user-level hook files:
   ```bash
   mv ~/.claude/hooks/gsd-context-monitor.js ~/.claude/hooks/gsd-context-monitor.js.bak
   mv ~/.claude/hooks/session-cleanup-tracker.js ~/.claude/hooks/session-cleanup-tracker.js.bak
   mv ~/.claude/hooks/session-cleanup-enforcer.js ~/.claude/hooks/session-cleanup-enforcer.js.bak
   ```

6. Restart Claude Code session

### Rollback

Reverse steps: remove from enabledPlugins, restore user-level hooks in settings.json, rename `.bak` files back.

## Key Gotchas

- **Hooks fire in subagent context**: These hooks trigger for both main context and subagent tool calls. The context-pressure-monitor checks for subagent (no metrics file → exit silently). Design is already subagent-safe.
- **Duplicate hook execution**: During parallel period, do NOT enable plugin while user-level hooks are active — both will fire, doubling warnings and tracker writes.
- **Bridge file providers**: `hyperfocus-statusline.js` (this plugin) or GSD statusline both write `/tmp/claude-ctx-{session_id}.json`. Run `/kc-statusline-setup` to install if no statusline is configured.
- **CRITICAL threshold divergence**: Monitor uses 25%, tracker uses 17%. Monitor warns the agent early; tracker's stricter threshold triggers enforcement only when context is truly exhausted.

## Editing Rules

- Hook JS files are in `hooks/scripts/` — hooks.json references them via `${CLAUDE_PLUGIN_ROOT}`
- Skills follow standard `skills/<name>/SKILL.md` structure
- After modifying hooks, test with `ccp` before syncing to cache
