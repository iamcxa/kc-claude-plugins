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

function writeYaml(filePath, content) {
  fs.writeFileSync(filePath, content.trimStart() + '\n', 'utf8');
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

  test("--json AC-3/AC-4/E2E-first: unqualified ambiguous element shows real candidates", function() {
    var localDir = makeTmpDir();
    try {
      writeYaml(path.join(localDir, 'ambiguous-map.yaml'), `
version: 2
app: ambiguous
base_url: http://localhost:3000
pages:
  page-a:
    url_pattern: /a
    elements:
      data_table:
        selector: role=table[name="A"]
  page-b:
    url_pattern: /b
    elements:
      data_table:
        selector: role=table[name="B"]
`);
      writeYaml(path.join(localDir, 'ambiguous-flow.yaml'), `
name: ambiguous-flow
mapping: ambiguous-map
steps:
  - id: click-table
    type: click
    action: Click data_table
`);
      var jsonResult = runCli([
        '--json',
        '--dry-run',
        'ambiguous-flow',
        '--flows-dir', localDir,
        '--mappings-dir', localDir,
        '--output-dir', tmpDir,
      ]);
      assert.equal(jsonResult.status, 1, 'Expected exit 1. stdout: ' + jsonResult.stdout);
      var doc = parseOnlyStdout(jsonResult);
      assert.equal(doc.ok, false);
      assert.equal(doc.errors.length, 1, 'one tier-1 ambiguous error');
      assert.deepEqual(doc.errors[0], {
        step_id: 'click-table',
        field: 'element',
        got: 'data_table',
        candidates: ['page-a', 'page-b'],
        message: doc.errors[0].message,
      });

      // E2E-first: cross-check against the SAME flow compiled without --json.
      var prosResult = runCli([
        '--dry-run',
        'ambiguous-flow',
        '--flows-dir', localDir,
        '--mappings-dir', localDir,
        '--output-dir', tmpDir,
      ]);
      assert.equal(prosResult.status, 1);
      var proseErrorLines = prosResult.stderr.split('\n').filter(function(l) { return l.indexOf('ERROR: ') === 0; });
      var uniqueProseMessages = Array.from(new Set(proseErrorLines.map(function(l) { return l.slice('ERROR: '.length); })));
      assert.deepEqual(uniqueProseMessages, [doc.errors[0].message], 'prose and --json must report byte-identical messages from the same resolve() call');
    } finally {
      fs.rmSync(localDir, { recursive: true, force: true });
    }
  });

  test("--json 3t page binding: page and element diagnostics keep tier-1 keys and candidates", function() {
    var localDir = makeTmpDir();
    try {
      writeYaml(path.join(localDir, 'page-binding-map.yaml'), `
version: 2
app: page-binding
base_url: http://localhost:3000
pages:
  login:
    url_pattern: /login
    elements: {}
  dashboard:
    url_pattern: /dashboard
    elements:
      heading:
        selector: role=heading[name="Dashboard"]
`);
      writeYaml(path.join(localDir, 'page-binding-flow.yaml'), `
name: page-binding-flow
mapping: page-binding-map
steps:
  - id: wrong-page
    type: click
    action: Click heading on login
  - id: missing-page
    type: click
    action: Click heading on dashbord
`);
      var result = runCli([
        '--json',
        '--dry-run',
        'page-binding-flow',
        '--flows-dir', localDir,
        '--mappings-dir', localDir,
        '--output-dir', tmpDir,
      ]);
      assert.equal(result.status, 1, 'Expected exit 1. stdout: ' + result.stdout + ' stderr: ' + result.stderr);
      var doc = parseOnlyStdout(result);
      assert.equal(doc.ok, false);
      assert.equal(doc.errors.length, 2);
      assert.deepEqual(Object.keys(doc.errors[0]), ['step_id', 'field', 'got', 'candidates', 'message']);
      assert.deepEqual(doc.errors[0], {
        step_id: 'wrong-page',
        field: 'element',
        got: 'heading',
        candidates: ['dashboard'],
        message: doc.errors[0].message,
      });
      assert.ok(doc.errors[0].message.includes("not found on page 'login'"));
      assert.ok(doc.errors[0].message.includes('shared: true'));

      assert.deepEqual(Object.keys(doc.errors[1]), ['step_id', 'field', 'got', 'candidates', 'message']);
      assert.deepEqual(doc.errors[1], {
        step_id: 'missing-page',
        field: 'page',
        got: 'dashbord',
        candidates: ['login', 'dashboard'],
        message: doc.errors[1].message,
      });
      assert.ok(doc.errors[1].message.includes("page 'dashbord' not found in mapping"));
    } finally {
      fs.rmSync(localDir, { recursive: true, force: true });
    }
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

  // -------------------------------------------------------------------------
  // AC-1 escape hatches: three --json invocation shapes that left stdout empty
  // or prose-filled. SKILL.md's rewritten Phase 3 depends on the single-document
  // guarantee unconditionally — it has no prose fallback left — so each of these
  // is a silent break for the skill, not a cosmetic gap.
  // -------------------------------------------------------------------------

  test("--all --json with an UNREADABLE flows directory: JSON document, distinct from the empty-dir shape", function() {
    var missingDir = path.join(makeTmpDir(), 'definitely-not-here');
    var result = runCli([
      '--all',
      '--json',
      '--flows-dir', missingDir,
      '--mappings-dir', FIXTURES_DIR,
      '--output-dir', tmpDir,
    ]);
    assert.equal(result.status, 1, 'an unreadable flows dir is a failure, unlike an empty one');
    var doc = parseOnlyStdout(result);
    assert.equal(doc.ok, false);
    assert.deepEqual(doc.flows, []);
    assert.deepEqual(doc.summary, { passed: 0, failed: 0 });
    assert.equal(doc.errors.length, 1, 'the enumeration failure must be representable in the document');
    assert.deepEqual(Object.keys(doc.errors[0]), ['message'], 'tier-2: no symbol, so message-only');
    assert.ok(doc.errors[0].message.includes(missingDir), 'message names the directory it could not read');
  });

  test("--json single flow with an unwritable output dir: JSON document, not empty stdout", function() {
    // Force a deterministic write failure by passing a path that already exists
    // as a FILE — mkdirSync(recursive) throws EEXIST. Preferred over chmod 500,
    // which is a no-op when tests run as root (CI containers commonly do).
    var blocker = path.join(makeTmpDir(), 'not-a-directory');
    fs.writeFileSync(blocker, 'blocker', 'utf8');
    var result = runCli([
      '--json',
      'simple-flow',
      '--flows-dir', FIXTURES_DIR,
      '--mappings-dir', FIXTURES_DIR,
      '--output-dir', blocker,
    ]);
    assert.equal(result.status, 1);
    var doc = parseOnlyStdout(result);
    assert.equal(doc.ok, false);
    assert.equal(doc.flow, 'simple-flow');
    assert.ok(doc.stats && typeof doc.stats === 'object', 'stats present even when compile threw');
    assert.equal(doc.errors.length, 1);
    assert.deepEqual(Object.keys(doc.errors[0]), ['message'], 'a thrown write error is tier-2');
    assert.ok(doc.errors[0].message.length > 0, 'the thrown error text must survive into the document');
  });

  test("--json with no flow name and no --all: JSON document on stdout, help prose on stderr, exit 1", function() {
    var result = runCli(['--json']);
    assert.equal(result.status, 1, 'nothing was compiled — must not report success (it exited 0 before)');
    var doc = parseOnlyStdout(result);
    assert.equal(doc.ok, false);
    assert.equal(doc.errors.length, 1);
    assert.deepEqual(Object.keys(doc.errors[0]), ['message']);
    assert.ok(
      /--all/.test(doc.errors[0].message) && /flow/i.test(doc.errors[0].message),
      'the message must say what the caller failed to supply. Got: ' + doc.errors[0].message
    );
    assert.ok(result.stderr.includes('Usage:'), 'a human running --json by hand still gets the usage text, on stderr');
  });
});
