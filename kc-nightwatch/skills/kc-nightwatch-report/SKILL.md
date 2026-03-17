---
name: kc-nightwatch-report
description: Use when checking nightwatch status, viewing last run results, reviewing improvement history, or reviewing pending proposals. Triggered by '/kc-nightwatch-report', '/kc-nightwatch-report --last', '/kc-nightwatch-report --review', or asking about nightwatch activity.
---

# kc-nightwatch Report

View nightwatch results or review pending proposals.

## Arguments

- `/kc-nightwatch-report` — **status mode** (default): show last run summary, recent activity, trends
- `/kc-nightwatch-report --last` — **trace mode**: show detailed execution trace of last run
- `/kc-nightwatch-report --compare` — **compare mode**: compare last N runs side-by-side
- `/kc-nightwatch-report --review` — **review mode**: interactive review of pending proposal and fix branches

Route to the appropriate section below.

---

## Status Mode (default)

### Step 1: Read Improvement Log

Read `~/.claude/kc-plugins-config/nightwatch-improvement-log.md` from the kc-nightwatch plugin directory.

The file has YAML frontmatter with `last_run` and `runs` fields, followed by markdown sections organized by date.

#### If No Runs Yet

If `last_run: null` or `runs: 0`:

```
🌙 kc-nightwatch — 尚未執行

No nightly runs recorded yet.
Run `/kc-nightwatch` manually or wait for the next cron cycle.
```

Stop here.

### Step 2: Present Summary

Display:

```
🌙 kc-nightwatch Report
Last run: {last_run}
Total runs: {runs}
```

### Step 3: Recent Improvements (Last 7 Days)

Parse the improvement-log.md sections for entries within the last 7 days.

Group by action type:

```
## Recent Activity (last 7 days)

🔧 Auto-fixes:
• {date} — {plugin}: {summary}
  Branch: {branch} | PR: {pr_link or "local branch"}

📋 Proposals:
• {date} — {plugin}: {summary}
  Branch: {branch} | PR: {pr_link or "local branch"}

⏭️ Skipped:
• {date} — {plugin}: {signal_id} — {reason}
```

#### PR Link Display

For entries with PR links (remote repos):
- Show clickable link: `[PR #{number}]({url})`

For entries with local branches only (no remote):
- Show branch name: `local branch: {branch_name}`
- Include a note: `(review with: git log main..{branch_name})`

#### If No Recent Activity

If no entries within last 7 days:

```
No activity in the last 7 days. All quiet. 🌙
```

### Step 4: Signal Trends (Optional)

If there are 3+ runs in the log, look for patterns:

- **Recurring signals**: Same proxy signal appearing in 3+ runs → flag as persistent gap
- **Plugin health**: Which plugins frequently need fixes vs which are stable
- **Signal confidence distribution**: Are most signals high/medium/low?

Present trends only if patterns are clear. Do not fabricate trends from insufficient data.

### Step 5: Pending Proposals

Check for open proposal branches:

```bash
git branch --list "kc-nightwatch/*-proposal" 2>/dev/null
```

For each proposal branch found:
1. Read `PROPOSAL.md` from the branch
2. Display a one-line summary

```
## Pending Proposals

• {branch}: {proposal title}
  Plugin: {plugin} | Created: {date}
```

If no proposal branches exist, skip this section.

Suggest: `Use /kc-nightwatch-report --review to accept, defer, or reject proposals.`

---

## Trace Mode (`--last`)

Show detailed execution trace of the last nightwatch run.

### Step T1: Read Run Trace

Read `~/.claude/kc-plugins-config/nightwatch-runs.yaml`. Take the last entry from the `runs` list.

If file doesn't exist or is empty:
```
No run trace found. Run /kc-nightwatch first.
```

### Step T2: Render Trace

Present the run trace as a human-readable report:

```
🌙 kc-nightwatch Run Trace — {date}
Mode: {mode} | Duration: {duration}s

📊 Targets ({active} active, {skipped} skipped):

  my-app:
    Agents:
      ✅ signal-harvester: 3 signals
      ❌ sentry-scanner: MCP unavailable
      ⬚ e2e-scanner: 0 signals (no e2e-reports/ dir)
      ✅ git-scanner: 1 signal

    Signal Funnel:
      found → dedup → filter → cooldown → classified → executed
        4   →   4   →   3    →    3     →     3      →    3

    Actions: 2× linear-issue, 1× alert

  ⏭️ Skipped: my-plugin (dirty), another-plugin (recent commit)

Summary: 4 signals → 3 actions, 1 error
```

### Step T3: Health Warnings

If the trace shows patterns worth flagging:

- Agent failed 3+ consecutive runs → `⚠️ {agent} has failed {N} consecutive runs — check MCP/tool config`
- Target skipped 3+ consecutive runs → `⚠️ {target} skipped {N} times — check repo state`
- Signal funnel has >50% drop at any stage → `ℹ️ High signal loss at {stage} — review filtering criteria`

Read previous entries from `nightwatch-runs.yaml` to detect consecutive patterns.

---

## Compare Mode (`--compare`)

Compare the last N runs side-by-side.

### Step C1: Read Runs

Read `~/.claude/kc-plugins-config/nightwatch-runs.yaml`. Default: last 3 runs. User can specify N.

### Step C2: Render Comparison

Present per-target signal funnel trends:

```
🌙 kc-nightwatch — Last 3 Runs

            │ Mar 13  │ Mar 14  │ Mar 15
────────────┼─────────┼─────────┼────────
my-app      │         │         │
  signals   │   -     │   4     │   6
  actions   │   -     │   2     │   3
  errors    │   -     │   0     │   1
────────────┼─────────┼─────────┼────────
my-plugin   │   3     │ skipped │   2
  signals   │   3     │   -     │   2
  actions   │   2     │   -     │   1
```

### Step C3: Trend Insights

If enough data (3+ runs), surface trends:
- "my-app signals trending up (4 → 6) — new sources finding more issues"
- "sentry-scanner failed 2/3 runs — investigate MCP connectivity"

---

## Review Mode (`--review`)

Interactive review of all pending nightwatch branches (proposals AND fixes).

### Step R1: Discover Branches

Scan ALL repos referenced in `~/.claude/kc-plugins-config/nightwatch-targets.yaml` for nightwatch branches:

```bash
cd {repo_root} && git branch --list "kc-nightwatch/*" 2>/dev/null
```

Classify each branch:
- `*-proposal` → proposal (needs human decision)
- `*-fixes` or `*-forge-fix` → fix (already validated, needs merge decision)

If zero branches found:

```
No pending nightwatch branches. Nothing to review.
```

Stop here.

### Step R2: Present Review Queue

Display all branches grouped by repo:

```
🌙 kc-nightwatch Review Queue

📦 my-plugins (local only):
  1. [proposal] kc-nightwatch/2026-03-15-kc-plugin-forge-proposal
  2. [proposal] kc-nightwatch/2026-03-15-kc-pr-flow-proposal
  3. [proposal] kc-nightwatch/2026-03-15-kc-team-ops-proposal
  4. [fix]      kc-nightwatch/2026-03-15-kc-team-ops-fixes

📦 kc-claude-plugins (has remote):
  5. [proposal] kc-nightwatch/2026-03-15-e2e-pipeline-proposal — Draft PR #2
  6. [fix]      kc-nightwatch/2026-03-15-e2e-pipeline-fixes — PR #1

Review all? Or enter numbers to review specific branches (e.g., "1,3,5"):
```

Wait for user input. If user says "all", review all branches in order.

### Step R3: Review Each Branch

**One-at-a-time principle:** Present proposals individually for focused decision-making. The overview in Step R2 gives the full picture; this step zooms in on one item at a time. Never batch multiple proposals into a single decision prompt.

For each selected branch:

1. **Show diff summary:**
   ```bash
   cd {repo_root} && git log main..{branch} --oneline
   ```

2. **For fixes** — show `git diff main..{branch} --stat`, then present options:
   ```
   [{branch}] — {summary}

   [M]erge  — merge to main, delete branch
   [D]efer  — keep branch for next review cycle
   [R]eject — delete branch, revert the fix
   ```
   Wait for user decision before proceeding.

3. **For proposals** — a PROPOSAL.md may contain multiple proposals (## 1, ## 2, …). Read via `git show {branch}:{plugin}/PROPOSAL.md`, then present **each proposal individually**:

   ```
   [{branch}] Proposal {N}/{total}: {title}
   Plugin: {plugin} | Confidence: {confidence} | Proxy signal: {proxy}

   Current: {1-2 sentence current state}
   Suggested: {1-2 sentence change}
   Files: {affected files}

   [A]ccept — merge to main, create implementation todo
   [D]efer  — keep for next review cycle
   [R]eject — not worth pursuing
   ```

   Wait for decision on this single proposal before showing the next one.

   **Branch-level resolution:** After all proposals in a PROPOSAL.md are reviewed:
   - All accepted → merge branch, delete
   - All rejected → delete branch
   - Mixed (some accepted, some rejected/deferred) → edit PROPOSAL.md on branch to remove rejected items, keep branch if any deferred items remain, merge if only accepted items remain

### Step R4: Execute Decisions

**Accept (proposal):**
```bash
cd {repo_root}
git merge {branch} --no-ff -m "kc-nightwatch: accept proposal — {summary}"
git branch -d {branch}
```
- If the repo has a remote and an open draft PR: close the PR with comment "Accepted via /kc-nightwatch-report --review"
- Offer to create a todo for implementation: `Would you like to create a todo for implementing this proposal?`

**Merge (fix):**
```bash
cd {repo_root}
git merge {branch} --no-ff -m "kc-nightwatch: merge fix — {summary}"
git branch -d {branch}
```
- If the repo has a remote and an open PR: merge the PR via `gh pr merge {number} --merge`

**Defer:**
No action. Branch stays. Log: `Deferred: {branch}`

**Reject:**
```bash
cd {repo_root}
git branch -D {branch}
```
- If the repo has a remote: close the PR via `gh pr close {number} --comment "Rejected via /kc-nightwatch-report --review"`
- Remove from remote if pushed: `git push origin --delete {branch}`

### Step R5: Summary

After all reviews complete:

```
🌙 Review Complete

Accepted:  {count} proposals
Merged:    {count} fixes
Deferred:  {count}
Rejected:  {count}
```

Update `~/.claude/kc-plugins-config/nightwatch-improvement-log.md` — add a `reviewed:` field to each processed signal entry with the decision and date.
