#!/bin/bash
# Install the PR review listener into the menu bar. Idempotent: safe to re-run on
# a new machine, after a SwiftBar reinstall, or to change the backend.
#
#   reviewer-listen-install.sh [--backend conductor|<name>] [--notify swiftbar|osascript]

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LISTENER="$SCRIPT_DIR/pr-reviewer-listen.sh"
CFG_DIR="${PR_LISTEN_CFG_DIR:-$HOME/.claude/kc-plugins-config/pr-flow}"
CONFIG="$CFG_DIR/reviewer-listen.config.json"
STATE="$CFG_DIR/reviewer-listen.state.json"
LEGACY="$CFG_DIR/reviewer-listen.json"

BACKEND=conductor
NOTIFY=swiftbar
while [[ $# -gt 0 ]]; do
  case "$1" in
    --backend) BACKEND="${2:?}"; shift 2 ;;
    --notify)  NOTIFY="${2:?}";  shift 2 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

say()  { printf '%s\n' "$*"; }
warn() { printf 'WARN  %s\n' "$*" >&2; }
die()  { printf 'ERROR %s\n' "$*" >&2; exit 1; }

command -v jq >/dev/null 2>&1 || die "jq not found — brew install jq"
command -v gh >/dev/null 2>&1 || die "gh not found — brew install gh"
gh auth status >/dev/null 2>&1 || die "gh is not authenticated — run: gh auth login"
[[ -x "$LISTENER" ]] || die "listener not executable: $LISTENER"

BACKEND_SCRIPT="$SCRIPT_DIR/backends/$BACKEND.sh"
if [[ ! -x "$BACKEND_SCRIPT" ]]; then
  say "No backend named '$BACKEND' exists yet."
  say "Implement one against scripts/backends/CONTRACT.md, then check it with:"
  say "  scripts/backends/conformance.sh <your-backend>"
  die "backend not found: $BACKEND_SCRIPT"
fi

if [[ ! -d /Applications/SwiftBar.app ]]; then
  warn "SwiftBar is not installed — brew install --cask swiftbar"
fi

mkdir -p "$CFG_DIR"

if [[ -s "$LEGACY" && ! -s "$CONFIG" ]]; then
  # Earlier builds kept intent and derived state in one file.
  jq '{master:false, backend:"'"$BACKEND"'", notify_via:(.notify_via // "'"$NOTIFY"'"), repos:(.repos // {})}' "$LEGACY" >"$CONFIG"
  jq '{seen:(.seen // {}), open:[], last_poll:null, last_error:null}' "$LEGACY" >"$STATE"
  mv "$LEGACY" "$LEGACY.migrated"
  say "Migrated the previous single-file config into config + state."
fi

# A fresh install starts paused: resuming is one click, and nobody wants an
# unattended review dispatched by an install script.
[[ -s "$CONFIG" ]] || jq -n --arg b "$BACKEND" --arg n "$NOTIFY" \
  '{master:false, backend:$b, notify_via:$n, repos:{}}' >"$CONFIG"
[[ -s "$STATE" ]] || jq -n '{seen:{}, open:[], last_poll:null, last_error:null}' >"$STATE"

tmp="$CONFIG.tmp.$$"
jq --arg b "$BACKEND" --arg n "$NOTIFY" '.backend = $b | .notify_via = $n' "$CONFIG" >"$tmp" && mv "$tmp" "$CONFIG"

PLUGIN_DIR=$(defaults read com.ameba.SwiftBar PluginDirectory 2>/dev/null || true)
if [[ -z "$PLUGIN_DIR" ]]; then
  PLUGIN_DIR="$HOME/SwiftBarPlugins"
  defaults write com.ameba.SwiftBar PluginDirectory "$PLUGIN_DIR"
fi
mkdir -p "$PLUGIN_DIR"

WRAPPER="$PLUGIN_DIR/pr-reviewer.60s.sh"
printf '#!/bin/bash\nexec %q "$@"\n' "$LISTENER" >"$WRAPPER"
chmod +x "$WRAPPER"

say ""
say "Installed."
say "  backend        $BACKEND"
say "  notify via     $NOTIFY"
say "  config         $CONFIG"
say "  state          $STATE"
say "  menu plugin    $WRAPPER  (the 60s is the poll interval)"
say ""
say "Two steps left, both in the UI:"
say "  1. Open SwiftBar. On first run it asks for a plugin folder — choose:"
say "     $PLUGIN_DIR"
say "  2. In the menu, click 'Resume listening'. It installs paused on purpose."
say ""
if [[ "$BACKEND" == "conductor" ]]; then
  say "Conductor: the keychain token (conductor auth login) covers its own"
  say "organization. For a repo in another organization, add that org's token:"
  say "  scripts/backends/conductor-token.sh <github-org>"
fi
