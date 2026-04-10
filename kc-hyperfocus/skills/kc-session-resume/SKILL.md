---
name: kc-session-resume
description: Use when user says 'resume', 'continue', '繼續', 'pick up where I left off', or mentions a branch name to resume previous work. Triggers on session handoff resume prompts.
argument-hint: "[handoff-id] [description]"
allowed-tools:
  - mcp__plugin_kc-hyperfocus_context-lake__get_metrics
  - mcp__plugin_kc-hyperfocus_context-lake__read_journal_entry
  - mcp__plugin_kc-hyperfocus_context-lake__list_recent_entries
  - mcp__plugin_kc-hyperfocus_context-lake__search_journal
---

# Session Resume

Restore context from a previous session's journal handoff entry.

**Companion skill:** `kc-session-handoff` creates the entries this skill reads.

## Routing

**Priority order** — explicit handoff ID always wins:

1. **User gave handoff ID** (`YYYY-MM-DD/HH-MM-SS-nnnnnnn` pattern) → Go directly to step 2A. **Do NOT check GSD checkpoints, do NOT read .continue-here.md, do NOT read STATE.md.** The handoff ID is the sole intent signal — GSD state is irrelevant when the user points to a specific journal entry.
2. **No handoff ID** → Check GSD structure:
   ```bash
   ls .planning/phases/*/.continue-here.md 2>/dev/null
   ls .planning/STATE.md 2>/dev/null
   ```
   - **GSD checkpoint found** → Check for recent journal handoffs too (step 2B preview: `list_recent_entries(days: 3, limit: 3, type: "project")`). If BOTH GSD checkpoint AND journal handoffs exist → **you MUST present numbered options and wait for user choice**:
     ```
     找到兩種可恢復的上下文：
     1. GSD Phase {N}: {description} (checkpoint)
     2. Journal handoff: {branch} — {description} ({date})

     要恢復哪一個？
     ```
     User picks GSD → invoke `/gsd:resume-work`. User picks journal → continue to step 2B.
     **Do NOT merge both sources on your own judgment.** Do NOT auto-select "the most recent one." Even if they point to the same branch, they represent different resume mechanisms — the user decides which context to restore.
   - **GSD checkpoint only** (no recent journal handoffs) → Inform user, invoke `/gsd:resume-work`.
   - **No GSD** → Continue to step 1.

## Process

### 1. Extract Clues (no handoff ID path only)

Extract branch name / topic keywords from prompt. Fallback: `git branch --show-current`.

Also check current state:

```bash
git branch --show-current
git status --short
git log --oneline -3
git rev-parse --show-toplevel
```

Derive repo slug (same logic as kc-session-handoff Step 1.5):

```bash
REPO_SLUG=$(basename "$(git rev-parse --git-common-dir 2>/dev/null | sed 's|/\.git$||')" 2>/dev/null | tr '[:upper:]' '[:lower:]')
REPO_SLUG=${REPO_SLUG:-$(basename "$(pwd)" | tr '[:upper:]' '[:lower:]')}
```

Go to step 2B (list mode).

### 2A. Direct Lookup (with Handoff ID)

Load the journal read tool:

```
ToolSearch → "select:mcp__plugin_kc-hyperfocus_context-lake__read_journal_entry"
```

Try paths in order (stop at first success):

1. **Repo-scoped (new):** `~/.private-journal/_repos/{REPO_SLUG}/{handoff-id}.md`
2. **Flat legacy:** `~/.private-journal/{handoff-id}.md`
3. **Project-dir legacy:** `{git-toplevel}/.private-journal/{handoff-id}.md`

If all three return "Entry not found":
- Report: "Handoff `{handoff-id}` not found in repo '{REPO_SLUG}'."
- Offer: "要搜尋其他 repo 的 handoff 嗎？"
- If user says yes → list all entries in `~/.private-journal/_repos/` subdirs matching the handoff-id date prefix

Skip to step 3.

### 2B. List Mode (no Handoff ID)

Load journal list tool:

```
ToolSearch → "select:mcp__plugin_kc-hyperfocus_context-lake__list_recent_entries"
```

Fetch recent handoffs scoped to current repo:

```
list_recent_entries:
  days: 7
  limit: 5
  type: "both"
  repo_slug: {REPO_SLUG}
  session_handoff_only: true
```

If zero results → widen: drop `session_handoff_only`, keep `repo_slug`. Still zero → drop `repo_slug` too (show all repos with warning).

Filter results for entries containing "Session Handoff:" in the excerpt. Present up to 3 matches as a numbered list:

```
找到 N 筆交接紀錄：

1. [{handoff-id}] {branch} — {description}
2. [{handoff-id}] {branch} — {description}

選哪一筆？(1/2)
```

Extract the handoff ID from the selected entry's path, then `read_journal_entry` to load full content.

### 3. Check MEMORY.md (MANDATORY — never skip)

Quick scan for relevant context:

```
Read → ~/.claude/projects/{project}/memory/MEMORY.md
```

Look for entries related to the current branch or topic — stable patterns, architectural decisions, or debugging notes that provide additional context.

**This step is mandatory regardless of time pressure.** "User said hurry" or "user said start immediately" does NOT skip MEMORY.md — stale context causes worse delays than a 10-second scan.

### 3.5. CLAUDE.md Migration Check

While MEMORY.md is loaded, scan for entries that may have matured into stable project conventions worth promoting to CLAUDE.md:

**Candidates for migration** (judge from MEMORY.md content + already-loaded CLAUDE.md — do NOT load journal tools or other external data):
- Entries with strong language ("always", "never", "MUST") suggesting established conventions
- Architectural constraints that affect all future work in this project
- Debugging lessons with evidence of recurrence (e.g., "caused 3 bugs", "hit this again")
- Rules that overlap with existing CLAUDE.md entries (consolidate to avoid drift)

**NOT candidates:**
- Personal preferences (stay in MEMORY.md as `user` type)
- Project-specific temporary state (stays in MEMORY.md as `project` type)
- One-off fixes or narrow gotchas

**If candidates found:**

1. List them briefly for the user:
   ```
   MEMORY.md → CLAUDE.md 候選：
   - "{entry name}" — {reason it's mature enough}
   ```
2. If user confirms → directly Edit the project's CLAUDE.md to add the entry in the appropriate section (do NOT invoke `revise-claude-md` — it's a full audit, too heavy for resume flow)
3. After migration, remove or simplify the corresponding MEMORY.md entry to avoid duplication

**If no candidates** → skip silently (no output).

**Rules:**
- Always confirm with user (CLAUDE.md is git-tracked)
- Do this check quickly — don't let it delay the resume flow
- Maximum 3 candidates per session (avoid overwhelming at session start)

### 4. Present and Confirm

**Worktree check** — if the handoff entry contains a `Worktree:` field:

1. Compare recorded worktree path with current `git rev-parse --show-toplevel`
2. If they differ → show a warning before the summary:

```
⚠️  Worktree mismatch:
  Handoff recorded: {recorded-worktree-path}
  Current location: {current-toplevel}

請先切換到正確的 worktree 再繼續，或確認要在目前位置工作。
```

3. If they match or no `Worktree:` field in entry → proceed normally.

**Working directory check** — if the entry contains a `Working dir:` field:

1. Compare recorded working dir with current `pwd`
2. If they differ → show a warning:

```
⚠️  Working directory mismatch:
  Handoff recorded: {recorded-working-dir}
  Current location: {current-pwd}

GSD/test commands may need to run from the recorded directory.
cd {recorded-working-dir}
```

3. If they match or no `Working dir:` field → proceed normally.

Summarize the handoff entry:

```
Found handoff [{handoff-id}] from {date}:

Branch: {branch}
Issue: {issue}
Working dir: {dir} (if recorded)
Worktree: {path} (if recorded)

Completed:
- ...

Remaining:
- ...

Decisions:
- ...

Where should we pick up?
```

**STOP HERE. Wait for user direction before starting any work.**

"Let's go", "resume and keep working", "直接開始" do NOT count as direction — they confirm the resume, not which task to start. You must receive a specific answer (e.g., "start with JWT middleware", "continue from item 2", or "從第一個開始") before writing any code or executing any task.

### 4.5. Record Resume Metric

After successfully loading and presenting a handoff entry, call `get_metrics` with `event: "resume"` to record this resume for dashboard tracking. Silent — no output needed. Skip this step if no handoff was found (step 5 path).

### 5. If No Handoff Found

When no journal entry matches (list mode returned zero "Session Handoff:" entries):

```
No previous handoff found.

Current state:
- Branch: {branch}
- Status: {clean/dirty}
- Recent commits: {last 3}

What would you like to work on?
```

## Red Flags — STOP If You're About To

- Read `.continue-here.md` or `STATE.md` when user provided a handoff ID
- Skip MEMORY.md because "user is in a hurry"
- Auto-select between GSD checkpoint and journal handoff without presenting options
- Start coding or executing tasks before receiving a specific task direction from user
- Treat "let's go" / "continue" / "直接開始" as task-specific direction
