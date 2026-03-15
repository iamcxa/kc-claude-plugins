'use strict';

/**
 * integration.test.js — end-to-end integration test.
 *
 * Copies the login-flow.yaml from the carlove corpus to a temp directory,
 * runs migrate.js on the copy, then compiles with compiler.js.
 * Asserts the generated .sh file is syntactically valid and well-formed.
 *
 * IMPORTANT: Original corpus files are NEVER modified.
 */

const { test, describe } = require('node:test');
const assert = require('node:assert/strict');
const fs     = require('node:fs');
const os     = require('node:os');
const path   = require('node:path');
const childProcess = require('node:child_process');

const { migrate }  = require('../migrate');
const { compile }  = require('../compiler');

// ---------------------------------------------------------------------------
// Corpus paths (read-only — never modified)
// ---------------------------------------------------------------------------

var CORPUS_FLOW     = '/Users/kent/Project/carlove/.claude/e2e/flows/login-flow.yaml';
var CORPUS_MAPPING  = '/Users/kent/Project/carlove/.claude/e2e/mappings';  // directory

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function mktemp() {
  return fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-integration-'));
}

function cleanup(dir) {
  fs.rmSync(dir, { recursive: true, force: true });
}

// ---------------------------------------------------------------------------
// Integration tests
// ---------------------------------------------------------------------------

describe('Integration: migrate + compile real carlove flow', function() {

  test('corpus files exist and are readable', function() {
    assert.ok(fs.existsSync(CORPUS_FLOW),    'login-flow.yaml must exist: ' + CORPUS_FLOW);
    assert.ok(fs.existsSync(CORPUS_MAPPING), 'mapping directory must exist: ' + CORPUS_MAPPING);
    assert.ok(
      fs.existsSync(path.join(CORPUS_MAPPING, 'secha-office.yaml')),
      'secha-office.yaml must exist in mapping dir'
    );
  });

  test('migrate produces a typed copy without modifying the original', async function() {
    var tmpDir = mktemp();
    try {
      // Copy flow to temp dir
      var tmpFlow = path.join(tmpDir, 'login-flow.yaml');
      fs.copyFileSync(CORPUS_FLOW, tmpFlow);

      // Remember original content fingerprint
      var originalContent = fs.readFileSync(CORPUS_FLOW, 'utf8');

      // Run migrate on the COPY (useClaude: false — unit test, no external call)
      var result = migrate(tmpFlow, { useClaude: false });

      // Corpus file must be unmodified
      var afterContent = fs.readFileSync(CORPUS_FLOW, 'utf8');
      assert.equal(afterContent, originalContent, 'original corpus file must not be modified');

      // At least some steps should be annotated
      assert.ok(result.annotated > 0, 'migrate() must annotate at least 1 step, got: ' + result.annotated);

      // The migrated copy must have type: fields
      var migratedText = fs.readFileSync(tmpFlow, 'utf8');
      assert.ok(migratedText.includes('type:'), 'migrated YAML must contain type: fields');

    } finally {
      cleanup(tmpDir);
    }
  });

  test('full pipeline: migrate -> compile -> bash -n passes', async function() {
    var tmpDir    = mktemp();
    var outDir    = path.join(tmpDir, 'compiled');
    try {
      // Step 1: Copy
      var tmpFlow = path.join(tmpDir, 'login-flow.yaml');
      fs.copyFileSync(CORPUS_FLOW, tmpFlow);

      // Step 2: Migrate (no claude -p in CI)
      migrate(tmpFlow, { useClaude: false });

      // Step 3: Compile
      var compileResult = await compile(tmpFlow, CORPUS_MAPPING, outDir);

      assert.ok(compileResult.success, 'compile() must succeed. errors: ' + JSON.stringify(compileResult.errors));
      assert.ok(compileResult.outputPath, 'compile() must return outputPath');
      assert.ok(fs.existsSync(compileResult.outputPath), 'output .sh must exist on disk');

      // Step 4: Verify the generated script
      var script = fs.readFileSync(compileResult.outputPath, 'utf8');

      assert.ok(
        script.startsWith('#!/usr/bin/env bash'),
        'script must start with #!/usr/bin/env bash'
      );

      assert.ok(
        script.includes('agent-browser'),
        'script must contain agent-browser commands'
      );

      assert.ok(
        /\[\d+\/\d+\]/.test(script),
        'script must contain [N/T] step logging'
      );

      assert.ok(
        script.includes('PASS'),
        'script must end with PASS summary'
      );

      // Step 5: bash -n syntax check — uses spawnSync to avoid shell injection
      var bashCheck = childProcess.spawnSync('bash', ['-n', compileResult.outputPath], { stdio: 'pipe' });
      assert.equal(bashCheck.status, 0, 'bash -n syntax check must exit 0');

    } finally {
      cleanup(tmpDir);
    }
  });

  test('generated script ends with exit 0 path', async function() {
    var tmpDir = mktemp();
    var outDir = path.join(tmpDir, 'compiled');
    try {
      var tmpFlow = path.join(tmpDir, 'login-flow.yaml');
      fs.copyFileSync(CORPUS_FLOW, tmpFlow);
      migrate(tmpFlow, { useClaude: false });

      var compileResult = await compile(tmpFlow, CORPUS_MAPPING, outDir);
      assert.ok(compileResult.success);

      var script = fs.readFileSync(compileResult.outputPath, 'utf8');

      // PASS block ends with exit 0
      assert.ok(
        script.includes('exit 0'),
        'script must contain exit 0 in PASS block'
      );
    } finally {
      cleanup(tmpDir);
    }
  });

  test('original corpus files are not modified after all operations', function() {
    // Final guard — re-read corpus file and confirm it has no type: field
    // (corpus flows are pre-migration, so they should not have type: fields)
    var original = fs.readFileSync(CORPUS_FLOW, 'utf8');

    // login-flow.yaml has no type: fields in any step before migration
    var yaml = require('js-yaml');
    var flow = yaml.load(original);
    var hasTypeField = flow.steps.some(function(s) { return s.type; });
    assert.equal(hasTypeField, false, 'corpus flow must not have type: fields (should be pre-migration state)');
  });

});
