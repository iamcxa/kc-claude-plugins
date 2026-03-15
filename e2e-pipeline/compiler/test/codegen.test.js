'use strict';

const { test, describe } = require('node:test');
const assert = require('node:assert/strict');

const { generate, generateHeader, singleQuote } = require('../codegen.js');

// ---------------------------------------------------------------------------
// Test helpers — build minimal resolved step objects matching resolver output
// ---------------------------------------------------------------------------

function makeNavigate(id, urlPath, action) {
  return {
    id: id,
    action: action || ('Navigate to ' + urlPath),
    type: 'navigate',
    operands: { target: urlPath, urlPath: urlPath },
  };
}

function makeClick(id, element, selector, action) {
  return {
    id: id,
    action: action || ('Click ' + element),
    type: 'click',
    operands: { element: element, selector: selector },
  };
}

function makeFill(id, element, selector, value, action) {
  return {
    id: id,
    action: action || ('Fill ' + element + " with '" + value + "'"),
    type: 'fill',
    operands: { element: element, selector: selector, value: value },
  };
}

function makeSnapshot(id, action) {
  return { id: id, action: action || 'Take snapshot', type: 'snapshot', operands: {} };
}

function makeWait(id, seconds, action) {
  return {
    id: id,
    action: action || ('Wait ' + seconds),
    type: 'wait',
    operands: { seconds: seconds },
  };
}

function makeVerifyExternal(id, action) {
  return { id: id, action: action || 'Verify external', type: 'verify-external', operands: {} };
}

function makeResolved(steps, name, description) {
  return {
    name: name || 'test-flow',
    description: description || 'A test flow',
    steps: steps,
  };
}

// ---------------------------------------------------------------------------
// singleQuote() tests
// ---------------------------------------------------------------------------

describe('singleQuote()', function() {
  test("simple string is wrapped in single quotes", function() {
    assert.equal(singleQuote('simple'), "'simple'");
  });

  test("string with embedded single quote uses escape pattern", function() {
    // input[type='password'] → 'input[type='\''password'\'']'
    // Each ' becomes '\'' — end quote, backslash-escaped quote, reopen quote
    assert.equal(singleQuote("input[type='password']"), "'input[type='\\''password'\\'']'");
  });

  test("string with double quotes is unaffected (only single quotes escaped)", function() {
    const result = singleQuote('role=textbox[name="Email"]');
    assert.equal(result, "'role=textbox[name=\"Email\"]'");
  });

  test("string with no special chars is wrapped as-is", function() {
    assert.equal(singleQuote('role=button[name=Submit]'), "'role=button[name=Submit]'");
  });
});

// ---------------------------------------------------------------------------
// Shell header tests
// ---------------------------------------------------------------------------

describe('generate() — shell header', function() {
  test("output starts with shebang and set -euo pipefail", function() {
    const script = generate(makeResolved([]), 'test-flow');
    assert.ok(
      script.startsWith('#!/usr/bin/env bash\nset -euo pipefail'),
      'Expected shebang + set -euo pipefail at start. Got: ' + script.slice(0, 80)
    );
  });

  test("output includes LANG export", function() {
    const script = generate(makeResolved([]), 'test-flow');
    assert.ok(script.includes('export LANG=en_US.UTF-8'), 'Missing LANG export');
  });

  test("output includes LC_ALL export", function() {
    const script = generate(makeResolved([]), 'test-flow');
    assert.ok(script.includes('export LC_ALL=en_US.UTF-8'), 'Missing LC_ALL export');
  });
});

// ---------------------------------------------------------------------------
// Action type codegen tests
// ---------------------------------------------------------------------------

describe('generate() — navigate action', function() {
  test("navigate emits agent-browser open with BASE_URL and urlPath", function() {
    const step = makeNavigate('nav-login', '/login');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('agent-browser open "${BASE_URL}/login"'),
      'Expected agent-browser open with BASE_URL. Got snippet: ' + script
    );
  });

  test("navigate to /dashboard emits correct URL", function() {
    const step = makeNavigate('nav-dashboard', '/dashboard');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(script.includes('agent-browser open "${BASE_URL}/dashboard"'));
  });

  test("navigate failure block calls _handle_failure with step id and message", function() {
    const step = makeNavigate('nav-login', '/login');
    const script = generate(makeResolved([step]), 'test-flow');
    // v2.0: _handle_failure replaces inline echo + exit 1
    assert.ok(
      script.includes('_handle_failure "nav-login"'),
      'Expected _handle_failure "nav-login" call. Got: ' + script
    );
    assert.ok(
      script.includes('navigate to /login failed'),
      'Expected failure message referencing urlPath. Got: ' + script
    );
  });
});

describe('generate() — click action', function() {
  test("click emits agent-browser click with single-quoted selector", function() {
    const step = makeClick('click-submit', 'login_button', 'role=button[name="Sign In"]');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes("agent-browser click 'role=button[name=\"Sign In\"]'"),
      'Expected single-quoted selector. Got: ' + script
    );
  });

  test("click failure block calls _handle_failure with step id and message", function() {
    const step = makeClick('click-submit', 'login_button', 'role=button[name="Sign In"]');
    const script = generate(makeResolved([step]), 'test-flow');
    // v2.0: _handle_failure replaces inline echo + exit 1
    assert.ok(
      script.includes('_handle_failure "click-submit"'),
      'Expected _handle_failure "click-submit" call. Got: ' + script
    );
    assert.ok(
      script.includes('click action failed'),
      'Expected click action failed message. Got: ' + script
    );
  });
});

describe('generate() — fill action', function() {
  test("fill emits agent-browser fill with single-quoted selector and value", function() {
    const step = makeFill('fill-email', 'email_input', 'role=textbox[name="Email"]', 'test@example.com');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes("agent-browser fill 'role=textbox[name=\"Email\"]' 'test@example.com'"),
      'Expected fill with quoted selector and value. Got: ' + script
    );
  });

  test("fill with selector containing single quotes produces correctly escaped bash", function() {
    const step = makeFill('fill-pass', 'password_input', "input[type='password']", 'secret');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes("agent-browser fill 'input[type='\\''password'\\'']' 'secret'"),
      'Expected escaped single quotes in fill. Got: ' + script
    );
  });

  test("fill failure block calls _handle_failure with step id and message", function() {
    const step = makeFill('fill-email', 'email_input', 'role=textbox[name="Email"]', 'test@example.com');
    const script = generate(makeResolved([step]), 'test-flow');
    // v2.0: _handle_failure replaces inline echo + exit 1
    assert.ok(
      script.includes('_handle_failure "fill-email"'),
      'Expected _handle_failure "fill-email" call. Got: ' + script
    );
    assert.ok(
      script.includes('fill action failed'),
      'Expected fill action failed message. Got: ' + script
    );
  });
});

describe('generate() — snapshot action', function() {
  test("snapshot emits agent-browser snapshot", function() {
    const step = makeSnapshot('take-snap');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(script.includes('agent-browser snapshot'), 'Expected agent-browser snapshot');
  });
});

describe('generate() — wait action', function() {
  test("wait with seconds=2 emits sleep 2", function() {
    const step = makeWait('wait-2', 2);
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(script.includes('sleep 2'), 'Expected sleep 2');
  });
});

describe('generate() — verify-external action', function() {
  test("verify-external emits SKIP echo and no exit", function() {
    const step = makeVerifyExternal('verify-ext');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('echo "SKIP: verify-ext -- external verification (no human in CI)"'),
      'Expected SKIP echo. Got: ' + script
    );
    // The SKIP line must NOT be followed by exit 1
    const skipLine = 'echo "SKIP: verify-ext -- external verification (no human in CI)"';
    const skipIdx = script.indexOf(skipLine);
    const afterSkip = script.slice(skipIdx + skipLine.length, skipIdx + skipLine.length + 30);
    assert.ok(!afterSkip.includes('exit 1'), 'verify-external must not have exit 1 after SKIP');
  });
});

// ---------------------------------------------------------------------------
// Expect codegen tests
// ---------------------------------------------------------------------------

describe('generate() — expect: visible', function() {
  test("visible expect uses poll-until pattern (v2.0: _poll_visible call)", function() {
    const step = makeClick('click-btn', 'login_button', 'role=button[name="Sign In"]');
    step.expects = [{ type: 'active', raw: 'login_button is visible', elementName: 'login_button', selector: 'role=button[name="Sign In"]' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes("_poll_visible 'role=button[name=\"Sign In\"]'"),
      'Expected _poll_visible call for active expect. Got: ' + script
    );
  });

  test("visible expect uses || _handle_failure pattern (no inline exit 1)", function() {
    const step = makeClick('click-btn', 'login_button', 'role=button[name="Sign In"]');
    step.expects = [{ type: 'active', raw: 'login_button is visible', elementName: 'login_button', selector: 'role=button[name="Sign In"]' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('|| _handle_failure "click-btn"'),
      'Expected || _handle_failure for poll failure. Got: ' + script
    );
  });

  test("visible expect FAIL message names the element (via _handle_failure)", function() {
    const step = makeClick('click-btn', 'login_button', 'role=button[name="Sign In"]');
    step.expects = [{ type: 'active', raw: 'login_button is visible', elementName: 'login_button', selector: 'role=button[name="Sign In"]' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('login_button not visible'),
      'Expected failure message naming element login_button. Got: ' + script
    );
  });
});

describe('generate() — expect: deferred', function() {
  test("deferred expect emits TODO echo", function() {
    const step = makeClick('click-btn', 'login_button', 'role=button[name="Sign In"]');
    step.expects = [{ type: 'deferred', raw: 'url contains /dashboard' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes("echo \"TODO: expect 'url contains /dashboard' not compiled (Phase 2)\""),
      'Expected TODO echo for deferred expect. Got: ' + script
    );
  });
});

// ---------------------------------------------------------------------------
// Task 2: Step logging, exit behavior, and success/fail summary
// ---------------------------------------------------------------------------

describe('generate() — step logging [N/T] prefix', function() {
  // Build a 6-step flow matching simple-flow.yaml's action types
  function makeSixStepFlow() {
    return [
      makeNavigate('navigate-to-login', '/login', 'Navigate to /login'),
      makeFill('fill-email', 'email_input', 'role=textbox[name="Email"]', 'test@example.com', "Fill email_input with 'test@example.com' on login"),
      makeClick('click-submit', 'login_button', 'role=button[name="Sign In"]', 'Click login_button on login'),
      makeSnapshot('take-snapshot', 'Take snapshot'),
      makeWait('wait-for-load', 2, 'Wait 2'),
      makeVerifyExternal('verify-external', 'Verify external'),
    ];
  }

  test("first step of 6-step flow logs [1/6]", function() {
    const script = generate(makeResolved(makeSixStepFlow()), 'test-flow');
    assert.ok(
      script.includes('echo "[1/6] navigate-to-login: Navigate to /login"'),
      'Expected [1/6] log. Got: ' + script.slice(0, 200)
    );
  });

  test("last step of 6-step flow logs [6/6]", function() {
    const script = generate(makeResolved(makeSixStepFlow()), 'test-flow');
    assert.ok(
      script.includes('echo "[6/6] verify-external: Verify external"'),
      'Expected [6/6] log. Got: ' + script
    );
  });

  test("middle step logs correct index (fill is step 2 of 6)", function() {
    const script = generate(makeResolved(makeSixStepFlow()), 'test-flow');
    assert.ok(script.includes("echo \"[2/6] fill-email:"));
  });

  test("verify-external step has [N/T] prefix THEN SKIP echo (two echo lines in order)", function() {
    const script = generate(makeResolved(makeSixStepFlow()), 'test-flow');
    const prefixLine = 'echo "[6/6] verify-external: Verify external"';
    const skipLine = 'echo "SKIP: verify-external -- external verification (no human in CI)"';
    const prefixIdx = script.indexOf(prefixLine);
    const skipIdx = script.indexOf(skipLine);
    assert.ok(prefixIdx !== -1, 'Missing [6/6] prefix echo');
    assert.ok(skipIdx !== -1, 'Missing SKIP echo');
    assert.ok(prefixIdx < skipIdx, '[N/T] prefix must come before SKIP echo');
  });

  test("1-step flow logs [1/1]", function() {
    const step = makeNavigate('nav', '/home', 'Navigate to /home');
    const script = generate(makeResolved([step]), 'mini-flow');
    assert.ok(script.includes('echo "[1/1] nav: Navigate to /home"'));
  });
});

describe('generate() — failure messages', function() {
  test("navigate failure reason includes urlPath (via _handle_failure call)", function() {
    const step = makeNavigate('nav-login', '/login', 'Navigate to /login');
    const script = generate(makeResolved([step]), 'test-flow');
    // v2.0: _handle_failure "step-id" "msg" replaces inline echo + exit 1
    assert.ok(
      script.includes('_handle_failure "nav-login"') && script.includes('navigate to /login failed'),
      'Navigate failure must call _handle_failure with step id and urlPath. Got: ' + script
    );
  });

  test("click failure reason is generic 'click action failed' (via _handle_failure call)", function() {
    const step = makeClick('click-btn', 'login_button', 'role=button[name="Sign In"]');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('_handle_failure "click-btn"') && script.includes('click action failed'),
      'Click failure must call _handle_failure with step id. Got: ' + script
    );
  });

  test("fill failure reason is generic 'fill action failed' (via _handle_failure call)", function() {
    const step = makeFill('fill-email', 'email_input', 'role=textbox[name="Email"]', 'test@example.com');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('_handle_failure "fill-email"') && script.includes('fill action failed'),
      'Fill failure must call _handle_failure with step id. Got: ' + script
    );
  });

  test("snapshot has no failure block (no _handle_failure call near snapshot)", function() {
    const step = makeSnapshot('take-snap');
    const script = generate(makeResolved([step]), 'test-flow');
    // snapshot block should not contain _handle_failure in its vicinity
    // A snapshot-only script has no retry wrapper and no _handle_failure call in step code
    const snapIdx = script.indexOf('agent-browser snapshot');
    const afterSnap = script.slice(snapIdx, snapIdx + 100);
    assert.ok(!afterSnap.includes('_handle_failure'), 'snapshot must not have _handle_failure call after it');
  });

  test("wait has no failure block", function() {
    const step = makeWait('wait-2', 2);
    const script = generate(makeResolved([step]), 'test-flow');
    const waitIdx = script.indexOf('sleep 2');
    const afterWait = script.slice(waitIdx, waitIdx + 30);
    assert.ok(!afterWait.includes('FAIL'), 'wait must not have failure block');
  });
});

describe('generate() — PASS summary and exit', function() {
  test("script ends with PASS summary for flow with no skips", function() {
    const steps = [makeNavigate('nav', '/home'), makeClick('click', 'btn', 'button')];
    const script = generate(makeResolved(steps, 'my-flow'), 'my-flow');
    assert.ok(
      script.includes('echo "PASS: my-flow (2/2 steps, 0 skipped)"'),
      'Expected PASS with 0 skipped. Got: ' + script.slice(-100)
    );
  });

  test("PASS skip count matches number of verify-external steps", function() {
    const steps = [
      makeNavigate('nav', '/home'),
      makeVerifyExternal('ext-1'),
      makeClick('click', 'btn', 'button'),
      makeVerifyExternal('ext-2'),
    ];
    const script = generate(makeResolved(steps, 'flow-with-skips'), 'flow-with-skips');
    assert.ok(
      script.includes('echo "PASS: flow-with-skips (4/4 steps, 2 skipped)"'),
      'Expected PASS with 2 skipped. Got: ' + script.slice(-150)
    );
  });

  test("script ends with exit 0 after PASS message", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(script.trimEnd().endsWith('exit 0'), 'Script must end with exit 0');
  });

  test("6-step flow with 1 verify-external has PASS (6/6 steps, 1 skipped)", function() {
    const steps = [
      makeNavigate('navigate-to-login', '/login', 'Navigate to /login'),
      makeFill('fill-email', 'email_input', 'role=textbox[name="Email"]', 'test@example.com', "Fill email_input with 'test@example.com' on login"),
      makeClick('click-submit', 'login_button', 'role=button[name="Sign In"]', 'Click login_button on login'),
      makeSnapshot('take-snapshot', 'Take snapshot'),
      makeWait('wait-for-load', 2, 'Wait 2'),
      makeVerifyExternal('verify-external', 'Verify external'),
    ];
    const script = generate(makeResolved(steps, 'test-login'), 'test-login');
    assert.ok(
      script.includes('echo "PASS: test-login (6/6 steps, 1 skipped)"'),
      'Expected PASS with 1 skipped for 6-step flow. Got: ' + script.slice(-150)
    );
  });
});

// ---------------------------------------------------------------------------
// Task 1: Variable handling (generateVariables + generate() integration)
// ---------------------------------------------------------------------------

const { generateVariables } = require('../codegen.js');

describe('generateVariables() — no variables', function() {
  test("undefined variables returns empty string", function() {
    assert.equal(generateVariables(undefined, 'test-flow'), '');
  });

  test("null variables returns empty string", function() {
    assert.equal(generateVariables(null, 'test-flow'), '');
  });

  test("empty object returns empty string", function() {
    assert.equal(generateVariables({}, 'test-flow'), '');
  });
});

describe('generateVariables() — single optional variable (has default)', function() {
  test("usage comment lists variable in square brackets (optional)", function() {
    const result = generateVariables({ base_url: 'http://localhost:3000' }, 'test-flow');
    assert.ok(
      result.includes('# Usage: test-flow.sh [base_url]'),
      'Expected optional var in square brackets. Got: ' + result
    );
  });

  test("parameter comment describes optional with env fallback and default", function() {
    const result = generateVariables({ base_url: 'http://localhost:3000' }, 'test-flow');
    assert.ok(
      result.includes('# $1 BASE_URL -- optional (or set E2E_BASE_URL, default: http://localhost:3000)'),
      'Expected optional parameter comment. Got: ' + result
    );
  });

  test("assignment uses :- pattern with env fallback and default value", function() {
    const result = generateVariables({ base_url: 'http://localhost:3000' }, 'test-flow');
    assert.ok(
      result.includes('BASE_URL="${1:-${E2E_BASE_URL:-http://localhost:3000}}"'),
      'Expected :- pattern with env+default. Got: ' + result
    );
  });

  test("variable name is uppercased in assignment", function() {
    const result = generateVariables({ base_url: 'http://localhost:3000' }, 'test-flow');
    assert.ok(result.includes('BASE_URL='), 'Expected uppercased variable name');
  });
});

describe('generateVariables() — single required variable (null default)', function() {
  test("usage comment lists variable in angle brackets (required)", function() {
    const result = generateVariables({ base_url: null }, 'test-flow');
    assert.ok(
      result.includes('# Usage: test-flow.sh <base_url>'),
      'Expected required var in angle brackets. Got: ' + result
    );
  });

  test("parameter comment describes required with env fallback only", function() {
    const result = generateVariables({ base_url: null }, 'test-flow');
    assert.ok(
      result.includes('# $1 BASE_URL -- required (or set E2E_BASE_URL)'),
      'Expected required parameter comment. Got: ' + result
    );
  });

  test("assignment uses :? pattern with usage message", function() {
    const result = generateVariables({ base_url: null }, 'test-flow');
    assert.ok(
      result.includes('BASE_URL="${1:?Usage: test-flow.sh <base_url>}"'),
      'Expected :? pattern for required var. Got: ' + result
    );
  });
});

describe('generateVariables() — multiple variables (required + optional)', function() {
  test("usage comment puts required first (angle brackets), optional second (square brackets)", function() {
    const result = generateVariables({ base_url: 'http://localhost:3000', password: null }, 'test-flow');
    assert.ok(
      result.includes('# Usage: test-flow.sh [base_url] <password>'),
      'Expected mixed required/optional usage. Got: ' + result
    );
  });

  test("positional args are 1-indexed: $1 BASE_URL, $2 PASSWORD", function() {
    const result = generateVariables({ base_url: 'http://localhost:3000', password: null }, 'test-flow');
    assert.ok(result.includes('# $1 BASE_URL'), 'Expected $1 for base_url. Got: ' + result);
    assert.ok(result.includes('# $2 PASSWORD'), 'Expected $2 for password. Got: ' + result);
  });

  test("optional var env fallback uses E2E_ prefix: base_url -> E2E_BASE_URL", function() {
    const result = generateVariables({ base_url: 'http://localhost:3000', password: null }, 'test-flow');
    assert.ok(result.includes('E2E_BASE_URL'), 'Expected E2E_BASE_URL. Got: ' + result);
  });

  test("required var env fallback uses E2E_ prefix: password -> E2E_PASSWORD", function() {
    const result = generateVariables({ base_url: 'http://localhost:3000', password: null }, 'test-flow');
    assert.ok(result.includes('E2E_PASSWORD'), 'Expected E2E_PASSWORD. Got: ' + result);
  });

  test("optional variable without meaningful default uses empty :- fallback (set -u safety)", function() {
    const result = generateVariables({ password_opt: '' }, 'test-flow');
    assert.ok(
      result.includes('PASSWORD_OPT="${1:-${E2E_PASSWORD_OPT:-}}"'),
      'Expected empty :- fallback for empty-string default. Got: ' + result
    );
  });
});

describe('generate() — variables block placement', function() {
  test("variable block appears after LANG export but before step code", function() {
    const resolved = {
      name: 'test-login',
      description: 'Test',
      variables: { base_url: 'http://localhost:3000' },
      steps: [makeNavigate('nav', '/login', 'Navigate to /login')],
    };
    const script = generate(resolved, 'test-login');
    const langIdx = script.indexOf('export LANG=en_US.UTF-8');
    const varIdx = script.indexOf('BASE_URL=');
    const stepIdx = script.indexOf('echo "[1/1]');
    assert.ok(langIdx !== -1, 'Missing LANG export');
    assert.ok(varIdx !== -1, 'Missing BASE_URL= assignment');
    assert.ok(stepIdx !== -1, 'Missing step echo');
    assert.ok(langIdx < varIdx, 'LANG export must come before variable block');
    assert.ok(varIdx < stepIdx, 'Variable block must come before step code');
  });

  test("generate() with variables replaces placeholder comment with real variable block", function() {
    const resolved = {
      name: 'test-login',
      description: 'Test',
      variables: { base_url: 'http://localhost:3000' },
      steps: [],
    };
    const script = generate(resolved, 'test-login');
    assert.ok(
      !script.includes('# Variables: added by generateVariables()'),
      'Placeholder comment must be replaced when variables present'
    );
    assert.ok(script.includes('BASE_URL='), 'Expected actual variable declaration');
  });

  test("generate() without variables keeps placeholder comment (no variables block)", function() {
    const resolved = { name: 'test-flow', description: 'Test', steps: [] };
    const script = generate(resolved, 'test-flow');
    // When no variables, the placeholder comment remains (as per Plan 02)
    // OR it's just absent — either is acceptable as long as no BASE_URL= appears
    assert.ok(!script.includes('BASE_URL='), 'Must not emit BASE_URL when no variables');
  });
});

// ---------------------------------------------------------------------------
// Phase 2: generateExpects() — new expect type handlers (Task 2)
// ---------------------------------------------------------------------------

describe('generateExpects() — element-visible (no is keyword)', function() {
  test("element-visible uses _poll_visible call (same as active type)", function() {
    const step = makeClick('click-btn', 'login_button', 'role=button[name="Sign In"]');
    step.expects = [{ type: 'element-visible', raw: 'login_button visible', elementName: 'login_button', selector: 'role=button[name="Sign In"]' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes("_poll_visible 'role=button[name=\"Sign In\"]'"),
      'element-visible should use _poll_visible call. Got: ' + script
    );
  });

  test("element-visible uses || _handle_failure pattern (no inline exit 1)", function() {
    const step = makeClick('click-btn', 'login_button', 'role=button[name="Sign In"]');
    step.expects = [{ type: 'element-visible', raw: 'login_button visible', elementName: 'login_button', selector: 'role=button[name="Sign In"]' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('|| _handle_failure "click-btn"'),
      'element-visible must use || _handle_failure. Got: ' + script
    );
  });

  test("element-visible FAIL message names element and step id", function() {
    const step = makeClick('click-btn', 'login_button', 'role=button[name="Sign In"]');
    step.expects = [{ type: 'element-visible', raw: 'login_button visible', elementName: 'login_button', selector: 'role=button[name="Sign In"]' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('login_button not visible'),
      'element-visible FAIL must name the element. Got: ' + script
    );
  });
});

describe('generateExpects() — element-not-visible', function() {
  test("element-not-visible uses _poll_not_visible call (inverted logic)", function() {
    const step = makeSnapshot('check-dialog', 'Take snapshot');
    step.expects = [{ type: 'element-not-visible', raw: 'dialog not visible', elementName: 'dialog', selector: 'role=dialog' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes("_poll_not_visible 'role=dialog'"),
      'element-not-visible should use _poll_not_visible call. Got: ' + script
    );
  });

  test("element-not-visible uses || _handle_failure pattern", function() {
    const step = makeSnapshot('check-dialog', 'Take snapshot');
    step.expects = [{ type: 'element-not-visible', raw: 'dialog not visible', elementName: 'dialog', selector: 'role=dialog' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('|| _handle_failure "check-dialog"'),
      'element-not-visible must use || _handle_failure. Got: ' + script
    );
  });

  test("element-not-visible FAIL message says 'still visible (expected not visible)'", function() {
    const step = makeSnapshot('check-dialog', 'Take snapshot');
    step.expects = [{ type: 'element-not-visible', raw: 'dialog not visible', elementName: 'dialog', selector: 'role=dialog' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('still visible') && script.includes('expected not visible'),
      'element-not-visible FAIL must mention still visible. Got: ' + script
    );
  });

  test("element-not-visible selector is single-quoted in poll call", function() {
    const step = makeSnapshot('check-modal', 'Take snapshot');
    step.expects = [{ type: 'element-not-visible', raw: 'modal not visible', elementName: 'modal', selector: "role=dialog[name='Confirm']" }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes("_poll_not_visible 'role=dialog[name='\\''Confirm'\\'']'"),
      'selector with single quotes must be escaped in _poll_not_visible call. Got: ' + script
    );
  });
});

describe('generateExpects() — url-contains', function() {
  test("url-contains uses _poll_url_contains call (poll-until, CODEGEN-01)", function() {
    const step = makeNavigate('nav-dashboard', '/dashboard');
    step.expects = [{ type: 'url-contains', raw: 'url contains /dashboard', value: '/dashboard' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes("_poll_url_contains '/dashboard'"),
      'url-contains must use _poll_url_contains call. Got: ' + script
    );
  });

  test("url-contains uses || _handle_failure pattern with step id", function() {
    const step = makeNavigate('nav-dashboard', '/dashboard');
    step.expects = [{ type: 'url-contains', raw: 'url contains /dashboard', value: '/dashboard' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('|| _handle_failure "nav-dashboard"'),
      'url-contains must use || _handle_failure. Got: ' + script
    );
  });

  test("url-contains FAIL message includes value (via _handle_failure)", function() {
    const step = makeNavigate('nav-dashboard', '/dashboard');
    step.expects = [{ type: 'url-contains', raw: 'url contains /dashboard', value: '/dashboard' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('url does not contain /dashboard'),
      'url-contains FAIL must mention the expected value. Got: ' + script
    );
  });
});

describe('generateExpects() — url-not-contains', function() {
  test("url-not-contains generates instant agent-browser get url capture (no poll)", function() {
    const step = makeNavigate('submit-login', '/login');
    step.expects = [{ type: 'url-not-contains', raw: 'url does not contain /login', value: '/login' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('current_url=$(agent-browser get url) || true'),
      'url-not-contains must capture current URL instantly. Got: ' + script
    );
  });

  test("url-not-contains bash glob checks url == *value* (inverted — fail if found)", function() {
    const step = makeNavigate('submit-login', '/login');
    step.expects = [{ type: 'url-not-contains', raw: 'url does not contain /login', value: '/login' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('[[ "$current_url" == *"/login"* ]]'),
      'url-not-contains should fail when URL matches. Got: ' + script
    );
  });

  test("url-not-contains FAIL message says 'url contains X but should not' (via _handle_failure)", function() {
    const step = makeNavigate('submit-login', '/login');
    step.expects = [{ type: 'url-not-contains', raw: 'url does not contain /login', value: '/login' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('url contains /login but should not (got: $current_url)'),
      'url-not-contains FAIL message must mention the value. Got: ' + script
    );
  });
});

describe('generateExpects() — text-visible', function() {
  test("text-visible generates agent-browser snapshot capture", function() {
    const step = makeSnapshot('verify-text', 'Take snapshot');
    step.expects = [{ type: 'text-visible', raw: "text '每日看板' on page", text: '每日看板' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('_snapshot=$(agent-browser snapshot) || true'),
      'text-visible must capture snapshot. Got: ' + script
    );
  });

  test("text-visible uses grep -qF for fixed-string matching (CJK safe)", function() {
    const step = makeSnapshot('verify-text', 'Take snapshot');
    step.expects = [{ type: 'text-visible', raw: "text '每日看板' on page", text: '每日看板' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes("grep -qF '每日看板'"),
      'text-visible must use grep -qF for fixed string match. Got: ' + script
    );
  });

  test("text-visible uses if ! pattern (fail when text NOT found)", function() {
    const step = makeSnapshot('verify-text', 'Take snapshot');
    step.expects = [{ type: 'text-visible', raw: "text '每日看板' on page", text: '每日看板' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes("if ! echo \"$_snapshot\" | grep -qF"),
      'text-visible must use if ! pattern for failure detection. Got: ' + script
    );
  });

  test("text-visible FAIL message names the text and step id (via _handle_failure)", function() {
    const step = makeSnapshot('verify-text', 'Take snapshot');
    step.expects = [{ type: 'text-visible', raw: "text '每日看板' on page", text: '每日看板' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes("_handle_failure \"verify-text\"") && script.includes("每日看板' not found on page"),
      'text-visible FAIL must name the text via _handle_failure. Got: ' + script
    );
  });

  test("text-visible with ASCII text works correctly", function() {
    const step = makeSnapshot('verify-title', 'Take snapshot');
    step.expects = [{ type: 'text-visible', raw: 'text "Dashboard" visible', text: 'Dashboard' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes("grep -qF 'Dashboard'"),
      'text-visible with ASCII text uses grep -qF. Got: ' + script
    );
  });
});

describe('generateExpects() — or-visible', function() {
  test("or-visible uses _poll_or_visible call (v2.0 poll-until)", function() {
    const step = makeSnapshot('check-or', 'Take snapshot');
    step.expects = [{
      type: 'or-visible',
      raw: 'email_input visible or login_button visible',
      elements: [
        { elementName: 'email_input', selector: 'role=textbox[name="Email"]' },
        { elementName: 'login_button', selector: 'role=button[name="Sign In"]' },
      ],
    }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('_poll_or_visible '),
      'or-visible must use _poll_or_visible call. Got: ' + script
    );
  });

  test("or-visible includes first element selector in poll call", function() {
    const step = makeSnapshot('check-or', 'Take snapshot');
    step.expects = [{
      type: 'or-visible',
      raw: 'email_input visible or login_button visible',
      elements: [
        { elementName: 'email_input', selector: 'role=textbox[name="Email"]' },
        { elementName: 'login_button', selector: 'role=button[name="Sign In"]' },
      ],
    }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes("'role=textbox[name=\"Email\"]'"),
      'or-visible must include first element selector. Got: ' + script
    );
  });

  test("or-visible includes second element selector in poll call", function() {
    const step = makeSnapshot('check-or', 'Take snapshot');
    step.expects = [{
      type: 'or-visible',
      raw: 'email_input visible or login_button visible',
      elements: [
        { elementName: 'email_input', selector: 'role=textbox[name="Email"]' },
        { elementName: 'login_button', selector: 'role=button[name="Sign In"]' },
      ],
    }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes("'role=button[name=\"Sign In\"]'"),
      'or-visible must include second element selector. Got: ' + script
    );
  });

  test("or-visible uses || _handle_failure pattern with step id", function() {
    const step = makeSnapshot('check-or', 'Take snapshot');
    step.expects = [{
      type: 'or-visible',
      raw: 'email_input visible or login_button visible',
      elements: [
        { elementName: 'email_input', selector: 'role=textbox[name="Email"]' },
        { elementName: 'login_button', selector: 'role=button[name="Sign In"]' },
      ],
    }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('|| _handle_failure "check-or"'),
      'or-visible must use || _handle_failure. Got: ' + script
    );
  });

  test("or-visible poll call includes step id as first argument", function() {
    const step = makeSnapshot('check-or', 'Take snapshot');
    step.expects = [{
      type: 'or-visible',
      raw: 'email_input visible or login_button visible',
      elements: [
        { elementName: 'email_input', selector: 'role=textbox[name="Email"]' },
        { elementName: 'login_button', selector: 'role=button[name="Sign In"]' },
      ],
    }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('_poll_or_visible "check-or"'),
      'or-visible poll call must include step id. Got: ' + script
    );
  });

  test("or-visible FAIL message names both elements (via _handle_failure)", function() {
    const step = makeSnapshot('check-or', 'Take snapshot');
    step.expects = [{
      type: 'or-visible',
      raw: 'email_input visible or login_button visible',
      elements: [
        { elementName: 'email_input', selector: 'role=textbox[name="Email"]' },
        { elementName: 'login_button', selector: 'role=button[name="Sign In"]' },
      ],
    }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('neither email_input nor login_button'),
      'or-visible FAIL must name both elements. Got: ' + script
    );
  });
});

// ---------------------------------------------------------------------------
// Phase 2 Plan 02: cross-site codegen — generateVariables per-site + --session prefix
// ---------------------------------------------------------------------------

describe('generateVariables() — per-site variables (cross-site support)', function() {
  test("generateVariables with OFFICE_BASE_URL and APP_BASE_URL produces correct bash declarations", function() {
    const result = generateVariables(
      { OFFICE_BASE_URL: 'http://localhost:5173', APP_BASE_URL: 'http://localhost:8081' },
      'cross-site-test'
    );
    assert.ok(
      result.includes('OFFICE_BASE_URL='),
      'Expected OFFICE_BASE_URL= declaration. Got: ' + result
    );
    assert.ok(
      result.includes('APP_BASE_URL='),
      'Expected APP_BASE_URL= declaration. Got: ' + result
    );
    assert.ok(
      result.includes('http://localhost:5173'),
      'Expected office base_url in output. Got: ' + result
    );
    assert.ok(
      result.includes('http://localhost:8081'),
      'Expected app base_url in output. Got: ' + result
    );
  });

  test("generateVariables with per-site names uppercases correctly (no collision with BASE_URL)", function() {
    const result = generateVariables(
      { OFFICE_BASE_URL: 'http://localhost:5173', APP_BASE_URL: 'http://localhost:8081' },
      'cross-site-test'
    );
    // Should NOT have plain BASE_URL (only OFFICE_BASE_URL and APP_BASE_URL)
    const lines = result.split('\n');
    const basUrlLines = lines.filter(l => l.match(/^BASE_URL=/));
    assert.equal(basUrlLines.length, 0, 'Should not have plain BASE_URL= in per-site vars. Got: ' + result);
  });
});

describe('cross-site codegen — --session prefix on agent-browser commands', function() {
  function makeCrossSiteNavigate(id, site, urlPath) {
    return {
      id: id,
      action: 'Navigate to ' + urlPath,
      type: 'navigate',
      session: site,
      operands: { target: urlPath, urlPath: urlPath },
    };
  }

  function makeCrossSiteClick(id, site, element, selector) {
    return {
      id: id,
      action: 'Click ' + element,
      type: 'click',
      session: site,
      operands: { element: element, selector: selector },
    };
  }

  function makeCrossSiteSnapshot(id, site) {
    return {
      id: id,
      action: 'Take snapshot',
      type: 'snapshot',
      session: site,
      operands: {},
    };
  }

  test("navigate with session field uses --session prefix before open command", function() {
    const step = makeCrossSiteNavigate('office-nav', 'office', '/dashboard');
    const script = generate(makeResolved([step]), 'cross-site-test');
    assert.ok(
      script.includes('agent-browser --session office open'),
      'cross-site navigate must use --session prefix. Got: ' + script
    );
  });

  test("cross-site navigate uses site-specific base URL variable (OFFICE_BASE_URL)", function() {
    const step = makeCrossSiteNavigate('office-nav', 'office', '/dashboard');
    const script = generate(makeResolved([step]), 'cross-site-test');
    assert.ok(
      script.includes('"${OFFICE_BASE_URL}/dashboard"'),
      'cross-site navigate must use OFFICE_BASE_URL. Got: ' + script
    );
  });

  test("cross-site navigate for 'app' site uses APP_BASE_URL", function() {
    const step = makeCrossSiteNavigate('app-nav', 'app', '/home');
    const script = generate(makeResolved([step]), 'cross-site-test');
    assert.ok(
      script.includes('"${APP_BASE_URL}/home"'),
      'cross-site navigate for app site must use APP_BASE_URL. Got: ' + script
    );
  });

  test("click with session field uses --session prefix", function() {
    const step = makeCrossSiteClick('app-click', 'app', 'button_b', 'role=button[name="App Button"]');
    const script = generate(makeResolved([step]), 'cross-site-test');
    assert.ok(
      script.includes("agent-browser --session app click"),
      'cross-site click must use --session prefix. Got: ' + script
    );
  });

  test("snapshot with session field uses --session prefix", function() {
    const step = makeCrossSiteSnapshot('office-snap', 'office');
    const script = generate(makeResolved([step]), 'cross-site-test');
    assert.ok(
      script.includes('agent-browser --session office snapshot'),
      'cross-site snapshot must use --session prefix. Got: ' + script
    );
  });

  test("expect with session field on step passes session to _poll_visible (v2.0 poll-until)", function() {
    const step = makeCrossSiteSnapshot('office-check', 'office');
    step.expects = [{
      type: 'active',
      raw: 'heading_a is visible',
      elementName: 'heading_a',
      selector: 'role=heading[name="Office Dashboard"]',
    }];
    const script = generate(makeResolved([step]), 'cross-site-test');
    // v2.0: session is passed as 4th arg to _poll_visible, not as inline prefix
    assert.ok(
      script.includes('_poll_visible') && script.includes('"office"'),
      'cross-site expect must pass session to _poll_visible. Got: ' + script
    );
  });

  test("step without session field uses empty session string in poll call", function() {
    const step = makeClick('click-btn', 'login_button', 'role=button[name="Sign In"]');
    step.expects = [{
      type: 'active',
      raw: 'login_button is visible',
      elementName: 'login_button',
      selector: 'role=button[name="Sign In"]',
    }];
    const script = generate(makeResolved([step]), 'test-flow');
    // Single-site step: empty session arg "" passed to poll helper
    assert.ok(
      script.includes('_poll_visible') && script.includes('""'),
      'single-site expect must use empty session arg in _poll_visible. Got: ' + script
    );
  });
});

// ---------------------------------------------------------------------------
// Phase 2 Plan 02 Task 3: generateHeader(meta) — provenance metadata
// ---------------------------------------------------------------------------

describe('generateHeader() — provenance metadata', function() {
  test("generateHeader() with no args returns minimal Phase 1 header (backwards compat)", function() {
    const header = generateHeader();
    assert.ok(header.startsWith('#!/usr/bin/env bash\nset -euo pipefail'), 'Expected shebang + set. Got: ' + header);
    assert.ok(header.includes('export LANG=en_US.UTF-8'), 'Expected LANG export');
    assert.ok(!header.includes('DO NOT EDIT'), 'No-args header must not have DO NOT EDIT');
    assert.ok(!header.includes('SHA-256'), 'No-args header must not have SHA-256');
  });

  test("generateHeader(null) returns minimal header (backwards compat)", function() {
    const header = generateHeader(null);
    assert.ok(!header.includes('DO NOT EDIT'), 'null meta must not have DO NOT EDIT');
  });

  test("generateHeader(meta) includes DO NOT EDIT comment", function() {
    const meta = {
      flowName: 'my-flow',
      flowPath: '/flows/my-flow.yaml',
      mappingPath: '/mappings/my-app.yaml',
      timestamp: '2026-03-15T10:00:00.000Z',
      hash: 'abc123',
    };
    const header = generateHeader(meta);
    assert.ok(
      header.includes('# DO NOT EDIT -- regenerate with: e2e-compile my-flow'),
      'Expected DO NOT EDIT comment. Got: ' + header
    );
  });

  test("generateHeader(meta) includes Source: flow path", function() {
    const meta = {
      flowName: 'my-flow',
      flowPath: '/flows/my-flow.yaml',
      mappingPath: '/mappings/my-app.yaml',
      timestamp: '2026-03-15T10:00:00.000Z',
      hash: 'abc123',
    };
    const header = generateHeader(meta);
    assert.ok(
      header.includes('# Source: /flows/my-flow.yaml'),
      'Expected Source: comment. Got: ' + header
    );
  });

  test("generateHeader(meta) with single mappingPath includes Mapping: line", function() {
    const meta = {
      flowName: 'my-flow',
      flowPath: '/flows/my-flow.yaml',
      mappingPath: '/mappings/my-app.yaml',
      timestamp: '2026-03-15T10:00:00.000Z',
      hash: 'abc123',
    };
    const header = generateHeader(meta);
    assert.ok(
      header.includes('# Mapping: /mappings/my-app.yaml'),
      'Expected Mapping: comment. Got: ' + header
    );
  });

  test("generateHeader(meta) with mappingPaths array lists each on separate Mapping: line", function() {
    const meta = {
      flowName: 'cross-flow',
      flowPath: '/flows/cross-flow.yaml',
      mappingPaths: ['/mappings/site-a.yaml', '/mappings/site-b.yaml'],
      timestamp: '2026-03-15T10:00:00.000Z',
      hash: 'def456',
    };
    const header = generateHeader(meta);
    assert.ok(
      header.includes('# Mapping: /mappings/site-a.yaml'),
      'Expected Mapping: for site-a. Got: ' + header
    );
    assert.ok(
      header.includes('# Mapping: /mappings/site-b.yaml'),
      'Expected Mapping: for site-b. Got: ' + header
    );
  });

  test("generateHeader(meta) includes Generated: timestamp line", function() {
    const meta = {
      flowName: 'my-flow',
      flowPath: '/flows/my-flow.yaml',
      mappingPath: '/mappings/my-app.yaml',
      timestamp: '2026-03-15T10:00:00.000Z',
      hash: 'abc123',
    };
    const header = generateHeader(meta);
    assert.ok(
      header.includes('# Generated: 2026-03-15T10:00:00.000Z'),
      'Expected Generated: comment. Got: ' + header
    );
  });

  test("generateHeader(meta) includes SHA-256 hash line", function() {
    const meta = {
      flowName: 'my-flow',
      flowPath: '/flows/my-flow.yaml',
      mappingPath: '/mappings/my-app.yaml',
      timestamp: '2026-03-15T10:00:00.000Z',
      hash: 'abc123deadbeef',
    };
    const header = generateHeader(meta);
    assert.ok(
      header.includes('# SHA-256: abc123deadbeef'),
      'Expected SHA-256: comment. Got: ' + header
    );
  });

  test("generateHeader(meta) still includes LANG and LC_ALL exports after provenance block", function() {
    const meta = {
      flowName: 'my-flow',
      flowPath: '/flows/my-flow.yaml',
      mappingPath: '/mappings/my-app.yaml',
      timestamp: '2026-03-15T10:00:00.000Z',
      hash: 'abc123',
    };
    const header = generateHeader(meta);
    assert.ok(header.includes('export LANG=en_US.UTF-8'), 'Must still have LANG export');
    assert.ok(header.includes('export LC_ALL=en_US.UTF-8'), 'Must still have LC_ALL export');
  });
});

// ---------------------------------------------------------------------------
// Phase 4 Plan 01: v2.0 runtime infrastructure (FLAG-02 + FLAG-03)
// ---------------------------------------------------------------------------

describe('v2.0 runtime infrastructure — flag parsing block', function() {
  test("compiled output contains CONTINUE_ON_ERROR=false default", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('CONTINUE_ON_ERROR=false'),
      'Expected CONTINUE_ON_ERROR=false default. Got: ' + script.slice(0, 300)
    );
  });

  test("compiled output contains RETRIES=0 default", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('RETRIES=0'),
      'Expected RETRIES=0 default. Got: ' + script.slice(0, 300)
    );
  });

  test("compiled output contains while flag-parsing loop header", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('while [[ $# -gt 0 ]]; do'),
      'Expected while flag-parsing loop. Got: ' + script
    );
  });

  test("compiled output contains --continue-on-error flag handler", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('--continue-on-error)'),
      'Expected --continue-on-error case. Got: ' + script
    );
  });

  test("compiled output contains --retries flag handler", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('--retries)'),
      'Expected --retries case. Got: ' + script
    );
  });

  test("compiled output contains set -- restore for positional args (bash 3.2 safe)", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('set -- "${_POSITIONAL[@]:-}"'),
      'Expected set -- "${_POSITIONAL[@]:-}" for bash 3.2 safety. Got: ' + script
    );
  });

  test("flag parsing block appears before variable assignment block", function() {
    const resolved = {
      name: 'test-flow',
      description: 'Test',
      variables: { base_url: 'http://localhost:3000' },
      steps: [makeNavigate('nav', '/login')],
    };
    const script = generate(resolved, 'test-flow');
    const flagIdx = script.indexOf('CONTINUE_ON_ERROR=false');
    const varIdx = script.indexOf('BASE_URL=');
    assert.ok(flagIdx !== -1, 'Missing flag block');
    assert.ok(varIdx !== -1, 'Missing variable block');
    assert.ok(flagIdx < varIdx, 'Flag parsing block must appear before variable assignment. flagIdx=' + flagIdx + ' varIdx=' + varIdx);
  });

  test("flag parsing block appears after LANG export (in correct header order)", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    const langIdx = script.indexOf('export LANG=en_US.UTF-8');
    const flagIdx = script.indexOf('CONTINUE_ON_ERROR=false');
    assert.ok(langIdx !== -1, 'Missing LANG export');
    assert.ok(flagIdx !== -1, 'Missing flag block');
    assert.ok(langIdx < flagIdx, 'LANG export must appear before flag block');
  });
});

describe('v2.0 runtime infrastructure — _handle_failure and _FAILED_STEPS', function() {
  test("compiled output contains _FAILED_STEPS=() array init", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('_FAILED_STEPS=()'),
      'Expected _FAILED_STEPS=() array. Got: ' + script
    );
  });

  test("compiled output contains _handle_failure() function definition", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('_handle_failure()'),
      'Expected _handle_failure() function definition. Got: ' + script
    );
  });

  test("_handle_failure function checks CONTINUE_ON_ERROR to decide accumulate vs exit 1", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('CONTINUE_ON_ERROR'),
      'Expected CONTINUE_ON_ERROR check inside _handle_failure. Got: ' + script
    );
    assert.ok(
      script.includes('_FAILED_STEPS+='),
      'Expected _FAILED_STEPS+= accumulate branch. Got: ' + script
    );
  });

  test("_handle_failure function returns 0 (must not cause set -e to abort)", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    // The function body must end with 'return 0' so || _handle_failure satisfies set -e
    assert.ok(
      script.includes('return 0'),
      'Expected return 0 in _handle_failure to satisfy set -e. Got: ' + script
    );
  });

  test("_FAILED_STEPS+= is in _handle_failure body (not elsewhere)", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    const fnStart = script.indexOf('_handle_failure()');
    const fnEnd = script.indexOf('\n}', fnStart);
    const fnBody = script.slice(fnStart, fnEnd + 2);
    assert.ok(
      fnBody.includes('_FAILED_STEPS+='),
      'Expected _FAILED_STEPS+= inside _handle_failure body. Got fn body: ' + fnBody
    );
  });
});

describe('v2.0 runtime infrastructure — retry wrapper on action steps', function() {
  test("navigate step uses _handle_failure instead of inline exit 1", function() {
    const step = makeNavigate('nav-login', '/login');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('_handle_failure'),
      'Expected _handle_failure in navigate step. Got: ' + script
    );
  });

  test("navigate step has retry wrapper with _retry=0 initialization", function() {
    const step = makeNavigate('nav-login', '/login');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('_retry=0'),
      'Expected _retry=0 in navigate step retry wrapper. Got: ' + script
    );
  });

  test("navigate step has while true retry loop", function() {
    const step = makeNavigate('nav-login', '/login');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('while true; do'),
      'Expected while true retry loop in navigate step. Got: ' + script
    );
  });

  test("navigate step has && break pattern for success exit", function() {
    const step = makeNavigate('nav-login', '/login');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('&& break'),
      'Expected && break for success exit from retry loop. Got: ' + script
    );
  });

  test("navigate step retry wrapper increments _retry with POSIX arithmetic", function() {
    const step = makeNavigate('nav-login', '/login');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('_retry=$((_retry + 1))'),
      'Expected _retry=$((_retry + 1)) — no let or (( )). Got: ' + script
    );
  });

  test("navigate retry wrapper checks RETRIES -eq 0 for immediate fail path", function() {
    const step = makeNavigate('nav-login', '/login');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('"$RETRIES" -eq 0'),
      'Expected RETRIES -eq 0 check for immediate fail. Got: ' + script
    );
  });

  test("navigate retry wrapper emits RETRY log line with counter", function() {
    const step = makeNavigate('nav-login', '/login');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('echo "RETRY [$_retry/$RETRIES]: nav-login"'),
      'Expected RETRY log line. Got: ' + script
    );
  });

  test("navigate retry wrapper has sleep 2 between retries", function() {
    const step = makeNavigate('nav-login', '/login');
    const script = generate(makeResolved([step]), 'test-flow');
    // sleep 2 is inside the retry loop (after RETRY echo, before next attempt)
    assert.ok(
      script.includes('sleep 2'),
      'Expected sleep 2 in retry loop. Got: ' + script
    );
  });

  test("click step uses _handle_failure instead of inline exit 1", function() {
    const step = makeClick('click-btn', 'login_button', 'role=button[name="Sign In"]');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('_handle_failure'),
      'Expected _handle_failure in click step. Got: ' + script
    );
  });

  test("click step has retry wrapper", function() {
    const step = makeClick('click-btn', 'login_button', 'role=button[name="Sign In"]');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('while true; do'),
      'Expected retry wrapper in click step. Got: ' + script
    );
  });

  test("fill step uses _handle_failure instead of inline exit 1", function() {
    const step = makeFill('fill-email', 'email_input', 'role=textbox[name="Email"]', 'test@example.com');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('_handle_failure'),
      'Expected _handle_failure in fill step. Got: ' + script
    );
  });

  test("fill step has retry wrapper", function() {
    const step = makeFill('fill-email', 'email_input', 'role=textbox[name="Email"]', 'test@example.com');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('while true; do'),
      'Expected retry wrapper in fill step. Got: ' + script
    );
  });
});

describe('v2.0 runtime infrastructure — non-action steps have NO retry wrapper', function() {
  test("snapshot step has NO retry wrapper (no while true loop)", function() {
    const step = makeSnapshot('take-snap');
    const script = generate(makeResolved([step]), 'test-flow');
    // A snapshot-only flow should not have a retry while loop
    assert.ok(
      !script.includes('while true; do'),
      'snapshot step must NOT have retry wrapper. Got: ' + script
    );
  });

  test("wait step has NO retry wrapper", function() {
    const step = makeWait('wait-2', 2);
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      !script.includes('while true; do'),
      'wait step must NOT have retry wrapper. Got: ' + script
    );
  });

  test("verify-external step has NO retry wrapper", function() {
    const step = makeVerifyExternal('verify-ext');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      !script.includes('while true; do'),
      'verify-external step must NOT have retry wrapper. Got: ' + script
    );
  });
});

describe('v2.0 runtime infrastructure — structured footer', function() {
  test("footer uses _FAILED_STEPS array length check", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('${#_FAILED_STEPS[@]}'),
      'Expected _FAILED_STEPS length check in footer. Got: ' + script
    );
  });

  test("footer exits 1 when failures exist", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    // The failure branch in the footer must have exit 1
    assert.ok(
      script.includes('exit 1'),
      'Expected exit 1 in footer failure branch. Got: ' + script
    );
  });

  test("footer exits 0 when no failures (PASS path)", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.trimEnd().endsWith('exit 0'),
      'Script must still end with exit 0 on the PASS path. Got end: ' + script.slice(-60)
    );
  });

  test("footer emits PASS message with flow name and step counts", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step], 'my-flow'), 'my-flow');
    assert.ok(
      script.includes('echo "PASS: my-flow'),
      'Expected PASS echo in footer with flow name. Got: ' + script.slice(-200)
    );
  });

  test("footer failure branch emits FAIL summary with failed step list", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    // The footer failure branch should emit a FAIL: N steps failed message
    assert.ok(
      script.includes('FAIL:'),
      'Expected FAIL: in footer failure branch. Got: ' + script.slice(-300)
    );
  });
});

describe('v2.0 runtime infrastructure — set -euo pipefail preserved', function() {
  test("set -euo pipefail still present in header", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('set -euo pipefail'),
      'Expected set -euo pipefail preserved. Got start: ' + script.slice(0, 100)
    );
  });

  test("set +e does NOT appear anywhere (must never disable errexit)", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      !script.includes('set +e'),
      'set +e must NOT appear in compiled script. Got: ' + script
    );
  });

  test("set -euo pipefail appears exactly once (not duplicated)", function() {
    const steps = [
      makeNavigate('nav', '/login'),
      makeClick('click-btn', 'login_button', 'role=button[name="Sign In"]'),
      makeFill('fill-email', 'email_input', 'role=textbox[name="Email"]', 'test@example.com'),
    ];
    const script = generate(makeResolved(steps), 'test-flow');
    const count = (script.match(/set -euo pipefail/g) || []).length;
    assert.equal(count, 1, 'set -euo pipefail must appear exactly once. Count: ' + count);
  });
});

describe('v2.0 runtime infrastructure — v1.0 backward compat (no flags = exit 1 on first failure)', function() {
  test("_handle_failure body includes exit 1 path (for CONTINUE_ON_ERROR=false)", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    // In the _handle_failure function, when CONTINUE_ON_ERROR=false, it must call exit 1
    const fnStart = script.indexOf('_handle_failure()');
    const fnEnd = script.indexOf('\n}', fnStart);
    const fnBody = script.slice(fnStart, fnEnd + 2);
    assert.ok(
      fnBody.includes('exit 1'),
      'Expected exit 1 in _handle_failure for CONTINUE_ON_ERROR=false path. Got fn body: ' + fnBody
    );
  });

  test("navigate failure message is preserved in FAIL echo inside handle_failure call", function() {
    const step = makeNavigate('nav-login', '/login');
    const script = generate(makeResolved([step]), 'test-flow');
    // The _handle_failure "nav-login" "msg" call must include the failure message
    assert.ok(
      script.includes('"nav-login"') || script.includes("nav-login"),
      'Expected step id nav-login passed to _handle_failure. Got: ' + script
    );
  });
});

// ---------------------------------------------------------------------------
// Phase 4 Plan 02: v2.0 poll-until codegen (CODEGEN-01 + CODEGEN-02)
// ---------------------------------------------------------------------------

describe('v2.0 poll-until — poll helpers emitted in generateRuntimeSupport', function() {
  test("_poll_visible() function is emitted in compiled output", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('_poll_visible()'),
      'Expected _poll_visible() function definition. Got: ' + script.slice(0, 500)
    );
  });

  test("_poll_not_visible() function is emitted in compiled output", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('_poll_not_visible()'),
      'Expected _poll_not_visible() function definition. Got: ' + script.slice(0, 500)
    );
  });

  test("_poll_url_contains() function is emitted in compiled output", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('_poll_url_contains()'),
      'Expected _poll_url_contains() function definition. Got: ' + script.slice(0, 500)
    );
  });

  test("_poll_or_visible() function is emitted in compiled output", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('_poll_or_visible()'),
      'Expected _poll_or_visible() function definition. Got: ' + script.slice(0, 500)
    );
  });

  test("_poll_visible uses $((_count + 1)) arithmetic (bash 3.2 safe — no let or (( )))", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    // Must use $(( )) arithmetic, not let or (( ))
    assert.ok(
      script.includes('$((_count + 1))'),
      'Expected $((_count + 1)) arithmetic in poll helper. Got snippet: ' + script.slice(0, 800)
    );
  });

  test("_poll_visible has deadline counter that returns 1 on timeout", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    // Poll helpers must return 1 on deadline (not exit 1 — callers use ||)
    const pollStart = script.indexOf('_poll_visible()');
    const pollEnd = script.indexOf('\n}', pollStart);
    const pollBody = script.slice(pollStart, pollEnd + 2);
    assert.ok(
      pollBody.includes('return 1'),
      'Expected return 1 on deadline in _poll_visible body. Got body: ' + pollBody
    );
  });

  test("poll helpers use 2>/dev/null on agent-browser calls", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    // _poll_visible should suppress agent-browser stderr
    const pollStart = script.indexOf('_poll_visible()');
    const pollEnd = script.indexOf('\n}', pollStart);
    const pollBody = script.slice(pollStart, pollEnd + 2);
    assert.ok(
      pollBody.includes('2>/dev/null'),
      'Expected 2>/dev/null in poll helper agent-browser call. Got body: ' + pollBody
    );
  });

  test("poll helpers use || true after $() capture to prevent set -e abort", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    const pollStart = script.indexOf('_poll_visible()');
    const pollEnd = script.indexOf('\n}', pollStart);
    const pollBody = script.slice(pollStart, pollEnd + 2);
    assert.ok(
      pollBody.includes('|| true'),
      'Expected || true after $() capture in poll helper. Got body: ' + pollBody
    );
  });

  test("poll helpers use local variables (bash 3.2 safe)", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    const pollStart = script.indexOf('_poll_visible()');
    const pollEnd = script.indexOf('\n}', pollStart);
    const pollBody = script.slice(pollStart, pollEnd + 2);
    assert.ok(
      pollBody.includes('local '),
      'Expected local variable declarations in poll helper. Got body: ' + pollBody
    );
  });

  test("_poll_not_visible checks for 'false' return (inverted logic)", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    const pollStart = script.indexOf('_poll_not_visible()');
    const pollEnd = script.indexOf('\n}', pollStart);
    const pollBody = script.slice(pollStart, pollEnd + 2);
    assert.ok(
      pollBody.includes('"false"'),
      'Expected _poll_not_visible to check for "false" return. Got body: ' + pollBody
    );
  });

  test("_poll_url_contains checks agent-browser get url", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    const pollStart = script.indexOf('_poll_url_contains()');
    const pollEnd = script.indexOf('\n}', pollStart);
    const pollBody = script.slice(pollStart, pollEnd + 2);
    assert.ok(
      pollBody.includes('agent-browser get url'),
      'Expected _poll_url_contains to call agent-browser get url. Got body: ' + pollBody
    );
  });

  test("_poll_or_visible checks multiple selectors and breaks when any returns true", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    const pollStart = script.indexOf('_poll_or_visible()');
    const pollEnd = script.indexOf('\n}', pollStart);
    const pollBody = script.slice(pollStart, pollEnd + 2);
    assert.ok(
      pollBody.includes('break'),
      'Expected break when element found in _poll_or_visible. Got body: ' + pollBody
    );
  });

  test("poll helpers use sleep 1 between iterations", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    const pollStart = script.indexOf('_poll_visible()');
    const pollEnd = script.indexOf('\n}', pollStart);
    const pollBody = script.slice(pollStart, pollEnd + 2);
    assert.ok(
      pollBody.includes('sleep 1'),
      'Expected sleep 1 between poll iterations. Got body: ' + pollBody
    );
  });
});

describe('v2.0 poll-until — generateExpects uses poll helpers (CODEGEN-01)', function() {
  test("active expect compiles to _poll_visible call (not inline is visible check)", function() {
    const step = makeClick('click-btn', 'login_button', 'role=button[name="Sign In"]');
    step.expects = [{ type: 'active', raw: 'login_button is visible', elementName: 'login_button', selector: 'role=button[name="Sign In"]' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes("_poll_visible 'role=button[name=\"Sign In\"]'"),
      'active expect must compile to _poll_visible call. Got: ' + script
    );
  });

  test("element-visible expect compiles to _poll_visible call", function() {
    const step = makeClick('click-btn', 'login_button', 'role=button[name="Sign In"]');
    step.expects = [{ type: 'element-visible', raw: 'login_button visible', elementName: 'login_button', selector: 'role=button[name="Sign In"]' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes("_poll_visible 'role=button[name=\"Sign In\"]'"),
      'element-visible expect must compile to _poll_visible call. Got: ' + script
    );
  });

  test("element-not-visible expect compiles to _poll_not_visible call", function() {
    const step = makeSnapshot('check-dialog', 'Take snapshot');
    step.expects = [{ type: 'element-not-visible', raw: 'dialog not visible', elementName: 'dialog', selector: 'role=dialog' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes("_poll_not_visible 'role=dialog'"),
      'element-not-visible must compile to _poll_not_visible call. Got: ' + script
    );
  });

  test("url-contains expect compiles to _poll_url_contains call", function() {
    const step = makeNavigate('nav-dashboard', '/dashboard');
    step.expects = [{ type: 'url-contains', raw: 'url contains /dashboard', value: '/dashboard' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes("_poll_url_contains '/dashboard'"),
      'url-contains must compile to _poll_url_contains call. Got: ' + script
    );
  });

  test("or-visible expect compiles to _poll_or_visible call with two selectors", function() {
    const step = makeSnapshot('check-or', 'Take snapshot');
    step.expects = [{
      type: 'or-visible',
      raw: 'email_input visible or login_button visible',
      elements: [
        { elementName: 'email_input', selector: 'role=textbox[name="Email"]' },
        { elementName: 'login_button', selector: 'role=button[name="Sign In"]' },
      ],
    }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('_poll_or_visible '),
      'or-visible must compile to _poll_or_visible call. Got: ' + script
    );
  });

  test("url-not-contains expect does NOT use poll (instant check — no reason to wait)", function() {
    const step = makeNavigate('submit-login', '/login');
    step.expects = [{ type: 'url-not-contains', raw: 'url does not contain /login', value: '/login' }];
    const script = generate(makeResolved([step]), 'test-flow');
    // url-not-contains remains an instant check — the expect section must not CALL _poll_url_contains
    // (the helper function definition is still emitted, but it must not be called for this expect type)
    // Check: step section should have 'current_url=' for instant capture, not a poll call
    const stepSection = script.slice(script.indexOf('[1/1]'), script.indexOf('# Exit summary'));
    assert.ok(
      stepSection.includes('current_url='),
      'url-not-contains must use instant current_url= capture, not poll. Got section: ' + stepSection
    );
    // The step section must NOT call _poll_url_contains (the helper exists but must not be invoked)
    assert.ok(
      !stepSection.includes('_poll_url_contains '),
      'url-not-contains must NOT call _poll_url_contains in expect section. Got section: ' + stepSection
    );
  });

  test("text-visible expect does NOT use poll (snapshot is too heavy for polling)", function() {
    const step = makeSnapshot('verify-text', 'Take snapshot');
    step.expects = [{ type: 'text-visible', raw: "text '每日看板' on page", text: '每日看板' }];
    const script = generate(makeResolved([step]), 'test-flow');
    // text-visible stays as instant snapshot + grep (no poll)
    assert.ok(
      script.includes('_snapshot=$(agent-browser snapshot) || true'),
      'text-visible must still use snapshot capture. Got: ' + script
    );
    // The step section must NOT call _poll_visible for text checks
    const stepSection = script.slice(script.indexOf('[1/1]'), script.indexOf('# Exit summary'));
    assert.ok(
      !stepSection.includes('_poll_visible '),
      'text-visible must NOT call _poll_visible in expect section. Got section: ' + stepSection
    );
  });

  test("_poll_visible call includes step id as second argument", function() {
    const step = makeClick('click-btn', 'login_button', 'role=button[name="Sign In"]');
    step.expects = [{ type: 'active', raw: 'login_button is visible', elementName: 'login_button', selector: 'role=button[name="Sign In"]' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('"click-btn"'),
      'Expected step id "click-btn" as argument to _poll_visible call. Got: ' + script
    );
  });

  test("active expect uses _poll_visible || _handle_failure pattern (no inline exit 1)", function() {
    const step = makeClick('click-btn', 'login_button', 'role=button[name="Sign In"]');
    step.expects = [{ type: 'active', raw: 'login_button is visible', elementName: 'login_button', selector: 'role=button[name="Sign In"]' }];
    const script = generate(makeResolved([step]), 'test-flow');
    // Must use || _handle_failure (not inline exit 1)
    assert.ok(
      script.includes('|| _handle_failure'),
      'Expected || _handle_failure pattern on _poll_visible call. Got: ' + script
    );
  });

  test("no inline exit 1 in generateExpects output — all failures through _handle_failure", function() {
    // Build a step with multiple expect types
    const step = makeSnapshot('multi-expect', 'Take snapshot');
    step.expects = [
      { type: 'active', raw: 'login_button is visible', elementName: 'login_button', selector: 'role=button[name="Sign In"]' },
      { type: 'element-not-visible', raw: 'dialog not visible', elementName: 'dialog', selector: 'role=dialog' },
    ];
    const script = generate(makeResolved([step]), 'test-flow');
    // Extract just the expect section (after the echo step marker, before footer)
    // There should be no raw 'exit 1' in the expects block other than through _handle_failure
    // Simpler check: every FAIL should come from _handle_failure, not bare exit 1
    // Check that 'exit 1' does not appear directly in the expects output for this step
    // (It can appear in _handle_failure function body and footer)
    const expectSection = script.slice(script.indexOf('[1/1]'), script.indexOf('# Exit summary'));
    assert.ok(
      !expectSection.includes('exit 1'),
      'No inline exit 1 should appear in expect section — use _handle_failure. Got section: ' + expectSection
    );
  });

  test("active expect failure message names element and uses _handle_failure", function() {
    const step = makeClick('click-btn', 'login_button', 'role=button[name="Sign In"]');
    step.expects = [{ type: 'active', raw: 'login_button is visible', elementName: 'login_button', selector: 'role=button[name="Sign In"]' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('login_button not visible'),
      'Expected failure message naming element login_button. Got: ' + script
    );
  });

  test("element-not-visible failure message says 'still visible'", function() {
    const step = makeSnapshot('check-dialog', 'Take snapshot');
    step.expects = [{ type: 'element-not-visible', raw: 'dialog not visible', elementName: 'dialog', selector: 'role=dialog' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('still visible'),
      'element-not-visible failure message must say "still visible". Got: ' + script
    );
  });
});

describe('v2.0 poll-until — step timeout from resolver (CODEGEN-02)', function() {
  test("step with timeout: 15 uses 15 as poll timeout argument", function() {
    const step = makeClick('click-btn', 'login_button', 'role=button[name="Sign In"]');
    step.timeout = 15;
    step.expects = [{ type: 'active', raw: 'login_button is visible', elementName: 'login_button', selector: 'role=button[name="Sign In"]' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes(' 15 ') || script.includes(' 15\n') || script.includes('"15"'),
      'Expected literal 15 as timeout argument in poll call. Got: ' + script
    );
  });

  test("step without timeout uses ${WAIT_TIMEOUT:-10} as default timeout argument", function() {
    const step = makeClick('click-btn', 'login_button', 'role=button[name="Sign In"]');
    step.expects = [{ type: 'active', raw: 'login_button is visible', elementName: 'login_button', selector: 'role=button[name="Sign In"]' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('"${WAIT_TIMEOUT:-10}"') || script.includes("${WAIT_TIMEOUT:-10}"),
      'Expected ${WAIT_TIMEOUT:-10} as default timeout. Got: ' + script
    );
  });

  test("url-contains expect also uses ${WAIT_TIMEOUT:-10} default when step has no timeout", function() {
    const step = makeNavigate('nav-dashboard', '/dashboard');
    step.expects = [{ type: 'url-contains', raw: 'url contains /dashboard', value: '/dashboard' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('${WAIT_TIMEOUT:-10}'),
      'Expected ${WAIT_TIMEOUT:-10} in url-contains poll call. Got: ' + script
    );
  });
});

describe('v2.0 poll-until — cross-site expects use session prefix', function() {
  function makeCrossSiteSnapshot(id, site) {
    return {
      id: id,
      action: 'Take snapshot',
      type: 'snapshot',
      session: site,
      operands: {},
    };
  }

  test("active expect on cross-site step passes session to poll helper", function() {
    const step = makeCrossSiteSnapshot('office-check', 'office');
    step.expects = [{
      type: 'active',
      raw: 'heading_a is visible',
      elementName: 'heading_a',
      selector: 'role=heading[name="Office Dashboard"]',
    }];
    const script = generate(makeResolved([step]), 'cross-site-test');
    // The poll call should pass session so it uses --session office
    assert.ok(
      script.includes('office'),
      'Expected session "office" in cross-site expect codegen. Got: ' + script
    );
    // The poll function call should include --session in its agent-browser command
    assert.ok(
      script.includes('_poll_visible ') && script.includes('office'),
      'Cross-site active expect must use _poll_visible with session reference. Got: ' + script
    );
  });
});
