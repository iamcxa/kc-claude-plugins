#!/usr/bin/env node
'use strict';

const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

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
  const initScript = option('--init-script');
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
    state.initRegistered = Boolean(initScript);
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
      state.requests = [];
    } else if (state.resetOnNavigation === 'browser') {
      state.browserPid += 1000;
      state.tabId = 't-reset';
      state.url = 'about:blank';
      state.initRegistered = false;
      state.requests = [];
    } else if (state.resetOnNavigation === 'page') {
      state.tabId = 't-reset';
      state.url = 'about:blank';
      state.initRegistered = false;
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
  process.stdout.write(
    JSON.stringify({
      success: true,
      data: { result: Boolean(state.initRegistered) },
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
