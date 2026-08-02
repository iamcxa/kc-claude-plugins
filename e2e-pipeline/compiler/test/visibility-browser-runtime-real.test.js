'use strict';

const { test } = require('node:test');
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const childProcess = require('node:child_process');
const fs = require('node:fs');
const http = require('node:http');
const os = require('node:os');
const path = require('node:path');

const { generate } = require('../codegen.js');

const PIPELINE = path.join(__dirname, '..', '..');
const RUNTIME = path.join(PIPELINE, 'bin', 'e2e-browser-runtime.js');
const CLI = path.join(PIPELINE, 'bin', 'e2e-visibility-probe.js');
const RUN_REAL = process.env.E2E_REAL_VISIBILITY === '1';

function run(command, args, options) {
  return childProcess.spawnSync(command, args, Object.assign({ encoding: 'utf8' }, options));
}

function runRuntime(baseArgs, command, environment) {
  return run(process.execPath, [RUNTIME, ...baseArgs, ...command], { env: environment });
}

function judgeOwnedSelector(baseArgs, selector, policy, assertion, environment) {
  const expression = run(process.execPath, [CLI, 'expression', '--selector', selector]);
  assert.equal(expression.status, 0, expression.stderr);
  const evaluated = runRuntime(baseArgs, ['eval', expression.stdout.trim(), '--json'], environment);
  const judged = run(process.execPath, [
    CLI,
    'judge',
    '--policy',
    policy,
    '--assert',
    assertion,
    '--transport-exit',
    String(evaluated.status),
  ], { input: evaluated.stdout });
  return { evaluated: evaluated, judged: judged, value: JSON.parse(judged.stdout) };
}

function generatedScript(selector, policy) {
  return generate({
    name: 'real-visibility',
    steps: [{
      id: 'real-visibility',
      action: 'Wait 0',
      type: 'wait',
      operands: { seconds: 0 },
      expects: [{
        type: 'element-visible',
        raw: 'target visible',
        elementName: 'target',
        selector: selector,
        cssSelector: selector,
        visibilityPolicy: policy,
      }],
    }],
  }, 'real-visibility');
}

test('owned real browser proves the visibility matrix for CLI and generated scripts', { skip: !RUN_REAL }, async function(t) {
  const suffix = crypto.randomBytes(5).toString('hex');
  const app = 'vis-' + suffix.slice(0, 6);
  const runId = 'visibility-' + suffix;
  const browserHome = process.env.E2E_AGENT_BROWSER_HOME || path.join(os.homedir(), '.agent-browser');
  const profile = path.join(browserHome, app);
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'visibility-real-'));
  const receiptDir = path.join(root, 'receipts');
  const receipt = path.join(receiptDir, app + '.json');
  fs.mkdirSync(profile, { recursive: true, mode: 0o700 });
  fs.mkdirSync(receiptDir, { recursive: true });

  const server = http.createServer(function(_request, response) {
    response.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
    response.end([
      '<!doctype html><html><body>',
      '<div class="all-non" style="display:none">display none</div>',
      '<div class="all-non" style="position:absolute;width:0;height:0;overflow:hidden">zero rect</div>',
      '<div class="singleton">singleton</div>',
      '<div class="ghost" style="position:absolute;width:0;height:0;overflow:hidden">ghost</div>',
      '<div class="ghost">rendered after ghost</div>',
      '<div class="hidden-extra" style="visibility:hidden">hidden style</div>',
      '<div class="hidden-extra">rendered after hidden</div>',
      '<div class="multi">rendered one</div><div class="multi">rendered two</div>',
      '</body></html>',
    ].join(''));
  });
  await new Promise(function(resolve) { server.listen(0, '127.0.0.1', resolve); });
  const url = 'http://127.0.0.1:' + server.address().port + '/visibility';
  const environment = Object.assign({}, process.env, {
    E2E_AGENT_BROWSER_BIN: process.env.E2E_AGENT_BROWSER_BIN || 'agent-browser',
    E2E_AGENT_BROWSER_HOME: browserHome,
  });
  const baseArgs = [
    '--run-id', runId,
    '--app', app,
    '--profile', profile,
    '--receipt', receipt,
  ];

  t.after(async function() {
    runRuntime(baseArgs, ['close'], environment);
    await new Promise(function(resolve) { server.close(resolve); });
    fs.rmSync(profile, { recursive: true, force: true });
    fs.rmSync(root, { recursive: true, force: true });
  });

  const opened = runRuntime(baseArgs, ['open', url], environment);
  assert.equal(opened.status, 0, opened.stderr);
  const ownership = JSON.parse(fs.readFileSync(receipt, 'utf8'));
  assert.equal(ownership.status, 'active');
  assert.equal(ownership.run_id, runId);
  assert.equal(ownership.session, app);
  assert.equal(ownership.profile, path.resolve(profile));
  assert.equal(ownership.first_navigation.status, 'verified');
  assert.match(ownership.executable, /chrome/i);
  assert.ok(ownership.daemon_pid > 0);
  assert.ok(ownership.browser_pid > 0);
  assert.match(ownership.profile_mode, /persistent-path|verified-snapshot/);

  const cases = [
    ['.no-match', 'strict', 'visible', 'no_match', 1],
    ['.all-non', 'strict', 'visible', 'all_non_rendered', 1],
    ['.singleton', 'strict', 'visible', 'unique_rendered', 0],
    ['.ghost', 'strict', 'visible', 'raw_multi_match', 2],
    ['.ghost', 'retained-zero-rect', 'visible', 'unique_rendered_with_retained_zero_rect', 0],
    ['.hidden-extra', 'retained-zero-rect', 'visible', 'raw_multi_match', 2],
    ['.multi', 'strict', 'visible', 'multiple_rendered', 2],
    ['[', 'strict', 'not-visible', 'invalid_selector', 2],
  ];
  for (const [selector, policy, assertion, expectedResult, expectedExit] of cases) {
    const actual = judgeOwnedSelector(baseArgs, selector, policy, assertion, environment);
    assert.equal(actual.judged.status, expectedExit, selector + ': ' + actual.judged.stderr);
    assert.equal(actual.value.result, expectedResult, selector);
  }

  for (const [selector, policy, expectedStatus] of [
    ['.ghost', 'retained-zero-rect', 0],
    ['[', 'strict', 1],
  ]) {
    const generated = run('/bin/bash', ['-c', generatedScript(selector, policy)], {
      env: Object.assign({}, environment, {
        E2E_BROWSER_RUNTIME: RUNTIME,
        E2E_BROWSER_RUN_ID: runId,
        E2E_BROWSER_RECEIPT_DIR: receiptDir,
        WAIT_TIMEOUT: '1',
      }),
    });
    assert.equal(generated.status, expectedStatus, selector + ': ' + generated.stdout + generated.stderr);
    if (selector === '.ghost') {
      const reopened = runRuntime(baseArgs, ['open', url], environment);
      assert.equal(reopened.status, 0, reopened.stderr);
    }
  }
});
