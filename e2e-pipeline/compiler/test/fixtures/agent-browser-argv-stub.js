#!/usr/bin/env node
'use strict';

/**
 * agent-browser stub that records argv and answers just enough to reach the end.
 *
 * WHAT IT IS FOR
 *
 * `happy-path.test.js` used to read the generated script. Two defect classes survive
 * that: escaping that is wrong but well-formed, and a missing action. Both become
 * visible the moment you assert on the arguments the program actually passes
 * (#180), which is what this exists to capture.
 *
 * HOW IT IS REACHED
 *
 * The compiled script does not call this directly. It defines its own
 * `agent-browser()` shell function that routes every call through
 * `node "$E2E_BROWSER_RUNTIME"`, so the seam is that variable, not PATH. Point it
 * at `browser-runtime-shim.js`, which strips the runtime's own flags and re-adds
 * `--session`, and it spawns `agent-browser` from PATH — this file. Both halves
 * already existed for `runtime-state-finalizer.test.js`; nothing new was invented.
 *
 * WHAT IT ANSWERS
 *
 * Only what the happy-path flow issues: open, fill, click, snapshot, get url,
 * is visible, eval, close. It is not a model of agent-browser and must not grow
 * into one — a stub that answers commands no test exercises is untested code that
 * looks like coverage.
 *
 * The `eval` envelope shape is not guessed. It was derived by feeding candidates to
 * the real judge (`compiler/lib/visibility-probe.js`) until all four
 * assertion x presence combinations came out right: visible/present -> satisfied,
 * not-visible/present -> retryable, visible/absent -> retryable,
 * not-visible/absent -> satisfied. A wrong envelope would make every visibility
 * assertion pass as `probe_error` and the gate would prove nothing.
 *
 * STATE
 *
 * `E2E_STUB_LOG` receives one JSON line per invocation. `E2E_STUB_STATE` holds the
 * current URL, so the flow's two `url contains` assertions can differ: `open` sets
 * it, and a click on the login submit advances it to the post-login path. Without
 * that the login and dashboard assertions would be indistinguishable and the gate
 * could not tell a flow that logs in from one that does not.
 *
 * `E2E_STUB_ABSENT_SELECTORS` is a comma-separated list of **substrings** reported
 * as not present — the flow asserts one element is *not* visible, and a stub that
 * says "everything is visible" would pass that assertion for the wrong reason.
 * Substrings rather than whole selectors because the probe expression carries the
 * selector JS-escaped (`[data-testid=\"login-error\"]`), so an exact comparison
 * against the mapping's literal never matches — which is how the first version of
 * this stub reported an absent element as visible.
 */

const fs = require('node:fs');

const argv = process.argv.slice(2);
const logPath = process.env.E2E_STUB_LOG;
const statePath = process.env.E2E_STUB_STATE;
const absent = (process.env.E2E_STUB_ABSENT_SELECTORS || '')
  .split(',')
  .map(function (s) { return s.trim(); })
  .filter(Boolean);

if (logPath) {
  fs.appendFileSync(logPath, JSON.stringify(argv) + '\n');
}

function readState() {
  if (!statePath || !fs.existsSync(statePath)) return { url: 'about:blank' };
  try {
    return JSON.parse(fs.readFileSync(statePath, 'utf8'));
  } catch (_error) {
    return { url: 'about:blank' };
  }
}

function writeState(state) {
  if (statePath) fs.writeFileSync(statePath, JSON.stringify(state));
}

/** Strip a leading `--session <name>`, which the shim re-adds. */
let args = argv.slice();
if (args[0] === '--session') args = args.slice(2);

const command = args[0];
const state = readState();

/**
 * The probe evidence the real judge accepts. `present: false` yields `no_match`,
 * which is `satisfied` for a not-visible assertion and `retryable` for a visible
 * one — the asymmetry the flow's negative expectation depends on.
 */
function probeEvidence(present) {
  return {
    probe_version: 1,
    probe_scope: 'current-document',
    candidate_evidence_limit: 5,
    candidate_evidence_truncated: false,
    match_count: present ? 1 : 0,
    nonzero_layout_visible_count: present ? 1 : 0,
    style_visible_zero_rect_count: 0,
    non_style_visible_count: 0,
    candidates: present
      ? [{
          style_visible: true,
          rendered: true,
          client_rect_count: 1,
          positive_area: true,
          width: 10,
          height: 10,
          disabled: false,
        }]
      : [],
  };
}

/** True when the probe expression names a selector the test declared absent. */
function expressionTargetsAbsent(expression) {
  return absent.some(function (selector) {
    return String(expression).includes(selector);
  });
}

switch (command) {
  case 'open': {
    writeState({ url: args[1] || state.url });
    process.stdout.write('ok\n');
    break;
  }
  case 'click': {
    // The flow's login submit is the only click that changes location. Keying on the
    // selector rather than a call counter keeps the stub honest if steps are
    // reordered — a counter would advance the URL for whichever click came third.
    if (String(args[1] || '').includes('login-submit')) {
      writeState({ url: String(state.url).replace(/\/login\b.*$/, '/dashboard') });
    }
    process.stdout.write('ok\n');
    break;
  }
  case 'get': {
    process.stdout.write(String(state.url) + '\n');
    break;
  }
  case 'eval': {
    const present = !expressionTargetsAbsent(args[1] || '');
    process.stdout.write(
      JSON.stringify({ success: true, data: { result: probeEvidence(present) } }) + '\n'
    );
    break;
  }
  case 'is': {
    process.stdout.write(expressionTargetsAbsent(args[2] || '') ? 'false\n' : 'true\n');
    break;
  }
  case 'snapshot': {
    process.stdout.write(String(process.env.E2E_STUB_SNAPSHOT || '') + '\n');
    break;
  }
  case 'fill':
  case 'close':
  // `screenshot` only appears on the failure path. Answering it keeps a failing run's
  // transcript readable instead of turning it into an unhandled-command cascade.
  case 'screenshot': {
    process.stdout.write('ok\n');
    break;
  }
  default: {
    // Exits 3 rather than answering. That is only *loud* where the script propagates
    // it: the cleanup `close` is emitted as `... 2>/dev/null || true`, so an unhandled
    // command there is swallowed and the run still exits 0. What actually catches it
    // is the `run.status` assertion in happy-path.test.js — at every position the
    // script does not deliberately ignore. Naming that rather than claiming the exit
    // code is self-enforcing.
    process.stderr.write('agent-browser-argv-stub: unhandled command ' + String(command) + '\n');
    process.exit(3);
  }
}
