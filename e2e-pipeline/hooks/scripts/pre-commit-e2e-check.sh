#!/bin/bash
set -euo pipefail

# PreToolUse hook: warn on git commit if E2E verification is missing
input=$(cat)
command=$(echo "$input" | jq -r '.tool_input.command // empty')

# Only intercept git commit
if [[ ! "$command" =~ git[[:space:]]+commit ]]; then
  exit 0
fi

project_dir="${CLAUDE_PROJECT_DIR:-$(echo "$input" | jq -r '.cwd // "."')}"

# Check if project has E2E mappings
mapping_dir="$project_dir/.claude/e2e/mappings"
if [ ! -d "$mapping_dir" ] || ! ls "$mapping_dir"/*.yaml &>/dev/null; then
  exit 0
fi

flow_dir="$project_dir/.claude/e2e/flows"
report_dir="$project_dir/e2e-reports"

# Check 1: Any flows exist?
flow_count=0
if [ -d "$flow_dir" ]; then
  flow_count=$(ls "$flow_dir"/*.yaml 2>/dev/null | wc -l | tr -d ' ')
fi

if [ "$flow_count" -eq 0 ]; then
  jq -n '{"systemMessage": "⚠ E2E mappings exist but no flow files in .claude/e2e/flows/. If this commit includes UI changes, consider running /e2e-flow to generate flows first."}'
  exit 0
fi

# Check 2: Recent test reports? (within last 2 hours)
recent_report=""
if [ -d "$report_dir" ]; then
  recent_report=$(find "$report_dir" -name "report.md" -mmin -120 2>/dev/null | head -1)
fi

if [ -z "$recent_report" ]; then
  jq -n '{"systemMessage": "⚠ E2E flows exist but no recent test report found. Consider running /e2e-test before finalizing this commit."}'
fi

exit 0
