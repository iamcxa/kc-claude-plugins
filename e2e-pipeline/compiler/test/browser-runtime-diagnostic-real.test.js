'use strict';

const { test } = require('node:test');
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const fs = require('node:fs');
const http = require('node:http');
const os = require('node:os');
const path = require('node:path');
const { spawn } = require('node:child_process');

const RUNTIME = path.join(__dirname, '..', '..', 'bin', 'e2e-browser-runtime.js');
const RUN_REAL = process.env.E2E_REAL_AGENT_BROWSER_032 === '1';

function runRuntime(args, environment) {
  return new Promise(function(resolve, reject) {
    const child = spawn(process.execPath, [RUNTIME, ...args], {
      env: environment,
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    let stdout = '';
    let stderr = '';
    const timer = setTimeout(function() {
      child.kill('SIGTERM');
      reject(new Error('real diagnostic runtime probe timed out'));
    }, 60000);
    child.stdout.on('data', function(chunk) {
      stdout += chunk;
    });
    child.stderr.on('data', function(chunk) {
      stderr += chunk;
    });
    child.on('error', function(error) {
      clearTimeout(timer);
      reject(error);
    });
    child.on('close', function(status) {
      clearTimeout(timer);
      resolve({ status, stderr, stdout });
    });
  });
}

test(
  'real agent-browser 0.32 recorder runs before the first document application code',
  { skip: !RUN_REAL },
  async function(t) {
    const browserHome =
      process.env.E2E_AGENT_BROWSER_HOME ||
      path.join(os.homedir(), '.agent-browser');
    const suffix = crypto.randomBytes(5).toString('hex');
    const app = 'dp-' + suffix.slice(0, 6);
    const runId = 'diagnostic-probe-' + suffix;
    const profile = path.join(browserHome, app);
    const root = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-diagnostic-real-'));
    const receipt = path.join(root, 'browser-ownership.json');
    const recorder = path.join(root, 'pre-navigation-recorder.js');
    const environment = Object.assign({}, process.env, {
      E2E_AGENT_BROWSER_BIN:
        process.env.E2E_AGENT_BROWSER_BIN || 'agent-browser',
      E2E_AGENT_BROWSER_HOME: browserHome,
    });

    fs.mkdirSync(profile, { mode: 0o700 });
    for (let index = 0; index < 3; index += 1) {
      fs.writeFileSync(
        path.join(profile, 'diagnostic-lineage-' + index + '.txt'),
        Buffer.alloc(512, 65 + index),
        { mode: 0o600 }
      );
    }
    fs.writeFileSync(
      recorder,
      [
        "globalThis.__E2E_PRENAV_VALUE__ = 'ready-before-document';",
        'publishDiagnosticProjection(',
        "  {app_saw_pre_navigation:{type:'boolean'}},",
        '  () => ({app_saw_pre_navigation: globalThis.__APP_SAW_PRENAV__ === true})',
        ');',
        '',
      ].join('\n'),
      { mode: 0o600 }
    );

    const server = http.createServer(function(_request, response) {
      response.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      response.end(
        [
          '<!doctype html>',
          '<html><body>',
          '<script>',
          'globalThis.__APP_SAW_PRENAV__ =',
          "  globalThis.__E2E_PRENAV_VALUE__ === 'ready-before-document';",
          '</script>',
          '<p>local diagnostic probe</p>',
          '</body></html>',
        ].join('\n')
      );
    });
    await new Promise(function(resolve) {
      server.listen(0, '127.0.0.1', resolve);
    });
    const address = server.address();
    const url = 'http://127.0.0.1:' + address.port + '/probe';

    t.after(async function() {
      await new Promise(function(resolve) {
        server.close(resolve);
      });
      fs.rmSync(profile, { recursive: true, force: true });
      fs.rmSync(root, { recursive: true, force: true });
    });

    const baseArgs = [
      '--run-id',
      runId,
      '--app',
      app,
      '--profile',
      profile,
      '--receipt',
      receipt,
      '--diagnostic-init-script',
      recorder,
    ];
    const opened = await runRuntime([...baseArgs, 'open', url], environment);
    assert.equal(opened.status, 0, opened.stderr);

    const projection = await runRuntime(
      [...baseArgs, 'diagnostic-projection'],
      environment
    );
    assert.equal(projection.status, 0, projection.stderr);
    assert.deepEqual(JSON.parse(projection.stdout), {
      projections: [
        {
          index: 0,
          basename: path.basename(recorder),
          values: { app_saw_pre_navigation: true },
        },
      ],
    });

    const lifecycle = JSON.parse(fs.readFileSync(receipt, 'utf8'));
    assert.equal(lifecycle.first_navigation.status, 'verified');
    assert.equal(lifecycle.diagnostic_init_scripts[0].status, 'observed');
    assert.equal(
      lifecycle.diagnostic_init_scripts[0].projection_status,
      'validated'
    );
    assert.equal(JSON.stringify(lifecycle).includes('ready-before-document'), false);

    const closed = await runRuntime([...baseArgs, 'close'], environment);
    assert.equal(closed.status, 0, closed.stderr);
  }
);

test(
  'real agent-browser 0.32 accepts caller-declared profile liveness only after true is observed',
  { skip: !RUN_REAL },
  async function(t) {
    const browserHome =
      process.env.E2E_AGENT_BROWSER_HOME ||
      path.join(os.homedir(), '.agent-browser');
    const suffix = crypto.randomBytes(5).toString('hex');
    const app = 'profile-live-' + suffix.slice(0, 6);
    const runId = 'profile-live-' + suffix;
    const profile = path.join(browserHome, app);
    const root = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-profile-liveness-real-'));
    const receipt = path.join(root, 'browser-ownership.json');
    const recorder = path.join(root, 'profile-liveness-recorder.js');
    const environment = Object.assign({}, process.env, {
      E2E_AGENT_BROWSER_BIN:
        process.env.E2E_AGENT_BROWSER_BIN || 'agent-browser',
      E2E_AGENT_BROWSER_HOME: browserHome,
    });

    fs.mkdirSync(profile, { recursive: true, mode: 0o700 });
    fs.writeFileSync(
      recorder,
      [
        'publishDiagnosticProjection(',
        "  {profile_live:{type:'boolean'}},",
        '  () => ({profile_live:true})',
        ');',
        '',
      ].join('\n'),
      { mode: 0o600 }
    );

    const server = http.createServer(function(_request, response) {
      response.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      response.end('<!doctype html><p>local profile liveness probe</p>');
    });
    await new Promise(function(resolve) {
      server.listen(0, '127.0.0.1', resolve);
    });
    const address = server.address();
    const url = 'http://127.0.0.1:' + address.port + '/profile-live';

    t.after(async function() {
      await new Promise(function(resolve) {
        server.close(resolve);
      });
      fs.rmSync(profile, { recursive: true, force: true });
      fs.rmSync(root, { recursive: true, force: true });
    });

    const baseArgs = [
      '--run-id', runId,
      '--app', app,
      '--profile', profile,
      '--receipt', receipt,
      '--diagnostic-init-script', recorder,
      '--profile-liveness-projection', '0:profile_live',
    ];
    const opened = await runRuntime([...baseArgs, 'open', url], environment);
    assert.equal(opened.status, 0, opened.stderr);

    const active = JSON.parse(fs.readFileSync(receipt, 'utf8'));
    assert.equal(active.first_navigation.status, 'verified');
    assert.equal(active.first_navigation.profile_state.status, 'observed');
    assert.deepEqual(active.first_navigation.profile_state.declarations, [
      { script_index: 0, field: 'profile_live' },
    ]);

    const closed = await runRuntime([...baseArgs, 'close'], environment);
    assert.equal(closed.status, 0, closed.stderr);
    const lifecycle = JSON.parse(fs.readFileSync(receipt, 'utf8'));
    assert.equal(lifecycle.status, 'closed');
  }
);

test(
  'real agent-browser 0.32 fails closed after bounded polling of an inert liveness projection',
  { skip: !RUN_REAL },
  async function(t) {
    const browserHome =
      process.env.E2E_AGENT_BROWSER_HOME ||
      path.join(os.homedir(), '.agent-browser');
    const suffix = crypto.randomBytes(5).toString('hex');
    const app = 'profile-inert-' + suffix.slice(0, 6);
    const runId = 'profile-inert-' + suffix;
    const profile = path.join(browserHome, app);
    const root = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-profile-liveness-real-'));
    const receipt = path.join(root, 'browser-ownership.json');
    const recorder = path.join(root, 'inert-profile-recorder.js');
    const environment = Object.assign({}, process.env, {
      E2E_AGENT_BROWSER_BIN:
        process.env.E2E_AGENT_BROWSER_BIN || 'agent-browser',
      E2E_AGENT_BROWSER_HOME: browserHome,
    });

    fs.mkdirSync(profile, { recursive: true, mode: 0o700 });
    fs.writeFileSync(
      recorder,
      [
        'publishDiagnosticProjection(',
        "  {profile_live:{type:'boolean'}},",
        '  () => ({profile_live:false})',
        ');',
        '',
      ].join('\n'),
      { mode: 0o600 }
    );

    const server = http.createServer(function(_request, response) {
      response.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      response.end('<!doctype html><p>local inert profile liveness probe</p>');
    });
    await new Promise(function(resolve) {
      server.listen(0, '127.0.0.1', resolve);
    });
    const address = server.address();
    const url = 'http://127.0.0.1:' + address.port + '/profile-inert';

    const baseArgs = [
      '--run-id', runId,
      '--app', app,
      '--profile', profile,
      '--receipt', receipt,
      '--diagnostic-init-script', recorder,
      '--profile-liveness-projection', '0:profile_live',
    ];

    t.after(async function() {
      await new Promise(function(resolve) {
        server.close(resolve);
      });
      await runRuntime([...baseArgs, 'close'], environment);
      fs.rmSync(profile, { recursive: true, force: true });
      fs.rmSync(root, { recursive: true, force: true });
    });
    const opened = await runRuntime([...baseArgs, 'open', url], environment);
    assert.notEqual(opened.status, 0);
    assert.match(opened.stderr, /declared profile liveness/i);

    const failed = JSON.parse(fs.readFileSync(receipt, 'utf8'));
    assert.equal(failed.first_navigation.status, 'failed');
    assert.equal(failed.first_navigation.post.profile_state.status, 'not-observed');
    assert.ok(failed.first_navigation.post.profile_state.attempts > 1);
    assert.ok(failed.first_navigation.post.profile_state.waited_ms_budget > 0);
    assert.equal(failed.status, 'failed');
  }
);
