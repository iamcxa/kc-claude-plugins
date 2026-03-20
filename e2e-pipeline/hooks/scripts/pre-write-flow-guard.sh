#!/bin/bash
set -euo pipefail

# PreToolUse hook: block direct writes to flow YAML unless authorized by /e2e-flow sentinel
# Fires on Write tool — only matches .claude/e2e/flows/*.yaml
input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty')

if [ -z "$file_path" ]; then
  exit 0
fi

# Only match .claude/e2e/flows/*.yaml
case "$file_path" in
  */.claude/e2e/flows/*.yaml) ;;
  *) exit 0 ;;
esac

# Derive sentinel path from flow file path
# .claude/e2e/flows/foo.yaml → .claude/e2e/.flow-write-authorized
flows_dir=$(dirname "$file_path")
e2e_dir=$(dirname "$flows_dir")
sentinel="$e2e_dir/.flow-write-authorized"

# Check for authorization sentinel
if [ -f "$sentinel" ]; then
  # Staleness check: reject if older than 10 minutes (600 seconds)
  if [ "$(uname)" = "Darwin" ]; then
    file_mtime=$(stat -f %m "$sentinel")
  else
    file_mtime=$(stat -c %Y "$sentinel")
  fi
  age=$(( $(date +%s) - file_mtime ))
  if [ "$age" -lt 600 ]; then
    exit 0
  fi
fi

# No valid sentinel → block
jq -n '{
  "decision": "block",
  "reason": "Flow YAML must be generated via /e2e-flow (or /e2e-flow --no-verify). Hand-writing bypasses codebase analysis, mapping validation, and external checkpoint detection. Use: /e2e-flow <description> or /e2e-flow --from <plan>"
}'
