#!/bin/bash
set -euo pipefail

# SessionStart hook: detect E2E infrastructure and inject planning reminder
input=$(cat)
project_dir="${CLAUDE_PROJECT_DIR:-$(echo "$input" | jq -r '.cwd // "."')}"

mapping_dir="$project_dir/.claude/e2e/mappings"
if [ ! -d "$mapping_dir" ] || ! ls "$mapping_dir"/*.yaml &>/dev/null; then
  exit 0
fi

mapping_count=$(ls "$mapping_dir"/*.yaml 2>/dev/null | wc -l | tr -d ' ')
flow_dir="$project_dir/.claude/e2e/flows"
flow_count=0
if [ -d "$flow_dir" ]; then
  flow_count=$(ls "$flow_dir"/*.yaml 2>/dev/null | wc -l | tr -d ' ')
fi

jq -n --arg msg "E2E infrastructure detected (${mapping_count} mapping(s), ${flow_count} flow(s)). When planning or implementing UI-facing features: include draft E2E flow YAMLs as acceptance criteria, use /e2e-acceptance to generate from plans, and run /e2e-test before finalizing." \
  '{"systemMessage": $msg}'
