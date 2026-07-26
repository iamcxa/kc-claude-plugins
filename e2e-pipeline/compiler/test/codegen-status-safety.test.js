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

function runVisiblePoll(helper, output, status, session) {
  return withFakeBrowser(visibilityBrowserScript(), function(binDir) {
    const logPath = path.join(binDir, 'browser.log');
    const support = generateRuntimeSupport();
    const invocation = helper === '_poll_or_visible'
      ? '_poll_or_visible "check-choice" 1 "' + (session || '') + '" "#first" "#second"'
      : '_poll_visible "#dialog" "check-dialog" 1 "' + (session || '') + '"';
    const result = runBash([
      'set -uo pipefail',
      'CONTINUE_ON_ERROR=false',
      support,
      'set +e',
      invocation,
      'exit $?',
    ].join('\n'), binDir, {
      AGENT_BROWSER_OUTPUT: output,
      AGENT_BROWSER_STATUS: String(status),
      AGENT_BROWSER_LOG: logPath,
    });
    result.browserLog = fs.existsSync(logPath) ? fs.readFileSync(logPath, 'utf8') : '';
    return result;
  });
}

function artifactName(stepId) {
  return withFakeBrowser('#!/usr/bin/env bash\nexit 0\n', function(binDir) {
    const result = runBash([
      'set -uo pipefail',
      generateRuntimeSupport(),
      '_artifact_name "$STEP_ID"',
    ].join('\n'), binDir, { STEP_ID: stepId });
    assert.equal(result.status, 0, result.stdout + result.stderr);
    return result.stdout;
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

function runVisibleFlow(expect, output, status) {
  return withFakeBrowser(visibilityBrowserScript(), function(binDir) {
    const logPath = path.join(binDir, 'browser.log');
    const script = generate({
      name: 'status-safe-visible',
      description: 'Runtime positive visibility status propagation regression',
      steps: [{
        id: 'check-choice',
        action: 'Wait 0',
        type: 'wait',
        operands: { seconds: 0 },
        expects: [expect],
      }],
    }, 'status-safe-visible');
    return runBash(script, binDir, {
      AGENT_BROWSER_OUTPUT: output,
      AGENT_BROWSER_STATUS: String(status),
      AGENT_BROWSER_LOG: logPath,
      WAIT_TIMEOUT: '1',
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

function runHatchOnlyFlow() {
  return withFakeBrowser('#!/usr/bin/env bash\nexit 0\n', function(binDir) {
    const metricsPath = path.join(binDir, 'metrics.json');
    const junitPath = path.join(binDir, 'junit.xml');
    const script = generate({
      name: 'hatchonly',
      description: 'Hatch-only compiled replay honesty',
      steps: [{
        id: 'manual-only',
        action: 'Take snapshot',
        type: 'snapshot',
        operands: {},
        expects: [{
          type: 'not-automated',
          raw: 'Checked by counsel.',
          reason: 'Checked by counsel.',
        }],
      }],
    }, 'hatchonly');
    const result = runBash(script, binDir, {}, [
      '--metrics-output', metricsPath,
      '--junit', junitPath,
    ]);
    result.generatedScript = script;
    result.metricsJson = fs.existsSync(metricsPath) ? fs.readFileSync(metricsPath, 'utf8') : null;
    result.junitXml = fs.existsSync(junitPath) ? fs.readFileSync(junitPath, 'utf8') : null;
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

describe('positive visibility polling runtime status safety', function() {
  for (const helper of ['_poll_visible', '_poll_or_visible']) {
    test(helper + ' returns status 2 when agent-browser command fails', function() {
      const result = runVisiblePoll(helper, '', 7);
      assert.equal(result.status, 2, result.stderr);
    });

    test(helper + ' returns status 2 when agent-browser output is invalid', function() {
      const result = runVisiblePoll(helper, 'unexpected', 0);
      assert.equal(result.status, 2, result.stderr);
    });
  }

  const positiveExpects = [
    {
      label: 'element-visible',
      value: { type: 'element-visible', elementName: 'custom', selector: 'css=.custom' },
    },
    {
      label: 'or-visible',
      value: {
        type: 'or-visible',
        elements: [
          { elementName: 'first', selector: 'css=.first' },
          { elementName: 'second', selector: 'css=.second' },
        ],
      },
    },
  ];

  for (const expect of positiveExpects) {
    test('generated ' + expect.label + ' reports command failure as infrastructure failure', function() {
      const result = runVisibleFlow(expect.value, '', 7);
      assert.equal(result.status, 1, result.stdout + result.stderr);
      assert.match(result.stdout, /agent-browser visibility probe failed/);
      assert.doesNotMatch(result.stdout, /after 1s/);
    });
  }
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

describe('generated action shell-data safety', function() {
  test('navigate keeps hostile URL paths and failure messages literal', function() {
    withFakeBrowser([
      '#!/usr/bin/env bash',
      'printf \'%s\\n\' "$*" >> "${AGENT_BROWSER_LOG:?}"',
      'for _arg in "$@"; do [ "$_arg" = "open" ] && exit 7; done',
      'exit 0',
    ].join('\n'), function(binDir) {
      const logPath = path.join(binDir, 'browser.log');
      const markerPath = path.join(binDir, 'navigate-expanded');
      const hostilePath = '/owned"$(touch "$ACTION_MARKER")`touch "$ACTION_MARKER"`$ACTION_MARKER';
      const script = generate({
        name: 'hostile-navigate-data',
        variables: { base_url: 'https://example.test' },
        steps: [{
          id: 'navigate-hostile', action: 'Navigate hostile path', type: 'navigate',
          operands: { urlPath: hostilePath },
        }],
      }, 'hostile-navigate-data');
      const result = runBash(script, binDir, {
        ACTION_MARKER: markerPath,
        AGENT_BROWSER_LOG: logPath,
      });
      assert.equal(result.status, 1, result.stdout + result.stderr);
      assert.equal(fs.existsSync(markerPath), false, 'navigate shell data must not execute');
      assert.match(fs.readFileSync(logPath, 'utf8'), /\$\(touch/);
      assert.ok(result.stdout.includes('navigate to ' + hostilePath + ' failed'));
    });
  });

  test('eval click keeps a hostile CSS selector literal', function() {
    withFakeBrowser('#!/usr/bin/env bash\nprintf \'%s\\n\' "$*" >> "${AGENT_BROWSER_LOG:?}"\nfor _arg in "$@"; do [ "$_arg" = "eval" ] && printf \'%s\' "${!#}" > "${LAST_ARGUMENT_LOG:?}"; done\nexit 0\n', function(binDir) {
      const logPath = path.join(binDir, 'browser.log');
      const lastArgumentPath = path.join(binDir, 'last-argument.log');
      const markerPath = path.join(binDir, 'click-expanded');
      const hostileSelector = '[data-value="$(touch \\"$ACTION_MARKER\\")`touch "$ACTION_MARKER"`$ACTION_MARKER\'s"]';
      const script = generate({
        name: 'hostile-click-data',
        steps: [{
          id: 'click-hostile', action: 'Click hostile selector', type: 'click',
          operands: { selector: 'css=' + hostileSelector, cssSelector: hostileSelector },
        }],
      }, 'hostile-click-data');
      const result = runBash(script, binDir, {
        ACTION_MARKER: markerPath,
        AGENT_BROWSER_LOG: logPath,
        LAST_ARGUMENT_LOG: lastArgumentPath,
      });
      assert.equal(result.status, 0, result.stdout + result.stderr);
      assert.equal(fs.existsSync(markerPath), false, 'click selector shell data must not execute');
      assert.match(fs.readFileSync(logPath, 'utf8'), /\$\(touch/);
      assert.ok(fs.readFileSync(lastArgumentPath, 'utf8').includes(JSON.stringify(hostileSelector)));
    });
  });

  test('eval fill keeps hostile CSS selector and value literal', function() {
    withFakeBrowser('#!/usr/bin/env bash\nprintf \'%s\\n\' "$*" >> "${AGENT_BROWSER_LOG:?}"\nfor _arg in "$@"; do [ "$_arg" = "eval" ] && printf \'%s\' "${!#}" > "${LAST_ARGUMENT_LOG:?}"; done\nexit 0\n', function(binDir) {
      const logPath = path.join(binDir, 'browser.log');
      const lastArgumentPath = path.join(binDir, 'last-argument.log');
      const markerPath = path.join(binDir, 'fill-expanded');
      const hostileSelector = 'input[data-value="$(touch \\"$ACTION_MARKER\\")`touch "$ACTION_MARKER"`"]';
      const hostileValue = 'value\'"$(touch "$ACTION_MARKER")`touch "$ACTION_MARKER"`$ACTION_MARKER\\tail';
      const script = generate({
        name: 'hostile-fill-data',
        steps: [{
          id: 'fill-hostile', action: 'Fill hostile data', type: 'fill',
          operands: { selector: 'css=' + hostileSelector, cssSelector: hostileSelector, value: hostileValue },
        }],
      }, 'hostile-fill-data');
      const result = runBash(script, binDir, {
        ACTION_MARKER: markerPath,
        AGENT_BROWSER_LOG: logPath,
        LAST_ARGUMENT_LOG: lastArgumentPath,
      });
      assert.equal(result.status, 0, result.stdout + result.stderr);
      assert.equal(fs.existsSync(markerPath), false, 'fill shell data must not execute');
      const browserLog = fs.readFileSync(logPath, 'utf8');
      assert.match(browserLog, /\$\(touch/);
      const evalSource = fs.readFileSync(lastArgumentPath, 'utf8');
      assert.ok(evalSource.includes(JSON.stringify(hostileSelector)));
      assert.ok(evalSource.includes(JSON.stringify(hostileValue)));
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
  test('distinct unsafe step IDs produce distinct path-safe artifact names', function() {
    const first = artifactName('checkout/payment');
    const second = artifactName('checkout?payment');
    assert.notEqual(first, second);
    for (const name of [first, second]) {
      assert.doesNotMatch(name, /[\\/]/);
      assert.doesNotMatch(name, /^\.\.?$/);
    }
  });

  test('already-safe step IDs keep their readable artifact names', function() {
    assert.equal(artifactName('checkout-payment_2.0'), 'checkout-payment_2.0');
  });

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

  test('requested screenshots for distinct unsafe step IDs do not overwrite each other', function() {
    withFakeBrowser([
      '#!/usr/bin/env bash',
      'printf \'%s\\n\' "$*" >> "${AGENT_BROWSER_LOG:?}"',
      'exit 0',
    ].join('\n'), function(binDir) {
      const logPath = path.join(binDir, 'browser.log');
      const script = generate({
        name: 'distinct-requested-screenshots',
        steps: ['checkout/payment', 'checkout?payment'].map(function(id) {
          return {
            id,
            action: 'Wait 0',
            type: 'wait',
            operands: { seconds: 0 },
            screenshot: true,
          };
        }),
      }, 'distinct-requested-screenshots');
      const result = runBash(script, binDir, { AGENT_BROWSER_LOG: logPath });
      assert.equal(result.status, 0, result.stdout + result.stderr);
      const screenshotPaths = fs.readFileSync(logPath, 'utf8')
        .split('\n')
        .filter(line => line.includes('screenshot '))
        .map(line => line.slice(line.indexOf('screenshot ') + 'screenshot '.length));
      assert.equal(screenshotPaths.length, 2);
      assert.notEqual(screenshotPaths[0], screenshotPaths[1]);
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

describe('hatch-only compiled replay honesty', function() {
  test('hatch-only step records not_automated across footer, metrics, and JUnit', function() {
    const report = runHatchOnlyFlow();
    assert.equal(report.status, 0, report.stdout + report.stderr);

    const stepStart = report.generatedScript.indexOf('_record_step_name "manual-only"');
    const stepEnd = report.generatedScript.indexOf('_STEP_TIMES+=("0")', stepStart);
    const stepBlock = report.generatedScript.slice(stepStart, stepEnd);
    assert.ok(stepBlock.includes('_STEP_RESULTS+=("not_automated")'), stepBlock);
    assert.equal(stepBlock.includes('_STEP_RESULTS+=("pass")'), false, stepBlock);

    assert.ok(
      report.stdout.includes('PASS: hatchonly (0/1 automated steps passed, 0 skipped, 1 not automated)'),
      report.stdout
    );

    const metrics = JSON.parse(report.metricsJson);
    assert.equal(metrics.steps[0].id, 'manual-only');
    assert.equal(metrics.steps[0].result, 'not_automated');
    assert.equal(metrics.summary.passed, 0);
    assert.equal(metrics.summary.failed, 0);
    assert.equal(metrics.summary.skipped, 0);
    assert.equal(metrics.summary.not_automated, 1);

    const junit = report.junitXml;
    assert.match(junit, /<testsuite[^>]* tests="1" failures="0" skipped="1"/);
    assert.match(junit, /<testcase[^>]* name="manual-only"[^>]*><skipped message="not automated"\/><\/testcase>/);
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

describe('JUnit failure diagnostic safety', function() {
  test('JUnit XML round-trips failure messages with XML specials and control whitespace', XMLLINT_TEST_OPTIONS, function() {
    const hostile = 'quote " less < greater > amp & line\nreturn\rtab\t';
    withFakeBrowser(snapshotBrowserScript(), function(binDir) {
      const junitPath = path.join(binDir, 'junit.xml');
      const script = generate(makeTextFlow({
        type: 'text-visible',
        raw: 'hostile XML text visible',
        text: hostile,
      }), 'junit-failure-message');
      const result = runBash(script, binDir, {
        AGENT_BROWSER_LOG: path.join(binDir, 'browser.log'),
        SNAPSHOT_OUTPUT: '- document "safe"',
      }, ['--continue-on-error', '--junit', junitPath]);
      assert.equal(result.status, 1, result.stdout + result.stderr);
      const xpath = childProcess.spawnSync(
        XMLLINT_COMMAND,
        ['--xpath', 'string(/testsuites/testsuite/testcase/failure/@message)', junitPath],
        { encoding: 'utf8' }
      );
      assert.equal(xpath.status, 0, xpath.stdout + xpath.stderr);
      assert.equal(xpath.stdout.slice(0, -1), "text '" + hostile + "' not found on page");
    });
  });

  test('metrics and JUnit preserve a trailing LF in a probe-failure message', XMLLINT_TEST_OPTIONS, function() {
    const elementName = 'hostile-__E2E_PIPELINE_MSG_END_7f3a9c__-trailing-newline\n';
    const expectedFailure = 'agent-browser snapshot probe failed for ' + elementName;
    withFakeBrowser(snapshotBrowserScript(), function(binDir) {
      const metricsPath = path.join(binDir, 'metrics.json');
      const junitPath = path.join(binDir, 'junit.xml');
      const script = generate({
        name: 'trailing-newline-failure',
        steps: [{
          id: 'probe-failure',
          action: 'Wait 0',
          type: 'wait',
          operands: { seconds: 0 },
          expects: [{
            type: 'element-visible',
            elementName,
            selector: 'role=heading[name="Home"]',
          }],
        }],
      }, 'trailing-newline-failure');
      const result = runBash(script, binDir, {
        AGENT_BROWSER_LOG: path.join(binDir, 'browser.log'),
        SNAPSHOT_STATUS: '7',
      }, [
        '--continue-on-error',
        '--metrics-output', metricsPath,
        '--junit', junitPath,
      ]);
      assert.equal(result.status, 1, result.stdout + result.stderr);

      const metrics = JSON.parse(fs.readFileSync(metricsPath, 'utf8'));
      assert.equal(metrics.steps[0].failure_msg, expectedFailure);

      const xpath = childProcess.spawnSync(
        XMLLINT_COMMAND,
        ['--xpath', 'string(/testsuites/testsuite/testcase/failure/@message)', junitPath],
        { encoding: 'utf8' }
      );
      assert.equal(xpath.status, 0, xpath.stdout + xpath.stderr);
      assert.equal(xpath.stdout.slice(0, -1), expectedFailure);
    });
  });
});

describe('compile-time JUnit XML control-character policy', function() {
  test('flow and step attributes replace every XML-illegal C0 byte while preserving legal text', XMLLINT_TEST_OPTIONS, function() {
    const illegalCodes = [
      0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
      0x0b, 0x0c,
      0x0e, 0x0f, 0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17,
      0x18, 0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f,
    ];
    const illegalC0 = String.fromCharCode.apply(String, illegalCodes);
    const legalTail = '\tline\nreturn\r<&>" 中文';
    const flowName = 'flow-' + illegalC0 + legalTail;
    const stepId = 'step-' + illegalC0 + legalTail;
    const expectedControls = '\ufffd'.repeat(illegalCodes.length);
    const expectedFlow = 'flow-' + expectedControls + legalTail;
    const expectedStep = 'step-' + expectedControls + legalTail;

    withFakeBrowser('#!/usr/bin/env bash\nexit 0\n', function(binDir) {
      const junitPath = path.join(binDir, 'junit.xml');
      const script = generate({
        name: flowName,
        steps: [{ id: stepId, action: 'Wait 0', type: 'wait', operands: { seconds: 0 } }],
      }, flowName);
      const result = runBash(script, binDir, {}, ['--junit', junitPath]);
      assert.equal(result.status, 0, result.stdout + result.stderr);

      const flowXpath = childProcess.spawnSync(
        XMLLINT_COMMAND,
        ['--xpath', 'string(/testsuites/testsuite/@name)', junitPath],
        { encoding: 'utf8' }
      );
      assert.equal(flowXpath.status, 0, flowXpath.stdout + flowXpath.stderr);
      assert.equal(flowXpath.stdout.slice(0, -1), expectedFlow);

      const stepXpath = childProcess.spawnSync(
        XMLLINT_COMMAND,
        ['--xpath', 'string(/testsuites/testsuite/testcase/@name)', junitPath],
        { encoding: 'utf8' }
      );
      assert.equal(stepXpath.status, 0, stepXpath.stdout + stepXpath.stderr);
      assert.equal(stepXpath.stdout.slice(0, -1), expectedStep);
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

// A `producer | grep -q` pipeline under `set -o pipefail` reports a SUCCESSFUL
// match as a no-match: grep exits 0 the instant it can decide and closes the
// pipe, the still-writing producer dies on SIGPIPE/EPIPE, and pipefail
// publishes the producer's status. Both conditions are required — an early
// decidable match AND a producer still writing — so the fixtures below pair
// each defect payload with the controls that isolate them.
//
// Sized at 256KB of bulk-after-match on purpose. A fixture sized at the
// intuitive pipe-buffer figure is GREEN before the fix on some hosts and would
// prove nothing; measured locally the false negative starts between 48KB and
// 64KB of bulk-after, and the ideation sweep on a different producer shape put
// it near 96KB. 256KB clears every measured threshold.
const SIGPIPE_BULK_BYTES = 256 * 1024;
const SIGPIPE_NEEDLE = 'create_customer_button';

function a11yFillerLines(byteBudget) {
  const lines = [];
  let total = 0;
  let index = 0;
  while (total < byteBudget) {
    const line = '  - text "filler row ' + index + ' ' + 'x'.repeat(60) + '"';
    lines.push(line);
    total += line.length + 1;
    index += 1;
  }
  return lines;
}

// The first line must satisfy _capture_snapshot's validator, otherwise capture
// returns 2 and the poll returns 2 — a different failure wearing the same red.
const A11Y_HEAD = '- generic [ref=e1]:';

function sigpipeSnapshot(shape, needle) {
  const hit = '  - button "' + needle + '" [ref=e9]';
  const filler = a11yFillerLines(SIGPIPE_BULK_BYTES);
  if (shape === 'early') return [A11Y_HEAD, '  - toolbar "Tools"', hit].concat(filler).join('\n');
  if (shape === 'late') return [A11Y_HEAD, '  - toolbar "Tools"'].concat(filler).concat([hit]).join('\n');
  if (shape === 'single') return A11Y_HEAD + ' ' + needle + ' ' + 'y'.repeat(SIGPIPE_BULK_BYTES);
  if (shape === 'absent') return [A11Y_HEAD, '  - toolbar "Tools"'].concat(filler).join('\n');
  if (shape === 'small') return [A11Y_HEAD, hit].join('\n');
  if (shape === 'small-absent') return [A11Y_HEAD, '  - toolbar "Tools"'].join('\n');
  throw new Error('unknown snapshot shape: ' + shape);
}

// Delivers the snapshot through a file rather than an env var: a 256KB
// AGENT_BROWSER_OUTPUT risks ARG_MAX.
function fileSnapshotBrowserScript() {
  return [
    '#!/usr/bin/env bash',
    'printf \'%s\\n\' "$*" >> "${AGENT_BROWSER_LOG:?}"',
    'for _arg in "$@"; do',
    '  if [ "$_arg" = "snapshot" ]; then',
    '    cat "${AGENT_BROWSER_SNAPSHOT_FILE:?}"',
    '    exit 0',
    '  fi',
    'done',
    'exit 0',
  ].join('\n');
}

function withSnapshotFile(shape, needle, callback) {
  return withFakeBrowser(fileSnapshotBrowserScript(), function(binDir) {
    const snapshotPath = path.join(binDir, 'snapshot.txt');
    fs.writeFileSync(snapshotPath, sigpipeSnapshot(shape, needle), 'utf8');
    return callback(binDir, {
      AGENT_BROWSER_LOG: path.join(binDir, 'browser.log'),
      AGENT_BROWSER_SNAPSHOT_FILE: snapshotPath,
    });
  });
}

function runSnapshotPoll(shape, needle) {
  return withSnapshotFile(shape, needle, function(binDir, env) {
    return runBash([
      'set -euo pipefail',
      generateRuntimeSupport(),
      'set +e',
      '_poll_snapshot_contains ' + singleQuote(needle) + ' "sigpipe-step" 1 ""',
      'exit $?',
    ].join('\n'), binDir, env);
  });
}

function runLargeTextFlow(expectType, shape, needle) {
  return withSnapshotFile(shape, needle, function(binDir, env) {
    const expect = expectType === 'text-visible'
      ? { type: 'text-visible', raw: "text '" + needle + "' on page", text: needle }
      : { type: 'text-not-visible', raw: "text '" + needle + "' not on page", text: needle };
    const script = generate(makeTextFlow(expect), 'status-safe-large-snapshot');
    return runBash(script, binDir, env);
  });
}

describe('snapshot matching is status-safe on large pages (pipefail false negative)', function() {
  test('_poll_snapshot_contains reports a match found on an early line of a large snapshot', function() {
    const result = runSnapshotPoll('early', SIGPIPE_NEEDLE);
    assert.equal(result.status, 0,
      'pattern IS present on line 3; poll must report a match. ' + result.stdout + result.stderr);
  });

  test('CONTROL: a match on the last line of the same payload still reports a match', function() {
    // Green before the fix by construction: with the match at the end the
    // matcher must drain everything, so no early close is possible. Proves the
    // evidence fixture needs an EARLY match, not merely a large payload.
    assert.equal(runSnapshotPoll('late', SIGPIPE_NEEDLE).status, 0);
  });

  test('CONTROL: a single-line payload of the same size still reports a match', function() {
    // Green before the fix by construction: without a line terminator the
    // matcher cannot decide early. Proves the evidence fixture needs a line
    // structure, not merely bytes.
    assert.equal(runSnapshotPoll('single', SIGPIPE_NEEDLE).status, 0);
  });

  test('CONTROL: an absent pattern still reports no-match', function() {
    // Green before the fix by construction, and the guard against a fix that
    // returns 0 unconditionally.
    assert.equal(runSnapshotPoll('absent', SIGPIPE_NEEDLE).status, 1);
  });

  test('text-visible passes when the text is on an early line of a large snapshot', function() {
    const result = runLargeTextFlow('text-visible', 'early', SIGPIPE_NEEDLE);
    assert.equal(result.status, 0,
      'text IS on the page; the assertion must pass. ' + result.stdout + result.stderr);
  });

  test('text-not-visible fails when the forbidden text is on an early line of a large snapshot', function() {
    // The silent one: pre-fix this exits 0, so `403 must not appear` style
    // assertions degrade to unconditional passes as pages grow.
    const result = runLargeTextFlow('text-not-visible', 'early', SIGPIPE_NEEDLE);
    assert.equal(result.status, 1,
      'text IS on the page; the assertion must fail. ' + result.stdout + result.stderr);
    assert.match(result.stdout, /should NOT be on page but was found/);
  });

  test('CONTROL: text assertions keep their verdicts on a small snapshot', function() {
    // Green before the fix by construction — small snapshots never reproduce.
    assert.equal(runLargeTextFlow('text-visible', 'small', SIGPIPE_NEEDLE).status, 0);
    assert.equal(runLargeTextFlow('text-not-visible', 'small-absent', SIGPIPE_NEEDLE).status, 0);
    assert.equal(runLargeTextFlow('text-not-visible', 'small', SIGPIPE_NEEDLE).status, 1);
  });

  test('CONTROL: the pattern operand stays a fixed string, not a glob', function() {
    // Green before the fix by construction (grep -F is also literal), and the
    // guard against a fix that swaps fixed-string matching for glob matching.
    const decoyHaystack = ['- generic [ref=e1]:', '  - text "a-b-c"'].join('\n');
    const result = withFakeBrowser(fileSnapshotBrowserScript(), function(binDir) {
      const snapshotPath = path.join(binDir, 'snapshot.txt');
      fs.writeFileSync(snapshotPath, decoyHaystack, 'utf8');
      return runBash([
        'set -euo pipefail',
        generateRuntimeSupport(),
        'set +e',
        '_poll_snapshot_contains ' + singleQuote('a*c') + ' "glob-decoy" 1 ""',
        'exit $?',
      ].join('\n'), binDir, {
        AGENT_BROWSER_LOG: path.join(binDir, 'browser.log'),
        AGENT_BROWSER_SNAPSHOT_FILE: snapshotPath,
      });
    });
    assert.equal(result.status, 1,
      'a*c must not match a-b-c — the pattern is a literal, not a glob. ' + result.stdout + result.stderr);
  });

  test('no emitted matcher pipes a producer into grep', function() {
    // Class-level guard: the defect is the pipeline, not any one call site. A
    // reintroduced `producer | grep` is caught here even if it happens to sit
    // below today's payload threshold.
    const flow = {
      name: 'no-grep-pipelines',
      steps: [
        {
          id: 'capture-booking-id',
          type: 'capture-url-query',
          action: 'Capture bookingId from URL query',
          operands: { param: 'bookingId', as: 'booking_id', validate: 'uuid' },
        },
        {
          id: 'verify-text',
          action: 'Wait 0',
          type: 'wait',
          operands: { seconds: 0 },
          expects: [
            { type: 'text-visible', raw: "text 'Dashboard' on page", text: 'Dashboard' },
            { type: 'text-not-visible', raw: "text 'Error' not on page", text: 'Error' },
          ],
        },
      ],
    };
    const emitted = generateRuntimeSupport() + '\n' + generate(flow, 'no-grep-pipelines');
    const offenders = emitted.split('\n').filter(function(line) {
      return /\|\s*grep\b/.test(line);
    });
    assert.deepEqual(offenders, [],
      'emitted script must not pipe into grep:\n' + offenders.join('\n'));
  });
});
