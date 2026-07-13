'use strict';

/**
 * runtime-state-finalizer.test.js — SC-1032 T1 vertical seam tests
 *
 * Covers:
 *   1. Parser validates runtime_values (required env, not positional)
 *   2. Parser validates capture-url-query steps (param, as, validate: uuid)
 *   3. Parser validates finally block with http steps
 *   4. Resolver produces runtime_ref operands on sensitive fill steps (not literal value in operands)
 *   5. Resolver produces capture-url-query operands (param, as, validate)
 *   6. Resolver produces finally steps with http operands
 *   7. Codegen: sensitive fill reads from stdin (read -s), never emits value literal or argv
 *   8. Codegen: capture-url-query exact-one UUID emits URL extraction + UUID validation
 *   9. Codegen: finally block runs inside trap EXIT — single authoritative EXIT controller
 *  10. Codegen: no secret literal in generated script (BOOKING_PASSWORD, ADMIN_TOKEN values not in output)
 *  11. Integration (compile): success path — BOOKING_ID captured, finalizer runs, exits 0
 *  12. Integration (compile): deliberate post-capture failure — finalizer still runs with same UUID, finalizer failure controls exit (exit != 0)
 */

const { test, describe } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const childProcess = require('node:child_process');

// Units under test
const { parse } = require('../parser.js');
const { resolve } = require('../resolver.js');
const {
  generate,
  generateRuntimeSupport,
  generateRuntimeValuesBlock,
} = require('../codegen.js');
const { compile } = require('../compiler.js');

const FIXTURES_DIR = path.join(__dirname, 'fixtures');
const FLOW_PATH = path.join(FIXTURES_DIR, 'runtime-state-finalizer-flow.yaml');
const MAPPING_DIR = FIXTURES_DIR;

const RUNTIME_BASH = fs.existsSync('/bin/bash') ? '/bin/bash' : 'bash';
const RUNNER_WATCHDOG_SOURCE = [
  "'use strict';",
  "const { spawn } = require('node:child_process');",
  'const timeoutMs = Number(process.argv[1]);',
  'const command = process.argv[2];',
  'const args = process.argv.slice(3);',
  'const child = spawn(command, args, {',
  '  detached: true,',
  "  stdio: ['pipe', 'inherit', 'inherit'],",
  '  env: process.env,',
  '});',
  'let childCode = null;',
  'let childSignal = null;',
  'let timedOut = false;',
  'function killGroup(signal) {',
  "  if (!child.pid) return;",
  '  try { process.kill(-child.pid, signal); } catch (error) {',
  "    if (error.code !== 'ESRCH') throw error;",
  '  }',
  '}',
  'const timeout = setTimeout(function() {',
  '  timedOut = true;',
  "  process.stderr.write('[test watchdog] generated runner timed out after ' + timeoutMs + 'ms\\n');",
  "  killGroup('SIGKILL');",
  '}, timeoutMs);',
  "['SIGTERM', 'SIGINT', 'SIGHUP'].forEach(function(signal) {",
  '  process.on(signal, function() {',
  '    timedOut = true;',
  "    killGroup('SIGKILL');",
  '    process.exit(124);',
  '  });',
  '});',
  "child.on('error', function(error) {",
  "  process.stderr.write('[test watchdog] failed to start runner: ' + error.message + '\\n');",
  '  childCode = 127;',
  '});',
  "child.on('exit', function(code, signal) {",
  '  childCode = code;',
  '  childSignal = signal;',
  "  if (!timedOut) killGroup('SIGKILL');",
  '});',
  "child.on('close', function() {",
  '  clearTimeout(timeout);',
  '  if (timedOut) {',
  '    process.exitCode = 124;',
  "  } else if (typeof childCode === 'number') {",
  '    process.exitCode = childCode;',
  '  } else {',
  "    process.stderr.write('[test watchdog] runner exited from signal ' + childSignal + '\\n');",
  '    process.exitCode = 1;',
  '  }',
  '});',
  'process.stdin.pipe(child.stdin);',
].join('\n');

function makeTmpDir() {
  return fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-sc1032-'));
}

function writeExecutable(filePath, contents) {
  fs.writeFileSync(filePath, contents, 'utf8');
  fs.chmodSync(filePath, 0o755);
}

function writeAgentBrowserStub(filePath, uuid, snapshotExit) {
  writeExecutable(filePath, [
    '#!/usr/bin/env bash',
    'if [ "$*" = "eval --stdin" ]; then',
    '  _program=$(cat)',
    '  case "$_program" in',
    '    *"searchParams.getAll"*) printf \'%s\\n\' ' + JSON.stringify('__E2E_CAPTURE__' + uuid) + ' ;;',
    '    *) exit 0 ;;',
    '  esac',
    '  exit 0',
    'fi',
    'case "$*" in',
    '  *"open "*|*"click "*|*"close"*) exit 0 ;;',
    '  *"snapshot"*) ' + (snapshotExit ? 'exit 1' : 'echo "- button Confirm Booking"') + ' ;;',
    '  *) exit 0 ;;',
    'esac',
  ].join('\n'));
}

function writeCurlStub(filePath, logPath) {
  writeExecutable(filePath, [
    '#!/usr/bin/env bash',
    logPath ? 'printf \'%s\\n\' "$*" >> ' + singleShellLiteral(logPath) : ':',
    '_out=""',
    'while [ "$#" -gt 0 ]; do',
    '  if [ "$1" = "-o" ]; then _out="$2"; shift 2; else shift; fi',
    'done',
    '[ -z "$_out" ] || printf \'%s\\n\' \'{"data":{"status":"cancelled"}}\' > "$_out"',
    'printf \'200\'',
  ].join('\n'));
}

function parseInlineFlow(flow) {
  const yaml = require('js-yaml');
  const tmpFlow = path.join(makeTmpDir(), 'flow.yaml');
  fs.writeFileSync(tmpFlow, yaml.dump(flow));
  const result = parse(tmpFlow, MAPPING_DIR);
  fs.rmSync(path.dirname(tmpFlow), { recursive: true, force: true });
  return result;
}

// ---------------------------------------------------------------------------
// Bash execution helper
// ---------------------------------------------------------------------------

function runScript(scriptPath, opts) {
  opts = opts || {};
  const env = Object.assign({}, process.env, opts.env || {});
  if (opts.binDir) {
    env.PATH = opts.binDir + path.delimiter + (env.PATH || '');
  }
  const timeout = opts.timeout || 15000;
  return childProcess.spawnSync(process.execPath, [
    '-e', RUNNER_WATCHDOG_SOURCE, String(timeout), RUNTIME_BASH, scriptPath,
  ].concat(opts.args || []), {
    encoding: 'utf8',
    env: env,
    input: opts.stdin || '',
    timeout: timeout + 5000,
  });
}

// ---------------------------------------------------------------------------
// describe: SC-1032 vertical seam
// ---------------------------------------------------------------------------

describe('SC-1032 vertical seam', function () {

  // -------------------------------------------------------------------------
  // 1. Parser: runtime_values validation
  // -------------------------------------------------------------------------
  describe('parser — runtime_values', function () {
    test('parse() accepts flow with runtime_values block', function () {
      const result = parse(FLOW_PATH, MAPPING_DIR);
      assert.equal(result.errors.length, 0,
        'Expected no parse errors. Got: ' + result.errors.join('; '));
    });

    test('parse() exposes runtime_values on flow object', function () {
      const result = parse(FLOW_PATH, MAPPING_DIR);
      assert.ok(result.flow.runtime_values,
        'Expected flow.runtime_values to be present');
      assert.ok(Object.prototype.hasOwnProperty.call(result.flow.runtime_values, 'booking_password'));
      assert.ok(Object.prototype.hasOwnProperty.call(result.flow.runtime_values, 'admin_token'));
    });

    test('parse() rejects runtime_values that is not an object', function () {
      // Build minimal inline YAML with bad runtime_values
      const yaml = require('js-yaml');
      const badFlow = yaml.dump({
        name: 'bad-flow',
        mapping: 'runtime-state-finalizer-mapping',
        runtime_values: 'a string',
        steps: [{ id: 'step1', type: 'snapshot', action: 'Take snapshot' }],
      });
      const tmpFlow = path.join(os.tmpdir(), 'bad-rv-flow.yaml');
      fs.writeFileSync(tmpFlow, badFlow);
      const result = parse(tmpFlow, MAPPING_DIR);
      assert.ok(result.errors.some(function (e) {
        return e.toLowerCase().includes('runtime_values');
      }), 'Expected error about runtime_values. Got: ' + result.errors.join('; '));
      fs.unlinkSync(tmpFlow);
    });

    test('parse() rejects runtime_values entries that are not typed objects', function () {
      const yaml = require('js-yaml');
      const badFlow = yaml.dump({
        name: 'bad-rv2',
        mapping: 'runtime-state-finalizer-mapping',
        runtime_values: { my_secret: 12345 },
        steps: [{ id: 'step1', type: 'snapshot', action: 'Take snapshot' }],
      });
      const tmpFlow = path.join(os.tmpdir(), 'bad-rv2-flow.yaml');
      fs.writeFileSync(tmpFlow, badFlow);
      const result = parse(tmpFlow, MAPPING_DIR);
      assert.ok(result.errors.some(function (e) {
        return e.toLowerCase().includes('runtime_value') || e.toLowerCase().includes('my_secret');
      }), 'Expected error about invalid runtime_value entry. Got: ' + result.errors.join('; '));
      fs.unlinkSync(tmpFlow);
    });
  });

  // -------------------------------------------------------------------------
  // 2. Parser: capture-url-query steps
  // -------------------------------------------------------------------------
  describe('parser — capture-url-query step', function () {
    test('parse() accepts capture-url-query step with uuid validate', function () {
      const result = parse(FLOW_PATH, MAPPING_DIR);
      assert.equal(result.errors.length, 0,
        'Expected no parse errors. Got: ' + result.errors.join('; '));
      const step = result.flow.steps.find(function (s) { return s.type === 'capture-url-query'; });
      assert.ok(step, 'Expected a capture-url-query step in flow');
      assert.equal(step.query, 'bookingId');
      assert.equal(step.save_as, 'booking_id');
      assert.equal(step.validate, 'uuid');
    });

    test('parse() rejects capture-url-query step missing query', function () {
      const yaml = require('js-yaml');
      const badFlow = yaml.dump({
        name: 'bad-cap',
        mapping: 'runtime-state-finalizer-mapping',
        steps: [{
          id: 'cap1',
          type: 'capture-url-query',
          action: 'Capture bookingId from url query',
          save_as: 'booking_id', validate: 'uuid',
        }],
      });
      const tmpFlow = path.join(os.tmpdir(), 'bad-cap-flow.yaml');
      fs.writeFileSync(tmpFlow, badFlow);
      const result = parse(tmpFlow, MAPPING_DIR);
      assert.ok(result.errors.some(function (e) {
        return e.toLowerCase().includes('param') || e.toLowerCase().includes('capture');
      }), 'Expected error about missing param. Got: ' + result.errors.join('; '));
      fs.unlinkSync(tmpFlow);
    });

    test('parse() rejects capture-url-query step missing save_as', function () {
      const yaml = require('js-yaml');
      const badFlow = yaml.dump({
        name: 'bad-cap2',
        mapping: 'runtime-state-finalizer-mapping',
        steps: [{
          id: 'cap2',
          type: 'capture-url-query',
          action: 'Capture bookingId from url query',
          query: 'bookingId', validate: 'uuid',
        }],
      });
      const tmpFlow = path.join(os.tmpdir(), 'bad-cap2-flow.yaml');
      fs.writeFileSync(tmpFlow, badFlow);
      const result = parse(tmpFlow, MAPPING_DIR);
      assert.ok(result.errors.some(function (e) {
        return e.toLowerCase().includes('as') || e.toLowerCase().includes('capture');
      }), 'Expected error about missing as. Got: ' + result.errors.join('; '));
      fs.unlinkSync(tmpFlow);
    });

    test('parse() rejects capture-url-query with unknown validate type', function () {
      const yaml = require('js-yaml');
      const badFlow = yaml.dump({
        name: 'bad-cap3',
        mapping: 'runtime-state-finalizer-mapping',
        steps: [{
          id: 'cap3',
          type: 'capture-url-query',
          action: 'Capture bookingId from url query',
          query: 'bookingId', save_as: 'booking_id', validate: 'isbn',
        }],
      });
      const tmpFlow = path.join(os.tmpdir(), 'bad-cap3-flow.yaml');
      fs.writeFileSync(tmpFlow, badFlow);
      const result = parse(tmpFlow, MAPPING_DIR);
      assert.ok(result.errors.some(function (e) {
        return e.toLowerCase().includes('validate') || e.toLowerCase().includes('isbn');
      }), 'Expected error about unknown validate type. Got: ' + result.errors.join('; '));
      fs.unlinkSync(tmpFlow);
    });
  });

  // -------------------------------------------------------------------------
  // 3. Parser: finally block
  // -------------------------------------------------------------------------
  describe('parser — finally block', function () {
    test('parse() accepts flow with finally block', function () {
      const result = parse(FLOW_PATH, MAPPING_DIR);
      assert.ok(result.flow.finally, 'Expected flow.finally to be present');
      assert.ok(Array.isArray(result.flow.finally), 'Expected flow.finally to be an array');
      assert.equal(result.flow.finally.length, 2);
    });

    test('parse() rejects finally step of type http missing http.url', function () {
      const yaml = require('js-yaml');
      const badFlow = yaml.dump({
        name: 'bad-fin',
        mapping: 'runtime-state-finalizer-mapping',
        steps: [{ id: 'step1', type: 'snapshot', action: 'Take snapshot' }],
        finally: [{
          id: 'fin1',
          type: 'http',
          action: 'POST /api/cancel',
          request: { method: 'POST' }, // missing url
        }],
      });
      const tmpFlow = path.join(os.tmpdir(), 'bad-fin-flow.yaml');
      fs.writeFileSync(tmpFlow, badFlow);
      const result = parse(tmpFlow, MAPPING_DIR);
      assert.ok(result.errors.some(function (e) {
        return e.toLowerCase().includes('url') || e.toLowerCase().includes('http');
      }), 'Expected error about missing http.url. Got: ' + result.errors.join('; '));
      fs.unlinkSync(tmpFlow);
    });

    test('parse() rejects finally step missing request method', function () {
      const yaml = require('js-yaml');
      const badFlow = yaml.dump({
        name: 'bad-fin2',
        mapping: 'runtime-state-finalizer-mapping',
        steps: [{ id: 'step1', type: 'snapshot', action: 'Take snapshot' }],
        finally: [{
          id: 'fin2',
          type: 'http',
          action: 'POST /api/cancel',
          request: { url: { base_from_env: 'E2E_API_BASE_URL', path_segments: ['api'] } },
        }],
      });
      const tmpFlow = path.join(os.tmpdir(), 'bad-fin2-flow.yaml');
      fs.writeFileSync(tmpFlow, badFlow);
      const result = parse(tmpFlow, MAPPING_DIR);
      assert.ok(result.errors.some(function (e) {
        return e.toLowerCase().includes('method');
      }), 'Expected error about request method. Got: ' + result.errors.join('; '));
      fs.unlinkSync(tmpFlow);
    });

    test('parse() accepts the exact one-level body_field contract', function () {
      const result = parse(FLOW_PATH, MAPPING_DIR);
      assert.equal(result.errors.length, 0, result.errors.join('; '));
      assert.deepEqual(result.flow.finally[1].expect.body_field, {
        object: 'data', field: 'status', equals_literal: 'cancelled',
      });
    });

    test('parse() rejects incomplete or wrongly typed body_field contracts', function () {
      const invalidContracts = [
        { field: 'status', equals_literal: 'cancelled' },
        { object: 42, field: 'status', equals_literal: 'cancelled' },
        { object: 'data', equals_literal: 'cancelled' },
        { object: 'data', field: false, equals_literal: 'cancelled' },
        { object: 'data', field: 'status' },
        { object: 'data', field: 'status', equals_literal: { value: 'cancelled' } },
      ];
      for (const bodyField of invalidContracts) {
        const flow = require('js-yaml').load(fs.readFileSync(FLOW_PATH, 'utf8'));
        flow.finally[1].expect.body_field = bodyField;
        const result = parseInlineFlow(flow);
        assert.ok(result.errors.some(function (error) {
          return error.includes('body_field');
        }), 'Expected body_field validation error for ' + JSON.stringify(bodyField) +
          '; got: ' + JSON.stringify(result.errors));
      }
    });
  });

  // -------------------------------------------------------------------------
  // 4. Resolver: runtime_ref on sensitive fill
  // -------------------------------------------------------------------------
  describe('resolver — runtime_ref operands', function () {
    var parsed;
    var resolved;

    test('resolve() succeeds for runtime-state-finalizer flow', function () {
      parsed = parse(FLOW_PATH, MAPPING_DIR);
      assert.equal(parsed.errors.length, 0,
        'Expected no parse errors. Got: ' + parsed.errors.join('; '));
      resolved = resolve(parsed.flow, parsed.mapping, { runtimeValues: parsed.flow.runtime_values });
      assert.equal(resolved.errors.length, 0,
        'Expected no resolve errors. Got: ' + resolved.errors.join('; '));
    });

    test('resolve() tags fill step with runtime_ref operand (no literal value in operands)', function () {
      parsed = parsed || parse(FLOW_PATH, MAPPING_DIR);
      resolved = resolve(parsed.flow, parsed.mapping, { runtimeValues: parsed.flow.runtime_values });

      const fillStep = resolved.resolved.steps.find(function (s) {
        return s.id === 'fill-password';
      });
      assert.ok(fillStep, 'Expected fill-password step in resolved steps');
      assert.equal(fillStep.type, 'fill');
      // Must have runtime_ref set, value must NOT be a literal string containing the secret name
      assert.ok(fillStep.operands.runtime_ref, 'Expected runtime_ref in fill operands');
      assert.equal(fillStep.operands.runtime_ref, 'booking_password');
      // Value field must not be the runtime_ref string "BOOKING_PASSWORD" embedded as a literal
      assert.ok(!fillStep.operands.value ||
        fillStep.operands.value !== 'runtime_ref:booking_password',
        'Fill operands.value should not be the raw runtime_ref: string');
    });

    test('resolve() produces capture-url-query step with capture operands', function () {
      parsed = parsed || parse(FLOW_PATH, MAPPING_DIR);
      resolved = resolve(parsed.flow, parsed.mapping, { runtimeValues: parsed.flow.runtime_values });

      const capStep = resolved.resolved.steps.find(function (s) {
        return s.type === 'capture-url-query';
      });
      assert.ok(capStep, 'Expected capture-url-query step in resolved steps');
      assert.equal(capStep.operands.param, 'bookingId');
      assert.equal(capStep.operands.as, 'BOOKING_ID');
      assert.equal(capStep.operands.validate, 'uuid');
    });

    test('resolve() includes finally steps in resolved output', function () {
      parsed = parsed || parse(FLOW_PATH, MAPPING_DIR);
      resolved = resolve(parsed.flow, parsed.mapping, { runtimeValues: parsed.flow.runtime_values });

      assert.ok(resolved.resolved.finally, 'Expected finally in resolved output');
      assert.ok(Array.isArray(resolved.resolved.finally), 'Expected finally to be array');
      assert.equal(resolved.resolved.finally.length, 2);
      const finStep = resolved.resolved.finally[0];
      assert.equal(finStep.type, 'http');
      assert.equal(finStep.operands.baseEnv, 'E2E_API_BASE_URL');
      assert.equal(finStep.operands.pathSegments[3].runtime_ref.state_key, 'booking_id');
      assert.equal(finStep.operands.method, 'POST');
      assert.deepEqual(resolved.resolved.finally[1].operands.expectedBodyField, {
        object: 'data', field: 'status', equals_literal: 'cancelled',
      });
    });
  });

  // -------------------------------------------------------------------------
  // 5. Codegen: generated script properties (static analysis)
  // -------------------------------------------------------------------------
  describe('codegen — generated script static analysis', function () {
    var script;

    function getScript() {
      if (script) return script;
      const parsed = parse(FLOW_PATH, MAPPING_DIR);
      assert.equal(parsed.errors.length, 0, parsed.errors.join('; '));
      const resolved = resolve(parsed.flow, parsed.mapping, { runtimeValues: parsed.flow.runtime_values });
      assert.equal(resolved.errors.length, 0, resolved.errors.join('; '));
      script = generate(resolved.resolved, parsed.flow.name);
      return script;
    }

    test('generated script contains #!/usr/bin/env bash shebang', function () {
      const s = getScript();
      assert.ok(s.startsWith('#!/usr/bin/env bash'), 'Expected bash shebang at start');
    });

    test('generated script has exactly one trap EXIT (single authoritative exit controller)', function () {
      const s = getScript();
      const trapMatches = s.match(/\btrap\s+(?!-)[^\n]*EXIT/g) || [];
      assert.equal(trapMatches.length, 1,
        'Expected exactly one "trap ... EXIT". Found: ' + trapMatches.join(' | '));
    });

    test('generated script does not contain the literal string BOOKING_PASSWORD as a value', function () {
      const s = getScript();
      // The variable name BOOKING_PASSWORD is fine (it's referenced), but the marker
      // "runtime_ref:BOOKING_PASSWORD" must never appear and no fill command should
      // embed a secret value literal on the command line.
      assert.ok(!s.includes('runtime_ref:booking_password'),
        'Must not embed runtime_ref: token literally in generated script');
    });

    test('generated script does not pass secret via argv (no agent-browser fill ... BOOKING_PASSWORD value on command line)', function () {
      const s = getScript();
      // Fill for sensitive step must use read -s or a heredoc/process substitution, not argv
      // Check that the fill password line does NOT appear as a positional arg to agent-browser fill
      assert.ok(!s.match(/agent-browser\s+fill\s+[^\n]+E2E_BOOKING_PASSWORD[^\n]*/),
        'Must not pass BOOKING_PASSWORD as arg to agent-browser fill');
    });

    test('generated script uses read -s for sensitive fill (stdin-based secret)', function () {
      const s = getScript();
      // Must use read -s to collect secret from stdin
      assert.ok(s.includes('read -s') || s.includes('read -rs'),
        'Expected "read -s" in generated script for sensitive fill');
    });

    test('generated script emits runtime_values env block (required env, not positional)', function () {
      const s = getScript();
      // runtime_values should be checked as env vars (not $1/$2 positional)
      // Look for BOOKING_PASSWORD and ADMIN_TOKEN env-based :? patterns
      assert.ok(s.includes('E2E_BOOKING_PASSWORD') && s.includes('E2E_ADMIN_TOKEN'),
        'Expected declared environment names in generated script');
      // They must use :? env check or similar, not positional $1 assignment for secrets
      assert.ok(s.includes('${E2E_BOOKING_PASSWORD:?'),
        'Expected env-based :? check, not positional assignment');
    });

    test('generated script includes UUID validation for capture-url-query', function () {
      const s = getScript();
      // Must validate UUID format — look for UUID regex or grep pattern
      assert.ok(
        s.match(/[0-9a-fA-F]{8}-[0-9a-fA-F]{4}/i) ||
        s.includes('uuid') ||
        s.match(/grep.*[0-9a-f]{8}/i) ||
        s.includes('[0-9a-f]'),
        'Expected UUID validation pattern in generated script');
    });

    test('generated script captures query param from URL (bookingId)', function () {
      const s = getScript();
      // Must extract bookingId from URL
      assert.ok(s.includes('bookingId'),
        'Expected "bookingId" in generated script for URL param capture');
    });

    test('generated script includes curl or native HTTP call in finally block', function () {
      const s = getScript();
      // Finally block must use curl (or equivalent) for HTTP call
      assert.ok(s.includes('curl') || s.includes('wget'),
        'Expected curl or wget in generated script for HTTP finally step');
    });

    test('generated script exports BOOKING_ID after capture (reuse in finally)', function () {
      const s = getScript();
      // Captured value must be assigned/exported for use in later steps
      assert.ok(s.includes('BOOKING_ID'),
        'Expected BOOKING_ID to be assigned in generated script for reuse');
    });

    test('generated script finally block is inside cleanup() function called from trap EXIT', function () {
      const s = getScript();
      // The finally HTTP call must be inside or called from the cleanup() function
      // We verify by checking that curl (or the HTTP call) is inside the cleanup function definition
      const cleanupMatch = s.match(/cleanup\s*\(\s*\)\s*\{([\s\S]*?)\n\}/);
      assert.ok(cleanupMatch,
        'Expected cleanup() function in generated script');
      const cleanupBody = cleanupMatch[1];
      assert.ok(cleanupBody.includes('curl') || cleanupBody.includes('BOOKING_ID') ||
        cleanupBody.includes('cancel'),
        'Expected finally HTTP call inside cleanup() body. cleanup body:\n' + cleanupBody);
    });
  });

  // -------------------------------------------------------------------------
  // 6. Integration: compile() with runtime fixture
  // -------------------------------------------------------------------------
  describe('codegen — runtime integration (bash execution)', function () {
    var tmpDir;
    var compiledScript;

    // Set up: compile the flow once for this group
    test('compile() runtime-state-finalizer-flow succeeds', async function () {
      tmpDir = makeTmpDir();
      const result = await compile(FLOW_PATH, MAPPING_DIR, tmpDir);
      assert.equal(result.success, true,
        'Expected compile success=true. Errors: ' + JSON.stringify(result.errors));
      assert.ok(fs.existsSync(result.outputPath), 'Expected output file to exist');
      compiledScript = result.outputPath;
    });

    test('SUCCESS path: script exits 0 when finalizer HTTP succeeds', function () {
      if (!compiledScript) {
        // compile test above must have run
        return;
      }

      const binDir = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-sc1032-bin-'));
      try {
        // Stub agent-browser: navigate succeeds, snapshot succeeds,
        // get url returns URL with bookingId UUID
        const testUuid = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890';
        writeAgentBrowserStub(path.join(binDir, 'agent-browser'), testUuid, false);
        // Stub curl: always succeeds
        writeCurlStub(path.join(binDir, 'curl'));
        // Stub sleep: no-op
        writeExecutable(path.join(binDir, 'sleep'), '#!/usr/bin/env bash\nexit 0\n');

        const result = runScript(compiledScript, {
          binDir: binDir,
          // Provide required env (runtime_values)
          env: {
            E2E_BOOKING_PASSWORD: 'test-secret-password',
            E2E_ADMIN_TOKEN: 'test-admin-token',
            E2E_API_BASE_URL: 'http://localhost:3000',
            BASE_URL: 'http://localhost:3000',
            E2E_SCREENSHOT_DIR: path.join(tmpDir, 'screenshots'),
          },
          stdin: '',
        });

        assert.equal(result.status, 0,
          'Expected exit 0 on success. stdout:\n' + result.stdout + '\nstderr:\n' + result.stderr);
        assert.ok(result.stdout.includes('PASS') || result.status === 0,
          'Expected PASS in stdout');
      } finally {
        fs.rmSync(binDir, { recursive: true, force: true });
      }
    });

    test('FAILURE path: deliberate post-capture step failure still runs finalizer with captured BOOKING_ID', function () {
      if (!compiledScript) return;

      const binDir = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-sc1032-fail-bin-'));
      const finalizerLog = path.join(binDir, 'finalizer-calls.log');
      try {
        const testUuid = 'deadbeef-dead-beef-dead-beefdeadbeef';
        writeAgentBrowserStub(path.join(binDir, 'agent-browser'), testUuid, true);
        // Stub curl: logs calls with BOOKING_ID from body, always succeeds
        writeCurlStub(path.join(binDir, 'curl'), finalizerLog);
        writeExecutable(path.join(binDir, 'sleep'), '#!/usr/bin/env bash\nexit 0\n');

        const result = runScript(compiledScript, {
          binDir: binDir,
          env: {
            E2E_BOOKING_PASSWORD: 'test-secret-password',
            E2E_ADMIN_TOKEN: 'test-admin-token',
            E2E_API_BASE_URL: 'http://localhost:3000',
            BASE_URL: 'http://localhost:3000',
            CONTINUE_ON_ERROR: 'true',
            E2E_SCREENSHOT_DIR: path.join(tmpDir, 'screenshots'),
          },
          stdin: '',
        });

        // Script should exit non-zero because snapshot step failed
        assert.notEqual(result.status, 0,
          'Expected non-zero exit after post-capture failure. stdout:\n' + result.stdout);

        // Finalizer must have been called (curl log exists and contains bookingId)
        assert.ok(fs.existsSync(finalizerLog),
          'Expected finalizer curl to have been called (log file missing)');
        const logContents = fs.readFileSync(finalizerLog, 'utf8');
        assert.ok(logContents.includes(testUuid),
          'Expected finalizer to use captured BOOKING_ID (' + testUuid + '). Got: ' + logContents);
      } finally {
        fs.rmSync(binDir, { recursive: true, force: true });
      }
    });

    test('FINALIZER FAILURE path: finalizer HTTP failure makes exit non-zero even on step success', function () {
      if (!compiledScript) return;

      const binDir = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-sc1032-finfail-bin-'));
      try {
        const testUuid = 'cafebabe-cafe-babe-cafe-babecafebabe';
        writeAgentBrowserStub(path.join(binDir, 'agent-browser'), testUuid, false);
        // curl FAILS — finalizer HTTP failure
        writeExecutable(path.join(binDir, 'curl'), [
          '#!/usr/bin/env bash',
          'echo "HTTP error: connection refused" >&2',
          'exit 1',
        ].join('\n'));
        writeExecutable(path.join(binDir, 'sleep'), '#!/usr/bin/env bash\nexit 0\n');

        const result = runScript(compiledScript, {
          binDir: binDir,
          env: {
            E2E_BOOKING_PASSWORD: 'test-secret-password',
            E2E_ADMIN_TOKEN: 'test-admin-token',
            E2E_API_BASE_URL: 'http://localhost:3000',
            BASE_URL: 'http://localhost:3000',
            E2E_SCREENSHOT_DIR: path.join(tmpDir, 'screenshots'),
          },
          stdin: '',
        });

        // Finalizer failure must make the script exit non-zero
        assert.notEqual(result.status, 0,
          'Expected non-zero exit when finalizer HTTP fails. stdout:\n' + result.stdout +
          '\nstderr:\n' + result.stderr);
      } finally {
        fs.rmSync(binDir, { recursive: true, force: true });
      }
    });

    test('generated script does not echo or print secret values (no diagnostic leak)', function () {
      if (!compiledScript) return;

      const content = fs.readFileSync(compiledScript, 'utf8');
      // The actual secret values should never appear in the generated Bash.
      // The variable NAME is fine but the value 'test-secret-password' etc. must not be hardcoded.
      assert.ok(!content.includes('test-secret-password'),
        'Secret value must not be hardcoded in generated script');
      // Also check no diagnostic echo that would print $BOOKING_PASSWORD to stdout
      assert.ok(!content.match(/echo\s+["']?\$BOOKING_PASSWORD/),
        'Must not echo $BOOKING_PASSWORD value to stdout');
    });
  });

  describe('T2 hostile sink and lifecycle coverage', function () {
    test('parser rejects hostile query/state identifiers, collisions, and unknown finalizer refs', function () {
      const base = {
        name: 'hostile-schema',
        mapping: 'runtime-state-finalizer-mapping',
        runtime_values: {
          booking_id: { from_env: 'E2E_BOOKING_ID', sensitive: false },
        },
        steps: [{
          id: 'capture', type: 'capture-url-query', action: 'Capture bookingId from URL query',
          query: 'bookingId;$(touch pwned)', save_as: 'booking_id', validate: 'uuid',
        }],
        finally: [{
          id: 'cleanup', type: 'http', action: 'cleanup',
          request: {
            method: 'POST',
            url: { base_from_env: 'E2E_API_BASE_URL', path_segments: [{ runtime_ref: 'missing' }] },
          },
        }],
      };
      const result = parseInlineFlow(base);
      assert.ok(result.errors.some(function (e) { return e.includes('ASCII URL query key'); }));
      assert.ok(result.errors.some(function (e) { return e.includes('collides'); }));
      assert.ok(result.errors.some(function (e) { return e.includes("unknown runtime_ref 'missing'"); }));

      base.steps[0].query = 'bookingId';
      base.steps[0].save_as = 'bad;state';
      const badState = parseInlineFlow(base);
      assert.ok(badState.errors.some(function (e) { return e.includes('non-reserved identifier'); }));
    });

    test('generated sinks use stdin, exact-one browser parsing, encoding, and post-finalizer reports', function () {
      const parsed = parse(FLOW_PATH, MAPPING_DIR);
      const resolved = resolve(parsed.flow, parsed.mapping, { runtimeValues: parsed.flow.runtime_values });
      const script = generate(resolved.resolved, parsed.flow.name);
      assert.ok(script.includes('searchParams.getAll("bookingId")'));
      assert.ok(script.includes('values.length!==1'));
      assert.ok(script.includes('eval --stdin'));
      assert.ok(script.includes('_base64_no_wrap'));
      assert.ok(script.includes('--config "$_FINALIZER_CONFIG"'));
      assert.ok(script.includes('--data-binary @-'));
      const cleanup = script.match(/cleanup\(\) \{([\s\S]*?)\n\}/)[1];
      assert.ok(cleanup.indexOf('cancel-booking-finalizer') < cleanup.indexOf('verify-booking-cancelled-finalizer'));
      assert.ok(cleanup.indexOf('verify-booking-cancelled-finalizer') < cleanup.indexOf('_emit_metrics'));
    });

    test('capture rejects missing, duplicate/empty, invalid UUID, and multiline protocol output', async function () {
      const tmpDir = makeTmpDir();
      const compiled = await compile(FLOW_PATH, MAPPING_DIR, tmpDir);
      const cases = [
        { name: 'missing', output: '', status: 1 },
        { name: 'duplicate', output: '', status: 1 },
        { name: 'empty', output: '__E2E_CAPTURE__', status: 0 },
        { name: 'invalid', output: '__E2E_CAPTURE__not-a-uuid', status: 0 },
        { name: 'multiline', output: '__E2E_CAPTURE__a1b2c3d4-e5f6-7890-abcd-ef1234567890\nnoise', status: 0 },
      ];
      for (const hostile of cases) {
        const binDir = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-sc1032-capture-'));
        writeExecutable(path.join(binDir, 'agent-browser'), [
          '#!/usr/bin/env bash',
          'if [ "$*" = "eval --stdin" ]; then',
          '  _program=$(cat)',
          '  case "$_program" in',
          '    *"searchParams.getAll"*) printf ' + singleShellLiteral('%s\n') + ' ' +
            singleShellLiteral(hostile.output) + '; exit ' + hostile.status + ' ;;',
          '    *) exit 0 ;;',
          '  esac',
          'fi',
          'case "$*" in *snapshot*) echo ok ;; *) exit 0 ;; esac',
        ].join('\n'));
        writeCurlStub(path.join(binDir, 'curl'));
        writeExecutable(path.join(binDir, 'sleep'), '#!/usr/bin/env bash\nexit 0\n');
        const result = runScript(compiled.outputPath, {
          binDir: binDir,
          env: {
            E2E_BOOKING_PASSWORD: 'secret', E2E_ADMIN_TOKEN: 'token',
            E2E_API_BASE_URL: 'http://localhost', BASE_URL: 'http://localhost',
            CONTINUE_ON_ERROR: 'true', E2E_SCREENSHOT_DIR: path.join(tmpDir, hostile.name),
          },
        });
        assert.notEqual(result.status, 0, hostile.name + ' capture must fail');
        fs.rmSync(binDir, { recursive: true, force: true });
      }
      fs.rmSync(tmpDir, { recursive: true, force: true });
    });

    test('hostile secret is literal, absent from argv/output, and cannot execute shell text', async function () {
      const tmpDir = makeTmpDir();
      const compiled = await compile(FLOW_PATH, MAPPING_DIR, tmpDir);
      const binDir = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-sc1032-secret-'));
      const marker = path.join(tmpDir, 'executed');
      const argvLog = path.join(tmpDir, 'argv.log');
      const secret = 'quote\'" `touch ' + marker + '` $(touch ' + marker + ') / % space\n\tend';
      writeAgentBrowserStub(path.join(binDir, 'agent-browser'), 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', false);
      writeExecutable(path.join(binDir, 'curl'), '#!/usr/bin/env bash\nprintf \'%s\\n\' "$*" >> ' +
        singleShellLiteral(argvLog) + '\necho \'{"status":"cancelled"}\'\n');
      writeExecutable(path.join(binDir, 'sleep'), '#!/usr/bin/env bash\nexit 0\n');
      const result = runScript(compiled.outputPath, {
        binDir: binDir,
        env: {
          E2E_BOOKING_PASSWORD: secret, E2E_ADMIN_TOKEN: secret,
          E2E_API_BASE_URL: 'http://localhost', BASE_URL: 'http://localhost',
          E2E_SCREENSHOT_DIR: path.join(tmpDir, 'shots'),
        },
      });
      assert.notEqual(result.status, 0, 'header control whitespace must fail the finalizer');
      assert.equal(fs.existsSync(marker), false);
      assert.equal((result.stdout + result.stderr).includes(secret), false);
      assert.equal(fs.existsSync(argvLog) && fs.readFileSync(argvLog, 'utf8').includes(secret), false);
      fs.rmSync(binDir, { recursive: true, force: true });
      fs.rmSync(tmpDir, { recursive: true, force: true });
    });

    test('ordered finalizers land in reports and combined failure remains authoritative', async function () {
      const tmpDir = makeTmpDir();
      const compiled = await compile(FLOW_PATH, MAPPING_DIR, tmpDir);
      const binDir = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-sc1032-report-'));
      const metrics = path.join(tmpDir, 'metrics.json');
      const junit = path.join(tmpDir, 'junit.xml');
      writeAgentBrowserStub(path.join(binDir, 'agent-browser'), 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', true);
      writeExecutable(path.join(binDir, 'curl'), '#!/usr/bin/env bash\nexit 1\n');
      writeExecutable(path.join(binDir, 'sleep'), '#!/usr/bin/env bash\nexit 0\n');
      const result = runScript(compiled.outputPath, {
        binDir: binDir,
        args: ['--continue-on-error', '--metrics-output', metrics, '--junit', junit],
        env: {
          E2E_BOOKING_PASSWORD: 'secret', E2E_ADMIN_TOKEN: 'token',
          E2E_API_BASE_URL: 'http://localhost', BASE_URL: 'http://localhost',
          E2E_SCREENSHOT_DIR: path.join(tmpDir, 'shots'),
        },
      });
      assert.notEqual(result.status, 0);
      const report = JSON.parse(fs.readFileSync(metrics, 'utf8'));
      const finalizerSteps = report.steps.slice(-2);
      assert.deepEqual(finalizerSteps.map(function (step) { return step.id; }), [
        'cancel-booking-finalizer', 'verify-booking-cancelled-finalizer',
      ]);
      assert.deepEqual(finalizerSteps.map(function (step) { return step.result; }), ['fail', 'fail']);
      const xml = fs.readFileSync(junit, 'utf8');
      assert.ok(xml.indexOf('cancel-booking-finalizer') < xml.indexOf('verify-booking-cancelled-finalizer'));
      fs.rmSync(binDir, { recursive: true, force: true });
      fs.rmSync(tmpDir, { recursive: true, force: true });
    });
  });

  describe('SC-1032 Verify repair regressions', function () {
    async function compilePreCaptureFailureFlow(tmpDir) {
      const yaml = require('js-yaml');
      const flowPath = path.join(tmpDir, 'pre-capture-failure-flow.yaml');
      fs.writeFileSync(flowPath, yaml.dump({
        name: 'pre-capture-failure-flow',
        mapping: 'runtime-state-finalizer-mapping',
        runtime_values: {
          admin_token: { from_env: 'E2E_ADMIN_TOKEN', sensitive: true },
        },
        steps: [
          { id: 'primary-failure', type: 'snapshot', action: 'Take snapshot' },
          {
            id: 'capture-booking-id', type: 'capture-url-query',
            action: 'Capture bookingId from URL query', query: 'bookingId',
            save_as: 'booking_id', validate: 'uuid',
          },
        ],
        finally: [
          {
            id: 'cancel-booking-finalizer', type: 'http', action: 'Cancel captured booking',
            request: {
              method: 'POST',
              url: {
                base_from_env: 'E2E_API_BASE_URL',
                path_segments: ['api', 'bookings', { runtime_ref: 'booking_id' }, 'cancel'],
              },
              headers: { Authorization: { scheme: 'Bearer', runtime_ref: 'admin_token' } },
            },
            expect: { status: 200 },
          },
          {
            id: 'verify-booking-finalizer', type: 'http', action: 'Read back booking',
            request: {
              method: 'GET',
              url: {
                base_from_env: 'E2E_API_BASE_URL',
                path_segments: ['api', 'bookings', { runtime_ref: 'booking_id' }],
              },
              headers: { Authorization: { scheme: 'Bearer', runtime_ref: 'admin_token' } },
            },
            expect: { status: 200, body: { field: 'status', equals: 'cancelled' } },
          },
        ],
      }));
      return compile(flowPath, MAPPING_DIR, path.join(tmpDir, 'compiled'));
    }

    test('runScript timeout terminates the generated runner process group', function () {
      const tmpDir = makeTmpDir();
      const scriptPath = path.join(tmpDir, 'leaking-runner.sh');
      const childPidPath = path.join(tmpDir, 'child.pid');
      try {
        writeExecutable(scriptPath, [
          '#!/usr/bin/env bash',
          '/bin/sh -c ' + singleShellLiteral(
            'trap "" TERM; echo $$ > "$1"; while :; do sleep 1; done'
          ) + ' sh ' + singleShellLiteral(childPidPath) + ' &',
          'wait',
        ].join('\n'));

        const startedAt = Date.now();
        const result = runScript(scriptPath, { timeout: 250 });
        assert.equal(result.status, 124, result.stdout + '\n' + result.stderr);
        assert.ok(Date.now() - startedAt < 3000, 'runner timeout must be bounded');
        const childPid = Number(fs.readFileSync(childPidPath, 'utf8').trim());
        assert.throws(function () { process.kill(childPid, 0); }, /ESRCH/,
          'runner descendants must be gone after timeout');
      } finally {
        fs.rmSync(tmpDir, { recursive: true, force: true });
      }
    });

    test('curl config escaping rejects representable C0 controls and DEL but preserves UTF-8', function () {
      const tmpDir = makeTmpDir();
      const scriptPath = path.join(tmpDir, 'curl-config-escape.sh');
      try {
        writeExecutable(scriptPath, [
          '#!/usr/bin/env bash',
          generateRuntimeSupport(true),
          'if _curl_config_escape "$TOKEN"; then exit 0; else exit 1; fi',
        ].join('\n'));

        const forbidden = [];
        for (let code = 1; code <= 31; code++) forbidden.push(code);
        forbidden.push(127);
        for (const code of forbidden) {
          const token = 'abc' + String.fromCharCode(code) + 'def';
          const result = runScript(scriptPath, { env: { TOKEN: token }, timeout: 2000 });
          assert.equal(result.status, 1,
            'control byte 0x' + code.toString(16).padStart(2, '0') + ' must be rejected');
          assert.equal((result.stdout + result.stderr).includes(token), false,
            'rejected token must not leak for byte 0x' + code.toString(16));
        }

        assert.throws(function () {
          runScript(scriptPath, { env: { TOKEN: 'abc\0def' }, timeout: 2000 });
        }, /null bytes/, 'NUL is rejected by the process environment boundary');

        const utf8Token = 'token-\u5bc6\u78bc-\u00e9-\ud83d\udd10';
        const utf8Result = runScript(scriptPath, { env: { TOKEN: utf8Token }, timeout: 2000 });
        assert.equal(utf8Result.status, 0, utf8Result.stderr);
        assert.equal(utf8Result.stdout, utf8Token);
      } finally {
        fs.rmSync(tmpDir, { recursive: true, force: true });
      }
    });

    test('unsafe credential control bytes fail before curl without leaking the secret', async function () {
      const tmpDir = makeTmpDir();
      const compiled = await compile(FLOW_PATH, MAPPING_DIR, path.join(tmpDir, 'compiled'));
      const binDir = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-sc1032-c0-secret-'));
      const curlLog = path.join(tmpDir, 'curl.log');
      const secret = 'abc\x01def';
      try {
        writeAgentBrowserStub(
          path.join(binDir, 'agent-browser'),
          'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
          false
        );
        writeCurlStub(path.join(binDir, 'curl'), curlLog);
        writeExecutable(path.join(binDir, 'sleep'), '#!/usr/bin/env bash\nexit 0\n');

        const result = runScript(compiled.outputPath, {
          binDir: binDir,
          env: {
            E2E_BOOKING_PASSWORD: 'password', E2E_ADMIN_TOKEN: secret,
            E2E_API_BASE_URL: 'http://localhost', BASE_URL: 'http://localhost',
            E2E_SCREENSHOT_DIR: path.join(tmpDir, 'shots'),
          },
        });

        assert.equal(result.status, 1, result.stdout + '\n' + result.stderr);
        assert.equal(fs.existsSync(curlLog), false, 'curl must not run for an unsafe credential');
        assert.equal((result.stdout + result.stderr).includes(secret), false,
          'unsafe credential must not appear in output');
      } finally {
        fs.rmSync(binDir, { recursive: true, force: true });
        fs.rmSync(tmpDir, { recursive: true, force: true });
      }
    });

    test('successful finalizers emit exactly one deferred success summary', async function () {
      const tmpDir = makeTmpDir();
      const compiled = await compile(FLOW_PATH, MAPPING_DIR, path.join(tmpDir, 'compiled'));
      const binDir = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-sc1032-summary-ok-'));
      try {
        const script = fs.readFileSync(compiled.outputPath, 'utf8');
        const cleanupStart = script.indexOf('cleanup() {');
        const trapStart = script.indexOf('trap cleanup EXIT');
        const successSummary = 'PASS: runtime-state-finalizer-flow (5/5 steps, 0 skipped)';
        assert.ok(script.slice(cleanupStart, trapStart).includes(successSummary),
          'finalizer success summary must be emitted by cleanup');
        assert.equal(script.slice(trapStart).includes(successSummary), false,
          'ordinary footer must not print success before finalizers');

        writeAgentBrowserStub(
          path.join(binDir, 'agent-browser'),
          'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
          false
        );
        writeCurlStub(path.join(binDir, 'curl'));
        writeExecutable(path.join(binDir, 'sleep'), '#!/usr/bin/env bash\nexit 0\n');
        const result = runScript(compiled.outputPath, {
          binDir: binDir,
          env: {
            E2E_BOOKING_PASSWORD: 'password', E2E_ADMIN_TOKEN: 'token',
            E2E_API_BASE_URL: 'http://localhost', BASE_URL: 'http://localhost',
            E2E_SCREENSHOT_DIR: path.join(tmpDir, 'shots'),
          },
        });
        assert.equal(result.status, 0, result.stdout + '\n' + result.stderr);
        const summaries = result.stdout.split('\n').filter(function (line) {
          return line.startsWith('PASS:') || line.startsWith('PASS (FLAKY):');
        });
        assert.deepEqual(summaries, [successSummary]);
      } finally {
        fs.rmSync(binDir, { recursive: true, force: true });
        fs.rmSync(tmpDir, { recursive: true, force: true });
      }
    });

    test('finalizer failure emits no PASS or flaky PASS summary', async function () {
      const tmpDir = makeTmpDir();
      const compiled = await compile(FLOW_PATH, MAPPING_DIR, path.join(tmpDir, 'compiled'));
      const binDir = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-sc1032-summary-fail-'));
      try {
        writeAgentBrowserStub(
          path.join(binDir, 'agent-browser'),
          'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
          false
        );
        writeExecutable(path.join(binDir, 'curl'), '#!/usr/bin/env bash\nexit 1\n');
        writeExecutable(path.join(binDir, 'sleep'), '#!/usr/bin/env bash\nexit 0\n');
        const result = runScript(compiled.outputPath, {
          binDir: binDir,
          env: {
            E2E_BOOKING_PASSWORD: 'password', E2E_ADMIN_TOKEN: 'token',
            E2E_API_BASE_URL: 'http://localhost', BASE_URL: 'http://localhost',
            E2E_SCREENSHOT_DIR: path.join(tmpDir, 'shots'),
          },
        });
        assert.equal(result.status, 1, result.stdout + '\n' + result.stderr);
        assert.equal(/PASS(?: \(FLAKY\))?:/.test(result.stdout), false, result.stdout);
      } finally {
        fs.rmSync(binDir, { recursive: true, force: true });
        fs.rmSync(tmpDir, { recursive: true, force: true });
      }
    });

    test('pre-capture primary failure records unavailable state, closes browser, emits reports, and preserves status', async function () {
      const tmpDir = makeTmpDir();
      const compiled = await compilePreCaptureFailureFlow(tmpDir);
      const binDir = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-sc1032-pre-capture-'));
      const browserLog = path.join(tmpDir, 'browser.log');
      const curlLog = path.join(tmpDir, 'curl.log');
      const metrics = path.join(tmpDir, 'metrics.json');
      const junit = path.join(tmpDir, 'junit.xml');
      try {
        writeExecutable(path.join(binDir, 'agent-browser'), [
          '#!/usr/bin/env bash',
          'printf \'%s\\n\' "$*" >> ' + singleShellLiteral(browserLog),
          'case "$*" in',
          '  *snapshot*) exit 42 ;;',
          '  *close*) exit 0 ;;',
          '  *) exit 0 ;;',
          'esac',
        ].join('\n'));
        writeExecutable(path.join(binDir, 'curl'), '#!/usr/bin/env bash\nprintf called >> ' +
          singleShellLiteral(curlLog) + '\nexit 0\n');

        const result = runScript(compiled.outputPath, {
          binDir: binDir,
          args: ['--metrics-output', metrics, '--junit', junit],
          env: {
            E2E_ADMIN_TOKEN: 'test-admin-token', E2E_API_BASE_URL: 'http://localhost',
            BASE_URL: 'http://localhost', E2E_SCREENSHOT_DIR: path.join(tmpDir, 'shots'),
          },
        });

        assert.equal(result.status, 42,
          'the primary status must outrank finalizer failure; stderr:\n' + result.stderr);
        assert.equal((result.stdout + result.stderr).includes('unbound variable'), false);
        assert.equal(fs.existsSync(curlLog), false, 'missing captured state must not issue HTTP requests');
        assert.ok(fs.readFileSync(browserLog, 'utf8').split('\n').some(function (line) {
          return line === 'close';
        }), 'browser close must still run after finalizer failures');
        const report = JSON.parse(fs.readFileSync(metrics, 'utf8'));
        assert.deepEqual(report.steps.map(function (step) { return step.id; }), [
          'cancel-booking-finalizer', 'verify-booking-finalizer',
        ]);
        assert.deepEqual(report.steps.map(function (step) { return step.result; }), ['fail', 'fail']);
        assert.ok(report.steps.every(function (step) {
          return step.failure_msg.includes("runtime state 'booking_id' is unavailable");
        }), JSON.stringify(report.steps));
        const xml = fs.readFileSync(junit, 'utf8');
        assert.ok(xml.includes('cancel-booking-finalizer'));
        assert.ok(xml.includes('verify-booking-finalizer'));
      } finally {
        fs.rmSync(binDir, { recursive: true, force: true });
        fs.rmSync(tmpDir, { recursive: true, force: true });
      }
    });

    test('readback structurally requires exact data.status despite a hostile top-level decoy', async function () {
      const tmpDir = makeTmpDir();
      const compiled = await compile(FLOW_PATH, MAPPING_DIR, tmpDir);
      const cases = [
        { name: 'valid', body: '{"status":"active","data":{"status":"cancelled"}}', expectedStatus: 0 },
        { name: 'malformed', body: '{"data":{"status":"cancelled"}', expectedStatus: 1 },
        { name: 'top-level-decoy', body: '{"status":"cancelled","data":{"status":"active"}}', expectedStatus: 1 },
        { name: 'missing-object', body: '{"status":"cancelled"}', expectedStatus: 1 },
        { name: 'wrong-object', body: '{"status":"cancelled","data":[]}', expectedStatus: 1 },
        { name: 'missing-field', body: '{"status":"cancelled","data":{"result":"cancelled"}}', expectedStatus: 1 },
        { name: 'wrong-field-type', body: '{"status":"cancelled","data":{"status":{"value":"cancelled"}}}', expectedStatus: 1 },
        { name: 'duplicate-object', body: '{"data":{"status":"active"},"data":{"status":"cancelled"}}', expectedStatus: 1 },
        { name: 'duplicate-field', body: '{"data":{"status":"active","status":"cancelled"}}', expectedStatus: 1 },
      ];
      try {
        for (const testCase of cases) {
          const binDir = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-sc1032-json-'));
          writeAgentBrowserStub(
            path.join(binDir, 'agent-browser'),
            'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
            false
          );
          writeExecutable(path.join(binDir, 'curl'), [
            '#!/usr/bin/env bash',
            '_out=""',
            'while [ "$#" -gt 0 ]; do',
            '  if [ "$1" = "-o" ]; then _out="$2"; shift 2; else shift; fi',
            'done',
            'printf \'%s\' ' + singleShellLiteral(testCase.body) + ' > "$_out"',
            'printf 200',
          ].join('\n'));
          writeExecutable(path.join(binDir, 'sleep'), '#!/usr/bin/env bash\nexit 0\n');

          const result = runScript(compiled.outputPath, {
            binDir: binDir,
            env: {
              E2E_BOOKING_PASSWORD: 'secret', E2E_ADMIN_TOKEN: 'token',
              E2E_API_BASE_URL: 'http://localhost', BASE_URL: 'http://localhost',
              E2E_SCREENSHOT_DIR: path.join(tmpDir, testCase.name),
            },
          });
          assert.equal(result.status, testCase.expectedStatus,
            testCase.name + ' body produced unexpected status; stdout:\n' + result.stdout +
            '\nstderr:\n' + result.stderr);
          fs.rmSync(binDir, { recursive: true, force: true });
        }
      } finally {
        fs.rmSync(tmpDir, { recursive: true, force: true });
      }
    });

    test('legacy top-level body field assertions remain executable', async function () {
      const tmpDir = makeTmpDir();
      const flow = require('js-yaml').load(fs.readFileSync(FLOW_PATH, 'utf8'));
      flow.name = 'legacy-top-level-readback';
      delete flow.finally[1].expect.body_field;
      flow.finally[1].expect.body = { field: 'status', equals: 'cancelled' };
      const flowPath = path.join(tmpDir, 'legacy-top-level-readback.yaml');
      fs.writeFileSync(flowPath, require('js-yaml').dump(flow));
      const compiled = await compile(flowPath, MAPPING_DIR, path.join(tmpDir, 'compiled'));
      const cases = [
        { name: 'valid', body: '{"status":"cancelled","data":{"status":"active"}}', expectedStatus: 0 },
        { name: 'nested-only', body: '{"data":{"status":"cancelled"}}', expectedStatus: 1 },
      ];
      try {
        for (const testCase of cases) {
          const binDir = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-sc1032-legacy-json-'));
          writeAgentBrowserStub(
            path.join(binDir, 'agent-browser'),
            'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
            false
          );
          writeExecutable(path.join(binDir, 'curl'), [
            '#!/usr/bin/env bash',
            '_out=""',
            'while [ "$#" -gt 0 ]; do',
            '  if [ "$1" = "-o" ]; then _out="$2"; shift 2; else shift; fi',
            'done',
            'printf \'%s\' ' + singleShellLiteral(testCase.body) + ' > "$_out"',
            'printf 200',
          ].join('\n'));
          writeExecutable(path.join(binDir, 'sleep'), '#!/usr/bin/env bash\nexit 0\n');

          const result = runScript(compiled.outputPath, {
            binDir: binDir,
            env: {
              E2E_BOOKING_PASSWORD: 'secret', E2E_ADMIN_TOKEN: 'token',
              E2E_API_BASE_URL: 'http://localhost', BASE_URL: 'http://localhost',
              E2E_SCREENSHOT_DIR: path.join(tmpDir, testCase.name),
            },
          });
          assert.equal(result.status, testCase.expectedStatus,
            testCase.name + ' body produced unexpected status; stdout:\n' + result.stdout +
            '\nstderr:\n' + result.stderr);
          fs.rmSync(binDir, { recursive: true, force: true });
        }
      } finally {
        fs.rmSync(tmpDir, { recursive: true, force: true });
      }
    });

    test('finalizer artifacts use a private directory, resist old-path symlinks, and are removed', async function () {
      const tmpDir = makeTmpDir();
      const compiled = await compile(FLOW_PATH, MAPPING_DIR, path.join(tmpDir, 'compiled'));
      const binDir = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-sc1032-temp-'));
      const attackerDir = path.join(tmpDir, 'attacker-tmp');
      const victim = path.join(tmpDir, 'victim');
      const evidence = path.join(tmpDir, 'curl-evidence.log');
      const secret = 'private-admin-token';
      fs.mkdirSync(attackerDir);
      fs.writeFileSync(victim, 'do-not-touch');
      try {
        writeExecutable(path.join(binDir, 'agent-browser'), [
          '#!/usr/bin/env bash',
          'for _suffix in 0.cfg 0.body 1.cfg 1.body; do',
          '  ln -s ' + singleShellLiteral(victim) + ' "$TMPDIR/e2e-finalizer-$PPID-$_suffix" 2>/dev/null || true',
          'done',
          'if [ "$*" = "eval --stdin" ]; then',
          '  _program=$(cat)',
          '  case "$_program" in',
          '    *"searchParams.getAll"*) printf \'%s\\n\' ' +
            singleShellLiteral('__E2E_CAPTURE__a1b2c3d4-e5f6-7890-abcd-ef1234567890') + ' ;;',
          '  esac',
          '  exit 0',
          'fi',
          'case "$*" in',
          '  *snapshot*) echo "- button Confirm Booking" ;;',
          '  *) exit 0 ;;',
          'esac',
        ].join('\n'));
        writeExecutable(path.join(binDir, 'curl'), [
          '#!/usr/bin/env bash',
          '_config=""',
          '_out=""',
          '_argv="$*"',
          'while [ "$#" -gt 0 ]; do',
          '  case "$1" in',
          '    --config) _config="$2"; shift 2 ;;',
          '    -o) _out="$2"; shift 2 ;;',
          '    *) shift ;;',
          '  esac',
          'done',
          '_dir=${_config%/*}',
          '_mode() { stat -f \'%Lp\' "$1" 2>/dev/null || stat -c \'%a\' "$1"; }',
          '{',
          '  printf \'config=%s\\nresponse=%s\\ndir=%s\\n\' "$_config" "$_out" "$_dir"',
          '  printf \'dir_mode=%s\\nconfig_mode=%s\\nresponse_mode=%s\\n\' "$(_mode "$_dir")" "$(_mode "$_config")" "$(_mode "$_out")"',
          '  if [ -L "$_config" ]; then echo config_symlink=true; else echo config_symlink=false; fi',
          '  if [ -L "$_out" ]; then echo response_symlink=true; else echo response_symlink=false; fi',
          '  printf \'argv=%s\\n\' "$_argv"',
          '} >> ' + singleShellLiteral(evidence),
          'printf \'%s\' \'{"data":{"status":"cancelled"}}\' > "$_out"',
          'printf 200',
        ].join('\n'));
        writeExecutable(path.join(binDir, 'sleep'), '#!/usr/bin/env bash\nexit 0\n');

        const result = runScript(compiled.outputPath, {
          binDir: binDir,
          env: {
            TMPDIR: attackerDir, E2E_BOOKING_PASSWORD: 'password', E2E_ADMIN_TOKEN: secret,
            E2E_API_BASE_URL: 'http://localhost', BASE_URL: 'http://localhost',
            E2E_SCREENSHOT_DIR: path.join(tmpDir, 'shots'),
          },
        });

        assert.equal(result.status, 0, result.stdout + '\n' + result.stderr);
        assert.equal(fs.readFileSync(victim, 'utf8'), 'do-not-touch',
          'pre-created legacy-path symlinks must not be followed');
        const log = fs.readFileSync(evidence, 'utf8');
        assert.equal(log.includes(secret), false, 'secret must not appear in curl argv evidence');
        assert.ok(log.includes('dir_mode=700'));
        assert.ok(log.includes('config_mode=600'));
        assert.ok(log.includes('response_mode=600'));
        assert.equal(log.includes('config_symlink=true'), false);
        assert.equal(log.includes('response_symlink=true'), false);
        const dirs = Array.from(new Set(log.match(/^dir=(.*)$/gm).map(function (line) {
          return line.slice('dir='.length);
        })));
        assert.equal(dirs.length, 1, log);
        assert.notEqual(dirs[0], attackerDir);
        assert.ok(path.basename(dirs[0]).startsWith('e2e-finalizer.'), dirs[0]);
        assert.equal(fs.existsSync(dirs[0]), false, 'private finalizer directory must be removed');
      } finally {
        fs.rmSync(binDir, { recursive: true, force: true });
        fs.rmSync(tmpDir, { recursive: true, force: true });
      }
    });
  });

  describe('SC-1032 review blockers', function () {
    function baseSingleSiteFlow() {
      return {
        name: 'review-blocker',
        mapping: 'runtime-state-finalizer-mapping',
        runtime_values: {
          admin_token: { from_env: 'E2E_ADMIN_TOKEN', sensitive: true },
        },
        steps: [{ id: 'snapshot', type: 'snapshot', action: 'Take snapshot' }],
      };
    }

    test('parser rejects hostile HTTP auth schemes before curl config codegen', function () {
      const hostileSchemes = [
        'Bearer"',
        'Bearer\nheader = "X-Injected: yes"',
        'Bear er',
        'Bearer\tInjected',
        'Bearer\u0001',
      ];
      for (const scheme of hostileSchemes) {
        const flow = baseSingleSiteFlow();
        flow.finally = [{
          id: 'cleanup', type: 'http', action: 'cleanup',
          request: {
            method: 'POST',
            url: { base_from_env: 'E2E_API_BASE_URL', path_segments: ['cleanup'] },
            headers: { Authorization: { scheme: scheme, runtime_ref: 'admin_token' } },
          },
        }];
        const result = parseInlineFlow(flow);
        assert.ok(result.errors.some(function (error) {
          return error.includes('auth scheme');
        }), JSON.stringify(scheme) + ' must be rejected: ' + result.errors.join('; '));
      }
    });

    test('parser rejects every unsupported finally type', function () {
      const flow = baseSingleSiteFlow();
      flow.finally = [{ id: 'cleanup', type: 'htp', action: 'typo must fail' }];
      const result = parseInlineFlow(flow);
      assert.ok(result.errors.some(function (error) {
        return error.includes("unsupported type 'htp'");
      }), result.errors.join('; '));
    });

    test('malformed path_segments returns validation errors without throwing', function () {
      const flow = baseSingleSiteFlow();
      flow.finally = [{
        id: 'cleanup', type: 'http', action: 'cleanup',
        request: {
          method: 'POST',
          url: { base_from_env: 'E2E_API_BASE_URL', path_segments: { bad: 'shape' } },
        },
      }];
      assert.doesNotThrow(function () { parseInlineFlow(flow); });
      const result = parseInlineFlow(flow);
      assert.ok(result.errors.some(function (error) {
        return error.includes('path_segments');
      }), result.errors.join('; '));
    });

    test('cross-site parse and compile fail closed for runtime values, capture, and finally', async function () {
      function crossSiteFlow() {
        return {
          name: 'cross-site-review-blocker',
          sites: { app: { mapping: 'runtime-state-finalizer-mapping' } },
          steps: [{ id: 'snapshot', site: 'app', type: 'snapshot', action: 'Take snapshot' }],
        };
      }
      const runtimeFlow = crossSiteFlow();
      runtimeFlow.runtime_values = {
        secret: { from_env: 'E2E_SECRET', sensitive: true },
      };
      const captureFlow = crossSiteFlow();
      captureFlow.mapping = 'runtime-state-finalizer-mapping';
      captureFlow.steps = [{
        id: 'capture', site: 'app', type: 'capture-url-query',
        action: 'Capture bookingId from URL query', query: 'bookingId', save_as: 'booking_id', validate: 'uuid',
      }];
      const finallyFlow = crossSiteFlow();
      finallyFlow.finally = [];

      for (const testCase of [runtimeFlow, captureFlow, finallyFlow]) {
        const yaml = require('js-yaml');
        const tmpDir = makeTmpDir();
        const flowPath = path.join(tmpDir, 'cross-site.yaml');
        fs.writeFileSync(flowPath, yaml.dump(testCase));
        const parseResult = parse(flowPath, MAPPING_DIR);
        assert.ok(parseResult.errors.some(function (error) {
          return error.includes('Cross-site flows do not support');
        }), parseResult.errors.join('; '));
        const compileResult = await compile(flowPath, MAPPING_DIR, path.join(tmpDir, 'out'));
        assert.equal(compileResult.success, false);
        assert.ok(compileResult.errors.some(function (error) {
          return error.includes('Cross-site flows do not support');
        }), compileResult.errors.join('; '));
        fs.rmSync(tmpDir, { recursive: true, force: true });
      }
    });

    test('cross-site malformed steps returns structured parse and compile errors without throwing', async function () {
      const yaml = require('js-yaml');
      const tmpDir = makeTmpDir();
      const flowPath = path.join(tmpDir, 'cross-site-malformed-steps.yaml');
      fs.writeFileSync(flowPath, yaml.dump({
        name: 'cross-site-malformed-steps',
        sites: { app: { mapping: 'runtime-state-finalizer-mapping' } },
        steps: { bad: 'shape' },
      }));

      let parseResult;
      assert.doesNotThrow(function () {
        parseResult = parse(flowPath, MAPPING_DIR);
      });
      assert.ok(parseResult.errors.some(function (error) {
        return error.includes('steps') && error.includes('array');
      }), parseResult.errors.join('; '));

      const compileResult = await compile(flowPath, MAPPING_DIR, path.join(tmpDir, 'out'));
      assert.equal(compileResult.success, false);
      assert.ok(compileResult.errors.some(function (error) {
        return error.includes('steps') && error.includes('array');
      }), compileResult.errors.join('; '));
      fs.rmSync(tmpDir, { recursive: true, force: true });
    });

    test('runtime value block does not embed hostile flow names in shell', function () {
      const hostileFlowName = 'flow}\necho REVIEW_BLOCKER_EXECUTED\n${';
      const block = generateRuntimeValuesBlock({
        secret: { from_env: 'E2E_SECRET', sensitive: true },
      }, hostileFlowName);
      assert.equal(block.includes(hostileFlowName), false);
      assert.equal(block.includes('REVIEW_BLOCKER_EXECUTED'), false);
    });
  });
});

function singleShellLiteral(value) {
  return "'" + String(value).replace(/'/g, "'\\''") + "'";
}
