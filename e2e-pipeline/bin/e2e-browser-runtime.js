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
  'cookies',
  'diagnostic-projection',
  'errors',
  'eval',
  'fill',
  'find',
  'get',
  'hover',
  'is',
  'network',
  'open',
  'press',
  'reload',
  'screenshot',
  'scroll',
  'select',
  'snapshot',
  'storage',
  'tab',
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
    diagnosticInitScripts: [],
    profileLivenessKeys: [],
    profileLivenessSelectors: [],
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
    } else if (value === '--diagnostic-init-script') {
      options.diagnosticInitScripts.push(argv[++index] || '');
    } else if (value === '--profile-liveness-key') {
      options.profileLivenessKeys.push(argv[++index] || '');
    } else if (value === '--profile-liveness-selector') {
      options.profileLivenessSelectors.push(argv[++index] || '');
    } else if (value === '--headed') {
      options.headed = true;
    } else {
      options.command = argv.slice(index);
      break;
    }
  }

  return options;
}

function validateDiagnosticInitScript(filePath, expectedUid) {
  if (!path.isAbsolute(filePath)) {
    throw new Error(
      'diagnostic init script path must be absolute: ' + (filePath || '(missing)')
    );
  }
  const resolvedPath = path.resolve(filePath);
  let pathStat;
  try {
    pathStat = fs.lstatSync(resolvedPath);
  } catch (_error) {
    throw new Error(
      'diagnostic init script must be an existing regular file: ' + resolvedPath
    );
  }
  if (pathStat.isSymbolicLink()) {
    throw new Error('diagnostic init script must not be a symlink: ' + resolvedPath);
  }
  if (!pathStat.isFile()) {
    throw new Error('diagnostic init script must be a regular file: ' + resolvedPath);
  }
  const runtimeUid =
    expectedUid === undefined && typeof process.getuid === 'function'
      ? process.getuid()
      : expectedUid;
  if (runtimeUid === undefined || pathStat.uid !== runtimeUid) {
    throw new Error(
      'diagnostic init script must be owned by the current user: ' + resolvedPath
    );
  }

  const noFollow = fs.constants.O_NOFOLLOW || 0;
  let descriptor;
  try {
    descriptor = fs.openSync(resolvedPath, fs.constants.O_RDONLY | noFollow);
    const descriptorStat = fs.fstatSync(descriptor);
    if (
      !descriptorStat.isFile() ||
      descriptorStat.uid !== runtimeUid ||
      String(descriptorStat.dev) !== String(pathStat.dev) ||
      String(descriptorStat.ino) !== String(pathStat.ino)
    ) {
      throw new Error('diagnostic init script identity changed during validation');
    }
    const contents = fs.readFileSync(descriptor);
    return {
      sourcePath: resolvedPath,
      basename: path.basename(resolvedPath),
      pathSha256: crypto
        .createHash('sha256')
        .update(resolvedPath)
        .digest('hex'),
      contentSha256: crypto
        .createHash('sha256')
        .update(contents)
        .digest('hex'),
      byteLength: contents.length,
      device: String(descriptorStat.dev),
      inode: String(descriptorStat.ino),
      uid: descriptorStat.uid,
      contents,
    };
  } catch (error) {
    if (error.message.startsWith('diagnostic init script')) throw error;
    throw new Error(
      'diagnostic init script is unreadable: ' +
        resolvedPath +
        ' (' +
        error.message +
        ')'
    );
  } finally {
    if (descriptor !== undefined) fs.closeSync(descriptor);
  }
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

// agent-browser names the daemon socket after the session, not a fixed filename:
// <socketHome>/namespaces/<namespace>/run/<session>.sock. Sizing the namespace against
// a fixed name under-counts by len(session) + 5 - len('daemon.sock'), and agent-browser
// then refuses a bind the runtime has already declared socket-safe.
function namespaceForRun(runId, socketHome, sessionName) {
  if (!sessionName) {
    throw new Error('a session name is required to size a socket-safe e2e namespace');
  }
  const socketFile = sessionName + '.sock';
  const readable = 'e2e-' + runId;
  if (
    Buffer.byteLength(
      path.join(path.resolve(socketHome), 'namespaces', readable, 'run', socketFile)
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
    socketFile
  );
  const available = 103 - Buffer.byteLength(oneCharacterPath) + 1;
  const fixedLength = Buffer.byteLength('e2e--' + digest);
  if (available < Buffer.byteLength('e2e-a-' + digest)) {
    throw new Error(
      'agent-browser home and session name leave no socket-safe e2e namespace: ' +
        path.resolve(socketHome) +
        ' with session ' +
        sessionName
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

function profileFlagFromCommand(command) {
  const match = command.match(
    /(?:^|\s)--user-data-dir=(?:"([^"]+)"|'([^']+)'|(\S+))/
  );
  return match ? match[1] || match[2] || match[3] || '' : '';
}

function structuralProfileManifest(profileRoot) {
  const manifest = new Map();
  const ignoredNames = new Set([
    'DevToolsActivePort',
    'LOCK',
    'LOG',
    'SingletonCookie',
    'SingletonLock',
    'SingletonSocket',
  ]);
  let visited = 0;

  function visit(currentPath, relativePath) {
    if (visited >= 10000) return;
    const stat = fs.lstatSync(currentPath);
    if (stat.isSymbolicLink()) return;
    const name = path.basename(currentPath);
    if (
      ignoredNames.has(name) ||
      name.endsWith('-journal') ||
      name.endsWith('-shm') ||
      name.endsWith('-wal')
    ) {
      return;
    }
    visited += 1;
    if (stat.isFile()) {
      manifest.set(relativePath, {
        mode: stat.mode & 0o777,
        size: stat.size,
      });
      return;
    }
    if (!stat.isDirectory()) return;
    for (const entry of fs.readdirSync(currentPath).sort()) {
      visit(path.join(currentPath, entry), path.join(relativePath, entry));
    }
  }

  visit(profileRoot, '.');
  return manifest;
}

function structuralProfileProof(sourceProfile, actualProfile) {
  const sourceManifest = structuralProfileManifest(sourceProfile);
  const actualManifest = structuralProfileManifest(actualProfile);
  const matches = [];
  let matchedBytes = 0;
  for (const [relativePath, source] of sourceManifest) {
    const actual = actualManifest.get(relativePath);
    if (
      !actual ||
      actual.size !== source.size ||
      actual.mode !== source.mode
    ) {
      continue;
    }
    matches.push(
      relativePath + '\0' + source.size + '\0' + source.mode.toString(8)
    );
    matchedBytes += source.size;
  }
  matches.sort();
  if (matches.length < 3 || matchedBytes < 1024) {
    throw new Error(
      'browser profile snapshot does not share enough structural evidence with its canonical source'
    );
  }
  return {
    digest: crypto
      .createHash('sha256')
      .update(matches.join('\n'))
      .digest('hex'),
    matchedBytes,
    matchedEntries: matches.length,
  };
}

function validateProfileLineage(actualProfile, requestedProfile, lineage) {
  const resolvedActual = path.resolve(actualProfile);
  const resolvedRequested = path.resolve(requestedProfile);
  if (
    resolvedActual === resolvedRequested &&
    !fs.existsSync(resolvedActual) &&
    process.env.E2E_RUNTIME_TEST_MODE === '1'
  ) {
    return {
      actualProfile: resolvedActual,
      actualProfileDevice: null,
      actualProfileInode: null,
      actualProfileMode: null,
      actualProfileUid: null,
      profileMode: 'persistent-path',
      tempRootMode: null,
      lineage: 'exact-path',
    };
  }
  const actualStat = fs.lstatSync(resolvedActual);
  if (!actualStat.isDirectory() || actualStat.isSymbolicLink()) {
    throw new Error('actual browser profile must be a non-symlink directory');
  }
  const uid = typeof process.getuid === 'function' ? process.getuid() : actualStat.uid;
  if (actualStat.uid !== uid) {
    throw new Error('actual browser profile owner does not match the runtime user');
  }
  if (resolvedActual === resolvedRequested) {
    return {
      actualProfile: resolvedActual,
      actualProfileDevice: String(actualStat.dev),
      actualProfileInode: String(actualStat.ino),
      actualProfileMode: actualStat.mode & 0o777,
      actualProfileUid: actualStat.uid,
      profileMode: 'persistent-path',
      tempRootMode: null,
      lineage: 'exact-path',
    };
  }
  if (!lineage) {
    throw new Error(
      'browser process used a profile snapshot without runtime lineage evidence'
    );
  }
  const temporaryRoot = fs.realpathSync(os.tmpdir());
  const realActual = fs.realpathSync(resolvedActual);
  const relative = path.relative(temporaryRoot, realActual);
  if (
    !relative ||
    relative.startsWith('..' + path.sep) ||
    path.isAbsolute(relative) ||
    relative.includes(path.sep) ||
    !/^agent-browser-chrome-[a-f0-9-]{16,}$/i.test(relative)
  ) {
    throw new Error(
      'actual browser profile snapshot is outside the owned OS temp root'
    );
  }
  const tempRootStat = fs.lstatSync(temporaryRoot);
  const tempRootMode = tempRootStat.mode & 0o777;
  if (tempRootStat.uid !== uid) {
    throw new Error('OS temp root owner does not match the runtime user');
  }
  if ((tempRootMode & 0o077) !== 0 && (actualStat.mode & 0o077) !== 0) {
    throw new Error(
      'browser profile snapshot is readable outside the runtime user'
    );
  }
  if (
    lineage.actualProfile &&
    path.resolve(lineage.actualProfile) === realActual
  ) {
    if (
      String(actualStat.dev) !== String(lineage.actualProfileDevice) ||
      String(actualStat.ino) !== String(lineage.actualProfileInode)
    ) {
      throw new Error('browser profile snapshot identity changed');
    }
    return {
      actualProfile: realActual,
      actualProfileDevice: String(actualStat.dev),
      actualProfileInode: String(actualStat.ino),
      actualProfileMode: actualStat.mode & 0o777,
      actualProfileUid: actualStat.uid,
      profileMode: 'verified-snapshot',
      tempRootMode,
      lineage: 'structural-metadata',
      structuralDigest: lineage.structuralDigest,
      structuralMatchedBytes: lineage.structuralMatchedBytes,
      structuralMatchedEntries: lineage.structuralMatchedEntries,
    };
  }
  if (
    Number.isFinite(lineage.launchStartedAt) &&
    actualStat.birthtimeMs + 2000 < lineage.launchStartedAt
  ) {
    throw new Error('browser profile snapshot predates this owned launch');
  }
  const structural = structuralProfileProof(resolvedRequested, realActual);
  return {
    actualProfile: realActual,
    actualProfileDevice: String(actualStat.dev),
    actualProfileInode: String(actualStat.ino),
    actualProfileMode: actualStat.mode & 0o777,
    actualProfileUid: actualStat.uid,
    profileMode: 'verified-snapshot',
    tempRootMode,
    lineage: 'structural-metadata',
    structuralDigest: structural.digest,
    structuralMatchedBytes: structural.matchedBytes,
    structuralMatchedEntries: structural.matchedEntries,
  };
}

function prepareProfileLineage(profile, runId, app, receiptPath) {
  const resolvedProfile = path.resolve(profile);
  if (!fs.existsSync(resolvedProfile)) {
    ensureOwnedDirectory(path.dirname(resolvedProfile));
    fs.mkdirSync(resolvedProfile);
  }
  const profileStat = fs.lstatSync(resolvedProfile);
  const uid = typeof process.getuid === 'function' ? process.getuid() : profileStat.uid;
  if (
    !profileStat.isDirectory() ||
    profileStat.isSymbolicLink() ||
    profileStat.uid !== uid
  ) {
    throw new Error('canonical profile is not an owned non-symlink directory');
  }
  return {
    launchStartedAt: Date.now(),
    sourceBinding: crypto
      .createHash('sha256')
      .update(
        runId +
          '\0' +
          app +
          '\0' +
          path.resolve(receiptPath) +
          '\0' +
          resolvedProfile +
          '\0' +
          String(profileStat.dev) +
          '\0' +
          String(profileStat.ino)
      )
      .digest('hex'),
    sourceDevice: String(profileStat.dev),
    sourceInode: String(profileStat.ino),
    sourceProfile: resolvedProfile,
  };
}

function browserProcessEvidence(
  executablePath,
  profile,
  daemonPid,
  childEnvironment,
  lineage
) {
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
  const matches = Array.from(processes.values()).filter(function(process) {
    return (
      (process.command === executablePath ||
        process.command.startsWith(executablePath + ' ')) &&
      Boolean(profileFlagFromCommand(process.command)) &&
      isDescendantOf(process, daemonPid, processes)
    );
  });
  if (matches.length !== 1) {
    throw new Error(
      'browser process evidence must identify exactly one Chrome for Testing process ' +
        'owned by the daemon'
    );
  }
  const profileEvidence = validateProfileLineage(
    profileFlagFromCommand(matches[0].command),
    profile,
    lineage
  );
  return Object.assign({}, matches[0], profileEvidence);
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
    options.childEnvironment,
    options.lineage
  );
  return {
    actualProfile: browserProcess.actualProfile,
    actualProfileDevice: browserProcess.actualProfileDevice,
    actualProfileInode: browserProcess.actualProfileInode,
    actualProfileMode: browserProcess.actualProfileMode,
    actualProfileUid: browserProcess.actualProfileUid,
    browserPid: browserProcess.pid,
    daemonPid: info.data.pid,
    launchHash: info.effectiveLaunch.launchHash,
    lineage: browserProcess.lineage,
    pageCount: info.runtime.pageCount,
    profileMode: browserProcess.profileMode,
    reused: info.lifecycle.reused,
    socketDir: info.data.socketDir,
    structuralDigest: browserProcess.structuralDigest,
    structuralMatchedBytes: browserProcess.structuralMatchedBytes,
    structuralMatchedEntries: browserProcess.structuralMatchedEntries,
    tempRootMode: browserProcess.tempRootMode,
  };
}

function runAgentBrowser(options, command) {
  const result = spawnSync(
    options.agentBrowser,
    [
      '--namespace',
      options.namespace,
      '--session',
      options.app,
      '--config',
      options.configPath,
      ...command,
    ],
    {
      encoding: 'utf8',
      env: options.childEnvironment,
    }
  );
  if (result.error || result.status !== 0) {
    throw new Error(
      'agent-browser lifecycle command failed (' +
        command.slice(0, 2).join(' ') +
        '): ' +
        (result.error
          ? result.error.message
          : String(result.stderr || result.stdout || '').trim())
    );
  }
  return String(result.stdout || '');
}

function agentBrowserLifecycleVersion(agentBrowser, childEnvironment) {
  const result = spawnSync(agentBrowser, ['--version'], {
    encoding: 'utf8',
    env: childEnvironment,
  });
  if (result.error || result.status !== 0) return '';
  const match = String(result.stdout || '').match(
    /agent-browser\s+(\d+(?:\.\d+){1,3})/
  );
  return match ? match[1] : '';
}

function parseAgentBrowserPayload(stdout, description) {
  let payload;
  try {
    payload = JSON.parse(stdout);
  } catch (_error) {
    throw new Error(description + ' is not valid JSON');
  }
  if (!payload || payload.success !== true || !payload.data) {
    throw new Error(description + ' is incomplete');
  }
  return payload.data;
}

function activePageIdentity(options) {
  const data = parseAgentBrowserPayload(
    runAgentBrowser(options, ['tab', 'list', '--json']),
    'agent-browser active page evidence'
  );
  const activePages = (data.tabs || []).filter(function(tab) {
    return tab && tab.active === true && tab.type === 'page';
  });
  if (
    activePages.length !== 1 ||
    typeof activePages[0].tabId !== 'string' ||
    !activePages[0].tabId
  ) {
    throw new Error(
      'agent-browser active page evidence must identify exactly one page'
    );
  }
  return {
    pageIdentity: activePages[0].tabId,
    url: String(activePages[0].url || ''),
  };
}

function captureNavigationEvidence(options) {
  const ownership = verifyBrowserOwnership(options);
  const page = activePageIdentity(options);
  return {
    namespace: options.namespace,
    session: options.app,
    daemon_pid: ownership.daemonPid,
    browser_pid: ownership.browserPid,
    page_identity: page.pageIdentity,
    actual_profile: ownership.actualProfile,
    actual_profile_device: ownership.actualProfileDevice,
    actual_profile_inode: ownership.actualProfileInode,
    actual_profile_mode: ownership.actualProfileMode,
    actual_profile_uid: ownership.actualProfileUid,
    profile_mode: ownership.profileMode,
    profile_lineage: ownership.lineage,
    structural_digest: ownership.structuralDigest || null,
    structural_matched_bytes: ownership.structuralMatchedBytes || null,
    structural_matched_entries: ownership.structuralMatchedEntries || null,
    temp_root_mode: ownership.tempRootMode,
    url: page.url,
    page_count: ownership.pageCount,
    launch_hash: ownership.launchHash,
    reused: ownership.reused,
    recorder: {
      init_script: options.initStatus || 'not-checked',
      har: options.harStatus || 'not-started',
    },
    captured_at: new Date().toISOString(),
  };
}

function assertStableNavigationIdentity(pre, post) {
  const identities = [
    ['namespace', 'namespace'],
    ['session', 'session'],
    ['daemon_pid', 'daemon'],
    ['browser_pid', 'browser'],
    ['page_identity', 'page identity'],
    ['actual_profile', 'actual profile'],
  ];
  for (const [field, label] of identities) {
    if (pre[field] !== post[field]) {
      throw new Error(
        'browser lifecycle infrastructure failure: ' +
          label +
          ' changed across navigation'
      );
    }
  }
}

function removePrivateLifecycleFile(filePath) {
  if (!filePath || !fs.existsSync(filePath)) return;
  const stat = fs.lstatSync(filePath);
  if (!stat.isFile() || stat.isSymbolicLink()) {
    throw new Error('refusing to remove non-regular lifecycle file: ' + filePath);
  }
  fs.unlinkSync(filePath);
}

function firstNavigationFiles(receiptPath) {
  const digest = crypto
    .createHash('sha256')
    .update(path.resolve(receiptPath))
    .digest('hex')
    .slice(0, 16);
  return {
    harPath: receiptPath + '.first-navigation-' + digest + '.har',
    initPath: receiptPath + '.first-navigation-' + digest + '.js',
  };
}

function diagnosticManifestPath(receiptPath) {
  return receiptPath + '.diagnostic-manifest.json';
}

function diagnosticWrapperPath(receiptPath, index, pathSha256) {
  return (
    receiptPath +
    '.diagnostic-' +
    index +
    '-' +
    pathSha256.slice(0, 12) +
    '.js'
  );
}

function diagnosticPublicProvenance(script, index, status) {
  return {
    index,
    basename: script.basename,
    byte_length:
      script.byte_length === undefined ? script.byteLength : script.byte_length,
    content_sha256: script.content_sha256 || script.contentSha256,
    path_sha256: script.path_sha256 || script.pathSha256,
    marker_key: script.marker_key,
    projection_key: script.projection_key,
    status,
  };
}

function diagnosticWrapperContents(script, markerKey, projectionKey) {
  return [
    '(function() {',
    "  'use strict';",
    '  var published = false;',
    '  var projectionSchema = null;',
    '  var projectionReader = null;',
    '  function isPlainObject(value) {',
    "    return value !== null && typeof value === 'object' && !Array.isArray(value);",
    '  }',
    '  function validateSchema(schema) {',
    "    if (!isPlainObject(schema)) throw new Error('diagnostic projection schema must be an object');",
    '    var keys = Object.keys(schema);',
    "    if (keys.length < 1 || keys.length > 32) throw new Error('diagnostic projection schema must have 1 to 32 fields');",
    '    keys.forEach(function(key) {',
    "      if (!/^[a-z][a-z0-9_]{0,63}$/.test(key)) throw new Error('diagnostic projection field name is invalid');",
    '      var descriptor = schema[key];',
    "      if (!isPlainObject(descriptor)) throw new Error('diagnostic projection field descriptor is invalid');",
    "      if (descriptor.type === 'boolean' || descriptor.type === 'sha256') return;",
    "      if (descriptor.type === 'integer') {",
    '        if (!Number.isSafeInteger(descriptor.min) || !Number.isSafeInteger(descriptor.max) || descriptor.min > descriptor.max) {',
    "          throw new Error('diagnostic projection integer field must have safe min and max bounds');",
    '        }',
    '        return;',
    '      }',
    "      if (descriptor.type === 'enum') {",
    '        if (!Array.isArray(descriptor.values) || descriptor.values.length < 1 || descriptor.values.length > 32 || descriptor.values.some(function(value) { return typeof value !== \'string\' || value.length < 1 || value.length > 64; })) {',
    "          throw new Error('diagnostic projection enum field must have 1 to 32 bounded string values');",
    '        }',
    '        return;',
    '      }',
    "      throw new Error('diagnostic projection field type is not allowed');",
    '    });',
    '  }',
    '  function projectValues(schema, values) {',
    "    if (!isPlainObject(values)) throw new Error('diagnostic projection reader must return an object');",
    '    var keys = Object.keys(schema);',
    '    var projected = {};',
    '    keys.forEach(function(key) {',
    '      projected[key] = values[key];',
    '    });',
    '    return projected;',
    '  }',
    '  (function(publishDiagnosticProjection) {',
    script.contents.toString('utf8'),
    '  })(function(schema, reader) {',
    "    if (published) throw new Error('diagnostic projection may only be published once');",
    '    validateSchema(schema);',
    "    if (typeof reader !== 'function') throw new Error('diagnostic projection reader must be a function');",
    '    published = true;',
    '    projectionSchema = schema;',
    '    projectionReader = reader;',
    '  });',
    "  if (!published) throw new Error('diagnostic projection was not published');",
    '  Object.defineProperty(globalThis, ' + JSON.stringify(markerKey) + ", { configurable: false, value: true });",
    '  Object.defineProperty(globalThis, ' + JSON.stringify(projectionKey) + ', {',
    '    configurable: false,',
    '    value: function() {',
    '      return { schema: projectionSchema, values: projectValues(projectionSchema, projectionReader()) };',
    '    }',
    '  });',
    '})();',
    '',
  ].join('\n');
}

function prepareDiagnosticLifecycle(receiptPath, scripts) {
  if (!scripts.length) return null;
  ensureOwnedDirectory(path.dirname(receiptPath));
  const prepared = [];
  try {
    scripts.forEach(function(script, index) {
      const wrapperPath = diagnosticWrapperPath(
        receiptPath,
        index,
        script.pathSha256
      );
      const markerKey =
        '__E2E_DIAGNOSTIC_MARKER_' +
        crypto.randomBytes(12).toString('hex').toUpperCase();
      const projectionKey =
        '__E2E_DIAGNOSTIC_PROJECTION_' +
        crypto.randomBytes(12).toString('hex').toUpperCase();
      const wrapperContents = diagnosticWrapperContents(
        script,
        markerKey,
        projectionKey
      );
      fs.writeFileSync(wrapperPath, wrapperContents, {
        flag: 'wx',
        mode: 0o600,
      });
      prepared.push({
        index,
        source_path: script.sourcePath,
        basename: script.basename,
        byte_length: script.byteLength,
        content_sha256: script.contentSha256,
        path_sha256: script.pathSha256,
        device: script.device,
        inode: script.inode,
        uid: script.uid,
        marker_key: markerKey,
        projection_key: projectionKey,
        wrapper_path: wrapperPath,
        wrapper_sha256: crypto
          .createHash('sha256')
          .update(wrapperContents)
          .digest('hex'),
      });
    });
    const manifest = {
      version: 1,
      status: 'pending',
      receipt_path_sha256: crypto
        .createHash('sha256')
        .update(path.resolve(receiptPath))
        .digest('hex'),
      scripts: prepared,
    };
    writeJsonAtomic(diagnosticManifestPath(receiptPath), manifest, true);
    return manifest;
  } catch (error) {
    for (const preparedScript of prepared) {
      removePrivateLifecycleFile(preparedScript.wrapper_path);
    }
    throw error;
  }
}

function readDiagnosticManifest(receiptPath) {
  const manifest = readRegularJson(
    diagnosticManifestPath(receiptPath),
    'diagnostic init-script manifest'
  );
  if (
    !manifest ||
    manifest.version !== 1 ||
    manifest.status !== 'pending' ||
    manifest.receipt_path_sha256 !==
      crypto
        .createHash('sha256')
        .update(path.resolve(receiptPath))
        .digest('hex') ||
    !Array.isArray(manifest.scripts)
  ) {
    throw new Error('diagnostic init-script manifest is unavailable or invalid');
  }
  return manifest;
}

function validateDiagnosticWrapper(script) {
  let stat;
  try {
    stat = fs.lstatSync(script.wrapper_path);
  } catch (_error) {
    throw new Error(
      'diagnostic wrapper ' + script.index + ' must be a regular file'
    );
  }
  if (!stat.isFile() || stat.isSymbolicLink()) {
    throw new Error(
      'diagnostic wrapper ' + script.index + ' must be a regular non-symlink file'
    );
  }
  const digest = crypto
    .createHash('sha256')
    .update(fs.readFileSync(script.wrapper_path))
    .digest('hex');
  if (digest !== script.wrapper_sha256) {
    throw new Error('diagnostic wrapper ' + script.index + ' content changed');
  }
}

function revalidateDiagnosticLifecycle(receiptPath, suppliedScripts) {
  const manifest = readDiagnosticManifest(receiptPath);
  if (manifest.scripts.length !== suppliedScripts.length) {
    throw new Error('diagnostic init-script input count changed');
  }
  manifest.scripts.forEach(function(recorded, index) {
    const supplied = suppliedScripts[index];
    if (
      supplied.pathSha256 !== recorded.path_sha256 ||
      supplied.basename !== recorded.basename
    ) {
      throw new Error('diagnostic init script ' + index + ' path changed');
    }
    if (
      supplied.contentSha256 !== recorded.content_sha256 ||
      supplied.byteLength !== recorded.byte_length
    ) {
      throw new Error('diagnostic init script ' + index + ' content changed');
    }
    if (
      supplied.device !== recorded.device ||
      supplied.inode !== recorded.inode ||
      supplied.uid !== recorded.uid
    ) {
      throw new Error('diagnostic init script ' + index + ' identity changed');
    }
    validateDiagnosticWrapper(recorded);
  });
  return manifest;
}

function cleanupDiagnosticLifecycle(receiptPath) {
  const manifestPath = diagnosticManifestPath(receiptPath);
  if (!fs.existsSync(manifestPath)) return 'not-applicable';
  const manifest = readDiagnosticManifest(receiptPath);
  for (const script of manifest.scripts) {
    validateDiagnosticWrapper(script);
  }
  for (const script of manifest.scripts) {
    removePrivateLifecycleFile(script.wrapper_path);
  }
  removePrivateLifecycleFile(manifestPath);
  return 'removed';
}

function assertDiagnosticKey(key, prefix) {
  const pattern = new RegExp('^' + prefix + '[A-F0-9]{24}$');
  if (!pattern.test(key || '')) {
    throw new Error('diagnostic projection receipt key is invalid');
  }
  return key;
}

function validateDiagnosticProjection(payload, index) {
  const schema = payload?.schema;
  const values = payload?.values;
  if (
    !schema ||
    typeof schema !== 'object' ||
    Array.isArray(schema) ||
    !values ||
    typeof values !== 'object' ||
    Array.isArray(values)
  ) {
    throw new Error('diagnostic projection ' + index + ' payload is invalid');
  }
  const keys = Object.keys(schema);
  const valueKeys = Object.keys(values);
  if (
    keys.length < 1 ||
    keys.length > 32 ||
    valueKeys.length !== keys.length ||
    valueKeys.some(function(key) {
      return !Object.hasOwn(schema, key);
    })
  ) {
    throw new Error(
      'diagnostic projection ' + index + ' values do not match its schema'
    );
  }
  keys.forEach(function(key) {
    if (!/^[a-z][a-z0-9_]{0,63}$/.test(key)) {
      throw new Error(
        'diagnostic projection ' + index + ' field name is invalid'
      );
    }
    const descriptor = schema[key];
    const value = values[key];
    if (!descriptor || typeof descriptor !== 'object' || Array.isArray(descriptor)) {
      throw new Error(
        'diagnostic projection ' + index + ' field ' + key + ' is invalid'
      );
    }
    if (descriptor.type === 'boolean') {
      if (typeof value !== 'boolean') {
        throw new Error(
          'diagnostic projection ' + index + ' field ' + key + ' must be boolean'
        );
      }
      return;
    }
    if (descriptor.type === 'integer') {
      if (
        !Number.isSafeInteger(descriptor.min) ||
        !Number.isSafeInteger(descriptor.max) ||
        descriptor.min > descriptor.max ||
        !Number.isSafeInteger(value) ||
        value < descriptor.min ||
        value > descriptor.max
      ) {
        throw new Error(
          'diagnostic projection ' + index + ' field ' + key + ' must be a bounded integer'
        );
      }
      return;
    }
    if (descriptor.type === 'enum') {
      if (
        !Array.isArray(descriptor.values) ||
        descriptor.values.length < 1 ||
        descriptor.values.length > 32 ||
        descriptor.values.some(function(candidate) {
          return (
            typeof candidate !== 'string' ||
            candidate.length < 1 ||
            candidate.length > 64
          );
        }) ||
        !descriptor.values.includes(value)
      ) {
        throw new Error(
          'diagnostic projection ' + index + ' field ' + key + ' must match enum'
        );
      }
      return;
    }
    if (descriptor.type === 'sha256') {
      if (typeof value !== 'string' || !/^[a-f0-9]{64}$/.test(value)) {
        throw new Error(
          'diagnostic projection ' + index + ' field ' + key + ' must be sha256'
        );
      }
      return;
    }
    throw new Error(
      'diagnostic projection ' + index + ' field ' + key + ' type is not allowed'
    );
  });
  return { keys: keys.sort(), values };
}

function assertDiagnosticReceiptBinding(receipt, suppliedScripts) {
  const recordedScripts = receipt.diagnostic_init_scripts || [];
  if (recordedScripts.length !== suppliedScripts.length) {
    throw new Error('diagnostic init-script input count changed');
  }
  recordedScripts.forEach(function(recorded, index) {
    const supplied = suppliedScripts[index];
    if (
      recorded.basename !== supplied.basename ||
      recorded.path_sha256 !== supplied.pathSha256
    ) {
      throw new Error('diagnostic init script ' + index + ' path changed');
    }
    if (
      recorded.byte_length !== supplied.byteLength ||
      recorded.content_sha256 !== supplied.contentSha256
    ) {
      throw new Error('diagnostic init script ' + index + ' content changed');
    }
  });
}

function diagnosticEval(options, expression, description) {
  return parseAgentBrowserPayload(
    runAgentBrowser(options, ['eval', expression, '--json']),
    description
  ).result;
}

function observeDiagnosticProjections(options, receipt, manifest) {
  manifest.scripts.forEach(function(script, index) {
    const markerKey = assertDiagnosticKey(
      script.marker_key,
      '__E2E_DIAGNOSTIC_MARKER_'
    );
    const projectionKey = assertDiagnosticKey(
      script.projection_key,
      '__E2E_DIAGNOSTIC_PROJECTION_'
    );
    const marker = diagnosticEval(
      options,
      'globalThis[' + JSON.stringify(markerKey) + '] === true',
      'agent-browser diagnostic marker evidence'
    );
    if (marker !== true) {
      throw new Error(
        'diagnostic init script ' + index + ' was not observed after navigation'
      );
    }
    const projection = diagnosticEval(
      options,
      'globalThis[' + JSON.stringify(projectionKey) + ']()',
      'agent-browser diagnostic projection evidence'
    );
    const validated = validateDiagnosticProjection(projection, index);
    receipt.diagnostic_init_scripts[index] = Object.assign(
      {},
      receipt.diagnostic_init_scripts[index],
      {
        allowlisted_keys: validated.keys,
        projection_status: 'validated',
        status: 'observed',
      }
    );
  });
}

function readDiagnosticProjections(options, receipt) {
  assertDiagnosticReceiptBinding(receipt, options.diagnosticScripts);
  if (receipt.first_navigation?.status !== 'verified') {
    throw new Error(
      'diagnostic projections require a verified first-navigation receipt'
    );
  }
  const projections = (receipt.diagnostic_init_scripts || []).map(function(
    script,
    index
  ) {
    if (script.status !== 'observed' || script.projection_status !== 'validated') {
      throw new Error(
        'diagnostic projection ' + index + ' is unavailable before observation'
      );
    }
    const projectionKey = assertDiagnosticKey(
      script.projection_key,
      '__E2E_DIAGNOSTIC_PROJECTION_'
    );
    const projection = diagnosticEval(
      options,
      'globalThis[' + JSON.stringify(projectionKey) + ']()',
      'agent-browser diagnostic projection'
    );
    const validated = validateDiagnosticProjection(projection, index);
    if (
      JSON.stringify(validated.keys) !==
      JSON.stringify((script.allowlisted_keys || []).slice().sort())
    ) {
      throw new Error(
        'diagnostic projection ' + index + ' schema changed after observation'
      );
    }
    return {
      index,
      basename: script.basename,
      values: validated.values,
    };
  });
  return { projections };
}

function createInitProbe(receiptPath) {
  const files = firstNavigationFiles(receiptPath);
  ensureOwnedDirectory(path.dirname(files.initPath));
  const key =
    '__E2E_RUNTIME_INIT_' + crypto.randomBytes(8).toString('hex').toUpperCase();
  const value = crypto.randomBytes(16).toString('hex');
  fs.writeFileSync(
    files.initPath,
    'Object.defineProperty(globalThis, ' +
      JSON.stringify(key) +
      ', { configurable: false, value: ' +
      JSON.stringify(value) +
      ' });\n',
    { flag: 'wx', mode: 0o600 }
  );
  return {
    harPath: files.harPath,
    initPath: files.initPath,
    probeExpression:
      'globalThis[' + JSON.stringify(key) + '] === ' + JSON.stringify(value),
  };
}

function inspectFirstNavigationHar(harPath) {
  const payload = readRegularJson(harPath, 'first-navigation HAR');
  const entries =
    Array.isArray(payload?.log?.entries)
      ? payload.log.entries
      : [];
  const documentCount = entries.filter(function(entry) {
    const resourceType = String(entry?._resourceType || '').toLowerCase();
    const mimeType = String(
      entry?.response?.content?.mimeType || ''
    ).toLowerCase();
    return resourceType === 'document' || mimeType.includes('text/html');
  }).length;
  if (documentCount < 1) {
    throw new Error(
      'browser lifecycle infrastructure failure: first-navigation HAR has no document request'
    );
  }
  return {
    document_count: documentCount,
    entry_count: entries.length,
    status: 'verified-and-discarded',
  };
}

function assertInitProbeObserved(options, expression) {
  const data = parseAgentBrowserPayload(
    runAgentBrowser(options, ['eval', expression, '--json']),
    'agent-browser init-script evidence'
  );
  if (data.result !== true) {
    throw new Error(
      'browser lifecycle infrastructure failure: init script was not observed after navigation'
    );
  }
}

/**
 * Post-navigation proof that the profile's state reached the live page (#149).
 *
 * agent-browser 0.32 snapshot mode drops Local Storage, so a pre-authenticated profile
 * can be silently inert while every file-level check — lineage, device, inode,
 * structural digest — still passes, because the files were fine. Nothing the runtime
 * already records can see that, and the recorder's own init-script probe is evidence
 * about the recorder rather than about the profile.
 *
 * The observation is DECLARED BY THE CALLER, not inferred. An earlier attempt counted
 * origin state and refused when it found none; it was reverted because counting cannot
 * distinguish state the profile carried from state the page minted on load. A logged-out
 * load still sets an anonymous session cookie, a CSRF token, a locale — so the count is
 * nonzero and a dropped profile passes. The same counter was simultaneously too strict:
 * `document.cookie` cannot see HttpOnly cookies, so a profile authenticated purely by an
 * HttpOnly session cookie read as empty and a working run would have been refused. The
 * runtime does not know what a given application should be carrying. The caller does.
 *
 * Both forms are DATA, never code: the key and the selector are JSON-encoded into the
 * expression, so a value cannot extend the expression it appears in.
 */
function profileLivenessExpression(keys, selectors) {
  return (
    '(() => {' +
    ' const keys = ' + JSON.stringify(keys) + ';' +
    ' const selectors = ' + JSON.stringify(selectors) + ';' +
    // The store lookup itself is inside the try. `globalThis.localStorage` throws on an
    // opaque origin, and reading it at a call site outside the guard — as an earlier
    // draft did by passing `localStorage` as an argument — lets the exception escape
    // and makes the unreadable path unreachable in a real browser.
    ' const readKey = (k) => {' +
    '  try { return globalThis.localStorage.getItem(k) !== null ? "present" : "absent"; }' +
    '  catch (_e) { return "unreadable"; }' +
    ' };' +
    ' const readSelector = (s) => {' +
    '  try { return globalThis.document.querySelector(s) !== null ? "present" : "absent"; }' +
    '  catch (_e) { return "unreadable"; }' +
    ' };' +
    ' return {' +
    '  origin: String(globalThis.location ? globalThis.location.origin || "" : ""),' +
    '  keys: keys.map((k) => ({ name: k, result: readKey(k) })),' +
    '  selectors: selectors.map((s) => ({ name: s, result: readSelector(s) }))' +
    ' };' +
    '})()'
  );
}

/**
 * Observe every declared liveness assertion and return the receipt fragment.
 *
 * Returns `not-asserted` when the caller declared nothing. That is the honest state and
 * it is recorded rather than omitted: this issue's complaint was that a reviewer reading
 * the artifact could not tell "profile restored" from "profile silently absent", and a
 * receipt that stays silent about the profile reproduces exactly that. `not-asserted`
 * says the run has no profile proof, which is a different claim from having one.
 */
const PROFILE_LIVENESS_TIMEOUT_MS = 10000;
const PROFILE_LIVENESS_INTERVAL_MS = 250;

function readProfileLiveness(options, keys, selectors) {
  const data = parseAgentBrowserPayload(
    runAgentBrowser(options, [
      'eval',
      profileLivenessExpression(keys, selectors),
      '--json',
    ]),
    'agent-browser profile liveness evidence'
  );
  const result = data.result;
  if (
    !result ||
    typeof result !== 'object' ||
    !Array.isArray(result.keys) ||
    !Array.isArray(result.selectors) ||
    result.keys.length !== keys.length ||
    result.selectors.length !== selectors.length
  ) {
    throw new Error('agent-browser profile liveness evidence is incomplete');
  }
  const unsatisfied = result.keys.concat(result.selectors).filter(function(observation) {
    return observation.result !== 'present';
  });
  return {
    status: unsatisfied.length === 0 ? 'observed' : 'unsatisfied',
    origin: String(result.origin || ''),
    keys: result.keys,
    selectors: result.selectors,
    unsatisfied: unsatisfied,
  };
}

function observeProfileLiveness(options) {
  const keys = options.profileLivenessKeys || [];
  const selectors = options.profileLivenessSelectors || [];
  if (keys.length === 0 && selectors.length === 0) {
    return {
      status: 'not-asserted',
      note:
        'no --profile-liveness-key or --profile-liveness-selector was declared, so this ' +
        'run carries no evidence that profile state reached the page',
      keys: [],
      selectors: [],
    };
  }
  // Polled, not one-shot. A restored session is not necessarily observable the instant
  // navigation returns: an SPA rehydrating from an HttpOnly cookie has to complete a
  // round trip before it renders anything authenticated-only, and a storage write can
  // trail the load event. Sampling once would fail those runs nondeterministically —
  // turning this guard into the flake class the rest of this work removed.
  //
  // Only the satisfied case can exit early; an unsatisfied one is retried until the
  // deadline, so the reported failure is "still absent after the full budget" rather
  // than "absent at one arbitrary instant".
  const timeoutMs =
    options.profileLivenessTimeoutMs === undefined
      ? PROFILE_LIVENESS_TIMEOUT_MS
      : options.profileLivenessTimeoutMs;
  const deadline = Date.now() + timeoutMs;
  let attempts = 0;
  let liveness;
  for (;;) {
    attempts += 1;
    liveness = readProfileLiveness(options, keys, selectors);
    if (liveness.status === 'observed' || Date.now() >= deadline) break;
    sleepSync(PROFILE_LIVENESS_INTERVAL_MS);
  }
  liveness.attempts = attempts;
  liveness.waited_ms_budget = timeoutMs;
  return liveness;
}

/**
 * Fail closed on a declared assertion that did not hold.
 *
 * Only a DECLARED assertion can fail here. `not-asserted` never fails — a caller that
 * did not name what the profile should carry has not made a claim the runtime can
 * refuse, and inventing one is what the reverted attempt got wrong.
 *
 * `unreadable` is grouped with `absent` on purpose, and this is the one place the two
 * differ from the earlier design: when the caller HAS declared that a key must be
 * readable, an origin where it cannot be read has not satisfied the assertion. Absent
 * evidence still is not evidence of absence — it is simply not the positive observation
 * that `verified` was made contingent on.
 */
function assertProfileLiveness(liveness) {
  if (liveness.status !== 'unsatisfied') return;
  const detail = liveness.unsatisfied
    .map(function(observation) {
      return observation.name + '=' + observation.result;
    })
    .join(', ');
  throw new Error(
    'browser lifecycle infrastructure failure: declared profile liveness was not ' +
      'observed after navigation (' + detail + ' at ' +
      (liveness.origin || 'the navigated origin') +
      '). The profile passed its file-level lineage checks, so its contents were ' +
      'dropped between the snapshot and the page rather than lost by the runtime — ' +
      'agent-browser 0.32 snapshot mode is known to drop Local Storage. Any proof ' +
      'depending on a pre-authenticated profile would run logged-out from here.'
  );
}

function writeLifecycleReceipt(receiptPath, receipt) {
  writeJsonAtomic(receiptPath, receipt, false);
  return receipt;
}

function failLifecycleReceipt(receiptPath, receipt, error, postEvidence) {
  if (!receipt) return;
  const failed = Object.assign({}, receipt, {
    status: 'failed',
    failure_class: 'infrastructure',
    error: error.message,
    failed_at: new Date().toISOString(),
  });
  if (failed.first_navigation) {
    failed.first_navigation = Object.assign({}, failed.first_navigation, {
      status: 'failed',
      post: postEvidence || failed.first_navigation.post || null,
    });
  }
  writeLifecycleReceipt(receiptPath, failed);
}

/**
 * Record a failure that happened on a navigation AFTER the first one.
 *
 * `failLifecycleReceipt` is first-navigation-shaped: it rewrites `first_navigation` to
 * `failed` and replaces its `post` with whatever evidence it is handed. Calling it for a
 * later navigation therefore backdates the failure onto a navigation that genuinely
 * verified, overwrites that navigation's evidence with a different page's, and leaves no
 * record of the navigation that actually failed. The history would then say the run
 * failed somewhere it did not.
 *
 * So a later failure marks the run failed, leaves `first_navigation` exactly as it was
 * earned, and records itself under `last_navigation`.
 */
function failLaterNavigationReceipt(receiptPath, receipt, error, pre, post) {
  if (!receipt) return;
  const failed = Object.assign({}, receipt, {
    status: 'failed',
    failure_class: 'infrastructure',
    error: error.message,
    failed_at: new Date().toISOString(),
    last_navigation: {
      status: 'failed',
      pre: pre || null,
      post: post || null,
      failed_at: new Date().toISOString(),
    },
  });
  writeLifecycleReceipt(receiptPath, failed);
}

function performOwnedOpen(options) {
  const targetUrl = options.command[1] || '';
  let receipt = options.existingReceipt;
  let pre;
  let probeExpression = '';
  let initPath = '';
  let diagnosticManifest = null;
  let lineage = receipt?.profile_lineage
    ? {
        actualProfile: receipt.actual_profile,
        actualProfileDevice: receipt.profile_lineage.actual_device,
        actualProfileInode: receipt.profile_lineage.actual_inode,
        structuralDigest: receipt.profile_lineage.structural_digest,
        structuralMatchedBytes:
          receipt.profile_lineage.structural_matched_bytes,
        structuralMatchedEntries:
          receipt.profile_lineage.structural_matched_entries,
      }
    : null;
  const files = firstNavigationFiles(options.receiptPath);

  if (!receipt) {
    lineage = prepareProfileLineage(
      options.profile,
      options.runId,
      options.app,
      options.receiptPath
    );
    const initProbe = createInitProbe(options.receiptPath);
    diagnosticManifest = prepareDiagnosticLifecycle(
      options.receiptPath,
      options.diagnosticScripts
    );
    initPath = initProbe.initPath;
    probeExpression = initProbe.probeExpression;
    const launch = [
      '--engine',
      'chrome',
      '--executable-path',
      options.executablePath,
      '--profile',
      options.profile,
    ];
    if (options.headed) launch.push('--headed');
    launch.push('--init-script', initProbe.initPath);
    for (const diagnostic of diagnosticManifest?.scripts || []) {
      launch.push('--init-script', diagnostic.wrapper_path);
    }
    launch.push('open');
    try {
      const stdout = runAgentBrowser(options, launch);
      if (stdout) process.stdout.write(stdout);
      pre = captureNavigationEvidence(
        Object.assign({}, options, {
          harStatus: 'not-started',
          initStatus: 'registered',
          lineage,
        })
      );
    } finally {
      removePrivateLifecycleFile(initProbe.initPath);
      initPath = '';
    }
    receipt = writeBrowserOwnershipReceipt(
      {
        app: options.app,
        executablePath: options.executablePath,
        namespace: options.namespace,
        profile: options.profile,
        receiptPath: options.receiptPath,
        runId: options.runId,
      },
      {
        browserPid: pre.browser_pid,
        daemonPid: pre.daemon_pid,
        reused: pre.reused,
        socketDir: options.expectedSocketDir,
      },
      null
    );
    receipt.actual_profile = pre.actual_profile;
    receipt.profile_mode = pre.profile_mode;
    receipt.profile_lineage = {
      proof: pre.profile_lineage,
      source_device: lineage.sourceDevice,
      source_inode: lineage.sourceInode,
      source_binding: lineage.sourceBinding,
      actual_device: pre.actual_profile_device,
      actual_inode: pre.actual_profile_inode,
      actual_mode: pre.actual_profile_mode,
      actual_uid: pre.actual_profile_uid,
      structural_digest: pre.structural_digest,
      structural_matched_bytes: pre.structural_matched_bytes,
      structural_matched_entries: pre.structural_matched_entries,
      temp_root_mode: pre.temp_root_mode,
    };
    lineage = {
      actualProfile: receipt.actual_profile,
      actualProfileDevice: receipt.profile_lineage.actual_device,
      actualProfileInode: receipt.profile_lineage.actual_inode,
      structuralDigest: receipt.profile_lineage.structural_digest,
      structuralMatchedBytes:
        receipt.profile_lineage.structural_matched_bytes,
      structuralMatchedEntries:
        receipt.profile_lineage.structural_matched_entries,
    };
    receipt.first_navigation = {
      status: 'pending',
      pre,
      post: null,
      init_script: 'registered',
      har: { status: 'not-started', document_count: 0, entry_count: 0 },
      probe_expression: probeExpression,
    };
    receipt.diagnostic_init_scripts = (diagnosticManifest?.scripts || []).map(function(
      script,
      index
    ) {
      return diagnosticPublicProvenance(script, index, 'registered');
    });
    writeLifecycleReceipt(options.receiptPath, receipt);
  } else {
    if (!receipt.first_navigation) {
      throw new Error(
        'browser lifecycle receipt predates first-navigation evidence; close and reopen the owned session'
      );
    }
    if (
      (receipt.diagnostic_init_scripts || []).length !==
      options.diagnosticScripts.length
    ) {
      throw new Error('diagnostic init-script input count changed');
    }
    probeExpression = receipt.first_navigation.probe_expression || '';
    pre = captureNavigationEvidence(
      Object.assign({}, options, {
        harStatus:
          receipt.first_navigation.status === 'pending'
            ? 'not-started'
            : 'not-applicable',
        initStatus:
          receipt.first_navigation.status === 'pending'
            ? 'registered'
            : 'previously-observed',
        lineage,
      })
    );
    assertReceiptBinding(receipt, {
      app: options.app,
      browserPid: pre.browser_pid,
      daemonPid: pre.daemon_pid,
      executablePath: options.executablePath,
      namespace: options.namespace,
      profile: options.profile,
      runId: options.runId,
      socketDir: options.expectedSocketDir,
    });
    if (
      receipt.actual_profile !== pre.actual_profile ||
      receipt.profile_mode !== pre.profile_mode ||
      String(receipt.profile_lineage.actual_device) !==
        String(pre.actual_profile_device) ||
      String(receipt.profile_lineage.actual_inode) !==
        String(pre.actual_profile_inode)
    ) {
      throw new Error(
        'browser lifecycle infrastructure failure: actual profile identity changed'
      );
    }
  }

  if (
    options.diagnosticScripts.length &&
    receipt.first_navigation.status === 'pending'
  ) {
    try {
      diagnosticManifest = revalidateDiagnosticLifecycle(
        options.receiptPath,
        options.diagnosticScripts
      );
    } catch (error) {
      failLifecycleReceipt(options.receiptPath, receipt, error, null);
      try {
        cleanupDiagnosticLifecycle(options.receiptPath);
      } catch (_cleanupError) {
        // Preserve the attributed source or wrapper failure.
      }
      throw error;
    }
  } else if (options.diagnosticScripts.length) {
    assertDiagnosticReceiptBinding(receipt, options.diagnosticScripts);
  } else if ((receipt.diagnostic_init_scripts || []).length) {
    const error = new Error('diagnostic init-script input count changed');
    failLifecycleReceipt(options.receiptPath, receipt, error, null);
    throw error;
  }

  if (!targetUrl || targetUrl === 'about:blank') {
    return receipt;
  }

  if (receipt.first_navigation.status !== 'pending') {
    const stdout = runAgentBrowser(options, ['open', targetUrl]);
    if (stdout) process.stdout.write(stdout);
    const post = captureNavigationEvidence(
      Object.assign({}, options, {
        harStatus: 'not-applicable',
        initStatus: 'previously-observed',
        lineage,
      })
    );
    assertStableNavigationIdentity(pre, post);
    // A declared assertion is checked on EVERY navigation that declares it, not only on
    // the first. Evaluating it solely while `first_navigation` was pending meant a later
    // `open --profile-liveness-key ...` silently succeeded without checking or recording
    // anything — a declared claim quietly going unverified, which is the same defect
    // class this issue is about, one navigation over.
    // Observation AND assertion both sit inside the recording path. An `eval` transport
    // failure or an incomplete payload throws out of `observeProfileLiveness`, and
    // leaving that outside the catch would exit unsuccessfully while the receipt still
    // read as verified from the previous navigation — a green artifact for a run that
    // failed, which is the defect class this whole issue is about.
    let lastLiveness;
    try {
      lastLiveness = observeProfileLiveness(options);
      post.profile_liveness = lastLiveness;
      assertProfileLiveness(lastLiveness);
    } catch (error) {
      failLaterNavigationReceipt(options.receiptPath, receipt, error, pre, post);
      throw error;
    }
    receipt.last_navigation = {
      status: 'verified',
      pre,
      post,
      profile_liveness: lastLiveness,
      verified_at: new Date().toISOString(),
    };
    writeLifecycleReceipt(options.receiptPath, receipt);
    return receipt;
  }

  let harStarted = false;
  let post = null;
  try {
    removePrivateLifecycleFile(files.harPath);
    runAgentBrowser(options, ['network', 'har', 'start']);
    harStarted = true;
    receipt.first_navigation.pre.recorder.har = 'started';
    writeLifecycleReceipt(options.receiptPath, receipt);
    const stdout = runAgentBrowser(options, ['open', targetUrl]);
    if (stdout) process.stdout.write(stdout);
    post = captureNavigationEvidence(
      Object.assign({}, options, {
        harStatus: 'started',
        initStatus: 'checking',
        lineage,
      })
    );
    assertStableNavigationIdentity(pre, post);
    if (!post.url || post.url === 'about:blank') {
      throw new Error(
        'browser lifecycle infrastructure failure: application URL reset to about:blank'
      );
    }
    assertInitProbeObserved(options, probeExpression);
    post.recorder.init_script = 'observed';
    // Attachment is evidence about the recorder, not about the profile. A declared
    // liveness assertion is the only thing here that can speak to the profile, and it
    // fails the run when it does not hold (#149).
    const profileLiveness = observeProfileLiveness(options);
    post.profile_liveness = profileLiveness;
    assertProfileLiveness(profileLiveness);
    if (diagnosticManifest?.scripts?.length) {
      observeDiagnosticProjections(options, receipt, diagnosticManifest);
    }
    runAgentBrowser(options, ['network', 'har', 'stop', files.harPath]);
    harStarted = false;
    const har = inspectFirstNavigationHar(files.harPath);
    post.recorder.har = har.status;
    receipt.first_navigation = {
      status: 'verified',
      pre: receipt.first_navigation.pre,
      post,
      init_script: 'observed',
      // Always present, including as `not-asserted`. `status: verified` has always meant
      // navigation and recorder continuity and still does; it never meant the profile
      // was live, and a receipt that stayed silent on the profile is what let a reviewer
      // read it as though it did.
      profile_liveness: profileLiveness,
      har,
      verified_at: new Date().toISOString(),
    };
    receipt.diagnostic_cleanup = cleanupDiagnosticLifecycle(options.receiptPath);
    writeLifecycleReceipt(options.receiptPath, receipt);
    return receipt;
  } catch (error) {
    if (harStarted) {
      try {
        runAgentBrowser(options, ['network', 'har', 'stop', files.harPath]);
      } catch (_stopError) {
        // Preserve the original lifecycle failure.
      }
    }
    failLifecycleReceipt(options.receiptPath, receipt, error, post);
    try {
      cleanupDiagnosticLifecycle(options.receiptPath);
    } catch (_cleanupError) {
      // Preserve the attributed observation or projection failure.
    }
    throw error;
  } finally {
    removePrivateLifecycleFile(initPath);
    removePrivateLifecycleFile(files.harPath);
  }
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

function markBrowserOwnershipClosed(receiptPath, receipt, profileCleanup) {
  if (!receipt) return;
  const closed = Object.assign({}, receipt, {
    status: 'closed',
    cleanup: 'owned-session-closed',
    profile_cleanup: profileCleanup || 'not-applicable',
    closed_at: new Date().toISOString(),
  });
  writeJsonAtomic(receiptPath, closed, false);
}

function cleanupOwnedProfileSnapshot(receipt) {
  if (!receipt || receipt.profile_mode !== 'verified-snapshot') {
    return 'not-applicable';
  }
  const actualProfile = receipt.actual_profile;
  if (!fs.existsSync(actualProfile)) return 'already-removed';
  const evidence = validateProfileLineage(actualProfile, receipt.profile, {
    actualProfile: receipt.actual_profile,
    actualProfileDevice: receipt.profile_lineage.actual_device,
    actualProfileInode: receipt.profile_lineage.actual_inode,
    structuralDigest: receipt.profile_lineage.structural_digest,
    structuralMatchedBytes: receipt.profile_lineage.structural_matched_bytes,
    structuralMatchedEntries:
      receipt.profile_lineage.structural_matched_entries,
  });
  if (
    evidence.profileMode !== 'verified-snapshot' ||
    String(evidence.actualProfileDevice) !==
      String(receipt.profile_lineage.actual_device) ||
    String(evidence.actualProfileInode) !==
      String(receipt.profile_lineage.actual_inode) ||
    evidence.actualProfileUid !== receipt.profile_lineage.actual_uid
  ) {
    throw new Error('owned browser profile snapshot identity changed before cleanup');
  }
  fs.rmSync(actualProfile, { recursive: true, force: false });
  return 'removed';
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
    namespace = namespaceForRun(options.runId, socketHome, options.app);
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
  const requestedOwnedClose =
    options.command[0] === 'close' ||
    options.command[0] === 'cleanup-flow-managed-profile';
  if (requestedOwnedClose) {
    options.diagnosticScripts = [];
  } else {
    try {
      options.diagnosticScripts = options.diagnosticInitScripts.map(function(
        scriptPath
      ) {
        return validateDiagnosticInitScript(scriptPath);
      });
    } catch (error) {
      process.stderr.write('e2e-browser-runtime: ' + error.message + '\n');
      return 2;
    }
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
        if (
          record.state.status === 'prepared' &&
          !fs.existsSync(record.binding.profile)
        ) {
          assertNoActiveFlowManagedBinding({
            browserHome,
            runId: options.runId,
            app: options.app,
          });
        } else if (
          record.state.status === 'active' &&
          record.state.binding === 'verified'
        ) {
          verifyFlowManagedProfile({
            browserHome,
            runId: options.runId,
            app: options.app,
            canonicalProfile: options.canonicalProfile,
            profile: options.profile,
          });
        } else {
          throw new Error(
            'flow-managed open requires a prepared fresh profile or the active binding'
          );
        }
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
  const lifecycleVersion =
    options.command[0] === 'open'
      ? agentBrowserLifecycleVersion(agentBrowser, childEnvironment)
      : '';
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
        lineage: existingReceipt.profile_lineage
          ? {
              actualProfile: existingReceipt.actual_profile,
              actualProfileDevice:
                existingReceipt.profile_lineage.actual_device,
              actualProfileInode:
                existingReceipt.profile_lineage.actual_inode,
              structuralDigest:
                existingReceipt.profile_lineage.structural_digest,
              structuralMatchedBytes:
                existingReceipt.profile_lineage.structural_matched_bytes,
              structuralMatchedEntries:
                existingReceipt.profile_lineage.structural_matched_entries,
            }
          : null,
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
      if (
        existingReceipt.actual_profile &&
        (existingReceipt.actual_profile !== liveEvidence.actualProfile ||
          String(existingReceipt.profile_lineage.actual_device) !==
            String(liveEvidence.actualProfileDevice) ||
          String(existingReceipt.profile_lineage.actual_inode) !==
            String(liveEvidence.actualProfileInode))
      ) {
        throw new Error(
          'browser ownership receipt does not match actual profile identity'
        );
      }
    } catch (error) {
      process.stderr.write('e2e-browser-runtime: ' + error.message + '\n');
      return 2;
    }
  }
  if (
    existingReceipt &&
    !isOwnedClose &&
    options.command[0] !== 'open'
  ) {
    try {
      assertDiagnosticReceiptBinding(
        existingReceipt,
        options.diagnosticScripts
      );
    } catch (error) {
      process.stderr.write('e2e-browser-runtime: ' + error.message + '\n');
      return 2;
    }
  }
  if (existingReceipt && !isOwnedClose) {
    args.splice(
      0,
      args.length,
      '--namespace',
      namespace,
      '--session',
      options.app,
      '--config',
      configPath,
      ...options.command
    );
  }
  if (options.command[0] === 'diagnostic-projection') {
    if (!existingReceipt) {
      process.stderr.write(
        'e2e-browser-runtime: diagnostic projection requires an ownership receipt\n'
      );
      return 2;
    }
    try {
      const projections = readDiagnosticProjections(
        {
          agentBrowser,
          app: options.app,
          childEnvironment,
          configPath,
          diagnosticScripts: options.diagnosticScripts,
          namespace,
        },
        existingReceipt
      );
      process.stdout.write(JSON.stringify(projections) + '\n');
      return 0;
    } catch (error) {
      process.stderr.write('e2e-browser-runtime: ' + error.message + '\n');
      return 2;
    }
  }
  if (
    options.command[0] === 'open' &&
    lifecycleVersion &&
    compareVersions(lifecycleVersion, '0.32.0') >= 0
  ) {
    try {
      performOwnedOpen({
        agentBrowser,
        app: options.app,
        childEnvironment,
        command: options.command,
        configPath,
        executablePath: options.executablePath,
        existingReceipt,
        expectedSocketDir: path.join(
          socketHome,
          'namespaces',
          namespace,
          'run'
        ),
        headed: options.headed,
        namespace,
        profile: path.resolve(options.profile),
        receiptPath,
        runId: options.runId,
        diagnosticScripts: options.diagnosticScripts,
        profileLivenessKeys: options.profileLivenessKeys,
        profileLivenessSelectors: options.profileLivenessSelectors,
      });
      if (options.authMode === 'flow-managed') {
        const record = readFlowManagedState({
          browserHome,
          runId: options.runId,
          app: options.app,
          canonicalProfile: options.canonicalProfile,
          profile: options.profile,
        });
        if (record.state.status === 'prepared') {
          markFlowManagedProfileActive({
            browserHome,
            runId: options.runId,
            app: options.app,
            canonicalProfile: options.canonicalProfile,
            profile: options.profile,
          });
        }
      }
      return 0;
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
          ? 'owned-session-close-failed-after-lifecycle-failure'
          : 'owned-session-closed-after-lifecycle-failure';
      try {
        cleanupClosedNamespaceState(socketHome, namespace, options.app);
      } catch (cleanupError) {
        ownershipCleanup =
          'owned-session-state-cleanup-failed-after-lifecycle-failure';
        process.stderr.write(
          'e2e-browser-runtime: lifecycle namespace cleanup failed: ' +
            cleanupError.message +
            '\n'
        );
      }
      try {
        const failedReceipt = readRegularJson(
          receiptPath,
          'browser ownership receipt'
        );
        if (failedReceipt) {
          failedReceipt.cleanup = ownershipCleanup;
          failedReceipt.profile_cleanup =
            cleanupOwnedProfileSnapshot(failedReceipt);
          writeLifecycleReceipt(receiptPath, failedReceipt);
        }
      } catch (receiptError) {
        process.stderr.write(
          'e2e-browser-runtime: lifecycle receipt update failed: ' +
            receiptError.message +
            '\n'
        );
      }
      if (options.authMode === 'flow-managed') {
        try {
          const record = readFlowManagedState({
            browserHome,
            runId: options.runId,
            app: options.app,
            canonicalProfile: options.canonicalProfile,
            profile: options.profile,
          });
          if (record.state.status === 'prepared') {
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
          }
        } catch (cleanupError) {
          process.stderr.write(
            'e2e-browser-runtime: lifecycle profile cleanup failed: ' +
              cleanupError.message +
              '\n'
          );
        }
      }
      process.stderr.write('e2e-browser-runtime: ' + error.message + '\n');
      return 2;
    }
  }
  if (
    options.command[0] === 'open' &&
    !lifecycleVersion &&
    process.env.E2E_RUNTIME_TEST_MODE !== '1'
  ) {
    process.stderr.write(
      'e2e-browser-runtime: could not verify an agent-browser lifecycle contract version\n'
    );
    return 2;
  }
  if (
    options.command[0] === 'open' &&
    lifecycleVersion &&
    compareVersions(lifecycleVersion, '0.32.0') < 0
  ) {
    process.stderr.write(
      'e2e-browser-runtime: agent-browser 0.32.0 or newer is required for owned navigation lifecycle evidence\n'
    );
    return 2;
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
      if (existingReceipt?.diagnostic_init_scripts?.length) {
        cleanupDiagnosticLifecycle(receiptPath);
      }
      cleanupClosedNamespaceState(socketHome, namespace, options.app);
      const profileCleanup = cleanupOwnedProfileSnapshot(existingReceipt);
      markBrowserOwnershipClosed(receiptPath, existingReceipt, profileCleanup);
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
  // Exported for a direct unit test. The integration fixture runs the expression through
  // `vm`, and `vm` does NOT forward a throwing getter from the sandbox — it yields
  // `undefined` instead — so an opaque origin cannot be modelled there at all. Guard
  // placement is only falsifiable against a real throwing getter, which needs
  // in-process evaluation.
  profileLivenessExpression,
  validateDiagnosticInitScript,
  prepareFlowManagedProfile,
  protectedRuntimeArgument,
  socketHomeForBrowserHome,
  verifyFlowManagedProfile,
};
