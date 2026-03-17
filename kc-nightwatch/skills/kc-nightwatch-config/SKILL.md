---
name: kc-nightwatch-config
description: Use when setting up, configuring, or managing kc-nightwatch scheduling and settings. Triggered by '/kc-nightwatch-config', or when user asks to schedule nightwatch, change cron time, configure Slack channel, or check what plugins are monitored.
---

# kc-nightwatch Config

Manage nightwatch schedule, Slack channel, and monitored plugins.

## Arguments

- `/kc-nightwatch-config` — **overview**: show current config status
- `/kc-nightwatch-config schedule` — manage cron schedule
- `/kc-nightwatch-config channel` — configure Slack notification channel
- `/kc-nightwatch-config plugins` — view and manage monitored plugins

Route to the appropriate section below.

---

## Bootstrap (auto, runs before any mode)

Check if config directory and files exist. If not, create them:

```bash
mkdir -p ~/.claude/kc-plugins-config
```

**If `nightwatch-targets.yaml` does not exist:**

Create a starter file with one commented-out example:

```yaml
# kc-nightwatch monitoring targets
# See README.md for field documentation
#
# Example:
#   my-plugin:
#     type: plugin
#     path: ~/Project/my-workspace/my-plugin
#     repo: my-plugins
#     north_star: "My plugin works perfectly"
#     keywords: [my-plugin, feature-x]
#     sources: [journal, episodic-memory, memory-md]
#     actions: [quick-fix, proposal]
#     proxy_signals:
#       - id: quality
#         description: "Plugin quality metric"
#         target: "100%"

targets: {}
```

Log: `[BOOTSTRAP] Created nightwatch-targets.yaml — add targets with /kc-nightwatch-config plugins`

**If `nightwatch-improvement-log.md` does not exist:**

Create with initial frontmatter:

```markdown
---
last_run: null
runs: 0
---
```

**If `channels.yaml` does not exist:** Create empty file. Channel will be asked on first run.

**If `language.yaml` does not exist:** Create with default:

```yaml
default: en
overrides: []
```

---

## Overview (no args)

Show current configuration at a glance:

### Step 1: Gather Status

```bash
# launchd status
launchctl list 2>/dev/null | grep com.kc.nightwatch

# Installed plist
ls -la ~/Library/LaunchAgents/com.kc.nightwatch.plist 2>/dev/null

# Wrapper script
ls -la ~/.claude/scripts/nightwatch-cron.sh 2>/dev/null
```

Read:
- `~/.claude/kc-plugins-config/channels.yaml` → `nightwatch` key
- `~/.claude/kc-plugins-config/nightwatch-targets.yaml` → target count + types
- `~/.claude/kc-plugins-config/nightwatch-improvement-log.md` (from kc-nightwatch plugin dir) → last run + total runs

### Step 2: Display

```
🌙 kc-nightwatch Config

Schedule:   {HH:MM daily} (launchd) | NOT INSTALLED
Slack:      #{channel_name} ({channel_id}) | NOT CONFIGURED
Targets:    {plugin_count} plugins, {product_count} products ({total} total)
Last run:   {date} (run #{number}) | Never

Use:
  /kc-nightwatch-config schedule   — install/change/remove schedule
  /kc-nightwatch-config channel    — set Slack channel
  /kc-nightwatch-config plugins    — view/add monitoring targets
```

---

## Schedule Mode (`schedule`)

Uses **launchd** (macOS native scheduler). Templates live in `config/` within the plugin source.

- Plist template: `config/com.kc.nightwatch.plist` (placeholders: `__HOME__`, `__HOUR__`, `__MINUTE__`)
- Script template: `config/nightwatch-cron.sh` (uses `~/.claude/plugins/local/` paths, no workspace placeholder needed)

### Step S1: Check Current State

```bash
launchctl list 2>/dev/null | grep com.kc.nightwatch
ls ~/Library/LaunchAgents/com.kc.nightwatch.plist 2>/dev/null
```

- If launchd job exists → show current schedule (read Hour/Minute from installed plist), ask what to do
- If not installed → offer to install

### Step S2: Choose Action

```
Current schedule: {HH:MM daily (launchd)} or "not installed"

[I]nstall  — set up nightly schedule (default: 3:00 AM)
[C]hange   — update schedule time
[R]emove   — uninstall schedule
[S]tatus   — just show current state (done)
```

Wait for user input.

### Step S3: Install / Change

Ask user for preferred time:

```
幾點執行 nightwatch？(default: 03:00)
格式：HH:MM (24hr)
```

Parse input:
- `03:00` or `3:00` → Hour=3, Minute=0
- `04:30` → Hour=4, Minute=30
- Empty/enter → default Hour=3, Minute=0

### Step S4: Install Wrapper Script (from template)

Copy template from plugin source to install location (no placeholder replacement needed — script uses `~/.claude/plugins/local/` paths):

```bash
PLUGIN_SRC="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}"
```

1. Copy `config/nightwatch-cron.sh` from plugin source to `~/.claude/scripts/nightwatch-cron.sh`
2. `chmod +x ~/.claude/scripts/nightwatch-cron.sh`

Skip if installed script is already up-to-date (compare content).

### Step S5: Install Plist (from template)

1. Read `config/com.kc.nightwatch.plist` from plugin source
2. Replace placeholders:
   - `__HOME__` → `$HOME` (e.g., `/Users/kent`)
   - `__HOUR__` → parsed hour (integer)
   - `__MINUTE__` → parsed minute (integer)
3. Write to `~/Library/LaunchAgents/com.kc.nightwatch.plist`

**If changing (job already loaded):**
```bash
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.kc.nightwatch.plist 2>/dev/null
```

**Load the job:**
```bash
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.kc.nightwatch.plist
```

### Step S6: Verify

```bash
launchctl list | grep com.kc.nightwatch
```

Display:
```
✅ Schedule installed: {HH:MM} daily (launchd)
   Plist:  ~/Library/LaunchAgents/com.kc.nightwatch.plist
   Script: ~/.claude/scripts/nightwatch-cron.sh
   Log:    /tmp/kc-nightwatch.log

launchd will run missed jobs when Mac wakes from sleep.
```

### Step S7: Remove

```bash
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.kc.nightwatch.plist 2>/dev/null
rm ~/Library/LaunchAgents/com.kc.nightwatch.plist
```

Verify: `launchctl list | grep com.kc.nightwatch` should return nothing.

```
✅ Schedule removed. Nightwatch will no longer run automatically.
   Manual run: /kc-nightwatch
   Script preserved: ~/.claude/scripts/nightwatch-cron.sh
```

---

## Channel Mode (`channel`)

### Step C1: Check Current

Read `~/.claude/kc-plugins-config/channels.yaml` → `nightwatch` key.

- If exists → show current channel, ask if want to change
- If not exists → ask which channel to use

### Step C2: Ask User

```
Nightwatch 晨報要發到哪個 Slack channel？
輸入 channel 名稱（我會搜尋 ID）或直接貼 channel ID：
```

### Step C3: Search and Confirm

Use `slack_search_channels` with user's input. Present matches:

```
找到以下 channels：

1. #my-team (C0XXXXXXXXX)
2. #my-team-pr (C0YYYYYYYYY)

哪一個？(1/2)
```

### Step C4: Save

Update `~/.claude/kc-plugins-config/channels.yaml`:

```yaml
  nightwatch:
    id: "{channel_id}"    # {channel_name}; set via /kc-nightwatch-config {date}
    defaults:
      tone: internal
      lang: zh-TW
      mention: ""
```

### Step C5: Test Send

Ask user:
```
要發一則測試訊息確認嗎？[Y/n]
```

If yes → send a brief test message:
```
🌙 kc-nightwatch 測試 — channel 配置完成 ✅
```

---

## Targets Mode (`plugins`)

### Step P1: Read Targets

Read `~/.claude/kc-plugins-config/nightwatch-targets.yaml`.

### Step P2: Display

```
🌙 Monitoring Targets ({count})

| Target | Type | Repo | North Star | Actions |
|--------|------|------|------------|---------|
| {name} | {type} | {repo} | {north_star (truncated to 50 chars)} | {actions} |
| ...    | ...  | ... | ... | ... |

# Commented-out targets are disabled templates
```

### Step P3: Offer Actions

```
[A]dd    — add a new target to monitoring
[V]iew   — view full north star + proxy signals for a target
[E]nable — uncomment a commented-out target
[D]one   — exit
```

**Add flow:**
1. Ask: plugin or product?
2. For `plugin` — ask for plugin name (e.g., `kc-pr-flow`). Path is auto-resolved at runtime from `~/.claude/plugins/local/` or `$KC_WORKSPACE`. Optionally ask for explicit `path` override.
3. For `product` — ask for target path (required); verify it's a git repo; ask for `linear_team`, `linear_project`, `sentry_org`, `sentry_projects` (optional)
4. Ask for north star goal (one sentence)
5. Ask for 2-3 keywords
6. Ask for 1-2 proxy signals (id + description)
7. Set sources and actions based on type:
   - `plugin`: sources `[journal, episodic-memory, memory-md]`, actions `[quick-fix, proposal]`
   - `product`: sources `[journal, episodic-memory, memory-md]`, actions `[proposal, linear-issue]`
10. Append to `~/.claude/kc-plugins-config/nightwatch-targets.yaml`
11. Suggest: "Run `/kc-nightwatch --dry-run` to verify the new target is picked up"

**Enable flow:**
1. List commented-out targets in the YAML file
2. User selects one
3. Uncomment the target block
4. Suggest dry run

**View flow:**
1. Show full entry from nightwatch-targets.yaml for selected target
2. Show improvement-log entries for that target (if any)
