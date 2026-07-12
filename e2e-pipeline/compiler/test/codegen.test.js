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

function makeEvalClick(id, element, selector, cssSelector, action) {
  return {
    id: id,
    action: action || ('Click ' + element),
    type: 'click',
    operands: { element: element, selector: selector, cssSelector: cssSelector },
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

function makeEvalFill(id, element, selector, cssSelector, value, action) {
  return {
    id: id,
    action: action || ('Fill ' + element + " with '" + value + "'"),
    type: 'fill',
    operands: { element: element, selector: selector, cssSelector: cssSelector, value: value },
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

// ---------------------------------------------------------------------------
// screenshot: true support
// ---------------------------------------------------------------------------

describe('generate() — screenshot capture (screenshot: true)', function() {
  test("step with screenshot: true emits agent-browser screenshot after action", function() {
    const step = makeClick('submit-login', 'login_button', 'role=button[name="Sign In"]');
    step.screenshot = true;
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('agent-browser screenshot "$_SCREENSHOT_DIR/submit-login.png"'),
      'Expected screenshot capture with step id filename. Got: ' + script
    );
  });

  test("step without screenshot does NOT emit screenshot command", function() {
    const step = makeClick('submit-login', 'login_button', 'role=button[name="Sign In"]');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      !script.includes('agent-browser screenshot "$_SCREENSHOT_DIR/submit-login.png"'),
      'Expected no screenshot capture. Got: ' + script
    );
  });

  test("screenshot failure is non-fatal (2>/dev/null || echo skipped)", function() {
    const step = makeSnapshot('verify-dash', 'Take snapshot');
    step.screenshot = true;
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('2>/dev/null || echo "(screenshot verify-dash skipped)"'),
      'Expected non-fatal screenshot with fallback echo. Got: ' + script
    );
  });
});

// ---------------------------------------------------------------------------
// eval-based click (cssSelector present)
// ---------------------------------------------------------------------------

describe('generate() — eval-based click (cssSelector)', function() {
  test("click with cssSelector emits agent-browser eval with querySelector.click()", function() {
    const step = makeEvalClick('click-submit', 'login_button', 'role=button[name="Sign In"]', 'button[type="submit"]');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('agent-browser eval "'),
      'Expected agent-browser eval command. Got: ' + script
    );
    assert.ok(
      script.includes('querySelector'),
      'Expected querySelector in eval. Got: ' + script
    );
    assert.ok(
      script.includes('button[type=\\"submit\\"]'),
      'Expected CSS selector in eval. Got: ' + script
    );
    assert.ok(
      script.includes('.click()'),
      'Expected .click() call in eval. Got: ' + script
    );
  });

  test("click with cssSelector has Playwright fallback", function() {
    const step = makeEvalClick('click-submit', 'login_button', 'role=button[name="Sign In"]', 'button[type="submit"]');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes("agent-browser click 'role=button[name=\"Sign In\"]'"),
      'Expected Playwright fallback click. Got: ' + script
    );
  });

  test("click with cssSelector does NOT have retry loop (eval + fallback instead)", function() {
    const step = makeEvalClick('click-submit', 'login_button', 'role=button[name="Sign In"]', 'button[type="submit"]');
    const script = generate(makeResolved([step]), 'test-flow');
    // eval-based click should not have while/retry loop — it uses eval + fallback
    assert.ok(
      !script.includes('while true; do'),
      'Expected no retry loop for eval-based click. Got: ' + script
    );
  });

  test("click without cssSelector still uses Playwright retry loop", function() {
    const step = makeClick('click-submit', 'login_button', 'role=button[name="Sign In"]');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('while true; do'),
      'Expected retry loop for Playwright click. Got: ' + script
    );
    assert.ok(
      !script.includes('agent-browser eval'),
      'Expected no eval command for Playwright click. Got: ' + script
    );
  });

  test("click with cssSelector still records step result and calls _handle_failure on fail", function() {
    const step = makeEvalClick('click-submit', 'login_button', 'role=button[name="Sign In"]', 'button[type="submit"]');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('_handle_failure "click-submit"') && script.includes('click action failed'),
      'Expected _handle_failure with click action failed. Got: ' + script
    );
  });
});

// ---------------------------------------------------------------------------
// eval-based fill (cssSelector present)
// ---------------------------------------------------------------------------

describe('generate() — eval-based fill (cssSelector)', function() {
  test("fill with cssSelector emits agent-browser eval with nativeInputValueSetter", function() {
    const step = makeEvalFill('fill-email', 'email_input', 'role=textbox[name="Email"]', 'input[name="email"]', 'test@example.com');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('agent-browser eval "'),
      'Expected agent-browser eval command. Got: ' + script
    );
    assert.ok(
      script.includes('nativeInputValueSetter') || script.includes('HTMLInputElement.prototype'),
      'Expected nativeInputValueSetter pattern. Got: ' + script
    );
    assert.ok(
      script.includes('input[name=\\"email\\"]'),
      'Expected CSS selector in eval. Got: ' + script
    );
    assert.ok(
      script.includes('test@example.com'),
      'Expected fill value in eval. Got: ' + script
    );
  });

  test("fill with cssSelector dispatches input and change events", function() {
    const step = makeEvalFill('fill-email', 'email_input', 'role=textbox[name="Email"]', 'input[name="email"]', 'test@example.com');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('dispatchEvent') && script.includes('input') && script.includes('change'),
      'Expected input + change event dispatch. Got: ' + script
    );
  });

  test("fill with cssSelector does NOT have retry loop", function() {
    const step = makeEvalFill('fill-email', 'email_input', 'role=textbox[name="Email"]', 'input[name="email"]', 'test@example.com');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      !script.includes('while true; do'),
      'Expected no retry loop for eval-based fill. Got: ' + script
    );
  });

  test("fill without cssSelector still uses Playwright retry loop", function() {
    const step = makeFill('fill-email', 'email_input', 'role=textbox[name="Email"]', 'test@example.com');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('while true; do'),
      'Expected retry loop for Playwright fill. Got: ' + script
    );
    assert.ok(
      !script.includes('agent-browser eval'),
      'Expected no eval command for Playwright fill. Got: ' + script
    );
  });

  test("fill with cssSelector records step result and calls _handle_failure on fail", function() {
    const step = makeEvalFill('fill-email', 'email_input', 'role=textbox[name="Email"]', 'input[name="email"]', 'test@example.com');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('_handle_failure "fill-email"') && script.includes('fill action failed'),
      'Expected _handle_failure with fill action failed. Got: ' + script
    );
  });

  test("fill with cssSelector uses IIFE to avoid const redeclaration", function() {
    const step = makeEvalFill('fill-email', 'email_input', 'role=textbox[name="Email"]', 'input[name="email"]', 'test@example.com');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('(()=>{') && script.includes('})()'),
      'Expected IIFE wrapper. Got: ' + script
    );
  });

  test("fill with cssSelector for password input (type selector)", function() {
    const step = makeEvalFill('fill-pass', 'password_input', 'role=textbox[name="Password"]', 'input[type="password"]', 'secret123');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('input[type=\\"password\\"]'),
      'Expected type=password CSS selector. Got: ' + script
    );
    assert.ok(
      script.includes('secret123'),
      'Expected password value in eval. Got: ' + script
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
  test("visible expect uses snapshot-based poll pattern (_poll_snapshot_contains for convertible selectors)", function() {
    const step = makeClick('click-btn', 'login_button', 'role=button[name="Sign In"]');
    step.expects = [{ type: 'active', raw: 'login_button is visible', elementName: 'login_button', selector: 'role=button[name="Sign In"]' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes("_poll_snapshot_contains 'button \"Sign In\"'"),
      'Expected _poll_snapshot_contains for convertible role selector. Got: ' + script
    );
  });

  test("visible expect uses status-aware _handle_failure paths (no inline exit 1)", function() {
    const step = makeClick('click-btn', 'login_button', 'role=button[name="Sign In"]');
    step.expects = [{ type: 'active', raw: 'login_button is visible', elementName: 'login_button', selector: 'role=button[name="Sign In"]' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('if _poll_snapshot_contains') &&
        script.includes('if [ "$_probe_status" -eq 2 ]') &&
        script.includes('_handle_failure "click-btn"'),
      'Expected status-aware _handle_failure paths. Got: ' + script
    );
  });

  test("visible expect FAIL message names the element (via _handle_failure)", function() {
    const step = makeClick('click-btn', 'login_button', 'role=button[name="Sign In"]');
    step.expects = [{ type: 'active', raw: 'login_button is visible', elementName: 'login_button', selector: 'role=button[name="Sign In"]' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('login_button not in a11y tree'),
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

  test("script emits _HAD_RETRIES=false default", function() {
    const steps = [makeNavigate('nav', '/home')];
    const script = generate(makeResolved(steps, 'f'), 'f');
    assert.ok(script.includes('_HAD_RETRIES=false'), 'Expected _HAD_RETRIES=false default');
  });

  test("retry branch sets _HAD_RETRIES=true before RETRY echo", function() {
    const steps = [makeNavigate('nav', '/home')];
    const script = generate(makeResolved(steps, 'f'), 'f');
    const retryIdx = script.indexOf('_HAD_RETRIES=true');
    const echoIdx = script.indexOf('echo "RETRY');
    assert.ok(retryIdx > -1, 'Expected _HAD_RETRIES=true in retry branch');
    assert.ok(retryIdx < echoIdx, '_HAD_RETRIES=true must come before RETRY echo');
  });

  test("footer emits PASS (FLAKY) when _HAD_RETRIES is true", function() {
    const steps = [makeNavigate('nav', '/home')];
    const script = generate(makeResolved(steps, 'f'), 'f');
    assert.ok(
      script.includes('if [ "$_HAD_RETRIES" = "true" ]; then'),
      'Expected flaky check in footer'
    );
    assert.ok(
      script.includes('echo "PASS (FLAKY): f ('),
      'Expected PASS (FLAKY) branch in footer'
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
  test("element-visible uses _poll_snapshot_contains for convertible selectors", function() {
    const step = makeClick('click-btn', 'login_button', 'role=button[name="Sign In"]');
    step.expects = [{ type: 'element-visible', raw: 'login_button visible', elementName: 'login_button', selector: 'role=button[name="Sign In"]' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes("_poll_snapshot_contains 'button \"Sign In\"'"),
      'element-visible should use _poll_snapshot_contains. Got: ' + script
    );
  });

  test("element-visible uses status-aware _handle_failure paths (no inline exit 1)", function() {
    const step = makeClick('click-btn', 'login_button', 'role=button[name="Sign In"]');
    step.expects = [{ type: 'element-visible', raw: 'login_button visible', elementName: 'login_button', selector: 'role=button[name="Sign In"]' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('if _poll_snapshot_contains') &&
        script.includes('if [ "$_probe_status" -eq 2 ]') &&
        script.includes('_handle_failure "click-btn"'),
      'element-visible must use status-aware _handle_failure paths. Got: ' + script
    );
  });

  test("element-visible FAIL message names element and step id", function() {
    const step = makeClick('click-btn', 'login_button', 'role=button[name="Sign In"]');
    step.expects = [{ type: 'element-visible', raw: 'login_button visible', elementName: 'login_button', selector: 'role=button[name="Sign In"]' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('login_button not in a11y tree'),
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

  test("element-not-visible uses status-aware _handle_failure paths", function() {
    const step = makeSnapshot('check-dialog', 'Take snapshot');
    step.expects = [{ type: 'element-not-visible', raw: 'dialog not visible', elementName: 'dialog', selector: 'role=dialog' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('if [ "$_probe_status" -eq 2 ]; then') &&
        script.includes('_handle_failure "check-dialog" ' + singleQuote('agent-browser visibility probe failed for dialog')),
      'element-not-visible must distinguish infrastructure failure. Got: ' + script
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

  test("url-contains uses status-aware _handle_failure paths with step id", function() {
    const step = makeNavigate('nav-dashboard', '/dashboard');
    step.expects = [{ type: 'url-contains', raw: 'url contains /dashboard', value: '/dashboard' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('if _poll_url_contains') &&
        script.includes('if [ "$_probe_status" -eq 2 ]') &&
        script.includes('_handle_failure "nav-dashboard"'),
      'url-contains must use status-aware _handle_failure paths. Got: ' + script
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
  test("url-not-contains uses _poll_url_not_contains helper (polls for redirect)", function() {
    const step = makeNavigate('submit-login', '/login');
    step.expects = [{ type: 'url-not-contains', raw: 'url does not contain /login', value: '/login' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes("_poll_url_not_contains '/login'"),
      'url-not-contains must use _poll_url_not_contains helper. Got: ' + script
    );
  });

  test("url-not-contains passes step id and timeout to poll helper", function() {
    const step = makeNavigate('submit-login', '/login');
    step.expects = [{ type: 'url-not-contains', raw: 'url does not contain /login', value: '/login' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('_poll_url_not_contains \'/login\' "submit-login"'),
      'url-not-contains must pass step id to poll helper. Got: ' + script
    );
  });

  test("url-not-contains FAIL message says 'url still contains X after Ns' (via _handle_failure)", function() {
    const step = makeNavigate('submit-login', '/login');
    step.expects = [{ type: 'url-not-contains', raw: 'url does not contain /login', value: '/login' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('url still contains /login after'),
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
      script.includes("if ! _snapshot=$(_capture_snapshot ''); then"),
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
      script.includes("elif ! echo \"$_snapshot\" | grep -qF"),
      'text-visible must use if ! pattern for failure detection. Got: ' + script
    );
  });

  test("text-visible FAIL message names the text and step id (via _handle_failure)", function() {
    const step = makeSnapshot('verify-text', 'Take snapshot');
    step.expects = [{ type: 'text-visible', raw: "text '每日看板' on page", text: '每日看板' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('_handle_failure "verify-text" ' + singleQuote("text '每日看板' not found on page")),
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

describe('generateExpects() — text-not-visible', function() {
  test("text-not-visible generates agent-browser snapshot capture", function() {
    const step = makeSnapshot('verify-text-absent', 'Take snapshot');
    step.expects = [{ type: 'text-not-visible', raw: "text 'Sign-in failed' not on page", text: 'Sign-in failed' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes("if ! _snapshot=$(_capture_snapshot ''); then"),
      'text-not-visible must capture snapshot. Got: ' + script
    );
  });

  test("text-not-visible uses grep -qF for fixed-string matching (CJK safe)", function() {
    const step = makeSnapshot('verify-text-absent', 'Take snapshot');
    step.expects = [{ type: 'text-not-visible', raw: "text '每日看板' not on page", text: '每日看板' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes("grep -qF '每日看板'"),
      'text-not-visible must use grep -qF for fixed string match. Got: ' + script
    );
  });

  test("text-not-visible uses inverted if pattern (fail when text IS found)", function() {
    const step = makeSnapshot('verify-text-absent', 'Take snapshot');
    step.expects = [{ type: 'text-not-visible', raw: "text 'Sign-in failed' not on page", text: 'Sign-in failed' }];
    const script = generate(makeResolved([step]), 'test-flow');
    // inverted: positive grep (no leading `!`); failure when grep DOES find the text
    assert.ok(
      script.includes('elif echo "$_snapshot" | grep -qF'),
      'text-not-visible must use positive `if echo ... | grep -qF` pattern (no leading !). Got: ' + script
    );
    assert.ok(
      !script.includes('elif ! echo "$_snapshot" | grep -qF \'Sign-in failed\''),
      'text-not-visible must NOT use `if !` (that is the positive text-visible pattern). Got: ' + script
    );
  });

  test("text-not-visible FAIL message names the text, step id, and 'should NOT' phrasing (via _handle_failure)", function() {
    const step = makeSnapshot('verify-text-absent', 'Take snapshot');
    step.expects = [{ type: 'text-not-visible', raw: "text 'Sign-in failed' not on page", text: 'Sign-in failed' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('_handle_failure "verify-text-absent"'),
      'text-not-visible FAIL must dispatch via _handle_failure. Got: ' + script
    );
    assert.ok(
      script.includes(singleQuote("text 'Sign-in failed' should NOT be on page but was found")),
      'text-not-visible FAIL message must include "should NOT be on page but was found". Got: ' + script
    );
  });

  test("text-not-visible with ASCII double-quoted text works correctly", function() {
    const step = makeSnapshot('verify-title-absent', 'Take snapshot');
    step.expects = [{ type: 'text-not-visible', raw: 'text "Dashboard" not visible', text: 'Dashboard' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes("grep -qF 'Dashboard'"),
      'text-not-visible with ASCII text uses grep -qF. Got: ' + script
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
      script.includes("agent-browser --session 'office' open"),
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
      script.includes("agent-browser --session 'app' click"),
      'cross-site click must use --session prefix. Got: ' + script
    );
  });

  test("snapshot with session field uses --session prefix", function() {
    const step = makeCrossSiteSnapshot('office-snap', 'office');
    const script = generate(makeResolved([step]), 'cross-site-test');
    assert.ok(
      script.includes("agent-browser --session 'office' snapshot"),
      'cross-site snapshot must use --session prefix. Got: ' + script
    );
  });

  test("expect with session field on step uses _poll_snapshot_contains for convertible selectors", function() {
    const step = makeCrossSiteSnapshot('office-check', 'office');
    step.expects = [{
      type: 'active',
      raw: 'heading_a is visible',
      elementName: 'heading_a',
      selector: 'role=heading[name="Office Dashboard"]',
    }];
    const script = generate(makeResolved([step]), 'cross-site-test');
    // Snapshot-based check: _poll_snapshot_contains replaces _poll_visible for convertible selectors
    assert.ok(
      script.includes("_poll_snapshot_contains 'heading \"Office Dashboard\"'"),
      'cross-site expect must use _poll_snapshot_contains for convertible selector. Got: ' + script
    );
  });

  test("step without session field uses _poll_snapshot_contains for convertible selectors", function() {
    const step = makeClick('click-btn', 'login_button', 'role=button[name="Sign In"]');
    step.expects = [{
      type: 'active',
      raw: 'login_button is visible',
      elementName: 'login_button',
      selector: 'role=button[name="Sign In"]',
    }];
    const script = generate(makeResolved([step]), 'test-flow');
    // Snapshot-based check doesn't need session arg (global snapshot)
    assert.ok(
      script.includes("_poll_snapshot_contains 'button \"Sign In\"'"),
      'single-site expect must use _poll_snapshot_contains. Got: ' + script
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

  test("_poll_url_not_contains() function is emitted in compiled output", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('_poll_url_not_contains()'),
      'Expected _poll_url_not_contains() function definition. Got: ' + script.slice(0, 500)
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
      pollBody.includes('false) return 0'),
      'Expected _poll_not_visible to check for "false" return. Got body: ' + pollBody
    );
  });

  test("_poll_url_contains uses the shared status-safe URL capture", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    const pollStart = script.indexOf('_poll_url_contains()');
    const pollEnd = script.indexOf('\n}', pollStart);
    const pollBody = script.slice(pollStart, pollEnd + 2);
    assert.ok(
      pollBody.includes('_capture_url "$_session"'),
      'Expected _poll_url_contains to use _capture_url. Got body: ' + pollBody
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
  test("active expect compiles to _poll_snapshot_contains for convertible selectors", function() {
    const step = makeClick('click-btn', 'login_button', 'role=button[name="Sign In"]');
    step.expects = [{ type: 'active', raw: 'login_button is visible', elementName: 'login_button', selector: 'role=button[name="Sign In"]' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes("_poll_snapshot_contains 'button \"Sign In\"'"),
      'active expect must compile to _poll_snapshot_contains. Got: ' + script
    );
  });

  test("element-visible expect compiles to _poll_snapshot_contains for convertible selectors", function() {
    const step = makeClick('click-btn', 'login_button', 'role=button[name="Sign In"]');
    step.expects = [{ type: 'element-visible', raw: 'login_button visible', elementName: 'login_button', selector: 'role=button[name="Sign In"]' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes("_poll_snapshot_contains 'button \"Sign In\"'"),
      'element-visible expect must compile to _poll_snapshot_contains. Got: ' + script
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

  test("url-not-contains uses _poll_url_not_contains (distinct from _poll_url_contains)", function() {
    const step = makeNavigate('submit-login', '/login');
    step.expects = [{ type: 'url-not-contains', raw: 'url does not contain /login', value: '/login' }];
    const script = generate(makeResolved([step]), 'test-flow');
    const stepSection = script.slice(script.indexOf('[1/1]'), script.indexOf('# Exit summary'));
    // Must use the _not_ variant, not the positive _poll_url_contains
    assert.ok(
      stepSection.includes('_poll_url_not_contains'),
      'url-not-contains must use _poll_url_not_contains helper. Got section: ' + stepSection
    );
    assert.ok(
      !stepSection.includes('_poll_url_contains '),
      'url-not-contains must NOT call _poll_url_contains (positive variant). Got section: ' + stepSection
    );
  });

  test("text-visible expect does NOT use poll (snapshot is too heavy for polling)", function() {
    const step = makeSnapshot('verify-text', 'Take snapshot');
    step.expects = [{ type: 'text-visible', raw: "text '每日看板' on page", text: '每日看板' }];
    const script = generate(makeResolved([step]), 'test-flow');
    // text-visible stays as instant snapshot + grep (no poll)
    assert.ok(
      script.includes("if ! _snapshot=$(_capture_snapshot ''); then"),
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

  test("active expect uses status-aware _handle_failure paths (no inline exit 1)", function() {
    const step = makeClick('click-btn', 'login_button', 'role=button[name="Sign In"]');
    step.expects = [{ type: 'active', raw: 'login_button is visible', elementName: 'login_button', selector: 'role=button[name="Sign In"]' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('if _poll_snapshot_contains') &&
        script.includes('if [ "$_probe_status" -eq 2 ]') &&
        script.includes('_handle_failure "click-btn"'),
      'Expected status-aware _handle_failure paths. Got: ' + script
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
      script.includes('login_button not in a11y tree'),
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
    // Snapshot-based check: _poll_snapshot_contains for convertible selector
    assert.ok(
      script.includes("_poll_snapshot_contains 'heading \"Office Dashboard\"'"),
      'Cross-site active expect must use _poll_snapshot_contains for convertible selector. Got: ' + script
    );
  });
});

// ---------------------------------------------------------------------------
// Phase 4 Plan 03: BASE_URL normalization and trap cleanup EXIT (CODEGEN-03 + CI-06)
// ---------------------------------------------------------------------------

describe('v2.0 BASE_URL normalization and cleanup', function() {

  // --- BASE_URL normalization tests ---

  test("single-site compiled output contains BASE_URL normalization line", function() {
    const resolved = {
      name: 'test-login',
      description: 'Test',
      variables: { base_url: 'http://localhost:3000' },
      steps: [makeNavigate('nav', '/login')],
    };
    const script = generate(resolved, 'test-login');
    assert.ok(
      script.includes('BASE_URL="${BASE_URL%/}"'),
      'Expected BASE_URL normalization line. Got snippet: ' + script.slice(0, 600)
    );
  });

  test("cross-site compiled output contains per-site BASE_URL normalization lines", function() {
    function makeCrossSiteStep(id, site, urlPath) {
      return {
        id: id, action: 'Navigate to ' + urlPath, type: 'navigate', session: site,
        operands: { target: urlPath, urlPath: urlPath },
      };
    }
    const resolved = {
      name: 'cross-site-test',
      description: 'Cross-site test',
      variables: { OFFICE_BASE_URL: 'http://localhost:5173', APP_BASE_URL: 'http://localhost:8081' },
      steps: [
        makeCrossSiteStep('office-nav', 'office', '/dashboard'),
        makeCrossSiteStep('app-nav', 'app', '/home'),
      ],
    };
    const script = generate(resolved, 'cross-site-test');
    assert.ok(
      script.includes('OFFICE_BASE_URL="${OFFICE_BASE_URL%/}"'),
      'Expected OFFICE_BASE_URL normalization. Got snippet: ' + script.slice(0, 800)
    );
    assert.ok(
      script.includes('APP_BASE_URL="${APP_BASE_URL%/}"'),
      'Expected APP_BASE_URL normalization. Got snippet: ' + script.slice(0, 800)
    );
  });

  test("BASE_URL normalization appears AFTER variable assignment block", function() {
    const resolved = {
      name: 'test-login',
      description: 'Test',
      variables: { base_url: 'http://localhost:3000' },
      steps: [makeNavigate('nav', '/login')],
    };
    const script = generate(resolved, 'test-login');
    const varIdx = script.indexOf('BASE_URL="${1:-');
    const normIdx = script.indexOf('BASE_URL="${BASE_URL%/}"');
    assert.ok(varIdx !== -1, 'Missing variable assignment block');
    assert.ok(normIdx !== -1, 'Missing BASE_URL normalization line');
    assert.ok(varIdx < normIdx, 'Normalization must appear AFTER variable assignment. varIdx=' + varIdx + ' normIdx=' + normIdx);
  });

  test("BASE_URL normalization appears BEFORE runtime support functions", function() {
    const resolved = {
      name: 'test-login',
      description: 'Test',
      variables: { base_url: 'http://localhost:3000' },
      steps: [makeNavigate('nav', '/login')],
    };
    const script = generate(resolved, 'test-login');
    const normIdx = script.indexOf('BASE_URL="${BASE_URL%/}"');
    const supportIdx = script.indexOf('_handle_failure()');
    assert.ok(normIdx !== -1, 'Missing BASE_URL normalization');
    assert.ok(supportIdx !== -1, 'Missing _handle_failure function');
    assert.ok(normIdx < supportIdx, 'Normalization must appear BEFORE runtime support. normIdx=' + normIdx + ' supportIdx=' + supportIdx);
  });

  test("non-base-url variables do NOT get %/ normalization", function() {
    const resolved = {
      name: 'test-login',
      description: 'Test',
      variables: { base_url: 'http://localhost:3000', user_email: 'test@example.com' },
      steps: [makeNavigate('nav', '/login')],
    };
    const script = generate(resolved, 'test-login');
    // USER_EMAIL should NOT have a normalization line
    assert.ok(
      !script.includes('USER_EMAIL="${USER_EMAIL%/}"'),
      'Non-base-url variable USER_EMAIL must not get normalization. Got snippet: ' + script.slice(0, 800)
    );
  });

  // --- Trap cleanup tests ---

  test("single-site compiled output contains cleanup() function with agent-browser close", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('cleanup()'),
      'Expected cleanup() function definition. Got snippet: ' + script.slice(0, 800)
    );
    assert.ok(
      script.includes('agent-browser close 2>/dev/null || true'),
      'Expected agent-browser close in cleanup. Got snippet: ' + script.slice(0, 800)
    );
  });

  test("compiled output contains trap cleanup EXIT line", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('trap cleanup EXIT'),
      'Expected trap cleanup EXIT. Got snippet: ' + script.slice(0, 800)
    );
  });

  test("trap cleanup EXIT appears BEFORE first step block", function() {
    const step = makeNavigate('nav', '/login');
    const script = generate(makeResolved([step]), 'test-flow');
    const trapIdx = script.indexOf('trap cleanup EXIT');
    const stepIdx = script.indexOf('echo "[1/1]');
    assert.ok(trapIdx !== -1, 'Missing trap cleanup EXIT');
    assert.ok(stepIdx !== -1, 'Missing first step echo');
    assert.ok(trapIdx < stepIdx, 'trap must appear BEFORE first step. trapIdx=' + trapIdx + ' stepIdx=' + stepIdx);
  });

  test("trap cleanup EXIT appears AFTER runtime support functions", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    const supportIdx = script.indexOf('_handle_failure()');
    const trapIdx = script.indexOf('trap cleanup EXIT');
    assert.ok(supportIdx !== -1, 'Missing _handle_failure function');
    assert.ok(trapIdx !== -1, 'Missing trap cleanup EXIT');
    assert.ok(supportIdx < trapIdx, 'trap must appear AFTER runtime support. supportIdx=' + supportIdx + ' trapIdx=' + trapIdx);
  });

  test("cross-site cleanup function closes all named sessions", function() {
    function makeCrossSiteStep(id, site, urlPath) {
      return {
        id: id, action: 'Navigate to ' + urlPath, type: 'navigate', session: site,
        operands: { target: urlPath, urlPath: urlPath },
      };
    }
    const resolved = {
      name: 'cross-site-test',
      description: 'Cross-site test',
      variables: { OFFICE_BASE_URL: 'http://localhost:5173', APP_BASE_URL: 'http://localhost:8081' },
      steps: [
        makeCrossSiteStep('office-nav', 'office', '/dashboard'),
        makeCrossSiteStep('app-nav', 'app', '/home'),
      ],
    };
    const script = generate(resolved, 'cross-site-test');
    assert.ok(
      script.includes("agent-browser --session 'office' close 2>/dev/null || true"),
      'Expected --session office close in cross-site cleanup. Got snippet: ' + script.slice(0, 1000)
    );
    assert.ok(
      script.includes("agent-browser --session 'app' close 2>/dev/null || true"),
      'Expected --session app close in cross-site cleanup. Got snippet: ' + script.slice(0, 1000)
    );
  });

  test("single-site cleanup has only default session close (no --session flag)", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    // Extract cleanup function body
    const cleanupStart = script.indexOf('cleanup()');
    const cleanupEnd = script.indexOf('\n}', cleanupStart);
    const cleanupBody = script.slice(cleanupStart, cleanupEnd + 2);
    assert.ok(
      !cleanupBody.includes('--session'),
      'Single-site cleanup must NOT have --session flag. Got cleanup body: ' + cleanupBody
    );
    assert.ok(
      cleanupBody.includes('agent-browser close'),
      'Single-site cleanup must have plain agent-browser close. Got cleanup body: ' + cleanupBody
    );
  });

  test("cleanup function uses || true to prevent cleanup failure from overriding exit code", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    const cleanupStart = script.indexOf('cleanup()');
    const cleanupEnd = script.indexOf('\n}', cleanupStart);
    const cleanupBody = script.slice(cleanupStart, cleanupEnd + 2);
    assert.ok(
      cleanupBody.includes('|| true'),
      'cleanup must use || true on close commands. Got cleanup body: ' + cleanupBody
    );
  });
});

// ---------------------------------------------------------------------------
// Phase 5 Plan 01: v2.0 JUnit XML codegen (FLAG-01)
// ---------------------------------------------------------------------------

const { xmlAttrEscape } = require('../codegen.js');

describe('v2.0 JUnit XML codegen (FLAG-01) — --junit flag in runtime flag block', function() {
  test("compiled output contains JUNIT_OUTPUT=\"\" default", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('JUNIT_OUTPUT=""'),
      'Expected JUNIT_OUTPUT="" default. Got snippet: ' + script.slice(0, 500)
    );
  });

  test("compiled output contains --junit) case handler", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('--junit)'),
      'Expected --junit) case in flag block. Got snippet: ' + script.slice(0, 600)
    );
  });

  test("--junit case sets JUNIT_OUTPUT to $2 and shift 2", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('JUNIT_OUTPUT="$2"'),
      'Expected JUNIT_OUTPUT="$2" in --junit case. Got snippet: ' + script.slice(0, 600)
    );
  });
});

describe('v2.0 JUnit XML codegen (FLAG-01) — step bookkeeping arrays', function() {
  test("compiled output contains _STEP_NAMES=() array", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('_STEP_NAMES=()'),
      'Expected _STEP_NAMES=() array init. Got snippet: ' + script.slice(0, 600)
    );
  });

  test("compiled output contains _STEP_RESULTS=() array", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('_STEP_RESULTS=()'),
      'Expected _STEP_RESULTS=() array init. Got snippet: ' + script.slice(0, 600)
    );
  });

  test("compiled output contains _STEP_FAILURES=() array", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('_STEP_FAILURES=()'),
      'Expected _STEP_FAILURES=() array init. Got snippet: ' + script.slice(0, 600)
    );
  });

  test("compiled output contains _STEP_TIMES=() array", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('_STEP_TIMES=()'),
      'Expected _STEP_TIMES=() array init. Got snippet: ' + script.slice(0, 600)
    );
  });

  test("compiled output contains _FLOW_START=$SECONDS", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('_FLOW_START=$SECONDS'),
      'Expected _FLOW_START=$SECONDS. Got snippet: ' + script.slice(0, 600)
    );
  });
});

describe('v2.0 JUnit XML codegen (FLAG-01) — per-step timing bookkeeping (navigate)', function() {
  test("navigate action block contains _STEP_START=$SECONDS before action", function() {
    const step = makeNavigate('nav-login', '/login');
    const script = generate(makeResolved([step]), 'test-flow');
    // _STEP_START must appear before the agent-browser open command
    const stepStartIdx = script.indexOf('_STEP_START=$SECONDS');
    const navIdx = script.indexOf('agent-browser open');
    assert.ok(stepStartIdx !== -1, 'Missing _STEP_START=$SECONDS in navigate block');
    assert.ok(navIdx !== -1, 'Missing agent-browser open command');
    assert.ok(stepStartIdx < navIdx, '_STEP_START must appear before agent-browser open. stepStartIdx=' + stepStartIdx + ' navIdx=' + navIdx);
  });

  test("navigate success path records raw and format-specific step identities", function() {
    const step = makeNavigate('nav-login', '/login');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('_record_step_name "nav-login" "nav-login" "nav-login"'),
      'Expected raw, JSON, and XML step identity arguments. Got snippet: ' + script
    );
  });

  test("navigate success path records pass result in _STEP_RESULTS", function() {
    const step = makeNavigate('nav-login', '/login');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('_STEP_RESULTS+=("pass")'),
      'Expected _STEP_RESULTS+=("pass") in navigate success path. Got snippet: ' + script
    );
  });

  test("navigate success path records empty failure in _STEP_FAILURES", function() {
    const step = makeNavigate('nav-login', '/login');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('_STEP_FAILURES+=("")'),
      'Expected _STEP_FAILURES+=("") in navigate success path. Got snippet: ' + script
    );
  });

  test("navigate block computes elapsed time with $(( SECONDS - _STEP_START ))", function() {
    const step = makeNavigate('nav-login', '/login');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('_elapsed=$(( SECONDS - _STEP_START ))') || script.includes('_elapsed=$(($SECONDS - $_STEP_START))') || script.includes('_elapsed=$(( SECONDS - _STEP_START))'),
      'Expected _elapsed=$(( SECONDS - _STEP_START )) in navigate block. Got snippet: ' + script
    );
  });
});

describe('v2.0 JUnit XML codegen (FLAG-01) — per-step timing bookkeeping (click)', function() {
  test("click action block contains _STEP_START=$SECONDS before action", function() {
    const step = makeClick('click-btn', 'login_button', 'role=button[name="Sign In"]');
    const script = generate(makeResolved([step]), 'test-flow');
    const stepStartIdx = script.indexOf('_STEP_START=$SECONDS');
    const clickIdx = script.indexOf('agent-browser click');
    assert.ok(stepStartIdx !== -1, 'Missing _STEP_START=$SECONDS in click block');
    assert.ok(clickIdx !== -1, 'Missing agent-browser click command');
    assert.ok(stepStartIdx < clickIdx, '_STEP_START must appear before agent-browser click');
  });

  test("click success path records pass result in _STEP_RESULTS", function() {
    const step = makeClick('click-btn', 'login_button', 'role=button[name="Sign In"]');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('_STEP_RESULTS+=("pass")'),
      'Expected _STEP_RESULTS+=("pass") in click success path. Got snippet: ' + script
    );
  });
});

describe('v2.0 JUnit XML codegen (FLAG-01) — per-step timing bookkeeping (verify-external skip)', function() {
  test("verify-external step records skip result in _STEP_RESULTS", function() {
    const step = makeVerifyExternal('verify-ext');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('_STEP_RESULTS+=("skip")'),
      'Expected _STEP_RESULTS+=("skip") for verify-external. Got snippet: ' + script
    );
  });

  test("verify-external step records time 0 in _STEP_TIMES", function() {
    const step = makeVerifyExternal('verify-ext');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('_STEP_TIMES+=("0")'),
      'Expected _STEP_TIMES+=("0") for verify-external. Got snippet: ' + script
    );
  });
});

describe('v2.0 JUnit XML codegen (FLAG-01) — _handle_failure records to _STEP_FAILURES', function() {
  test("_handle_failure contains ANSI strip pattern (sed)", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes("sed 's/\\x1b\\[[0-9;]*m//g'") || script.includes("sed 's/\\x1b"),
      'Expected ANSI strip sed pattern in _handle_failure. Got snippet: ' + script.slice(script.indexOf('_handle_failure()'), script.indexOf('_handle_failure()') + 300)
    );
  });

  test("_handle_failure preserves control characters for format-specific report encoders", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    const fnStart = script.indexOf('_handle_failure()');
    const fnEnd = script.indexOf('\n}', fnStart);
    const fnBody = script.slice(fnStart, fnEnd + 2);
    assert.ok(
      !fnBody.includes('tr -d') && script.includes('_json_escape()') && script.includes('_xml_attr_escape()'),
      'Expected report encoders to own control-character handling. Got fn body: ' + fnBody
    );
  });

  test("_handle_failure overwrites last _STEP_FAILURES and _STEP_RESULTS entries", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    const fnStart = script.indexOf('_handle_failure()');
    const fnEnd = script.indexOf('\n}', fnStart);
    const fnBody = script.slice(fnStart, fnEnd + 2);
    assert.ok(
      fnBody.includes('_STEP_FAILURES[$_last_idx]'),
      'Expected _STEP_FAILURES[$_last_idx]= (overwrite) inside _handle_failure. Got fn body: ' + fnBody
    );
    assert.ok(
      fnBody.includes('_STEP_RESULTS[$_last_idx]="fail"'),
      'Expected _STEP_RESULTS[$_last_idx]="fail" (overwrite) inside _handle_failure. Got fn body: ' + fnBody
    );
  });
});

describe('v2.0 JUnit XML codegen (FLAG-01) — _emit_junit function in compiled output', function() {
  test("compiled output contains _emit_junit() function definition", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('_emit_junit()'),
      'Expected _emit_junit() function definition. Got snippet: ' + script.slice(0, 800)
    );
  });

  test("_emit_junit function writes XML declaration", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    const emitStart = script.indexOf('_emit_junit()');
    const emitEnd = script.indexOf('\n}', emitStart);
    const emitBody = script.slice(emitStart, emitEnd + 2);
    assert.ok(
      emitBody.includes('<?xml') || emitBody.includes('xml version'),
      'Expected XML declaration in _emit_junit function. Got body: ' + emitBody
    );
  });

  test("_emit_junit function writes testsuites element", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    const emitStart = script.indexOf('_emit_junit()');
    const emitEnd = script.indexOf('\n}', emitStart);
    const emitBody = script.slice(emitStart, emitEnd + 2);
    assert.ok(
      emitBody.includes('testsuites') || emitBody.includes('<testsuites'),
      'Expected testsuites element in _emit_junit function. Got body: ' + emitBody
    );
  });

  test("_emit_junit function writes testsuite element", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    const emitStart = script.indexOf('_emit_junit()');
    const emitEnd = script.indexOf('\n}', emitStart);
    const emitBody = script.slice(emitStart, emitEnd + 2);
    assert.ok(
      emitBody.includes('testsuite') || emitBody.includes('<testsuite'),
      'Expected testsuite element in _emit_junit function. Got body: ' + emitBody
    );
  });

  test("_emit_junit function writes testcase element", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    const emitStart = script.indexOf('_emit_junit()');
    const emitEnd = script.indexOf('\n}', emitStart);
    const emitBody = script.slice(emitStart, emitEnd + 2);
    assert.ok(
      emitBody.includes('testcase') || emitBody.includes('<testcase'),
      'Expected testcase element in _emit_junit function. Got body: ' + emitBody
    );
  });

  test("footer calls _emit_junit when JUNIT_OUTPUT is non-empty", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('_emit_junit "$JUNIT_OUTPUT"') || script.includes('_emit_junit'),
      'Expected _emit_junit call in footer. Got snippet: ' + script.slice(-500)
    );
    assert.ok(
      script.includes('if [ -n "$JUNIT_OUTPUT" ]'),
      'Expected conditional _emit_junit call based on JUNIT_OUTPUT. Got snippet: ' + script.slice(-500)
    );
  });
});

describe('v2.0 JUnit XML codegen (FLAG-01) — xmlAttrEscape', function() {
  test("xmlAttrEscape replaces NUL and XML-illegal C0 controls", function() {
    const illegal = String.fromCharCode(
      0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
      0x0b, 0x0c,
      0x0e, 0x0f, 0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17,
      0x18, 0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f
    );
    assert.equal(xmlAttrEscape(illegal), '\ufffd'.repeat(29));
  });

  test("xmlAttrEscape escapes < as &lt;", function() {
    const result = xmlAttrEscape('a<b');
    assert.ok(
      result.includes('&lt;'),
      'Expected &lt; for < character. Got: ' + result
    );
  });

  test("xmlAttrEscape escapes > as &gt;", function() {
    const result = xmlAttrEscape('a>b');
    assert.ok(
      result.includes('&gt;'),
      'Expected &gt; for > character. Got: ' + result
    );
  });

  test("xmlAttrEscape escapes & as &amp;", function() {
    const result = xmlAttrEscape('a&b');
    assert.ok(
      result.includes('&amp;'),
      'Expected &amp; for & character. Got: ' + result
    );
  });

  test("xmlAttrEscape escapes \" as &quot;", function() {
    const result = xmlAttrEscape('a"b');
    assert.ok(
      result.includes('&quot;'),
      'Expected &quot; for " character. Got: ' + result
    );
  });

  test("xmlAttrEscape passes through normal ASCII text unchanged", function() {
    const result = xmlAttrEscape('normal text');
    assert.equal(result, 'normal text', 'Expected normal text unchanged');
  });

  test("xmlAttrEscape returns empty string for empty input", function() {
    const result = xmlAttrEscape('');
    assert.equal(result, '', 'Expected empty string for empty input');
  });

  test("xmlAttrEscape passes CJK characters through as UTF-8 (not numeric entities)", function() {
    const result = xmlAttrEscape('登入頁面');
    assert.ok(
      result.includes('登入頁面'),
      'Expected CJK characters to pass through as UTF-8. Got: ' + result
    );
    assert.ok(
      !result.includes('&#'),
      'CJK must not be encoded as numeric entities. Got: ' + result
    );
  });
});

describe('v2.0 JUnit XML codegen (FLAG-01) — CJK step identity encoding', function() {
  test("flow with CJK step ID keeps UTF-8 in raw, JSON, and XML forms", function() {
    const step = {
      id: '登入頁面',
      action: 'Navigate to login',
      type: 'navigate',
      operands: { target: '/login', urlPath: '/login' },
    };
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('_record_step_name "登入頁面" "登入頁面" "登入頁面"'),
      'Expected CJK step id as UTF-8 in all identity forms. Got snippet: ' + script
    );
    const recordLine = script.split('\n').find(line => line.includes('_record_step_name "登入頁面"'));
    assert.ok(recordLine && !recordLine.includes('&#'), 'CJK step identity must not use numeric entities. Got: ' + recordLine);
  });
});

describe('v2.0 JUnit XML codegen (FLAG-01) — format-specific step identity encoding', function() {
  test("flow with angle bracket step ID keeps raw identity and XML-escapes only the XML form", function() {
    const step = {
      id: 'check-<input>-field',
      action: 'Check input field',
      type: 'navigate',
      operands: { target: '/form', urlPath: '/form' },
    };
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes(
        '_record_step_name "check-<input>-field" "check-<input>-field" "check-&lt;input&gt;-field"'
      ),
      'Expected raw/JSON identity plus XML-specific escaping. Got snippet: ' + script
    );
  });
});

describe('v2.0 JUnit XML codegen (FLAG-01) — --junit omitted preserves v1.0 behavior', function() {
  test("JUNIT_OUTPUT=\"\" is the default (no --junit = empty string)", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('JUNIT_OUTPUT=""'),
      'Expected JUNIT_OUTPUT="" default for v1.0 compat. Got snippet: ' + script.slice(0, 400)
    );
  });

  test("footer has conditional _emit_junit (no-op when JUNIT_OUTPUT is empty)", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('if [ -n "$JUNIT_OUTPUT" ]'),
      'Expected conditional check before _emit_junit call. Got snippet: ' + script.slice(-500)
    );
  });

  test("step bookkeeping arrays are always emitted regardless of --junit", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    // Arrays present even without --junit (overhead is negligible)
    assert.ok(
      script.includes('_STEP_NAMES=()') &&
      script.includes('_STEP_RESULTS=()') &&
      script.includes('_STEP_FAILURES=()') &&
      script.includes('_STEP_TIMES=()'),
      'All step bookkeeping arrays must always be emitted. Got snippet: ' + script.slice(0, 600)
    );
  });
});

describe('v2.0 JUnit XML codegen (FLAG-01) — --junit empty-path guard (Pitfall 5)', function() {
  test("compiled output contains empty-path guard in --junit case", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('echo "ERROR: --junit requires a path argument"'),
      'Expected ERROR message for empty --junit path. Got snippet: ' + script.slice(0, 700)
    );
  });

  test("empty-path guard exits 1 when JUNIT_OUTPUT is empty after --junit flag", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'test-flow');
    // The --junit case block must have an exit 1 guard for empty path
    const junitCaseIdx = script.indexOf('--junit)');
    const junitCaseEnd = script.indexOf(';;', junitCaseIdx);
    const junitCaseBlock = script.slice(junitCaseIdx, junitCaseEnd);
    assert.ok(
      junitCaseBlock.includes('exit 1'),
      'Expected exit 1 guard in --junit case for empty path. Got case block: ' + junitCaseBlock
    );
  });
});

// ---------------------------------------------------------------------------
// Phase 7 Plan 01: metrics codegen (FLAKY-02)
// ---------------------------------------------------------------------------

const {
  generateRuntimeFlagBlock,
  generateRuntimeSupport,
  generateFooter,
  generateMetricsEmitter,
} = require('../codegen.js');

describe('metrics codegen (FLAKY-02) — generateRuntimeFlagBlock()', function() {
  test("output includes METRICS_OUTPUT empty default", function() {
    const block = generateRuntimeFlagBlock();
    assert.ok(
      block.includes('METRICS_OUTPUT=""'),
      'Expected METRICS_OUTPUT="" default. Got: ' + block
    );
  });

  test("output includes --metrics-output case", function() {
    const block = generateRuntimeFlagBlock();
    assert.ok(
      block.includes('--metrics-output)'),
      'Expected --metrics-output) case. Got: ' + block
    );
  });

  test("--metrics-output case uses shift 2", function() {
    const block = generateRuntimeFlagBlock();
    const metricsIdx = block.indexOf('--metrics-output)');
    const afterMetrics = block.slice(metricsIdx, metricsIdx + 200);
    assert.ok(
      afterMetrics.includes('shift 2'),
      'Expected shift 2 in --metrics-output case. Got: ' + afterMetrics
    );
  });

  test("--metrics-output case has empty-path guard", function() {
    const block = generateRuntimeFlagBlock();
    const metricsIdx = block.indexOf('--metrics-output)');
    const doubleColonIdx = block.indexOf(';;', metricsIdx);
    const caseBlock = block.slice(metricsIdx, doubleColonIdx);
    assert.ok(
      caseBlock.includes('exit 1'),
      'Expected exit 1 guard in --metrics-output case for empty path. Got: ' + caseBlock
    );
  });
});

describe('metrics codegen (FLAKY-02) — generateRuntimeSupport()', function() {
  test("output includes _TOTAL_ATTEMPTS=1", function() {
    const block = generateRuntimeSupport();
    assert.ok(
      block.includes('_TOTAL_ATTEMPTS=1'),
      'Expected _TOTAL_ATTEMPTS=1 in runtime support. Got snippet: ' + block.slice(0, 400)
    );
  });

  test("output includes _ATTEMPT_NUM=1", function() {
    const block = generateRuntimeSupport();
    assert.ok(
      block.includes('_ATTEMPT_NUM=1'),
      'Expected _ATTEMPT_NUM=1 in runtime support. Got snippet: ' + block.slice(0, 400)
    );
  });
});

describe('metrics codegen (FLAKY-02) — generateMetricsEmitter()', function() {
  test("generateMetricsEmitter() is exported from codegen.js", function() {
    assert.equal(typeof generateMetricsEmitter, 'function',
      'Expected generateMetricsEmitter to be a function');
  });

  test("output defines _emit_metrics() bash function", function() {
    const block = generateMetricsEmitter('login-flow');
    assert.ok(
      block.includes('_emit_metrics()'),
      'Expected _emit_metrics() function definition. Got: ' + block.slice(0, 300)
    );
  });

  test("flow name is embedded at compile time", function() {
    const block = generateMetricsEmitter('login-flow');
    assert.ok(
      block.includes('login-flow'),
      'Expected flow name embedded in _emit_metrics. Got: ' + block.slice(0, 400)
    );
  });

  test("_emit_metrics iterates _STEP_NAMES array", function() {
    const block = generateMetricsEmitter('login-flow');
    assert.ok(
      block.includes('_STEP_NAMES'),
      'Expected _STEP_NAMES iteration in _emit_metrics. Got: ' + block.slice(0, 500)
    );
  });

  test("_emit_metrics iterates _STEP_RESULTS array", function() {
    const block = generateMetricsEmitter('login-flow');
    assert.ok(
      block.includes('_STEP_RESULTS'),
      'Expected _STEP_RESULTS in _emit_metrics. Got: ' + block.slice(0, 500)
    );
  });

  test("_emit_metrics iterates _STEP_TIMES array", function() {
    const block = generateMetricsEmitter('login-flow');
    assert.ok(
      block.includes('_STEP_TIMES'),
      'Expected _STEP_TIMES in _emit_metrics. Got: ' + block.slice(0, 500)
    );
  });

  test("_emit_metrics iterates _STEP_FAILURES array", function() {
    const block = generateMetricsEmitter('login-flow');
    assert.ok(
      block.includes('_STEP_FAILURES'),
      'Expected _STEP_FAILURES in _emit_metrics. Got: ' + block.slice(0, 500)
    );
  });

  test("_emit_metrics JSON includes \"flow\" field", function() {
    const block = generateMetricsEmitter('login-flow');
    assert.ok(
      block.includes('"flow"'),
      'Expected "flow" JSON field in _emit_metrics. Got: ' + block.slice(0, 600)
    );
  });

  test("_emit_metrics JSON includes \"timestamp\" field", function() {
    const block = generateMetricsEmitter('login-flow');
    assert.ok(
      block.includes('"timestamp"'),
      'Expected "timestamp" JSON field in _emit_metrics. Got: ' + block.slice(0, 600)
    );
  });

  test("_emit_metrics JSON includes \"passed_first_try\" field", function() {
    const block = generateMetricsEmitter('login-flow');
    assert.ok(
      block.includes('"passed_first_try"'),
      'Expected "passed_first_try" JSON field in _emit_metrics. Got: ' + block.slice(0, 600)
    );
  });

  test("_emit_metrics JSON includes \"flaky_pass\" field", function() {
    const block = generateMetricsEmitter('login-flow');
    assert.ok(
      block.includes('"flaky_pass"'),
      'Expected "flaky_pass" JSON field in _emit_metrics. Got: ' + block.slice(0, 600)
    );
  });

  test("_emit_metrics JSON includes \"steps\" field", function() {
    const block = generateMetricsEmitter('login-flow');
    assert.ok(
      block.includes('"steps"'),
      'Expected "steps" JSON field in _emit_metrics. Got: ' + block.slice(0, 600)
    );
  });

  test("_emit_metrics JSON includes \"summary\" field", function() {
    const block = generateMetricsEmitter('login-flow');
    assert.ok(
      block.includes('"summary"'),
      'Expected "summary" JSON field in _emit_metrics. Got: ' + block.slice(0, 600)
    );
  });
});

describe('metrics codegen (FLAKY-02) — generate() integration', function() {
  test("generated script contains _emit_metrics function definition", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'my-flow');
    assert.ok(
      script.includes('_emit_metrics()'),
      'Expected _emit_metrics() in generated script. Got snippet: ' + script.slice(0, 800)
    );
  });

  test("generated script footer calls _emit_metrics when METRICS_OUTPUT is set", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'my-flow');
    assert.ok(
      script.includes('_emit_metrics "$METRICS_OUTPUT"'),
      'Expected _emit_metrics "$METRICS_OUTPUT" call in footer. Got snippet: ' + script.slice(-400)
    );
  });

  test("generated script footer wraps _emit_metrics call in METRICS_OUTPUT guard", function() {
    const step = makeNavigate('nav', '/home');
    const script = generate(makeResolved([step]), 'my-flow');
    assert.ok(
      script.includes('[ -n "$METRICS_OUTPUT" ]') && script.includes('_emit_metrics "$METRICS_OUTPUT"'),
      'Expected METRICS_OUTPUT guard around _emit_metrics call. Got snippet: ' + script.slice(-600)
    );
  });
});

describe('metrics codegen (FLAKY-02) — generateFooter() integration', function() {
  test("footer contains conditional _emit_metrics call", function() {
    const footer = generateFooter('my-flow', 3, 0);
    assert.ok(
      footer.includes('_emit_metrics'),
      'Expected _emit_metrics call in footer. Got: ' + footer
    );
  });

  test("footer _emit_metrics call is guarded by METRICS_OUTPUT check", function() {
    const footer = generateFooter('my-flow', 3, 0);
    const metricsIdx = footer.indexOf('_emit_metrics');
    // Find the surrounding context
    const context = footer.slice(Math.max(0, metricsIdx - 60), metricsIdx + 60);
    assert.ok(
      context.includes('METRICS_OUTPUT'),
      'Expected METRICS_OUTPUT guard near _emit_metrics call. Got context: ' + context
    );
  });

  test("footer _emit_metrics call appears before JUnit emission", function() {
    const footer = generateFooter('my-flow', 3, 0);
    const metricsIdx = footer.indexOf('_emit_metrics');
    const junitIdx = footer.indexOf('_emit_junit');
    assert.ok(
      metricsIdx < junitIdx,
      'Expected _emit_metrics before _emit_junit in footer. metricsIdx=' + metricsIdx + ' junitIdx=' + junitIdx
    );
  });
});
