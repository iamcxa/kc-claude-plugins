'use strict';

/**
 * selector-lint-drift.test.js — AC-2: the bash linter's verdicts come from the shared
 * table, not from a private copy of it.
 *
 * A test that ran `lint-mapping.sh` and the policy module over the same bytes and
 * compared them would be tautological once the script execs the module — both sides
 * would be one code path and no edit could redden it. This test perturbs instead: it
 * copies the plugin to a scratch directory, deletes one class from `BANNED_CLASSES`
 * there, and asserts the SCRIPT's findings change to match. A linter carrying its own
 * regex for that class keeps reporting it, and this goes red.
 *
 * The claim being enforced is the bounded one — "the linter's verdicts track this
 * table" — not "no second table can exist", which nothing here or anywhere would make
 * true.
 */

const { test, describe, before, after } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { execFileSync } = require('node:child_process');

const PLUGIN_ROOT = path.join(__dirname, '..', '..');
const LINTER = path.join(PLUGIN_ROOT, 'scripts', 'lint-mapping.sh');

// A fixture carrying two distinct banned classes, so removing one from the table
// leaves the other reporting — which distinguishes "the table drove the change" from
// "the linter broke entirely".
const FIXTURE = [
  'version: 2',
  'pages:',
  '  home:',
  '    elements:',
  '      third_button:',
  "        selector: '.MuiButton-root >> nth=2'",
  '      dialog_heading:',
  '        selector: \'.MuiDialog :has-text("Confirm")\'',
  '',
].join('\n');

/** Run the linter, returning {status, stderr}. Exit 2 is the expected banned-token code. */
function runLinter(linterPath, mappingPath) {
  try {
    const stdout = execFileSync('bash', [linterPath, mappingPath], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] });
    return { status: 0, stdout: stdout, stderr: '' };
  } catch (err) {
    return { status: err.status, stdout: String(err.stdout || ''), stderr: String(err.stderr || '') };
  }
}

describe('lint-mapping.sh verdicts track BANNED_CLASSES (AC-2)', function () {
  let scratch;
  let mappingPath;

  before(function () {
    scratch = fs.mkdtempSync(path.join(os.tmpdir(), 'selector-drift-'));
    mappingPath = path.join(scratch, 'mapping.yaml');
    fs.writeFileSync(mappingPath, FIXTURE, 'utf8');
  });

  after(function () {
    fs.rmSync(scratch, { recursive: true, force: true });
  });

  test('unperturbed: both classes are reported and the exit code is 2', function () {
    const res = runLinter(LINTER, mappingPath);
    assert.equal(res.status, 2);
    assert.match(res.stderr, />>nth/);
    assert.match(res.stderr, /has-text/);
  });

  test('perturbing the table changes what the script reports', function () {
    // Scratch copy of the two files the linter needs: the script and the module.
    const copyRoot = path.join(scratch, 'plugin');
    fs.mkdirSync(path.join(copyRoot, 'scripts'), { recursive: true });
    fs.mkdirSync(path.join(copyRoot, 'compiler', 'lib'), { recursive: true });
    fs.copyFileSync(LINTER, path.join(copyRoot, 'scripts', 'lint-mapping.sh'));
    fs.chmodSync(path.join(copyRoot, 'scripts', 'lint-mapping.sh'), 0o755);

    const moduleSrc = fs.readFileSync(
      path.join(PLUGIN_ROOT, 'compiler', 'lib', 'selector-policy.js'),
      'utf8'
    );
    // Delete the has-text entry from the table in the copy. Anchored on the id line so
    // an unrelated edit to the module does not silently turn this into a no-op.
    const perturbed = moduleSrc.replace(
      /\{\s*\n\s*id: 'has-text',[\s\S]*?\n\s*\},\n/,
      ''
    );
    assert.notEqual(perturbed, moduleSrc, 'perturbation matched nothing — the test would prove nothing');
    fs.writeFileSync(path.join(copyRoot, 'compiler', 'lib', 'selector-policy.js'), perturbed, 'utf8');

    const res = runLinter(path.join(copyRoot, 'scripts', 'lint-mapping.sh'), mappingPath);

    // Still fails, on the class that is still in the table...
    assert.equal(res.status, 2);
    assert.match(res.stderr, />>nth/);
    // ...and no longer reports the one removed from it. A private regex in the script
    // would keep reporting it, and this assertion is what catches that.
    assert.doesNotMatch(res.stderr, /has-text/);
  });
});
