---
name: kc-session-handoff
description: Use when user says 'handoff', 'prepare handoff', '準備交接', or when context pressure is high and work state needs preservation before session ends.
allowed-tools:
  - mcp__plugin_kc-hyperfocus_context-lake__store_insight
  - mcp__plugin_kc-hyperfocus_context-lake__invalidate_stale
  - mcp__plugin_kc-hyperfocus_context-lake__get_metrics
  - mcp__plugin_kc-hyperfocus_context-lake__process_thoughts
  - mcp__plugin_kc-hyperfocus_context-lake__list_recent_entries
---

# Session Handoff

Write a journal entry and produce a minimal resume prompt for the next session.

**Companion skill:** `kc-session-resume` handles context restoration on the other side.

## When NOT to Use

- Trivial sessions (pure Q&A, no code changes)
- Active GSD phase — use `/gsd:pause-work` instead

## Primary Trigger

Context pressure (WARNING/CRITICAL) is the most common trigger. The skill is designed to work under tight context budgets. Steps 2.5 and 2.7 are conditional — skip them freely. Steps 1–3 and the confirmation block are **never optional**, regardless of remaining context.

## Process

### 1. Gather State

```bash
pwd                          # current working directory
git branch --show-current 2>/dev/null || echo "(no git branch)"
git status --short 2>/dev/null || echo "(no git repo)"
git log --oneline -5 2>/dev/null
git rev-parse --show-toplevel 2>/dev/null
```

**Non-git fallback**: If git commands fail (workspace root, temp dir, non-repo), proceed with `branch = "(no branch)"`. The journal and resume prompt still work — use the working directory and description as the primary identifiers instead.

**Working directory**: Record `pwd` output. This is critical for multi-directory workspaces where GSD, `bun test`, or other tools must run from a specific subdirectory (not the git root or workspace root). The resume skill restores this context so the next session starts in the right place.

**Worktree detection** — compare `--show-toplevel` against main worktree:

```bash
git worktree list
```

If `--show-toplevel` differs from the first line of `worktree list` → you are in a **linked worktree**. Record the path. If they match → main worktree, omit worktree field. If `git worktree list` fails → omit worktree field (assume main).

From conversation: completed work, decisions, remaining work, blockers, Linear issue (if any).

### 2. Write Journal & Capture Handoff ID

Load journal tools:

```
ToolSearch → "select:mcp__plugin_kc-hyperfocus_context-lake__process_thoughts,mcp__plugin_kc-hyperfocus_context-lake__list_recent_entries"
```

Call `process_thoughts` with these fields:

| Field | Content |
|-------|---------|
| `feelings` | 1-2 honest sentences about your current state (mandatory) |
| `project_notes` | Structured handoff using template below |

**project_notes template** — the `Session Handoff:` header is critical for searchability:

```
Session Handoff: {branch} — {short description}
Issue: {SC-xxx} (if any)
Working dir: {pwd output} (always include — critical for multi-dir workspaces)
Worktree: {path} (only if linked worktree, omit for main)

## Completed
- ...

## Remaining
- ...

## Decisions
- ...

## Key Files
- ...
```

Optionally add `technical_insights` if you discovered reusable patterns worth preserving.

**project_notes minimum content** — the entry MUST contain at least:
- The `Session Handoff:` header line
- `Working dir:` line
- At least ONE item under `## Completed` or `## Remaining`

A journal entry with only the header and empty sections is vacuous — it tells the next session nothing. If you genuinely have nothing to report under Completed or Remaining, you are in a trivial session and should not be running this skill.

**Immediately after writing**, call `list_recent_entries(limit: 1, type: "project")` to capture the entry path. The tool returns entries with a `Path:` field like:

```
Path: /path/to/project/.private-journal/2026-03-06/02-35-35-040018.md
```

Extract the **handoff ID** — strip everything before `.private-journal/` and the trailing `.md` to get `2026-03-06/02-35-35-040018`. This ID is used in step 3.

**If `list_recent_entries` returns no results** (MCP failure, timing issue): retry once. If still empty, report the failure to the user — do NOT fabricate an ID or skip the resume prompt. The user needs to know the handoff is incomplete.

### 2.5. Knowledge Capture Check

If the journal entry you just wrote includes `technical_insights`:

1. Read the project's MEMORY.md:
   ```
   Read → ~/.claude/projects/{project}/memory/MEMORY.md
   ```
2. For each insight, evaluate:
   - Is it a **reusable pattern** (not a one-off fix)?
   - Is it **already in MEMORY.md** (search by keyword)?
3. If new + reusable → append a one-liner entry to MEMORY.md:
   ```markdown
   ## Topic Name (YYYY-MM-DD)

   One-sentence summary of the reusable pattern.
   ```
4. If nothing to capture → skip silently (no output).

**Rules:**
- No user confirmation (minimize friction under context pressure)
- One-liner entries only (deep write-ups are for 1-on-1 harvest)
- Skip: syntax fixes, one-off debug, project-specific gotchas (those go to CLAUDE.md via 1-on-1 harvest)

### 2.7. Context Lake Capture (optional)

If the context lake MCP server is available (check by attempting to call `store_insight`):

1. Read `/tmp/claude-lake-touched-{session_id}.json` — list of files Read during this session
2. Read `/tmp/claude-lake-explores-{session_id}.json` — list of completed Explore dispatches
3. Combine both sources. Deduplicate the file list.
4. **Safety net check**: For each completed Explore, check if the key files from that exploration already have `store_insight` calls in this session (the post-explore-nudge hook prompted you to cache during the session). If insights were already stored → skip those files.
5. For remaining files you explored deeply enough to summarize (analyzed, explained, modified, or debugged — not merely glanced at):
   - Produce a 3-5 sentence insight **in English** answering: What does this file do? Key functions/classes? Dependencies and gotchas?
   - Call `store_insight` for each with `source: "handoff"`
6. Report: "Cached N insights to context lake (M already cached during session, K skipped — no deep analysis)"
7. Delete both temp files (`/tmp/claude-lake-touched-{session_id}.json`, `/tmp/claude-lake-explores-{session_id}.json`)

**Skip conditions**: Neither temp file exists, no files with meaningful analysis in this session, or MCP server not available.

### 3. Resume Prompt

Output a one-line prompt the user copies into the next session. Include the **handoff ID** from step 2 so the resume skill can do a direct O(1) lookup instead of searching:

```
resume {handoff-id} 繼續 {branch} 的 {description}
```

If in a linked worktree, append the worktree path:

```
resume {handoff-id} 繼續 {branch} 的 {description} (worktree: {path})
```

Example: `resume 2026-03-06/02-35-35-040018 繼續 feature/sc-571 的租戶切換問題`
Example (worktree): `resume 2026-03-06/02-35-35-040018 繼續 feature/sc-571 的租戶切換問題 (worktree: /path/to/project-wt-sc-571)`

### 4. Confirm

```
Handoff complete:
- Handoff ID: {handoff-id}
- Journal: project_notes with "Session Handoff: {branch}"
- MEMORY.md: {+N insights captured / no new insights}
- Branch: {branch}
- Working dir: {pwd}
- Worktree: {path} (or "main" if not in a linked worktree)

Resume prompt:
───────────────────
resume {handoff-id} 繼續 {branch} 的 {description}
───────────────────
```

### 5. Record Handoff Metric

Estimate the journal entry size: count the characters in `project_notes` you wrote in step 2, divide by 4 to get approximate tokens.

Call `get_metrics` with:
- `event: "handoff"`
- `event_details: { entryTokens: <estimated_tokens> }`

Silent — no output needed.

## NOT DONE UNTIL

| Evidence | Required |
|----------|:--------:|
| Journal written with `Session Handoff:` header | ✅ |
| `list_recent_entries` called, handoff ID extracted | ✅ |
| Resume prompt with handoff ID output to user | ✅ |
| Confirmation block output | ✅ |
| `get_metrics(event: "handoff")` called | ✅ |

**Any missing row = incomplete handoff.** The user cannot resume without the handoff ID. Writing journal alone is NOT a handoff — it's just a journal entry.

## Red Flags — You Are Bypassing This Skill

- Writing `process_thoughts` directly without invoking this skill
- Outputting "I saved state to journal" without a resume ID
- Skipping `list_recent_entries` because "context is low"
- Saying "use `/kc-session-resume` to find it" instead of providing the ID
- Following CLAUDE.md Context Cleanup instructions instead of this skill
- Constructing a handoff ID from timestamp or guess instead of reading it from `list_recent_entries` — the ID MUST come from the journal tool's returned `Path:` field
- Writing a journal entry with `Session Handoff:` header but empty Completed/Remaining sections

**All of these produce a handoff without resume ID → the user must manually search before resuming.**
