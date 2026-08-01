'use strict';

const { test } = require('node:test');
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');

const RUNTIME = path.join(__dirname, '..', '..', 'bin', 'e2e-browser-runtime.js');
const runtimeModule = require(RUNTIME);

function makeExecutable(filePath, source) {
  fs.writeFileSync(filePath, source, { mode: 0o755 });
}

function managedChromeForTesting(browserHome) {
  const executablePath = path.join(
    browserHome,
    'browsers',
    'chrome-151.0.2.1',
    'chrome-mac-arm64',
    'Google Chrome for Testing.app',
    'Contents',
    'MacOS',
    'Google Chrome for Testing'
  );
  fs.mkdirSync(path.dirname(executablePath), { recursive: true });
  makeExecutable(executablePath, '#!/usr/bin/env bash\nexit 0\n');
  return executablePath;
}

function sessionInfo(namespace, session, options) {
  const settings = Object.assign(
    {
      active: true,
      daemonPid: 321,
      reused: false,
      socketDir: '',
      engine: 'chrome',
      browserLaunched: true,
    },
    options || {}
  );
  return {
    success: true,
    data: {
      active: settings.active,
      namespace,
      pid: settings.daemonPid,
      session,
      socketDir: settings.socketDir,
      version: '0.32.0',
      runtimeError: null,
      runtime: {
        backgroundPid: settings.daemonPid,
        browserLaunched: settings.browserLaunched,
        engine: settings.engine,
        namespace,
        session,
        socketDir: settings.socketDir,
        effectiveLaunch: {
          browserLaunched: settings.browserLaunched,
          engine: settings.engine,
          launchHash: 12345,
        },
        lifecycle: {
          effectiveLaunch: {
            browserLaunched: settings.browserLaunched,
            engine: settings.engine,
            launchHash: 12345,
          },
          launched: !settings.reused,
          relaunchedBrowser: false,
          restartedBackground: false,
          restoreStatus: 'not_configured',
          reused: settings.reused,
          saveStatus: 'not_attempted',
        },
      },
    },
  };
}

function setupRuntime(t, options) {
  const settings = Object.assign(
    {
      runId: 'run-123',
      app: 'storefront',
      reused: false,
      sessionOverrides: {},
      processProfile: '',
    },
    options || {}
  );
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-browser-ownership-'));
  t.after(function() {
    fs.rmSync(dir, { recursive: true, force: true });
  });
  const browserHome = path.join(
    '/tmp',
    'e2e-bh-' + path.basename(dir)
  );
  fs.mkdirSync(browserHome);
  t.after(function() {
    fs.rmSync(browserHome, { recursive: true, force: true });
  });
  const chrome = managedChromeForTesting(browserHome);
  const profile = path.join(browserHome, settings.app);
  const receipt = path.join(dir, 'report', 'browser-ownership.json');
  const browserLog = path.join(dir, 'agent-browser.log');
  const namespace = 'e2e-' + settings.runId;
  const socketDir = path.join(
    runtimeModule.socketHomeForBrowserHome(browserHome),
    'namespaces',
    namespace,
    'run'
  );
  const info = sessionInfo(
    settings.sessionOverrides.namespace || namespace,
    settings.sessionOverrides.session || settings.app,
    Object.assign(
      {
        reused: settings.reused,
        socketDir: settings.sessionOverrides.socketDir || socketDir,
      },
      settings.sessionOverrides
    )
  );
  const agentBrowser = path.join(dir, 'agent-browser');
  makeExecutable(
    agentBrowser,
    [
      '#!/usr/bin/env node',
      "'use strict';",
      "const fs = require('node:fs');",
      'const args = process.argv.slice(2);',
      "fs.appendFileSync(process.env.E2E_TEST_BROWSER_LOG, JSON.stringify(args) + '\\n');",
      "if (args.includes('session') && args.includes('info')) {",
      '  process.stdout.write(process.env.E2E_TEST_SESSION_INFO + "\\n");',
      '}',
      '',
    ].join('\n')
  );
  const ps = path.join(dir, 'ps');
  const processProfile = settings.processProfile || profile;
  makeExecutable(
    ps,
    [
      '#!/usr/bin/env node',
      "process.stdout.write('654 321 ' + process.env.E2E_TEST_CHROME +",
      "  ' --remote-debugging-port=0 --user-data-dir=' +",
      "  process.env.E2E_TEST_PROCESS_PROFILE + '\\n');",
      '',
    ].join('\n')
  );
  return {
    app: settings.app,
    browserHome,
    browserLog,
    chrome,
    dir,
    namespace,
    profile,
    ps,
    receipt,
    runId: settings.runId,
    socketDir,
    env: Object.assign({}, process.env, {
      E2E_AGENT_BROWSER_BIN: agentBrowser,
      E2E_AGENT_BROWSER_HOME: browserHome,
      E2E_PS_BIN: ps,
      E2E_RUNTIME_TEST_MODE: '1',
      E2E_TEST_BROWSER_LOG: browserLog,
      E2E_TEST_CHROME: chrome,
      E2E_TEST_PROCESS_PROFILE: processProfile,
      E2E_TEST_SESSION_INFO: JSON.stringify(info),
    }),
  };
}

function openRuntime(fixture) {
  return spawnSync(
    process.execPath,
    [
      RUNTIME,
      '--run-id',
      fixture.runId,
      '--app',
      fixture.app,
      '--executable-path',
      fixture.chrome,
      '--profile',
      fixture.profile,
      '--receipt',
      fixture.receipt,
      'open',
      'https://example.test',
    ],
    { encoding: 'utf8', env: fixture.env }
  );
}

test('first open verifies daemon, Chrome process, profile, and non-reuse before writing a receipt', function(t) {
  const fixture = setupRuntime(t);
  const result = openRuntime(fixture);

  assert.equal(result.status, 0, result.stderr);
  const receipt = JSON.parse(fs.readFileSync(fixture.receipt, 'utf8'));
  assert.deepEqual(
    {
      version: receipt.version,
      status: receipt.status,
      runId: receipt.run_id,
      app: receipt.app,
      namespace: receipt.namespace,
      session: receipt.session,
      executable: receipt.executable,
      profile: receipt.profile,
      socketDir: receipt.socket_dir,
      daemonPid: receipt.daemon_pid,
      browserPid: receipt.browser_pid,
      initialReused: receipt.initial_reused,
    },
    {
      version: 1,
      status: 'active',
      runId: fixture.runId,
      app: fixture.app,
      namespace: fixture.namespace,
      session: fixture.app,
      executable: fixture.chrome,
      profile: fixture.profile,
      socketDir: fixture.socketDir,
      daemonPid: 321,
      browserPid: 654,
      initialReused: false,
    }
  );
});

test('first open fails closed when agent-browser reports daemon reuse', function(t) {
  const fixture = setupRuntime(t, { reused: true });
  const result = openRuntime(fixture);

  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /reused=false|unexpected daemon reuse/i);
  assert.equal(fs.existsSync(fixture.receipt), false);
});

test('persistent mode rejects foreign and symlinked app profiles before browser launch', function(t) {
  const foreignFixture = setupRuntime(t);
  const foreignProfile = path.join(foreignFixture.dir, 'personal-profile');
  const foreignResult = spawnSync(
    process.execPath,
    [
      RUNTIME,
      '--run-id',
      foreignFixture.runId,
      '--app',
      foreignFixture.app,
      '--executable-path',
      foreignFixture.chrome,
      '--profile',
      foreignProfile,
      '--receipt',
      foreignFixture.receipt,
      'open',
      'https://example.test',
    ],
    { encoding: 'utf8', env: foreignFixture.env }
  );

  assert.notEqual(foreignResult.status, 0);
  assert.match(foreignResult.stderr, /persistent profile must be the app profile/i);
  assert.equal(fs.existsSync(foreignFixture.browserLog), false);

  const symlinkFixture = setupRuntime(t);
  const personalProfile = path.join(symlinkFixture.dir, 'personal-profile');
  fs.mkdirSync(personalProfile);
  fs.symlinkSync(personalProfile, symlinkFixture.profile);
  const symlinkResult = openRuntime(symlinkFixture);

  assert.notEqual(symlinkResult.status, 0);
  assert.match(symlinkResult.stderr, /canonical profile must not be a symlink/i);
  assert.equal(fs.existsSync(symlinkFixture.browserLog), false);
});

test('same-run navigation permits reuse only against a matching existing receipt', function(t) {
  const first = setupRuntime(t);
  const initial = openRuntime(first);
  assert.equal(initial.status, 0, initial.stderr);

  const reusedInfo = sessionInfo(first.namespace, first.app, {
    reused: true,
    socketDir: first.socketDir,
  });
  first.env.E2E_TEST_SESSION_INFO = JSON.stringify(reusedInfo);
  const second = openRuntime(first);

  assert.equal(second.status, 0, second.stderr);
  const receipt = JSON.parse(fs.readFileSync(first.receipt, 'utf8'));
  assert.equal(receipt.initial_reused, false);
  assert.equal(receipt.last_reused, true);
});

test('subsequent browser actions fail before execution when ownership receipt drifts', function(t) {
  const fixture = setupRuntime(t);
  const initial = openRuntime(fixture);
  assert.equal(initial.status, 0, initial.stderr);
  const command = [
    RUNTIME,
    '--run-id',
    fixture.runId,
    '--app',
    fixture.app,
    '--executable-path',
    fixture.chrome,
    '--profile',
    fixture.profile,
    '--receipt',
    fixture.receipt,
    'snapshot',
    '-i',
  ];
  const valid = spawnSync(process.execPath, command, {
    encoding: 'utf8',
    env: fixture.env,
  });
  assert.equal(valid.status, 0, valid.stderr);

  const receipt = JSON.parse(fs.readFileSync(fixture.receipt, 'utf8'));
  receipt.executable = path.join(fixture.dir, 'personal-browser');
  fs.writeFileSync(fixture.receipt, JSON.stringify(receipt, null, 2) + '\n');
  const before = fs.readFileSync(fixture.browserLog, 'utf8');

  const result = spawnSync(process.execPath, command, {
    encoding: 'utf8',
    env: fixture.env,
  });

  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /receipt does not match executable/i);
  assert.equal(fs.readFileSync(fixture.browserLog, 'utf8'), before);
});

test('scoped close records cleanup and removes only its owned session state', function(t) {
  const fixture = setupRuntime(t);
  const initial = openRuntime(fixture);
  assert.equal(initial.status, 0, initial.stderr);
  fs.mkdirSync(fixture.socketDir, { recursive: true });
  const ownedConfig = path.join(fixture.socketDir, fixture.app + '.config');
  const peerConfig = path.join(fixture.socketDir, 'peer.config');
  fs.writeFileSync(ownedConfig, '{}');
  fs.writeFileSync(peerConfig, '{}');

  const result = spawnSync(
    process.execPath,
    [
      RUNTIME,
      '--run-id',
      fixture.runId,
      '--app',
      fixture.app,
      '--profile',
      fixture.profile,
      '--receipt',
      fixture.receipt,
      'close',
    ],
    { encoding: 'utf8', env: fixture.env }
  );

  assert.equal(result.status, 0, result.stderr);
  const receipt = JSON.parse(fs.readFileSync(fixture.receipt, 'utf8'));
  assert.equal(receipt.status, 'closed');
  assert.equal(receipt.cleanup, 'owned-session-closed');
  assert.equal(fs.existsSync(ownedConfig), false);
  assert.equal(fs.existsSync(peerConfig), true);
});

test('ownership validation rejects session and process binding drift', function(t) {
  const wrongSession = setupRuntime(t, {
    sessionOverrides: { session: 'someone-else' },
  });
  const wrongProfile = setupRuntime(t, {
    processProfile: path.join(os.tmpdir(), 'foreign-profile'),
  });

  const sessionResult = openRuntime(wrongSession);
  const profileResult = openRuntime(wrongProfile);

  assert.notEqual(sessionResult.status, 0);
  assert.match(sessionResult.stderr, /session.*does not match|ownership/i);
  assert.notEqual(profileResult.status, 0);
  assert.match(profileResult.stderr, /profile|process.*evidence/i);
  assert.equal(fs.existsSync(wrongSession.receipt), false);
  assert.equal(fs.existsSync(wrongProfile.receipt), false);
});

// agent-browser names the socket after the session, not a fixed "daemon.sock":
// <socketHome>/namespaces/<namespace>/run/<session>.sock. Confirmed on disk against
// agent-browser 0.32.0. Budgeting against a fixed filename under-counts by
// (len(session) + 5) - len('daemon.sock') bytes, which agent-browser then refuses.
function socketPathFor(socketHome, namespace, session) {
  return path.join(socketHome, 'namespaces', namespace, 'run', session + '.sock');
}

test('long run identities normalize to distinct socket-safe namespaces', function() {
  const browserHome = '/tmp/agent-browser-home';
  const session = 'secha-office';
  const firstRun = 'task23-' + 'a'.repeat(100);
  const secondRun = 'task23-' + 'b'.repeat(100);

  assert.equal(typeof runtimeModule.namespaceForRun, 'function');
  const first = runtimeModule.namespaceForRun(firstRun, browserHome, session);
  const second = runtimeModule.namespaceForRun(secondRun, browserHome, session);

  assert.match(first, /^e2e-[a-z0-9-]+-[a-f0-9]{12}$/);
  assert.match(second, /^e2e-[a-z0-9-]+-[a-f0-9]{12}$/);
  assert.notEqual(first, second);
  for (const namespace of [first, second]) {
    const finalSocketPath = socketPathFor(browserHome, namespace, session);
    assert.ok(
      Buffer.byteLength(finalSocketPath) <= 103,
      crypto.createHash('sha256').update(finalSocketPath).digest('hex')
    );
  }
});

test('a generated run identity stays socket-safe for a realistic session name', function() {
  // Shape produced by `new-run-id`: base36 timestamp + '-' + 20 hex characters.
  const runId = 'msahjbw3-c5db2df771f976678836';
  // Shape produced by socketHomeForBrowserHome for a real home directory.
  const socketHome = '/tmp/e2e-agent-browser-502-5943dac8f232';

  for (const session of ['secha-app', 'secha-office', 'a'.repeat(24)]) {
    const namespace = runtimeModule.namespaceForRun(runId, socketHome, session);
    const socketPath = socketPathFor(socketHome, namespace, session);
    assert.ok(
      Buffer.byteLength(socketPath) <= 103,
      session + ' -> ' + Buffer.byteLength(socketPath) + ' bytes: ' + socketPath
    );
  }
});

test('an unusable session name fails in the runtime, not inside agent-browser', function() {
  const socketHome = '/tmp/e2e-agent-browser-502-5943dac8f232';
  assert.throws(
    function() {
      runtimeModule.namespaceForRun('abc123', socketHome, 'x'.repeat(80));
    },
    /socket-safe/
  );
});
