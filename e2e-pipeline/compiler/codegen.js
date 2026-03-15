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
      lines.push('agent-browser ' + sessionPrefix + 'open "' + baseUrlVar + urlPath + '" || {');
      lines.push('  echo "FAIL: ' + step.id + ' -- navigate to ' + urlPath + ' failed"');
      lines.push('  exit 1');
      lines.push('}');
      break;
    }

    case 'click': {
      var sel = singleQuote(step.operands.selector);
      lines.push('agent-browser ' + sessionPrefix + 'click ' + sel + ' || {');
      lines.push('  echo "FAIL: ' + step.id + ' -- click action failed"');
      lines.push('  exit 1');
      lines.push('}');
      break;
    }

    case 'fill': {
      var fillSel = singleQuote(step.operands.selector);
      var fillVal = singleQuote(step.operands.value);
      lines.push('agent-browser ' + sessionPrefix + 'fill ' + fillSel + ' ' + fillVal + ' || {');
      lines.push('  echo "FAIL: ' + step.id + ' -- fill action failed"');
      lines.push('  exit 1');
      lines.push('}');
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
 * Cross-site: when step.session is set, agent-browser commands use --session prefix.
 */
function generateExpects(step) {
  if (!step.expects || step.expects.length === 0) {
    return '';
  }

  var lines = [];
  var session = step.session;
  var sessionPrefix = session ? '--session ' + session + ' ' : '';

  for (var i = 0; i < step.expects.length; i++) {
    var expect = step.expects[i];

    if (expect.type === 'active' || expect.type === 'element-visible') {
      // SHEL-09: stdout capture pattern — never rely on exit code
      // 'active' = Phase 1 "element is visible"; 'element-visible' = Phase 2 "element visible"
      var sel = singleQuote(expect.selector);
      lines.push('result=$(agent-browser ' + sessionPrefix + 'is visible ' + sel + ') || true');
      lines.push('if [ "$result" != "true" ]; then');
      lines.push('  echo "FAIL: ' + step.id + ' -- ' + expect.elementName + ' is not visible"');
      lines.push('  exit 1');
      lines.push('fi');

    } else if (expect.type === 'element-not-visible') {
      // Check result != "false" — if result is anything other than "false", element is still visible
      var sel = singleQuote(expect.selector);
      lines.push('result=$(agent-browser ' + sessionPrefix + 'is visible ' + sel + ') || true');
      lines.push('if [ "$result" != "false" ]; then');
      lines.push('  echo "FAIL: ' + step.id + ' -- ' + expect.elementName + ' is still visible (expected not visible)"');
      lines.push('  exit 1');
      lines.push('fi');

    } else if (expect.type === 'url-contains') {
      // agent-browser get url returns current URL as stdout
      lines.push('current_url=$(agent-browser get url) || true');
      lines.push('if [[ "$current_url" != *"' + expect.value + '"* ]]; then');
      lines.push('  echo "FAIL: ' + step.id + ' -- url does not contain ' + expect.value + ' (got: $current_url)"');
      lines.push('  exit 1');
      lines.push('fi');

    } else if (expect.type === 'url-not-contains') {
      // Fail if the URL DOES contain the value
      lines.push('current_url=$(agent-browser get url) || true');
      lines.push('if [[ "$current_url" == *"' + expect.value + '"* ]]; then');
      lines.push('  echo "FAIL: ' + step.id + ' -- url contains ' + expect.value + ' but should not (got: $current_url)"');
      lines.push('  exit 1');
      lines.push('fi');

    } else if (expect.type === 'text-visible') {
      // snapshot outputs page accessibility tree; grep -qF for fixed-string (CJK-safe)
      // Use single-quoted grep argument to handle special chars
      var quotedText = singleQuote(expect.text);
      lines.push('_snapshot=$(agent-browser snapshot) || true');
      lines.push('if ! echo "$_snapshot" | grep -qF ' + quotedText + '; then');
      lines.push('  echo "FAIL: ' + step.id + ' -- text \'' + expect.text + '\' not found on page"');
      lines.push('  exit 1');
      lines.push('fi');

    } else if (expect.type === 'or-visible') {
      // Accumulator pattern — check each element, pass if any is visible
      var elements = expect.elements;
      lines.push('_or_pass="false"');
      for (var j = 0; j < elements.length; j++) {
        var elemSel = singleQuote(elements[j].selector);
        lines.push('_r=$(agent-browser ' + sessionPrefix + 'is visible ' + elemSel + ') || true');
        lines.push('[ "$_r" = "true" ] && _or_pass="true"');
      }
      // Build the element names list for FAIL message
      var elemNames = elements.map(function(e) { return e.elementName; });
      var neitherMsg = 'neither ' + elemNames.join(' nor ') + ' is visible';
      lines.push('if [ "$_or_pass" != "true" ]; then');
      lines.push('  echo "FAIL: ' + step.id + ' -- ' + neitherMsg + '"');
      lines.push('  exit 1');
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

  // Count verify-external steps for PASS summary
  for (var i = 0; i < steps.length; i++) {
    if (steps[i].type === 'verify-external') {
      skipped++;
    }
  }

  var parts = [];

  // 1. Shell header (with optional provenance metadata)
  parts.push(generateHeader(meta));

  // 2. Variable handling — generateVariables() adds block when present
  var varBlock = generateVariables(resolved.variables, flowName);
  if (varBlock) {
    parts.push(varBlock);
    parts.push('');
  }

  // 3. Per-step action blocks
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

  // 4. PASS summary and exit
  parts.push('echo "PASS: ' + flowName + ' (' + totalSteps + '/' + totalSteps + ' steps, ' + skipped + ' skipped)"');
  parts.push('exit 0');

  return parts.join('\n');
}

// ---------------------------------------------------------------------------
// Exports
// ---------------------------------------------------------------------------

module.exports = { generate: generate, generateHeader: generateHeader, singleQuote: singleQuote, generateVariables: generateVariables };
