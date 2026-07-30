#!/usr/bin/env node
'use strict';

const { spawn, spawnSync } = require('node:child_process');
const crypto = require('node:crypto');
const fs = require('node:fs');
const net = require('node:net');
const path = require('node:path');

const ALLOWED_HOSTS = new Set(['127.0.0.1', '::1', 'localhost']);

function fail(message, code) {
  const error = new Error(message);
  error.exitCode = code || 2;
  throw error;
}

function parseArgs(argv) {
  const command = argv[0] || '';
  const options = { command, manifest: '', runId: '', stateDir: '' };
  for (let index = 1; index < argv.length; index += 1) {
    const value = argv[index];
    if (value === '--manifest') options.manifest = argv[++index] || '';
    else if (value === '--run-id') options.runId = argv[++index] || '';
    else if (value === '--state-dir') options.stateDir = argv[++index] || '';
    else fail('unknown argument: ' + value, 64);
  }
  return options;
}

function assertRunId(runId) {
  if (!/^[a-z0-9][a-z0-9-]{2,127}$/.test(runId)) {
    fail('run identity must use 3-128 lowercase letters, digits, or hyphens', 64);
  }
}

function assertRegularFile(filePath, description) {
  let stat;
  try {
    stat = fs.lstatSync(filePath);
  } catch (_error) {
    fail(description + ' is unavailable: ' + filePath, 64);
  }
  if (!stat.isFile() || stat.isSymbolicLink()) {
    fail(description + ' must be a regular file: ' + filePath, 64);
  }
}

function readJson(filePath, description) {
  assertRegularFile(filePath, description);
  try {
    return JSON.parse(fs.readFileSync(filePath, 'utf8'));
  } catch (_error) {
    fail(description + ' is not valid JSON: ' + filePath, 64);
  }
}

function assertOnlyKeys(value, allowed, description) {
  for (const key of Object.keys(value)) {
    if (!allowed.has(key)) fail(description + ' contains unknown field: ' + key, 64);
  }
}

function findExecutable(command, environment) {
  if (path.isAbsolute(command)) {
    try {
      fs.accessSync(command, fs.constants.X_OK);
      return command;
    } catch (_error) {
      return '';
    }
  }
  const pathValue = (environment.PATH || '').split(path.delimiter);
  for (const directory of pathValue) {
    if (!directory) continue;
    const candidate = path.join(directory, command);
    try {
      fs.accessSync(candidate, fs.constants.X_OK);
      return candidate;
    } catch (_error) {
      // Continue searching PATH.
    }
  }
  return '';
}

function requiredTool(name, candidates) {
  for (const candidate of candidates) {
    const executable = findExecutable(candidate, process.env);
    if (executable) return executable;
  }
  fail('required local-service ownership tool is unavailable: ' + name, 69);
}

let resolvedPs = '';
let resolvedLsof = '';

function psTool() {
  if (!resolvedPs) {
    resolvedPs =
      process.env.E2E_RUNTIME_TEST_MODE === '1' && process.env.E2E_SERVICE_PS_BIN
      ? requiredTool('ps', [process.env.E2E_SERVICE_PS_BIN])
      : requiredTool('ps', ['/bin/ps', '/usr/bin/ps', 'ps']);
  }
  return resolvedPs;
}

function lsofTool() {
  if (!resolvedLsof) {
    resolvedLsof =
      process.env.E2E_RUNTIME_TEST_MODE === '1' &&
      process.env.E2E_SERVICE_LSOF_BIN
      ? requiredTool('lsof', [process.env.E2E_SERVICE_LSOF_BIN])
      : requiredTool('lsof', ['/usr/sbin/lsof', '/usr/bin/lsof', 'lsof']);
  }
  return resolvedLsof;
}

function processGroupId(pid) {
  const result = spawnSync(psTool(), ['-o', 'pgid=', '-p', String(pid)], {
    encoding: 'utf8',
  });
  if (result.status !== 0) return null;
  const pgid = Number(String(result.stdout || '').trim());
  return Number.isInteger(pgid) && pgid > 0 ? pgid : null;
}

function processCommand(pid) {
  const result = spawnSync(
    psTool(),
    ['-ww', '-o', 'command=', '-p', String(pid)],
    { encoding: 'utf8' }
  );
  if (result.status !== 0) return '';
  return String(result.stdout || '').trim();
}

function listenerPids(port) {
  const result = spawnSync(
    lsofTool(),
    ['-nP', '-iTCP:' + port, '-sTCP:LISTEN', '-t'],
    { encoding: 'utf8' }
  );
  if (result.status !== 0 && result.status !== 1) {
    fail('lsof listener probe failed for port ' + port, 70);
  }
  return Array.from(
    new Set(
      String(result.stdout || '')
        .split(/\s+/)
        .filter(Boolean)
        .map(Number)
        .filter(function(pid) {
          return Number.isInteger(pid) && pid > 0;
        })
    )
  );
}

function validateCapabilities() {
  if (process.platform !== 'darwin' && process.platform !== 'linux') {
    fail('local-service process-group supervision is unsupported on ' + process.platform, 69);
  }
  const pgid = processGroupId(process.pid);
  if (!pgid) fail('process-group feature test failed', 69);
  const lsof = spawnSync(lsofTool(), ['-v'], { encoding: 'utf8' });
  if (lsof.error) fail('lsof feature test failed: ' + lsof.error.message, 69);
}

function validateManifest(manifestPath, rejectListeners) {
  if (!path.isAbsolute(manifestPath)) {
    fail('service manifest path must be absolute', 64);
  }
  const manifest = readJson(manifestPath, 'service manifest');
  if (!manifest || Array.isArray(manifest) || typeof manifest !== 'object') {
    fail('service manifest must be an object', 64);
  }
  assertOnlyKeys(manifest, new Set(['version', 'services']), 'service manifest');
  if (manifest.version !== 1 || !Array.isArray(manifest.services) || manifest.services.length === 0) {
    fail('service manifest requires version 1 and a non-empty services array', 64);
  }
  const names = new Set();
  const ports = new Set();
  const services = manifest.services.map(function(service, index) {
    if (!service || Array.isArray(service) || typeof service !== 'object') {
      fail('service ' + index + ' must be an object', 64);
    }
    assertOnlyKeys(
      service,
      new Set(['name', 'command', 'cwd', 'host', 'port', 'readiness_timeout_ms']),
      'service ' + index
    );
    if (!/^[a-z0-9][a-z0-9-]{0,62}$/.test(service.name || '')) {
      fail('service name must be lowercase letters, digits, or hyphens', 64);
    }
    if (names.has(service.name)) fail('duplicate service name: ' + service.name, 64);
    names.add(service.name);
    if (
      !Array.isArray(service.command) ||
      service.command.length === 0 ||
      service.command.some(function(value) {
        return (
          typeof value !== 'string' ||
          value.length === 0 ||
          value.includes('\0') ||
          /[\r\n]/.test(value)
        );
      })
    ) {
      fail(
        'service ' + service.name +
          ' command must be a non-empty argv array; shell strings are prohibited',
        64
      );
    }
    const executable = findExecutable(service.command[0], process.env);
    if (!executable) fail('service executable is unavailable: ' + service.command[0], 69);
    if (!path.isAbsolute(service.cwd || '')) {
      fail('service ' + service.name + ' cwd must be absolute', 64);
    }
    let cwdStat;
    try {
      cwdStat = fs.lstatSync(service.cwd);
    } catch (_error) {
      fail('service ' + service.name + ' cwd is unavailable: ' + service.cwd, 64);
    }
    if (!cwdStat.isDirectory() || cwdStat.isSymbolicLink()) {
      fail('service ' + service.name + ' cwd must be a non-symlink directory', 64);
    }
    if (!ALLOWED_HOSTS.has(service.host)) {
      fail('service ' + service.name + ' host must be loopback', 64);
    }
    if (!Number.isInteger(service.port) || service.port < 1 || service.port > 65535) {
      fail('service ' + service.name + ' port must be 1-65535', 64);
    }
    if (ports.has(service.port)) fail('duplicate service port: ' + service.port, 64);
    ports.add(service.port);
    if (
      !Number.isInteger(service.readiness_timeout_ms) ||
      service.readiness_timeout_ms < 100 ||
      service.readiness_timeout_ms > 120000
    ) {
      fail('service readiness_timeout_ms must be 100-120000', 64);
    }
    if (rejectListeners && listenerPids(service.port).length > 0) {
      fail(
        'foreign process is already listening on service port ' + service.port,
        65
      );
    }
    return Object.assign({}, service, {
      command: [executable].concat(service.command.slice(1)),
    });
  });
  return { version: 1, services, manifestPath };
}

function ensureStateDirectory(stateDir) {
  if (!path.isAbsolute(stateDir)) fail('state directory must be absolute', 64);
  fs.mkdirSync(stateDir, { recursive: true, mode: 0o700 });
  const stat = fs.lstatSync(stateDir);
  if (!stat.isDirectory() || stat.isSymbolicLink()) {
    fail('state directory must be a non-symlink directory', 64);
  }
  return stateDir;
}

function statePath(stateDir, runId) {
  return path.join(stateDir, runId + '.json');
}

function writeState(filePath, state) {
  const temporary =
    filePath + '.tmp-' + process.pid + '-' + crypto.randomBytes(4).toString('hex');
  fs.writeFileSync(temporary, JSON.stringify(state, null, 2) + '\n', {
    mode: 0o600,
  });
  fs.renameSync(temporary, filePath);
}

function readState(stateDir, runId) {
  const filePath = statePath(stateDir, runId);
  const state = readJson(filePath, 'local-service ownership receipt');
  if (state.version !== 1 || state.run_id !== runId) {
    fail('local-service ownership receipt does not match run identity', 66);
  }
  return { filePath, state };
}

function processExists(pid) {
  try {
    process.kill(pid, 0);
    return true;
  } catch (_error) {
    return false;
  }
}

function groupExists(pgid) {
  try {
    process.kill(-pgid, 0);
    return true;
  } catch (_error) {
    return false;
  }
}

function waitForPort(host, port, timeoutMs) {
  const deadline = Date.now() + timeoutMs;
  return new Promise(function(resolve, reject) {
    function probe() {
      const socket = net.connect({ host, port });
      let settled = false;
      socket.once('connect', function() {
        settled = true;
        socket.destroy();
        resolve();
      });
      socket.once('error', function() {
        if (settled) return;
        socket.destroy();
        if (Date.now() >= deadline) reject(new Error('readiness timeout on port ' + port));
        else setTimeout(probe, 40);
      });
    }
    probe();
  });
}

function delay(milliseconds) {
  return new Promise(function(resolve) {
    setTimeout(resolve, milliseconds);
  });
}

async function terminateGroups(services) {
  for (const service of services.slice().reverse()) {
    if (!groupExists(service.process_group_id)) continue;
    try {
      process.kill(-service.process_group_id, 'SIGTERM');
    } catch (_error) {
      // The group exited between validation and signaling.
    }
  }
  const deadline = Date.now() + 3000;
  while (
    Date.now() < deadline &&
    services.some(function(service) {
      return groupExists(service.process_group_id);
    })
  ) {
    await delay(40);
  }
  for (const service of services.slice().reverse()) {
    if (!groupExists(service.process_group_id)) continue;
    try {
      process.kill(-service.process_group_id, 'SIGKILL');
    } catch (_error) {
      // The group exited before escalation.
    }
  }
}

async function abortStartingSupervisor(child, options, stateDir) {
  if (processExists(child.pid)) {
    try {
      process.kill(child.pid, 'SIGTERM');
    } catch (_error) {
      // The supervisor exited between the liveness check and signaling.
    }
  }
  const deadline = Date.now() + 10000;
  while (processExists(child.pid) && Date.now() < deadline) {
    await delay(40);
  }
  if (processExists(child.pid)) {
    const command = processCommand(child.pid);
    if (
      command.includes(path.resolve(__filename)) &&
      command.includes('supervise') &&
      command.includes(options.runId) &&
      command.includes(path.resolve(stateDir))
    ) {
      try {
        process.kill(child.pid, 'SIGKILL');
      } catch (_error) {
        // The supervisor exited before escalation.
      }
    }
  }
  const receiptPath = statePath(stateDir, options.runId);
  if (fs.existsSync(receiptPath)) {
    try {
      const state = readState(stateDir, options.runId).state;
      await terminateGroups(Array.isArray(state.services) ? state.services : []);
    } catch (_error) {
      // Preserve the original startup failure; receipt validation reports drift later.
    }
  }
}

async function supervise(options) {
  validateCapabilities();
  const manifest = validateManifest(options.manifest, true);
  const stateDir = ensureStateDirectory(options.stateDir);
  const filePath = statePath(stateDir, options.runId);
  const state = {
    version: 1,
    status: 'starting',
    run_id: options.runId,
    manifest: options.manifest,
    supervisor_pid: process.pid,
    services: [],
    started_at: new Date().toISOString(),
  };
  writeState(filePath, state);
  let stopping = false;

  async function stop(status, errorMessage) {
    if (stopping) return;
    stopping = true;
    await terminateGroups(state.services);
    state.status = status;
    state.cleanup = 'owned-process-groups-terminated';
    if (errorMessage) state.error = errorMessage;
    state.stopped_at = new Date().toISOString();
    writeState(filePath, state);
    process.exitCode = status === 'stopped' ? 0 : 1;
  }

  process.on('SIGTERM', function() {
    stop('stopped').then(function() {
      process.exit(process.exitCode);
    });
  });
  process.on('SIGINT', function() {
    stop('stopped').then(function() {
      process.exit(process.exitCode);
    });
  });

  try {
    for (const service of manifest.services) {
      const logPath = path.join(stateDir, options.runId + '-' + service.name + '.log');
      const logFd = fs.openSync(logPath, 'a', 0o600);
      const child = spawn(service.command[0], service.command.slice(1), {
        cwd: service.cwd,
        detached: true,
        env: process.env,
        shell: false,
        stdio: ['ignore', logFd, logFd],
      });
      fs.closeSync(logFd);
      const pgid = child.pid && processGroupId(child.pid);
      if (!child.pid || !pgid || pgid !== child.pid) {
        fail('service process-group ownership could not be established: ' + service.name, 70);
      }
      const record = {
        name: service.name,
        command: service.command,
        cwd: service.cwd,
        host: service.host,
        port: service.port,
        launcher_pid: child.pid,
        process_group_id: pgid,
        listener_pid: null,
        log_path: logPath,
      };
      state.services.push(record);
      writeState(filePath, state);
      child.once('exit', function(code, signal) {
        if (stopping) return;
        stop(
          'failed',
          'service ' + service.name + ' exited: code=' + code + ' signal=' + signal
        ).then(function() {
          process.exit(process.exitCode);
        });
      });
      await waitForPort(service.host, service.port, service.readiness_timeout_ms);
      const listeners = listenerPids(service.port);
      if (listeners.length !== 1) {
        fail(
          'service listener ownership requires exactly one PID: ' + service.name,
          70
        );
      }
      const listenerPgid = processGroupId(listeners[0]);
      if (listenerPgid !== pgid) {
        fail('service listener is not owned by its process group: ' + service.name, 70);
      }
      record.listener_pid = listeners[0];
      writeState(filePath, state);
    }
    state.status = 'active';
    state.ready_at = new Date().toISOString();
    writeState(filePath, state);
    await new Promise(function() {});
  } catch (error) {
    await stop('failed', error.message);
    process.exit(process.exitCode);
  }
}

function validateSupervisorOwnership(state, stateDir) {
  if (
    !processExists(state.supervisor_pid) ||
    processGroupId(state.supervisor_pid) !== state.supervisor_pid
  ) {
    fail('local-service supervisor ownership drift: process is not active', 2);
  }
  const command = processCommand(state.supervisor_pid);
  const required = [
    process.execPath,
    path.resolve(__filename),
    'supervise',
    '--manifest',
    state.manifest,
    '--run-id',
    state.run_id,
    '--state-dir',
    path.resolve(stateDir),
  ];
  if (
    !command ||
    required.some(function(value) {
      return !command.includes(value);
    })
  ) {
    fail('local-service supervisor ownership drift: command binding mismatch', 2);
  }
}

function validateActiveState(state, stateDir) {
  if (state.status !== 'active') {
    fail('local-service ownership drift: supervisor is not active', 2);
  }
  validateSupervisorOwnership(state, stateDir);
  for (const service of state.services) {
    if (
      !groupExists(service.process_group_id) ||
      processGroupId(service.listener_pid) !== service.process_group_id ||
      !listenerPids(service.port).includes(service.listener_pid)
    ) {
      fail('local-service ownership drift: ' + service.name, 2);
    }
  }
}

async function start(options) {
  assertRunId(options.runId);
  validateCapabilities();
  const manifest = validateManifest(options.manifest, true);
  const stateDir = ensureStateDirectory(options.stateDir);
  const filePath = statePath(stateDir, options.runId);
  if (fs.existsSync(filePath)) fail('run receipt already exists: ' + filePath, 66);
  const child = spawn(
    process.execPath,
    [
      __filename,
      'supervise',
      '--manifest',
      options.manifest,
      '--run-id',
      options.runId,
      '--state-dir',
      stateDir,
    ],
    { detached: true, shell: false, stdio: 'ignore', env: process.env }
  );
  child.unref();
  const readinessBudget = manifest.services.reduce(function(total, service) {
    return total + service.readiness_timeout_ms;
  }, 0);
  const deadline = Date.now() + readinessBudget + 5000;
  while (Date.now() < deadline) {
    if (fs.existsSync(filePath)) {
      const state = readState(stateDir, options.runId).state;
      if (state.status === 'active') {
        process.stdout.write(JSON.stringify(state) + '\n');
        return;
      }
      if (state.status === 'failed') fail(state.error || 'service supervisor failed', 1);
    }
    if (!processExists(child.pid)) {
      await abortStartingSupervisor(child, options, stateDir);
      fail('service supervisor exited before readiness', 1);
    }
    await delay(40);
  }
  await abortStartingSupervisor(child, options, stateDir);
  fail('service supervisor readiness timed out', 1);
}

async function status(options) {
  assertRunId(options.runId);
  const record = readState(ensureStateDirectory(options.stateDir), options.runId);
  if (record.state.status === 'active') {
    validateActiveState(record.state, options.stateDir);
  }
  process.stdout.write(JSON.stringify(record.state) + '\n');
}

async function stop(options) {
  assertRunId(options.runId);
  const record = readState(ensureStateDirectory(options.stateDir), options.runId);
  if (record.state.status === 'stopped') {
    process.stdout.write(JSON.stringify(record.state) + '\n');
    return;
  }
  validateSupervisorOwnership(record.state, options.stateDir);
  process.kill(record.state.supervisor_pid, 'SIGTERM');
  const deadline = Date.now() + 10000;
  while (Date.now() < deadline) {
    const current = readState(options.stateDir, options.runId).state;
    if (current.status === 'stopped') {
      process.stdout.write(JSON.stringify(current) + '\n');
      return;
    }
    await delay(40);
  }
  fail('local-service supervisor did not stop within 10 seconds', 1);
}

async function main(argv) {
  const options = parseArgs(argv);
  if (options.command === 'new-run-id') {
    process.stdout.write(
      Date.now().toString(36) + '-' + crypto.randomBytes(10).toString('hex') + '\n'
    );
    return;
  }
  if (options.command === 'preflight') {
    validateCapabilities();
    const manifest = validateManifest(options.manifest, true);
    process.stdout.write(
      JSON.stringify({
        version: 1,
        status: 'ready',
        manifest: manifest.manifestPath,
        services: manifest.services.map(function(service) {
          return { name: service.name, host: service.host, port: service.port };
        }),
      }) + '\n'
    );
    return;
  }
  if (options.command === 'start') return start(options);
  if (options.command === 'status') return status(options);
  if (options.command === 'stop') return stop(options);
  if (options.command === 'supervise') {
    assertRunId(options.runId);
    return supervise(options);
  }
  fail('command must be new-run-id, preflight, start, status, or stop', 64);
}

if (require.main === module) {
  main(process.argv.slice(2)).catch(function(error) {
    process.stderr.write('e2e-local-service-runtime: ' + error.message + '\n');
    process.exitCode = error.exitCode || 1;
  });
}

module.exports = {
  listenerPids,
  parseArgs,
  validateManifest,
};
