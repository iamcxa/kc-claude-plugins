#!/usr/bin/env node
'use strict';

/**
 * e2e-quarantine.js — CLI entry point for quarantine evaluation.
 *
 * Reads per-run metrics files, evaluates quarantine state transitions,
 * and writes updated quarantine.json. Designed for GHA invocation.
 *
 * Usage:
 *   node bin/e2e-quarantine.js \
 *     --metrics-dir <path> \
 *     --quarantine-path <path> \
 *     [--rotate] \
 *     [--manage-issues] \
 *     [--pr-comment <number>]
 *
 * Flags:
 *   --metrics-dir <path>      Required. Directory containing per-run metrics JSON files.
 *   --quarantine-path <path>  Required. Path to quarantine.json (created if missing).
 *   --rotate                  Optional. Delete metrics files beyond 2x window per flow.
 *   --manage-issues           Optional. Enable GitHub issue create/close (Plan 07-03).
 *   --pr-comment <number>     Optional. PR number for quarantine comment (Plan 07-03).
 *
 * Output:
 *   Prints evaluation result as JSON to stdout (for GHA step output parsing).
 *   Exits 0 on success, 1 on error.
 */

var path = require('node:path');
var fs = require('node:fs');
var { evaluateQuarantine, initQuarantineJson } = require('../compiler/quarantine.js');

// ---------------------------------------------------------------------------
// Parse CLI arguments (manual — no Commander needed for these flags)
// ---------------------------------------------------------------------------

var args = process.argv.slice(2);
var metricsDir = null;
var quarantinePath = null;
var rotate = false;
var manageIssues = false;
var prComment = null;

for (var i = 0; i < args.length; i++) {
  var arg = args[i];
  if (arg === '--metrics-dir' && args[i + 1]) {
    metricsDir = args[i + 1];
    i += 1;
  } else if (arg === '--quarantine-path' && args[i + 1]) {
    quarantinePath = args[i + 1];
    i += 1;
  } else if (arg === '--rotate') {
    rotate = true;
  } else if (arg === '--manage-issues') {
    manageIssues = true;
  } else if (arg === '--pr-comment' && args[i + 1]) {
    prComment = args[i + 1];
    i += 1;
  } else if (arg === '--help' || arg === '-h') {
    process.stdout.write([
      'Usage: e2e-quarantine.js --metrics-dir <path> --quarantine-path <path> [options]',
      '',
      'Options:',
      '  --metrics-dir <path>      Required. Directory with per-run metrics JSON files.',
      '  --quarantine-path <path>  Required. Path to quarantine.json.',
      '  --rotate                  Delete metrics files beyond 2x window per flow.',
      '  --manage-issues           Enable GitHub issue create/close (Plan 07-03).',
      '  --pr-comment <number>     PR number for quarantine PR comment (Plan 07-03).',
      '',
    ].join('\n'));
    process.exit(0);
  }
}

// ---------------------------------------------------------------------------
// Validate required arguments
// ---------------------------------------------------------------------------

if (!metricsDir || !quarantinePath) {
  process.stderr.write('Error: --metrics-dir and --quarantine-path are required\n');
  process.stderr.write('Run with --help for usage information\n');
  process.exit(1);
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

try {
  // Run quarantine evaluation
  var result = evaluateQuarantine(quarantinePath, metricsDir);

  // Print changes as JSON for GHA step output parsing
  process.stdout.write(JSON.stringify(result, null, 2) + '\n');

  // Metrics rotation: delete files beyond 2x window per flow
  if (rotate) {
    try {
      var quarantineData = JSON.parse(fs.readFileSync(quarantinePath, 'utf8'));
      var window = (quarantineData.config &&
        quarantineData.config.thresholds &&
        quarantineData.config.thresholds.window) || 20;
      var rotateLimit = window * 2;

      // Discover all flow names from metrics files
      var allFiles = fs.readdirSync(metricsDir);
      var flowFileMap = {};
      allFiles.forEach(function(f) {
        if (!f.endsWith('.json')) return;
        var match = f.match(/^(.+)-\d{8}T\d{6}Z\.json$/);
        if (match) {
          var flowName = match[1];
          if (!flowFileMap[flowName]) {
            flowFileMap[flowName] = [];
          }
          flowFileMap[flowName].push(f);
        }
      });

      // For each flow, sort and delete oldest files beyond 2x window
      Object.keys(flowFileMap).forEach(function(flowName) {
        var flowFiles = flowFileMap[flowName].sort(); // lexicographic = chronological
        if (flowFiles.length > rotateLimit) {
          var toDelete = flowFiles.slice(0, flowFiles.length - rotateLimit);
          toDelete.forEach(function(f) {
            try {
              fs.unlinkSync(path.join(metricsDir, f));
            } catch (e) {
              // Ignore individual deletion errors
            }
          });
        }
      });
    } catch (e) {
      process.stderr.write('Warning: metrics rotation failed: ' + e.message + '\n');
      // Rotation failure is non-fatal — quarantine evaluation already succeeded
    }
  }

  // TODO: Plan 07-03 implements issue management
  if (manageIssues) {
    // TODO: Plan 07-03 — create GitHub issues for newly quarantined flows, close for recovered flows
    process.stderr.write('Warning: --manage-issues is not yet implemented (Plan 07-03)\n');
  }

  // TODO: Plan 07-03 implements PR comment posting
  if (prComment) {
    // TODO: Plan 07-03 — post quarantine status table as PR comment on the specified PR
    process.stderr.write('Warning: --pr-comment is not yet implemented (Plan 07-03)\n');
  }

  process.exit(0);
} catch (e) {
  process.stderr.write('Error: ' + e.message + '\n');
  process.exit(1);
}
