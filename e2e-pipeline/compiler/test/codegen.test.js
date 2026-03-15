'use strict';

const { test, describe } = require('node:test');
const assert = require('node:assert/strict');

const { generate, singleQuote } = require('../codegen.js');

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

  test("navigate failure block includes FAIL message and exit 1", function() {
    const step = makeNavigate('nav-login', '/login');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(script.includes('FAIL: nav-login -- navigate to /login failed'));
    assert.ok(script.includes('exit 1'));
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

  test("click failure block includes FAIL message and exit 1", function() {
    const step = makeClick('click-submit', 'login_button', 'role=button[name="Sign In"]');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(script.includes('FAIL: click-submit -- click action failed'));
    assert.ok(script.includes('exit 1'));
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

  test("fill failure block includes FAIL message and exit 1", function() {
    const step = makeFill('fill-email', 'email_input', 'role=textbox[name="Email"]', 'test@example.com');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(script.includes('FAIL: fill-email -- fill action failed'));
    assert.ok(script.includes('exit 1'));
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
  test("visible expect uses stdout capture pattern (|| true, not exit code)", function() {
    const step = makeClick('click-btn', 'login_button', 'role=button[name="Sign In"]');
    step.expects = [{ type: 'active', raw: 'login_button is visible', elementName: 'login_button', selector: 'role=button[name="Sign In"]' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes("result=$(agent-browser is visible 'role=button[name=\"Sign In\"]') || true"),
      'Expected stdout capture with || true. Got: ' + script
    );
  });

  test("visible expect check uses string comparison not exit code", function() {
    const step = makeClick('click-btn', 'login_button', 'role=button[name="Sign In"]');
    step.expects = [{ type: 'active', raw: 'login_button is visible', elementName: 'login_button', selector: 'role=button[name="Sign In"]' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(script.includes('if [ "$result" != "true" ]; then'));
  });

  test("visible expect FAIL message names the element", function() {
    const step = makeClick('click-btn', 'login_button', 'role=button[name="Sign In"]');
    step.expects = [{ type: 'active', raw: 'login_button is visible', elementName: 'login_button', selector: 'role=button[name="Sign In"]' }];
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(script.includes('FAIL: click-btn -- login_button is not visible'));
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
  test("navigate failure reason includes urlPath", function() {
    const step = makeNavigate('nav-login', '/login', 'Navigate to /login');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(
      script.includes('echo "FAIL: nav-login -- navigate to /login failed"'),
      'Navigate FAIL must reference the urlPath. Got: ' + script
    );
  });

  test("click failure reason is generic 'click action failed'", function() {
    const step = makeClick('click-btn', 'login_button', 'role=button[name="Sign In"]');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(script.includes('echo "FAIL: click-btn -- click action failed"'));
  });

  test("fill failure reason is generic 'fill action failed'", function() {
    const step = makeFill('fill-email', 'email_input', 'role=textbox[name="Email"]', 'test@example.com');
    const script = generate(makeResolved([step]), 'test-flow');
    assert.ok(script.includes('echo "FAIL: fill-email -- fill action failed"'));
  });

  test("snapshot has no failure block", function() {
    const step = makeSnapshot('take-snap');
    const script = generate(makeResolved([step]), 'test-flow');
    // snapshot block should not contain FAIL
    const snapIdx = script.indexOf('agent-browser snapshot');
    const afterSnap = script.slice(snapIdx, snapIdx + 60);
    assert.ok(!afterSnap.includes('FAIL'), 'snapshot must not have failure block');
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
