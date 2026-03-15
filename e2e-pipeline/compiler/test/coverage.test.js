'use strict';

/**
 * Unit tests for compiler/coverage.js
 *
 * Tests for analyzeCoverage(), appendCoverageHistory(), checkCoverageRegression().
 * Uses inline mock data — no fixtures needed.
 */

const { test, describe, before, after } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const { analyzeCoverage, appendCoverageHistory, checkCoverageRegression } = require('../coverage.js');

// ---------------------------------------------------------------------------
// Mock data helpers
// ---------------------------------------------------------------------------

// Minimal mapping with 2 pages and 5 elements total
var MOCK_MAPPING = {
  base_url: 'http://localhost:3000',
  pages: {
    login: {
      url_pattern: '/login',
      elements: {
        email_input: { selector: 'role=textbox', description: 'Email' },
        login_button: { selector: 'role=button', description: 'Submit' },
        password_input: { selector: 'input[type=password]', description: 'Password' },
      }
    },
    dashboard: {
      url_pattern: '/dashboard',
      elements: {
        heading: { selector: 'role=heading', description: 'Dashboard heading' },
        sidebar_home: { selector: 'role=menuitem', description: 'Home link' },
      }
    }
  }
};

// Step helpers
function makeClickStep(id, element, page) {
  return { id: id, type: 'click', operands: { element: element, page: page }, expects: [] };
}

function makeFillStep(id, element, page) {
  return { id: id, type: 'fill', operands: { element: element, page: page }, expects: [] };
}

function makeNavigateStep(id, target) {
  return { id: id, type: 'navigate', operands: { target: target }, expects: [] };
}

function makeVerifyExternalStep(id) {
  return { id: id, type: 'verify-external', operands: {}, expects: [] };
}

function makeSnapshotStep(id) {
  return { id: id, type: 'snapshot', operands: {}, expects: [] };
}

function makeExpectVisibleStep(id, element) {
  return {
    id: id,
    type: 'click',
    operands: { element: element, page: 'login' },
    expects: [{ type: 'element-visible', elementName: element, raw: element + ' visible' }]
  };
}

function makeStepWithOrVisible(id, elementA, elementB) {
  return {
    id: id,
    type: 'click',
    operands: {},
    expects: [{
      type: 'or-visible',
      elements: [{ elementName: elementA }, { elementName: elementB }],
      raw: elementA + ' or ' + elementB + ' visible'
    }]
  };
}

// ---------------------------------------------------------------------------
// analyzeCoverage() — element-level tracking
// ---------------------------------------------------------------------------

describe('analyzeCoverage() — click action sets reached_count', function() {
  test('element used in click action has reached_count=1', function() {
    var steps = [makeClickStep('s1', 'login_button', 'login')];
    var result = analyzeCoverage(MOCK_MAPPING, steps);
    var el = result.elements.find(function(e) { return e.name === 'login_button'; });
    assert.ok(el, 'login_button must be in elements');
    assert.equal(el.reached_count, 1, 'Expected reached_count=1 for clicked element');
  });

  test('element used in click action has verified_count=0', function() {
    var steps = [makeClickStep('s1', 'login_button', 'login')];
    var result = analyzeCoverage(MOCK_MAPPING, steps);
    var el = result.elements.find(function(e) { return e.name === 'login_button'; });
    assert.equal(el.verified_count, 0, 'Expected verified_count=0 for only-clicked element');
  });

  test('element used in fill action has reached_count=1', function() {
    var steps = [makeFillStep('s1', 'email_input', 'login')];
    var result = analyzeCoverage(MOCK_MAPPING, steps);
    var el = result.elements.find(function(e) { return e.name === 'email_input'; });
    assert.equal(el.reached_count, 1, 'Expected reached_count=1 for filled element');
  });
});

describe('analyzeCoverage() — expect assertion sets verified_count', function() {
  test('element in element-visible expect has verified_count=1', function() {
    var steps = [{
      id: 's1', type: 'click', operands: {},
      expects: [{ type: 'element-visible', elementName: 'heading', raw: 'heading visible' }]
    }];
    var result = analyzeCoverage(MOCK_MAPPING, steps);
    var el = result.elements.find(function(e) { return e.name === 'heading'; });
    assert.ok(el, 'heading must be in elements');
    assert.equal(el.verified_count, 1, 'Expected verified_count=1');
  });

  test('element in element-visible expect has reached_count=0 when not in operands', function() {
    var steps = [{
      id: 's1', type: 'click', operands: {},
      expects: [{ type: 'element-visible', elementName: 'heading', raw: 'heading visible' }]
    }];
    var result = analyzeCoverage(MOCK_MAPPING, steps);
    var el = result.elements.find(function(e) { return e.name === 'heading'; });
    assert.equal(el.reached_count, 0, 'Expected reached_count=0 when only in expect');
  });
});

describe('analyzeCoverage() — element with both click and expect', function() {
  test('element used in click and expect has reached_count=1 and verified_count=1', function() {
    var steps = [makeExpectVisibleStep('s1', 'email_input')];
    var result = analyzeCoverage(MOCK_MAPPING, steps);
    var el = result.elements.find(function(e) { return e.name === 'email_input'; });
    assert.equal(el.reached_count, 1, 'Expected reached_count=1');
    assert.equal(el.verified_count, 1, 'Expected verified_count=1');
  });
});

describe('analyzeCoverage() — untouched elements', function() {
  test('element not in any step has reached_count=0 and verified_count=0', function() {
    var steps = [makeClickStep('s1', 'login_button', 'login')];
    var result = analyzeCoverage(MOCK_MAPPING, steps);
    var el = result.elements.find(function(e) { return e.name === 'password_input'; });
    assert.ok(el, 'password_input must be in elements');
    assert.equal(el.reached_count, 0, 'password_input should have reached_count=0');
    assert.equal(el.verified_count, 0, 'password_input should have verified_count=0');
  });

  test('all mapping elements appear in result even if untouched', function() {
    var result = analyzeCoverage(MOCK_MAPPING, []);
    var totalInMapping = 0;
    Object.keys(MOCK_MAPPING.pages).forEach(function(page) {
      totalInMapping += Object.keys(MOCK_MAPPING.pages[page].elements).length;
    });
    assert.equal(result.elements.length, totalInMapping, 'All mapping elements must be in result');
  });
});

describe('analyzeCoverage() — or-visible expect', function() {
  test('or-visible expect increments verified_count for both elements', function() {
    var steps = [makeStepWithOrVisible('s1', 'email_input', 'login_button')];
    var result = analyzeCoverage(MOCK_MAPPING, steps);
    var elA = result.elements.find(function(e) { return e.name === 'email_input'; });
    var elB = result.elements.find(function(e) { return e.name === 'login_button'; });
    assert.equal(elA.verified_count, 1, 'email_input should have verified_count=1 from or-visible');
    assert.equal(elB.verified_count, 1, 'login_button should have verified_count=1 from or-visible');
  });
});

describe('analyzeCoverage() — verify-external steps are skipped', function() {
  test('verify-external step does not contribute to element coverage', function() {
    var steps = [makeVerifyExternalStep('s1')];
    var result = analyzeCoverage(MOCK_MAPPING, steps);
    result.elements.forEach(function(el) {
      assert.equal(el.reached_count, 0, el.name + ' should have reached_count=0 after verify-external');
      assert.equal(el.verified_count, 0, el.name + ' should have verified_count=0 after verify-external');
    });
  });
});

describe('analyzeCoverage() — navigate steps', function() {
  test('navigate step does not contribute to element coverage', function() {
    var steps = [makeNavigateStep('s1', 'login')];
    var result = analyzeCoverage(MOCK_MAPPING, steps);
    result.elements.forEach(function(el) {
      assert.equal(el.reached_count, 0, el.name + ' should have reached_count=0 after navigate');
    });
  });
});

// ---------------------------------------------------------------------------
// analyzeCoverage() — summary
// ---------------------------------------------------------------------------

describe('analyzeCoverage() — summary fields', function() {
  test('summary.total equals total elements across all pages', function() {
    var result = analyzeCoverage(MOCK_MAPPING, []);
    var expectedTotal = 5; // 3 in login + 2 in dashboard
    assert.equal(result.summary.total, expectedTotal, 'summary.total must equal total elements');
  });

  test('summary.reached equals elements with reached_count > 0', function() {
    var steps = [makeClickStep('s1', 'login_button', 'login'), makeClickStep('s2', 'heading', 'dashboard')];
    var result = analyzeCoverage(MOCK_MAPPING, steps);
    assert.equal(result.summary.reached, 2, 'summary.reached must be 2');
  });

  test('summary.verified equals elements with verified_count > 0', function() {
    var steps = [{
      id: 's1', type: 'click', operands: {},
      expects: [{ type: 'element-visible', elementName: 'heading', raw: 'heading visible' }]
    }];
    var result = analyzeCoverage(MOCK_MAPPING, steps);
    assert.equal(result.summary.verified, 1, 'summary.verified must be 1');
  });

  test('summary.percent = Math.round(verified/total * 100)', function() {
    var steps = [makeExpectVisibleStep('s1', 'email_input')];
    var result = analyzeCoverage(MOCK_MAPPING, steps);
    // 1 verified out of 5 total = 20%
    assert.equal(result.summary.percent, 20, 'Expected 20% (1/5)');
  });

  test('summary.percent is 0 when no elements verified', function() {
    var result = analyzeCoverage(MOCK_MAPPING, []);
    assert.equal(result.summary.percent, 0, 'Expected 0% when nothing verified');
  });

  test('summary.percent is 0 when total is 0 (empty mapping)', function() {
    var emptyMapping = { pages: {} };
    var result = analyzeCoverage(emptyMapping, []);
    assert.equal(result.summary.percent, 0, 'Expected 0% for empty mapping');
  });
});

describe('analyzeCoverage() — page-level coverage', function() {
  test('summary.pages_total equals number of pages in mapping', function() {
    var result = analyzeCoverage(MOCK_MAPPING, []);
    assert.equal(result.summary.pages_total, 2, 'Expected 2 pages total');
  });

  test('summary.pages_reached = 0 when no navigate steps', function() {
    var steps = [makeClickStep('s1', 'login_button', 'login')];
    var result = analyzeCoverage(MOCK_MAPPING, steps);
    assert.equal(result.summary.pages_reached, 0, 'No navigate steps means pages_reached=0');
  });

  test('summary.pages_reached counts unique pages navigated to', function() {
    var steps = [
      makeNavigateStep('s1', 'login'),
      makeNavigateStep('s2', 'dashboard'),
      makeNavigateStep('s3', 'login'), // duplicate, should not double-count
    ];
    var result = analyzeCoverage(MOCK_MAPPING, steps);
    assert.equal(result.summary.pages_reached, 2, 'Expected 2 unique pages reached');
  });

  test('navigate to unknown page does not count toward pages_reached', function() {
    var steps = [makeNavigateStep('s1', 'unknown-page')];
    var result = analyzeCoverage(MOCK_MAPPING, steps);
    assert.equal(result.summary.pages_reached, 0, 'Unknown page should not count');
  });
});

// ---------------------------------------------------------------------------
// analyzeCoverage() — result shape
// ---------------------------------------------------------------------------

describe('analyzeCoverage() — result shape', function() {
  test('returns object with elements array and summary object', function() {
    var result = analyzeCoverage(MOCK_MAPPING, []);
    assert.ok(Array.isArray(result.elements), 'result.elements must be an array');
    assert.ok(result.summary && typeof result.summary === 'object', 'result.summary must be an object');
  });

  test('each element has name, page, reached_count, verified_count', function() {
    var result = analyzeCoverage(MOCK_MAPPING, []);
    result.elements.forEach(function(el) {
      assert.ok(typeof el.name === 'string', 'el.name must be string');
      assert.ok(typeof el.page === 'string', 'el.page must be string');
      assert.equal(typeof el.reached_count, 'number', 'el.reached_count must be number');
      assert.equal(typeof el.verified_count, 'number', 'el.verified_count must be number');
    });
  });
});

// ---------------------------------------------------------------------------
// appendCoverageHistory()
// ---------------------------------------------------------------------------

describe('appendCoverageHistory() — creates file if missing', function() {
  var tmpDir;

  before(function() {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'coverage-test-'));
  });

  after(function() {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  test('creates history file when it does not exist', function() {
    var historyPath = path.join(tmpDir, 'coverage-history.json');
    assert.ok(!fs.existsSync(historyPath), 'file must not exist before test');
    appendCoverageHistory(historyPath, { flow: 'test-flow', percent: 80 });
    assert.ok(fs.existsSync(historyPath), 'history file must be created');
  });

  test('created file contains valid JSON array with one entry', function() {
    var historyPath = path.join(tmpDir, 'new-history.json');
    appendCoverageHistory(historyPath, { flow: 'test-flow', percent: 80 });
    var data = JSON.parse(fs.readFileSync(historyPath, 'utf8'));
    assert.ok(Array.isArray(data), 'history must be JSON array');
    assert.equal(data.length, 1, 'array must have 1 entry');
    assert.equal(data[0].flow, 'test-flow', 'entry must have flow field');
    assert.equal(data[0].percent, 80, 'entry must have percent field');
  });
});

describe('appendCoverageHistory() — appends to existing file', function() {
  var tmpDir;

  before(function() {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'coverage-test-append-'));
  });

  after(function() {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  test('appends entry to existing file (does not overwrite)', function() {
    var historyPath = path.join(tmpDir, 'history.json');
    appendCoverageHistory(historyPath, { flow: 'flow-a', percent: 60 });
    appendCoverageHistory(historyPath, { flow: 'flow-b', percent: 70 });
    var data = JSON.parse(fs.readFileSync(historyPath, 'utf8'));
    assert.equal(data.length, 2, 'history must have 2 entries after 2 appends');
    assert.equal(data[0].flow, 'flow-a', 'first entry must be flow-a');
    assert.equal(data[1].flow, 'flow-b', 'second entry must be flow-b');
  });

  test('creates parent directories if missing', function() {
    var deepPath = path.join(tmpDir, 'deep', 'nested', 'history.json');
    appendCoverageHistory(deepPath, { flow: 'test', percent: 50 });
    assert.ok(fs.existsSync(deepPath), 'must create file even in nested dirs');
  });
});

// ---------------------------------------------------------------------------
// checkCoverageRegression()
// ---------------------------------------------------------------------------

describe('checkCoverageRegression() — not enough history', function() {
  var tmpDir;

  before(function() {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'coverage-regression-'));
  });

  after(function() {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  test('returns null when history file does not exist', function() {
    var missingPath = path.join(tmpDir, 'nonexistent.json');
    var result = checkCoverageRegression(missingPath, 'my-flow', 80);
    assert.equal(result, null, 'Expected null when no history file');
  });

  test('returns null when only 1 entry for this flow', function() {
    var historyPath = path.join(tmpDir, 'single-entry.json');
    fs.writeFileSync(historyPath, JSON.stringify([{ flow: 'my-flow', percent: 80 }]) + '\n');
    var result = checkCoverageRegression(historyPath, 'my-flow', 75);
    assert.equal(result, null, 'Expected null with only 1 entry (need >=2 to compare)');
  });

  test('returns null when no entries for this flow', function() {
    var historyPath = path.join(tmpDir, 'other-flow.json');
    fs.writeFileSync(historyPath, JSON.stringify([{ flow: 'other-flow', percent: 80 }]) + '\n');
    var result = checkCoverageRegression(historyPath, 'my-flow', 60);
    assert.equal(result, null, 'Expected null when flow has no history');
  });
});

describe('checkCoverageRegression() — regression detection', function() {
  var tmpDir;

  before(function() {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'coverage-regression2-'));
  });

  after(function() {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  test('returns warning string when coverage drops more than 5%', function() {
    var historyPath = path.join(tmpDir, 'regression.json');
    fs.writeFileSync(historyPath, JSON.stringify([
      { flow: 'my-flow', percent: 80 },
      { flow: 'my-flow', percent: 70 }
    ]) + '\n');
    // currentPercent=64 (dropped 6 from previous 70)
    var result = checkCoverageRegression(historyPath, 'my-flow', 64);
    assert.ok(typeof result === 'string', 'Expected string warning when regression > 5%');
    assert.ok(result.includes('::warning::'), 'Warning must use ::warning:: format');
  });

  test('returns null when drop is exactly 5% (not more than 5)', function() {
    var historyPath = path.join(tmpDir, 'edge-case.json');
    fs.writeFileSync(historyPath, JSON.stringify([
      { flow: 'my-flow', percent: 80 },
      { flow: 'my-flow', percent: 70 }
    ]) + '\n');
    // currentPercent=65 (dropped exactly 5 from 70)
    var result = checkCoverageRegression(historyPath, 'my-flow', 65);
    assert.equal(result, null, 'Expected null when drop is exactly 5% (not more than 5)');
  });

  test('returns null when coverage increases', function() {
    var historyPath = path.join(tmpDir, 'increase.json');
    fs.writeFileSync(historyPath, JSON.stringify([
      { flow: 'my-flow', percent: 70 },
      { flow: 'my-flow', percent: 80 }
    ]) + '\n');
    var result = checkCoverageRegression(historyPath, 'my-flow', 90);
    assert.equal(result, null, 'Expected null when coverage increases');
  });

  test('compares against most recent entry for same flow (not entries for other flows)', function() {
    var historyPath = path.join(tmpDir, 'multi-flow.json');
    fs.writeFileSync(historyPath, JSON.stringify([
      { flow: 'my-flow', percent: 80 },
      { flow: 'other-flow', percent: 10 }, // this should not interfere
      { flow: 'my-flow', percent: 75 },
    ]) + '\n');
    // currentPercent=74 (dropped 1 from previous my-flow=75) — no regression
    var result = checkCoverageRegression(historyPath, 'my-flow', 74);
    assert.equal(result, null, 'Expected null for 1% drop (other-flow entries must be ignored)');
  });

  test('warning string contains flow name', function() {
    var historyPath = path.join(tmpDir, 'with-name.json');
    fs.writeFileSync(historyPath, JSON.stringify([
      { flow: 'test-login', percent: 90 },
      { flow: 'test-login', percent: 85 }
    ]) + '\n');
    var result = checkCoverageRegression(historyPath, 'test-login', 78);
    assert.ok(result && result.includes('test-login'), 'Warning must include flow name');
  });
});
