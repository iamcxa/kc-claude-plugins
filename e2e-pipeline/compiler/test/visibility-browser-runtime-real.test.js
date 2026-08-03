'use strict';

const { test } = require('node:test');
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const { spawn } = require('node:child_process');
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
  return new Promise(function(resolve, reject) {
    const spawnOptions = Object.assign({}, options);
    const input = spawnOptions.input;
    delete spawnOptions.input;
    const child = spawn(command, args, Object.assign({}, spawnOptions, {
      stdio: ['pipe', 'pipe', 'pipe'],
    }));
    let stdout = '';
    let stderr = '';
    const timer = setTimeout(function() {
      child.kill('SIGTERM');
      reject(new Error('real visibility runtime probe timed out'));
    }, 60000);
    child.stdout.on('data', function(chunk) { stdout += chunk; });
    child.stderr.on('data', function(chunk) { stderr += chunk; });
    child.on('error', function(error) {
      clearTimeout(timer);
      reject(error);
    });
    child.on('close', function(status) {
      clearTimeout(timer);
      resolve({ status: status, stderr: stderr, stdout: stdout });
    });
    child.stdin.end(input);
  });
}

function runRuntime(baseArgs, command, environment) {
  return run(process.execPath, [RUNTIME, ...baseArgs, ...command], { env: environment });
}

async function judgeOwnedSelector(baseArgs, selector, policy, assertion, environment) {
  const expression = await run(process.execPath, [CLI, 'expression', '--selector', selector]);
  assert.equal(expression.status, 0, expression.stderr);
  const evaluated = await runRuntime(baseArgs, ['eval', expression.stdout.trim(), '--json'], environment);
  const judged = await run(process.execPath, [
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

function generatedScript(options) {
  const assertion = options.assertion;
  const expectationType = assertion === 'not-visible'
    ? 'element-not-visible'
    : assertion === 'enabled'
      ? 'element-enabled'
      : assertion === 'disabled'
        ? 'element-disabled'
        : 'element-visible';
  return generate({
    name: 'real-visibility',
    variables: { base_url: options.baseUrl },
    browserApps: { default: options.app },
    steps: [
      {
        id: 'navigate-visibility',
        action: 'Navigate to /visibility',
        type: 'navigate',
        operands: { target: '/visibility', urlPath: '/visibility' },
        expects: [],
      },
      {
        id: 'real-visibility',
        action: 'Wait 0',
        type: 'wait',
        operands: { seconds: 0 },
        expects: [{
          type: expectationType,
          raw: 'target ' + assertion,
          elementName: 'target',
          selector: options.selector,
          cssSelector: options.selector,
          visibilityPolicy: options.policy,
        }],
      },
    ],
  }, 'real-visibility');
}

test('generated real-browser fixture binds its app and navigates before visibility', function() {
  const script = generatedScript({
    app: 'vis-contract',
    assertion: 'visible',
    baseUrl: 'http://127.0.0.1:3000',
    policy: 'retained-zero-rect',
    selector: '.ghost',
  });
  const navigation = 'agent-browser open "${BASE_URL}"\'/visibility\'';
  const visibility = "_poll_visibility '.ghost' 'retained-zero-rect' visible";

  assert.match(script, /local _browser_app='vis-contract'/);
  assert.match(script, /BASE_URL="\$\{1:-\$\{E2E_BASE_URL:-http:\/\/127\.0\.0\.1:3000\}\}"/);
  assert.ok(script.indexOf(navigation) !== -1, script);
  assert.ok(script.indexOf(visibility) !== -1, script);
  assert.ok(script.indexOf(navigation) < script.indexOf(visibility), script);
});

test('owned real browser proves the visibility matrix for CLI and generated scripts', { skip: !RUN_REAL }, async function(t) {
  const browserHome = process.env.E2E_AGENT_BROWSER_HOME || path.join(os.homedir(), '.agent-browser');
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'visibility-real-'));
  const bindings = [];

  function createBinding(label, appLabel) {
    const identity = crypto.randomBytes(5).toString('hex');
    const app = (appLabel || ('vis-' + label)) + '-' + identity.slice(0, 6);
    const runId = 'visibility-' + label + '-' + identity;
    const profile = path.join(browserHome, app);
    const caseRoot = path.join(root, label + '-' + identity);
    const receiptDir = path.join(caseRoot, 'receipts');
    const binding = {
      app: app,
      artifactRoot: path.join(caseRoot, 'artifacts'),
      baseArgs: [
        '--run-id', runId,
        '--app', app,
        '--profile', profile,
        '--receipt', path.join(receiptDir, app + '.json'),
      ],
      metrics: path.join(caseRoot, 'metrics.json'),
      profile: profile,
      receipt: path.join(receiptDir, app + '.json'),
      receiptDir: receiptDir,
      runId: runId,
    };
    fs.mkdirSync(profile, { recursive: true, mode: 0o700 });
    fs.mkdirSync(caseRoot, { recursive: true, mode: 0o700 });
    bindings.push(binding);
    return binding;
  }

  async function closeIfActive(binding, environment) {
    if (!fs.existsSync(binding.receipt)) return;
    const ownership = JSON.parse(fs.readFileSync(binding.receipt, 'utf8'));
    if (ownership.status !== 'active') return;
    const closed = await runRuntime(binding.baseArgs, ['close'], environment);
    assert.equal(closed.status, 0, closed.stderr);
  }

  function assertClosedOwnership(binding) {
    const ownership = JSON.parse(fs.readFileSync(binding.receipt, 'utf8'));
    assert.equal(ownership.run_id, binding.runId);
    assert.equal(ownership.app, binding.app);
    assert.equal(ownership.session, binding.app);
    assert.equal(ownership.profile, path.resolve(binding.profile));
    assert.equal(ownership.initial_reused, false);
    assert.equal(ownership.first_navigation.status, 'verified');
    assert.equal(ownership.status, 'closed');
    assert.equal(ownership.cleanup, 'owned-session-closed');
  }

  const directBinding = createBinding('cli');

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
      '<button class="enabled-candidate" disabled style="position:absolute;width:0;height:0;padding:0;border:0;overflow:hidden">disabled ghost</button>',
      '<button class="enabled-candidate">enabled rendered candidate</button>',
      '<button class="delayed-enabled" disabled style="position:absolute;width:0;height:0;padding:0;border:0;overflow:hidden">disabled ghost</button>',
      '<button id="delayed-enabled-target" class="delayed-enabled" disabled>enables later</button>',
      '<button class="delayed-disabled" disabled style="position:absolute;width:0;height:0;padding:0;border:0;overflow:hidden">disabled ghost</button>',
      '<button id="delayed-disabled-target" class="delayed-disabled">disables later</button>',
      '<script>',
      'setTimeout(function () { document.querySelector("#delayed-enabled-target").disabled = false; }, 1500);',
      'setTimeout(function () { document.querySelector("#delayed-disabled-target").disabled = true; }, 1500);',
      '</script>',
      '</body></html>',
    ].join(''));
  });
  await new Promise(function(resolve) { server.listen(0, '127.0.0.1', resolve); });
  const baseUrl = 'http://127.0.0.1:' + server.address().port;
  const url = baseUrl + '/visibility';
  const environment = Object.assign({}, process.env, {
    E2E_AGENT_BROWSER_BIN: process.env.E2E_AGENT_BROWSER_BIN || 'agent-browser',
    E2E_AGENT_BROWSER_HOME: browserHome,
  });

  t.after(async function() {
    for (const binding of bindings) {
      await closeIfActive(binding, environment);
    }
    await new Promise(function(resolve) { server.close(resolve); });
    for (const binding of bindings) {
      fs.rmSync(binding.profile, { recursive: true, force: true });
    }
    fs.rmSync(root, { recursive: true, force: true });
  });

  const opened = await runRuntime(directBinding.baseArgs, ['open', url], environment);
  assert.equal(opened.status, 0, opened.stderr);
  const ownership = JSON.parse(fs.readFileSync(directBinding.receipt, 'utf8'));
  assert.equal(ownership.status, 'active');
  assert.equal(ownership.run_id, directBinding.runId);
  assert.equal(ownership.session, directBinding.app);
  assert.equal(ownership.profile, path.resolve(directBinding.profile));
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
    const actual = await judgeOwnedSelector(directBinding.baseArgs, selector, policy, assertion, environment);
    assert.equal(actual.judged.status, expectedExit, selector + ': ' + actual.judged.stderr);
    assert.equal(actual.value.result, expectedResult, selector);
  }

  const directClosed = await runRuntime(directBinding.baseArgs, ['close'], environment);
  assert.equal(directClosed.status, 0, directClosed.stderr);
  assertClosedOwnership(directBinding);

  for (const [label, appLabel, selector, policy, assertion, expectedStatus, expectedResult, expectedCount, expectedJudgment] of [
    ['generated-ghost', 'vg', '.ghost', 'retained-zero-rect', 'visible', 0, 'unique_rendered_with_retained_zero_rect', 2, 'satisfied'],
    ['generated-invalid', 'vi', '[', 'strict', 'not-visible', 1, 'invalid_selector', null, 'terminal'],
    ['generated-enabled-candidate', 'vec', '.enabled-candidate', 'retained-zero-rect', 'enabled', 0, 'unique_rendered_with_retained_zero_rect', 2, 'satisfied'],
    ['generated-delayed-enabled', 'vde', '.delayed-enabled', 'retained-zero-rect', 'enabled', 0, 'unique_rendered_with_retained_zero_rect', 2, 'satisfied'],
    ['generated-delayed-disabled', 'vdd', '.delayed-disabled', 'retained-zero-rect', 'disabled', 0, 'unique_rendered_with_retained_zero_rect', 2, 'satisfied'],
  ]) {
    const binding = createBinding(label, appLabel);
    assert.equal(fs.existsSync(binding.receipt), false);
    const generated = await run('/bin/bash', [
      '-c',
      generatedScript({
        app: binding.app,
        assertion: assertion,
        baseUrl: baseUrl,
        policy: policy,
        selector: selector,
      }),
      '--',
      '--continue-on-error',
      '--metrics-output',
      binding.metrics,
    ], {
      env: Object.assign({}, environment, {
        E2E_BROWSER_RECEIPT_DIR: binding.receiptDir,
        E2E_BROWSER_RUNTIME: RUNTIME,
        E2E_BROWSER_RUN_ID: binding.runId,
        E2E_SCREENSHOT_DIR: binding.artifactRoot,
        WAIT_TIMEOUT: '4',
      }),
    });
    assert.equal(generated.status, expectedStatus, selector + ': ' + generated.stdout + generated.stderr);
    assertClosedOwnership(binding);
    const report = JSON.parse(fs.readFileSync(binding.metrics, 'utf8'));
    assert.equal(report.visibility_results.length, 1);
    assert.equal(report.visibility_results[0].result_class, expectedResult);
    assert.equal(report.visibility_results[0].effective_selector, selector);
    assert.equal(report.visibility_results[0].visibility_policy, policy);
    assert.equal(report.visibility_results[0].assertion, assertion);
    assert.equal(report.visibility_results[0].judgment, expectedJudgment);
    assert.equal(report.visibility_results[0].match_count, expectedCount);
    if (assertion === 'enabled' || assertion === 'disabled') {
      assert.equal(report.visibility_results[0].rendered_candidate.index, 1);
      assert.equal(report.visibility_results[0].rendered_candidate.enabled, assertion === 'enabled');
      if (label.startsWith('generated-delayed-')) {
        assert.ok(report.visibility_results[0].attempts >= 2, label);
      }
    }
  }
});
