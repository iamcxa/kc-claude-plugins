'use strict';

/**
 * codegen.js — Transforms resolved compiler data into bash script content.
 *
 * Input:  resolved object from resolver.js (steps with operands and selectors)
 * Output: complete bash script as string
 *
 * All agent-browser commands use positional args (not flags) per commands.md.
 * Selectors are wrapped in single quotes using the singleQuote() escape pattern.
 * Negative visibility and text assertions preserve command/protocol failures.
 *
 * Cross-site support (Phase 2 Plan 02):
 *   - When step.session is set, all agent-browser commands get --session <name> prefix
 *   - Navigate in cross-site uses ${SITE_BASE_URL} (e.g., ${OFFICE_BASE_URL})
 *
 * JUnit XML support (Phase 5 Plan 01, FLAG-01):
 *   - Compiled scripts accept --junit <path> flag at runtime
 *   - Step-level timing/result tracking arrays always emitted
 *   - _emit_junit() bash function writes valid JUnit XML with pre-escaped values
 */

// ---------------------------------------------------------------------------
// Report encoding helpers (compile-time)
// ---------------------------------------------------------------------------

/**
 * xmlAttrEscape(str) — escape a string for safe embedding as XML attribute value.
 *
 * Escapes XML attribute syntax and preserves control whitespace with numeric
 * character references so XML parsers do not normalize identity to spaces.
 *
 * CJK and other Unicode characters pass through as valid UTF-8.
 * Returns the escaped string (no surrounding quotes).
 */
function xmlAttrEscape(str) {
  return str
    .split('')
    .map(function(char) {
      var code = char.charCodeAt(0);
      var isIllegalC0 = code <= 0x08 || code === 0x0B || code === 0x0C ||
        (code >= 0x0E && code <= 0x1F);
      return isIllegalC0 ? '\uFFFD' : char;
    })
    .join('')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/\t/g, '&#x9;')
    .replace(/\n/g, '&#xA;')
    .replace(/\r/g, '&#xD;');
}

function jsonStringContent(str) {
  return JSON.stringify(str).slice(1, -1);
}

// ---------------------------------------------------------------------------
// Shell quoting helper
// ---------------------------------------------------------------------------

/**
 * Wrap str in single quotes, escaping any embedded single quotes with '\''
 * Pattern: end-quote, backslash-single-quote, reopen-quote
 */
function singleQuote(str) {
  return "'" + str.replace(/'/g, "'\\''") + "'";
}

/** Wrap str in double quotes while preserving it as literal shell data. */
function escapeDoubleQuoted(str) {
  return str
    .replace(/\\/g, '\\\\')
    .replace(/"/g, '\\"')
    .replace(/\$/g, '\\$')
    .replace(/`/g, '\\`');
}

function doubleQuote(str) {
  return '"' + escapeDoubleQuoted(str) + '"';
}

/** Produce a path component that cannot traverse outside an artifact directory. */
function artifactFileComponent(str) {
  if (/^[A-Za-z0-9._-]*$/.test(str)) return str;
  return '%' + Buffer.from(str, 'utf8').toString('hex');
}

// ---------------------------------------------------------------------------
// Selector → a11y tree pattern conversion (for snapshot-based visibility checks)
// Canonical translator lives in lib/selector-translate.js (single definition site).
// ---------------------------------------------------------------------------

const { selectorToA11yPattern } = require('./lib/selector-translate.js');
const { renderStandaloneSupport } = require('./lib/visibility-probe.js');
const { siteBaseUrlVariable } = require('./site-name');

// ---------------------------------------------------------------------------
// Variable handling
// ---------------------------------------------------------------------------

/**
 * generateVariables(variables, flowName) — produce bash variable declarations.
 *
 * variables: { [name: string]: string | null }
 *   - null or undefined value => required variable (uses :? pattern)
 *   - string value => optional variable (uses :- pattern with env fallback)
 * flowName: string — used in :? usage message and usage comment
 *
 * Returns: string (multi-line bash block), or '' if variables is empty/absent
 */
function generateVariables(variables, flowName) {
  if (!variables) return '';

  var entries = Object.entries(variables);
  if (entries.length === 0) return '';

  // Classify each variable and build usage parts
  var usageParts = [];
  for (var i = 0; i < entries.length; i++) {
    var name = entries[i][0];
    var value = entries[i][1];
    var isRequired = (value === null || value === undefined);
    usageParts.push(isRequired ? '<' + name + '>' : '[' + name + ']');
  }

  var usageLine = '# Usage: ' + flowName + '.sh ' + usageParts.join(' ');
  var lines = [usageLine, '# Parameters:'];

  // Build assignment lines in same pass
  var assignments = [];

  for (var j = 0; j < entries.length; j++) {
    var varName = entries[j][0];
    var varValue = entries[j][1];
    var isReq = (varValue === null || varValue === undefined);
    // Use varName directly uppercased (already may be OFFICE_BASE_URL etc.)
    var bashName = varName.toUpperCase();
    var envName = 'E2E_' + bashName;
    var pos = j + 1;

    if (isReq) {
      // Required: collect all usage params for the :? message
      var reqUsage = flowName + '.sh ' + usageParts.join(' ');
      lines.push('# $' + pos + ' ' + bashName + ' -- required (or set ' + envName + ')');
      assignments.push(bashName + '="${' + pos + ':?Usage: ' + reqUsage + '}"');
    } else {
      var defaultStr = String(varValue);
      if (defaultStr === '') {
        lines.push('# $' + pos + ' ' + bashName + ' -- optional (or set ' + envName + ')');
        assignments.push(bashName + '="${' + pos + ':-${' + envName + ':-}}"');
      } else {
        lines.push('# $' + pos + ' ' + bashName + ' -- optional (or set ' + envName + ', default: ' + defaultStr + ')');
        assignments.push(bashName + '="${' + pos + ':-${' + envName + ':-' + defaultStr + '}}"');
      }
    }
  }

  // Combine comments and assignments
  return lines.join('\n') + '\n' + assignments.join('\n');
}

// ---------------------------------------------------------------------------
// Runtime values block (SC-1032) — required env variables, not positional args
// ---------------------------------------------------------------------------

/**
 * generateRuntimeValuesBlock(runtimeValues, flowName) — emit env-based required variable checks.
 *
 * Unlike generateVariables() which reads positional args ($1, $2, ...),
 * runtime_values entries are always read from the environment (never from argv).
 * This is mandatory for secrets: passing secrets via argv leaks them into
 * process lists, shell history, and log files.
 *
 * Each entry:
 *   - null => required env: VAR="${VAR:?Usage: set VAR env for flowName}"
 *   - string => optional env with default: VAR="${VAR:-default}"
 *
 * Returns: string (multi-line bash block), or '' if runtimeValues is empty/absent
 */
function generateRuntimeValuesBlock(runtimeValues, _flowName) {
  if (!runtimeValues) return '';
  var entries = Object.entries(runtimeValues);
  if (entries.length === 0) return '';

  var lines = ['# Runtime values (required env vars — never pass secrets via argv)'];
  for (var i = 0; i < entries.length; i++) {
    var varName = entries[i][0];
    var declaration = entries[i][1];
    var bashName = declaration.from_env;
    lines.push(bashName + '="${' + bashName + ':?Error: ' + bashName +
      ' must be set in environment}"');
  }
  return lines.join('\n');
}


// ---------------------------------------------------------------------------
// Header generation
// ---------------------------------------------------------------------------

/**
 * generateHeader(meta) — produce bash script header.
 *
 * When called with no args (or meta=null/undefined), returns minimal Phase 1 header.
 * When called with a meta object, inserts provenance comment block between
 * set -euo pipefail and export LANG lines.
 *
 * meta: {
 *   flowName: string,       // flow name for "e2e-compile <flowName>" hint
 *   flowPath: string,       // source flow path
 *   mappingPath?: string,   // single mapping path (single-site)
 *   mappingPaths?: string[],// multiple mapping paths (cross-site)
 *   timestamp: string,      // ISO-8601 timestamp
 *   hash: string,           // SHA-256 hex digest of source files
 *   compilerVersion?: string, // e2e-pipeline package version
 * }
 */
function generateHeader(meta) {
  var lines = [
    '#!/usr/bin/env bash',
    'set -euo pipefail',
    '',
  ];

  if (meta) {
    lines.push('# DO NOT EDIT -- regenerate with: e2e-compile ' + meta.flowName);
    lines.push('# Source: ' + meta.flowPath);
    if (Array.isArray(meta.mappingPaths)) {
      meta.mappingPaths.forEach(function(p) { lines.push('# Mapping: ' + p); });
    } else if (meta.mappingPath) {
      lines.push('# Mapping: ' + meta.mappingPath);
    }
    lines.push('# Generated: ' + meta.timestamp);
    lines.push('# SHA-256: ' + meta.hash);
    if (meta.compilerVersion) {
      lines.push('# Compiler: ' + meta.compilerVersion);
    }
    lines.push('');
  }

  lines.push('export LANG=en_US.UTF-8');
  lines.push('export LC_ALL=en_US.UTF-8');
  lines.push('');

  return lines.join('\n');
}

// ---------------------------------------------------------------------------
// Runtime flag parsing block (FLAG-02 + FLAG-03)
// ---------------------------------------------------------------------------

/**
 * generateRuntimeFlagBlock() — produce bash flag-parsing block for compiled scripts.
 *
 * Parses --continue-on-error, --retries N, --junit <path>, and --metrics-output <path>
 * at script runtime. Must appear BEFORE variable assignment (uses shift/set -- to
 * consume flags before positionals are read).
 *
 * Uses set -- "${_POSITIONAL[@]:-}" (the :- is required for bash 3.2 + set -u)
 *
 * Returns: string (multi-line bash block)
 */
function generateRuntimeFlagBlock() {
  var lines = [
    '# Runtime flags',
    'CONTINUE_ON_ERROR=false',
    'RETRIES=0',
    'JUNIT_OUTPUT=""',
    'METRICS_OUTPUT=""',
    '_POSITIONAL=()',
    'while [[ $# -gt 0 ]]; do',
    '  case "$1" in',
    '    --continue-on-error)',
    '      CONTINUE_ON_ERROR=true',
    '      shift',
    '      ;;',
    '    --retries)',
    '      RETRIES="$2"',
    '      shift 2',
    '      ;;',
    '    --junit)',
    '      JUNIT_OUTPUT="$2"',
    '      shift 2',
    '      if [ -z "$JUNIT_OUTPUT" ]; then',
    '        echo "ERROR: --junit requires a path argument"',
    '        exit 1',
    '      fi',
    '      ;;',
    '    --metrics-output)',
    '      METRICS_OUTPUT="$2"',
    '      shift 2',
    '      if [ -z "$METRICS_OUTPUT" ]; then',
    '        echo "ERROR: --metrics-output requires a path argument"',
    '        exit 1',
    '      fi',
    '      ;;',
    '    *)',
    '      _POSITIONAL+=("$1")',
    '      shift',
    '      ;;',
    '  esac',
    'done',
    'set -- "${_POSITIONAL[@]:-}"',
    '',
  ];
  return lines.join('\n');
}

// ---------------------------------------------------------------------------
// Runtime support functions (_handle_failure, _FAILED_STEPS)
// ---------------------------------------------------------------------------

/**
 * generateRuntimeSupport() — produce _FAILED_STEPS array, _handle_failure() function,
 * and poll-until helper functions.
 *
 * _handle_failure "step_id" "msg" [session]:
 *   - Echoes FAIL line
 *   - If CONTINUE_ON_ERROR=true: accumulates each step_id once in _FAILED_STEPS
 *   - If CONTINUE_ON_ERROR=false: calls exit 1 (v1.0 backward compat)
 *   - Always returns 0 so the || operator satisfies set -e
 *
 * Poll helpers (_poll_visible, _poll_not_visible, _poll_url_contains, _poll_or_visible):
 *   - Use local variables (bash 3.2 safe)
 *   - Use $((_count + 1)) arithmetic (no let, no (( )))
 *   - Use sleep 1 between iterations
 *   - Use 2>/dev/null on agent-browser calls
 *   - Capture commands without letting set -e abort the polling loop
 *   - Return 1 on deadline; visibility helpers return 2 on command/protocol failure
 *
 * Never emit a `producer | grep -q` text match. The compiled script runs under
 * `set -euo pipefail`: grep exits 0 the instant it can decide and closes the
 * pipe, the still-writing producer dies on SIGPIPE (or EPIPE where SIGPIPE is
 * ignored), and pipefail publishes the producer's status — so a SUCCESSFUL
 * match reads as a no-match. It needs an early-decidable match plus a producer
 * still writing, which a11y snapshots satisfy once a page grows past the pipe
 * buffer. Use the subprocess-free bash forms instead: `[[ "$s" == *"$p"* ]]`
 * for fixed strings (a quoted pattern operand is literal, not a glob) and
 * `[[ "$s" =~ re ]]` for anchored regexes. The `=~` conversions are exact
 * because every input reaching them is already proven single-line upstream
 * (`sed -n 1p`, or an explicit embedded-newline rejection), so grep's
 * match-any-line semantics had nothing extra to match.
 *
 * Returns: string (multi-line bash block)
 */
function generateVisibilitySupport() {
  var nodeProgram = [
    "'use strict';",
    "const fs = require('node:fs');",
    'const api = ' + renderStandaloneSupport() + ';',
    'const mode = process.argv[1];',
    "if (mode === 'expression') {",
    '  process.stdout.write(api.buildProbeExpression(process.argv[2]) + "\\n");',
    "} else if (mode === 'judge') {",
    '  const raw = fs.readFileSync(0, "utf8");',
    '  const evidence = api.unwrapEvalEnvelope(raw, Number(process.argv[4]));',
    '  const classified = api.classifyVisibility(evidence, process.argv[2]);',
    '  const judged = api.judgeVisibility(classified, process.argv[3]);',
    '  process.stdout.write(JSON.stringify(judged) + "\\n");',
    '  process.exitCode = judged.exit_code;',
    "} else if (mode === 'report') {",
    '  const judged = JSON.parse(fs.readFileSync(0, "utf8"));',
    '  const report = {',
    '    result_class: judged.result,',
    '    effective_selector: process.argv[2],',
    '    visibility_policy: judged.policy,',
    '    assertion: judged.assertion,',
    '    judgment: judged.judgment,',
    '    match_count: judged.match_count,',
    '    nonzero_layout_visible_count: judged.nonzero_layout_visible_count,',
    '    style_visible_zero_rect_count: judged.style_visible_zero_rect_count,',
    '    non_style_visible_count: judged.non_style_visible_count,',
    '    attempts: Number(process.argv[3]),',
    '    elapsed_seconds: Number(process.argv[4]),',
    '    candidate_evidence_limit: judged.candidate_evidence_limit,',
    '    candidate_evidence_truncated: judged.candidate_evidence_truncated,',
    '    candidate_evidence: judged.candidates,',
    '    rendered_candidate: judged.rendered_candidate,',
    '  };',
    '  if (judged.error) report.error = judged.error;',
    '  process.stdout.write(JSON.stringify(report) + "\\n");',
    '} else {',
    '  process.stderr.write("unknown visibility support mode\\n");',
    '  process.exitCode = 2;',
    '}',
  ].join('\n');

  return [
    '# Shared deterministic DOM visibility support (generated from compiler/lib/visibility-probe.js).',
    '_VISIBILITY_LAST_RESULT=""',
    '_VISIBILITY_RESULTS=()',
    '_visibility_node() {',
    '  node -e ' + singleQuote(nodeProgram) + ' "$@"',
    '}',
    '',
    '_probe_visibility_once() {',
    '  local _selector="$1"',
    '  local _policy="$2"',
    '  local _assertion="$3"',
    '  local _session="${4:-}"',
    '  local _expression',
    '  local _envelope',
    '  local _transport',
    '  local _judged',
    '  local _judge_status',
    '  if ! _expression=$(_visibility_node expression "$_selector"); then return 2; fi',
    '  if [ -n "$_session" ]; then',
    '    if _envelope=$(agent-browser --session "$_session" eval "$_expression" --json 2>&1); then',
    '      _transport=0',
    '    else',
    '      _transport=$?',
    '    fi',
    '  else',
    '    if _envelope=$(agent-browser eval "$_expression" --json 2>&1); then',
    '      _transport=0',
    '    else',
    '      _transport=$?',
    '    fi',
    '  fi',
    '  if _judged=$(printf \'%s\' "$_envelope" | _visibility_node judge "$_policy" "$_assertion" "$_transport"); then',
    '    _judge_status=0',
    '  else',
    '    _judge_status=$?',
    '  fi',
    '  _VISIBILITY_LAST_RESULT="$_judged"',
    '  return "$_judge_status"',
    '}',
    '',
    '_record_visibility_json() {',
    '  local _judged="$1"',
    '  local _selector="$2"',
    '  local _attempts="$3"',
    '  local _elapsed="$4"',
    '  local _report',
    '  if ! _report=$(printf \'%s\' "$_judged" | _visibility_node report "$_selector" "$_attempts" "$_elapsed"); then',
    '    return 2',
    '  fi',
    '  _VISIBILITY_RESULTS+=("$_report")',
    '}',
    '',
    '_record_visibility_result() {',
    '  _record_visibility_json "$_VISIBILITY_LAST_RESULT" "$1" "$2" "$3"',
    '}',
    '',
    '_poll_visibility() {',
    '  local _selector="$1"',
    '  local _policy="$2"',
    '  local _assertion="$3"',
    '  local _step_id="$4"',
    '  local _timeout="${5:-10}"',
    '  local _session="${6:-}"',
    '  local _count=0',
    '  local _attempts=0',
    '  local _started=$SECONDS',
    '  local _elapsed=0',
    '  local _status',
    '  while :; do',
    '    _attempts=$((_attempts + 1))',
    '    if _probe_visibility_once "$_selector" "$_policy" "$_assertion" "$_session"; then',
    '      _status=0',
    '    else',
    '      _status=$?',
    '    fi',
    '    _elapsed=$(( SECONDS - _started ))',
    '    if [ "$_timeout" -eq 0 ]; then _elapsed=0; fi',
    '    if [ "$_status" -eq 0 ]; then',
    '      _record_visibility_result "$_selector" "$_attempts" "$_elapsed" || return 2',
    '      return 0',
    '    fi',
    '    if [ "$_status" -eq 2 ]; then',
    '      _record_visibility_result "$_selector" "$_attempts" "$_elapsed" || return 2',
    '      return 2',
    '    fi',
    '    if [ "$_count" -ge "$_timeout" ]; then',
    '      _record_visibility_result "$_selector" "$_attempts" "$_elapsed" || return 2',
    '      return 1',
    '    fi',
    '    sleep 1',
    '    _count=$((_count + 1))',
    '  done',
    '}',
    '',
    '_poll_or_visibility() {',
    '  local _step_id="$1"',
    '  local _timeout="$2"',
    '  local _session="$3"',
    '  local _selector_a="$4"',
    '  local _policy_a="$5"',
    '  local _selector_b="$6"',
    '  local _policy_b="$7"',
    '  local _count=0',
    '  local _attempts=0',
    '  local _started=$SECONDS',
    '  local _elapsed=0',
    '  local _status_a',
    '  local _status_b',
    '  local _result_a',
    '  local _result_b',
    '  while :; do',
    '    _attempts=$((_attempts + 1))',
    '    if _probe_visibility_once "$_selector_a" "$_policy_a" visible "$_session"; then _status_a=0; else _status_a=$?; fi',
    '    _result_a="$_VISIBILITY_LAST_RESULT"',
    '    if _probe_visibility_once "$_selector_b" "$_policy_b" visible "$_session"; then _status_b=0; else _status_b=$?; fi',
    '    _result_b="$_VISIBILITY_LAST_RESULT"',
    '    _elapsed=$(( SECONDS - _started ))',
    '    if [ "$_timeout" -eq 0 ]; then _elapsed=0; fi',
    '    if [ "$_status_a" -eq 2 ] || [ "$_status_b" -eq 2 ]; then',
    '      _record_visibility_json "$_result_a" "$_selector_a" "$_attempts" "$_elapsed" || return 2',
    '      _record_visibility_json "$_result_b" "$_selector_b" "$_attempts" "$_elapsed" || return 2',
    '      return 2',
    '    fi',
    '    if [ "$_status_a" -eq 0 ] || [ "$_status_b" -eq 0 ]; then',
    '      _record_visibility_json "$_result_a" "$_selector_a" "$_attempts" "$_elapsed" || return 2',
    '      _record_visibility_json "$_result_b" "$_selector_b" "$_attempts" "$_elapsed" || return 2',
    '      return 0',
    '    fi',
    '    if [ "$_count" -ge "$_timeout" ]; then',
    '      _record_visibility_json "$_result_a" "$_selector_a" "$_attempts" "$_elapsed" || return 2',
    '      _record_visibility_json "$_result_b" "$_selector_b" "$_attempts" "$_elapsed" || return 2',
    '      return 1',
    '    fi',
    '    sleep 1',
    '    _count=$((_count + 1))',
    '  done',
    '}',
    '',
    '_poll_enabled_state() {',
    '  local _selector="$1"',
    '  local _policy="$2"',
    '  local _expected="$3"',
    '  local _step_id="$4"',
    '  local _timeout="${5:-10}"',
    '  local _session="${6:-}"',
    '  _poll_visibility "$_selector" "$_policy" "$_expected" "$_step_id" "$_timeout" "$_session"',
    '}',
  ].join('\n');
}

function generateRuntimeSupport(includeRuntimeStateSupport, includeVisibilitySupport) {
  var lines = [
    '# Failure accumulator',
    '_FAILED_STEPS=()',
    '_HAD_RETRIES=false',
    '# Attempt tracking (FLAKY-02)',
    '_TOTAL_ATTEMPTS=1',
    '_ATTEMPT_NUM=1',
    '# JUnit step tracking arrays (FLAG-01)',
    '_STEP_NAMES=()',
    '_STEP_JSON_NAMES=()',
    '_STEP_XML_NAMES=()',
    '_STEP_RESULTS=()',
    '_STEP_FAILURES=()',
    '_STEP_TIMES=()',
    '_FLOW_START=$SECONDS',
    '_SCREENSHOT_DIR="${E2E_SCREENSHOT_DIR:-/tmp/e2e-screenshots}"',
    'mkdir -p "$_SCREENSHOT_DIR"',
    '',
    '_record_step_name() {',
    '  _STEP_NAMES+=("$1")',
    '  _STEP_JSON_NAMES+=("$2")',
    '  _STEP_XML_NAMES+=("$3")',
    '}',
    '',
    '_diagnostic_browser() {',
    '  local _session="$1"',
    '  shift',
    '  if [ -n "$_session" ]; then',
    '    agent-browser --session "$_session" "$@"',
    '  else',
    '    agent-browser "$@"',
    '  fi',
    '}',
    '',
    '_artifact_name() {',
    '  local _raw="$1"',
    '  local _safe',
    "  _safe=$(printf '%s' \"$_raw\" | LC_ALL=C tr -c 'A-Za-z0-9._-' '_')",
    '  if [ "$_safe" = "$_raw" ]; then',
    "    printf '%s' \"$_raw\"",
    '  else',
    "    printf '%%'",
    "    printf '%s' \"$_raw\" | LC_ALL=C od -An -v -t x1 | tr -d ' \\n'",
    '  fi',
    '}',
    '',
    '_json_escape() {',
    '  local _byte',
    "  printf '%s' \"$1\" | LC_ALL=C od -An -v -t u1 | tr -s ' ' '\\n' | while IFS= read -r _byte; do",
    '    [ -z "$_byte" ] && continue',
    '    case "$_byte" in',
    "      8) printf '%s' '\\b' ;;",
    "      9) printf '%s' '\\t' ;;",
    "      10) printf '%s' '\\n' ;;",
    "      12) printf '%s' '\\f' ;;",
    "      13) printf '%s' '\\r' ;;",
    "      34) printf '%s' '\\\"' ;;",
    "      92) printf '%s' '\\\\' ;;",
    '      1|2|3|4|5|6|7|11|14|15|16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31)',
    "        printf '\\\\u%04x' \"$_byte\"",
    '        ;;',
    '      *)',
    "        printf \"\\\\$(printf '%03o' \"$_byte\")\"",
    '        ;;',
    '    esac',
    '  done',
    '}',
    '',
    '_base64_no_wrap() {',
    "  printf '%s' \"$1\" | base64 | tr -d '\\r\\n'",
    '}',
    '',
    '_url_encode() {',
    '  local _byte',
    "  printf '%s' \"$1\" | LC_ALL=C od -An -v -t u1 | tr -s ' ' '\\n' | while IFS= read -r _byte; do",
    '    [ -z "$_byte" ] && continue',
    '    case "$_byte" in',
    '      45|46|48|49|50|51|52|53|54|55|56|57|65|66|67|68|69|70|71|72|73|74|75|76|77|78|79|80|81|82|83|84|85|86|87|88|89|90|95|97|98|99|100|101|102|103|104|105|106|107|108|109|110|111|112|113|114|115|116|117|118|119|120|121|122|126)',
    "        printf \"\\\\$(printf '%03o' \"$_byte\")\" ;;",
    "      *) printf '%%%02X' \"$_byte\" ;;",
    '    esac',
    '  done',
    '}',
    '',
    '_curl_config_escape() {',
    '  local _byte',
    "  if ! printf '%s' \"$1\" | LC_ALL=C od -An -v -t u1 | tr -s ' ' '\\n' | while IFS= read -r _byte; do",
    '    [ -z "$_byte" ] && continue',
    '    case "$_byte" in',
    '      0|1|2|3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31|127) exit 1 ;;',
    '    esac',
    '  done; then',
    '    return 1',
    '  fi',
    "  printf '%s' \"$1\" | sed 's/\\\\/\\\\\\\\/g; s/\"/\\\\\"/g'",
    '}',
    '',
    '_json_top_level_string_equals() {',
    '  local _json_file="$1"',
    '  local _json_field="$2"',
    '  local _json_expected="$3"',
    '  local _json_object="${4-}"',
    '  node - "$_json_file" "$_json_field" "$_json_expected" "$_json_object" <<\'__E2E_JSON_ASSERT__\'',
    "'use strict';",
    "const fs = require('fs');",
    'const source = fs.readFileSync(process.argv[2], \'utf8\');',
    'const field = process.argv[3];',
    'const expected = process.argv[4];',
    'const object = process.argv[5];',
    'let offset = 0;',
    'function invalid() { throw new Error(\'invalid JSON response\'); }',
    'function whitespace() { while (/\\s/.test(source[offset] || \'\')) offset += 1; }',
    'function stringValue() {',
    '  const start = offset;',
    '  if (source[offset] !== \'"\') invalid();',
    '  offset += 1;',
    '  while (offset < source.length) {',
    '    const code = source.charCodeAt(offset);',
    '    if (source[offset] === \'"\') {',
    '      offset += 1;',
    '      return JSON.parse(source.slice(start, offset));',
    '    }',
    '    if (source[offset] === \'\\\\\') {',
    '      offset += 1;',
    '      if (offset >= source.length) invalid();',
    '      if (source[offset] === \'u\') {',
    '        if (!/^[0-9a-fA-F]{4}$/.test(source.slice(offset + 1, offset + 5))) invalid();',
    '        offset += 5;',
    '      } else {',
    '        if (!/["\\\\/bfnrt]/.test(source[offset])) invalid();',
    '        offset += 1;',
    '      }',
    '    } else {',
    '      if (code <= 0x1f) invalid();',
    '      offset += 1;',
    '    }',
    '  }',
    '  invalid();',
    '}',
    'function value() {',
    '  whitespace();',
    '  if (source[offset] === \'"\') return stringValue();',
    '  if (source[offset] === \'{\') {',
    '    const object = Object.create(null);',
    '    const keys = new Set();',
    '    offset += 1;',
    '    whitespace();',
    '    if (source[offset] === \'}\') { offset += 1; return object; }',
    '    while (true) {',
    '      whitespace();',
    '      const key = stringValue();',
    '      if (keys.has(key)) invalid();',
    '      keys.add(key);',
    '      whitespace();',
    '      if (source[offset] !== \':\') invalid();',
    '      offset += 1;',
    '      object[key] = value();',
    '      whitespace();',
    '      if (source[offset] === \'}\') { offset += 1; return object; }',
    '      if (source[offset] !== \',\') invalid();',
    '      offset += 1;',
    '    }',
    '  }',
    '  if (source[offset] === \'[\') {',
    '    const array = [];',
    '    offset += 1;',
    '    whitespace();',
    '    if (source[offset] === \']\') { offset += 1; return array; }',
    '    while (true) {',
    '      array.push(value());',
    '      whitespace();',
    '      if (source[offset] === \']\') { offset += 1; return array; }',
    '      if (source[offset] !== \',\') invalid();',
    '      offset += 1;',
    '    }',
    '  }',
    '  const rest = source.slice(offset);',
    '  const number = rest.match(/^-?(?:0|[1-9]\\d*)(?:\\.\\d+)?(?:[eE][+-]?\\d+)?/);',
    '  if (number) { offset += number[0].length; return Number(number[0]); }',
    '  if (rest.startsWith(\'true\')) { offset += 4; return true; }',
    '  if (rest.startsWith(\'false\')) { offset += 5; return false; }',
    '  if (rest.startsWith(\'null\')) { offset += 4; return null; }',
    '  invalid();',
    '}',
    'try {',
    '  const document = value();',
    '  whitespace();',
    '  if (offset !== source.length) invalid();',
    '  if (document === null || Array.isArray(document) || typeof document !== \'object\') invalid();',
    '  let target = document;',
    '  if (object) {',
    '    if (!Object.prototype.hasOwnProperty.call(document, object)) invalid();',
    '    target = document[object];',
    '    if (target === null || Array.isArray(target) || typeof target !== \'object\') invalid();',
    '  }',
    '  if (!Object.prototype.hasOwnProperty.call(target, field)) invalid();',
    '  if (typeof target[field] !== \'string\' || target[field] !== expected) invalid();',
    '} catch (_error) {',
    '  process.exit(1);',
    '}',
    '__E2E_JSON_ASSERT__',
    '}',
    '',
    '_xml_attr_escape() {',
    '  local _byte',
    "  printf '%s' \"$1\" | LC_ALL=C od -An -v -t u1 | tr -s ' ' '\\n' | while IFS= read -r _byte; do",
    '    [ -z "$_byte" ] && continue',
    '    case "$_byte" in',
    "      9) printf '%s' '&#x9;' ;;",
    "      10) printf '%s' '&#xA;' ;;",
    "      13) printf '%s' '&#xD;' ;;",
    "      34) printf '%s' '&quot;' ;;",
    "      38) printf '%s' '&amp;' ;;",
    "      60) printf '%s' '&lt;' ;;",
    "      62) printf '%s' '&gt;' ;;",
    '      1|2|3|4|5|6|7|8|11|12|14|15|16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31)',
    "        printf '%s' '&#xFFFD;'",
    '        ;;',
    '      *)',
    "        printf \"\\\\$(printf '%03o' \"$_byte\")\"",
    '        ;;',
    '    esac',
    '  done',
    '}',
    '',
    '_handle_failure() {',
    '  local _step_id="$1"',
    '  local _msg="$2"',
    '  local _session="${3:-}"',
    '  local _step_file',
    '  _step_file=$(_artifact_name "$_step_id")',
    '  echo "FAIL: $_step_id -- $_msg"',
    '  # Capture diagnostic artifacts on failure',
    '  echo "--- Diagnostic: screenshot ---"',
    '  _diagnostic_browser "$_session" screenshot "$_SCREENSHOT_DIR/fail-$' +
      '{_step_file}.png" 2>&1 || echo "(screenshot failed)"',
    '  echo "--- Diagnostic: current URL ---"',
    '  _diagnostic_browser "$_session" get url 2>&1 || echo "(get url failed)"',
    '  echo "--- Diagnostic: a11y snapshot (first 80 lines) ---"',
    '  _diagnostic_browser "$_session" snapshot 2>&1 | head -80 || echo "(snapshot failed)"',
    '  echo "--- End diagnostic ---"',
    '  local _msg_clean',
    "  local _msg_sentinel='__E2E_PIPELINE_MSG_END_7f3a9c__'",
    "  _msg_clean=$({ printf '%s' \"$_msg\"; printf '%s' \"$_msg_sentinel\"; } | sed 's/\\x1b\\[[0-9;]*m//g')",
    '  _msg_clean="${_msg_clean%"$_msg_sentinel"}"',
    '  # Overwrite last entry (not append) to keep arrays aligned with step count',
    '  local _last_idx=$(( ${#_STEP_RESULTS[@]} - 1 ))',
    '  _STEP_RESULTS[$_last_idx]="fail"',
    '  _STEP_FAILURES[$_last_idx]="$_msg_clean"',
    '  if [ "$CONTINUE_ON_ERROR" = "true" ]; then',
    '    local _already_failed=false',
    '    local _failed_step',
    '    if [ "$' + '{#_FAILED_STEPS[@]}" -gt 0 ]; then',
    '      for _failed_step in "$' + '{_FAILED_STEPS[@]}"; do',
    '        if [ "$_failed_step" = "$_step_id" ]; then _already_failed=true; break; fi',
    '      done',
    '    fi',
    '    if [ "$_already_failed" = "false" ]; then _FAILED_STEPS+=("$_step_id"); fi',
    '  else',
    '    exit 1',
    '  fi',
    '  return 0',
    '}',
    '',
    '_count_step_results() {',
    '  local _target="$1"',
    '  local _count=0',
    '  local _i',
    '  for _i in "${!_STEP_RESULTS[@]}"; do',
    '    if [ "${_STEP_RESULTS[$_i]}" = "$_target" ]; then _count=$(( _count + 1 )); fi',
    '  done',
    '  printf \'%s\' "$_count"',
    '}',
    '',
    '# Poll-until helpers (CODEGEN-01)',
    '# NOTE: _poll_visible uses agent-browser "is visible" which fails in headless CI on Linux.',
    '# Use _poll_snapshot_contains as the primary visibility check (grepping the a11y tree).',
    '_poll_visible() {',
    '  local _sel="$1"',
    '  local _step_id="$2"',
    '  local _timeout="${3:-10}"',
    '  local _session="${4:-}"',
    '  local _count=0',
    '  local _result',
    '  while [ "$_count" -lt "$_timeout" ]; do',
    '    if [ -n "$_session" ]; then',
    '      if ! _result=$(agent-browser --session "$_session" is visible "$_sel" 2>/dev/null); then return 2; fi',
    '    else',
    '      if ! _result=$(agent-browser is visible "$_sel" 2>/dev/null); then return 2; fi',
    '    fi',
    '    case "$_result" in',
    '      true) return 0 ;;',
    '      false) ;;',
    '      *) return 2 ;;',
    '    esac',
    '    sleep 1',
    '    _count=$((_count + 1))',
    '  done',
    '  return 1',
    '}',
    '',
    '_poll_not_visible() {',
    '  local _sel="$1"',
    '  local _step_id="$2"',
    '  local _timeout="${3:-10}"',
    '  local _session="${4:-}"',
    '  local _count=0',
    '  local _result',
    '  while [ "$_count" -lt "$_timeout" ]; do',
    '    if [ -n "$_session" ]; then',
    '      if ! _result=$(agent-browser --session "$_session" is visible "$_sel" 2>/dev/null); then return 2; fi',
    '    else',
    '      if ! _result=$(agent-browser is visible "$_sel" 2>/dev/null); then return 2; fi',
    '    fi',
    '    case "$_result" in',
    '      false) return 0 ;;',
    '      true) ;;',
    '      *) return 2 ;;',
    '    esac',
    '    sleep 1',
    '    _count=$((_count + 1))',
    '  done',
    '  return 1',
    '}',
    '',
    '# Status-safe snapshot capture shared by text and polling assertions.',
    '_capture_snapshot() {',
    '  local _session="$' + '{1:-}"',
    '  local _snapshot',
    '  local _first_line',
    '  if [ -n "$_session" ]; then',
    '    if ! _snapshot=$(agent-browser --session "$_session" snapshot 2>/dev/null); then return 2; fi',
    '  else',
    '    if ! _snapshot=$(agent-browser snapshot 2>/dev/null); then return 2; fi',
    '  fi',
    '  _first_line=$(printf \'%s\\n\' "$_snapshot" | sed -n \'1p\')',
    '  if [ "$_first_line" != "(empty page)" ] && ! [[ "$_first_line" =~ ^-[[:space:]]+[a-z][a-z0-9-]*([[:space:]:].*)?$ ]]; then return 2; fi',
    '  printf \'%s\\n\' "$_snapshot"',
    '}',
    '',
    '# Status-safe URL capture. A valid browser URL is exactly one URI line.',
    '_capture_url() {',
    '  local _session="$' + '{1:-}"',
    '  local _url',
    '  if [ -n "$_session" ]; then',
    '    if ! _url=$(agent-browser --session "$_session" get url 2>/dev/null); then return 2; fi',
    '  else',
    '    if ! _url=$(agent-browser get url 2>/dev/null); then return 2; fi',
    '  fi',
    "  case \"$_url\" in *$'\\n'*) return 2 ;; esac",
    '  if ! [[ "$_url" =~ ^[A-Za-z][A-Za-z0-9+.-]*:[^[:space:]]*$ ]]; then return 2; fi',
    '  printf \'%s\\n\' "$_url"',
    '}',
    '',
    '_poll_url_contains() {',
    '  local _value="$1"',
    '  local _step_id="$2"',
    '  local _timeout="${3:-10}"',
    '  local _session="${4:-}"',
    '  local _count=0',
    '  local _url',
    '  while [ "$_count" -lt "$_timeout" ]; do',
    '    if ! _url=$(_capture_url "$_session"); then return 2; fi',
    '    [[ "$_url" == *"$_value"* ]] && return 0',
    '    sleep 1',
    '    _count=$((_count + 1))',
    '  done',
    '  return 1',
    '}',
    '',
    '_poll_url_not_contains() {',
    '  local _value="$1"',
    '  local _step_id="$2"',
    '  local _timeout="${3:-10}"',
    '  local _session="${4:-}"',
    '  local _count=0',
    '  local _url',
    '  while [ "$_count" -lt "$_timeout" ]; do',
    '    if ! _url=$(_capture_url "$_session"); then return 2; fi',
    '    [[ "$_url" != *"$_value"* ]] && return 0',
    '    sleep 1',
    '    _count=$((_count + 1))',
    '  done',
    '  return 1',
    '}',
    '',
    '_poll_or_visible() {',
    '  local _step_id="$1"',
    '  local _timeout="$2"',
    '  local _session="$3"',
    '  shift 3',
    '  local _count=0',
    '  local _result',
    '  local _found',
    '  while [ "$_count" -lt "$_timeout" ]; do',
    '    _found=false',
    '    for _sel in "$@"; do',
    '      if [ -n "$_session" ]; then',
    '        if ! _result=$(agent-browser --session "$_session" is visible "$_sel" 2>/dev/null); then return 2; fi',
    '      else',
    '        if ! _result=$(agent-browser is visible "$_sel" 2>/dev/null); then return 2; fi',
    '      fi',
    '      case "$_result" in',
    '        true) _found=true; break ;;',
    '        false) ;;',
    '        *) return 2 ;;',
    '      esac',
    '    done',
    '    [ "$_found" = "true" ] && return 0',
    '    sleep 1',
    '    _count=$((_count + 1))',
    '  done',
    '  return 1',
    '}',
    '',
    '# Snapshot-based visibility check — workaround for "is visible" returning false in headless CI.',
    '# Polls the a11y tree for a text pattern instead of using Playwright isVisible().',
    '_poll_snapshot_contains() {',
    '  local _pattern="$1"',
    '  local _step_id="$2"',
    '  local _timeout="${3:-10}"',
    '  local _session="${4:-}"',
    '  local _count=0',
    '  local _snapshot',
    '  while [ "$_count" -lt "$_timeout" ]; do',
    '    if ! _snapshot=$(_capture_snapshot "$_session"); then return 2; fi',
    '    if [[ "$_snapshot" == *"$_pattern"* ]]; then',
    '      return 0',
    '    fi',
    '    sleep 1',
    '    _count=$((_count + 1))',
    '  done',
    '  return 1',
    '}',
    '',
  ];
  if (!includeRuntimeStateSupport) {
    var runtimeSupportStart = lines.indexOf('_base64_no_wrap() {');
    var runtimeSupportEnd = lines.indexOf('_xml_attr_escape() {');
    lines.splice(runtimeSupportStart, runtimeSupportEnd - runtimeSupportStart);
  }
  var output = lines.join('\n');
  if (includeVisibilitySupport) output += '\n\n' + generateVisibilitySupport();
  return output;
}

// ---------------------------------------------------------------------------
// BASE_URL normalization (CODEGEN-03)
// ---------------------------------------------------------------------------

/**
 * generateBaseUrlNormalization(variables) — produce trailing-slash normalization lines.
 *
 * For each variable whose uppercased name is exactly BASE_URL or ends with _BASE_URL,
 * emit: VARNAME="${VARNAME%/}"
 *
 * The %/ shell parameter expansion strips one trailing slash (no-op if absent).
 * This prevents double-slash URLs when CI env vars include trailing slashes.
 *
 * Returns: string (multi-line block, or '' if no base URL variables)
 */
function generateBaseUrlNormalization(variables) {
  if (!variables) return '';
  var lines = [];
  var entries = Object.entries(variables);
  for (var i = 0; i < entries.length; i++) {
    var name = entries[i][0].toUpperCase();
    if (name === 'BASE_URL' || name.endsWith('_BASE_URL')) {
      lines.push(name + '="${' + name + '%/}"');
    }
  }
  return lines.length > 0 ? lines.join('\n') : '';
}

function generateBrowserRuntime(browserApps) {
  var apps = browserApps || {};
  var defaultApp = apps.default || 'compiled-flow';
  var lines = [
    '# Owned browser runtime',
    ': "${E2E_BROWSER_RUNTIME:?Error: E2E_BROWSER_RUNTIME must point to e2e-browser-runtime.js}"',
    'if [ "${E2E_BROWSER_RUNTIME#/}" = "$E2E_BROWSER_RUNTIME" ] || [ ! -f "$E2E_BROWSER_RUNTIME" ] || [ -L "$E2E_BROWSER_RUNTIME" ]; then',
    '  echo "ERROR: E2E_BROWSER_RUNTIME must be an absolute regular file"',
    '  exit 2',
    'fi',
    'if [ -z "${E2E_BROWSER_RUN_ID:-}" ]; then',
    '  E2E_BROWSER_RUN_ID=$(node "$E2E_BROWSER_RUNTIME" new-run-id)',
    'fi',
    'E2E_BROWSER_RECEIPT_DIR="${E2E_BROWSER_RECEIPT_DIR:-$_SCREENSHOT_DIR/browser-runtime}"',
    'mkdir -p "$E2E_BROWSER_RECEIPT_DIR"',
    '_E2E_DIAGNOSTIC_ARGS=()',
    '_E2E_DIAGNOSTIC_ACTIVE=false',
    'while IFS= read -r _diagnostic_script; do',
    '  if [ -n "$_diagnostic_script" ]; then',
    '    _E2E_DIAGNOSTIC_ARGS+=(--diagnostic-init-script "$_diagnostic_script")',
    '    _E2E_DIAGNOSTIC_ACTIVE=true',
    '  fi',
    'done <<< "${E2E_DIAGNOSTIC_INIT_SCRIPTS:-}"',
    '_E2E_PROFILE_LIVENESS_ARGS=()',
    'while IFS= read -r _profile_liveness; do',
    '  if [ -n "$_profile_liveness" ]; then',
    '    _E2E_PROFILE_LIVENESS_ARGS+=(--profile-liveness-projection "$_profile_liveness")',
    '  fi',
    'done <<< "${E2E_PROFILE_LIVENESS_PROJECTIONS:-}"',
    '',
    'agent-browser() {',
    '  local _browser_session=""',
    '  local _browser_app=' + singleQuote(defaultApp),
    '  if [ "${1:-}" = "--session" ]; then',
    '    if [ "$#" -lt 3 ]; then',
    '      echo "ERROR: --session requires a session and browser command" >&2',
    '      return 2',
    '    fi',
    '    _browser_session="$2"',
    '    shift 2',
    '    case "$_browser_session" in',
  ];
  var names = Object.keys(apps)
    .filter(function(name) { return name !== 'default'; })
    .sort();
  for (var index = 0; index < names.length; index++) {
    lines.push(
      '      ' + singleQuote(names[index]) + ') _browser_app=' +
        singleQuote(apps[names[index]]) + ' ;;'
    );
  }
  lines.push(
    '      *) _browser_app="$_browser_session" ;;',
    '    esac',
    '  fi',
    '    E2E_COMPILED_BROWSER_ALIAS="$_browser_session" node "$E2E_BROWSER_RUNTIME" \\',
    '      --run-id "$E2E_BROWSER_RUN_ID" \\',
    '      --app "$_browser_app" \\',
    '      --receipt "$E2E_BROWSER_RECEIPT_DIR/$_browser_app.json" \\',
    '      ${_E2E_DIAGNOSTIC_ARGS[@]+"${_E2E_DIAGNOSTIC_ARGS[@]}"} \\',
    '      ${_E2E_PROFILE_LIVENESS_ARGS[@]+"${_E2E_PROFILE_LIVENESS_ARGS[@]}"} \\',
    '      "$@"',
    '}',
    ''
  );
  return lines.join('\n');
}

function generateLocalServiceRuntime() {
  return [
    '# Optional owned local-service runtime',
    '_E2E_SERVICES_ACTIVE=false',
    'E2E_SERVICE_MANIFEST="${E2E_SERVICE_MANIFEST:-}"',
    'if [ -z "$E2E_SERVICE_MANIFEST" ] && [ -f "$(pwd)/.claude/e2e/services.json" ]; then',
    '  E2E_SERVICE_MANIFEST="$(pwd)/.claude/e2e/services.json"',
    'fi',
    '_start_local_services() {',
    '  if [ -z "$E2E_SERVICE_MANIFEST" ]; then return 0; fi',
    '  : "${E2E_SERVICE_RUNTIME:?Error: E2E_SERVICE_RUNTIME must point to e2e-local-service-runtime.js}"',
    '  if [ "${E2E_SERVICE_RUNTIME#/}" = "$E2E_SERVICE_RUNTIME" ] || [ ! -f "$E2E_SERVICE_RUNTIME" ] || [ -L "$E2E_SERVICE_RUNTIME" ]; then',
    '    echo "ERROR: E2E_SERVICE_RUNTIME must be an absolute regular file"',
    '    return 2',
    '  fi',
    '  E2E_SERVICE_STATE_DIR="${E2E_SERVICE_STATE_DIR:-$_SCREENSHOT_DIR/local-services}"',
    '  mkdir -p "$E2E_SERVICE_STATE_DIR"',
    '  E2E_SERVICE_STATE_DIR=$(cd "$E2E_SERVICE_STATE_DIR" && pwd)',
    '  if [ -z "${E2E_SERVICE_RUN_ID:-}" ]; then',
    '    E2E_SERVICE_RUN_ID=$(node "$E2E_SERVICE_RUNTIME" new-run-id)',
    '  fi',
    '  node "$E2E_SERVICE_RUNTIME" preflight --manifest "$E2E_SERVICE_MANIFEST"',
    '  node "$E2E_SERVICE_RUNTIME" start \\',
    '    --manifest "$E2E_SERVICE_MANIFEST" \\',
    '    --run-id "$E2E_SERVICE_RUN_ID" \\',
    '    --state-dir "$E2E_SERVICE_STATE_DIR"',
    '  _E2E_SERVICES_ACTIVE=true',
    '}',
    '',
  ].join('\n');
}

// ---------------------------------------------------------------------------
// Cleanup trap (CI-06)
// ---------------------------------------------------------------------------

/**
 * generateCleanupTrap(steps, finallySteps) — produce cleanup() function and trap cleanup EXIT.
 *
 * Collects unique step.session values from resolved steps.
 * - Single-site (no sessions): emits default agent-browser close
 * - Cross-site (sessions present): emits per-session close for each distinct session
 *
 * SC-1032: if finallySteps is provided, the cleanup() function also runs HTTP finalizer
 * steps before closing the browser. Each http finalizer uses curl. If on_fail=fail
 * and the HTTP call fails, the finalizer sets _FINALIZER_FAILED=1 so the trap
 * can exit with non-zero even when all test steps passed.
 *
 * The trap ensures agent-browser is closed on PASS, FAIL, and unexpected exit.
 * Browser-close failures remain best effort so they do not override the script's
 * exit code. Local-service cleanup failures and on_fail=fail finalizer failures
 * do override an otherwise successful run because they invalidate ownership proof.
 *
 * Returns: string (multi-line bash block)
 */
function generateCleanupTrap(steps, finallySteps, summary) {
  var sessions = [];
  var seen = new Set();
  var hasFinalizers = Array.isArray(finallySteps) && finallySteps.length > 0;
  for (var i = 0; i < steps.length; i++) {
    var s = steps[i].session;
    if (s && !seen.has(s)) {
      seen.add(s);
      sessions.push(s);
    }
  }

  if (!hasFinalizers) {
    var legacyLines = [
      'cleanup() {',
      '  local _prev_exit=$?',
      '  local _service_cleanup_failed=0',
      '  trap - EXIT',
    ];
    if (sessions.length === 0) {
      legacyLines.push('  agent-browser close 2>/dev/null || true');
    } else {
      for (var legacyIndex = 0; legacyIndex < sessions.length; legacyIndex++) {
        legacyLines.push(
          '  agent-browser --session ' + singleQuote(sessions[legacyIndex]) + ' close 2>/dev/null || true'
        );
      }
    }
    legacyLines.push('  if [ "$_E2E_SERVICES_ACTIVE" = true ]; then');
    legacyLines.push('    if ! node "$E2E_SERVICE_RUNTIME" stop --run-id "$E2E_SERVICE_RUN_ID" --state-dir "$E2E_SERVICE_STATE_DIR" >/dev/null; then');
    legacyLines.push('      echo "ERROR: local-service cleanup failed; inspect $E2E_SERVICE_STATE_DIR/$E2E_SERVICE_RUN_ID.json" >&2');
    legacyLines.push('      _service_cleanup_failed=1');
    legacyLines.push('    fi');
    legacyLines.push('  fi');
    legacyLines.push('  if [ "$_service_cleanup_failed" -ne 0 ] && [ "$_prev_exit" -eq 0 ]; then');
    legacyLines.push('    _prev_exit=1');
    legacyLines.push('  fi');
    legacyLines.push('  exit "$_prev_exit"');
    legacyLines.push('}');
    legacyLines.push('trap cleanup EXIT');
    return legacyLines.join('\n');
  }

  var lines = [
    '_FINALIZER_FAILED=0',
    'cleanup() {',
    '  local _prev_exit=$?',
    '  local _service_cleanup_failed=0',
    '  trap - EXIT',
  ];

  if (hasFinalizers) {
    lines.push('  _FINALIZER_TMPDIR=""');
    lines.push('  _FINALIZER_OLD_UMASK=$(umask)');
    lines.push('  umask 077');
    lines.push('  if _FINALIZER_TMPDIR=$(mktemp -d "${TMPDIR:-/tmp}/e2e-finalizer.XXXXXX"); then');
    lines.push('    if ! chmod 700 "$_FINALIZER_TMPDIR"; then');
    lines.push('      rm -rf -- "$_FINALIZER_TMPDIR" 2>/dev/null || true');
    lines.push('      _FINALIZER_TMPDIR=""');
    lines.push('    fi');
    lines.push('  else');
    lines.push('    _FINALIZER_TMPDIR=""');
    lines.push('  fi');
    for (var fi = 0; fi < finallySteps.length; fi++) {
      var fStep = finallySteps[fi];
      if (fStep.type !== 'http') continue;
      var op = fStep.operands;
      var method = op.method || 'POST';
      var recordName = '_record_step_name ' + singleQuote(fStep.id) + ' ' +
        singleQuote(jsonStringContent(fStep.id)) + ' ' + singleQuote(xmlAttrEscape(fStep.id));

      lines.push('  echo ' + doubleQuote('[finally] ' + fStep.id + ': ' + fStep.action));
      lines.push('  _FINALIZER_START=$SECONDS');
      lines.push('  _FINALIZER_OK=true');
      lines.push('  _FINALIZER_FAILURE=""');
      lines.push('  _FINALIZER_URL="${' + op.baseEnv + '-}"');
      lines.push('  if [ -z "$_FINALIZER_URL" ]; then');
      lines.push('    _FINALIZER_OK=false');
      lines.push('    _FINALIZER_FAILURE=' + singleQuote("finalizer base URL environment '" + op.baseEnv + "' is unavailable"));
      lines.push('  else');
      lines.push('    _FINALIZER_URL="${_FINALIZER_URL%/}"');
      lines.push('  fi');
      for (var pi = 0; pi < op.pathSegments.length; pi++) {
        var segment = op.pathSegments[pi];
        lines.push('  if [ "$_FINALIZER_OK" = true ]; then');
        if (segment.literal !== undefined) {
          lines.push('    _FINALIZER_SEGMENT=' + singleQuote(segment.literal));
          lines.push('    _FINALIZER_ENCODED=$(_url_encode "$_FINALIZER_SEGMENT")');
          lines.push('    _FINALIZER_URL="$_FINALIZER_URL/$_FINALIZER_ENCODED"');
        } else {
          lines.push('    _FINALIZER_SEGMENT="${' + segment.runtime_ref.env + '-}"');
          lines.push('    if [ -z "$_FINALIZER_SEGMENT" ]; then');
          lines.push('      _FINALIZER_OK=false');
          lines.push('      _FINALIZER_FAILURE=' + singleQuote(
            "runtime state '" + segment.runtime_ref.state_key + "' is unavailable"
          ));
          lines.push('    else');
          lines.push('      _FINALIZER_ENCODED=$(_url_encode "$_FINALIZER_SEGMENT")');
          lines.push('      _FINALIZER_URL="$_FINALIZER_URL/$_FINALIZER_ENCODED"');
          lines.push('    fi');
        }
        lines.push('  fi');
      }
      lines.push('  _FINALIZER_CONFIG=""');
      lines.push('  _FINALIZER_RESPONSE=""');
      lines.push('  if [ "$_FINALIZER_OK" = true ] && [ -z "$_FINALIZER_TMPDIR" ]; then');
      lines.push('    _FINALIZER_OK=false');
      lines.push('    _FINALIZER_FAILURE=' + singleQuote('private finalizer temporary directory creation failed'));
      lines.push('  fi');
      lines.push('  if [ "$_FINALIZER_OK" = true ]; then');
      lines.push('    _FINALIZER_CONFIG="$_FINALIZER_TMPDIR/' + fi + '.cfg"');
      lines.push('    _FINALIZER_RESPONSE="$_FINALIZER_TMPDIR/' + fi + '.body"');
      lines.push('    if ! (umask 077; : > "$_FINALIZER_CONFIG" && : > "$_FINALIZER_RESPONSE"); then');
      lines.push('      _FINALIZER_OK=false');
      lines.push('      _FINALIZER_FAILURE=' + singleQuote('finalizer temporary artifact creation failed'));
      lines.push('    fi');
      lines.push('  fi');
      var headerKeys = op.headers ? Object.keys(op.headers) : [];
      for (var hi = 0; hi < headerKeys.length; hi++) {
        var hKey = headerKeys[hi];
        var header = op.headers[hKey];
        lines.push('  if [ "$_FINALIZER_OK" = true ]; then');
        lines.push('    if _FINALIZER_HEADER=$(_curl_config_escape "${' + header.runtime_ref.env + '-}"); then');
        lines.push('      if ! printf ' + singleQuote('header = "' + hKey + ': ' + header.scheme + ' %s"\n') +
          ' "$_FINALIZER_HEADER" >> "$_FINALIZER_CONFIG"; then');
        lines.push('        _FINALIZER_OK=false');
        lines.push('        _FINALIZER_FAILURE=' + singleQuote('finalizer credential artifact write failed'));
        lines.push('      fi');
        lines.push('    else');
        lines.push('      _FINALIZER_OK=false');
        lines.push('      _FINALIZER_FAILURE=' + singleQuote('finalizer header contains forbidden control characters'));
        lines.push('    fi');
        lines.push('  fi');
      }
      var curlCommand = 'curl -s -X ' + singleQuote(method) +
        ' --config "$_FINALIZER_CONFIG" -o "$_FINALIZER_RESPONSE" -w ' +
        singleQuote('%{http_code}') + ' "$_FINALIZER_URL"';
      if (op.body) {
        lines.push('  if [ "$_FINALIZER_OK" = true ] && ! _FINALIZER_STATUS=$(printf ' +
          singleQuote('%s') + ' ' + singleQuote(JSON.stringify(op.body)) + ' | ' +
          curlCommand.replace('curl ', 'curl --data-binary @- ') + '); then');
      } else {
        lines.push('  if [ "$_FINALIZER_OK" = true ] && ! _FINALIZER_STATUS=$(' + curlCommand + '); then');
      }
      lines.push('    _FINALIZER_OK=false');
      lines.push('    _FINALIZER_FAILURE=' + singleQuote('HTTP request failed'));
      lines.push('  fi');
      if (op.expectedStatus !== undefined) {
        lines.push('  if [ "$_FINALIZER_OK" = true ] && [ "$_FINALIZER_STATUS" != ' +
          singleQuote(String(op.expectedStatus)) + ' ]; then');
        lines.push('    _FINALIZER_OK=false');
        lines.push('    _FINALIZER_FAILURE=' + singleQuote('HTTP status assertion failed'));
        lines.push('  fi');
      }
      if (op.expectedBodyField && op.expectedBodyField.object && op.expectedBodyField.field &&
          op.expectedBodyField.equals_literal !== undefined) {
        lines.push('  if [ "$_FINALIZER_OK" = true ] && ! _json_top_level_string_equals ' +
          '"$_FINALIZER_RESPONSE" ' + singleQuote(String(op.expectedBodyField.field)) + ' ' +
          singleQuote(String(op.expectedBodyField.equals_literal)) + ' ' +
          singleQuote(String(op.expectedBodyField.object)) + ' 2>/dev/null; then');
        lines.push('    _FINALIZER_OK=false');
        lines.push('    _FINALIZER_FAILURE=' + singleQuote('HTTP response body assertion failed'));
        lines.push('  fi');
      } else if (op.expectedBody && op.expectedBody.field && op.expectedBody.equals !== undefined) {
        lines.push('  if [ "$_FINALIZER_OK" = true ] && ! _json_top_level_string_equals ' +
          '"$_FINALIZER_RESPONSE" ' + singleQuote(String(op.expectedBody.field)) + ' ' +
          singleQuote(String(op.expectedBody.equals)) + ' 2>/dev/null; then');
        lines.push('    _FINALIZER_OK=false');
        lines.push('    _FINALIZER_FAILURE=' + singleQuote('HTTP response body assertion failed'));
        lines.push('  fi');
      }
      lines.push('  if [ -n "$_FINALIZER_CONFIG" ]; then rm -f -- "$_FINALIZER_CONFIG" 2>/dev/null || true; fi');
      lines.push('  if [ -n "$_FINALIZER_RESPONSE" ]; then rm -f -- "$_FINALIZER_RESPONSE" 2>/dev/null || true; fi');
      lines.push('  _FINALIZER_ELAPSED=$(( SECONDS - _FINALIZER_START ))');
      lines.push('  ' + recordName);
      lines.push('  if [ "$_FINALIZER_OK" = true ]; then');
      lines.push('    _STEP_RESULTS+=("pass")');
      lines.push('    _STEP_FAILURES+=("")');
      lines.push('  else');
      lines.push('    _STEP_RESULTS+=("fail")');
      lines.push('    _STEP_FAILURES+=("$_FINALIZER_FAILURE")');
      lines.push('    _FAILED_STEPS+=(' + singleQuote(fStep.id) + ')');
      lines.push('    _FINALIZER_FAILED=1');
      lines.push('  fi');
      lines.push('  _STEP_TIMES+=("$_FINALIZER_ELAPSED")');
    }
    lines.push('  if [ -n "$_FINALIZER_TMPDIR" ]; then rm -rf -- "$_FINALIZER_TMPDIR" 2>/dev/null || true; fi');
    lines.push('  umask "$_FINALIZER_OLD_UMASK"');
  }

  if (sessions.length === 0) {
    lines.push('  agent-browser close 2>/dev/null || true');
  } else {
    for (var j = 0; j < sessions.length; j++) {
      lines.push('  agent-browser --session ' + singleQuote(sessions[j]) + ' close 2>/dev/null || true');
    }
  }
  lines.push('  if [ "$_E2E_SERVICES_ACTIVE" = true ]; then');
  lines.push('    if ! node "$E2E_SERVICE_RUNTIME" stop --run-id "$E2E_SERVICE_RUN_ID" --state-dir "$E2E_SERVICE_STATE_DIR" >/dev/null; then');
  lines.push('      echo "ERROR: local-service cleanup failed; inspect $E2E_SERVICE_STATE_DIR/$E2E_SERVICE_RUN_ID.json" >&2');
  lines.push('      _service_cleanup_failed=1');
  lines.push('    fi');
  lines.push('  fi');

  lines.push('  if [ -n "$METRICS_OUTPUT" ]; then _emit_metrics "$METRICS_OUTPUT"; fi');
  lines.push('  if [ -n "$JUNIT_OUTPUT" ]; then _emit_junit "$JUNIT_OUTPUT"; fi');
  lines.push('  _FINAL_EXIT="$_prev_exit"');
  lines.push('  if [ "$_FINALIZER_FAILED" -ne 0 ] && [ "$_prev_exit" -eq 0 ]; then');
  lines.push('    _FINAL_EXIT=1');
  lines.push('  fi');
  lines.push('  if [ "$_service_cleanup_failed" -ne 0 ] && [ "$_FINAL_EXIT" -eq 0 ]; then');
  lines.push('    _FINAL_EXIT=1');
  lines.push('  fi');
  if (summary) {
    lines.push('  if [ "$' + '{#_FAILED_STEPS[@]}" -gt 0 ]; then');
    lines.push('    echo "FAIL: $' + '{#_FAILED_STEPS[@]} steps failed: $' + '{_FAILED_STEPS[*]}"');
    lines.push('  elif [ "$_FINAL_EXIT" -eq 0 ]; then');
    lines.push('    _not_automated=$(_count_step_results not_automated)');
    lines.push('    _automated_total=$(( ' + summary.totalSteps + ' - ' + summary.skipped + ' - _not_automated ))');
    lines.push('    if [ "$_HAD_RETRIES" = "true" ]; then');
    lines.push('      if [ "$_not_automated" -gt 0 ]; then');
    lines.push('        echo ' + doubleQuote(
      'PASS (FLAKY): ' + summary.flowName + ' ($_automated_total/' + summary.totalSteps +
      ' automated steps passed, ' + summary.skipped + ' skipped, $_not_automated not automated)'
    ));
    lines.push('      else');
    lines.push('      echo ' + singleQuote(
      'PASS (FLAKY): ' + summary.flowName + ' (' + summary.totalSteps + '/' + summary.totalSteps +
      ' steps, ' + summary.skipped + ' skipped)'
    ));
    lines.push('      fi');
    lines.push('    else');
    lines.push('      if [ "$_not_automated" -gt 0 ]; then');
    lines.push('        echo ' + doubleQuote(
      'PASS: ' + summary.flowName + ' ($_automated_total/' + summary.totalSteps +
      ' automated steps passed, ' + summary.skipped + ' skipped, $_not_automated not automated)'
    ));
    lines.push('      else');
    lines.push('      echo ' + singleQuote(
      'PASS: ' + summary.flowName + ' (' + summary.totalSteps + '/' + summary.totalSteps +
      ' steps, ' + summary.skipped + ' skipped)'
    ));
    lines.push('      fi');
    lines.push('    fi');
    lines.push('  fi');
  }
  lines.push('  exit "$_FINAL_EXIT"');
  lines.push('}');
  lines.push('trap cleanup EXIT');

  return lines.join('\n');
}

// ---------------------------------------------------------------------------
// JUnit XML emitter function codegen (FLAG-01)
// ---------------------------------------------------------------------------

/**
 * generateJUnitEmitter(flowName) — produce _emit_junit() bash function.
 *
 * Pre-escapes flowName using xmlAttrEscape at compile time.
 * The emitted bash function:
 *   - Accepts $1 = output file path
 *   - Iterates _STEP_NAMES/_STEP_RESULTS/_STEP_FAILURES/_STEP_TIMES arrays
 *   - Writes valid JUnit XML with printf (no echo, no ESC bytes)
 *   - Step names are pre-escaped at compile time (embedded as literals)
 *   - Failure messages are ANSI-stripped at runtime by _handle_failure
 *
 * Returns: string (multi-line bash block)
 */
function generateJUnitEmitter(flowName) {
  var escapedFlow = xmlAttrEscape(flowName);
  var lines = [
    '_emit_junit() {',
    '  local _out="$1"',
    '  local _total=${#_STEP_NAMES[@]}',
    '  local _failures=0',
    '  local _skipped=0',
    '  local _not_automated=0',
    '  local _duration=$(( SECONDS - _FLOW_START ))',
    '  local _i',
    '  for _i in "${!_STEP_RESULTS[@]}"; do',
    '    case "${_STEP_RESULTS[$_i]}" in',
    '      fail) _failures=$(( _failures + 1 )) ;;',
    '      skip) _skipped=$(( _skipped + 1 )) ;;',
    '      not_automated) _not_automated=$(( _not_automated + 1 )); _skipped=$(( _skipped + 1 )) ;;',
    '    esac',
    '  done',
    '  {',
    '    printf \'<?xml version="1.0" encoding="UTF-8"?>\\n\'',
    '    printf \'<testsuites>\\n\'',
    '    printf \'  <testsuite name="' + escapedFlow + '" tests="%s" failures="%s" skipped="%s" time="%s" timestamp="%s">\\n\' \\',
    '      "$_total" "$_failures" "$_skipped" "$_duration" "$(date -u +%Y-%m-%dT%H:%M:%SZ)"',
    '    for _i in "${!_STEP_NAMES[@]}"; do',
    '      local _sname="${_STEP_XML_NAMES[$_i]}"',
    '      local _sresult="${_STEP_RESULTS[$_i]}"',
    '      local _stime="${_STEP_TIMES[$_i]}"',
    '      local _sfail="${_STEP_FAILURES[$_i]}"',
    '      local _sfail_xml',
    '      _sfail_xml=$(_xml_attr_escape "$_sfail")',
    '      if [ "$_sresult" = "not_automated" ]; then',
    '        printf \'    <testcase classname="' + escapedFlow + '" name="%s" time="%s"><skipped message="not automated"/></testcase>\\n\' \\',
    '          "$_sname" "$_stime"',
    '      elif [ "$_sresult" = "skip" ]; then',
    '        printf \'    <testcase classname="' + escapedFlow + '" name="%s" time="%s"><skipped/></testcase>\\n\' \\',
    '          "$_sname" "$_stime"',
    '      elif [ "$_sresult" = "fail" ]; then',
    '        printf \'    <testcase classname="' + escapedFlow + '" name="%s" time="%s"><failure message="%s"/></testcase>\\n\' \\',
    '          "$_sname" "$_stime" "$_sfail_xml"',
    '      else',
    '        printf \'    <testcase classname="' + escapedFlow + '" name="%s" time="%s"/>\\n\' \\',
    '          "$_sname" "$_stime"',
    '      fi',
    '    done',
    '    printf \'  </testsuite>\\n\'',
    '    printf \'</testsuites>\\n\'',
    '  } > "$_out"',
    '}',
    '',
  ];
  return lines.join('\n');
}

// ---------------------------------------------------------------------------
// Metrics JSON emitter function codegen (FLAKY-02)
// ---------------------------------------------------------------------------

/**
 * generateMetricsEmitter(flowName) — produce _emit_metrics() bash function.
 *
 * Flow name is embedded at compile time (same pattern as _emit_junit).
 * The emitted bash function:
 *   - Accepts $1 = output file path
 *   - Determines pass/fail from ${#_FAILED_STEPS[@]}
 *   - Calculates passed_first_try = (no failures AND no retries)
 *   - Calculates flaky_pass = (no failures AND had retries)
 *   - Iterates _STEP_NAMES/_STEP_RESULTS/_STEP_TIMES/_STEP_FAILURES for per-step entries
 *   - JSON-escapes failure messages (backslash + double-quote + newline)
 *   - Writes JSON matching the locked schema from CONTEXT.md
 *
 * Returns: string (multi-line bash block)
 */
function generateMetricsEmitter(flowName, includeVisibilityResults) {
  var escapedFlow = doubleQuote(jsonStringContent(flowName));
  var lines = [
    '_emit_metrics() {',
    '  local _out="$1"',
    '  local _total=${#_STEP_NAMES[@]}',
    '  local _passed=0',
    '  local _failed=0',
    '  local _skipped=0',
    '  local _not_automated=0',
    '  local _i',
    '  for _i in "${!_STEP_RESULTS[@]}"; do',
    '    case "${_STEP_RESULTS[$_i]}" in',
    '      pass) _passed=$(( _passed + 1 )) ;;',
    '      fail) _failed=$(( _failed + 1 )) ;;',
    '      skip) _skipped=$(( _skipped + 1 )) ;;',
    '      not_automated) _not_automated=$(( _not_automated + 1 )) ;;',
    '    esac',
    '  done',
    '  local _exit_fail=0',
    '  [ "${#_FAILED_STEPS[@]}" -gt 0 ] && _exit_fail=1',
    '  local _passed_first_try=false',
    '  local _flaky_pass=false',
    '  if [ "$_exit_fail" -eq 0 ] && [ "$_HAD_RETRIES" = "false" ]; then',
    '    _passed_first_try=true',
    '  fi',
    '  if [ "$_exit_fail" -eq 0 ] && [ "$_HAD_RETRIES" = "true" ]; then',
    '    _flaky_pass=true',
    '  fi',
    '  {',
    '    printf \'{"flow":"\' ; printf \'%s\' ' + escapedFlow + ' ; printf \'",\'',
    '    printf \'"timestamp":"%s",\' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"',
    '    printf \'"attempt":%s,\' "$_ATTEMPT_NUM"',
    '    printf \'"total_attempts":%s,\' "$_TOTAL_ATTEMPTS"',
    '    printf \'"passed_first_try":%s,\' "$_passed_first_try"',
    '    printf \'"flaky_pass":%s,\' "$_flaky_pass"',
    '    printf \'"steps":[\' ',
    '    local _first=true',
    '    for _i in "${!_STEP_NAMES[@]}"; do',
    '      local _sname="${_STEP_JSON_NAMES[$_i]}"',
    '      local _sresult="${_STEP_RESULTS[$_i]}"',
    '      local _stime="${_STEP_TIMES[$_i]}"',
    '      local _sfail="${_STEP_FAILURES[$_i]}"',
    '      local _sfail_esc',
    '      _sfail_esc=$(_json_escape "$_sfail")',
    '      if [ "$_first" = "true" ]; then _first=false; else printf \',\'; fi',
    '      printf \'{"id":"%s","result":"%s","time_s":%s,"failure_msg":"%s"}\' \\',
    '        "$_sname" "$_sresult" "$_stime" "$_sfail_esc"',
    '    done',
  ];
  if (includeVisibilityResults) {
    lines.push(
      '    printf \'],"visibility_results":[\'',
      '    local _visibility_first=true',
      '    for _i in "${!_VISIBILITY_RESULTS[@]}"; do',
      '      if [ "$_visibility_first" = "true" ]; then _visibility_first=false; else printf \',\'; fi',
      '      printf \'%s\' "${_VISIBILITY_RESULTS[$_i]}"',
      '    done',
      '    printf \'],"summary":{"total":%s,"passed":%s,"failed":%s,"skipped":%s,"not_automated":%s,"flaky_pass":%s}}\' \\',
      '      "$_total" "$_passed" "$_failed" "$_skipped" "$_not_automated" "$_flaky_pass"'
    );
  } else {
    lines.push(
      '    printf \'],"summary":{"total":%s,"passed":%s,"failed":%s,"skipped":%s,"not_automated":%s,"flaky_pass":%s}}\' \\',
      '      "$_total" "$_passed" "$_failed" "$_skipped" "$_not_automated" "$_flaky_pass"'
    );
  }
  lines.push(
    '    printf \'\\n\'',
    '  } > "$_out"',
    '}',
    ''
  );
  return lines.join('\n');
}

// ---------------------------------------------------------------------------
// Footer generation (structured PASS/FAIL summary)
// ---------------------------------------------------------------------------

/**
 * generateFooter(flowName, totalSteps, skipped) — produce structured exit block.
 *
 * If any steps in _FAILED_STEPS: emit "FAIL: N steps failed: list" and exit 1
 * Otherwise: emit "PASS: flowName (N/N steps, M skipped)" and exit 0
 *
 * Returns: string (multi-line bash block)
 */
function generateFooter(flowName, totalSteps, skipped, deferReportsToCleanup) {
  if (deferReportsToCleanup) {
    return [
      '# Exit summary deferred until finalizers complete',
      'if [ ${#_FAILED_STEPS[@]} -gt 0 ]; then',
      '  exit 1',
      'fi',
      'exit 0',
    ].join('\n');
  }

  var lines = [];
  lines.push('# Emit metrics JSON if --metrics-output path was provided (FLAKY-02)');
  lines.push('if [ -n "$METRICS_OUTPUT" ]; then _emit_metrics "$METRICS_OUTPUT"; fi');
  lines.push('# Emit JUnit XML if --junit path was provided (FLAG-01)');
  lines.push('if [ -n "$JUNIT_OUTPUT" ]; then _emit_junit "$JUNIT_OUTPUT"; fi');
  lines.push(
    '# Exit summary',
    'if [ ${#_FAILED_STEPS[@]} -gt 0 ]; then',
    '  echo "FAIL: ${#_FAILED_STEPS[@]} steps failed: ${_FAILED_STEPS[*]}"',
    '  exit 1',
    'fi',
    '_not_automated=$(_count_step_results not_automated)',
    '_automated_total=$(( ' + totalSteps + ' - ' + skipped + ' - _not_automated ))',
    'if [ "$_HAD_RETRIES" = "true" ]; then',
    '  if [ "$_not_automated" -gt 0 ]; then',
    '    echo "PASS (FLAKY): ' + flowName + ' ($_automated_total/' + totalSteps + ' automated steps passed, ' + skipped + ' skipped, $_not_automated not automated)"',
    '  else',
    '    echo "PASS (FLAKY): ' + flowName + ' (' + totalSteps + '/' + totalSteps + ' steps, ' + skipped + ' skipped)"',
    '  fi',
    'else',
    '  if [ "$_not_automated" -gt 0 ]; then',
    '    echo "PASS: ' + flowName + ' ($_automated_total/' + totalSteps + ' automated steps passed, ' + skipped + ' skipped, $_not_automated not automated)"',
    '  else',
    '    echo "PASS: ' + flowName + ' (' + totalSteps + '/' + totalSteps + ' steps, ' + skipped + ' skipped)"',
    '  fi',
    'fi',
    'exit 0'
  );
  return lines.join('\n');
}

// ---------------------------------------------------------------------------
// Per-action bash block generation
// ---------------------------------------------------------------------------

function stepSuccessResult(step) {
  var expects = Array.isArray(step.expects) ? step.expects : [];
  if (expects.length === 0) return 'pass';
  return expects.every(function(expect) { return expect.type === 'not-automated'; })
    ? 'not_automated'
    : 'pass';
}

/**
 * Generate bash lines for a single step action.
 * stepIndex: 0-based index into the resolved steps array
 * totalSteps: total number of steps in the flow
 *
 * Cross-site: when step.session is set, all agent-browser commands get
 * '--session <session>' inserted after 'agent-browser'.
 */
function generateAction(step, stepIndex, totalSteps) {
  var lines = [];
  var n = stepIndex + 1;
  var t = totalSteps;

  // Step progress log — always first
  lines.push('echo ' + doubleQuote('[' + n + '/' + t + '] ' + step.id + ': ' + step.action));

  // Cross-site: compute session prefix for all agent-browser invocations
  var session = step.session;
  var sessionPrefix = session ? '--session ' + singleQuote(session) + ' ' : '';
  var failureSessionArg = session ? ' ' + singleQuote(session) : '';
  // Cross-site: compute base URL variable name (OFFICE_BASE_URL, APP_BASE_URL, etc.)
  var baseUrlVar = session ? '${' + siteBaseUrlVariable(session) + '}' : '${BASE_URL}';

  // Pre-escape step id for XML attribute embedding (compile-time)
  var escapedId = xmlAttrEscape(step.id);
  var quotedId = doubleQuote(step.id);
  var recordStepName = '_record_step_name ' + quotedId + ' ' +
    doubleQuote(jsonStringContent(step.id)) + ' ' + doubleQuote(escapedId);
  var successResult = stepSuccessResult(step);

  switch (step.type) {
    case 'navigate': {
      var urlPath = step.operands.urlPath || step.operands.target;
      var navCmd = 'agent-browser ' + sessionPrefix + 'open "' + baseUrlVar + '"' + singleQuote(urlPath);
      var navMsg = 'navigate to ' + urlPath + ' failed';
      lines.push('_STEP_START=$SECONDS');
      lines.push('_retry=0');
      lines.push('_step_ok=true');
      lines.push('while true; do');
      lines.push('  ' + navCmd + ' && break');
      lines.push('  _retry=$((_retry + 1))');
      lines.push('  if [ "$_retry" -ge "$RETRIES" ] || [ "$RETRIES" -eq 0 ]; then');
      lines.push('    _step_ok=false');
      lines.push('    break');
      lines.push('  fi');
      lines.push('  _HAD_RETRIES=true');
      lines.push('  echo "RETRY [$_retry/$RETRIES]: ' + escapeDoubleQuoted(step.id) + '"');
      lines.push('  sleep 2');
      lines.push('done');
      lines.push('_elapsed=$(( SECONDS - _STEP_START ))');
      lines.push('if [ "$_step_ok" = "true" ]; then');
      lines.push('  ' + recordStepName);
      lines.push('  _STEP_RESULTS+=("' + successResult + '")');
      lines.push('  _STEP_FAILURES+=("")');
      lines.push('  _STEP_TIMES+=("$_elapsed")');
      lines.push('else');
      lines.push('  ' + recordStepName);
      lines.push('  _STEP_RESULTS+=("fail")');
      lines.push('  _STEP_TIMES+=("$_elapsed")');
      lines.push('  _handle_failure ' + quotedId + ' ' + singleQuote(navMsg) + failureSessionArg);
      lines.push('fi');
      break;
    }

    case 'click': {
      var sel = singleQuote(step.operands.selector);
      var cssSel = step.operands.cssSelector || null;
      lines.push('_STEP_START=$SECONDS');
      lines.push('_step_ok=true');

      if (cssSel) {
        // eval-based click: querySelector + .click() — reliable in headless CI
        var jsCss = JSON.stringify(cssSel);
        var clickEval = "(()=>{"
          + "const el=document.querySelector(" + jsCss + ");"
          + "if(!el)throw new Error('element not found: '+" + jsCss + ");"
          + "el.click();"
          + "})()";
        var evalClickCmd = 'agent-browser ' + sessionPrefix + 'eval ' + singleQuote(clickEval);
        lines.push(evalClickCmd + ' || _step_ok=false');
        // Fallback: try Playwright click if eval fails
        lines.push('if [ "$_step_ok" = "false" ]; then');
        lines.push('  agent-browser ' + sessionPrefix + 'click ' + sel + ' && _step_ok=true');
        lines.push('fi');
      } else {
        // Playwright click with retry loop
        lines.push('_retry=0');
        lines.push('while true; do');
        lines.push('  agent-browser ' + sessionPrefix + 'click ' + sel + ' && break');
        lines.push('  _retry=$((_retry + 1))');
        lines.push('  if [ "$_retry" -ge "$RETRIES" ] || [ "$RETRIES" -eq 0 ]; then');
        lines.push('    _step_ok=false');
        lines.push('    break');
        lines.push('  fi');
        lines.push('  _HAD_RETRIES=true');
        lines.push('  echo "RETRY [$_retry/$RETRIES]: ' + escapeDoubleQuoted(step.id) + '"');
        lines.push('  sleep 2');
        lines.push('done');
      }

      lines.push('_elapsed=$(( SECONDS - _STEP_START ))');
      lines.push('if [ "$_step_ok" = "true" ]; then');
      lines.push('  ' + recordStepName);
      lines.push('  _STEP_RESULTS+=("' + successResult + '")');
      lines.push('  _STEP_FAILURES+=("")');
      lines.push('  _STEP_TIMES+=("$_elapsed")');
      lines.push('else');
      lines.push('  ' + recordStepName);
      lines.push('  _STEP_RESULTS+=("fail")');
      lines.push('  _STEP_TIMES+=("$_elapsed")');
      lines.push('  _handle_failure ' + quotedId + ' "click action failed"' + failureSessionArg);
      lines.push('fi');
      break;
    }

    case 'fill': {
      var fillSel = singleQuote(step.operands.selector);
      var fillVal = step.operands.value;
      var fillCssSel = step.operands.cssSelector || null;
      var fillRuntimeRef = step.operands.runtime_ref || null;
      var fillRuntimeEnv = step.operands.runtime_env || null;
      lines.push('_STEP_START=$SECONDS');
      lines.push('_step_ok=true');

      if (fillRuntimeRef) {
        // SC-1032: sensitive fill — read value from stdin (read -s) to avoid argv leakage.
        // The secret name is the runtime_ref var; we read into a local temp var.
        var secretVar = '_E2E_SECRET_' + fillRuntimeRef.toUpperCase();
        lines.push('# Sensitive fill: read value from env (never argv) — SC-1032');
        lines.push('# Use declared env for runtime key ' + fillRuntimeRef + ' (never echo or log it)');
        // If env var is set, use it directly; otherwise prompt via read -s on stderr
        lines.push(secretVar + '="${' + fillRuntimeEnv + ':-}"');
        lines.push('if [ -z "$' + secretVar + '" ]; then');
        lines.push('  # Prompt for secret via stdin (stderr prompt, no echo)');
        lines.push('  printf \'Enter runtime value: \' >&2');
        lines.push('  read -rs ' + secretVar);
        lines.push('  printf \'\\n\' >&2');
        lines.push('fi');
        if (!fillCssSel) throw new Error('runtime_ref fill requires mapping css_selector');
        var sensitiveCss = JSON.stringify(fillCssSel);
        var sensitivePrefix = "(()=>{const el=document.querySelector(" + sensitiveCss + ");" +
          "if(!el)throw new Error('element not found');el.focus();" +
          "const b=atob('";
        var sensitiveSuffix = "');const a=Uint8Array.from(b,c=>c.charCodeAt(0));" +
          "const v=new TextDecoder().decode(a);" +
          "const s=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set;s.call(el,v);" +
          "const t=el._valueTracker;if(t)t.setValue('');" +
          "el.dispatchEvent(new Event('input',{bubbles:true}));" +
          "el.dispatchEvent(new Event('change',{bubbles:true}));})()";
        lines.push('_E2E_SECRET_B64=$(_base64_no_wrap "$' + secretVar + '")');
        lines.push('{ printf \'%s\' ' + singleQuote(sensitivePrefix) +
          '; printf \'%s\' "$_E2E_SECRET_B64"; printf \'%s\' ' + singleQuote(sensitiveSuffix) +
          '; } | agent-browser ' + sessionPrefix + 'eval --stdin || _step_ok=false');
      } else if (fillCssSel) {
        // eval-based fill: nativeInputValueSetter — bypasses React controlled inputs
        var jsFillCss = JSON.stringify(fillCssSel);
        var jsFillVal = JSON.stringify(fillVal);
        var fillEval = "(()=>{" +
          "const el=document.querySelector(" + jsFillCss + ");" +
          "if(!el)throw new Error('element not found: '+" + jsFillCss + ");" +
          "el.focus();" +
          "const s=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set;" +
          "s.call(el," + jsFillVal + ");" +
          "const t=el._valueTracker;if(t)t.setValue('');" +
          "el.dispatchEvent(new Event('input',{bubbles:true}));" +
          "el.dispatchEvent(new Event('change',{bubbles:true}));" +
          "})()";
        var evalFillCmd = 'agent-browser ' + sessionPrefix + 'eval ' + singleQuote(fillEval);
        lines.push(evalFillCmd + ' || _step_ok=false');
      } else {
        // Playwright fill with retry loop
        lines.push('_retry=0');
        lines.push('while true; do');
        lines.push('  agent-browser ' + sessionPrefix + 'fill ' + fillSel + ' ' + singleQuote(fillVal) + ' && break');
        lines.push('  _retry=$((_retry + 1))');
        lines.push('  if [ "$_retry" -ge "$RETRIES" ] || [ "$RETRIES" -eq 0 ]; then');
        lines.push('    _step_ok=false');
        lines.push('    break');
        lines.push('  fi');
        lines.push('  _HAD_RETRIES=true');
        lines.push('  echo "RETRY [$_retry/$RETRIES]: ' + escapeDoubleQuoted(step.id) + '"');
        lines.push('  sleep 2');
        lines.push('done');
      }

      lines.push('_elapsed=$(( SECONDS - _STEP_START ))');
      lines.push('if [ "$_step_ok" = "true" ]; then');
      lines.push('  ' + recordStepName);
      lines.push('  _STEP_RESULTS+=("' + successResult + '")');
      lines.push('  _STEP_FAILURES+=("")');
      lines.push('  _STEP_TIMES+=("$_elapsed")');
      lines.push('else');
      lines.push('  ' + recordStepName);
      lines.push('  _STEP_RESULTS+=("fail")');
      lines.push('  _STEP_TIMES+=("$_elapsed")');
      lines.push('  _handle_failure ' + quotedId + ' "fill action failed"' + failureSessionArg);
      lines.push('fi');
      break;
    }

    case 'capture-url-query': {
      // SC-1032: capture a named query parameter from the current URL.
      // validate: uuid checks exact-one UUID format (RFC 4122 lowercase).
      var capParam = step.operands.param;
      var capAs = step.operands.as;
      var capValidate = step.operands.validate;
      var uuidPattern = '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$';

      lines.push('# uuid validation for capture-url-query');
      lines.push('_STEP_START=$SECONDS');
      lines.push('_step_ok=true');
      var captureJs = "(()=>{const values=new URL(location.href).searchParams.getAll(" +
        JSON.stringify(capParam) + ");if(values.length!==1)throw new Error('expected exactly one query value');" +
        "if(values[0].length===0)throw new Error('query value is empty');return '__E2E_CAPTURE__'+values[0]})()";
      lines.push('_CAPTURE_FAIL_MSG=""');
      lines.push('_capture_result=""');
      lines.push('if ! _capture_result=$(printf \'%s\' ' + singleQuote(captureJs) +
        ' | agent-browser ' + sessionPrefix + 'eval --stdin 2>/dev/null); then');
      lines.push('  _step_ok=false');
      lines.push('  _CAPTURE_FAIL_MSG=' + singleQuote('capture-url-query: browser URL parse failed or query was not exact-one'));
      lines.push('else');
      lines.push('  ' + capAs + '=""');
      lines.push("  case \"$_capture_result\" in *$'\\n'*|*$'\\r'*) _step_ok=false; " +
        '_CAPTURE_FAIL_MSG=' + singleQuote('capture-url-query: multiline browser protocol output') + ' ;; esac');
      lines.push('  case "$_capture_result" in');
      lines.push('    __E2E_CAPTURE__*) ' + capAs + '="${_capture_result#__E2E_CAPTURE__}" ;;');
      lines.push('    *) _step_ok=false; _CAPTURE_FAIL_MSG=' +
        singleQuote('capture-url-query: malformed browser protocol output') + ' ;;');
      lines.push('  esac');
      lines.push('  if [ -z "$' + capAs + '" ]; then');
      lines.push('    _step_ok=false');
      lines.push('    _CAPTURE_FAIL_MSG=' + singleQuote('capture-url-query: param "' + capParam + '" not found in URL'));
      lines.push('  else');
      if (capValidate === 'uuid') {
        // UUID exact-one validation: must match RFC 4122 pattern
        lines.push('    if ! [[ "$' + capAs + '" =~ ' + uuidPattern + ' ]]; then');
        lines.push('      _step_ok=false');
        lines.push('      _CAPTURE_FAIL_MSG=' + singleQuote('capture-url-query: param "' + capParam + '" value is not a valid UUID'));
        lines.push('    fi');
      }
      lines.push('  fi');
      lines.push('fi');
      lines.push('_elapsed=$(( SECONDS - _STEP_START ))');
      lines.push('if [ "$_step_ok" = "true" ]; then');
      lines.push('  ' + recordStepName);
      lines.push('  _STEP_RESULTS+=("' + successResult + '")');
      lines.push('  _STEP_FAILURES+=("")');
      lines.push('  _STEP_TIMES+=("$_elapsed")');
      lines.push('else');
      lines.push('  ' + recordStepName);
      lines.push('  _STEP_RESULTS+=("fail")');
      lines.push('  _STEP_TIMES+=("$_elapsed")');
      // Use the step-local failure message variable if set
      lines.push('  _handle_failure ' + quotedId + ' "${_CAPTURE_FAIL_MSG:-capture-url-query failed}"' + failureSessionArg);
      lines.push('fi');
      break;
    }

    case 'snapshot': {
      lines.push('agent-browser ' + sessionPrefix + 'snapshot');
      lines.push(recordStepName);
      lines.push('_STEP_RESULTS+=("' + successResult + '")');
      lines.push('_STEP_FAILURES+=("")');
      lines.push('_STEP_TIMES+=("0")');
      break;
    }

    case 'wait': {
      lines.push('sleep ' + step.operands.seconds);
      lines.push(recordStepName);
      lines.push('_STEP_RESULTS+=("' + successResult + '")');
      lines.push('_STEP_FAILURES+=("")');
      lines.push('_STEP_TIMES+=("' + step.operands.seconds + '")');
      break;
    }

    case 'verify-external': {
      lines.push('echo ' + doubleQuote('SKIP: ' + step.id + ' -- external verification (no human in CI)'));
      lines.push(recordStepName);
      lines.push('_STEP_RESULTS+=("skip")');
      lines.push('_STEP_FAILURES+=("")');
      lines.push('_STEP_TIMES+=("0")');
      break;
    }

    case 'execute-external': {
      lines.push('echo ' + doubleQuote('SKIP: ' + step.id + ' -- external execution (no human in CI)'));
      lines.push(recordStepName);
      lines.push('_STEP_RESULTS+=("skip")');
      lines.push('_STEP_FAILURES+=("")');
      lines.push('_STEP_TIMES+=("0")');
      break;
    }

    default: {
      lines.push('# Unknown action type: ' + step.type);
      break;
    }
  }

  return lines.join('\n');
}

// ---------------------------------------------------------------------------
// Per-step expect assertion generation
// ---------------------------------------------------------------------------

/**
 * Generate bash assertions for a step's expects array.
 * Handles all Phase 1 and Phase 2 expect types.
 *
 * Visibility assertions use poll-until loops (_poll_visible, _poll_not_visible, etc.)
 * with a deadline counter (CODEGEN-01). Per-step timeout comes from step.timeout
 * (threaded from YAML wait: field via resolver), defaulting to ${WAIT_TIMEOUT:-10}.
 *
 * Cross-site: when step.session is set, poll helpers receive session as argument.
 * Text assertions remain instant checks; URL assertions poll the named session.
 */
function generateExpects(step) {
  if (!step.expects || step.expects.length === 0) {
    return '';
  }

  var lines = [];
  var session = step.session || '';
  var quotedSession = singleQuote(session);
  var quotedId = doubleQuote(step.id);
  var sessionArg = ' ' + quotedSession;
  var failureSessionArg = session ? ' ' + quotedSession : '';

  // Timeout argument: literal number if step.timeout set, else env var default
  var timeoutArg = (step.timeout != null) ? String(step.timeout) : '"${WAIT_TIMEOUT:-10}"';

  function failureCall(message) {
    return '_handle_failure ' + quotedId + ' ' + singleQuote(message) + failureSessionArg;
  }

  function timedFailureCall(prefix, suffix) {
    return '_handle_failure ' + quotedId + ' ' + singleQuote(prefix + ' after ') +
      timeoutArg + singleQuote('s' + (suffix || '')) + failureSessionArg;
  }

  for (var i = 0; i < step.expects.length; i++) {
    var expect = step.expects[i];

    if (expect.type === 'active' || expect.type === 'element-visible') {
      if (expect.cssSelector) {
        lines.push(
          'if _poll_visibility ' + singleQuote(expect.cssSelector) + ' ' +
          singleQuote(expect.visibilityPolicy || 'strict') + ' visible ' + quotedId + ' ' +
          timeoutArg + sessionArg + '; then'
        );
        lines.push('  :');
        lines.push('else');
        lines.push('  _probe_status=$?');
        lines.push('  if [ "$_probe_status" -eq 2 ]; then');
        lines.push('    ' + failureCall('deterministic visibility probe failed for ' + expect.elementName));
        lines.push('  else');
        lines.push('    ' + timedFailureCall(expect.elementName + ' not visible'));
        lines.push('  fi');
        lines.push('fi');
      } else {
        // Backward-compatible direct-codegen input. Resolver-produced mapped visibility
        // always carries cssSelector and therefore cannot reach this legacy branch.
        var a11yPattern = selectorToA11yPattern(expect.selector);
        if (a11yPattern) {
        lines.push('if _poll_snapshot_contains ' + singleQuote(a11yPattern) + ' ' + quotedId + ' ' + timeoutArg + sessionArg + '; then');
        lines.push('  :');
        lines.push('else');
        lines.push('  _probe_status=$?');
        lines.push('  if [ "$_probe_status" -eq 2 ]; then');
        lines.push('    ' + failureCall('agent-browser snapshot probe failed for ' + expect.elementName));
        lines.push('  else');
        lines.push('    ' + timedFailureCall(expect.elementName + ' not in a11y tree'));
        lines.push('  fi');
        lines.push('fi');
        } else {
        // Fallback to _poll_visible for non-convertible selectors (e.g., css=)
        var sel = singleQuote(expect.selector);
        lines.push('if _poll_visible ' + sel + ' ' + quotedId + ' ' + timeoutArg + sessionArg + '; then');
        lines.push('  :');
        lines.push('else');
        lines.push('  _probe_status=$?');
        lines.push('  if [ "$_probe_status" -eq 2 ]; then');
        lines.push('    ' + failureCall('agent-browser visibility probe failed for ' + expect.elementName));
        lines.push('  else');
        lines.push('    ' + timedFailureCall(expect.elementName + ' not visible'));
        lines.push('  fi');
        lines.push('fi');
        }
      }

    } else if (expect.type === 'element-not-visible') {
      var negativeHelper = expect.cssSelector ? '_poll_visibility' : '_poll_not_visible';
      var negativeArgs = expect.cssSelector
        ? singleQuote(expect.cssSelector) + ' ' + singleQuote(expect.visibilityPolicy || 'strict') +
          ' not-visible ' + quotedId + ' ' + timeoutArg + sessionArg
        : singleQuote(expect.selector) + ' ' + quotedId + ' ' + timeoutArg + sessionArg;
      lines.push('if ' + negativeHelper + ' ' + negativeArgs + '; then');
      lines.push('  :');
      lines.push('else');
      lines.push('  _probe_status=$?');
      lines.push('  if [ "$_probe_status" -eq 2 ]; then');
      lines.push('    ' + failureCall(
        (expect.cssSelector ? 'deterministic visibility probe failed for ' : 'agent-browser visibility probe failed for ') +
        expect.elementName
      ));
      lines.push('  else');
      lines.push('    ' + timedFailureCall(expect.elementName + ' still visible', ' (expected not visible)'));
      lines.push('  fi');
      lines.push('fi');

    } else if (expect.type === 'element-enabled' || expect.type === 'element-disabled') {
      var expectedState = expect.type === 'element-enabled' ? 'enabled' : 'disabled';
      lines.push(
        'if _poll_enabled_state ' + singleQuote(expect.cssSelector) + ' ' +
        singleQuote(expect.visibilityPolicy || 'strict') + ' ' + expectedState + ' ' + quotedId +
        ' ' + timeoutArg + sessionArg + '; then'
      );
      lines.push('  :');
      lines.push('else');
      lines.push('  _probe_status=$?');
      lines.push('  if [ "$_probe_status" -eq 2 ]; then');
      lines.push('    ' + failureCall('deterministic visibility/state probe failed for ' + expect.elementName));
      lines.push('  else');
      lines.push('    ' + timedFailureCall(expect.elementName + ' not ' + expectedState));
      lines.push('  fi');
      lines.push('fi');

    } else if (expect.type === 'url-contains') {
      // Poll until URL contains value (CODEGEN-01)
      lines.push('if _poll_url_contains ' + singleQuote(expect.value) + ' ' + quotedId + ' ' + timeoutArg + sessionArg + '; then');
      lines.push('  :');
      lines.push('else');
      lines.push('  _probe_status=$?');
      lines.push('  if [ "$_probe_status" -eq 2 ]; then');
      lines.push('    ' + failureCall('agent-browser URL probe failed'));
      lines.push('  else');
      lines.push('    ' + timedFailureCall('url does not contain ' + expect.value));
      lines.push('  fi');
      lines.push('fi');

    } else if (expect.type === 'url-not-contains') {
      // Poll until URL does NOT contain value — redirects (e.g., login → dashboard) need time
      lines.push('if _poll_url_not_contains ' + singleQuote(expect.value) + ' ' + quotedId + ' ' + timeoutArg + sessionArg + '; then');
      lines.push('  :');
      lines.push('else');
      lines.push('  _probe_status=$?');
      lines.push('  if [ "$_probe_status" -eq 2 ]; then');
      lines.push('    ' + failureCall('agent-browser URL probe failed'));
      lines.push('  else');
      lines.push('    ' + timedFailureCall('url still contains ' + expect.value));
      lines.push('  fi');
      lines.push('fi');

    } else if (expect.type === 'text-visible') {
      // Instant check — snapshot + grep is too heavy for polling.
      var quotedText = singleQuote(expect.text);
      lines.push('if ! _snapshot=$(_capture_snapshot ' + quotedSession + '); then');
      lines.push('  ' + failureCall('agent-browser snapshot failed'));
      lines.push('elif ! [[ "$_snapshot" == *' + quotedText + '* ]]; then');
      lines.push('  ' + failureCall("text '" + expect.text + "' not found on page"));
      lines.push('fi');

    } else if (expect.type === 'text-not-visible') {
      // Inverted snapshot grep — fail if the text IS found on page.
      var quotedText = singleQuote(expect.text);
      lines.push('if ! _snapshot=$(_capture_snapshot ' + quotedSession + '); then');
      lines.push('  ' + failureCall('agent-browser snapshot failed'));
      lines.push('elif [[ "$_snapshot" == *' + quotedText + '* ]]; then');
      lines.push('  ' + failureCall("text '" + expect.text + "' should NOT be on page but was found"));
      lines.push('fi');

    } else if (expect.type === 'or-visible') {
      var elements = expect.elements;
      var elemNames = elements.map(function(e) { return e.elementName; });
      var mappedOr = elements.every(function(element) { return Boolean(element.cssSelector); });
      var selectorArgs = mappedOr
        ? elements.map(function(element) {
          return singleQuote(element.cssSelector) + ' ' + singleQuote(element.visibilityPolicy || 'strict');
        }).join(' ')
        : elements.map(function(element) { return singleQuote(element.selector); }).join(' ');
      var orHelper = mappedOr ? '_poll_or_visibility' : '_poll_or_visible';
      lines.push('if ' + orHelper + ' ' + quotedId + ' ' + timeoutArg + ' ' + quotedSession + ' ' + selectorArgs + '; then');
      lines.push('  :');
      lines.push('else');
      lines.push('  _probe_status=$?');
      lines.push('  if [ "$_probe_status" -eq 2 ]; then');
      lines.push('    ' + failureCall(
        (mappedOr ? 'deterministic visibility probe failed for ' : 'agent-browser visibility probe failed for ') +
        elemNames.join(' or ')
      ));
      lines.push('  else');
      lines.push('    ' + timedFailureCall('neither ' + elemNames.join(' nor ') + ' visible'));
      lines.push('  fi');
      lines.push('fi');

    } else if (expect.type === 'not-automated') {
      // Deliberately no runtime assertion: this is reported in compile/runner summaries only.
      continue;
    } else if (expect.type === 'deferred') {
      throw new Error('Unsupported deferred expect reached codegen: ' + expect.raw);
    }
  }

  return lines.length > 0 ? lines.join('\n') : '';
}

// ---------------------------------------------------------------------------
// Main generate() function
// ---------------------------------------------------------------------------

/**
 * generate(resolved, flowName, meta) — produce a complete bash script string.
 *
 * resolved: { name, description, variables?, steps: ResolvedStep[] }
 * flowName: string used in PASS/FAIL summary messages
 * meta:     optional provenance metadata (see generateHeader)
 * Returns:  string (complete bash script content)
 */
function generate(resolved, flowName, meta) {
  var steps = resolved.steps || [];
  var totalSteps = steps.length;
  var skipped = 0;
  var hasFinalizers = Array.isArray(resolved.finally) && resolved.finally.length > 0;
  var hasRuntimeState = hasFinalizers ||
    Boolean(resolved.runtimeValues && Object.keys(resolved.runtimeValues).length > 0) ||
    steps.some(function(step) { return step.type === 'capture-url-query'; });
  var hasMappedVisibility = steps.some(function(step) {
    return (step.expects || []).some(function(expect) {
      if (expect.type === 'or-visible') {
        return Array.isArray(expect.elements) && expect.elements.every(function(element) {
          return Boolean(element.cssSelector);
        });
      }
      return Boolean(expect.cssSelector) && [
        'active',
        'element-visible',
        'element-not-visible',
        'element-enabled',
        'element-disabled',
      ].includes(expect.type);
    });
  });

  // Count verify-external and execute-external steps for PASS summary
  for (var i = 0; i < steps.length; i++) {
    if (steps[i].type === 'verify-external' || steps[i].type === 'execute-external') {
      skipped++;
    }
  }

  var parts = [];

  // 1. Shell header (with optional provenance metadata)
  parts.push(generateHeader(meta));

  // 2. Runtime flag parsing — BEFORE variable block (flags consume $1/$2 positional args)
  parts.push(generateRuntimeFlagBlock());

  // 3. Variable handling — generateVariables() adds block when present
  var varBlock = generateVariables(resolved.variables, flowName);
  if (varBlock) {
    parts.push(varBlock);
    parts.push('');
  }

  // 3b. SC-1032: Runtime values (required env vars — never positional args)
  var runtimeValuesBlock = generateRuntimeValuesBlock(resolved.runtimeValues, flowName);
  if (runtimeValuesBlock) {
    parts.push(runtimeValuesBlock);
    parts.push('');
  }

  // 4. BASE_URL normalization — strips trailing slash from all *_BASE_URL variables (CODEGEN-03)
  var normBlock = generateBaseUrlNormalization(resolved.variables);
  if (normBlock) {
    parts.push(normBlock);
    parts.push('');
  }

  // 5. Runtime support functions (_handle_failure, _FAILED_STEPS, poll helpers)
  parts.push(generateRuntimeSupport(hasRuntimeState, hasMappedVisibility));

  // 5a. Route generated browser calls through the shared owned runtime.
  parts.push(generateBrowserRuntime(resolved.browserApps));

  // 5b. Configure optional local services before installing the cleanup trap.
  parts.push(generateLocalServiceRuntime());

  // 5c. JUnit emitter function (FLAG-01) — defined here, called in footer
  parts.push(generateJUnitEmitter(flowName));

  // 5d. Metrics emitter function (FLAKY-02) — defined here, called in footer
  parts.push(generateMetricsEmitter(flowName, hasMappedVisibility));

  // 6. Cleanup trap — registers agent-browser close on EXIT (CI-06)
  // SC-1032: pass finallySteps so cleanup() runs HTTP finalizers before browser close
  parts.push(generateCleanupTrap(steps, resolved.finally, {
    flowName: flowName,
    totalSteps: totalSteps,
    skipped: skipped,
  }));
  parts.push('_start_local_services');
  parts.push('');

  // 7. Per-step action blocks
  for (var si = 0; si < steps.length; si++) {
    var step = steps[si];

    var actionBlock = generateAction(step, si, totalSteps);
    parts.push(actionBlock);

    var expectBlock = generateExpects(step);
    if (expectBlock) {
      parts.push(expectBlock);
    }

    // Post-step screenshot capture (flow YAML screenshot: true)
    if (step.screenshot) {
      var session = step.session;
      var sessionPrefix = session ? '--session ' + singleQuote(session) + ' ' : '';
      var screenshotName = artifactFileComponent(step.id);
      parts.push(
        'agent-browser ' + sessionPrefix + 'screenshot "$_SCREENSHOT_DIR/' + screenshotName +
        '.png" 2>/dev/null || echo ' + doubleQuote('(screenshot ' + step.id + ' skipped)')
      );
    }

    parts.push('');
  }

  // 8. Structured footer (replaces inline PASS/exit 0)
  parts.push(generateFooter(flowName, totalSteps, skipped, hasFinalizers));

  return parts.join('\n');
}

// ---------------------------------------------------------------------------
// Exports
// ---------------------------------------------------------------------------

module.exports = {
  generate: generate,
  generateHeader: generateHeader,
  singleQuote: singleQuote,
  selectorToA11yPattern: selectorToA11yPattern,
  generateVariables: generateVariables,
  generateRuntimeValuesBlock: generateRuntimeValuesBlock,
  generateBaseUrlNormalization: generateBaseUrlNormalization,
  generateBrowserRuntime: generateBrowserRuntime,
  generateLocalServiceRuntime: generateLocalServiceRuntime,
  generateCleanupTrap: generateCleanupTrap,
  generateJUnitEmitter: generateJUnitEmitter,
  generateMetricsEmitter: generateMetricsEmitter,
  generateRuntimeFlagBlock: generateRuntimeFlagBlock,
  generateRuntimeSupport: generateRuntimeSupport,
  generateFooter: generateFooter,
  xmlAttrEscape: xmlAttrEscape,
};
