'use strict';

const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');

const RUNTIME = path.join(__dirname, '..', '..', 'bin', 'e2e-browser-runtime.js');

function makeExecutable(filePath, source) {
  fs.writeFileSync(filePath, source, { mode: 0o755 });
}

function managedChromeForTesting(browserHome, relativeExecutable) {
  const executablePath = path.join(
    browserHome,
    'browsers',
    'chrome-151.0.2.1',
    ...(relativeExecutable || [
      'chrome-mac-arm64',
      'Google Chrome for Testing.app',
      'Contents',
      'MacOS',
      'Google Chrome for Testing',
    ])
  );
  fs.mkdirSync(path.dirname(executablePath), { recursive: true });
  makeExecutable(executablePath, '#!/usr/bin/env bash\nexit 0\n');
  return executablePath;
}

function documentedRuntimeCommands() {
  const sources = [
    fs.readFileSync(
      path.join(__dirname, '..', '..', 'agents', 'e2e-test-runner.md'),
      'utf8'
    ),
    fs.readFileSync(
      path.join(__dirname, '..', '..', 'references', 'commands.md'),
      'utf8'
    ),
  ];
  const commands = new Set();
  const pattern =
    /(?:\{\{browser_command\}\}|\{\{runtime_base_command\}\}|e2e_browser)\s+(--version|[a-z][a-z-]*)/g;
  for (const source of sources) {
    for (const match of source.matchAll(pattern)) commands.add(match[1]);
  }
  return Array.from(commands)
    .filter(function(command) {
      return ![
        'cleanup-flow-managed-profile',
        'verify-flow-managed-profile',
      ].includes(command);
    })
    .sort();
}

test('open pins Chrome for Testing inside a run-scoped daemon namespace', function(t) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-browser-runtime-'));
  t.after(function() {
    fs.rmSync(dir, { recursive: true, force: true });
  });

  const browserLog = path.join(dir, 'browser.log');
  const agentBrowser = path.join(dir, 'agent-browser');
  const chromeForTesting = managedChromeForTesting(dir);
  makeExecutable(
    agentBrowser,
    '#!/usr/bin/env bash\nprintf \'%s\\n\' \"$@\" > \"$E2E_TEST_BROWSER_LOG\"\n'
  );
  const result = spawnSync(
    process.execPath,
    [
      RUNTIME,
      '--run-id', 'run-123',
      '--app', 'storefront',
      '--executable-path', chromeForTesting,
      '--profile', path.join(dir, 'profile'),
      '--headed',
      'open', 'https://example.test',
    ],
    {
      encoding: 'utf8',
      env: Object.assign({}, process.env, {
        E2E_AGENT_BROWSER_BIN: agentBrowser,
        E2E_AGENT_BROWSER_HOME: dir,
        E2E_TEST_BROWSER_LOG: browserLog,
      }),
    }
  );

  assert.equal(result.status, 0, result.stderr);
  assert.deepEqual(fs.readFileSync(browserLog, 'utf8').trim().split('\n'), [
    '--namespace',
    'e2e-run-123',
    '--session',
    'storefront',
    '--config',
    path.join(__dirname, '..', '..', 'references', 'agent-browser-runtime.json'),
    '--engine',
    'chrome',
    '--executable-path',
    chromeForTesting,
    '--profile',
    path.join(dir, 'profile'),
    '--headed',
    'open',
    'https://example.test',
  ]);
});

test('overrides inherited browser attachment settings with the owned runtime contract', function(t) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-browser-runtime-'));
  t.after(function() {
    fs.rmSync(dir, { recursive: true, force: true });
  });

  const browserLog = path.join(dir, 'browser.log');
  const environmentLog = path.join(dir, 'environment.log');
  const agentBrowser = path.join(dir, 'agent-browser');
  const chromeForTesting = managedChromeForTesting(dir);
  makeExecutable(
    agentBrowser,
    [
      '#!/usr/bin/env bash',
      'printf \'%s\\n\' "$@" > "$E2E_TEST_BROWSER_LOG"',
      'printf \'%s|%s|%s|%s\\n\' "${AGENT_BROWSER_AUTO_CONNECT-unset}" "${AGENT_BROWSER_CDP-unset}" "${AGENT_BROWSER_PROVIDER-unset}" "${AGENT_BROWSER_CONFIG-unset}" > "$E2E_TEST_ENV_LOG"',
      '',
    ].join('\n')
  );
  const result = spawnSync(
    process.execPath,
    [
      RUNTIME,
      '--run-id', 'run-123',
      '--app', 'storefront',
      '--executable-path', chromeForTesting,
      'open', 'https://example.test',
    ],
    {
      encoding: 'utf8',
      env: Object.assign({}, process.env, {
        AGENT_BROWSER_AUTO_CONNECT: '1',
        AGENT_BROWSER_CDP: '9222',
        AGENT_BROWSER_CONFIG: path.join(dir, 'unsafe.json'),
        AGENT_BROWSER_PROVIDER: 'browserbase',
        E2E_AGENT_BROWSER_BIN: agentBrowser,
        E2E_AGENT_BROWSER_HOME: dir,
        E2E_TEST_BROWSER_LOG: browserLog,
        E2E_TEST_ENV_LOG: environmentLog,
      }),
    }
  );

  assert.equal(result.status, 0, result.stderr);
  assert.equal(
    fs.readFileSync(environmentLog, 'utf8').trim(),
    'unset|unset|unset|' +
      path.join(__dirname, '..', '..', 'references', 'agent-browser-runtime.json')
  );
  const args = fs.readFileSync(browserLog, 'utf8').trim().split('\n');
  assert.deepEqual(args.slice(4, 8), [
    '--config',
    path.join(__dirname, '..', '..', 'references', 'agent-browser-runtime.json'),
    '--engine',
    'chrome',
  ]);
  assert.equal(args.includes('--auto-connect'), false);
  assert.equal(args.includes('--cdp'), false);
});

test('rejects protected runtime options anywhere in child argv', function(t) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-browser-runtime-'));
  t.after(function() {
    fs.rmSync(dir, { recursive: true, force: true });
  });

  const browserLog = path.join(dir, 'browser.log');
  const agentBrowser = path.join(dir, 'agent-browser');
  const chromeForTesting = managedChromeForTesting(dir);
  makeExecutable(
    agentBrowser,
    '#!/usr/bin/env bash\nprintf \'invoked\\n\' >> \"$E2E_TEST_BROWSER_LOG\"\n'
  );
  for (const command of [
    ['open', 'https://example.test', '--namespace', 'other'],
    ['open', 'https://example.test', '--namespace=other'],
    ['open', 'https://example.test', '--session', 'other'],
    ['open', 'https://example.test', '--session=other'],
    ['open', 'https://example.test', '--config', '/tmp/other.json'],
    ['open', 'https://example.test', '--config=/tmp/other.json'],
    ['open', 'https://example.test', '--engine', 'lightpanda'],
    ['open', 'https://example.test', '--engine=lightpanda'],
    ['open', 'https://example.test', '--executable-path', '/Applications/Dia.app'],
    ['open', 'https://example.test', '--executable-path=/Applications/Dia.app'],
    ['open', 'https://example.test', '--provider', 'browserbase'],
    ['open', 'https://example.test', '--provider=browserbase'],
    ['open', 'https://example.test', '-p', 'browserbase'],
    ['open', 'https://example.test', '-p=browserbase'],
    ['open', 'https://example.test', '--profile', 'Default'],
    ['open', 'https://example.test', '--profile=Default'],
    ['open', 'https://example.test', '--headed'],
    ['open', 'https://example.test', '--headed=false'],
    ['open', 'https://example.test', '--auto-connect'],
    ['open', 'https://example.test', '--auto-connect=true'],
    ['open', 'https://example.test', '--auto-connect=false'],
    ['snapshot', '--cdp', '9222'],
    ['snapshot', '--cdp=9222'],
    ['connect', '9222'],
    ['open', 'https://example.test', '--all'],
    ['open', 'https://example.test', '--all=true'],
    ['close', '--all'],
    ['close', '--all=true'],
  ]) {
    const result = spawnSync(
      process.execPath,
      [
        RUNTIME,
        '--run-id', 'run-123',
        '--app', 'storefront',
        '--executable-path', chromeForTesting,
      ].concat(command),
      {
        encoding: 'utf8',
        env: Object.assign({}, process.env, {
          E2E_AGENT_BROWSER_BIN: agentBrowser,
          E2E_AGENT_BROWSER_HOME: dir,
          E2E_TEST_BROWSER_LOG: browserLog,
        }),
      }
    );

    assert.notEqual(result.status, 0, command.join(' '));
    assert.match(result.stderr, /protected|CDP|auto-connect/i);
  }
  assert.equal(fs.existsSync(browserLog), false);
});

test('allows connect as a literal command operand', function(t) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-browser-runtime-'));
  t.after(function() {
    fs.rmSync(dir, { recursive: true, force: true });
  });

  const browserLog = path.join(dir, 'browser.log');
  const agentBrowser = path.join(dir, 'agent-browser');
  const chromeForTesting = managedChromeForTesting(dir);
  makeExecutable(
    agentBrowser,
    '#!/usr/bin/env bash\nprintf \'%s\\n\' "$@" > "$E2E_TEST_BROWSER_LOG"\n'
  );

  const result = spawnSync(
    process.execPath,
    [
      RUNTIME,
      '--run-id', 'run-123',
      '--app', 'storefront',
      '--executable-path', chromeForTesting,
      'fill', '@e1', 'connect',
    ],
    {
      encoding: 'utf8',
      env: Object.assign({}, process.env, {
        E2E_AGENT_BROWSER_BIN: agentBrowser,
        E2E_AGENT_BROWSER_HOME: dir,
        E2E_TEST_BROWSER_LOG: browserLog,
      }),
    }
  );

  assert.equal(result.status, 0, result.stderr);
  assert.deepEqual(fs.readFileSync(browserLog, 'utf8').trim().split('\n').slice(-3), [
    'fill',
    '@e1',
    'connect',
  ]);
});

test('rejects batch argv and stdin programs before invoking agent-browser', function(t) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-browser-runtime-'));
  t.after(function() {
    fs.rmSync(dir, { recursive: true, force: true });
  });

  const browserLog = path.join(dir, 'browser.log');
  const agentBrowser = path.join(dir, 'agent-browser');
  const chromeForTesting = managedChromeForTesting(dir);
  makeExecutable(
    agentBrowser,
    '#!/usr/bin/env bash\nprintf \'invoked\\n\' >> "$E2E_TEST_BROWSER_LOG"\n'
  );
  const baseArgs = [
    RUNTIME,
    '--run-id', 'run-123',
    '--app', 'storefront',
    '--executable-path', chromeForTesting,
  ];
  const childEnvironment = Object.assign({}, process.env, {
    E2E_AGENT_BROWSER_BIN: agentBrowser,
    E2E_AGENT_BROWSER_HOME: dir,
    E2E_TEST_BROWSER_LOG: browserLog,
  });
  const argvProgram = spawnSync(
    process.execPath,
    baseArgs.concat(['batch', '--bail', 'connect 9222']),
    { encoding: 'utf8', env: childEnvironment }
  );
  const stdinProgram = spawnSync(
    process.execPath,
    baseArgs.concat(['batch']),
    {
      encoding: 'utf8',
      env: childEnvironment,
      input: '{"commands":["connect 9222"]}\n',
    }
  );

  assert.notEqual(argvProgram.status, 0);
  assert.match(argvProgram.stderr, /command.*not allowed/i);
  assert.notEqual(stdinProgram.status, 0);
  assert.match(stdinProgram.stderr, /command.*not allowed/i);
  assert.equal(fs.existsSync(browserLog), false);
});

test('allows every command family referenced by e2e-test runtime surfaces', function(t) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-browser-runtime-'));
  t.after(function() {
    fs.rmSync(dir, { recursive: true, force: true });
  });

  const browserLog = path.join(dir, 'browser.log');
  const agentBrowser = path.join(dir, 'agent-browser');
  const chromeForTesting = managedChromeForTesting(dir);
  makeExecutable(
    agentBrowser,
    '#!/usr/bin/env bash\nprintf \'invoked\\n\' >> "$E2E_TEST_BROWSER_LOG"\n'
  );
  const commands = documentedRuntimeCommands();

  assert.deepEqual(commands, [
    '--version',
    'back',
    'check',
    'click',
    'close',
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
  for (const command of commands) {
    const result = spawnSync(
      process.execPath,
      [
        RUNTIME,
        '--run-id', 'run-123',
        '--app', 'storefront',
        '--executable-path', chromeForTesting,
        command,
      ],
      {
        encoding: 'utf8',
        env: Object.assign({}, process.env, {
          E2E_AGENT_BROWSER_BIN: agentBrowser,
          E2E_AGENT_BROWSER_HOME: dir,
          E2E_TEST_BROWSER_LOG: browserLog,
        }),
      }
    );
    assert.equal(result.status, 0, command + ': ' + result.stderr);
  }
});

test('fails closed when the Chrome for Testing executable is unavailable', function(t) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-browser-runtime-'));
  t.after(function() {
    fs.rmSync(dir, { recursive: true, force: true });
  });

  const browserLog = path.join(dir, 'browser.log');
  const agentBrowser = path.join(dir, 'agent-browser');
  makeExecutable(
    agentBrowser,
    '#!/usr/bin/env bash\nprintf \'invoked\\n\' >> \"$E2E_TEST_BROWSER_LOG\"\n'
  );

  const result = spawnSync(
    process.execPath,
    [
      RUNTIME,
      '--run-id', 'run-123',
      '--app', 'storefront',
      '--executable-path', path.join(dir, 'missing Chrome for Testing'),
      'open', 'https://example.test',
    ],
    {
      encoding: 'utf8',
      env: Object.assign({}, process.env, {
        E2E_AGENT_BROWSER_BIN: agentBrowser,
        E2E_TEST_BROWSER_LOG: browserLog,
      }),
    }
  );

  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /Chrome for Testing executable.*unavailable/i);
  assert.equal(fs.existsSync(browserLog), false);
});

test('discovers the newest installed Chrome for Testing when no path is supplied', function(t) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-browser-runtime-'));
  t.after(function() {
    fs.rmSync(dir, { recursive: true, force: true });
  });

  const browserLog = path.join(dir, 'browser.log');
  const agentBrowser = path.join(dir, 'agent-browser');
  makeExecutable(
    agentBrowser,
    '#!/usr/bin/env bash\nprintf \'%s\\n\' \"$@\" > \"$E2E_TEST_BROWSER_LOG\"\n'
  );
  const oldChrome = path.join(
    dir,
    'browsers',
    'chrome-150.0.1.1',
    'chrome-mac-arm64',
    'Google Chrome for Testing.app',
    'Contents',
    'MacOS',
    'Google Chrome for Testing'
  );
  const newChrome = path.join(
    dir,
    'browsers',
    'chrome-151.0.2.1',
    'chrome-mac-arm64',
    'Google Chrome for Testing.app',
    'Contents',
    'MacOS',
    'Google Chrome for Testing'
  );
  fs.mkdirSync(path.dirname(oldChrome), { recursive: true });
  fs.mkdirSync(path.dirname(newChrome), { recursive: true });
  makeExecutable(oldChrome, '#!/usr/bin/env bash\nexit 0\n');
  makeExecutable(newChrome, '#!/usr/bin/env bash\nexit 0\n');

  const result = spawnSync(
    process.execPath,
    [
      RUNTIME,
      '--run-id', 'run-123',
      '--app', 'storefront',
      'open', 'https://example.test',
    ],
    {
      encoding: 'utf8',
      env: Object.assign({}, process.env, {
        E2E_AGENT_BROWSER_BIN: agentBrowser,
        E2E_AGENT_BROWSER_HOME: dir,
        E2E_TEST_BROWSER_LOG: browserLog,
      }),
    }
  );

  assert.equal(result.status, 0, result.stderr);
  const args = fs.readFileSync(browserLog, 'utf8').trim().split('\n');
  assert.equal(args[args.indexOf('--executable-path') + 1], newChrome);
});

test('accepts exact agent-browser 0.32 managed Chrome for Testing layouts', function(t) {
  const layouts = [
    [
      'chrome-mac-arm64',
      'Google Chrome for Testing.app',
      'Contents',
      'MacOS',
      'Google Chrome for Testing',
    ],
    [
      'chrome-mac-x64',
      'Google Chrome for Testing.app',
      'Contents',
      'MacOS',
      'Google Chrome for Testing',
    ],
    ['chrome-linux64', 'chrome'],
    ['chrome-win64', 'chrome.exe'],
  ];

  for (const [index, layout] of layouts.entries()) {
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-browser-runtime-layout-'));
    t.after(function() {
      fs.rmSync(dir, { recursive: true, force: true });
    });
    const browserLog = path.join(dir, 'browser.log');
    const agentBrowser = path.join(dir, 'agent-browser');
    const chromeForTesting = managedChromeForTesting(dir, layout);
    makeExecutable(
      agentBrowser,
      '#!/usr/bin/env bash\nprintf \'%s\\n\' "$@" > "$E2E_TEST_BROWSER_LOG"\n'
    );

    const result = spawnSync(
      process.execPath,
      [
        RUNTIME,
        '--run-id', 'run-' + index,
        '--app', 'storefront',
        '--executable-path', chromeForTesting,
        'open', 'https://example.test',
      ],
      {
        encoding: 'utf8',
        env: Object.assign({}, process.env, {
          E2E_AGENT_BROWSER_BIN: agentBrowser,
          E2E_AGENT_BROWSER_HOME: dir,
          E2E_TEST_BROWSER_LOG: browserLog,
        }),
      }
    );

    assert.equal(result.status, 0, layout.join('/') + ': ' + result.stderr);
  }
});

test('rejects an executable that is not Chrome for Testing', function(t) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-browser-runtime-'));
  t.after(function() {
    fs.rmSync(dir, { recursive: true, force: true });
  });

  const browserLog = path.join(dir, 'browser.log');
  const agentBrowser = path.join(dir, 'agent-browser');
  const dia = path.join(dir, 'Dia.app', 'Contents', 'MacOS', 'Dia');
  fs.mkdirSync(path.dirname(dia), { recursive: true });
  makeExecutable(
    agentBrowser,
    '#!/usr/bin/env bash\nprintf \'invoked\\n\' >> \"$E2E_TEST_BROWSER_LOG\"\n'
  );
  makeExecutable(dia, '#!/usr/bin/env bash\nexit 0\n');

  const result = spawnSync(
    process.execPath,
    [
      RUNTIME,
      '--run-id', 'run-123',
      '--app', 'storefront',
      '--executable-path', dia,
      'open', 'https://example.test',
    ],
    {
      encoding: 'utf8',
      env: Object.assign({}, process.env, {
        E2E_AGENT_BROWSER_BIN: agentBrowser,
        E2E_TEST_BROWSER_LOG: browserLog,
      }),
    }
  );

  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /not a Chrome for Testing installation/i);
  assert.equal(fs.existsSync(browserLog), false);
});

test('rejects misleading executables merely nested below a Chrome for Testing substring', function(t) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-browser-runtime-'));
  t.after(function() {
    fs.rmSync(dir, { recursive: true, force: true });
  });

  const browserLog = path.join(dir, 'browser.log');
  const agentBrowser = path.join(dir, 'agent-browser');
  const misleadingDia = path.join(dir, 'Google Chrome for Testing', 'Dia');
  fs.mkdirSync(path.dirname(misleadingDia), { recursive: true });
  makeExecutable(
    agentBrowser,
    '#!/usr/bin/env bash\nprintf \'invoked\\n\' >> "$E2E_TEST_BROWSER_LOG"\n'
  );
  makeExecutable(misleadingDia, '#!/usr/bin/env bash\nexit 0\n');

  const result = spawnSync(
    process.execPath,
    [
      RUNTIME,
      '--run-id', 'run-123',
      '--app', 'storefront',
      '--executable-path', misleadingDia,
      'open', 'https://example.test',
    ],
    {
      encoding: 'utf8',
      env: Object.assign({}, process.env, {
        E2E_AGENT_BROWSER_BIN: agentBrowser,
        E2E_AGENT_BROWSER_HOME: dir,
        E2E_TEST_BROWSER_LOG: browserLog,
      }),
    }
  );

  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /not a Chrome for Testing installation/i);
  assert.equal(fs.existsSync(browserLog), false);
});

test('new-run-id returns a unique shell-safe identity for each run', function() {
  const first = spawnSync(process.execPath, [RUNTIME, 'new-run-id'], { encoding: 'utf8' });
  const second = spawnSync(process.execPath, [RUNTIME, 'new-run-id'], { encoding: 'utf8' });

  assert.equal(first.status, 0, first.stderr);
  assert.equal(second.status, 0, second.stderr);
  assert.match(first.stdout.trim(), /^[a-z0-9][a-z0-9-]{15,}$/);
  assert.match(second.stdout.trim(), /^[a-z0-9][a-z0-9-]{15,}$/);
  assert.notEqual(first.stdout.trim(), second.stdout.trim());
});

test('rejects missing or unsafe run and app identities before invoking agent-browser', function(t) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-browser-runtime-'));
  t.after(function() {
    fs.rmSync(dir, { recursive: true, force: true });
  });

  const browserLog = path.join(dir, 'browser.log');
  const agentBrowser = path.join(dir, 'agent-browser');
  const chromeForTesting = managedChromeForTesting(dir);
  makeExecutable(
    agentBrowser,
    '#!/usr/bin/env bash\nprintf \'invoked\\n\' >> "$E2E_TEST_BROWSER_LOG"\n'
  );
  for (const identityArgs of [
    ['--app', 'storefront'],
    ['--run-id', 'run-123'],
    ['--run-id', '../shared', '--app', 'storefront'],
    ['--run-id', 'run-123', '--app', 'other session'],
  ]) {
    const result = spawnSync(
      process.execPath,
      [
        RUNTIME,
      ].concat(
        identityArgs,
        ['--executable-path', chromeForTesting, 'open', 'https://example.test']
      ),
      {
        encoding: 'utf8',
        env: Object.assign({}, process.env, {
          E2E_AGENT_BROWSER_BIN: agentBrowser,
          E2E_AGENT_BROWSER_HOME: dir,
          E2E_TEST_BROWSER_LOG: browserLog,
        }),
      }
    );

    assert.notEqual(result.status, 0, identityArgs.join(' '));
    assert.match(result.stderr, /valid (run|app) identity/i);
  }
  assert.equal(fs.existsSync(browserLog), false);
});

test('close targets only the requested run namespace and app session', function(t) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-browser-runtime-'));
  t.after(function() {
    fs.rmSync(dir, { recursive: true, force: true });
  });

  const browserLog = path.join(dir, 'browser.log');
  const agentBrowser = path.join(dir, 'agent-browser');
  const chromeForTesting = managedChromeForTesting(dir);
  makeExecutable(
    agentBrowser,
    '#!/usr/bin/env bash\nprintf \'%s\\n\' "$@" > "$E2E_TEST_BROWSER_LOG"\n'
  );
  const result = spawnSync(
    process.execPath,
    [
      RUNTIME,
      '--run-id', 'run-123',
      '--app', 'storefront',
      '--executable-path', chromeForTesting,
      'close',
    ],
    {
      encoding: 'utf8',
      env: Object.assign({}, process.env, {
        E2E_AGENT_BROWSER_BIN: agentBrowser,
        E2E_AGENT_BROWSER_HOME: dir,
        E2E_TEST_BROWSER_LOG: browserLog,
      }),
    }
  );

  assert.equal(result.status, 0, result.stderr);
  const args = fs.readFileSync(browserLog, 'utf8').trim().split('\n');
  assert.deepEqual(args.slice(0, 4), ['--namespace', 'e2e-run-123', '--session', 'storefront']);
  assert.equal(args.at(-1), 'close');
  assert.equal(args.includes('--all'), false);
});

test('close remains available after Chrome for Testing is removed', function(t) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-browser-runtime-'));
  t.after(function() {
    fs.rmSync(dir, { recursive: true, force: true });
  });

  const browserLog = path.join(dir, 'browser.log');
  const agentBrowser = path.join(dir, 'agent-browser');
  makeExecutable(
    agentBrowser,
    '#!/usr/bin/env bash\nprintf \'%s\\n\' "$@" > "$E2E_TEST_BROWSER_LOG"\n'
  );

  const result = spawnSync(
    process.execPath,
    [
      RUNTIME,
      '--run-id', 'run-123',
      '--app', 'storefront',
      'close',
    ],
    {
      encoding: 'utf8',
      env: Object.assign({}, process.env, {
        E2E_AGENT_BROWSER_BIN: agentBrowser,
        E2E_AGENT_BROWSER_HOME: dir,
        E2E_TEST_BROWSER_LOG: browserLog,
      }),
    }
  );

  assert.equal(result.status, 0, result.stderr);
  assert.deepEqual(fs.readFileSync(browserLog, 'utf8').trim().split('\n'), [
    '--namespace',
    'e2e-run-123',
    '--session',
    'storefront',
    '--config',
    path.join(__dirname, '..', '..', 'references', 'agent-browser-runtime.json'),
    'close',
  ]);
});
