'use strict';

const { describe, test } = require('node:test');
const assert = require('node:assert/strict');
const childProcess = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const { generate, generateRuntimeSupport } = require('../codegen.js');

function writeExecutable(filePath, contents) {
  fs.writeFileSync(filePath, contents, 'utf8');
  fs.chmodSync(filePath, 0o755);
}

function withFakeBrowser(browserScript, callback) {
  const binDir = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-codegen-status-'));
  try {
    writeExecutable(path.join(binDir, 'agent-browser'), browserScript);
    writeExecutable(path.join(binDir, 'sleep'), '#!/usr/bin/env bash\nexit 0\n');
    return callback(binDir);
  } finally {
    fs.rmSync(binDir, { recursive: true, force: true });
  }
}

function runBash(script, binDir, extraEnv, scriptArgs) {
  return childProcess.spawnSync('bash', ['-c', script, 'generated-test'].concat(scriptArgs || []), {
    encoding: 'utf8',
    env: Object.assign({}, process.env, extraEnv, {
      PATH: binDir + path.delimiter + process.env.PATH,
    }),
  });
}

function visibilityBrowserScript() {
  return [
    '#!/usr/bin/env bash',
    'printf \'%s\\n\' "$*" >> "${AGENT_BROWSER_LOG:?}"',
    'if [ "${AGENT_BROWSER_STATUS:-0}" -ne 0 ]; then',
    '  exit "$AGENT_BROWSER_STATUS"',
    'fi',
    'printf \'%s\\n\' "${AGENT_BROWSER_OUTPUT:-}"',
  ].join('\n');
}

function runPollNotVisible(output, status, session) {
  return withFakeBrowser(visibilityBrowserScript(), function(binDir) {
    const logPath = path.join(binDir, 'browser.log');
    const support = generateRuntimeSupport();
    const script = [
      'set -uo pipefail',
      'CONTINUE_ON_ERROR=false',
      support,
      'set +e',
      '_poll_not_visible "#dialog" "check-dialog" 1 "' + (session || '') + '"',
      'exit $?',
    ].join('\n');
    const result = runBash(script, binDir, {
      AGENT_BROWSER_OUTPUT: output,
      AGENT_BROWSER_STATUS: String(status),
      AGENT_BROWSER_LOG: logPath,
    });
    result.browserLog = fs.existsSync(logPath) ? fs.readFileSync(logPath, 'utf8') : '';
    return result;
  });
}

function makeTextFlow(expect, session) {
  return {
    name: 'status-safe-text-assertion',
    description: 'Runtime status propagation regression',
    steps: [{
      id: 'verify-text',
      action: 'Wait 0',
      type: 'wait',
      operands: { seconds: 0 },
      expects: [expect],
      session: session || undefined,
    }],
  };
}

function snapshotBrowserScript() {
  return [
    '#!/usr/bin/env bash',
    'printf \'%s\\n\' "$*" >> "${AGENT_BROWSER_LOG:?}"',
    'for _arg in "$@"; do',
    '  if [ "$_arg" = "snapshot" ]; then',
    '    if [ "${SNAPSHOT_STATUS:-0}" -ne 0 ]; then exit "$SNAPSHOT_STATUS"; fi',
    '    printf \'%s\\n\' "${SNAPSHOT_OUTPUT:-}"',
    '    exit 0',
    '  fi',
    'done',
    'exit 0',
  ].join('\n');
}

function runTextFlow(expect, options) {
  const opts = options || {};
  return withFakeBrowser(snapshotBrowserScript(), function(binDir) {
    const logPath = path.join(binDir, 'browser.log');
    const script = generate(makeTextFlow(expect, opts.session), 'status-safe-text-assertion');
    const result = runBash(script, binDir, {
      AGENT_BROWSER_LOG: logPath,
      SNAPSHOT_OUTPUT: opts.snapshotOutput || '',
      SNAPSHOT_STATUS: String(opts.snapshotStatus || 0),
    }, opts.scriptArgs);
    result.browserLog = fs.existsSync(logPath) ? fs.readFileSync(logPath, 'utf8') : '';
    return result;
  });
}

describe('_poll_not_visible runtime status safety', function() {
  test('succeeds only when agent-browser returns literal false', function() {
    assert.equal(runPollNotVisible('false', 0).status, 0);
    assert.equal(runPollNotVisible('true', 0).status, 1);
  });

  test('returns status 2 when agent-browser command fails', function() {
    const result = runPollNotVisible('', 7);
    assert.equal(result.status, 2, result.stderr);
  });

  test('returns status 2 when agent-browser output is invalid', function() {
    const result = runPollNotVisible('unexpected', 0);
    assert.equal(result.status, 2, result.stderr);
  });

  test('preserves the optional session argument', function() {
    const result = runPollNotVisible('false', 0, 'office');
    assert.equal(result.status, 0, result.stderr);
    assert.match(result.browserLog, /--session office is visible #dialog/);
  });
});

describe('text assertion runtime status safety', function() {
  test('text-visible reports snapshot command failure as infrastructure failure', function() {
    const result = runTextFlow(
      { type: 'text-visible', raw: "text 'Dashboard' on page", text: 'Dashboard' },
      { snapshotStatus: 7 }
    );
    assert.equal(result.status, 1, result.stdout + result.stderr);
    assert.match(result.stdout, /agent-browser snapshot failed/);
    assert.doesNotMatch(result.stdout, /text 'Dashboard' not found on page/);
  });

  test('text-not-visible cannot pass when the snapshot command fails', function() {
    const result = runTextFlow(
      { type: 'text-not-visible', raw: "text 'Failure' not on page", text: 'Failure' },
      { snapshotStatus: 7 }
    );
    assert.equal(result.status, 1, result.stdout + result.stderr);
    assert.match(result.stdout, /agent-browser snapshot failed/);
  });

  test('snapshot infrastructure failure remains failed with continue-on-error', function() {
    const result = runTextFlow(
      { type: 'text-not-visible', raw: "text 'Failure' not on page", text: 'Failure' },
      { snapshotStatus: 7, scriptArgs: ['--continue-on-error'] }
    );
    assert.equal(result.status, 1, result.stdout + result.stderr);
    assert.match(result.stdout, /FAIL: 1 steps failed: verify-text/);
    assert.match(result.stdout, /agent-browser snapshot failed/);
  });

  test('text snapshots preserve the optional session argument', function() {
    const result = runTextFlow(
      { type: 'text-visible', raw: "text 'Dashboard' on page", text: 'Dashboard' },
      { snapshotOutput: 'Dashboard', session: 'office' }
    );
    assert.equal(result.status, 0, result.stdout + result.stderr);
    assert.match(result.browserLog, /--session office snapshot/);
  });

  test('preserves successful visible and not-visible assertions', function() {
    const visible = runTextFlow(
      { type: 'text-visible', raw: "text 'Dashboard' on page", text: 'Dashboard' },
      { snapshotOutput: 'Dashboard' }
    );
    const notVisible = runTextFlow(
      { type: 'text-not-visible', raw: "text 'Failure' not on page", text: 'Failure' },
      { snapshotOutput: 'Dashboard' }
    );
    assert.equal(visible.status, 0, visible.stdout + visible.stderr);
    assert.equal(notVisible.status, 0, notVisible.stdout + notVisible.stderr);
  });
});
