'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { execFileSync, spawn, spawnSync } = require('node:child_process');
const { describe, test } = require('node:test');

const pluginRoot = path.resolve(__dirname, '..', '..');
const finalizer = path.join(pluginRoot, 'scripts', 'finalize-trace.sh');
const archiveValidator = path.join(pluginRoot, 'scripts', 'validate-trace-archive.py');
const chromeValidator = path.join(pluginRoot, 'scripts', 'validate-chrome-trace.py');
const chromeTraceFixture = path.join(
  __dirname,
  'fixtures',
  'chrome-trace-event.json'
);
const identifierValidator = path.join(
  pluginRoot,
  'scripts',
  'validate-trace-identifiers.sh'
);
const teamTraceLifecycle = path.join(
  pluginRoot,
  'scripts',
  'team-trace-lifecycle.sh'
);

function makeTempDir() {
  return fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-trace-finalization-'));
}

function writePathWithoutPython(dir) {
  const binDir = path.join(dir, 'bin-without-python');
  fs.mkdirSync(binDir);
  for (const command of [
    'bash',
    'basename',
    'cat',
    'dirname',
    'mkdir',
    'mktemp',
    'mv',
    'rm',
    'tr',
  ]) {
    const resolved = execFileSync('sh', ['-c', `command -v ${command}`], {
      encoding: 'utf8',
    }).trim();
    fs.symlinkSync(resolved, path.join(binDir, command));
  }
  return binDir;
}

function writeAgentBrowserStub(dir) {
  const stub = path.join(dir, 'agent-browser-stub.sh');
  fs.writeFileSync(stub, `#!/usr/bin/env bash
set -eu

if [ -n "\${AGENT_BROWSER_LOG:-}" ]; then
  printf '%s\\n' "$*" >> "$AGENT_BROWSER_LOG"
fi

if [ "$#" -eq 1 ] && [ "$1" = "--version" ]; then
  printf '%s\\n' 'agent-browser 0.32.0'
  exit 0
fi
if [ "$#" -eq 2 ] && [ "$1" = "trace" ] && [ "$2" = "--help" ]; then
  if [ "\${TRACE_CAPABILITY_MODE:-}" = unknown ]; then
    printf '%s\\n' 'Record an implementation-defined trace.'
    exit 0
  fi
  printf '%s\\n' \
    'Record a Chrome DevTools trace for debugging.' \
    'agent-browser trace stop ./debug-trace.json'
  exit 0
fi

last_arg=
for arg in "$@"; do
  last_arg=$arg
done

case " $* " in
  *" trace start "*)
    if [ "\${TRACE_STUB_MODE:-}" = state-write-fail ]; then
      mkdir -p "$LIFECYCLE_STATE_PATH"
    fi
    exit 0
    ;;
  *" trace stop "*)
    case "\${TRACE_STUB_MODE:?}" in
      hang)
        while :; do sleep 1; done
        ;;
      fork-late-write)
        sh -c '
          trap "" TERM
          printf "%s\n" "$$" > "$1"
          sleep 4
          cp "$2" "$3"
          while :; do sleep 1; done
        ' sh "$DESCENDANT_PID_FILE" "$TRACE_FIXTURE" "$last_arg" &
        while :; do sleep 1; done
        ;;
      truncated)
        printf 'PK\\003\\004truncated' > "$last_arg"
        exit 0
        ;;
      directory)
        mkdir -p "$last_arg"
        exit 0
        ;;
      valid)
        cp "$TRACE_FIXTURE" "$last_arg"
        exit 0
        ;;
      state-write-fail)
        cp "$TRACE_FIXTURE" "$last_arg"
        exit 0
        ;;
    esac
    ;;
  *" close "*)
    : > "$RECOVERY_MARKER"
    exit 0
    ;;
esac

exit 64
`);
  fs.chmodSync(stub, 0o755);
  return stub;
}

function writeBrowserRuntimeStub(dir) {
  const stub = path.join(dir, 'browser-runtime-stub.sh');
  fs.writeFileSync(stub, `#!/usr/bin/env bash
set -eu

for arg in "$@"; do
  printf '<%s>\\n' "$arg" >> "$BROWSER_RUNTIME_LOG"
done
printf '%s\\n' '---' >> "$BROWSER_RUNTIME_LOG"

[ "$1" = "--run-id" ]
[ "$2" = "$EXPECTED_BROWSER_RUN_ID" ]
[ "$3" = "--app" ]
[ "$4" = "$EXPECTED_BROWSER_APP" ]
shift 4
exec "$AGENT_BROWSER_UNDERLYING" "$@"
`);
  fs.chmodSync(stub, 0o755);
  return stub;
}

function createValidTraceZip(dir) {
  const source = path.join(dir, 'trace-source');
  const archive = path.join(dir, 'valid-playwright-trace.zip');
  fs.mkdirSync(source);
  fs.writeFileSync(
    path.join(source, 'trace.trace'),
    '{"type":"context-options","timestamp":1}\n'
  );
  fs.mkdirSync(path.join(source, 'resources'));
  fs.writeFileSync(path.join(source, 'resources', 'sha1.dat'), 'body');
  fs.writeFileSync(path.join(source, 'ignored-metadata.txt'), 'not consumed by analyzer');
  execFileSync('zip', ['-q', '-r', archive, '.'], { cwd: source });
  return archive;
}

function createUnrelatedZip(dir) {
  const source = path.join(dir, 'unrelated-source');
  const archive = path.join(dir, 'unrelated.zip');
  fs.mkdirSync(source);
  fs.writeFileSync(path.join(source, 'report.txt'), 'not a Playwright trace');
  execFileSync('zip', ['-q', '-r', archive, '.'], { cwd: source });
  return archive;
}

function createNestedTraceZip(dir) {
  const source = path.join(dir, 'nested-trace-source');
  const archive = path.join(dir, 'nested-playwright-trace.zip');
  fs.mkdirSync(path.join(source, 'nested'), { recursive: true });
  fs.writeFileSync(
    path.join(source, 'nested', 'trace.trace'),
    '{"type":"context-options","timestamp":1}\n'
  );
  execFileSync('zip', ['-q', '-r', archive, '.'], { cwd: source });
  return archive;
}

function createUnsafeTraceZip(dir, kind) {
  const archive = path.join(dir, `unsafe-${kind}.zip`);
  execFileSync(
    'python3',
    [
      '-c',
      `
import stat
import sys
import zipfile

archive, kind = sys.argv[1:3]
with zipfile.ZipFile(archive, "w") as zf:
    trace = zipfile.ZipInfo("trace.trace")
    trace.create_system = 3
    trace.external_attr = (stat.S_IFREG | 0o600) << 16
    zf.writestr(trace, b'{"type":"context-options","timestamp":1}\\n')

    if kind == "symlink":
        unsafe = zipfile.ZipInfo("resources/host-link")
        unsafe.create_system = 3
        unsafe.external_attr = (stat.S_IFLNK | 0o777) << 16
        zf.writestr(unsafe, "/etc/hosts")
    elif kind == "traversal":
        unsafe = zipfile.ZipInfo("resources/../../escape")
        unsafe.create_system = 3
        unsafe.external_attr = (stat.S_IFREG | 0o600) << 16
        zf.writestr(unsafe, "escape")
    elif kind == "fifo":
        unsafe = zipfile.ZipInfo("resources/pipe")
        unsafe.create_system = 3
        unsafe.external_attr = (stat.S_IFIFO | 0o600) << 16
        zf.writestr(unsafe, "")
    else:
        raise SystemExit(f"unknown kind: {kind}")
`,
      archive,
      kind,
    ]
  );
  return archive;
}

function createResourceLimitTraceZip(dir, corruptPayload = false) {
  const archive = path.join(
    dir,
    corruptPayload ? 'resource-limit-corrupt.zip' : 'resource-limit.zip'
  );
  execFileSync(
    'python3',
    [
      '-c',
      `
import struct
import sys
import zipfile

archive = sys.argv[1]
corrupt = sys.argv[2] == "true"
with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zf:
    zf.writestr("trace.trace", b"A" * 65536)
    for index in range(4):
        zf.writestr(f"resources/{index:040x}", bytes([index]) * 4096)

if corrupt:
    with zipfile.ZipFile(archive) as zf:
        info = zf.getinfo("trace.trace")
        with open(archive, "r+b") as output:
            output.seek(info.header_offset)
            header = output.read(30)
            name_length, extra_length = struct.unpack_from("<HH", header, 26)
            data_offset = info.header_offset + 30 + name_length + extra_length
            output.seek(data_offset)
            first = output.read(1)
            output.seek(data_offset)
            output.write(bytes([first[0] ^ 0xFF]))
`,
      archive,
      String(corruptPayload),
    ]
  );
  return archive;
}

function writeHangingArchiveValidator(dir) {
  const validator = path.join(dir, 'hanging-validator.py');
  fs.writeFileSync(
    validator,
    `#!/usr/bin/env python3
import os
import signal
import time

signal.signal(signal.SIGTERM, signal.SIG_IGN)
child = os.fork()
if child == 0:
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    time.sleep(4)
    with open(os.environ["VALIDATOR_LATE_MARKER"], "w", encoding="utf-8") as marker:
        marker.write("late")
    while True:
        time.sleep(1)

while True:
    time.sleep(1)
`
  );
  return validator;
}

function writeMarkerArchiveValidator(dir, markerPath) {
  const validator = path.join(dir, 'marker-archive-validator.py');
  fs.writeFileSync(
    validator,
    [
      '#!/usr/bin/env python3',
      'from pathlib import Path',
      `Path(${JSON.stringify(markerPath)}).write_text("called", encoding="utf-8")`,
      'raise SystemExit(2)',
      '',
    ].join('\n')
  );
  return validator;
}

function parseResultFile(resultPath) {
  const result = {};
  const lines = fs.readFileSync(resultPath, 'utf8').trim().split('\n');
  for (const line of lines) {
    const separator = line.indexOf('=');
    result[line.slice(0, separator)] = line.slice(separator + 1);
  }
  return result;
}

function runFinalizer(options) {
  const dir = options.dir;
  const resultPath = options.resultPath || path.join(dir, 'trace-finalization.env');
  const traceFormat = options.traceFormat || 'playwright-trace-zip';
  const tracePath =
    options.tracePath ||
    path.join(
      dir,
      traceFormat === 'chrome-trace-json' ? 'trace.json' : 'trace.zip'
    );
  const recoveryMarker = options.recoveryMarker || path.join(dir, 'recovery-reached');
  const descendantPidFile = options.descendantPidFile || path.join(dir, 'descendant.pid');
  const agentBrowserLog = options.agentBrowserLog || path.join(dir, 'agent-browser.log');
  const stub = options.stub || writeAgentBrowserStub(dir);
  const finalizerArgs = [
    '--trace-path', tracePath,
    '--flow-verdict', options.flowVerdict || 'PASS',
    '--trace-producer', options.traceProducer || 'agent-browser',
    '--trace-producer-version', options.traceProducerVersion || 'test',
    '--trace-format', traceFormat,
    '--timeout', options.mode === 'hang' ? '1' : options.mode === 'fork-late-write' ? '2' : '10',
    // The owned runtime performs its own Node startup before forwarding close.
    // Leave one extra second under concurrent test load so this validates
    // recovery behavior rather than scheduler latency.
    '--recovery-timeout', options.browserRuntime ? '2' : '1',
    '--validation-timeout', options.validationTimeout || '10',
    '--result-file', resultPath,
  ];
  if (options.session) {
    finalizerArgs.push('--session', options.session);
  }
  if (options.browserRuntime) {
    finalizerArgs.push(
      '--browser-runtime', options.browserRuntime,
      '--browser-run-id', options.browserRunId,
      '--app', options.browserApp
    );
  }
  const startedAt = Date.now();
  const run = spawnSync(
    finalizer,
    finalizerArgs,
    {
      encoding: 'utf8',
      env: {
        ...process.env,
        AGENT_BROWSER_LOG: agentBrowserLog,
        AGENT_BROWSER_BIN: stub,
        AGENT_BROWSER_UNDERLYING: stub,
        BROWSER_RUNTIME_LOG: options.browserRuntimeLog || path.join(dir, 'browser-runtime.log'),
        DESCENDANT_PID_FILE: descendantPidFile,
        EXPECTED_BROWSER_APP: options.browserApp || '',
        EXPECTED_BROWSER_RUN_ID: options.browserRunId || '',
        E2E_TRACE_ARCHIVE_VALIDATOR: options.archiveValidator || '',
        E2E_CHROME_TRACE_VALIDATOR: options.chromeValidator || chromeValidator,
        RECOVERY_MARKER: recoveryMarker,
        TRACE_FIXTURE: options.fixture || '',
        TRACE_STUB_MODE: options.mode,
        VALIDATOR_LATE_MARKER: options.validatorLateMarker || '',
        ...(options.extraEnv || {}),
      },
      timeout: 15000,
    }
  );

  return {
    ...run,
    elapsedMs: Date.now() - startedAt,
    resultPath,
    tracePath,
    recoveryMarker,
    descendantPidFile,
    agentBrowserLog,
  };
}

describe('shared trace finalization contract', () => {
  test('never-exiting trace stop is bounded, recovers, and leaves report completion reachable', () => {
    const dir = makeTempDir();
    try {
      const run = runFinalizer({ dir, mode: 'hang', flowVerdict: 'PASS' });

      assert.equal(run.signal, null, run.error?.message);
      assert.equal(run.status, 20, run.stderr);
      // The finalizer itself normally completes in ~3s, but this file runs
      // concurrently with CPU-heavy compiler tests in the full suite. Keep
      // the assertion below spawnSync's 15s hard timeout without making it
      // sensitive to host scheduling pressure.
      assert.ok(run.elapsedMs < 12000, `finalizer took ${run.elapsedMs}ms`);
      assert.ok(fs.existsSync(run.recoveryMarker), 'bounded recovery must run after timeout');

      const result = parseResultFile(run.resultPath);
      assert.equal(result.flow_verdict, 'PASS');
      assert.equal(result.infrastructure_result, 'FAIL');
      assert.equal(result.stop_status, 'timeout');
      assert.equal(result.recovery_status, 'closed');
      assert.equal(result.analysis_eligible, 'false');

      const reportPath = path.join(dir, 'report.md');
      fs.writeFileSync(
        reportPath,
        `Flow verdict: ${result.flow_verdict}\nTrace infrastructure: ${result.infrastructure_result}\n`
      );
      assert.match(fs.readFileSync(reportPath, 'utf8'), /Flow verdict: PASS/);
    } finally {
      fs.rmSync(dir, { recursive: true, force: true });
    }
  });

  test('timeout kills TERM-ignoring descendants before they can late-write trace.zip', () => {
    const dir = makeTempDir();
    try {
      const fixture = createValidTraceZip(dir);
      const run = runFinalizer({ dir, mode: 'fork-late-write', fixture });

      assert.equal(run.status, 20, run.stderr);
      assert.ok(fs.existsSync(run.descendantPidFile), 'stub must record its forked child');
      const descendantPid = Number.parseInt(
        fs.readFileSync(run.descendantPidFile, 'utf8').trim(),
        10
      );

      spawnSync('sleep', ['5']);

      assert.equal(
        fs.existsSync(run.tracePath),
        false,
        'no descendant may recreate the valid trace path after finalization'
      );
      assert.throws(
        () => process.kill(descendantPid, 0),
        /ESRCH/,
        'forked descendant must be terminated and reaped'
      );
    } finally {
      fs.rmSync(dir, { recursive: true, force: true });
    }
  });

  test('external termination kills the active process group before signal cleanup returns', async () => {
    const dir = makeTempDir();
    try {
      const fixture = createValidTraceZip(dir);
      const tracePath = path.join(dir, 'trace.zip');
      const descendantPidFile = path.join(dir, 'descendant.pid');
      const stub = writeAgentBrowserStub(dir);
      const child = spawn(
        finalizer,
        [
          '--trace-path', tracePath,
          '--flow-verdict', 'PASS',
          '--trace-producer', 'agent-browser',
          '--trace-producer-version', 'test',
          '--trace-format', 'playwright-trace-zip',
          '--timeout', '10',
          '--recovery-timeout', '1',
          '--result-file', path.join(dir, 'trace-finalization.env'),
        ],
        {
          env: {
            ...process.env,
            AGENT_BROWSER_BIN: stub,
            DESCENDANT_PID_FILE: descendantPidFile,
            RECOVERY_MARKER: path.join(dir, 'recovery-reached'),
            TRACE_FIXTURE: fixture,
            TRACE_STUB_MODE: 'fork-late-write',
          },
          stdio: 'ignore',
        }
      );

      for (let attempt = 0; attempt < 50 && !fs.existsSync(descendantPidFile); attempt++) {
        spawnSync('sleep', ['0.1']);
      }
      assert.ok(fs.existsSync(descendantPidFile), 'stub must record its forked child');

      child.kill('SIGTERM');
      const close = await new Promise((resolve) => {
        child.once('close', (code, signal) => resolve({ code, signal }));
      });
      assert.deepEqual(close, { code: 130, signal: null });

      const descendantPid = Number.parseInt(
        fs.readFileSync(descendantPidFile, 'utf8').trim(),
        10
      );
      spawnSync('sleep', ['5']);
      assert.equal(
        fs.existsSync(tracePath),
        false,
        'signal cleanup must prevent a descendant from recreating trace.zip'
      );
      assert.throws(() => process.kill(descendantPid, 0), /ESRCH/);
    } finally {
      fs.rmSync(dir, { recursive: true, force: true });
    }
  });

  test('exit-zero truncated ZIP is rejected and quarantined under an invalid name', () => {
    const dir = makeTempDir();
    try {
      const run = runFinalizer({ dir, mode: 'truncated' });

      assert.equal(run.status, 22, run.stderr);
      const result = parseResultFile(run.resultPath);
      assert.equal(result.stop_status, 'completed');
      assert.equal(result.validation_status, 'invalid_zip');
      assert.equal(result.analysis_eligible, 'false');
      assert.equal(result.artifact_disposition, 'quarantined');
      assert.match(path.basename(result.artifact_path), /^trace\.invalid-invalid_zip-/);
      assert.ok(fs.existsSync(result.artifact_path), 'invalid artifact must be retained');
      assert.equal(fs.existsSync(run.tracePath), false, 'invalid artifact must not keep valid name');
    } finally {
      fs.rmSync(dir, { recursive: true, force: true });
    }
  });

  test('non-regular trace artifacts retain a reportable status across all consumers', () => {
    const dir = makeTempDir();
    try {
      const run = runFinalizer({ dir, mode: 'directory' });

      assert.equal(run.status, 22, run.stderr);
      const result = parseResultFile(run.resultPath);
      assert.equal(result.validation_status, 'not_regular');
      assert.equal(result.analysis_eligible, 'false');
      assert.equal(result.artifact_disposition, 'retained_invalid');

      for (const relativePath of [
        'agents/e2e-test-runner.md',
        'agents/e2e-flow-verifier.md',
        'references/common-patterns.md',
      ]) {
        const consumer = fs.readFileSync(path.join(pluginRoot, relativePath), 'utf8');
        assert.match(
          consumer,
          /validation_status[^.\n]*not_regular/,
          `${relativePath} must recognize not_regular`
        );
      }
    } finally {
      fs.rmSync(dir, { recursive: true, force: true });
    }
  });

  test('valid ZIP with Playwright trace content is accepted for analysis', () => {
    const dir = makeTempDir();
    try {
      const fixture = createValidTraceZip(dir);
      const run = runFinalizer({ dir, mode: 'valid', fixture, flowVerdict: 'FAIL' });

      assert.equal(run.status, 0, run.stderr);
      const result = parseResultFile(run.resultPath);
      assert.equal(result.flow_verdict, 'FAIL');
      assert.equal(result.infrastructure_result, 'PASS');
      assert.equal(result.stop_status, 'completed');
      assert.equal(result.validation_status, 'valid');
      assert.equal(result.recovery_status, 'not_needed');
      assert.equal(result.artifact_disposition, 'accepted');
      assert.equal(result.analysis_eligible, 'true');
      assert.equal(result.artifact_path, run.tracePath);
      assert.equal(result.producer, 'agent-browser');
      assert.equal(result.producer_version, 'test');
      assert.equal(result.declared_format, 'playwright-trace-zip');
      assert.equal(result.detected_format, 'playwright-trace-zip');
      assert.equal(result.validator, 'validate-trace-archive.py');
    } finally {
      fs.rmSync(dir, { recursive: true, force: true });
    }
  });

  test('real Chrome trace JSON is validated without entering the Playwright ZIP path', () => {
    const dir = makeTempDir();
    try {
      const archiveMarker = path.join(dir, 'archive-validator-called');
      const markerValidator = writeMarkerArchiveValidator(dir, archiveMarker);
      const run = runFinalizer({
        dir,
        mode: 'valid',
        fixture: chromeTraceFixture,
        traceFormat: 'chrome-trace-json',
        archiveValidator: markerValidator,
      });

      assert.equal(run.status, 0, run.stderr);
      const result = parseResultFile(run.resultPath);
      assert.equal(result.flow_verdict, 'PASS');
      assert.equal(result.infrastructure_result, 'PASS');
      assert.equal(result.finalization_status, 'valid');
      assert.equal(result.validation_status, 'valid');
      assert.equal(result.declared_format, 'chrome-trace-json');
      assert.equal(result.detected_format, 'chrome-trace-json');
      assert.equal(result.validator, 'validate-chrome-trace.py');
      assert.equal(result.analysis_eligible, 'true');
      assert.equal(path.extname(result.artifact_path), '.json');
      assert.equal(fs.existsSync(archiveMarker), false);
    } finally {
      fs.rmSync(dir, { recursive: true, force: true });
    }
  });

  test('Chrome JSON declared as Playwright is quarantined before ZIP validation', () => {
    const dir = makeTempDir();
    try {
      const archiveMarker = path.join(dir, 'archive-validator-called');
      const markerValidator = writeMarkerArchiveValidator(dir, archiveMarker);
      const run = runFinalizer({
        dir,
        mode: 'valid',
        fixture: chromeTraceFixture,
        traceFormat: 'playwright-trace-zip',
        archiveValidator: markerValidator,
      });

      assert.equal(run.status, 23, run.stderr);
      const result = parseResultFile(run.resultPath);
      assert.equal(result.flow_verdict, 'PASS');
      assert.equal(result.infrastructure_result, 'FAIL');
      assert.equal(result.finalization_status, 'format_mismatch');
      assert.equal(result.validation_status, 'format_mismatch');
      assert.equal(result.declared_format, 'playwright-trace-zip');
      assert.equal(result.detected_format, 'chrome-trace-json');
      assert.equal(result.validator, 'not_run');
      assert.equal(result.analysis_eligible, 'false');
      assert.equal(fs.existsSync(archiveMarker), false);
    } finally {
      fs.rmSync(dir, { recursive: true, force: true });
    }
  });

  test('declared format and output extension mismatch fails before trace stop', () => {
    const dir = makeTempDir();
    try {
      const run = runFinalizer({
        dir,
        mode: 'valid',
        fixture: chromeTraceFixture,
        traceFormat: 'chrome-trace-json',
        tracePath: path.join(dir, 'trace.zip'),
      });

      assert.equal(run.status, 23, run.stderr);
      const result = parseResultFile(run.resultPath);
      assert.equal(result.flow_verdict, 'PASS');
      assert.equal(result.finalization_status, 'format_mismatch');
      assert.equal(result.stop_status, 'not_run');
      assert.equal(result.validation_status, 'format_mismatch');
      assert.equal(result.declared_format, 'chrome-trace-json');
      assert.equal(result.detected_format, 'not_run');
      assert.equal(result.analysis_eligible, 'false');
      const browserCalls = fs.existsSync(run.agentBrowserLog)
        ? fs.readFileSync(run.agentBrowserLog, 'utf8')
        : '';
      assert.doesNotMatch(browserCalls, /trace stop/);
    } finally {
      fs.rmSync(dir, { recursive: true, force: true });
    }
  });

  test('archive validation timeout kills its process group and still persists a result', () => {
    const dir = makeTempDir();
    try {
      const fixture = createValidTraceZip(dir);
      const validator = writeHangingArchiveValidator(dir);
      const lateMarker = path.join(dir, 'validator-late-write');
      const run = runFinalizer({
        dir,
        mode: 'valid',
        fixture,
        archiveValidator: validator,
        validationTimeout: '1',
        validatorLateMarker: lateMarker,
      });

      assert.equal(run.status, 22, run.stderr);
      assert.ok(run.elapsedMs < 12000, `finalizer took ${run.elapsedMs}ms`);
      const result = parseResultFile(run.resultPath);
      assert.equal(result.flow_verdict, 'PASS');
      assert.equal(result.infrastructure_result, 'FAIL');
      assert.equal(result.validation_status, 'timeout');
      assert.equal(result.finalization_status, 'invalid_artifact');
      assert.equal(result.analysis_eligible, 'false');
      assert.match(path.basename(result.artifact_path), /^trace\.invalid-timeout-/);

      spawnSync('sleep', ['5']);
      assert.equal(
        fs.existsSync(lateMarker),
        false,
        'validation watchdog must kill TERM-ignoring descendants'
      );
    } finally {
      fs.rmSync(dir, { recursive: true, force: true });
    }
  });

  test('archive metadata limits reject zip bombs before CRC/full-read validation', () => {
    const dir = makeTempDir();
    try {
      const fixture = createResourceLimitTraceZip(dir);
      const corruptFixture = createResourceLimitTraceZip(dir, true);
      const cases = [
        {
          name: 'entry count',
          archive: fixture,
          env: { E2E_TRACE_MAX_ENTRIES: '2' },
          pattern: /max_entries/,
        },
        {
          name: 'total uncompressed bytes',
          archive: fixture,
          env: { E2E_TRACE_MAX_TOTAL_UNCOMPRESSED_BYTES: '1024' },
          pattern: /max_total_uncompressed_bytes/,
        },
        {
          name: 'per-entry uncompressed bytes',
          archive: fixture,
          env: { E2E_TRACE_MAX_ENTRY_UNCOMPRESSED_BYTES: '1024' },
          pattern: /max_entry_uncompressed_bytes/,
        },
        {
          name: 'compression ratio before corrupt payload read',
          archive: corruptFixture,
          env: { E2E_TRACE_MAX_COMPRESSION_RATIO: '2' },
          pattern: /max_compression_ratio/,
        },
      ];

      for (const limitCase of cases) {
        const validation = spawnSync(
          'python3',
          [archiveValidator, 'validate', limitCase.archive],
          {
            encoding: 'utf8',
            env: { ...process.env, ...limitCase.env },
          }
        );
        assert.equal(validation.status, 6, `${limitCase.name}: ${validation.stderr}`);
        assert.match(validation.stderr, /^archive_limit_exceeded:/);
        assert.match(validation.stderr, limitCase.pattern);
      }

      const defaultValidation = spawnSync(
        'python3',
        [archiveValidator, 'validate', fixture],
        { encoding: 'utf8' }
      );
      assert.equal(defaultValidation.status, 0, defaultValidation.stderr);

      const finalizerRun = runFinalizer({
        dir,
        mode: 'valid',
        fixture,
        tracePath: path.join(dir, 'limited-trace.zip'),
        resultPath: path.join(dir, 'limited-finalization.env'),
        extraEnv: { E2E_TRACE_MAX_ENTRIES: '2' },
      });
      assert.equal(finalizerRun.status, 22, finalizerRun.stderr);
      const finalizerResult = parseResultFile(finalizerRun.resultPath);
      assert.equal(finalizerResult.validation_status, 'resource_limit_exceeded');
      assert.equal(finalizerResult.infrastructure_result, 'FAIL');
      assert.equal(finalizerResult.analysis_eligible, 'false');
      assert.match(
        path.basename(finalizerResult.artifact_path),
        /^limited-trace\.invalid-resource_limit_exceeded-/
      );

      const commonPatterns = fs.readFileSync(
        path.join(pluginRoot, 'references/common-patterns.md'),
        'utf8'
      );
      for (const setting of [
        'E2E_TRACE_VALIDATION_TIMEOUT',
        'E2E_TRACE_MAX_ENTRIES',
        'E2E_TRACE_MAX_TOTAL_UNCOMPRESSED_BYTES',
        'E2E_TRACE_MAX_ENTRY_UNCOMPRESSED_BYTES',
        'E2E_TRACE_MAX_COMPRESSION_RATIO',
      ]) {
        assert.match(commonPatterns, new RegExp(setting));
      }
      for (const relativePath of [
        'agents/e2e-test-runner.md',
        'agents/e2e-flow-verifier.md',
        'references/common-patterns.md',
      ]) {
        const reportContract = fs.readFileSync(
          path.join(pluginRoot, relativePath),
          'utf8'
        );
        assert.match(reportContract, /validation_status[\s\S]*timeout/);
        assert.match(
          reportContract,
          /validation_status[\s\S]*resource_limit_exceeded/
        );
      }
    } finally {
      fs.rmSync(dir, { recursive: true, force: true });
    }
  });

  test('valid ZIP without Playwright trace entries is rejected', () => {
    const dir = makeTempDir();
    try {
      const fixture = createUnrelatedZip(dir);
      const run = runFinalizer({ dir, mode: 'valid', fixture });

      assert.equal(run.status, 22, run.stderr);
      const result = parseResultFile(run.resultPath);
      assert.equal(result.validation_status, 'missing_playwright_content');
      assert.equal(result.analysis_eligible, 'false');
      assert.equal(result.artifact_disposition, 'quarantined');
      assert.match(
        path.basename(result.artifact_path),
        /^trace\.invalid-missing_playwright_content-/
      );

      const analyzer = fs.readFileSync(
        path.join(pluginRoot, 'agents/e2e-trace-analyzer.md'),
        'utf8'
      );
      assert.ok(
        analyzer.includes('validate-trace-archive.py') &&
          analyzer.includes('python3 "$TRACE_ARCHIVE_TOOL" extract'),
        'analyzer must use the shared validator and safe materializer'
      );
      assert.doesNotMatch(
        analyzer,
        /^\s*unzip -o/m,
        'analyzer must not execute whole-archive extraction'
      );
    } finally {
      fs.rmSync(dir, { recursive: true, force: true });
    }
  });

  test('nested-only Playwright entries are rejected by the root-level analyzer contract', () => {
    const dir = makeTempDir();
    try {
      const fixture = createNestedTraceZip(dir);
      const run = runFinalizer({ dir, mode: 'valid', fixture });

      assert.equal(run.status, 22, run.stderr);
      const result = parseResultFile(run.resultPath);
      assert.equal(result.validation_status, 'missing_playwright_content');
      assert.equal(result.analysis_eligible, 'false');
      assert.equal(result.artifact_disposition, 'quarantined');
      assert.match(
        path.basename(result.artifact_path),
        /^trace\.invalid-missing_playwright_content-/
      );
    } finally {
      fs.rmSync(dir, { recursive: true, force: true });
    }
  });

  test('ZIPs with unsafe entry names or types are rejected before analysis', () => {
    for (const kind of ['symlink', 'traversal', 'fifo']) {
      const dir = makeTempDir();
      try {
        const fixture = createUnsafeTraceZip(dir, kind);
        const run = runFinalizer({ dir, mode: 'valid', fixture });

        assert.equal(run.status, 22, `${kind}: ${run.stderr}`);
        const result = parseResultFile(run.resultPath);
        assert.equal(result.validation_status, 'unsafe_archive', kind);
        assert.equal(result.analysis_eligible, 'false', kind);
        assert.equal(result.artifact_disposition, 'quarantined', kind);
      } finally {
        fs.rmSync(dir, { recursive: true, force: true });
      }
    }
  });

  test('safe extractor materializes only expected regular trace data into a fresh directory', () => {
    const dir = makeTempDir();
    try {
      const fixture = createValidTraceZip(dir);
      const destination = path.join(dir, 'materialized');
      const extracted = spawnSync(
        'python3',
        [archiveValidator, 'extract', fixture, destination],
        { encoding: 'utf8' }
      );

      assert.equal(extracted.status, 0, extracted.stderr);
      assert.ok(fs.statSync(path.join(destination, 'trace.trace')).isFile());
      assert.ok(fs.statSync(path.join(destination, 'resources', 'sha1.dat')).isFile());
      assert.equal(fs.existsSync(path.join(destination, 'ignored-metadata.txt')), false);

      const unsafeFixture = createUnsafeTraceZip(dir, 'symlink');
      const unsafeDestination = path.join(dir, 'unsafe-materialized');
      const rejected = spawnSync(
        'python3',
        [archiveValidator, 'extract', unsafeFixture, unsafeDestination],
        { encoding: 'utf8' }
      );
      assert.equal(rejected.status, 3, rejected.stderr);
      assert.equal(fs.existsSync(unsafeDestination), false);
    } finally {
      fs.rmSync(dir, { recursive: true, force: true });
    }
  });

  test('analyzer resourceSha and bodySha lookups cannot escape extracted resources', () => {
    const dir = makeTempDir();
    try {
      const materialized = path.join(dir, 'materialized');
      const resources = path.join(materialized, 'resources');
      fs.mkdirSync(resources, { recursive: true });
      fs.writeFileSync(path.join(dir, 'host-secret.txt'), 'must not be readable');

      for (const field of ['resourceSha', 'bodySha']) {
        const maliciousNetworkEntry = {
          response: { status: 500, [field]: '../../host-secret.txt' },
        };
        const maliciousId = maliciousNetworkEntry.response[field];
        const rejected = spawnSync(
          'python3',
          [archiveValidator, 'resource-path', materialized, maliciousId],
          { encoding: 'utf8' }
        );
        assert.equal(rejected.status, 3, `${field}: ${rejected.stderr}`);
        assert.equal(rejected.stdout, '', field);

        const validId = field === 'resourceSha' ? 'a'.repeat(40) : 'b'.repeat(40);
        const validPath = path.join(resources, validId);
        fs.writeFileSync(validPath, `${field} body`);
        const accepted = spawnSync(
          'python3',
          [archiveValidator, 'resource-path', materialized, validId],
          { encoding: 'utf8' }
        );
        assert.equal(accepted.status, 0, `${field}: ${accepted.stderr}`);
        assert.equal(accepted.stdout.trim(), fs.realpathSync(validPath), field);
      }

      const analyzer = fs.readFileSync(
        path.join(pluginRoot, 'agents/e2e-trace-analyzer.md'),
        'utf8'
      );
      assert.match(
        analyzer,
        /resource-path "\$TRACE_MATERIALIZED_DIR" "\$sha"/
      );
      assert.match(analyzer, /exactly 40 lowercase hexadecimal characters/);
      assert.doesNotMatch(
        analyzer,
        /^TMPDIR=/m,
        'analyzer must not repurpose the process-wide TMPDIR environment variable'
      );
      assert.match(
        analyzer,
        /rm -rf "\$TRACE_WORK_DIR"/,
        'analyzer must clean the complete temporary work directory'
      );
    } finally {
      fs.rmSync(dir, { recursive: true, force: true });
    }
  });

  test('result contract rejects newline injection and unknown flow verdicts before trace stop', () => {
    const cases = [
      {
        name: 'flow verdict newline',
        flowVerdict: 'PASS\nanalysis_eligible=true',
      },
      {
        name: 'trace path newline',
        tracePathSuffix: 'trace.zip\nanalysis_eligible=true',
      },
      {
        name: 'trace producer newline',
        traceProducer: 'agent-browser\nanalysis_eligible=true',
      },
      {
        name: 'trace producer version newline',
        traceProducerVersion: '0.32.0\nanalysis_eligible=true',
      },
      {
        name: 'unknown verdict',
        flowVerdict: 'UNKNOWN',
      },
    ];

    for (const testCase of cases) {
      const dir = makeTempDir();
      try {
        const fixture = createValidTraceZip(dir);
        const resultPath = path.join(dir, 'trace-finalization.env');
        const run = runFinalizer({
          dir,
          mode: 'valid',
          fixture,
          flowVerdict: testCase.flowVerdict,
          traceProducer: testCase.traceProducer,
          traceProducerVersion: testCase.traceProducerVersion,
          tracePath: testCase.tracePathSuffix
            ? path.join(dir, testCase.tracePathSuffix)
            : undefined,
          resultPath,
        });

        assert.equal(run.status, 64, `${testCase.name}: ${run.stderr}`);
        assert.equal(
          fs.existsSync(resultPath),
          false,
          `${testCase.name}: invalid input must not emit a result contract`
        );
        assert.equal(
          fs.existsSync(run.agentBrowserLog),
          false,
          `${testCase.name}: invalid input must fail before trace stop`
        );
      } finally {
        fs.rmSync(dir, { recursive: true, force: true });
      }
    }
  });

  test('finalizer rejects directory and FIFO result destinations before trace stop', () => {
    for (const kind of ['directory', 'fifo']) {
      const dir = makeTempDir();
      try {
        const fixture = createValidTraceZip(dir);
        const resultPath = path.join(dir, 'trace-finalization.env');
        if (kind === 'directory') {
          fs.mkdirSync(resultPath);
        } else {
          execFileSync('mkfifo', [resultPath]);
        }

        const run = runFinalizer({
          dir,
          mode: 'valid',
          fixture,
          resultPath,
        });
        assert.equal(run.status, 64, `${kind}: ${run.stderr}`);
        assert.equal(
          fs.existsSync(run.agentBrowserLog),
          false,
          `${kind}: trace stop must not run for an invalid result destination`
        );
        assert.equal(fs.statSync(resultPath).isFile(), false, kind);
      } finally {
        fs.rmSync(dir, { recursive: true, force: true });
      }
    }
  });

  test('missing Python fails before workdir allocation with a deterministic result contract', () => {
    const dir = makeTempDir();
    try {
      const isolatedTmp = path.join(dir, 'tmp');
      fs.mkdirSync(isolatedTmp);
      const resultPath = path.join(dir, 'trace-finalization.env');
      const agentBrowserLog = path.join(dir, 'agent-browser.log');
      const run = spawnSync(
        finalizer,
        [
          '--trace-path', path.join(dir, 'trace.zip'),
          '--flow-verdict', 'PASS',
          '--trace-producer', 'agent-browser',
          '--trace-producer-version', 'test',
          '--trace-format', 'playwright-trace-zip',
          '--result-file', resultPath,
        ],
        {
          encoding: 'utf8',
          env: {
            ...process.env,
            PATH: writePathWithoutPython(dir),
            TMPDIR: isolatedTmp,
            AGENT_BROWSER_BIN: writeAgentBrowserStub(dir),
            AGENT_BROWSER_LOG: agentBrowserLog,
          },
        }
      );

      assert.equal(run.status, 69, run.stderr || run.error?.message);
      assert.equal(fs.existsSync(agentBrowserLog), false);
      assert.deepEqual(
        fs.readdirSync(isolatedTmp).filter((entry) =>
          entry.startsWith('e2e-trace-finalize.')
        ),
        [],
        'dependency failure must not leak a finalizer work directory'
      );
      const result = parseResultFile(resultPath);
      assert.equal(result.producer, 'agent-browser');
      assert.equal(result.producer_version, 'test');
      assert.equal(result.declared_format, 'playwright-trace-zip');
      assert.equal(result.detected_format, 'not_run');
      assert.equal(result.validator, 'not_run');
      assert.equal(result.infrastructure_result, 'FAIL');
      assert.equal(result.finalization_status, 'dependency_missing');
      assert.equal(result.stop_status, 'not_run');
      assert.equal(result.validation_status, 'not_run');
      assert.equal(result.analysis_eligible, 'false');
      assert.equal(result.dependency_status, 'missing_python3');

      const teamsRun = spawnSync(
        teamTraceLifecycle,
        [
          'begin',
          '--report-dir', path.join(dir, 'teams-report'),
          '--flow-run-id', 'run-1',
          '--session', 'admin-panel',
        ],
        {
          encoding: 'utf8',
          env: {
            ...process.env,
            PATH: path.join(dir, 'bin-without-python'),
            TMPDIR: isolatedTmp,
            AGENT_BROWSER_BIN: writeAgentBrowserStub(dir),
            AGENT_BROWSER_LOG: agentBrowserLog,
          },
        }
      );
      assert.equal(teamsRun.status, 69, teamsRun.stderr);
      assert.equal(fs.existsSync(agentBrowserLog), false);

      for (const relativePath of [
        'references/commands.md',
        'skills/e2e-test/SKILL.md',
        'agents/e2e-test-runner.md',
        'skills/e2e-walkthrough/SKILL.md',
        'agents/e2e-flow-verifier.md',
      ]) {
        const content = fs.readFileSync(path.join(pluginRoot, relativePath), 'utf8');
        assert.match(
          content,
          /python3[\s\S]{0,240}(?:before|prior to)[\s\S]{0,120}trac/i,
          `${relativePath} must require Python before tracing`
        );
        assert.match(
          content,
          /trace-finalization\.env[\s\S]{0,120}(?:missing|absent)[\s\S]{0,180}infrastructure/i,
          `${relativePath} must fail closed when the result contract is absent`
        );
      }
    } finally {
      fs.rmSync(dir, { recursive: true, force: true });
    }
  });

  test('unsafe trace session identifiers fail before agent-browser invocation', () => {
    for (const session of ['../escape', 'two words', '*', 'line\nbreak']) {
      const dir = makeTempDir();
      try {
        const fixture = createValidTraceZip(dir);
        const run = runFinalizer({ dir, mode: 'valid', fixture, session });

        assert.equal(run.status, 64, `${JSON.stringify(session)}: ${run.stderr}`);
        assert.equal(
          fs.existsSync(run.agentBrowserLog),
          false,
          `${JSON.stringify(session)} must fail before trace stop`
        );
      } finally {
        fs.rmSync(dir, { recursive: true, force: true });
      }
    }
  });

  test('central identifier validator rejects unsafe values and normalization collisions', () => {
    const valid = spawnSync(
      identifierValidator,
      ['admin-panel', 'customer_portal', 'site.2'],
      { encoding: 'utf8' }
    );
    assert.equal(valid.status, 0, valid.stderr || valid.error?.message);

    for (const unsafe of ['../escape', 'two words', '*', 'line\nbreak', '.hidden']) {
      const rejected = spawnSync(identifierValidator, [unsafe], { encoding: 'utf8' });
      assert.equal(rejected.status, 64, `${JSON.stringify(unsafe)}: ${rejected.stderr}`);
    }

    for (const collision of [
      ['Admin', 'admin'],
      ['foo-bar', 'foo_bar'],
      ['foo.bar', 'foo_bar'],
    ]) {
      const rejected = spawnSync(identifierValidator, collision, { encoding: 'utf8' });
      assert.equal(rejected.status, 65, `${collision.join(', ')}: ${rejected.stderr}`);
    }
  });

  test('multi-site producers validate identifiers centrally and iterate arrays without splitting', () => {
    const walkthrough = fs.readFileSync(
      path.join(pluginRoot, 'skills/e2e-walkthrough/reference.md'),
      'utf8'
    );
    const testSkill = fs.readFileSync(
      path.join(pluginRoot, 'skills/e2e-test/SKILL.md'),
      'utf8'
    );

    for (const [name, content] of [
      ['walkthrough', walkthrough],
      ['e2e-test', testSkill],
    ]) {
      assert.match(content, /validate-trace-identifiers\.sh/, `${name}: central validation`);
    }
    assert.match(
      walkthrough,
      /for APP in "\$\{TRACE_STARTED_APPS\[@\]\}"/,
      'walkthrough must preserve each validated app as one array element'
    );
    assert.doesNotMatch(
      walkthrough,
      /for APP in \$TRACE_STARTED_APPS/,
      'walkthrough must not split or glob app identifiers'
    );
  });

  test('Teams lifecycle gives two sequential flows fresh traces and replays duplicates', () => {
    const dir = makeTempDir();
    try {
      const reportDir = path.join(dir, 'runner-admin');
      const fixture = chromeTraceFixture;
      const stub = writeAgentBrowserStub(dir);
      const agentBrowserLog = path.join(dir, 'agent-browser.log');
      const env = {
        ...process.env,
        AGENT_BROWSER_BIN: stub,
        AGENT_BROWSER_LOG: agentBrowserLog,
        RECOVERY_MARKER: path.join(dir, 'recovery-reached'),
        TRACE_FIXTURE: fixture,
        TRACE_STUB_MODE: 'valid',
      };
      const invoke = (command, runId, verdict) => {
        const args = [
          command,
          '--report-dir', reportDir,
          '--flow-run-id', runId,
          '--session', 'admin-panel',
        ];
        if (verdict) args.push('--flow-verdict', verdict);
        return spawnSync(teamTraceLifecycle, args, { encoding: 'utf8', env });
      };

      const beginOne = invoke('begin', 'run-1');
      assert.equal(beginOne.status, 0, beginOne.stderr || beginOne.error?.message);
      assert.match(beginOne.stdout, /trace_format=chrome-trace-json/);
      assert.match(beginOne.stdout, /trace_producer=agent-browser/);
      assert.match(beginOne.stdout, /trace_producer_version=0\.32\.0/);
      assert.match(beginOne.stdout, /trace_path=.*\/trace\.json/);
      const duplicateBeginOne = invoke('begin', 'run-1');
      assert.equal(duplicateBeginOne.status, 0, duplicateBeginOne.stderr);
      const finalizeOne = invoke('finalize', 'run-1', 'PASS');
      assert.equal(finalizeOne.status, 0, finalizeOne.stderr);
      const duplicateFinalizeOne = invoke('finalize', 'run-1', 'PASS');
      assert.equal(duplicateFinalizeOne.status, 0, duplicateFinalizeOne.stderr);
      assert.equal(duplicateFinalizeOne.stdout, finalizeOne.stdout);

      const beginTwo = invoke('begin', 'run-2');
      assert.equal(beginTwo.status, 0, beginTwo.stderr);
      const finalizeTwo = invoke('finalize', 'run-2', 'FAIL');
      assert.equal(finalizeTwo.status, 0, finalizeTwo.stderr);

      const logLines = fs.readFileSync(agentBrowserLog, 'utf8').trim().split('\n');
      assert.ok(
        logLines.indexOf('trace --help') < logLines.findIndex((line) =>
          line.includes(' trace start')
        ),
        'capability detection must finish before trace start'
      );
      assert.equal(logLines.filter((line) => line.includes(' trace start')).length, 2);
      assert.equal(logLines.filter((line) => line.includes(' trace stop ')).length, 2);
      for (const runId of ['run-1', 'run-2']) {
        const resultPath = path.join(
          reportDir,
          'runs',
          runId,
          'trace-finalization.env'
        );
        assert.ok(
          fs.existsSync(resultPath),
          `${runId} must have its own finalization result`
        );
        const result = parseResultFile(resultPath);
        assert.equal(result.producer, 'agent-browser');
        assert.equal(result.producer_version, '0.32.0');
        assert.equal(result.declared_format, 'chrome-trace-json');
        assert.equal(result.detected_format, 'chrome-trace-json');
        assert.equal(result.validator, 'validate-chrome-trace.py');
      }
    } finally {
      fs.rmSync(dir, { recursive: true, force: true });
    }
  });

  test('Teams lifecycle routes trace start and finalization through the owned browser runtime', () => {
    const dir = makeTempDir();
    try {
      const reportDir = path.join(dir, 'runner-admin');
      const fixture = chromeTraceFixture;
      const agentStub = writeAgentBrowserStub(dir);
      const runtime = writeBrowserRuntimeStub(dir);
      const runtimeLog = path.join(dir, 'browser-runtime.log');
      const commonArgs = [
        '--report-dir', reportDir,
        '--flow-run-id', 'flow-run-1',
        '--session', 'admin-panel',
        '--browser-runtime', runtime,
        '--browser-run-id', 'browser-run-123',
        '--app', 'admin-panel',
      ];
      const env = {
        ...process.env,
        AGENT_BROWSER_BIN: agentStub,
        AGENT_BROWSER_UNDERLYING: agentStub,
        BROWSER_RUNTIME_LOG: runtimeLog,
        EXPECTED_BROWSER_APP: 'admin-panel',
        EXPECTED_BROWSER_RUN_ID: 'browser-run-123',
        RECOVERY_MARKER: path.join(dir, 'recovery-reached'),
        TRACE_FIXTURE: fixture,
        TRACE_STUB_MODE: 'valid',
      };

      const begin = spawnSync(teamTraceLifecycle, ['begin', ...commonArgs], {
        encoding: 'utf8',
        env,
      });
      assert.equal(begin.status, 0, begin.stderr || begin.error?.message);
      const finalize = spawnSync(
        teamTraceLifecycle,
        ['finalize', ...commonArgs, '--flow-verdict', 'PASS'],
        { encoding: 'utf8', env }
      );
      assert.equal(finalize.status, 0, finalize.stderr || finalize.error?.message);

      const runtimeInvocations = fs.readFileSync(runtimeLog, 'utf8');
      assert.match(
        runtimeInvocations,
        /<--run-id>\n<browser-run-123>\n<--app>\n<admin-panel>\n<trace>\n<start>/
      );
      assert.match(
        runtimeInvocations,
        /<--run-id>\n<browser-run-123>\n<--app>\n<admin-panel>\n<trace>\n<stop>/
      );
      assert.doesNotMatch(runtimeInvocations, /<--session>/);
    } finally {
      fs.rmSync(dir, { recursive: true, force: true });
    }
  });

  test('Teams lifecycle rejects browser ownership drift between begin and finalize', () => {
    const dir = makeTempDir();
    try {
      const reportDir = path.join(dir, 'runner-admin');
      const fixture = chromeTraceFixture;
      const agentStub = writeAgentBrowserStub(dir);
      const runtime = writeBrowserRuntimeStub(dir);
      const runtimeLog = path.join(dir, 'browser-runtime.log');
      const baseArgs = [
        '--report-dir', reportDir,
        '--flow-run-id', 'flow-run-1',
        '--session', 'admin-panel',
        '--browser-runtime', runtime,
        '--app', 'admin-panel',
      ];
      const baseEnv = {
        ...process.env,
        AGENT_BROWSER_BIN: agentStub,
        AGENT_BROWSER_UNDERLYING: agentStub,
        BROWSER_RUNTIME_LOG: runtimeLog,
        EXPECTED_BROWSER_APP: 'admin-panel',
        RECOVERY_MARKER: path.join(dir, 'recovery-reached'),
        TRACE_FIXTURE: fixture,
        TRACE_STUB_MODE: 'valid',
      };
      const begin = spawnSync(
        teamTraceLifecycle,
        ['begin', ...baseArgs, '--browser-run-id', 'browser-run-a'],
        {
          encoding: 'utf8',
          env: { ...baseEnv, EXPECTED_BROWSER_RUN_ID: 'browser-run-a' },
        }
      );
      assert.equal(begin.status, 0, begin.stderr || begin.error?.message);
      const logBeforeFinalize = fs.readFileSync(runtimeLog, 'utf8');

      const finalize = spawnSync(
        teamTraceLifecycle,
        [
          'finalize',
          ...baseArgs,
          '--browser-run-id', 'browser-run-b',
          '--flow-verdict', 'PASS',
        ],
        {
          encoding: 'utf8',
          env: { ...baseEnv, EXPECTED_BROWSER_RUN_ID: 'browser-run-b' },
        }
      );
      assert.equal(finalize.status, 66, finalize.stderr);
      assert.match(finalize.stderr, /not the active trace|ownership/i);
      assert.equal(
        fs.readFileSync(runtimeLog, 'utf8'),
        logBeforeFinalize,
        'mismatched ownership must fail before stopping any browser trace'
      );
    } finally {
      fs.rmSync(dir, { recursive: true, force: true });
    }
  });

  test('Teams begin rejects non-regular state destinations before starting trace', () => {
    for (const kind of ['directory', 'fifo']) {
      const dir = makeTempDir();
      try {
        const reportDir = path.join(dir, 'runner-admin');
        fs.mkdirSync(reportDir);
        const statePath = path.join(reportDir, '.trace-lifecycle.env');
        if (kind === 'directory') {
          fs.mkdirSync(statePath);
        } else {
          execFileSync('mkfifo', [statePath]);
        }
        const agentBrowserLog = path.join(dir, 'agent-browser.log');
        const run = spawnSync(
          teamTraceLifecycle,
          [
            'begin',
            '--report-dir', reportDir,
            '--flow-run-id', 'run-1',
            '--session', 'admin-panel',
          ],
          {
            encoding: 'utf8',
            env: {
              ...process.env,
              AGENT_BROWSER_BIN: writeAgentBrowserStub(dir),
              AGENT_BROWSER_LOG: agentBrowserLog,
              TRACE_STUB_MODE: 'valid',
            },
          }
        );

        assert.equal(run.status, 64, `${kind}: ${run.stderr}`);
        assert.equal(fs.existsSync(agentBrowserLog), false, kind);
      } finally {
        fs.rmSync(dir, { recursive: true, force: true });
      }
    }
  });

  test('Teams begin fails closed on an unknown trace capability before capture', () => {
    const dir = makeTempDir();
    try {
      const agentBrowserLog = path.join(dir, 'agent-browser.log');
      const run = spawnSync(
        teamTraceLifecycle,
        [
          'begin',
          '--report-dir', path.join(dir, 'runner-admin'),
          '--flow-run-id', 'run-1',
          '--session', 'admin-panel',
        ],
        {
          encoding: 'utf8',
          env: {
            ...process.env,
            AGENT_BROWSER_BIN: writeAgentBrowserStub(dir),
            AGENT_BROWSER_LOG: agentBrowserLog,
            TRACE_CAPABILITY_MODE: 'unknown',
            TRACE_STUB_MODE: 'valid',
          },
        }
      );

      assert.equal(run.status, 72, run.stderr);
      const log = fs.readFileSync(agentBrowserLog, 'utf8');
      assert.match(log, /trace --help/);
      assert.doesNotMatch(log, / trace start/);
    } finally {
      fs.rmSync(dir, { recursive: true, force: true });
    }
  });

  test('Teams begin performs bounded trace cleanup when active-state persistence fails', () => {
    const dir = makeTempDir();
    try {
      const reportDir = path.join(dir, 'runner-admin');
      const statePath = path.join(reportDir, '.trace-lifecycle.env');
      const fixture = chromeTraceFixture;
      const agentBrowserLog = path.join(dir, 'agent-browser.log');
      const run = spawnSync(
        teamTraceLifecycle,
        [
          'begin',
          '--report-dir', reportDir,
          '--flow-run-id', 'run-1',
          '--session', 'admin-panel',
        ],
        {
          encoding: 'utf8',
          env: {
            ...process.env,
            AGENT_BROWSER_BIN: writeAgentBrowserStub(dir),
            AGENT_BROWSER_LOG: agentBrowserLog,
            LIFECYCLE_STATE_PATH: statePath,
            RECOVERY_MARKER: path.join(dir, 'recovery-reached'),
            TRACE_FIXTURE: fixture,
            TRACE_STUB_MODE: 'state-write-fail',
          },
        }
      );

      assert.equal(run.status, 70, run.stderr);
      assert.doesNotMatch(run.stdout, /begin_status=started/);
      const logLines = fs.readFileSync(agentBrowserLog, 'utf8').trim().split('\n');
      assert.equal(logLines.filter((line) => line.includes(' trace start')).length, 1);
      assert.equal(logLines.filter((line) => line.includes(' trace stop ')).length, 1);
      assert.ok(
        fs.existsSync(
          path.join(reportDir, 'runs', 'run-1', 'trace-finalization.env')
        )
      );
    } finally {
      fs.rmSync(dir, { recursive: true, force: true });
    }
  });

  test('Scenario C and runner protocol carry an explicit flow_run_id begin/finalize lifecycle', () => {
    const testSkill = fs.readFileSync(
      path.join(pluginRoot, 'skills/e2e-test/SKILL.md'),
      'utf8'
    );
    const runner = fs.readFileSync(
      path.join(pluginRoot, 'agents/e2e-test-runner.md'),
      'utf8'
    );
    const scenarioC = testSkill.match(
      /#### Scenario C:[\s\S]*?(?=\n#### Scenario D:)/
    )?.[0] || '';
    const beginHandler = runner.match(
      /### On receiving BEGIN_FLOW message[\s\S]*?(?=\n### On receiving )/
    )?.[0] || '';
    const finalizeHandler = runner.match(
      /### On receiving FINALIZE_FLOW message[\s\S]*?(?=\n### On receiving )/
    )?.[0] || '';

    assert.match(scenarioC, /BEGIN_FLOW[\s\S]*flow_run_id:/);
    assert.match(
      scenarioC,
      /BEGIN_FLOW[\s\S]*browser_runtime:[\s\S]*browser_run_id:/,
      'owned runtime fields must be forwarded when the orchestrator supplies them'
    );
    assert.match(
      scenarioC,
      /runs\/<flow_run_id>\/trace-finalization\.env|distinct `runs\/<flow_run_id>\/` trace and result path/,
      'Scenario C result paths must be keyed by run identity'
    );
    assert.match(
      beginHandler,
      /team-trace-lifecycle\.sh"[\s\S]*"\$TRACE_LIFECYCLE" begin/
    );
    assert.match(beginHandler, /FLOW READY\\nflow_run_id:/);
    assert.match(
      finalizeHandler,
      /team-trace-lifecycle\.sh"[\s\S]*"\$TRACE_LIFECYCLE" finalize/
    );
    assert.match(finalizeHandler, /flow_run_id:/);
  });

  test('named sessions finalize independently into distinct artifacts and result files', () => {
    const dir = makeTempDir();
    try {
      const fixture = createValidTraceZip(dir);
      const stub = writeAgentBrowserStub(dir);
      const agentBrowserLog = path.join(dir, 'agent-browser.log');
      const sites = ['admin-panel', 'customer-portal'];

      for (const site of sites) {
        const siteDir = path.join(dir, 'sites', site);
        fs.mkdirSync(siteDir, { recursive: true });
        const run = runFinalizer({
          dir,
          mode: 'valid',
          fixture,
          stub,
          session: site,
          tracePath: path.join(siteDir, 'trace.zip'),
          resultPath: path.join(siteDir, 'trace-finalization.env'),
          recoveryMarker: path.join(siteDir, 'recovery-reached'),
          agentBrowserLog,
        });

        assert.equal(run.status, 0, `${site}: ${run.stderr}`);
        const result = parseResultFile(run.resultPath);
        assert.equal(result.analysis_eligible, 'true');
        assert.equal(result.artifact_path, run.tracePath);
      }

      const log = fs.readFileSync(agentBrowserLog, 'utf8');
      for (const site of sites) {
        assert.match(
          log,
          new RegExp(`--session ${site} trace stop .*/sites/${site}/trace\\.zip`)
        );
      }
      assert.notEqual(
        path.join(dir, 'sites', sites[0], 'trace.zip'),
        path.join(dir, 'sites', sites[1], 'trace.zip')
      );
    } finally {
      fs.rmSync(dir, { recursive: true, force: true });
    }
  });

  test('multi-site walkthrough finalizes each named session and preserves single-site finalization', () => {
    for (const relativePath of [
      'skills/e2e-walkthrough/SKILL.md',
      'skills/e2e-walkthrough/reference.md',
    ]) {
      const content = fs.readFileSync(path.join(pluginRoot, relativePath), 'utf8');
      const finalizeSection = content.match(
        /(?:Finalize trace|### Finalize Trace)[\s\S]*?(?=\n(?:\d+\. |#{2,3} )[A-Z])/
      )?.[0] || '';

      assert.match(finalizeSection, /when [`"]?--sites/i, `${relativePath}: multi-site branch`);
      assert.match(finalizeSection, /--session "\$APP"/, `${relativePath}: named trace stop`);
      assert.match(
        finalizeSection,
        /\$REPORT_DIR\/sites\/\$APP\/trace\$\{trace_extension\}/,
        `${relativePath}: per-site trace path`
      );
      assert.match(
        finalizeSection,
        /\$REPORT_DIR\/sites\/\$APP\/trace-finalization\.env/,
        `${relativePath}: per-site result path`
      );
      assert.match(
        finalizeSection,
        /--trace-path "\$TRACE_PATH"/,
        `${relativePath}: single-site trace path`
      );
    }
  });

  test('Teams completion handoffs include trace finalization contract fields', () => {
    const handoffs = [
      {
        path: 'agents/e2e-test-runner.md',
        marker: 'FLOW COMPLETE',
      },
      {
        path: 'agents/e2e-flow-verifier.md',
        marker: 'VERIFICATION COMPLETE',
      },
    ];

    for (const handoff of handoffs) {
      const content = fs.readFileSync(path.join(pluginRoot, handoff.path), 'utf8');
      const message = content.match(
        new RegExp(`message="${handoff.marker}\\\\n[^"]*"`)
      )?.[0] || '';

      assert.match(
        message,
        /trace_finalization_result_path:/,
        `${handoff.path}: finalization result path`
      );
      assert.match(
        message,
        /trace_infrastructure_result:/,
        `${handoff.path}: infrastructure result`
      );
      assert.match(
        message,
        /trace_analysis_eligible:/,
        `${handoff.path}: analysis eligibility`
      );
    }
  });

  test('Agent Teams uses TRACE FINALIZED as the canonical finalization response token', () => {
    const teamsReference = fs.readFileSync(
      path.join(pluginRoot, 'references/agent-teams.md'),
      'utf8'
    );

    assert.match(teamsReference, /`TRACE FINALIZED`/);
    assert.doesNotMatch(teamsReference, /FLOW FINALIZED/);
  });

  test('Scenario C sends one explicit finalization command after step routing', () => {
    const testSkill = fs.readFileSync(
      path.join(pluginRoot, 'skills/e2e-test/SKILL.md'),
      'utf8'
    );
    const scenarioB = testSkill.match(
      /#### Scenario B:[\s\S]*?(?=\n#### Scenario C:)/
    )?.[0] || '';
    const scenarioC = testSkill.match(
      /#### Scenario C:[\s\S]*?(?=\n#### Scenario D:)/
    )?.[0] || '';
    const scenarioD = testSkill.match(
      /#### Scenario D:[\s\S]*?(?=\n#### Teams mode:)/
    )?.[0] || '';
    const traceAnalysis = testSkill.match(
      /### Phase 1\.75 — Trace Analysis[\s\S]*?(?=\n## Phase 1\.8)/
    )?.[0] || '';

    assert.match(scenarioC, /FINALIZE_FLOW/, 'Scenario C needs an end-of-flow command');
    assert.match(
      scenarioC,
      /flow_verdict: PASS\|FAIL/,
      'lead must preserve and send the application verdict'
    );
    assert.match(
      scenarioC,
      /FLOW READY[\s\S]*detected trace_path/,
      'each named runner must return its detected trace path'
    );
    assert.match(
      scenarioC,
      /FLOW READY[\s\S]*trace_finalization_result_path/,
      'each named runner must return its distinct result path'
    );
    assert.doesNotMatch(
      scenarioC,
      /message="(?:BEGIN_FLOW|FINALIZE_FLOW)[^"]*trace\.zip/,
      'the lead must not guess a trace extension before capability detection'
    );
    assert.match(
      scenarioC,
      /Wait for `TRACE FINALIZED`[\s\S]*before Phase 1\.75/,
      'trace aggregation must wait for finalization responses'
    );
    assert.match(
      scenarioC,
      /120-second response budget/,
      'finalization wait must exceed the nested stop, recovery, and validation watchdogs'
    );
    assert.doesNotMatch(
      scenarioB,
      /FINALIZE_FLOW/,
      'Scenario B EXECUTE_FLOW already finalizes and must not double-finalize'
    );
    assert.match(
      scenarioD,
      /FINALIZE_FLOW[\s\S]*browser/,
      'Scenario D must finalize its step-routed browser roles'
    );
    assert.match(
      scenarioD,
      /Never send[\s\S]*`runner-cli`/,
      'Scenario D CLI runner must not receive browser finalization'
    );
    assert.match(
      scenarioD,
      /never send it to a browser runner that already returned[\s\S]*`FLOW COMPLETE`/i,
      'Scenario D must not double-finalize full-flow browser runners'
    );
    assert.match(
      traceAnalysis,
      /independently for every `TRACE FINALIZED` response/,
      'Phase 1.75 must aggregate each named finalization before analysis'
    );
  });

  test('step-routed Teams runner handles finalization separately from STEP COMPLETE', () => {
    const runner = fs.readFileSync(
      path.join(pluginRoot, 'agents/e2e-test-runner.md'),
      'utf8'
    );
    const stepHandler = runner.match(
      /### On receiving EXECUTE_STEP message[\s\S]*?(?=\n### On receiving )/
    )?.[0] || '';
    const finalizationHandler = runner.match(
      /### On receiving FINALIZE_FLOW message[\s\S]*?(?=\n### On receiving )/
    )?.[0] || '';

    assert.doesNotMatch(
      stepHandler,
      /finalize-trace\.sh|TRACE FINALIZED/,
      'per-step completion must not finalize the persistent trace'
    );
    assert.match(
      finalizationHandler,
      /\$\{CLAUDE_PLUGIN_ROOT\}\/scripts\/team-trace-lifecycle\.sh/
    );
    assert.match(finalizationHandler, /--session "\{\{app\}\}"/);
    assert.match(finalizationHandler, /--flow-run-id "<parsed flow_run_id>"/);
    assert.match(finalizationHandler, /--flow-verdict "<parsed flow_verdict>"/);
    assert.match(finalizationHandler, /--browser-runtime "<parsed browser_runtime>"/);
    assert.match(finalizationHandler, /--browser-run-id "<parsed browser_run_id>"/);
    assert.match(finalizationHandler, /--app "\{\{app\}\}"/);
    assert.match(finalizationHandler, /message="TRACE FINALIZED\\n/);
    assert.match(finalizationHandler, /trace_finalization_result_path:/);
    assert.match(finalizationHandler, /trace_infrastructure_result:/);
    assert.match(finalizationHandler, /trace_analysis_eligible:/);
    assert.match(
      finalizationHandler,
      /duplicate[\s\S]*without another stop/i,
      'duplicate end-of-flow commands must be idempotent'
    );

    const lifecycle = fs.readFileSync(teamTraceLifecycle, 'utf8');
    assert.match(lifecycle, /finalize-trace\.sh/);
    assert.match(lifecycle, /--session "\$session_name"/);
    assert.match(lifecycle, /--trace-path "\$trace_path"/);
    assert.match(lifecycle, /--result-file "\$result_file"/);

    const teamsReference = fs.readFileSync(
      path.join(pluginRoot, 'references/agent-teams.md'),
      'utf8'
    );
    assert.match(
      teamsReference,
      /`FINALIZE_FLOW`[\s\S]*120 seconds/,
      'shared Teams timeout must allow bounded trace stop, recovery, and validation'
    );
  });

  test('all producers use the shared finalizer and e2e-test gates trace analysis', () => {
    const producers = [
      'agents/e2e-test-runner.md',
      'agents/e2e-flow-verifier.md',
      'skills/e2e-walkthrough/SKILL.md',
    ];

    for (const relativePath of producers) {
      const content = fs.readFileSync(path.join(pluginRoot, relativePath), 'utf8');
      assert.match(
        content,
        /\$\{CLAUDE_PLUGIN_ROOT\}\/scripts\/finalize-trace\.sh/,
        `${relativePath} must invoke the shared finalizer`
      );
      assert.doesNotMatch(
        content,
        /^\s*agent-browser(?: --session \S+)? trace stop(?:\s|$)/m,
        `${relativePath} must not retain a raw trace stop command`
      );
    }

    const testSkill = fs.readFileSync(
      path.join(pluginRoot, 'skills/e2e-test/SKILL.md'),
      'utf8'
    );
    assert.match(testSkill, /analysis_eligible:\s*true/);
    assert.match(testSkill, /Do NOT dispatch.*trace-analyzer/i);
  });

  test('active trace producers detect the artifact contract before capture', () => {
    const producers = [
      'agents/e2e-test-runner.md',
      'agents/e2e-flow-verifier.md',
      'skills/e2e-walkthrough/reference.md',
    ];

    for (const relativePath of producers) {
      const content = fs.readFileSync(path.join(pluginRoot, relativePath), 'utf8');
      const detectorIndex = content.indexOf('e2e-trace-contract.js');
      const startIndex = content.search(
        /^\s*(?:\{\{browser_command\}\}|<browser_command[^>]*>) trace start\s*$/m
      );
      assert.ok(detectorIndex >= 0, `${relativePath}: missing capability detector`);
      assert.ok(
        detectorIndex < startIndex,
        `${relativePath}: capability detection must precede trace start`
      );
      assert.match(
        content,
        /\$\{AGENT_BROWSER_BIN:-agent-browser\}/,
        `${relativePath}: detector must probe the runtime-selected executable`
      );
      assert.match(content, /TRACE_PATH=.*trace_extension/);
      assert.match(content, /--trace-producer "\$trace_producer"/);
      assert.match(content, /--trace-producer-version "\$trace_producer_version"/);
      assert.match(content, /--trace-format "\$trace_format"/);
      assert.doesNotMatch(
        content,
        /--trace-path "[^"]*trace\.zip"/,
        `${relativePath}: finalization must use the detected extension`
      );
    }
  });

  test('trace analyzer routes Playwright ZIP and Chrome JSON without false clean claims', () => {
    const analyzer = fs.readFileSync(
      path.join(pluginRoot, 'agents/e2e-trace-analyzer.md'),
      'utf8'
    );

    assert.match(analyzer, /`trace_format` \| \*\*Required\*\*/);
    assert.match(analyzer, /playwright-trace-zip/);
    assert.match(analyzer, /chrome-trace-json/);
    assert.match(analyzer, /validate-trace-archive\.py/);
    assert.match(analyzer, /validate-chrome-trace\.py/);
    assert.match(analyzer, /analysis_scope: performance/);
    assert.match(analyzer, /api_failures: unavailable/);
    assert.match(analyzer, /console_errors: unavailable/);
    assert.match(analyzer, /clean: unknown/);
  });

  test('every active trace-analyzer dispatch carries an explicit format', () => {
    for (const relativePath of [
      'skills/e2e-dispatch/SKILL.md',
      'skills/e2e-test/SKILL.md',
      'skills/e2e-flow/SKILL.md',
      'skills/e2e-flow/reference.md',
      'skills/e2e-walkthrough/SKILL.md',
      'skills/e2e-walkthrough/reference.md',
    ]) {
      const content = fs.readFileSync(path.join(pluginRoot, relativePath), 'utf8');
      assert.match(content, /trace_format/, `${relativePath}: trace format input`);
    }
  });

  test('persistent full-flow verification and re-runs start a fresh trace before executing steps', () => {
    const verifier = fs.readFileSync(
      path.join(pluginRoot, 'agents/e2e-flow-verifier.md'),
      'utf8'
    );
    const runner = fs.readFileSync(
      path.join(pluginRoot, 'agents/e2e-test-runner.md'),
      'utf8'
    );
    const verifyHandler = verifier.match(
      /### On receiving VERIFY_FLOW message[\s\S]*?(?=\n### On receiving |\n\*\*Stop turn)/
    )?.[0] || '';
    const rerunHandler = runner.match(
      /### On receiving RE-RUN message[\s\S]*?(?=\n### On receiving )/
    )?.[0] || '';

    assert.match(
      verifyHandler,
      /python3[\s\S]*trace start[\s\S]*Execute \*\*Round 1 only\*\*/,
      'every VERIFY_FLOW command must start a fresh trace before Round 1'
    );
    assert.match(
      rerunHandler,
      /python3[\s\S]*trace start[\s\S]*Re-execute the flow/,
      'every RE-RUN command must start a fresh trace before executing the flow'
    );
  });

  test('owned browser runtime receives trace stop and recovery as exact argv without raw session flags', () => {
    const dir = makeTempDir();
    try {
      const runtimeLog = path.join(dir, 'browser-runtime.log');
      const runtime = writeBrowserRuntimeStub(dir);
      const run = runFinalizer({
        dir,
        mode: 'hang',
        session: 'admin-panel',
        browserRuntime: runtime,
        browserRunId: 'run-123',
        browserApp: 'admin-panel',
        browserRuntimeLog: runtimeLog,
      });

      assert.equal(run.status, 20, run.stderr);
      assert.ok(fs.existsSync(run.recoveryMarker), 'owned runtime recovery must remain reachable');
      const invocations = fs
        .readFileSync(runtimeLog, 'utf8')
        .trim()
        .split('\n---\n')
        .map((entry) => entry.split('\n').filter((line) => line !== '---'));
      assert.deepEqual(invocations[0].slice(0, 5), [
        '<--run-id>',
        '<run-123>',
        '<--app>',
        '<admin-panel>',
        '<trace>',
      ]);
      assert.match(invocations[0].join('\n'), /<stop>\n<.*trace\.zip>/);
      assert.deepEqual(invocations[1], [
        '<--run-id>',
        '<run-123>',
        '<--app>',
        '<admin-panel>',
        '<close>',
      ]);
      assert.doesNotMatch(fs.readFileSync(runtimeLog, 'utf8'), /<--session>/);
    } finally {
      fs.rmSync(dir, { recursive: true, force: true });
    }
  });

  test('owned browser runtime rejects unsafe run identities before executable invocation', () => {
    const dir = makeTempDir();
    try {
      const runtimeLog = path.join(dir, 'browser-runtime.log');
      const run = runFinalizer({
        dir,
        mode: 'valid',
        fixture: createValidTraceZip(dir),
        session: 'admin-panel',
        browserRuntime: writeBrowserRuntimeStub(dir),
        browserRunId: 'run-123;echo-pwned',
        browserApp: 'admin-panel',
        browserRuntimeLog: runtimeLog,
      });

      assert.equal(run.status, 64, run.stderr);
      assert.equal(
        fs.existsSync(runtimeLog),
        false,
        'invalid ownership input must fail before invoking the runtime executable'
      );
    } finally {
      fs.rmSync(dir, { recursive: true, force: true });
    }
  });
});
