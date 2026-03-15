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
 *   --metrics-dir <path>      Required for evaluation. Directory containing per-run metrics JSON files.
 *   --quarantine-path <path>  Required. Path to quarantine.json (created if missing).
 *   --rotate                  Optional. Delete metrics files beyond 2x window per flow.
 *   --manage-issues           Optional. Enable GitHub issue create/close.
 *   --pr-comment <number>     Optional. PR number for quarantine comment.
 *
 * Output:
 *   Prints evaluation result as JSON to stdout (for GHA step output parsing).
 *   Exits 0 on success, 1 on error.
 */

var path = require('node:path');
var fs = require('node:fs');
var { spawnSync } = require('node:child_process');
var { evaluateQuarantine, initQuarantineJson, checkStaleQuarantine } = require('../compiler/quarantine.js');
var { readMetricsFiles } = require('../compiler/metrics.js');

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
      'Usage: e2e-quarantine.js --quarantine-path <path> [options]',
      '',
      'Options:',
      '  --metrics-dir <path>      Required for evaluation. Directory with per-run metrics JSON files.',
      '  --quarantine-path <path>  Required. Path to quarantine.json.',
      '  --rotate                  Delete metrics files beyond 2x window per flow.',
      '  --manage-issues           Enable GitHub issue create/close.',
      '  --pr-comment <number>     PR number for quarantine PR comment.',
      '',
    ].join('\n'));
    process.exit(0);
  }
}

// ---------------------------------------------------------------------------
// Validate required arguments
// ---------------------------------------------------------------------------

if (!quarantinePath) {
  process.stderr.write('Error: --quarantine-path is required\n');
  process.stderr.write('Run with --help for usage information\n');
  process.exit(1);
}

// --metrics-dir required when evaluation is needed (not for --pr-comment only)
var evaluationMode = !prComment || manageIssues || rotate || metricsDir;
if (evaluationMode && !metricsDir) {
  process.stderr.write('Error: --metrics-dir is required for quarantine evaluation\n');
  process.stderr.write('Run with --help for usage information\n');
  process.exit(1);
}

// ---------------------------------------------------------------------------
// Helper: run a gh command with spawnSync. Returns { ok, stdout, stderr }.
// All gh calls are best-effort — issue management never blocks flow evaluation.
// ---------------------------------------------------------------------------

function ghRun(ghArgs) {
  var result = spawnSync('gh', ghArgs, { encoding: 'utf8' });
  var ok = result.status === 0;
  if (!ok && result.stderr) {
    process.stderr.write('gh warning: ' + result.stderr.trim() + '\n');
  }
  return {
    ok: ok,
    stdout: (result.stdout || '').trim(),
    stderr: (result.stderr || '').trim(),
  };
}

// ---------------------------------------------------------------------------
// Helper: pre-create a label (--force allows idempotent re-creation)
// ---------------------------------------------------------------------------

function ensureLabel(labelName, color, description) {
  ghRun(['label', 'create', labelName,
    '--color', color,
    '--description', description,
    '--force']);
}

// ---------------------------------------------------------------------------
// Helper: build failure history table for issue body
// ---------------------------------------------------------------------------

function buildFailureHistoryTable(metricsForFlow) {
  var lines = [
    '| Run | Result | Flaky Pass | Most Failed Step |',
    '| --- | ------ | ---------- | ---------------- |',
  ];
  var records = metricsForFlow.slice(-20); // last 20 runs
  records.forEach(function(r) {
    var runDate = r.timestamp ? r.timestamp.slice(0, 10) : '—';
    var result = r.passed_first_try ? 'pass' : (r.flaky_pass ? 'flaky' : 'fail');
    var flakyPass = r.flaky_pass ? 'yes' : 'no';
    // Find most-failed step in this single run
    var mostFailed = '—';
    if (Array.isArray(r.steps)) {
      var failedSteps = r.steps.filter(function(s) { return s.result === 'fail'; });
      if (failedSteps.length > 0) {
        mostFailed = '`' + failedSteps[0].id + '`';
      }
    }
    lines.push('| ' + runDate + ' | ' + result + ' | ' + flakyPass + ' | ' + mostFailed + ' |');
  });
  return lines.join('\n');
}

// ---------------------------------------------------------------------------
// Helper: build GitHub issue body for a newly quarantined flow
// ---------------------------------------------------------------------------

function buildIssueBody(flowName, change, metricsDir, windowSize, closedIssueRef) {
  var metricsForFlow = [];
  try {
    metricsForFlow = readMetricsFiles(metricsDir, flowName, 20);
  } catch (e) {
    // Metrics unavailable — still create issue with partial info
  }

  var flakyRatePct = (change.flaky_rate * 100).toFixed(0) + '%';
  var mostFlakyStep = change.most_flaky_step || '(unknown)';
  var historyTable = buildFailureHistoryTable(metricsForFlow);

  var lines = [
    'Flow `' + flowName + '` has been automatically quarantined due to excessive flakiness.',
    '',
    '**Diagnostics:**',
    '- Flaky rate: ' + flakyRatePct + ' (threshold: 20%)',
    '- Most-flaky step: `' + mostFlakyStep + '`',
    '',
    '**Suggested fix:** Investigate step `' + mostFlakyStep + '` — check selector stability and timing sensitivity.',
    '',
    '**Failure History (last 20 runs):**',
    '',
    historyTable,
    '',
    '---',
    '*Auto-created by e2e-pipeline quarantine system.*',
  ];

  if (closedIssueRef) {
    lines.splice(lines.length - 2, 0, '**Previously:** #' + closedIssueRef);
    lines.splice(lines.length - 2, 0, '');
  }

  return lines.join('\n');
}

// ---------------------------------------------------------------------------
// --manage-issues implementation
// ---------------------------------------------------------------------------

function manageGithubIssues(result, quarantineData, quarantinePath, metricsDir) {
  var thresholds = quarantineData.config && quarantineData.config.thresholds || {};
  var staleDays = thresholds.stale_days || 14;
  var windowSize = thresholds.window || 20;

  // Process state transitions
  result.changes.forEach(function(change) {
    var flowName = change.flow;
    var flowState = quarantineData.flows[flowName];
    if (!flowState) return;

    if (change.from === 'healthy' && change.to === 'quarantined') {
      // New quarantine — create GitHub issue with dedup
      process.stdout.write('Managing issue for newly quarantined flow: ' + flowName + '\n');

      // Ensure labels exist
      ensureLabel('e2e-flaky', 'e4e669', 'Flaky E2E test flow');
      ensureLabel(flowName, 'c5def5', 'E2E flow: ' + flowName);

      // Dedup check: look for existing open issue
      var openCheck = ghRun(['issue', 'list',
        '--label', 'e2e-flaky',
        '--label', flowName,
        '--state', 'open',
        '--json', 'number,title',
        '--jq', '.[0].number // empty']);

      if (openCheck.stdout) {
        // Open issue already exists — store issue_number and skip creation
        var existingNumber = parseInt(openCheck.stdout, 10);
        if (!isNaN(existingNumber)) {
          process.stdout.write('Open issue #' + existingNumber + ' already exists for ' + flowName + ' — skipping creation\n');
          flowState.issue_number = existingNumber;
        }
      } else {
        // No open issue — check for closed issues to reference
        var closedCheck = ghRun(['issue', 'list',
          '--label', 'e2e-flaky',
          '--label', flowName,
          '--state', 'closed',
          '--json', 'number',
          '--jq', '.[0].number // empty']);
        var closedRef = closedCheck.stdout ? parseInt(closedCheck.stdout, 10) : null;
        if (isNaN(closedRef)) closedRef = null;

        var issueBody = buildIssueBody(flowName, change, metricsDir, windowSize, closedRef);

        var createResult = ghRun(['issue', 'create',
          '--title', '[E2E Flaky] ' + flowName,
          '--label', 'e2e-flaky',
          '--label', flowName,
          '--body', issueBody]);

        if (createResult.ok && createResult.stdout) {
          // stdout is the issue URL — extract number from URL
          var urlMatch = createResult.stdout.match(/\/(\d+)$/);
          if (urlMatch) {
            var issueNumber = parseInt(urlMatch[1], 10);
            flowState.issue_number = issueNumber;
            process.stdout.write('Created issue #' + issueNumber + ' for quarantined flow: ' + flowName + '\n');
          }
        } else {
          process.stderr.write('Warning: failed to create issue for ' + flowName + '\n');
        }
      }

    } else if (change.from === 'quarantined' && change.to === 'healthy') {
      // Recovery — close issue with summary
      if (flowState.issue_number) {
        var issueNumber = flowState.issue_number;
        var today = new Date().toISOString().slice(0, 10);
        var enteredDate = flowState.entered || '(unknown)';
        var durationDays = '(unknown)';
        if (flowState.entered) {
          var enteredMs = new Date(flowState.entered).getTime();
          var todayMs = new Date(today).getTime();
          durationDays = Math.round((todayMs - enteredMs) / (1000 * 60 * 60 * 24));
        }
        var mostFlakyStep = change.most_flaky_step || '(unknown)';
        var consecutivePasses = flowState.consecutive_passes || 0;

        var recoveryComment = [
          'Flow `' + flowName + '` has recovered from quarantine.',
          '',
          '**Summary:**',
          '- Quarantined: ' + enteredDate,
          '- Recovered: ' + today,
          '- Duration: ' + durationDays + ' days',
          '- Most-flaky step: `' + mostFlakyStep + '`',
          '- Consecutive first-attempt passes: ' + consecutivePasses,
          '',
          '*Auto-closed by e2e-pipeline quarantine system.*',
        ].join('\n');

        var closeResult = ghRun(['issue', 'close',
          String(issueNumber),
          '--comment', recoveryComment,
          '--reason', 'completed']);

        if (closeResult.ok) {
          process.stdout.write('Closed issue #' + issueNumber + ' for recovered flow: ' + flowName + '\n');
        } else {
          process.stderr.write('Warning: failed to close issue #' + issueNumber + ' for ' + flowName + '\n');
        }

        // Clear issue_number on recovery
        flowState.issue_number = null;
      } else {
        process.stdout.write('No issue number recorded for recovered flow: ' + flowName + ' — skipping close\n');
      }
    }
  });

  // Stale label escalation for still-quarantined flows
  Object.keys(quarantineData.flows).forEach(function(flowName) {
    var flowState = quarantineData.flows[flowName];
    if (!flowState || flowState.status !== 'quarantined') return;
    if (!flowState.issue_number) return;

    if (checkStaleQuarantine(flowState, staleDays)) {
      ensureLabel('e2e-stale', 'd93f0b', 'E2E flow stale in quarantine (>14 days)');
      var editResult = ghRun(['issue', 'edit',
        String(flowState.issue_number),
        '--add-label', 'e2e-stale']);
      if (editResult.ok) {
        process.stdout.write('Added e2e-stale label to issue #' + flowState.issue_number + ' for ' + flowName + '\n');
      }
    }
  });

  // Write updated quarantine.json (with issue_numbers)
  var dir = path.dirname(quarantinePath);
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(quarantinePath, JSON.stringify(quarantineData, null, 2) + '\n', 'utf8');
}

// ---------------------------------------------------------------------------
// --pr-comment implementation
// ---------------------------------------------------------------------------

function postPrComment(prNumber, quarantinePath) {
  // Read quarantine.json
  var quarantineData;
  try {
    quarantineData = JSON.parse(fs.readFileSync(quarantinePath, 'utf8'));
  } catch (e) {
    process.stderr.write('Warning: could not read quarantine.json: ' + e.message + '\n');
    return;
  }

  // Filter to quarantined flows
  var quarantinedFlows = Object.keys(quarantineData.flows || {}).filter(function(f) {
    return quarantineData.flows[f].status === 'quarantined';
  });

  // Zero noise: skip comment if no quarantined flows
  if (quarantinedFlows.length === 0) {
    process.stdout.write('No quarantined flows — skipping PR comment\n');
    return;
  }

  // Build comment body
  var tableRows = quarantinedFlows.map(function(flowName) {
    var flow = quarantineData.flows[flowName];
    var flakyRate = ((flow.flaky_rate || 0) * 100).toFixed(0) + '%';
    var lastFailure = flow.last_run || '—';
    return '| ' + flowName + ' | ' + flakyRate + ' | quarantined | ' + lastFailure + ' |';
  });

  var commentBody = [
    '<!-- e2e-quarantine-report -->',
    '## E2E Quarantine Report',
    '',
    '| Flow | Flaky Rate | Status | Last Failure |',
    '| ---- | ---------- | ------ | ------------ |',
  ].concat(tableRows).concat([
    '',
    '[View quarantine.json](.claude/e2e/quarantine.json)',
  ]).join('\n');

  // Check for existing comment with marker
  var repo = process.env.GITHUB_REPOSITORY || '';
  var existingCommentId = null;

  if (repo) {
    var findResult = ghRun(['api',
      'repos/' + repo + '/issues/' + prNumber + '/comments',
      '--jq', '[.[] | select(.body | contains("<!-- e2e-quarantine-report -->")) | .id][0] // empty']);
    if (findResult.ok && findResult.stdout) {
      var parsedId = parseInt(findResult.stdout, 10);
      if (!isNaN(parsedId)) {
        existingCommentId = parsedId;
      }
    }
  }

  if (existingCommentId && repo) {
    // Update existing comment
    var updateResult = ghRun(['api',
      'repos/' + repo + '/issues/comments/' + existingCommentId,
      '--method', 'PATCH',
      '--field', 'body=' + commentBody]);
    if (updateResult.ok) {
      process.stdout.write('Updated PR comment #' + existingCommentId + ' on PR ' + prNumber + '\n');
    } else {
      process.stderr.write('Warning: failed to update PR comment\n');
    }
  } else {
    // Post new comment
    var createResult = ghRun(['pr', 'comment', String(prNumber),
      '--body', commentBody]);
    if (createResult.ok) {
      process.stdout.write('Posted quarantine PR comment on PR ' + prNumber + '\n');
    } else {
      process.stderr.write('Warning: failed to post PR comment\n');
    }
  }
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

try {
  // If only --pr-comment is specified (no evaluation needed), run just that
  if (prComment && !metricsDir) {
    postPrComment(prComment, quarantinePath);
    process.exit(0);
  }

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

  // --manage-issues: create/close GitHub issues for quarantine transitions
  if (manageIssues) {
    try {
      var issueQuarantineData = JSON.parse(fs.readFileSync(quarantinePath, 'utf8'));
      manageGithubIssues(result, issueQuarantineData, quarantinePath, metricsDir);
    } catch (e) {
      process.stderr.write('Warning: --manage-issues failed: ' + e.message + '\n');
      // Issue management is best-effort — quarantine evaluation already succeeded
    }
  }

  // --pr-comment: post quarantine status table to PR
  if (prComment) {
    try {
      postPrComment(prComment, quarantinePath);
    } catch (e) {
      process.stderr.write('Warning: --pr-comment failed: ' + e.message + '\n');
      // PR comment is best-effort
    }
  }

  process.exit(0);
} catch (e) {
  process.stderr.write('Error: ' + e.message + '\n');
  process.exit(1);
}
