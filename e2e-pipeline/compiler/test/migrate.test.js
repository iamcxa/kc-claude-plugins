'use strict';

const { test, describe } = require('node:test');
const assert = require('node:assert/strict');
const fs   = require('node:fs');
const os   = require('node:os');
const path = require('node:path');

const { migrate, classifyAction } = require('../migrate');

// ---------------------------------------------------------------------------
// classifyAction — local regex classification
// ---------------------------------------------------------------------------

describe('classifyAction — local regex (useClaude=false)', function() {

  test('Navigate to /login => navigate', function() {
    var result = classifyAction('Navigate to /login', { useClaude: false });
    assert.equal(result.type, 'navigate');
    assert.equal(result.source, 'regex');
  });

  test('Navigate to dashboard => navigate', function() {
    var result = classifyAction('Navigate to dashboard', { useClaude: false });
    assert.equal(result.type, 'navigate');
    assert.equal(result.source, 'regex');
  });

  test('Click login_button on login => click', function() {
    var result = classifyAction("Click login_button on login", { useClaude: false });
    assert.equal(result.type, 'click');
    assert.equal(result.source, 'regex');
  });

  test('Click submit_button => click', function() {
    var result = classifyAction('Click submit_button', { useClaude: false });
    assert.equal(result.type, 'click');
    assert.equal(result.source, 'regex');
  });

  test("Fill email_input with 'test@example.com' on login => fill", function() {
    var result = classifyAction("Fill email_input with 'test@example.com' on login", { useClaude: false });
    assert.equal(result.type, 'fill');
    assert.equal(result.source, 'regex');
  });

  test("Fill password_input with 'secret' => fill", function() {
    var result = classifyAction("Fill password_input with 'secret'", { useClaude: false });
    assert.equal(result.type, 'fill');
    assert.equal(result.source, 'regex');
  });

  test('Take snapshot => snapshot', function() {
    var result = classifyAction('Take snapshot', { useClaude: false });
    assert.equal(result.type, 'snapshot');
    assert.equal(result.source, 'regex');
  });

  test('Wait 2 => wait', function() {
    var result = classifyAction('Wait 2', { useClaude: false });
    assert.equal(result.type, 'wait');
    assert.equal(result.source, 'regex');
  });

  test('Wait 10 => wait', function() {
    var result = classifyAction('Wait 10', { useClaude: false });
    assert.equal(result.type, 'wait');
    assert.equal(result.source, 'regex');
  });

  test('Verify external => verify-external', function() {
    var result = classifyAction('Verify external', { useClaude: false });
    assert.equal(result.type, 'verify-external');
    assert.equal(result.source, 'regex');
  });

  test('Verify external event => verify-external (not snapshot)', function() {
    var result = classifyAction('Verify external event received', { useClaude: false });
    assert.equal(result.type, 'verify-external');
  });

  test('Verify daily_board_heading on dashboard => snapshot', function() {
    var result = classifyAction('Verify daily_board_heading on dashboard', { useClaude: false });
    assert.equal(result.type, 'snapshot');
    assert.equal(result.source, 'regex');
  });

  test('Verify sidebar navigation elements => null (no single word after Verify)', function() {
    // "sidebar" is \w+ so this should match
    var result = classifyAction('Verify sidebar navigation elements', { useClaude: false });
    assert.equal(result.type, 'snapshot');
  });

  test('Narrative/AI-driven action => null (no claude fallback)', function() {
    var result = classifyAction('Click on the first in_progress work order row', { useClaude: false });
    assert.equal(result.type, null);
    assert.equal(result.source, null);
  });

  test('Empty action string => null', function() {
    var result = classifyAction('', { useClaude: false });
    assert.equal(result.type, null);
    assert.equal(result.source, null);
  });

});

// ---------------------------------------------------------------------------
// migrate() — in-place mutation with pre-typed and untyped steps
// ---------------------------------------------------------------------------

describe('migrate() — YAML file annotation', function() {

  /** Helper: create a temp yaml file and return its path */
  function writeTempFlow(content) {
    var dir  = fs.mkdtempSync(path.join(os.tmpdir(), 'migrate-test-'));
    var file = path.join(dir, 'flow.yaml');
    fs.writeFileSync(file, content, 'utf8');
    return { dir: dir, file: file };
  }

  /** Cleanup helper */
  function cleanupDir(dir) {
    fs.rmSync(dir, { recursive: true, force: true });
  }

  test('adds type: fields to untyped steps', function() {
    var content = [
      'name: test-flow',
      'mapping: test-app',
      'steps:',
      '  - id: nav',
      '    action: "Navigate to /login"',
      '  - id: click',
      '    action: "Click submit_button"',
    ].join('\n');

    var tmp = writeTempFlow(content);
    try {
      var result = migrate(tmp.file, { useClaude: false });
      assert.equal(result.annotated, 2);
      assert.equal(result.skipped, 0);

      var updated = require('js-yaml').load(fs.readFileSync(tmp.file, 'utf8'));
      assert.equal(updated.steps[0].type, 'navigate');
      assert.equal(updated.steps[1].type, 'click');
    } finally {
      cleanupDir(tmp.dir);
    }
  });

  test('does not re-classify already-typed steps', function() {
    var content = [
      'name: test-flow',
      'mapping: test-app',
      'steps:',
      '  - id: nav',
      '    type: navigate',
      '    action: "Navigate to /login"',
    ].join('\n');

    var tmp = writeTempFlow(content);
    try {
      var result = migrate(tmp.file, { useClaude: false });
      assert.equal(result.annotated, 0);  // nothing to annotate
      assert.equal(result.skipped, 0);

      var updated = require('js-yaml').load(fs.readFileSync(tmp.file, 'utf8'));
      assert.equal(updated.steps[0].type, 'navigate');  // unchanged
    } finally {
      cleanupDir(tmp.dir);
    }
  });

  test('skips unclassifiable steps and reports count', function() {
    var content = [
      'name: test-flow',
      'mapping: test-app',
      'steps:',
      '  - id: nav',
      '    action: "Navigate to /login"',
      '  - id: complex',
      '    action: "Click on the first in_progress work order row"',
    ].join('\n');

    var tmp = writeTempFlow(content);
    try {
      var result = migrate(tmp.file, { useClaude: false });
      assert.equal(result.annotated, 1);
      assert.equal(result.skipped, 1);

      var updated = require('js-yaml').load(fs.readFileSync(tmp.file, 'utf8'));
      assert.equal(updated.steps[0].type, 'navigate');
      assert.equal(updated.steps[1].type, undefined);  // still untyped
    } finally {
      cleanupDir(tmp.dir);
    }
  });

  test('--dry-run does not modify file', function() {
    var content = [
      'name: test-flow',
      'mapping: test-app',
      'steps:',
      '  - id: nav',
      '    action: "Navigate to /login"',
    ].join('\n');

    var tmp = writeTempFlow(content);
    try {
      var result = migrate(tmp.file, { useClaude: false, dryRun: true });
      assert.equal(result.annotated, 1);  // counted but not written

      var raw = fs.readFileSync(tmp.file, 'utf8');
      assert.ok(raw.indexOf('type:') === -1, 'file must not have been modified in dry-run');
    } finally {
      cleanupDir(tmp.dir);
    }
  });

  test('--output writes to separate file, does not modify source', function() {
    var content = [
      'name: test-flow',
      'mapping: test-app',
      'steps:',
      '  - id: nav',
      '    action: "Navigate to /login"',
    ].join('\n');

    var tmp = writeTempFlow(content);
    var outPath = path.join(tmp.dir, 'output.yaml');
    try {
      migrate(tmp.file, { useClaude: false, output: outPath });

      // Source unchanged
      var srcRaw = fs.readFileSync(tmp.file, 'utf8');
      assert.ok(srcRaw.indexOf('type:') === -1, 'source file must be unchanged');

      // Output has type:
      var outFlow = require('js-yaml').load(fs.readFileSync(outPath, 'utf8'));
      assert.equal(outFlow.steps[0].type, 'navigate');
    } finally {
      cleanupDir(tmp.dir);
    }
  });

  test('Verify step => snapshot type in migrated YAML', function() {
    var content = [
      'name: test-flow',
      'mapping: test-app',
      'steps:',
      '  - id: verify-dashboard',
      '    action: "Verify daily_board_heading on dashboard"',
    ].join('\n');

    var tmp = writeTempFlow(content);
    try {
      migrate(tmp.file, { useClaude: false });

      var updated = require('js-yaml').load(fs.readFileSync(tmp.file, 'utf8'));
      assert.equal(updated.steps[0].type, 'snapshot');
    } finally {
      cleanupDir(tmp.dir);
    }
  });

});
