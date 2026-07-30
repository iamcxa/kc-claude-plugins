'use strict';

const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');

const RUNTIME = path.join(__dirname, '..', '..', 'bin', 'e2e-browser-runtime.js');
const runtime = require(RUNTIME);

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

function fixture(t) {
  const browserHome = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-flow-auth-'));
  t.after(function() {
    fs.rmSync(browserHome, { recursive: true, force: true });
  });
  const canonicalProfile = path.join(browserHome, 'storefront');
  fs.mkdirSync(canonicalProfile, { recursive: true });
  fs.writeFileSync(path.join(canonicalProfile, 'Cookies'), 'canonical-cookie-bytes');
  return { browserHome, canonicalProfile };
}

test('prepares a previously absent unique profile for every replay', function(t) {
  const { browserHome, canonicalProfile } = fixture(t);
  const first = runtime.prepareFlowManagedProfile({
    browserHome,
    runId: 'run-123',
    app: 'storefront',
    canonicalProfile,
    replayId: 'aaaaaaaaaaaaaaaa',
  });
  const second = runtime.prepareFlowManagedProfile({
    browserHome,
    runId: 'run-123',
    app: 'storefront',
    canonicalProfile,
    replayId: 'bbbbbbbbbbbbbbbb',
  });

  assert.notEqual(first.profile, second.profile);
  assert.equal(fs.existsSync(first.profile), false);
  assert.equal(fs.existsSync(second.profile), false);
  assert.equal(first.freshness, 'verified-absent');
  assert.equal(first.canonical_digest, second.canonical_digest);
});

test('rejects a pre-existing requested ephemeral profile', function(t) {
  const { browserHome, canonicalProfile } = fixture(t);
  const profile = runtime.flowManagedProfilePath(
    browserHome,
    'run-123',
    'storefront',
    'aaaaaaaaaaaaaaaa'
  );
  fs.mkdirSync(profile, { recursive: true });
  fs.writeFileSync(path.join(profile, 'unexpected'), 'occupied');

  assert.throws(
    function() {
      runtime.prepareFlowManagedProfile({
        browserHome,
        runId: 'run-123',
        app: 'storefront',
        canonicalProfile,
        replayId: 'aaaaaaaaaaaaaaaa',
      });
    },
    /already exists/
  );
});

test('rejects a symlinked managed profile root', function(t) {
  const { browserHome, canonicalProfile } = fixture(t);
  const outside = path.join(browserHome, 'outside');
  const managedRoot = path.join(browserHome, 'flow-managed-profiles');
  fs.mkdirSync(outside);
  fs.symlinkSync(outside, managedRoot);

  assert.throws(
    function() {
      runtime.prepareFlowManagedProfile({
        browserHome,
        runId: 'run-123',
        app: 'storefront',
        canonicalProfile,
        replayId: 'aaaaaaaaaaaaaaaa',
      });
    },
    /symlink|owned directory/i
  );
});

test('rejects a symlinked canonical profile before browser interaction', function(t) {
  const { browserHome, canonicalProfile } = fixture(t);
  const canonicalTarget = canonicalProfile + '-target';
  fs.renameSync(canonicalProfile, canonicalTarget);
  fs.symlinkSync(canonicalTarget, canonicalProfile);

  assert.throws(
    function() {
      runtime.prepareFlowManagedProfile({
        browserHome,
        runId: 'run-123',
        app: 'storefront',
        canonicalProfile,
        replayId: 'aaaaaaaaaaaaaaaa',
      });
    },
    /canonical profile.*symlink/i
  );
  assert.equal(
    fs.existsSync(path.join(browserHome, 'flow-managed-profiles', 'storefront')),
    false
  );
});

test('flow-managed open verifies that Chrome adopted the requested profile', function(t) {
  const { browserHome, canonicalProfile } = fixture(t);
  const chromeForTesting = managedChromeForTesting(browserHome);
  const agentBrowser = path.join(browserHome, 'agent-browser');
  makeExecutable(
    agentBrowser,
    [
      '#!/usr/bin/env bash',
      'profile=""',
      'previous=""',
      'for value in "$@"; do',
      '  if [ "$previous" = "--profile" ]; then profile="$value"; fi',
      '  previous="$value"',
      'done',
      'if [ -n "$profile" ]; then',
      '  mkdir -p "$profile/Default"',
      '  printf "{}" > "$profile/Local State"',
      '  printf "{}" > "$profile/Default/Preferences"',
      'fi',
      '',
    ].join('\n')
  );
  const prepared = runtime.prepareFlowManagedProfile({
    browserHome,
    runId: 'run-123',
    app: 'storefront',
    canonicalProfile,
    replayId: 'aaaaaaaaaaaaaaaa',
  });

  const result = spawnSync(
    process.execPath,
    [
      RUNTIME,
      '--run-id', 'run-123',
      '--app', 'storefront',
      '--auth-mode', 'flow-managed',
      '--canonical-profile', canonicalProfile,
      '--profile', prepared.profile,
      '--executable-path', chromeForTesting,
      'open', 'https://example.test/auth/login',
    ],
    {
      encoding: 'utf8',
      env: Object.assign({}, process.env, {
        E2E_AGENT_BROWSER_BIN: agentBrowser,
        E2E_AGENT_BROWSER_HOME: browserHome,
      }),
    }
  );

  assert.equal(result.status, 0, result.stderr);
  const verified = runtime.verifyFlowManagedProfile({
    browserHome,
    runId: 'run-123',
    app: 'storefront',
    canonicalProfile,
    profile: prepared.profile,
  });
  assert.equal(verified.binding, 'verified');
  assert.equal(verified.status, 'active');
});

test('flow-managed open fails when the daemon does not materialize the requested profile', function(t) {
  const { browserHome, canonicalProfile } = fixture(t);
  const chromeForTesting = managedChromeForTesting(browserHome);
  const agentBrowser = path.join(browserHome, 'agent-browser');
  makeExecutable(agentBrowser, '#!/usr/bin/env bash\nexit 0\n');
  const prepared = runtime.prepareFlowManagedProfile({
    browserHome,
    runId: 'run-123',
    app: 'storefront',
    canonicalProfile,
    replayId: 'aaaaaaaaaaaaaaaa',
  });

  const result = spawnSync(
    process.execPath,
    [
      RUNTIME,
      '--run-id', 'run-123',
      '--app', 'storefront',
      '--auth-mode', 'flow-managed',
      '--canonical-profile', canonicalProfile,
      '--profile', prepared.profile,
      '--executable-path', chromeForTesting,
      'open', 'https://example.test/auth/login',
    ],
    {
      encoding: 'utf8',
      env: Object.assign({}, process.env, {
        E2E_AGENT_BROWSER_BIN: agentBrowser,
        E2E_AGENT_BROWSER_HOME: browserHome,
      }),
    }
  );

  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /did not adopt requested profile/i);
});

test('binding failure closes and removes a partially materialized owned profile', function(t) {
  const { browserHome, canonicalProfile } = fixture(t);
  const chromeForTesting = managedChromeForTesting(browserHome);
  const agentBrowser = path.join(browserHome, 'agent-browser');
  makeExecutable(
    agentBrowser,
    [
      '#!/usr/bin/env bash',
      'profile=""',
      'previous=""',
      'for value in "$@"; do',
      '  if [ "$previous" = "--profile" ]; then profile="$value"; fi',
      '  previous="$value"',
      'done',
      'if [ -n "$profile" ]; then mkdir -p "$profile"; fi',
      '',
    ].join('\n')
  );
  const prepared = runtime.prepareFlowManagedProfile({
    browserHome,
    runId: 'run-123',
    app: 'storefront',
    canonicalProfile,
    replayId: 'aaaaaaaaaaaaaaaa',
  });

  const result = spawnSync(
    process.execPath,
    [
      RUNTIME,
      '--run-id', 'run-123',
      '--app', 'storefront',
      '--auth-mode', 'flow-managed',
      '--canonical-profile', canonicalProfile,
      '--profile', prepared.profile,
      '--executable-path', chromeForTesting,
      'open', 'https://example.test/auth/login',
    ],
    {
      encoding: 'utf8',
      env: Object.assign({}, process.env, {
        E2E_AGENT_BROWSER_BIN: agentBrowser,
        E2E_AGENT_BROWSER_HOME: browserHome,
      }),
    }
  );

  assert.notEqual(result.status, 0);
  assert.equal(fs.existsSync(prepared.profile), false);
});

test('cleanup removes only the owned ephemeral profile and verifies canonical bytes', function(t) {
  const { browserHome, canonicalProfile } = fixture(t);
  const prepared = runtime.prepareFlowManagedProfile({
    browserHome,
    runId: 'run-123',
    app: 'storefront',
    canonicalProfile,
    replayId: 'aaaaaaaaaaaaaaaa',
  });
  fs.mkdirSync(path.join(prepared.profile, 'Default'), { recursive: true });
  fs.writeFileSync(path.join(prepared.profile, 'Local State'), '{}');
  fs.writeFileSync(path.join(prepared.profile, 'Default', 'Preferences'), '{}');
  runtime.markFlowManagedProfileActive({
    browserHome,
    runId: 'run-123',
    app: 'storefront',
    canonicalProfile,
    profile: prepared.profile,
  });

  const result = runtime.cleanupFlowManagedProfile({
    browserHome,
    runId: 'run-123',
    app: 'storefront',
    canonicalProfile,
    profile: prepared.profile,
  });

  assert.equal(result.cleanup, 'removed');
  assert.equal(result.canonical_profile, 'unchanged');
  assert.equal(fs.existsSync(prepared.profile), false);
  assert.equal(
    fs.readFileSync(path.join(canonicalProfile, 'Cookies'), 'utf8'),
    'canonical-cookie-bytes'
  );
});

test('cleanup refuses a profile directory replaced after binding', function(t) {
  const { browserHome, canonicalProfile } = fixture(t);
  const prepared = runtime.prepareFlowManagedProfile({
    browserHome,
    runId: 'run-123',
    app: 'storefront',
    canonicalProfile,
    replayId: 'aaaaaaaaaaaaaaaa',
  });
  fs.mkdirSync(path.join(prepared.profile, 'Default'), { recursive: true });
  fs.writeFileSync(path.join(prepared.profile, 'Local State'), '{}');
  runtime.markFlowManagedProfileActive({
    browserHome,
    runId: 'run-123',
    app: 'storefront',
    canonicalProfile,
    profile: prepared.profile,
  });
  const original = prepared.profile + '-original';
  fs.renameSync(prepared.profile, original);
  fs.mkdirSync(prepared.profile);
  fs.writeFileSync(path.join(prepared.profile, 'do-not-delete'), 'replacement');

  assert.throws(
    function() {
      runtime.cleanupFlowManagedProfile({
        browserHome,
        runId: 'run-123',
        app: 'storefront',
        canonicalProfile,
        profile: prepared.profile,
      });
    },
    /replaced|identity/i
  );
  assert.equal(
    fs.readFileSync(path.join(prepared.profile, 'do-not-delete'), 'utf8'),
    'replacement'
  );
});

test('activation refuses to replace an existing active replay binding', function(t) {
  const { browserHome, canonicalProfile } = fixture(t);

  function materialize(replayId) {
    const prepared = runtime.prepareFlowManagedProfile({
      browserHome,
      runId: 'run-123',
      app: 'storefront',
      canonicalProfile,
      replayId,
    });
    fs.mkdirSync(path.join(prepared.profile, 'Default'), { recursive: true });
    fs.writeFileSync(path.join(prepared.profile, 'Local State'), '{}');
    return prepared;
  }

  const active = materialize('aaaaaaaaaaaaaaaa');
  runtime.markFlowManagedProfileActive({
    browserHome,
    runId: 'run-123',
    app: 'storefront',
    canonicalProfile,
    profile: active.profile,
  });
  const candidate = materialize('bbbbbbbbbbbbbbbb');

  assert.throws(
    function() {
      runtime.markFlowManagedProfileActive({
        browserHome,
        runId: 'run-123',
        app: 'storefront',
        canonicalProfile,
        profile: candidate.profile,
      });
    },
    /another flow-managed profile is active/i
  );
  assert.equal(
    runtime.verifyFlowManagedProfile({
      browserHome,
      runId: 'run-123',
      app: 'storefront',
      canonicalProfile,
      profile: active.profile,
    }).binding,
    'verified'
  );
});

test('open and close reject a new replay before browser interaction while another binding is active', function(t) {
  const { browserHome, canonicalProfile } = fixture(t);
  const chromeForTesting = managedChromeForTesting(browserHome);
  const browserLog = path.join(browserHome, 'agent-browser.log');
  const agentBrowser = path.join(browserHome, 'agent-browser');
  makeExecutable(
    agentBrowser,
    [
      '#!/usr/bin/env bash',
      'printf "%s\\n" "$*" >> "$E2E_AGENT_BROWSER_LOG"',
      '',
    ].join('\n')
  );

  function materialize(replayId) {
    const prepared = runtime.prepareFlowManagedProfile({
      browserHome,
      runId: 'run-123',
      app: 'storefront',
      canonicalProfile,
      replayId,
    });
    fs.mkdirSync(path.join(prepared.profile, 'Default'), { recursive: true });
    fs.writeFileSync(path.join(prepared.profile, 'Local State'), '{}');
    return prepared;
  }

  const active = materialize('aaaaaaaaaaaaaaaa');
  runtime.markFlowManagedProfileActive({
    browserHome,
    runId: 'run-123',
    app: 'storefront',
    canonicalProfile,
    profile: active.profile,
  });
  const candidate = runtime.prepareFlowManagedProfile({
    browserHome,
    runId: 'run-123',
    app: 'storefront',
    canonicalProfile,
    replayId: 'bbbbbbbbbbbbbbbb',
  });

  for (const command of [
    ['close'],
    ['open', 'https://example.test/auth/login'],
  ]) {
    const result = spawnSync(
      process.execPath,
      [
        RUNTIME,
        '--run-id', 'run-123',
        '--app', 'storefront',
        '--auth-mode', 'flow-managed',
        '--canonical-profile', canonicalProfile,
        '--profile', candidate.profile,
        '--executable-path', chromeForTesting,
        ...command,
      ],
      {
        encoding: 'utf8',
        env: Object.assign({}, process.env, {
          E2E_AGENT_BROWSER_BIN: agentBrowser,
          E2E_AGENT_BROWSER_HOME: browserHome,
          E2E_AGENT_BROWSER_LOG: browserLog,
        }),
      }
    );

    assert.notEqual(result.status, 0);
    assert.match(result.stderr, /another flow-managed profile is active|stale/i);
    assert.equal(
      fs.existsSync(browserLog),
      false,
      'rejected ' + command[0] + ' must not invoke agent-browser'
    );
  }
  assert.equal(
    runtime.verifyFlowManagedProfile({
      browserHome,
      runId: 'run-123',
      app: 'storefront',
      canonicalProfile,
      profile: active.profile,
    }).binding,
    'verified'
  );
});

test('stale cleanup cannot close a newer active replay profile', function(t) {
  const { browserHome, canonicalProfile } = fixture(t);
  const closeLog = path.join(browserHome, 'agent-browser.log');
  const agentBrowser = path.join(browserHome, 'agent-browser');
  makeExecutable(
    agentBrowser,
    [
      '#!/usr/bin/env bash',
      'printf "%s\\n" "$*" >> "$E2E_AGENT_BROWSER_LOG"',
      '',
    ].join('\n')
  );

  function activate(replayId) {
    const prepared = runtime.prepareFlowManagedProfile({
      browserHome,
      runId: 'run-123',
      app: 'storefront',
      canonicalProfile,
      replayId,
    });
    fs.mkdirSync(path.join(prepared.profile, 'Default'), { recursive: true });
    fs.writeFileSync(path.join(prepared.profile, 'Local State'), '{}');
    runtime.markFlowManagedProfileActive({
      browserHome,
      runId: 'run-123',
      app: 'storefront',
      canonicalProfile,
      profile: prepared.profile,
    });
    return prepared;
  }

  const stale = activate('aaaaaaaaaaaaaaaa');
  fs.unlinkSync(
    path.join(
      browserHome,
      'flow-managed-state',
      'run-123',
      'storefront',
      'active-profile.json'
    )
  );
  const current = activate('bbbbbbbbbbbbbbbb');
  const result = spawnSync(
    process.execPath,
    [
      RUNTIME,
      '--run-id', 'run-123',
      '--app', 'storefront',
      '--auth-mode', 'flow-managed',
      '--canonical-profile', canonicalProfile,
      '--profile', stale.profile,
      'cleanup-flow-managed-profile',
    ],
    {
      encoding: 'utf8',
      env: Object.assign({}, process.env, {
        E2E_AGENT_BROWSER_BIN: agentBrowser,
        E2E_AGENT_BROWSER_HOME: browserHome,
        E2E_AGENT_BROWSER_LOG: closeLog,
      }),
    }
  );

  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /stale|active binding/i);
  assert.equal(fs.existsSync(closeLog), false, 'stale cleanup must fail before close');
  assert.equal(fs.existsSync(stale.profile), true);
  assert.equal(fs.existsSync(current.profile), true);
  assert.equal(
    runtime.verifyFlowManagedProfile({
      browserHome,
      runId: 'run-123',
      app: 'storefront',
      canonicalProfile,
      profile: current.profile,
    }).binding,
    'verified'
  );
});

test('duplicate cleanup is rejected before close and cannot close a newer replay', function(t) {
  const { browserHome, canonicalProfile } = fixture(t);
  const closeLog = path.join(browserHome, 'agent-browser.log');
  const agentBrowser = path.join(browserHome, 'agent-browser');
  makeExecutable(
    agentBrowser,
    [
      '#!/usr/bin/env bash',
      'printf "%s\\n" "$*" >> "$E2E_AGENT_BROWSER_LOG"',
      '',
    ].join('\n')
  );

  function activate(replayId) {
    const prepared = runtime.prepareFlowManagedProfile({
      browserHome,
      runId: 'run-123',
      app: 'storefront',
      canonicalProfile,
      replayId,
    });
    fs.mkdirSync(path.join(prepared.profile, 'Default'), { recursive: true });
    fs.writeFileSync(path.join(prepared.profile, 'Local State'), '{}');
    runtime.markFlowManagedProfileActive({
      browserHome,
      runId: 'run-123',
      app: 'storefront',
      canonicalProfile,
      profile: prepared.profile,
    });
    return prepared;
  }

  const completed = activate('aaaaaaaaaaaaaaaa');
  runtime.cleanupFlowManagedProfile({
    browserHome,
    runId: 'run-123',
    app: 'storefront',
    canonicalProfile,
    profile: completed.profile,
  });
  const current = activate('bbbbbbbbbbbbbbbb');

  const result = spawnSync(
    process.execPath,
    [
      RUNTIME,
      '--run-id', 'run-123',
      '--app', 'storefront',
      '--auth-mode', 'flow-managed',
      '--canonical-profile', canonicalProfile,
      '--profile', completed.profile,
      'cleanup-flow-managed-profile',
    ],
    {
      encoding: 'utf8',
      env: Object.assign({}, process.env, {
        E2E_AGENT_BROWSER_BIN: agentBrowser,
        E2E_AGENT_BROWSER_HOME: browserHome,
        E2E_AGENT_BROWSER_LOG: closeLog,
      }),
    }
  );

  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /active|lifecycle state/i);
  assert.equal(fs.existsSync(closeLog), false, 'duplicate cleanup must fail before close');
  assert.equal(fs.existsSync(current.profile), true);
  assert.equal(
    runtime.verifyFlowManagedProfile({
      browserHome,
      runId: 'run-123',
      app: 'storefront',
      canonicalProfile,
      profile: current.profile,
    }).binding,
    'verified'
  );
});
