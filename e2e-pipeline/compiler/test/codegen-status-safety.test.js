'use strict';

const { describe, test } = require('node:test');
const assert = require('node:assert/strict');
const childProcess = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const { generate, generateRuntimeSupport, singleQuote } = require('../codegen.js');

const RUNTIME_BASH = fs.existsSync('/bin/bash') ? '/bin/bash' : 'bash';

function resolveXmllint(env) {
  const commands = env.XMLLINT ? [env.XMLLINT] : ['xmllint'];

  for (const command of commands) {
    const probe = childProcess.spawnSync(command, ['--version'], {
      env,
      stdio: 'ignore',
    });
    if (!probe.error && probe.status === 0) return command;
  }
  return null;
}

const XMLLINT_COMMAND = resolveXmllint(process.env);
const XMLLINT_TEST_OPTIONS = XMLLINT_COMMAND
  ? {}
  : { skip: 'xmllint is unavailable via XMLLINT or PATH' };

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

const COMPLEX_STEP_ID = '步驟<&"\'\nline\rreturn\ttab$()../path/`tick`';
const COMPLEX_FLOW_NAME = '流程 "quoted" \\ path\nline\rreturn\ttab\bbackspace\fformfeed';

function withIdentityReports(stepId, callback) {
  return withFakeBrowser('#!/usr/bin/env bash\nexit 0\n', function(binDir) {
    const metricsPath = path.join(binDir, 'metrics.json');
    const junitPath = path.join(binDir, 'junit.xml');
    const script = generate({
      name: 'step-identity-round-trip',
      steps: [{
        id: stepId,
        action: 'Wait 0',
        type: 'wait',
        operands: { seconds: 0 },
      }],
    }, 'step-identity-round-trip');
    const result = runBash(script, binDir, {}, [
      '--metrics-output', metricsPath,
      '--junit', junitPath,
    ]);
    return callback({ result, metricsPath, junitPath });
  });
}

describe('xmllint test dependency discovery', function() {
  test('uses a PATH-provided xmllint when no fixed absolute path is available', function() {
    const binDir = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-xmllint-path-'));
    try {
      writeExecutable(path.join(binDir, 'xmllint'), '#!/bin/sh\nexit 0\n');
      assert.equal(resolveXmllint({ PATH: binDir }), 'xmllint');
    } finally {
      fs.rmSync(binDir, { recursive: true, force: true });
    }
  });

  test('reports xmllint unavailable when neither override nor PATH can provide it', function() {
    const emptyBinDir = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-xmllint-empty-'));
    try {
      assert.equal(resolveXmllint({ PATH: emptyBinDir }), null);
    } finally {
      fs.rmSync(emptyBinDir, { recursive: true, force: true });
    }
  });

  test('treats an explicit unavailable XMLLINT override as authoritative', function() {
    const binDir = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-xmllint-override-'));
    try {
      writeExecutable(path.join(binDir, 'xmllint'), '#!/bin/sh\nexit 0\n');
      assert.equal(resolveXmllint({
        PATH: binDir,
        XMLLINT: path.join(binDir, 'missing-xmllint'),
      }), null);
    } finally {
      fs.rmSync(binDir, { recursive: true, force: true });
    }
  });
});

describe('cross-site polling assertion runtime safety', function() {
  test('convertible element-visible snapshots use the named session', function() {
    const result = runPollingAssertion({
      type: 'element-visible', raw: 'Dashboard heading visible', elementName: 'Dashboard heading',
      selector: 'role=heading[name="Dashboard"]',
    }, { snapshotOutput: '- heading "Dashboard" [ref=e1]' });
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

  test('one clean generic URI line is accepted as URL evidence', function() {
    for (const urlOutput of [
      'about:blank',
      'data:text/html,<h1>Dashboard</h1>',
      'file:///tmp/dashboard.html',
      'chrome://settings/dashboard',
      'myapp+test.v2:dashboard',
      'custom:',
    ]) {
      const notContains = runPollingAssertion(
        { type: 'url-not-contains', raw: 'url does not contain forbidden', value: 'forbidden' },
        { urlOutput }
      );
      assert.equal(notContains.status, 0, notContains.stdout + notContains.stderr);
      assert.match(notContains.browserLog, /--session office get url/);
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

  test('real agent-browser snapshot first-line shapes are valid evidence', function() {
    const snapshots = [
      '(empty page)',
      '- application "App"',
      '- article',
      '- toolbar "Tools"',
    ];
    for (const snapshotOutput of snapshots) {
      const result = withFakeBrowser(snapshotBrowserScript(), function(binDir) {
        const support = generateRuntimeSupport();
        return runBash([
          'set -uo pipefail',
          support,
          '_capture_snapshot "office" >/dev/null',
        ].join('\n'), binDir, {
          AGENT_BROWSER_LOG: path.join(binDir, 'browser.log'),
          SNAPSHOT_OUTPUT: snapshotOutput,
          SNAPSHOT_STATUS: '0',
        });
      });
      assert.equal(result.status, 0, snapshotOutput + ': ' + result.stdout + result.stderr);
    }
  });

  test('empty or malformed snapshot output is reported as infrastructure failure', function() {
    for (const snapshotOutput of [
      '',
      'agent-browser internal error',
      'agent-browser internal error\n- heading "Dashboard" [ref=e1]',
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

describe('generated assertion failure-message shell safety', function() {
  test('quotes every user-controlled assertion diagnostic as literal shell data', function() {
    const hostile = 'literal "quote" \'single\' $EXPAND $(touch "$FAILURE_MARKER") `touch "$FAILURE_MARKER"` \\slash\nnext-line';
    const step = {
      id: 'hostile-assertion-messages',
      action: 'Wait 0',
      type: 'wait',
      operands: { seconds: 0 },
      expects: [
        { type: 'element-visible', elementName: hostile, selector: 'role=heading[name="Home"]' },
        { type: 'element-visible', elementName: hostile, selector: 'css=.home' },
        { type: 'element-not-visible', elementName: hostile, selector: 'role=dialog' },
        { type: 'url-contains', value: hostile },
        { type: 'url-not-contains', value: hostile },
        { type: 'text-visible', text: hostile },
        { type: 'text-not-visible', text: hostile },
        {
          type: 'or-visible',
          elements: [
            { elementName: hostile, selector: 'role=heading' },
            { elementName: hostile, selector: 'role=dialog' },
          ],
        },
      ],
    };
    const script = generate({ name: 'hostile-assertion-messages', steps: [step] }, 'hostile-assertion-messages');
    const failureLines = script.split('\n').filter(line => line.includes('_handle_failure "hostile-assertion-messages"'));
    const timeout = '"${WAIT_TIMEOUT:-10}"';
    const expectedShellMessages = [
      singleQuote('agent-browser snapshot probe failed for ' + hostile),
      singleQuote(hostile + ' not in a11y tree after ') + timeout + singleQuote('s'),
      singleQuote(hostile + ' not visible after ') + timeout + singleQuote('s'),
      singleQuote('agent-browser visibility probe failed for ' + hostile),
      singleQuote(hostile + ' still visible after ') + timeout + singleQuote('s (expected not visible)'),
      singleQuote('url does not contain ' + hostile + ' after ') + timeout + singleQuote('s'),
      singleQuote('url still contains ' + hostile + ' after ') + timeout + singleQuote('s'),
      singleQuote("text '" + hostile + "' not found on page"),
      singleQuote("text '" + hostile + "' should NOT be on page but was found"),
      singleQuote('neither ' + hostile + ' nor ' + hostile + ' visible after ') + timeout + singleQuote('s'),
    ];

    expectedShellMessages.forEach(function(message) {
      assert.ok(
        script.includes(message),
        'expected shell-quoted literal failure message: ' + message + '\nGenerated failure calls:\n' + failureLines.join('\n')
      );
    });

    const syntax = childProcess.spawnSync(RUNTIME_BASH, ['-n'], { input: script, encoding: 'utf8' });
    assert.equal(syntax.status, 0, syntax.stdout + syntax.stderr);
  });
});

describe('step ID runtime and artifact safety', function() {
  test('metrics JSON decodes the exact raw step ID', function() {
    withIdentityReports(COMPLEX_STEP_ID, function(report) {
      assert.equal(report.result.status, 0, report.result.stdout + report.result.stderr);
      const metrics = JSON.parse(fs.readFileSync(report.metricsPath, 'utf8'));
      assert.equal(metrics.steps[0].id, COMPLEX_STEP_ID);
    });
  });

  test('JUnit XML decodes the exact raw step ID including control whitespace', XMLLINT_TEST_OPTIONS, function() {
    withIdentityReports(COMPLEX_STEP_ID, function(report) {
      assert.equal(report.result.status, 0, report.result.stdout + report.result.stderr);
      const xpath = childProcess.spawnSync(
        XMLLINT_COMMAND,
        ['--xpath', 'string(/testsuites/testsuite/testcase/@name)', report.junitPath],
        { encoding: 'utf8' }
      );
      assert.equal(xpath.status, 0, xpath.stdout + xpath.stderr);
      assert.equal(xpath.stdout.slice(0, -1), COMPLEX_STEP_ID);
    });
  });

  test('hostile step IDs remain literal and failure screenshots stay inside the artifact directory', function() {
    withFakeBrowser([
      '#!/usr/bin/env bash',
      'printf \'%s\\n\' "$*" >> "${AGENT_BROWSER_LOG:?}"',
      'for _arg in "$@"; do [ "$_arg" = "open" ] && exit 1; done',
      'exit 0',
    ].join('\n'), function(binDir) {
      const logPath = path.join(binDir, 'browser.log');
      const screenshotDir = path.join(binDir, 'screenshots');
      const markerPath = path.join(binDir, 'step-id-expanded');
      const hostileId = 'x/../../owned$(touch "$STEP_MARKER")\nnext-line';
      const script = generate({
        name: 'hostile-step-id',
        variables: { base_url: 'https://example.test' },
        steps: [{
          id: hostileId,
          action: 'Navigate to /home',
          type: 'navigate',
          operands: { urlPath: '/home' },
        }],
      }, 'hostile-step-id');
      const result = runBash(script, binDir, {
        AGENT_BROWSER_LOG: logPath,
        E2E_SCREENSHOT_DIR: screenshotDir,
        STEP_MARKER: markerPath,
      });

      assert.equal(result.status, 1, result.stdout + result.stderr);
      assert.equal(fs.existsSync(markerPath), false, 'step ID command substitution must remain literal');
      assert.match(result.stdout, /owned\$\(touch/);
      assert.match(result.stdout, /next-line/);
      const screenshotLine = fs.readFileSync(logPath, 'utf8').split('\n').find(line => line.includes('screenshot '));
      assert.ok(screenshotLine, 'failure diagnostics must request a screenshot');
      const screenshotPath = screenshotLine.slice(screenshotLine.indexOf('screenshot ') + 'screenshot '.length);
      assert.ok(
        path.resolve(screenshotPath).startsWith(path.resolve(screenshotDir) + path.sep),
        'failure screenshot escaped artifact directory: ' + screenshotPath
      );
    });
  });

  test('requested step screenshots sanitize only the artifact filename', function() {
    withFakeBrowser([
      '#!/usr/bin/env bash',
      'printf \'%s\\n\' "$*" >> "${AGENT_BROWSER_LOG:?}"',
      'exit 0',
    ].join('\n'), function(binDir) {
      const logPath = path.join(binDir, 'browser.log');
      const screenshotDir = path.join(binDir, 'screenshots');
      const stepId = 'x/../../post-shot';
      const script = generate({
        name: 'requested-step-screenshot',
        steps: [{
          id: stepId,
          action: 'Wait 0',
          type: 'wait',
          operands: { seconds: 0 },
          screenshot: true,
        }],
      }, 'requested-step-screenshot');
      const result = runBash(script, binDir, {
        AGENT_BROWSER_LOG: logPath,
        E2E_SCREENSHOT_DIR: screenshotDir,
      });

      assert.equal(result.status, 0, result.stdout + result.stderr);
      assert.match(result.stdout, /x\/\.\.\/\.\.\/post-shot/);
      const screenshotLine = fs.readFileSync(logPath, 'utf8').split('\n').find(line => line.includes('screenshot '));
      assert.ok(screenshotLine, 'step must request its configured screenshot');
      const screenshotPath = screenshotLine.slice(screenshotLine.indexOf('screenshot ') + 'screenshot '.length);
      assert.ok(
        path.resolve(screenshotPath).startsWith(path.resolve(screenshotDir) + path.sep),
        'requested screenshot escaped artifact directory: ' + screenshotPath
      );
    });
  });
});

describe('metrics flow identity safety', function() {
  test('metrics JSON round-trips the exact flow name', function() {
    withFakeBrowser('#!/usr/bin/env bash\nexit 0\n', function(binDir) {
      const metricsPath = path.join(binDir, 'metrics.json');
      const script = generate({
        name: COMPLEX_FLOW_NAME,
        steps: [{ id: 'wait', action: 'Wait 0', type: 'wait', operands: { seconds: 0 } }],
      }, COMPLEX_FLOW_NAME);
      const result = runBash(script, binDir, {}, ['--metrics-output', metricsPath]);
      assert.equal(result.status, 0, result.stdout + result.stderr);
      const metrics = JSON.parse(fs.readFileSync(metricsPath, 'utf8'));
      assert.equal(metrics.flow, COMPLEX_FLOW_NAME);
    });
  });
});

describe('metrics failure diagnostic safety', function() {
  test('metrics JSON round-trips failure messages with JSON control characters', function() {
    const hostile = 'quote " slash \\ line\nreturn\rtab\tbackspace\bformfeed\fcontrol\u0001';
    withFakeBrowser(snapshotBrowserScript(), function(binDir) {
      const metricsPath = path.join(binDir, 'metrics.json');
      const script = generate(makeTextFlow({
        type: 'text-visible',
        raw: 'hostile text visible',
        text: hostile,
      }), 'metrics-failure-message');
      const result = runBash(script, binDir, {
        AGENT_BROWSER_LOG: path.join(binDir, 'browser.log'),
        SNAPSHOT_OUTPUT: '- document "safe"',
      }, ['--continue-on-error', '--metrics-output', metricsPath]);
      assert.equal(result.status, 1, result.stdout + result.stderr);
      const metrics = JSON.parse(fs.readFileSync(metricsPath, 'utf8'));
      assert.equal(metrics.steps[0].failure_msg, "text '" + hostile + "' not found on page");
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
        SNAPSHOT_OUTPUT: '- heading "Dashboard" [ref=e1]',
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
      'agent-browser internal error\n- text "Dashboard"',
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
      { snapshotOutput: '- heading "Dashboard" [ref=e1]', session: 'office' }
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
      { snapshotOutput: '- text "Dashboard"' }
    );
    assert.equal(visible.status, 0, visible.stdout + visible.stderr);
    assert.equal(notVisible.status, 0, notVisible.stdout + notVisible.stderr);
  });
});
