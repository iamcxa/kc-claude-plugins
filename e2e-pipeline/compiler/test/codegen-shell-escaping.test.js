'use strict';

/**
 * codegen-shell-escaping.test.js — issue #190.
 *
 * Every expansion-active emission context in codegen.js that carries a flow- or
 * mapping-sourced string must land in the compiled script as literal data.
 *
 * The pre-mortem for this class is a test that reads the emitted bytes and calls
 * an escape "present" without ever running it, so every case here executes the
 * emitted bash under a real shell and asserts a canary file was never created.
 */

const { describe, test } = require('node:test');
const assert = require('node:assert/strict');
const childProcess = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const {
  generate,
  generateHeader,
  generateVariables,
  generateFooter,
  generateJUnitEmitter,
  generateRuntimeSupport,
} = require('../codegen.js');

const RUNTIME_BASH = fs.existsSync('/bin/bash') ? '/bin/bash' : 'bash';

// First line of the runtime-support block — the boundary between the variable
// prologue and the rest of the script. Derived, not hardcoded, so a reworded
// banner cannot silently turn these tests into no-ops.
const RUNTIME_SUPPORT_MARKER = generateRuntimeSupport(false, false).split('\n')[0];

function withScratch(callback) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e190-'));
  try {
    return callback(dir, path.join(dir, 'canary'));
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
}

function runBash(script, dir) {
  const scriptPath = path.join(dir, 'prologue.sh');
  fs.writeFileSync(scriptPath, script, 'utf8');
  return childProcess.spawnSync(RUNTIME_BASH, [scriptPath], {
    encoding: 'utf8',
    cwd: dir,
  });
}

/** Slice the generated script down to header + flags + variable declarations. */
function prologueOf(script) {
  const idx = script.indexOf('\n' + RUNTIME_SUPPORT_MARKER + '\n');
  assert.ok(idx > 0, 'runtime-support marker not found — prologue slice is stale');
  return script.slice(0, idx);
}

function makeResolved(variables) {
  return { name: 'flow', variables: variables, steps: [] };
}

describe('#190 — variable prologue is inert against flow/mapping-sourced metacharacters', function() {
  // AC-1: byte shape of the BASE_URL default (codegen.js generateVariables).
  test('mapping base_url with $(...) is emitted backslash-escaped, not raw', function() {
    const block = generateVariables(
      { base_url: 'http://localhost:3000/$(id -u)' },
      'demo'
    );
    const assignment = block.split('\n').filter(function(line) {
      return line.indexOf('BASE_URL="') === 0;
    })[0];
    assert.equal(
      assignment,
      'BASE_URL="${1:-${E2E_BASE_URL:-http://localhost:3000/\\$(id -u)}}"'
    );
    assert.ok(
      block.indexOf('${E2E_BASE_URL:-http://localhost:3000/$(id -u)}') === -1,
      'raw unescaped $(id -u) still present in the emitted default'
    );
  });

  // AC-2: the end-value AC. Execute, do not read.
  test('executing the prologue leaves the canary absent and BASE_URL literal', function() {
    withScratch(function(dir, canary) {
      const baseUrl = 'http://localhost:3000/$(touch ' + canary + ')/`touch ' +
        canary + '`/${HOME}';
      const script = generate(makeResolved({ base_url: baseUrl }), 'demo', null);
      const result = runBash(
        prologueOf(script) + '\nprintf \'%s\' "$BASE_URL" > ' +
          JSON.stringify(path.join(dir, 'value.txt')) + '\n',
        dir
      );

      assert.equal(result.status, 0, 'prologue exited non-zero: ' + result.stderr);
      assert.equal(fs.existsSync(canary), false, 'command substitution ran in the base_url default');
      assert.equal(fs.readFileSync(path.join(dir, 'value.txt'), 'utf8'), baseUrl);
    });
  });

  test('a $(...) in the ${N:?usage} word of a required variable does not run', function() {
    withScratch(function(dir, canary) {
      const flowName = 'demo$(touch ' + canary + ')`touch ' + canary + '`';
      const script = generate(makeResolved({ token: null }), flowName, null);
      const result = runBash(prologueOf(script) + '\necho UNREACHABLE\n', dir);

      assert.equal(fs.existsSync(canary), false, 'command substitution ran in the :? usage word');
      assert.ok(
        result.stderr.indexOf(flowName + '.sh <token>') !== -1,
        'usage message did not carry the literal flow name; stderr was: ' + result.stderr
      );
    });
  });

  test('a newline in a flow name cannot terminate the # Usage comment', function() {
    withScratch(function(dir, canary) {
      const flowName = 'demo\ntouch ' + canary + '\n#';
      const script = generate(makeResolved({ base_url: 'http://h' }), flowName, null);
      const result = runBash(prologueOf(script) + '\necho OK\n', dir);

      assert.equal(fs.existsSync(canary), false, 'the flow name broke out of the # Usage comment');
      assert.equal(result.status, 0, 'prologue exited non-zero: ' + result.stderr);
    });
  });

  test('a newline in a variable default cannot terminate the # Parameters comment', function() {
    withScratch(function(dir, canary) {
      const baseUrl = 'http://h\ntouch ' + canary + '\n#';
      const script = generate(makeResolved({ base_url: baseUrl }), 'demo', null);
      const result = runBash(prologueOf(script) + '\necho OK\n', dir);

      assert.equal(fs.existsSync(canary), false, 'the default value broke out of the # comment');
      assert.equal(result.status, 0, 'prologue exited non-zero: ' + result.stderr);
    });
  });

  test('a newline in provenance metadata cannot terminate a header comment', function() {
    withScratch(function(dir, canary) {
      const header = generateHeader({
        flowName: 'demo\ntouch ' + canary + '.flow\n#',
        flowPath: '/flows/demo.yaml',
        mappingPath: '/mappings/app\ntouch ' + canary + '.map\n#.yaml',
        timestamp: '2026-01-01T00:00:00Z',
        hash: 'deadbeef',
      });
      const result = runBash(header + '\necho OK\n', dir);

      assert.equal(fs.existsSync(canary + '.flow'), false, 'flowName broke out of the header comment');
      assert.equal(fs.existsSync(canary + '.map'), false, 'mappingPath broke out of the header comment');
      assert.equal(result.status, 0, 'header exited non-zero: ' + result.stderr);
    });
  });

  // The JUnit printf format strings are hand-written single-quoted bash literals.
  // xmlAttrEscape() does not escape an apostrophe, so the flow name can close the
  // literal — "looks single-quoted" is not the same as inert.
  test('an apostrophe in the flow name cannot break out of the JUnit printf literal', function() {
    withScratch(function(dir, canary) {
      const flowName = "a'; touch " + canary + "; : '";
      const harness = [
        'set -uo pipefail',
        '_STEP_NAMES=()',
        '_STEP_XML_NAMES=()',
        '_STEP_RESULTS=()',
        '_STEP_FAILURES=()',
        '_STEP_TIMES=()',
        '_FLOW_START=0',
        '_xml_attr_escape() { printf \'%s\' "$1"; }',
        generateJUnitEmitter(flowName),
        '_emit_junit ' + JSON.stringify(path.join(dir, 'out.xml')),
      ].join('\n');
      const result = runBash(harness + '\n', dir);

      assert.equal(fs.existsSync(canary), false, 'the flow name closed the printf single-quoted literal');
      assert.equal(result.status, 0, 'JUnit emitter exited non-zero: ' + result.stderr);
      const xml = fs.readFileSync(path.join(dir, 'out.xml'), 'utf8');
      assert.ok(
        xml.indexOf('<testsuite name="' + flowName + '"') !== -1,
        'testsuite name attribute did not carry the literal flow name; got: ' + xml
      );
    });
  });

  test('the PASS summary footer prints the flow name literally', function() {
    withScratch(function(dir, canary) {
      const flowName = 'demo$(touch ' + canary + ')`touch ' + canary + '`';
      const stubs = [
        'set -uo pipefail',
        '_FAILED_STEPS=()',
        '_HAD_RETRIES=false',
        'METRICS_OUTPUT=""',
        'JUNIT_OUTPUT=""',
        '_count_step_results() { echo 0; }',
      ].join('\n');
      const result = runBash(stubs + '\n' + generateFooter(flowName, 2, 0, false) + '\n', dir);

      assert.equal(fs.existsSync(canary), false, 'command substitution ran in the footer summary');
      assert.equal(result.status, 0, 'footer exited non-zero: ' + result.stderr);
      assert.equal(result.stdout, 'PASS: ' + flowName + ' (2/2 steps, 0 skipped)\n');
    });
  });
});

describe('#190 — step ids reaching echo and _record_step_name stay literal', function() {
  function compileStepIdFlow(stepId) {
    const resolved = {
      name: 'flow',
      variables: { base_url: 'http://h' },
      steps: [{
        id: stepId,
        action: 'Navigate to /home',
        type: 'navigate',
        operands: { target: '/home', urlPath: '/home' },
      }],
    };
    return generate(resolved, 'demo', null);
  }

  test('the emitted echo and _record_step_name lines execute without substitution', function() {
    withScratch(function(dir, canary) {
      const stepId = 'open$(touch ' + canary + ')`touch ' + canary + '`-home';
      const script = compileStepIdFlow(stepId);

      const echoLine = script.split('\n').filter(function(line) {
        return line.indexOf('echo "[1/1] ') === 0;
      })[0];
      const recordLine = script.split('\n').filter(function(line) {
        return line.trim().indexOf('_record_step_name ') === 0;
      })[0];
      // Arrangement checks: green in both worlds, they prove the case found the
      // lines it claims to exercise rather than silently testing nothing.
      assert.ok(echoLine, 'no step progress echo line found in the generated script');
      assert.ok(recordLine, 'no _record_step_name line found in the generated script');

      const harness = [
        'set -uo pipefail',
        '_STEP_NAMES=()',
        '_STEP_JSON_NAMES=()',
        '_STEP_XML_NAMES=()',
        '_record_step_name() { printf \'%s\' "$1" > ' +
          JSON.stringify(path.join(dir, 'recorded.txt')) + '; }',
        echoLine,
        recordLine.trim(),
      ].join('\n');
      const result = runBash(harness + '\n', dir);

      assert.equal(fs.existsSync(canary), false, 'command substitution ran from the step id');
      assert.equal(result.status, 0, 'step id harness exited non-zero: ' + result.stderr);
      assert.equal(result.stdout, '[1/1] ' + stepId + ': Navigate to /home\n');
      assert.equal(fs.readFileSync(path.join(dir, 'recorded.txt'), 'utf8'), stepId);
    });
  });
});
