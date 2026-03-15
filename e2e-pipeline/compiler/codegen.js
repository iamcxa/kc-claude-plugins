'use strict';

/**
 * codegen.js — Transforms resolved compiler data into bash script content.
 *
 * Input:  resolved object from resolver.js (steps with operands and selectors)
 * Output: complete bash script as string
 *
 * All agent-browser commands use positional args (not flags) per commands.md.
 * Selectors are wrapped in single quotes using the singleQuote() escape pattern.
 * Visibility assertions use stdout capture (|| true), never exit code.
 *
 * Cross-site support (Phase 2 Plan 02):
 *   - When step.session is set, all agent-browser commands get --session <name> prefix
 *   - Navigate in cross-site uses ${SITE_BASE_URL} (e.g., ${OFFICE_BASE_URL})
 */

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
 * Parses --continue-on-error and --retries N at script runtime.
 * Must appear BEFORE variable assignment (uses shift/set -- to consume flags).
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
 * _handle_failure "step_id" "msg":
 *   - Echoes FAIL line
 *   - If CONTINUE_ON_ERROR=true: accumulates step_id into _FAILED_STEPS
 *   - If CONTINUE_ON_ERROR=false: calls exit 1 (v1.0 backward compat)
 *   - Always returns 0 so the || operator satisfies set -e
 *
 * Poll helpers (_poll_visible, _poll_not_visible, _poll_url_contains, _poll_or_visible):
 *   - Use local variables (bash 3.2 safe)
 *   - Use $((_count + 1)) arithmetic (no let, no (( )))
 *   - Use sleep 1 between iterations
 *   - Use 2>/dev/null on agent-browser calls
 *   - Use || true after $() capture to prevent set -e abort
 *   - Return 1 on deadline (callers use || _handle_failure)
 *
 * Returns: string (multi-line bash block)
 */
function generateRuntimeSupport() {
  var lines = [
    '# Failure accumulator',
    '_FAILED_STEPS=()',
    '_handle_failure() {',
    '  local _step_id="$1"',
    '  local _msg="$2"',
    '  echo "FAIL: $_step_id -- $_msg"',
    '  if [ "$CONTINUE_ON_ERROR" = "true" ]; then',
    '    _FAILED_STEPS+=("$_step_id")',
    '  else',
    '    exit 1',
    '  fi',
    '  return 0',
    '}',
    '',
    '# Poll-until helpers (CODEGEN-01)',
    '_poll_visible() {',
    '  local _sel="$1"',
    '  local _step_id="$2"',
    '  local _timeout="${3:-10}"',
    '  local _session="${4:-}"',
    '  local _count=0',
    '  local _result',
    '  while [ "$_count" -lt "$_timeout" ]; do',
    '    if [ -n "$_session" ]; then',
    '      _result=$(agent-browser --session "$_session" is visible "$_sel" 2>/dev/null) || true',
    '    else',
    '      _result=$(agent-browser is visible "$_sel" 2>/dev/null) || true',
    '    fi',
    '    [ "$_result" = "true" ] && return 0',
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
    '      _result=$(agent-browser --session "$_session" is visible "$_sel" 2>/dev/null) || true',
    '    else',
    '      _result=$(agent-browser is visible "$_sel" 2>/dev/null) || true',
    '    fi',
    '    [ "$_result" = "false" ] && return 0',
    '    sleep 1',
    '    _count=$((_count + 1))',
    '  done',
    '  return 1',
    '}',
    '',
    '_poll_url_contains() {',
    '  local _value="$1"',
    '  local _step_id="$2"',
    '  local _timeout="${3:-10}"',
    '  local _count=0',
    '  local _url',
    '  while [ "$_count" -lt "$_timeout" ]; do',
    '    _url=$(agent-browser get url 2>/dev/null) || true',
    '    [[ "$_url" == *"$_value"* ]] && return 0',
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
    '        _result=$(agent-browser --session "$_session" is visible "$_sel" 2>/dev/null) || true',
    '      else',
    '        _result=$(agent-browser is visible "$_sel" 2>/dev/null) || true',
    '      fi',
    '      if [ "$_result" = "true" ]; then _found=true; break; fi',
    '    done',
    '    [ "$_found" = "true" ] && return 0',
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
  var seen = {};
  for (var i = 0; i < steps.length; i++) {
    var s = steps[i].session;
    if (s && !seen[s]) {
      seen[s] = true;
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
      lines.push('  agent-browser --session ' + sessions[j] + ' close 2>/dev/null || true');
    }
  }

  lines.push('}');
  lines.push('trap cleanup EXIT');

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
    '# Exit summary',
    'if [ ${#_FAILED_STEPS[@]} -gt 0 ]; then',
    '  echo "FAIL: ${#_FAILED_STEPS[@]} steps failed: ${_FAILED_STEPS[*]}"',
    '  exit 1',
    'fi',
    'echo "PASS: ' + flowName + ' (' + totalSteps + '/' + totalSteps + ' steps, ' + skipped + ' skipped)"',
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
  lines.push('echo "[' + n + '/' + t + '] ' + step.id + ': ' + step.action + '"');

  // Cross-site: compute session prefix for all agent-browser invocations
  var session = step.session;
  var sessionPrefix = session ? '--session ' + session + ' ' : '';
  // Cross-site: compute base URL variable name (OFFICE_BASE_URL, APP_BASE_URL, etc.)
  var baseUrlVar = session ? '${' + session.toUpperCase() + '_BASE_URL}' : '${BASE_URL}';

  switch (step.type) {
    case 'navigate': {
      var urlPath = step.operands.urlPath || step.operands.target;
      var navCmd = 'agent-browser ' + sessionPrefix + 'open "' + baseUrlVar + urlPath + '"';
      var navMsg = 'navigate to ' + urlPath + ' failed';
      lines.push('_retry=0');
      lines.push('while true; do');
      lines.push('  ' + navCmd + ' && break');
      lines.push('  _retry=$((_retry + 1))');
      lines.push('  if [ "$_retry" -ge "$RETRIES" ] || [ "$RETRIES" -eq 0 ]; then');
      lines.push('    _handle_failure "' + step.id + '" "' + navMsg + '"');
      lines.push('    break');
      lines.push('  fi');
      lines.push('  echo "RETRY [$_retry/$RETRIES]: ' + step.id + '"');
      lines.push('  sleep 2');
      lines.push('done');
      break;
    }

    case 'click': {
      var sel = singleQuote(step.operands.selector);
      var clickCmd = 'agent-browser ' + sessionPrefix + 'click ' + sel;
      lines.push('_retry=0');
      lines.push('while true; do');
      lines.push('  ' + clickCmd + ' && break');
      lines.push('  _retry=$((_retry + 1))');
      lines.push('  if [ "$_retry" -ge "$RETRIES" ] || [ "$RETRIES" -eq 0 ]; then');
      lines.push('    _handle_failure "' + step.id + '" "click action failed"');
      lines.push('    break');
      lines.push('  fi');
      lines.push('  echo "RETRY [$_retry/$RETRIES]: ' + step.id + '"');
      lines.push('  sleep 2');
      lines.push('done');
      break;
    }

    case 'fill': {
      var fillSel = singleQuote(step.operands.selector);
      var fillVal = singleQuote(step.operands.value);
      var fillCmd = 'agent-browser ' + sessionPrefix + 'fill ' + fillSel + ' ' + fillVal;
      lines.push('_retry=0');
      lines.push('while true; do');
      lines.push('  ' + fillCmd + ' && break');
      lines.push('  _retry=$((_retry + 1))');
      lines.push('  if [ "$_retry" -ge "$RETRIES" ] || [ "$RETRIES" -eq 0 ]; then');
      lines.push('    _handle_failure "' + step.id + '" "fill action failed"');
      lines.push('    break');
      lines.push('  fi');
      lines.push('  echo "RETRY [$_retry/$RETRIES]: ' + step.id + '"');
      lines.push('  sleep 2');
      lines.push('done');
      break;
    }

    case 'snapshot': {
      lines.push('agent-browser ' + sessionPrefix + 'snapshot');
      break;
    }

    case 'wait': {
      lines.push('sleep ' + step.operands.seconds);
      break;
    }

    case 'verify-external': {
      lines.push('echo "SKIP: ' + step.id + ' -- external verification (no human in CI)"');
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
 * url-not-contains and text-visible remain instant checks (no poll).
 */
function generateExpects(step) {
  if (!step.expects || step.expects.length === 0) {
    return '';
  }

  var lines = [];
  var session = step.session || '';
  var sessionArg = session ? ' "' + session + '"' : ' ""';

  // Timeout argument: literal number if step.timeout set, else env var default
  var timeoutArg = (step.timeout != null) ? String(step.timeout) : '"${WAIT_TIMEOUT:-10}"';

  for (var i = 0; i < step.expects.length; i++) {
    var expect = step.expects[i];

    if (expect.type === 'active' || expect.type === 'element-visible') {
      // Poll until element is visible (CODEGEN-01)
      var sel = singleQuote(expect.selector);
      var failMsg = expect.elementName + ' not visible after ' + timeoutArg + 's';
      lines.push('_poll_visible ' + sel + ' "' + step.id + '" ' + timeoutArg + sessionArg + ' || _handle_failure "' + step.id + '" "' + failMsg + '"');

    } else if (expect.type === 'element-not-visible') {
      // Poll until element is not visible (inverted logic — CODEGEN-01 Pitfall 4)
      var sel = singleQuote(expect.selector);
      var failMsg = expect.elementName + ' still visible after ' + timeoutArg + 's (expected not visible)';
      lines.push('_poll_not_visible ' + sel + ' "' + step.id + '" ' + timeoutArg + sessionArg + ' || _handle_failure "' + step.id + '" "' + failMsg + '"');

    } else if (expect.type === 'url-contains') {
      // Poll until URL contains value (CODEGEN-01)
      var failMsg = 'url does not contain ' + expect.value + ' after ' + timeoutArg + 's';
      lines.push('_poll_url_contains ' + singleQuote(expect.value) + ' "' + step.id + '" ' + timeoutArg + ' || _handle_failure "' + step.id + '" "' + failMsg + '"');

    } else if (expect.type === 'url-not-contains') {
      // Instant check — no poll. There is no reason to wait for a forbidden URL substring to appear.
      lines.push('current_url=$(agent-browser get url) || true');
      lines.push('if [[ "$current_url" == *"' + expect.value + '"* ]]; then');
      lines.push('  _handle_failure "' + step.id + '" "url contains ' + expect.value + ' but should not (got: $current_url)"');
      lines.push('fi');

    } else if (expect.type === 'text-visible') {
      // Instant check — snapshot + grep is too heavy for polling.
      var quotedText = singleQuote(expect.text);
      lines.push('_snapshot=$(agent-browser snapshot) || true');
      lines.push('if ! echo "$_snapshot" | grep -qF ' + quotedText + '; then');
      lines.push('  _handle_failure "' + step.id + '" "text \'' + expect.text + '\' not found on page"');
      lines.push('fi');

    } else if (expect.type === 'or-visible') {
      // Poll until either element is visible (CODEGEN-01)
      var elements = expect.elements;
      var elemNames = elements.map(function(e) { return e.elementName; });
      var neitherMsg = 'neither ' + elemNames.join(' nor ') + ' visible after ' + timeoutArg + 's';
      var selectorArgs = elements.map(function(e) { return singleQuote(e.selector); }).join(' ');
      lines.push('_poll_or_visible "' + step.id + '" ' + timeoutArg + ' "' + session + '" ' + selectorArgs + ' || _handle_failure "' + step.id + '" "' + neitherMsg + '"');

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

  // Count verify-external steps for PASS summary
  for (var i = 0; i < steps.length; i++) {
    if (steps[i].type === 'verify-external') {
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

    parts.push('');
  }

  // 8. Structured footer (replaces inline PASS/exit 0)
  parts.push(generateFooter(flowName, totalSteps, skipped));

  return parts.join('\n');
}

// ---------------------------------------------------------------------------
// Exports
// ---------------------------------------------------------------------------

module.exports = { generate: generate, generateHeader: generateHeader, singleQuote: singleQuote, generateVariables: generateVariables, generateBaseUrlNormalization: generateBaseUrlNormalization, generateCleanupTrap: generateCleanupTrap };
