#!/usr/bin/env node
'use strict';

const fs = require('node:fs');
const path = require('node:path');
const { spawnSync } = require('node:child_process');

function fail(message, exitCode) {
  process.stderr.write('e2e-trace-contract: ' + message + '\n');
  process.exit(exitCode);
}

function parseArgs(argv) {
  if (
    ![2, 4].includes(argv.length) ||
    argv[0] !== '--agent-browser' ||
    (argv.length === 4 && (argv[2] !== '--output' || argv[3] !== 'env'))
  ) {
    fail('usage: e2e-trace-contract --agent-browser <absolute-executable>', 64);
  }
  const executable = argv[1];
  if (!path.isAbsolute(executable)) {
    fail('agent-browser must be an absolute executable path', 64);
  }
  let resolvedExecutable;
  let stat;
  try {
    resolvedExecutable = fs.realpathSync(executable);
    stat = fs.statSync(resolvedExecutable);
    fs.accessSync(executable, fs.constants.X_OK);
  } catch {
    fail('agent-browser must be an executable regular file', 64);
  }
  if (!stat.isFile()) {
    fail('agent-browser must be an executable regular file', 64);
  }
  return {
    executable: resolvedExecutable,
    output: argv.length === 4 ? 'env' : 'json',
  };
}

function run(executable, args) {
  const result = spawnSync(executable, args, {
    encoding: 'utf8',
    maxBuffer: 1024 * 1024,
    timeout: 2_000,
    killSignal: 'SIGKILL',
  });
  if (result.error || result.status !== 0) {
    fail('agent-browser capability probe failed', 65);
  }
  return String(result.stdout || '');
}

function detect(executable) {
  const versionOutput = run(executable, ['--version']).trim();
  const versionMatch = versionOutput.match(/^agent-browser\s+(\d+\.\d+\.\d+)$/);
  if (!versionMatch) {
    fail('could not determine agent-browser version', 65);
  }

  const help = run(executable, ['trace', '--help']);
  const chrome =
    /Chrome DevTools trace/i.test(help) && /(?:debug-)?trace\.json/i.test(help);
  const playwright =
    /Playwright trace archive/i.test(help) && /trace\.zip/i.test(help);
  if (chrome === playwright) {
    fail('unsupported agent-browser trace capability', 65);
  }

  if (chrome) {
    return {
      version: 1,
      producer: 'agent-browser',
      producer_version: versionMatch[1],
      declared_format: 'chrome-trace-json',
      extension: '.json',
      validator: 'validate-chrome-trace.py',
      analyzer: 'e2e-trace-analyzer',
    };
  }
  return {
    version: 1,
    producer: 'agent-browser',
    producer_version: versionMatch[1],
    declared_format: 'playwright-trace-zip',
    extension: '.zip',
    validator: 'validate-trace-archive.py',
    analyzer: 'e2e-trace-analyzer',
  };
}

function renderEnv(contract) {
  return [
    'trace_producer=' + contract.producer,
    'trace_producer_version=' + contract.producer_version,
    'trace_format=' + contract.declared_format,
    'trace_extension=' + contract.extension,
    'trace_validator=' + contract.validator,
    'trace_analyzer=' + contract.analyzer,
    '',
  ].join('\n');
}

const options = parseArgs(process.argv.slice(2));
const contract = detect(options.executable);
process.stdout.write(
  options.output === 'env' ? renderEnv(contract) : JSON.stringify(contract) + '\n'
);
