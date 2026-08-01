#!/usr/bin/env bash

set -euo pipefail

usage() {
  echo "Usage: post-release-sync.sh <plugin> [--repo <repository-root>]" >&2
}

PLUGIN="${1:-}"
if [[ -z "$PLUGIN" ]]; then
  usage
  exit 2
fi
shift

REPO_ROOT=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      REPO_ROOT="${2:-}"
      [[ -n "$REPO_ROOT" ]] || { usage; exit 2; }
      shift 2
      ;;
    *)
      usage
      exit 2
      ;;
  esac
done

if [[ ! "$PLUGIN" =~ ^[a-z0-9][a-z0-9-]*$ ]]; then
  echo "post-release sync: invalid plugin name '$PLUGIN'" >&2
  exit 2
fi

if [[ -z "$REPO_ROOT" ]]; then
  REPO_ROOT="$(git -C "$PWD" rev-parse --show-toplevel 2>/dev/null)" || {
    echo "post-release sync: run from the marketplace main workspace or pass --repo" >&2
    exit 2
  }
fi
REPO_ROOT="$(cd "$REPO_ROOT" && pwd)"

[[ -f "$REPO_ROOT/.claude-plugin/marketplace.json" ]] || {
  echo "post-release sync: $REPO_ROOT is not a marketplace repository" >&2
  exit 2
}

SOURCE="$REPO_ROOT/$PLUGIN"
[[ -f "$SOURCE/.claude-plugin/plugin.json" ]] || {
  echo "post-release sync: plugin '$PLUGIN' is not present under $REPO_ROOT" >&2
  exit 2
}

BRANCH="$(git -C "$REPO_ROOT" branch --show-current)"
if [[ "$BRANCH" != "main" ]]; then
  echo "post-release sync: source must be the main branch, found '${BRANCH:-detached}'" >&2
  exit 1
fi
if [[ -n "$(git -C "$REPO_ROOT" status --porcelain=v1)" ]]; then
  echo "post-release sync: source workspace must be clean" >&2
  exit 1
fi
if git -C "$REPO_ROOT" show-ref --verify --quiet refs/remotes/origin/main; then
  HEAD_SHA="$(git -C "$REPO_ROOT" rev-parse HEAD)"
  ORIGIN_SHA="$(git -C "$REPO_ROOT" rev-parse refs/remotes/origin/main)"
  if [[ "$HEAD_SHA" != "$ORIGIN_SHA" ]]; then
    echo "post-release sync: main must exactly match origin/main" >&2
    exit 1
  fi
fi

python3 - "$SOURCE/.claude-plugin/plugin.json" "$PLUGIN" <<'PY'
import json
import sys

path, expected = sys.argv[1:]
with open(path, encoding="utf-8") as handle:
    actual = json.load(handle).get("name")
if actual != expected:
    raise SystemExit(f"post-release sync: manifest names {actual!r}, expected {expected!r}")
PY

sync_destination() {
  local destination="$1"
  mkdir -p "$(dirname "$destination")" "$destination"
  rsync -a --delete --exclude '.git' "$SOURCE/" "$destination/"
  printf 'synced %s\n' "$destination"
}

CLAUDE_DESTINATION="$HOME/.claude/plugins/local/$PLUGIN"
CODEX_DESTINATION="$HOME/.codex/local-plugins/$PLUGIN"
for destination in "$CLAUDE_DESTINATION" "$CODEX_DESTINATION"; do
  if [[ -L "$destination" ]]; then
    echo "post-release sync: refusing to replace symlink $destination" >&2
    exit 1
  fi
done

sync_destination "$CLAUDE_DESTINATION"
sync_destination "$CODEX_DESTINATION"
