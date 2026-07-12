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
 * Returns: string (multi-line bash block)
 */
function generateRuntimeSupport() {
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
    '  if [ "$_first_line" != "(empty page)" ] && ! printf \'%s\\n\' "$_first_line" | grep -Eq \'^-[[:space:]]+[a-z][a-z0-9-]*([[:space:]:].*)?$\'; then return 2; fi',
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
    '  if ! printf \'%s\\n\' "$_url" | grep -Eq \'^[A-Za-z][A-Za-z0-9+.-]*:[^[:space:]]*$\'; then return 2; fi',
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
    '    if printf \'%s\\n\' "$_snapshot" | grep -Fq "$_pattern"; then',
    '      return 0',
    '    fi',
    '    sleep 1',
    '    _count=$((_count + 1))',
    '  done',
    '  return 1',
    '}',
    '',
  ];
  return lines.join('\n');
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

// ---------------------------------------------------------------------------
// Cleanup trap (CI-06)
// ---------------------------------------------------------------------------

/**
 * generateCleanupTrap(steps) — produce cleanup() function and trap cleanup EXIT.
 *
 * Collects unique step.session values from resolved steps.
 * - Single-site (no sessions): emits default agent-browser close
 * - Cross-site (sessions present): emits per-session close for each distinct session
 *
 * The trap ensures agent-browser is closed on PASS, FAIL, and unexpected exit.
 * Uses || true to prevent cleanup failure from overriding the script's exit code.
 *
 * Returns: string (multi-line bash block)
 */
function generateCleanupTrap(steps) {
  // Collect distinct session names (excluding falsy/empty)
  var sessions = [];
  var seen = new Set();
  for (var i = 0; i < steps.length; i++) {
    var s = steps[i].session;
    if (s && !seen.has(s)) {
      seen.add(s);
      sessions.push(s);
    }
  }

  var lines = ['cleanup() {'];

  if (sessions.length === 0) {
    // Single-site: default session close
    lines.push('  agent-browser close 2>/dev/null || true');
  } else {
    // Cross-site: close each named session
    for (var j = 0; j < sessions.length; j++) {
      lines.push('  agent-browser --session ' + singleQuote(sessions[j]) + ' close 2>/dev/null || true');
    }
  }

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
    '  local _duration=$(( SECONDS - _FLOW_START ))',
    '  local _i',
    '  for _i in "${!_STEP_RESULTS[@]}"; do',
    '    case "${_STEP_RESULTS[$_i]}" in',
    '      fail) _failures=$(( _failures + 1 )) ;;',
    '      skip) _skipped=$(( _skipped + 1 )) ;;',
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
    '      if [ "$_sresult" = "skip" ]; then',
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
function generateMetricsEmitter(flowName) {
  var escapedFlow = doubleQuote(jsonStringContent(flowName));
  var lines = [
    '_emit_metrics() {',
    '  local _out="$1"',
    '  local _total=${#_STEP_NAMES[@]}',
    '  local _passed=0',
    '  local _failed=0',
    '  local _skipped=0',
    '  local _i',
    '  for _i in "${!_STEP_RESULTS[@]}"; do',
    '    case "${_STEP_RESULTS[$_i]}" in',
    '      pass) _passed=$(( _passed + 1 )) ;;',
    '      fail) _failed=$(( _failed + 1 )) ;;',
    '      skip) _skipped=$(( _skipped + 1 )) ;;',
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
    '    printf \'],"summary":{"total":%s,"passed":%s,"failed":%s,"skipped":%s,"flaky_pass":%s}}\' \\',
    '      "$_total" "$_passed" "$_failed" "$_skipped" "$_flaky_pass"',
    '    printf \'\\n\'',
    '  } > "$_out"',
    '}',
    '',
  ];
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
function generateFooter(flowName, totalSteps, skipped) {
  var lines = [
    '# Emit metrics JSON if --metrics-output path was provided (FLAKY-02)',
    'if [ -n "$METRICS_OUTPUT" ]; then _emit_metrics "$METRICS_OUTPUT"; fi',
    '# Emit JUnit XML if --junit path was provided (FLAG-01)',
    'if [ -n "$JUNIT_OUTPUT" ]; then _emit_junit "$JUNIT_OUTPUT"; fi',
    '# Exit summary',
    'if [ ${#_FAILED_STEPS[@]} -gt 0 ]; then',
    '  echo "FAIL: ${#_FAILED_STEPS[@]} steps failed: ${_FAILED_STEPS[*]}"',
    '  exit 1',
    'fi',
    'if [ "$_HAD_RETRIES" = "true" ]; then',
    '  echo "PASS (FLAKY): ' + flowName + ' (' + totalSteps + '/' + totalSteps + ' steps, ' + skipped + ' skipped)"',
    'else',
    '  echo "PASS: ' + flowName + ' (' + totalSteps + '/' + totalSteps + ' steps, ' + skipped + ' skipped)"',
    'fi',
    'exit 0',
  ];
  return lines.join('\n');
}

// ---------------------------------------------------------------------------
// Per-action bash block generation
// ---------------------------------------------------------------------------

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
      lines.push('  _STEP_RESULTS+=("pass")');
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
      lines.push('  _STEP_RESULTS+=("pass")');
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
      lines.push('_STEP_START=$SECONDS');
      lines.push('_step_ok=true');

      if (fillCssSel) {
        // eval-based fill: nativeInputValueSetter — bypasses React controlled inputs
        var jsFillCss = JSON.stringify(fillCssSel);
        var jsFillVal = JSON.stringify(fillVal);
        var fillEval = "(()=>{"
          + "const el=document.querySelector(" + jsFillCss + ");"
          + "if(!el)throw new Error('element not found: '+" + jsFillCss + ");"
          + "el.focus();"
          + "const s=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set;"
          + "s.call(el," + jsFillVal + ");"
          + "const t=el._valueTracker;if(t)t.setValue('');"
          + "el.dispatchEvent(new Event('input',{bubbles:true}));"
          + "el.dispatchEvent(new Event('change',{bubbles:true}));"
          + "})()";
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
      lines.push('  _STEP_RESULTS+=("pass")');
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

    case 'snapshot': {
      lines.push('agent-browser ' + sessionPrefix + 'snapshot');
      lines.push(recordStepName);
      lines.push('_STEP_RESULTS+=("pass")');
      lines.push('_STEP_FAILURES+=("")');
      lines.push('_STEP_TIMES+=("0")');
      break;
    }

    case 'wait': {
      lines.push('sleep ' + step.operands.seconds);
      lines.push(recordStepName);
      lines.push('_STEP_RESULTS+=("pass")');
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
      // Prefer snapshot-based check (agent-browser "is visible" fails in headless CI on Linux)
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

    } else if (expect.type === 'element-not-visible') {
      // Poll until element is not visible (inverted logic — CODEGEN-01 Pitfall 4)
      // Keep _poll_not_visible — headless CI issue is less critical for "not visible" checks
      var sel = singleQuote(expect.selector);
      lines.push('if _poll_not_visible ' + sel + ' ' + quotedId + ' ' + timeoutArg + sessionArg + '; then');
      lines.push('  :');
      lines.push('else');
      lines.push('  _probe_status=$?');
      lines.push('  if [ "$_probe_status" -eq 2 ]; then');
      lines.push('    ' + failureCall('agent-browser visibility probe failed for ' + expect.elementName));
      lines.push('  else');
      lines.push('    ' + timedFailureCall(expect.elementName + ' still visible', ' (expected not visible)'));
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
      lines.push('elif ! echo "$_snapshot" | grep -qF ' + quotedText + '; then');
      lines.push('  ' + failureCall("text '" + expect.text + "' not found on page"));
      lines.push('fi');

    } else if (expect.type === 'text-not-visible') {
      // Inverted snapshot grep — fail if the text IS found on page.
      var quotedText = singleQuote(expect.text);
      lines.push('if ! _snapshot=$(_capture_snapshot ' + quotedSession + '); then');
      lines.push('  ' + failureCall('agent-browser snapshot failed'));
      lines.push('elif echo "$_snapshot" | grep -qF ' + quotedText + '; then');
      lines.push('  ' + failureCall("text '" + expect.text + "' should NOT be on page but was found"));
      lines.push('fi');

    } else if (expect.type === 'or-visible') {
      // Poll until either element is visible (CODEGEN-01)
      var elements = expect.elements;
      var elemNames = elements.map(function(e) { return e.elementName; });
      var selectorArgs = elements.map(function(e) { return singleQuote(e.selector); }).join(' ');
      lines.push('if _poll_or_visible ' + quotedId + ' ' + timeoutArg + ' ' + quotedSession + ' ' + selectorArgs + '; then');
      lines.push('  :');
      lines.push('else');
      lines.push('  _probe_status=$?');
      lines.push('  if [ "$_probe_status" -eq 2 ]; then');
      lines.push('    ' + failureCall('agent-browser visibility probe failed for ' + elemNames.join(' or ')));
      lines.push('  else');
      lines.push('    ' + timedFailureCall('neither ' + elemNames.join(' nor ') + ' visible'));
      lines.push('  fi');
      lines.push('fi');

    } else if (expect.type === 'deferred') {
      lines.push('echo "TODO: expect \'' + expect.raw + '\' not compiled (Phase 2)"');
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

  // 4. BASE_URL normalization — strips trailing slash from all *_BASE_URL variables (CODEGEN-03)
  var normBlock = generateBaseUrlNormalization(resolved.variables);
  if (normBlock) {
    parts.push(normBlock);
    parts.push('');
  }

  // 5. Runtime support functions (_handle_failure, _FAILED_STEPS, poll helpers)
  parts.push(generateRuntimeSupport());

  // 5b. JUnit emitter function (FLAG-01) — defined here, called in footer
  parts.push(generateJUnitEmitter(flowName));

  // 5c. Metrics emitter function (FLAKY-02) — defined here, called in footer
  parts.push(generateMetricsEmitter(flowName));

  // 6. Cleanup trap — registers agent-browser close on EXIT (CI-06)
  parts.push(generateCleanupTrap(steps));
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
  parts.push(generateFooter(flowName, totalSteps, skipped));

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
  generateBaseUrlNormalization: generateBaseUrlNormalization,
  generateCleanupTrap: generateCleanupTrap,
  generateJUnitEmitter: generateJUnitEmitter,
  generateMetricsEmitter: generateMetricsEmitter,
  generateRuntimeFlagBlock: generateRuntimeFlagBlock,
  generateRuntimeSupport: generateRuntimeSupport,
  generateFooter: generateFooter,
  xmlAttrEscape: xmlAttrEscape,
};
