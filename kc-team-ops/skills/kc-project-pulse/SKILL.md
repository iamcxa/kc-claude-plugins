---
name: kc-project-pulse
description: This skill should be used when the user asks to "update project status", "write pulse update", "draft weekly update", "post project pulse", "project 更新", "寫 pulse", "weekly update", or wants to draft and post Linear project status updates. Covers data collection, health assessment, drafting, and posting.
---

# Project Pulse Update

Draft and post Linear project status updates (pulse updates) by collecting live data, assessing health, and presenting drafts for user approval before posting.

**REQUIRED:** Use `linear-expert` skill for Linear operations (loaded by `linear-manager` agent).

## Process Flow

```
Collect Data (parallel) → Assess Health → Draft Updates → GATE → Post to Linear
```

## MCP Availability

**If Linear MCP is unavailable** (tools fail or server not connected): Inform the user that this skill requires Linear API access for live data. Offer: (1) retry after connecting Linear MCP, (2) draft from git log + user-provided context only (health = user's judgment, not computed), (3) abort. Do not fabricate issue data from memory.

## Steps

### 1. Collect Data (parallel)

Fetch all data sources in parallel for efficiency:

| Source | Tool / Method | What to collect |
|--------|--------------|-----------------|
| **Projects** | `list_projects` | Active projects where user is lead or member |
| **Previous updates** | `get_status_updates(type: "project", user: "me")` | Last pulse per project for diff context |
| **Completed issues** | `list_issues(assignee: "me", state: "completed", updatedAt: "-P7D")` | Work done this cycle |
| **In-progress issues** | `list_issues(assignee: "me", state: "started")` | Current work |
| **Cycles** | `list_cycles(teamId, type: "current")` + `list_cycles(teamId, type: "next")` | Cycle dates for deadline context |
| **Git activity** | `git log --all --oneline --since=<cycle-start> --author=<user>` | Commits for additional context |
| **Project details** | `get_project(query, includeMilestones: true)` per project | Milestone progress and targets |
| **All project issues** | `list_issues(project: <name>)` per project | Full issue landscape (not just user's) |

**Two-phase collection:** Sources 1-6 run in parallel (round 1). Sources 7-8 depend on project list from round 1 and run in parallel per project (round 2).

**Tip:** `list_projects` with `includeMembers` and `includeMilestones` may exceed query complexity. Fetch projects first (lightweight), then `get_project` per project with milestones.

### 2. Classify Projects

Separate projects into two groups:

| Group | Criteria | Action |
|-------|----------|--------|
| **Lead** | User is `project.lead` | Draft pulse update |
| **Contributor** | User has issues but is not lead | List in a "Contributor Activity" section shown to user (not posted to Linear) |

Present the classification table to user for confirmation before drafting. The contributor summary is informational for the user only — it is never posted as a pulse update.

### 3. Assess Health

Per project, evaluate health using the heuristic in `${CLAUDE_PLUGIN_ROOT}/reference/health-assessment.md`.

**Quick thresholds** (inline fallback if reference unavailable):
- **onTrack** — progress proportional to elapsed time, remaining work assigned, no blockers
- **atRisk** — progress <30% with <3 days to target, critical issues unassigned, or target needs shifting. Default here when uncertain.
- **offTrack** — will miss target without scope reduction or deadline extension, progress <10% in current cycle

Evaluate per milestone, roll up to project level (worst milestone wins). Milestones without target dates are informational — exclude from rollup. Evaluate against post-adjustment scope when issues have been moved.

### 4. Draft Updates

One draft per lead project. Structure per update:

```markdown
## <Milestone Name> (<progress>, target <date>)

### Completed
- **DRC-XXXX** Description (assignee)

### In progress / Remaining
- **DRC-XXXX** Description (assignee, status)

### Risk (if atRisk or offTrack)
Explain what's behind and what's needed.

### Scope adjustment (if any)
Issues moved between milestones, with reasoning.

### Action needed (if any)
@mentions for reviews, decisions, or unblocking.

### Summary
1-2 sentence executive summary of where the project stands.

### Next: <Next Milestone> (if applicable)
- Upcoming issues not yet started
```

**Drafting rules:**
- Include ALL assignees' work, not just user's — the update represents the whole project
- Group by milestone when project has multiple active milestones
- Use issue identifiers (DRC-XXXX) for traceability
- Note cross-project contributions in "Cross-project delivery" section
- Mention cycle numbers when discussing timeline shifts

### 5. GATE — Present for Review

Show all drafts to user with a summary table:

```
| Project | Health | Key highlights |
```

**GATE is mandatory.** Never post without user confirmation — even if user explicitly asks to skip review. Blanket pre-approval is not confirmation; always present the draft first. A wrong health signal propagates to the entire team.

User may:
- Adjust health assessment
- Add/remove content
- Change wording
- Request specific @mentions
- Shift milestone targets

Incorporate all feedback, then confirm again if changes are significant.

### 6. Post to Linear

Post all approved updates in parallel using `save_status_update`:

```
save_status_update(
  type: "project",
  project: "<project name>",
  health: "onTrack" | "atRisk" | "offTrack",
  body: "<markdown content>"
)
```

After posting, present a summary table with links:

```
| Project | Health | Diff | Link |
```

Linear auto-generates a `diffMarkdown` showing milestone progress changes since last update — include this in the summary.

## Arguments

The skill accepts optional arguments:

- **No args** — update all projects where user is lead
- **Project name** — update a specific project only
- **`--contributor`** — also draft updates for contributor projects (unusual, but supported)

## Rules

- **Always collect fresh data** — never rely on memory or prior conversation context for issue states
- **Parallel fetch** — collect all data sources concurrently
- **GATE before every post** — user approves all content
- **Lead projects only** by default — contributor projects are lead's responsibility
- **Include team contributions** — pulse represents the project, not just the user
- **Health is a signal, not a grade** — `atRisk` means "team pay attention", not failure

## Red Flags — STOP and Reconsider

- About to post pulse update without showing draft to user
- User asks to skip review — this is a GATE bypass, not pre-approval
- Drafting update for a contributor project without `--contributor` flag
- Using stale data from earlier in the conversation instead of fresh API calls
- Health assessment doesn't match the reasoning in the draft body
- Omitting conditional sections (Risk, Scope adjustment) to shorten the update when they apply

## Additional Resources

### Reference Files

- **`${CLAUDE_PLUGIN_ROOT}/reference/health-assessment.md`** — Health assessment heuristic with examples
