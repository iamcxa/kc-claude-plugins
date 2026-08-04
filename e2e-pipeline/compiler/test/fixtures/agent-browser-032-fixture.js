#!/usr/bin/env node
'use strict';

const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const vm = require('node:vm');

const statePath = process.env.E2E_AGENT_BROWSER_032_STATE;
if (!statePath) {
  process.stderr.write('E2E_AGENT_BROWSER_032_STATE is required\n');
  process.exit(2);
}

function readState() {
  return JSON.parse(fs.readFileSync(statePath, 'utf8'));
}

function writeState(state) {
  fs.writeFileSync(statePath, JSON.stringify(state, null, 2) + '\n');
}

function appendEvent(state, command, args, argv) {
  state.events = state.events || [];
  state.events.push({ command, args, argv });
}

if (path.basename(process.argv[1]) === 'ps') {
  const state = readState();
  if (state.active) {
    process.stdout.write(
      state.browserPid +
        ' ' +
        state.daemonPid +
        ' ' +
        state.executable +
        ' --remote-debugging-port=0 --user-data-dir=' +
        state.actualProfile +
        '\n'
    );
  }
  process.exit(0);
}

const args = process.argv.slice(2);
if (args.length === 1 && args[0] === '--version') {
  process.stdout.write('agent-browser 0.32.0\n');
  process.exit(0);
}
function option(name) {
  const index = args.indexOf(name);
  return index === -1 ? '' : args[index + 1] || '';
}

function options(name) {
  return args.flatMap(function(value, index) {
    return value === name ? [args[index + 1] || ''] : [];
  });
}

const commands = new Set([
  'close',
  'eval',
  'get',
  'network',
  'open',
  'session',
  'snapshot',
  'tab',
]);
const commandIndex = args.findIndex(function(value) {
  return commands.has(value);
});
const command = commandIndex === -1 ? '' : args[commandIndex];
const commandArgs = commandIndex === -1 ? [] : args.slice(commandIndex + 1);
const state = readState();
appendEvent(state, command, commandArgs, args);

if (command === 'session' && commandArgs[0] === 'info') {
  writeState(state);
  process.stdout.write(
    JSON.stringify({
      success: true,
      data: {
        active: state.active,
        namespace: option('--namespace'),
        pid: state.daemonPid,
        session: option('--session'),
        socketDir: state.socketDir,
        version: '0.32.0',
        runtimeError: null,
        runtime: {
          backgroundPid: state.daemonPid,
          browserLaunched: state.active,
          effectiveLaunch: {
            browserLaunched: state.active,
            engine: 'chrome',
            launchHash: state.launchHash,
          },
          engine: 'chrome',
          lifecycle: {
            effectiveLaunch: {
              browserLaunched: state.active,
              engine: 'chrome',
              launchHash: state.launchHash,
            },
            launched: !state.reused,
            relaunchedBrowser: false,
            restartedBackground: false,
            restoreStatus: 'not_configured',
            reused: state.reused,
            saveStatus: 'not_attempted',
          },
          namespace: option('--namespace'),
          pageCount: state.active ? 1 : 0,
          session: option('--session'),
          socketDir: state.socketDir,
        },
      },
    }) + '\n'
  );
  process.exit(0);
}

if (command === 'tab' && commandArgs[0] === 'list') {
  writeState(state);
  process.stdout.write(
    JSON.stringify({
      success: true,
      data: {
        tabs: state.active
          ? [
              {
                active: true,
                tabId: state.tabId,
                title: state.url,
                type: 'page',
                url: state.url,
              },
            ]
          : [],
      },
    }) + '\n'
  );
  process.exit(0);
}

if (command === 'network' && commandArgs[0] === 'har') {
  if (commandArgs[1] === 'start') {
    state.harActive = true;
    state.requests = [];
  } else if (commandArgs[1] === 'stop') {
    const harPath = commandArgs[2];
    state.harActive = false;
    fs.writeFileSync(
      harPath,
      JSON.stringify({
        log: {
          entries: (state.requests || []).map(function(request) {
            return {
              request: { method: 'GET', url: request.url },
              response: {
                content: { mimeType: request.mimeType },
                status: 200,
              },
              _resourceType: request.resourceType,
            };
          }),
        },
      })
    );
  }
  writeState(state);
  process.stdout.write(JSON.stringify({ success: true }) + '\n');
  process.exit(0);
}

if (command === 'network' && commandArgs[0] === 'requests') {
  writeState(state);
  process.stdout.write(
    JSON.stringify({
      success: true,
      data: { requests: state.requests || [] },
    }) + '\n'
  );
  process.exit(0);
}

if (command === 'open') {
  const requestedProfile = option('--profile');
  const initScripts = options('--init-script');
  const targetUrl = commandArgs[0] || '';
  if (!state.active) {
    state.active = true;
    state.reused = false;
    state.actualProfile =
      state.profileMode === 'snapshot'
        ? path.join(
            os.tmpdir(),
            'agent-browser-chrome-' + state.snapshotId
          )
        : requestedProfile;
    if (state.profileMode === 'snapshot') {
      fs.mkdirSync(state.actualProfile, { recursive: true, mode: 0o700 });
      fs.chmodSync(state.actualProfile, 0o700);
      fs.mkdirSync(path.join(requestedProfile, 'Default'), { recursive: true });
      fs.mkdirSync(path.join(state.actualProfile, 'Default'), {
        recursive: true,
      });
      const structuralFiles = [
        ['Local State', 512],
        [path.join('Default', 'Preferences'), 768],
        [path.join('Default', 'Cookies'), 1024],
      ];
      for (const [relativePath, size] of structuralFiles) {
        const sourcePath = path.join(requestedProfile, relativePath);
        const actualPath = path.join(state.actualProfile, relativePath);
        fs.writeFileSync(sourcePath, Buffer.alloc(size, 65), { mode: 0o600 });
        fs.writeFileSync(
          actualPath,
          Buffer.alloc(state.copyLineage === false ? size + 1 : size, 65),
          { mode: 0o600 }
        );
      }
    }
    state.url = 'about:blank';
    state.initScripts = initScripts;
    state.initRegistered = initScripts.length > 0;
    state.diagnosticGlobals = {};
    initScripts.forEach(function(initScriptPath, index) {
      if (index > 0 && index - 1 === state.dropDiagnosticIndex) return;
      const context = {};
      context.globalThis = context;
      try {
        vm.runInNewContext(fs.readFileSync(initScriptPath, 'utf8'), context);
        for (const key of Object.getOwnPropertyNames(context)) {
          if (key.startsWith('__E2E_DIAGNOSTIC_MARKER_')) {
            state.diagnosticGlobals[key] = context[key];
          }
          if (
            key.startsWith('__E2E_DIAGNOSTIC_PROJECTION_') &&
            typeof context[key] === 'function'
          ) {
            state.diagnosticGlobals[key] = context[key]();
          }
        }
      } catch (error) {
        state.diagnosticGlobals['fixture-error-' + index] = error.message;
      }
    });
  } else {
    state.reused = true;
  }
  if (targetUrl && targetUrl !== 'about:blank') {
    if (state.resetOnNavigation === 'daemon') {
      state.daemonPid += 1000;
      state.browserPid += 1000;
      state.tabId = 't-reset';
      state.url = 'about:blank';
      state.initRegistered = false;
      state.diagnosticGlobals = {};
      state.requests = [];
    } else if (state.resetOnNavigation === 'browser') {
      state.browserPid += 1000;
      state.tabId = 't-reset';
      state.url = 'about:blank';
      state.initRegistered = false;
      state.diagnosticGlobals = {};
      state.requests = [];
    } else if (state.resetOnNavigation === 'page') {
      state.tabId = 't-reset';
      state.url = 'about:blank';
      state.initRegistered = false;
      state.diagnosticGlobals = {};
      state.requests = [];
    } else {
      state.url = targetUrl;
      state.launchHash += 1;
      if (state.harActive) {
        state.requests.push({
          method: 'GET',
          mimeType: 'text/html',
          resourceType: 'Document',
          status: 200,
          url: targetUrl,
        });
      }
    }
  }
  writeState(state);
  process.stdout.write('opened\n');
  process.exit(0);
}

if (command === 'eval') {
  writeState(state);
  const expression = commandArgs[0] || '';
  // Profile-liveness probe (#149). This branch EVALUATES the runtime's real expression
  // against a synthetic global rather than returning a canned object, because the thing
  // most worth testing is where the guards sit: `localStorage` is reachable only through
  // a getter that can throw, and an expression that touches it outside a `try` lets the
  // exception escape. A fixture that answered with pre-baked JSON would pass either way,
  // which is exactly how the reverted first attempt shipped an unreachable code path.
  if (expression.includes('readSelector')) {
    const liveness = state.profileLiveness || {};
    if (liveness.mode === 'probe-broken') {
      // Transport failure, not absence: the probe itself could not produce evidence.
      writeState(state);
      process.stdout.write(
        JSON.stringify({ success: false, error: 'eval transport failure' }) + '\n'
      );
      process.exit(0);
    }
    // `appearAfter` models the SPA that has not rendered its authenticated affordance
    // yet: the first N samples see nothing, later ones see it. A one-shot probe fails
    // this; a polling one does not.
    state.livenessSamples = (state.livenessSamples || 0) + 1;
    const appearAfter = liveness.appearAfter || 0;
    const visible = state.livenessSamples > appearAfter;
    const presentKeys = visible ? liveness.keys || [] : [];
    const presentSelectors = visible ? liveness.selectors || [] : [];
    writeState(state);
    const context = {
      location: { origin: liveness.origin || 'https://application.example.test' },
      document: {
        querySelector: function(selector) {
          if (liveness.mode === 'document-throws') throw new Error('SecurityError');
          return presentSelectors.includes(selector) ? {} : null;
        },
      },
    };
    context.globalThis = context;
    // `storage-throws` models a store that exists but refuses the read. It does NOT
    // model an opaque origin, where the property ACCESS itself throws: `vm` does not
    // forward a throwing getter from a sandbox object — it yields `undefined` — so that
    // case is untestable here by construction and is covered by the direct unit test on
    // `profileLivenessExpression` instead. Saying so because a fixture that silently
    // fails to model what its mode is named after is how the reverted attempt shipped
    // an unreachable code path with a green test over it.
    context.localStorage = {
      getItem: function(key) {
        if (liveness.mode === 'storage-throws') {
          throw new Error('SecurityError: storage is not available');
        }
        return presentKeys.includes(key) ? 'value' : null;
      },
    };
    let result;
    try {
      result = vm.runInNewContext(expression, context);
    } catch (error) {
      process.stdout.write(
        JSON.stringify({ success: false, error: String(error && error.message) }) + '\n'
      );
      process.exit(0);
    }
    process.stdout.write(
      JSON.stringify({ success: true, data: { result } }) + '\n'
    );
    process.exit(0);
  }
  const globalMatch = expression.match(
    /globalThis\[("(?:[^"\\]|\\.)*")\]/
  );
  let result = Boolean(state.initRegistered);
  if (globalMatch) {
    const key = JSON.parse(globalMatch[1]);
    if (Object.hasOwn(state.diagnosticGlobals, key)) {
      result = state.diagnosticGlobals[key];
      if (expression.includes('=== true')) result = result === true;
    } else if (key.startsWith('__E2E_DIAGNOSTIC_')) {
      result = expression.includes('=== true') ? false : undefined;
    }
  }
  process.stdout.write(
    JSON.stringify({
      success: true,
      data: { result },
    }) + '\n'
  );
  process.exit(0);
}

if (command === 'get' && commandArgs[0] === 'url') {
  writeState(state);
  process.stdout.write(state.url + '\n');
  process.exit(0);
}

if (command === 'close') {
  state.active = false;
  writeState(state);
  process.stdout.write('closed\n');
  process.exit(0);
}

if (command === 'snapshot') {
  writeState(state);
  process.stdout.write('snapshot\n');
  process.exit(0);
}

writeState(state);
process.stderr.write('unsupported fixture command: ' + args.join(' ') + '\n');
process.exit(2);
