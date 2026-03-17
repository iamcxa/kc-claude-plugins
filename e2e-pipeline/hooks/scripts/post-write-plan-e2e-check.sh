#!/bin/bash
set -euo pipefail

# PostToolUse hook: warn when a plan file is written without E2E verification steps
# Fires on Write tool — checks if the written file is a plan in a project with E2E mappings
input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty')

# No file path → not a Write call we care about
if [ -z "$file_path" ]; then
  exit 0
fi

# Match plan file patterns across frameworks:
#   superpowers: docs/superpowers/plans/*-plan.md, docs/superpowers/specs/*-design.md
#   GSD: .planning/phases/*/PLAN.md
#   plan mode / manual: *plan*.md, *PLAN*.md
basename=$(basename "$file_path")
dirpath=$(dirname "$file_path")

is_plan=false
case "$basename" in
  PLAN.md|plan.md) is_plan=true ;;
  *-plan.md|*-plan-*.md) is_plan=true ;;
esac

# Also check directory patterns
case "$dirpath" in
  */docs/superpowers/plans*|*/docs/superpowers/specs*) is_plan=true ;;
  */.planning/phases/*) is_plan=true ;;
esac

if [ "$is_plan" = false ]; then
  exit 0
fi

# Find project root — walk up from file_path looking for .claude/ or .git/
check_dir=$(dirname "$file_path")
project_dir=""
while [ "$check_dir" != "/" ]; do
  if [ -d "$check_dir/.claude" ] || [ -d "$check_dir/.git" ]; then
    project_dir="$check_dir"
    break
  fi
  check_dir=$(dirname "$check_dir")
done

if [ -z "$project_dir" ]; then
  exit 0
fi

# Check if project has E2E mappings
mapping_dir="$project_dir/.claude/e2e/mappings"
if [ ! -d "$mapping_dir" ] || ! ls "$mapping_dir"/*.yaml &>/dev/null 2>&1; then
  exit 0
fi

# Check if the plan file mentions E2E verification
if grep -qiE '/e2e-flow|/e2e-test|e2e.verif|e2e.valid|e2e.acceptance' "$file_path" 2>/dev/null; then
  exit 0
fi

# Plan exists in E2E-enabled project but has no E2E steps
mapping_count=$(ls "$mapping_dir"/*.yaml 2>/dev/null | wc -l | tr -d ' ')
jq -n --arg count "$mapping_count" \
  '{"systemMessage": ("⚠ This plan is in a project with E2E infrastructure (" + $count + " mapping(s)) but does not include E2E verification steps. Per E2E-First rules: add /e2e-flow to generate flows from acceptance criteria, and /e2e-test as the final verification task. Skip only if changes are backend-only with no browser-visible impact.")}'

exit 0
