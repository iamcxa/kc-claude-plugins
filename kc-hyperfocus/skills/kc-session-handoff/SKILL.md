---
name: kc-session-handoff
description: Use when user says 'handoff', 'prepare handoff', '準備交接', or when context pressure is high and work state needs preservation before session ends.
argument-hint: "[focus note]"
allowed-tools:
  - mcp__plugin_kc-hyperfocus_context-lake__store_insight
  - mcp__plugin_kc-hyperfocus_context-lake__invalidate_stale
  - mcp__plugin_kc-hyperfocus_context-lake__get_metrics
  - mcp__plugin_kc-hyperfocus_context-lake__process_thoughts
---

# Session Handoff

Write a journal entry and produce a minimal resume prompt for the next session.

**Companion skill:** `kc-session-resume` handles context restoration on the other side.

## When NOT to Use

- Trivial sessions (pure Q&A, no code changes)
- Active GSD phase — use `/gsd:pause-work` instead

## Focus Note (optional argument)

If the user provided text after `/kc-session-handoff` (e.g., `/kc-session-handoff 重點記錄 auth middleware 決策`), treat it as a **focus note** — emphasize these topics in the journal's `## Completed` / `## Remaining` / `## Decisions` sections. This does NOT replace git/conversation state gathering — it supplements it with explicit user intent about what matters most for the next session.

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

### 1.5. Derive Repo Slug

Derive the repo slug for `_repos/` routing:

```bash
# git-common-dir handles linked worktrees (all point to same .git)
REPO_SLUG=$(basename "$(git rev-parse --git-common-dir 2>/dev/null | sed 's|/\.git$||')" 2>/dev/null | tr '[:upper:]' '[:lower:]')
# Fallback: basename of cwd
REPO_SLUG=${REPO_SLUG:-$(basename "$(pwd)" | tr '[:upper:]' '[:lower:]')}
```

Use this slug in Step 2 as `repo_slug` parameter.

### 2. Write Journal & Capture Handoff ID

Load the journal tool:

```
ToolSearch → "select:mcp__plugin_kc-hyperfocus_context-lake__process_thoughts"
```

Call `process_thoughts` with these fields:

| Field | Content |
|-------|---------|
| `repo_slug` | Derived slug from Step 1.5 (mandatory for handoffs) |
| `session_handoff` | `true` |
| `branch` | Git branch from Step 1 |
| `description` | One-line summary of session work |
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

**Capture the handoff ID directly from the response.** `process_thoughts` returns a JSON payload like:

```json
{"status":"recorded","handoff_id":"2026-03-06/02-35-35-040018","project_path":"/.../...md","user_path":"/.../...md"}
```

The `handoff_id` field is the resume identifier — use it verbatim in step 3. No follow-up `list_recent_entries` call needed. If the response is missing `handoff_id` (older MCP server build), report the failure to the user — do NOT fabricate an ID or skip the resume prompt.

### 2.1. Verify Write Success

Parse the `process_thoughts` response JSON. Check:

1. `path` field contains `_repos/{slug}/` (confirms repo-scoped write)
2. `handoff_id` field is present and non-empty
3. `repo_slug` field echoes back the slug you sent

If ANY check fails:
- Retry the `process_thoughts` call (max 3 attempts)
- Log: "Handoff write verification failed (attempt N/3): {what failed}"
- After 3 failures → report error to user: "Handoff 寫入失敗，process_thoughts 回傳不符預期。請手動檢查 ~/.private-journal/_repos/{slug}/ 目錄。"
- Do NOT output a success confirmation or resume prompt

**Only proceed to Step 2.5 after verification passes.**

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
| `handoff_id` parsed from `process_thoughts` JSON response | ✅ |
| Resume prompt with handoff ID output to user | ✅ |
| Confirmation block output | ✅ |
| `get_metrics(event: "handoff")` called | ✅ |
| `path` contains `_repos/{slug}/` | ✅ |

**Any missing row = incomplete handoff.** The user cannot resume without the handoff ID. Writing journal alone is NOT a handoff — it's just a journal entry.

## Red Flags — You Are Bypassing This Skill

- Writing `process_thoughts` directly without invoking this skill
- Outputting "I saved state to journal" without a resume ID
- Saying "use `/kc-session-resume` to find it" instead of providing the ID
- Following CLAUDE.md Context Cleanup instructions instead of this skill
- Constructing a handoff ID from timestamp or guess instead of reading the `handoff_id` field from the `process_thoughts` JSON response
- Writing a journal entry with `Session Handoff:` header but empty Completed/Remaining sections
- Calling `list_recent_entries` after `process_thoughts` (the ID is already in the response — extra call wastes ~200 tokens under context pressure)

**All of these produce a handoff without resume ID → the user must manually search before resuming.**
