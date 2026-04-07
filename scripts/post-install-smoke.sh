#!/usr/bin/env bash
# post-install-smoke.sh — Post-marketplace-install integration test
#
# Tests the full lifecycle: marketplace add → plugin install → MCP deps → smoke test.
# Runs in isolated temp HOME — zero impact on real ~/.claude/.
#
# Usage:
#   ./scripts/post-install-smoke.sh                    # all plugins with smoke YAMLs
#   ./scripts/post-install-smoke.sh kc-hyperfocus      # single plugin
#   ./scripts/post-install-smoke.sh --dry-run           # install only, skip smoke
#
# Requires: claude CLI, python3, bun (for MCP deps)
# Cost: ~$0.02-0.03 per smoke test (--effort low)
#
# Exit: 0 = all pass, 1 = assertion failure, 2 = setup error
#
# Smoke YAML format (in <plugin>/smoke-tests/*.smoke.yaml):
#   skill: <name>
#   trigger: "<prompt>"
#   timeout: <seconds>
#   assertions:
#     - contains: <pattern>
#     - not_contains: <pattern>

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MARKETPLACE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
MARKETPLACE_JSON="$MARKETPLACE_DIR/.claude-plugin/marketplace.json"

# --- Args ---
TARGET_PLUGIN=""
DRY_RUN=false
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
    -*) echo "Unknown flag: $arg"; exit 2 ;;
    *) TARGET_PLUGIN="$arg" ;;
  esac
done

if [[ ! -f "$MARKETPLACE_JSON" ]]; then
  echo "ERROR: marketplace.json not found at $MARKETPLACE_JSON"
  exit 2
fi

# --- API key resolution (same as clean-profile-test.sh) ---
KEY_SOURCE=""
FORGE_CONFIG="$HOME/.claude/kc-plugins-config/forge.yaml"

if [[ -n "${ANTHROPIC_API_KEY:-}" ]]; then
  KEY_SOURCE="env"
elif [[ -f "$FORGE_CONFIG" ]]; then
  API_KEY_FILE=$(grep '^api_key_file:' "$FORGE_CONFIG" | sed 's/^api_key_file:[[:space:]]*//' | sed 's/[[:space:]]*$//')
  if [[ -n "$API_KEY_FILE" && -f "$API_KEY_FILE" ]]; then
    source "$API_KEY_FILE"
    export ANTHROPIC_API_KEY
    if [[ -n "${ANTHROPIC_API_KEY:-}" ]]; then
      KEY_SOURCE="$API_KEY_FILE"
    fi
  fi
fi

if [[ -z "${ANTHROPIC_API_KEY:-}" ]]; then
  echo "ERROR: ANTHROPIC_API_KEY not found"
  echo "  Set it in env, or configure api_key_file in $FORGE_CONFIG"
  exit 2
fi

MARKETPLACE_NAME=$(python3 -c "import json; print(json.load(open('$MARKETPLACE_JSON'))['name'])")
ALL_PLUGINS=$(python3 -c "import json; [print(p['name']) for p in json.load(open('$MARKETPLACE_JSON'))['plugins']]")

# Filter to target if specified
if [[ -n "$TARGET_PLUGIN" ]]; then
  if ! echo "$ALL_PLUGINS" | grep -qx "$TARGET_PLUGIN"; then
    echo "ERROR: plugin '$TARGET_PLUGIN' not found in marketplace"
    echo "Available: $ALL_PLUGINS"
    exit 2
  fi
  PLUGINS="$TARGET_PLUGIN"
else
  PLUGINS="$ALL_PLUGINS"
fi

# --- Isolated temp HOME ---
TEMP_HOME=$(mktemp -d)
trap 'rm -rf "$TEMP_HOME"' EXIT

echo "=== Post-Install Smoke Test ==="
echo "  Marketplace: $MARKETPLACE_NAME"
echo "  Source:      $MARKETPLACE_DIR"
echo "  Temp HOME:   $TEMP_HOME"
echo "  API key:     $KEY_SOURCE"
echo "  Plugins:     $(echo "$PLUGINS" | tr '\n' ' ')"
echo "  Dry run:     $DRY_RUN"
echo ""

FAIL=0
TOTAL_COST=0
RESULTS=()

# No settings.json needed — --dangerously-skip-permissions handles auth in sandbox.

# ─── Phase 1: Marketplace Add + Install ────────────────────────
echo "--- Phase 1: Install ---"
if ! HOME="$TEMP_HOME" claude plugin marketplace add "$MARKETPLACE_DIR" 2>&1; then
  echo "  ✗ marketplace add FAILED"
  exit 2
fi

for PLUGIN in $PLUGINS; do
  if HOME="$TEMP_HOME" claude plugin install "$PLUGIN@$MARKETPLACE_NAME" 2>&1; then
    echo "  ✓ $PLUGIN installed"
  else
    echo "  ✗ $PLUGIN install FAILED"
    RESULTS+=("install $PLUGIN: FAIL")
    FAIL=1
  fi
done
echo ""

# ─── Phase 2: MCP Dependencies ────────────────────────────────
echo "--- Phase 2: MCP Dependencies ---"
for PLUGIN in $PLUGINS; do
  # Find installed plugin path
  INSTALLED_PATH=$(find "$TEMP_HOME/.claude/plugins/cache" -path "*/$PLUGIN/*/.claude-plugin/plugin.json" 2>/dev/null | head -1 | xargs dirname 2>/dev/null | xargs dirname 2>/dev/null)
  if [[ -z "$INSTALLED_PATH" ]]; then
    continue
  fi

  # Check for MCP server requiring deps
  if [[ -f "$INSTALLED_PATH/.mcp.json" && -f "$INSTALLED_PATH/package.json" ]]; then
    echo "  $PLUGIN: installing MCP deps..."
    if (cd "$INSTALLED_PATH" && bun install --production 2>&1 | tail -1); then
      echo "  ✓ $PLUGIN MCP deps installed"
    else
      echo "  ✗ $PLUGIN MCP deps FAILED"
      RESULTS+=("mcp-deps $PLUGIN: FAIL")
      FAIL=1
    fi
  else
    echo "  $PLUGIN: no MCP server (skip)"
  fi
done
echo ""

if $DRY_RUN; then
  echo "=== Dry run — skipping smoke tests ==="
  for R in "${RESULTS[@]+"${RESULTS[@]}"}"; do echo "  $R"; done
  exit $FAIL
fi

# ─── Phase 3: Smoke Tests ─────────────────────────────────────
echo "--- Phase 3: Smoke Tests ---"
SMOKE_COUNT=0
SMOKE_PASS=0

for PLUGIN in $PLUGINS; do
  PLUGIN_SRC="$MARKETPLACE_DIR/$PLUGIN"
  SMOKE_DIR="$PLUGIN_SRC/smoke-tests"

  if [[ ! -d "$SMOKE_DIR" ]]; then
    echo "  $PLUGIN: no smoke-tests/ (skip)"
    RESULTS+=("smoke $PLUGIN: SKIP (no tests)")
    continue
  fi

  for SMOKE_FILE in "$SMOKE_DIR"/*.smoke.yaml; do
    [[ -f "$SMOKE_FILE" ]] || continue
    SMOKE_NAME=$(basename "$SMOKE_FILE" .smoke.yaml)

    # Parse YAML (simple grep — no yq dependency)
    TRIGGER=$(grep '^trigger:' "$SMOKE_FILE" | sed 's/^trigger:[[:space:]]*//' | sed 's/^["'"'"']//;s/["'"'"']$//')
    TIMEOUT=$(grep '^timeout:' "$SMOKE_FILE" | sed 's/^timeout:[[:space:]]*//' || echo "90")

    if [[ -z "$TRIGGER" ]]; then
      echo "  $SMOKE_NAME: no trigger in YAML (skip)"
      continue
    fi

    SMOKE_COUNT=$((SMOKE_COUNT + 1))
    echo "  $SMOKE_NAME: running (timeout ${TIMEOUT}s)..."

    # HOME=$TEMP_HOME: installed plugin MCP servers auto-start via cache.
    # ANTHROPIC_API_KEY: auth without keychain (temp HOME has none).
    # --dangerously-skip-permissions: auto-approve all tool calls in sandbox.
    JSON_OUTPUT=$(HOME="$TEMP_HOME" ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
      timeout "$TIMEOUT" claude --effort low --dangerously-skip-permissions \
      -p "$TRIGGER" --output-format json --max-turns 3 2>/dev/null) || true

    if [[ -z "$JSON_OUTPUT" ]]; then
      echo "    ✗ empty output or timeout"
      RESULTS+=("smoke $SMOKE_NAME: FAIL (empty/timeout)")
      FAIL=1
      continue
    fi

    # Extract result text
    OUTPUT=$(echo "$JSON_OUTPUT" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(data.get('result', ''))
" 2>/dev/null || echo "")

    # Extract cost
    COST=$(echo "$JSON_OUTPUT" | python3 -c "
import json, sys
data = json.load(sys.stdin)
cost = data.get('total_cost_usd', 0)
duration = data.get('duration_ms', 0)
usage = data.get('usage', {})
input_t = usage.get('input_tokens', 0) + usage.get('cache_read_input_tokens', 0) + usage.get('cache_creation_input_tokens', 0)
output_t = usage.get('output_tokens', 0)
print(f'\${cost:.4f} {duration}ms {input_t}in+{output_t}out')
" 2>/dev/null || echo "? ? ?")

    # Parse and check assertions
    ASSERTION_FAIL=0
    while IFS= read -r line; do
      line=$(echo "$line" | sed 's/^[[:space:]]*-[[:space:]]*//')
      case "$line" in
        contains:*)
          pattern="${line#contains:*}"
          pattern=$(echo "$pattern" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//;s/^["'"'"']//;s/["'"'"']$//')
          if ! echo "$OUTPUT" | grep -qiF -- "$pattern"; then
            echo "    ✗ expected '$pattern' not found"
            ASSERTION_FAIL=1
          fi
          ;;
        not_contains:*)
          pattern="${line#not_contains:*}"
          pattern=$(echo "$pattern" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//;s/^["'"'"']//;s/["'"'"']$//')
          if echo "$OUTPUT" | grep -qiF -- "$pattern"; then
            echo "    ✗ unexpected '$pattern' found"
            ASSERTION_FAIL=1
          fi
          ;;
      esac
    done < <(grep -E '^\s*-\s*(contains|not_contains):' "$SMOKE_FILE")

    if [[ $ASSERTION_FAIL -eq 0 ]]; then
      echo "    ✓ PASS ($COST)"
      RESULTS+=("smoke $SMOKE_NAME: PASS ($COST)")
      SMOKE_PASS=$((SMOKE_PASS + 1))
    else
      echo "    ✗ FAIL ($COST)"
      RESULTS+=("smoke $SMOKE_NAME: FAIL ($COST)")
      FAIL=1
    fi
  done
done
echo ""

# ─── Summary ──────────────────────────────────────────────────
echo "=== Results ==="
for R in "${RESULTS[@]+"${RESULTS[@]}"}"; do
  echo "  $R"
done
echo ""
echo "  Plugins: $(echo "$PLUGINS" | wc -w | tr -d ' ')"
echo "  Smoke tests: $SMOKE_COUNT run, $SMOKE_PASS pass, $((SMOKE_COUNT - SMOKE_PASS)) fail"

if [[ $FAIL -eq 0 ]]; then
  echo ""
  echo "=== All checks passed ✓ ==="
  exit 0
else
  echo ""
  echo "=== Some checks FAILED ✗ ==="
  exit 1
fi
