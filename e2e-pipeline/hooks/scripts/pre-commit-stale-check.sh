#!/bin/bash
set -euo pipefail

# PreToolUse hook: warn on git commit if compiled E2E scripts are stale
# A compiled script is stale when its source flow/mapping YAML files have changed
# since the last compilation. Warning only — never blocks the commit.

input=$(cat)
command=$(echo "$input" | jq -r '.tool_input.command // empty')

# Only intercept git commit
if [[ ! "$command" =~ git[[:space:]]+commit ]]; then
  exit 0
fi

project_dir="${CLAUDE_PROJECT_DIR:-$(echo "$input" | jq -r '.cwd // "."')}"

# Guard: check if compiled directory exists and has .sh files
compiled_dir="$project_dir/.claude/e2e/compiled"
if [ ! -d "$compiled_dir" ] || ! ls "$compiled_dir"/*.sh &>/dev/null; then
  exit 0
fi

# Cross-platform sha256: prefer sha256sum (Linux), fall back to shasum (macOS)
sha256() {
  if command -v sha256sum &>/dev/null; then
    sha256sum | awk '{print $1}'
  else
    shasum -a 256 | awk '{print $1}'
  fi
}

stale=()

for script in "$compiled_dir"/*.sh; do
  # Extract stored hash from header
  stored_hash=$(grep "^# SHA-256:" "$script" 2>/dev/null | sed 's/^# SHA-256: //' || true)
  # Extract source flow path (relative to project root)
  flow_path=$(grep "^# Source:" "$script" 2>/dev/null | sed 's/^# Source: //' || true)

  # Guard: malformed header — skip this script
  if [ -z "$stored_hash" ] || [ -z "$flow_path" ]; then
    continue
  fi

  # Guard: source file no longer exists — not a staleness issue, skip
  if [ ! -f "$project_dir/$flow_path" ]; then
    continue
  fi

  # Extract ALL mapping paths (cross-site flows have multiple # Mapping: lines)
  # Use while-read instead of mapfile for bash 3.x compatibility (macOS)
  mapping_paths=()
  while IFS= read -r mp; do
    mapping_paths+=("$mp")
  done < <(grep "^# Mapping:" "$script" 2>/dev/null | sed 's/^# Mapping: //' || true)

  # Guard: any mapping file missing — skip
  all_mappings_exist=true
  for mp in "${mapping_paths[@]}"; do
    if [ ! -f "$project_dir/$mp" ]; then
      all_mappings_exist=false
      break
    fi
  done
  if [ "$all_mappings_exist" = false ]; then
    continue
  fi

  # Recompute hash using the same algorithm as compiler.js hashSources():
  # cat flow mapping1 mapping2 | sha256 — no separators, matches JS hash.update() chaining
  # Prepend $project_dir/ to convert relative header paths to absolute paths
  abs_mapping_paths=()
  for mp in "${mapping_paths[@]}"; do
    abs_mapping_paths+=("$project_dir/$mp")
  done

  current_hash=$(cat "$project_dir/$flow_path" "${abs_mapping_paths[@]}" | sha256)

  if [ "$stored_hash" != "$current_hash" ]; then
    stale+=("$(basename "$script")")
  fi
done

# Emit warning if any stale scripts found
if [ ${#stale[@]} -gt 0 ]; then
  stale_list=$(printf ", %s" "${stale[@]}")
  stale_list=${stale_list:2}  # remove leading ", "
  jq -n --arg msg "WARNING: stale compiled scripts detected: $stale_list. Source files have changed since last compilation. Run /e2e-compile --all to update." \
    '{"systemMessage": $msg}'
fi

exit 0  # Always exit 0 — warning only, never block
