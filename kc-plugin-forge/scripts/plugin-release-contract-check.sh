#!/usr/bin/env bash

set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_ROOT="$(cd "$HERE/.." && pwd)"
REPO_ROOT=""

if [[ "${1:-}" == "--repo" ]]; then
  REPO_ROOT="${2:-}"
  if [[ -z "$REPO_ROOT" ]]; then
    echo "plugin release contract: --repo requires a path" >&2
    exit 2
  fi
fi

fail() {
  printf 'plugin release contract: %s\n' "$1" >&2
  exit 1
}

for relative in \
  "skills/kc-plugin-release/SKILL.md" \
  "scripts/post-release-sync.sh" \
  "scripts/watch-pr-checks.sh"; do
  [[ -f "$PLUGIN_ROOT/$relative" ]] || fail "missing $relative"
done

PACKAGE_INSTRUCTIONS=(
  "$PLUGIN_ROOT/skills/kc-plugin-release/SKILL.md"
  "$PLUGIN_ROOT/README.md"
  "$PLUGIN_ROOT/CLAUDE.md"
  "$PLUGIN_ROOT/docs/commands.md"
  "$PLUGIN_ROOT/docs/architecture.md"
)

if grep -nE 'kc-marketplace-sync|kc-Codex|\.Codex' "${PACKAGE_INSTRUCTIONS[@]}" >/dev/null; then
  fail "obsolete helper or path found in maintained instructions"
fi

if grep -nE 'git[[:space:]]+tag|plugin\.json.*version|marketplace\.json.*version' \
  "$PLUGIN_ROOT/skills/kc-plugin-release/SKILL.md" \
  "$PLUGIN_ROOT/scripts/post-release-sync.sh" >/dev/null; then
  fail "release mutation escaped the release-please authority boundary"
fi

if [[ -n "$REPO_ROOT" ]]; then
  REPO_ROOT="$(cd "$REPO_ROOT" && pwd)"
  REPO_INSTRUCTIONS=(
    "$REPO_ROOT/CLAUDE.md"
    "$REPO_ROOT/e2e-pipeline/CLAUDE.md"
    "$REPO_ROOT/kc-plugin-forge/CLAUDE.md"
    "$REPO_ROOT/kc-plugin-forge/README.md"
    "$REPO_ROOT/kc-plugin-forge/docs/commands.md"
    "$REPO_ROOT/kc-plugin-forge/docs/architecture.md"
    "$REPO_ROOT/kc-plugin-forge/skills/kc-plugin-forge-sanitize-check/SKILL.md"
    "$REPO_ROOT/kc-plugin-forge/skills/kc-plugin-release/SKILL.md"
  )
  for instruction in "${REPO_INSTRUCTIONS[@]}"; do
    [[ -f "$instruction" ]] || fail "missing maintained instruction ${instruction#"$REPO_ROOT"/}"
  done
  if grep -nE 'kc-marketplace-sync|kc-Codex|\.Codex' "${REPO_INSTRUCTIONS[@]}" >/dev/null; then
    fail "obsolete helper or path found in maintained instructions"
  fi
fi

echo "plugin release contract: PASS"
