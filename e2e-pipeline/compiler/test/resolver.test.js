'use strict';

const { test, describe } = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');

const { resolve, resolveMultiSite } = require('../resolver');
const { parse } = require('../parser');

const FIXTURES = path.join(__dirname, 'fixtures');

// ---------------------------------------------------------------------------
// Inline test fixtures (for isolation — no FS dependency in resolver tests)
// ---------------------------------------------------------------------------

/**
 * Minimal mapping matching simple-mapping.yaml / test-app.yaml structure.
 * 5 elements total: email_input, password_input, login_button (login),
 *                   heading (dashboard), sidebar_home (_global)
 */
const SIMPLE_MAPPING = {
  version: 2,
  app: 'test-app',
  base_url: 'http://localhost:3000',
  pages: {
    login: {
      url_pattern: '/login',
      elements: {
        email_input: { selector: 'role=textbox[name="Email"]', description: 'Email input' },
        password_input: { selector: "input[type='password']", description: 'Password input' },
        login_button: { selector: 'role=button[name="Sign In"]', description: 'Login button' },
      },
    },
    dashboard: {
      url_pattern: '/dashboard',
      elements: {
        heading: { selector: 'role=heading[name="Dashboard"]', description: 'Dashboard heading' },
      },
    },
    _global: {
      description: 'Global elements',
      elements: {
        sidebar_home: { selector: 'role=menuitem[name="Home"]', description: 'Sidebar home link' },
      },
    },
  },
};

const DUPLICATE_MAPPING = {
  version: 2,
  app: 'test-app-dupes',
  base_url: 'http://localhost:3000',
  pages: {
    'page-a': {
      url_pattern: '/a',
      elements: {
        data_table: { selector: 'role=table', description: 'Table on page A' },
        unique_a: { selector: '.unique-a', description: 'Only on A' },
      },
    },
    'page-b': {
      url_pattern: '/b',
      elements: {
        data_table: { selector: 'role=grid', description: 'Table on page B' },
        unique_b: { selector: '.unique-b', description: 'Only on B' },
      },
    },
  },
};

const SIMPLE_FLOW = {
  name: 'test-login',
  description: 'Test login flow',
  tags: ['smoke'],
  mapping: 'test-app',
  variables: { base_url: 'http://localhost:3000' },
  steps: [
    { id: 'navigate-to-login', type: 'navigate', action: 'Navigate to /login' },
    { id: 'fill-email', type: 'fill', action: "Fill email_input with 'test@example.com' on login", expect: ['email_input is visible'] },
    { id: 'click-submit', type: 'click', action: 'Click login_button on login' },
    { id: 'take-snapshot', type: 'snapshot', action: 'Take snapshot' },
    { id: 'wait-for-load', type: 'wait', action: 'Wait 2' },
    { id: 'verify-external', type: 'verify-external', action: 'Verify external' },
  ],
};

const MISSING_ELEMENT_FLOW = {
  name: 'test-missing',
  description: 'Flow with missing element ref',
  tags: ['test'],
  mapping: 'test-app',
  steps: [
    { id: 'click-nonexistent', type: 'click', action: 'Click nonexistent_button on login' },
  ],
};

// ---------------------------------------------------------------------------
// Symbol table tests
// ---------------------------------------------------------------------------

test('buildSymbolTable: simple mapping yields 5 entries', () => {
  // We test this indirectly via resolve — but resolve exposes stats
  // Use a flow that resolves all 5 elements to confirm all are in the table
  const flow = {
    name: 'test',
    steps: [
      { id: 'nav', type: 'navigate', action: 'Navigate to /login' },
      { id: 'click-email', type: 'click', action: 'Click email_input on login' },
      { id: 'click-pwd', type: 'click', action: 'Click password_input on login' },
      { id: 'click-btn', type: 'click', action: 'Click login_button on login' },
      { id: 'click-heading', type: 'click', action: 'Click heading on dashboard' },
      { id: 'click-sidebar', type: 'click', action: 'Click sidebar_home' },
    ],
  };
  const result = resolve(flow, SIMPLE_MAPPING);
  assert.deepEqual(result.errors, [], 'should resolve all 5 elements without error');
});

test('buildSymbolTable: duplicate elements mapping returns ambiguous error', () => {
  const flow = {
    name: 'test',
    steps: [
      { id: 'click-table', type: 'click', action: 'Click data_table on page-a' },
    ],
  };
  const result = resolve(flow, DUPLICATE_MAPPING);
  const dupeError = result.errors.find(e => e.includes("'data_table' is ambiguous"));
  assert.ok(dupeError, "should have ambiguous error for data_table. Errors: " + result.errors.join('; '));
  assert.ok(dupeError.includes('page-a'), 'error should name page-a');
  assert.ok(dupeError.includes('page-b'), 'error should name page-b');
});

// ---------------------------------------------------------------------------
// Element resolution tests
// ---------------------------------------------------------------------------

test('resolve: simple-flow resolves email_input to correct selector', () => {
  const result = resolve(SIMPLE_FLOW, SIMPLE_MAPPING);
  assert.deepEqual(result.errors, [], 'no errors expected. Got: ' + result.errors.join('; '));

  const fillStep = result.resolved.steps.find(s => s.id === 'fill-email');
  assert.ok(fillStep, 'fill-email step should be in resolved output');
  assert.equal(fillStep.operands.element, 'email_input');
  assert.equal(fillStep.operands.selector, 'role=textbox[name="Email"]');
});

test('resolve: css_selector in mapping passes through as cssSelector in operands', () => {
  const mappingWithCss = {
    version: 2, app: 'test', base_url: 'http://localhost',
    pages: {
      login: {
        url_pattern: '/login',
        elements: {
          email_input: { selector: 'role=textbox[name="Email"]', css_selector: 'input[name="email"]' },
          login_button: { selector: 'role=button[name="Sign In"]', css_selector: 'button[type="submit"]' },
        },
      },
    },
  };
  const flow = {
    name: 'test-css',
    steps: [
      { id: 'fill-email', type: 'fill', action: "Fill email_input with 'test@example.com' on login" },
      { id: 'click-submit', type: 'click', action: 'Click login_button on login' },
    ],
  };
  const result = resolve(flow, mappingWithCss);
  assert.deepEqual(result.errors, [], 'no errors expected');

  const fillStep = result.resolved.steps.find(s => s.id === 'fill-email');
  assert.equal(fillStep.operands.cssSelector, 'input[name="email"]', 'fill should have cssSelector');
  assert.equal(fillStep.operands.selector, 'role=textbox[name="Email"]', 'fill should keep ARIA selector');

  const clickStep = result.resolved.steps.find(s => s.id === 'click-submit');
  assert.equal(clickStep.operands.cssSelector, 'button[type="submit"]', 'click should have cssSelector');
});

test('resolve: element without css_selector has no cssSelector in operands', () => {
  const result = resolve(SIMPLE_FLOW, SIMPLE_MAPPING);
  const fillStep = result.resolved.steps.find(s => s.id === 'fill-email');
  assert.equal(fillStep.operands.cssSelector, undefined, 'cssSelector should be undefined when not in mapping');
});

test('resolve: screenshot: true passes through to resolved step', () => {
  const flow = {
    name: 'test-screenshot',
    steps: [
      { id: 'nav', type: 'navigate', action: 'Navigate to /login', screenshot: true },
      { id: 'fill', type: 'fill', action: "Fill email_input with 'x@y.z' on login" },
    ],
  };
  const result = resolve(flow, SIMPLE_MAPPING);
  assert.deepEqual(result.errors, []);
  const navStep = result.resolved.steps.find(s => s.id === 'nav');
  assert.equal(navStep.screenshot, true, 'screenshot should be true');
  const fillStep = result.resolved.steps.find(s => s.id === 'fill');
  assert.equal(fillStep.screenshot, undefined, 'screenshot should be undefined when not set');
});

test('resolve: missing element returns descriptive error', () => {
  const result = resolve(MISSING_ELEMENT_FLOW, SIMPLE_MAPPING);
  const missingErr = result.errors.find(e =>
    e.includes("'nonexistent_button' not found")
  );
  assert.ok(missingErr, "should report missing element. Errors: " + result.errors.join('; '));
  assert.ok(missingErr.includes("click-nonexistent"), 'error should name the step ID');
});

test('resolve: accumulates ALL missing element errors across all steps', () => {
  const flow = {
    name: 'test-multi-missing',
    steps: [
      { id: 'step-1', type: 'click', action: 'Click ghost_button on login' },
      { id: 'step-2', type: 'click', action: 'Click phantom_link' },
    ],
  };
  const result = resolve(flow, SIMPLE_MAPPING);
  assert.equal(result.errors.length, 2, 'should have 2 errors for 2 missing elements');
  assert.ok(result.errors.some(e => e.includes('ghost_button')));
  assert.ok(result.errors.some(e => e.includes('phantom_link')));
});

// ---------------------------------------------------------------------------
// Navigate resolution tests
// ---------------------------------------------------------------------------

test('resolve: navigate with / prefix uses URL path directly', () => {
  const flow = {
    name: 'test',
    steps: [{ id: 'nav', type: 'navigate', action: 'Navigate to /login' }],
  };
  const result = resolve(flow, SIMPLE_MAPPING);
  assert.deepEqual(result.errors, [], 'no errors expected');

  const navStep = result.resolved.steps.find(s => s.id === 'nav');
  assert.equal(navStep.operands.target, '/login', 'target should be the URL path');
});

test('resolve: navigate without / prefix looks up page url_pattern', () => {
  const flow = {
    name: 'test',
    steps: [{ id: 'nav', type: 'navigate', action: 'Navigate to dashboard' }],
  };
  const result = resolve(flow, SIMPLE_MAPPING);
  assert.deepEqual(result.errors, [], 'no errors expected');

  const navStep = result.resolved.steps.find(s => s.id === 'nav');
  assert.equal(navStep.operands.urlPath, '/dashboard', 'urlPath should be the page url_pattern');
});

test('resolve: navigate to _global (no url_pattern) returns error', () => {
  const flow = {
    name: 'test',
    steps: [{ id: 'nav-global', type: 'navigate', action: 'Navigate to _global' }],
  };
  const result = resolve(flow, SIMPLE_MAPPING);
  const err = result.errors.find(e => e.includes("cannot navigate to '_global'"));
  assert.ok(err, "should error on navigate to _global. Errors: " + result.errors.join('; '));
  assert.ok(err.includes('nav-global'), 'error should name the step ID');
});

test('resolve: navigate to nonexistent page returns error', () => {
  const flow = {
    name: 'test',
    steps: [{ id: 'nav-404', type: 'navigate', action: 'Navigate to nonexistent' }],
  };
  const result = resolve(flow, SIMPLE_MAPPING);
  const err = result.errors.find(e =>
    e.includes("page 'nonexistent' not found") || e.includes('nonexistent')
  );
  assert.ok(err, "should error on nonexistent page. Errors: " + result.errors.join('; '));
  assert.ok(err.includes('nav-404'), 'error should name the step ID');
});

// ---------------------------------------------------------------------------
// Stats counting tests
// ---------------------------------------------------------------------------

test('resolve: stats counts total, activeExpects, deferredExpects, skipped', () => {
  const result = resolve(SIMPLE_FLOW, SIMPLE_MAPPING);
  assert.deepEqual(result.errors, [], 'no errors expected');

  // 6 total steps
  assert.equal(result.stats.total, 6);
  // 1 expect: "email_input is visible" → active
  assert.equal(result.stats.activeExpects, 1);
  // 0 deferred expects
  assert.equal(result.stats.deferredExpects, 0);
  // 1 verify-external → skipped
  assert.equal(result.stats.skipped, 1);
});

test('resolve: activeExpects counted for "element is visible" format', () => {
  const flow = {
    name: 'test',
    steps: [
      {
        id: 'fill-email',
        type: 'fill',
        action: "Fill email_input with 'test@example.com' on login",
        expect: ['email_input is visible', 'url contains /login'],
      },
    ],
  };
  const result = resolve(flow, SIMPLE_MAPPING);
  // Phase 2: "email_input is visible" → active; "url contains /login" → also active (Phase 2)
  assert.equal(result.stats.activeExpects, 2);
  assert.equal(result.stats.deferredExpects, 0);
});

test('resolve: expect "element is visible" resolves element name to selector', () => {
  const flow = {
    name: 'test',
    steps: [
      {
        id: 'fill-email',
        type: 'fill',
        action: "Fill email_input with 'test@example.com' on login",
        expect: ['email_input is visible'],
      },
    ],
  };
  const result = resolve(flow, SIMPLE_MAPPING);
  assert.deepEqual(result.errors, [], 'no errors expected');

  const step = result.resolved.steps[0];
  assert.ok(step.expects, 'step should have expects array');
  const activeExpect = step.expects.find(e => e.type === 'active');
  assert.ok(activeExpect, 'should have one active expect');
  assert.equal(activeExpect.selector, 'role=textbox[name="Email"]');
  assert.equal(activeExpect.elementName, 'email_input');
});

// ---------------------------------------------------------------------------
// Action parser regex tests
// ---------------------------------------------------------------------------

test('resolve: step with no type field returns error', () => {
  const flow = {
    name: 'test',
    steps: [{ id: 'no-type', action: 'Click something' }],
  };
  const result = resolve(flow, SIMPLE_MAPPING);
  const err = result.errors.find(e => e.includes('no-type') && e.includes('no type'));
  assert.ok(err, "should error on missing type. Errors: " + result.errors.join('; '));
});

test('resolve: action string not matching regex returns descriptive error', () => {
  const flow = {
    name: 'test',
    steps: [
      {
        id: 'bad-fill',
        type: 'fill',
        action: 'This does not match the fill pattern',
      },
    ],
  };
  const result = resolve(flow, SIMPLE_MAPPING);
  const err = result.errors.find(e =>
    e.includes('bad-fill') &&
    (e.includes('does not match') || e.includes('format'))
  );
  assert.ok(err, "should error on unmatched action string. Errors: " + result.errors.join('; '));
  assert.ok(err.includes('fill'), "error should mention the type 'fill'");
});

// ---------------------------------------------------------------------------
// Integration test: use parser + resolver together on fixture files
// ---------------------------------------------------------------------------

test('integration: parse + resolve simple-flow.yaml produces no errors', () => {
  const flowPath = path.join(FIXTURES, 'simple-flow.yaml');
  const parseResult = parse(flowPath, FIXTURES);
  assert.deepEqual(parseResult.errors, [], 'parse should succeed');

  const resolveResult = resolve(parseResult.flow, parseResult.mapping);
  assert.deepEqual(resolveResult.errors, [], 'resolve should succeed');
  assert.equal(resolveResult.stats.total, 6);
});

test('integration: parse + resolve missing-element-flow.yaml surfaces element error', () => {
  const flowPath = path.join(FIXTURES, 'missing-element-flow.yaml');
  const parseResult = parse(flowPath, FIXTURES);
  assert.deepEqual(parseResult.errors, [], 'parse should succeed');

  const resolveResult = resolve(parseResult.flow, parseResult.mapping);
  assert.ok(resolveResult.errors.length > 0, 'resolve should surface missing element error');
  assert.ok(resolveResult.errors.some(e => e.includes('nonexistent_button')));
});

// ---------------------------------------------------------------------------
// Phase 2: resolveExpects() — new expect patterns
// ---------------------------------------------------------------------------

// Helper: build a flow with one step containing a set of expects
function flowWithExpects(expects) {
  return {
    name: 'test',
    steps: [
      {
        id: 'step1',
        type: 'snapshot',
        action: 'Take snapshot',
        expect: expects,
      },
    ],
  };
}

// Extended SIMPLE_MAPPING with sidebar_dashboard for or-visible tests
const EXTENDED_MAPPING = {
  version: 2,
  app: 'test-app',
  base_url: 'http://localhost:3000',
  pages: {
    login: {
      url_pattern: '/login',
      elements: {
        email_input: { selector: 'role=textbox[name="Email"]', description: 'Email input' },
        password_input: { selector: "input[type='password']", description: 'Password input' },
        login_button: { selector: 'role=button[name="Sign In"]', description: 'Login button' },
      },
    },
    dashboard: {
      url_pattern: '/dashboard',
      elements: {
        heading: { selector: 'role=heading[name="Dashboard"]', description: 'Dashboard heading' },
        sidebar_dashboard: { selector: 'role=menuitem[name="Dashboard"]', description: 'Sidebar dashboard link' },
      },
    },
    _global: {
      description: 'Global elements',
      elements: {
        sidebar_home: { selector: 'role=menuitem[name="Home"]', description: 'Sidebar home link' },
      },
    },
  },
};

test('resolveExpects Phase 2: "element visible" (no is) resolves type element-visible', () => {
  const flow = flowWithExpects(['sidebar_dashboard visible']);
  const result = resolve(flow, EXTENDED_MAPPING);
  assert.deepEqual(result.errors, [], 'no errors expected. Got: ' + result.errors.join('; '));
  const step = result.resolved.steps[0];
  assert.ok(step.expects, 'step should have expects');
  const exp = step.expects[0];
  assert.equal(exp.type, 'element-visible');
  assert.equal(exp.elementName, 'sidebar_dashboard');
  assert.equal(exp.selector, 'role=menuitem[name="Dashboard"]');
  assert.equal(result.stats.activeExpects, 1);
  assert.equal(result.stats.deferredExpects, 0);
});

test('resolveExpects Phase 2: "element visible on page" resolves type element-visible with page qualifier', () => {
  const flow = flowWithExpects(['sidebar_dashboard visible on dashboard']);
  const result = resolve(flow, EXTENDED_MAPPING);
  assert.deepEqual(result.errors, [], 'no errors expected. Got: ' + result.errors.join('; '));
  const step = result.resolved.steps[0];
  const exp = step.expects[0];
  assert.equal(exp.type, 'element-visible');
  assert.equal(exp.elementName, 'sidebar_dashboard');
  assert.equal(exp.selector, 'role=menuitem[name="Dashboard"]');
  assert.equal(result.stats.activeExpects, 1);
  assert.equal(result.stats.deferredExpects, 0);
});

test('resolveExpects Phase 2: "dialog not visible" resolves to built-in role=dialog', () => {
  const flow = flowWithExpects(['dialog not visible']);
  const result = resolve(flow, SIMPLE_MAPPING);
  assert.deepEqual(result.errors, [], 'no errors expected. Got: ' + result.errors.join('; '));
  const step = result.resolved.steps[0];
  const exp = step.expects[0];
  assert.equal(exp.type, 'element-not-visible');
  assert.equal(exp.elementName, 'dialog');
  assert.equal(exp.selector, 'role=dialog');
  assert.equal(result.stats.activeExpects, 1);
  assert.equal(result.stats.deferredExpects, 0);
});

test('resolveExpects Phase 2: "heading is not visible" resolves type element-not-visible from table', () => {
  const flow = flowWithExpects(['heading is not visible']);
  const result = resolve(flow, SIMPLE_MAPPING);
  assert.deepEqual(result.errors, [], 'no errors expected. Got: ' + result.errors.join('; '));
  const step = result.resolved.steps[0];
  const exp = step.expects[0];
  assert.equal(exp.type, 'element-not-visible');
  assert.equal(exp.elementName, 'heading');
  assert.equal(exp.selector, 'role=heading[name="Dashboard"]');
  assert.equal(result.stats.activeExpects, 1);
  assert.equal(result.stats.deferredExpects, 0);
});

test('resolveExpects Phase 2: "url contains /dashboard" resolves type url-contains', () => {
  const flow = flowWithExpects(['url contains /dashboard']);
  const result = resolve(flow, SIMPLE_MAPPING);
  assert.deepEqual(result.errors, [], 'no errors expected. Got: ' + result.errors.join('; '));
  const step = result.resolved.steps[0];
  const exp = step.expects[0];
  assert.equal(exp.type, 'url-contains');
  assert.equal(exp.value, '/dashboard');
  assert.equal(result.stats.activeExpects, 1);
  assert.equal(result.stats.deferredExpects, 0);
});

test('resolveExpects Phase 2: "url does not contain /login" resolves type url-not-contains', () => {
  const flow = flowWithExpects(['url does not contain /login']);
  const result = resolve(flow, SIMPLE_MAPPING);
  assert.deepEqual(result.errors, [], 'no errors expected. Got: ' + result.errors.join('; '));
  const step = result.resolved.steps[0];
  const exp = step.expects[0];
  assert.equal(exp.type, 'url-not-contains');
  assert.equal(exp.value, '/login');
  assert.equal(result.stats.activeExpects, 1);
  assert.equal(result.stats.deferredExpects, 0);
});

test('resolveExpects Phase 2: "text \'每日看板\' on page" resolves type text-visible', () => {
  const flow = flowWithExpects(["text '每日看板' on page"]);
  const result = resolve(flow, SIMPLE_MAPPING);
  assert.deepEqual(result.errors, [], 'no errors expected. Got: ' + result.errors.join('; '));
  const step = result.resolved.steps[0];
  const exp = step.expects[0];
  assert.equal(exp.type, 'text-visible');
  assert.equal(exp.text, '每日看板');
  assert.equal(result.stats.activeExpects, 1);
  assert.equal(result.stats.deferredExpects, 0);
});

test('resolveExpects Phase 2: text with double-quote format resolves type text-visible', () => {
  const flow = flowWithExpects(['text "Dashboard" visible']);
  const result = resolve(flow, SIMPLE_MAPPING);
  assert.deepEqual(result.errors, [], 'no errors expected. Got: ' + result.errors.join('; '));
  const step = result.resolved.steps[0];
  const exp = step.expects[0];
  assert.equal(exp.type, 'text-visible');
  assert.equal(exp.text, 'Dashboard');
  assert.equal(result.stats.activeExpects, 1);
  assert.equal(result.stats.deferredExpects, 0);
});

test("resolveExpects Phase 2: \"text 'X' not on page\" resolves type text-not-visible", () => {
  const flow = flowWithExpects(["text 'Sign-in failed' not on page"]);
  const result = resolve(flow, SIMPLE_MAPPING);
  assert.deepEqual(result.errors, [], 'no errors expected. Got: ' + result.errors.join('; '));
  const step = result.resolved.steps[0];
  const exp = step.expects[0];
  assert.equal(exp.type, 'text-not-visible');
  assert.equal(exp.text, 'Sign-in failed');
  assert.equal(result.stats.activeExpects, 1);
  assert.equal(result.stats.deferredExpects, 0);
});

test('resolveExpects Phase 2: text with double-quote "not visible" format resolves type text-not-visible', () => {
  const flow = flowWithExpects(['text "Dashboard" not visible']);
  const result = resolve(flow, SIMPLE_MAPPING);
  assert.deepEqual(result.errors, [], 'no errors expected. Got: ' + result.errors.join('; '));
  const step = result.resolved.steps[0];
  const exp = step.expects[0];
  assert.equal(exp.type, 'text-not-visible');
  assert.equal(exp.text, 'Dashboard');
  assert.equal(result.stats.activeExpects, 1);
  assert.equal(result.stats.deferredExpects, 0);
});

test('resolveExpects Phase 2: "element not visible on page" resolves type element-not-visible with page qualifier', () => {
  const flow = flowWithExpects(['heading not visible on dashboard']);
  const result = resolve(flow, SIMPLE_MAPPING);
  assert.deepEqual(result.errors, [], 'no errors expected. Got: ' + result.errors.join('; '));
  const step = result.resolved.steps[0];
  const exp = step.expects[0];
  assert.equal(exp.type, 'element-not-visible');
  assert.equal(exp.elementName, 'heading');
  assert.equal(exp.selector, 'role=heading[name="Dashboard"]');
  assert.equal(result.stats.activeExpects, 1);
  assert.equal(result.stats.deferredExpects, 0);
});

test('resolveExpects Phase 2: "element is not visible on page" resolves type element-not-visible with page qualifier', () => {
  const flow = flowWithExpects(['heading is not visible on dashboard']);
  const result = resolve(flow, SIMPLE_MAPPING);
  assert.deepEqual(result.errors, [], 'no errors expected. Got: ' + result.errors.join('; '));
  const step = result.resolved.steps[0];
  const exp = step.expects[0];
  assert.equal(exp.type, 'element-not-visible');
  assert.equal(exp.elementName, 'heading');
  assert.equal(exp.selector, 'role=heading[name="Dashboard"]');
  assert.equal(result.stats.activeExpects, 1);
  assert.equal(result.stats.deferredExpects, 0);
});

test('resolveExpects Phase 2: or-visible resolves both elements with correct selectors', () => {
  const flow = flowWithExpects(['email_input visible or login_button visible']);
  const result = resolve(flow, SIMPLE_MAPPING);
  assert.deepEqual(result.errors, [], 'no errors expected. Got: ' + result.errors.join('; '));
  const step = result.resolved.steps[0];
  const exp = step.expects[0];
  assert.equal(exp.type, 'or-visible');
  assert.ok(Array.isArray(exp.elements), 'elements should be an array');
  assert.equal(exp.elements.length, 2);
  assert.equal(exp.elements[0].elementName, 'email_input');
  assert.equal(exp.elements[0].selector, 'role=textbox[name="Email"]');
  assert.equal(exp.elements[1].elementName, 'login_button');
  assert.equal(exp.elements[1].selector, 'role=button[name="Sign In"]');
  assert.equal(result.stats.activeExpects, 1);
  assert.equal(result.stats.deferredExpects, 0);
});

test('resolveExpects Phase 2: unrecognized format still becomes deferred', () => {
  const flow = flowWithExpects(['something completely unknown xyz123']);
  const result = resolve(flow, SIMPLE_MAPPING);
  const step = result.resolved.steps[0];
  const exp = step.expects[0];
  assert.equal(exp.type, 'deferred');
  assert.equal(result.stats.deferredExpects, 1);
  assert.equal(result.stats.activeExpects, 0);
});

test('resolveExpects Phase 2: nonexistent element in visible pattern returns error', () => {
  const flow = flowWithExpects(['nonexistent visible']);
  const result = resolve(flow, SIMPLE_MAPPING);
  assert.ok(result.errors.length > 0, 'should have error for missing element');
  assert.ok(result.errors.some(e => e.includes('nonexistent')), 'error should mention element name');
});

test('resolveExpects Phase 2: Phase 1 "element is visible" still works (backwards compat)', () => {
  const flow = flowWithExpects(['email_input is visible']);
  const result = resolve(flow, SIMPLE_MAPPING);
  assert.deepEqual(result.errors, [], 'no errors expected');
  const step = result.resolved.steps[0];
  const exp = step.expects[0];
  // Phase 1 pattern keeps type 'active' (or could be 'element-visible' — accept either)
  assert.ok(exp.type === 'active' || exp.type === 'element-visible', 'should be active or element-visible type');
  assert.equal(exp.elementName, 'email_input');
  assert.equal(exp.selector, 'role=textbox[name="Email"]');
  assert.equal(result.stats.activeExpects, 1);
  assert.equal(result.stats.deferredExpects, 0);
});

// ---------------------------------------------------------------------------
// xn (e2e-expect-grammar-permutations): 2 corpus-justified quoting permutations
// the Phase 2 table forgot — both single-quote "is"-predicate forms. See
// docs/writing-tests.md "Expect Grammar Reference" for the full table.
// ---------------------------------------------------------------------------

test("resolveExpects xn AC2: \"text '<value>' is visible\" resolves type text-visible", () => {
  const flow = flowWithExpects(["text '請先選擇廠牌' is visible"]);
  const result = resolve(flow, SIMPLE_MAPPING);
  assert.deepEqual(result.errors, [], 'no errors expected. Got: ' + result.errors.join('; '));
  const step = result.resolved.steps[0];
  const exp = step.expects[0];
  assert.equal(exp.type, 'text-visible');
  assert.equal(exp.text, '請先選擇廠牌');
  assert.equal(result.stats.activeExpects, 1);
  assert.equal(result.stats.deferredExpects, 0);
});

test("resolveExpects xn AC3: \"text '<value>' is not visible\" resolves type text-not-visible, NOT text-visible", () => {
  const flow = flowWithExpects(["text '工單記錄' is not visible"]);
  const result = resolve(flow, SIMPLE_MAPPING);
  assert.deepEqual(result.errors, [], 'no errors expected. Got: ' + result.errors.join('; '));
  const step = result.resolved.steps[0];
  const exp = step.expects[0];
  // The specific regression the table's negatives-before-positives convention exists
  // to prevent: the positive pattern (`^text '(.+)' is visible$`) capturing the negated
  // string first. Assert the negative type explicitly rather than just absence of error —
  // this assertion is what would fail if that shadowing regression were reintroduced.
  assert.notEqual(exp.type, 'text-visible', 'negated form must not be captured by the positive pattern');
  assert.equal(exp.type, 'text-not-visible');
  assert.equal(exp.text, '工單記錄');
  assert.equal(result.stats.activeExpects, 1);
  assert.equal(result.stats.deferredExpects, 0);
});

test('resolveExpects xn AC4 (ordering): all 8 corpus strings the new patterns recover, plus 2 pre-existing sibling-shaped forms, resolve without shadowing', () => {
  // Every corpus string the Design table's 2 new rows recover (Corpus evidence in the
  // entity body), interleaved with a pre-existing element-not-visible form and a
  // pre-existing text-visible (double-quote sibling) form. Table order is not being
  // varied here in the array-position sense (that arrangement was proved
  // order-independent 16/16 by the ideation-stage corpus spike, both at the designed
  // position and appended at the very end of EXPECT_PATTERNS) — this test instead
  // proves it in the running code: none of the 4 negative-form strings resolve as
  // text-visible, none of the 4 positive-form strings resolve as text-not-visible,
  // and neither pre-existing sibling form's type changes.
  const expects = [
    "text '請先選擇廠牌' is visible",
    "text '請選擇車主' is visible",
    "text '新增「hino」' is visible",
    "text '廠牌' is visible",
    "text '工單記錄' is not visible",
    "text '建立提醒' is not visible",
    "text '安排預約' is not visible",
    "text '排程通知' is not visible",
    'heading is not visible',
    "text '每日看板' on page",
  ];
  const flow = flowWithExpects(expects);
  const result = resolve(flow, SIMPLE_MAPPING);
  assert.deepEqual(result.errors, [], 'no errors expected. Got: ' + result.errors.join('; '));
  const types = result.resolved.steps[0].expects.map((e) => e.type);
  assert.deepEqual(types, [
    'text-visible', 'text-visible', 'text-visible', 'text-visible',
    'text-not-visible', 'text-not-visible', 'text-not-visible', 'text-not-visible',
    'element-not-visible', 'text-visible',
  ]);
  assert.equal(result.stats.activeExpects, 10);
  assert.equal(result.stats.deferredExpects, 0);
});

// ---------------------------------------------------------------------------
// Phase 2 Plan 02: cross-site sites: block — resolver
// ---------------------------------------------------------------------------

const SITE_A_MAPPING = {
  version: 2,
  app: 'site-a',
  base_url: 'http://localhost:5173',
  pages: {
    dashboard: {
      url_pattern: '/dashboard',
      elements: {
        heading_a: { selector: 'role=heading[name="Office Dashboard"]', description: 'Office dashboard heading' },
      },
    },
  },
};

const SITE_B_MAPPING = {
  version: 2,
  app: 'site-b',
  base_url: 'http://localhost:8081',
  pages: {
    home: {
      url_pattern: '/home',
      elements: {
        button_b: { selector: 'role=button[name="App Button"]', description: 'App button' },
      },
    },
  },
};

const CROSS_SITE_FLOW = {
  name: 'cross-site-test',
  description: 'Cross-site authentication check',
  sites: {
    office: { mapping: 'site-a' },
    app: { mapping: 'site-b' },
  },
  steps: [
    { id: 'office-nav', site: 'office', type: 'navigate', action: 'Navigate to /dashboard' },
    { id: 'office-check', site: 'office', type: 'snapshot', action: 'Take snapshot', expect: ['heading_a is visible'] },
    { id: 'app-nav', site: 'app', type: 'navigate', action: 'Navigate to /home' },
    { id: 'app-check', site: 'app', type: 'click', action: 'Click button_b on home' },
  ],
};

const SITE_MAPPINGS = {
  office: { mappingName: 'site-a', mapping: SITE_A_MAPPING },
  app: { mappingName: 'site-b', mapping: SITE_B_MAPPING },
};

describe('cross-site sites: block — resolver', function() {
  test('resolveMultiSite: steps get session field from site: qualifier', function() {
    const result = resolveMultiSite(CROSS_SITE_FLOW, SITE_MAPPINGS);
    assert.deepEqual(result.errors, [], 'no errors expected. Got: ' + result.errors.join('; '));
    const officeNav = result.resolved.steps.find(s => s.id === 'office-nav');
    assert.ok(officeNav, 'office-nav step should be in resolved output');
    assert.equal(officeNav.session, 'office', 'step should have session=office');

    const appNav = result.resolved.steps.find(s => s.id === 'app-nav');
    assert.ok(appNav, 'app-nav step should be in resolved output');
    assert.equal(appNav.session, 'app', 'step should have session=app');
  });

  test('resolveMultiSite: elements resolve from correct site symbol table', function() {
    const result = resolveMultiSite(CROSS_SITE_FLOW, SITE_MAPPINGS);
    assert.deepEqual(result.errors, [], 'no errors expected. Got: ' + result.errors.join('; '));

    const appCheck = result.resolved.steps.find(s => s.id === 'app-check');
    assert.ok(appCheck, 'app-check step should be in resolved output');
    assert.equal(appCheck.operands.selector, 'role=button[name="App Button"]', 'button_b selector from site-b');

    const officeCheck = result.resolved.steps.find(s => s.id === 'office-check');
    assert.ok(officeCheck, 'office-check should have expects');
    assert.ok(officeCheck.expects && officeCheck.expects.length > 0, 'office-check should have resolved expects');
    assert.equal(officeCheck.expects[0].selector, 'role=heading[name="Office Dashboard"]', 'heading_a from site-a');
  });

  test('resolveMultiSite: error when step has no site: qualifier', function() {
    const flowNoSite = {
      name: 'bad-cross-site',
      sites: { office: { mapping: 'site-a' }, app: { mapping: 'site-b' } },
      steps: [
        { id: 'no-site-step', type: 'snapshot', action: 'Take snapshot' },
      ],
    };
    const result = resolveMultiSite(flowNoSite, SITE_MAPPINGS);
    assert.ok(result.errors.length > 0, 'should have error for step without site: qualifier');
    const err = result.errors.find(e => e.includes('no-site-step') && e.includes('site'));
    assert.ok(err, 'error should name the step and mention site. Errors: ' + result.errors.join('; '));
  });

  test('resolveMultiSite: rejects invalid site names when called directly', function() {
    const invalidSite = 'admin-panel';
    const result = resolveMultiSite({
      name: 'invalid-site-name',
      steps: [{ id: 'bad-site', site: invalidSite, type: 'snapshot', action: 'Take snapshot' }],
    }, {
      [invalidSite]: SITE_MAPPINGS.office,
    });
    assert.ok(
      result.errors.some(error =>
        error.includes(invalidSite) && error.includes('^[A-Za-z_][A-Za-z0-9_]*$')
      ),
      'direct resolver call must enforce the central site-name contract: ' + result.errors.join('; ')
    );
  });

  test('resolveMultiSite: rejects reserved prototype aliases when called directly', function() {
    const siteMappings = Object.create(null);
    siteMappings.__proto__ = SITE_MAPPINGS.office;
    const result = resolveMultiSite({
      name: 'reserved-site-alias',
      steps: [{ id: 'reserved', site: '__proto__', type: 'snapshot', action: 'Take snapshot' }],
    }, siteMappings);
    assert.ok(
      result.errors.some(error => error.includes('__proto__') && error.includes('reserved')),
      'direct resolver must reject prototype-reserved aliases: ' + result.errors.join('; ')
    );
  });

  test('resolveMultiSite: rejects normalized base URL variable collisions', function() {
    const result = resolveMultiSite({
      name: 'colliding-site-aliases',
      steps: [
        { id: 'lower', site: 'office', type: 'snapshot', action: 'Take snapshot' },
        { id: 'upper', site: 'OFFICE', type: 'snapshot', action: 'Take snapshot' },
      ],
    }, {
      office: SITE_MAPPINGS.office,
      OFFICE: SITE_MAPPINGS.app,
    });
    assert.ok(
      result.errors.some(error =>
        error.includes('office') && error.includes('OFFICE') && error.includes('OFFICE_BASE_URL')
      ),
      'direct resolver must reject normalized env-key collisions: ' + result.errors.join('; ')
    );
  });

  test('resolveMultiSite: all 4 steps resolve without errors using inline mappings', function() {
    const result = resolveMultiSite(CROSS_SITE_FLOW, SITE_MAPPINGS);
    assert.deepEqual(result.errors, [], 'no errors expected. Got: ' + result.errors.join('; '));
    assert.equal(result.resolved.steps.length, 4, 'all 4 steps should be resolved');
  });

  test('parser: both mapping: and sites: present triggers error', function() {
    const parseResult = parse(
      path.join(FIXTURES, 'cross-site-flow.yaml'),
      FIXTURES
    );
    // cross-site-flow.yaml has only sites:, no mapping: — parse should succeed
    assert.deepEqual(parseResult.errors, [], 'cross-site-flow.yaml (sites only) should parse without error');
    assert.ok(parseResult.sites, 'parseResult.sites should be populated');
    assert.equal(parseResult.mapping, null, 'parseResult.mapping should be null for cross-site');
  });

  test('parser: cross-site-flow.yaml loads site-a and site-b mappings', function() {
    const parseResult = parse(
      path.join(FIXTURES, 'cross-site-flow.yaml'),
      FIXTURES
    );
    assert.deepEqual(parseResult.errors, [], 'parse should succeed. Got: ' + parseResult.errors.join('; '));
    assert.ok(parseResult.sites, 'parseResult.sites should exist');
    assert.ok(parseResult.sites.office, 'sites.office should exist');
    assert.ok(parseResult.sites.app, 'sites.app should exist');
    assert.equal(parseResult.sites.office.mappingName, 'site-a');
    assert.equal(parseResult.sites.app.mappingName, 'site-b');
    assert.ok(parseResult.sites.office.mapping, 'sites.office.mapping should be loaded');
    assert.ok(parseResult.sites.app.mapping, 'sites.app.mapping should be loaded');
  });
});

// ---------------------------------------------------------------------------
// Phase 4 Plan 02: wait: field threading (CODEGEN-02)
// ---------------------------------------------------------------------------

test('resolve: step with wait: 15 produces resolvedStep with timeout: 15', () => {
  const flow = {
    name: 'test-timeout',
    steps: [
      {
        id: 'fill-email',
        type: 'fill',
        action: "Fill email_input with 'test@example.com' on login",
        wait: 15,
        expect: ['email_input is visible'],
      },
    ],
  };
  const result = resolve(flow, SIMPLE_MAPPING);
  assert.deepEqual(result.errors, [], 'no errors expected. Got: ' + result.errors.join('; '));
  const step = result.resolved.steps[0];
  assert.ok(step, 'step should be resolved');
  assert.equal(step.timeout, 15, 'step.timeout should be 15 (from wait: 15). Got: ' + step.timeout);
});

test('resolve: step without wait: field produces resolvedStep with no timeout key', () => {
  const flow = {
    name: 'test-no-timeout',
    steps: [
      {
        id: 'fill-email',
        type: 'fill',
        action: "Fill email_input with 'test@example.com' on login",
        expect: ['email_input is visible'],
      },
    ],
  };
  const result = resolve(flow, SIMPLE_MAPPING);
  assert.deepEqual(result.errors, [], 'no errors expected. Got: ' + result.errors.join('; '));
  const step = result.resolved.steps[0];
  assert.ok(step, 'step should be resolved');
  assert.equal(step.timeout, undefined, 'step.timeout should be undefined when no wait: field. Got: ' + step.timeout);
});

test('resolveMultiSite: cross-site step with wait: also gets timeout threaded', () => {
  const crossSiteFlowWithWait = {
    name: 'cross-site-timeout',
    sites: {
      office: { mapping: 'site-a' },
      app: { mapping: 'site-b' },
    },
    steps: [
      { id: 'office-nav', site: 'office', type: 'navigate', action: 'Navigate to /dashboard', wait: 20 },
      { id: 'app-nav', site: 'app', type: 'navigate', action: 'Navigate to /home' },
    ],
  };
  const result = resolveMultiSite(crossSiteFlowWithWait, SITE_MAPPINGS);
  assert.deepEqual(result.errors, [], 'no errors expected. Got: ' + result.errors.join('; '));

  const officeNav = result.resolved.steps.find(s => s.id === 'office-nav');
  assert.ok(officeNav, 'office-nav step should be resolved');
  assert.equal(officeNav.timeout, 20, 'office-nav should have timeout: 20 (from wait: 20)');

  const appNav = result.resolved.steps.find(s => s.id === 'app-nav');
  assert.ok(appNav, 'app-nav step should be resolved');
  assert.equal(appNav.timeout, undefined, 'app-nav without wait: should have no timeout');
});
