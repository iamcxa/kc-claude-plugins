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

/** Configure what the fixture's synthetic page will report for the liveness probe. */
function setFixtureLiveness(fixture, liveness) {
  const state = JSON.parse(fs.readFileSync(fixture.statePath, 'utf8'));
  state.profileLiveness = liveness;
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

// #149. The receipt used to reach `verified` on the strength of the init script having
// attached, which is evidence about the recorder and says nothing about whether the
// browser populated the origin from the profile. agent-browser 0.32 snapshot mode drops
// Local Storage, so a run against a pre-authenticated profile behaved as a logged-out
// visitor start to finish while the artifact stayed green.
//
// The first attempt at this counted origin state and refused when it found none. It was
// reverted: counting cannot separate state the profile carried from state the page minted
// on load, so a dropped profile passed whenever the app set any cookie of its own. These
// cases pin the replacement — a caller-declared observation — and the boundary that the
// runtime never invents a claim the caller did not make.

test('a declared localStorage key that survived is recorded and verifies', function(t) {
  const fixture = setup(t, { profileMode: 'snapshot' });
  setFixtureLiveness(fixture, {
    origin: 'https://application.example.test',
    keys: ['auth_token'],
    selectors: [],
  });

  const result = runOpen(fixture, 'https://application.example.test/live', [], [
    '--profile-liveness-key', 'auth_token',
  ]);

  assert.equal(result.status, 0, result.stderr);
  const receipt = JSON.parse(fs.readFileSync(fixture.receipt, 'utf8'));
  assert.equal(receipt.first_navigation.status, 'verified');
  assert.equal(receipt.first_navigation.profile_liveness.status, 'observed');
  assert.deepEqual(receipt.first_navigation.profile_liveness.keys, [
    { name: 'auth_token', result: 'present' },
  ]);
});

test('a declared key the dropped snapshot did not carry fails closed', function(t) {
  const fixture = setup(t, { profileMode: 'snapshot' });
  // The reverted design's blind spot, made explicit: the page HAS state — an anonymous
  // session key it minted itself — and the profile's key is still gone. Counting saw
  // "1 key, nonzero, fine". A declared observation sees the one that matters.
  setFixtureLiveness(fixture, {
    origin: 'https://application.example.test',
    keys: ['anon_session_id'],
    selectors: [],
  });

  const result = runOpen(fixture, 'https://application.example.test/inert', [], [
    '--profile-liveness-key', 'auth_token',
  ]);

  assert.notEqual(result.status, 0);
  const receipt = JSON.parse(fs.readFileSync(fixture.receipt, 'utf8'));
  assert.equal(receipt.status, 'failed');
  assert.equal(receipt.failure_class, 'infrastructure');
  assert.match(receipt.error, /declared profile liveness was not observed/);
  assert.match(receipt.error, /auth_token=absent/);
  assert.notEqual(receipt.first_navigation.status, 'verified');
});

test('a declared authenticated-only affordance covers HttpOnly-cookie sessions', function(t) {
  // The other half of why counting failed: `document.cookie` cannot see HttpOnly
  // cookies, so a session carried entirely by one read as empty storage and a WORKING
  // run would have been refused. A DOM affordance is observable regardless of where the
  // session actually lives.
  const fixture = setup(t, { profileMode: 'snapshot' });
  setFixtureLiveness(fixture, {
    origin: 'https://application.example.test',
    keys: [],
    selectors: ['[data-testid="sign-out"]'],
  });

  const result = runOpen(fixture, 'https://application.example.test/httponly', [], [
    '--profile-liveness-selector', '[data-testid="sign-out"]',
  ]);

  assert.equal(result.status, 0, result.stderr);
  const receipt = JSON.parse(fs.readFileSync(fixture.receipt, 'utf8'));
  assert.equal(receipt.first_navigation.profile_liveness.status, 'observed');
  assert.deepEqual(receipt.first_navigation.profile_liveness.selectors, [
    { name: '[data-testid="sign-out"]', result: 'present' },
  ]);
});

test('a storage read that refuses does not satisfy a declared key', function(t) {
  const fixture = setup(t, { profileMode: 'snapshot' });
  setFixtureLiveness(fixture, { mode: 'storage-throws', keys: [], selectors: [] });

  const result = runOpen(fixture, 'https://application.example.test/refused', [], [
    '--profile-liveness-key', 'auth_token',
  ]);

  assert.notEqual(result.status, 0);
  const receipt = JSON.parse(fs.readFileSync(fixture.receipt, 'utf8'));
  assert.equal(receipt.failure_class, 'infrastructure');
  // `unreadable`, not `absent` — the probe distinguishes them — but a declared assertion
  // is unsatisfied either way, because neither is the positive observation `verified`
  // was made contingent on.
  assert.match(receipt.error, /auth_token=unreadable/);
});

test('a late-rendering affordance is polled for, not sampled once', function(t) {
  // codex: an SPA rehydrating from an HttpOnly cookie has to finish a round trip before
  // it renders anything authenticated-only, so a one-shot probe fails valid profiles
  // nondeterministically — which would have made this guard the very flake class the
  // rest of this sprint removed. The fixture withholds the affordance for the first
  // three samples; only a polling probe gets past it.
  const fixture = setup(t, { profileMode: 'snapshot' });
  setFixtureLiveness(fixture, {
    origin: 'https://application.example.test',
    keys: [],
    selectors: ['[data-testid="sign-out"]'],
    appearAfter: 3,
  });

  const result = runOpen(fixture, 'https://application.example.test/spa', [], [
    '--profile-liveness-selector', '[data-testid="sign-out"]',
  ]);

  assert.equal(result.status, 0, result.stderr);
  const receipt = JSON.parse(fs.readFileSync(fixture.receipt, 'utf8'));
  assert.equal(receipt.first_navigation.profile_liveness.status, 'observed');
  assert.ok(
    receipt.first_navigation.profile_liveness.attempts > 1,
    'the probe must have sampled more than once'
  );
});

test('a declared assertion is checked on a later open, not only the first', function(t) {
  // codex: liveness was evaluated only while `first_navigation` was pending, so a
  // declared flag on any subsequent `open` silently succeeded without checking or
  // recording anything. A declared claim going quietly unverified is this issue's own
  // defect class, one navigation over.
  const fixture = setup(t, { profileMode: 'snapshot' });
  setFixtureLiveness(fixture, {
    origin: 'https://application.example.test',
    keys: ['auth_token'],
    selectors: [],
  });

  const first = runOpen(fixture, 'https://application.example.test/one', [], [
    '--profile-liveness-key', 'auth_token',
  ]);
  assert.equal(first.status, 0, first.stderr);

  // The session drops between navigations.
  setFixtureLiveness(fixture, {
    origin: 'https://application.example.test',
    keys: [],
    selectors: [],
  });

  const second = runOpen(fixture, 'https://application.example.test/two', [], [
    '--profile-liveness-key', 'auth_token',
  ]);

  assert.notEqual(second.status, 0, 'a later navigation must still check what it declares');
  const receipt = JSON.parse(fs.readFileSync(fixture.receipt, 'utf8'));
  assert.match(receipt.error, /auth_token=absent/);

  // The failure is recorded where it happened. `failLifecycleReceipt` is
  // first-navigation-shaped — it rewrites `first_navigation` to failed and replaces its
  // `post` — so using it here would backdate the failure onto a navigation that genuinely
  // verified, overwrite that navigation's evidence with a different page's, and leave no
  // record of the navigation that actually failed.
  assert.equal(receipt.status, 'failed');
  assert.equal(receipt.last_navigation.status, 'failed');
  assert.equal(
    receipt.first_navigation.status,
    'verified',
    'a later failure must not rewrite a first navigation that was earned'
  );
  assert.equal(
    receipt.first_navigation.post.url,
    'https://application.example.test/one',
    "first_navigation's evidence must still be its own page"
  );
});

test('a liveness probe transport failure on a later navigation is recorded, not silent', function(t) {
  // codex: only the assertion was inside the recording path, so an `eval` transport
  // failure or an incomplete payload threw straight out — the command exited
  // unsuccessfully while the receipt still read as verified from the previous
  // navigation. A green artifact for a failed run is the exact shape this issue is about.
  const fixture = setup(t, { profileMode: 'snapshot' });
  setFixtureLiveness(fixture, {
    origin: 'https://application.example.test',
    keys: ['auth_token'],
    selectors: [],
  });

  const first = runOpen(fixture, 'https://application.example.test/one', [], [
    '--profile-liveness-key', 'auth_token',
  ]);
  assert.equal(first.status, 0, first.stderr);

  // Make the probe itself fail rather than merely report absence.
  setFixtureLiveness(fixture, { mode: 'probe-broken', keys: [], selectors: [] });

  const second = runOpen(fixture, 'https://application.example.test/two', [], [
    '--profile-liveness-key', 'auth_token',
  ]);

  assert.notEqual(second.status, 0);
  const receipt = JSON.parse(fs.readFileSync(fixture.receipt, 'utf8'));
  assert.equal(receipt.status, 'failed', 'the receipt must not still read as verified');
  assert.equal(receipt.last_navigation.status, 'failed');
  assert.equal(receipt.first_navigation.status, 'verified');
});

test('OPAQUE ORIGIN: the storage lookup stays inside the guard', function(t) {
  // codex found that the predecessor read `localStorage` at a call site OUTSIDE the
  // guard, so on an opaque origin the getter threw before `try` was entered and the
  // documented `unreadable` path was unreachable in a real browser.
  //
  // This cannot be tested through the integration fixture: it evaluates the expression
  // with `vm`, and `vm` does not forward a throwing getter from a sandbox object — it
  // yields `undefined`, so the access never throws and BOTH guard placements produce
  // `unreadable` for the wrong reason. Measured, not assumed; a fixture-based version of
  // this test passed against the very regression it was written to catch.
  //
  // So the expression is evaluated in-process against a real throwing getter instead.
  const throwingGlobal = { location: { origin: 'https://opaque.test' }, document: { querySelector: () => null } };
  Object.defineProperty(throwingGlobal, 'localStorage', {
    get() { throw new Error('SecurityError: localStorage is not available'); },
  });

  // Harness self-check first. If this stops throwing, the test below proves nothing —
  // which is exactly the failure mode being guarded against.
  assert.throws(() => throwingGlobal.localStorage, /SecurityError/,
    'harness must model an origin where property ACCESS throws');

  const expression = runtimeModule.profileLivenessExpression(['auth_token'], []);
  // `new Function` on a built string is the injection shape, and here the string is the
  // module's own output from JSON-encoded literals, in a test, with no external input.
  // Evaluating the real emitted expression is the whole point: a hand-copied equivalent
  // would pass while the shipped one regressed. `globalThis` is a parameter so the stub
  // shadows the real global.
  // eslint-disable-next-line no-new-func
  const evaluate = new Function('globalThis', 'return ' + expression);

  const observed = evaluate(throwingGlobal);
  assert.deepEqual(observed.keys, [{ name: 'auth_token', result: 'unreadable' }]);
});

test('with nothing declared the receipt says so instead of implying a profile proof', function(t) {
  const fixture = setup(t, { profileMode: 'snapshot' });

  const result = runOpen(fixture, 'https://application.example.test/undeclared');

  // The run is not refused: a caller that never named what the profile should carry has
  // made no claim the runtime can check, and inventing one is what the reverted attempt
  // got wrong. What changes is that the artifact stops being silent — this issue's
  // complaint was that a reviewer could not tell "profile restored" from "profile
  // silently absent", and `not-asserted` tells them which one they are looking at.
  assert.equal(result.status, 0, result.stderr);
  const receipt = JSON.parse(fs.readFileSync(fixture.receipt, 'utf8'));
  assert.equal(receipt.first_navigation.status, 'verified');
  assert.equal(receipt.first_navigation.profile_liveness.status, 'not-asserted');
  assert.match(receipt.first_navigation.profile_liveness.note, /no evidence|carries no evidence/);
});

test('a liveness value cannot break out of the expression it is embedded in', function(t) {
  const fixture = setup(t, { profileMode: 'snapshot' });
  setFixtureLiveness(fixture, {
    origin: 'https://application.example.test',
    keys: ['"] ); globalThis.pwned = 1; //'],
    selectors: [],
  });

  const result = runOpen(fixture, 'https://application.example.test/injection', [], [
    '--profile-liveness-key', '"] ); globalThis.pwned = 1; //',
  ]);

  // The value is JSON-encoded into the expression, so it stays a string operand. It
  // matches the fixture's present key, so the run verifies — the point is that it was
  // compared as data rather than executed as code.
  assert.equal(result.status, 0, result.stderr);
  const receipt = JSON.parse(fs.readFileSync(fixture.receipt, 'utf8'));
  assert.equal(receipt.first_navigation.profile_liveness.status, 'observed');
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
