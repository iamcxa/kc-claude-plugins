'use strict';

/**
 * happy-path.test.js — one real-shaped flow, compiled and then RUN.
 *
 * WHAT CHANGED, AND WHY IT MATTERS
 *
 * This used to read the generated script and assert that selectors and assertions
 * appeared in the text. Two defect classes survived that (#180):
 *
 *   - escaping that is wrong but well-formed. `recoverSelectorText` normalised bash
 *     quoting so an assertion could name a selector as written, which also made a
 *     broken emission — `'input[type='email']'`, which bash passes as
 *     `input[type=email]` — read exactly like a correct one.
 *   - missing actions. Selectors and assertions were pinned; the `open`, `fill`,
 *     `click` and `wait` between them were not. Dropping the navigation, either
 *     wait, or the password fill left every scenario green.
 *
 * It now also executes the script against a stubbed agent-browser and asserts the
 * argv it receives. "This text appears in the source" becomes "the program passed
 * this argument", which closes both classes and makes the selector assertions exact
 * rather than normalised.
 *
 * ALSO, not INSTEAD. A first revision deleted the source assertions, and that was a
 * net loss on two shapes: the flow's two `url contains` expectations emit an
 * identical `get url`, so argv cannot tell them apart or tell one from two; and
 * assertion polarity lives in the inline judge call, not in what agent-browser
 * receives. Both are pinned in source and unreachable from argv. The two layers see
 * different things and both run.
 *
 * HOW THE STUB IS REACHED
 *
 * The compiled script defines its own `agent-browser()` shell function routing every
 * call through `node "$E2E_BROWSER_RUNTIME"`, so the seam is that variable and not
 * PATH — the issue's premise that a PATH stub alone would do was wrong. Point it at
 * `browser-runtime-shim.js` (which strips the runtime's flags and re-adds
 * `--session`) and it spawns `agent-browser` from PATH: the argv stub. Both halves
 * already existed for `runtime-state-finalizer.test.js`.
 *
 * WHAT THIS HAS AND HAS NOT EARNED
 *
 * **It has never caught an escaped defect.** Checked against the six issues in
 * sprint S2, the sprint whose "combination defects" motivated it: it would have
 * caught none of them. That made the source-reading version speculative, and the
 * argv version is still speculative about the *class*; what it is no longer
 * speculative about is whether it can see the class at all.
 *
 * If a year passes without it failing on something a unit test missed, deleting it
 * is the correct outcome, not a loss.
 *
 * WHY THESE COMBINATIONS
 *
 * Measured against a real consumer corpus (47 flows, 5 mappings), not chosen:
 *
 *   selectors  plain CSS 40% · data-testid 28% · text= 14% · role=X[name=/re/] 11%   93%
 *   actions    Click 39% · Navigate 18% · Wait 14% · Fill 11% · Verify 10%           91%
 *   expects    "visible on" 53% · "url contains" 34% · "is visible" 7% · "not" 2%    96%
 *
 * IT ASSERTS THE SCRIPT'S OWN VERDICT FIRST
 *
 * `run.status` before any argv. A first version omitted it, and the gate went green
 * on a run that exited 1 — every required call had been made, and nothing checked
 * whether the flow passed. A gate built to stop proxies standing in for outcomes had
 * made itself one.
 *
 * BOTH CLASSES ARE PROVEN CAUGHT, NOT ASSERTED
 *
 *   missing action — delete the password fill step from the flow fixture: red, on
 *     "must invoke fill input[type='password']". The source-reading version stayed
 *     green, because the selector still appeared in the login visibility expectation.
 *
 *   wrong but well-formed — emit the fill selector with naive quoting, so the line
 *     reads `agent-browser fill 'input[type='email']' …`. `bash -n` **accepts** it,
 *     and bash passes `input[type=email]` — quotes gone. Red here, on the argv.
 *     Verified by diffing the compiled output before and after, because the first
 *     attempt at this mutation was a no-op that still reported "applied".
 *
 * WHAT IT STILL CANNOT CATCH
 *
 * The stub answers; it does not render. Whether a selector matches a real element is
 * the real-browser job (#176, weekly). This proves the script asks for the right
 * things in the right order, not that the page obliges.
 *
 * A dropped `wait` also survives: waits compile to `sleep`, not to a browser call, so
 * nothing reaches the stub to be counted. #180 listed that with the other two; it is
 * the one this instrument does not close.
 *
 * WHEN A BUG IS FIXED
 *
 * Add the combination that produced it here, and say which issue it came from. The
 * first such entry is what would move this file from speculative to earned.
 */

const { test, describe } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const childProcess = require('node:child_process');

const { compile } = require('../compiler');

const FIXTURES = path.join(__dirname, 'fixtures');
const RUNTIME_SHIM = path.join(FIXTURES, 'browser-runtime-shim.js');
const ARGV_STUB = path.join(FIXTURES, 'agent-browser-argv-stub.js');

// The element the flow asserts is NOT visible. The stub must report it absent, or
// that assertion passes for the wrong reason. A substring, not the whole selector:
// the probe expression carries it JS-escaped.
const ABSENT = 'login-error';

/**
 * Every browser call the flow must make, in order, as (command, args) prefixes.
 *
 * Order matters and is asserted: a script that fills the password before the email,
 * or clicks submit before either, is wrong in a way no per-call check would see.
 * Only the calls the flow's own steps produce are listed — polling repeats `eval`,
 * `get url` and `snapshot`, so those are matched as a subsequence rather than an
 * exact transcript.
 */
const MUST_INVOKE_IN_ORDER = [
  ['open', /\/login$/],
  ['fill', /^input\[type='email'\]$/, /^user@example\.com$/],
  ['fill', /^input\[type='password'\]$/, /^correct horse$/],
  ['click', /login-submit/],
  // The refresh click is the 11% regex-role shape and the only action whose element
  // carries a `css_selector`, so codegen emits it as an eval-based
  // `querySelector().click()` with `agent-browser click` only as a fallback. Pinned
  // as the eval, because the fallback does not run when the eval succeeds.
  ['eval', /querySelector\("button\[aria-label=\\"重新整理\\"\]"\)[\s\S]*\.click\(\)/],
];

/** Assertions the script must actually perform, identified by the argv they carry. */
const MUST_ASSERT = [
  { what: 'login url', match: function(c) { return c[0] === 'get' && c[1] === 'url'; } },
  {
    what: 'welcome heading visibility probe',
    match: function(c) { return c[0] === 'eval' && /data-testid=\\?"welcome\\?"/.test(c[1] || ''); },
  },
  {
    what: 'error banner negative probe',
    match: function(c) { return c[0] === 'eval' && /login-error/.test(c[1] || ''); },
  },
  {
    what: 'results table probe',
    match: function(c) { return c[0] === 'eval' && /table\\?\.results|table\.results/.test(c[1] || ''); },
  },
  // The bare `<element> is visible` form — 7% of corpus expects, and a shared
  // `_global` element rather than a page-scoped one. It resolves through the same
  // eval probe as the others; the `agent-browser is visible` calls in the generated
  // script are helper *definitions*, not calls this flow makes, which is what a
  // first version of this entry asserted before the baseline refused it.
  {
    what: 'shared-element visibility probe',
    match: function(c) { return c[0] === 'eval' && /nav-dashboard/.test(c[1] || ''); },
  },
];

/**
 * The source-level assertions, kept rather than replaced.
 *
 * Argv is strictly better for identity and for "did this call happen at all", and
 * strictly worse for two things, because argv erases distinctions the source keeps:
 *
 *   - the flow's two `url contains` expectations emit the *identical* `get url`
 *     call, so no argv assertion can tell one from the other, or one from two.
 *   - assertion polarity lives in the inline judge invocation, not in what
 *     agent-browser receives, so `visible` and `not-visible` are indistinguishable
 *     in argv.
 *
 * A first revision deleted these and disclosed neither loss. The two instruments
 * catch disjoint classes; running both is the honest arrangement.
 */
const MUST_EMIT = [
  /_poll_url_contains '\/login'/,
  /_poll_url_contains '\/dashboard'/,
  /_poll_visibility '\[data-testid="login-error"\]' 'strict' not-visible/,
  /_poll_visibility '\[data-testid="welcome"\]' 'strict' visible/,
  /_poll_visibility 'table\.results' 'strict' visible/,
];

/**
 * Recover a selector's written form from the generated script.
 *
 * Undoes bash single-quoting and the JS string inside it, so `MUST_EMIT` pins the
 * identity rather than codegen's quoting style. That normalisation is exactly why
 * source assertions cannot see a wrong-but-well-formed emission — which is what the
 * argv assertions below are for.
 */
function recoverSelectorText(script) {
  return script.split("'\\''").join("'").split('\\"').join('"');
}

function readInvocations(logPath) {
  if (!fs.existsSync(logPath)) return [];
  return fs
    .readFileSync(logPath, 'utf8')
    .split('\n')
    .filter(Boolean)
    .map(function(line) { return JSON.parse(line); })
    .map(function(argv) {
      // The shim re-adds `--session <name>`; drop it so assertions name the command.
      return argv[0] === '--session' ? argv.slice(2) : argv;
    });
}

describe('happy path: the commands real flows issue', function() {
  test('the corpus-shaped flow compiles and runs the calls it claims to', async function(t) {
    const mappingDir = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-happy-map-'));
    const outDir = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-happy-out-'));
    const runDir = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-happy-run-'));
    t.after(function() {
      for (const dir of [mappingDir, outDir, runDir]) {
        fs.rmSync(dir, { recursive: true, force: true });
      }
    });
    fs.copyFileSync(
      path.join(FIXTURES, 'happy-path-mapping.yaml'),
      path.join(mappingDir, 'happy-path-app.yaml')
    );

    const result = await compile(
      path.join(FIXTURES, 'happy-path-flow.yaml'),
      mappingDir,
      outDir
    );
    assert.ok(result.success, 'compile must succeed. errors: ' + JSON.stringify(result.errors));

    // `bash -n` still earns its place: it is the cheapest instrument that fails on the
    // quoting defects codegen can emit, and it fails before the script is run.
    const syntax = childProcess.spawnSync('bash', ['-n', result.outputPath], { stdio: 'pipe' });
    assert.equal(syntax.status, 0, 'bash -n must accept the script: ' + syntax.stderr);

    // Source-level, for the two things argv erases: which url assertion, and polarity.
    const readable = recoverSelectorText(fs.readFileSync(result.outputPath, 'utf8'));
    for (const emission of MUST_EMIT) {
      assert.match(readable, emission, 'generated script must emit ' + emission);
    }

    // A directory on PATH holding only the stub, named as the binary the shim spawns.
    const binDir = path.join(runDir, 'bin');
    fs.mkdirSync(binDir);
    const stubPath = path.join(binDir, 'agent-browser');
    fs.writeFileSync(
      stubPath,
      '#!/usr/bin/env bash\nexec "' + process.execPath + '" "' + ARGV_STUB + '" "$@"\n',
      { mode: 0o755 }
    );

    const logPath = path.join(runDir, 'argv.log');
    const run = childProcess.spawnSync('bash', [result.outputPath], {
      encoding: 'utf8',
      timeout: 120000,
      env: Object.assign({}, process.env, {
        PATH: binDir + path.delimiter + process.env.PATH,
        E2E_BROWSER_RUNTIME: RUNTIME_SHIM,
        E2E_BROWSER_RUN_ID: 'happy-path-run',
        E2E_SCREENSHOT_DIR: path.join(runDir, 'shots'),
        E2E_STUB_LOG: logPath,
        E2E_STUB_STATE: path.join(runDir, 'state.json'),
        E2E_STUB_ABSENT_SELECTORS: ABSENT,
        E2E_STUB_SNAPSHOT: 'Dashboard',
        RETRIES: '1',
      }),
    });

    const calls = readInvocations(logPath);
    const transcript = calls.map(function(c) { return c.join(' '); }).join('\n');
    const diagnostic = '\n--- stdout ---\n' + (run.stdout || '') +
      '\n--- stderr ---\n' + (run.stderr || '') +
      '\n--- argv ---\n' + transcript;

    // The script's own verdict, before any argv is inspected. Without this the gate
    // asserts that calls were *made* and never that the flow *passed*: reporting the
    // results table absent makes the script exit 1, and every assertion below still
    // holds, so the gate went green on a failing run. That is the same shape as the
    // classes this file exists to close — a proxy standing in for the outcome.
    assert.equal(run.status, 0, 'the compiled script must exit 0' + diagnostic);

    assert.ok(calls.length > 0, 'the script must invoke agent-browser at all' + diagnostic);

    // Ordered subsequence: every required call appears, and in this relative order.
    let cursor = 0;
    for (const expected of MUST_INVOKE_IN_ORDER) {
      const found = calls.findIndex(function(call, index) {
        if (index < cursor) return false;
        return expected.every(function(part, i) {
          return typeof part === 'string' ? call[i] === part : part.test(call[i] || '');
        });
      });
      assert.ok(
        found >= 0,
        'the script must invoke ' + JSON.stringify(expected.map(String)) +
          ' after index ' + cursor + diagnostic
      );
      cursor = found + 1;
    }

    for (const assertion of MUST_ASSERT) {
      assert.ok(
        calls.some(assertion.match),
        'the script must perform the ' + assertion.what + ' check' + diagnostic
      );
    }
  });
});
