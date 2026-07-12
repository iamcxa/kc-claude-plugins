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
const NO_VARS_FLOW = path.join(FIXTURES_DIR, 'no-vars-flow.yaml');
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
// compile() — flow without variables block auto-injects BASE_URL from mapping
// ---------------------------------------------------------------------------

describe('compile() — flow without variables block', function() {
  var tmpDir;

  before(function() {
    tmpDir = makeTmpDir();
  });

  after(function() {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  test("flow without variables block still has BASE_URL declared in output", async function() {
    const result = await compile(NO_VARS_FLOW, FIXTURES_DIR, tmpDir);
    assert.ok(result.success, 'Compile should succeed. Errors: ' + JSON.stringify(result.errors));
    const content = fs.readFileSync(result.outputPath, 'utf8');
    assert.ok(content.includes('BASE_URL='), 'Expected BASE_URL= declaration even without variables block');
  });

  test("BASE_URL is declared before first ${BASE_URL} reference", async function() {
    const result = await compile(NO_VARS_FLOW, FIXTURES_DIR, tmpDir);
    const content = fs.readFileSync(result.outputPath, 'utf8');
    const lines = content.split('\n');
    var declLine = -1;
    var firstRefLine = -1;
    for (var i = 0; i < lines.length; i++) {
      if (declLine === -1 && lines[i].includes('BASE_URL=')) declLine = i;
      if (firstRefLine === -1 && lines[i].includes('${BASE_URL}')) firstRefLine = i;
    }
    assert.ok(declLine !== -1, 'BASE_URL= must exist');
    assert.ok(firstRefLine !== -1, '${BASE_URL} reference must exist');
    assert.ok(declLine < firstRefLine, 'Declaration must come before reference');
  });

  test("auto-injected BASE_URL uses mapping base_url as default value", async function() {
    const result = await compile(NO_VARS_FLOW, FIXTURES_DIR, tmpDir);
    const content = fs.readFileSync(result.outputPath, 'utf8');
    assert.ok(
      content.includes('http://localhost:3000'),
      'Expected mapping base_url as default. Got: ' + content.slice(0, 500)
    );
  });

  test("bash -n syntax check passes on flow without variables", async function() {
    const result = await compile(NO_VARS_FLOW, FIXTURES_DIR, tmpDir);
    const bashResult = spawnSync('bash', ['-n', result.outputPath], { encoding: 'utf8' });
    assert.equal(bashResult.status, 0, 'bash -n failed. stderr: ' + bashResult.stderr);
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

// ---------------------------------------------------------------------------
// Phase 2 Plan 02: cross-site integration — compile cross-site-flow.yaml
// ---------------------------------------------------------------------------

const CROSS_SITE_FLOW_PATH = path.join(FIXTURES_DIR, 'cross-site-flow.yaml');

describe('compile() — cross-site flow integration', function() {
  var tmpDir;
  var outputPath;
  var outputContent;

  before(async function() {
    tmpDir = makeTmpDir();
    const result = await compile(CROSS_SITE_FLOW_PATH, FIXTURES_DIR, tmpDir);
    assert.ok(result.success, 'Cross-site compile must succeed. Errors: ' + JSON.stringify(result.errors));
    outputPath = result.outputPath;
    outputContent = fs.readFileSync(outputPath, 'utf8');
  });

  after(function() {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  test("cross-site compile returns success=true", async function() {
    // Already verified in before() — just assert the outputPath
    assert.ok(outputPath, 'outputPath must be set');
    assert.ok(fs.existsSync(outputPath), 'output file must exist');
  });

  test("compiled output contains shell-quoted office session prefix", function() {
    assert.ok(
      outputContent.includes("--session 'office'"),
      "Expected --session 'office' in output. Got snippet: " + outputContent.slice(0, 500)
    );
  });

  test("compiled output contains shell-quoted app session prefix", function() {
    assert.ok(
      outputContent.includes("--session 'app'"),
      "Expected --session 'app' in output. Got snippet: " + outputContent.slice(0, 500)
    );
  });

  test("compiled output contains OFFICE_BASE_URL variable", function() {
    assert.ok(
      outputContent.includes('OFFICE_BASE_URL'),
      'Expected OFFICE_BASE_URL in output. Got snippet: ' + outputContent.slice(0, 500)
    );
  });

  test("compiled output contains APP_BASE_URL variable", function() {
    assert.ok(
      outputContent.includes('APP_BASE_URL'),
      'Expected APP_BASE_URL in output. Got snippet: ' + outputContent.slice(0, 500)
    );
  });

  test("cross-site compiled script passes bash -n syntax check", function() {
    const result = spawnSync('bash', ['-n', outputPath], { encoding: 'utf8' });
    assert.equal(result.status, 0, 'bash -n failed. stderr: ' + result.stderr);
  });
});

describe('compile() — cross-site site-name validation', function() {
  test('rejects inherited Object prototype names when they are not declared sites', async function() {
    for (const undeclaredSite of ['toString', 'valueOf']) {
      const tmpDir = makeTmpDir();
      const flowPath = path.join(tmpDir, 'undeclared-' + undeclaredSite + '.json');
      fs.writeFileSync(flowPath, JSON.stringify({
        name: 'undeclared-' + undeclaredSite,
        sites: { office: { mapping: 'site-a' } },
        steps: [{
          id: 'check-' + undeclaredSite,
          site: undeclaredSite,
          type: 'snapshot',
          action: 'Take snapshot',
        }],
      }), 'utf8');

      try {
        const result = await compile(flowPath, FIXTURES_DIR, tmpDir);
        assert.equal(result.success, false, undeclaredSite + ' must be rejected without throwing');
        assert.ok(
          result.errors.some(error => error.includes("unknown site '" + undeclaredSite + "'")),
          'error must identify the undeclared site: ' + JSON.stringify(result.errors)
        );
        assert.equal(
          fs.existsSync(path.join(tmpDir, 'undeclared-' + undeclaredSite + '.sh')),
          false,
          'rejected flow must not produce output'
        );
      } finally {
        fs.rmSync(tmpDir, { recursive: true, force: true });
      }
    }
  });

  test('accepts an explicitly declared toString site alias', async function() {
    const tmpDir = makeTmpDir();
    const flowPath = path.join(tmpDir, 'declared-tostring.json');
    fs.writeFileSync(flowPath, JSON.stringify({
      name: 'declared-tostring',
      sites: { toString: { mapping: 'site-a' } },
      steps: [{ id: 'declared-site', site: 'toString', type: 'snapshot', action: 'Take snapshot' }],
    }), 'utf8');

    try {
      const result = await compile(flowPath, FIXTURES_DIR, tmpDir);
      assert.equal(result.success, true, 'declared valid alias must compile: ' + JSON.stringify(result.errors));
      assert.ok(fs.existsSync(result.outputPath), 'declared valid alias must produce output');
    } finally {
      fs.rmSync(tmpDir, { recursive: true, force: true });
    }
  });

  test('rejects a hostile site name before code generation or execution', async function() {
    const tmpDir = makeTmpDir();
    const hostileSite = 'x:-$(/usr/bin/touch "$SITE_MARKER")';
    const flowPath = path.join(tmpDir, 'hostile-site.json');
    const markerPath = path.join(tmpDir, 'site-expanded');
    const binDir = path.join(tmpDir, 'bin');
    fs.mkdirSync(binDir);
    const browserPath = path.join(binDir, 'agent-browser');
    fs.writeFileSync(browserPath, '#!/bin/bash\nexit 0\n', 'utf8');
    fs.chmodSync(browserPath, 0o755);
    fs.writeFileSync(flowPath, JSON.stringify({
      name: 'hostile-site-name',
      sites: { [hostileSite]: { mapping: 'site-b' } },
      steps: [{
        id: 'navigate-home',
        site: hostileSite,
        type: 'navigate',
        action: 'Navigate to /home',
      }],
    }), 'utf8');

    try {
      const result = await compile(flowPath, FIXTURES_DIR, tmpDir);
      if (result.success && result.outputPath) {
        spawnSync('/bin/bash', [result.outputPath], {
          encoding: 'utf8',
          env: Object.assign({}, process.env, {
            PATH: binDir + path.delimiter + process.env.PATH,
            SITE_MARKER: markerPath,
          }),
        });
      }
      assert.equal(result.success, false, 'hostile site name must be rejected before codegen');
      assert.ok(
        result.errors.some(error =>
          error.includes(hostileSite) && error.includes('^[A-Za-z_][A-Za-z0-9_]*$')
        ),
        'validation error must name the site and accepted format: ' + JSON.stringify(result.errors)
      );
      assert.equal(fs.existsSync(markerPath), false, 'hostile site name must never execute');
      assert.equal(fs.existsSync(path.join(tmpDir, 'hostile-site-name.sh')), false, 'rejected flow must not produce a script');
    } finally {
      fs.rmSync(tmpDir, { recursive: true, force: true });
    }
  });

  test('accepts shell-identifier site names including underscore forms', async function() {
    const tmpDir = makeTmpDir();
    const flowPath = path.join(tmpDir, 'valid-sites.json');
    fs.writeFileSync(flowPath, JSON.stringify({
      name: 'valid-site-names',
      sites: {
        _office: { mapping: 'site-a' },
        app_2: { mapping: 'site-b' },
      },
      steps: [
        { id: 'office-home', site: '_office', type: 'navigate', action: 'Navigate to /dashboard' },
        { id: 'app-home', site: 'app_2', type: 'navigate', action: 'Navigate to /home' },
      ],
    }), 'utf8');

    try {
      const result = await compile(flowPath, FIXTURES_DIR, tmpDir);
      assert.equal(result.success, true, 'valid site names must compile: ' + JSON.stringify(result.errors));
      const output = fs.readFileSync(result.outputPath, 'utf8');
      assert.match(output, /_OFFICE_BASE_URL/);
      assert.match(output, /APP_2_BASE_URL/);
    } finally {
      fs.rmSync(tmpDir, { recursive: true, force: true });
    }
  });

  test('rejects the reserved __proto__ alias before producing output', async function() {
    const tmpDir = makeTmpDir();
    const flowPath = path.join(tmpDir, 'reserved-site.json');
    fs.writeFileSync(flowPath, JSON.stringify({
      name: 'reserved-site-name',
      sites: JSON.parse('{"__proto__":{"mapping":"site-b"}}'),
      steps: [{ id: 'reserved-home', site: '__proto__', type: 'navigate', action: 'Navigate to /home' }],
    }), 'utf8');

    try {
      const result = await compile(flowPath, FIXTURES_DIR, tmpDir);
      assert.equal(result.success, false, '__proto__ must be rejected before codegen');
      assert.ok(
        result.errors.some(error => error.includes('__proto__') && error.includes('reserved')),
        'error must name the reserved alias: ' + JSON.stringify(result.errors)
      );
      assert.equal(fs.existsSync(path.join(tmpDir, 'reserved-site-name.sh')), false);
    } finally {
      fs.rmSync(tmpDir, { recursive: true, force: true });
    }
  });

  test('rejects aliases that collide on normalized base URL variable', async function() {
    const tmpDir = makeTmpDir();
    const flowPath = path.join(tmpDir, 'colliding-sites.json');
    fs.writeFileSync(flowPath, JSON.stringify({
      name: 'colliding-site-names',
      sites: {
        office: { mapping: 'site-a' },
        OFFICE: { mapping: 'site-b' },
      },
      steps: [
        { id: 'lower-office', site: 'office', type: 'navigate', action: 'Navigate to /dashboard' },
        { id: 'upper-office', site: 'OFFICE', type: 'navigate', action: 'Navigate to /home' },
      ],
    }), 'utf8');

    try {
      const result = await compile(flowPath, FIXTURES_DIR, tmpDir);
      assert.equal(result.success, false, 'normalized env-key collision must be rejected');
      assert.ok(
        result.errors.some(error =>
          error.includes('office') && error.includes('OFFICE') && error.includes('OFFICE_BASE_URL')
        ),
        'error must name both aliases and normalized key: ' + JSON.stringify(result.errors)
      );
      assert.equal(fs.existsSync(path.join(tmpDir, 'colliding-site-names.sh')), false);
    } finally {
      fs.rmSync(tmpDir, { recursive: true, force: true });
    }
  });
});

describe('compile() — normalized flow variable validation', function() {
  test('accepts a valid variable key that shadows an Object prototype method', async function() {
    const tmpDir = makeTmpDir();
    const flowPath = path.join(tmpDir, 'prototype-method-variable.json');
    fs.writeFileSync(flowPath, JSON.stringify({
      name: 'prototype-method-variable',
      variables: { hasOwnProperty: 'literal-value' },
      sites: { office: { mapping: 'site-a' } },
      steps: [{ id: 'office-home', site: 'office', type: 'navigate', action: 'Navigate to /dashboard' }],
    }), 'utf8');

    try {
      const result = await compile(flowPath, FIXTURES_DIR, tmpDir);
      assert.equal(result.success, true, 'valid shell identifier must not break own-key lookup: ' + JSON.stringify(result.errors));
      assert.ok(fs.existsSync(result.outputPath));
    } finally {
      fs.rmSync(tmpDir, { recursive: true, force: true });
    }
  });

  test('rejects a flow variable that collides with an injected site base URL', async function() {
    const tmpDir = makeTmpDir();
    const flowPath = path.join(tmpDir, 'site-variable-collision.json');
    fs.writeFileSync(flowPath, JSON.stringify({
      name: 'site-variable-collision',
      variables: { office_base_url: 'https://override.invalid' },
      sites: { office: { mapping: 'site-a' } },
      steps: [{ id: 'office-home', site: 'office', type: 'navigate', action: 'Navigate to /dashboard' }],
    }), 'utf8');

    try {
      const result = await compile(flowPath, FIXTURES_DIR, tmpDir);
      assert.equal(result.success, false, 'site variable collision must fail before codegen');
      assert.ok(
        result.errors.some(error =>
          error.includes('office_base_url') && error.includes('office') && error.includes('OFFICE_BASE_URL')
        ),
        'error must name both sources and normalized key: ' + JSON.stringify(result.errors)
      );
      assert.equal(fs.existsSync(path.join(tmpDir, 'site-variable-collision.sh')), false);
    } finally {
      fs.rmSync(tmpDir, { recursive: true, force: true });
    }
  });

  test('rejects user variable case collisions and invalid or reserved keys', async function() {
    const cases = [
      {
        name: 'user-variable-collision',
        variables: { token: 'one', TOKEN: 'two' },
        expected: ['token', 'TOKEN'],
      },
      { name: 'invalid-variable', variables: { 'api-token': 'secret' }, expected: ['api-token', 'shell identifier'] },
      {
        name: 'reserved-variable',
        variables: JSON.parse('{"__proto__":"secret"}'),
        expected: ['__proto__', 'reserved'],
      },
    ];

    for (const testCase of cases) {
      const tmpDir = makeTmpDir();
      const flowPath = path.join(tmpDir, testCase.name + '.json');
      fs.writeFileSync(flowPath, JSON.stringify({
        name: testCase.name,
        variables: testCase.variables,
        mapping: 'site-a',
        steps: [{ id: 'home', type: 'navigate', action: 'Navigate to /dashboard' }],
      }), 'utf8');
      try {
        const result = await compile(flowPath, FIXTURES_DIR, tmpDir);
        assert.equal(result.success, false, testCase.name + ' must fail before codegen');
        assert.ok(
          result.errors.some(error => testCase.expected.every(part => error.includes(part))),
          testCase.name + ' error must explain the offending keys: ' + JSON.stringify(result.errors)
        );
        assert.equal(fs.existsSync(path.join(tmpDir, testCase.name + '.sh')), false);
      } finally {
        fs.rmSync(tmpDir, { recursive: true, force: true });
      }
    }
  });
});

// ---------------------------------------------------------------------------
// Phase 2 Plan 03 Task 1: compile() dryRun and verbose options
// ---------------------------------------------------------------------------

describe('compile() dryRun and verbose options', function() {
  var tmpDir;

  before(function() {
    tmpDir = makeTmpDir();
  });

  after(function() {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  test("compile() with dryRun:true does NOT create output file", async function() {
    const dryDir = makeTmpDir();
    try {
      const result = await compile(SIMPLE_FLOW, FIXTURES_DIR, dryDir, { dryRun: true });
      // The output file must NOT exist
      const outFile = path.join(dryDir, 'test-login.sh');
      assert.ok(!fs.existsSync(outFile), 'DRY RUN must not create output file');
    } finally {
      fs.rmSync(dryDir, { recursive: true, force: true });
    }
  });

  test("compile() with dryRun:true still returns success:true with outputPath and stats", async function() {
    const dryDir = makeTmpDir();
    try {
      const result = await compile(SIMPLE_FLOW, FIXTURES_DIR, dryDir, { dryRun: true });
      assert.equal(result.success, true, 'Expected success=true even in dryRun mode');
      assert.ok(result.outputPath, 'Expected outputPath in dryRun result');
      assert.ok(result.stats, 'Expected stats in dryRun result');
    } finally {
      fs.rmSync(dryDir, { recursive: true, force: true });
    }
  });

  test("compile() with verbose:true still creates output file", async function() {
    const verbDir = makeTmpDir();
    try {
      const result = await compile(SIMPLE_FLOW, FIXTURES_DIR, verbDir, { verbose: true });
      assert.equal(result.success, true, 'Expected success=true with verbose');
      assert.ok(fs.existsSync(result.outputPath), 'verbose mode must still create output file');
    } finally {
      fs.rmSync(verbDir, { recursive: true, force: true });
    }
  });

  test("compile() with dryRun:true and verbose:true does NOT create file but returns success", async function() {
    const bothDir = makeTmpDir();
    try {
      const result = await compile(SIMPLE_FLOW, FIXTURES_DIR, bothDir, { dryRun: true, verbose: true });
      assert.equal(result.success, true, 'Expected success=true for dryRun+verbose');
      const outFile = path.join(bothDir, 'test-login.sh');
      assert.ok(!fs.existsSync(outFile), 'dryRun+verbose must not create output file');
    } finally {
      fs.rmSync(bothDir, { recursive: true, force: true });
    }
  });

  test("compile() with no options argument still works (backwards compat)", async function() {
    const compatDir = makeTmpDir();
    try {
      const result = await compile(SIMPLE_FLOW, FIXTURES_DIR, compatDir);
      assert.equal(result.success, true, 'Expected success=true with no options (backwards compat)');
      assert.ok(fs.existsSync(result.outputPath), 'Output file must exist with no options');
    } finally {
      fs.rmSync(compatDir, { recursive: true, force: true });
    }
  });
});

// ---------------------------------------------------------------------------
// Phase 2 Plan 02 Task 3: SHA-256 source hashing + header provenance
// ---------------------------------------------------------------------------

describe('SHA-256 source hashing', function() {
  var tmpDir;

  before(function() {
    tmpDir = makeTmpDir();
  });

  after(function() {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  test("compiled output from simple-flow.yaml contains '# SHA-256:' line", async function() {
    const result = await compile(SIMPLE_FLOW, FIXTURES_DIR, tmpDir);
    assert.ok(result.success, 'Compile must succeed. Errors: ' + JSON.stringify(result.errors));
    const content = fs.readFileSync(result.outputPath, 'utf8');
    assert.ok(
      content.includes('# SHA-256:'),
      'Expected SHA-256: line in output. Got header: ' + content.slice(0, 400)
    );
  });

  test("hash is deterministic: compile same flow twice, hashes match", async function() {
    const tmpDir2 = makeTmpDir();
    try {
      const result1 = await compile(SIMPLE_FLOW, FIXTURES_DIR, tmpDir);
      const result2 = await compile(SIMPLE_FLOW, FIXTURES_DIR, tmpDir2);
      const content1 = fs.readFileSync(result1.outputPath, 'utf8');
      const content2 = fs.readFileSync(result2.outputPath, 'utf8');

      const hashLine1 = content1.split('\n').find(l => l.startsWith('# SHA-256:'));
      const hashLine2 = content2.split('\n').find(l => l.startsWith('# SHA-256:'));

      assert.ok(hashLine1, 'Expected SHA-256: line in first compile output');
      assert.ok(hashLine2, 'Expected SHA-256: line in second compile output');
      assert.equal(hashLine1, hashLine2, 'Hashes must be identical for same source files');
    } finally {
      fs.rmSync(tmpDir2, { recursive: true, force: true });
    }
  });

  test("compiled output contains '# DO NOT EDIT' line", async function() {
    const result = await compile(SIMPLE_FLOW, FIXTURES_DIR, tmpDir);
    const content = fs.readFileSync(result.outputPath, 'utf8');
    assert.ok(
      content.includes('# DO NOT EDIT'),
      'Expected DO NOT EDIT line in output. Got header: ' + content.slice(0, 400)
    );
  });

  test("compiled output contains '# Source:' line with flow path", async function() {
    const result = await compile(SIMPLE_FLOW, FIXTURES_DIR, tmpDir);
    const content = fs.readFileSync(result.outputPath, 'utf8');
    assert.ok(
      content.includes('# Source: ' + SIMPLE_FLOW),
      'Expected Source: line with flow path. Got header: ' + content.slice(0, 400)
    );
  });

  test("cross-site compiled output also contains SHA-256 and DO NOT EDIT", async function() {
    const tmpDir2 = makeTmpDir();
    try {
      const result = await compile(CROSS_SITE_FLOW_PATH, FIXTURES_DIR, tmpDir2);
      assert.ok(result.success, 'Cross-site compile must succeed. Errors: ' + JSON.stringify(result.errors));
      const content = fs.readFileSync(result.outputPath, 'utf8');
      assert.ok(content.includes('# SHA-256:'), 'Cross-site output must have SHA-256:');
      assert.ok(content.includes('# DO NOT EDIT'), 'Cross-site output must have DO NOT EDIT');
    } finally {
      fs.rmSync(tmpDir2, { recursive: true, force: true });
    }
  });
});

// ---------------------------------------------------------------------------
// Phase 6 Plan 01: compile() with options.coverage
// ---------------------------------------------------------------------------

describe('compile() — options.coverage', function() {
  var tmpDir;

  before(function() {
    tmpDir = makeTmpDir();
  });

  after(function() {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  test("compile() with coverage:true returns result.coverage object", async function() {
    const result = await compile(SIMPLE_FLOW, FIXTURES_DIR, tmpDir, { coverage: true });
    assert.ok(result.success, 'Compile must succeed. Errors: ' + JSON.stringify(result.errors));
    assert.ok(result.coverage && typeof result.coverage === 'object', 'Expected result.coverage to be an object');
  });

  test("compile() with coverage:true returns result.coverage.elements array", async function() {
    const result = await compile(SIMPLE_FLOW, FIXTURES_DIR, tmpDir, { coverage: true });
    assert.ok(result.success, 'Compile must succeed');
    assert.ok(Array.isArray(result.coverage.elements), 'result.coverage.elements must be an array');
  });

  test("compile() with coverage:true returns result.coverage.summary object", async function() {
    const result = await compile(SIMPLE_FLOW, FIXTURES_DIR, tmpDir, { coverage: true });
    assert.ok(result.success, 'Compile must succeed');
    assert.ok(result.coverage.summary && typeof result.coverage.summary === 'object', 'result.coverage.summary must be an object');
  });

  test("compile() with coverage:false (default) does NOT include result.coverage", async function() {
    const tmpDir2 = makeTmpDir();
    try {
      const result = await compile(SIMPLE_FLOW, FIXTURES_DIR, tmpDir2, { coverage: false });
      assert.ok(result.success, 'Compile must succeed');
      assert.equal(result.coverage, undefined, 'result.coverage must not exist when coverage:false');
    } finally {
      fs.rmSync(tmpDir2, { recursive: true, force: true });
    }
  });

  test("compile() with no options does NOT include result.coverage", async function() {
    const tmpDir3 = makeTmpDir();
    try {
      const result = await compile(SIMPLE_FLOW, FIXTURES_DIR, tmpDir3);
      assert.ok(result.success, 'Compile must succeed');
      assert.equal(result.coverage, undefined, 'result.coverage must not exist with no options');
    } finally {
      fs.rmSync(tmpDir3, { recursive: true, force: true });
    }
  });

  test("compile() with coverage:true for cross-site flow does not crash (unsupported warning)", async function() {
    const tmpDir4 = makeTmpDir();
    try {
      const result = await compile(CROSS_SITE_FLOW_PATH, FIXTURES_DIR, tmpDir4, { coverage: true });
      assert.ok(result.success, 'Cross-site compile must succeed even with coverage:true');
      // Cross-site coverage is not yet supported — coverage should be null or undefined
      assert.ok(
        result.coverage === null || result.coverage === undefined,
        'Cross-site flow coverage should be null (not yet supported). Got: ' + JSON.stringify(result.coverage)
      );
    } finally {
      fs.rmSync(tmpDir4, { recursive: true, force: true });
    }
  });
});
