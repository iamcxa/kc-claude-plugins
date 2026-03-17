#!/bin/bash
# kc-nightwatch cron wrapper
# Template source: kc-nightwatch/config/nightwatch-cron.sh
# Installed to: ~/.claude/scripts/nightwatch-cron.sh
# Scheduler: launchd (~/Library/LaunchAgents/com.kc.nightwatch.plist)
#
# launchd's StartCalendarInterval will run missed jobs on wake.
#
# Plugins are loaded from ~/.claude/plugins/local/ (layout-independent).
# To add optional plugins, append --plugin-dir lines below.

# TODO: Option B — pmset wake + AC power guard
# Install scheduled wake: pmset repeat wake MTWRFSU 02:58:00
# Then uncomment the guard below to skip execution on battery:
#
# if ! pmset -g ps | grep -q "AC Power"; then
#   echo "$(date): skipped — on battery" >> /tmp/kc-nightwatch.log
#   exit 0
# fi

LOG=/tmp/kc-nightwatch.log
echo "$(date): nightwatch started" >> "$LOG"

PLUGINS="$HOME/.claude/plugins/local"
SUPERPOWERS=~/.claude/plugins/cache/superpowers-marketplace/superpowers

# Find latest superpowers version (only marketplace plugin needed)
SP_DIR=$(ls -d "$SUPERPOWERS"/*/ 2>/dev/null | sort -V | tail -1)

if [ -z "$SP_DIR" ]; then
  echo "$(date): ERROR — superpowers not found in marketplace cache" >> "$LOG"
  exit 1
fi

# Build optional plugin-dir flags (skip if not installed)
FORGE_FLAG=""
E2E_FLAG=""
[ -d "$PLUGINS/kc-plugin-forge" ] && FORGE_FLAG="--plugin-dir $PLUGINS/kc-plugin-forge"
[ -d "$PLUGINS/e2e-pipeline" ] && E2E_FLAG="--plugin-dir $PLUGINS/e2e-pipeline"

# --- Session 1: Self-repair (config validation + feedback) ---
echo "$(date): self-repair started" >> "$LOG"

timeout 600 claude -p "/kc-nightwatch --self-repair" \
  --dangerously-skip-permissions \
  --plugin-dir "$SP_DIR" \
  $FORGE_FLAG \
  --plugin-dir "$PLUGINS/kc-nightwatch" \
  >> "$LOG" 2>&1

echo "$(date): self-repair finished (exit $?)" >> "$LOG"

# --- Session 2: Regular pipeline (all targets) ---
echo "$(date): pipeline started" >> "$LOG"

timeout 1800 claude -p "/kc-nightwatch" \
  --dangerously-skip-permissions \
  --plugin-dir "$SP_DIR" \
  $E2E_FLAG \
  $FORGE_FLAG \
  --plugin-dir "$PLUGINS/kc-nightwatch" \
  >> "$LOG" 2>&1

echo "$(date): pipeline finished (exit $?)" >> "$LOG"
