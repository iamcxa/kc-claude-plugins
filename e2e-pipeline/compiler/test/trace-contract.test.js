'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const { test } = require('node:test');

const pipelineRoot = path.resolve(__dirname, '..', '..');
const contractCli = path.join(pipelineRoot, 'bin', 'e2e-trace-contract.js');

function makeFakeAgentBrowser(versionOutput, traceHelp) {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-trace-contract-'));
  const executable = path.join(directory, 'agent-browser');
  fs.writeFileSync(
    executable,
    [
      '#!/usr/bin/env node',
      "'use strict';",
      'const args = process.argv.slice(2);',
      "if (args.length === 1 && args[0] === '--version') {",
      `  process.stdout.write(${JSON.stringify(versionOutput)});`,
      '  process.exit(0);',
      '}',
      "if (args.length === 2 && args[0] === 'trace' && args[1] === '--help') {",
      `  process.stdout.write(${JSON.stringify(traceHelp)});`,
      '  process.exit(0);',
      '}',
      'process.exit(64);',
      '',
    ].join('\n')
  );
  fs.chmodSync(executable, 0o755);
  return { directory, executable };
}

function runContract(executable) {
  return spawnSync(
    process.execPath,
    [contractCli, '--agent-browser', executable],
    { encoding: 'utf8', timeout: 6_000 }
  );
}

test('detects agent-browser 0.32 Chrome DevTools trace JSON before capture', () => {
  const fake = makeFakeAgentBrowser(
    'agent-browser 0.32.0\n',
    [
      'agent-browser trace - Record execution trace',
      'Record a Chrome DevTools trace for debugging.',
      'agent-browser trace stop ./debug-trace.json',
      '',
    ].join('\n')
  );
  try {
    const result = runContract(fake.executable);
    assert.equal(result.status, 0, result.stderr);
    assert.deepEqual(JSON.parse(result.stdout), {
      version: 1,
      producer: 'agent-browser',
      producer_version: '0.32.0',
      declared_format: 'chrome-trace-json',
      extension: '.json',
      validator: 'validate-chrome-trace.py',
      analyzer: 'e2e-trace-analyzer',
    });
  } finally {
    fs.rmSync(fake.directory, { recursive: true, force: true });
  }
});

test('keeps Playwright ZIP available only for a runtime that advertises it', () => {
  const fake = makeFakeAgentBrowser(
    'agent-browser 0.40.0\n',
    [
      'Record a Playwright trace archive for debugging.',
      'agent-browser trace stop ./trace.zip',
      '',
    ].join('\n')
  );
  try {
    const result = runContract(fake.executable);
    assert.equal(result.status, 0, result.stderr);
    assert.deepEqual(JSON.parse(result.stdout), {
      version: 1,
      producer: 'agent-browser',
      producer_version: '0.40.0',
      declared_format: 'playwright-trace-zip',
      extension: '.zip',
      validator: 'validate-trace-archive.py',
      analyzer: 'e2e-trace-analyzer',
    });
  } finally {
    fs.rmSync(fake.directory, { recursive: true, force: true });
  }
});

test('accepts an absolute package-manager symlink to an executable', () => {
  const fake = makeFakeAgentBrowser(
    'agent-browser 0.32.0\n',
    [
      'Record a Chrome DevTools trace for debugging.',
      'agent-browser trace stop ./debug-trace.json',
      '',
    ].join('\n')
  );
  const symlink = path.join(fake.directory, 'agent-browser-link');
  fs.symlinkSync(fake.executable, symlink);
  try {
    const result = runContract(symlink);
    assert.equal(result.status, 0, result.stderr);
    assert.equal(JSON.parse(result.stdout).declared_format, 'chrome-trace-json');
  } finally {
    fs.rmSync(fake.directory, { recursive: true, force: true });
  }
});

test('fails closed when the trace capability is unknown', () => {
  const fake = makeFakeAgentBrowser(
    'agent-browser 0.99.0\n',
    'Record an implementation-defined trace.\n'
  );
  try {
    const result = runContract(fake.executable);
    assert.equal(result.status, 65);
    assert.match(result.stderr, /unsupported agent-browser trace capability/i);
    assert.equal(result.stdout, '');
  } finally {
    fs.rmSync(fake.directory, { recursive: true, force: true });
  }
});

test('bounds a hung capability probe before capture', () => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-trace-contract-'));
  const executable = path.join(directory, 'agent-browser');
  fs.writeFileSync(
    executable,
    [
      '#!/usr/bin/env node',
      "'use strict';",
      'setTimeout(() => {}, 30_000);',
      '',
    ].join('\n')
  );
  fs.chmodSync(executable, 0o755);
  try {
    const started = Date.now();
    const result = runContract(executable);
    const elapsed = Date.now() - started;
    assert.equal(result.status, 65);
    assert.match(result.stderr, /capability probe failed/i);
    assert.ok(elapsed < 4_000, `capability probe took ${elapsed}ms`);
  } finally {
    fs.rmSync(directory, { recursive: true, force: true });
  }
});

test('requires an absolute executable path and strict version output', () => {
  const relative = spawnSync(
    process.execPath,
    [contractCli, '--agent-browser', 'agent-browser'],
    { encoding: 'utf8' }
  );
  assert.equal(relative.status, 64);
  assert.match(relative.stderr, /absolute executable path/i);

  const fake = makeFakeAgentBrowser(
    'custom wrapper version unknown\n',
    'Record a Chrome DevTools trace for debugging.\n'
  );
  try {
    const result = runContract(fake.executable);
    assert.equal(result.status, 65);
    assert.match(result.stderr, /could not determine agent-browser version/i);
  } finally {
    fs.rmSync(fake.directory, { recursive: true, force: true });
  }
});
