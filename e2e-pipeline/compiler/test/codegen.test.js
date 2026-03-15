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
    assert.equal(singleQuote("input[type='password']"), "'input[type='\\''password'\\''']'");
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
      script.includes("agent-browser fill 'input[type='\\''password'\\''']' 'secret'"),
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
