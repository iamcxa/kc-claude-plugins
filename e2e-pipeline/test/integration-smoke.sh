#!/usr/bin/env bash
# integration-smoke.sh — End-to-end smoke orchestrator for the post-001 selector grammar contract.
#
# Validates the full /e2e-map → lint → /e2e-test cycle. LLM-agent invocations
# (e2e-mapper, e2e-test-runner) cannot be triggered headlessly; this script either
# documents the manual sequence or runs the phases it can automate (pre-checks,
# linter, report generation). Where a step requires captain intervention, it prints
# the exact command to run and exits 1 so the captain can act and re-invoke.
#
# Usage:
#   bash integration-smoke.sh --target-url <url> [--mapping <path>] [--flow <path>] [--output <path>]
#
# Arguments:
#   --target-url <url>    (required) Base URL of the app to test, e.g. http://localhost:8000
#   --mapping <path>      (optional) Path to an already-generated mapping YAML.
#                         If omitted: script prints the manual /e2e-map invocation and exits 1.
#                         Captain must run map, then re-invoke with --mapping <path>.
#   --flow <path>         (required for phase 4) Path to a flow YAML referencing the mapping.
#                         If omitted: script skips phase 4 and notes it in the report.
#   --output <path>       (default: e2e-pipeline/test/integration-smoke-report.json)
#                         Where to write the JSON smoke report.
#
# Exit codes:
#   0   — all executed phases PASS
#   1   — captain action required (manual step pending) OR a phase FAILED
#
# Phases:
#   Phase 1 — Pre-checks       (automated)
#   Phase 2 — Map step         (manual — documents invocation, then requires --mapping)
#   Phase 3 — Lint step        (automated — runs lint-mapping.sh on the provided mapping)
#   Phase 4 — Test step        (manual — documents invocation, checks eval_fallback_hits)
#   Phase 5 — Report           (automated — writes integration-smoke-report.json)
# ─────────────────────────────────────────────────────────────────────────────

set -uo pipefail

SCRIPT_NAME="$(basename "$0")"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# ── Helpers ──────────────────────────────────────────────────────────────────

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

info()    { echo -e "${CYAN}[smoke]${RESET} $*"; }
ok()      { echo -e "${GREEN}[PASS]${RESET}  $*"; }
warn()    { echo -e "${YELLOW}[WARN]${RESET}  $*"; }
fail()    { echo -e "${RED}[FAIL]${RESET}  $*" >&2; }
section() { echo -e "\n${BOLD}$*${RESET}"; }

iso_now() { date -u +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date -u +"%Y-%m-%dT%H:%M:%SZ"; }

# ── Argument parsing ──────────────────────────────────────────────────────────

TARGET_URL=""
MAPPING_PATH=""
FLOW_PATH=""
OUTPUT_PATH="${PLUGIN_ROOT}/test/integration-smoke-report.json"

usage() {
  cat <<EOF
Usage: $SCRIPT_NAME --target-url <url> [--mapping <path>] [--flow <path>] [--output <path>]

End-to-end smoke orchestrator for the post-001 selector grammar contract.
Validates the /e2e-map → linter → /e2e-test pipeline in four phases.

Arguments:
  --target-url <url>    (required) Base URL, e.g. http://localhost:8000
  --mapping <path>      (optional) Path to mapping YAML produced by /e2e-map.
                        If omitted: script prints the manual step and exits 1.
  --flow <path>         (optional) Path to flow YAML that references the mapping.
                        If omitted: phase 4 is skipped (noted in report).
  --output <path>       (default: e2e-pipeline/test/integration-smoke-report.json)

Phases:
  Phase 1  Pre-checks      — agent-browser, linter, target URL reachability
  Phase 2  Map step        — /e2e-map invocation (manual; prints command if mapping absent)
  Phase 3  Lint step       — runs scripts/lint-mapping.sh; FAIL if banned tokens found
  Phase 4  Test step       — /e2e-test invocation (manual; checks eval_fallback_hits)
  Phase 5  Report          — writes JSON smoke report to --output path

Post-001 contract: lint exit = 0, eval_fallback_hits = 0 on a fresh mapping.

Examples:
  # First run — no mapping yet (prints phase 2 instruction, exits 1):
  bash integration-smoke.sh --target-url http://localhost:8000

  # After captain runs /e2e-map:
  bash integration-smoke.sh \\
    --target-url http://localhost:8000 \\
    --mapping .claude/e2e/mappings/localhost.yaml \\
    --flow .claude/e2e/flows/my-feature.yaml
EOF
  exit 0
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target-url) TARGET_URL="$2"; shift 2 ;;
    --mapping)    MAPPING_PATH="$2"; shift 2 ;;
    --flow)       FLOW_PATH="$2"; shift 2 ;;
    --output)     OUTPUT_PATH="$2"; shift 2 ;;
    --help|-h)    usage ;;
    *) fail "Unknown argument: $1"; echo "Run '$SCRIPT_NAME --help' for usage." >&2; exit 1 ;;
  esac
done

if [[ -z "$TARGET_URL" ]]; then
  fail "Missing required argument: --target-url"
  echo "Run '$SCRIPT_NAME --help' for usage." >&2
  exit 1
fi

# ── State tracking ────────────────────────────────────────────────────────────

SMOKED_AT="$(iso_now)"
LINTER_EXIT="null"
TEST_EVAL_FALLBACK_HITS="null"
VERDICT="FAIL"
NOTES=""
CAPTAIN_ACTION_REQUIRED=0

append_note() { NOTES="${NOTES}${NOTES:+ | }$1"; }

# Ensure output directory exists before any phase can attempt to write a report
# (PR #8 R2 fix — caller may pass --output to a new directory; pre-create so
# Phase 1 failure path can produce the promised JSON failure report).
mkdir -p "$(dirname "$OUTPUT_PATH")"

# ── Phase 1 — Pre-checks ──────────────────────────────────────────────────────

section "Phase 1 — Pre-checks"

phase1_ok=1

# 1a. agent-browser
if command -v agent-browser > /dev/null 2>&1; then
  ok "agent-browser found: $(command -v agent-browser)"
else
  fail "agent-browser not found in PATH"
  fail "Install agent-browser before running this smoke. See: https://github.com/anthropics/agent-browser"
  phase1_ok=0
fi

# 1b. linter
LINTER_SCRIPT="${PLUGIN_ROOT}/scripts/lint-mapping.sh"
if [[ -x "$LINTER_SCRIPT" ]]; then
  ok "linter found: $LINTER_SCRIPT"
else
  fail "linter not found or not executable: $LINTER_SCRIPT"
  fail "Expected: e2e-pipeline/scripts/lint-mapping.sh (created by T0.2)"
  phase1_ok=0
fi

# 1c. target URL reachability
info "Checking target URL: $TARGET_URL"
if curl -sf "$TARGET_URL" > /dev/null 2>&1; then
  ok "target URL reachable: $TARGET_URL"
else
  fail "target URL unreachable: $TARGET_URL"
  fail "Start the application server before running this smoke."
  phase1_ok=0
fi

if [[ $phase1_ok -eq 0 ]]; then
  append_note "Phase 1 pre-checks failed"
  # Write a minimal failure report and exit (output dir pre-created above)
  cat > "$OUTPUT_PATH" <<JSON
{
  "smoked_at": "$SMOKED_AT",
  "target_url": "$TARGET_URL",
  "mapping_path": null,
  "linter_exit": null,
  "test_eval_fallback_hits": null,
  "verdict": "FAIL",
  "notes": "Phase 1 pre-checks failed — see stderr for details"
}
JSON
  fail "Pre-checks failed. Fix the issues above and re-run."
  exit 1
fi

# ── Phase 2 — Map step ────────────────────────────────────────────────────────

section "Phase 2 — Map step"

if [[ -z "$MAPPING_PATH" ]]; then
  warn "No --mapping provided. Captain must run the map step manually."
  echo ""
  echo "  NEXT MANUAL STEP — run in your Claude Code session:"
  echo ""
  echo "    claude --plugin-dir ${PLUGIN_ROOT} -p \"/e2e-map ${TARGET_URL}\""
  echo ""
  echo "  This dispatches the e2e-mapper agent, which will:"
  echo "    1. Open a browser session against ${TARGET_URL}"
  echo "    2. Explore pages and collect stable selectors"
  echo "    3. Emit a mapping YAML to .claude/e2e/mappings/<host>.yaml"
  echo ""
  echo "  Once the mapping is written, re-run this smoke with:"
  echo ""
  echo "    bash ${SCRIPT_NAME} \\"
  echo "      --target-url ${TARGET_URL} \\"
  echo "      --mapping .claude/e2e/mappings/<host>.yaml \\"
  echo "      --flow .claude/e2e/flows/<your-flow>.yaml"
  echo ""
  append_note "Phase 2 skipped — mapping not provided; captain must run /e2e-map"
  CAPTAIN_ACTION_REQUIRED=1

  # Write interim report and exit 1 so the caller knows action is needed
  cat > "$OUTPUT_PATH" <<JSON
{
  "smoked_at": "$SMOKED_AT",
  "target_url": "$TARGET_URL",
  "mapping_path": null,
  "linter_exit": null,
  "test_eval_fallback_hits": null,
  "verdict": "PENDING",
  "notes": "Phase 2 skipped — captain must run /e2e-map ${TARGET_URL} then re-invoke with --mapping"
}
JSON
  info "Interim report written: $OUTPUT_PATH"
  exit 1
else
  if [[ ! -f "$MAPPING_PATH" ]]; then
    fail "Mapping file not found: $MAPPING_PATH"
    append_note "Mapping file not found: $MAPPING_PATH"
    exit 1
  fi
  ok "Mapping provided: $MAPPING_PATH"
  echo ""
  echo "  (If you need to regenerate the mapping, run:)"
  echo "    claude --plugin-dir ${PLUGIN_ROOT} -p \"/e2e-map ${TARGET_URL}\""
fi

# ── Phase 3 — Lint step ───────────────────────────────────────────────────────

section "Phase 3 — Lint step"

info "Running linter: $LINTER_SCRIPT $MAPPING_PATH"
echo ""

set +e
lint_output="$("$LINTER_SCRIPT" "$MAPPING_PATH" 2>&1)"
LINTER_EXIT=$?
set -e

echo "$lint_output"
echo ""

if [[ $LINTER_EXIT -eq 0 ]]; then
  ok "Linter passed — no banned selector tokens found"
  append_note "lint=PASS"
else
  fail "Linter FAILED (exit $LINTER_EXIT) — banned selector tokens detected"
  fail "This is a regression: the contract requires 0 banned tokens in fresh mappings."
  fail "Check which class below fired before blaming the mapper: role=<r>[name=...] and"
  fail "bare text=<v> are NATIVE forms the mapper is supposed to emit, so a failure here"
  fail "is a chord, a has-text(, or a find-subcommand stored as a selector value."
  fail ""
  fail "Banned token classes (from lint-mapping.sh):"
  fail "  CLASS 2: >> nth=<N>                        → replace with: :nth-of-type(N)"
  fail "  CLASS 4: :has-text(                        → restructure selector (no replacement)"
  fail "  CLASS 5: find role|text|label|testid <..>  → replace with: role=<r>[name=\"<v>\"]"
  fail "  (role=<r>[name=...] and bare text=<v> are native forms — see CLAUDE.md § Selector Priority)"
  append_note "lint=FAIL (exit $LINTER_EXIT) — banned tokens in mapping"
fi

# ── Phase 4 — Test step ───────────────────────────────────────────────────────

section "Phase 4 — Test step"

phase4_verdict="SKIP"

if [[ -z "$FLOW_PATH" ]]; then
  warn "No --flow provided. Phase 4 skipped."
  echo ""
  echo "  To run phase 4, provide a flow YAML that references your mapping."
  echo "  If no flow exists yet, generate one in your Claude Code session:"
  echo ""
  echo "    claude --plugin-dir ${PLUGIN_ROOT} -p \"/e2e-flow --from <plan-or-spec>\""
  echo ""
  echo "  Then re-invoke this smoke with:"
  echo ""
  echo "    bash ${SCRIPT_NAME} \\"
  echo "      --target-url ${TARGET_URL} \\"
  echo "      --mapping ${MAPPING_PATH} \\"
  echo "      --flow .claude/e2e/flows/<your-flow>.yaml"
  echo ""
  append_note "Phase 4 skipped — no --flow provided"
  CAPTAIN_ACTION_REQUIRED=1
else
  if [[ ! -f "$FLOW_PATH" ]]; then
    fail "Flow file not found: $FLOW_PATH"
    append_note "Phase 4 failed — flow file not found: $FLOW_PATH"
    phase4_verdict="FAIL"
  else
    ok "Flow provided: $FLOW_PATH"
    echo ""
    echo "  NEXT MANUAL STEP — run in your Claude Code session:"
    echo ""
    echo "    claude --plugin-dir ${PLUGIN_ROOT} -p \"/e2e-test ${FLOW_PATH}\""
    echo ""
    echo "  The e2e-test-runner agent will:"
    echo "    1. Execute each step in the flow against ${TARGET_URL}"
    echo "    2. Produce a report at .claude/e2e/reports/<ts>/report.md"
    echo "    3. Emit eval_fallback_hits: <N> in the trace summary"
    echo ""
    echo "  Post-001 contract: eval_fallback_hits must be 0 on a fresh mapping."
    echo "  If eval_fallback_hits > 0, the mapping still contains selectors that"
    echo "  required eval-based fallback resolution — a regression from the grammar fix."
    echo ""
    echo "  After the test run, inspect the report for:"
    echo "    grep 'eval_fallback_hits' .claude/e2e/reports/*/report.md"
    echo ""
    echo "  Then update this smoke report manually or re-invoke with:"
    echo "    (future: --trace-report <path> flag to auto-parse eval_fallback_hits)"
    echo ""

    # If a trace report already exists alongside the flow, attempt to parse it
    FLOW_DIR="$(dirname "$FLOW_PATH")"
    FLOW_BASE="$(basename "$FLOW_PATH" .yaml)"
    # Look for most recent report directory that might contain results
    LATEST_REPORT_DIR=""
    if [[ -d ".claude/e2e/reports" ]]; then
      LATEST_REPORT_DIR="$(ls -td .claude/e2e/reports/*/ 2>/dev/null | head -1)"
    fi

    if [[ -n "$LATEST_REPORT_DIR" ]] && ls "${LATEST_REPORT_DIR}"*.md > /dev/null 2>&1; then
      info "Found recent report directory: $LATEST_REPORT_DIR"
      # Attempt to extract eval_fallback_hits from most recent report
      FALLBACK_LINE="$(grep -r 'eval_fallback_hits' "${LATEST_REPORT_DIR}" 2>/dev/null | head -1 || true)"
      if [[ -n "$FALLBACK_LINE" ]]; then
        # PR #8 R3 fix — extract digit IMMEDIATELY after `eval_fallback_hits:` only.
        # Prior pattern `[0-9]+ | tail -1` could pick up trailing digits from
        # paths/timestamps in the report line (e.g., `eval_fallback_hits: 3 (measured 2026)`
        # would extract `2026`, not `3`).
        HITS="$(echo "$FALLBACK_LINE" | sed -nE 's/.*eval_fallback_hits[[:space:]]*:[[:space:]]*([0-9]+).*/\1/p' | head -1)"
        if [[ -n "$HITS" ]]; then
          TEST_EVAL_FALLBACK_HITS="$HITS"
          if [[ "$HITS" -eq 0 ]]; then
            ok "eval_fallback_hits = 0 — post-001 contract satisfied"
            phase4_verdict="PASS"
            append_note "test=PASS (eval_fallback_hits=0)"
          else
            fail "eval_fallback_hits = $HITS — post-001 contract VIOLATED"
            fail "Mapping still contains selectors requiring eval-based fallback."
            phase4_verdict="FAIL"
            append_note "test=FAIL (eval_fallback_hits=$HITS)"
          fi
        fi
      else
        warn "Could not extract eval_fallback_hits from recent report."
        warn "Check manually: grep 'eval_fallback_hits' ${LATEST_REPORT_DIR}*.md"
        append_note "Phase 4 — captain must run /e2e-test and verify eval_fallback_hits=0"
        CAPTAIN_ACTION_REQUIRED=1
      fi
    else
      warn "No recent test report found. Captain must run /e2e-test first."
      append_note "Phase 4 — captain must run /e2e-test ${FLOW_PATH}"
      CAPTAIN_ACTION_REQUIRED=1
    fi
  fi
fi

# ── Phase 5 — Report ──────────────────────────────────────────────────────────

section "Phase 5 — Report"

# Determine overall verdict
if [[ $LINTER_EXIT -eq 0 ]] && \
   [[ "$phase4_verdict" == "PASS" ]]; then
  VERDICT="PASS"
elif [[ $LINTER_EXIT -eq 0 ]] && \
     [[ "$phase4_verdict" == "SKIP" ]] && \
     [[ $CAPTAIN_ACTION_REQUIRED -eq 1 ]]; then
  VERDICT="PENDING"
elif [[ $LINTER_EXIT -ne 0 ]] || [[ "$phase4_verdict" == "FAIL" ]]; then
  VERDICT="FAIL"
else
  VERDICT="PENDING"
fi

# Normalize JSON values
MAPPING_JSON="null"
[[ -n "$MAPPING_PATH" ]] && MAPPING_JSON="\"${MAPPING_PATH}\""

LINTER_EXIT_JSON="null"
[[ "$LINTER_EXIT" != "null" ]] && LINTER_EXIT_JSON="$LINTER_EXIT"

FALLBACK_JSON="null"
[[ "$TEST_EVAL_FALLBACK_HITS" != "null" ]] && FALLBACK_JSON="$TEST_EVAL_FALLBACK_HITS"

# Escape any double-quotes in NOTES
NOTES_ESCAPED="${NOTES//\"/\\\"}"

# Ensure output directory exists
OUTPUT_DIR="$(dirname "$OUTPUT_PATH")"
mkdir -p "$OUTPUT_DIR"

cat > "$OUTPUT_PATH" <<JSON
{
  "smoked_at": "${SMOKED_AT}",
  "target_url": "${TARGET_URL}",
  "mapping_path": ${MAPPING_JSON},
  "linter_exit": ${LINTER_EXIT_JSON},
  "test_eval_fallback_hits": ${FALLBACK_JSON},
  "verdict": "${VERDICT}",
  "notes": "${NOTES_ESCAPED}"
}
JSON

info "Smoke report written: $OUTPUT_PATH"
echo ""

# ── Summary ───────────────────────────────────────────────────────────────────

section "Summary"
echo ""
echo "  Target URL : $TARGET_URL"
echo "  Mapping    : ${MAPPING_PATH:-<not provided>}"
echo "  Flow       : ${FLOW_PATH:-<not provided>}"
echo "  Linter     : ${LINTER_EXIT_JSON} (0 = PASS)"
echo "  Fallbacks  : ${FALLBACK_JSON} (0 = post-001 contract satisfied)"
echo "  Verdict    : $VERDICT"
echo "  Report     : $OUTPUT_PATH"
echo ""

if [[ $CAPTAIN_ACTION_REQUIRED -eq 1 ]]; then
  warn "One or more phases require captain action. See instructions above."
  warn "Re-invoke this script after completing each manual step."
fi

case "$VERDICT" in
  PASS)    ok "Smoke PASS — post-001 selector grammar contract satisfied." ;;
  FAIL)    fail "Smoke FAIL — see phase output above for details." ;;
  PENDING) warn "Smoke PENDING — captain action required to complete remaining phases." ;;
esac

echo ""

[[ "$VERDICT" == "PASS" ]] && exit 0 || exit 1
