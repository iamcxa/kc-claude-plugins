'use strict';

const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const net = require('node:net');
const os = require('node:os');
const path = require('node:path');
const { spawn, spawnSync } = require('node:child_process');

const RUNTIME = path.join(
  __dirname,
  '..',
  '..',
  'bin',
  'e2e-local-service-runtime.js'
);
const FIXTURE = path.join(
  __dirname,
  'fixtures',
  'local-service-fixture.js'
);

function temporaryDirectory(t) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-local-services-'));
  t.after(function() {
    fs.rmSync(dir, { recursive: true, force: true });
  });
  return dir;
}

function freePort() {
  return new Promise(function(resolve, reject) {
    const server = net.createServer();
    server.once('error', reject);
    server.listen(0, '127.0.0.1', function() {
      const port = server.address().port;
      server.close(function(error) {
        if (error) reject(error);
        else resolve(port);
      });
    });
  });
}

function writeManifest(dir, port, overrides) {
  const manifest = Object.assign(
    {
      version: 1,
      services: [
        {
          name: 'web',
          command: [
            process.execPath,
            FIXTURE,
            '--port',
            String(port),
            '--host',
            '127.0.0.1',
          ],
          cwd: dir,
          host: '127.0.0.1',
          port,
          readiness_timeout_ms: 5000,
        },
      ],
    },
    overrides || {}
  );
  const manifestPath = path.join(dir, 'services.json');
  fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2) + '\n');
  return manifestPath;
}

function run(args, options) {
  return spawnSync(process.execPath, [RUNTIME].concat(args), {
    encoding: 'utf8',
    env: Object.assign({}, process.env, (options && options.env) || {}),
    timeout: (options && options.timeout) || 15000,
  });
}

test('macOS zsh control proves wait -n is not portable', function() {
  if (process.platform !== 'darwin') return;
  const result = spawnSync(
    'zsh',
    ['-c', 'sleep 0.01 & wait -n'],
    { encoding: 'utf8' }
  );
  assert.equal(result.status, 127);
  assert.match(result.stderr, /job not found: -n/);
});

test('preflight rejects shell strings and invalid manifests before starting children', async function(t) {
  const dir = temporaryDirectory(t);
  const port = await freePort();
  const manifest = writeManifest(dir, port, {
    version: 1,
    services: [
      {
        name: 'web',
        command: 'npm run dev',
        cwd: dir,
        host: '127.0.0.1',
        port,
        readiness_timeout_ms: 5000,
      },
    ],
  });

  const result = run(['preflight', '--manifest', manifest]);

  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /command.*argv|array|shell/i);
});

test('preflight rejects duplicate ownership, relative cwd, invalid timeouts, and missing tools', async function(t) {
  const dir = temporaryDirectory(t);
  const port = await freePort();
  const validService = {
    name: 'web',
    command: [process.execPath, FIXTURE, '--port', String(port)],
    cwd: dir,
    host: '127.0.0.1',
    port,
    readiness_timeout_ms: 5000,
  };
  const cases = [
    {
      name: 'duplicate name',
      services: [validService, Object.assign({}, validService, { port: port + 1 })],
      pattern: /duplicate service name/i,
    },
    {
      name: 'duplicate port',
      services: [validService, Object.assign({}, validService, { name: 'api' })],
      pattern: /duplicate service port/i,
    },
    {
      name: 'relative cwd',
      services: [Object.assign({}, validService, { cwd: '.' })],
      pattern: /cwd must be absolute/i,
    },
    {
      name: 'invalid timeout',
      services: [Object.assign({}, validService, { readiness_timeout_ms: 99 })],
      pattern: /readiness_timeout_ms must be/i,
    },
  ];

  for (const testCase of cases) {
    const manifest = writeManifest(dir, port, {
      version: 1,
      services: testCase.services,
    });
    const result = run(['preflight', '--manifest', manifest]);
    assert.notEqual(result.status, 0, testCase.name);
    assert.match(result.stderr, testCase.pattern, testCase.name);
  }

  const manifest = writeManifest(dir, port);
  const missingTool = run(
    ['preflight', '--manifest', manifest],
    {
      env: {
        E2E_RUNTIME_TEST_MODE: '1',
        E2E_SERVICE_LSOF_BIN: path.join(dir, 'missing-lsof'),
      },
    }
  );
  assert.notEqual(missingTool.status, 0);
  assert.match(missingTool.stderr, /required.*tool.*unavailable|lsof/i);
});

test('start records supervisor, process-group, and listener ownership; status and stop preserve receipt', async function(t) {
  const dir = temporaryDirectory(t);
  const port = await freePort();
  const manifest = writeManifest(dir, port);
  const stateDir = path.join(dir, 'state');
  const runId = 'service-run-123';

  const start = run([
    'start',
    '--manifest',
    manifest,
    '--run-id',
    runId,
    '--state-dir',
    stateDir,
  ]);
  assert.equal(start.status, 0, start.stderr);
  const receipt = JSON.parse(start.stdout);
  t.after(function() {
    const statePath = path.join(stateDir, runId + '.json');
    if (!fs.existsSync(statePath)) return;
    const state = JSON.parse(fs.readFileSync(statePath, 'utf8'));
    if (state.status === 'active') {
      const cleanup = run([
        'stop',
        '--run-id',
        runId,
        '--state-dir',
        stateDir,
      ]);
      if (cleanup.status !== 0 && state.supervisor_pid) {
        try {
          process.kill(state.supervisor_pid, 'SIGTERM');
        } catch (_error) {
          // The supervisor is already absent.
        }
      }
    }
  });
  assert.equal(receipt.status, 'active');
  assert.equal(receipt.run_id, runId);
  assert.ok(Number.isInteger(receipt.supervisor_pid));
  assert.equal(receipt.services.length, 1);
  assert.equal(receipt.services[0].name, 'web');
  assert.ok(Number.isInteger(receipt.services[0].launcher_pid));
  assert.ok(Number.isInteger(receipt.services[0].process_group_id));
  assert.ok(Number.isInteger(receipt.services[0].listener_pid));
  assert.equal(
    receipt.services[0].listener_pid,
    receipt.services[0].launcher_pid
  );

  const status = run([
    'status',
    '--run-id',
    runId,
    '--state-dir',
    stateDir,
  ]);
  assert.equal(status.status, 0, status.stderr);
  assert.equal(JSON.parse(status.stdout).status, 'active');

  const statePath = path.join(stateDir, runId + '.json');
  const drifted = JSON.parse(fs.readFileSync(statePath, 'utf8'));
  drifted.services[0].listener_pid = process.pid;
  fs.writeFileSync(statePath, JSON.stringify(drifted, null, 2) + '\n');
  const driftStatus = run([
    'status',
    '--run-id',
    runId,
    '--state-dir',
    stateDir,
  ]);
  assert.notEqual(driftStatus.status, 0);
  assert.match(driftStatus.stderr, /ownership drift/i);
  fs.writeFileSync(statePath, JSON.stringify(receipt, null, 2) + '\n');

  const foreignProcess = spawn(
    process.execPath,
    ['-e', 'setInterval(function() {}, 1000)'],
    { detached: true, stdio: 'ignore' }
  );
  foreignProcess.unref();
  t.after(function() {
    try {
      process.kill(-foreignProcess.pid, 'SIGTERM');
    } catch (_error) {
      // The foreign process is already absent.
    }
  });
  await new Promise(function(resolve) {
    setTimeout(resolve, 50);
  });
  const foreignSupervisor = JSON.parse(JSON.stringify(receipt));
  foreignSupervisor.supervisor_pid = foreignProcess.pid;
  fs.writeFileSync(
    statePath,
    JSON.stringify(foreignSupervisor, null, 2) + '\n'
  );
  const supervisorDrift = run([
    'stop',
    '--run-id',
    runId,
    '--state-dir',
    stateDir,
  ]);
  assert.notEqual(supervisorDrift.status, 0);
  assert.match(supervisorDrift.stderr, /supervisor.*ownership drift/i);
  assert.doesNotThrow(function() {
    process.kill(foreignProcess.pid, 0);
  });
  fs.writeFileSync(statePath, JSON.stringify(receipt, null, 2) + '\n');

  const stop = run([
    'stop',
    '--run-id',
    runId,
    '--state-dir',
    stateDir,
  ]);
  assert.equal(stop.status, 0, stop.stderr);
  const stopped = JSON.parse(stop.stdout);
  assert.equal(stopped.status, 'stopped');
  assert.equal(stopped.cleanup, 'owned-process-groups-terminated');
  assert.equal(fs.existsSync(path.join(stateDir, runId + '.json')), true);
  assert.throws(function() {
    process.kill(receipt.services[0].launcher_pid, 0);
  });
});

test('preflight rejects a foreign listener without adopting or terminating it', async function(t) {
  const dir = temporaryDirectory(t);
  const port = await freePort();
  const manifest = writeManifest(dir, port);
  const foreign = spawn(process.execPath, [
    FIXTURE,
    '--port',
    String(port),
    '--host',
    '127.0.0.1',
  ]);
  t.after(function() {
    try {
      foreign.kill('SIGTERM');
    } catch (_error) {
      // The fixture is already stopped.
    }
  });
  await new Promise(function(resolve, reject) {
    const deadline = Date.now() + 3000;
    function probe() {
      const socket = net.connect(port, '127.0.0.1');
      socket.once('connect', function() {
        socket.destroy();
        resolve();
      });
      socket.once('error', function() {
        socket.destroy();
        if (Date.now() >= deadline) reject(new Error('foreign listener not ready'));
        else setTimeout(probe, 25);
      });
    }
    probe();
  });

  const result = run(['preflight', '--manifest', manifest]);

  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /foreign|already.*listen|port.*owned/i);
  assert.doesNotThrow(function() {
    process.kill(foreign.pid, 0);
  });
});
