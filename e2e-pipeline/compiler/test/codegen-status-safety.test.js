'use strict';

const { describe, test } = require('node:test');
const assert = require('node:assert/strict');
const childProcess = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const { generate, generateRuntimeSupport } = require('../codegen.js');

const RUNTIME_BASH = fs.existsSync('/bin/bash') ? '/bin/bash' : 'bash';

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
  return childProcess.spawnSync(RUNTIME_BASH, ['-c', script, 'generated-test'].concat(scriptArgs || []), {
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
      expects: Array.isArray(expect) ? expect : [expect],
      session: session || undefined,
    }],
  };
}

function runNotVisibleFlow(output, status) {
  return withFakeBrowser(visibilityBrowserScript(), function(binDir) {
    const logPath = path.join(binDir, 'browser.log');
    const script = generate({
      name: 'status-safe-not-visible',
      description: 'Runtime visibility status propagation regression',
      steps: [{
        id: 'check-dialog',
        action: 'Wait 0',
        type: 'wait',
        operands: { seconds: 0 },
        expects: [{
          type: 'element-not-visible',
          raw: 'dialog not visible',
          elementName: 'dialog',
          selector: 'role=dialog',
        }],
      }],
    }, 'status-safe-not-visible');
    return runBash(script, binDir, {
      AGENT_BROWSER_OUTPUT: output,
      AGENT_BROWSER_STATUS: String(status),
      AGENT_BROWSER_LOG: logPath,
    });
  });
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

function assertionBrowserScript() {
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
    'if [ "${*: -2}" = "get url" ]; then',
    '  if [ "${URL_STATUS:-0}" -ne 0 ]; then exit "$URL_STATUS"; fi',
    '  printf \'%s\\n\' "${URL_OUTPUT:-}"',
    '  exit 0',
    'fi',
    'exit 0',
  ].join('\n');
}

function runPollingAssertion(expect, options) {
  const opts = options || {};
  return withFakeBrowser(assertionBrowserScript(), function(binDir) {
    const logPath = path.join(binDir, 'browser.log');
    const script = generate(makeTextFlow(expect, opts.session || 'office'), 'status-safe-polling-assertion');
    const result = runBash(script, binDir, {
      AGENT_BROWSER_LOG: logPath,
      SNAPSHOT_OUTPUT: opts.snapshotOutput || '',
      SNAPSHOT_STATUS: String(opts.snapshotStatus || 0),
      URL_OUTPUT: opts.urlOutput || '',
      URL_STATUS: String(opts.urlStatus || 0),
      WAIT_TIMEOUT: '1',
    });
    result.browserLog = fs.existsSync(logPath) ? fs.readFileSync(logPath, 'utf8') : '';
    return result;
  });
}

describe('cross-site polling assertion runtime safety', function() {
  test('convertible element-visible snapshots use the named session', function() {
    const result = runPollingAssertion({
      type: 'element-visible', raw: 'Dashboard heading visible', elementName: 'Dashboard heading',
      selector: 'role=heading[name="Dashboard"]',
    }, { snapshotOutput: 'heading "Dashboard"' });
    assert.equal(result.status, 0, result.stdout + result.stderr);
    assert.match(result.browserLog, /--session office snapshot/);
    assert.doesNotMatch(result.browserLog, /^snapshot$/m);
  });

  test('url contains and url not contains use the named session', function() {
    for (const urlOutput of ['http://example.test/dashboard', 'https://example.test/dashboard']) {
      const contains = runPollingAssertion(
        { type: 'url-contains', raw: 'url contains dashboard', value: 'dashboard' },
        { urlOutput }
      );
      const notContains = runPollingAssertion(
        { type: 'url-not-contains', raw: 'url does not contain login', value: 'login' },
        { urlOutput }
      );
      assert.equal(contains.status, 0, contains.stdout + contains.stderr);
      assert.equal(notContains.status, 0, notContains.stdout + notContains.stderr);
      assert.match(contains.browserLog, /--session office get url/);
      assert.match(notContains.browserLog, /--session office get url/);
      assert.doesNotMatch(contains.browserLog, /^get url$/m);
      assert.doesNotMatch(notContains.browserLog, /^get url$/m);
    }
  });

  test('snapshot command failure is reported as infrastructure failure', function() {
    const result = runPollingAssertion({
      type: 'element-visible', raw: 'Dashboard heading visible', elementName: 'Dashboard heading',
      selector: 'role=heading[name="Dashboard"]',
    }, { snapshotStatus: 7 });
    assert.equal(result.status, 1, result.stdout + result.stderr);
    assert.match(result.stdout, /agent-browser snapshot probe failed/);
    assert.doesNotMatch(result.stdout, /not in a11y tree after/);
  });

  test('empty or malformed snapshot output is reported as infrastructure failure', function() {
    for (const snapshotOutput of [
      '',
      'agent-browser internal error',
      'agent-browser internal error\nheading "Dashboard" [ref=e1]',
    ]) {
      const result = runPollingAssertion({
        type: 'element-visible', raw: 'Dashboard heading visible', elementName: 'Dashboard heading',
        selector: 'role=heading[name="Dashboard"]',
      }, { snapshotOutput });
      assert.equal(result.status, 1, result.stdout + result.stderr);
      assert.match(result.stdout, /agent-browser snapshot probe failed/);
      assert.doesNotMatch(result.stdout, /not in a11y tree after/);
    }
  });

  test('url probe failure and malformed or noisy output are infrastructure failures', function() {
    const invalidEvidence = [
      { urlStatus: 7 },
      { urlOutput: 'not-a-url' },
      { urlOutput: 'agent-browser error: websocket:// disconnected' },
      { urlOutput: 'https://example.test/dashboard warning' },
      { urlOutput: 'diagnostic noise\nhttps://example.test/dashboard' },
      { urlOutput: 'https://example.test/dashboard\nagent-browser warning' },
    ];
    const expectations = [
      { type: 'url-contains', raw: 'url contains dashboard', value: 'dashboard' },
      { type: 'url-not-contains', raw: 'url does not contain login', value: 'login' },
    ];
    for (const expect of expectations) {
      for (const options of invalidEvidence) {
        const result = runPollingAssertion(expect, options);
        assert.equal(result.status, 1, result.stdout + result.stderr);
        assert.match(result.stdout, /agent-browser URL probe failed/);
        assert.doesNotMatch(result.stdout, /url (still contains|does not contain)/);
      }
    }
  });
});

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

describe('generated element-not-visible status reporting', function() {
  test('reports command failure as infrastructure failure', function() {
    const result = runNotVisibleFlow('', 7);
    assert.equal(result.status, 1, result.stdout + result.stderr);
    assert.match(result.stdout, /agent-browser visibility probe failed/);
    assert.doesNotMatch(result.stdout, /still visible/);
  });

  test('retains the ordinary still-visible message on timeout', function() {
    const result = runNotVisibleFlow('true', 0);
    assert.equal(result.status, 1, result.stdout + result.stderr);
    assert.match(result.stdout, /still visible/);
    assert.doesNotMatch(result.stdout, /visibility probe failed/);
  });
});

describe('generated cleanup session deduplication', function() {
  test('closes inherited-property session aliases exactly once without default close', function() {
    const aliases = ['toString', 'hasOwnProperty', 'valueOf'];
    withFakeBrowser(snapshotBrowserScript(), function(binDir) {
      const logPath = path.join(binDir, 'browser.log');
      const steps = [];
      aliases.forEach(function(alias) {
        steps.push({ id: alias + '-first', action: 'Wait 0', type: 'wait', operands: { seconds: 0 }, session: alias });
        steps.push({ id: alias + '-second', action: 'Wait 0', type: 'wait', operands: { seconds: 0 }, session: alias });
      });
      const script = generate({ name: 'cleanup-inherited-aliases', steps }, 'cleanup-inherited-aliases');
      const result = runBash(script, binDir, {
        AGENT_BROWSER_LOG: logPath,
        SNAPSHOT_OUTPUT: '',
        SNAPSHOT_STATUS: '0',
      });
      assert.equal(result.status, 0, result.stdout + result.stderr);
      const logLines = fs.readFileSync(logPath, 'utf8').trim().split('\n');
      aliases.forEach(function(alias) {
        assert.equal(
          logLines.filter(line => line === '--session ' + alias + ' close').length,
          1,
          'cleanup must close session ' + alias + ' exactly once. Log: ' + logLines.join(' | ')
        );
      });
      assert.equal(
        logLines.filter(line => line === 'close').length,
        0,
        'cross-site cleanup must not emit default close. Log: ' + logLines.join(' | ')
      );
    });
  });

  test('keeps one default close for a flow without named sessions', function() {
    withFakeBrowser(snapshotBrowserScript(), function(binDir) {
      const logPath = path.join(binDir, 'browser.log');
      const script = generate({
        name: 'cleanup-default-session',
        steps: [{ id: 'wait', action: 'Wait 0', type: 'wait', operands: { seconds: 0 } }],
      }, 'cleanup-default-session');
      const result = runBash(script, binDir, {
        AGENT_BROWSER_LOG: logPath,
        SNAPSHOT_OUTPUT: '',
        SNAPSHOT_STATUS: '0',
      });
      assert.equal(result.status, 0, result.stdout + result.stderr);
      assert.deepEqual(fs.readFileSync(logPath, 'utf8').trim().split('\n'), ['close']);
    });
  });
});

function diagnosticBrowserScript() {
  return [
    '#!/usr/bin/env bash',
    'printf \'%s\\n\' "$*" >> "${AGENT_BROWSER_LOG:?}"',
    'case " $* " in',
    '  *" click "*) exit "${ACTION_STATUS:-0}" ;;',
    '  *" get url "*) printf \'%s\\n\' "${URL_OUTPUT:-https://example.test/login}" ;;',
    '  *" snapshot "*) printf \'%s\\n\' \'- document:\' \'  - heading "Login" [ref=e1]\' ;;',
    'esac',
    'exit 0',
  ].join('\n');
}

function assertOnlyNamedDiagnosticCalls(log) {
  assert.match(log, /--session office screenshot \/tmp\/e2e-screenshots\/fail-/);
  assert.match(log, /--session office get url/);
  assert.match(log, /--session office snapshot/);
  assert.doesNotMatch(log, /^screenshot /m);
  assert.doesNotMatch(log, /^get url$/m);
  assert.doesNotMatch(log, /^snapshot$/m);
}

describe('named-session failure diagnostics', function() {
  test('every generated cross-site action and assertion failure passes the session explicitly', function() {
    const steps = [
      { id: 'nav', action: 'Navigate', type: 'navigate', operands: { urlPath: '/home' }, session: 'office' },
      { id: 'click', action: 'Click', type: 'click', operands: { selector: 'css=.submit' }, session: 'office' },
      { id: 'fill', action: 'Fill', type: 'fill', operands: { selector: 'css=input', value: 'value' }, session: 'office' },
      {
        id: 'assertions', action: 'Wait 0', type: 'wait', operands: { seconds: 0 }, session: 'office',
        expects: [
          { type: 'element-visible', elementName: 'heading', selector: 'role=heading[name="Home"]' },
          { type: 'element-visible', elementName: 'custom', selector: 'css=.custom' },
          { type: 'element-not-visible', elementName: 'dialog', selector: 'role=dialog' },
          { type: 'url-contains', value: 'home' },
          { type: 'url-not-contains', value: 'login' },
          { type: 'text-visible', text: 'Home' },
          { type: 'text-not-visible', text: 'Error' },
          {
            type: 'or-visible',
            elements: [
              { elementName: 'heading', selector: 'role=heading' },
              { elementName: 'dialog', selector: 'role=dialog' },
            ],
          },
        ],
      },
    ];
    const script = generate({ name: 'all-named-failures', steps }, 'all-named-failures');
    const stepSection = script.slice(script.indexOf('echo "[1/4]'), script.indexOf('# Emit metrics JSON'));
    const failureLines = stepSection.split('\n').filter(line => line.includes('_handle_failure "'));
    assert.ok(failureLines.length >= 13, 'expected every failure path in generated step section');
    failureLines.forEach(function(line) {
      assert.match(line, / 'office'$/, 'failure call must end with explicit named session: ' + line);
    });
  });

  test('action failures keep screenshot, URL, and snapshot diagnostics in the named session', function() {
    withFakeBrowser(diagnosticBrowserScript(), function(binDir) {
      const logPath = path.join(binDir, 'browser.log');
      const script = generate({
        name: 'named-action-failure',
        steps: [{
          id: 'click-submit', action: 'Click submit', type: 'click',
          operands: { selector: 'role=button[name="Submit"]' }, session: 'office',
        }],
      }, 'named-action-failure');
      const result = runBash(script, binDir, {
        ACTION_STATUS: '7', AGENT_BROWSER_LOG: logPath,
      });
      assert.equal(result.status, 1, result.stdout + result.stderr);
      assertOnlyNamedDiagnosticCalls(fs.readFileSync(logPath, 'utf8'));
    });
  });

  test('assertion failures keep screenshot, URL, and snapshot diagnostics in the named session', function() {
    withFakeBrowser(diagnosticBrowserScript(), function(binDir) {
      const logPath = path.join(binDir, 'browser.log');
      const script = generate(makeTextFlow(
        { type: 'url-contains', raw: 'url contains dashboard', value: 'dashboard' },
        'office'
      ), 'named-assertion-failure');
      const result = runBash(script, binDir, {
        AGENT_BROWSER_LOG: logPath, URL_OUTPUT: 'https://example.test/login', WAIT_TIMEOUT: '1',
      });
      assert.equal(result.status, 1, result.stdout + result.stderr);
      assertOnlyNamedDiagnosticCalls(fs.readFileSync(logPath, 'utf8'));
    });
  });
});

describe('text assertion runtime status safety', function() {
  test('treats hostile session command substitution as a literal value', function() {
    const hostileSession = '$(printf exploited > "$SESSION_MARKER")';
    withFakeBrowser(snapshotBrowserScript(), function(binDir) {
      const logPath = path.join(binDir, 'browser.log');
      const markerPath = path.join(binDir, 'session-executed');
      const script = generate(makeTextFlow(
        { type: 'text-visible', raw: "text 'Dashboard' on page", text: 'Dashboard' },
        hostileSession
      ), 'status-safe-text-assertion');
      const result = runBash(script, binDir, {
        AGENT_BROWSER_LOG: logPath,
        SESSION_MARKER: markerPath,
        SNAPSHOT_OUTPUT: 'heading "Dashboard" [ref=e1]',
        SNAPSHOT_STATUS: '0',
      });
      assert.equal(result.status, 0, result.stdout + result.stderr);
      assert.equal(fs.existsSync(markerPath), false, 'session command substitution must not execute');
      const browserLog = fs.readFileSync(logPath, 'utf8');
      assert.ok(
        browserLog.includes('--session ' + hostileSession + ' snapshot'),
        'agent-browser must receive the literal session. Log: ' + browserLog
      );
    });
  });

  test('single-quotes session arguments across generated expectation helpers', function() {
    const hostileSession = '$(printf exploited)';
    const step = {
      id: 'hostile-session-expects',
      action: 'Wait 0',
      type: 'wait',
      operands: { seconds: 0 },
      session: hostileSession,
      expects: [
        { type: 'element-visible', raw: 'thing visible', elementName: 'thing', selector: 'css=.thing' },
        { type: 'element-not-visible', raw: 'dialog not visible', elementName: 'dialog', selector: 'role=dialog' },
        { type: 'text-visible', raw: "text 'Dashboard' on page", text: 'Dashboard' },
        {
          type: 'or-visible',
          raw: 'thing visible or dialog visible',
          elements: [
            { elementName: 'thing', selector: 'css=.thing' },
            { elementName: 'dialog', selector: 'role=dialog' },
          ],
        },
      ],
    };
    const script = generate({ name: 'hostile-session-expects', steps: [step] }, 'hostile-session-expects');
    const quotedSession = "'$(printf exploited)'";
    assert.ok(script.includes('_poll_visible \'css=.thing\' "hostile-session-expects" "${WAIT_TIMEOUT:-10}" ' + quotedSession));
    assert.ok(script.includes('_poll_not_visible \'role=dialog\' "hostile-session-expects" "${WAIT_TIMEOUT:-10}" ' + quotedSession));
    assert.ok(script.includes('_capture_snapshot ' + quotedSession));
    assert.ok(script.includes('_poll_or_visible "hostile-session-expects" "${WAIT_TIMEOUT:-10}" ' + quotedSession));
  });

  test('text-visible reports snapshot command failure as infrastructure failure', function() {
    const result = runTextFlow(
      { type: 'text-visible', raw: "text 'Dashboard' on page", text: 'Dashboard' },
      { snapshotStatus: 7 }
    );
    assert.equal(result.status, 1, result.stdout + result.stderr);
    assert.match(result.stdout, /agent-browser snapshot failed/);
    assert.doesNotMatch(result.stdout, /text 'Dashboard' not found on page/);
  });

  test('text-visible rejects empty and malformed snapshot evidence', function() {
    for (const snapshotOutput of [
      '',
      'agent-browser internal error',
      'agent-browser internal error\ntext "Dashboard"',
    ]) {
      const result = runTextFlow(
        { type: 'text-visible', raw: "text 'Dashboard' on page", text: 'Dashboard' },
        { snapshotOutput }
      );
      assert.equal(result.status, 1, result.stdout + result.stderr);
      assert.match(result.stdout, /agent-browser snapshot failed/);
      assert.doesNotMatch(result.stdout, /text 'Dashboard' not found on page/);
    }
  });

  test('text-not-visible cannot pass when the snapshot command fails', function() {
    const result = runTextFlow(
      { type: 'text-not-visible', raw: "text 'Failure' not on page", text: 'Failure' },
      { snapshotStatus: 7 }
    );
    assert.equal(result.status, 1, result.stdout + result.stderr);
    assert.match(result.stdout, /agent-browser snapshot failed/);
  });

  test('snapshot infrastructure failure remains nonzero despite EXIT cleanup', function() {
    const result = runTextFlow(
      { type: 'text-not-visible', raw: "text 'Failure' not on page", text: 'Failure' },
      { snapshotStatus: 7, scriptArgs: ['--continue-on-error'] }
    );
    assert.equal(result.status, 1, result.stdout + result.stderr);
    assert.match(result.stdout, /FAIL: 1 steps failed: verify-text/);
    assert.match(result.stdout, /agent-browser snapshot failed/);
  });

  test('counts multiple failed expectations on one step only once', function() {
    const result = runTextFlow([
      { type: 'text-visible', raw: "text 'Dashboard' on page", text: 'Dashboard' },
      { type: 'text-not-visible', raw: "text 'Failure' not on page", text: 'Failure' },
    ], { snapshotStatus: 7, scriptArgs: ['--continue-on-error'] });
    assert.equal(result.status, 1, result.stdout + result.stderr);
    assert.match(result.stdout, /FAIL: 1 steps failed: verify-text/);
    assert.doesNotMatch(result.stdout, /FAIL: 2 steps failed: verify-text verify-text/);
  });

  test('still counts genuinely different failed steps separately', function() {
    const expect = { type: 'text-not-visible', raw: "text 'Failure' not on page", text: 'Failure' };
    const flow = makeTextFlow(expect);
    flow.steps = [
      Object.assign({}, flow.steps[0], { id: 'first' }),
      Object.assign({}, flow.steps[0], { id: 'second' }),
    ];
    const result = withFakeBrowser(snapshotBrowserScript(), function(binDir) {
      const logPath = path.join(binDir, 'browser.log');
      return runBash(generate(flow, flow.name), binDir, {
        AGENT_BROWSER_LOG: logPath,
        SNAPSHOT_OUTPUT: '',
        SNAPSHOT_STATUS: '7',
      }, ['--continue-on-error']);
    });
    assert.equal(result.status, 1, result.stdout + result.stderr);
    assert.match(result.stdout, /FAIL: 2 steps failed: first second/);
  });

  test('text snapshots preserve the optional session argument', function() {
    const result = runTextFlow(
      { type: 'text-visible', raw: "text 'Dashboard' on page", text: 'Dashboard' },
      { snapshotOutput: 'heading "Dashboard" [ref=e1]', session: 'office' }
    );
    assert.equal(result.status, 0, result.stdout + result.stderr);
    assert.match(result.browserLog, /--session office snapshot/);
  });

  test('preserves successful visible and not-visible assertions', function() {
    const visible = runTextFlow(
      { type: 'text-visible', raw: "text 'Dashboard' on page", text: 'Dashboard' },
      { snapshotOutput: '- document:\n  - heading "Dashboard" [ref=e1]' }
    );
    const notVisible = runTextFlow(
      { type: 'text-not-visible', raw: "text 'Failure' not on page", text: 'Failure' },
      { snapshotOutput: 'text "Dashboard"' }
    );
    assert.equal(visible.status, 0, visible.stdout + visible.stderr);
    assert.equal(notVisible.status, 0, notVisible.stdout + notVisible.stderr);
  });
});
