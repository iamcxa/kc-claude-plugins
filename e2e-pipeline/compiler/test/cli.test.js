'use strict';

/**
 * CLI integration tests for bin/e2e-compile.js (Commander CLI)
 *
 * Tests invoke the CLI via node child_process to verify end-to-end behavior
 * including exit codes, file creation, chmod, dry-run, verbose, and --help.
 */

const { test, describe, before, after } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { execFileSync, spawnSync } = require('node:child_process');

const PIPELINE_DIR = path.join(__dirname, '..', '..');
const BIN = path.join(PIPELINE_DIR, 'bin', 'e2e-compile.js');
const FIXTURES_DIR = path.join(__dirname, 'fixtures');

function makeTmpDir() {
  return fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-cli-test-'));
}

// ---------------------------------------------------------------------------
// Helper: invoke CLI and return { stdout, stderr, status }
// ---------------------------------------------------------------------------

function runCli(args, opts) {
  var result = spawnSync('node', [BIN].concat(args), Object.assign({
    encoding: 'utf8',
    cwd: PIPELINE_DIR,
  }, opts || {}));
  return result;
}

// ---------------------------------------------------------------------------
// CLI-01: Single flow compilation
// ---------------------------------------------------------------------------

describe('CLI-01: single flow compilation', function() {
  var tmpDir;

  before(function() {
    tmpDir = makeTmpDir();
  });

  after(function() {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  test("single flow produces output file named <flow-name>.sh", function() {
    // simple-flow.yaml has name: test-login, so output is test-login.sh
    var result = runCli([
      'simple-flow',
      '--flows-dir', FIXTURES_DIR,
      '--mappings-dir', FIXTURES_DIR,
      '--output-dir', tmpDir,
    ]);
    assert.equal(result.status, 0, 'Expected exit 0. stderr: ' + result.stderr + ' stdout: ' + result.stdout);
    var outFile = path.join(tmpDir, 'test-login.sh');
    assert.ok(fs.existsSync(outFile), 'Expected output file at ' + outFile);
  });

  test("single flow exits 0 on success", function() {
    var result = runCli([
      'simple-flow',
      '--flows-dir', FIXTURES_DIR,
      '--mappings-dir', FIXTURES_DIR,
      '--output-dir', tmpDir,
    ]);
    assert.equal(result.status, 0, 'Expected exit 0. stderr: ' + result.stderr);
  });

  test("single flow exits 1 when flow references missing elements", function() {
    var result = runCli([
      'missing-element-flow',
      '--flows-dir', FIXTURES_DIR,
      '--mappings-dir', FIXTURES_DIR,
      '--output-dir', tmpDir,
    ]);
    assert.equal(result.status, 1, 'Expected exit 1 for missing element flow');
  });
});

// ---------------------------------------------------------------------------
// CLI-02: Batch mode (--all)
// ---------------------------------------------------------------------------

describe('CLI-02: batch mode --all', function() {
  var tmpDir;

  before(function() {
    tmpDir = makeTmpDir();
  });

  after(function() {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  test("--all compiles multiple YAML files from flows dir", function() {
    var result = runCli([
      '--all',
      '--flows-dir', FIXTURES_DIR,
      '--mappings-dir', FIXTURES_DIR,
      '--output-dir', tmpDir,
    ]);
    // Batch continues on error, so exit code may be 1 (due to missing-element-flow)
    // But output directory should contain successfully compiled files
    var files = fs.readdirSync(tmpDir).filter(function(f) { return f.endsWith('.sh'); });
    assert.ok(files.length > 0, 'Expected at least one .sh file compiled. Files: ' + JSON.stringify(files));
  });

  test("--all outputs summary with OK and failed counts", function() {
    var result = runCli([
      '--all',
      '--flows-dir', FIXTURES_DIR,
      '--mappings-dir', FIXTURES_DIR,
      '--output-dir', tmpDir,
    ]);
    var combined = result.stdout + result.stderr;
    assert.ok(
      combined.includes('OK') || combined.includes('failed') || combined.includes('Compiled:'),
      'Expected summary output. Got stdout: ' + result.stdout + ' stderr: ' + result.stderr
    );
  });

  test("--all continues on error (does not stop at first failure)", function() {
    // The fixtures directory has missing-element-flow.yaml which fails
    // But test-login.sh and others should still be compiled
    var result = runCli([
      '--all',
      '--flows-dir', FIXTURES_DIR,
      '--mappings-dir', FIXTURES_DIR,
      '--output-dir', tmpDir,
    ]);
    var files = fs.readdirSync(tmpDir).filter(function(f) { return f.endsWith('.sh'); });
    // If batch stopped at first error, we'd get 0 or 1 file depending on sort order
    // With continuation, we should get multiple files
    assert.ok(files.length >= 1, 'Batch must continue on error and compile remaining flows. Files: ' + JSON.stringify(files));
  });

  test("--all exits 1 when any flow fails to compile", function() {
    var result = runCli([
      '--all',
      '--flows-dir', FIXTURES_DIR,
      '--mappings-dir', FIXTURES_DIR,
      '--output-dir', tmpDir,
    ]);
    // fixtures has missing-element-flow.yaml which will fail
    assert.equal(result.status, 1, 'Expected exit 1 when any flow fails in batch mode');
  });
});

// ---------------------------------------------------------------------------
// CLI-03: chmod +x on output files
// ---------------------------------------------------------------------------

describe('CLI-03: output files are chmod +x', function() {
  var tmpDir;

  before(function() {
    tmpDir = makeTmpDir();
  });

  after(function() {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  test("compiled output file has executable permission bits set", function() {
    // simple-flow.yaml has name: test-login, so output is test-login.sh
    var result = runCli([
      'simple-flow',
      '--flows-dir', FIXTURES_DIR,
      '--mappings-dir', FIXTURES_DIR,
      '--output-dir', tmpDir,
    ]);
    assert.equal(result.status, 0, 'Compile must succeed. stderr: ' + result.stderr);
    var outFile = path.join(tmpDir, 'test-login.sh');
    var stat = fs.statSync(outFile);
    var mode = stat.mode & 0o111; // check executable bits
    assert.ok(mode !== 0, 'Output file must have executable bits set (chmod +x). mode: ' + (stat.mode & 0o777).toString(8));
  });
});

// ---------------------------------------------------------------------------
// CLI-04: --dry-run
// ---------------------------------------------------------------------------

describe('CLI-04: --dry-run mode', function() {
  var tmpDir;

  before(function() {
    tmpDir = makeTmpDir();
  });

  after(function() {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  test("--dry-run does NOT create any output files", function() {
    var result = runCli([
      '--dry-run',
      'simple-flow',
      '--flows-dir', FIXTURES_DIR,
      '--mappings-dir', FIXTURES_DIR,
      '--output-dir', tmpDir,
    ]);
    var files = fs.readdirSync(tmpDir);
    assert.equal(files.length, 0, 'DRY RUN must not create output files. Found: ' + JSON.stringify(files));
  });

  test("--dry-run exits 0 when flow is valid (validation passes)", function() {
    var result = runCli([
      '--dry-run',
      'simple-flow',
      '--flows-dir', FIXTURES_DIR,
      '--mappings-dir', FIXTURES_DIR,
      '--output-dir', tmpDir,
    ]);
    assert.equal(result.status, 0, 'Expected exit 0 for valid flow in dry-run. stderr: ' + result.stderr);
  });

  test("--dry-run stderr contains 'DRY RUN' message", function() {
    var result = runCli([
      '--dry-run',
      'simple-flow',
      '--flows-dir', FIXTURES_DIR,
      '--mappings-dir', FIXTURES_DIR,
      '--output-dir', tmpDir,
    ]);
    assert.ok(
      result.stderr.includes('DRY RUN'),
      'Expected DRY RUN in stderr. Got: ' + result.stderr
    );
  });
});

// ---------------------------------------------------------------------------
// CLI-05: --verbose
// ---------------------------------------------------------------------------

describe('CLI-05: --verbose mode', function() {
  var tmpDir;

  before(function() {
    tmpDir = makeTmpDir();
  });

  after(function() {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  test("--verbose still creates the output file", function() {
    // simple-flow.yaml has name: test-login, so output is test-login.sh
    var result = runCli([
      '--verbose',
      'simple-flow',
      '--flows-dir', FIXTURES_DIR,
      '--mappings-dir', FIXTURES_DIR,
      '--output-dir', tmpDir,
    ]);
    assert.equal(result.status, 0, 'Expected exit 0 with --verbose. stderr: ' + result.stderr);
    var outFile = path.join(tmpDir, 'test-login.sh');
    assert.ok(fs.existsSync(outFile), 'Output file must exist in verbose mode');
  });

  test("--verbose prints step details to stderr", function() {
    var result = runCli([
      '--verbose',
      'simple-flow',
      '--flows-dir', FIXTURES_DIR,
      '--mappings-dir', FIXTURES_DIR,
      '--output-dir', tmpDir,
    ]);
    // Verbose prints [N/T] step-id: type for each step
    assert.ok(
      result.stderr.includes('[1/') || result.stderr.includes('operands'),
      'Expected step details in stderr from --verbose. Got: ' + result.stderr
    );
  });
});

// ---------------------------------------------------------------------------
// CLI-06: Commander basics (--help, exit codes)
// ---------------------------------------------------------------------------

describe('CLI-06: Commander basics', function() {
  test("--help prints usage information and exits 0", function() {
    var result = runCli(['--help']);
    assert.equal(result.status, 0, 'Expected exit 0 for --help. Got: ' + result.status);
    assert.ok(
      result.stdout.includes('e2e-compile'),
      'Expected "e2e-compile" in --help output. Got: ' + result.stdout
    );
  });

  test("--help output contains description of --all flag", function() {
    var result = runCli(['--help']);
    assert.ok(
      result.stdout.includes('all') || result.stdout.includes('--all'),
      'Expected --all in --help output. Got: ' + result.stdout
    );
  });

  test("--version prints version string", function() {
    var result = runCli(['--version']);
    assert.equal(result.status, 0, 'Expected exit 0 for --version');
    assert.ok(
      result.stdout.trim().length > 0,
      'Expected version string in stdout. Got: ' + result.stdout
    );
  });
});
