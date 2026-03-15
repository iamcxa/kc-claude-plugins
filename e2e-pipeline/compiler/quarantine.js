'use strict';

var fs = require('node:fs');
var path = require('node:path');

/**
 * initQuarantineJson() — returns default quarantine.json structure.
 *
 * @returns {{ config: object, flows: object }}
 */
function initQuarantineJson() {
  return {
    config: {
      thresholds: {
        flaky_rate: 0.2,
        window: 20,
        recovery_passes: 5,
        stale_days: 14,
      },
    },
    flows: {},
  };
}

/**
 * computeFlakyRate(metricsDir, flowName, windowSize) — read per-run metrics files
 * and compute flaky statistics for a given flow.
 *
 * Metrics files must match the naming pattern: `<flowName>-<timestamp>.json`
 * Files are sorted lexicographically (ISO compact timestamps are lexicographically sortable).
 * Only the most recent `windowSize` files are considered.
 *
 * @param {string} metricsDir - Directory containing metrics JSON files.
 * @param {string} flowName - Name of the flow to analyze.
 * @param {number} windowSize - Maximum number of recent files to analyze.
 * @returns {{ flaky_rate: number, consecutive_passes: number, most_flaky_step: string|null }}
 */
function computeFlakyRate(metricsDir, flowName, windowSize) {
  var empty = { flaky_rate: 0, consecutive_passes: 0, most_flaky_step: null };

  var files;
  try {
    files = fs.readdirSync(metricsDir);
  } catch (e) {
    return empty;
  }

  // Filter to files belonging to this flow
  var prefix = flowName + '-';
  var flowFiles = files.filter(function(f) {
    return f.startsWith(prefix) && f.endsWith('.json');
  });

  if (flowFiles.length === 0) {
    return empty;
  }

  // Sort lexicographically (ISO compact timestamps are lexicographic-safe)
  flowFiles.sort();

  // Use only the most recent windowSize files
  if (flowFiles.length > windowSize) {
    flowFiles = flowFiles.slice(flowFiles.length - windowSize);
  }

  // Parse all files in the window
  var records = [];
  flowFiles.forEach(function(f) {
    try {
      var raw = fs.readFileSync(path.join(metricsDir, f), 'utf8');
      records.push(JSON.parse(raw));
    } catch (e) {
      // Skip unreadable/malformed files
    }
  });

  if (records.length === 0) {
    return empty;
  }

  // Count flaky passes
  var flakyCount = 0;
  records.forEach(function(r) {
    if (r.flaky_pass === true) {
      flakyCount += 1;
    }
  });

  var flakyRate = flakyCount / records.length;

  // Count consecutive first-attempt passes from most recent backward
  var consecutivePasses = 0;
  for (var i = records.length - 1; i >= 0; i--) {
    if (records[i].passed_first_try === true) {
      consecutivePasses += 1;
    } else {
      break;
    }
  }

  // Find most-flaky step: step with highest failure count across window
  var stepFailures = {};
  records.forEach(function(r) {
    var steps = Array.isArray(r.steps) ? r.steps : [];
    steps.forEach(function(step) {
      if (step.result === 'fail') {
        if (!stepFailures[step.id]) {
          stepFailures[step.id] = 0;
        }
        stepFailures[step.id] += 1;
      }
    });
  });

  var mostFlakyStep = null;
  var maxFailures = 0;
  Object.keys(stepFailures).forEach(function(stepId) {
    if (stepFailures[stepId] > maxFailures) {
      maxFailures = stepFailures[stepId];
      mostFlakyStep = stepId;
    }
  });

  return {
    flaky_rate: flakyRate,
    consecutive_passes: consecutivePasses,
    most_flaky_step: mostFlakyStep,
  };
}

/**
 * evaluateQuarantine(quarantinePath, metricsDir, configOverride) — read/create quarantine.json,
 * compute flaky rates for all flows found in metricsDir, apply state transitions, and write
 * updated quarantine.json.
 *
 * State transitions:
 * - healthy -> quarantined: when flaky_rate > threshold (strictly greater)
 * - quarantined -> healthy: when consecutive_passes >= recovery_passes
 * - override="skip": forces healthy regardless of metrics
 * - override="quarantine": forces quarantined regardless of metrics
 *
 * @param {string} quarantinePath - Path to quarantine.json (created if missing).
 * @param {string} metricsDir - Directory containing metrics JSON files.
 * @param {object} [configOverride] - Optional config overrides merged into thresholds.
 * @returns {{ updated: boolean, changes: Array }}
 */
function evaluateQuarantine(quarantinePath, metricsDir, configOverride) {
  // Read or create quarantine.json
  var quarantine;
  try {
    var raw = fs.readFileSync(quarantinePath, 'utf8');
    quarantine = JSON.parse(raw);
    if (!quarantine || typeof quarantine !== 'object') {
      quarantine = initQuarantineJson();
    }
  } catch (e) {
    quarantine = initQuarantineJson();
  }

  // Ensure config structure exists
  if (!quarantine.config || !quarantine.config.thresholds) {
    quarantine.config = initQuarantineJson().config;
  }
  if (!quarantine.flows || typeof quarantine.flows !== 'object') {
    quarantine.flows = {};
  }

  // Merge configOverride if provided
  if (configOverride && typeof configOverride === 'object') {
    Object.keys(configOverride).forEach(function(key) {
      quarantine.config.thresholds[key] = configOverride[key];
    });
  }

  var thresholds = quarantine.config.thresholds;
  var flakyThreshold = thresholds.flaky_rate;
  var windowSize = thresholds.window;
  var recoveryPasses = thresholds.recovery_passes;

  // Discover unique flow names from metrics dir
  var flowNames = {};
  try {
    var files = fs.readdirSync(metricsDir);
    files.forEach(function(f) {
      if (!f.endsWith('.json')) return;
      // Extract flow name: everything before the last `-YYYYMMDDTHHMMSSZ.json` segment
      // Pattern: <flowname>-<compactISO>.json where compact ISO matches \d{8}T\d{6}Z
      var match = f.match(/^(.+)-\d{8}T\d{6}Z\.json$/);
      if (match) {
        flowNames[match[1]] = true;
      }
    });
  } catch (e) {
    // Metrics dir unreadable — no flows to evaluate
  }

  var changes = [];
  var updated = false;
  var today = new Date().toISOString().slice(0, 10);

  Object.keys(flowNames).forEach(function(flowName) {
    var stats = computeFlakyRate(metricsDir, flowName, windowSize);

    // Get or init flow state
    var flowState = quarantine.flows[flowName];
    if (!flowState || typeof flowState !== 'object') {
      flowState = {
        status: 'healthy',
        flaky_rate: 0,
        entered: null,
        last_run: null,
        consecutive_passes: 0,
        override: null,
        issue_number: null,
      };
    }

    var previousStatus = flowState.status;

    // Apply override logic first
    if (flowState.override === 'skip') {
      // Force healthy regardless
      flowState.status = 'healthy';
    } else if (flowState.override === 'quarantine') {
      // Force quarantined regardless — set entered if not set
      if (!flowState.entered) {
        flowState.entered = today;
      }
      flowState.status = 'quarantined';
    } else {
      // Normal state machine transitions
      if (flowState.status === 'healthy' && stats.flaky_rate > flakyThreshold) {
        // healthy -> quarantined
        flowState.status = 'quarantined';
        flowState.entered = today;
      } else if (flowState.status === 'quarantined' && stats.consecutive_passes >= recoveryPasses) {
        // quarantined -> healthy
        flowState.status = 'healthy';
        flowState.entered = null;
      }
      // else: already quarantined and still flaky — preserve entered date
    }

    // Always update metrics fields
    flowState.flaky_rate = stats.flaky_rate;
    flowState.consecutive_passes = stats.consecutive_passes;
    flowState.last_run = today;

    // Track changes
    if (flowState.status !== previousStatus) {
      updated = true;
      changes.push({
        flow: flowName,
        from: previousStatus,
        to: flowState.status,
        flaky_rate: stats.flaky_rate,
        most_flaky_step: stats.most_flaky_step,
      });
    }

    quarantine.flows[flowName] = flowState;
  });

  // Write updated quarantine.json
  var dir = path.dirname(quarantinePath);
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(quarantinePath, JSON.stringify(quarantine, null, 2) + '\n', 'utf8');

  return { updated: updated, changes: changes };
}

/**
 * checkStaleQuarantine(flowState, staleDays) — check if a quarantined flow has been
 * in quarantine longer than staleDays.
 *
 * @param {object} flowState - Flow entry from quarantine.json flows map.
 * @param {number} staleDays - Number of days after which quarantine is considered stale.
 * @returns {boolean}
 */
function checkStaleQuarantine(flowState, staleDays) {
  if (!flowState || flowState.status !== 'quarantined') {
    return false;
  }
  if (!flowState.entered) {
    return false;
  }
  var entered = new Date(flowState.entered);
  var now = new Date();
  var diffDays = (now - entered) / (1000 * 60 * 60 * 24);
  return diffDays > staleDays;
}

module.exports = {
  initQuarantineJson: initQuarantineJson,
  computeFlakyRate: computeFlakyRate,
  evaluateQuarantine: evaluateQuarantine,
  checkStaleQuarantine: checkStaleQuarantine,
};
