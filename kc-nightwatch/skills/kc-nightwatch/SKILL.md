---
name: kc-nightwatch
description: Use when running nightly plugin improvement cycle — forge validation, signal harvesting, north-star gap analysis, auto-fix and proposal generation. Triggered by cron or manual invocation.
---

# kc-nightwatch — Nightly Plugin Improvement

Autonomous nightly pipeline that patrols each plugin, fixes structural issues, and proposes north-star-aligned improvements.

**Core philosophy:** Find cracks in the wall and patch them nightly. Never tear down a wall.

## Arguments

Parse the invocation arguments:

- `/kc-nightwatch` — **production mode** (all safety guards active)
- `/kc-nightwatch --self-repair` — **self-repair mode**: validate config, collect feedback, check own forge status. Runs as Phase SR (before Phase 0). Does NOT run the regular pipeline.
- `/kc-nightwatch --dry-run` — **dry-run mode**: bypasses `skip_if_dirty` and `skip_if_recent_human_commit` guards. Combinable with any mode.

When `--dry-run` is active, prefix all log output with `[DRY-RUN]`.
When `--self-repair` is active, prefix all log output with `[SELF-REPAIR]`.

**Mode routing:**
- `--self-repair` → execute Phase SR only, then stop
- no args / `--dry-run` only → execute Phase 0-5 (existing pipeline)

## Prerequisites Check

Before starting, check for optional plugin dependencies:
- **kc-plugin-forge** — invoke `Skill: "kc-plugin-forge"` with `validate-only` (used in Phase 1)

If kc-plugin-forge is not loaded:
```
[WARN] kc-plugin-forge not loaded — Phase 1 (forge validation) will be skipped
```
Set `forge_available = false` and continue. Phase 1 will be skipped entirely.

## Phase SR: Self-Repair (--self-repair mode only)

Runs in a dedicated session before the regular pipeline. Three responsibilities:
1. Config validation + auto-fix
2. Feedback collection from previous runs
3. Own plugin forge check

### Step SR.1: Load Self-Repair Config

Read:
1. `~/.claude/kc-plugins-config/nightwatch-targets.yaml` — targets to validate
2. `config/safety.yaml` → `self_repair` section — limits and matching algorithm
3. `~/.claude/kc-plugins-config/nightwatch-improvement-log.md` → `last_run` timestamp (for feedback scan window)

### Step SR.2: Config Validation + Auto-Fix

For each target in `nightwatch-targets.yaml`:

**Checks to perform:**

| Field | Check | Auto-fixable? |
|-------|-------|--------------|
| `path` | Directory exists | No — log warning, mark target for skip |
| `linear_team` | Team exists in Linear (`list_teams`) | Yes — name resolution |
| `linear_project` | Project exists (`list_projects`) | Yes — name resolution |
| `sentry_org` + `sentry_projects` | Accessible (no 403) | No — log warning with suggestion |
| `webhook` (from channels.yaml) | URL responds to POST | No — log warning |

**Name resolution matching algorithm** (from `safety.yaml`):

1. Fetch all teams/projects from Linear MCP
2. For the configured value, try in order:
   a. **Exact match** → use it (no fix needed)
   b. **Case-insensitive exact match** → auto-fix, log correction
   c. **Single substring match** (configured value is substring of exactly one result) → auto-fix, log correction
   d. **2+ substring matches** → ambiguous, skip — log all candidates
   e. **Zero matches** → skip — log error

**Before modifying `nightwatch-targets.yaml`:**
```bash
cp ~/.claude/kc-plugins-config/nightwatch-targets.yaml \
   ~/.claude/kc-plugins-config/nightwatch-targets.yaml.bak
```

**Cap:** max `self_repair.max_config_fixes` corrections per run (default: 3). After reaching the cap, log remaining issues without fixing.

**Linear/Sentry MCP unavailable:** If Linear or Sentry MCP tools are not available in this session, skip those checks — log: `[SELF-REPAIR] Linear MCP unavailable, skipping team/project validation`. Do NOT fail the entire self-repair phase.

### Step SR.3: Feedback Collection

Scan nightwatch's own output from previous runs to close the feedback loop.

**PR feedback** — for each repo that has a remote:

```bash
gh pr list --label kc-nightwatch --state all --limit 10 --json number,title,state,comments,reviews,mergedAt,closedAt
```

For each PR updated since `last_run`:
- **Merged (no review comments)** → `status: accepted`
- **Merged (with review comments)** → `status: corrected`, extract correction summary
- **Closed without merge** → `status: rejected`
- **Still open** → skip (not yet resolved)

Extract the `signal_id` from the PR body (nightwatch PRs include signal ID in the description).

**Linear issue feedback** — for each target with `linear_team`:

```
list_issues: team={linear_team}, labels=["nightwatch"], includeArchived: true
```

For each issue updated since `last_run`:
- **Done / Completed** → `status: accepted`
- **Won't fix / Canceled** → `status: rejected`, `cooldown_override: 30d`
- **Duplicate** → `status: duplicate`, follow to original issue
- **Still open** → skip

**Aggregate reject rates:**

For each proxy signal that has 3+ historical feedback entries in `nightwatch-improvement-log.md`:
- Count accepted vs rejected
- Calculate reject rate: `rejected / (accepted + rejected)`
- Store in aggregates

**Write output** to `~/.claude/kc-plugins-config/nightwatch-feedback.yaml`:

```yaml
collected_at: {ISO 8601 timestamp}
pr_feedback:
  - signal_id: {id}
    status: {accepted | rejected | corrected}
    source: "{PR #N description}"
    cooldown_override: null  # or "30d" for rejected
linear_feedback:
  - signal_id: {id}
    status: {accepted | rejected | duplicate}
    source: "{issue identifier}"
    cooldown_override: null
aggregates:
  proxy_signal_reject_rates:
    {proxy_signal_id}: {float 0.0-1.0}
```

If no feedback found, write file with empty lists (the file existing with `collected_at` is the signal that self-repair ran).

### Step SR.4: Own Plugin Forge Check

Run forge validate-only on kc-nightwatch itself. This replaces the v0.1 self-monitoring exclusion.

**Prerequisites:** kc-plugin-forge must be loaded in this session. If not → log warning and skip.

```
Skill: "kc-plugin-forge" args: "validate-only {kc-nightwatch plugin path}"
```

**Scope restriction:** Only act on **structural** FAIL items (plugin.json schema, missing required files). Do NOT fix behavioral skill content (that goes through the normal proposal pipeline).

**If FAIL (structural):**
1. Create branch: `kc-nightwatch/$(date +%Y-%m-%d)-self-forge-fix`
2. Apply fixes (subject to `auto_fix.allowed_operations` and `auto_fix.max_files_per_plugin`)
3. Re-validate with forge
4. If still FAIL → revert, log failure
5. If PASS → commit, return to main
6. **Circuit breaker:** max `self_repair.max_self_fix_prs` PRs (default: 1)

**If PASS:** log `[SELF-REPAIR] forge: PASS` and continue.

### Step SR.5: Write Self-Repair Output

Write all results to `~/.claude/kc-plugins-config/nightwatch-self-repair.yaml`:

```yaml
run_date: {ISO 8601 timestamp}
config_fixes:
  - target: {name}
    field: {field_name}
    before: "{old value}"
    after: "{new value}"
    method: "{exact | case-insensitive | single-substring}"
config_warnings:
  - target: {name}
    field: {field_name}
    error: "{error description}"
    suggestion: "{what user should do}"
forge_result:
  status: {pass | fail | skipped}
  branch: null  # or branch name if PR created
  details: "{if fail, what failed}"
feedback_collected:
  prs_scanned: {count}
  issues_scanned: {count}
  new_feedback_entries: {count}
```

Report completion:
```
[SELF-REPAIR] complete
  Config fixes: {count}
  Config warnings: {count}
  Forge: {pass/fail/skipped}
  Feedback: {prs_scanned} PRs, {issues_scanned} issues → {new_feedback_entries} new entries
```

## Phase 0: Preflight

### Step 0.1: Load Configuration

Read these files:

1. `~/.claude/kc-plugins-config/nightwatch-targets.yaml` — monitoring targets with paths, keywords, proxy signals, type, sources, actions
2. `config/safety.yaml` (from kc-nightwatch plugin directory) — all safety boundaries and limits
3. `~/.claude/kc-plugins-config/nightwatch-improvement-log.md` (from kc-nightwatch plugin directory) — last run results and cooldown data
4. `~/.claude/kc-plugins-config/language.yaml` — output language preferences (shared across kc-plugins)
5. `~/.claude/kc-plugins-config/nightwatch-feedback.yaml` (optional) — feedback from self-repair session. If file exists and `collected_at` is within the last 24h, apply these adjustments:
   - For each proxy signal in `aggregates.proxy_signal_reject_rates`:
     - Rate > 0.5 → only process `confidence: high` signals for this proxy signal (drop `medium`)
     - Rate ≤ 0.5 → keep default threshold (`medium` and above)
   - For each entry with `cooldown_override: 30d` → extend that signal's cooldown from 7d to 30d
   - If file doesn't exist or `collected_at` is stale (>24h) → no adjustments (default behavior)

**Language resolution:** For each target, resolve the output language:
1. Match target's `path` against `overrides` entries in `language.yaml` (longest prefix match)
2. If no override matches → use `default` (typically `en`)
3. Store the resolved language per target for use in Phase 4 (Linear issue title/description, Slack report text) and Phase 5 (Slack morning report)

**Target filtering:** Only process targets whose `type` and `actions` are supported by the current version. In v0.3, supported types: `plugin`, `product`. Supported actions: `quick-fix`, `proposal`, `linear-issue`, `alert`, `e2e-flow`. Skip targets whose `actions` list is empty or contains unknown action types.

Store the safety values for reference throughout execution:
- `auto_fix.max_files_per_plugin`: max files to auto-fix per plugin
- `auto_fix.allowed_operations`: what file operations are allowed for auto-fix
- `proposal.max_per_plugin`: max proposals per plugin
- `e2e_flow.max_files_per_target`: max flow YAML files to create per target (default: 1)
- `e2e_flow.require_existing_mapping`: whether to require existing `.claude/e2e/mappings/`
- `alert.max_per_target`: max alert signals per target per run (default: 5)
- `global.skip_if_dirty`: whether to skip plugins with uncommitted changes
- `global.skip_if_recent_human_commit`: time threshold for recent human commits
- `global.cooldown_per_signal`: cooldown period for signal deduplication

### Step 0.2: Resolve Target Paths

**For `type: plugin` targets** — `path` field is optional. Resolve source path automatically:

1. Check `~/.claude/plugins/local/{target_name}`:
   ```bash
   readlink -f ~/.claude/plugins/local/{target_name} 2>/dev/null
   ```
   If it's a symlink → resolved path is the source directory.
   If it's a regular directory AND is a git repo → use it as source.
   If it's a regular directory but NOT a git repo → it's a copy, continue to step 2.

2. Scan `$KC_WORKSPACE` (if env var is set) for the plugin:
   ```bash
   find "$KC_WORKSPACE" -path "*/{target_name}/.claude-plugin/plugin.json" -maxdepth 4 2>/dev/null | head -1
   ```
   Extract parent directory as source path.

3. If still not found → log warning and skip: `[WARN] Cannot resolve source path for {target_name} — skipping`

4. If target has an explicit `path` field → use it directly (override auto-resolution).

Store for each plugin target:
- `path` — resolved source directory (e.g., `~/Project/workspace/kc-claude-plugins/kc-pr-flow`)
- `repo_root` — git repo root: `git -C {path} rev-parse --show-toplevel`
- `repo` — from target config if set, otherwise basename of `repo_root`
- `has_remote` — `git -C {repo_root} remote get-url origin 2>/dev/null` succeeds

**For `type: product` targets** — `path` is required. Resolve:
1. Expand `~` in path to absolute path
2. Verify the directory exists
3. Verify it's a git repo

If a target path is invalid, log a warning and skip it (do not abort the entire run).

### Step 0.3: Check Skip Conditions (per plugin)

**If `--dry-run` mode:** Skip all guard checks below. All verified plugins become active. Log: `[DRY-RUN] Bypassing skip guards — all plugins active`

**If production mode:** For each plugin:

**skip_if_dirty check:**
```bash
cd {plugin_repo_root} && git diff --quiet HEAD
```
If exit code is non-zero (tracked files have uncommitted changes) → skip ALL plugins in this repo. Log: `Skipping {plugin}: uncommitted changes detected`

Note: This uses `git diff --quiet HEAD` instead of `git status --porcelain` to ignore untracked files. Untracked files don't affect git branch/checkout operations and should not block nightwatch.

**skip_if_recent_human_commit check:**
```bash
cd {plugin_repo_root} && git log -1 --format="%aI" --no-merges
```
Parse the timestamp. If the most recent commit is within `skip_if_recent_human_commit` (default: 2h) of now → skip this plugin. Log: `Skipping {plugin}: recent human commit at {timestamp}`

**IMPORTANT:** Check BOTH conditions. A plugin can be skipped for either reason.

Build the list of **active plugins** (those that passed both checks).

If zero active plugins remain → log `kc-nightwatch: all plugins skipped — silent night` and proceed directly to Phase 5 (output a "no changes" report).

### Step 0.4: Scan Feedback from Previous Runs

Check if nightwatch's previous output received responses. This closes the feedback loop — rejected or corrected signals inform future classification.

**PR feedback (repos with remote):**

For each repo that has a remote, search for nightwatch PR comments:

```bash
gh pr list --label kc-nightwatch --state all --limit 10 --json number,title,state,comments,reviews
```

For each PR with new comments or reviews since `last_run`:
- **Rejected** (PR closed without merge + negative comment): add signal ID to `~/.claude/kc-plugins-config/nightwatch-improvement-log.md` with `feedback: rejected` and extend cooldown to 30 days
- **Correction** (PR merged but with review comments suggesting a different approach): log `feedback: corrected` with the correction summary — future signals on the same proxy signal will use this context
- **Approved** (PR merged, no issues): log `feedback: accepted` — confirms signal quality

**Linear issue feedback:**

For each target with `linear_project` configured:

```
list_issues: project={linear_project}, labels=["nightwatch"], state="done", updated_after={last_run}
```

For each resolved issue:
- **Won't fix / Not planned**: add signal ID with `feedback: rejected`, extend cooldown to 30 days
- **Duplicate**: log `feedback: duplicate` with the original issue ID — merge signal references
- **Done**: log `feedback: accepted`

**Store feedback in improvement-log.md:**

Add a `## Feedback` section under the run date:

```markdown
## Feedback (from previous runs)

- signal: sig-20260315-003
  feedback: rejected
  source: PR #1 closed with comment "not applicable to our setup"
  cooldown_override: 30d

- signal: sig-20260314-001
  feedback: accepted
  source: Linear SC-XXX completed
```

**Impact on Phase 3:** When classifying signals in Step 3.2 (Cooldown Check), check the `feedback` field:
- `rejected` → signal is in permanent cooldown (30d) regardless of the default 7d
- `corrected` → use correction context to adjust confidence (typically downgrade by one level)
- `accepted` → no change (confirms the signal was valuable)

## Phase 0.5: Indicator Baseline Measurement

**Purpose:** Measure quantified indicator values BEFORE any actions, providing a baseline to compare against after the run.

For each active target's `indicators` list (from nightwatch-targets.yaml), measure the current value:

1. **Read the target's indicators** from nightwatch-targets.yaml. Each indicator has `id` and `description`.
2. **For each indicator**, attempt to measure its current value using available tools:
   - Test coverage: run `bun test --coverage` or read last coverage report
   - Git churn: count commits in last 7 days via `git log --oneline --since="7 days ago" | wc -l`
   - Open issues: count via `gh issue list --state open --json number | jq length`
   - Lint warnings: run linter in count mode
   - If measurement fails, log warning and skip that indicator
3. **Compute trend** by comparing against the previous run's baseline (from `nightwatch-feedback.yaml` under `baselines:` key):
   - Value improved → `trend: improving`
   - Value unchanged (within 5%) → `trend: stable`
   - Value worsened → `trend: degrading`
   - No previous value → `trend: stable` (first measurement)
4. **Store baselines** in the run's structured output (written to summary.yaml in Phase 5)

**Output format** (YAML, written as part of summary.yaml per-target section):

```yaml
indicator_baseline:
  test-coverage:
    value: 85
    measurement: "percent"
    previous_value: 82
    trend: improving
  open-issues:
    value: 12
    measurement: "count"
    previous_value: 15
    trend: improving
```

If a target has no `indicators` defined, skip Phase 0.5 for that target and leave `indicator_baseline: {}`.

## Phase 1: Forge Validation

**Skip entirely if `forge_available = false`** — log `[SKIP] Phase 1: kc-plugin-forge not loaded` and proceed to Phase 2.

**Only for `type: plugin` targets.** Product targets skip Phase 1 entirely — proceed directly to Phase 2.

For each active plugin target (can be parallel):

### Step 1.1: Run Forge Validate-Only

```
Skill: "kc-plugin-forge" args: "validate-only {plugin_path}"
```

If the skill invocation fails (not loaded, error), log the error and skip this plugin for Phase 1.

### Step 1.2: Handle FAIL Items

If forge reports any FAIL items:

1. **Create a fix branch:**
   ```bash
   cd {plugin_repo_root}
   git checkout -b kc-nightwatch/$(date +%Y-%m-%d)-{plugin_name}-forge-fix
   ```

2. **Auto-fix each FAIL item**, subject to these constraints:
   - Maximum `auto_fix.max_files_per_plugin` files (read from safety.yaml)
   - Only `auto_fix.allowed_operations` operations (default: `[edit]` — NO create, NO delete)
   - If more FAIL items exist than the file limit allows, prioritize by severity (structural > cosmetic)

3. **Re-validate after fixing:**
   ```
   Skill: "kc-plugin-forge" args: "validate-only {plugin_path}"
   ```
   If still FAIL → revert changes on this branch and log: `Auto-fix failed for {plugin}: forge still reports FAIL after fixes`

4. **Commit to branch:**
   ```bash
   git add {changed_files}
   git commit -m "kc-nightwatch: fix {summary_of_fixes}"
   ```

5. **Return to main:**
   ```bash
   git checkout main
   ```

### Step 1.3: PASS → Proceed

If forge reports PASS (or PASS after auto-fix), mark this plugin as ready for Phase 2.

### Safety Guards — Phase 1

<CRITICAL>
These rules are NON-NEGOTIABLE. Do not rationalize exceptions.

1. **File limit is absolute.** If safety.yaml says `max_files_per_plugin: 3` and you have 5 FAIL items, you fix AT MOST 3 files. The remaining 2 are logged and deferred. Do not think "but this one is trivial, it doesn't really count."

2. **Edit-only means edit-only.** If `allowed_operations: [edit]`, you may NOT create new files, NOT delete files, NOT rename files. Even if the fix "obviously requires" creating a helper file — you cannot. Log it as "auto-fix not possible: requires create operation" and defer.

3. **Skip-if-dirty is absolute.** If a plugin has uncommitted changes, you skip it entirely. Do not think "I'll stash the changes first" or "I'll only touch different files." SKIP.
</CRITICAL>

## Phase 2: Signal Harvest

For each active target (can be parallel across targets):

### Source → Agent Mapping

The orchestrator dispatches discovery agents based on the target's `sources` field:

| Source | Agent | Required config |
|--------|-------|----------------|
| `journal`, `episodic-memory`, `memory-md` | `signal-harvester` | (always available) |
| `sentry` | `sentry-scanner` | `sentry_projects` + `sentry_org` in target |
| `e2e-reports` | `e2e-scanner` | (scans `{path}/e2e-reports/` and `{path}/.claude/e2e/`) |
| `git-stats` | `git-scanner` | (scans git log in `{path}`) |

Group sources by agent: if a target has `[journal, episodic-memory, memory-md, sentry, git-stats]`, dispatch 3 agents: signal-harvester, sentry-scanner, git-scanner.

### Step 2.1: Dispatch Discovery Agents

For each active target, determine which agents to dispatch based on `sources`:

**Signal-harvester** — if sources includes ANY of `journal`, `episodic-memory`, `memory-md`:
```
Agent:
  subagent_type: kc-nightwatch:signal-harvester
  prompt: "Harvest signals for {name}. Keywords: {keywords}. North star: {north_star}. Proxy signals: {proxy_signals}. Plugin path: {path}. Repo: {repo}."
  model: sonnet
```

If the signal-harvester agent is not available (plugin not loaded), fall back to a general-purpose agent with the signal-harvester system prompt injected. Read the agent definition from `agents/signal-harvester.md` and include the full system prompt section in the dispatch.

**Sentry-scanner** — if sources includes `sentry` AND target has `sentry_projects`:
```
Agent:
  subagent_type: kc-nightwatch:sentry-scanner
  prompt: "Scan Sentry for {name}. Org: {sentry_org}. Projects: {sentry_projects}. Keywords: {keywords}. North star: {north_star}. Proxy signals: {proxy_signals}. Plugin path: {path}. Repo: {repo}."
  model: sonnet
```

If `sentry` is in sources but `sentry_projects` is missing → log warning: `Skipping sentry source for {name}: no sentry_projects configured`

**E2E-scanner** — if sources includes `e2e-reports`:
```
Agent:
  subagent_type: kc-nightwatch:e2e-scanner
  prompt: "Scan E2E reports for {name}. Path: {path}. Keywords: {keywords}. North star: {north_star}. Proxy signals: {proxy_signals}. Plugin path: {path}. Repo: {repo}."
  model: sonnet
```

**Git-scanner** — if sources includes `git-stats`:
```
Agent:
  subagent_type: kc-nightwatch:git-scanner
  prompt: "Scan git stats for {name}. Path: {path}. Keywords: {keywords}. North star: {north_star}. Proxy signals: {proxy_signals}. Plugin path: {path}. Repo: {repo}."
  model: sonnet
```

**Dispatch all agents for all targets in parallel** (use multiple Agent tool calls in one message). Each agent runs independently.

**Agent dispatch failure handling:** If an agent fails to dispatch (e.g., Sentry MCP tools not connected), treat it as returning an empty signals list with a warning. Log: `Agent {agent} failed for {target}: {error}. Continuing with other agents.` Do NOT abort the entire Phase 2.

### Step 2.2: Collect and Merge Results

For each target, collect YAML outputs from all dispatched agents.

**Merge rules:**
1. Concatenate all `signals` arrays into one list per target
2. **Cross-source deduplication:** Compare summaries across agents. If sentry-scanner and signal-harvester both surface the same underlying issue (e.g., Sentry error about booking + journal complaint about booking failures), merge into one signal with `source: sentry+journal`
3. Apply per-source max caps BEFORE merge (each agent already caps internally), then apply per-target max of 10 signals after merge
4. If any agent returns malformed output → log warning, use signals from other agents

**Output:** One merged signal list per target, ready for Phase 3.

## Phase 3: Gap Analysis

### Step 3.1: Aggregate Signals

Collect all signals from all harvesters. Filter:
- **Keep:** `confidence: high` and `confidence: medium`
- **Drop:** `confidence: low`

### Step 3.2: Cooldown Check

For each remaining signal, check `~/.claude/kc-plugins-config/nightwatch-improvement-log.md`:

**Method A — ID match:**
Search for matching `signal:` entries within the last `cooldown_per_signal` days (default: 7d). If found → skip signal.

**Method B — Summary similarity:**
For signals that pass Method A, compare their `summary` against recent improvement-log entries. If a recent entry has substantially the same improvement (different signal ID but same underlying issue) → skip signal. This prevents re-proposing the same improvement under a new harvester-generated ID.

### Step 3.3: Classify

For each signal that passes cooldown, classify based on the target's `actions` list from nightwatch-targets.yaml:

**Quick-fix** (auto-commit, regular PR) — requires `quick-fix` in target's `actions`:
- Wording improvements, typo fixes
- Missing edge case in existing step
- Reference path updates
- Configuration value corrections
- **Test:** Does this change the skill's behavioral logic? If NO → quick-fix.

**Proposal** (draft PR, human review required) — requires `proposal` in target's `actions`:
- New steps or sections in a skill
- Logic changes in existing steps
- New agent capabilities
- Cross-skill dependency changes
- **Test:** Does this change the skill's behavioral logic? If YES → proposal.

**Linear Issue** (informational, no code change) — requires `linear-issue` in target's `actions`:
- Signals from product targets where code changes are not appropriate
- Error trends, performance degradation, coverage gaps
- Signals where the right fix is unclear and needs team investigation
- **Test:** Is this a `type: product` target AND the signal suggests investigation rather than a specific code change? → linear-issue.

**Alert** (notify only, no issue or PR) — requires `alert` in target's `actions`:
- Sentry error spikes that may self-resolve (transient infra issues)
- Signals where awareness is sufficient, no action needed yet
- High-frequency events that would flood Linear if filed as issues
- **Test:** Is the signal informational AND likely transient? → alert.

**E2E Flow** (generate E2E flow YAML) — requires `e2e-flow` in target's `actions`:
- Coverage gaps identified by e2e-scanner where a flow YAML should be created
- Test failure patterns that suggest a new regression test flow
- **Test:** Does the signal point to a missing E2E flow that could catch this issue? → e2e-flow.

**Classification priority:** If a signal could be both `proposal` and `linear-issue`, prefer the action that appears in the target's `actions` list. If both are available, use `linear-issue` for investigation-type signals and `proposal` for specific improvement suggestions.

**Extended priority:** `alert` is the least-invasive action — prefer it for transient Sentry signals. `e2e-flow` is preferred over `linear-issue` when the signal clearly maps to a testable user flow.

### Step 3.4: Quick-Fix Pre-Check

For each signal classified as `quick-fix`, verify the fix hasn't already been applied:

1. Identify the target file(s) the signal refers to (from signal summary and source context)
2. Read the target file and search for keywords from the signal's suggested fix
3. If the fix content is already present → reclassify as `skipped` with reason `already addressed in {file}:{line}`

This prevents Phase 4 from attempting fixes that were already applied manually or in a previous session, and keeps the improvement-log free of noise.

### Step 3.5: Cap Per Target

Apply `proposal.max_per_plugin` limit (default: 3) per target across all action types. If more signals pass, keep the highest confidence ones.

### Safety Guards — Phase 3

<CRITICAL>
1. **Classification boundary is behavioral logic.** "Clearer wording" is quick-fix. "Add a validation step" is proposal. When in doubt, classify as proposal (conservative).

2. **Cooldown is non-negotiable.** If a signal was processed within `cooldown_per_signal` days, it is SKIPPED. Do not think "but this time it's more urgent" or "the previous fix didn't fully address it." The cooldown exists to prevent nightly nagging.

3. **Respect target's actions list.** If a target only allows `[proposal, linear-issue]`, do NOT classify any signal as `quick-fix` even if it looks trivial. The target owner has explicitly restricted what nightwatch can do.
</CRITICAL>

## Phase 3.5: Pre-Action Strategy Assessment

**Purpose:** Document the reasoning and strategy BEFORE taking action. This becomes the "Strategy" text visible in the dashboard.

For each active target, AFTER gap analysis classifies signals but BEFORE execution:

1. Review the classified signals and their confidence levels
2. Write a 2-4 sentence pre-assessment summarizing:
   - How many signals will be acted on and why
   - Which indicators are being targeted
   - What the expected impact on the north star is
   - Any signals deliberately skipped and why

**Output:** Store as `pre_assessment` string in the per-target section of summary.yaml.

Example:

```
pre_assessment: "3 high-priority signals identified targeting code quality and test coverage. Focusing on 2 code-fix actions (lint warnings, missing error handling) and 1 proposal (test infrastructure). Skipping 1 low-confidence churn signal. Expected to improve coverage by ~5% and reduce lint warnings to zero."
```

This text should be natural-language prose readable by humans in the dashboard, not structured data.

## Phase 4: Execute

### Step 4.1: Execute Quick-Fixes

For each quick-fix signal:

1. **Create branch:**
   ```bash
   cd {plugin_repo_root}
   git checkout -b kc-nightwatch/$(date +%Y-%m-%d)-{plugin_name}-fixes
   ```

2. **Apply changes:**
   - Only `auto_fix.allowed_operations` operations
   - Only `auto_fix.max_files_per_plugin` files maximum
   - If multiple quick-fixes target the same plugin, batch them on one branch

3. **Re-validate:**
   ```
   Skill: "kc-plugin-forge" args: "validate-only {plugin_path}"
   ```
   If FAIL → revert this quick-fix and log. Do not commit broken changes.

4. **Commit:**
   ```bash
   git add {changed_files}
   git commit -m "kc-nightwatch: {summary}"
   ```

5. **Return to main:**
   ```bash
   git checkout main
   ```

### Step 4.2: Execute Proposals

For each proposal signal:

1. **Create branch:**
   ```bash
   cd {plugin_repo_root}
   git checkout -b kc-nightwatch/$(date +%Y-%m-%d)-{plugin_name}-proposal
   ```

2. **Write PROPOSAL.md** in the plugin's root directory:
   ```markdown
   # Proposal: {signal summary}

   ## Signal
   - ID: {signal_id}
   - Source: {source}
   - Date: {date}
   - Confidence: {confidence}
   - Related proxy signal: {relevant_proxy}

   ## Current State
   {Brief description of current behavior}

   ## Suggested Change
   {What should change and why}

   ## Impact Scope
   - Files likely affected: {list}
   - Cross-plugin dependencies: {if any}

   ## North Star Alignment
   How this moves toward: "{north_star}"
   ```

3. **Commit:**
   ```bash
   git add PROPOSAL.md
   git commit -m "kc-nightwatch: propose {summary}"
   ```

4. **Return to main:**
   ```bash
   git checkout main
   ```

### Step 4.3: Open Linear Issues

For each signal classified as `linear-issue` action (typically from `type: product` targets):

1. **Check target config:** Verify the target has `linear_team` defined in nightwatch-targets.yaml. If not → log: `Cannot create Linear issue for {target}: no linear_team configured` and skip.

   **First-run setup:** If this is the first run for a target with `linear-issue` action:
   - Discover the team: use `list_teams` to find the team, match by `linear_team` name in target config
   - Verify "nightwatch" label exists in the team: use `list_issue_labels` with team filter and name "nightwatch"
   - If label doesn't exist: create it with `create_issue_label` (name: "nightwatch", color: "#6B7280", description: "Auto-generated by kc-nightwatch")
   - Log: `First-run setup for {target}: team={team_name}, label=nightwatch created/verified`

2. **Search for duplicates:** Use Linear MCP to search ALL issues (not just open):
   ```
   list_issues with team: {linear_team}, query: {signal summary keywords}, includeArchived: true
   ```

   If a substantially similar issue is found, route by its status:

   | Issue status | Action | Log message |
   |-------------|--------|-------------|
   | **Open** (Triage / Todo / Backlog / In Progress) | Skip | `similar open issue exists ({issue_id})` |
   | **Done / Completed** | Skip | `already resolved by ({issue_id}), skipping` |
   | **Canceled** | Skip + add 30d cooldown to improvement-log | `previously canceled ({issue_id}), cooldown applied` |
   | **Duplicate** | Follow `relation: duplicate of` to the original issue, then re-evaluate using this same status table against the original | `duplicate of ({original_id}), checking original…` |

   Only proceed to step 3 when **no matching issue is found across any status**.

3. **Create issue:**
   ```
   save_issue:
     title: "nightwatch: {signal summary}"
     team: {linear_team}              # REQUIRED — team name from target config
     project: {linear_project}        # optional — associates with project
     state: "Triage"                  # initial status for investigation
     description: |
       ## Signal
       - ID: {signal_id}
       - Source: {source}
       - Date: {date}
       - Confidence: {confidence}
       - Related proxy signal: {relevant_proxy}

       ## Context
       {signal summary with evidence from harvester}

       ## Suggested Action
       {what should be investigated or improved}

       ## North Star
       {north_star}

       ---
       🤖 Auto-generated by kc-nightwatch
     labels: ["nightwatch"]
     priority: 3  # medium (adjustable: high signal → priority 2)
   ```

   **Key fields:**
   - `team`: required by Linear API, must match a team in the workspace
   - `project`: optional grouping, uses `linear_project` from target config
   - `state`: "Triage" for new discoveries (team investigates and triages)
   - `labels`: "nightwatch" label for filtering and feedback scan (Step 0.4)

   **Language:** Write issue title and description in the target's resolved language (from Step 0.1 language resolution). For example, if a target resolves to `zh-TW`, write the title and description in 正體中文. The `nightwatch:` prefix in the title stays in English (it's a machine identifier, not prose).

4. **Record in improvement-log:**
   ```
   - signal: {signal_id}
     action: linear-issue
     issue: {issue_identifier}
     summary: "{summary}"
   ```

### Step 4.4: Execute Alerts

Apply `alert.max_per_target` cap: if more alert signals exist for a target than the cap allows, keep the highest confidence ones and drop the rest (mark as `skipped` with reason `alert cap exceeded`).

For each alert signal within the cap:

1. **No branch, no PR, no issue.** Alerts are notification-only.

2. **Record in improvement-log:**
   ```
   - signal: {signal_id}
     action: alert
     summary: "{summary}"
     source: {source}
   ```

3. **Queue for Slack report** — alerts appear in a dedicated section of the morning report (see Step 5.3).

Alert signals still respect cooldown — the same alert won't fire again within `cooldown_per_signal` days.

### Step 4.5: Execute E2E Flows

Apply `e2e_flow.max_files_per_target` cap: if more e2e-flow signals exist for a target than the cap allows, keep the highest confidence ones and downgrade the rest to `linear-issue`.

For each e2e-flow signal within the cap:

1. **Check prerequisites:**
   - If `e2e_flow.require_existing_mapping` is true (default): target must have `.claude/e2e/mappings/` directory with at least one mapping YAML
   - If no mapping exists → downgrade to `linear-issue` with note "needs mapping first"

2. **Create branch:**
   ```bash
   cd {target_repo_root}
   git checkout -b kc-nightwatch/$(date +%Y-%m-%d)-{target_name}-e2e-flow
   ```

3. **Generate flow YAML:**
   Create `.claude/e2e/flows/{flow-name}.yaml` based on the signal:
   - Use v2 format: `mapping:`, steps with `id:`, `action:`, `expect:`
   - Reference element names from the existing mapping YAML
   - Flow name derived from signal summary (e.g., `booking-payment-error-regression.yaml`)
   - Include comment: `# Auto-generated by kc-nightwatch from {signal_id}`

4. **Commit:**
   ```bash
   git add .claude/e2e/flows/{flow-name}.yaml
   git commit -m "kc-nightwatch: add E2E flow for {summary}"
   ```

5. **Return to main:**
   ```bash
   git checkout main
   ```

### Safety Guards — Phase 4

<CRITICAL>
1. **Proposals only create PROPOSAL.md.** A proposal branch contains ONLY the PROPOSAL.md file. It does NOT modify any plugin source files. The human decides whether to implement the proposal.

2. **Quick-fixes must pass forge.** Every quick-fix batch must re-validate with forge before committing. If forge fails, ALL changes in that batch are reverted. Do not commit partial fixes.

3. **One branch per plugin per type.** Do not create multiple fix branches for the same plugin in the same run. Batch quick-fixes together.

4. **Linear issues are informational only.** They describe findings and suggest investigation — they do NOT contain implementation instructions or code snippets. The team triages and implements.

5. **Duplicate check before creating.** Always search for existing similar issues. Do not flood the backlog with redundant issues.

6. **Alerts create no artifacts.** An alert signal produces a Slack notification and an improvement-log entry. Nothing else. Do not rationalize "this alert should really be an issue."

7. **E2E flows require existing mappings.** If no mapping YAML exists, downgrade to linear-issue. Do not generate a flow that references unmapped elements.
</CRITICAL>

## Phase 4.5: Post-Action Reflection

**Purpose:** Evaluate what happened AFTER executing actions. This becomes the "Reflection" text visible in the dashboard.

For each active target, AFTER all Phase 4 actions are complete:

1. Review the outcomes of each executed action (success/failure, PR created, etc.)
2. Write a 2-4 sentence post-assessment summarizing:
   - How many actions succeeded vs failed
   - What concrete artifacts were produced (PRs, fixes, proposals)
   - Whether the actions align with the north star
   - Any unexpected outcomes or concerns

**Output:** Store as `post_assessment` string in the per-target section of summary.yaml.

Example:

```
post_assessment: "Executed 2 of 3 planned actions. Code-fix for lint warnings succeeded (PR #47 created). Error handling fix succeeded (PR #48). Test infrastructure proposal deferred -- target repo has CI constraints that need manual resolution. Overall: code quality improved, test coverage unchanged."
```

This text should be natural-language prose, not structured data.

## Phase 5: Output

### Step 5.1: PR Routing

For each branch created in Phase 1 and Phase 4:

**Check repo remote:**
```bash
cd {plugin_repo_root}
git remote -v
```

**Has remote → create PR:**
```bash
gh pr create --base main --head {branch_name} --title "kc-nightwatch: {summary}" --body "{description}" --label "kc-nightwatch"
```
- Quick-fix branches → regular PR
- Proposal branches → draft PR (`gh pr create --draft`)
- E2E flow branches → regular PR

**No remote → local branch only:**
Log the branch name in improvement-log.md. The Slack report shows these as "local branch" entries.

### Step 5.2: Update Improvement Log

Read current `~/.claude/kc-plugins-config/nightwatch-improvement-log.md`, update:

1. Increment `runs` counter in YAML frontmatter
2. Update `last_run` timestamp
3. Add a new date section with all processed signals:

```markdown
## {YYYY-MM-DD}

slack_url: {full Slack message URL or null}

### {plugin_name}
- signal: {signal_id}
  action: quick-fix | proposal | linear-issue | e2e-flow | alert | auto-fix (Phase 1) | skipped
  branch: {branch_name}           # for quick-fix/proposal
  pr: {PR URL or "local branch"}  # for quick-fix/proposal
  issue: {issue identifier}       # for linear-issue
  files_changed: [{list}]         # for quick-fix
  reason: "{if skipped, why}"     # for skipped
```

**slack_url field:** Written after Step 5.4 Slack delivery. Contains the full Slack message URL for reaction collection on the next run (see Step 0.4.5). Value is `null` when Slack delivery fails or uses webhook fallback (no URL returned). This field is at the run-date level (not per-target) because one Slack message covers all targets.

### Step 5.2.5: Write summary.yaml (Dashboard Structured Output)

Write the complete structured run summary to `{run_dir}/summary.yaml` in the run directory. This file is read by the dashboard executor to populate RunSummary.per_target.

**The file MUST include the full per-target structure:**

```yaml
targets_active: {count}
targets_skipped: {count}
total_signals: {count}
total_actions: {count}
errors: {count}
per_target:
  {target-name}:
    monitors:
      {monitor-name}:
        status: ok | error
        signals: {count}
    pipeline:
      found: {n}
      after_dedup: {n}
      after_confidence_filter: {n}
      after_cooldown: {n}
      classified: { code-fix: n, proposal: n, ... }
      executed: { code-fix: n, proposal: n, ... }
    actions:
      - signal_id: "{id}"
        type: "{type}"
        summary: "{description}"
        pr_url: "{url}"  # if PR created
        branch: "{branch}"  # if branch created
        indicator: "{indicator-id}"
        assessment:
          closer_to_north_star: yes | no | uncertain
          confidence: high | medium | low
          reasoning: "{prose explanation}"
    indicator_baseline:
      {indicator-id}:
        value: {number}
        measurement: "{unit}"
        previous_value: {number}  # from last run, if available
        trend: improving | stable | degrading
    pre_assessment: "{strategy prose from Phase 3.5}"
    post_assessment: "{reflection prose from Phase 4.5}"
    implementation_outcomes: []
```

**Important:** Accumulate all per-target data throughout Phases 0.5 (indicator_baseline), 3.5 (pre_assessment), 4 (actions with assessment), and 4.5 (post_assessment) so this file can be written completely in Step 5.2.5.

### Step 5.3: Write Run Trace

Write structured execution metrics to `~/.claude/kc-plugins-config/nightwatch-runs.yaml`.

**Format:**

```yaml
runs:
  - date: {ISO 8601 timestamp}
    mode: {production | dry-run}
    duration_seconds: {elapsed time}
    targets:
      {target_name}:
        agents:
          {agent_name}: {status: ok | failed | empty, signals: N}
          # failed agents include: reason: "{error message}"
          # empty agents include: note: "{why empty}"
        pipeline:
          found: {total signals from all agents}
          after_dedup: {after cross-source dedup}
          after_confidence_filter: {after dropping low confidence}
          after_cooldown: {after cooldown check}
          classified:
            {action_type}: {count}
          executed:
            {action_type}: {count}
    skipped_targets:
      - {name: {target}, reason: {dirty | recent_commit | invalid_path}}
    summary:
      targets_active: {N}
      targets_skipped: {N}
      total_signals: {N}
      total_actions: {N}
      errors: {N}
```

**Rolling policy:** Keep last 10 runs. If file already has 10 entries, remove the oldest before appending.

**If file doesn't exist:** Create it with a single `runs:` list.

**Collect metrics throughout execution:** As each Phase completes, accumulate the metrics that will be written here. Do not wait until Phase 5 to start tracking — begin tracking at Phase 0 (skipped targets), continue through Phase 2 (agent results), Phase 3 (pipeline funnel), and Phase 4 (executed actions).

### Step 5.4: Slack Morning Report

**Channel resolution:**

1. Read `~/.claude/kc-plugins-config/channels.yaml` → look for `nightwatch` key
2. If `nightwatch` key exists → use that channel ID
3. If `nightwatch` key does NOT exist → **ask the user**:
   ```
   Nightwatch 晨報要發到哪個 Slack channel？
   請提供 channel 名稱（我會搜尋 ID）或直接貼 channel ID。
   輸入 "skip" 跳過 Slack 通知。
   ```
   - If user provides a channel → search with `slack_search_channels`, confirm with user, then save to `channels.yaml` under `nightwatch` key
   - If user says "skip" → skip Slack for this run, do NOT save (ask again next run)
4. If channel is archived or send fails → report the error, ask user for alternative channel

**Message format:**

```
🌙 kc-nightwatch 晨報 — {YYYY-MM-DD}

🔧 Auto-fixes ({count}):
• {target}: {summary} — {PR link or "local branch: {branch}"}

📋 Proposals ({count}):
• {target}: {summary} — {PR link or "local branch: {branch}"}

📝 Linear Issues ({count}):
• {target}: {summary} — {issue link}

🧪 E2E Flows ({count}):
• {target}: {summary} — {PR link or "local branch: {branch}"}

⚡ Alerts ({count}):
• {target}: {summary}

⏭️ Skipped: {count} signals ({reasons})

📊 Assessment (per active target):
• {target}: *Strategy:* {pre_assessment first sentence} | *Reflection:* {post_assessment first sentence}
• {target}: *Baselines:* {count} indicators — {improving_count} improving, {degrading_count} degrading
```

**Assessment section rules (ASSESS-04):**

After the per-target actions table, include a brief assessment summary per active target:

```
*Strategy:* {pre_assessment first sentence}
*Reflection:* {post_assessment first sentence}
*Baselines:* {count} indicators measured, {improving_count} improving, {degrading_count} degrading
```

If `pre_assessment` or `post_assessment` is empty, omit that line. If no baselines were measured for a target, omit the baselines line. If no targets produced assessment data, omit the entire Assessment section.

**Delivery strategy (try in order):**

1. **Slack MCP** — `slack_send_message` with channel ID. Preferred in interactive sessions.
2. **Webhook fallback** — if MCP unavailable or fails, check `channels.yaml` for `webhook` field:
   ```bash
   curl -s -X POST "$WEBHOOK_URL" \
     -H 'Content-type: application/json' \
     -d '{"text": "<message in mrkdwn format>"}'
   ```
3. **Log only** — if both fail, log `Slack delivery failed — report in improvement-log only` and continue.

**Capture Slack message URL for feedback collection:**

After successful Slack delivery (MCP or webhook):
1. If sent via `slack_send_message` MCP — the response includes the message URL or `ts` value. Construct the full URL: `https://{workspace}.slack.com/archives/{channel_id}/p{ts_without_dot}`
2. If sent via webhook — webhook responses do not return message metadata. Set `slack_url: null` (reaction collection will be skipped next run).
3. If delivery failed — set `slack_url: null`.

Store the `slack_url` value for use in Step 5.2 (improvement-log update).

**Silent night report** — when zero active targets (all skipped):

Send a concise report with per-target skip reasons:

```
🌙 kc-nightwatch — silent night ({YYYY-MM-DD})

全部 {N} 個 target 被跳過：
• {target}: {reason}
• {target}: {reason}
…
```

Where `{reason}` is the specific guard that triggered:
- `uncommitted changes` — `skip_if_dirty` guard (tracked files have modifications)
- `recent commit ({timestamp})` — human commit within `skip_if_recent_human_commit` window
- `uncommitted changes + recent commit` — both guards triggered
- `path not found` — target directory doesn't exist

This ensures the channel always reflects whether nightwatch ran, even when nothing was acted on.

**Rules:**
- Error notifications always sent regardless of change count
- In headless cron mode (no TTY): if no channel configured, skip Slack silently and log a warning
- Never fail the entire run due to Slack delivery issues

### Step 5.5: Final Cleanup

Ensure you are back on the `main` branch:
```bash
git checkout main
```

Report completion:
```
kc-nightwatch: run complete
  Targets scanned: {total}
  Targets active: {active}
  Forge fixes: {count}
  Quick-fixes: {count}
  Proposals: {count}
  Linear issues: {count}
  E2E flows: {count}
  Alerts: {count}
  Skipped signals: {count}
  Duration: {minutes}m
```

## Error Handling

If ANY phase throws an unhandled error:
1. Log the error with full context
2. If `global.slack_on_error` is true → send error notification to Slack channel
3. Ensure you return to the `main` branch
4. Write partial results to improvement-log.md (do not lose completed work)
5. Exit with error summary

## Anti-Rationalization Rules

<CRITICAL>
These are the most common rationalization patterns. If you catch yourself thinking any of these, STOP.

1. **"Just this one more file"** — The file limit is absolute. Period.
2. **"I'll stash and restore"** — skip-if-dirty means SKIP. No stashing.
3. **"This is clearly a quick-fix even though it adds a new step"** — New steps = proposal. Always.
4. **"The cooldown just expired yesterday, but the signal is urgent"** — Cooldown is non-negotiable. Wait.
5. **"I'll create the file since the fix obviously needs it"** — edit-only means NO create. Log and defer.
6. **"This proposal is so simple I'll just implement it directly"** — Proposals get PROPOSAL.md only. Human decides.
7. **"I should also improve this while I'm here"** — Stay scoped. Only act on classified signals.
8. **"This product signal needs a quick code fix"** — If target actions don't include `quick-fix`, you CANNOT make code changes. Use `linear-issue`, `alert`, or `e2e-flow` as available in the target's actions list.
9. **"I'll add implementation details to the Linear issue"** — Linear issues are investigation prompts, not instructions. Keep them descriptive, not prescriptive.
</CRITICAL>
