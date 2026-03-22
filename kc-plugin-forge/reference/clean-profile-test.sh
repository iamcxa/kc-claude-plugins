#!/bin/bash
# Clean Profile Test — execution isolator for forge Phase 2.5
# Runs claude -p in a clean HOME via safehouse to simulate first-time user.
#
# Usage: clean-profile-test.sh <plugin-dir> <prompt> <timeout> [assertion...]
# Exit:  0 = all assertions pass
#        1 = assertion failure
#        2 = execution error (auth, timeout, safehouse)
#
# Assertions format:
#   contains:<pattern>       — output must include pattern (case-insensitive)
#   not_contains:<pattern>   — output must NOT include pattern (case-insensitive)

set -uo pipefail

PLUGIN_DIR="$1"; shift
PROMPT="$1"; shift
TIMEOUT="${1:-60}"; shift 2>/dev/null || true
ASSERTIONS=("$@")

CLEAN_HOME=$(mktemp -d)
trap "rm -rf '$CLEAN_HOME'" EXIT

# Keychain auth is UID-based, unaffected by HOME change.
# Safehouse reads HOME at startup (home_dir="${HOME:-}") and passes it
# through to sandbox-exec env (HOME=${home_dir}).
OUTPUT=$(timeout "$TIMEOUT" env HOME="$CLEAN_HOME" safehouse \
  --dangerously-skip-permissions \
  claude --plugin-dir "$PLUGIN_DIR" -p "$PROMPT" 2>&1)
CLAUDE_EXIT=$?
if [[ $CLAUDE_EXIT -ne 0 ]]; then
  echo "ERROR: claude execution failed (exit $CLAUDE_EXIT)"
  exit 2
fi

FAILED=0
for assertion in "${ASSERTIONS[@]}"; do
  case "$assertion" in
    contains:*)
      pattern="${assertion#contains:}"
      if ! echo "$OUTPUT" | grep -qi "$pattern"; then
        echo "FAIL: expected '$pattern' not found"
        FAILED=1
      fi
      ;;
    not_contains:*)
      pattern="${assertion#not_contains:}"
      if echo "$OUTPUT" | grep -qi "$pattern"; then
        echo "FAIL: unexpected '$pattern' found"
        FAILED=1
      fi
      ;;
  esac
done

if [[ $FAILED -eq 0 ]]; then
  echo "PASS"
  exit 0
else
  exit 1
fi
