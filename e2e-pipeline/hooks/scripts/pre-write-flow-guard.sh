#!/bin/bash
set -euo pipefail

# PreToolUse hook: warn when flow YAML is written directly instead of via /e2e-flow
# Fires on Write tool — detects hand-writing of flow files
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

jq -n '{"systemMessage": "⚠ Direct flow YAML write detected. If you are the e2e-flow-writer agent, ignore this — you are the authorized generator. Otherwise: flow YAML should be generated via /e2e-flow (or /e2e-flow --no-verify to skip browser verification), not hand-written. Hand-written flows bypass codebase analysis, mapping validation, and external checkpoint detection."}'

exit 0
