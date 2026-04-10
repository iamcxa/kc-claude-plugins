# Journal Handoff Redesign — Unified User-Scope with Repo Isolation

**Date:** 2026-04-09
**Status:** Implemented 2026-04-10 — Tasks 1-7 landed across both repos; end-to-end handoff verification requires next session restart (stdio MCP is process-bound)
**Scope:** kc-hyperfocus (MCP server + skills), kc-hyperfocus-insights (JournalAdapter)

---

## Problem Statement

Session handoffs via `process_thoughts` have two failure modes:

1. **Silent field drop**: LLM occasionally emits malformed XML tool calls where `project_notes` parameter tag uses wrong namespace (`parameter` instead of `antml:parameter`). Claude Code's XML parser silently drops the field. The MCP server receives `project_notes: undefined`, skips project-scope write, returns `project_path: null`. No error raised — the skill outputs a success message with a handoff ID that points to an incomplete entry.

2. **Cross-repo contamination**: All handoffs land in flat `~/.private-journal/{date}/{time}.md` (user-installed mode) or `{cwd}/.private-journal/` (project-scoped). Resume skill's `list_recent_entries` returns entries from ALL repos. Direct lookup by handoff ID has no repo validation — loading a handoff from repo B while working in repo A silently succeeds.

Additionally, `resolveProjectJournalPath()` uses `process.cwd()` of the MCP server subprocess (fixed at Claude Code launch time), not the session's cwd. This makes "project scope" misleading for user-installed plugins.

**Prior art:** `journal-scope-design.md` (2026-04-08) and `xml-parameter-tag-silent-drop.md` (2026-04-07) in kc-claude-workspace project memory.

---

## Design

### Storage Layout

```
~/.private-journal/
├── _repos/                              # repo-scoped entries
│   ├── carlove/
│   │   ├── 2026-04-09/
│   │   │   ├── 07-17-36-594787.md      # handoff
│   │   │   └── 16-27-41-001357.md
│   │   └── 2026-04-10/
│   └── kc-plugin-forge/
│       └── 2026-04-08/
├── 2026-04-09/                          # personal entries (no repo context)
│   └── 12-34-56-abcdef.md
└── (legacy: ~/Project/*/.private-journal/ entries remain in place)
```

### Routing Rule

Single rule in `writeThoughts()`:

- `repo_slug` parameter provided → write all fields to `~/.private-journal/_repos/{slug}/{date}/{time}.md`
- `repo_slug` absent → write to `~/.private-journal/{date}/{time}.md` (unchanged behavior)

No dual-write. No `process.cwd()` dependency. No new tools.

### Frontmatter Schema (repo-scoped entries)

```yaml
---
title: "4:27:41 PM - April 9, 2026"
date: 2026-04-09T08:27:41.001Z
timestamp: 1775723261001
repo_slug: carlove
session_handoff: true
branch: gsd/v2.0-service-order-unification
description: "Phase 24-10 staging import unblocked"
---
```

Fields `repo_slug`, `session_handoff`, `branch`, `description` are new frontmatter. Only `repo_slug` affects storage path.

### Handoff ID

Format unchanged: `{date}/{time}` (e.g., `2026-04-09/16-27-41-001357`).

Resume reconstructs full path: `_repos/{slug}/{date}/{time}.md` where slug is derived from the session's cwd at resume time.

---

## Changes

### 1. kc-hyperfocus — lib/journal.ts

**Corruption detection** (new function):

```typescript
const XML_POLLUTION_PATTERNS = [
  /<\/parameter>/,
  /<parameter\s+name=/,
  /<\/feelings>/,
  /<\/project_notes>/,
  /<\/technical_insights>/,
  /<\/user_context>/,
  /<\/world_knowledge>/,
  /<invoke\s+name=/,
  /<function_calls>/,
];

function detectFieldCorruption(thoughts: ThoughtsInput): void {
  for (const [field, value] of Object.entries(thoughts)) {
    if (typeof value !== "string") continue;
    for (const pattern of XML_POLLUTION_PATTERNS) {
      if (pattern.test(value)) {
        throw new Error(
          `Field '${field}' contains tool-call XML marker (${pattern}). ` +
          `This indicates an LLM emit parse error. Retry the call.`
        );
      }
    }
  }
}
```

Runs on every `process_thoughts` call, before any write.

**Repo-scope routing** (new method):

```typescript
async writeToRepoScope(
  thoughts: ThoughtsInput & { repo_slug: string; session_handoff?: boolean; branch?: string; description?: string },
  timestamp: Date,
  dateStr: string,
  timeStr: string
): Promise<string> {
  const basePath = path.join(resolveUserJournalPath(), '_repos', thoughts.repo_slug);
  // Writes all fields (feelings + project_notes + technical_insights + ...) to one file
  // Adds repo_slug, session_handoff, branch, description to frontmatter
  return this.writeToLocation(thoughts, timestamp, basePath, dateStr, timeStr);
}
```

**writeThoughts routing change:**

```typescript
async writeThoughts(thoughts: ThoughtsInput & {
  repo_slug?: string;
  session_handoff?: boolean;
  branch?: string;
  description?: string;
}): Promise<{ path: string; entryId: string; repoSlug: string | null }> {
  detectFieldCorruption(thoughts);

  const dateStr = this.formatDate(timestamp);
  const timeStr = this.formatTimestamp(timestamp);

  if (thoughts.repo_slug) {
    const filePath = await this.writeToRepoScope(thoughts, timestamp, dateStr, timeStr);
    return { path: filePath, entryId: `${dateStr}/${timeStr}`, repoSlug: thoughts.repo_slug };
  }

  // Legacy: no repo_slug → flat user scope (unchanged behavior)
  const filePath = await this.writeToLocation(thoughts, timestamp, this.userPath, dateStr, timeStr);
  return { path: filePath, entryId: `${dateStr}/${timeStr}`, repoSlug: null };
}
```

**writeToLocation change:** When writing to repo scope, include new frontmatter fields (`repo_slug`, `session_handoff`, `branch`, `description`). All content sections (Feelings, Project Notes, Technical Insights, etc.) merge into one file.

### 2. kc-hyperfocus — server/context-lake-mcp.ts

**process_thoughts inputSchema** — add optional fields:

```typescript
repo_slug: { type: "string", description: "Repo identifier. When provided, writes to _repos/{slug}/." },
session_handoff: { type: "boolean", description: "Tag entry as session handoff in frontmatter." },
branch: { type: "string", description: "Git branch name for frontmatter metadata." },
description: { type: "string", description: "Short description for list display." },
```

**Handler response** — add `repo_slug` echo:

```typescript
return {
  status: "recorded",
  handoff_id: result.entryId,
  path: result.path,
  repo_slug: result.repoSlug,
  // Deprecated but kept for backward compat:
  project_path: null,
  user_path: result.path,
};
```

**list_recent_entries** — add optional filters:

```typescript
repo_slug: { type: "string", description: "Filter to entries with this repo_slug in frontmatter." },
session_handoff_only: { type: "boolean", description: "Only return entries with session_handoff: true." },
```

Scan logic:
- No `repo_slug` filter → scan flat `{date}/` dirs + all `_repos/*/` slug dirs
- With `repo_slug` filter → scan only `_repos/{slug}/{date}/` dirs (physical isolation)
- `session_handoff_only` → post-filter by frontmatter after reading

**search_journal** — same `_repos/*/` scan addition for embedding search.

### 3. kc-hyperfocus-insights — server/lib/journal-adapter.ts

**discoverJournalSources()** — add `_repos/` scanning:

```typescript
// After existing USER_JOURNAL source:
const reposDir = path.join(USER_JOURNAL, '_repos');
if (existsSync(reposDir)) {
  const slugDirs = await readdir(reposDir, { withFileTypes: true });
  for (const slug of slugDirs) {
    if (!slug.isDirectory()) continue;
    sources.push({
      dir: path.join(reposDir, slug.name),
      source: 'project-level',
      project: slug.name,
    });
  }
}
```

No changes needed to `readEntries()`, `dedup()`, `parseSections()`, or `segmentSessions()`. The `_repos/{slug}/{date}/*.md` structure matches the existing date-subdir pattern.

### 4. kc-session-handoff skill

**Step 1.5 (new):** Derive repo_slug from cwd:

```bash
# Handles linked worktrees correctly
slug=$(basename "$(git rev-parse --git-common-dir 2>/dev/null | sed 's|/\.git$||')" 2>/dev/null)
# Fallback: basename of cwd
slug=${slug:-$(basename "$(pwd)")}
```

**Step 2:** Call process_thoughts with:
- `repo_slug`: derived slug
- `session_handoff: true`
- `branch`: from git
- `description`: short summary
- `feelings` + `project_notes`: existing content

**Step 2.1 (new):** Verify response:
1. Check `path` contains `_repos/{slug}/`
2. Check `handoff_id` is present
3. If either fails → retry (max 3 attempts)
4. After 3 failures → report error, do NOT output success

### 5. kc-session-resume skill

**Direct lookup (Step 2A):**

```
1. Derive slug from cwd
2. Try: ~/.private-journal/_repos/{slug}/{handoff-id}.md
3. Fallback: ~/.private-journal/{handoff-id}.md (flat legacy)
4. Fallback: {git-toplevel}/.private-journal/{handoff-id}.md (project-dir legacy)
5. All miss → "Handoff not found in repo '{slug}'"
   → Offer: "Search other repos?"
```

**List mode (Step 2B):**

```
list_recent_entries(
  repo_slug: {derived slug},
  session_handoff_only: true,
  days: 7,
  limit: 5
)
```

Shows only current repo's handoffs. Physical isolation + filter double guard.

---

## Backward Compatibility

| Scenario | Behavior |
|----------|----------|
| Existing skill calls `process_thoughts` without `repo_slug` | Unchanged — flat write to `~/.private-journal/{date}/` |
| Old handoffs in `~/Project/*/.private-journal/` | Resume fallback path reads them |
| Old handoffs in flat `~/.private-journal/{date}/` | Resume fallback path reads them |
| `kc-hyperfocus-insights` reads old entries | Existing project-dir scan logic preserved |
| `list_recent_entries` called without new filters | Returns all entries (flat + `_repos/*`) |
| `kc-nightwatch` signal-harvester | `search_journal` scans `_repos/*/` too |

---

## Repo Slug Derivation

Done by the SKILL (LLM-side), not the MCP server.

```
Priority:
1. git rev-parse --git-common-dir → strip /.git → basename → lowercase
   (handles linked worktrees: all point to same common dir)
2. Fallback: basename(cwd) → lowercase
```

No config file, no git remote parsing. Simplest possible derivation. If collisions arise in the future, add explicit config then.

---

## Testing Strategy

### Unit Tests (kc-hyperfocus)

- `detectFieldCorruption`: known XML patterns throw, clean content passes
- `writeThoughts` with `repo_slug`: file lands in `_repos/{slug}/{date}/`
- `writeThoughts` without `repo_slug`: file lands in flat `{date}/` (regression)
- Frontmatter includes `repo_slug`, `session_handoff`, `branch`, `description` when provided
- `list_recent_entries` with `repo_slug` filter: only returns matching slug entries
- `list_recent_entries` with `session_handoff_only`: only returns tagged entries
- `list_recent_entries` without filters: returns both flat + `_repos/*` entries

### Unit Tests (kc-hyperfocus-insights)

- `discoverJournalSources`: includes `_repos/*/` dirs as project-level sources
- `readEntries` on `_repos/{slug}/{date}/`: parses correctly (existing date-subdir pattern)
- `dedup`: user-level flat entry + `_repos` entry with same timestamp merge correctly

### Integration / Manual

- Full handoff → resume cycle with `repo_slug`
- Resume from different repo → 404 on wrong slug, fallback offer
- Resume with legacy handoff ID → fallback paths work
- insights report includes entries from `_repos/`

---

## Out of Scope

- Migration script for old entries (natural decay + fallback reads)
- Separate `write_handoff` tool (not needed — `process_thoughts` enhanced)
- Separate `find_handoffs` tool (not needed — `list_recent_entries` filters)
- Git remote URL parsing for slug (YAGNI — basename is sufficient)
- Branch in storage path (stays in frontmatter only)

---

## Files to Modify

| File | Repo | Change |
|------|------|--------|
| `kc-hyperfocus/lib/journal.ts` | kc-claude-plugins | Corruption detection + repo-scope routing |
| `kc-hyperfocus/server/context-lake-mcp.ts` | kc-claude-plugins | Schema + handler + list filters + search scan |
| `kc-hyperfocus/skills/kc-session-handoff/SKILL.md` | kc-claude-plugins | Slug derivation + verify/retry loop |
| `kc-hyperfocus/skills/kc-session-resume/SKILL.md` | kc-claude-plugins | Fallback path chain + slug-scoped list |
| `kc-hyperfocus-insights/server/lib/journal-adapter.ts` | claude-plugins-principle | `_repos/*/` scan in discoverJournalSources |
