---
name: kc-pr-daemon
description: "Use when user says 'start daemon', 'stop daemon', 'daemon status', 'pr daemon', 'daemon config', 'daemon 掛了', 'daemon error', '啟動 daemon', '停止 daemon', 'daemon 狀態', or wants to manage, configure, or troubleshoot the PR review closed-loop daemon."
argument-hint: "[start | stop | status | config]"
---

All text output follows unified language preference. See plugin CLAUDE.md for query flow.

## Overview

Manage the PR Review Closed-Loop Daemon — an external shell loop that automatically reviews and fixes PRs using `claude -p`.

**Config**: `~/.claude/kc-plugins-config/pr-flow/daemon.yaml`
**Script**: `${CLAUDE_PLUGIN_ROOT}/scripts/pr-review-daemon.sh`
**Usage log**: `~/.claude/audit/pr-daemon-usage.jsonl`

## Default (no subcommand)

When invoked without a subcommand (`/kc-pr-daemon`, `pr daemon`, `daemon`), show overview + status + next step:

```
PR Review Daemon
────────────────
Commands:
  /kc-pr-daemon start   — start daemon (mprocs or direct)
  /kc-pr-daemon stop    — stop daemon
  /kc-pr-daemon status  — usage stats (cost, iterations, last action)
  /kc-pr-daemon config  — view/edit settings

{status block — run the `status` bash snippet below}

Suggested next step:
  {if no usage log} → /kc-pr-daemon config — set up config first
  {if last run > 24h ago} → /kc-pr-daemon start — daemon not running
  {if last action was STUCK} → Check PR #{N} — daemon flagged it as stuck
  {if running normally} → /kc-pr-daemon status — view detailed stats
```

## Commands

### start

**Option A — via project wrapper** (recommended for teams):

Projects can ship a thin wrapper at `.claude/scripts/pr-review-daemon.sh` that reads `plugin_dir` from `daemon.yaml` and `exec`s the plugin script. This keeps `mprocs.yaml` portable:

```yaml
# mprocs.yaml (checked into repo — no user-specific paths)
pr-daemon:
  cmd: ["bash", ".claude/scripts/pr-review-daemon.sh"]
  autostart: false
  env:
    POLL_INTERVAL: "300"
```

Each user sets their plugin path in config:

```yaml
# ~/.claude/kc-plugins-config/pr-flow/daemon.yaml
plugin_dir: /path/to/kc-pr-flow
```

**Option B — direct** (personal use):

```bash
cd <project-root>
bash ${CLAUDE_PLUGIN_ROOT}/scripts/pr-review-daemon.sh
```

Tell the user the plugin path: `Read ${CLAUDE_PLUGIN_ROOT}/scripts/pr-review-daemon.sh` to get the absolute path.

### stop

If running in mprocs: instruct user to press `s` on the pr-daemon process.
If running in terminal: `Ctrl+C`.

### status

Show daemon status from the usage log:

```bash
USAGE_LOG="$HOME/.claude/audit/pr-daemon-usage.jsonl"
if [[ -s "$USAGE_LOG" ]]; then
  echo "=== PR Daemon Usage ==="
  jq -rs '{
    total_iterations: length,
    total_cost: ([.[].cost] | add | . * 10000 | round / 10000),
    this_month: ([.[] | select(.ts[:7] == (now | strftime("%Y-%m")))] | {
      iterations: length,
      cost: ([.[].cost] | add | . * 10000 | round / 10000)
    }),
    last_action: (last | {ts, action, cost}),
    actions_taken: ([.[] | select(.action != "" and .action != "Action taken: NONE (all skipped)")] | length)
  }' < "$USAGE_LOG"
else
  echo "No usage data yet. Daemon has not run."
fi
```

Monthly cost breakdown:

```bash
jq -s 'group_by(.ts[:7]) | .[] | {month: .[0].ts[:7], cost: ([.[].cost] | add | . * 100 | round / 100), iters: length}' ~/.claude/audit/pr-daemon-usage.jsonl
```

### config

Read and display current config:

```bash
cat ~/.claude/kc-plugins-config/pr-flow/daemon.yaml
```

Full YAML schema with defaults:

```yaml
plugin_dir: ""            # absolute path to kc-pr-flow plugin (required for wrapper)
poll_interval: 300        # seconds between iterations (default: 5 min)
model: sonnet             # claude -p model (subagents inherit)
max_turns: 30             # pipe-mode safety valve
ci_gate_context: ci-gate  # commit status context ("none" to skip check)
commit_scope: review      # → fix(review): <description>
slack_webhook: ""         # Slack incoming webhook URL (empty = disabled)
gate_script: ""           # custom pre-flight gate script path (exit 0 = go, 1 = skip)
```

Environment variable overrides (take precedence over YAML):

| Env Var | Overrides | Example |
|---------|-----------|---------|
| `POLL_INTERVAL` | `poll_interval` | `POLL_INTERVAL=600` (10 min) |
| `PR_DAEMON_SLACK_WEBHOOK` | `slack_webhook` | Slack incoming webhook URL |
| `PR_DAEMON_GATE` | `gate_script` | Path to custom gate script |

To modify: edit `~/.claude/kc-plugins-config/pr-flow/daemon.yaml` directly. Changes take effect on next iteration (no restart needed — script re-reads config each loop).

First-time setup (if config directory doesn't exist):

```bash
mkdir -p ~/.claude/kc-plugins-config/pr-flow
cat > ~/.claude/kc-plugins-config/pr-flow/daemon.yaml << 'EOF'
poll_interval: 300
model: sonnet
max_turns: 30
ci_gate_context: ci-gate
commit_scope: review
slack_webhook: ""
gate_script: ""
EOF
```

## Troubleshooting

The daemon runs preflight checks on startup. Common errors:

| Error | Cause | Fix |
|-------|-------|-----|
| `ERROR: claude CLI not found in PATH` | Non-interactive shell PATH missing claude | Add full path: `export PATH="$HOME/.claude/bin:$PATH"` in script or mprocs env |
| `ERROR: gh CLI not found in PATH` | Same PATH issue for gh | `which gh` in interactive shell → add that directory to daemon PATH |
| `ERROR: Prompt file not found` | Plugin directory moved or broken symlink | Re-check `--plugin-dir` path or reinstall plugin |
| Daemon exits immediately | `set -euo pipefail` + unhandled error | Check stderr output; common: `yq` not installed (non-fatal, falls back to defaults) |
| `⏭️ No open non-draft PRs` every iteration | No actionable PRs or wrong repo | Verify `cd <project-root>` before starting; check `gh pr list` in that directory |
| `claude -p exited with code 1` | API error, rate limit, or max-turns exceeded | Check Claude API status; reduce `max_turns` if context overflows |
| Slack notification not arriving | Webhook URL misconfigured | Test: `curl -s -X POST "$WEBHOOK" -H 'Content-Type: application/json' -d '{"text":"test"}'` |

**Daemon always set** (not configurable): `PR_DAEMON_MODE=1` (bypasses SessionStart superpowers hook) and `PR_DAEMON_AUDIT=1` (enables Bash command audit logging via PostToolUse hook).

## Prerequisites

- `claude` CLI in PATH
- `gh` CLI authenticated
- `yq` for YAML parsing (optional — falls back to defaults without it)
- `terminal-notifier` for click-to-open macOS notifications (optional — falls back to `osascript`)
- `jq` for JSON processing

## Architecture

```
mprocs / terminal
└── pr-review-daemon.sh (shell while-loop)
    ├── Pre-flight gate (gh pr list + ci-gate check)
    └── claude -p (fresh Sonnet session per iteration)
        ├── Classify PRs (SKIP / STUCK / REVIEW / FIX)
        ├── REVIEW → Skill("kc-pr-flow:kc-pr-review")
        └── FIX → Skill("kc-pr-flow:kc-pr-review-resolve")
```

Each iteration is stateless. GitHub API is the single source of truth.
