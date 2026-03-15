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
// Header generation
// ---------------------------------------------------------------------------

function generateHeader() {
  return [
    '#!/usr/bin/env bash',
    'set -euo pipefail',
    '',
    'export LANG=en_US.UTF-8',
    'export LC_ALL=en_US.UTF-8',
    '',
  ].join('\n');
}

// ---------------------------------------------------------------------------
// Per-action bash block generation
// ---------------------------------------------------------------------------

/**
 * Generate bash lines for a single step action.
 * stepIndex: 0-based index into the resolved steps array
 * totalSteps: total number of steps in the flow
 */
function generateAction(step, stepIndex, totalSteps) {
  var lines = [];
  var n = stepIndex + 1;
  var t = totalSteps;

  // Step progress log — always first
  lines.push('echo "[' + n + '/' + t + '] ' + step.id + ': ' + step.action + '"');

  switch (step.type) {
    case 'navigate': {
      var urlPath = step.operands.urlPath || step.operands.target;
      lines.push('agent-browser open "${BASE_URL}' + urlPath + '" || {');
      lines.push('  echo "FAIL: ' + step.id + ' -- navigate to ' + urlPath + ' failed"');
      lines.push('  exit 1');
      lines.push('}');
      break;
    }

    case 'click': {
      var sel = singleQuote(step.operands.selector);
      lines.push('agent-browser click ' + sel + ' || {');
      lines.push('  echo "FAIL: ' + step.id + ' -- click action failed"');
      lines.push('  exit 1');
      lines.push('}');
      break;
    }

    case 'fill': {
      var fillSel = singleQuote(step.operands.selector);
      var fillVal = singleQuote(step.operands.value);
      lines.push('agent-browser fill ' + fillSel + ' ' + fillVal + ' || {');
      lines.push('  echo "FAIL: ' + step.id + ' -- fill action failed"');
      lines.push('  exit 1');
      lines.push('}');
      break;
    }

    case 'snapshot': {
      lines.push('agent-browser snapshot');
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
 * Only 'active' (visible) expects are compiled; deferred emits TODO.
 */
function generateExpects(step) {
  if (!step.expects || step.expects.length === 0) {
    return '';
  }

  var lines = [];

  for (var i = 0; i < step.expects.length; i++) {
    var expect = step.expects[i];

    if (expect.type === 'active') {
      // SHEL-09: stdout capture pattern — never rely on exit code
      var sel = singleQuote(expect.selector);
      lines.push('result=$(agent-browser is visible ' + sel + ') || true');
      lines.push('if [ "$result" != "true" ]; then');
      lines.push('  echo "FAIL: ' + step.id + ' -- ' + expect.elementName + ' is not visible"');
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
 * generate(resolved, flowName) — produce a complete bash script string.
 *
 * resolved: { name, description, variables?, steps: ResolvedStep[] }
 * flowName: string used in PASS/FAIL summary messages
 * Returns:  string (complete bash script content)
 */
function generate(resolved, flowName) {
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

  // 1. Shell header
  parts.push(generateHeader());

  // 2. Variable handling — placeholder for Plan 01-03
  parts.push('# Variables: added by generateVariables() when present');
  parts.push('');

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

module.exports = { generate: generate, singleQuote: singleQuote };
