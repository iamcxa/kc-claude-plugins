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
    executablePath: '',
    profile: '',
    headed: false,
    command: [],
  };

  for (let index = 0; index < argv.length; index += 1) {
    const value = argv[index];
    if (value === '--run-id') {
      options.runId = argv[++index] || '';
    } else if (value === '--app') {
      options.app = argv[++index] || '';
    } else if (value === '--executable-path') {
      options.executablePath = argv[++index] || '';
    } else if (value === '--profile') {
      options.profile = argv[++index] || '';
    } else if (value === '--headed') {
      options.headed = true;
    } else {
      options.command = argv.slice(index);
      break;
    }
  }

  return options;
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
  if (!/^[a-z0-9][a-z0-9-]{2,127}$/.test(options.runId)) {
    process.stderr.write(
      'e2e-browser-runtime: provide a valid run identity (lowercase letters, digits, and hyphens)\n'
    );
    return 2;
  }
  if (!/^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$/.test(options.app)) {
    process.stderr.write(
      'e2e-browser-runtime: provide a valid app identity (letters, digits, dots, underscores, and hyphens)\n'
    );
    return 2;
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
  const browserHome =
    process.env.E2E_AGENT_BROWSER_HOME || path.join(os.homedir(), '.agent-browser');
  const isOwnedClose = options.command[0] === 'close';
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
    'e2e-' + options.runId,
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
  args.push(...options.command);

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
  delete childEnvironment.CDP_PORT;
  delete childEnvironment.CDP_URL;
  const result = spawnSync(agentBrowser, args, {
    env: childEnvironment,
    stdio: 'inherit',
  });
  if (result.error) {
    process.stderr.write('e2e-browser-runtime: ' + result.error.message + '\n');
    return 1;
  }
  return result.status === null ? 1 : result.status;
}

if (require.main === module) {
  process.exitCode = main(process.argv.slice(2));
}

module.exports = {
  compareVersions,
  discoverChromeForTesting,
  isChromeForTestingExecutable,
  isAllowedCommand,
  managedExecutableSuffixes,
  main,
  parseArgs,
  protectedRuntimeArgument,
};
