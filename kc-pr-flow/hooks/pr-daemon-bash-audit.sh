#!/bin/bash
# pr-daemon-bash-audit.sh
# Logs all Bash commands to audit file for later review.
# Only active when PR_DAEMON_AUDIT=1 (set by daemon script).
# Non-blocking — logs silently, never fails the tool call.

[ "$PR_DAEMON_AUDIT" != "1" ] && exit 0

AUDIT_DIR="$HOME/.claude/audit"
AUDIT_FILE="$AUDIT_DIR/pr-daemon-bash.log"
MAX_SIZE=1048576  # 1MB

mkdir -p "$AUDIT_DIR"

# Rotate if too large
if [ -f "$AUDIT_FILE" ] && [ "$(stat -f%z "$AUDIT_FILE" 2>/dev/null || stat -c%s "$AUDIT_FILE" 2>/dev/null)" -gt "$MAX_SIZE" ]; then
  mv "$AUDIT_FILE" "$AUDIT_FILE.old"
fi

cmd=$(echo "$CLAUDE_TOOL_INPUT" | jq -r '.command // empty' 2>/dev/null)
[ -z "$cmd" ] && exit 0

echo "{\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"cmd\":\"$(echo "$cmd" | head -c 500 | sed 's/"/\\"/g')\"}" >> "$AUDIT_FILE"
