#!/bin/bash
# Clean Profile Test — execution isolator for forge Phase 2.5
# Runs claude --bare -p to simulate a first-time user with zero context.
#
# --bare skips: auto-memory (MEMORY.md), CLAUDE.md auto-discovery,
# hooks, plugin sync, keychain reads. Only --plugin-dir content is loaded.
#
# API key resolution (in order):
#   1. ANTHROPIC_API_KEY already in environment → use it
#   2. ~/.claude/kc-plugins-config/forge.yaml api_key_file → source it
#   3. Neither → exit 2
#
# Usage: clean-profile-test.sh <plugin-dir> <prompt> <timeout> [assertion...]
# Exit:  0 = all assertions pass
#        1 = assertion failure
#        2 = execution error (auth, timeout, missing key)
#
# Output: PASS/FAIL line with metrics (cost, duration, tokens, key_source)
#
# Assertions format:
#   contains:<pattern>       — output must include pattern (case-insensitive)
#   not_contains:<pattern>   — output must NOT include pattern (case-insensitive)
#
# Extended mode (used by reference/skill-runner.py, the Phase 2 clean runner):
#   SKILL_RUNNER_MODEL        — pin the claude model via --model (unset = unpinned, unchanged default)
#   SKILL_RUNNER_STREAM_JSON  — path to also write the full --output-format stream-json transcript
#                                (tool calls + tool results), needed to score file-state assertions.
#   Both are no-ops when unset — Phase 2.5's plain contains:/not_contains: callers are unaffected.

set -uo pipefail

PLUGIN_DIR="$1"; shift
PROMPT="$1"; shift
TIMEOUT="${1:-60}"; shift 2>/dev/null || true
ASSERTIONS=("$@")

# --- API key resolution ---
KEY_SOURCE=""
FORGE_CONFIG="$HOME/.claude/kc-plugins-config/forge.yaml"

if [[ -n "${ANTHROPIC_API_KEY:-}" ]]; then
  KEY_SOURCE="env"
elif [[ -f "$FORGE_CONFIG" ]]; then
  # Extract api_key_file from YAML (simple grep, no yq dependency)
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

MODEL_FLAG=()
if [[ -n "${SKILL_RUNNER_MODEL:-}" ]]; then
  MODEL_FLAG=(--model "$SKILL_RUNNER_MODEL")
fi

if [[ -n "${SKILL_RUNNER_STREAM_JSON:-}" ]]; then
  RAW=$(timeout "$TIMEOUT" claude --bare --effort low "${MODEL_FLAG[@]}" \
    --plugin-dir "$PLUGIN_DIR" -p "$PROMPT" --output-format stream-json --verbose 2>/dev/null)
  CLAUDE_EXIT=$?
  printf '%s\n' "$RAW" > "$SKILL_RUNNER_STREAM_JSON"
  # The stream is one JSON object per line; the final `type: result` line carries
  # the same summary fields the plain `json` output-format returns as a whole.
  JSON_OUTPUT=$(printf '%s\n' "$RAW" | python3 -c "
import json, sys
last = ''
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        d = json.loads(line)
    except Exception:
        continue
    if d.get('type') == 'result':
        last = line
print(last)
")
else
  JSON_OUTPUT=$(timeout "$TIMEOUT" claude --bare --effort low "${MODEL_FLAG[@]}" \
    --plugin-dir "$PLUGIN_DIR" -p "$PROMPT" --output-format json 2>/dev/null)
  CLAUDE_EXIT=$?
fi
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
  echo "PASS ($METRICS key_source=$KEY_SOURCE)"
  exit 0
else
  echo "METRICS: $METRICS key_source=$KEY_SOURCE"
  exit 1
fi
