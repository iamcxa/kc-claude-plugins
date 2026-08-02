'use strict';

const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const { parse } = require('../parser');

function parseMapping(t, policy, options) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'visibility-policy-'));
  t.after(function () { fs.rmSync(dir, { recursive: true, force: true }); });
  const element = { selector: '[data-testid="heading"]' };
  if (policy !== undefined) element.visibility_policy = policy;
  const mapping = {
    version: 2,
    app: 'visibility-policy-fixture',
    base_url: 'https://example.test',
    pages: { home: { url_pattern: '/', elements: { page_heading: element } } },
  };
  fs.writeFileSync(path.join(dir, 'fixture.yaml'), JSON.stringify(mapping), 'utf8');

  const flow = options?.crossSite ? {
    name: 'visibility-policy-cross-site',
    sites: { primary: { mapping: 'fixture' } },
    steps: [{ id: 'snapshot', site: 'primary', type: 'snapshot', action: 'Take snapshot' }],
  } : {
    name: 'visibility-policy-single-site',
    mapping: 'fixture',
    steps: [{ id: 'snapshot', type: 'snapshot', action: 'Take snapshot' }],
  };
  const flowPath = path.join(dir, 'flow.json');
  fs.writeFileSync(flowPath, JSON.stringify(flow), 'utf8');
  return parse(flowPath, dir);
}

test('mapping visibility_policy accepts absence, strict, and retained-zero-rect', function (t) {
  for (const policy of [undefined, 'strict', 'retained-zero-rect']) {
    const result = parseMapping(t, policy);
    assert.deepEqual(result.errors, [], policy + ': ' + JSON.stringify(result.errors));
  }
});

test('mapping visibility_policy rejects invalid values and types with element identity', function (t) {
  for (const policy of ['any-visible', '', false, 1, null, ['strict'], { mode: 'strict' }]) {
    const result = parseMapping(t, policy);
    const error = result.errors.find(function (item) {
      return item.includes('visibility_policy');
    });
    assert.ok(error, JSON.stringify({ policy: policy, errors: result.errors }));
    assert.match(error, /fixture\.yaml/);
    assert.match(error, /home\.page_heading/);
    assert.match(error, /strict/);
    assert.match(error, /retained-zero-rect/);
  }
});

test('cross-site mapping validation rejects invalid visibility_policy before resolution', function (t) {
  const result = parseMapping(t, 'any-visible', { crossSite: true });
  assert.ok(result.errors.some(function (error) {
    return error.includes('fixture.yaml') && error.includes('home.page_heading');
  }), JSON.stringify(result.errors));
});
