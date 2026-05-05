#!/usr/bin/env bash
# measure-fallback-baseline.sh — Baseline eval_fallback_hits counter per flow.
#
# Usage:
#   measure-fallback-baseline.sh --flows-dir <dir> --target-url <url> [options]
#
# Options:
#   --flows-dir <dir>       (required) Directory containing flow YAML files to measure.
#   --target-url <url>      (required) Base URL the flows assume is running.
#   --output <path>         Path to write the baseline JSON.
#                           Default: e2e-pipeline/test/baselines/fallback-baseline.json
#   --auth-token <token>    (optional) Auth token passed through to the runner.
#   --help                  Show this help message and exit.
#
# ─────────────────────────────────────────────────────────────────────────────
# IMPORTANT: This script CANNOT dispatch LLM agents directly from bash.
#
# The e2e-test-runner is an LLM agent, not a standalone binary. It is dispatched
# by the /e2e-test skill inside a Claude Code session. Bash has no mechanism to
# invoke that agent autonomously.
#
# TWO MODES:
#   MODE A (claude CLI available + ANTHROPIC_API_KEY set):
#     Attempts to invoke `claude` CLI per flow to run `/e2e-test <flow>`,
#     parses the trace output for `eval_fallback_hits: <N>`, and records results.
#     Still experimental — the claude CLI headless + plugin-dir path must be
#     verified for your installation before relying on this mode.
#
#   MODE B (documenter mode, default when claude CLI is absent or API key unset):
#     Lists all flows found and prints the manual invocation lines the captain
#     should run from a Claude Code session where the e2e-test skill is available.
#     Use this output as a checklist; fill in the hit counts manually in the JSON.
#
# Captain-driven workflow:
#   1. Ensure the target site is running at --target-url.
#   2. Run this script in MODE B to get the invocation lines.
#   3. In a Claude Code session with the e2e-pipeline plugin loaded, run each
#      `/e2e-test <flow>` invocation.
#   4. From each test report, note the `eval_fallback_hits` value.
#   5. Re-run this script with --populate-from-report (future flag) or
#      manually edit the output JSON.
#
# This measurement is not a gate — exit code is always 0.
# The gate is T2.2's --strict-native-selectors flag on the test runner.
#
# See: docs/ship-flow/001-selector-grammar-alignment/spec.md (Pre-mortem section)
#      e2e-pipeline/test/baselines/README.md
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

# ── defaults ──────────────────────────────────────────────────────────────────
FLOWS_DIR=""
TARGET_URL=""
AUTH_TOKEN=""
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
OUTPUT="${PLUGIN_ROOT}/test/baselines/fallback-baseline.json"

# ── usage ─────────────────────────────────────────────────────────────────────
usage() {
  grep '^#' "$0" | grep -v '^#!/' | sed 's/^# \{0,1\}//'
  exit 0
}

# ── arg parse ─────────────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --flows-dir)         FLOWS_DIR="$2";          shift 2 ;;
    --target-url)        TARGET_URL="$2";         shift 2 ;;
    --output)            OUTPUT="$2";             shift 2 ;;
    --auth-token)        AUTH_TOKEN="$2";         shift 2 ;;
    --strict-target-url) STRICT_TARGET_URL=1;     shift   ;;
    --help|-h)           usage ;;
    *)
      echo "ERROR: unknown option: $1" >&2
      echo "Run with --help for usage." >&2
      exit 1
      ;;
  esac
done

# ── required args ─────────────────────────────────────────────────────────────
if [[ -z "$FLOWS_DIR" ]]; then
  echo "ERROR: --flows-dir is required." >&2
  exit 1
fi
if [[ -z "$TARGET_URL" ]]; then
  echo "ERROR: --target-url is required." >&2
  exit 1
fi
if [[ ! -d "$FLOWS_DIR" ]]; then
  echo "ERROR: flows directory does not exist: $FLOWS_DIR" >&2
  exit 1
fi

# PR #8 R5 fix — validate target URL reachability so caller can't silently
# baseline against a wrong env. Default: warn-and-continue (captain may run
# offline / against fixtures); --strict-target-url makes it a hard error.
TARGET_REACHABLE=1
if ! curl -sf --max-time 5 "$TARGET_URL" > /dev/null 2>&1; then
  TARGET_REACHABLE=0
  echo "WARNING: target URL not reachable: $TARGET_URL" >&2
  echo "  baseline JSON will record target_url_reachable: false." >&2
  echo "  re-run with --strict-target-url to make this fatal." >&2
  if [[ "${STRICT_TARGET_URL:-0}" == "1" ]]; then
    echo "ERROR: --strict-target-url set; aborting." >&2
    exit 1
  fi
fi

# ── detect mode ───────────────────────────────────────────────────────────────
CLAUDE_BIN="$(command -v claude 2>/dev/null || true)"
if [[ -n "$CLAUDE_BIN" && -n "${ANTHROPIC_API_KEY:-}" ]]; then
  MODE="claude-cli"
else
  MODE="documenter"
fi

echo "=== measure-fallback-baseline ==="
echo "flows-dir  : $FLOWS_DIR"
echo "target-url : $TARGET_URL"
echo "output     : $OUTPUT"
echo "mode       : $MODE"
echo ""

# ── collect flow files ────────────────────────────────────────────────────────
# PR #8 R4 fix — parenthesize the alternation. Prior form
#   `find ... -maxdepth 3 -name '*.yaml' -o -name '*.yml'`
# applied -maxdepth only to the first branch (-o has lower precedence than the
# implicit AND), so deeply-nested *.yml files were swept in unexpectedly.
mapfile -t FLOW_FILES < <(find "$FLOWS_DIR" -maxdepth 3 \( -name "*.yaml" -o -name "*.yml" \) | sort)

if [[ ${#FLOW_FILES[@]} -eq 0 ]]; then
  echo "WARNING: No flow YAML files found in: $FLOWS_DIR"
  echo "Nothing to measure. Exiting 0."
  exit 0
fi

echo "Found ${#FLOW_FILES[@]} flow file(s):"
for f in "${FLOW_FILES[@]}"; do
  echo "  $f"
done
echo ""

# ── ensure output directory exists ───────────────────────────────────────────
OUTPUT_DIR="$(dirname "$OUTPUT")"
mkdir -p "$OUTPUT_DIR"

# ── MODE B: documenter ────────────────────────────────────────────────────────
if [[ "$MODE" == "documenter" ]]; then
  echo "──────────────────────────────────────────────────────────────────────────"
  echo "MODE B: documenter (claude CLI or ANTHROPIC_API_KEY not available)"
  echo ""
  echo "Manual invocation lines — run each in a Claude Code session with"
  echo "the e2e-pipeline plugin loaded (/e2e-test skill must be available):"
  echo ""
  for f in "${FLOW_FILES[@]}"; do
    if [[ -n "$AUTH_TOKEN" ]]; then
      echo "  /e2e-test $f  # --auth-token is project-specific; configure auth in your Claude session"
    else
      echo "  /e2e-test $f"
    fi
  done
  echo ""
  echo "After each run, check the test report for: eval_fallback_hits: <N>"
  echo "Report location: .claude/e2e/reports/<timestamp>/report.md"
  echo ""
  echo "──────────────────────────────────────────────────────────────────────────"
  echo "Writing skeleton baseline JSON (all hits = null = unmeasured)..."
  echo ""

  # Write skeleton JSON for captain to fill in
  MEASURED_AT="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  RUNNER_VERSION="$(jq -r '.version // "unknown"' "${PLUGIN_ROOT}/.claude-plugin/plugin.json" 2>/dev/null || echo "unknown")"

  # Build flows array with null hits (unmeasured)
  FLOWS_JSON="["
  FIRST=1
  for f in "${FLOW_FILES[@]}"; do
    [[ $FIRST -eq 0 ]] && FLOWS_JSON+=","
    FIRST=0
    BASENAME="$(basename "$f")"
    # Use python3 or node to safely encode the path as JSON string
    if command -v python3 &>/dev/null; then
      SAFE_PATH="$(python3 -c "import json,sys; print(json.dumps(sys.argv[1]))" "$f")"
    else
      # Fallback: basic escaping (sufficient for typical paths)
      SAFE_PATH="\"$(echo "$f" | sed 's/\\/\\\\/g; s/"/\\"/g')\""
    fi
    FLOWS_JSON+=$(cat <<EOF

    {
      "flow": ${SAFE_PATH},
      "eval_fallback_hits": null,
      "trace_excerpt": "unmeasured — run /e2e-test ${BASENAME} in Claude Code session"
    }
EOF
    )
  done
  FLOWS_JSON+="
  ]"

  REACHABLE_FLAG=$([[ "$TARGET_REACHABLE" == "1" ]] && echo "true" || echo "false")
  mkdir -p "$(dirname "$OUTPUT")"
  cat > "$OUTPUT" <<JSONEOF
{
  "measured_at": "${MEASURED_AT}",
  "target_url": "${TARGET_URL}",
  "target_url_reachable": ${REACHABLE_FLAG},
  "runner_version": "${RUNNER_VERSION}",
  "mode": "skeleton — hits unmeasured, fill in after manual /e2e-test runs",
  "flows": ${FLOWS_JSON}
}
JSONEOF

  echo "Skeleton baseline written to: $OUTPUT"
  echo ""
  echo "Next steps:"
  echo "  1. Run each /e2e-test invocation above in a Claude Code session."
  echo "  2. Check the test report for eval_fallback_hits values."
  echo "  3. Update $OUTPUT with the actual hit counts."
  echo "  4. Commit as pre-T2.2 baseline."
  echo ""
  echo "EXIT 0 (measurement is not a gate — T2.2 --strict-native-selectors is the gate)"
  exit 0
fi

# ── MODE A: claude CLI ────────────────────────────────────────────────────────
echo "──────────────────────────────────────────────────────────────────────────"
echo "MODE A: claude CLI (experimental)"
echo "WARNING: This mode dispatches LLM agents via claude CLI. Each run incurs"
echo "         API token costs and requires the target site at $TARGET_URL."
echo ""

MEASURED_AT="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
RUNNER_VERSION="$(jq -r '.version // "unknown"' "${PLUGIN_ROOT}/.claude-plugin/plugin.json" 2>/dev/null || echo "unknown")"

FLOWS_RESULTS=()

for f in "${FLOW_FILES[@]}"; do
  BASENAME="$(basename "$f")"
  echo "  Running: /e2e-test $f"

  # Capture runner output; on failure record error, do not abort
  RAW_OUTPUT=""
  RUN_STATUS=0
  RAW_OUTPUT="$(
    "${CLAUDE_BIN}" \
      --plugin-dir "${PLUGIN_ROOT}" \
      --no-interactive \
      -p "/e2e-test ${f}" \
      2>&1
  )" || RUN_STATUS=$?

  # Parse eval_fallback_hits from trace output
  # Expected line format: "eval_fallback_hits: 3"
  HITS=""
  if echo "$RAW_OUTPUT" | grep -qE 'eval_fallback_hits\s*:\s*[0-9]+'; then
    HITS="$(echo "$RAW_OUTPUT" | grep -oE 'eval_fallback_hits\s*:\s*[0-9]+' | head -1 | grep -oE '[0-9]+$')"
  fi

  if [[ -z "$HITS" ]]; then
    HITS="null"
    TRACE_EXCERPT="eval_fallback_hits not found in output (run status: ${RUN_STATUS})"
  else
    TRACE_EXCERPT="$(echo "$RAW_OUTPUT" | grep -A2 -B2 'eval_fallback_hits' | head -6 | tr '\n' ' ' | sed 's/  */ /g')"
  fi

  if command -v python3 &>/dev/null; then
    SAFE_PATH="$(python3 -c "import json,sys; print(json.dumps(sys.argv[1]))" "$f")"
    SAFE_EXCERPT="$(python3 -c "import json,sys; print(json.dumps(sys.argv[1]))" "$TRACE_EXCERPT")"
  else
    SAFE_PATH="\"$(echo "$f" | sed 's/\\/\\\\/g; s/"/\\"/g')\""
    SAFE_EXCERPT="\"$(echo "$TRACE_EXCERPT" | sed 's/\\/\\\\/g; s/"/\\"/g')\""
  fi

  FLOWS_RESULTS+=("$(cat <<EOF
    {
      "flow": ${SAFE_PATH},
      "eval_fallback_hits": ${HITS},
      "trace_excerpt": ${SAFE_EXCERPT}
    }
EOF
  )")

  echo "    eval_fallback_hits: ${HITS}"
done

echo ""
echo "Writing baseline JSON to: $OUTPUT"

FLOWS_JSON="$(printf '%s,\n' "${FLOWS_RESULTS[@]}" | sed '$ s/,$//')"

REACHABLE_FLAG=$([[ "$TARGET_REACHABLE" == "1" ]] && echo "true" || echo "false")
mkdir -p "$(dirname "$OUTPUT")"

cat > "$OUTPUT" <<JSONEOF
{
  "measured_at": "${MEASURED_AT}",
  "target_url": "${TARGET_URL}",
  "target_url_reachable": ${REACHABLE_FLAG},
  "runner_version": "${RUNNER_VERSION}",
  "flows": [
${FLOWS_JSON}
  ]
}
JSONEOF

echo ""
echo "Baseline written:"
echo "  $OUTPUT"
echo ""
echo "Total flows measured: ${#FLOWS_RESULTS[@]}"
echo ""
echo "EXIT 0 (measurement is not a gate — T2.2 --strict-native-selectors is the gate)"
exit 0
