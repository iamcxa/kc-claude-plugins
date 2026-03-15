'use strict';

/**
 * Unit tests for compiler/metrics.js
 *
 * Tests for metricsFileName() and readMetricsFiles().
 * Uses tmpdir for file-system tests, inline data for logic tests.
 */

const { test, describe, before, after } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const { metricsFileName, readMetricsFiles } = require('../metrics.js');

// ---------------------------------------------------------------------------
// metricsFileName() tests
// ---------------------------------------------------------------------------

describe('metricsFileName()', function() {
  test("converts ISO timestamp to compact format without milliseconds", function() {
    const result = metricsFileName('login-flow', '2026-03-15T14:23:01.000Z');
    assert.equal(result, 'login-flow-20260315T142301Z.json');
  });

  test("handles midnight timestamp (all zeros)", function() {
    const result = metricsFileName('login-flow', '2026-01-01T00:00:00.000Z');
    assert.equal(result, 'login-flow-20260101T000000Z.json');
  });

  test("strips milliseconds from ISO timestamp", function() {
    const result = metricsFileName('my-flow', '2026-06-30T23:59:59.999Z');
    // milliseconds (.999) must be stripped
    assert.equal(result, 'my-flow-20260630T235959Z.json');
  });

  test("preserves hyphens in flow name", function() {
    const result = metricsFileName('user-login-flow', '2026-03-15T14:23:01.000Z');
    assert.equal(result, 'user-login-flow-20260315T142301Z.json');
  });

  test("produces filename ending in .json", function() {
    const result = metricsFileName('any-flow', '2026-03-15T14:23:01.000Z');
    assert.ok(result.endsWith('.json'), 'Expected .json suffix, got: ' + result);
  });

  test("filenames sort lexicographically by timestamp (ISO8601-compact property)", function() {
    const earlier = metricsFileName('flow', '2026-01-01T00:00:00.000Z');
    const later = metricsFileName('flow', '2026-12-31T23:59:59.000Z');
    assert.ok(earlier < later, 'Earlier timestamp should sort before later: ' + earlier + ' vs ' + later);
  });
});

// ---------------------------------------------------------------------------
// readMetricsFiles() tests
// ---------------------------------------------------------------------------

describe('readMetricsFiles()', function() {
  var tmpDir;

  before(function() {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'metrics-test-'));
  });

  after(function() {
    // Clean up temp directory
    try {
      fs.rmSync(tmpDir, { recursive: true, force: true });
    } catch (e) {
      // ignore cleanup errors
    }
  });

  test("returns empty array when directory does not exist", function() {
    const result = readMetricsFiles('/nonexistent/path/abc123', 'login-flow', 20);
    assert.deepEqual(result, []);
  });

  test("returns empty array when no matching files exist", function() {
    // tmpDir exists but has no files matching login-flow
    const result = readMetricsFiles(tmpDir, 'login-flow', 20);
    assert.deepEqual(result, []);
  });

  test("returns parsed JSON objects, not raw strings", function() {
    const filename = metricsFileName('login-flow', '2026-03-15T14:23:01.000Z');
    const entry = { flow: 'login-flow', timestamp: '2026-03-15T14:23:01Z', passed_first_try: true };
    fs.writeFileSync(path.join(tmpDir, filename), JSON.stringify(entry), 'utf8');

    const result = readMetricsFiles(tmpDir, 'login-flow', 20);
    assert.equal(result.length, 1);
    assert.equal(typeof result[0], 'object');
    assert.equal(result[0].flow, 'login-flow');
  });

  test("filters by flow name prefix — ignores other flows' files", function() {
    // Create files for two different flows
    const file1 = metricsFileName('login-flow', '2026-03-15T10:00:00.000Z');
    const file2 = metricsFileName('checkout-flow', '2026-03-15T10:00:00.000Z');
    fs.writeFileSync(path.join(tmpDir, file1), JSON.stringify({ flow: 'login-flow' }), 'utf8');
    fs.writeFileSync(path.join(tmpDir, file2), JSON.stringify({ flow: 'checkout-flow' }), 'utf8');

    const result = readMetricsFiles(tmpDir, 'login-flow', 20);
    // Should only return login-flow files, not checkout-flow
    const flowNames = result.map(function(r) { return r.flow; });
    assert.ok(flowNames.every(function(n) { return n === 'login-flow'; }),
      'Expected only login-flow entries, got: ' + JSON.stringify(flowNames));
  });

  test("returns files sorted chronologically (ascending by filename)", function() {
    const file1 = metricsFileName('sort-flow', '2026-03-15T10:00:00.000Z');
    const file2 = metricsFileName('sort-flow', '2026-03-15T12:00:00.000Z');
    const file3 = metricsFileName('sort-flow', '2026-03-15T11:00:00.000Z');
    fs.writeFileSync(path.join(tmpDir, file1), JSON.stringify({ ts: '10:00' }), 'utf8');
    fs.writeFileSync(path.join(tmpDir, file2), JSON.stringify({ ts: '12:00' }), 'utf8');
    fs.writeFileSync(path.join(tmpDir, file3), JSON.stringify({ ts: '11:00' }), 'utf8');

    const result = readMetricsFiles(tmpDir, 'sort-flow', 20);
    assert.equal(result.length, 3);
    assert.equal(result[0].ts, '10:00');
    assert.equal(result[1].ts, '11:00');
    assert.equal(result[2].ts, '12:00');
  });

  test("returns last N files when window size limits results", function() {
    // Create 5 files for window-flow
    for (var i = 1; i <= 5; i++) {
      var ts = '2026-03-15T' + String(i).padStart(2, '0') + ':00:00.000Z';
      var fname = metricsFileName('window-flow', ts);
      fs.writeFileSync(path.join(tmpDir, fname), JSON.stringify({ seq: i }), 'utf8');
    }

    const result = readMetricsFiles(tmpDir, 'window-flow', 3);
    assert.equal(result.length, 3);
    // Should be the last 3 (seq 3, 4, 5)
    assert.equal(result[0].seq, 3);
    assert.equal(result[1].seq, 4);
    assert.equal(result[2].seq, 5);
  });

  test("returns all files when fewer than window size available (no error)", function() {
    const file1 = metricsFileName('small-flow', '2026-03-15T10:00:00.000Z');
    const file2 = metricsFileName('small-flow', '2026-03-15T11:00:00.000Z');
    fs.writeFileSync(path.join(tmpDir, file1), JSON.stringify({ n: 1 }), 'utf8');
    fs.writeFileSync(path.join(tmpDir, file2), JSON.stringify({ n: 2 }), 'utf8');

    // Request window of 20 but only 2 files exist
    const result = readMetricsFiles(tmpDir, 'small-flow', 20);
    assert.equal(result.length, 2);
  });
});
