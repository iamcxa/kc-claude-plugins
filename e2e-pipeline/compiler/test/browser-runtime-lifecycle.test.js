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
      dropDiagnosticIndex: -1,
      profileMode: 'persistent',
      profileProjectionAppearAfter: 1,
      profileProjectionValue: null,
      resetOnNavigation: '',
      switchPageOnProjection: false,
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
    runtimeModule.socketHomeForBrowserHome(browserHome),
    app
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
        diagnosticGlobals: {},
        dropDiagnosticIndex: settings.dropDiagnosticIndex,
        daemonPid: 321,
        events: [],
        executable,
        harActive: false,
        initRegistered: false,
        initScripts: [],
        launchHash: 12345,
        profileMode: settings.profileMode,
        profileProjectionAppearAfter: settings.profileProjectionAppearAfter,
        profileProjectionReads: 0,
        profileProjectionValue: settings.profileProjectionValue,
        requests: [],
        resetOnNavigation: settings.resetOnNavigation,
        reused: false,
        snapshotId,
        socketDir,
        switchPageOnProjection: settings.switchPageOnProjection,
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

function runOpen(fixture, url, diagnosticInitScripts, livenessArgs) {
  const diagnosticArgs = (diagnosticInitScripts || []).flatMap(function(
    scriptPath
  ) {
    return ['--diagnostic-init-script', scriptPath];
  });
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
      ...diagnosticArgs,
      ...(livenessArgs || []),
      'open',
      url,
    ],
    { encoding: 'utf8', env: fixture.env }
  );
}

function setProfileProjection(fixture, value, appearAfter) {
  const state = JSON.parse(fs.readFileSync(fixture.statePath, 'utf8'));
  state.profileProjectionValue = value;
  state.profileProjectionAppearAfter = appearAfter || 1;
  state.profileProjectionReads = 0;
  fs.writeFileSync(fixture.statePath, JSON.stringify(state, null, 2) + '\n');
}

function runClose(fixture, diagnosticInitScripts) {
  const diagnosticArgs = (diagnosticInitScripts || []).flatMap(function(
    scriptPath
  ) {
    return ['--diagnostic-init-script', scriptPath];
  });
  return spawnSync(
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
      ...diagnosticArgs,
      'close',
    ],
    { encoding: 'utf8', env: fixture.env }
  );
}

function runDiagnosticProjection(fixture, diagnosticInitScripts) {
  const diagnosticArgs = (diagnosticInitScripts || []).flatMap(function(
    scriptPath
  ) {
    return ['--diagnostic-init-script', scriptPath];
  });
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
      ...diagnosticArgs,
      'diagnostic-projection',
    ],
    { encoding: 'utf8', env: fixture.env }
  );
}

test('rejects invalid diagnostic init-script inputs before browser launch', function(t) {
  const fixture = setup(t);
  const directory = path.join(fixture.root, 'recorder-directory');
  const missing = path.join(fixture.root, 'missing-recorder.js');
  const target = path.join(fixture.root, 'recorder-target.js');
  const symlink = path.join(fixture.root, 'recorder-symlink.js');
  fs.mkdirSync(directory);
  fs.writeFileSync(target, 'publishDiagnosticProjection({}, () => ({}));\n');
  fs.symlinkSync(target, symlink);

  for (const [label, scriptPath, errorPattern] of [
    ['relative', 'recorder.js', /absolute/i],
    ['missing', missing, /missing|regular file/i],
    ['directory', directory, /regular file/i],
    ['symlink', symlink, /symlink/i],
  ]) {
    const result = runOpen(
      fixture,
      'https://application.example.test/' + label,
      [scriptPath]
    );
    assert.notEqual(result.status, 0, label);
    assert.match(result.stderr, errorPattern, label);
  }

  const state = JSON.parse(fs.readFileSync(fixture.statePath, 'utf8'));
  assert.equal(
    state.events.some(function(event) {
      return event.command === 'open';
    }),
    false
  );
});

test('accepts repeated current-user-owned diagnostic init-script files', function(t) {
  const fixture = setup(t);
  const first = path.join(fixture.root, 'first-recorder.js');
  const second = path.join(fixture.root, 'second-recorder.js');
  fs.writeFileSync(first, 'publishDiagnosticProjection({}, () => ({}));\n');
  fs.writeFileSync(second, 'publishDiagnosticProjection({}, () => ({}));\n');

  const result = runOpen(fixture, 'about:blank', [first, second]);

  assert.equal(result.status, 0, result.stderr);
  const state = JSON.parse(fs.readFileSync(fixture.statePath, 'utf8'));
  assert.equal(
    state.events.some(function(event) {
      return event.command === 'open';
    }),
    true
  );
});

test('launches isolated diagnostic wrappers and records only safe provenance', function(t) {
  const fixture = setup(t);
  const first = path.join(fixture.root, 'first-recorder.js');
  const second = path.join(fixture.root, 'second-recorder.js');
  const firstSource =
    "publishDiagnosticProjection({ready:{type:'boolean'}},()=>({ready:true}));\n";
  const secondSource =
    "publishDiagnosticProjection({phase:{type:'enum',values:['init']}},()=>({phase:'init'}));\n";
  fs.writeFileSync(first, firstSource);
  fs.writeFileSync(second, secondSource);

  const result = runOpen(fixture, 'about:blank', [first, second]);

  assert.equal(result.status, 0, result.stderr);
  const state = JSON.parse(fs.readFileSync(fixture.statePath, 'utf8'));
  const launch = state.events.find(function(event) {
    return event.command === 'open';
  });
  const initScripts = launch.argv.flatMap(function(value, index, argv) {
    return value === '--init-script' ? [argv[index + 1]] : [];
  });
  assert.equal(initScripts.length, 3);
  assert.equal(initScripts.includes(first), false);
  assert.equal(initScripts.includes(second), false);

  const receiptText = fs.readFileSync(fixture.receipt, 'utf8');
  const receipt = JSON.parse(receiptText);
  assert.equal(receipt.diagnostic_init_scripts.length, 2);
  assert.deepEqual(
    receipt.diagnostic_init_scripts.map(function(script) {
      return script.basename;
    }),
    ['first-recorder.js', 'second-recorder.js']
  );
  for (const script of receipt.diagnostic_init_scripts) {
    assert.match(script.content_sha256, /^[a-f0-9]{64}$/);
    assert.match(script.path_sha256, /^[a-f0-9]{64}$/);
    assert.equal(script.status, 'registered');
  }
  assert.equal(receiptText.includes(first), false);
  assert.equal(receiptText.includes(second), false);
  assert.equal(receiptText.includes(firstSource.trim()), false);
  assert.equal(receiptText.includes(secondSource.trim()), false);
});

test('fails before first application navigation when a diagnostic source changes', function(t) {
  const fixture = setup(t);
  const recorder = path.join(fixture.root, 'mutable-recorder.js');
  fs.writeFileSync(
    recorder,
    "publishDiagnosticProjection({ready:{type:'boolean'}},()=>({ready:true}));\n"
  );
  assert.equal(runOpen(fixture, 'about:blank', [recorder]).status, 0);
  fs.writeFileSync(
    recorder,
    "publishDiagnosticProjection({ready:{type:'boolean'}},()=>({ready:false}));\n"
  );
  const targetUrl = 'https://application.example.test/mutated';

  const result = runOpen(fixture, targetUrl, [recorder]);

  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /diagnostic init script 0.*content changed/i);
  const state = JSON.parse(fs.readFileSync(fixture.statePath, 'utf8'));
  const applicationOpen = state.events.find(function(event) {
    return event.command === 'open' && event.args.includes(targetUrl);
  });
  assert.equal(applicationOpen, undefined);
  const receipt = JSON.parse(fs.readFileSync(fixture.receipt, 'utf8'));
  assert.equal(receipt.status, 'failed');
  assert.match(receipt.error, /diagnostic init script 0.*content changed/i);
});

test('rejects substituted runtime-owned diagnostic files without touching caller source', function(t) {
  const fixture = setup(t);
  const recorder = path.join(fixture.root, 'caller-recorder.js');
  const callerSource =
    "publishDiagnosticProjection({ready:{type:'boolean'}},()=>({ready:true}));\n";
  fs.writeFileSync(recorder, callerSource);
  assert.equal(runOpen(fixture, 'about:blank', [recorder]).status, 0);
  const manifestPath = fixture.receipt + '.diagnostic-manifest.json';
  const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
  const wrapperPath = manifest.scripts[0].wrapper_path;
  fs.rmSync(wrapperPath);
  fs.symlinkSync(recorder, wrapperPath);
  const targetUrl = 'https://application.example.test/substituted';

  const result = runOpen(fixture, targetUrl, [recorder]);

  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /diagnostic wrapper.*regular|symlink/i);
  assert.equal(fs.readFileSync(recorder, 'utf8'), callerSource);
  const state = JSON.parse(fs.readFileSync(fixture.statePath, 'utf8'));
  assert.equal(
    state.events.some(function(event) {
      return event.command === 'open' && event.args.includes(targetUrl);
    }),
    false
  );
});

test('successful navigation removes only runtime-owned diagnostic files', function(t) {
  const fixture = setup(t);
  const recorder = path.join(fixture.root, 'success-recorder.js');
  fs.writeFileSync(
    recorder,
    "publishDiagnosticProjection({ready:{type:'boolean'}},()=>({ready:true}));\n"
  );
  const manifestPath = fixture.receipt + '.diagnostic-manifest.json';

  const result = runOpen(
    fixture,
    'https://application.example.test/success',
    [recorder]
  );

  assert.equal(result.status, 0, result.stderr);
  assert.equal(fs.existsSync(manifestPath), false);
  assert.equal(fs.existsSync(recorder), true);
  const privateFiles = fs
    .readdirSync(fixture.root)
    .filter(function(fileName) {
      return fileName.includes('.diagnostic-');
    });
  assert.deepEqual(privateFiles, []);
});

test('close removes pending runtime files but preserves caller scripts', function(t) {
  const fixture = setup(t);
  const recorder = path.join(fixture.root, 'pending-recorder.js');
  const source =
    "publishDiagnosticProjection({ready:{type:'boolean'}},()=>({ready:true}));\n";
  fs.writeFileSync(recorder, source);
  assert.equal(runOpen(fixture, 'about:blank', [recorder]).status, 0);

  const pendingProjection = runDiagnosticProjection(fixture, [recorder]);
  assert.notEqual(pendingProjection.status, 0);
  assert.match(pendingProjection.stderr, /verified first-navigation/i);

  const result = runClose(fixture, [recorder]);

  assert.equal(result.status, 0, result.stderr);
  assert.equal(fs.readFileSync(recorder, 'utf8'), source);
  assert.equal(
    fs
      .readdirSync(fixture.root)
      .some(function(fileName) {
        return fileName.includes('.diagnostic-');
      }),
    false
  );
});

test('close cleans pending runtime files after the caller script disappears', function(t) {
  const fixture = setup(t);
  const recorder = path.join(fixture.root, 'removed-recorder.js');
  fs.writeFileSync(
    recorder,
    "publishDiagnosticProjection({ready:{type:'boolean'}},()=>({ready:true}));\n"
  );
  assert.equal(runOpen(fixture, 'about:blank', [recorder]).status, 0);
  fs.rmSync(recorder);

  const result = runClose(fixture, [recorder]);

  assert.equal(result.status, 0, result.stderr);
  assert.equal(
    fs
      .readdirSync(fixture.root)
      .some(function(fileName) {
        return fileName.includes('.diagnostic-');
      }),
    false
  );
});

test('observes every diagnostic recorder and returns only typed projections', function(t) {
  const fixture = setup(t);
  const recorder = path.join(fixture.root, 'typed-recorder.js');
  fs.writeFileSync(
    recorder,
    [
      'publishDiagnosticProjection(',
      '  {',
      "    ready: {type:'boolean'},",
      "    phase: {type:'enum',values:['init','ready']},",
      "    request_count: {type:'integer',min:0,max:10},",
      "    fingerprint: {type:'sha256'}",
      '  },',
      '  () => ({',
      '    ready: true,',
      "    phase: 'ready',",
      '    request_count: 2,',
      "    fingerprint: '" + 'a'.repeat(64) + "'",
      '  })',
      ');',
      '',
    ].join('\n')
  );

  const open = runOpen(
    fixture,
    'https://application.example.test/typed',
    [recorder]
  );
  assert.equal(open.status, 0, open.stderr);
  const receiptText = fs.readFileSync(fixture.receipt, 'utf8');
  const receipt = JSON.parse(receiptText);
  assert.equal(receipt.diagnostic_init_scripts[0].status, 'observed');
  assert.equal(
    receipt.diagnostic_init_scripts[0].projection_status,
    'validated'
  );
  assert.equal(receiptText.includes('"ready": true'), false);
  assert.equal(receiptText.includes('"phase": "ready"'), false);
  assert.equal(receiptText.includes('a'.repeat(64)), false);

  const projection = runDiagnosticProjection(fixture, [recorder]);
  assert.equal(projection.status, 0, projection.stderr);
  assert.deepEqual(JSON.parse(projection.stdout), {
    projections: [
      {
        index: 0,
        basename: 'typed-recorder.js',
        values: {
          ready: true,
          phase: 'ready',
          request_count: 2,
          fingerprint: 'a'.repeat(64),
        },
      },
    ],
  });
});

test('fails with the recorder index when a diagnostic script is unobserved', function(t) {
  const fixture = setup(t, { dropDiagnosticIndex: 0 });
  const recorder = path.join(fixture.root, 'unobserved-recorder.js');
  fs.writeFileSync(
    recorder,
    "publishDiagnosticProjection({ready:{type:'boolean'}},()=>({ready:true}));\n"
  );

  const result = runOpen(
    fixture,
    'https://application.example.test/unobserved',
    [recorder]
  );

  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /diagnostic init script 0.*not observed/i);
  const receipt = JSON.parse(fs.readFileSync(fixture.receipt, 'utf8'));
  assert.equal(receipt.status, 'failed');
  assert.match(receipt.error, /diagnostic init script 0.*not observed/i);
});

test('rejects a projection value outside its explicit schema', function(t) {
  const fixture = setup(t);
  const recorder = path.join(fixture.root, 'invalid-projection.js');
  fs.writeFileSync(
    recorder,
    [
      'publishDiagnosticProjection(',
      "  {phase:{type:'enum',values:['init','ready']}},",
      "  () => ({phase:'secret-value'})",
      ');',
      '',
    ].join('\n')
  );

  const result = runOpen(
    fixture,
    'https://application.example.test/invalid-projection',
    [recorder]
  );

  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /diagnostic projection 0.*phase.*enum/i);
  const receiptText = fs.readFileSync(fixture.receipt, 'utf8');
  assert.equal(receiptText.includes('secret-value'), false);
});

test('parallel recorders stay isolated and cleanup preserves both caller files', function(t) {
  const first = setup(t);
  const second = setup(t);
  const firstRecorder = path.join(first.root, 'first.js');
  const secondRecorder = path.join(second.root, 'second.js');
  fs.writeFileSync(
    firstRecorder,
    "publishDiagnosticProjection({run:{type:'enum',values:['first']}},()=>({run:'first'}));\n"
  );
  fs.writeFileSync(
    secondRecorder,
    "publishDiagnosticProjection({run:{type:'enum',values:['second']}},()=>({run:'second'}));\n"
  );
  assert.equal(
    runOpen(first, 'https://application.example.test/first', [firstRecorder])
      .status,
    0
  );
  assert.equal(
    runOpen(second, 'https://application.example.test/second', [secondRecorder])
      .status,
    0
  );

  const firstProjection = JSON.parse(
    runDiagnosticProjection(first, [firstRecorder]).stdout
  );
  const secondProjection = JSON.parse(
    runDiagnosticProjection(second, [secondRecorder]).stdout
  );
  assert.equal(firstProjection.projections[0].values.run, 'first');
  assert.equal(secondProjection.projections[0].values.run, 'second');
  assert.equal(runClose(first, [firstRecorder]).status, 0);
  assert.equal(
    runDiagnosticProjection(second, [secondRecorder]).status,
    0
  );
  assert.equal(fs.existsSync(firstRecorder), true);
  assert.equal(fs.existsSync(secondRecorder), true);
});

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

// #149. `verified` was being read as though it covered the profile, because the receipt
// said nothing about the profile's contents either way. These pin the disclosure that
// replaces that silence, and the boundary it must not quietly cross: it is a statement
// about what was NOT observed, so any future edit that lets it read like a positive
// observation has to fail here first.

test('a snapshot run discloses that verified did not cover the profile contents', function(t) {
  const fixture = setup(t, { profileMode: 'snapshot' });

  const result = runOpen(fixture, 'https://application.example.test/disclosure');

  assert.equal(result.status, 0, result.stderr);
  const receipt = JSON.parse(fs.readFileSync(fixture.receipt, 'utf8'));
  const disclosure = receipt.first_navigation.profile_state;

  assert.equal(receipt.first_navigation.status, 'verified');
  assert.equal(disclosure.status, 'not-observed');
  assert.equal(disclosure.verified_excludes, 'whether profile contents reached the page');
  // The mode that copies before launch is the only one whose contents can be lost on the
  // way to the page, so the disclosure has to say which mode this run was.
  assert.equal(disclosure.profile_copied_before_launch, true);
  assert.match(disclosure.note, /do not read `verified` as evidence/);
});

test('a persistent-path run discloses the absence of a copy step, still without observing', function(t) {
  const fixture = setup(t);

  const result = runOpen(fixture, 'https://application.example.test/persistent');

  assert.equal(result.status, 0, result.stderr);
  const receipt = JSON.parse(fs.readFileSync(fixture.receipt, 'utf8'));
  const disclosure = receipt.first_navigation.profile_state;

  assert.equal(receipt.profile_mode, 'persistent-path');
  assert.equal(disclosure.profile_copied_before_launch, false);
  // Still `not-observed`: no copy step is a reason the contents are unlikely to be lost,
  // not an observation that they arrived. Downgrading the risk is not the same as
  // taking a measurement, and the receipt must not blur the two.
  assert.equal(disclosure.status, 'not-observed');
  assert.match(disclosure.note, /nothing here observed the page/);
});

test('the disclosure never claims an observation the runtime did not take', function(t) {
  // The boundary. Every status this field can carry today says the same thing, because
  // nothing in this runtime observes the page's profile state. A future detector may add
  // a positive status — but it has to add the observation in the same change, and this
  // assertion is what makes shipping the word without the measurement fail.
  const observed = [];
  for (const profileMode of ['snapshot', 'persistent']) {
    const fixture = setup(t, { profileMode });
    const result = runOpen(
      fixture,
      'https://application.example.test/boundary-' + profileMode
    );
    assert.equal(result.status, 0, result.stderr);
    const receipt = JSON.parse(fs.readFileSync(fixture.receipt, 'utf8'));
    observed.push(receipt.first_navigation.profile_state.status);
  }
  assert.deepEqual(observed, ['not-observed', 'not-observed']);
});

test('verified requires a caller-declared positive projection on the captured page', function(t) {
  const fixture = setup(t, {
    profileMode: 'snapshot',
    profileProjectionValue: true,
  });
  const recorder = path.join(fixture.root, 'profile-state.js');
  fs.writeFileSync(
    recorder,
    "publishDiagnosticProjection({profile_live:{type:'boolean'}},()=>({profile_live:false}));\n"
  );

  const result = runOpen(
    fixture,
    'https://application.example.test/account',
    [recorder],
    ['--profile-liveness-projection', '0:profile_live']
  );

  assert.equal(result.status, 0, result.stderr);
  const receipt = JSON.parse(fs.readFileSync(fixture.receipt, 'utf8'));
  assert.equal(receipt.first_navigation.status, 'verified');
  assert.equal(receipt.first_navigation.profile_state.status, 'observed');
  assert.equal(receipt.first_navigation.profile_state.page_identity, 't1');
  assert.deepEqual(receipt.first_navigation.profile_state.declarations, [
    { script_index: 0, field: 'profile_live' },
  ]);
});

test('false is not a positive observation and fails closed after a bounded poll', function(t) {
  const fixture = setup(t, {
    profileMode: 'snapshot',
    profileProjectionValue: false,
  });
  const recorder = path.join(fixture.root, 'inert-profile.js');
  fs.writeFileSync(
    recorder,
    "publishDiagnosticProjection({profile_live:{type:'boolean'}},()=>({profile_live:false}));\n"
  );

  const result = runOpen(
    fixture,
    'https://application.example.test/logged-out',
    [recorder],
    ['--profile-liveness-projection', '0:profile_live']
  );

  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /declared profile liveness/i);
  const receipt = JSON.parse(fs.readFileSync(fixture.receipt, 'utf8'));
  assert.equal(receipt.first_navigation.status, 'failed');
  assert.equal(receipt.first_navigation.post.profile_state.status, 'not-observed');
  assert.ok(receipt.first_navigation.post.profile_state.attempts > 1);
  assert.ok(receipt.first_navigation.post.profile_state.waited_ms_budget > 0);
});

test('polling tolerates SPA rehydration before the positive projection appears', function(t) {
  const fixture = setup(t, {
    profileMode: 'snapshot',
    profileProjectionValue: true,
    profileProjectionAppearAfter: 4,
  });
  const recorder = path.join(fixture.root, 'http-only-dom-affordance.js');
  fs.writeFileSync(
    recorder,
    "publishDiagnosticProjection({profile_live:{type:'boolean'}},()=>({profile_live:false}));\n"
  );

  const result = runOpen(
    fixture,
    'https://application.example.test/rehydrating',
    [recorder],
    ['--profile-liveness-projection', '0:profile_live']
  );

  assert.equal(result.status, 0, result.stderr);
  const receipt = JSON.parse(fs.readFileSync(fixture.receipt, 'utf8'));
  assert.equal(receipt.first_navigation.profile_state.status, 'observed');
  assert.ok(receipt.first_navigation.profile_state.attempts > 1);
});

test('a positive projection from a different active page cannot verify navigation', function(t) {
  const fixture = setup(t, {
    profileMode: 'snapshot',
    profileProjectionValue: true,
    switchPageOnProjection: true,
  });
  const recorder = path.join(fixture.root, 'wrong-page.js');
  fs.writeFileSync(
    recorder,
    "publishDiagnosticProjection({profile_live:{type:'boolean'}},()=>({profile_live:true}));\n"
  );

  const result = runOpen(
    fixture,
    'https://application.example.test/captured-page',
    [recorder],
    ['--profile-liveness-projection', '0:profile_live']
  );

  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /page identity/i);
  const receipt = JSON.parse(fs.readFileSync(fixture.receipt, 'utf8'));
  assert.notEqual(receipt.first_navigation.status, 'verified');
});

test('a declared projection remains enforced on later navigations', function(t) {
  const fixture = setup(t, {
    profileMode: 'snapshot',
    profileProjectionValue: true,
  });
  const recorder = path.join(fixture.root, 'session-state.js');
  fs.writeFileSync(
    recorder,
    "publishDiagnosticProjection({profile_live:{type:'boolean'}},()=>({profile_live:true}));\n"
  );
  const args = ['--profile-liveness-projection', '0:profile_live'];
  assert.equal(
    runOpen(fixture, 'https://application.example.test/one', [recorder], args).status,
    0
  );
  setProfileProjection(fixture, false);

  const second = runOpen(
    fixture,
    'https://application.example.test/two',
    [recorder],
    args
  );

  assert.notEqual(second.status, 0);
  const receipt = JSON.parse(fs.readFileSync(fixture.receipt, 'utf8'));
  assert.equal(receipt.first_navigation.status, 'verified');
  assert.equal(receipt.last_navigation.status, 'failed');
  assert.equal(receipt.last_navigation.post.profile_state.status, 'not-observed');
});

test('a misplaced liveness projection is refused instead of silently ignored', function(t) {
  const fixture = setup(t, { profileMode: 'snapshot' });
  const result = runOpen(fixture, 'https://application.example.test/no-op', [], [
    'open',
    '--profile-liveness-projection',
    '0:profile_live',
  ]);

  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /must precede the browser command|misplaced no-op/i);
  assert.equal(fs.existsSync(fixture.receipt), false);
});

test('BOUNDED: a legacy receipt is left alone rather than retrofitted by a read-only command', function(t) {
  // The disclosure is written at the pending-to-verified transition, so a receipt an
  // older runtime left at `verified` does not carry it. Retrofitting was implemented and
  // removed, and this pins the removal rather than the gap: backfilling meant writing the
  // receipt from `snapshot`, `click` and `eval`, which until then only read it, and the
  // write replaced the whole object read before live ownership verification. Teammates
  // within one run share a receipt, so a `snapshot` could erase a `last_navigation` a
  // concurrent `open` had just written — destroying evidence to add a derived field.
  //
  // If a future change reintroduces the backfill, this test is where it has to argue with
  // the concurrency hazard first.
  const fixture = setup(t, { profileMode: 'snapshot' });

  const first = runOpen(fixture, 'https://application.example.test/legacy');
  assert.equal(first.status, 0, first.stderr);

  const legacy = JSON.parse(fs.readFileSync(fixture.receipt, 'utf8'));
  delete legacy.first_navigation.profile_state;
  legacy.last_navigation = { status: 'verified', sentinel: 'written-by-a-peer' };
  fs.writeFileSync(fixture.receipt, JSON.stringify(legacy, null, 2) + '\n');

  const snapshot = spawnSync(
    process.execPath,
    [
      RUNTIME,
      '--run-id', fixture.runId,
      '--app', fixture.app,
      '--executable-path', fixture.executable,
      '--profile', fixture.profile,
      '--receipt', fixture.receipt,
      'snapshot',
    ],
    { encoding: 'utf8', env: fixture.env }
  );
  assert.equal(snapshot.status, 0, snapshot.stderr);

  const after = JSON.parse(fs.readFileSync(fixture.receipt, 'utf8'));
  assert.equal(
    after.first_navigation.profile_state,
    undefined,
    'a read-only command must not retrofit the disclosure'
  );
  assert.equal(
    after.last_navigation.sentinel,
    'written-by-a-peer',
    'and must not have rewritten the receipt at all — this is the evidence-loss hazard'
  );
  // The reader is not left without the fact: `profile_mode` still says whether a copy
  // step existed, and references/commands.md states what a missing field means.
  assert.equal(after.profile_mode, 'verified-snapshot');
});

test('no profile-liveness flag is silently accepted and ignored, in either position', function(t) {
  // The reverted attempt's worst failure was a documented flag that nothing forwarded, so
  // a caller got a silent no-op while believing a guard was installed. Both argument
  // positions are covered because they took different routes: before the command the flag
  // became `command[0]` and was rejected as an unknown command, but AFTER it the flag sat
  // in the command tail, which `isAllowedCommand` never inspects — so it was discarded
  // and the run produced a verified receipt. An earlier version of this test only
  // exercised the position that already failed.
  for (const [label, argv] of [
    ['before the command', [
      '--profile-liveness-key', 'auth_token',
      'open', 'https://application.example.test/ghost-before',
    ]],
    ['in the command tail', [
      'open', 'https://application.example.test/ghost-after',
      '--profile-liveness-key', 'auth_token',
    ]],
    ['selector form in the tail', [
      'open', 'https://application.example.test/ghost-selector',
      '--profile-liveness-selector', '[data-testid="sign-out"]',
    ]],
  ]) {
    const fixture = setup(t, { profileMode: 'snapshot' });
    const result = spawnSync(
      process.execPath,
      [
        RUNTIME,
        '--run-id', fixture.runId,
        '--app', fixture.app,
        '--executable-path', fixture.executable,
        '--profile', fixture.profile,
        '--receipt', fixture.receipt,
        ...argv,
      ],
      { encoding: 'utf8', env: fixture.env }
    );

    assert.notEqual(result.status, 0, label + ': a retired liveness flag must not be ignored');
    assert.match(result.stderr, /retired flag --profile-liveness/, label + ': refused by name');
    assert.equal(
      fs.existsSync(fixture.receipt),
      false,
      label + ': it must fail before writing a receipt that would read as a verified run'
    );
  }
});

test('the refusal matches the retired option names, not anything starting with them', function(t) {
  // A prefix match would also reject a legitimate payload whose value merely begins with
  // the string. Refusing real work to catch a retired option is a worse trade than the
  // option being retired at all, so the refusal is by exact name.
  const fixture = setup(t, { profileMode: 'snapshot' });

  const result = spawnSync(
    process.execPath,
    [
      RUNTIME,
      '--run-id', fixture.runId,
      '--app', fixture.app,
      '--executable-path', fixture.executable,
      '--profile', fixture.profile,
      '--receipt', fixture.receipt,
      'eval', '--profile-liveness-key-is-retired-see-issue-149',
    ],
    { encoding: 'utf8', env: fixture.env }
  );

  assert.doesNotMatch(
    result.stderr,
    /retired flag/,
    'a data argument that merely starts with the retired name must not be refused'
  );
});

// #174. The temp-root guard tested `uid === me` and nothing else, which holds on macOS
// (per-user $TMPDIR) and fails on Linux (`/tmp` is root-owned `1777`). That rejected the
// standard configuration of an entire platform: the browser runtime could not launch on
// an ordinary Linux box, in CI or anywhere else, and nothing said so.
//
// The property the guard is actually for is that nobody else can remove or rename our
// snapshot. These pin all three ways that holds and the one way it does not, so a future
// tightening back to a uid test fails here first.

// Skipped when the process is root: `/tmp` is then owned by us, so the case this test
// exists for — a root-owned root that is NOT ours — cannot be built from the host
// filesystem. Root-running containers are common enough that leaving it to fail there
// would be a red that says nothing about the guard.
const RUNNING_AS_ROOT = process.getuid() === 0;

test('a temp root that is root-owned and sticky is accepted, as on Linux', {
  skip: RUNNING_AS_ROOT ? 'process is root, so /tmp is not a foreign-owned root' : false,
}, function(t) {
  // `/tmp` on macOS is root-owned mode 1777 — byte-for-byte the Linux shape, so this runs
  // the real condition rather than a model of it.
  const stickyRoot = fs.realpathSync('/tmp');
  const stat = fs.lstatSync(stickyRoot);
  assert.notEqual(stat.uid, process.getuid(), 'precondition: /tmp is not owned by us');
  assert.notEqual(stat.mode & 0o1000, 0, 'precondition: /tmp carries the sticky bit');

  const fixture = setup(t, { profileMode: 'snapshot' });
  fixture.env.TMPDIR = stickyRoot;

  const result = runOpen(fixture, 'https://application.example.test/sticky');

  assert.equal(result.status, 0, result.stderr);
  const receipt = JSON.parse(fs.readFileSync(fixture.receipt, 'utf8'));
  assert.equal(receipt.first_navigation.status, 'verified');
});

test('the guard refuses exactly the roots another user could swap, and no others', function() {
  // Unit-level on purpose. An earlier version drove the whole runtime with TMPDIR set to a
  // scratch directory, and on a Linux runner the socket-namespace check rejected that
  // longer path *before* this guard was reached: the run failed, the assertion on the
  // message did not, and the test was passing on the author's machine for a reason that
  // had nothing to do with what it claimed to prove. Driving the system to reach a pure
  // predicate buys nothing and couples the result to path length.
  const guard = runtimeModule.assertTempRootCannotBeHijacked;
  const me = process.getuid();
  const root = { uid: 0 };
  const stranger = { uid: me + 4242 };

  // Safe: trusted owner, and nobody else may write in the directory at all.
  guard('/safe/private', { mode: 0o40700, uid: me });
  guard('/safe/readable', { mode: 0o40755, uid: me });
  guard('/safe/root-private', { mode: 0o40755, uid: root.uid });
  // Safe: trusted owner, and sticky stops non-owners removing our entry. Linux /tmp.
  guard('/tmp', { mode: 0o41777, uid: root.uid });

  // Unsafe: group- or world-writable with no sticky bit, so our entry can be unlinked
  // by anyone who can write there.
  for (const mode of [0o40777, 0o40707, 0o40770]) {
    assert.throws(
      () => guard('/unsafe', { mode: mode, uid: me }),
      /writable by other users without the sticky bit/,
      'mode ' + mode.toString(8) + ' must be refused'
    );
  }

  // Unsafe: sticky does NOT restrain the directory's own owner, so an attacker-owned
  // 1777 root permits substitution even though it looks exactly like /tmp. This is the
  // hole the cross-model gate found in the first version of this fix, which tested
  // permissions alone.
  assert.throws(
    () => guard('/stranger-tmp', { mode: 0o41777, uid: stranger.uid }),
    /owned by another user, who may remove or rename entries in it/,
    'a sticky root owned by someone else is still swappable by its owner'
  );
  // Same for a locked-down root owned by someone else: the owner can unlink regardless.
  assert.throws(
    () => guard('/stranger-private', { mode: 0o40700, uid: stranger.uid }),
    /owned by another user/,
    'permissions do not restrain the owner'
  );

  // Both messages have to be actionable: a user hitting either needs to know what to fix.
  assert.throws(
    () => guard('/unsafe', { mode: 0o40777, uid: me }),
    /Point TMPDIR at a directory you own, or restore the sticky bit/
  );
  assert.throws(
    () => guard('/stranger-tmp', { mode: 0o41777, uid: stranger.uid }),
    /Point TMPDIR at a directory you own\./
  );
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

test('subsequent actions reject diagnostic source drift before browser execution', function(t) {
  const fixture = setup(t, { profileMode: 'snapshot' });
  const recorder = path.join(fixture.root, 'drifted-recorder.js');
  fs.writeFileSync(
    recorder,
    "publishDiagnosticProjection({ready:{type:'boolean'}},()=>({ready:true}));\n"
  );
  assert.equal(
    runOpen(
      fixture,
      'https://application.example.test/diagnostic-binding',
      [recorder]
    ).status,
    0
  );
  fs.writeFileSync(
    recorder,
    "publishDiagnosticProjection({ready:{type:'boolean'}},()=>({ready:false}));\n"
  );

  const result = spawnSync(
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
      '--diagnostic-init-script',
      recorder,
      'snapshot',
      '-i',
    ],
    { encoding: 'utf8', env: fixture.env }
  );

  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /diagnostic init script 0.*content changed/i);
  const state = JSON.parse(fs.readFileSync(fixture.statePath, 'utf8'));
  assert.equal(
    state.events.some(function(event) {
      return event.command === 'snapshot';
    }),
    false
  );
});

test('a missing agent-browser names the prerequisite instead of a version problem', function(t) {
  const fixture = setup(t);
  // Point at a path that does not exist. The `open` path probes `--version`
  // first, and until this test both "absent" and "unreadable version" produced
  // the same falsy result — so the reader was told the contract version could
  // not be verified when nothing was installed at all.
  const env = Object.assign({}, fixture.env, {
    E2E_AGENT_BROWSER_BIN: path.join(fixture.root, 'no-such-agent-browser'),
  });
  delete env.E2E_RUNTIME_TEST_MODE;

  const result = spawnSync(
    process.execPath,
    [
      RUNTIME,
      '--run-id', fixture.runId,
      '--app', fixture.app,
      '--executable-path', fixture.executable,
      '--profile', fixture.profile,
      '--receipt', fixture.receipt,
      'open',
      'about:blank',
    ],
    { encoding: 'utf8', env: env }
  );

  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /agent-browser is required and was not found/);
  assert.match(result.stderr, /npm install -g agent-browser/);
  assert.match(result.stderr, /E2E_AGENT_BROWSER_BIN/);
  // The wrong message must not be what the reader sees.
  assert.doesNotMatch(result.stderr, /lifecycle contract version/);
});
