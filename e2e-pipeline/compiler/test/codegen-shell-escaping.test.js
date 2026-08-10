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
  generateCleanupTrap,
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

/**
 * Metacharacter axes that a `${...}` word re-activates.
 *
 * A `${VAR:-word}` / `${VAR:?word}` word is NOT an ordinary double-quoted
 * string: it re-enables quote processing (`'`), it ends at the first unquoted
 * `}`, and it still performs process substitution (`<(...)`, `>(...)`). So a
 * character-by-character escaper aimed at double-quoted text is the wrong tool
 * for it — the fix is to nest the payload in its own double quotes so the word
 * is parsed as a quoted string, not as expansion grammar.
 *
 * `seed(canary)` returns a payload whose only correct behaviour is to survive
 * verbatim with no side effect.
 */
const METACHAR_AXES = [
  { label: 'command substitution $(...)', seed: function(c) { return 'a$(touch ' + c + ')b'; } },
  { label: 'backtick substitution', seed: function(c) { return 'a`touch ' + c + '`b'; } },
  { label: 'parameter expansion ${...}', seed: function() { return 'a${HOME}b'; } },
  { label: 'expansion-closing brace }', seed: function(c) { return 'a}; touch ' + c + '; #b'; } },
  { label: 'process substitution <(...)', seed: function(c) { return 'a<(touch ' + c + ')b'; } },
  { label: 'process substitution >(...)', seed: function(c) { return 'a>(touch ' + c + ')b'; } },
  // One apostrophe, not a balanced pair: a `${...}` word re-enables quote
  // processing, so a lone `'` opens a literal that swallows the rest of the file.
  { label: 'apostrophe', seed: function() { return "it's"; } },
  { label: 'double quote and backslash', seed: function() { return 'a"b\\c'; } },
];

describe('#190 — variable prologue is inert against flow/mapping-sourced metacharacters', function() {
  // AC-1: byte shape of the BASE_URL default (codegen.js generateVariables).
  // The payload is nested in its own double quotes: that, not the backslashes,
  // is what makes the word a quoted string rather than expansion grammar.
  test('mapping base_url with $(...) is emitted nested-quoted and backslash-escaped', function() {
    const block = generateVariables(
      { base_url: 'http://localhost:3000/$(id -u)' },
      'demo'
    );
    const assignment = block.split('\n').filter(function(line) {
      return line.indexOf('BASE_URL="') === 0;
    })[0];
    assert.equal(
      assignment,
      'BASE_URL="${1:-${E2E_BASE_URL:-"http://localhost:3000/\\$(id -u)"}}"'
    );
  });

  // AC-2: the end-value AC. Execute, do not read.
  METACHAR_AXES.forEach(function(axis) {
    test('${N:-default} word survives ' + axis.label + ' with no side effect', function() {
      withScratch(function(dir, canary) {
        const baseUrl = 'http://localhost:3000/' + axis.seed(canary);
        const script = generate(makeResolved({ base_url: baseUrl }), 'demo', null);
        const result = runBash(
          prologueOf(script) + '\nprintf \'%s\' "$BASE_URL" > ' +
            JSON.stringify(path.join(dir, 'value.txt')) + '\n',
          dir
        );

        assert.equal(result.status, 0, 'prologue exited non-zero: ' + result.stderr);
        assert.equal(fs.existsSync(canary), false, axis.label + ' executed in the base_url default');
        assert.equal(fs.readFileSync(path.join(dir, 'value.txt'), 'utf8'), baseUrl);
      });
    });
  });

  METACHAR_AXES.forEach(function(axis) {
    test('${N:?usage} word survives ' + axis.label + ' with no side effect', function() {
      withScratch(function(dir, canary) {
        const flowName = 'demo-' + axis.seed(canary);
        const script = generate(makeResolved({ token: null }), flowName, null);
        const result = runBash(prologueOf(script) + '\necho UNREACHABLE\n', dir);

        assert.equal(fs.existsSync(canary), false, axis.label + ' executed in the :? usage word');
        assert.ok(
          result.stderr.indexOf(flowName + '.sh <token>') !== -1,
          'usage message did not carry the literal flow name; stderr was: ' + result.stderr
        );
        assert.equal(result.stdout, '', 'the prologue continued past the required-variable check');
      });
    });
  });

  // The usage word also carries the flow's own variable NAMES, which the parser
  // constrains to shell identifiers — this pins that the nested-quote shape does
  // not corrupt the `<name>` / `[name]` usage parts around them.
  test('${N:?usage} word keeps both required and optional usage parts literal', function() {
    withScratch(function(dir) {
      const script = generate(
        makeResolved({ token: null, base_url: 'http://h' }),
        'demo',
        null
      );
      const result = runBash(prologueOf(script) + '\necho UNREACHABLE\n', dir);

      assert.ok(
        result.stderr.indexOf('demo.sh <token> [base_url]') !== -1,
        'usage parts were not emitted literally; stderr was: ' + result.stderr
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

  // parser.js does NOT charset-validate flow `variables:` KEYS, and the key
  // reaches the "# Usage:" and "# $N ..." lines verbatim, so an embedded newline
  // ends the comment there.
  //
  // Scope: this covers the COMMENT block only. The same unvalidated key is also
  // uppercased into a bash IDENTIFIER (`A\nTOUCH X\n#B="..."`), which no escaper
  // can make safe — that needs parser-side name validation, a behaviour change
  // for existing flows, and is reported as a follow-up rather than fixed here.
  // The slice length is derived from the ESCAPED structure (1 usage line +
  // "# Parameters:" + 1 line per variable), so in the unescaped world the
  // payload falls inside the window instead of being filtered out of it.
  test('a newline in a variable name cannot terminate the # Usage comment', function() {
    withScratch(function(dir, canary) {
      const variables = {};
      variables['a\ntouch ' + canary + '\n#b'] = 'http://h';
      const block = generateVariables(variables, 'demo');
      const commentBlock = block.split('\n').slice(0, 3).join('\n');
      const result = runBash('set -uo pipefail\n' + commentBlock + '\necho OK\n', dir);

      assert.equal(fs.existsSync(canary), false,
        'the variable name broke out of a # comment; emitted block was:\n' + block + '\nstderr: ' + result.stderr);
      assert.equal(result.stdout, 'OK\n', 'comment block was not inert: ' + result.stdout);
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
        flowPath: '/flows/demo\ntouch ' + canary + '.src\n#.yaml',
        mappingPath: '/mappings/app\ntouch ' + canary + '.map\n#.yaml',
        timestamp: '2026-01-01T00:00:00Z',
        hash: 'deadbeef',
      });
      const result = runBash(header + '\necho OK\n', dir);

      assert.equal(fs.existsSync(canary + '.flow'), false, 'flowName broke out of the header comment');
      assert.equal(fs.existsSync(canary + '.src'), false, 'flowPath broke out of the header comment');
      assert.equal(fs.existsSync(canary + '.map'), false, 'mappingPath broke out of the header comment');
      assert.equal(result.status, 0, 'header exited non-zero: ' + result.stderr);
    });
  });

  // The cross-site branch (meta.mappingPaths, an array) is a SEPARATE emission
  // from the singular meta.mappingPath above — compiler.js populates it whenever
  // a flow declares 2+ sites:, each path built from the flow-YAML mappingName.
  test('a newline in any cross-site mapping path cannot terminate a header comment', function() {
    withScratch(function(dir, canary) {
      const header = generateHeader({
        flowName: 'demo',
        flowPath: '/flows/demo.yaml',
        mappingPaths: [
          '/mappings/one\ntouch ' + canary + '.m1\n#.yaml',
          '/mappings/two\ntouch ' + canary + '.m2\n#.yaml',
        ],
        timestamp: '2026-01-01T00:00:00Z',
        hash: 'deadbeef',
      });
      const result = runBash(header + '\necho OK\n', dir);

      assert.equal(fs.existsSync(canary + '.m1'), false, 'mappingPaths[0] broke out of the header comment');
      assert.equal(fs.existsSync(canary + '.m2'), false, 'mappingPaths[1] broke out of the header comment');
      assert.equal(result.status, 0, 'header exited non-zero: ' + result.stderr);
    });
  });

  // The JUnit printf format strings are hand-written single-quoted bash literals
  // AND printf FORMAT operands. Two distinct hazards land there: an apostrophe
  // closes the single-quoted literal, and a `%` conversion specifier shifts the
  // argument list. xmlAttrEscape() neutralises neither.
  //
  // _STEP_* must be POPULATED: `for _i in "${!_STEP_NAMES[@]}"` never iterates on
  // an empty array, so an empty stub leaves all four <testcase> formats — including
  // the one used for every PASSING step — never executed by the test at all.
  function junitHarness(dir, flowName) {
    return [
      'set -uo pipefail',
      // one entry per result class so all four <testcase> printf formats run
      '_STEP_NAMES=(s-pass s-skip s-na s-fail)',
      '_STEP_XML_NAMES=(s-pass s-skip s-na s-fail)',
      '_STEP_RESULTS=(pass skip not_automated fail)',
      '_STEP_FAILURES=("" "" "" boom)',
      '_STEP_TIMES=(1 2 3 4)',
      '_FLOW_START=0',
      '_xml_attr_escape() { printf \'%s\' "$1"; }',
      generateJUnitEmitter(flowName),
      '_emit_junit ' + JSON.stringify(path.join(dir, 'out.xml')),
    ].join('\n');
  }

  function assertFlowNameIntact(xml, flowName) {
    assert.ok(
      xml.indexOf('<testsuite name="' + flowName + '" tests="4" failures="1" skipped="2"') !== -1,
      'testsuite attributes did not carry the literal flow name and true counts; got: ' + xml
    );
    const classnames = xml.split('\n').filter(function(line) {
      return line.indexOf('<testcase ') !== -1;
    });
    assert.equal(classnames.length, 4, 'expected one <testcase> per result class; got: ' + xml);
    classnames.forEach(function(line) {
      assert.ok(
        line.indexOf('<testcase classname="' + flowName + '" name="s-') !== -1,
        'testcase did not carry the literal flow name in classname: ' + line
      );
    });
  }

  test('an apostrophe in the flow name cannot break out of the JUnit printf literal', function() {
    withScratch(function(dir, canary) {
      const flowName = "a'; touch " + canary + "; : '";
      const result = runBash(junitHarness(dir, flowName) + '\n', dir);

      assert.equal(fs.existsSync(canary), false, 'the flow name closed the printf single-quoted literal');
      assert.equal(result.status, 0, 'JUnit emitter exited non-zero: ' + result.stderr);
      assertFlowNameIntact(fs.readFileSync(path.join(dir, 'out.xml'), 'utf8'), flowName);
    });
  });

  test('a % in the flow name cannot shift the JUnit printf argument list', function() {
    withScratch(function(dir) {
      const flowName = 'flow%s%s-X';
      const result = runBash(junitHarness(dir, flowName) + '\n', dir);

      assert.equal(result.status, 0, 'JUnit emitter exited non-zero: ' + result.stderr);
      assertFlowNameIntact(fs.readFileSync(path.join(dir, 'out.xml'), 'utf8'), flowName);
    });
  });

  // generate() is exported, so a caller-supplied step type reaches the
  // "Unknown action type" comment even though resolver.js never produces one.
  test('a newline in an unknown step type cannot terminate its comment', function() {
    withScratch(function(dir, canary) {
      const script = generate({
        name: 'flow',
        variables: { base_url: 'http://h' },
        steps: [{ id: 'x', action: 'do', type: 'weird\ntouch ' + canary + '\n#', operands: {} }],
      }, 'demo', null);
      const all = script.split('\n');
      const at = all.findIndex(function(l) {
        return l.indexOf('# Unknown action type: ') === 0;
      });
      // Arrangement check: green in both worlds, proves the emission was found.
      assert.ok(at > 0, 'no "Unknown action type" comment found in the generated script');
      // The window must extend PAST the comment: an unescaped newline puts the
      // payload on the following lines, so a one-line harness never exercises it.
      // Three lines is exactly the span the two-newline payload above would
      // occupy; the emitted lines that follow are comments and a blank line.
      const window = all.slice(at, at + 3).join('\n');

      const result = runBash('set -uo pipefail\n' + window + '\necho OK\n', dir);
      assert.equal(fs.existsSync(canary), false, 'the step type broke out of its # comment');
      assert.equal(result.stdout, 'OK\n', 'harness output was not the single echo: ' + result.stdout);
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

describe('#190 — flow-sourced text in a printf FORMAT operand stays literal', function() {
  // parser.js validates a finally-step HTTP header name against
  // /^[!#$%&'*+.^_`|~0-9A-Za-z-]+$/ — a pattern that explicitly PERMITS `%`.
  // The name is spliced into a printf format, so `X-%s` relocates the token
  // argument into the header-NAME position and empties the header value.
  test('a % in a finalizer HTTP header name does not consume the token argument', function() {
    withScratch(function(dir) {
      const cleanup = generateCleanupTrap([], [{
        id: 'cleanup-record',
        action: 'Finalize record',
        type: 'http',
        operands: {
          method: 'GET',
          baseEnv: 'API_BASE_URL',
          pathSegments: [],
          headers: {
            'X-%s': { scheme: 'Bearer', runtime_ref: { env: 'TOK', state_key: 'tok' } },
          },
        },
      }]);

      const lines = cleanup.split('\n');
      const i = lines.findIndex(function(line) { return line.indexOf('header = ') !== -1; });
      // Arrangement check: green in both worlds, it proves the case located the
      // emission it claims to exercise instead of running an empty harness.
      assert.ok(i > 0, 'no finalizer header printf emission found in the cleanup trap');
      const statement = (lines[i] + '\n' + lines[i + 1])
        .replace('if ! ', '')
        .replace(/; then$/, '');

      const configPath = path.join(dir, 'curl.cfg');
      const result = runBash([
        'set -uo pipefail',
        '_FINALIZER_HEADER=tok3n',
        '_FINALIZER_CONFIG=' + JSON.stringify(configPath),
        statement,
      ].join('\n') + '\n', dir);

      assert.equal(result.status, 0, 'header printf exited non-zero: ' + result.stderr);
      assert.equal(
        fs.readFileSync(configPath, 'utf8'),
        'header = "X-%s: Bearer tok3n"\n'
      );
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
