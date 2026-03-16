'use strict';

/**
 * migrate.js — one-time migration tool to add type: fields to flow YAML steps.
 *
 * CLI: node migrate.js <flow.yaml> [--output <path>] [--dry-run]
 *
 * For each step that does NOT already have a type: field:
 *   1. Try local regex classification (same patterns as resolver.js ACTION_PARSERS).
 *   2. If no regex match, fall back to `claude -p` for classification.
 *   3. If result is 'manual' or low-confidence, skip and print a warning.
 *
 * Export: module.exports = { migrate, classifyAction }
 */

const fs   = require('node:fs');
const path = require('node:path');
const yaml = require('js-yaml');

// ---------------------------------------------------------------------------
// Local regex classifiers — mirror resolver.js ACTION_PARSERS order
// ---------------------------------------------------------------------------

var LOCAL_CLASSIFIERS = [
  { type: 'navigate',        pattern: /^Navigate to\s+/i },
  { type: 'verify-external', pattern: /^Verify external/i },     // before generic Verify
  { type: 'execute-external', pattern: /^Execute external/i },   // before generic click/fill
  { type: 'snapshot',        pattern: /^Verify\s+\w+/i },        // element verification -> snapshot
  { type: 'click',           pattern: /^Click\s+\w+_\w+/i },   // element name must be snake_case
  { type: 'fill',            pattern: /^Fill\s+\w+_\w+\s+with\s+/i }, // element name must be snake_case
  { type: 'snapshot',        pattern: /snapshot/i },
  { type: 'wait',            pattern: /^Wait\s+\d+/i },
];

/**
 * classifyAction(action) — classify an action string to a step type.
 *
 * Returns { type, source } where source is 'regex' | 'claude' | null.
 * Returns null type when classification fails or results in manual/low-confidence.
 *
 * @param {string} action
 * @param {object} [options]
 * @param {boolean} [options.useClaude=true]  — allow claude -p fallback
 * @returns {{ type: string|null, source: string|null }}
 */
function classifyAction(action, options) {
  var opts = options || {};
  var useClaude = opts.useClaude !== false;

  // 1. Local regex pass
  for (var i = 0; i < LOCAL_CLASSIFIERS.length; i++) {
    var classifier = LOCAL_CLASSIFIERS[i];
    if (classifier.pattern.test(action)) {
      return { type: classifier.type, source: 'regex' };
    }
  }

  // 2. Claude -p fallback
  if (useClaude) {
    return classifyWithClaude(action);
  }

  return { type: null, source: null };
}

/**
 * classifyWithClaude(action) — ask claude -p to classify the action string.
 * Uses execFileSync to avoid shell injection.
 *
 * @param {string} action
 * @returns {{ type: string|null, source: string|null }}
 */
function classifyWithClaude(action) {
  try {
    var execFileSync = require('node:child_process').execFileSync;
    var prompt = (
      'Classify this E2E flow action string into one type: ' +
      'navigate, click, fill, snapshot, wait, verify-external, or manual. ' +
      'Action: \'' + action + '\'. ' +
      'Respond with JSON only: {"type":"...","confidence":"high|low"}'
    );

    var output = execFileSync('claude', ['-p', prompt], {
      encoding: 'utf8',
      timeout: 30000,
    });

    // Find the JSON object in the output (claude -p may include extra text)
    var jsonMatch = output.match(/\{[^}]+\}/);
    if (!jsonMatch) {
      return { type: null, source: null };
    }

    var parsed = JSON.parse(jsonMatch[0]);
    var type = parsed.type;
    var confidence = parsed.confidence;

    var knownTypes = ['navigate', 'click', 'fill', 'snapshot', 'wait', 'verify-external', 'execute-external'];
    if (!knownTypes.includes(type) || type === 'manual') {
      return { type: null, source: null };
    }

    if (confidence !== 'high') {
      return { type: null, source: null };
    }

    return { type: type, source: 'claude' };
  } catch (err) {
    // claude -p unavailable or failed — treat as unclassifiable
    return { type: null, source: null };
  }
}

/**
 * migrate(flowPath, options) — add type: fields to compilable steps in a flow YAML.
 *
 * @param {string} flowPath
 * @param {object} [options]
 * @param {string}  [options.output]    — path to write output; defaults to flowPath (in-place)
 * @param {boolean} [options.dryRun]    — if true, print diff but do not write
 * @param {boolean} [options.useClaude] — if false, disable claude -p fallback
 * @returns {{ annotated: number, skipped: number }}
 */
function migrate(flowPath, options) {
  var opts = options || {};
  var outputPath = opts.output || flowPath;
  var dryRun     = !!opts.dryRun;
  var useClaude  = opts.useClaude !== false;

  var raw  = fs.readFileSync(flowPath, 'utf8');
  var flow = yaml.load(raw);

  if (!flow || !Array.isArray(flow.steps)) {
    console.warn('WARN: no steps found in ' + flowPath);
    return { annotated: 0, skipped: 0 };
  }

  var annotated = 0;
  var skipped   = 0;

  var steps = flow.steps;
  for (var i = 0; i < steps.length; i++) {
    var step = steps[i];

    // Already typed — skip
    if (step.type) {
      continue;
    }

    var action = step.action || '';
    var result = classifyAction(action, { useClaude: useClaude });

    if (result.type) {
      if (dryRun) {
        console.log('WOULD ADD type: ' + result.type + ' to step \'' + (step.id || i) + '\' [' + result.source + ']');
      } else {
        step.type = result.type;
      }
      annotated++;
    } else {
      console.warn('SKIP: step \'' + (step.id || i) + '\' -- could not classify action (manual/AI-driven): ' + action);
      skipped++;
    }
  }

  if (!dryRun) {
    var output = yaml.dump(flow, { lineWidth: -1, quotingType: '"', noRefs: true });
    fs.writeFileSync(outputPath, output, 'utf8');
  }

  console.log('Migrated: ' + annotated + ' annotated, ' + skipped + ' skipped (manual/low-confidence)');

  return { annotated: annotated, skipped: skipped };
}

module.exports = { migrate: migrate, classifyAction: classifyAction };

// ---------------------------------------------------------------------------
// CLI entry point — only runs when executed directly
// ---------------------------------------------------------------------------

if (require.main === module) {
  var args = process.argv.slice(2);
  if (args.length === 0) {
    console.error('Usage: node migrate.js <flow.yaml> [--output <path>] [--dry-run]');
    process.exit(1);
  }

  var flowPath = args[0];
  var outputPath = null;
  var dryRun = false;

  for (var i = 1; i < args.length; i++) {
    if (args[i] === '--output' && args[i + 1]) {
      outputPath = args[++i];
    }
    if (args[i] === '--dry-run') {
      dryRun = true;
    }
  }

  var migrateOpts = { dryRun: dryRun };
  if (outputPath) { migrateOpts.output = outputPath; }

  migrate(flowPath, migrateOpts);
}
