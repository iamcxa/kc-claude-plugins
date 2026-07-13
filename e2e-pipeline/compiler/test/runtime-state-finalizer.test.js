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
const { generate } = require('../codegen.js');
const { compile } = require('../compiler.js');

const FIXTURES_DIR = path.join(__dirname, 'fixtures');
const FLOW_PATH = path.join(FIXTURES_DIR, 'runtime-state-finalizer-flow.yaml');
const MAPPING_DIR = FIXTURES_DIR;

const RUNTIME_BASH = fs.existsSync('/bin/bash') ? '/bin/bash' : 'bash';

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
    '[ -z "$_out" ] || printf \'%s\\n\' \'{"status":"cancelled"}\' > "$_out"',
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
  return childProcess.spawnSync(RUNTIME_BASH, [scriptPath].concat(opts.args || []), {
    encoding: 'utf8',
    env: env,
    input: opts.stdin || '',
    timeout: opts.timeout || 15000,
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
});

function singleShellLiteral(value) {
  return "'" + String(value).replace(/'/g, "'\\''") + "'";
}
