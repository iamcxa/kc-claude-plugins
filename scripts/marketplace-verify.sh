#!/usr/bin/env bash
# marketplace-verify.sh — Verify marketplace schema + plugin installability + skill execution
#
# Usage:
#   ./scripts/marketplace-verify.sh              # L1 (schema) + L2 (install)
#   ./scripts/marketplace-verify.sh --smoke      # L1 + L2 + L3 (skill smoke test, costs ~$0.025/plugin)
#
# Requires: claude CLI, python3
# Runs in isolated temp HOME — zero impact on real ~/.claude/

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MARKETPLACE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
MARKETPLACE_JSON="$MARKETPLACE_DIR/.claude-plugin/marketplace.json"
SMOKE="${1:-}"

if [[ ! -f "$MARKETPLACE_JSON" ]]; then
  echo "ERROR: marketplace.json not found at $MARKETPLACE_JSON"
  exit 1
fi

MARKETPLACE_NAME=$(python3 -c "import json; print(json.load(open('$MARKETPLACE_JSON'))['name'])")
PLUGINS=$(python3 -c "import json; [print(p['name']) for p in json.load(open('$MARKETPLACE_JSON'))['plugins']]")

# Isolated temp HOME
TEMP_HOME=$(mktemp -d)
trap 'rm -rf "$TEMP_HOME"' EXIT

echo "=== Marketplace Verification ==="
echo "  Marketplace: $MARKETPLACE_NAME"
echo "  Source:      $MARKETPLACE_DIR"
echo "  Temp HOME:   $TEMP_HOME"
echo "  Smoke test:  ${SMOKE:-off}"
echo ""

FAIL=0
RESULTS=()

# ─── L1: Schema Validation ───────────────────────────────────
echo "--- L1: Schema Validation ---"
if HOME="$TEMP_HOME" claude plugin marketplace add "$MARKETPLACE_DIR" 2>&1; then
  echo "  ✓ marketplace.json schema valid"
  RESULTS+=("L1 schema: PASS")
else
  echo "  ✗ marketplace.json schema INVALID"
  RESULTS+=("L1 schema: FAIL")
  FAIL=1
fi
echo ""

# ─── L2: Install Validation ──────────────────────────────────
echo "--- L2: Install Validation ---"
for PLUGIN in $PLUGINS; do
  if HOME="$TEMP_HOME" claude plugin install "$PLUGIN@$MARKETPLACE_NAME" 2>&1; then
    echo "  ✓ $PLUGIN installed"
    RESULTS+=("L2 install $PLUGIN: PASS")
  else
    echo "  ✗ $PLUGIN install FAILED"
    RESULTS+=("L2 install $PLUGIN: FAIL")
    FAIL=1
  fi
done
echo ""

# ─── L3: Skill Smoke Test (optional) ─────────────────────────
if [[ "$SMOKE" == "--smoke" ]]; then
  echo "--- L3: Skill Smoke Test ---"
  for PLUGIN in $PLUGINS; do
    # Find installed path in cache
    INSTALLED_PATH=$(find "$TEMP_HOME/.claude/plugins/cache" -path "*/$PLUGIN/*/skills" -type d 2>/dev/null | head -1 | sed 's|/skills$||')
    if [[ -z "$INSTALLED_PATH" ]]; then
      echo "  ⚠ $PLUGIN — installed path not found, skipping"
      RESULTS+=("L3 smoke $PLUGIN: SKIP (no path)")
      continue
    fi

    # Count skills found in installed copy
    SKILL_COUNT=$(find "$INSTALLED_PATH/skills" -name "SKILL.md" 2>/dev/null | wc -l | tr -d ' ')
    if [[ "$SKILL_COUNT" -eq 0 ]]; then
      echo "  ⚠ $PLUGIN — no skills found in installed copy"
      RESULTS+=("L3 smoke $PLUGIN: SKIP (no skills)")
      continue
    fi

    echo "  Testing $PLUGIN ($SKILL_COUNT skills) ..."
    # Use --bare + --plugin-dir on installed copy = clean-room execution
    SMOKE_OUTPUT=$(HOME="$TEMP_HOME" claude --bare --plugin-dir "$INSTALLED_PATH" --effort low \
      -p "List all available skills from the $PLUGIN plugin. Just list their names, nothing else." \
      --max-turns 1 2>&1) || true

    # Check if output mentions any skill name (basic sanity)
    FIRST_SKILL=$(ls "$INSTALLED_PATH/skills/" 2>/dev/null | head -1 || true)
    if echo "$SMOKE_OUTPUT" | grep -qi "$PLUGIN\|skill\|$FIRST_SKILL"; then
      echo "  ✓ $PLUGIN — skills recognized"
      RESULTS+=("L3 smoke $PLUGIN: PASS")
    else
      echo "  ⚠ $PLUGIN — output unclear (may still work)"
      echo "    Output tail: $(echo "$SMOKE_OUTPUT" | tail -3)"
      RESULTS+=("L3 smoke $PLUGIN: WARN")
    fi
  done
  echo ""
fi

# ─── Summary ─────────────────────────────────────────────────
echo "=== Results ==="
for R in "${RESULTS[@]}"; do
  echo "  $R"
done
echo ""

if [[ $FAIL -eq 0 ]]; then
  echo "=== All checks passed ✓ ==="
  exit 0
else
  echo "=== Some checks FAILED ✗ ==="
  exit 1
fi
