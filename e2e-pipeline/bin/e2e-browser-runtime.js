#!/usr/bin/env node
'use strict';

const { spawnSync } = require('node:child_process');
const crypto = require('node:crypto');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const ALLOWED_COMMANDS = new Set([
  '--version',
  'back',
  'check',
  'click',
  'close',
  'cleanup-flow-managed-profile',
  'console',
  'errors',
  'eval',
  'fill',
  'find',
  'get',
  'hover',
  'is',
  'open',
  'press',
  'reload',
  'screenshot',
  'scroll',
  'select',
  'snapshot',
  'trace',
  'type',
  'uncheck',
  'wait',
]);

function parseArgs(argv) {
  const options = {
    runId: '',
    app: '',
    authMode: 'persistent',
    canonicalProfile: '',
    executablePath: '',
    profile: '',
    receipt: '',
    headed: false,
    command: [],
  };

  for (let index = 0; index < argv.length; index += 1) {
    const value = argv[index];
    if (value === '--run-id') {
      options.runId = argv[++index] || '';
    } else if (value === '--app') {
      options.app = argv[++index] || '';
    } else if (value === '--auth-mode') {
      options.authMode = argv[++index] || '';
    } else if (value === '--canonical-profile') {
      options.canonicalProfile = argv[++index] || '';
    } else if (value === '--executable-path') {
      options.executablePath = argv[++index] || '';
    } else if (value === '--profile') {
      options.profile = argv[++index] || '';
    } else if (value === '--receipt') {
      options.receipt = argv[++index] || '';
    } else if (value === '--headed') {
      options.headed = true;
    } else {
      options.command = argv.slice(index);
      break;
    }
  }

  return options;
}

function socketHomeForBrowserHome(browserHome) {
  const temporaryRoot = process.platform === 'darwin' ? '/tmp' : os.tmpdir();
  const identity = crypto
    .createHash('sha256')
    .update(path.resolve(browserHome))
    .digest('hex')
    .slice(0, 12);
  const uid = typeof process.getuid === 'function' ? process.getuid() : 'user';
  return path.join(temporaryRoot, 'e2e-agent-browser-' + uid + '-' + identity);
}

function namespaceForRun(runId, socketHome) {
  const readable = 'e2e-' + runId;
  if (
    Buffer.byteLength(
      path.join(
        path.resolve(socketHome),
        'namespaces',
        readable,
        'run',
        'daemon.sock'
      )
    ) <= 103
  ) {
    return readable;
  }

  const digest = crypto.createHash('sha256').update(runId).digest('hex').slice(0, 12);
  const oneCharacterPath = path.join(
    path.resolve(socketHome),
    'namespaces',
    'X',
    'run',
    'daemon.sock'
  );
  const available = 103 - Buffer.byteLength(oneCharacterPath) + 1;
  const fixedLength = Buffer.byteLength('e2e--' + digest);
  if (available < Buffer.byteLength('e2e-a-' + digest)) {
    throw new Error(
      'agent-browser home is too long for a socket-safe e2e namespace: ' +
        path.resolve(socketHome)
    );
  }
  const prefixLength = available - fixedLength;
  const prefix = runId.slice(0, prefixLength).replace(/-+$/, '') || 'run';
  return 'e2e-' + prefix + '-' + digest;
}

function assertRunAndApp(runId, app) {
  if (!/^[a-z0-9][a-z0-9-]{2,127}$/.test(runId)) {
    throw new Error(
      'provide a valid run identity (lowercase letters, digits, and hyphens)'
    );
  }
  if (!/^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$/.test(app)) {
    throw new Error(
      'provide a valid app identity (letters, digits, dots, underscores, and hyphens)'
    );
  }
}

function assertCanonicalProfileRoot(profilePath) {
  const resolvedRoot = path.resolve(profilePath);
  if (!fs.existsSync(resolvedRoot)) return resolvedRoot;
  const stat = fs.lstatSync(resolvedRoot);
  if (stat.isSymbolicLink()) {
    throw new Error('canonical profile must not be a symlink: ' + resolvedRoot);
  }
  if (!stat.isDirectory()) {
    throw new Error('canonical profile must be a directory: ' + resolvedRoot);
  }
  return resolvedRoot;
}

function canonicalProfileDigest(profilePath) {
  const digest = crypto.createHash('sha256');
  const resolvedRoot = assertCanonicalProfileRoot(profilePath);

  function visit(currentPath, relativePath) {
    const stat = fs.lstatSync(currentPath);
    const type = stat.isDirectory()
      ? 'directory'
      : stat.isFile()
        ? 'file'
        : stat.isSymbolicLink()
          ? 'symlink'
          : 'other';
    digest.update(type + '\0' + relativePath + '\0' + stat.mode.toString(8) + '\0');
    if (stat.isSymbolicLink()) {
      digest.update(fs.readlinkSync(currentPath) + '\0');
      return;
    }
    if (stat.isFile()) {
      digest.update(fs.readFileSync(currentPath));
      digest.update('\0');
      return;
    }
    if (stat.isDirectory()) {
      for (const entry of fs.readdirSync(currentPath).sort()) {
        visit(path.join(currentPath, entry), path.join(relativePath, entry));
      }
    }
  }

  if (!fs.existsSync(resolvedRoot)) {
    digest.update('absent\0');
  } else {
    visit(resolvedRoot, '.');
  }
  return digest.digest('hex');
}

function ensureOwnedDirectory(directoryPath) {
  if (fs.existsSync(directoryPath)) {
    const stat = fs.lstatSync(directoryPath);
    if (!stat.isDirectory() || stat.isSymbolicLink()) {
      throw new Error('owned directory must not be a symlink: ' + directoryPath);
    }
    return;
  }
  fs.mkdirSync(directoryPath);
}

function ensureFlowManagedRoots(browserHome, runId, app) {
  const resolvedHome = path.resolve(browserHome);
  ensureOwnedDirectory(resolvedHome);
  const profileBase = path.join(resolvedHome, 'flow-managed-profiles');
  ensureOwnedDirectory(profileBase);
  ensureOwnedDirectory(path.join(profileBase, app));
  const stateBase = path.join(resolvedHome, 'flow-managed-state');
  ensureOwnedDirectory(stateBase);
  const runState = path.join(stateBase, runId);
  ensureOwnedDirectory(runState);
  ensureOwnedDirectory(path.join(runState, app));
}

function flowManagedProfilePath(browserHome, runId, app, replayId) {
  assertRunAndApp(runId, app);
  if (!/^[a-f0-9]{16}$/.test(replayId)) {
    throw new Error('flow-managed replay identity must be 16 lowercase hex characters');
  }
  return path.join(
    path.resolve(browserHome),
    'flow-managed-profiles',
    app,
    runId + '-' + replayId
  );
}

function expectedCanonicalProfile(browserHome, app) {
  return path.join(path.resolve(browserHome), app);
}

function flowManagedStatePath(browserHome, runId, app, profile) {
  const profileName = path.basename(profile);
  return path.join(
    path.resolve(browserHome),
    'flow-managed-state',
    runId,
    app,
    profileName + '.json'
  );
}

function flowManagedActiveBindingPath(browserHome, runId, app) {
  return path.join(
    path.resolve(browserHome),
    'flow-managed-state',
    runId,
    app,
    'active-profile.json'
  );
}

function assertFlowManagedBinding(options) {
  assertRunAndApp(options.runId, options.app);
  const canonicalProfile = path.resolve(options.canonicalProfile || '');
  const expectedCanonical = expectedCanonicalProfile(options.browserHome, options.app);
  if (!options.canonicalProfile || canonicalProfile !== expectedCanonical) {
    throw new Error(
      'canonical profile must be the app profile at ' + expectedCanonical
    );
  }
  const profile = path.resolve(options.profile || '');
  const profileRoot = path.join(
    path.resolve(options.browserHome),
    'flow-managed-profiles',
    options.app
  );
  const resolvedBrowserHome = path.resolve(options.browserHome);
  const realBrowserHome = fs.realpathSync(resolvedBrowserHome);
  for (const ownedPath of [
    resolvedBrowserHome,
    path.join(path.resolve(options.browserHome), 'flow-managed-profiles'),
    profileRoot,
  ]) {
    const stat = fs.lstatSync(ownedPath);
    if (!stat.isDirectory() || stat.isSymbolicLink()) {
      throw new Error('owned directory must not be a symlink: ' + ownedPath);
    }
    const expectedRealPath = path.join(
      realBrowserHome,
      path.relative(resolvedBrowserHome, ownedPath)
    );
    if (fs.realpathSync(ownedPath) !== expectedRealPath) {
      throw new Error('owned directory resolved outside its managed path: ' + ownedPath);
    }
  }
  const relative = path.relative(profileRoot, profile);
  if (
    !relative ||
    relative.startsWith('..' + path.sep) ||
    path.isAbsolute(relative) ||
    relative.includes(path.sep) ||
    !new RegExp(
      '^' + options.runId.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '-[a-f0-9]{16}$'
    ).test(relative)
  ) {
    throw new Error('ephemeral profile is outside the owned flow-managed profile root');
  }
  if (profile === canonicalProfile) {
    throw new Error('ephemeral profile must differ from the canonical profile');
  }
  return { canonicalProfile, profile };
}

function writeJsonAtomic(filePath, value, exclusive) {
  ensureOwnedDirectory(path.dirname(filePath));
  if (exclusive) {
    fs.writeFileSync(filePath, JSON.stringify(value, null, 2) + '\n', {
      flag: 'wx',
      mode: 0o600,
    });
    return;
  }
  const temporaryPath =
    filePath + '.tmp-' + process.pid + '-' + crypto.randomBytes(4).toString('hex');
  fs.writeFileSync(temporaryPath, JSON.stringify(value, null, 2) + '\n', {
    flag: 'w',
    mode: 0o600,
  });
  fs.renameSync(temporaryPath, filePath);
}

function readRegularJson(filePath, description) {
  let stat;
  try {
    stat = fs.lstatSync(filePath);
  } catch (error) {
    if (error.code === 'ENOENT') return null;
    throw error;
  }
  if (!stat.isFile() || stat.isSymbolicLink()) {
    throw new Error(description + ' must be a regular file: ' + filePath);
  }
  try {
    return JSON.parse(fs.readFileSync(filePath, 'utf8'));
  } catch (_error) {
    throw new Error(description + ' is not valid JSON: ' + filePath);
  }
}

function parseSessionInfo(stdout) {
  let payload;
  try {
    payload = JSON.parse(stdout);
  } catch (_error) {
    throw new Error('agent-browser session ownership evidence is not valid JSON');
  }
  const data = payload && payload.success === true && payload.data;
  const runtime = data && data.runtime;
  const lifecycle = runtime && runtime.lifecycle;
  const effectiveLaunch = runtime && runtime.effectiveLaunch;
  if (
    !data ||
    data.active !== true ||
    !Number.isInteger(data.pid) ||
    !runtime ||
    !lifecycle ||
    !effectiveLaunch
  ) {
    throw new Error('agent-browser session ownership evidence is incomplete');
  }
  return { data, effectiveLaunch, lifecycle, runtime };
}

function parseProcessTable(stdout) {
  const processes = new Map();
  for (const line of stdout.split('\n')) {
    const match = line.match(/^\s*(\d+)\s+(\d+)\s+(.+)$/);
    if (!match) continue;
    processes.set(Number(match[1]), {
      pid: Number(match[1]),
      ppid: Number(match[2]),
      command: match[3],
    });
  }
  return processes;
}

function isDescendantOf(process, ancestorPid, processes) {
  const visited = new Set();
  let current = process;
  while (current && !visited.has(current.pid)) {
    if (current.ppid === ancestorPid) return true;
    visited.add(current.pid);
    current = processes.get(current.ppid);
  }
  return false;
}

function browserProcessEvidence(executablePath, profile, daemonPid, childEnvironment) {
  const psBin =
    process.env.E2E_RUNTIME_TEST_MODE === '1' && process.env.E2E_PS_BIN
      ? process.env.E2E_PS_BIN
      : fs.existsSync('/bin/ps')
        ? '/bin/ps'
        : fs.existsSync('/usr/bin/ps')
          ? '/usr/bin/ps'
          : 'ps';
  const result = spawnSync(psBin, ['-axo', 'pid=,ppid=,command='], {
    encoding: 'utf8',
    env: childEnvironment,
  });
  if (result.error || result.status !== 0) {
    throw new Error(
      'could not inspect browser process evidence: ' +
        (result.error ? result.error.message : String(result.stderr || '').trim())
    );
  }
  const processes = parseProcessTable(result.stdout || '');
  const profileFlag = '--user-data-dir=' + profile;
  const matches = Array.from(processes.values()).filter(function(process) {
    return (
      (process.command === executablePath ||
        process.command.startsWith(executablePath + ' ')) &&
      process.command.split(' ').includes(profileFlag) &&
      isDescendantOf(process, daemonPid, processes)
    );
  });
  if (matches.length !== 1) {
    throw new Error(
      'browser process evidence must identify exactly one Chrome for Testing process ' +
        'owned by the daemon and bound to profile ' +
        profile
    );
  }
  return matches[0];
}

function defaultReceiptPath(browserHome, runId, app) {
  const receiptRoot = path.join(path.resolve(browserHome), 'ownership-receipts');
  ensureOwnedDirectory(receiptRoot);
  const runRoot = path.join(receiptRoot, runId);
  ensureOwnedDirectory(runRoot);
  return path.join(runRoot, app + '.json');
}

function defaultReceiptLocation(browserHome, runId, app) {
  return path.join(
    path.resolve(browserHome),
    'ownership-receipts',
    runId,
    app + '.json'
  );
}

function assertReceiptBinding(receipt, expected) {
  const fields = [
    ['run_id', expected.runId],
    ['app', expected.app],
    ['namespace', expected.namespace],
    ['session', expected.app],
    ['executable', expected.executablePath],
    ['profile', expected.profile],
    ['socket_dir', expected.socketDir],
    ['daemon_pid', expected.daemonPid],
    ['browser_pid', expected.browserPid],
  ];
  if (
    receipt.version !== 1 ||
    receipt.status !== 'active' ||
    receipt.initial_reused !== false
  ) {
    throw new Error('browser ownership receipt is not active or has an unsupported version');
  }
  for (const [field, value] of fields) {
    if (receipt[field] !== value) {
      throw new Error('browser ownership receipt does not match ' + field);
    }
  }
}

function verifyBrowserOwnership(options) {
  const infoResult = spawnSync(
    options.agentBrowser,
    [
      '--namespace',
      options.namespace,
      '--session',
      options.app,
      '--config',
      options.configPath,
      'session',
      'info',
      '--json',
    ],
    {
      encoding: 'utf8',
      env: options.childEnvironment,
    }
  );
  if (infoResult.error || infoResult.status !== 0) {
    throw new Error(
      'could not read agent-browser session ownership evidence: ' +
        (infoResult.error
          ? infoResult.error.message
          : String(infoResult.stderr || '').trim())
    );
  }
  const info = parseSessionInfo(infoResult.stdout || '');
  if (
    info.data.namespace !== options.namespace ||
    info.runtime.namespace !== options.namespace
  ) {
    throw new Error('browser ownership namespace does not match requested namespace');
  }
  if (info.data.session !== options.app || info.runtime.session !== options.app) {
    throw new Error('browser ownership session does not match requested app');
  }
  if (
    info.runtime.socketDir !== info.data.socketDir ||
    info.data.socketDir !== options.expectedSocketDir ||
    info.effectiveLaunch.engine !== 'chrome' ||
    info.effectiveLaunch.browserLaunched !== true
  ) {
    throw new Error('browser ownership runtime binding is incomplete or not Chrome');
  }
  const browserProcess = browserProcessEvidence(
    options.executablePath,
    options.profile,
    info.data.pid,
    options.childEnvironment
  );
  return {
    browserPid: browserProcess.pid,
    daemonPid: info.data.pid,
    reused: info.lifecycle.reused,
    socketDir: info.data.socketDir,
  };
}

function writeBrowserOwnershipReceipt(options, evidence, existingReceipt) {
  if (!existingReceipt && evidence.reused !== false) {
    throw new Error(
      'unexpected daemon reuse on first open; ownership requires reused=false'
    );
  }
  const binding = {
    runId: options.runId,
    app: options.app,
    namespace: options.namespace,
    executablePath: options.executablePath,
    profile: options.profile,
    socketDir: evidence.socketDir,
    daemonPid: evidence.daemonPid,
    browserPid: evidence.browserPid,
  };
  if (existingReceipt) {
    assertReceiptBinding(existingReceipt, binding);
  }
  const now = new Date().toISOString();
  const receipt = Object.assign({}, existingReceipt || {}, {
    version: 1,
    status: 'active',
    run_id: options.runId,
    app: options.app,
    namespace: options.namespace,
    session: options.app,
    executable: options.executablePath,
    profile: options.profile,
    socket_dir: evidence.socketDir,
    daemon_pid: evidence.daemonPid,
    browser_pid: evidence.browserPid,
    initial_reused: existingReceipt ? existingReceipt.initial_reused : false,
    last_reused: evidence.reused,
    verified_at: now,
  });
  if (!existingReceipt) receipt.created_at = now;
  writeJsonAtomic(options.receiptPath, receipt, false);
  return receipt;
}

function closeReceiptBinding(receipt, options) {
  assertReceiptBinding(receipt, {
    runId: options.runId,
    app: options.app,
    namespace: options.namespace,
    executablePath: receipt.executable,
    profile: receipt.profile,
    socketDir: receipt.socket_dir,
    daemonPid: receipt.daemon_pid,
    browserPid: receipt.browser_pid,
  });
  if (options.profile && path.resolve(options.profile) !== receipt.profile) {
    throw new Error('browser ownership receipt does not match profile');
  }
}

function sleepSync(milliseconds) {
  const signal = new Int32Array(new SharedArrayBuffer(4));
  Atomics.wait(signal, 0, 0, milliseconds);
}

function cleanupClosedNamespaceState(socketHome, namespace, app) {
  const namespaceRoot = path.join(path.resolve(socketHome), 'namespaces', namespace);
  const runRoot = path.join(namespaceRoot, 'run');
  const configPath = path.join(runRoot, app + '.config');
  const deadline = Date.now() + 2000;
  while (Date.now() < deadline) {
    if (fs.existsSync(configPath)) {
      const stat = fs.lstatSync(configPath);
      if (!stat.isFile() || stat.isSymbolicLink()) {
        throw new Error('owned browser session config is not a regular file');
      }
      fs.unlinkSync(configPath);
    }
    let runRemoved = false;
    try {
      fs.rmdirSync(runRoot);
      runRemoved = true;
    } catch (error) {
      if (error.code === 'ENOENT') return;
      if (error.code !== 'ENOTEMPTY') throw error;
    }
    if (runRemoved) {
      try {
        fs.rmdirSync(namespaceRoot);
      } catch (error) {
        if (error.code !== 'ENOENT' && error.code !== 'ENOTEMPTY') throw error;
      }
      return;
    }
    const entries = fs.readdirSync(runRoot);
    if (
      entries.some(function(entry) {
        return entry.endsWith('.config') && entry !== app + '.config';
      })
    ) {
      return;
    }
    sleepSync(40);
  }
  throw new Error('owned browser namespace did not settle after close');
}

function markBrowserOwnershipClosed(receiptPath, receipt) {
  if (!receipt) return;
  const closed = Object.assign({}, receipt, {
    status: 'closed',
    cleanup: 'owned-session-closed',
    closed_at: new Date().toISOString(),
  });
  writeJsonAtomic(receiptPath, closed, false);
}

function markBrowserOwnershipFailed(receiptPath, errorMessage, cleanup) {
  if (!receiptPath) return;
  const receipt = readRegularJson(receiptPath, 'browser ownership receipt');
  if (!receipt) return;
  const failed = Object.assign({}, receipt, {
    status: 'failed',
    cleanup,
    error: errorMessage,
    failed_at: new Date().toISOString(),
  });
  writeJsonAtomic(receiptPath, failed, false);
}

function readFlowManagedState(options) {
  const binding = assertFlowManagedBinding(options);
  const statePath = flowManagedStatePath(
    options.browserHome,
    options.runId,
    options.app,
    binding.profile
  );
  let state;
  try {
    state = JSON.parse(fs.readFileSync(statePath, 'utf8'));
  } catch (_error) {
    throw new Error('flow-managed lifecycle state is missing or invalid');
  }
  if (
    state.run_id !== options.runId ||
    state.app !== options.app ||
    state.profile !== binding.profile ||
    state.canonical_profile !== binding.canonicalProfile
  ) {
    throw new Error('flow-managed lifecycle state does not match run/app/profile binding');
  }
  return { binding, state, statePath };
}

function assertActiveFlowManagedBinding(options, binding) {
  const activeBindingPath = flowManagedActiveBindingPath(
    options.browserHome,
    options.runId,
    options.app
  );
  let active;
  try {
    const stat = fs.lstatSync(activeBindingPath);
    if (!stat.isFile() || stat.isSymbolicLink()) {
      throw new Error('active binding is not a regular file');
    }
    active = JSON.parse(fs.readFileSync(activeBindingPath, 'utf8'));
  } catch (_error) {
    throw new Error('flow-managed active binding is missing or invalid');
  }
  if (
    active.run_id !== options.runId ||
    active.app !== options.app ||
    active.profile !== binding.profile ||
    active.canonical_profile !== binding.canonicalProfile
  ) {
    throw new Error(
      'flow-managed profile binding is stale; a different profile is active'
    );
  }
  return activeBindingPath;
}

function assertNoActiveFlowManagedBinding(options) {
  const activeBindingPath = flowManagedActiveBindingPath(
    options.browserHome,
    options.runId,
    options.app
  );
  if (!fs.existsSync(activeBindingPath)) return;
  const stat = fs.lstatSync(activeBindingPath);
  if (!stat.isFile() || stat.isSymbolicLink()) {
    throw new Error('flow-managed active binding is invalid');
  }
  throw new Error(
    'another flow-managed profile is active; finish cleanup before activating a new replay'
  );
}

function prepareFlowManagedProfile(options) {
  assertRunAndApp(options.runId, options.app);
  assertCanonicalProfileRoot(options.canonicalProfile);
  ensureFlowManagedRoots(options.browserHome, options.runId, options.app);
  const replayId = options.replayId || crypto.randomBytes(8).toString('hex');
  const requestedProfile =
    options.profile ||
    flowManagedProfilePath(options.browserHome, options.runId, options.app, replayId);
  const binding = assertFlowManagedBinding(
    Object.assign({}, options, { profile: requestedProfile })
  );
  if (fs.existsSync(binding.profile)) {
    throw new Error('requested flow-managed profile already exists: ' + binding.profile);
  }
  const statePath = flowManagedStatePath(
    options.browserHome,
    options.runId,
    options.app,
    binding.profile
  );
  if (fs.existsSync(statePath)) {
    throw new Error('flow-managed lifecycle state already exists');
  }
  const state = {
    version: 1,
    status: 'prepared',
    run_id: options.runId,
    app: options.app,
    profile: binding.profile,
    canonical_profile: binding.canonicalProfile,
    canonical_digest: canonicalProfileDigest(binding.canonicalProfile),
    freshness: 'verified-absent',
    binding: 'pending',
    cleanup: 'pending',
    prepared_at: new Date().toISOString(),
  };
  writeJsonAtomic(statePath, state, true);
  return state;
}

function markFlowManagedProfileActive(options) {
  const record = readFlowManagedState(options);
  if (record.state.status !== 'prepared') {
    throw new Error('flow-managed profile must be prepared before browser launch');
  }
  assertNoActiveFlowManagedBinding(options);
  let profileStat;
  try {
    profileStat = fs.lstatSync(record.binding.profile);
  } catch (_error) {
    throw new Error('browser did not adopt requested profile: profile path is absent');
  }
  if (
    !profileStat.isDirectory() ||
    profileStat.isSymbolicLink() ||
    !fs.existsSync(path.join(record.binding.profile, 'Local State'))
  ) {
    throw new Error(
      'browser did not adopt requested profile: Chrome profile artifacts are missing'
    );
  }
  record.state.status = 'active';
  record.state.binding = 'verified';
  record.state.profile_device = String(profileStat.dev);
  record.state.profile_inode = String(profileStat.ino);
  record.state.activated_at = new Date().toISOString();
  writeJsonAtomic(
    flowManagedActiveBindingPath(
      options.browserHome,
      options.runId,
      options.app
    ),
    {
      version: 1,
      run_id: options.runId,
      app: options.app,
      profile: record.binding.profile,
      canonical_profile: record.binding.canonicalProfile,
      activated_at: record.state.activated_at,
    },
    true
  );
  writeJsonAtomic(record.statePath, record.state, false);
  return record.state;
}

function verifyFlowManagedProfile(options) {
  const record = readFlowManagedState(options);
  if (record.state.status !== 'active' || record.state.binding !== 'verified') {
    throw new Error('flow-managed profile is not active and binding-verified');
  }
  assertActiveFlowManagedBinding(options, record.binding);
  const profileStat = fs.lstatSync(record.binding.profile);
  if (
    !profileStat.isDirectory() ||
    profileStat.isSymbolicLink() ||
    !fs.existsSync(path.join(record.binding.profile, 'Local State')) ||
    String(profileStat.dev) !== record.state.profile_device ||
    String(profileStat.ino) !== record.state.profile_inode
  ) {
    throw new Error('flow-managed profile binding identity is no longer valid');
  }
  return record.state;
}

function cleanupFlowManagedProfile(options) {
  const record = readFlowManagedState(options);
  if (record.state.status !== 'active') {
    throw new Error('only an active flow-managed profile can be cleaned up');
  }
  const activeBindingPath = assertActiveFlowManagedBinding(options, record.binding);
  const currentCanonicalDigest = canonicalProfileDigest(record.binding.canonicalProfile);
  const canonicalUnchanged =
    currentCanonicalDigest === record.state.canonical_digest;
  const profileStat = fs.lstatSync(record.binding.profile);
  if (!profileStat.isDirectory() || profileStat.isSymbolicLink()) {
    throw new Error('refusing to remove a non-directory flow-managed profile');
  }
  if (
    String(profileStat.dev) !== record.state.profile_device ||
    String(profileStat.ino) !== record.state.profile_inode
  ) {
    throw new Error('flow-managed profile was replaced after binding');
  }
  fs.rmSync(record.binding.profile, { recursive: true, force: false });
  record.state.status = canonicalUnchanged ? 'cleaned' : 'cleaned-canonical-changed';
  record.state.cleanup = 'removed';
  record.state.canonical_profile = canonicalUnchanged ? 'unchanged' : 'changed';
  record.state.cleaned_at = new Date().toISOString();
  writeJsonAtomic(record.statePath, record.state, false);
  fs.unlinkSync(activeBindingPath);
  return record.state;
}

function discardFailedFlowManagedProfile(options, failureMessage) {
  const record = readFlowManagedState(options);
  if (record.state.status !== 'prepared') {
    throw new Error('only a prepared flow-managed profile can be discarded');
  }
  if (fs.existsSync(record.binding.profile)) {
    const profileStat = fs.lstatSync(record.binding.profile);
    if (!profileStat.isDirectory() || profileStat.isSymbolicLink()) {
      throw new Error('refusing to discard a non-directory flow-managed profile');
    }
    fs.rmSync(record.binding.profile, { recursive: true, force: false });
  }
  record.state.status = 'binding-failed';
  record.state.binding = 'failed';
  record.state.cleanup = 'removed';
  record.state.failure = failureMessage;
  record.state.failed_at = new Date().toISOString();
  writeJsonAtomic(record.statePath, record.state, false);
  return record.state;
}

function compareVersions(left, right) {
  const leftParts = left.split('.').map(Number);
  const rightParts = right.split('.').map(Number);
  const length = Math.max(leftParts.length, rightParts.length);
  for (let index = 0; index < length; index += 1) {
    const difference = (leftParts[index] || 0) - (rightParts[index] || 0);
    if (difference !== 0) return difference;
  }
  return 0;
}

function managedExecutableSuffixes() {
  const macExecutable = [
    'Google Chrome for Testing.app',
    'Contents',
    'MacOS',
    'Google Chrome for Testing',
  ];
  return [
    macExecutable,
    ['chrome-mac-arm64', ...macExecutable],
    ['chrome-mac-x64', ...macExecutable],
    ['chrome-linux64', 'chrome'],
    ['chrome-win64', 'chrome.exe'],
    ['chrome'],
    ['chrome.exe'],
  ];
}

function discoverChromeForTesting(browserHome) {
  const browsersDir = path.join(browserHome, 'browsers');
  let versions;
  try {
    versions = fs
      .readdirSync(browsersDir, { withFileTypes: true })
      .filter(function(entry) {
        return entry.isDirectory() && /^chrome-\d+(?:\.\d+)*$/.test(entry.name);
      })
      .map(function(entry) {
        return entry.name.slice('chrome-'.length);
      })
      .sort(compareVersions)
      .reverse();
  } catch (_error) {
    return '';
  }

  const suffixes = managedExecutableSuffixes();
  for (const version of versions) {
    for (const suffix of suffixes) {
      const candidate = path.join(browsersDir, 'chrome-' + version, ...suffix);
      try {
        fs.accessSync(candidate, fs.constants.X_OK);
        return candidate;
      } catch (_error) {
        // Continue to the next platform-specific candidate.
      }
    }
  }
  return '';
}

function isChromeForTestingExecutable(executablePath, browserHome) {
  let resolvedPath;
  let resolvedBrowserHome;
  try {
    resolvedPath = fs.realpathSync(executablePath);
    resolvedBrowserHome = fs.realpathSync(browserHome);
  } catch (_error) {
    return false;
  }

  const relativePath = path.relative(resolvedBrowserHome, resolvedPath);
  if (
    !relativePath ||
    relativePath.startsWith('..' + path.sep) ||
    path.isAbsolute(relativePath)
  ) {
    return false;
  }

  const parts = relativePath.split(path.sep);
  if (parts[0] !== 'browsers' || !/^chrome-\d+(?:\.\d+)*$/.test(parts[1] || '')) {
    return false;
  }
  return managedExecutableSuffixes().some(function(suffix) {
    return parts.length === suffix.length + 2 &&
      suffix.every(function(segment, index) {
        return parts[index + 2] === segment;
      });
  });
}

function protectedRuntimeArgument(command) {
  const protectedLongOptions = [
    '--namespace',
    '--session',
    '--config',
    '--engine',
    '--executable-path',
    '--provider',
    '--profile',
    '--headed',
    '--auto-connect',
    '--cdp',
    '--all',
  ];
  if (command[0] === 'connect') return 'connect';
  for (const value of command) {
    if (
      value === '-p' ||
      value.startsWith('-p=') ||
      /^-p[^-]/.test(value) ||
      protectedLongOptions.some(function(option) {
        return value === option || value.startsWith(option + '=');
      })
    ) {
      return value;
    }
  }
  return '';
}

function isAllowedCommand(command) {
  return ALLOWED_COMMANDS.has(command[0]);
}

function main(argv) {
  const options = parseArgs(argv);
  if (options.command[0] === 'new-run-id') {
    process.stdout.write(
      Date.now().toString(36) + '-' + crypto.randomBytes(10).toString('hex') + '\n'
    );
    return 0;
  }
  try {
    assertRunAndApp(options.runId, options.app);
  } catch (error) {
    process.stderr.write('e2e-browser-runtime: ' + error.message + '\n');
    return 2;
  }
  const browserHome =
    process.env.E2E_AGENT_BROWSER_HOME || path.join(os.homedir(), '.agent-browser');
  const socketHome = socketHomeForBrowserHome(browserHome);
  let namespace;
  try {
    ensureOwnedDirectory(socketHome);
    namespace = namespaceForRun(options.runId, socketHome);
  } catch (error) {
    process.stderr.write('e2e-browser-runtime: ' + error.message + '\n');
    return 2;
  }
  if (!['persistent', 'flow-managed'].includes(options.authMode)) {
    process.stderr.write(
      'e2e-browser-runtime: auth mode must be persistent or flow-managed\n'
    );
    return 2;
  }
  if (options.command[0] === 'prepare-flow-managed-profile') {
    if (options.authMode !== 'flow-managed') {
      process.stderr.write(
        'e2e-browser-runtime: prepare-flow-managed-profile requires --auth-mode flow-managed\n'
      );
      return 2;
    }
    try {
      const state = prepareFlowManagedProfile({
        browserHome,
        runId: options.runId,
        app: options.app,
        canonicalProfile: options.canonicalProfile,
        profile: options.profile,
      });
      process.stdout.write(JSON.stringify(state) + '\n');
      return 0;
    } catch (error) {
      process.stderr.write('e2e-browser-runtime: ' + error.message + '\n');
      return 2;
    }
  }
  if (options.command[0] === 'verify-flow-managed-profile') {
    if (options.authMode !== 'flow-managed') {
      process.stderr.write(
        'e2e-browser-runtime: verify-flow-managed-profile requires --auth-mode flow-managed\n'
      );
      return 2;
    }
    try {
      const state = verifyFlowManagedProfile({
        browserHome,
        runId: options.runId,
        app: options.app,
        canonicalProfile: options.canonicalProfile,
        profile: options.profile,
      });
      process.stdout.write(JSON.stringify(state) + '\n');
      return 0;
    } catch (error) {
      process.stderr.write('e2e-browser-runtime: ' + error.message + '\n');
      return 2;
    }
  }
  const prohibitedFlag = protectedRuntimeArgument(options.command);
  if (prohibitedFlag) {
    process.stderr.write(
      'e2e-browser-runtime: protected browser runtime option is prohibited: ' +
        prohibitedFlag +
        '\n'
    );
    return 2;
  }
  if (!isAllowedCommand(options.command)) {
    process.stderr.write(
      'e2e-browser-runtime: command is not allowed by the e2e-test runtime: ' +
        (options.command[0] || '(missing)') +
        '\n'
    );
    return 2;
  }
  const isFlowManagedCleanup =
    options.command[0] === 'cleanup-flow-managed-profile';
  if (isFlowManagedCleanup && options.authMode !== 'flow-managed') {
    process.stderr.write(
      'e2e-browser-runtime: cleanup-flow-managed-profile requires --auth-mode flow-managed\n'
    );
    return 2;
  }
  if (options.authMode === 'flow-managed') {
    if (!options.profile || !options.canonicalProfile) {
      process.stderr.write(
        'e2e-browser-runtime: flow-managed auth requires --profile and --canonical-profile\n'
      );
      return 2;
    }
    try {
      const record = readFlowManagedState({
        browserHome,
        runId: options.runId,
        app: options.app,
        canonicalProfile: options.canonicalProfile,
        profile: options.profile,
      });
      if (options.command[0] === 'open') {
        if (record.state.status !== 'prepared' || fs.existsSync(record.binding.profile)) {
          throw new Error(
            'flow-managed open requires a prepared, previously absent profile'
          );
        }
        assertNoActiveFlowManagedBinding({
          browserHome,
          runId: options.runId,
          app: options.app,
        });
      } else if (isFlowManagedCleanup) {
        verifyFlowManagedProfile({
          browserHome,
          runId: options.runId,
          app: options.app,
          canonicalProfile: options.canonicalProfile,
          profile: options.profile,
        });
      } else if (options.command[0] === 'close') {
        const activeBindingPath = flowManagedActiveBindingPath(
          browserHome,
          options.runId,
          options.app
        );
        if (fs.existsSync(activeBindingPath)) {
          assertActiveFlowManagedBinding(
            {
              browserHome,
              runId: options.runId,
              app: options.app,
            },
            record.binding
          );
        } else if (record.state.status !== 'prepared') {
          throw new Error(
            'flow-managed close requires the active binding or a prepared fresh profile'
          );
        }
      } else if (!isFlowManagedCleanup && options.command[0] !== 'close') {
        verifyFlowManagedProfile({
          browserHome,
          runId: options.runId,
          app: options.app,
          canonicalProfile: options.canonicalProfile,
          profile: options.profile,
        });
      }
    } catch (error) {
      process.stderr.write('e2e-browser-runtime: ' + error.message + '\n');
      return 2;
    }
  }
  const isOwnedClose = options.command[0] === 'close' || isFlowManagedCleanup;
  if (options.authMode === 'persistent') {
    const canonicalProfile = expectedCanonicalProfile(browserHome, options.app);
    if (options.profile && path.resolve(options.profile) !== canonicalProfile) {
      process.stderr.write(
        'e2e-browser-runtime: persistent profile must be the app profile at ' +
          canonicalProfile +
          '\n'
      );
      return 2;
    }
    try {
      options.profile = assertCanonicalProfileRoot(canonicalProfile);
    } catch (error) {
      process.stderr.write('e2e-browser-runtime: ' + error.message + '\n');
      return 2;
    }
  }
  options.executablePath =
    options.executablePath ||
    process.env.E2E_CHROME_FOR_TESTING_EXECUTABLE ||
    discoverChromeForTesting(browserHome);
  if (!isOwnedClose) {
    try {
      fs.accessSync(options.executablePath, fs.constants.X_OK);
    } catch (_error) {
      process.stderr.write(
        'e2e-browser-runtime: Chrome for Testing executable is unavailable: ' +
          options.executablePath +
          '\n'
      );
      return 2;
    }
    if (!isChromeForTestingExecutable(options.executablePath, browserHome)) {
      process.stderr.write(
        'e2e-browser-runtime: executable is not a Chrome for Testing installation: ' +
          options.executablePath +
          '\n'
      );
      return 2;
    }
  }
  const agentBrowser = process.env.E2E_AGENT_BROWSER_BIN || 'agent-browser';
  const configPath = path.join(__dirname, '..', 'references', 'agent-browser-runtime.json');
  const args = [
    '--namespace',
    namespace,
    '--session',
    options.app,
    '--config',
    configPath,
  ];
  if (!isOwnedClose) {
    args.push('--engine', 'chrome', '--executable-path', options.executablePath);
    if (options.profile) args.push('--profile', options.profile);
    if (options.headed) args.push('--headed');
  }
  args.push(...(isFlowManagedCleanup ? ['close'] : options.command));

  const childEnvironment = Object.assign({}, process.env, {
    AGENT_BROWSER_CONFIG: configPath,
  });
  delete childEnvironment.AGENT_BROWSER_AUTO_CONNECT;
  delete childEnvironment.AGENT_BROWSER_CDP;
  delete childEnvironment.AGENT_BROWSER_CDP_PORT;
  delete childEnvironment.AGENT_BROWSER_CDP_URL;
  delete childEnvironment.AGENT_BROWSER_ENGINE;
  delete childEnvironment.AGENT_BROWSER_EXECUTABLE_PATH;
  delete childEnvironment.AGENT_BROWSER_HEADED;
  delete childEnvironment.AGENT_BROWSER_NAMESPACE;
  delete childEnvironment.AGENT_BROWSER_PROFILE;
  delete childEnvironment.AGENT_BROWSER_PROVIDER;
  delete childEnvironment.AGENT_BROWSER_SESSION;
  childEnvironment.AGENT_BROWSER_SOCKET_DIR = socketHome;
  delete childEnvironment.CDP_PORT;
  delete childEnvironment.CDP_URL;
  delete childEnvironment.E2E_COMPILED_BROWSER_ALIAS;
  delete childEnvironment.E2E_PS_BIN;
  delete childEnvironment.E2E_RUNTIME_TEST_MODE;
  let receiptPath = '';
  let existingReceipt = null;
  if (options.command[0] === 'open') {
    try {
      receiptPath = options.receipt
        ? path.resolve(options.receipt)
        : defaultReceiptPath(browserHome, options.runId, options.app);
      existingReceipt = readRegularJson(receiptPath, 'browser ownership receipt');
    } catch (error) {
      process.stderr.write('e2e-browser-runtime: ' + error.message + '\n');
      return 2;
    }
  } else if (isOwnedClose) {
    try {
      receiptPath = options.receipt
        ? path.resolve(options.receipt)
        : defaultReceiptLocation(browserHome, options.runId, options.app);
      existingReceipt = readRegularJson(receiptPath, 'browser ownership receipt');
      if (options.receipt && !existingReceipt) {
        throw new Error('browser ownership receipt is unavailable: ' + receiptPath);
      }
      if (existingReceipt) {
        closeReceiptBinding(existingReceipt, {
          app: options.app,
          namespace,
          profile: options.profile,
          runId: options.runId,
        });
      }
    } catch (error) {
      process.stderr.write('e2e-browser-runtime: ' + error.message + '\n');
      return 2;
    }
  } else if (options.receipt && options.command[0] !== '--version') {
    try {
      receiptPath = path.resolve(options.receipt);
      existingReceipt = readRegularJson(receiptPath, 'browser ownership receipt');
      if (!existingReceipt) {
        throw new Error('browser ownership receipt is unavailable: ' + receiptPath);
      }
      assertReceiptBinding(existingReceipt, {
        app: options.app,
        browserPid: existingReceipt.browser_pid,
        daemonPid: existingReceipt.daemon_pid,
        executablePath: options.executablePath,
        namespace,
        profile: path.resolve(options.profile),
        runId: options.runId,
        socketDir: path.join(socketHome, 'namespaces', namespace, 'run'),
      });
      const liveEvidence = verifyBrowserOwnership({
        agentBrowser,
        app: options.app,
        browserHome,
        childEnvironment,
        configPath,
        executablePath: options.executablePath,
        expectedSocketDir: path.join(socketHome, 'namespaces', namespace, 'run'),
        namespace,
        profile: path.resolve(options.profile),
        runId: options.runId,
      });
      assertReceiptBinding(existingReceipt, {
        app: options.app,
        browserPid: liveEvidence.browserPid,
        daemonPid: liveEvidence.daemonPid,
        executablePath: options.executablePath,
        namespace,
        profile: path.resolve(options.profile),
        runId: options.runId,
        socketDir: liveEvidence.socketDir,
      });
    } catch (error) {
      process.stderr.write('e2e-browser-runtime: ' + error.message + '\n');
      return 2;
    }
  }
  const result = spawnSync(agentBrowser, args, {
    env: childEnvironment,
    stdio: 'inherit',
  });
  if (result.error) {
    process.stderr.write('e2e-browser-runtime: ' + result.error.message + '\n');
    return 1;
  }
  const childStatus = result.status === null ? 1 : result.status;
  if (childStatus !== 0) return childStatus;
  if (options.command[0] === 'open') {
    try {
      const evidence = verifyBrowserOwnership({
        agentBrowser,
        app: options.app,
        browserHome,
        childEnvironment,
        configPath,
        executablePath: options.executablePath,
        expectedSocketDir: path.join(socketHome, 'namespaces', namespace, 'run'),
        namespace,
        profile: path.resolve(options.profile),
        runId: options.runId,
      });
      writeBrowserOwnershipReceipt(
        {
          app: options.app,
          executablePath: options.executablePath,
          namespace,
          profile: path.resolve(options.profile),
          receiptPath,
          runId: options.runId,
        },
        evidence,
        existingReceipt
      );
      if (options.authMode === 'flow-managed') {
        markFlowManagedProfileActive({
          browserHome,
          runId: options.runId,
          app: options.app,
          canonicalProfile: options.canonicalProfile,
          profile: options.profile,
        });
      }
    } catch (error) {
      const closeResult = spawnSync(
        agentBrowser,
        [
          '--namespace',
          namespace,
          '--session',
          options.app,
          '--config',
          configPath,
          'close',
        ],
        {
          env: childEnvironment,
          stdio: 'ignore',
        }
      );
      let ownershipCleanup =
        closeResult.error || closeResult.status !== 0
          ? 'owned-session-close-failed-after-binding-failure'
          : 'owned-session-closed-after-binding-failure';
      try {
        cleanupClosedNamespaceState(socketHome, namespace, options.app);
      } catch (namespaceCleanupError) {
        ownershipCleanup = 'owned-session-state-cleanup-failed-after-binding-failure';
        process.stderr.write(
          'e2e-browser-runtime: binding-failure namespace cleanup failed: ' +
            namespaceCleanupError.message +
            '\n'
        );
      }
      try {
        markBrowserOwnershipFailed(receiptPath, error.message, ownershipCleanup);
      } catch (receiptError) {
        process.stderr.write(
          'e2e-browser-runtime: binding-failure receipt update failed: ' +
            receiptError.message +
            '\n'
        );
      }
      if (options.authMode === 'flow-managed') {
        try {
          discardFailedFlowManagedProfile(
            {
              browserHome,
              runId: options.runId,
              app: options.app,
              canonicalProfile: options.canonicalProfile,
              profile: options.profile,
            },
            error.message
          );
        } catch (cleanupError) {
          process.stderr.write(
            'e2e-browser-runtime: binding-failure cleanup failed: ' +
              cleanupError.message +
              '\n'
          );
        }
      }
      process.stderr.write('e2e-browser-runtime: ' + error.message + '\n');
      return 2;
    }
  }
  if (isOwnedClose) {
    try {
      cleanupClosedNamespaceState(socketHome, namespace, options.app);
      markBrowserOwnershipClosed(receiptPath, existingReceipt);
    } catch (error) {
      process.stderr.write(
        'e2e-browser-runtime: owned browser cleanup evidence failed: ' +
          error.message +
          '\n'
      );
      return 2;
    }
  }
  if (isFlowManagedCleanup) {
    try {
      const state = cleanupFlowManagedProfile({
        browserHome,
        runId: options.runId,
        app: options.app,
        canonicalProfile: options.canonicalProfile,
        profile: options.profile,
      });
      process.stdout.write(JSON.stringify(state) + '\n');
      return state.canonical_profile === 'unchanged' ? 0 : 2;
    } catch (error) {
      process.stderr.write('e2e-browser-runtime: ' + error.message + '\n');
      return 2;
    }
  }
  return 0;
}

if (require.main === module) {
  process.exitCode = main(process.argv.slice(2));
}

module.exports = {
  canonicalProfileDigest,
  cleanupFlowManagedProfile,
  compareVersions,
  discardFailedFlowManagedProfile,
  discoverChromeForTesting,
  flowManagedProfilePath,
  isChromeForTestingExecutable,
  isAllowedCommand,
  managedExecutableSuffixes,
  main,
  markFlowManagedProfileActive,
  namespaceForRun,
  parseArgs,
  prepareFlowManagedProfile,
  protectedRuntimeArgument,
  socketHomeForBrowserHome,
  verifyFlowManagedProfile,
};
