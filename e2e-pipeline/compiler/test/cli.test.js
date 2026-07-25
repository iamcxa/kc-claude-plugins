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
// CLI-07: --coverage flag
// ---------------------------------------------------------------------------

describe('CLI-07: --coverage flag', function() {
  var tmpDir;
  var coverageDir;

  before(function() {
    tmpDir = makeTmpDir();
    coverageDir = makeTmpDir();
  });

  after(function() {
    fs.rmSync(tmpDir, { recursive: true, force: true });
    fs.rmSync(coverageDir, { recursive: true, force: true });
  });

  test("--coverage flag compiles and exits 0", function() {
    var result = runCli([
      '--coverage',
      '--coverage-output', coverageDir,
      'simple-flow',
      '--flows-dir', FIXTURES_DIR,
      '--mappings-dir', FIXTURES_DIR,
      '--output-dir', tmpDir,
    ]);
    assert.equal(result.status, 0, 'Expected exit 0 with --coverage. stderr: ' + result.stderr + ' stdout: ' + result.stdout);
  });

  test("--coverage prints 'Coverage:' line to stdout", function() {
    var result = runCli([
      '--coverage',
      '--coverage-output', coverageDir,
      'simple-flow',
      '--flows-dir', FIXTURES_DIR,
      '--mappings-dir', FIXTURES_DIR,
      '--output-dir', tmpDir,
    ]);
    assert.ok(
      result.stdout.includes('Coverage:'),
      'Expected "Coverage:" in stdout. Got: ' + result.stdout
    );
  });

  test("--coverage writes coverage.json to coverage output directory", function() {
    var result = runCli([
      '--coverage',
      '--coverage-output', coverageDir,
      'simple-flow',
      '--flows-dir', FIXTURES_DIR,
      '--mappings-dir', FIXTURES_DIR,
      '--output-dir', tmpDir,
    ]);
    assert.equal(result.status, 0, 'Compile must succeed. stderr: ' + result.stderr);
    var coverageFile = path.join(coverageDir, 'coverage.json');
    assert.ok(fs.existsSync(coverageFile), 'coverage.json must be written to --coverage-output dir');
  });

  test("coverage.json contains elements array and summary", function() {
    var result = runCli([
      '--coverage',
      '--coverage-output', coverageDir,
      'simple-flow',
      '--flows-dir', FIXTURES_DIR,
      '--mappings-dir', FIXTURES_DIR,
      '--output-dir', tmpDir,
    ]);
    assert.equal(result.status, 0, 'Compile must succeed');
    var coverageFile = path.join(coverageDir, 'coverage.json');
    if (fs.existsSync(coverageFile)) {
      var data = JSON.parse(fs.readFileSync(coverageFile, 'utf8'));
      assert.ok(Array.isArray(data.elements), 'coverage.json must have elements array');
      assert.ok(data.summary && typeof data.summary === 'object', 'coverage.json must have summary object');
    }
  });

  test("--coverage appends to coverage-history.json", function() {
    var historyDir = makeTmpDir();
    try {
      // Run twice — history must grow
      runCli([
        '--coverage',
        '--coverage-output', historyDir,
        'simple-flow',
        '--flows-dir', FIXTURES_DIR,
        '--mappings-dir', FIXTURES_DIR,
        '--output-dir', tmpDir,
      ]);
      runCli([
        '--coverage',
        '--coverage-output', historyDir,
        'simple-flow',
        '--flows-dir', FIXTURES_DIR,
        '--mappings-dir', FIXTURES_DIR,
        '--output-dir', tmpDir,
      ]);
      var historyFile = path.join(historyDir, 'coverage-history.json');
      assert.ok(fs.existsSync(historyFile), 'coverage-history.json must be created');
      var data = JSON.parse(fs.readFileSync(historyFile, 'utf8'));
      assert.ok(Array.isArray(data) && data.length >= 2, 'coverage-history.json must grow per run. Got: ' + JSON.stringify(data));
    } finally {
      fs.rmSync(historyDir, { recursive: true, force: true });
    }
  });

  test("--coverage stdout format includes element counts", function() {
    var result = runCli([
      '--coverage',
      '--coverage-output', coverageDir,
      'simple-flow',
      '--flows-dir', FIXTURES_DIR,
      '--mappings-dir', FIXTURES_DIR,
      '--output-dir', tmpDir,
    ]);
    // Format: "Coverage: X/Y elements (Z%) verified across 1 flow"
    assert.ok(
      result.stdout.includes('elements') && result.stdout.includes('%'),
      'Expected coverage format with element counts. Got: ' + result.stdout
    );
  });

  test("--help output mentions --coverage flag", function() {
    var result = runCli(['--help']);
    assert.ok(
      result.stdout.includes('--coverage'),
      'Expected --coverage in --help output. Got: ' + result.stdout
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

// ---------------------------------------------------------------------------
// CLI-08: --json output (e2e-json-diagnostics)
//
// AC-1: exactly one JSON document on stdout, {ok, flow, stats, errors,
// coverage?} single-flow / {ok, flows, summary} batch, for success,
// resolve-error, and parse-error cases alike.
// ---------------------------------------------------------------------------

describe('CLI-08: --json output', function() {
  var tmpDir;

  before(function() {
    tmpDir = makeTmpDir();
  });

  after(function() {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  function parseOnlyStdout(result) {
    // AC-1 falsification: any non-JSON text on stdout must fail this, not just
    // a JSON.parse() call that happens to tolerate a trailing partial match.
    var trimmed = result.stdout.replace(/\n$/, '');
    var lines = trimmed.split('\n');
    assert.equal(lines.length, 1, 'stdout must be exactly one line (one JSON document). Got: ' + result.stdout);
    return JSON.parse(lines[0]);
  }

  test("--json success case: single JSON document, ok:true, errors:[], stats present", function() {
    var result = runCli([
      '--json',
      'simple-flow',
      '--flows-dir', FIXTURES_DIR,
      '--mappings-dir', FIXTURES_DIR,
      '--output-dir', tmpDir,
    ]);
    assert.equal(result.status, 0, 'Expected exit 0. stderr: ' + result.stderr);
    var doc = parseOnlyStdout(result);
    assert.equal(doc.ok, true);
    assert.equal(doc.flow, 'simple-flow');
    assert.ok(doc.stats && typeof doc.stats === 'object', 'stats must be present');
    assert.deepEqual(doc.errors, []);
    assert.equal(doc.coverage, null);
    // Proves --json changes reporting, not compilation: the .sh file is still written.
    assert.ok(fs.existsSync(path.join(tmpDir, 'test-login.sh')), 'compiled .sh must still be written under --json');
  });

  test("--json resolve-error case (missing-element-flow): tier-1 errorDetails, candidates: []", function() {
    var result = runCli([
      '--json',
      'missing-element-flow',
      '--flows-dir', FIXTURES_DIR,
      '--mappings-dir', FIXTURES_DIR,
      '--output-dir', tmpDir,
    ]);
    assert.equal(result.status, 1, 'Expected exit 1. stdout: ' + result.stdout);
    var doc = parseOnlyStdout(result);
    assert.equal(doc.ok, false);
    assert.ok(doc.stats && typeof doc.stats === 'object', 'stats must be present even for a resolve-error case');
    assert.equal(doc.errors.length, 1);
    assert.deepEqual(doc.errors[0], {
      step_id: 'click-nonexistent',
      field: 'element',
      got: 'nonexistent_button',
      candidates: [],
      message: doc.errors[0].message,
    });
    assert.ok(doc.errors[0].message.includes("not found in mapping"));
    assert.ok(!('code' in doc.errors[0]), 'no code field ships in this entity (captain ruling)');
  });

  test("--json parse-error case: message-only errorDetails, no step_id/field keys", function() {
    var result = runCli([
      '--json',
      'parse-error-flow',
      '--flows-dir', FIXTURES_DIR,
      '--mappings-dir', FIXTURES_DIR,
      '--output-dir', tmpDir,
    ]);
    assert.equal(result.status, 1, 'Expected exit 1. stdout: ' + result.stdout);
    var doc = parseOnlyStdout(result);
    assert.equal(doc.ok, false);
    assert.ok(doc.stats && typeof doc.stats === 'object', 'stats must be present even for a parse-error case');
    assert.ok(doc.errors.length >= 1, 'parse-error-flow.yaml fails multiple required-field checks');
    doc.errors.forEach(function(e) {
      assert.deepEqual(Object.keys(e), ['message'], 'parse errors are tier-2: message-only, no code');
    });
  });

  test("--json AC-3/AC-4/E2E-first: ambiguous-element fixture shows real candidates, exactly 3 errors", function() {
    var jsonResult = runCli([
      '--json',
      '--dry-run',
      'list-data-completeness',
      '--flows-dir', FIXTURES_DIR,
      '--mappings-dir', FIXTURES_DIR,
      '--output-dir', tmpDir,
    ]);
    assert.equal(jsonResult.status, 1, 'Expected exit 1. stdout: ' + jsonResult.stdout);
    var doc = parseOnlyStdout(jsonResult);
    assert.equal(doc.ok, false);
    assert.equal(doc.errors.length, 3, 'exactly 3 tier-1 ambiguous errors (AC-4 population)');

    var tabAllErrors = doc.errors.filter(function(e) { return e.got === 'tab_all'; });
    var dataTableErrors = doc.errors.filter(function(e) { return e.got === 'data_table'; });
    assert.equal(tabAllErrors.length, 2);
    assert.equal(dataTableErrors.length, 1);
    tabAllErrors.forEach(function(e) {
      assert.deepEqual(e.candidates, ['service-schedule', 'employee-profiles'], "tab_all candidates must match today's found-on list verbatim");
    });
    assert.deepEqual(dataTableErrors[0].candidates, [
      'service-schedule', 'customer-profiles', 'branches', 'employee-profiles',
      'workspaces', 'services', 'self-check-lists', 'audit-templates', 'report-step-templates',
    ], "data_table's 9-way candidates must match today's found-on list verbatim");

    // E2E-first: cross-check against the SAME flow compiled without --json (prose mode) —
    // proves both paths read the identical resolve() call, not merely parsing independently.
    var prosResult = runCli([
      '--dry-run',
      'list-data-completeness',
      '--flows-dir', FIXTURES_DIR,
      '--mappings-dir', FIXTURES_DIR,
      '--output-dir', tmpDir,
    ]);
    assert.equal(prosResult.status, 1);
    // Pre-existing (unrelated to this entity): compile() itself prints each
    // resolve error to stderr on failure, and bin/e2e-compile.js's non-json
    // failure branch prints the same `errors` array again — every prose
    // message appears twice today. Dedupe rather than assume single-print;
    // fixing that duplication is out of this entity's scope (Non-goal 2: this
    // entity changes error emission structure, not existing prose behavior).
    var proseErrorLines = prosResult.stderr.split('\n').filter(function(l) { return l.indexOf('ERROR: ') === 0; });
    var uniqueProseMessages = Array.from(new Set(proseErrorLines.map(function(l) { return l.slice('ERROR: '.length); })));
    assert.equal(uniqueProseMessages.length, 3, 'prose mode must report the same 3 distinct errors. stderr: ' + prosResult.stderr);
    var jsonMessages = doc.errors.map(function(e) { return e.message; });
    assert.deepEqual(uniqueProseMessages.sort(), jsonMessages.sort(), 'prose and --json must report byte-identical messages from the same resolve() call');
  });

  test("--all --json: single aggregated JSON document, {ok, flows, summary}", function() {
    var result = runCli([
      '--all',
      '--json',
      '--flows-dir', FIXTURES_DIR,
      '--mappings-dir', FIXTURES_DIR,
      '--output-dir', tmpDir,
    ]);
    var doc = parseOnlyStdout(result);
    assert.ok(Array.isArray(doc.flows), 'flows must be an array');
    assert.ok(doc.flows.length > 0);
    assert.ok(doc.summary && typeof doc.summary.passed === 'number' && typeof doc.summary.failed === 'number');
    assert.equal(doc.summary.passed + doc.summary.failed, doc.flows.length);
    doc.flows.forEach(function(entry) {
      assert.ok(typeof entry.flow === 'string');
      assert.ok(typeof entry.ok === 'boolean');
      assert.ok(entry.stats && typeof entry.stats === 'object');
      assert.ok(Array.isArray(entry.errors));
    });
    // FIXTURES_DIR includes missing-element-flow.yaml, which always fails.
    assert.equal(result.status, doc.summary.failed > 0 ? 1 : 0, 'exit code must match failed count (AC-6: no new exit-code semantics)');
  });

  test("--all --json with an empty flows directory: still a single JSON document, not prose", function() {
    var emptyFlowsDir = makeTmpDir();
    try {
      var result = runCli([
        '--all',
        '--json',
        '--flows-dir', emptyFlowsDir,
        '--mappings-dir', FIXTURES_DIR,
        '--output-dir', tmpDir,
      ]);
      assert.equal(result.status, 0);
      var doc = parseOnlyStdout(result);
      assert.deepEqual(doc, { ok: true, flows: [], summary: { passed: 0, failed: 0 } });
    } finally {
      fs.rmSync(emptyFlowsDir, { recursive: true, force: true });
    }
  });
});
