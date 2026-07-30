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

test('counts each comma-delimited Chrome trace category independently', () => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-chrome-validator-'));
  try {
    const artifact = path.join(directory, 'category-list.json');
    fs.writeFileSync(
      artifact,
      JSON.stringify({
        traceEvents: [
          {
            name: 'RunTask',
            cat: 'gpu, toplevel.flow',
            ph: 'X',
            dur: 1,
          },
        ],
      })
    );

    const result = run('summarize', artifact);
    assert.equal(result.status, 0, result.stderr);
    assert.deepEqual(JSON.parse(result.stdout).categories, [
      { name: 'gpu', count: 1 },
      { name: 'toplevel.flow', count: 1 },
    ]);
  } finally {
    fs.rmSync(directory, { recursive: true, force: true });
  }
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

    const detectionWithChromeLimit = run('detect', archive, {
      E2E_CHROME_TRACE_MAX_FILE_BYTES: '32',
    });
    assert.equal(
      detectionWithChromeLimit.status,
      0,
      detectionWithChromeLimit.stderr
    );
    assert.equal(
      detectionWithChromeLimit.stdout.trim(),
      'playwright-trace-zip'
    );

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
    const nonJsonWhitespace = path.join(directory, 'non-json-whitespace.json');
    const unrelated = path.join(directory, 'unrelated.json');
    fs.writeFileSync(malformed, '{"traceEvents": [');
    fs.writeFileSync(
      nonJsonWhitespace,
      '{"traceEvents":\u00a0[{"name":"RunTask","ph":"X","dur":1}]}'
    );
    fs.writeFileSync(unrelated, '{"events": []}\n');

    const malformedResult = run('validate', malformed);
    assert.equal(malformedResult.status, 2);
    assert.match(malformedResult.stderr, /invalid JSON/i);

    const nonJsonWhitespaceResult = run('validate', nonJsonWhitespace);
    assert.equal(nonJsonWhitespaceResult.status, 2);
    assert.match(nonJsonWhitespaceResult.stderr, /invalid JSON/i);

    const unrelatedResult = run('validate', unrelated);
    assert.equal(unrelatedResult.status, 3);
    assert.match(unrelatedResult.stderr, /traceEvents/i);
  } finally {
    fs.rmSync(directory, { recursive: true, force: true });
  }
});

test('detects Chrome traceEvents regardless of top-level key order', () => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-chrome-validator-'));
  try {
    const reordered = path.join(directory, 'reordered.json');
    fs.writeFileSync(
      reordered,
      JSON.stringify({
        metadata: { source: 'agent-browser' },
        traceEvents: [{ name: 'RunTask', ph: 'X', dur: 1 }],
      })
    );

    const detection = run('detect', reordered);
    assert.equal(detection.status, 0, detection.stderr);
    assert.equal(detection.stdout.trim(), 'chrome-trace-json');

    const validation = run('validate', reordered);
    assert.equal(validation.status, 0, validation.stderr);
  } finally {
    fs.rmSync(directory, { recursive: true, force: true });
  }
});

test('rejects non-finite Chrome trace numbers', () => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-chrome-validator-'));
  try {
    const cases = [
      ['nan.json', '{"traceEvents":[{"name":"RunTask","ph":"X","dur":NaN}]}'],
      [
        'infinity.json',
        '{"traceEvents":[{"name":"RunTask","ph":"X","dur":Infinity}]}',
      ],
      [
        'overflow.json',
        '{"traceEvents":[{"name":"RunTask","ph":"X","dur":1e9999}]}',
      ],
      [
        'pid-overflow.json',
        '{"traceEvents":[{"name":"RunTask","ph":"X","pid":1e9999,"tid":2,"dur":1}]}',
      ],
    ];

    for (const [name, contents] of cases) {
      const artifact = path.join(directory, name);
      fs.writeFileSync(artifact, contents);
      const result = run('summarize', artifact);
      assert.equal(result.status, 2, `${name}: ${result.stderr}`);
      assert.match(result.stderr, /finite|invalid JSON/i);
    }
  } finally {
    fs.rmSync(directory, { recursive: true, force: true });
  }
});

test('enforces the detection deadline before a late traceEvents field', () => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-chrome-validator-'));
  try {
    const artifact = path.join(directory, 'late-trace-events.json');
    fs.writeFileSync(
      artifact,
      `{${'"padding":0,'.repeat(4_000_000)}"traceEvents":[{"name":"RunTask","ph":"X","dur":1}]}`
    );

    const result = run('detect', artifact, {
      E2E_CHROME_TRACE_TIMEOUT_SECONDS: '1',
    });
    assert.equal(result.status, 4, result.stderr);
    assert.match(result.stderr, /timeout_seconds/i);
  } finally {
    fs.rmSync(directory, { recursive: true, force: true });
  }
});

test('enforces one deadline through trailing top-level fields', () => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-chrome-validator-'));
  try {
    const artifact = path.join(directory, 'trailing-fields.json');
    fs.writeFileSync(
      artifact,
      `{"traceEvents":[{"name":"RunTask","ph":"X","dur":1}],${'"padding":0,'.repeat(4_000_000)}"tail":0}`
    );

    const result = run('validate', artifact, {
      E2E_CHROME_TRACE_TIMEOUT_SECONDS: '1',
    });
    assert.equal(result.status, 4, result.stderr);
    assert.match(result.stderr, /timeout_seconds/i);
  } finally {
    fs.rmSync(directory, { recursive: true, force: true });
  }
});

test('bounds individual and aggregate strings retained by summaries', () => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-chrome-validator-'));
  try {
    const longName = path.join(directory, 'long-name.json');
    const aggregate = path.join(directory, 'aggregate.json');
    fs.writeFileSync(
      longName,
      JSON.stringify({
        traceEvents: [{ name: '123456789', ph: 'X', dur: 1 }],
      })
    );
    fs.writeFileSync(
      aggregate,
      JSON.stringify({
        traceEvents: [{ name: '12345', cat: 'abcde', ph: 'X', dur: 1 }],
      })
    );

    const longNameResult = run('summarize', longName, {
      E2E_CHROME_TRACE_MAX_STRING_BYTES: '8',
    });
    assert.equal(longNameResult.status, 4, longNameResult.stderr);
    assert.match(longNameResult.stderr, /max_string_bytes/i);

    const aggregateResult = run('summarize', aggregate, {
      E2E_CHROME_TRACE_MAX_SUMMARY_STRING_BYTES: '8',
    });
    assert.equal(aggregateResult.status, 4, aggregateResult.stderr);
    assert.match(aggregateResult.stderr, /max_summary_string_bytes/i);
  } finally {
    fs.rmSync(directory, { recursive: true, force: true });
  }
});

test('enforces max event bytes even when one buffer contains the complete event', () => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-chrome-validator-'));
  try {
    const artifact = path.join(directory, 'oversized-event.json');
    fs.writeFileSync(
      artifact,
      JSON.stringify({
        traceEvents: [
          {
            name: 'RunTask',
            ph: 'X',
            dur: 1,
            args: { payload: 'x'.repeat(1024) },
          },
        ],
      })
    );

    const result = run('validate', artifact, {
      E2E_CHROME_TRACE_MAX_EVENT_BYTES: '100',
    });
    assert.equal(result.status, 4, result.stderr);
    assert.match(result.stderr, /max_event_bytes/i);
  } finally {
    fs.rmSync(directory, { recursive: true, force: true });
  }
});

test('accepts the standard Chrome link-ID event phase', () => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-chrome-validator-'));
  try {
    const artifact = path.join(directory, 'link-id.json');
    fs.writeFileSync(
      artifact,
      JSON.stringify({
        traceEvents: [
          { name: 'LinkIds', ph: '=', ts: 1, pid: 1, tid: 1 },
        ],
      })
    );

    const result = run('validate', artifact);
    assert.equal(result.status, 0, result.stderr);
    assert.equal(result.stdout.trim(), 'chrome-trace-json');
  } finally {
    fs.rmSync(directory, { recursive: true, force: true });
  }
});

test('rejects unknown phase tokens and incomplete duration events', () => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-chrome-validator-'));
  try {
    const cases = [
      [
        'unknown-phase.json',
        { traceEvents: [{ name: 'RunTask', ph: 'not-a-phase' }] },
      ],
      [
        'missing-duration.json',
        { traceEvents: [{ name: 'RunTask', ph: 'X' }] },
      ],
      [
        'negative-duration.json',
        { traceEvents: [{ name: 'RunTask', ph: 'X', dur: -1 }] },
      ],
    ];

    for (const [name, contents] of cases) {
      const artifact = path.join(directory, name);
      fs.writeFileSync(artifact, JSON.stringify(contents));
      const result = run('validate', artifact);
      assert.equal(result.status, 3, `${name}: ${result.stderr}`);
      assert.match(result.stderr, /phase|duration|dur/i);
    }
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
