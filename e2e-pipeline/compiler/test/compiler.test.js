'use strict';

const { test, describe, before, after } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');

const { compile } = require('../compiler.js');

const FIXTURES_DIR = path.join(__dirname, 'fixtures');
const SIMPLE_FLOW = path.join(FIXTURES_DIR, 'simple-flow.yaml');
const MISSING_ELEM_FLOW = path.join(FIXTURES_DIR, 'missing-element-flow.yaml');

// ---------------------------------------------------------------------------
// Helper: create a temp output directory for each test group
// ---------------------------------------------------------------------------

function makeTmpDir() {
  return fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-compiler-test-'));
}

// ---------------------------------------------------------------------------
// compile() basic output
// ---------------------------------------------------------------------------

describe('compile() — basic output', function() {
  var tmpDir;

  before(function() {
    tmpDir = makeTmpDir();
  });

  after(function() {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  test("compile(simple-flow.yaml) returns success=true", async function() {
    const result = await compile(SIMPLE_FLOW, FIXTURES_DIR, tmpDir);
    assert.equal(result.success, true, 'Expected success=true. Result: ' + JSON.stringify(result));
  });

  test("compile() writes .sh file named after flow", async function() {
    const result = await compile(SIMPLE_FLOW, FIXTURES_DIR, tmpDir);
    assert.ok(result.outputPath, 'Expected outputPath in result');
    assert.ok(
      result.outputPath.endsWith('test-login.sh'),
      'Expected output named test-login.sh. Got: ' + result.outputPath
    );
    assert.ok(fs.existsSync(result.outputPath), 'Output file must exist on disk');
  });

  test("written file starts with #!/usr/bin/env bash", async function() {
    const result = await compile(SIMPLE_FLOW, FIXTURES_DIR, tmpDir);
    const content = fs.readFileSync(result.outputPath, 'utf8');
    assert.ok(content.startsWith('#!/usr/bin/env bash'), 'Expected shebang at start');
  });

  test("written file has chmod 755 (executable by owner)", async function() {
    const result = await compile(SIMPLE_FLOW, FIXTURES_DIR, tmpDir);
    const stat = fs.statSync(result.outputPath);
    const mode = stat.mode & 0o777;
    // 0o755 = owner rwx, group rx, others rx
    assert.equal(mode, 0o755, 'Expected chmod 755. Got: ' + mode.toString(8));
  });
});

// ---------------------------------------------------------------------------
// compile() summary stats
// ---------------------------------------------------------------------------

describe('compile() — summary stats', function() {
  var tmpDir;
  var capturedStdout;
  var originalLog;

  before(function() {
    tmpDir = makeTmpDir();
  });

  after(function() {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  test("compile() returns stats with total, activeExpects, deferredExpects", async function() {
    const result = await compile(SIMPLE_FLOW, FIXTURES_DIR, tmpDir);
    assert.ok(result.stats, 'Expected stats in result');
    assert.ok(typeof result.stats.total === 'number', 'stats.total must be a number');
    assert.ok(typeof result.stats.activeExpects === 'number', 'stats.activeExpects must be a number');
    assert.ok(typeof result.stats.deferredExpects === 'number', 'stats.deferredExpects must be a number');
  });

  test("simple-flow.yaml has 6 total steps", async function() {
    const result = await compile(SIMPLE_FLOW, FIXTURES_DIR, tmpDir);
    assert.equal(result.stats.total, 6, 'Expected 6 steps for simple-flow.yaml');
  });
});

// ---------------------------------------------------------------------------
// compile() error handling
// ---------------------------------------------------------------------------

describe('compile() — error handling', function() {
  var tmpDir;

  before(function() {
    tmpDir = makeTmpDir();
  });

  after(function() {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  test("compile() with missing-element-flow.yaml returns success=false", async function() {
    const result = await compile(MISSING_ELEM_FLOW, FIXTURES_DIR, tmpDir);
    assert.equal(result.success, false, 'Expected success=false for missing element');
  });

  test("compile() with missing-element-flow.yaml returns errors array with content", async function() {
    const result = await compile(MISSING_ELEM_FLOW, FIXTURES_DIR, tmpDir);
    assert.ok(Array.isArray(result.errors) && result.errors.length > 0, 'Expected non-empty errors array');
  });

  test("compile() with nonexistent file returns success=false", async function() {
    const result = await compile('/nonexistent/flow.yaml', FIXTURES_DIR, tmpDir);
    assert.equal(result.success, false, 'Expected success=false for nonexistent file');
  });

  test("compile() accumulates errors from parse phase", async function() {
    const result = await compile('/nonexistent/flow.yaml', FIXTURES_DIR, tmpDir);
    assert.ok(result.errors && result.errors.length > 0, 'Expected errors from parse phase');
  });
});

// ---------------------------------------------------------------------------
// compile() module interface
// ---------------------------------------------------------------------------

describe('compile() — module interface', function() {
  test("compile is a function (module export)", function() {
    assert.equal(typeof compile, 'function', 'compile must be exported as a function');
  });
});

// ---------------------------------------------------------------------------
// Integration: BASE_URL variable ordering + bash -n syntax check
// ---------------------------------------------------------------------------

describe('Integration: complete pipeline produces valid bash script', function() {
  var tmpDir;
  var outputPath;

  before(async function() {
    tmpDir = makeTmpDir();
    const result = await compile(SIMPLE_FLOW, FIXTURES_DIR, tmpDir);
    assert.ok(result.success, 'Integration setup: compile must succeed');
    outputPath = result.outputPath;
  });

  after(function() {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  test("BASE_URL= declaration appears before first ${BASE_URL} reference", function() {
    const content = fs.readFileSync(outputPath, 'utf8');
    const lines = content.split('\n');

    var declLine = -1;
    var firstRefLine = -1;

    for (var i = 0; i < lines.length; i++) {
      if (declLine === -1 && lines[i].includes('BASE_URL=')) {
        declLine = i;
      }
      if (firstRefLine === -1 && lines[i].includes('${BASE_URL}')) {
        firstRefLine = i;
      }
    }

    assert.ok(declLine !== -1, 'BASE_URL= declaration must exist in output');
    assert.ok(firstRefLine !== -1, '${BASE_URL} reference must exist in output');
    assert.ok(
      declLine < firstRefLine,
      'BASE_URL= (line ' + (declLine + 1) + ') must come before ${BASE_URL} (line ' + (firstRefLine + 1) + ')'
    );
  });

  test("bash -n syntax check passes on compiled output", function() {
    const result = spawnSync('bash', ['-n', outputPath], { encoding: 'utf8' });
    assert.equal(
      result.status,
      0,
      'bash -n syntax check failed. stderr: ' + result.stderr
    );
  });

  test("compiled script contains variable block before steps", function() {
    const content = fs.readFileSync(outputPath, 'utf8');
    assert.ok(content.includes('BASE_URL='), 'Expected BASE_URL= in output');
    assert.ok(content.includes('#!/usr/bin/env bash'), 'Expected shebang');
    assert.ok(content.includes('agent-browser open "${BASE_URL}'), 'Expected navigate action with BASE_URL');
  });
});

// ---------------------------------------------------------------------------
// CLI: node compiler.js with no args exits 1 and prints usage
// ---------------------------------------------------------------------------

describe('CLI: node compiler.js', function() {
  var compilerPath = path.join(__dirname, '..', 'compiler.js');

  test("node compiler.js with no args exits with code 1", function() {
    const result = spawnSync('node', [compilerPath], { encoding: 'utf8' });
    assert.equal(result.status, 1, 'Expected exit code 1 with no args. Got: ' + result.status);
  });

  test("node compiler.js with no args prints usage to stderr", function() {
    const result = spawnSync('node', [compilerPath], { encoding: 'utf8' });
    assert.ok(
      result.stderr.includes('Usage:') || result.stderr.includes('usage:'),
      'Expected usage message in stderr. Got: ' + result.stderr
    );
  });

  test("node compiler.js <flow.yaml> exits 0 on success", function() {
    const tmpDir = makeTmpDir();
    try {
      const result = spawnSync(
        'node',
        [compilerPath, SIMPLE_FLOW, '--mapping-dir', FIXTURES_DIR, '--output-dir', tmpDir],
        { encoding: 'utf8' }
      );
      assert.equal(result.status, 0, 'Expected exit 0. stderr: ' + result.stderr + ' stdout: ' + result.stdout);
    } finally {
      fs.rmSync(tmpDir, { recursive: true, force: true });
    }
  });

  test("node compiler.js <flow.yaml> prints Compiled summary to stdout", function() {
    const tmpDir = makeTmpDir();
    try {
      const result = spawnSync(
        'node',
        [compilerPath, SIMPLE_FLOW, '--mapping-dir', FIXTURES_DIR, '--output-dir', tmpDir],
        { encoding: 'utf8' }
      );
      assert.ok(
        result.stdout.includes('Compiled:'),
        'Expected "Compiled:" in stdout. Got: ' + result.stdout
      );
    } finally {
      fs.rmSync(tmpDir, { recursive: true, force: true });
    }
  });

  test("node compiler.js <missing-element-flow.yaml> exits 1", function() {
    const tmpDir = makeTmpDir();
    try {
      const result = spawnSync(
        'node',
        [compilerPath, MISSING_ELEM_FLOW, '--mapping-dir', FIXTURES_DIR, '--output-dir', tmpDir],
        { encoding: 'utf8' }
      );
      assert.equal(result.status, 1, 'Expected exit 1 for compilation error. Got: ' + result.status);
    } finally {
      fs.rmSync(tmpDir, { recursive: true, force: true });
    }
  });
});
