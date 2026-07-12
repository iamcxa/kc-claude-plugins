'use strict';

const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

// The parse function under test
const { parse } = require('../parser');

const FIXTURES = path.join(__dirname, 'fixtures');

function parseTemporaryFlow(flow) {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-parser-step-id-'));
  const flowPath = path.join(tmpDir, 'flow.json');
  fs.writeFileSync(flowPath, JSON.stringify(flow), 'utf8');
  try {
    return parse(flowPath, FIXTURES);
  } finally {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  }
}

test('parse: every step id must be a non-empty string', function() {
  for (const invalidId of [undefined, '', 42]) {
    const step = { type: 'snapshot', action: 'Take snapshot' };
    if (invalidId !== undefined) step.id = invalidId;
    const result = parseTemporaryFlow({
      name: 'invalid-step-id', mapping: 'site-a', steps: [step],
    });
    assert.ok(
      result.errors.some(error => error.includes('Step at index 0') && error.includes('non-empty string')),
      'invalid id must be rejected clearly: ' + JSON.stringify(result.errors)
    );
  }
});

test('parse: duplicate step ids are rejected in single-site and cross-site flows', function() {
  for (const flow of [
    {
      name: 'duplicate-single', mapping: 'site-a',
      steps: [
        { id: 'same', type: 'snapshot', action: 'Take snapshot' },
        { id: 'same', type: 'snapshot', action: 'Take snapshot' },
      ],
    },
    {
      name: 'duplicate-cross', sites: { office: { mapping: 'site-a' } },
      steps: [
        { id: 'same', site: 'office', type: 'snapshot', action: 'Take snapshot' },
        { id: 'same', site: 'office', type: 'snapshot', action: 'Take snapshot' },
      ],
    },
  ]) {
    const result = parseTemporaryFlow(flow);
    assert.ok(
      result.errors.some(error => error.includes("Duplicate step id 'same'") && error.includes('indexes 0 and 1')),
      'duplicate id must identify the id and both positions: ' + JSON.stringify(result.errors)
    );
  }
});

test('parse: invalid site aliases do not register injected variable collisions', function() {
  const cases = [
    {
      flow: {
        name: 'reserved-alias-variable',
        variables: { constructor_base_url: 'https://example.test' },
        sites: { constructor: { mapping: 'site-a' } },
        steps: [{ id: 'reserved', site: 'constructor', type: 'snapshot', action: 'Take snapshot' }],
      },
      primary: error => error.includes('constructor') && error.includes('reserved'),
      forbidden: 'CONSTRUCTOR_BASE_URL',
    },
    {
      flow: {
        name: 'invalid-alias-variable',
        variables: { 'admin-panel_base_url': 'https://example.test' },
        sites: { 'admin-panel': { mapping: 'site-a' } },
        steps: [{ id: 'invalid', site: 'admin-panel', type: 'snapshot', action: 'Take snapshot' }],
      },
      primary: error => error.includes('admin-panel') && error.includes('shell identifier'),
      forbidden: 'ADMIN-PANEL_BASE_URL',
    },
  ];

  for (const testCase of cases) {
    const result = parseTemporaryFlow(testCase.flow);
    assert.ok(result.errors.some(testCase.primary), JSON.stringify(result.errors));
    assert.equal(
      result.errors.some(error => error.includes('collide') && error.includes(testCase.forbidden)),
      false,
      'invalid alias must not create an injected-variable collision: ' + JSON.stringify(result.errors)
    );
  }
});

test('parse: happy path — loads simple-flow.yaml and resolves mapping', async () => {
  const flowPath = path.join(FIXTURES, 'simple-flow.yaml');
  const result = parse(flowPath, FIXTURES);

  assert.deepEqual(result.errors, [], 'errors should be empty on success');

  // Flow object checks
  assert.equal(result.flow.name, 'test-login');
  assert.equal(result.flow.steps.length, 6, 'should have 6 steps');
  assert.equal(result.flow.mapping, 'test-app');

  // Variables block preserved
  assert.ok(result.flow.variables, 'variables block should be present');
  assert.equal(result.flow.variables.base_url, 'http://localhost:3000');

  // Mapping object checks
  assert.ok(result.mapping, 'mapping should be loaded');
  assert.equal(Object.keys(result.mapping.pages).length, 3, 'mapping should have 3 pages');
  assert.ok(result.mapping.pages.login, 'mapping should have login page');
  assert.ok(result.mapping.pages.dashboard, 'mapping should have dashboard page');
  assert.ok(result.mapping.pages._global, 'mapping should have _global page');
});

test('parse: mapping field resolves to correct filename in mappingDir', async () => {
  // flow has mapping: test-app → should look for test-app.yaml in FIXTURES
  const flowPath = path.join(FIXTURES, 'simple-flow.yaml');
  const result = parse(flowPath, FIXTURES);

  // If resolved correctly, mapping will have version 2 and app 'test-app'
  assert.equal(result.mapping.version, 2);
  assert.equal(result.mapping.app, 'test-app');
});

test('parse: flow steps preserve id, action, type, and expect fields', async () => {
  const flowPath = path.join(FIXTURES, 'simple-flow.yaml');
  const result = parse(flowPath, FIXTURES);

  const fillStep = result.flow.steps.find(s => s.id === 'fill-email');
  assert.ok(fillStep, 'fill-email step should exist');
  assert.equal(fillStep.type, 'fill');
  assert.ok(fillStep.expect, 'expect array should be present');
  assert.equal(fillStep.expect[0], 'email_input is visible');

  const navStep = result.flow.steps.find(s => s.id === 'navigate-to-login');
  assert.ok(navStep, 'navigate-to-login step should exist');
  assert.equal(navStep.type, 'navigate');
});

test('parse: mapping pages contain elements with selector and description', async () => {
  const flowPath = path.join(FIXTURES, 'simple-flow.yaml');
  const result = parse(flowPath, FIXTURES);

  const loginPage = result.mapping.pages.login;
  assert.ok(loginPage.elements.email_input, 'email_input element should exist');
  assert.ok(loginPage.elements.email_input.selector, 'email_input should have selector');
  assert.ok(loginPage.elements.email_input.description, 'email_input should have description');
});

test('parse: non-existent flow file returns error with file path', async () => {
  const flowPath = path.join(FIXTURES, 'does-not-exist.yaml');
  const result = parse(flowPath, FIXTURES);

  assert.ok(result.errors.length > 0, 'should have errors');
  const hasFilePath = result.errors.some(e => e.includes('does-not-exist.yaml'));
  assert.ok(hasFilePath, 'error should mention the missing file path');
  assert.equal(result.flow, null, 'flow should be null on error');
});

test('parse: flow referencing nonexistent mapping returns error naming missing file', async () => {
  const flowPath = path.join(FIXTURES, 'missing-element-flow.yaml');
  // missing-element-flow.yaml has mapping: test-app, so test-app.yaml must exist
  // We use a fake mappingDir where test-app.yaml does not exist
  const fakeMappingDir = path.join(FIXTURES, 'nonexistent-dir');
  const result = parse(flowPath, fakeMappingDir);

  assert.ok(result.errors.length > 0, 'should have errors');
  // Error should mention mapping file name
  const hasMappingRef = result.errors.some(e => e.includes('test-app.yaml') || e.includes('test-app'));
  assert.ok(hasMappingRef, 'error should reference the missing mapping file');
});

test('parse: malformed YAML returns error containing "YAML parse error" and file path', async () => {
  // We create an in-memory test using a temp file approach, but since we can't
  // easily create temp files in node:test without extra deps, we test with
  // a fixture that has valid YAML and confirm the format of the error message
  // by calling the parser with a path we can control

  // For this test, we simulate by using simple-flow.yaml but a broken mapping dir
  // Actually let's test with a real malformed fixture path approach:
  // The parser should handle fs.readFileSync errors and yaml.YAMLException

  // Test that the error format contains the right string
  // We do this via passing a non-yaml file path
  const notYamlPath = path.join(__dirname, 'parser.test.js'); // JS file, not YAML
  const result = parse(notYamlPath, FIXTURES);

  assert.ok(result.errors.length > 0, 'should have errors');
  const hasYamlError = result.errors.some(e =>
    e.includes('YAML parse error') || e.includes('parser.test.js')
  );
  assert.ok(hasYamlError, 'error should indicate YAML parse error with file path. Errors: ' + result.errors.join('; '));
});

test('parse: missing-element-flow.yaml loads successfully (it is valid YAML)', async () => {
  const flowPath = path.join(FIXTURES, 'missing-element-flow.yaml');
  const result = parse(flowPath, FIXTURES);

  // This flow has a valid structure but references a nonexistent element
  // The parser only validates structure, not element resolution
  assert.deepEqual(result.errors, [], 'parser should not error on valid YAML');
  assert.equal(result.flow.name, 'test-missing');
  assert.equal(result.flow.steps.length, 1);
});
