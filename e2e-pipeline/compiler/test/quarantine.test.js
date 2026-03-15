'use strict';

/**
 * Unit tests for compiler/quarantine.js
 *
 * Tests for computeFlakyRate(), evaluateQuarantine(), checkStaleQuarantine(), initQuarantineJson().
 * Uses tmpdir-based fixtures for metrics files.
 */

const { test, describe, before, after } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const {
  computeFlakyRate,
  evaluateQuarantine,
  checkStaleQuarantine,
  initQuarantineJson,
} = require('../quarantine.js');

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Write a metrics JSON file for a given flow into a directory.
 * timestamp is used for the filename (compact ISO8601: YYYYMMDDTHHMMSSZ).
 */
function writeMetrics(dir, flowName, timestamp, data) {
  var fileName = flowName + '-' + timestamp + '.json';
  var filePath = path.join(dir, fileName);
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2) + '\n', 'utf8');
  return filePath;
}

/**
 * Create a minimal metrics record.
 * @param {boolean} flakyPass - true means flow passed but needed retry
 * @param {boolean} passedFirstTry - true means passed on attempt 1
 * @param {Array} steps - optional steps array
 */
function makeMetrics(flowName, flakyPass, passedFirstTry, steps) {
  return {
    flow: flowName,
    timestamp: '2026-03-15T14:23:01Z',
    attempt: passedFirstTry ? 1 : 2,
    total_attempts: passedFirstTry ? 1 : 2,
    passed_first_try: passedFirstTry,
    flaky_pass: flakyPass,
    steps: steps || [{ id: 'step-1', result: 'pass', time_s: 1, failure_msg: '' }],
    summary: {
      total: steps ? steps.length : 1,
      passed: passedFirstTry ? (steps ? steps.length : 1) : 0,
      failed: passedFirstTry ? 0 : 1,
      skipped: 0,
      flaky_pass: flakyPass,
    },
  };
}

// ISO compact timestamp sequence generator (lexicographic order)
function makeTimestamp(index) {
  // Pad index to ensure lexicographic sort matches chronological order
  var n = String(index).padStart(6, '0');
  return '20260315T' + n + 'Z';
}

// ---------------------------------------------------------------------------
// initQuarantineJson()
// ---------------------------------------------------------------------------

describe('initQuarantineJson() — returns default config structure', function() {
  test('returns object with config.thresholds and flows', function() {
    var result = initQuarantineJson();
    assert.ok(result && typeof result === 'object', 'must return an object');
    assert.ok(result.config && result.config.thresholds, 'must have config.thresholds');
    assert.ok(typeof result.flows === 'object', 'must have flows object');
  });

  test('default flaky_rate threshold is 0.2', function() {
    var result = initQuarantineJson();
    assert.equal(result.config.thresholds.flaky_rate, 0.2, 'default flaky_rate must be 0.2');
  });

  test('default window is 20', function() {
    var result = initQuarantineJson();
    assert.equal(result.config.thresholds.window, 20, 'default window must be 20');
  });

  test('default recovery_passes is 5', function() {
    var result = initQuarantineJson();
    assert.equal(result.config.thresholds.recovery_passes, 5, 'default recovery_passes must be 5');
  });

  test('default stale_days is 14', function() {
    var result = initQuarantineJson();
    assert.equal(result.config.thresholds.stale_days, 14, 'default stale_days must be 14');
  });

  test('flows is an empty object', function() {
    var result = initQuarantineJson();
    assert.deepEqual(result.flows, {}, 'flows must be empty object');
  });
});

// ---------------------------------------------------------------------------
// computeFlakyRate()
// ---------------------------------------------------------------------------

describe('computeFlakyRate() — empty metrics dir', function() {
  var tmpDir;

  before(function() {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'quarantine-empty-'));
  });

  after(function() {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  test('returns flaky_rate=0 for empty dir', function() {
    var result = computeFlakyRate(tmpDir, 'login-flow', 20);
    assert.equal(result.flaky_rate, 0, 'Expected flaky_rate=0 for empty dir');
  });

  test('returns consecutive_passes=0 for empty dir', function() {
    var result = computeFlakyRate(tmpDir, 'login-flow', 20);
    assert.equal(result.consecutive_passes, 0, 'Expected consecutive_passes=0 for empty dir');
  });

  test('returns most_flaky_step=null for empty dir', function() {
    var result = computeFlakyRate(tmpDir, 'login-flow', 20);
    assert.equal(result.most_flaky_step, null, 'Expected most_flaky_step=null for empty dir');
  });
});

describe('computeFlakyRate() — non-existent directory returns zero stats', function() {
  test('returns flaky_rate=0 when dir does not exist', function() {
    var result = computeFlakyRate('/tmp/nonexistent-dir-abc123', 'login-flow', 20);
    assert.equal(result.flaky_rate, 0, 'Expected flaky_rate=0 for missing dir');
  });
});

describe('computeFlakyRate() — flaky rate calculation', function() {
  var tmpDir;

  before(function() {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'quarantine-flaky-'));
    // Write 20 files: 5 with flaky_pass=true, 15 with passed_first_try=true
    for (var i = 0; i < 20; i++) {
      var ts = makeTimestamp(i);
      var isFlaky = i < 5; // first 5 (oldest) are flaky
      writeMetrics(tmpDir, 'login-flow', ts, makeMetrics('login-flow', isFlaky, !isFlaky));
    }
  });

  after(function() {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  test('returns flaky_rate=0.25 when 5 of 20 files have flaky_pass=true', function() {
    var result = computeFlakyRate(tmpDir, 'login-flow', 20);
    assert.equal(result.flaky_rate, 0.25, 'Expected flaky_rate=0.25 (5/20)');
  });
});

describe('computeFlakyRate() — window smaller than total files', function() {
  var tmpDir;

  before(function() {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'quarantine-window-'));
    // Write 10 files: first 5 (oldest) are flaky, last 5 are clean
    for (var i = 0; i < 10; i++) {
      var ts = makeTimestamp(i);
      var isFlaky = i < 5;
      writeMetrics(tmpDir, 'login-flow', ts, makeMetrics('login-flow', isFlaky, !isFlaky));
    }
  });

  after(function() {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  test('window=5 uses only most recent 5 files (all clean = flaky_rate=0)', function() {
    var result = computeFlakyRate(tmpDir, 'login-flow', 5);
    assert.equal(result.flaky_rate, 0, 'Most recent 5 files are clean, expected flaky_rate=0');
  });

  test('window=10 sees all files including old flaky ones', function() {
    var result = computeFlakyRate(tmpDir, 'login-flow', 10);
    assert.equal(result.flaky_rate, 0.5, 'Expected flaky_rate=0.5 (5/10)');
  });
});

describe('computeFlakyRate() — fewer than window files uses actual count', function() {
  var tmpDir;

  before(function() {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'quarantine-fewer-'));
    // Only 4 files available with window=20
    for (var i = 0; i < 4; i++) {
      var ts = makeTimestamp(i);
      var isFlaky = i < 2; // 2 of 4 are flaky = 0.5 rate
      writeMetrics(tmpDir, 'login-flow', ts, makeMetrics('login-flow', isFlaky, !isFlaky));
    }
  });

  after(function() {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  test('returns flaky_rate=0.5 when 2 of 4 actual files are flaky (not 2/20)', function() {
    var result = computeFlakyRate(tmpDir, 'login-flow', 20);
    assert.equal(result.flaky_rate, 0.5, 'Denominator must be actual count (4), not window (20)');
  });
});

describe('computeFlakyRate() — consecutive passes counted from most recent backward', function() {
  var tmpDir;

  before(function() {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'quarantine-consec-'));
    // 8 files: indices 0-4 are NOT passed_first_try, indices 5-7 ARE passed_first_try
    for (var i = 0; i < 8; i++) {
      var ts = makeTimestamp(i);
      var firstTry = i >= 5;
      writeMetrics(tmpDir, 'login-flow', ts, makeMetrics('login-flow', !firstTry, firstTry));
    }
  });

  after(function() {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  test('counts 3 consecutive passes when last 3 files have passed_first_try=true', function() {
    var result = computeFlakyRate(tmpDir, 'login-flow', 20);
    assert.equal(result.consecutive_passes, 3, 'Expected 3 consecutive passes from most recent');
  });
});

describe('computeFlakyRate() — consecutive passes = 0 when most recent failed first try', function() {
  var tmpDir;

  before(function() {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'quarantine-consec-zero-'));
    // 5 files: indices 0-3 are passed_first_try, index 4 (most recent) is NOT
    for (var i = 0; i < 5; i++) {
      var ts = makeTimestamp(i);
      var firstTry = i < 4;
      writeMetrics(tmpDir, 'login-flow', ts, makeMetrics('login-flow', !firstTry, firstTry));
    }
  });

  after(function() {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  test('returns 0 consecutive_passes when most recent file is not passed_first_try', function() {
    var result = computeFlakyRate(tmpDir, 'login-flow', 20);
    assert.equal(result.consecutive_passes, 0, 'Expected 0 when most recent is not first-try pass');
  });
});

describe('computeFlakyRate() — most_flaky_step identification', function() {
  var tmpDir;

  before(function() {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'quarantine-mfs-'));
    // 3 runs: step-A fails in 2, step-B fails in 1
    var runs = [
      makeMetrics('login-flow', true, false, [
        { id: 'step-A', result: 'fail', time_s: 1, failure_msg: 'timeout' },
        { id: 'step-B', result: 'pass', time_s: 1, failure_msg: '' },
      ]),
      makeMetrics('login-flow', true, false, [
        { id: 'step-A', result: 'fail', time_s: 1, failure_msg: 'timeout' },
        { id: 'step-B', result: 'fail', time_s: 1, failure_msg: 'not found' },
      ]),
      makeMetrics('login-flow', false, true, [
        { id: 'step-A', result: 'pass', time_s: 1, failure_msg: '' },
        { id: 'step-B', result: 'pass', time_s: 1, failure_msg: '' },
      ]),
    ];
    runs.forEach(function(run, i) {
      writeMetrics(tmpDir, 'login-flow', makeTimestamp(i), run);
    });
  });

  after(function() {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  test('most_flaky_step is the step with highest failure count across window', function() {
    var result = computeFlakyRate(tmpDir, 'login-flow', 20);
    assert.equal(result.most_flaky_step, 'step-A', 'Expected step-A (2 failures vs step-B 1 failure)');
  });
});

describe('computeFlakyRate() — tied most_flaky_step returns one of the tied steps', function() {
  var tmpDir;

  before(function() {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'quarantine-tied-'));
    // 2 runs: step-A fails in run 1, step-B fails in run 2 — tied at 1 each
    var runs = [
      makeMetrics('login-flow', true, false, [
        { id: 'step-A', result: 'fail', time_s: 1, failure_msg: 'timeout' },
        { id: 'step-B', result: 'pass', time_s: 1, failure_msg: '' },
      ]),
      makeMetrics('login-flow', true, false, [
        { id: 'step-A', result: 'pass', time_s: 1, failure_msg: '' },
        { id: 'step-B', result: 'fail', time_s: 1, failure_msg: 'not found' },
      ]),
    ];
    runs.forEach(function(run, i) {
      writeMetrics(tmpDir, 'login-flow', makeTimestamp(i), run);
    });
  });

  after(function() {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  test('most_flaky_step is one of the tied steps (step-A or step-B)', function() {
    var result = computeFlakyRate(tmpDir, 'login-flow', 20);
    assert.ok(
      result.most_flaky_step === 'step-A' || result.most_flaky_step === 'step-B',
      'Expected one of tied steps, got: ' + result.most_flaky_step
    );
  });
});

describe('computeFlakyRate() — most_flaky_step is null when no step failures', function() {
  var tmpDir;

  before(function() {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'quarantine-no-fail-'));
    writeMetrics(tmpDir, 'login-flow', makeTimestamp(0), makeMetrics('login-flow', false, true, [
      { id: 'step-A', result: 'pass', time_s: 1, failure_msg: '' },
    ]));
  });

  after(function() {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  test('most_flaky_step is null when all steps pass', function() {
    var result = computeFlakyRate(tmpDir, 'login-flow', 20);
    assert.equal(result.most_flaky_step, null, 'Expected null when no step failures');
  });
});

// ---------------------------------------------------------------------------
// evaluateQuarantine()
// ---------------------------------------------------------------------------

describe('evaluateQuarantine() — auto-creates quarantine.json when missing', function() {
  var tmpDir;

  before(function() {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'quarantine-autocreate-'));
    // Write 5 clean runs so there IS a flow in metrics but no quarantine.json
    for (var i = 0; i < 5; i++) {
      writeMetrics(tmpDir, 'login-flow', makeTimestamp(i), makeMetrics('login-flow', false, true));
    }
  });

  after(function() {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  test('creates quarantine.json with default config when file does not exist', function() {
    var qPath = path.join(tmpDir, 'quarantine.json');
    assert.ok(!fs.existsSync(qPath), 'quarantine.json must not exist before test');
    evaluateQuarantine(qPath, tmpDir);
    assert.ok(fs.existsSync(qPath), 'quarantine.json must be created by evaluateQuarantine');
    var data = JSON.parse(fs.readFileSync(qPath, 'utf8'));
    assert.ok(data.config && data.config.thresholds, 'created file must have config.thresholds');
  });
});

describe('evaluateQuarantine() — healthy to quarantined transition', function() {
  var tmpDir;

  before(function() {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'quarantine-enter-'));
    // Write 10 flaky runs (flaky_rate = 1.0, way above 0.2 threshold)
    for (var i = 0; i < 10; i++) {
      writeMetrics(tmpDir, 'login-flow', makeTimestamp(i), makeMetrics('login-flow', true, false));
    }
  });

  after(function() {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  test('transitions flow to quarantined when flaky_rate > 0.2', function() {
    var qPath = path.join(tmpDir, 'quarantine.json');
    evaluateQuarantine(qPath, tmpDir);
    var data = JSON.parse(fs.readFileSync(qPath, 'utf8'));
    assert.equal(data.flows['login-flow'].status, 'quarantined', 'Expected quarantined status');
  });

  test('sets entered date when transitioning to quarantined', function() {
    var qPath = path.join(tmpDir, 'quarantine.json');
    var data = JSON.parse(fs.readFileSync(qPath, 'utf8'));
    assert.ok(data.flows['login-flow'].entered !== null, 'entered must be set on quarantine entry');
    assert.ok(typeof data.flows['login-flow'].entered === 'string', 'entered must be a string date');
  });

  test('changes array includes the flow with from=healthy and to=quarantined', function() {
    var qPath = path.join(tmpDir, 'quarantine.json');
    // Reset and re-evaluate to test return value
    fs.unlinkSync(qPath);
    var result = evaluateQuarantine(qPath, tmpDir);
    assert.ok(Array.isArray(result.changes), 'result.changes must be array');
    var change = result.changes.find(function(c) { return c.flow === 'login-flow'; });
    assert.ok(change, 'changes must include login-flow');
    assert.equal(change.from, 'healthy', 'from must be healthy');
    assert.equal(change.to, 'quarantined', 'to must be quarantined');
  });
});

describe('evaluateQuarantine() — does NOT quarantine at exactly 0.2 (strictly greater)', function() {
  var tmpDir;

  before(function() {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'quarantine-exact-'));
    // 4 of 20 runs are flaky = exactly 0.2 rate
    for (var i = 0; i < 20; i++) {
      var isFlaky = i < 4;
      writeMetrics(tmpDir, 'login-flow', makeTimestamp(i), makeMetrics('login-flow', isFlaky, !isFlaky));
    }
  });

  after(function() {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  test('flow remains healthy at exactly 0.2 flaky_rate (not strictly greater)', function() {
    var qPath = path.join(tmpDir, 'quarantine.json');
    evaluateQuarantine(qPath, tmpDir);
    var data = JSON.parse(fs.readFileSync(qPath, 'utf8'));
    assert.equal(data.flows['login-flow'].status, 'healthy', 'Expected healthy at exactly 0.2');
  });
});

describe('evaluateQuarantine() — quarantined to healthy transition', function() {
  var tmpDir;

  before(function() {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'quarantine-exit-'));
    // 10 runs: first 5 flaky, last 5 all passed_first_try=true
    for (var i = 0; i < 10; i++) {
      var isFlaky = i < 5;
      writeMetrics(tmpDir, 'login-flow', makeTimestamp(i), makeMetrics('login-flow', isFlaky, !isFlaky));
    }
  });

  after(function() {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  test('exits quarantine after 5 consecutive passes', function() {
    var qPath = path.join(tmpDir, 'quarantine.json');
    // Pre-seed quarantine.json with flow already quarantined
    var initial = initQuarantineJson();
    initial.flows['login-flow'] = {
      status: 'quarantined',
      flaky_rate: 0.5,
      entered: '2026-03-10',
      last_run: '2026-03-14',
      consecutive_passes: 0,
      override: null,
      issue_number: null,
    };
    fs.writeFileSync(qPath, JSON.stringify(initial, null, 2) + '\n', 'utf8');

    evaluateQuarantine(qPath, tmpDir);
    var data = JSON.parse(fs.readFileSync(qPath, 'utf8'));
    assert.equal(data.flows['login-flow'].status, 'healthy', 'Expected healthy after 5 consecutive passes');
  });
});

describe('evaluateQuarantine() — preserves entered date when already quarantined', function() {
  var tmpDir;

  before(function() {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'quarantine-preserve-'));
    // Still flaky: 10 flaky runs
    for (var i = 0; i < 10; i++) {
      writeMetrics(tmpDir, 'login-flow', makeTimestamp(i), makeMetrics('login-flow', true, false));
    }
  });

  after(function() {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  test('entered date is not overwritten when flow is already quarantined', function() {
    var qPath = path.join(tmpDir, 'quarantine.json');
    var originalEntered = '2026-03-01';
    var initial = initQuarantineJson();
    initial.flows['login-flow'] = {
      status: 'quarantined',
      flaky_rate: 0.9,
      entered: originalEntered,
      last_run: '2026-03-14',
      consecutive_passes: 0,
      override: null,
      issue_number: null,
    };
    fs.writeFileSync(qPath, JSON.stringify(initial, null, 2) + '\n', 'utf8');

    evaluateQuarantine(qPath, tmpDir);
    var data = JSON.parse(fs.readFileSync(qPath, 'utf8'));
    assert.equal(
      data.flows['login-flow'].entered,
      originalEntered,
      'entered date must not be overwritten for already-quarantined flow'
    );
  });
});

describe('evaluateQuarantine() — always updates flaky_rate and last_run', function() {
  var tmpDir;

  before(function() {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'quarantine-update-'));
    // 5 clean runs
    for (var i = 0; i < 5; i++) {
      writeMetrics(tmpDir, 'login-flow', makeTimestamp(i), makeMetrics('login-flow', false, true));
    }
  });

  after(function() {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  test('flaky_rate is updated to current value on every evaluation', function() {
    var qPath = path.join(tmpDir, 'quarantine.json');
    // Pre-seed with stale data
    var initial = initQuarantineJson();
    initial.flows['login-flow'] = {
      status: 'healthy',
      flaky_rate: 0.99,
      entered: null,
      last_run: '2020-01-01',
      consecutive_passes: 0,
      override: null,
      issue_number: null,
    };
    fs.writeFileSync(qPath, JSON.stringify(initial, null, 2) + '\n', 'utf8');

    evaluateQuarantine(qPath, tmpDir);
    var data = JSON.parse(fs.readFileSync(qPath, 'utf8'));
    assert.equal(data.flows['login-flow'].flaky_rate, 0, 'flaky_rate must be updated to 0 (5 clean runs)');
  });

  test('last_run is updated to today on every evaluation', function() {
    var qPath = path.join(tmpDir, 'quarantine.json');
    var data = JSON.parse(fs.readFileSync(qPath, 'utf8'));
    var today = new Date().toISOString().slice(0, 10);
    assert.equal(data.flows['login-flow'].last_run, today, 'last_run must be updated to today');
  });
});

describe('evaluateQuarantine() — override="skip" forces healthy', function() {
  var tmpDir;

  before(function() {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'quarantine-skip-'));
    // 10 flaky runs (would normally quarantine)
    for (var i = 0; i < 10; i++) {
      writeMetrics(tmpDir, 'login-flow', makeTimestamp(i), makeMetrics('login-flow', true, false));
    }
  });

  after(function() {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  test('flow with override=skip stays healthy despite high flaky_rate', function() {
    var qPath = path.join(tmpDir, 'quarantine.json');
    var initial = initQuarantineJson();
    initial.flows['login-flow'] = {
      status: 'healthy',
      flaky_rate: 0.0,
      entered: null,
      last_run: '2026-03-14',
      consecutive_passes: 0,
      override: 'skip',
      issue_number: null,
    };
    fs.writeFileSync(qPath, JSON.stringify(initial, null, 2) + '\n', 'utf8');

    evaluateQuarantine(qPath, tmpDir);
    var data = JSON.parse(fs.readFileSync(qPath, 'utf8'));
    assert.equal(data.flows['login-flow'].status, 'healthy', 'override=skip must keep status healthy');
  });
});

describe('evaluateQuarantine() — override="quarantine" forces quarantined', function() {
  var tmpDir;

  before(function() {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'quarantine-force-'));
    // 5 clean runs (would normally be healthy)
    for (var i = 0; i < 5; i++) {
      writeMetrics(tmpDir, 'login-flow', makeTimestamp(i), makeMetrics('login-flow', false, true));
    }
  });

  after(function() {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  test('flow with override=quarantine stays quarantined despite low flaky_rate', function() {
    var qPath = path.join(tmpDir, 'quarantine.json');
    var initial = initQuarantineJson();
    initial.flows['login-flow'] = {
      status: 'quarantined',
      flaky_rate: 0.8,
      entered: '2026-03-10',
      last_run: '2026-03-14',
      consecutive_passes: 5,
      override: 'quarantine',
      issue_number: null,
    };
    fs.writeFileSync(qPath, JSON.stringify(initial, null, 2) + '\n', 'utf8');

    evaluateQuarantine(qPath, tmpDir);
    var data = JSON.parse(fs.readFileSync(qPath, 'utf8'));
    assert.equal(
      data.flows['login-flow'].status,
      'quarantined',
      'override=quarantine must keep status quarantined despite 5 consecutive passes'
    );
  });
});

describe('evaluateQuarantine() — result shape', function() {
  var tmpDir;

  before(function() {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'quarantine-result-'));
    writeMetrics(tmpDir, 'login-flow', makeTimestamp(0), makeMetrics('login-flow', false, true));
  });

  after(function() {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  test('returns object with updated boolean and changes array', function() {
    var qPath = path.join(tmpDir, 'quarantine.json');
    var result = evaluateQuarantine(qPath, tmpDir);
    assert.ok(typeof result.updated === 'boolean', 'result.updated must be boolean');
    assert.ok(Array.isArray(result.changes), 'result.changes must be array');
  });
});

// ---------------------------------------------------------------------------
// checkStaleQuarantine()
// ---------------------------------------------------------------------------

describe('checkStaleQuarantine() — basic behavior', function() {
  test('returns true when quarantined for more than staleDays', function() {
    var entered = new Date();
    entered.setDate(entered.getDate() - 15); // 15 days ago
    var flowState = {
      status: 'quarantined',
      entered: entered.toISOString().slice(0, 10),
    };
    assert.equal(checkStaleQuarantine(flowState, 14), true, 'Expected true for 15 days > 14 staleDays');
  });

  test('returns false when quarantined for fewer than staleDays', function() {
    var entered = new Date();
    entered.setDate(entered.getDate() - 7); // 7 days ago
    var flowState = {
      status: 'quarantined',
      entered: entered.toISOString().slice(0, 10),
    };
    assert.equal(checkStaleQuarantine(flowState, 14), false, 'Expected false for 7 days < 14 staleDays');
  });

  test('returns false for healthy flows even if entered date is old', function() {
    var flowState = {
      status: 'healthy',
      entered: '2020-01-01', // very old date, but status is healthy
    };
    assert.equal(checkStaleQuarantine(flowState, 14), false, 'Expected false for healthy flow');
  });

  test('returns false when entered is null', function() {
    var flowState = {
      status: 'quarantined',
      entered: null,
    };
    assert.equal(checkStaleQuarantine(flowState, 14), false, 'Expected false when entered is null');
  });

  test('returns false when flowState is missing status', function() {
    var flowState = { entered: '2020-01-01' };
    assert.equal(checkStaleQuarantine(flowState, 14), false, 'Expected false when status is missing');
  });
});
