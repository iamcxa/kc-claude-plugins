#!/bin/sh
# Launcher for the kc-hyperfocus context-lake MCP server.
#
# Why a launcher? macOS GUI applications (Claude Code Desktop, Conductor.app,
# any wrapper that inherits PATH from launchd rather than the user's shell rc)
# do not see `$HOME/.bun/bin` on PATH. Bun installed via the official installer
# lives there. Without this launcher, the plugin manifest's `"command": "bun"`
# would fail with ENOENT and the MCP server would never spawn — the plugin's
# skills would still load (they don't run bun), but `/mcp` would report
# "Failed to reconnect to plugin:kc-hyperfocus:context-lake".
#
# Pattern adopted from spacebridge's launch-mcp.sh.
#
# Plugin manifest invokes:
#   "command": "sh"
#   "args":    ["${CLAUDE_PLUGIN_ROOT}/scripts/launch-mcp.sh"]

set -e

# ─── Resolve real script path (handles symlinked plugin installs) ────────────
SCRIPT_PATH="$0"
while [ -L "$SCRIPT_PATH" ]; do
  LINK_TARGET="$(readlink "$SCRIPT_PATH")"
  case "$LINK_TARGET" in
    /*) SCRIPT_PATH="$LINK_TARGET" ;;
    *)  SCRIPT_PATH="$(dirname "$SCRIPT_PATH")/$LINK_TARGET" ;;
  esac
done

PLUGIN_DIR="$(cd "$(dirname "$SCRIPT_PATH")/.." && pwd)"

# ─── Augment PATH with common bun install locations ─────────────────────────
# Order matters: user-local first, Apple Silicon Homebrew next, Intel/Linux last.
export PATH="$HOME/.bun/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"

# ─── Verify bun is reachable ────────────────────────────────────────────────
if ! command -v bun >/dev/null 2>&1; then
  cat >&2 <<EOF
ERROR: kc-hyperfocus context-lake MCP server requires Bun, but it was not found.

Install Bun from https://bun.sh, then either:
  1. Restart your Claude Code app, OR
  2. Symlink Bun to a system path that GUI apps inherit:
       sudo ln -s "\$HOME/.bun/bin/bun" /usr/local/bin/bun

Locations checked: \$HOME/.bun/bin, /opt/homebrew/bin, /usr/local/bin, \$PATH
Current PATH: $PATH
EOF
  exit 127
fi

# ─── Hand off to the MCP server ─────────────────────────────────────────────
exec bun "$PLUGIN_DIR/server/context-lake-mcp.ts"
