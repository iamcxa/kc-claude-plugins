# Linear Integration

Post a brief comment on linked Linear issue(s) after PR creation.

## When to Post

Skip if no Linear issue ID found in PR title scope.

Examples:
- `feat(SC-123):` → Post (issue scope `SC-123`)
- `feat(mcp):` → Skip (code scope, no issue ID)
- `fix(PROJ-456):` → Post (issue scope `PROJ-456`)

## Extract Issue ID

Parse the PR title scope to find the Linear issue identifier.

**Pattern**: `<type>(ISSUE-ID):` → extract `ISSUE-ID`

Examples:
- `feat(SC-123): add new feature` → `SC-123`
- `fix(PROJ-789): bug fix` → `PROJ-789`

## Comment Format

Use this template:

```
PR #{number} — {one-line summary of how it was handled}

{PR URL}
```

**Guidelines**:
- First line: `PR #{number}` + brief description of approach (not repeat PR title)
- Second line: blank
- Third line: full PR URL

**Example**:

```
PR #456 — 移除所有 Supabase security advisor 警告的 RLS policy，新增 8 個 migration files

https://github.com/duckbase-co/qnow/pull/456
```

## Posting Fallback (3-Tier)

If primary method fails, fall back to next tier:

### 1. Direct MCP

- Use `ToolSearch` to find Linear comment tool
- Call with issue ID + comment body

### 2. linear-manager Agent

- Dispatch `linear-manager` agent with message: `"Post comment on ISSUE-ID: {comment}"`
- Let agent handle Linear API interaction

### 3. Manual Fallback

- Print the comment text to user
- Ask user to paste into Linear web UI

## Rules

- Keep comment to **1–2 lines** (status update, not documentation)
- **Describe what was done** (the approach), not repeat PR title
- If PR covers **2+ issues**, comment on each with the same message
- **Do NOT block** PR creation on Linear comment failure — warn and continue
