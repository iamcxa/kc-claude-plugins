'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { execFileSync, spawnSync } = require('node:child_process');
const { test } = require('node:test');

const pipelineRoot = path.resolve(__dirname, '..', '..');
const validator = path.join(
  pipelineRoot,
  'scripts',
  'validate-chrome-trace.py'
);
const fixture = path.join(
  __dirname,
  'fixtures',
  'chrome-trace-event.json'
);

function run(command, artifact, extraEnv) {
  return spawnSync('python3', [validator, command, artifact], {
    encoding: 'utf8',
    env: { ...process.env, ...(extraEnv || {}) },
  });
}

test('validates and detects a real agent-browser Chrome trace JSON fixture', () => {
  const detection = run('detect', fixture);
  assert.equal(detection.status, 0, detection.stderr);
  assert.equal(detection.stdout.trim(), 'chrome-trace-json');

  const validation = run('validate', fixture);
  assert.equal(validation.status, 0, validation.stderr);
  assert.equal(validation.stdout.trim(), 'chrome-trace-json');
});

test('summarizes Chrome events without materializing the full trace', () => {
  const result = run('summarize', fixture);
  assert.equal(result.status, 0, result.stderr);
  const summary = JSON.parse(result.stdout);
  assert.equal(summary.format, 'chrome-trace-json');
  assert.equal(summary.trace_event_count, 4);
  assert.equal(summary.metadata_event_count, 3);
  assert.equal(summary.duration_event_count, 1);
  assert.equal(summary.process_count, 3);
  assert.equal(summary.thread_count, 3);
  assert.deepEqual(summary.categories, [
    { name: '__metadata', count: 3 },
    { name: 'ipc', count: 1 },
  ]);
  assert.deepEqual(summary.longest_events, [
    {
      name: 'Release QoS Voucher',
      category: 'ipc',
      duration_us: 2,
      pid: 35391,
      tid: 58305442,
    },
  ]);
});

test('detects Playwright ZIP before attempting Chrome JSON validation', () => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-chrome-validator-'));
  const archive = path.join(directory, 'trace.zip');
  try {
    fs.writeFileSync(path.join(directory, 'trace.trace'), '{}\n');
    execFileSync('zip', ['-q', archive, 'trace.trace'], { cwd: directory });

    const detection = run('detect', archive);
    assert.equal(detection.status, 0, detection.stderr);
    assert.equal(detection.stdout.trim(), 'playwright-trace-zip');

    const validation = run('validate', archive);
    assert.equal(validation.status, 3);
    assert.match(validation.stderr, /expected Chrome trace JSON/i);
  } finally {
    fs.rmSync(directory, { recursive: true, force: true });
  }
});

test('rejects malformed or non-Chrome JSON as an invalid artifact', () => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-chrome-validator-'));
  try {
    const malformed = path.join(directory, 'malformed.json');
    const unrelated = path.join(directory, 'unrelated.json');
    fs.writeFileSync(malformed, '{"traceEvents": [');
    fs.writeFileSync(unrelated, '{"events": []}\n');

    const malformedResult = run('validate', malformed);
    assert.equal(malformedResult.status, 2);
    assert.match(malformedResult.stderr, /invalid JSON/i);

    const unrelatedResult = run('validate', unrelated);
    assert.equal(unrelatedResult.status, 3);
    assert.match(unrelatedResult.stderr, /traceEvents/i);
  } finally {
    fs.rmSync(directory, { recursive: true, force: true });
  }
});

test('fails closed when file or event-count budgets are exceeded', () => {
  const fileLimit = run('validate', fixture, {
    E2E_CHROME_TRACE_MAX_FILE_BYTES: '32',
  });
  assert.equal(fileLimit.status, 4);
  assert.match(fileLimit.stderr, /max_file_bytes/i);

  const eventLimit = run('validate', fixture, {
    E2E_CHROME_TRACE_MAX_EVENTS: '2',
  });
  assert.equal(eventLimit.status, 4);
  assert.match(eventLimit.stderr, /max_events/i);
});
