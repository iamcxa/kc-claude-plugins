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
const yaml = require('js-yaml');

const { migrate }  = require('../migrate');
const { compile }  = require('../compiler');

// ---------------------------------------------------------------------------
// Corpus paths (read-only — never modified)
//
// This is a real consumer's mapping/flow corpus, which lives outside this repository
// and is not published with it. These tests were written against an absolute path on
// one machine, so they passed there and could not pass anywhere else — including CI,
// where they surfaced as four ENOENT failures the first time the suite ran on a runner.
//
// Absent corpus is now a skip, not a failure. A test that cannot run in an environment
// should say so; failing there teaches everyone to ignore the red, which costs more than
// the coverage is worth. Point E2E_CORPUS_ROOT at a checkout to run them elsewhere.
// ---------------------------------------------------------------------------

var CORPUS_ROOT = process.env.E2E_CORPUS_ROOT || '/Users/kent/Project/carlove';
var CORPUS_FLOW     = path.join(CORPUS_ROOT, '.claude/e2e/flows/gate-login-flow.yaml');
var CORPUS_MAPPING  = path.join(CORPUS_ROOT, '.claude/e2e/mappings');  // directory
var CORPUS_PRESENT  = fs.existsSync(CORPUS_FLOW) && fs.existsSync(CORPUS_MAPPING);
var CORPUS_SKIP     = CORPUS_PRESENT
  ? false
  : 'corpus not present at ' + CORPUS_ROOT + ' (set E2E_CORPUS_ROOT to run)';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function mktemp() {
  return fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-integration-'));
}

function cleanup(dir) {
  fs.rmSync(dir, { recursive: true, force: true });
}

function copyCorpusMappingWithSyntheticVisibilityDomIdentity(tmpDir) {
  var mappingDir = path.join(tmpDir, 'mappings');
  fs.mkdirSync(mappingDir);
  var mappingPath = path.join(CORPUS_MAPPING, 'secha-office.yaml');
  var mapping = yaml.load(fs.readFileSync(mappingPath, 'utf8'));

  // This integration test keeps the external CarLove corpus read-only. These temporary,
  // synthetic CSS identities exercise compiler migration and do not claim equivalence
  // with the external application's computed accessible names; real-browser proof is
  // owned by the visibility runtime matrix.
  mapping.pages.dashboard.elements.daily_board_heading.css_selector =
    '[data-testid="dashboard-page"] h2';
  mapping.pages._global.elements.sidebar_dashboard.css_selector =
    '[role="menuitem"][aria-label="營運概況"]';
  mapping.pages._global.elements.sidebar_branches.css_selector =
    '[role="menuitem"][aria-label="門市管理"]';
  mapping.pages._global.elements.sidebar_catalog.css_selector =
    '[role="menuitem"][aria-label="服務目錄"]';
  mapping.pages._global.elements.sidebar_operations.css_selector =
    '[role="menuitem"][aria-label="營運管理"]';
  mapping.pages._global.elements.search_button.css_selector =
    'button[aria-label="開啟搜尋"]';
  mapping.pages._global.elements.dark_mode_toggle.css_selector =
    'button[aria-label^="切換為"][aria-label$="模式"]';

  fs.writeFileSync(
    path.join(mappingDir, 'secha-office.yaml'),
    yaml.dump(mapping, { lineWidth: -1 }),
    'utf8'
  );
  return mappingDir;
}

// ---------------------------------------------------------------------------
// Integration tests
// ---------------------------------------------------------------------------

describe('Integration: migrate + compile real carlove flow', { skip: CORPUS_SKIP }, function() {

  test('corpus files exist and are readable', function() {
    assert.ok(fs.existsSync(CORPUS_FLOW),    'gate-login-flow.yaml must exist: ' + CORPUS_FLOW);
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

      // Already-v2 flows may have 0 new annotations (all steps already typed)
      assert.ok(result.annotated >= 0, 'migrate() must return non-negative annotated count, got: ' + result.annotated);

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
      var mappingDir = copyCorpusMappingWithSyntheticVisibilityDomIdentity(tmpDir);
      var compileResult = await compile(tmpFlow, mappingDir, outDir);

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

      var mappingDir = copyCorpusMappingWithSyntheticVisibilityDomIdentity(tmpDir);
      var compileResult = await compile(tmpFlow, mappingDir, outDir);
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
    // Final guard — re-read corpus file and confirm content hasn't changed
    // (the copy-then-migrate pattern must never touch the original)
    var original = fs.readFileSync(CORPUS_FLOW, 'utf8');
    var flow = yaml.load(original);
    // gate-login-flow.yaml is already v2 (has type: fields) — just verify it parses and has steps
    assert.ok(flow.steps && flow.steps.length > 0, 'corpus flow must have steps');
    assert.ok(flow.mapping || flow.sites, 'corpus flow must have mapping or sites field (v2 format)');
  });

});

// ---------------------------------------------------------------------------
// Phase 5 Plan 01: JUnit XML codegen integration tests
// ---------------------------------------------------------------------------

const { generate } = require('../codegen');

describe('Integration: JUnit XML codegen (FLAG-01)', function() {

  test('compiled script keeps CJK step identity in all report forms', function() {
    var resolved = {
      name: 'cjk-flow',
      description: 'CJK step test',
      steps: [{
        id: '登入-login',
        action: 'Navigate to login',
        type: 'navigate',
        operands: { target: '/login', urlPath: '/login' },
      }],
    };
    var script = generate(resolved, 'cjk-flow');
    assert.ok(
      script.includes('_record_step_name "登入-login" "登入-login" "登入-login"'),
      'CJK step id must appear as UTF-8 in all identity forms. Got snippet: ' + script
    );
    var recordLine = script.split('\n').find(function(line) {
      return line.includes('_record_step_name "登入-login"');
    });
    assert.ok(recordLine && !recordLine.includes('&#'), 'CJK step identity must not use numeric entities. Got: ' + recordLine);
  });

  test('compiled script XML-escapes only the JUnit step identity', function() {
    var resolved = {
      name: 'xml-special-flow',
      description: 'XML special chars test',
      steps: [{
        id: 'check-<input>-field',
        action: 'Check input field',
        type: 'navigate',
        operands: { target: '/form', urlPath: '/form' },
      }],
    };
    var script = generate(resolved, 'xml-special-flow');
    assert.ok(
      script.includes(
        '_record_step_name "check-<input>-field" "check-<input>-field" "check-&lt;input&gt;-field"'
      ),
      'Angle bracket step id must keep raw/JSON identity and XML-escape JUnit identity. Got snippet: ' + script
    );
  });

  test('_emit_junit function body contains pre-escaped flow name (& → &amp;)', function() {
    var resolved = {
      name: 'login & signup',
      description: 'Login and signup flow',
      steps: [{
        id: 'nav-login',
        action: 'Navigate to login',
        type: 'navigate',
        operands: { target: '/login', urlPath: '/login' },
      }],
    };
    var script = generate(resolved, 'login & signup');
    var emitStart = script.indexOf('_emit_junit()');
    var emitEnd = script.lastIndexOf('}');
    var emitBody = script.slice(emitStart, emitEnd + 1);
    assert.ok(
      emitBody.includes('login &amp; signup'),
      'Flow name with & must be pre-escaped as &amp; in _emit_junit. Got body snippet: ' + emitBody.slice(0, 300)
    );
  });

  test('ANSI strip pattern present in _handle_failure', function() {
    var resolved = {
      name: 'test-flow',
      description: 'Test',
      steps: [{
        id: 'nav',
        action: 'Navigate to /home',
        type: 'navigate',
        operands: { target: '/home', urlPath: '/home' },
      }],
    };
    var script = generate(resolved, 'test-flow');
    assert.ok(
      script.includes("sed 's/\\x1b\\[[0-9;]*m//g'") || script.includes("sed 's/\\x1b"),
      'Expected ANSI strip sed pattern in compiled output. Got fn snippet: ' +
        script.slice(script.indexOf('_handle_failure()'), script.indexOf('_handle_failure()') + 300)
    );
    assert.ok(
      script.includes('_json_escape()') && script.includes('_xml_attr_escape()'),
      'Expected format-specific control-character encoders in compiled output.'
    );
  });

});
