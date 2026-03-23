#!/bin/bash
# Clean Profile Test — execution isolator for forge Phase 2.5
# Runs claude --bare -p to simulate a first-time user with zero context.
#
# --bare skips: auto-memory (MEMORY.md), CLAUDE.md auto-discovery,
# hooks, plugin sync, keychain reads. Only --plugin-dir content is loaded.
#
# Prerequisites: ANTHROPIC_API_KEY must be set (--bare requires it).
#
# Usage: clean-profile-test.sh <plugin-dir> <prompt> <timeout> [assertion...]
# Exit:  0 = all assertions pass
#        1 = assertion failure
#        2 = execution error (auth, timeout, missing key)
#
# Output: PASS/FAIL line + metrics line (cost, duration, tokens)
#
# Assertions format:
#   contains:<pattern>       — output must include pattern (case-insensitive)
#   not_contains:<pattern>   — output must NOT include pattern (case-insensitive)

set -uo pipefail

PLUGIN_DIR="$1"; shift
PROMPT="$1"; shift
TIMEOUT="${1:-60}"; shift 2>/dev/null || true
ASSERTIONS=("$@")

if [[ -z "${ANTHROPIC_API_KEY:-}" ]]; then
  echo "ERROR: ANTHROPIC_API_KEY not set (required for --bare mode)"
  exit 2
fi

JSON_OUTPUT=$(timeout "$TIMEOUT" claude --bare --effort low \
  --plugin-dir "$PLUGIN_DIR" -p "$PROMPT" --output-format json 2>/dev/null)
CLAUDE_EXIT=$?
if [[ $CLAUDE_EXIT -ne 0 ]]; then
  echo "ERROR: claude execution failed (exit $CLAUDE_EXIT)"
  exit 2
fi

# Extract text result and metrics from JSON
OUTPUT=$(echo "$JSON_OUTPUT" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(data.get('result', ''))
" 2>/dev/null)

METRICS=$(echo "$JSON_OUTPUT" | python3 -c "
import json, sys
data = json.load(sys.stdin)
cost = data.get('total_cost_usd', 0)
duration = data.get('duration_ms', 0)
usage = data.get('usage', {})
input_t = usage.get('input_tokens', 0) + usage.get('cache_read_input_tokens', 0) + usage.get('cache_creation_input_tokens', 0)
output_t = usage.get('output_tokens', 0)
print(f'cost=\${cost:.4f} duration={duration}ms tokens={input_t}in+{output_t}out')
" 2>/dev/null || echo "cost=? duration=? tokens=?")

if [[ -z "$OUTPUT" ]]; then
  echo "ERROR: empty result from claude"
  exit 2
fi

FAILED=0
for assertion in "${ASSERTIONS[@]}"; do
  case "$assertion" in
    contains:*)
      pattern="${assertion#contains:}"
      if ! echo "$OUTPUT" | grep -qiF -- "$pattern"; then
        echo "FAIL: expected '$pattern' not found"
        FAILED=1
      fi
      ;;
    not_contains:*)
      pattern="${assertion#not_contains:}"
      if echo "$OUTPUT" | grep -qiF -- "$pattern"; then
        echo "FAIL: unexpected '$pattern' found"
        FAILED=1
      fi
      ;;
  esac
done

if [[ $FAILED -eq 0 ]]; then
  echo "PASS ($METRICS)"
  exit 0
else
  echo "METRICS: $METRICS"
  exit 1
fi
