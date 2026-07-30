'use strict';

const { test } = require('node:test');
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');

const PIPELINE = path.join(__dirname, '..', '..');
const RUNTIME = path.join(PIPELINE, 'bin', 'e2e-browser-runtime.js');
const FIXTURE = path.join(
  __dirname,
  'fixtures',
  'agent-browser-032-fixture.js'
);
const runtimeModule = require(RUNTIME);

function makeExecutable(filePath, source) {
  fs.writeFileSync(filePath, source, { mode: 0o755 });
}

function setup(t, options) {
  const settings = Object.assign(
    {
      copyLineage: true,
      profileMode: 'persistent',
      resetOnNavigation: '',
    },
    options || {}
  );
  const root = fs.mkdtempSync(
    path.join(os.tmpdir(), 'e2e-browser-lifecycle-')
  );
  t.after(function() {
    fs.rmSync(root, { recursive: true, force: true });
  });
  const browserHome = path.join(
    os.tmpdir(),
    'e2e-browser-lifecycle-home-' + path.basename(root)
  );
  fs.mkdirSync(browserHome);
  t.after(function() {
    fs.rmSync(browserHome, { recursive: true, force: true });
  });
  const executable = path.join(
    browserHome,
    'browsers',
    'chrome-151.0.7922.47',
    'chrome-mac-arm64',
    'Google Chrome for Testing.app',
    'Contents',
    'MacOS',
    'Google Chrome for Testing'
  );
  fs.mkdirSync(path.dirname(executable), { recursive: true });
  makeExecutable(executable, '#!/usr/bin/env bash\nexit 0\n');
  const agentBrowser = path.join(root, 'agent-browser');
  const ps = path.join(root, 'ps');
  const fixtureSource = fs.readFileSync(FIXTURE, 'utf8');
  makeExecutable(agentBrowser, fixtureSource);
  makeExecutable(ps, fixtureSource);
  const runId = 'issue107-' + path.basename(root).toLowerCase();
  const app = 'storefront';
  const profile = path.join(browserHome, app);
  const receipt = path.join(root, 'browser-ownership.json');
  const namespace = runtimeModule.namespaceForRun(
    runId,
    runtimeModule.socketHomeForBrowserHome(browserHome)
  );
  const socketDir = path.join(
    runtimeModule.socketHomeForBrowserHome(browserHome),
    'namespaces',
    namespace,
    'run'
  );
  const statePath = path.join(root, 'agent-browser-state.json');
  const snapshotHex = crypto
    .createHash('sha256')
    .update(root)
    .digest('hex')
    .slice(0, 32);
  const snapshotId = [
    snapshotHex.slice(0, 8),
    snapshotHex.slice(8, 12),
    snapshotHex.slice(12, 16),
    snapshotHex.slice(16, 20),
    snapshotHex.slice(20),
  ].join('-');
  fs.writeFileSync(
    statePath,
    JSON.stringify(
      {
        active: false,
        actualProfile: '',
        browserPid: 654,
        copyLineage: settings.copyLineage,
        daemonPid: 321,
        events: [],
        executable,
        harActive: false,
        initRegistered: false,
        launchHash: 12345,
        profileMode: settings.profileMode,
        requests: [],
        resetOnNavigation: settings.resetOnNavigation,
        reused: false,
        snapshotId,
        socketDir,
        tabId: 't1',
        url: 'about:blank',
      },
      null,
      2
    ) + '\n'
  );
  t.after(function() {
    if (!fs.existsSync(statePath)) return;
    const finalState = JSON.parse(fs.readFileSync(statePath, 'utf8'));
    const actualProfile = finalState.actualProfile || '';
    if (
      path.dirname(actualProfile) === path.resolve(os.tmpdir()) &&
      /^agent-browser-chrome-[a-f0-9-]+$/i.test(path.basename(actualProfile))
    ) {
      fs.rmSync(actualProfile, { recursive: true, force: true });
    }
  });
  return {
    agentBrowser,
    app,
    browserHome,
    env: Object.assign({}, process.env, {
      E2E_AGENT_BROWSER_032_STATE: statePath,
      E2E_AGENT_BROWSER_BIN: agentBrowser,
      E2E_AGENT_BROWSER_HOME: browserHome,
      E2E_PS_BIN: ps,
      E2E_RUNTIME_TEST_MODE: '1',
    }),
    executable,
    profile,
    receipt,
    root,
    runId,
    statePath,
  };
}

function runOpen(fixture, url) {
  return spawnSync(
    process.execPath,
    [
      RUNTIME,
      '--run-id',
      fixture.runId,
      '--app',
      fixture.app,
      '--executable-path',
      fixture.executable,
      '--profile',
      fixture.profile,
      '--receipt',
      fixture.receipt,
      'open',
      url,
    ],
    { encoding: 'utf8', env: fixture.env }
  );
}

test('unbound 0.32 snapshot fails before the application URL is requested', function(t) {
  const fixture = setup(t, {
    copyLineage: false,
    profileMode: 'snapshot',
  });
  const targetUrl = 'https://application.example.test/first';

  const result = runOpen(fixture, targetUrl);
  const state = JSON.parse(fs.readFileSync(fixture.statePath, 'utf8'));
  const openedUrls = state.events
    .filter(function(event) {
      return event.command === 'open';
    })
    .flatMap(function(event) {
      return event.args;
    });

  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /profile|user-data-dir|persistent/i);
  assert.equal(openedUrls.includes(targetUrl), false);
});

test('0.32 snapshot is bound to its canonical source without reading profile secrets', function(t) {
  const fixture = setup(t, { profileMode: 'snapshot' });
  const targetUrl = 'https://application.example.test/snapshot';

  const result = runOpen(fixture, targetUrl);

  assert.equal(result.status, 0, result.stderr);
  const receipt = JSON.parse(fs.readFileSync(fixture.receipt, 'utf8'));
  assert.equal(receipt.profile, fixture.profile);
  assert.match(
    receipt.actual_profile,
    /agent-browser-chrome-[a-f0-9-]+$/
  );
  assert.equal(receipt.profile_mode, 'verified-snapshot');
  assert.equal(receipt.profile_lineage.proof, 'structural-metadata');
  assert.match(receipt.profile_lineage.structural_digest, /^[a-f0-9]{64}$/);
  assert.ok(receipt.profile_lineage.structural_matched_entries >= 3);
  assert.equal(receipt.first_navigation.status, 'verified');
});

test('first navigation records stable identity, init probe, and document HAR', function(t) {
  const fixture = setup(t);
  const targetUrl = 'https://application.example.test/first';

  const result = runOpen(fixture, targetUrl);

  assert.equal(result.status, 0, result.stderr);
  const receipt = JSON.parse(fs.readFileSync(fixture.receipt, 'utf8'));
  assert.equal(receipt.first_navigation.status, 'verified');
  assert.equal(receipt.first_navigation.pre.daemon_pid, 321);
  assert.equal(receipt.first_navigation.post.daemon_pid, 321);
  assert.equal(receipt.first_navigation.pre.browser_pid, 654);
  assert.equal(receipt.first_navigation.post.browser_pid, 654);
  assert.equal(receipt.first_navigation.pre.page_identity, 't1');
  assert.equal(receipt.first_navigation.post.page_identity, 't1');
  assert.equal(receipt.first_navigation.pre.actual_profile, fixture.profile);
  assert.equal(receipt.first_navigation.post.actual_profile, fixture.profile);
  assert.equal(receipt.first_navigation.post.url, targetUrl);
  assert.equal(receipt.first_navigation.init_script, 'observed');
  assert.equal(receipt.first_navigation.har.status, 'verified-and-discarded');
  assert.ok(receipt.first_navigation.har.document_count >= 1);
});

for (const reset of ['daemon', 'browser', 'page']) {
  test('forced ' + reset + ' reset is a deterministic infrastructure failure', function(t) {
    const fixture = setup(t, { resetOnNavigation: reset });

    const result = runOpen(
      fixture,
      'https://application.example.test/reset-' + reset
    );

    assert.notEqual(result.status, 0);
    const receipt = JSON.parse(fs.readFileSync(fixture.receipt, 'utf8'));
    assert.equal(receipt.status, 'failed');
    assert.equal(receipt.failure_class, 'infrastructure');
    assert.match(
      receipt.error,
      reset === 'page'
        ? /page identity changed/i
        : new RegExp(reset + '.*changed', 'i')
    );
  });
}

test('parallel run cleanup leaves the peer run and personal profile untouched', function(t) {
  const first = setup(t);
  const second = setup(t);
  const personalProfile = path.join(first.root, 'personal-profile');
  fs.mkdirSync(personalProfile);
  fs.writeFileSync(path.join(personalProfile, 'Cookies'), 'personal');
  assert.equal(
    runOpen(first, 'https://application.example.test/one').status,
    0
  );
  assert.equal(
    runOpen(second, 'https://application.example.test/two').status,
    0
  );

  const close = spawnSync(
    process.execPath,
    [
      RUNTIME,
      '--run-id',
      first.runId,
      '--app',
      first.app,
      '--profile',
      first.profile,
      '--receipt',
      first.receipt,
      'close',
    ],
    { encoding: 'utf8', env: first.env }
  );

  assert.equal(close.status, 0, close.stderr);
  assert.equal(
    JSON.parse(fs.readFileSync(second.statePath, 'utf8')).active,
    true
  );
  assert.equal(
    fs.readFileSync(path.join(personalProfile, 'Cookies'), 'utf8'),
    'personal'
  );
});

test('subsequent actions do not replay browser launch flags', function(t) {
  const fixture = setup(t, { profileMode: 'snapshot' });
  assert.equal(
    runOpen(fixture, 'https://application.example.test/first').status,
    0
  );

  const action = spawnSync(
    process.execPath,
    [
      RUNTIME,
      '--run-id',
      fixture.runId,
      '--app',
      fixture.app,
      '--executable-path',
      fixture.executable,
      '--profile',
      fixture.profile,
      '--receipt',
      fixture.receipt,
      'snapshot',
      '-i',
    ],
    { encoding: 'utf8', env: fixture.env }
  );

  assert.equal(action.status, 0, action.stderr);
  const state = JSON.parse(fs.readFileSync(fixture.statePath, 'utf8'));
  const event = state.events.findLast(function(candidate) {
    return candidate.command === 'snapshot';
  });
  assert.ok(event);
  assert.equal(event.argv.includes('--profile'), false);
  assert.equal(event.argv.includes('--executable-path'), false);
  assert.equal(event.argv.includes('--engine'), false);
});
